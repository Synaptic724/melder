# Context Compass Workflow (Epic / Story / Task)

## Purpose
Provide a consistent planning and tracking workflow that uses GitHub-style tickets and survives context compaction.

## Ticket Size Guidance
- Epic: big project or cross-cutting initiative with multiple stories.
- Story: medium scope that delivers a user- or system-facing slice and needs multiple tasks.
- Task: small, single deliverable that can stand alone.

## Folder Structure
- `epics/` - epic tickets
- `epics/completed/` - completed epic tickets with summary + date
- `stories/` - story tickets
- `stories/completed/` - completed story tickets with summary + date
- `tasks/` - task tickets
- `tasks/completed/` - completed task tickets with summary + date
- `templates/` - templates for all ticket types
- `architecture/` - C4 architecture docs for src and tests
- `components/` - C3/C2/C1 component docs for src and tests
- `completed/` - legacy completed ticket archive (pre-split)

## Workflow Steps
1. Choose the smallest ticket type that fits the scope:
    - Big project: epic -> stories -> tasks.
    - Medium scope: story -> tasks.
    - Small scope: task only.
2. Create the required ticket(s) using the templates.
3. Track progress using checkboxes (`- [ ]`) and keep status fields updated.
4. Keep links consistent (epic <-> story <-> task IDs) when using multiple levels.
5. Use the Ticket Microcycle continuously:
    - `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
6. For every meaningful finding, immediately append a ticket `## Notes` entry before any further investigation.
   - Use evidence ranges (`path:start_line-end_line`) rather than single-line anchors.
7. Update "Context / Handoff Summary" sections as work progresses.
8. Before closing a ticket:
    - Walk through what was delivered.
    - Ask the user to confirm the acceptance criteria are met.
9. After confirmation:
    - Add a short completion summary with the date.
    - Move the file to its matching completed folder (`epics/completed/`,
      `stories/completed/`, or `tasks/completed/`).

## DO NOT ASSUME / Unknowns Gate
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

## Status Discipline
- Update "Status" and "Updated" fields whenever work changes state.
- Prefer: draft -> ready -> in_progress -> blocked/done.
- If blocked, explain why and list the unblock action.

## Ticket Microcycle (Required)
- Route from `attention_board.md` to one active ticket at a time.
- Investigate until one meaningful finding is identified.
- Immediately document that finding in the ticket `## Notes` section before reading more.
- Use UNKNOWN as the default claim state; promote to FACT only with evidence.
- Do not implement from `UNKNOWN` or `HYPOTHESIS` without an evidence-backed decision.
- If investigation expands beyond the current subsystem or exceeds 10 files in one pass, add a `DECISION` note and request user confirmation before continuing.
- Score each note for compaction usefulness (`SCORE_0_TO_10`); improve notes below 8 before continuing.

## Microcycle Configuration
- Policy toggle source: `config/context_compass_config.yaml`.
- Default mode is `enabled: true` with strict gate enforcement.
- If disabled (`enabled: false`), use relaxed mode:
  - Keep investigate->document notes for meaningful findings.
  - Require note updates before implementation and validation transitions.
  - Keep UNKNOWN->FACT promotion evidence requirements unchanged.

## Completion Summary Format
At the top of the completed ticket, add:

- Completed: YYYY-MM-DD
- Summary: <1-3 lines describing what was delivered>

## Context Compaction Rule
Before context compaction or major handoff:
- Follow `CONTEXT_COMPACTION.md`.
- Ensure the active tickets contain accurate handoff summaries.


## Agent Operating Notes (Optional but Recommended)
This section exists to reduce “process drift” when the workflow is executed by multiple humans and/or AI agents.

### Definition of Done (DoD) for a ticket
Before moving a ticket to a completed folder:
- [ ] Acceptance criteria are explicitly met (not “mostly done”).
- [ ] Any new/changed behavior has been documented in the relevant C4/C3 docs.
- [ ] Unknowns introduced during work are either resolved (with evidence) or recorded as **UNKNOWN** with investigation pointers.
- [ ] Completion summary includes the *user-visible* outcomes and any important caveats.

### When a task changes architecture or components
If a ticket modifies system behavior, make a small doc update as part of the same change:
- Update `architecture/src_architecture.md` when system boundaries/boot/ownership/invariants change.
- Update `components/src_components.md` when ownership, wiring, registries, or call flows change.
- Keep diagrams in sync with the change.

### Evidence discipline still applies
Even inside tickets:
- Prefer `path/to/file:Symbol` evidence when describing a behavior change.
- If you can’t confirm, mark it **UNKNOWN** and create a follow-up task for investigation.

### Active Notes Discipline
- Every active ticket must include a `## Notes` section.
- New notes entries should be append-only and include:
  - `DATE`
  - `TYPE` (`FACT` | `UNKNOWN` | `HYPOTHESIS` | `DECISION` | `PLAN` | `MEASURE` | `RISK`)
  - `CLAIM`
  - `EVIDENCE` (`path:start_line-end_line`; for a single line use `start=end`)
  - `IMPACT`
  - `NEXT`
  - `REREAD` (`REQUIRED` | `HELPFUL`)
  - `SCORE_0_TO_10` (compaction usefulness score)
- Legacy entries may omit newer fields; do not rewrite history unless correcting factual errors.
