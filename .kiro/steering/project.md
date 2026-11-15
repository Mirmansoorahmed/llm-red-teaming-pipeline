# Steering — llm-red-teaming-pipeline

## Purpose
Portfolio project under the **AI Governance Platform** umbrella. **LLM Red-Teaming Pipeline** (`llm-red-teaming-pipeline`) is an automated red-team harness that runs versioned attack suites (German and English) against *our* targets and scores outcomes at the **tool-call and data-access** level, not just model text. Findings map to OWASP Top 10 for LLM Applications 2026 (with a 2025 crosswalk), OWASP Top 10 for Agentic Applications 2026, and MITRE ATLAS v2026.10. A CI gate fails the build on regression against a committed baseline.

Demo consultancy: **Northwind Advisory**. Demo client: **Ortenwald Handel GmbH** (fictional mid-size German B2B wholesaler, about 1,200 employees, headquarters in Germany, several regional sales offices). Not a real firm. Not Tarsfeld, NordPay, Northwind, Rheinwerk, Vaillant, or any other real employer.

This repo is the planned owner of the Testing gaps recorded in ACA `docs/AGENT-SECURITY-FRAMEWORK.md`: red-teaming harness, tool-call-level security evals, an enforcing regression gate on model/prompt/tool change, and approval↔args binding tests.

## Sibling and boundaries
- **AI Compliance Automation** (`ai-compliance-automation`) is a *target* and an optional defense config, reached only through its public HTTP contract (`POST /v1/labels`) or a recorded fixture. Do not edit that repo, the Agent Access Governance Gateway, `agent-trust-gateway`, or the data-governance repo, and do not open PRs to them from this work.
- Do not build the **Agent Hardening Sandbox** here. A small `defended` profile of the *demo* agent is allowed as a test double so binding and allowlist tests can pass. Runtime hardening of production agents stays on that sibling's roadmap.
- Do not build **AI Audit Logging & Monitoring** or the **Multi-Agent AI System (LangGraph)** here.
- **No real attacks on third-party systems.** The only permitted targets are the in-repo demo agent and the configured ACA lab endpoint or fixture. The harness must refuse anything else.

## Stack (hybrid, portable by default)
- **Default profile `oss` (CI must pass with this only):** Python harness, our scenario DSL, a shipped demo sales agent with `vulnerable` and `defended` profiles, a scripted/mock target backend (no GPU, no paid API), deterministic judges, CI regression gate, PDF report. Optional extras, not required for default CI or `make demo`: NVIDIA garak 0.17.1, AgentDojo 0.1.35 (pin and isolate; API may change), Microsoft PyRIT 1.2.0, promptfoo 0.125.1 (Node; remains MIT OSS as of that release).
- **Optional profile `hybrid`:** same core, plus feature-flagged, env-only adapters (`LRTP_*`): Azure OpenAI in **Germany West Central** as an optional target and/or pinned judge (availability on the student tenant is **unverified**); Azure AI Content Safety Prompt Shields as one defended-config *signal*, never a verdict (F0 in Germany West Central was created, used, and deleted on 14 November 2026; portal cost 0). Adapters degrade cleanly when credentials are missing.
- Portal-only Azure creation (Azure CLI device login is blocked). Smallest or free tiers, create-test-delete. Budget alert already exists.

## Hard constraints
- **Synthetic data only.** Fictional firms: Northwind Advisory and Ortenwald Handel GmbH. No real client data.
- **No employer branding** (no Telekom, Magenta, PwC, or other real employer names) on demos, READMEs, or reports. No real company as the client.
- **No AI attribution** and **no `Co-authored-by`** (or similar) on commits. Commits are small and labelled (for example `phase-4: add DE indirect-injection suite`).
- **Never invent metrics.** Every number in README / report / case study / CV draft must come from a **committed run** with **timestamp + git SHA**. Until then write "TO BE MEASURED" or "TARGET". No invented hybrid numbers.
- **Do not copy legal, OWASP, or ATLAS text.** Official ids plus short titles in our own words. Mappings are illustrative, not a certification or conformity claim. Use the mapping table in DESIGN.md §7; do not pad coverage.
- Tests required for schema validation, judges (including approval binding), target allowlist (refuse unknown targets), adapter-absent paths, the regression gate, and the eval runner.
- README must be skimmable in ~3 minutes: problem → icon architecture figure → how to run (`make demo`, both profiles) → results table (when measured) → limitations.
- Full `make demo` (oss, scripted/mock backend) must run in **under 15 minutes** after dependencies are already installed.
- Do not publish the lab subscription id, university / IU tenant, or credit amount in the README, case-study PDF, or commit messages.

## Docs Mir will place for you
- `docs/DESIGN.md` (product design)
- `docs/CASE-STUDY.md` (consulting narrative; do not invent results)
- `docs/diagrams/architecture.png` (icon-based published figure, plus svg / generator when placed; if the figure is not in the repo yet, include mermaid in design.md for review and leave a path for the icon figure — do not ship a box-only mermaid as the final published architecture)
- `README.md`

## Out of scope (v1)
- Attacks, probes, or scans against third-party systems, real CRMs, or live vendor endpoints we do not own
- Implementing the Agent Hardening Sandbox, editing ACA or the gateway, or building the audit-logging / LangGraph siblings
- Hands-on use of Lakera / Check Point, Prisma AIRS / Protect AI, or HiddenLayer (Buy vs. Build documentation only)
- Treating Prompt Shields or an LLM judge as an authorization control
- Production HA, multi-region cut-over, or a second-cloud implementation
- Legal sign-off, a works agreement, or a certification claim
