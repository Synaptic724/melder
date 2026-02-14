# ticketing

Purpose
- Define the ticketing system used to plan, execute, and close work in this repo.

Ticket types
- Epic: big project or cross-cutting initiative with multiple stories.
- Story: medium scope, user- or system-facing slice that can stand alone or live under an epic.
- Task: small, single deliverable that can stand alone.

Templates
- `templates/epic_template.md`
- `templates/story_template.md`
- `templates/task_template.md`

Deep descriptive model (required)
Each ticket must be specific, evidence-based, and durable. Avoid vague goals.

Required elements
- Problem / Opportunity
- Context (why now, relationship to architecture)
- MRP alignment
- Goals / Non-goals
- Scope boundaries
- Requirements (functional + non-functional)
- Acceptance criteria (observable outcomes)
- Risks / Mitigations
- Validation plan (tests or verification)
- Decision log
- Notes (active findings with evidence pointers)
- Context / Handoff summary

Workflow rules
1) Choose the smallest ticket type that fits the scope:
   - Big project: epic -> stories -> tasks.
   - Medium scope: story -> tasks.
   - Small scope: task only.
2) Keep links consistent (epic <-> story <-> task IDs) when using multiple levels.
3) Track progress with checkboxes and status fields.
4) Use the Ticket Microcycle while active:
   - `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
5) For every meaningful finding, update `## Notes` immediately before any further investigation.
6) Treat new claims as `UNKNOWN` by default; promote to `FACT` only with evidence.
7) If investigation expands beyond the current subsystem or exceeds 10 files in one pass, add a `DECISION` note and request user confirmation.
8) Update Context / Handoff Summary as work changes.
9) Before closing a ticket:
   - Walk through what was delivered.
   - Ask the user to confirm acceptance criteria.
10) After confirmation:
   - Add a completion summary + date.
   - Move the ticket to its matching completed folder (`epics/completed/`,
     `stories/completed/`, or `tasks/completed/`).

Notes format requirement
- New note entries should include:
  - `DATE`
  - `TYPE` (`FACT` | `UNKNOWN` | `HYPOTHESIS` | `DECISION` | `PLAN` | `MEASURE` | `RISK`)
  - `CLAIM`
  - `EVIDENCE` (`path:start_line-end_line`; use `start=end` for single-line evidence)
  - `IMPACT`
  - `NEXT`
  - `REREAD` (`REQUIRED` | `HELPFUL`)
  - `SCORE_0_TO_10` (compaction usefulness score; improve entries below 8)
- Keep notes append-only except when correcting factual errors.
- Legacy entries may omit newer fields; do not rewrite history unless correcting factual errors.

Status discipline
- Update Status and Updated fields on each state change.
- Prefer: draft -> ready -> in_progress -> blocked/done.
- If blocked, document the blocker and the unblock action.

Validation reporting
- Never claim tests ran unless they actually ran.
- If not run, say "Not run" and explain why.

References
- `WORKFLOW.md`
- `SKILLS.MD`
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/agent/general/skills/active_documentation.md`
