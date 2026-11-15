"""Minimal CLI surface for the harness.

Only the pieces needed by the implemented phases are wired here. The
``check-target`` subcommand exists so the target allowlist (R4) can be exercised
from the command line and exits non-zero on refusal.
"""

from __future__ import annotations

import argparse
import sys

from lrtp.allowlist import TargetNotAllowed, check_target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lrtp")
    sub = parser.add_subparsers(dest="command", required=True)

    ct = sub.add_parser("check-target", help="validate a target against the allowlist")
    ct.add_argument("name")

    g = sub.add_parser("gate", help="run the suite and compare against a baseline")
    g.add_argument("--baseline", default="eval/results/baseline.json")
    g.add_argument(
        "--current",
        default=None,
        help="path to a current run file; if omitted, the suite is run fresh",
    )

    args = parser.parse_args(argv)

    if args.command == "check-target":
        try:
            check_target(args.name)
        except TargetNotAllowed as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        print(f"OK: target '{args.name}' is allowed")
        return 0

    if args.command == "gate":
        return _run_gate(args.baseline, args.current)

    return 1


def _run_gate(baseline_path: str, current_path: str | None) -> int:
    from lrtp.eval_run import records, run_all
    from lrtp.gate import compare, load_records

    baseline = load_records(baseline_path)
    current = records(run_all()) if current_path is None else load_records(current_path)
    result = compare(baseline, current)
    print(f"defended ASR: baseline {result.baseline_asr:.3f} -> current {result.current_asr:.3f}")
    if result.passed:
        print("GATE PASS: no defended regression vs baseline")
        return 0
    print("GATE FAIL: defended regression detected", file=sys.stderr)
    for r in result.regressions:
        print(f"  - {r}", file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
