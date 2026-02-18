

# Engineer Career

Purpose
- Engineer-specific onboarding deltas on top of the shared general baseline.

Scope rule
- Keep only engineer-specific policy/behavior here.
- Shared rules remain in `agent_onboarding/default/general/` and are indexed in
  `agent_onboarding/default/general/SKILLS.MD`.
- Engineer extends `general` and must remain a delta layer:
  no path overlap with `agent_onboarding/default/general/SKILLS.MD`.

Engineer inventory
- `agent_onboarding/default/engineer/SKILLS.MD`: engineer-specific read sequence.
- `skills/engineer_execution.md`: execution discipline for engineering work.
- `skills/technical_expertise.md`: root-cause-first debugging discipline.
- `skills/system_orientation.md`: system explanation flow for engineers.
- `skills/architecture_contexts.md`: architecture/components source-of-truth policy.
- `skills/src_architecture_instructions.md`: creation/maintenance mechanics for
  `system_docs/src_architecture.md`.
- `skills/src_components_instructions.md`: creation/maintenance mechanics for
  `system_docs/src_components.md`.
- `skills/tests_architecture_instructions.md`: creation/maintenance mechanics
  for `system_docs/tests_architecture.md`.
- `skills/tests_components_instructions.md`: creation/maintenance mechanics for
  `system_docs/tests_components.md`.
- `skills/documentation_standards.md`: deep architecture/components documentation quality contract.
- `skills/context_protocol.md`: code-work discovery order and docs-first boundary rules.
- `skills/staleness_protocol.md`: stale-doc handling for engineering context maintenance.
- `policies/engineer_quality_policy.md`: quality and evidence bar.
- `policies/ctx_autonomy_policy.md`: engineer context-quality constraints.
- `policies/ctx_autonomy_rubric.md`: full CTX Autonomy scoring rubric for file/dir/component/architecture layers.
- `behavioral_guidelines/engineer_workflow.md`: engineer execution flow.
- `behavioral_guidelines/task_execution_and_validation.md`: implementation and validation flow for engineering tasks.
- `examples/eng_task_flow.md`: concise engineer task flow.
- `examples/artifact_workflow.md`: scratch-to-ticket artifact promotion pattern.

User-defined overlay boundary
- Preference-heavy Python/testing/library-style rules are routed through:
  `agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`.
- Default engineer keeps generalized, reusable engineering guidance only.

Unknowns Gate
- Apply the canonical policy in
  `agent_onboarding/default/general/skills/unknowns_gate_reference.md`.
- Engineer onboarding claims about code behavior, contracts, and validation
  status must remain UNKNOWN until direct source evidence is attached.
- During execution handoffs, promote to FACT only with reproducible evidence
  pointers that another engineer can verify quickly.





