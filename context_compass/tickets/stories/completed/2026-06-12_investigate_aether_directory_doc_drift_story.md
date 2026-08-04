<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Story: Investigate Aether Directory Doc Drift

## Metadata
- Story ID: STORY-2026-06-12-investigate-aether-directory-doc-drift
- Epic: EPIC-2026-06-12-investigate-source-system-doc-drift-excluding-mutation-and-crystallizer
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p0
- Created: 2026-06-12T13:00:58Z
- Updated: 2026-06-12T13:00:58Z

## User Narrative
As the documentation maintainer, I want the meaningful `src/melder/aether/**`
runtime surfaces mapped against the live code, so the architecture,
components, and graph docs stop drifting on the main runtime substrate.

## Value / MRP Alignment
`aether` is the highest-value first directory because it contains the runtime
substrate, conduits, dev-ops state, and the `aether/spellbook` path family that
already surfaced the first concrete drift seam.

## Ticket Contract
- ENTRY_GATE: the new source-system doc-drift epic is active and the first
  concrete drift seam already points into the `aether/spellbook` path family.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/**`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/system_docs/src_graph.json`
- DEPENDENCIES:
  - `tickets/tasks/2026-06-12_investigate_current_source_system_doc_drift_task.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/system_docs/src_graph.json`
- EXIT_GATE: concrete `aether`-scoped drift is inventoried and the first
  bounded refresh slice is either completed or split into child tasks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  the lane spills into excluded mutation-research or crystallizer work.

## Requirements (Functional)
- verify current `aether` doc claims against live `src/melder/aether/**` code
- patch directly evidenced drift only
- keep low-signal files out of the mapping surface

## Requirements (Non-Functional)
- preserve evidence-backed section and graph contracts
- skip `__init__`, metadata shims, caches, and other low-signal junk

## Scope Boundaries
- In scope:
  - `aetheric_frame`
  - `conduit`
  - `dev_ops`
  - `aether/spellbook`
- Out of scope:
  - `mutation_research`
  - `crystallizer`
  - `__pycache__`
  - package metadata files with no real runtime architecture value

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the first real drift finding already sits in the
  `aether/spellbook` path family, so `aether` is the correct first directory lane.

## Dependencies / Related Work
- bootstrap task: `TASK-2026-06-12-investigate-current-source-system-doc-drift`
- prior reference:
  `tickets/tasks/completed/2026-04-10_refresh_src_architecture_and_components_for_recent_rift_and_meld_changes.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-06-12-investigate-current-source-system-doc-drift - bootstrap drift inventory and first bounded slice
- [ ] Task: TBD - first bounded `aether` doc refresh slice if the bootstrap task proves it should split
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `aether`-scoped drift is concrete and evidence-backed
- low-signal files are excluded from the mapping surface
- the next `aether` patch slice is explicit or complete

## Validation / Test Plan
- doc and graph consistency scans only unless a later patch touches executable
  helpers or validation tooling

## UX / API / Data Notes
- current likely drift includes public conjure posture language and old
  spellbook path references inside `aether`

## Risks / Mitigations
- Risk: `aether` is broad enough to become a rewrite blob.
  Mitigation: keep work bounded to evidenced seams and split child tasks if needed.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether the first `aether` patch slice should stop at path-map + conjure
  posture drift or also include nearby `spellbook_configuration` naming drift

## Decision Log
- 2026-06-12: start with `aether` because the first concrete mismatch is in the
  live `aether/spellbook` tree and its associated docs/graph entries.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - aether directory drift
  - path-map drift
  - conjure posture drift
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-12T13:00:58Z
  TYPE: FACT
  CLAIM: The first concrete drift seam is already `aether`-scoped: the docs
    and graph still cite `src/melder/spellbook/...`, while the live code is
    under `src/melder/aether/spellbook/...` and the public conjure API uses
    `dynamic`, not `automatic`.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-12_investigate_current_source_system_doc_drift_task.md:1-95
  IMPACT: The first bounded `aether` story slice can start immediately without
    more story-level discovery.
  NEXT: continue the active bootstrap task and split the first concrete patch
    task if the seam widens past a small edit boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This is the first directory story under the new doc-drift epic. It starts from
the already-proven `aether/spellbook` path and conjure-posture drift seam.
