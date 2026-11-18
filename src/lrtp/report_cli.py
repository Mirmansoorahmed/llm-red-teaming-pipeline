"""CLI for `make report` — write docs/REPORT-DATA.md from a committed run file.

Fails closed (non-zero exit) when no committed run file exists, so the report can
never contain an un-measured number.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lrtp.report import ReportError, latest_run_file, render_report_data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lrtp-report")
    parser.add_argument("--results", default="eval/results")
    parser.add_argument("--out", default="docs/REPORT-DATA.md")
    parser.add_argument("--run", default=None, help="specific run file (default: latest)")
    args = parser.parse_args(argv)

    try:
        run_path = Path(args.run) if args.run else latest_run_file(args.results)
        content = render_report_data(run_path)
    except ReportError as exc:
        print(f"REPORT FAIL (fail-closed): {exc}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"wrote {out} from {run_path.name}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
