# LLM Red-Teaming Pipeline

An automated red-team harness that scores **tool calls and data access** — not just model text — against a shipped sales agent, and fails CI when a committed baseline regresses. Portfolio lab project; synthetic data only.

Fictional consultancy **Northwind Advisory** runs the harness for a fictional client, **Ortenwald Handel GmbH** (a German B2B wholesaler). No real company, no real data.

## The problem

A sales assistant wired to CRM, email, and documents can *say* the right thing and still send the wrong email or read a record it should not. Text-only evals miss that. This harness runs versioned attack suites (German + English) against a deliberately **vulnerable** agent and a **defended** test-double profile, and judges success from what the agent *did*: which tool ran, which data was accessed, whether an approval stayed bound to its exact arguments, and whether hidden instructions leaked.

Findings map to OWASP Top 10 for LLM Applications 2026 (with a 2025 crosswalk), OWASP Top 10 for Agentic Applications 2026, and MITRE ATLAS v2026.10. Mappings are illustrative, not a certification claim.

## Architecture

```mermaid
flowchart LR
    suites["Scenario DSL\nDE+EN suites (YAML)"] --> runner["Eval runner\n(+ target allowlist)"]
    runner --> demo["Demo agent\nvulnerable / defended"]
    runner --> aca["ACA target\nHTTP or fixture"]
    demo --> judges["Deterministic judges\ntool call · data access\napproval binding · canary"]
    aca --> judges
    judges --> results["Run files\neval/results/ (git SHA + ts)"]
    results --> gate["Regression gate\nvs committed baseline"]
    adapters["Optional OSS runners\ngarak · AgentDojo · PyRIT · promptfoo"] -. normalise .-> runner
```

This Mermaid diagram is for review. The published figure will be the icon-based `docs/diagrams/architecture.png` once placed; a box-only Mermaid will not be shipped as the final figure.

## How to run (oss profile — no cloud, no network, no GPU)

The core harness is standard-library only. Nothing to install beyond Python 3.10+ and (for tests) `pytest`.

```bash
make test     # run the test suite
make demo     # run every scenario vs vulnerable AND defended; write a timestamped run file
make gate     # fail if the defended profile regresses vs the committed baseline
make report   # regenerate docs/REPORT-DATA.md from the latest committed run file
make smoke    # optional-adapter smoke check (skips cleanly when extras are absent)
```

Optional OSS runner adapters (garak, AgentDojo, PyRIT, promptfoo) and Azure hybrid adapters are feature-flagged and skip cleanly when absent; default CI passes with them uninstalled.

## Results

From the committed run `eval/results/run-20261115T182308Z-4ff503afea47.json` (git SHA `4ff503afea47`, scripted/mock backend). Full tables in [`docs/REPORT-DATA.md`](docs/REPORT-DATA.md).

| Metric | Value |
|---|---|
| Scenarios (DE / EN) | 16 (8 / 8) |
| Vulnerable attack-success rate | 1.000 |
| Defended attack-success rate | 0.000 |
| Benign false-block rate (defended) | 0.000 |

Every number here is copied from that committed run file. Any metric without a committed run stays **TO BE MEASURED**.

## Limitations

- Lab project, synthetic data, fictional client. Not legal advice, not a security certification.
- Only two targets are permitted — the in-repo demo agent and a configured ACA lab endpoint/fixture — and the harness refuses anything else. No real attacks on third-party systems.
- The `defended` profile is a **test double** for controls the planned Agent Hardening Sandbox would own, not a claim that sandbox is implemented.
- Optional runners and Azure adapters are integrations, not used to produce any number above.
- Framework mappings are illustrative. The deterministic tool-call / data-access judges are authoritative; a text (LLM) judge is never treated as an authorization control.

See [`docs/DESIGN.md`](docs/DESIGN.md) for the full design and [`docs/CASE-STUDY.md`](docs/CASE-STUDY.md) for the consulting narrative.
