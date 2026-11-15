"""Finding record model, provenance, and redaction (requirements.md R2.5, R6).

A finding is produced per scenario x target x profile x runner. Each record
carries provenance (git SHA + timestamp + runner versions + model backend) so
every number in the README / report traces to a committed run. Secrets and raw
personal fields are redacted before a record is persisted (C8).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lrtp.schema import validate

_FINDING_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "finding.schema.json"

VERDICTS = ("success", "blocked", "routed_to_review", "error", "skipped")


def args_hash(tool_name: str, args: dict[str, Any]) -> str:
    """Stable hash of an exact tool name + arguments (used for approval binding)."""
    payload = json.dumps({"tool": tool_name, "args": args}, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git_sha(repo: str | Path | None = None) -> str:
    """Return the current git SHA, or 'unknown' when not in a repo."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(repo) if repo else None,
            check=True,
        )
        return out.stdout.strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Redaction: secret-like tokens and raw personal fields. These patterns are
# deliberately broad; a missed secret is worse than an over-redaction.
_SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwort)\b\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9]{8,}"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # email addresses
    re.compile(r"\b(?:\+?\d[\d ()/-]{7,}\d)\b"),  # phone-like numbers
]
_REDACTED = "[REDACTED]"


def redact(text: str) -> str:
    """Remove secret-like tokens and raw personal fields from free text."""
    if not text:
        return text
    out = text
    for pat in _SECRET_PATTERNS:
        out = pat.sub(_REDACTED, out)
    return out


@dataclass
class ToolCall:
    name: str
    args_hash: str
    authorised: bool
    approved: bool
    binding_ok: bool


@dataclass
class DataAccess:
    resource: str
    authorised: bool


@dataclass
class Provenance:
    git_sha: str
    timestamp: str
    runner_versions: dict[str, str]
    model_backend: str


@dataclass
class Finding:
    scenario_id: str
    suite: str
    language: str
    target: str
    profile: str
    runner: str
    verdict: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    data_access: list[DataAccess] = field(default_factory=list)
    judges: dict[str, Any] = field(default_factory=dict)
    mappings: dict[str, Any] = field(default_factory=dict)
    provenance: Provenance | None = None
    text_excerpt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.text_excerpt is not None:
            d["text_excerpt"] = redact(self.text_excerpt)
        else:
            d.pop("text_excerpt", None)
        if d.get("provenance") is None:
            d.pop("provenance", None)
        return d

    def validate(self) -> None:
        schema = json.loads(_FINDING_SCHEMA_PATH.read_text(encoding="utf-8"))
        validate(self.to_dict(), schema)


def make_provenance(
    *,
    runner_versions: dict[str, str] | None = None,
    model_backend: str = "scripted-mock",
    repo: str | Path | None = None,
) -> Provenance:
    return Provenance(
        git_sha=git_sha(repo),
        timestamp=utc_timestamp(),
        runner_versions=runner_versions or {"lrtp": __import__("lrtp").__version__},
        model_backend=model_backend,
    )


def write_findings(findings: list[Finding], path: str | Path) -> Path:
    """Persist findings as JSON (validated + redacted). Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for f in findings:
        f.validate()
        records.append(f.to_dict())
    path.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
