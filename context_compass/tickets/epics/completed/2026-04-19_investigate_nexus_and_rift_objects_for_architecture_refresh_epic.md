# Epic: Investigate Nexus And Rift Objects For Architecture Refresh
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-19-investigate-nexus-and-rift-objects-for-architecture-refresh
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T11:02:52Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-19
- Related Program/Initiative: Nexus/Rift architecture documentation fidelity

## Problem / Opportunity
The current April 19 AR doc lanes already captured broad `Nexus -> Rift ->
RiftSpace` drift, but the user explicitly requested a deeper object-first pass
over `Nexus` and `Rift` before another architecture/components update. The
existing comparison and sync tasks are broad documentation lanes, not dedicated
object-model investigations.

## MRP Alignment (Most Reasonable Product)
The durable docs need to be rooted in the real object contracts, not in a
partial memory of recent AR refactors. The smallest trustworthy slice is:
- investigate `Nexus` as an owned singleton object,
- investigate `Rift` as an owned live runtime object,
- then update the relevant `src_architecture.md` and `src_components.md`
  sections from those object-level findings.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a new object-first investigation
  lane for `Nexus` and `Rift` before further architecture/components edits.
- EXECUTION_BOUNDARY: bounded investigation and documentation updates across:
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/rift/rift.py`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - active ticket and board state
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_compare_architecture_docs_against_live_nexus_rift_task.md
  - tickets/tasks/2026-04-19_sync_nexus_rift_architecture_docs_to_live_model_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: `Nexus` and `Rift` each have one evidence-backed task trail, the
  relevant architecture/component sections are updated from those findings, and
  residual UNKNOWNs are explicit instead of implied.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if either object cannot be
  understood from its bounded file without widening into additional owned
  helpers/managers beyond the current task boundary.

## Goals (Outcomes)
- Build one bounded investigation trail for `Nexus`.
- Build one bounded investigation trail for `Rift`.
- Update the relevant `src_architecture.md` and `src_components.md` sections
  from those object-level findings.
- Record any remaining UNKNOWNs instead of bluffing completeness.

## Non-Goals (Explicit Exclusions)
- Do not perform a repo-wide AR documentation sweep in this epic.
- Do not modify runtime code in this epic unless a doc fix requires a proven
  comment/docstring correction inside the bounded object file.
- Do not reopen unrelated ACL, room, or command-system lanes here.

## Scope Boundaries
- In scope:
  - `Nexus` object investigation and doc alignment
  - `Rift` object investigation and doc alignment
  - relevant architecture/component doc sections for those two objects
- Out of scope:
  - `RiftSpace` deep dive as a primary lane
  - manager/helper deep dives unless object-local evidence proves they are
    required
  - unrelated runtime behavior changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: both object tasks are now documented and the relevant
  architecture/component lines were refreshed from those findings.

## Success Metrics
- The `Nexus` task records enough evidence to update the `Nexus` ownership,
  lifecycle, registry, and refresh sections without assumption.
- The `Rift` task records enough evidence to update the `Rift` ownership,
  lifecycle, frame-contract, gate, and room sections without assumption.
- The final doc edits for this lane are traceable back to the task notes.

## Requirements (Functional + Non-Functional)
- Investigate `Nexus` and `Rift` separately.
- Keep each object task bounded to its object file plus the two target docs.
- Append evidence-backed notes before further scope expansion.
- Preserve UNKNOWN-first discipline for anything not directly proven.
- Keep changes reviewable and object-scoped.

## Constraints / Assumptions
- `nexus.py` and `rift.py` both exceed or approach the read-window limit, so
  source reads must stay chunked and ordered.
- The prior April 19 compare/sync tasks remain valid history, but they do not
  replace this deeper object-first pass.
- The architecture update should follow the live object contracts, not the
  older task summaries.

## Dependencies / External References
- `codex/context_compass/attention_board.md`
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`
- `src/melder/aether/nexus/nexus.py`
- `src/melder/aether/nexus/rift/rift.py`

## Milestones (Track Progress)
- [x] Milestone 1: `Nexus` object investigation is complete and documented
- [x] Milestone 2: `Rift` object investigation is complete and documented
- [x] Milestone 3: architecture/component docs are updated from those findings

## Stories (Required to Complete)
- None. The user explicitly requested a direct epic + per-object task split for
  this bounded investigation lane.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-04-19-investigate-nexus-object-for-architecture-refresh
- [ ] Task: TASK-2026-04-19-investigate-rift-object-for-architecture-refresh
- [ ] Task: Verify Ticket Microcycle enforcement across the object tasks.

## Acceptance Criteria (Epic Done)
- `Nexus` and `Rift` each have one bounded task with evidence-backed notes.
- The relevant `src_architecture.md` and `src_components.md` sections have been
  refreshed from those notes or explicit UNKNOWNs remain recorded.
- The attention board routes to the active object task during investigation.

## Risks / Mitigations
- Risk: the objects may depend on helper/manager files not obvious from the top
  of the file.
  Mitigation: stay bounded first; if that is insufficient, record a
  `DECISION_REQUEST` instead of silently widening scope.
- Risk: prior broad doc-sync work may tempt a shallow â€œalready doneâ€ answer.
  Mitigation: use the object files as the primary evidence source in this epic.

## Applicable Anti-Patterns
- [ ] No â€œdocs are already syncedâ€ claim without rereading the object files.
- [ ] No helper/manager scope expansion without evidence that the object file is
      insufficient.
- [ ] No closure while one of the object tasks lacks source-backed notes.

## Validation / Test Approach
- Documentation investigation first.
- If doc-only edits land, validation will be recorded truthfully at task level.

## Rollout / Adoption Plan
- Complete the `Nexus` task first.
- Continue into the `Rift` task second.
- Apply any doc refresh once the object findings are explicit.

## Open Questions
- Does the bounded object pass prove enough on its own, or will one or both
  tasks need a later helper/manager escalation?

## Decision Log
- 2026-04-19T11:02:52Z: Chose a direct epic + two task split because the user
  explicitly asked for per-object investigation tasks rather than another broad
  doc-only lane.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T11:02:52Z
  TYPE: PLAN
  CLAIM: The new lane exists because the user asked for a deeper object-first
    reinvestigation of `Nexus` and `Rift` before another doc refresh. The
    current April 19 compare/sync tasks are broad documentation lanes, not
    per-object object-model investigations.
  EVIDENCE:
  - codex/context_compass/attention_board.md:29-30
  - src/melder/aether/nexus/nexus.py:60-80
  - src/melder/aether/nexus/rift/rift.py:27-66
  IMPACT: This epic should not pretend the broader doc-sync lane is the same
    thing as the deeper object pass the user asked for.
  NEXT: create one task for `Nexus`, one task for `Rift`, and route the board
    to the `Nexus` task first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-task tradeoffs, and the handoff
  point between the two object investigations.
- Reference the object task evidence instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic stages a deeper object-first pass over `Nexus` and `Rift` before any
further architecture/component refresh. `Nexus` is the first active task.