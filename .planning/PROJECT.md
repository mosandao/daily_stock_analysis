# A股自选股智能分析系统

## What This Is

A股自选股智能分析系统 — Multi-agent stock analysis system for China A-share market. Users select stocks, agents fetch data, analyze technical/fundamental/sentiment factors, and deliver investment recommendations through multiple channels.

## Core Value

**Accurate, actionable stock analysis that investors can trust.**

If the analysis is wrong, the system has no value. Everything else serves this goal.

## Requirements

### Validated

- ✓ Multi-agent pipeline architecture (Technical → Intel → Risk → Strategy → Decision) — existing
- ✓ Multiple LLM provider support (Gemini, DeepSeek, Anthropic, OpenAI) via LiteLLM — existing
- ✓ Market data integration (efinance, akshare, tushare, pytdx, baostock, yfinance) — existing
- ✓ Multiple notification channels (WeChat, Feishu, DingTalk, Discord, Telegram, Email) — existing
- ✓ Web UI (React 19, FastAPI backend) — existing
- ✓ Desktop app (Electron) — existing
- ✓ CLI modes (analyze, backtest, schedule, market-review) — existing
- ✓ Agent pipeline modes (quick, standard, full, strategy) — existing

### Active

- [ ] Deeper reasoning — Multi-source synthesis (technical + fundamental + sentiment), chain-of-thought analysis, cross-data connections
- [ ] Better LLM usage — Reasoning model integration (DeepSeek R1, Claude thinking), intelligent model selection based on task type, prompt optimization
- [ ] Measurable results — Backtesting accuracy metrics, prediction tracking, analysis quality scoring, feedback loops

### Out of Scope

- Real-time trading execution — regulatory and risk concerns
- Non-China markets — focus on A-share expertise
- Mobile native apps — web-first, Electron desktop sufficient

## Context

**Technical Environment:**
- Python 3.11 backend with FastAPI
- React 19 frontend with TypeScript
- LiteLLM 1.80+ for multi-provider LLM support
- Electron 31 for desktop wrapper

**Agent Architecture:**
- Layered architecture: API → Service → Agent → Data Fetcher → Repository → Infrastructure
- Agent pipeline: TechnicalAgent → IntelAgent → RiskAgent → StrategyAgent → DecisionAgent
- Multiple pipeline modes for different analysis depths

**Current State:**
- System is functional with basic analysis capabilities
- LLM usage is straightforward without reasoning models
- No systematic quality measurement or feedback loops

## Constraints

- **Tech Stack**: Must integrate with existing Python/React/LiteLLM architecture
- **Model Budget**: Use cost-effective models where possible (DeepSeek for reasoning, Haiku for simple tasks)
- **Data Sources**: Leverage existing market data providers, no new paid subscriptions

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Focus on smarter analysis rather than new features | Core value is analysis quality | — Pending |
| Enhance existing agents rather than rebuild | Preserve working pipeline | — Pending |

---
*Last updated: 2026-03-15 after initialization*