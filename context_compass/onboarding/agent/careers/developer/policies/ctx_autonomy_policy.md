# ctx_autonomy_policy

Purpose
- Apply CTX Autonomy ranking to developer ctx work.
- Keep file ctx strong enough to support downstream dir/component/architecture ctx.

Policy
- Use the CTX Autonomy rubric before accepting any file ctx update.
- Target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60.
- Ensure file ctx captures public surface, dependencies, error model, invariants, lifecycle, and testing.
- If code changed, refresh file ctx first, then regenerate dir ctx and resurvey higher layers.

Developer emphasis
- Fidelity: every listed behavior must map to actual code paths.
- Coverage: include non-obvious error paths and side effects.
- Depth: specify invariants, inputs/outputs, and dependency rules.

References
- context_compass/onboarding/agent/general/policies/ctx_autonomy_policy.md
- context_compass/onboarding/agent/careers/developer/policies/developer_quality_policy.md
