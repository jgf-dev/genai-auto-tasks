## [PR-3](https://github.com/jgf-dev/genai-auto-tasks/pull/3) - 2026-09-22

### Summary

Add deterministic unit tests for coin evaluation edge cases that previously had no coverage, and keep the live Gemini benchmark out of the default suite.

### Added

- Pytest `pythonpath` so `src.*` imports collect under `uv run pytest`.
- Unit tests for `CoinIdentity` / `CoinGrade` / `CoinAnalysis` required fields, defaults, and JSON validation in `tests/test_models.py`.
- Analyzer tests for unreadable images, empty Gemini responses, and invalid JSON in `tests/test_analyzer.py`.
- Market tests for broader-search fallback, precious-metal melt queries, base-metal skip, and empty identity fields in `tests/test_market.py`.
- Reporter tests for missing search-result fields and empty comps in `tests/test_reporter.py`.
- Agent CLI tests for missing `GOOGLE_API_KEY`, non-image directories, extension filtering, and report writes in `tests/test_agent.py`.

### Changed

- `tests/test_benchmark_comparison.py` is marked integration and skipped unless `RUN_LIVE_BENCHMARK=1`.
