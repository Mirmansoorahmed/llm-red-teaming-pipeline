"""Phase 0.4 — target allowlist refuses unknown targets (R4)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from lrtp.allowlist import ALLOWED_TARGETS, TargetNotAllowed, check_aca_url, check_target

REPO = Path(__file__).resolve().parents[1]


def _env():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    return env


def test_allowed_targets_pass():
    for name in ALLOWED_TARGETS:
        assert check_target(name) == name


@pytest.mark.parametrize(
    "bad",
    ["https://example.com", "prod-crm", "openai", "huggingface.co", "", "DEMO"],
)
def test_unknown_target_refused(bad):
    with pytest.raises(TargetNotAllowed):
        check_target(bad)


def test_aca_url_host_allowlist():
    assert check_aca_url("http://localhost:8080/v1/labels")
    with pytest.raises(TargetNotAllowed):
        check_aca_url("https://aca.example.com/v1/labels")


def test_cli_refuses_with_nonzero_exit():
    """The CLI must exit non-zero on a refused target (no network call made)."""
    proc = subprocess.run(
        [sys.executable, "-m", "lrtp.cli", "check-target", "https://evil.example"],
        capture_output=True,
        text=True,
        env=_env(),
        cwd=str(REPO),
        check=False,
    )
    assert proc.returncode == 2
    assert "REFUSED" in proc.stderr


def test_cli_allows_known_target():
    proc = subprocess.run(
        [sys.executable, "-m", "lrtp.cli", "check-target", "demo"],
        capture_output=True,
        text=True,
        env=_env(),
        cwd=str(REPO),
        check=False,
    )
    assert proc.returncode == 0
    assert "OK" in proc.stdout
