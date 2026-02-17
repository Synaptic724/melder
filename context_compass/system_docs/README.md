# Architecture Docs (C4 Mapping)

Purpose
- System-level C4 map for runtime boundaries, boot flow, lifecycle, and invariants.
- Keep this folder compaction-safe and evidence-backed.

Start here
1. `system_docs/src_architecture.md` (runtime architecture).
2. `system_docs/src_components.md` (component wiring and code map).
3. `system_docs/tests_architecture.md` and `system_docs/tests_components.md` for test architecture.

Read by intent
- Bootstrap/runtime entrypoints:
  - `src_architecture.md` -> Entrypoints and Runtime Guardrails
  - `src_architecture.md` -> Boot and Configuration Sequence
- Ownership/lifecycle/cleanup:
  - `src_architecture.md` -> Ownership, Lifecycle, and Cleanup
  - `system_docs/src_components.md` -> lifecycle sections by component
- Failure/debug:
  - `src_architecture.md` -> Failure Modes and Error Paths
  - `system_docs/src_components.md` -> Method-Level Call Flows (C1)

Update triggers
- New subsystem or boundary change.
- Lifecycle/ownership/invariant changes.
- Public API boundary changes.

Editing checklist
- Keep C4 and C3/C2/C1 docs consistent.
- Keep ASCII + Mermaid diagrams aligned to current behavior.
- Update information sources when new evidence files are used.
- Keep unresolved claims in Unknowns until verified.

Unknowns and evidence policy
- Use canonical Unknowns Gate:
  `context_compass/agent_onboarding/agent/general/skills/unknowns_gate_reference.md`.

Reference examples
- `context_compass/examples/example_architecture/`

