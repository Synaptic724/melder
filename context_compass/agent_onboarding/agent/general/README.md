# General Career (Shared)

Purpose
- Shared onboarding baseline for all careers.
- Defines where execution policy, narrative workflow, and examples live.

Primary entrypoints
- `agent_onboarding/agent/general/SKILLS.md`: canonical read order.
- `agent_onboarding/agent/general/policies/policy_router.md`: policy chain and execution gates.

Folder map
- `behavioral_guidelines/`: descriptive execution stories.
  - `onboarding_summary.md`
  - `agent_lifecycle_and_heartbeat.md`
  - `work_intake_and_execution.md`
  - `task_execution_and_validation.md`
- `policies/`: operational policy modules.
- `skills/`: enforceable behavior and certification docs.
- `examples/`: copy-first examples for ticketing and coding patterns.
  - `agent_onboarding/agent/general/examples/python/` for docstrings, cleanup, logging, and pytest patterns.
  - `context_compass/examples/` for ticket/doc structure references.

Override rule
- Career-specific docs should contain only true deltas from this shared baseline.
- If content is shared across careers, keep it here instead of duplicating.

Unknowns Gate
- Apply the canonical policy in
  `agent_onboarding/agent/general/skills/unknowns_gate_reference.md`.
- Local onboarding guidance must treat unevidenced claims as UNKNOWN.
- Onboarding summaries must include concrete source pointers for promoted FACT claims.
