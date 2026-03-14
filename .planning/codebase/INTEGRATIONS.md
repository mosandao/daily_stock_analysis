# External Integrations

**Analysis Date:** 2026-03-14

## APIs & External Services

**LLM Providers (via LiteLLM):**
- Google Gemini - AI analysis (`GEMINI_API_KEY`, `GEMINI_API_KEYS` for multi-key)
- DeepSeek - Cost-effective alternative (`DEEPSEEK_API_KEY`)
- Anthropic Claude - High-quality reasoning (`ANTHROPIC_API_KEY`)
- OpenAI - GPT models (`OPENAI_API_KEY`, `OPENAI_BASE_URL`)
- AIHubmix - Aggregator platform (`AIHUBMIX_KEY`)
- Custom providers - Via `LLM_CHANNELS` multi-channel config

**Search APIs:**
- Bocha Search - Chinese search optimization (`BOCHA_API_KEYS`)
- Tavily - AI-powered search (`TAVILY_API_KEYS`)
- SerpAPI - Google search results (`SERPAPI_API_KEYS`)
- Brave Search - Privacy-focused (`BRAVE_API_KEYS`)
- SearXNG - Self-hosted meta-search (`SEARXNG_BASE_URLS`)
- MiniMax - Coding Plan Web Search (`MINIMAX_API_KEYS`)

**Market Data Providers:**
- East Money (efinance/akshare) - Primary China A-share data (Priority 0-1)
- Tushare Pro - Premium market data (requires token, 2000+ points for full access)
- Tongdaxin (pytdx) - Real-time quotes from broker servers
- Baostock - Free securities data
- Yahoo Finance - US stocks and fallback (`yfinance`)

## Data Storage

**Databases:**
- SQLite 3 - Primary database (file-based, no server required)
  - Location: `./data/stock_analysis.db` (configurable via `DATABASE_PATH`)
  - Client: SQLAlchemy 2.0 ORM
  - Tables: `stock_daily`, `analysis_history`, `backtest_result`, `backtest_summary`

**File Storage:**
- Local filesystem only
  - Logs: `./logs/`
  - Reports: `./reports/`
  - Data: `./data/`
  - Static assets: `./static/` (built frontend)

**Caching:**
- In-memory caching via Python dicts
- No external cache (Redis/Memcached) detected

## Authentication & Identity

**Auth Provider:**
- Custom session-based authentication for web UI
- Session cookies with configurable expiry (`ADMIN_SESSION_MAX_AGE_HOURS=24`)
- Password reset via CLI: `python -m src.auth reset_password`
- Optional: `ADMIN_AUTH_ENABLED` flag

**Bot Platform Auth:**
- DingTalk: AppKey/AppSecret + signature verification (`bot/platforms/dingtalk.py`)
- Feishu: App ID/Secret with long-connection mode (`bot/platforms/feishu_stream.py`)
- Discord: Bot token or Webhook URL

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry/Datadog integration)
- Local logging only via Python `logging` module

**Logs:**
- Python logging to file (`./logs/`)
- Configurable level: `LOG_LEVEL=INFO/DEBUG/WARNING/ERROR`
- Docker: JSON file driver, 10MB rotation, 3 files max

**Health Checks:**
- `/api/health` endpoint (FastAPI)
- Docker HEALTHCHECK every 30s

## CI/CD & Deployment

**Hosting:**
- Self-hosted (no PaaS dependency)
- Docker container (primary deployment method)
- Can run standalone Python script

**CI Pipeline:**
- GitHub Actions
  - `ci.yml` - PR validation (backend + frontend)
  - `docker-publish.yml` - Docker image to GHCR/DockerHub
  - `desktop-release.yml` - Electron app builds
  - `pr-review.yml` - AI-assisted code review
  - `daily_analysis.yml` - Scheduled analysis job

**CD:**
- Automated releases via `create-release.yml`
- Auto-tagging via `auto-tag.yml`

## Environment Configuration

**Required env vars (minimum):**
- `GEMINI_API_KEY` or `DEEPSEEK_API_KEY` or `ANTHROPIC_API_KEY` - At least one LLM key
- `DATABASE_PATH` - SQLite location (default: `./data/stock_analysis.db`)
- `STOCK_LIST` - Stock codes to analyze (e.g., `600519,300750,002594`)

**Optional but common:**
- `TUSHARE_TOKEN` - For Tushare Pro data
- `SCHEDULE_TIME` - Cron time (e.g., `18:00`)
- Notification channel configs (see below)

**Secrets location:**
- `.env` file (gitignored)
- Docker secrets via `env_file` in docker-compose
- No external secret manager (Vault/AWS Secrets Manager) detected

## Webhooks & Callbacks

**Incoming:**
- DingTalk Stream mode - Real-time bot commands (`DINGTALK_STREAM_ENABLED=true`)
- Feishu long-connection - Bot interactions (`FEISHU_STREAM_ENABLED=true`)
- FastAPI REST endpoints - Web UI and external API (`/api/v1/*`)
- Discord bot events - Via discord.py event handlers

**Outgoing (Notification Channels):**
- WeChat Work (企业微信) - Webhook (`WECHAT_WEBHOOK_URL`)
- Feishu/Lark (飞书) - Webhook (`FEISHU_WEBHOOK_URL`)
- Telegram - Bot API (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`)
- Email - SMTP (QQ/163/Gmail/Outlook) (`EMAIL_SENDER`, `EMAIL_PASSWORD`)
- DingTalk - Custom Webhook (`CUSTOM_WEBHOOK_URLS`)
- Discord - Webhook or Bot API (`DISCORD_WEBHOOK_URL` or `DISCORD_BOT_TOKEN`)
- Pushover - Push notifications (`PUSHOVER_USER_KEY`, `PUSHOVER_API_TOKEN`)
- PushPlus - China push service (`PUSHPLUS_TOKEN`)
- ServerChan3 - WeChat push (`SERVERCHAN3_SENDKEY`)

**Webhook Auto-Detection:**
- DingTalk: Detects `oapi.dingtalk.com` URLs, uses `{"msgtype": "text", "text": {"content": "..."}}` format
- Discord: Detects `discord.com/api/webhooks`, uses `{"content": "..."}` format
- Slack: Detects `hooks.slack.com`, uses `{"text": "..."}` format
- Generic: Falls back to `{"text": "...", "content": "..."}` format

## Bot Platform Integrations

**DingTalk (钉钉):**
- SDK: `dingtalk-stream >= 0.24.3`
- Location: `bot/platforms/dingtalk.py`, `bot/platforms/dingtalk_stream.py`
- Auth: AppKey + AppSecret with HMAC-SHA256 signature
- Commands: `/analyze`, `/ask`, `/chat`, `/batch`, `/market`, `/status`, `/help`

**Feishu/Lark (飞书):**
- SDK: `lark-oapi >= 1.0.0`
- Location: `bot/platforms/feishu_stream.py`
- Auth: App ID + App Secret
- Long-connection mode for real-time interaction

**Discord:**
- SDK: `discord.py >= 2.0.0`
- Location: `bot/platforms/discord.py`, `src/notification_sender/discord_sender.py`
- Two modes: Webhook (simpler) or Bot API (full permissions)

---

*Integration audit: 2026-03-14*
