# -*- coding: utf-8 -*-
"""
===================================
全 A 股每日成交数据服务（异步协程版）
===================================

功能：
1. 获取全 A 股列表（沪深京 A 股）
2. 每日定时获取所有 A 股的成交数据
3. 使用 akshare 接口，前复权数据
4. 初始化时获取 2025-07-01 以来的历史数据
5. 数据存储到 stock_daily 表
6. 使用 6 个协程并发获取数据
7. 重试机制 + 错误暂停恢复

数据来源：复用 AkshareFetcher._fetch_raw_data()
"""

import logging
import asyncio
import time
import requests
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import and_, select, func

from src.storage import StockDaily, get_db
from data_provider.akshare_fetcher import AkshareFetcher

logger = logging.getLogger(__name__)


# 协程并发数
CONCURRENT_SEMAPHORE = 6

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）
ERROR_PAUSE_DELAY = 30  # 错误暂停延迟（秒）


class CircuitBreaker:
    """
    熔断器：当错误率达到阈值时，暂停所有协程
    """

    def __init__(self, error_threshold: int = 5, pause_delay: int = ERROR_PAUSE_DELAY):
        self.error_threshold = error_threshold
        self.pause_delay = pause_delay
        self.error_count = 0
        self.last_error_time: Optional[float] = None
        self.is_paused = False
        self._lock = asyncio.Lock()

    async def record_error(self):
        """记录错误，如果超过阈值则进入暂停状态"""
        async with self._lock:
            self.error_count += 1
            self.last_error_time = asyncio.get_event_loop().time()

            if self.error_count >= self.error_threshold:
                self.is_paused = True
                logger.warning(f"熔断器触发：错误数达到 {self.error_count}，暂停 {self.pause_delay} 秒")

    async def check_pause(self):
        """检查是否需要暂停或恢复"""
        async with self._lock:
            if self.is_paused:
                if self.last_error_time and \
                   (asyncio.get_event_loop().time() - self.last_error_time) >= self.pause_delay:
                    logger.info("熔断器恢复：暂停时间结束，继续执行")
                    self.is_paused = False
                    self.error_count = 0
                else:
                    remaining = self.pause_delay - (asyncio.get_event_loop().time() - self.last_error_time)
                    if remaining > 0:
                        logger.info(f"熔断器暂停中，剩余 {remaining:.1f} 秒")
                    return True
            return False

    async def reset(self):
        """重置错误计数（成功时调用）"""
        async with self._lock:
            if self.error_count > 0:
                self.error_count = max(0, self.error_count - 1)


class AllSharesDailyService:
    """
    全 A 股每日成交数据服务（异步协程版）

    职责：
    - 获取全 A 股列表
    - 批量获取历史数据（从 2025-07-01 开始）
    - 每日更新最新数据
    - 复用 AkshareFetcher 获取数据
    - 6 协程并发获取
    - 重试机制 + 熔断器保护
    """

    # 历史数据开始日期
    HISTORY_START_DATE = "20250701"

    def __init__(self):
        self.db = get_db()
        self.fetcher = AkshareFetcher()  # 复用现有的 AkshareFetcher
        self._executor = ThreadPoolExecutor(max_workers=CONCURRENT_SEMAPHORE)
        self._semaphore = asyncio.Semaphore(CONCURRENT_SEMAPHORE)
        self._circuit_breaker = CircuitBreaker(
            error_threshold=5,
            pause_delay=ERROR_PAUSE_DELAY
        )

    def __del__(self):
        if hasattr(self, '_executor') and self._executor:
            self._executor.shutdown(wait=False)

    def get_all_a_shares_list(self) -> Optional[pd.DataFrame]:
        """
        获取全 A 股列表（沪深京 A 股）
        带重试机制，防封禁策略，多数据源 fallback

        Returns:
            包含 code, name 列的 DataFrame
        """
        import akshare as ak
        import requests

        max_retries = 3
        retry_delay = 2

        # 尝试多个数据源
        data_sources = ['sina']

        for source in data_sources:
            logger.info(f"尝试使用 {source} 数据源获取 A 股列表...")

            try:
                if source == 'eastmoney':
                    # 东方财富数据源
                    for attempt in range(max_retries):
                        try:
                            logger.info(f"正在获取沪深 A 股列表... (尝试 {attempt + 1}/{max_retries})")
                            df_sh = ak.stock_sh_a_spot_em()
                            df_sz = ak.stock_sz_a_spot_em()

                            # 合并沪深 A 股
                            if not df_sh.empty and not df_sz.empty:
                                df_all = pd.concat([df_sh, df_sz], ignore_index=True)
                            elif not df_sh.empty:
                                df_all = df_sh
                            elif not df_sz.empty:
                                df_all = df_sz
                            else:
                                logger.error("无法获取 A 股列表")
                                continue

                            # 获取京市 A 股
                            try:
                                logger.info("正在获取京市 A 股列表...")
                                df_bse = ak.stock_bj_a_spot_em()
                                if not df_bse.empty:
                                    df_all = pd.concat([df_all, df_bse], ignore_index=True)
                            except Exception as e:
                                logger.warning(f"获取京市 A 股列表失败：{e}")

                            return self._process_stock_list(df_all)

                        except Exception as e:
                            logger.warning(f"获取 A 股列表失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                            if attempt < max_retries - 1:
                                delay = retry_delay * (2 ** attempt)
                                logger.info(f"{delay} 秒后重试...")
                                time.sleep(delay)
                            else:
                                logger.error(f"东方财富数据源失败，已达最大重试次数")
                                break

                elif source == 'sina':
                    # 新浪财经数据源 - 获取 A 股代码列表
                    logger.info("使用新浪财经数据源获取 A 股列表...")
                    all_codes = []

                    # 获取沪市 A 股
                    all_codes.extend(self._get_sina_a_shares('sh'))
                    # 获取深市 A 股
                    all_codes.extend(self._get_sina_a_shares('sz'))

                    if all_codes:
                        df_result = pd.DataFrame(all_codes, columns=['code'])
                        df_result = df_result[df_result['code'].str.match(r'^\d{6}$')]
                        logger.info(f"获取到 A 股列表：{len(df_result)} 只股票")
                        return df_result

            except Exception as e:
                logger.exception(f"数据源 {source} 失败：{e}")
                continue

        logger.error("所有数据源均失败")
        return None

    def _get_sina_a_shares(self, exchange: str) -> List[Dict[str, str]]:
        """
        从新浪财经获取 A 股列表

        Args:
            exchange: 'sh' 或 'sz'

        Returns:
            包含 code 的字典列表
        """
        result = []
        page = 1
        page_size = 100

        while True:
            try:
                url = f"http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple"
                params = {
                    "page": page,
                    "num": page_size,
                    "sort": "symbol",
                    "asc": "1",
                    "node": f"{exchange}_a",
                    "[object]": "HTML"
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data or len(data) == 0:
                    break

                for item in data:
                    result.append({
                        'code': item.get('code', ''),
                        'name': item.get('name', '')
                    })

                if len(data) < page_size:
                    break

                page += 1
                time.sleep(0.5)  # 避免请求过快

            except Exception as e:
                logger.warning(f"获取新浪财经 {exchange} 数据失败：{e}")
                break

        return result

    def _process_stock_list(self, df_all: pd.DataFrame) -> Optional[pd.DataFrame]:
        """处理股票列表 DataFrame"""
        # 标准化列名
        df_all.columns = df_all.columns.str.lower().str.strip()

        # 找到代码列
        code_col = None
        for col in ['代码', 'code', '股票代码']:
            if col in df_all.columns:
                code_col = col
                break

        if code_col:
            df_result = df_all[[code_col]].copy()
            df_result.columns = ['code']

            # 标准化代码格式（去除前缀）
            from data_provider.base import normalize_stock_code
            df_result['code'] = df_result['code'].apply(normalize_stock_code)

            # 过滤出 A 股代码（6 位数字）
            df_result = df_result[df_result['code'].str.match(r'^\d{6}$')]

            # 添加名称列
            name_col = None
            for col in ['名称', 'name', '股票名称']:
                if col in df_all.columns:
                    name_col = col
                    break
            if name_col:
                df_result['name'] = df_all[name_col].values

            logger.info(f"获取到 A 股列表：{len(df_result)} 只股票")
            return df_result
        else:
            logger.error(f"无法识别代码列，可用列：{df_all.columns.tolist()}")
            return None

    def _fetch_daily_data_sync(
        self,
        stock_code: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        同步方法：获取单只股票的历史日线数据（前复权）
        复用 AkshareFetcher._fetch_raw_data()
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")

            logger.debug(f"获取 {stock_code} 的历史数据：{start_date} - {end_date}")

            # 复用 AkshareFetcher 的 _fetch_raw_data 方法（已包含前复权逻辑）
            df = self.fetcher._fetch_raw_data(stock_code, start_date, end_date)

            if df is not None and not df.empty:
                logger.debug(f"股票 {stock_code} 获取到 {len(df)} 条数据")
                return df

            return None

        except Exception as e:
            logger.warning(f"获取 {stock_code} 的历史数据失败：{e}")
            return None

    async def _fetch_daily_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        异步方法：获取单只股票的历史日线数据（带重试）
        """
        async with self._semaphore:
            # 检查熔断器状态
            if await self._circuit_breaker.check_pause():
                while await self._circuit_breaker.check_pause():
                    await asyncio.sleep(1)

            for attempt in range(MAX_RETRIES):
                try:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self._executor,
                        self._fetch_daily_data_sync,
                        stock_code,
                        start_date,
                        end_date
                    )

                    if result is not None:
                        await self._circuit_breaker.reset()
                        return result

                    return None

                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"获取 {stock_code} 失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {error_msg}")

                    await self._circuit_breaker.record_error()

                    if attempt < MAX_RETRIES - 1:
                        retry_delay = RETRY_DELAY * (2 ** attempt)
                        logger.info(f"{retry_delay} 秒后重试...")
                        await asyncio.sleep(retry_delay)

                        if await self._circuit_breaker.check_pause():
                            while await self._circuit_breaker.check_pause():
                                await asyncio.sleep(1)
                    else:
                        logger.error(f"获取 {stock_code} 失败，已达最大重试次数")
                        return None

            return None

    def _save_daily_data_sync(self, df: pd.DataFrame, stock_code: str, data_source: str = "akshare"):
        """
        同步方法：保存日线数据到数据库
        """
        if df is None or df.empty:
            return

        session = None
        try:
            session = self.db.get_session()

            # 标准化列名映射（akshare 返回的列名）
            column_mapping = {
                '日期': 'date',
                'open': 'open',
                '开盘': 'open',
                'close': 'close',
                '收盘': 'close',
                'high': 'high',
                '最高': 'high',
                'low': 'low',
                '最低': 'low',
                '成交量': 'volume',
                'volume': 'volume',
                '成交额': 'amount',
                'amount': 'amount',
                '涨跌幅': 'pct_chg',
                'pct_chg': 'pct_chg',
            }

            df_copy = df.copy()
            df_copy.columns = [column_mapping.get(col, col) for col in df_copy.columns]

            if 'date' in df_copy.columns:
                df_copy['date'] = pd.to_datetime(df_copy['date']).dt.date

            saved_count = 0
            updated_count = 0

            for _, row in df_copy.iterrows():
                try:
                    trade_date = row.get('date')
                    if trade_date is None:
                        continue

                    if isinstance(trade_date, (datetime, pd.Timestamp)):
                        trade_date = trade_date.date()
                    elif isinstance(trade_date, str):
                        trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()

                    existing = session.execute(
                        select(StockDaily).where(
                            and_(
                                StockDaily.code == stock_code,
                                StockDaily.date == trade_date
                            )
                        )
                    ).scalars().first()

                    if existing:
                        existing.open = row.get('open')
                        existing.high = row.get('high')
                        existing.low = row.get('low')
                        existing.close = row.get('close')
                        existing.volume = row.get('volume')
                        existing.amount = row.get('amount')
                        existing.pct_chg = row.get('pct_chg')
                        existing.data_source = data_source
                        updated_count += 1
                    else:
                        daily = StockDaily(
                            code=stock_code,
                            date=trade_date,
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            close=row.get('close'),
                            volume=row.get('volume'),
                            amount=row.get('amount'),
                            pct_chg=row.get('pct_chg'),
                            data_source=data_source
                        )
                        session.add(daily)
                        saved_count += 1

                except Exception as e:
                    logger.warning(f"保存 {stock_code} 日期 {row.get('date')} 失败：{e}")
                    continue

            session.commit()
            logger.info(f"股票 {stock_code} 数据保存完成：新增 {saved_count} 条，更新 {updated_count} 条")

        except Exception as e:
            logger.exception(f"保存 {stock_code} 数据失败：{e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()

    async def _save_daily_data(self, df: pd.DataFrame, stock_code: str, data_source: str = "akshare"):
        """异步方法：保存日线数据到数据库"""
        if df is None or df.empty:
            return

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            self._save_daily_data_sync,
            df,
            stock_code,
            data_source
        )

    def _get_latest_date_in_db_sync(self, stock_code: str) -> Optional[date]:
        """同步方法：获取数据库中某股票的最新日期"""
        try:
            session = self.db.get_session()
            result = session.execute(
                select(func.max(StockDaily.date)).where(StockDaily.code == stock_code)
            ).scalar()
            session.close()
            return result
        except Exception as e:
            logger.warning(f"获取 {stock_code} 最新日期失败：{e}")
            return None

    async def _get_latest_date_in_db(self, stock_code: str) -> Optional[date]:
        """异步方法：获取数据库中某股票的最新日期"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._get_latest_date_in_db_sync,
            stock_code
        )

    async def _process_stock(
        self,
        stock_code: str,
        stock_name: str,
        start_date: str,
        end_date: Optional[str] = None,
        skip_if_exists: bool = True
    ) -> Tuple[bool, str]:
        """
        处理单只股票：获取并保存数据（带重试和熔断器保护）
        """
        try:
            # 检查熔断器状态
            if await self._circuit_breaker.check_pause():
                while await self._circuit_breaker.check_pause():
                    await asyncio.sleep(1)

            # 检查数据库中是否已有数据
            latest_date = await self._get_latest_date_in_db(stock_code)

            if latest_date and skip_if_exists:
                logger.debug(f"股票 {stock_code} 已有数据，最新日期：{latest_date}，跳过")
                await self._circuit_breaker.reset()
                return True, "exists"

            # 确定开始日期
            if latest_date:
                actual_start = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
            else:
                actual_start = start_date

            # 获取历史数据（带重试）
            df = await self._fetch_daily_data(stock_code, actual_start, end_date)

            if df is not None and not df.empty:
                await self._save_daily_data(df, stock_code)
                return True, f"saved {len(df)} records"
            else:
                logger.warning(f"股票 {stock_code} 无数据返回")
                return False, "no data"

        except asyncio.CancelledError:
            logger.warning(f"股票 {stock_code} 任务被取消")
            return False, "cancelled"
        except Exception as e:
            logger.exception(f"处理股票 {stock_code} 失败：{e}")
            return False, str(e)

    async def initialize_historical_data_async(
        self,
        start_date: str = HISTORY_START_DATE,
        limit: Optional[int] = None
    ):
        """异步初始化历史数据（带熔断器保护）"""
        logger.info(f"开始初始化历史数据，开始日期：{start_date}，并发数：{CONCURRENT_SEMAPHORE}")

        stock_list = self.get_all_a_shares_list()
        if stock_list is None or stock_list.empty:
            logger.error("无法获取 A 股列表，初始化失败")
            return

        if limit:
            stock_list = stock_list.head(limit)
            logger.info(f"限制处理 {limit} 只股票（测试模式）")

        total = len(stock_list)
        logger.info(f"共获取到 {total} 只股票，开始获取历史数据...")

        tasks = []
        end_date = datetime.now().strftime("%Y%m%d")

        for idx, row in stock_list.iterrows():
            stock_code = row['code']
            stock_name = row.get('name', 'Unknown')

            task = self._process_stock(
                stock_code=stock_code,
                stock_name=stock_name,
                start_date=start_date,
                end_date=end_date,
                skip_if_exists=True
            )
            tasks.append(asyncio.create_task(task))

        success_count = 0
        fail_count = 0
        batch_size = CONCURRENT_SEMAPHORE

        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]

            if await self._circuit_breaker.check_pause():
                logger.info(f"批次 {i//batch_size + 1} 开始前，熔断器触发，等待恢复...")
                while await self._circuit_breaker.check_pause():
                    await asyncio.sleep(1)

            results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for j, result in enumerate(results):
                stock_idx = i + j
                if isinstance(result, Exception):
                    fail_count += 1
                    logger.warning(f"股票 {stock_list.iloc[stock_idx]['code']} 处理异常：{result}")
                    await self._circuit_breaker.record_error()
                elif isinstance(result, tuple):
                    success, msg = result
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        if msg not in ["exists", "no data"]:
                            await self._circuit_breaker.record_error()

            completed = min(i + batch_size, total)
            if completed % 100 == 0 or completed == total:
                logger.info(f"进度：{completed}/{total}，成功：{success_count}，失败：{fail_count}")

            if self._circuit_breaker.is_paused:
                logger.info(f"批次 {i//batch_size + 1} 完成后熔断器触发，等待 {ERROR_PAUSE_DELAY} 秒后继续...")
                await asyncio.sleep(ERROR_PAUSE_DELAY)
                await self._circuit_breaker.reset()

        logger.info(f"历史数据初始化完成！成功：{success_count}，失败：{fail_count}")

    async def update_today_data_async(self):
        """异步更新今日数据（带熔断器保护）"""
        logger.info(f"开始更新今日数据，并发数：{CONCURRENT_SEMAPHORE}")

        stock_list = self.get_all_a_shares_list()
        if stock_list is None or stock_list.empty:
            logger.error("无法获取 A 股列表")
            return

        today = date.today()
        end_date = today.strftime("%Y%m%d")

        tasks = []
        for _, row in stock_list.iterrows():
            stock_code = row['code']
            stock_name = row.get('name', 'Unknown')

            task = self._process_stock(
                stock_code=stock_code,
                stock_name=stock_name,
                start_date=self.HISTORY_START_DATE,
                end_date=end_date,
                skip_if_exists=True
            )
            tasks.append(asyncio.create_task(task))

        success_count = 0
        fail_count = 0
        batch_size = CONCURRENT_SEMAPHORE

        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]

            if await self._circuit_breaker.check_pause():
                logger.info(f"批次 {i//batch_size + 1} 开始前，熔断器触发，等待恢复...")
                while await self._circuit_breaker.check_pause():
                    await asyncio.sleep(1)

            results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for j, result in enumerate(results):
                stock_idx = i + j
                if isinstance(result, Exception):
                    fail_count += 1
                    logger.warning(f"股票 {stock_list.iloc[stock_idx]['code']} 处理异常：{result}")
                    await self._circuit_breaker.record_error()
                elif isinstance(result, tuple):
                    success, _ = result
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1

            completed = min(i + batch_size, len(tasks))
            if completed % 100 == 0 or completed == len(tasks):
                logger.info(f"进度：{completed}/{len(tasks)}，成功：{success_count}，失败：{fail_count}")

            if self._circuit_breaker.is_paused:
                logger.info(f"批次 {i//batch_size + 1} 完成后熔断器触发，等待 {ERROR_PAUSE_DELAY} 秒后继续...")
                await asyncio.sleep(ERROR_PAUSE_DELAY)
                await self._circuit_breaker.reset()

        logger.info(f"今日数据更新完成，成功：{success_count}，失败：{fail_count}")

    def run(self, mode: str = "update", limit: Optional[int] = None, start_date: Optional[str] = None):
        """
        运行服务（同步入口）

        Args:
            mode: 运行模式
                - "init": 初始化历史数据
                - "update": 更新今日数据
            limit: 限制处理的股票数量（测试用）
            start_date: 历史数据开始日期（仅 init 模式）
        """
        logger.info(f"全 A 股每日数据服务启动，模式：{mode}，并发数：{CONCURRENT_SEMAPHORE}")

        if start_date is None:
            start_date = self.HISTORY_START_DATE

        if mode == "init":
            asyncio.run(self.initialize_historical_data_async(start_date=start_date, limit=limit))
        elif mode == "update":
            asyncio.run(self.update_today_data_async())
        else:
            logger.error(f"未知模式：{mode}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='全 A 股每日成交数据服务')
    parser.add_argument(
        '--mode',
        choices=['init', 'update'],
        default='update',
        help='运行模式：init=初始化历史数据，update=更新今日数据'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='限制处理的股票数量（测试用）'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default='20250701',
        help='历史数据开始日期，格式 YYYYMMDD'
    )

    args = parser.parse_args()

    service = AllSharesDailyService()

    if args.mode == 'init':
        service.run(mode='init', limit=args.limit, start_date=args.start_date)
    else:
        service.run(mode='update')


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )
    main()
