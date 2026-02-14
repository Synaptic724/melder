# developer_quality_policy

Purpose
- Establish the quality bar for developer changes.

Policy
- Every touched function/class must have a rich docstring aligned with the behavior.
- Tests must be added or updated for behavioral changes.
- Avoid drive-by refactors; limit edits to the requested scope.

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

Exceptions
- Only allowed with explicit user approval, documented in the response.

References
- `AGENTS.MD`
- `agent_onboarding/agent/general/skills/testing/evidence_reporting.md`
