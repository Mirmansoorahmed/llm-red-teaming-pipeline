# Case study: LLM Red-Teaming Pipeline for Ortenwald Handel GmbH

**Portfolio case study** · prepared for Mir Mansoor Ahmed
**Role in the fiction:** consultant at *Northwind Advisory*
**Client in the fiction:** *Ortenwald Handel GmbH* (mid-size German B2B wholesaler, technical and industrial products, about 1,200 employees, headquarters in Germany, several regional sales offices)
**Date:** 15 November 2026 (Europe/Berlin)
**Status:** proposed engagement and lab design. This is not a completed client delivery, not legal advice, and not a security certification or conformity assessment. No results have been measured yet.

Technical design: Technical design: [`DESIGN.md`](DESIGN.md).

---

## Rules (do not delete from this case study)

- Never invent metrics, headcount of a real employer, repo stars, or outcomes. If it was not measured, write **TO BE MEASURED** and leave the cell empty of numbers.
- Never copy text from ISO, the EU AI Act, OWASP, or MITRE ATLAS. Use official ids plus a short title in our own words. Mappings are illustrative, not a certification claim.
- Synthetic data and fictional names only. No real client data. No real company as the client. No employer branding and no real employer names anywhere.
- **No real attacks on third-party systems.** Only the in-repo demo agent and our own ACA lab target.
- Cloud and vendor choices must be honest: adapters and feature flags, a path that runs without paid APIs, unverified Azure OpenAI access listed as a TODO. Do not publish the lab subscription id, student lab tenant name, or credit amount in this PDF.
- Commits in the real repo: no `Co-authored-by`, no AI attribution.

---

## 1. Client brief

Ortenwald Handel is a fictional mid-size German B2B wholesaler. About 1,200 people work there, at a German headquarters and several regional sales offices. The sales organisation is piloting an internal assistant connected to the company CRM, email, and a shared document store. The same assistant would serve a junior sales representative and the head of sales. Typical tasks are retrieving customer records, summarising conversations, drafting emails, and updating deal status.

The pain the CISO and the sales-operations lead bring to Northwind Advisory is practical:

- Public incidents have already shown that an AI agent can be steered into retrieving or sending data it should not touch. Leadership does not want a “it looked fine in a chat log” go-live.
- Native filters (prompt-injection detectors, vendor guardrails) exist or can be bought. They mostly score what the model *says*. They do not, by themselves, prove that a disallowed tool call or an unauthorised CRM read was blocked.
- A junior representative must not be able to pull a company-wide forecast, or to approve a sensitive action, simply because the agent asked. If a human approves an email to one customer, the agent must not quietly change the recipient afterwards.
- The firm will change models, prompts, and tools. There is no regression test that fails the build when a previously blocked attack starts working again.
- Legal, the DPO, and (because logs can identify staff) the Betriebsrat will ask what was tested, against which recognised framework, and what evidence remains.

Northwind Advisory is asked for a repeatable red-team pipeline the firm can run in CI: attack suites in German and English, verdicts at the tool-call and data-access layer, a mapped risk memo, and a gate that fails on regression — without ever pointing the harness at a customer’s real systems or at any third party.

---

## 2. Problem diagnosis

### As-is

- The sales assistant is being wired to CRM, email, and documents with a shared service identity. Least privilege for the *user* is not enforced at tool-call time.
- ACA (a sibling lab) can label intent and route a request to review, but its own eval still scores routing decisions rather than live tool calls. It has no red-team harness and no approval↔args binding test.
- Vendor or open-source scanners (garak, promptfoo, commercial suites) can generate many prompts. They are a starting point, not a complete test of *this* agent’s tools, approvals, and data access.
- There is no committed baseline that CI can compare against when the model or the tool list changes.

### Risks

- Indirect prompt injection in an email or a CRM note causes the agent to send internal data outside the firm, or to change a deal, while the chat reply still looks polite.
- A junior user obtains head-of-sales data, or a destructive tool runs without a bound approval.
- A model upgrade reopens an attack that a manual review closed last quarter.
- An audit finds a slide deck of “we red-teamed the chatbot” and no evidence that tool calls were checked.
- Buying a platform without a tool-level success criterion leaves the same gap, at higher cost.

### Legal and organisational requirements (illustrative, not a classification)

- **OWASP Top 10 for LLM Applications 2026** as the primary application-risk language, with a crosswalk to the 2025 list (Hidden Context Exposure is the renamed, broader form of 2025 System Prompt Leakage).
- **OWASP Top 10 for Agentic Applications 2026**, especially Agent Goal Hijack, Tool Misuse, Identity and Privilege Abuse, and Human-Agent Trust Exploitation.
- **MITRE ATLAS v2026.10** for technique-level reporting (prompt injection, jailbreak, tool invocation, exfiltration via tools, system instructions).
- **EU AI Act** record-keeping and human-oversight themes (Art. 12 / 14) only at theme level, and only where Legal later classifies a system as in scope. This lab does not classify the sales assistant.
- **GDPR** purpose limitation and minimisation for any test logs that could identify staff. **Betriebsrat** co-determination under § 87 Abs. 1 Nr. 6 BetrVG is a client legal path, not something this lab “implements”. The technical default is synthetic identities and redacted reports.
- **ISO/IEC 27001:2022** themes already used elsewhere in the portfolio (testing, logging, access, leakage) as a cross-walk only — no copied control text, no certification claim.

### Stakeholders

| Role | Interest |
|---|---|
| CISO / security operations | Evidence that disallowed actions are blocked, not only that the model refused in text |
| DPO / Legal | Lawful testing, no live data, recognised framework mappings, no fake certification |
| Betriebsrat | Purpose limitation, no performance surveillance disguised as security testing |
| Sales operations / head of sales | The assistant must still do lawful daily work; over-blocking is a failure |
| Platform engineering | A CI gate that runs offline, with optional Azure adapters, and does not lock the firm to one vendor |

---

## 3. Options and decision

Three options were compared. The detailed Buy vs. Build table is in [`DESIGN.md` §8](DESIGN.md).

**A. Buy only.** Licence a commercial AI red-team or runtime platform — Check Point (Lakera, acquired October 2025), Palo Alto Prisma AIRS (Protect AI, acquisition completed July 2025), HiddenLayer — and turn on whatever Microsoft already offers (Prompt Shields, Foundry safety evals). Strength: a vendor holds product risk, catalogues are large, some buyers already have the licence. Weakness: many offerings still emphasise model-text findings; they may not test Ortenwald’s exact tools, the junior-vs-head-of-sales split, or approval↔args binding. EU residency, price, and lock-in stay on the client. The lab would have little honest, reproducible evidence if the licence is missing.

**B. Build only, open source.** Our scenario DSL, our demo agent, our judges and CI gate, plus optional NVIDIA garak, AgentDojo, PyRIT, and promptfoo. Strength: portable, CI-native, tool-call-level scoring, no student-account or vendor-quota risk. Weakness: we maintain the suites; adaptive commercial catalogues are larger; a Microsoft-leaning client will ask why Azure is absent.

**C. Hybrid (recommended).** Keep the scoring contract, the Ortenwald suites, the regression gate, the framework mapping, and the risk memo as our code, runnable fully open source with a mock target. Integrate garak, AgentDojo, PyRIT, and promptfoo as optional adapters. Use Azure OpenAI (if the student tenant can actually host it) as an optional target or judge, and Prompt Shields as one defended-config signal, in Germany West Central, created, tested, and deleted in the same session. Recommend a commercial platform when the firm needs continuous vendor-supported coverage — and still require tool-level judges and a regression gate.

**Decision: C.** It matches how a consultant would land this at a Microsoft-leaning mid-market German firm, without making CI depend on Azure or a paid scanner. Prompt Shields on this lab subscription was already reached once (F0, Germany West Central, 14 November 2026, then deleted, portal cost 0). Azure OpenAI access remains a TODO. Until a short, approved portal session says otherwise, the open-source profile is the one that must always run.

---

## 4. Solution

See [`DESIGN.md`](DESIGN.md) for the architecture, suites, mappings, profiles, and demo script.

In one paragraph for a hiring manager: Northwind Advisory builds a GitHub-native red-team pipeline around a deliberately vulnerable — and a defended — sales assistant, plus the existing AI Compliance Automation service as a second target. Versioned scenarios in German and English describe the attack and the machine-checkable success criterion (which tool, which data, whether an approval stayed bound to its arguments). Optional open-source runners feed the same finding schema. CI compares each run to a committed baseline and fails the build on regression. The output is a findings report and a risk memo mapped to OWASP LLM 2026, OWASP Agentic 2026, and MITRE ATLAS, with every number taken from a committed run. Azure is optional. No third-party system is attacked. `make demo` tells that story in under 15 minutes; `make report` writes the PDF.

---

## 5. Results

Nothing has been measured yet. Every row stays **TO BE MEASURED** until a committed run with timestamp and git SHA exists. Do not fill this table from targets or memory.

| Result | Figure | Source (file, timestamp, git SHA) |
|---|---|---|
| ASR on the vulnerable demo profile (tool-call / data-access judges), DE+EN | TO BE MEASURED | — |
| ASR on the defended demo profile | TO BE MEASURED | — |
| Approval-binding bypass rate (vulnerable vs defended) | TO BE MEASURED | — |
| Benign task success / false-block rate on the defended profile | TO BE MEASURED | — |
| ACA target: routed-to-review vs residual tool-call success | TO BE MEASURED | — |
| Regression gate: fixture that must fail CI when a blocked case reopens | TO BE MEASURED | — |
| `make demo` duration (`oss`, after dependencies) | TO BE MEASURED | — |
| Hybrid session: which adapters were live vs mocked, region, SKU, teardown, portal cost | TO BE MEASURED | — |

---

## 6. Roadmap and recommendation

Estimates below are design-planning figures only, not a booked delivery. Phase detail is in `PLAN.md`.

1. Agree the spec (`requirements.md`, `design.md`, `tasks.md`) on branch `spec` and stop for review.
2. Implement Phases 0–8 on the `oss` profile until `make demo` and `make report` run, and commit the first measured result file.
3. Only then, with an explicit go, run a short Germany West Central portal session for Phase 9 (Prompt Shields as a defended config; Azure OpenAI only if the portal actually allows it). Write `docs/HYBRID.md`, capture results, delete the resources the same day.
4. Keep commercial red-team platforms as documented buy options. Do not imply hands-on Lakera, Prisma AIRS, or HiddenLayer experience.
5. Feed findings back into ACA eval cases where they fit; do not modify the ACA repo from this project. Runtime control gaps stay on the Agent Hardening Sandbox roadmap.

**Recommendation to the fictional client:** adopt the hybrid pipeline. Do not go live on the sales assistant until tool-call-level suites pass on a defended configuration and the CI gate is in the model/tool change path. Buy a commercial scanner if the firm wants continuous vendor coverage, but do not treat it as a substitute for tests of *this* agent’s tools, approvals, and data access.
