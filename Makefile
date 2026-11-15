# LLM Red-Teaming Pipeline — Makefile
# Default profile is `oss`: standard-library only, no cloud, no network, no GPU.
# Optional runner extras (garak/AgentDojo/PyRIT/promptfoo) and Azure hybrid
# adapters are NOT required for any target below.

PYTHON ?= python3
PROFILE ?= oss
# The harness is importable from ./src without installation (stdlib-only core).
export PYTHONPATH := src

.PHONY: help test lint demo gate report smoke clean

help:
	@echo "Targets:"
	@echo "  make test     - run the test suite (pytest), stdlib-only harness"
	@echo "  make lint     - run ruff if present (optional; no-op otherwise)"
	@echo "  make demo     - run the full suite vs vulnerable AND defended; write a run file"
	@echo "  make gate     - run the regression gate vs committed baseline"
	@echo "  make report   - regenerate docs/REPORT-DATA.md from the latest committed run (no PDF)"
	@echo "  make smoke    - optional-adapter smoke check (skips cleanly with no extras)"

test:
	$(PYTHON) -m pytest

lint:
	@if command -v ruff >/dev/null 2>&1; then ruff check src tests; \
	else echo "ruff not installed; skipping lint (optional)"; fi

# Optional adapter smoke check. Skips every adapter whose extra is absent and
# exits 0, so it is safe to run in the default oss environment.
smoke:
	$(PYTHON) -m lrtp.adapters.smoke

# Run the full suite against vulnerable AND defended on the oss scripted backend
# and write a timestamped JSON run file to eval/results/.
demo:
	$(PYTHON) -m lrtp.demo

gate:
	$(PYTHON) -m lrtp.cli gate --baseline eval/results/baseline.json

# Regenerate docs/REPORT-DATA.md from the latest committed run file (no PDF).
report:
	$(PYTHON) -m lrtp.report_cli --results eval/results --out docs/REPORT-DATA.md

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
