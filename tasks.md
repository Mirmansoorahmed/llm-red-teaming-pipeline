# Tasks — LLM Red-Teaming Pipeline

**Repo:** `llm-red-teaming-pipeline` · branch `spec`.
**Status:** spec. No implementation in this turn — this is the ordered plan for review.
**Aligns with:** [`requirements.md`](requirements.md), [`design.md`](design.md), and [`docs/DESIGN.md`](docs/DESIGN.md) §14 phases.

Rules for every task: small, labelled commits (e.g. `phase-4: add DE indirect-injection suite`); no `Co-authored-by`, no AI attribution; synthetic data only; no invented metrics; tests sit next to each slice. `oss` (Phases 0–8) first; `hybrid` (Phase 9) last and only after the oss demo + PDF exist and Mir says go.

Each task lists requirement refs and test hooks. Checkboxes are unchecked (not started).

---

## Phase 0 — Repo foundation *(no Azure)*
- [x] **0.1** Add `Makefile` targets (`test`, `lint`, `demo`, `gate`, `report`) and `pyproject.toml` with core deps and pinned optional extras groups (`[adapters]`, `[hybrid]`). _Refs: C6, C9._
- [x] **0.2** Add JSON Schemas `schemas/scenario.schema.json` and `schemas/finding.schema.json` (skeleton). _Refs: R1, R6._
- [x] **0.3** Add CI workflow that runs lint + tests on an empty/placeholder fixture set with all optional extras uninstalled. _Refs: C6._ _Test: CI green with no extras._
- [x] **0.4** Add `allowlist.py` stub that fails closed on unknown targets (refusal + non-zero exit, no network call). _Refs: R4._ _Test: refuse arbitrary URL / unlisted name._
- [x] **0.5** Confirm `docs/DESIGN.md` and `docs/CASE-STUDY.md` are placed; record commit-hygiene rules in `CONTRIBUTING`/README stub. _Refs: C7._

## Phase 1 — Scenario DSL + finding schema *(no Azure)*
- [x] **1.1** Finalise `schemas/scenario.schema.json` with all §5 fields and enums (8 suites, `de`/`en`). _Refs: R1.1–R1.2._
- [x] **1.2** Build `mappings/frameworks.yaml` from §7 (OWASP LLM 2026 + 2025 crosswalk, Agentic 2026, ATLAS v2026.10); use `AML.T0085.003`; no padding. _Refs: R1.3–R1.4, C3._
- [x] **1.3** Implement `loader.py` with fail-closed validation and mapping-id allowlist. _Refs: R1.5._ _Test: valid + each missing field + bad enum + out-of-set mapping id._
- [x] **1.4** Finalise `finding.schema.json` + `findings.py` record model with provenance and redaction hooks. _Refs: R2.5, R6._ _Test: record carries git SHA + timestamp; redaction removes seeded markers._
- [x] **1.5** Define DE+EN fixture layout under `scenarios/` and `fixtures/`. _Refs: R5._

## Phase 2 — Demo sales agent *(no Azure)*
- [x] **2.1** Implement synthetic CRM / mailboxes / documents and the §6 tools. _Refs: R3.1._
- [x] **2.2** Add fixture users (junior rep, head of sales); restrict forecast to head of sales. _Refs: R3.2._ _Test: junior denied forecast on defended._
- [x] **2.3** Implement `vulnerable` profile (shared high-privilege tools, docs-as-instructions, no binding, retrievable system prompt). _Refs: R3.3._
- [x] **2.4** Implement `defended` profile test double (per-user allowlist, narrow wrappers, risk-tiered approval, approval token = hash(tool+args), canaries, retrieved-as-data). Label as test double. _Refs: R3.4._
- [x] **2.5** Implement scripted/mock backend (deterministic tool calls, offline, no GPU); optional local gen model skipped cleanly and recorded in provenance. _Refs: R3.5._ _Test: scripted backend runs offline._

## Phase 3 — Core harness + judges *(no Azure)*
- [x] **3.1** Implement `runner.py` (scenario × target × profile × runner); enforce allowlist before any call. _Refs: R2.1, R4._
- [x] **3.2** Implement `trace.py` (prompts, tool calls + args hash, data access, approvals, redacted text). _Refs: R2.1._
- [x] **3.3** Implement deterministic judges: tool-call, data-access, approval-binding, canary/hidden-context, and secondary text judge. _Refs: R2.2–R2.4._ _Test: each judge + text-vs-tool conflict (tool wins)._
- [x] **3.4** Persist findings under results dir with provenance + redaction. _Refs: R6._ _Test: result traceable to git SHA + timestamp._

## Phase 4 — v1 attack suites *(no Azure)*
- [x] **4.1** Direct prompt injection (DE+EN). _Refs: R5.1._
- [x] **4.2** Indirect prompt injection via email/doc fixtures (DE+EN). _Refs: R5.1._
- [x] **4.3** Jailbreak (DE+EN). _Refs: R5.1._
- [x] **4.4** Data exfiltration via tools (DE+EN). _Refs: R5.1._
- [x] **4.5** Excessive agency: unauthorized tool, destructive action, junior-vs-forecast (DE+EN). _Refs: R5.1._
- [x] **4.6** Hidden context / system-instruction leak (DE+EN). _Refs: R5.1._
- [x] **4.7** Approval↔args binding bypass incl. approval replay (DE+EN). _Refs: R5.1, R2.3._
- [x] **4.8** Benign hard negatives that must succeed on `defended`. _Refs: R5.2._ _Test: ≥1 DE + ≥1 EN per suite; benign passes on defended; no block-everything._

## Phase 5 — Optional OSS adapters *(no Azure)*
- [x] **5.1** Define adapter interface normalising into the finding schema. _Refs: R7.1._
- [x] **5.2** garak 0.17.1 adapter (optional extra). _Refs: R7.2._
- [x] **5.3** AgentDojo 0.1.35 adapter, isolated/pinned (API may change). _Refs: R7.2._
- [x] **5.4** PyRIT 1.2.0 adapter (optional, heavy). _Refs: R7.2._
- [x] **5.5** promptfoo 0.125.1 adapter; re-check MIT licence + install path. _Refs: R7.2._
- [x] **5.6** Optional smoke target that runs an adapter only if its extra is present. _Refs: R7.4._ _Test: each adapter skips cleanly when absent; default CI green with extras uninstalled._

## Phase 6 — ACA target adapter *(no Azure)*
- [x] **6.1** Implement `aca.py` HTTP mode (`POST /v1/labels`) and recorded fixture mode. _Refs: R8.1._
- [x] **6.2** Score routing decision **and** residual tool-call success; `ask`/`four-eyes` not a block unless the tool call did not happen. _Refs: R8.2._ _Test: fixture `ask` + landed tool call = residual success._
- [x] **6.3** Ensure `oss` CI needs no live ACA; do not edit the ACA repo. _Refs: R8.3._

## Phase 7 — CI regression gate *(no Azure)*
- [ ] **7.1** Commit `results/baseline.json` (git SHA + timestamp). _Refs: R9.1._
- [ ] **7.2** Implement `gate.py` + `make gate`; declared thresholds in config; fail on ASR rise or reopened blocked scenario. _Refs: R9.2, R9.4._
- [ ] **7.3** Add `fixtures/regression/` model/tool-change fixture that reopens a blocked case. _Refs: R9.3._ _Test: gate passes on baseline, fails (non-zero) on regression fixture._

## Phase 8 — Demo, PDF, README *(no Azure)*
- [ ] **8.1** Wire `make demo` to the §10 script on `oss` with scripted backend; keep under 15 min; record duration (TO BE MEASURED until run). _Refs: R10.1, C9._
- [ ] **8.2** Implement `report.py` + `make report` (brief, diagnosis, options, solution, results, mappings, roadmap); fail closed on missing field / uncommitted number. _Refs: R10.2._ _Test: fail-closed cases._
- [ ] **8.3** Write 3-minute README (problem → figure → run → results-when-measured → limits). _Refs: R10.3._
- [ ] **8.4** Reference icon-based `docs/diagrams/architecture.png` when placed; keep Mermaid review diagram until then; no box-only Mermaid as final. _Refs: R10.4._
- [ ] **8.5** Commit first measured results file; update README/PDF numbers only from it. _Refs: C2._

## Phase 9 — Hybrid adapters + runbook *(Azure — only after oss demo + PDF exist and Mir says go)*
- [ ] **9.1** Env-only `LRTP_*` config loader; mocked in tests; clean degrade when credentials missing. _Refs: R11.1–R11.2._ _Test: credentials-absent degrade; oss still runs._
- [ ] **9.2** Prompt Shields adapter scored as a separate defended-config signal, never a verdict. _Refs: R11.3._ _Test: recorded as signal, not verdict._
- [ ] **9.3** Optional Azure OpenAI target backend and/or pinned judge (judge off by default; deterministic judges stay primary). _Refs: R11.3._
- [ ] **9.4** Write `docs/HYBRID.md`: portal steps (Germany West Central only, portal-only, smallest/free tiers, create-test-delete), env vars, cost notes, teardown, place for real-session results; never invent numbers; no restricted identifiers. _Refs: R11.4–R11.5, C8._
- [ ] **9.5** Record a real hybrid session's results only if a live portal session is run and committed; otherwise leave TO BE MEASURED. _Refs: C2._

---

## Exit criteria
- **oss done:** Phases 0–8 complete; `make demo` < 15 min; `make gate` and `make report` work; first measured results committed; README skimmable in 3 minutes.
- **hybrid done:** Phase 9 complete after an explicit go; adapters degrade cleanly; `docs/HYBRID.md` written; no invented hybrid numbers; no restricted identifiers published.
