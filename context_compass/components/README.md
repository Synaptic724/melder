# Components Docs (C3/C2/C1)

Purpose
- Component-level ownership map under the C4 architecture docs.
- Defines C3 components, C2 subcomponents, and C1 code-entry anchors.

Start here
1. `architecture/src_architecture.md` for system boundaries and boot/lifecycle.
2. `components/src_components.md` for component contracts, wiring, and call flows.
3. `components/tests_components.md` for test component structure.

What to keep current
- Component boundaries and ownership.
- Lifecycle/cleanup responsibilities.
- Concurrency and failure-path behavior.
- Method-level call flows for critical runtime paths.
- C1 code map paths and symbol references.

Editing checklist
- Keep C3/C2/C1 terms aligned with C4 terminology.
- Keep diagrams (ASCII + Mermaid) aligned to current runtime behavior.
- Update information sources when adding new evidence files.
- Preserve explicit Unknowns for unresolved claims.

Unknowns and evidence policy
- Use canonical Unknowns Gate:
  `context_compass/agent_onboarding/agent/general/skills/unknowns_gate_reference.md`.

Reference examples
- `context_compass/examples/example_components/`
