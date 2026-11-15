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

    args = parser.parse_args(argv)

    if args.command == "check-target":
        try:
            check_target(args.name)
        except TargetNotAllowed as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        print(f"OK: target '{args.name}' is allowed")
        return 0

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
