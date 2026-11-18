"""Target allowlist — fail closed on anything that is not a permitted target.

Per requirements.md R4 and docs/DESIGN.md §3, the harness may only run against:

  1. the in-repo demo sales agent (``demo``), and
  2. the configured ACA lab endpoint or recorded fixture (``aca``).

Any other target name, host, or URL is refused *before* any network call or
tool invocation. Refusal raises :class:`TargetNotAllowed`; the CLI maps that to
a non-zero exit. There is no override flag: this is a safety control, not a
convenience toggle.
"""

from __future__ import annotations

from urllib.parse import urlparse

# The only permitted logical targets.
ALLOWED_TARGETS: frozenset[str] = frozenset({"demo", "aca"})

# When the ACA target is reached over HTTP, only these hosts are permitted.
# Loopback by default; a deployment may extend this via configuration, but never
# to a third-party or public-internet host.
ALLOWED_ACA_HOSTS: frozenset[str] = frozenset({"localhost", "127.0.0.1", "::1"})


class TargetNotAllowed(RuntimeError):
    """Raised when a run is pointed at a target outside the allowlist."""


def check_target(name: str) -> str:
    """Return ``name`` if it is an allowed logical target, else refuse.

    Refusal happens here, before the runner performs any call.
    """
    if name not in ALLOWED_TARGETS:
        raise TargetNotAllowed(
            f"refusing to run against target '{name}': only {sorted(ALLOWED_TARGETS)} "
            f"are permitted. No third-party system may be attacked."
        )
    return name


def check_aca_url(url: str) -> str:
    """Validate an ACA endpoint URL against the host allowlist; else refuse."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host not in ALLOWED_ACA_HOSTS:
        raise TargetNotAllowed(
            f"refusing ACA endpoint host '{host}': only {sorted(ALLOWED_ACA_HOSTS)} "
            f"are permitted for the ACA lab target. Use a recorded fixture otherwise."
        )
    return url
