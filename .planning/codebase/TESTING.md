# Testing Patterns

**Analysis Date:** 2026-03-14

## Test Framework

**Python Backend:**
- **Primary:** `unittest` (stdlib) - Class-based tests
- **Secondary:** `pytest` - For newer tests with fixtures
- **Config:** `pyproject.toml` (Black, isort, bandit settings)

**Run Commands:**
```bash
# Run all tests with unittest
python -m unittest discover tests/

# Run specific test file
python -m unittest tests/test_auth.py

# Run with pytest (if installed)
pytest tests/

# Run with coverage
coverage run -m unittest discover tests/
coverage report

# Run single test class
python -m unittest tests.test_stock_code_utils.TestIsCodeLike

# Run single test method
python -m unittest tests.test_stock_code_utils.TestIsCodeLike.test_plain_6_digit
```

**Frontend (apps/dsa-web/):**
- No test framework configured
- Testing relies on manual verification and E2E workflows

## Test File Organization

**Location:**
- Tests directory: `tests/` at project root
- Pattern: Co-located with source in separate directory (not alongside source)

**Naming:**
- Files: `test_*.py` (e.g., `test_auth.py`, `test_formatters.py`, `test_backtest_engine.py`)
- Classes: `*TestCase` for unittest (e.g., `AuthValidationTestCase`)
- Classes: `Test*` for pytest (e.g., `TestIsCodeLike`)
- Methods: `test_*` with descriptive names (e.g., `test_validate_password_empty`)

**Directory Structure:**
```
daily_stock_analysis/
├── src/
│   ├── auth.py
│   ├── config.py
│   └── ...
├── api/
│   └── ...
├── tests/
│   ├── test_auth.py
│   ├── test_config_manager.py
│   ├── test_formatters.py
│   ├── test_stock_code_utils.py
│   └── ...
└── pyproject.toml
```

## Test Structure

**Unittest Pattern (Class-based):**
```python
# -*- coding: utf-8 -*-
"""Unit tests for formatters."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.formatters import chunk_content_by_max_words, TRUNCATION_SUFFIX


class TestChunkContentByMaxWords(unittest.TestCase):
    """Tests for chunk_content_by_max_words."""

    def test_empty_string_returns_single_empty_chunk(self):
        result = chunk_content_by_max_words("", 100)
        self.assertEqual(result, [""])

    def test_short_content_no_separators_returns_single_chunk(self):
        text = "Short message without separators."
        result = chunk_content_by_max_words(text, 100)
        self.assertEqual(result, [text])

    def test_content_with_dash_separator_fits_in_one_chunk(self):
        text = "Part A\n---\nPart B"
        result = chunk_content_by_max_words(text, 500)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], text)

    def test_raises_when_max_words_below_min(self):
        with self.assertRaises(ValueError) as ctx:
            chunk_content_by_max_words("\n---\n###\n**\n##\n\n", MIN_MAX_WORDS)
        self.assertIn(str(MIN_MAX_WORDS), str(ctx.exception))
```

**Pytest Pattern:**
```python
# -*- coding: utf-8 -*-
"""Tests for src/services/stock_code_utils.py"""
import pytest
from src.services.stock_code_utils import is_code_like, normalize_code


class TestIsCodeLike:
    # --- Plain digit codes ---
    def test_plain_6_digit(self):
        assert is_code_like("600519") is True

    def test_plain_5_digit(self):
        assert is_code_like("00700") is True

    def test_4_digit_rejected(self):
        assert is_code_like("6001") is False

    # --- Negative cases ---
    def test_plain_text(self):
        assert is_code_like("贵州茅台") is False

    def test_empty(self):
        assert is_code_like("") is False
```

**Setup/Teardown Pattern:**
```python
class AuthValidationTestCase(unittest.TestCase):
    """Test password validation."""

    def setUp(self) -> None:
        """Reset auth module globals for test isolation."""
        _reset_auth_globals()

    def test_validate_password_empty(self) -> None:
        self.assertIsNotNone(auth._validate_password(""))
        self.assertIsNotNone(auth._validate_password("   "))

    def test_validate_password_valid(self) -> None:
        self.assertIsNone(auth._validate_password("123456"))
```

**Fixture Pattern (pytest):**
```python
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_config():
    """Fixture for mocking config."""
    with patch("src.config.Config") as mock:
        yield mock

def test_manual_mode_uses_configured_agent_skills(mock_config):
    # Test using fixture
    pass
```

## Mocking

**Framework:** `unittest.mock` (stdlib)

**Patterns:**
```python
from unittest.mock import patch, MagicMock

# Patch environment variable check
@patch.object(auth, "_is_auth_enabled_from_env", return_value=True)
@patch.object(auth, "_get_data_dir", return_value=test_data_dir)
def test_auth_enabled_flow(mock_get_dir, mock_enabled):
    auth._auth_enabled = True
    # ... test logic

# Patch time for testing expiry
def test_verify_session_expired(self) -> None:
    def run():
        past = time.time() - 48 * 3600
        with patch.object(auth, "time") as mock_time:
            mock_time.time.return_value = past
            tok = auth.create_session()
        self.assertFalse(auth.verify_session(tok))
    self._patch_env_and_run(test_fn=run)

# Mock class methods
from unittest.mock import MagicMock

mock_instance = MagicMock()
mock_instance.some_method.return_value = {"key": "value"}
```

**What to Mock:**
- External API calls (LLM, data providers)
- File system operations
- Time-dependent operations
- Environment variables
- Database connections

**What NOT to Mock:**
- Pure functions with deterministic output
- Core business logic under test
- Data transformations

## Fixtures and Factories

**Test Data Helpers:**
```python
# tests/test_backtest_engine.py
from dataclasses import dataclass
from datetime import date, timedelta

@dataclass
class Bar:
    date: date
    high: float
    low: float
    close: float

class BacktestEngineTestCase(unittest.TestCase):
    def _bars(self, start: date, closes, highs=None, lows=None):
        """Helper to create test bar data."""
        highs = highs or closes
        lows = lows or closes
        bars = []
        for i, c in enumerate(closes):
            bars.append(Bar(
                date=start + timedelta(days=i + 1),
                high=highs[i],
                low=lows[i],
                close=c
            ))
        return bars

    def test_buy_win_when_up(self):
        cfg = EvaluationConfig(eval_window_days=3, neutral_band_pct=2.0)
        bars = self._bars(
            date(2024, 1, 1),
            [102, 104, 105],
            highs=[103, 105, 106],
            lows=[101, 103, 104]
        )
        res = BacktestEngine.evaluate_single(
            operation_advice="买入",
            analysis_date=date(2024, 1, 1),
            start_price=100,
            forward_bars=bars,
            stop_loss=95,
            take_profit=110,
            config=cfg,
        )
        self.assertEqual(res["eval_status"], "completed")
        self.assertEqual(res["outcome"], "win")
```

**Location:**
- Test helpers defined within test classes as `_private` methods
- No separate fixtures directory (helpers co-located with tests)

## Coverage

**Requirements:** No explicit coverage threshold enforced

**View Coverage:**
```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run -m unittest discover tests/

# Generate report
coverage report -m

# HTML report
coverage html
open htmlcov/index.html
```

## Test Types

**Unit Tests:**
- Scope: Individual functions, classes, methods
- Approach: Isolate unit with mocks for dependencies
- Examples:
  - `test_formatters.py` - String formatting utilities
  - `test_stock_code_utils.py` - Stock code validation
  - `test_auth.py` - Authentication module functions

**Integration Tests:**
- Scope: API endpoints, service interactions
- Approach: Test with minimal mocking
- Examples:
  - `test_auth_api.py` - Auth endpoint integration
  - `test_system_config_api.py` - Config API tests
  - `test_analysis_history.py` - History API tests

**E2E Tests:**
- Framework: Not configured
- Coverage: Manual testing and production monitoring

## Common Patterns

**Parameterized-style Tests (Unittest):**
```python
class TestIsCodeLike(unittest.TestCase):
    # --- Suffix format ---
    def test_suffix_sh(self):
        assert is_code_like("600519.SH") is True

    def test_suffix_sz(self):
        assert is_code_like("000001.SZ") is True

    def test_suffix_lowercase(self):
        assert is_code_like("600519.sh") is True

    # --- Exchange prefix format ---
    def test_prefix_sh_upper(self):
        assert is_code_like("SH600519") is True

    def test_prefix_sh_lower(self):
        assert is_code_like("sh600519") is True
```

**Error Testing:**
```python
def test_chunk_raises_when_max_words_below_min(self):
    """Guard against infinite recursion - should raise ValueError."""
    with self.assertRaises(ValueError) as ctx:
        chunk_content_by_max_words("\n---\n###\n**\n##\n\n", MIN_MAX_WORDS)
    self.assertIn(str(MIN_MAX_WORDS), str(ctx.exception))

def test_parse_failure_returns_hold(self):
    """When JSON parsing fails, should return neutral/hold decision."""
    result = parse_strategy_opinions("invalid json {{{")
    self.assertEqual(result.signal, "hold")
    self.assertIsNone(result.strategy_id)
```

**Async Testing:**
```python
async def test_fetcher_with_logging(self):
    """Test async data fetching with logging verification."""
    fetcher = AkShareFetcher()
    with patch("logging.Logger.info") as mock_log:
        result = await fetcher.fetch_realtime_data("600519")
        mock_log.assert_called()
        self.assertIsNotNone(result)
```

**Skip Decorator:**
```python
import unittest

# Skip if optional dependencies not installed
_AKSHARE_IMPORTS_OK = True
try:
    from data_provider.akshare_fetcher import AkShareFetcher
except ImportError:
    _AKSHARE_IMPORTS_OK = False

@unittest.skipIf(not _AKSHARE_IMPORTS_OK, "akshare fetcher not installed")
class TestAkshareToSinaTxSymbol(unittest.TestCase):
    def test_convert_sh_stock(self):
        # ...
        pass
```

**Test Helper for Isolation:**
```python
def _reset_auth_globals() -> None:
    """Reset auth module globals for test isolation."""
    auth._auth_enabled = None
    auth._session_secret = None
    auth._password_hash_salt = None
    auth._password_hash_stored = None
    auth._rate_limit = {}


class AuthPasswordHashTestCase(unittest.TestCase):
    def setUp(self) -> None:
        _reset_auth_globals()

    def test_verify_password_hash_correct(self) -> None:
        salt = secrets.token_bytes(32)
        pwd = "testpass123"
        derived = hashlib.pbkdf2_hmac(
            "sha256", pwd.encode("utf-8"), salt=salt,
            iterations=auth.PBKDF2_ITERATIONS
        )
        self.assertTrue(auth._verify_password_hash(pwd, salt, derived))
```

## Test Files Inventory

**Core Module Tests:**
- `tests/test_auth.py` - Authentication and session management
- `tests/test_config_manager.py` - Configuration management
- `tests/test_formatters.py` - Text formatting utilities
- `tests/test_storage.py` - Database storage operations

**Feature Tests:**
- `tests/test_backtest_engine.py` - Backtest evaluation logic
- `tests/test_backtest_service.py` - Backtest service layer
- `tests/test_agent_executor.py` - Agent execution pipeline
- `tests/test_multi_agent.py` - Multi-agent orchestration

**Integration Tests:**
- `tests/test_auth_api.py` - Auth REST API
- `tests/test_system_config_api.py` - System config API
- `tests/test_analysis_history.py` - Analysis history API

**Data Provider Tests:**
- `tests/test_fundamental_adapter.py` - Financial data adapter
- `tests/test_us_index_mapping.py` - US index code mapping
- `tests/test_stock_code_utils.py` - Stock code validation
- `tests/test_stock_code_bse.py` - BSE stock code handling

---

*Testing analysis: 2026-03-14*
