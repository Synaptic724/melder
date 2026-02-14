# ctx_autonomy_policy

Purpose
- Apply CTX Autonomy ranking to developer ctx work.
- Keep file ctx strong enough to support downstream dir/component/architecture ctx.

Policy
- Use the CTX Autonomy rubric before accepting any file ctx update.
- Target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60.
- Ensure file ctx captures public surface, dependencies, error model, invariants, lifecycle, and testing.
- If code changed, refresh file ctx first, then regenerate dir ctx and resurvey higher layers.

Unknowns Gate (No Unverified Claims)
- Any statement not supported by evidence is UNKNOWN.
- Evidence means at least one of:
  - A specific source file reference (preferred: file + symbol/method/class name).
  - A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).
- If not evidenced => UNKNOWN.
- UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section).
- UNKNOWN items must be investigated by reading the relevant source(s).
- If investigation cannot be completed (missing source access, ambiguity, or time),
  the item must remain UNKNOWN and must not be promoted to fact.
- No reasonable assumptions. Do not infer behavior from naming, patterns,
  conventions, or typical frameworks. Only the code/docs count.

Developer emphasis
- Fidelity: every listed behavior must map to actual code paths.
- Coverage: include non-obvious error paths and side effects.
- Depth: specify invariants, inputs/outputs, and dependency rules.

References
- agent_onboarding/agent/general/policies/ctx_autonomy_policy.md
- agent_onboarding/agent/developer/policies/developer_quality_policy.md
