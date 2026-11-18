"""`make demo` entrypoint (requirements.md R10.1, Phase 8).

Runs the full scenario set against the demo agent on BOTH the vulnerable and the
defended profiles with the scripted/mock backend (oss, offline), prints a short
summary following the DESIGN.md demo script, and writes a single timestamped JSON
run file under ``eval/results/``. That committed run file is the only source for
numbers in the README and docs/REPORT-DATA.md (C2: never invent metrics).
"""

from __future__ import annotations

import sys
from pathlib import Path

from lrtp.eval_run import RESULTS_DIR, run_all, timestamped_run_name, write_run
from lrtp.report import summarise


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    out_dir = Path(argv[0]) if argv else RESULTS_DIR

    findings = run_all()
    out_dir.mkdir(parents=True, exist_ok=True)
    run_name = timestamped_run_name(findings)
    write_run(findings, out_dir / run_name)

    summary = summarise([f.to_dict() for f in findings])
    print("LLM Red-Teaming Pipeline — oss demo (scripted/mock backend)")
    print(f"scenarios: {summary['scenario_count']}  (DE {summary['de']} / EN {summary['en']})")
    print(f"vulnerable ASR: {summary['vulnerable_asr']:.3f}")
    print(f"defended ASR:   {summary['defended_asr']:.3f}")
    print(f"benign false-block rate (defended): {summary['benign_false_block_rate']:.3f}")
    print(f"run file: eval/results/{run_name}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
