

# Story: map_dependency_watchers_and_announcers - every dependency watcher and announcer measured

## Metadata
- Story ID: STORY-2026-10-25-map_dependency_watchers_and_announcers
- Epic: EPIC-2026-10-25-dependency_watchers_listen_for_names
- Status: ready
- Owner: Mark (owner)
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-25T02:26:33Z
- Updated: 2026-10-25T02:26:33Z

## User Narrative
As an agent iterating on providers in a live world, I want every way a waiting consumer can miss its provider's
arrival known and measured, so that one fix covers all of them instead of one event at a time.

## Value / MRP Alignment
The one measured case (a class-annotated consumer, a provider under a Protocol) points at a keying split between
watchers and announcers. Mapping the whole surface before designing the fix keeps the fix structural.

## Ticket Contract
- ENTRY_GATE: the epic is routed; STORY-2026-10-25-probe_and_purge_reach_every_version has landed, or the owner says
  to run in parallel.
- EXECUTION_BOUNDARY: read-only in src; a matrix probe and diagnostics under an artifact folder of this epic; notes
  here and a synthesis on the epic.
- DEPENDENCIES: the reproducer (Artifact Links); the 0.2.8222 task's out-of-scope list.
- EXIT_GATE: the matrix measured the GIL off and on; each miss traced to the source range that decides it; a
  DECISION_REQUEST with costed fix options on the epic.
- FAILURE_ESCALATION: DECISION_REQUEST when a miss is by design; BLOCKER when a cell cannot be isolated.

## Requirements (Functional)
- The matrix: socket kind (UNRESOLVED_INPUT, AMBIGUOUS_INPUT, OVERRIDE_REQUIRED, NORMAL collection; SpellMap and
  SpellContract defaults for contrast) x annotation kind (class, Protocol, string name, list[...]) x provider
  binding shape (bare, string category, Protocol frame, existing object) x change event (bind after conjure,
  bind_inactive and notch, notch away and back, add_to_spell_index and remove_from_spell_index, cleanup_spell, a
  contract added and removed, an ownership transfer).
- Each cell answers: does the consumer's next meld see the change; which keys the watcher holds; which keys the event
  stages; whether the consumer is marked.
- Read in full: Phase 3's key builders and matcher, the watcher index, the dirty marker, each announcer's staging and
  Phase 4's cycle heuristic's name keying.

## Requirements (Non-Functional)
- Behaviour claims from public calls; internal reads only for the diagnosis, labelled as such.

## Scope Boundaries
- In scope: the cells above, measured on 0.2.8267 or the tree current when S1 starts.
- Out of scope: any src edit; the fix design beyond costed options.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: filed with the epic on the owner's ask (chat 2026-10-25); scope and probe defined.

## Dependencies / Related Work
- EPIC-2026-10-25-dependency_watchers_listen_for_names
- The S2 story's meld-identity map (FACT notes of 2026-10-25T02:01:57Z).

## Tasks (Implementation Checklist)
- [ ] Task: read the keying and announcing code in full and record the map.
- [ ] Task: the matrix probe, run the GIL off and on, its run file in the artifact folder.
- [ ] Task: the root cause and the fix options on the epic for the owner.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Every cell measured, the GIL off and on, with the probe and its runs beside the story.
- Each miss traced to the source range that decides it.
- The owner has the fix options on the epic.

## Validation / Test Plan
- The matrix probe; no product tests (investigation only).

## UX / API / Data Notes
- None (investigation only).

## Risks / Mitigations
- The matrix is large: cells that share code paths are grouped once the code reading shows they cannot differ.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- UNKNOWN: which cells miss.

## Decision Log
- 2026-10-25T02:26:33Z: filed with the epic on the owner's ask.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/diag_class_annotated_consumer_after_notch_back.py (the reproducer this story starts from)
  - artifacts/correctness_defects_20261017/runs/diag_class_annotated_consumer_after_notch_back_0_2_8267.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the matrix probe and its runs join the artifacts when S1 runs

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - watcher keys, match keys and announced keys
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; filed 2026-10-25T02:26:33Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-25T02:26:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Start from the one measured miss and widen: read `_dependency_key_for_dep` and `_spell_keys_for` (what a
    socket is keyed by and what it matches), `_extract_collection_frame_keys` and `mark_collection_dependents_dirty`
    (what is watched and how a mark finds it), `_default_dirty_marker` and each announcer's staging (bind's
    `_try_update_staged_binding_keys`, the notch strategy's `binding_key`, the index moves, cleanup_spell, the
    contract and transfer paths); then probe the matrix cell by cell, the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:883-926
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1889-1929
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1625-1696
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:841-877
  - src/melder/aether/spellbook/spellbook.py:5526-5598
  IMPACT: The map comes from the code that decides each cell, so the fix options cover every path.
  NEXT: Begin when the probe-and-purge story lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: the watcher/announcer matrix and the root cause, read-only in src.
- State: ready, melder_1; nothing run yet.
- Next: (1) the code reading of the PLAN note; (2) the matrix probe; (3) the fix options on the epic.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
