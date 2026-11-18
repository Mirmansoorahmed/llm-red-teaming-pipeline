# Scenarios

Versioned red-team scenarios in the LRTP DSL (YAML), one document per file,
validated against [`schemas/scenario.schema.json`](../schemas/scenario.schema.json).

Layout: one directory per suite (the `suite` enum). Each suite carries both a
German (`*.de.yaml`) and an English (`*.en.yaml`) scenario in v1.

```
scenarios/
  prompt_injection_direct/
  prompt_injection_indirect/
  jailbreak/
  exfil_via_tools/
  excessive_agency/
  hidden_context_leak/
  approval_binding/
  benign/
```

All payloads and data are synthetic and exist only to test the in-repo demo
agent and the configured ACA lab target. See `fixtures/` for the synthetic CRM,
mailboxes, and documents that indirect-injection scenarios reference.
