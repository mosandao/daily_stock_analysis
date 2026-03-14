# Technology Stack

**Analysis Date:** 2026-03-14

## Languages

**Primary:**
- Python 3.11 - Backend, data processing, AI analysis, notification services
- TypeScript 5.9 - Frontend web application (dsa-web)
- JavaScript (ES Modules) - Electron desktop app (dsa-desktop)

**Secondary:**
- SQL (SQLite) - Local database queries
- YAML - Configuration files (LiteLLM, strategies)

## Runtime

**Environment:**
- Python 3.11-3.12 (Debian Bookworm base)
- Node.js 20.x - Frontend build and Electron

**Package Manager:**
- pip - Python dependencies
- npm - Node.js dependencies
- Lockfiles: `requirements.txt` (Python), `package-lock.json` (Node) - both present

## Frameworks

**Core Backend:**
- FastAPI 0.109+ - REST API and web server (`api/app.py`)
- Uvicorn 0.27+ - ASGI server
- SQLAlchemy 2.0+ - ORM and database layer (`src/storage.py`)

**Frontend:**
- React 19.2 - UI framework (`apps/dsa-web/src/`)
- Vite 7.2 - Build tool and dev server
- TypeScript - Type-safe development
- Tailwind CSS 4.1 - Styling
- Zustand 5.0 - State management
- React Router 7.13 - Client-side routing
- Axios 1.13 - HTTP client

**Desktop:**
- Electron 31.4 - Cross-platform desktop wrapper (`apps/dsa-desktop/`)
- electron-builder 24.13 - Desktop app packaging

**Testing:**
- flake8 - Python linting (CI)
- pytest - Python testing
- ESLint 9.39 - TypeScript linting

**Build/Dev:**
- black - Python code formatting (`pyproject.toml`)
- isort - Python import sorting
- bandit - Python security linting

## Key Dependencies

**AI/LLM:**
- litellm 1.80+ - Unified LLM router (Anthropic/OpenAI/Google/DeepSeek) (`src/agent/llm_adapter.py`)
- tiktoken 0.8-0.12 - Token counting for LLM calls
- openai 1.0+ - OpenAI SDK (transitive via litellm)

**Data Sources (China A-Share focused):**
- efinance 0.5.5+ - Priority 0: East Money data (`data_provider/efinance_fetcher.py`)
- akshare 1.12+ - Priority 1: East Money crawler (`data_provider/akshare_fetcher.py`)
- tushare 1.4+ - Priority 2: Tushare Pro API (`data_provider/tushare_fetcher.py`)
- pytdx 1.72 - Priority 2: Tongdaxin market data (`data_provider/pytdx_fetcher.py`)
- baostock 0.8+ - Priority 3: Securities data (`data_provider/baostock_fetcher.py`)
- yfinance 0.2+ - Priority 4: Yahoo Finance fallback (`data_provider/yfinance_fetcher.py`)

**Data Processing:**
- pandas 2.0+ - Data analysis and manipulation
- numpy 1.24+ - Numerical computation
- openpyxl 3.1+ - Excel file parsing

**Notification/IM Integration:**
- lark-oapi 1.0+ - Feishu/Lark bot SDK
- dingtalk-stream 0.24.3+ - DingTalk Stream SDK
- discord.py 2.0+ - Discord bot

**Search:**
- tavily-python 0.3+ - Tavily Search API
- google-search-results 2.4+ - SerpAPI
- newspaper3k 0.2.8 - Web article extraction

**Utilities:**
- python-dotenv 1.0+ - Environment configuration
- tenacity 8.2+ - Retry logic with exponential backoff
- schedule 1.2+ - Cron-like task scheduling
- exchange-calendars 4.5+ - Trading calendar (CN/US/HK markets)
- PyYAML 6.0+ - YAML parsing
- jinja2 3.1+ - Report template rendering
- markdown2 2.4+ - Markdown to HTML
- imgkit 1.2+ - Markdown to image (requires wkhtmltopdf)

## Configuration

**Environment:**
- `.env` file-based configuration (`.env.example` provided)
- `python-dotenv` for loading
- 50+ configurable variables for AI, notifications, data sources, scheduling

**Key Config Files:**
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Python tooling config (black, isort, bandit)
- `setup.cfg` - Additional Python settings
- `apps/dsa-web/tsconfig.json` - TypeScript compiler options
- `apps/dsa-web/vite.config.ts` - Vite build configuration
- `apps/dsa-web/tailwind.config.js` - Tailwind CSS config
- `litellm_config.example.yaml` - LiteLLM router configuration

**Build:**
- Multi-stage Docker build (Node for frontend, Python for backend)
- `docker/Dockerfile` - Production container image
- `docker/docker-compose.yml` - Container orchestration

## Platform Requirements

**Development:**
- Python 3.11-3.12
- Node.js 20.x
- wkhtmltopdf - Markdown to image conversion
- pip and npm package managers

**Production:**
- Docker container deployment (recommended)
- Base image: `python:3.11-slim-bookworm`
- Memory: 512MB limit (configurable)
- Persistent volumes: `/app/data`, `/app/logs`, `/app/reports`

**CI/CD:**
- GitHub Actions workflows (`.github/workflows/`)
- Multi-job pipeline: backend-gate, docker-build, web-gate
- Automated PR review, release tagging, Docker publishing

---

*Stack analysis: 2026-03-14*
