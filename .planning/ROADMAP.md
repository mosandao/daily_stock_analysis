# Roadmap: A股自选股智能分析系统增强

## Overview

This roadmap transforms the existing multi-agent stock analysis system from basic analysis to trustworthy, measurable analysis. We enhance reasoning depth, optimize LLM usage, and build quality measurement infrastructure. The journey progresses from smarter analysis core (Phase 1) to quality infrastructure (Phase 2) to user-visible metrics and feedback loops (Phase 3).

## Phases

- [ ] **Phase 1: Reasoning Enhancement** - Multi-source synthesis, chain-of-thought, confidence scoring, reasoning model integration
- [ ] **Phase 2: Quality Infrastructure** - Cross-data connections, prompt optimization, caching, backtesting, calibration
- [ ] **Phase 3: Quality Dashboard & Feedback** - Quality scoring, performance dashboard, improvement feedback loop

## Phase Details

### Phase 1: Reasoning Enhancement
**Goal**: Users receive analysis that shows reasoning steps with confidence scores, powered by reasoning models.
**Depends on**: Nothing (first phase)
**Requirements**: DR-01, DR-02, DR-04, LLM-01, LLM-02
**Success Criteria** (what must be TRUE):
  1. User can see technical + fundamental + sentiment data synthesized in analysis output
  2. User can view the reasoning steps behind each analysis conclusion
  3. Each analysis includes a confidence score with supporting evidence
  4. System uses reasoning models (DeepSeek R1 or Claude thinking) for complex analysis tasks
  5. Tasks are automatically routed to appropriate models based on complexity
**Plans**: TBD

Plans:
- [ ] 01-01: Multi-source data synthesis
- [ ] 01-02: Chain-of-thought reasoning output
- [ ] 01-03: Confidence scoring mechanism
- [ ] 01-04: Reasoning model integration
- [ ] 01-05: Intelligent model selection

### Phase 2: Quality Infrastructure
**Goal**: Users benefit from cross-data validation and measurable accuracy tracking.
**Depends on**: Phase 1
**Requirements**: DR-03, LLM-03, LLM-04, MR-01, MR-02
**Success Criteria** (what must be TRUE):
  1. Analysis identifies and reports correlations and contradictions between data sources
  2. Prompts are optimized for each agent's specific task
  3. Similar queries return cached results (faster, more consistent)
  4. System tracks predictions vs actual outcomes for accuracy measurement
  5. Confidence calibration shows whether high-confidence predictions are actually more accurate
**Plans**: TBD

Plans:
- [ ] 02-01: Cross-data connection detection
- [ ] 02-02: Prompt optimization per agent
- [ ] 02-03: Response caching system
- [ ] 02-04: Backtesting accuracy tracking
- [ ] 02-05: Confidence calibration metrics

### Phase 3: Quality Dashboard & Feedback
**Goal**: Users can view quality metrics and the system improves over time from feedback.
**Depends on**: Phase 2
**Requirements**: MR-03, MR-04, MR-05
**Success Criteria** (what must be TRUE):
  1. Analysis quality is scored based on historical outcomes and user feedback
  2. User can view performance metrics (accuracy, calibration, quality scores) in dashboard
  3. Historical performance data influences future analysis quality
**Plans**: TBD

Plans:
- [ ] 03-01: Analysis quality scoring
- [ ] 03-02: Performance dashboard UI
- [ ] 03-03: Feedback loop implementation

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Reasoning Enhancement | 0/5 | Not started | - |
| 2. Quality Infrastructure | 0/5 | Not started | - |
| 3. Quality Dashboard & Feedback | 0/3 | Not started | - |