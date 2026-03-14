# Coding Conventions

**Analysis Date:** 2026-03-14

## Naming Patterns

**Files:**
- TypeScript components: `PascalCase.tsx` (e.g., `Button.tsx`, `ApiErrorAlert.tsx`)
- TypeScript utilities: `camelCase.ts` (e.g., `format.ts`, `validation.ts`, `constants.ts`)
- TypeScript types: `camelCase.ts` (e.g., `analysis.ts`, `backtest.ts`)
- Python modules: `snake_case.py` (e.g., `stock_code_utils.py`, `config_manager.py`)
- Test files: `test_*.py` (e.g., `test_auth.py`, `test_formatters.py`)
- API schemas: `snake_case.py` (e.g., `analysis.py`, `common.py`)

**Functions:**
- TypeScript: `camelCase` (e.g., `validateStockCode`, `formatDateTime`, `getTodayInShanghai`)
- Python: `snake_case` (e.g., `is_code_like`, `normalize_code`, `parse_env_bool`)
- React hooks: `usePascalCase` (e.g., `useAuth`, `useAnalysisStore`, `useTaskStream`)

**Variables:**
- TypeScript: `camelCase` for local variables, `PascalCase` for types/interfaces
- Python: `snake_case` for all variables
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`, `PBKDF2_ITERATIONS`)

**Types/Interfaces:**
- TypeScript: `PascalCase` (e.g., `AnalysisRequest`, `ParsedApiError`, `AuthContextValue`)
- Python dataclasses: `PascalCase` (e.g., `ConfigIssue`, `EvaluationConfig`)
- Pydantic models: `PascalCase` (e.g., `AnalyzeRequest`, `TaskStatus`)

## Code Style

**TypeScript (apps/dsa-web/):**
```typescript
// Function with explicit return type inference
export const validateStockCode = (value: string): ValidationResult => {
  const normalized = value.trim().toUpperCase();
  // ...
};

// Interface definition
interface ApiErrorAlertProps {
  error: ParsedApiError;
  className?: string;
  actionLabel?: string;
  onAction?: () => void;
}

// React component with type-safe props
export const ApiErrorAlert: React.FC<ApiErrorAlertProps> = ({
  error,
  className = '',
  actionLabel,
  onAction,
}) => {
  return <div className={`... ${className}`} role="alert">...</div>;
};
```

**Python (src/, api/, tests/):**
```python
# -*- coding: utf-8 -*-
"""
Module docstring describing purpose and responsibilities.
"""

from typing import Optional, Tuple

def parse_env_bool(value: Optional[str], default: bool = False) -> bool:
    """Parse common truthy/falsey environment-style values.

    Args:
        value: Environment variable value
        default: Default value if None or empty

    Returns:
        Boolean result
    """
    if value is None:
        return default
    return value.strip().lower() not in _FALSEY_ENV_VALUES
```

**Formatting Tools:**
- TypeScript: ESLint 9.x with typescript-eslint
  - Config: `apps/dsa-web/eslint.config.js`
  - Rules: react-hooks, react-refresh, browser globals
- Python: Black formatter
  - Line length: 120 characters
  - Target version: Python 3.10, 3.11, 3.12
  - Config: `pyproject.toml`
- Python imports: isort with black profile
  - Skip: `.git`, `__pycache__`, `.env`, `venv`, `.venv`

## Import Organization

**TypeScript Import Order:**
1. React and external libraries
2. Type imports (using `import type`)
3. API clients
4. Local utilities
5. Components
6. Stores/Hooks
7. Types

```typescript
import type React from 'react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { getParsedApiError } from '../api/error';
import type { HistoryItem, AnalysisReport } from '../types/analysis';
import { historyApi } from '../api/history';
import { validateStockCode } from '../utils/validation';
import { ReportSummary } from '../components/report';
import { useAnalysisStore } from '../stores/analysisStore';
```

**Python Import Order:**
1. Future imports (`from __future__ import annotations`)
2. Standard library (alphabetical)
3. Third-party packages (alphabetical)
4. Local modules (alphabetical)

```python
from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path
from typing import Optional, Tuple

from dotenv import dotenv_values
from fastapi import FastAPI, Request

from src.config import setup_env
```

## Error Handling

**TypeScript - Structured Error Parsing:**
```typescript
// Custom error category system (apps/dsa-web/src/api/error.ts)
export type ApiErrorCategory =
  | 'agent_disabled'
  | 'missing_params'
  | 'llm_not_configured'
  | 'upstream_timeout'
  | 'local_connection_failed'
  | 'http_error'
  | 'unknown';

export interface ParsedApiError {
  title: string;
  message: string;
  rawMessage: string;
  status?: number;
  category: ApiErrorCategory;
}

// Error parsing with category detection
export function parseApiError(error: unknown): ParsedApiError {
  const response = getResponse(error);
  const matchText = buildMatchText([...]);

  if (includesAny(matchText, ['agent_mode is not enabled'])) {
    return createParsedApiError({
      title: 'Agent 模式未开启',
      message: '当前功能依赖 Agent 模式，请先开启后再重试。',
      category: 'agent_disabled',
    });
  }
  // ... more categories
}

// Axios interceptor for automatic error attachment
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    attachParsedApiError(error);
    return Promise.reject(error);
  }
);
```

**Python - Exception Handling with Logging:**
```python
import logging

logger = logging.getLogger(__name__)

def set_initial_password(password: str) -> Optional[str]:
    """Set initial password. Returns error message or None on success."""
    err = _validate_password(password)
    if err:
        return err

    try:
        tmp_path = cred_path.with_suffix(".tmp")
        tmp_path.write_text(content)
        tmp_path.chmod(0o600)
        tmp_path.replace(cred_path)
        return None
    except OSError as e:
        logger.error("Failed to write credential file: %s", e)
        return "密码保存失败"

# Custom exception for specific cases
class DuplicateTaskError(Exception):
    """Raised when a duplicate analysis task is submitted."""
    def __init__(self, stock_code: str, existing_task_id: str):
        self.stock_code = stock_code
        self.existing_task_id = existing_task_id
```

## Logging

**TypeScript:**
- Framework: `console` methods
- Pattern: Use `console.error()` for errors, `console.warn()` for warnings, `console.log()` for debug
```typescript
console.error('Failed to fetch history:', err);
console.warn('SSE connection disconnected, reconnecting...');
```

**Python:**
- Framework: `logging` module from stdlib
- Pattern: Module-level logger with `__name__`
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Session secret rotated successfully")
logger.warning("Invalid .session_secret length, regenerating")
logger.error("Failed to write credential file: %s", e)
```

## Comments

**TypeScript:**
- JSDoc for exported functions and complex logic
- Inline comments for non-obvious behavior
- Component props documented via interface

```typescript
/**
 * Returns the date N days ago as YYYY-MM-DD in Asia/Shanghai timezone.
 * Consistent with getTodayInShanghai() so both ends of the date range
 * are expressed in the same timezone as the backend.
 */
export const getRecentStartDate = (days: number): string => {
  // ...
};

// Used to track the current analysis request to avoid race conditions
const analysisRequestIdRef = useRef<number>(0);
```

**Python:**
- Module docstrings at file top with `"""` triple quotes
- Function docstrings with Args/Returns sections
- UTF-8 coding declaration: `# -*- coding: utf-8 -*-`
- Inline comments for complex logic

```python
# -*- coding: utf-8 -*-
"""
===================================
A 股自选股智能分析系统 - 配置管理模块
===================================

职责：
1. 使用单例模式管理全局配置
2. 从 .env 文件加载敏感配置
3. 提供类型安全的配置访问接口
"""

def _parse_password_hash(value: str) -> Optional[Tuple[bytes, bytes]]:
    """Parse salt_b64:hash_b64. Returns (salt, hash) or None."""
```

## Function Design

**Size:**
- TypeScript: Functions typically 20-60 lines; components can be larger (HomePage.tsx ~570 lines)
- Python: Functions typically 20-80 lines; complex functions split into helpers

**Parameters:**
- TypeScript: Use interface/type for complex objects with 3+ parameters
- Python: Use dataclasses or typed dictionaries for grouped parameters

**Return Values:**
- TypeScript: Explicit return type annotations for exported functions
- Python: Type hints with `-> ReturnType`

## Module Design

**Exports:**
- TypeScript: Named exports for utilities, default export for main components
- Python: Explicit `__all__` in package `__init__.py` files

**Barrel Files:**
- TypeScript: Index files re-export from subdirectories
```typescript
// apps/dsa-web/src/components/common/index.ts
export { ApiErrorAlert } from './ApiErrorAlert';
export { Badge } from './Badge';
export { Button } from './Button';
// ...
```

## React Patterns

**Component Structure:**
```typescript
const HomePage: React.FC = () => {
  // 1. State declarations
  const [stockCode, setStockCode] = useState('');

  // 2. Refs for mutable state
  const analysisRequestIdRef = useRef<number>(0);

  // 3. Callbacks (useCallback for stability)
  const updateTask = useCallback((updatedTask: TaskInfo) => {
    // ...
  }, []);

  // 4. Effects
  useEffect(() => {
    fetchHistory(true);
  }, []);

  // 5. Event handlers
  const handleAnalyze = async () => {
    // ...
  };

  // 6. Render
  return <div>...</div>;
};
```

**State Management:**
- Zustand for global state (stores/*.ts)
- React Context for cross-component state (AuthContext)
- Local state for component-specific data

```typescript
// Zustand store pattern (src/stores/analysisStore.ts)
export const useAnalysisStore = create<AnalysisState>((set) => ({
  isLoading: false,
  result: null,
  error: null,

  setLoading: (loading) => set({ isLoading: loading }),
  setResult: (result) => set({ result, error: null }),
  // ...
}));
```

---

*Convention analysis: 2026-03-14*
