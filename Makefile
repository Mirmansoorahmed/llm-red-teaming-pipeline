# LLM Red-Teaming Pipeline — Makefile
# Default profile is `oss`: standard-library only, no cloud, no network, no GPU.
# Optional runner extras (garak/AgentDojo/PyRIT/promptfoo) and Azure hybrid
# adapters are NOT required for any target below.

PYTHON ?= python3
PROFILE ?= oss

.PHONY: help test lint demo gate report clean

help:
	@echo "Targets:"
	@echo "  make test     - run the test suite (pytest), stdlib-only harness"
	@echo "  make lint     - run ruff if present (optional; no-op otherwise)"
	@echo "  make demo     - run the oss demo script (Phase 8; placeholder until then)"
	@echo "  make gate     - run the regression gate vs committed baseline (Phase 7)"
	@echo "  make report   - build findings report + risk-memo PDF (Phase 8)"

test:
	$(PYTHON) -m pytest

lint:
	@if command -v ruff >/dev/null 2>&1; then ruff check src tests; \
	else echo "ruff not installed; skipping lint (optional)"; fi

# Phases 7/8 are not implemented yet; these fail loudly rather than fake output.
demo:
	@echo "make demo is implemented in Phase 8 (oss). Not available yet." && exit 1

gate:
	@echo "make gate is implemented in Phase 7. Not available yet." && exit 1

report:
	@echo "make report is implemented in Phase 8. Not available yet." && exit 1

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
