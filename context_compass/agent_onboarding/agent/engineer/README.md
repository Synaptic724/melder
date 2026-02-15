# Engineer Career

This folder is reserved for engineer-specific onboarding material that
extends or overrides the shared general career content under
`agent_onboarding/agent/general/`.

Add only engineer-specific skills, policies, or behavioral guidance here.
Shared defaults live in `agent_onboarding/agent/general/` and are
indexed in `agent_onboarding/agent/general/SKILLS.md`.

Key files
- SKILLS.md: engineer-specific read order
- skills/engineer_execution.md: engineer execution rules
- policies/engineer_quality_policy.md: quality bar for code changes
- behavioral_guidelines/engineer_workflow.md: execution flow guidance

DO NOT ASSUME / Unknowns Gate
Rule: No Unverified Claims.
Any statement that is not directly supported by evidence must be treated as UNKNOWN.

Evidence means at least one of:
- A specific source file reference (preferred: file + symbol/method/class name).
- A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be explicitly labeled UNKNOWN (or added to an Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:
- Mark it UNKNOWN.
- Identify the most likely evidence target (file + symbol).
- Investigate, then update the doc (or leave it UNKNOWN).
