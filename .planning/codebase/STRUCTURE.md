# Codebase Structure

**Analysis Date:** 2026-03-14

## Directory Layout

```
daily_stock_analysis/
├── main.py                     # CLI entry point, scheduler
├── server.py                   # API server entry point
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata
├── .env                        # Environment configuration (not committed)
├── .github/workflows/          # GitHub Actions CI/CD
├── api/                        # FastAPI REST API
│   ├── app.py                  # FastAPI application factory
│   ├── deps.py                 # Dependency injection
│   ├── middlewares/            # Auth, error handling
│   └── v1/                     # API v1
│       ├── router.py           # v1 router aggregation
│       ├── endpoints/          # Route handlers
│       └── schemas/            # Pydantic request/response models
├── src/                        # Core application code
│   ├── agent/                  # Multi-agent AI system
│   │   ├── agents/             # Specialized agents (technical, intel, risk, decision)
│   │   ├── tools/              # Tool definitions and registry
│   │   ├── strategies/         # Strategy agents
│   │   ├── orchestrator.py     # Multi-agent pipeline coordinator
│   │   ├── executor.py         # ReAct loop executor
│   │   ├── runner.py           # Shared agent loop implementation
│   │   ├── llm_adapter.py      # LLM tool-calling adapter
│   │   └── protocols.py        # Agent context/opinion types
│   ├── core/                   # Core business logic
│   │   ├── pipeline.py         # Stock analysis pipeline
│   │   ├── market_review.py    # Market overview analysis
│   │   ├── trading_calendar.py # Market holiday checking
│   │   └── backtest_engine.py  # Backtesting engine
│   ├── services/               # Business services
│   ├── repositories/           # Data access layer
│   ├── data/                   # Data utilities
│   ├── schemas/                # Internal data schemas
│   ├── utils/                  # Shared utilities
│   ├── config.py               # Configuration management
│   ├── storage.py              # Database ORM and connection
│   ├── analyzer.py             # Legacy LLM analyzer (GeminiAnalyzer)
│   ├── stock_analyzer.py       # Trend analysis engine
│   ├── search_service.py       # News search aggregation
│   ├── notification.py         # Multi-channel notification
│   └── logging_config.py       # Logging setup
├── data_provider/              # Market data fetchers
│   ├── base.py                 # Base fetcher class
│   ├── akshare_fetcher.py      # AkShare data source
│   ├── tushare_fetcher.py      # Tushare Pro API
│   ├── yfinance_fetcher.py     # Yahoo Finance (US stocks)
│   ├── efinance_fetcher.py     # East Money data
│   └── realtime_types.py       # Realtime data types
├── bot/                        # Chat bot platforms
│   ├── handler.py              # Message handler
│   ├── dispatcher.py           # Command dispatcher
│   ├── commands/               # Command implementations
│   └── platforms/              # Platform adapters (DingTalk, Feishu, Discord)
├── apps/                       # Frontend applications
│   ├── dsa-web/                # React web UI
│   │   ├── src/
│   │   │   ├── api/            # API client
│   │   │   ├── components/     # React components
│   │   │   ├── pages/          # Page components
│   │   │   ├── hooks/          # React hooks
│   │   │   ├── stores/         # Zustand stores
│   │   │   ├── contexts/       # React contexts
│   │   │   ├── types/          # TypeScript types
│   │   │   └── utils/          # Utilities
│   │   └── dist/               # Built static assets (generated)
│   └── dsa-desktop/            # Electron desktop app
├── strategies/                 # Trading strategy definitions
├── docs/                       # Documentation
├── templates/                  # Jinja2 templates
├── scripts/                    # Utility scripts
└── tests/                      # Test suite
```

## Directory Purposes

**`api/`:**
- Purpose: RESTful API layer for web UI and external integration
- Contains: FastAPI routers, endpoint handlers, middleware, Pydantic schemas
- Key files: `api/app.py` (app factory), `api/v1/router.py` (routing), `api/v1/endpoints/analysis.py` (analysis endpoint)

**`src/agent/`:**
- Purpose: Multi-agent AI analysis system
- Contains: Agent base class, specialized agents, tool registry, orchestrator, LLM adapter
- Key files: `src/agent/orchestrator.py`, `src/agent/executor.py`, `src/agent/agents/base_agent.py`

**`src/core/`:**
- Purpose: Core business logic and pipeline orchestration
- Contains: Analysis pipeline, market review, trading calendar, backtest engine
- Key files: `src/core/pipeline.py` (main coordinator), `src/core/market_review.py`

**`src/services/`:**
- Purpose: Business service layer
- Contains: AnalysisService, TaskQueue, BacktestService, SystemConfigService
- Key files: `src/services/analysis_service.py`, `src/services/task_queue.py`

**`src/repositories/`:**
- Purpose: Data access layer (repository pattern)
- Contains: CRUD operations for analysis history, backtest results, stocks
- Key files: `src/repositories/analysis_repo.py`

**`data_provider/`:**
- Purpose: Multi-source market data abstraction
- Contains: Platform-specific data fetchers with priority fallback
- Key files: `data_provider/base.py`, `data_provider/__init__.py` (manager)

**`bot/`:**
- Purpose: Chat bot platform integrations
- Contains: Message handler, command parsers, platform adapters
- Key files: `bot/handler.py`, `bot/platforms/dingtalk_stream.py`

**`apps/dsa-web/src/`:**
- Purpose: React-based web management UI
- Contains: Components, pages, API client, state management
- Key files: `apps/dsa-web/src/App.tsx`, `apps/dsa-web/src/api/analysis.ts`

## Key File Locations

**Entry Points:**
- `main.py`: CLI entry, scheduler, mode selection (analyze/backtest/serve/schedule)
- `server.py`: API server bootstrap (uvicorn entry point)
- `api/app.py`: FastAPI application factory

**Configuration:**
- `src/config.py`: Configuration singleton, environment variable parsing, stock list management
- `.env`: Runtime configuration (not committed)

**Core Logic:**
- `src/core/pipeline.py` (1370 lines): Main analysis pipeline with thread pool
- `src/agent/orchestrator.py` (1361 lines): Multi-agent coordinator
- `src/analyzer.py`: Legacy AI analyzer with LiteLLM integration
- `src/stock_analyzer.py`: Technical trend analyzer

**Data Layer:**
- `src/storage.py`: SQLAlchemy ORM models, database connection singleton
- `data_provider/__init__.py`: DataFetcherManager with priority chain

**API:**
- `api/v1/endpoints/analysis.py`: POST /analyze endpoint, SSE streaming
- `api/v1/endpoints/agent.py`: Agent chat endpoint
- `api/v1/endpoints/history.py`: History CRUD endpoints

**Testing:**
- `tests/`: Test suite (unit and integration tests)

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `analysis_service.py`, `data_tools.py`)
- TypeScript/React: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- Schemas: `*_schema.py` (e.g., `report_schema.py`) or Pydantic in `schemas/`

**Classes:**
- Services: `*Service` (e.g., `AnalysisService`, `BacktestService`)
- Agents: `*Agent` (e.g., `TechnicalAgent`, `DecisionAgent`)
- Fetchers: `*Fetcher` (e.g., `AkShareFetcher`, `YFinanceFetcher`)
- Repositories: `*Repository` (e.g., `AnalysisRepository`)

**Functions:**
- snake_case, verb-first for actions (e.g., `analyze_stock`, `get_realtime_quote`)
- Predicates: `is_*`, `has_*`, `can_*` (e.g., `is_market_open`, `is_auth_enabled`)

## Where to Add New Code

**New Feature (Analysis):**
- Primary code: `src/services/` for business logic, `src/agent/tools/` for new agent tools
- Tests: `tests/test_*.py`
- API endpoint: `api/v1/endpoints/`

**New Data Source:**
- Implementation: `data_provider/*_fetcher.py` (extend `DataFetcher` base class)
- Register in: `data_provider/__init__.py::DataFetcherManager`

**New Agent:**
- Implementation: `src/agent/agents/*_agent.py` (extend `BaseAgent`)
- Register in: `src/agent/orchestrator.py` pipeline
- Tools (if needed): `src/agent/tools/*_tools.py`

**New Notification Channel:**
- Implementation: `src/notification_sender/*_sender.py` (extend base)
- Register in: `src/notification.py::NotificationService`

**Utilities:**
- Shared helpers: `src/utils/`
- Data processing: `src/utils/data_processing.py`

**New API Route:**
- Endpoint: `api/v1/endpoints/*.py`
- Schema: `api/v1/schemas/*.py`
- Router: `api/v1/router.py` (include in aggregation)

## Special Directories

**`apps/dsa-web/dist/`:**
- Purpose: Built React frontend static assets
- Generated: Yes (via `npm run build`)
- Committed: No (served by FastAPI in production)

**`logs/`:**
- Purpose: Application log files
- Generated: Yes (per `log_dir` config)
- Committed: No (in `.gitignore`)

**`data/`:**
- Purpose: Local cache, temporary data files
- Generated: Yes
- Committed: No

**`strategies/`:**
- Purpose: Trading strategy definitions (blueprint pattern)
- Generated: No
- Committed: Yes

**`.github/workflows/`:**
- Purpose: GitHub Actions CI/CD pipelines
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-03-14*
