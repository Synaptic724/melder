# developer_quality_policy

Purpose
- Establish the quality bar for developer changes.

Policy
- Every touched function/class must have a rich docstring aligned with the behavior.
- Tests must be added or updated for behavioral changes.
- Avoid drive-by refactors; limit edits to the requested scope.
- Follow the CRUD vs Query API split: single-table changes use CRUD, multi-table atomic work uses Query API.

Exceptions
- Only allowed with explicit user approval, documented in the response.

References
- `src/AGENTS.md`
- `context_compass/onboarding/agent/general/skills/testing/evidence_reporting.md`
