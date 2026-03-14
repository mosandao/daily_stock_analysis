# Architecture

**Analysis Date:** 2026-03-14

## Pattern Overview

**Overall:** Multi-Agent System with Layered Architecture

**Key Characteristics:**
- Multi-agent pipeline for stock analysis (Technical → Intel → Risk → Strategy → Decision)
- Event-driven task queue for async analysis
- Strategy pattern for market-specific analysis (A-share vs US stock)
- Repository pattern for data access
- Factory pattern for LLM provider abstraction via LiteLLM

## Layers

**API Layer:**
- Purpose: RESTful API endpoints and middleware
- Location: `api/v1/endpoints/`, `api/middlewares/`
- Contains: Route handlers, request/response schemas, authentication middleware
- Depends on: Services layer
- Used by: Web UI, external clients, bot platforms

**Service Layer:**
- Purpose: Business logic orchestration
- Location: `src/services/`, `src/core/`
- Contains: AnalysisService, TaskQueue, BacktestService, SystemConfigService
- Depends on: Repository layer, Agent layer
- Used by: API endpoints, CLI scheduler, Bot handler

**Agent Layer (Multi-Agent System):**
- Purpose: AI-powered stock analysis via specialized agents
- Location: `src/agent/`, `src/agent/agents/`, `src/agent/tools/`
- Contains: Orchestrator, AgentExecutor, specialized agents (Technical, Intel, Risk, Decision), tool registry
- Depends on: LLM adapter, data fetchers
- Used by: Services layer, bot chat flows

**Data Fetcher Layer:**
- Purpose: Multi-source market data abstraction
- Location: `data_provider/`
- Contains: DataFetcherManager, platform-specific fetchers (AkShare, Tushare, YFinance, etc.)
- Depends on: External APIs
- Used by: Agent tools, analysis pipeline

**Repository Layer:**
- Purpose: Database access abstraction
- Location: `src/repositories/`
- Contains: AnalysisRepository, BacktestRepository, StockRepository
- Depends on: SQLAlchemy ORM in `src/storage.py`
- Used by: Services layer

**Infrastructure Layer:**
- Purpose: Cross-cutting concerns
- Location: `src/config.py`, `src/storage.py`, `src/logging_config.py`, `src/auth.py`
- Contains: Configuration management, database connection, logging setup, authentication
- Used by: All layers

## Data Flow

**Stock Analysis Flow (CLI/Scheduled):**

1. `main.py` parses arguments and creates `StockAnalysisPipeline`
2. Pipeline submits tasks to `TaskQueue` (async mode) or runs synchronously
3. `AnalysisService.analyze_stock()` executes analysis:
   - Fetches realtime quote and historical data via `DataFetcherManager`
   - Runs multi-agent pipeline via `AgentOrchestrator`
   - Agents execute in sequence: Technical → Intel → Risk → Strategy → Decision
   - Each agent uses `ToolRegistry` to fetch data and `LLMToolAdapter` for LLM calls
4. Results persisted via `AnalysisRepository` to SQLite
5. `NotificationService` sends reports to configured channels

**API Analysis Flow:**

```
POST /api/v1/analysis/analyze
    ↓
api/v1/endpoints/analysis.py::trigger_analysis()
    ↓
TaskQueue.submit_task() → AnalysisService.analyze_stock()
    ↓
AgentOrchestrator.run() → AgentExecutor.run() → run_agent_loop()
    ↓
LLMToolAdapter.chat_with_tools() → litellm.completion()
    ↓
Tool execution → DataFetcherManager.*()
    ↓
Decision dashboard JSON → persist → return
```

**Bot Chat Flow:**

```
Bot message (DingTalk/Feishu/Discord)
    ↓
bot/handler.py::handle_message()
    ↓
AgentExecutor.chat() with conversation history
    ↓
Multi-turn ReAct loop with tool calls
    ↓
Streaming response via progress_callback
```

**State Management:**
- Conversation state: `AgentMemory` stores per-session history in SQLite
- Task state: `TaskQueue` maintains in-memory task status with persistence
- Analysis history: `AnalysisHistory` table with query_id indexing
- Configuration: Runtime config via `Config` singleton with hot-reload support

## Key Abstractions

**AgentOrchestrator (`src/agent/orchestrator.py`):**
- Purpose: Coordinates multi-agent pipeline for single stock analysis
- Location: `src/agent/orchestrator.py`
- Pattern: Pipeline/Chain of Responsibility
- Modes: quick (2 stages), standard (3 stages), full (4 stages), strategy (5 stages)

**AgentContext (`src/agent/protocols.py`):**
- Purpose: Shared context passed between agents in pipeline
- Contains: stock_code, stock_name, query_id, data cache, opinions list
- Pattern: Context Object

**ToolRegistry (`src/agent/tools/registry.py`):**
- Purpose: Central registration and discovery of agent tools
- Pattern: Registry + OpenAI tool declaration format
- Tools: get_realtime_quote, get_daily_history, analyze_trend, search_stock_news, etc.

**LLMToolAdapter (`src/agent/llm_adapter.py`):**
- Purpose: Unified tool-calling interface across LLM providers
- Location: `src/agent/llm_adapter.py`
- Pattern: Adapter + Router (via LiteLLM)
- Supports: Gemini, OpenAI, Anthropic, DeepSeek, Qwen, etc.

**DataFetcherManager (`data_provider/__init__.py`):**
- Purpose: Multi-source data fetcher with priority fallback
- Pattern: Chain of Responsibility + Strategy
- Priority: efinance → AkShare → Tushare → Pytdx → Baostock → YFinance

**StockAnalysisPipeline (`src/core/pipeline.py`):**
- Purpose: Main analysis coordinator with concurrency control
- Pattern: Pipeline + Thread Pool Executor
- Features: Per-stock trading day check, delayed market review, context snapshots

## Entry Points

**CLI Entry Point:**
- Location: `main.py`
- Triggers: Direct execution, cron jobs, GitHub Actions
- Responsibilities: Argument parsing, mode selection (analyze/backtest/serve/schedule), signal handling

**API Server:**
- Location: `server.py`, `api/app.py`
- Triggers: uvicorn, `--serve` flag
- Responsibilities: FastAPI app factory, CORS, middleware, static file serving

**Bot Handler:**
- Location: `bot/handler.py`, `bot/dispatcher.py`
- Triggers: Incoming messages from DingTalk/Feishu/Discord
- Responsibilities: Message routing, command parsing, session management

**Scheduled Tasks:**
- Location: `src/scheduler.py`
- Triggers: `schedule` library, GitHub Actions cron
- Responsibilities: Daily execution at configured time, immediate run option

## Error Handling

**Strategy:** Fail-open with graceful degradation

**Patterns:**
- Tool failure: Log error, continue with available data, mark tool as failed in context
- LLM failure: Retry with fallback models (router pattern in LiteLLM), parse partial JSON with json-repair
- Agent failure: Skip agent, proceed to decision with available opinions
- Pipeline failure: Single stock failure doesn't block other stocks (ThreadPoolExecutor isolation)
- API errors: HTTPException with structured error responses, error handler middleware

**Retry Mechanisms:**
- Tenacity for exponential backoff on API calls
- LLM model fallback via LiteLLM router
- Data fetcher priority fallback chain

## Cross-Cutting Concerns

**Logging:** `src/logging_config.py` — structured logging to file + console, per-component loggers
**Validation:** Pydantic schemas in `api/v1/schemas/`, runtime validation in services
**Authentication:** Cookie-based session in `src/auth.py`, middleware in `api/middlewares/auth.py`
**Configuration:** Environment-driven via `.env`, runtime reload via `src/config.py::Config`
**Rate Limiting:** Per-provider token counting via litellm, news_max_age_days filter

---

*Architecture analysis: 2026-03-14*
