# Engineer Career

Purpose
- Engineer-specific onboarding deltas on top of the shared general baseline.

Scope rule
- Keep only engineer-specific policy/behavior here.
- Shared rules remain in `agent_onboarding/agent/general/` and are indexed in
  `agent_onboarding/agent/general/SKILLS.md`.

Engineer inventory
- `SKILLS.md`: engineer-specific read sequence.
- `skills/engineer_execution.md`: execution discipline for engineering work.
- `skills/architecture_contexts.md`: architecture/components source-of-truth policy.
- `skills/src_architecture_instructions.md`: creation/maintenance mechanics for
  `system_docs/src_architecture.md`.
- `skills/src_components_instructions.md`: creation/maintenance mechanics for
  `system_docs/src_components.md`.
- `skills/tests_architecture_instructions.md`: creation/maintenance mechanics
  for `system_docs/tests_architecture.md`.
- `skills/tests_components_instructions.md`: creation/maintenance mechanics for
  `system_docs/tests_components.md`.
- `policies/engineer_quality_policy.md`: quality and evidence bar.
- `policies/ctx_autonomy_policy.md`: engineer context-quality constraints.
- `behavioral_guidelines/engineer_workflow.md`: engineer execution flow.
- `examples/eng_task_flow.md`: concise engineer task flow.
- `examples/artifact_workflow.md`: scratch-to-ticket artifact promotion pattern.

Unknowns Gate
- Apply the canonical policy in
  `agent_onboarding/agent/general/skills/unknowns_gate_reference.md`.
- Engineer onboarding claims about code behavior, contracts, and validation
  status must remain UNKNOWN until direct source evidence is attached.
- During execution handoffs, promote to FACT only with reproducible evidence
  pointers that another engineer can verify quickly.
