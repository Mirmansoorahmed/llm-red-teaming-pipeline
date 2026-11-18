"""Optional adapter smoke check (requirements.md R7.4).

Runs only for adapters whose backing tool is actually present. In the default
`oss` environment (no extras installed) this reports every adapter as skipped
and exits 0, so it never fails CI. It executes nothing heavyweight; it only
confirms each present adapter can normalise a trivial payload.
"""

from __future__ import annotations

from lrtp.adapters import discover_adapters


def run_smoke() -> dict[str, str]:
    """Return {adapter_name: 'skipped'|'ok'} for every registered adapter."""
    status: dict[str, str] = {}
    for adapter in discover_adapters():
        if not adapter.available():
            status[adapter.name] = "skipped"
            continue
        try:
            adapter.normalise([])  # empty payload: must not raise
            status[adapter.name] = "ok"
        except Exception:  # noqa: BLE001 - optional runner may raise anything  # pragma: no cover
            status[adapter.name] = "error"
    return status


def main() -> int:  # pragma: no cover - CLI convenience
    status = run_smoke()
    for name, state in status.items():
        print(f"{name}: {state}")
    # Never fail just because extras are absent.
    return 0 if all(v in ("skipped", "ok") for v in status.values()) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
