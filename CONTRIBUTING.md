# Contributing

Portfolio lab repo. These rules are enforced in review and in CI.

## Commit hygiene
- Small, labelled commits. Prefix with the phase, e.g. `phase-4: add DE indirect-injection suite`.
- **No `Co-authored-by` trailers and no AI attribution** in commit messages or anywhere else.

## Safety and honesty
- **Synthetic data only.** Fictional consultancy *Northwind Advisory*, fictional client *Ortenwald Handel GmbH*. No real company as the client, no employer branding, no real employer names anywhere.
- **No real attacks on third-party systems.** The harness runs only against the in-repo demo agent and the configured ACA lab endpoint or recorded fixture; it refuses anything else (see `src/lrtp/allowlist.py`).
- **Never invent metrics.** Any number in the README, report, or case study must come from a committed run with a timestamp and git SHA. Otherwise write `TO BE MEASURED` or `TARGET`.
- **Do not copy legal, OWASP, or ATLAS text.** Use official ids plus short titles in our own words. Mappings are illustrative, not a certification claim.
- Do not publish the lab subscription id, student lab tenant name, or credit amount.

## Profiles
- The default `oss` profile and CI must pass with **no cloud account, no network, no GPU**, and all optional runner extras uninstalled. The harness core is standard-library only.
- Optional OSS runner adapters (Phase 5) and Azure hybrid adapters (Phase 9) are feature-flagged and must degrade cleanly when absent.

## Tests
- Put tests next to each slice under `tests/`. Required coverage: schema validation, judges (including approval binding), the target allowlist, adapter-absent paths, the regression gate, and the eval runner.
- Run locally with `make test` (just `pytest`).
