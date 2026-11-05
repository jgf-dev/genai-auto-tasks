## [PR-4](https://github.com/jgf-dev/genai-auto-tasks/pull/4) - 2026-09-23

### Summary

Add hermetic unit tests for mint-mark search queries, listing comps with missing fields, CLI image filtering, and BIN price parsing, and keep the live Gemini benchmark out of the default suite.

### Added

- Pytest `pythonpath` so `src.*` imports collect under `uv run pytest`.
- Market tests for mint-mark/variety query construction and silver broader-search plus melt/spot follow-up in `tests/test_market.py`.
- Analyzer tests for empty image lists, unreadable files, empty Gemini responses, and JSON `response_schema` configuration in `tests/test_analyzer.py`.
- Agent CLI tests for missing `GOOGLE_API_KEY`, png/jpeg vs gif filtering, and `evaluation_report.md` writes in `tests/test_agent.py`.
- Price-parser tests for labels, comma amounts, and missing prices in `tests/test_price_parsing.py`.
- Reporter tests for missing search-result title/href placeholders in `tests/test_reporter.py`.

### Changed

- `tests/test_benchmark_comparison.py` is marked integration and skipped unless `RUN_LIVE_BENCHMARK=1`.
