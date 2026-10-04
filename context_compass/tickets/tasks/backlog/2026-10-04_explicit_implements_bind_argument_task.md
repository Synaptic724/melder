

# Task: An explicit `implements=(...)` bind argument records contracts without a Protocol spellframe

## Metadata
- Task ID: TASK-2026-10-04-explicit-implements-bind-argument
- Story: STORY-2026-10-03-annotation-type-vs-category-matching
- Status: draft
- Owner: user
- Agent Name: unassigned
- Priority: p3
- Created: 2026-10-04T12:00:00Z
- Updated: 2026-10-04T12:00:00Z

## Objective
Since 0.2.8222 a spell records the Protocol it implements only when that Protocol IS its spellframe, so one
spell can declare one contract and cannot be grouped under a string category at the same time. Design and
land `bind(..., implements=(IProto, ...))`: each Protocol is checked as a contract frame is today and recorded
in `Spell.implemented_protocols`, so a Protocol annotation selects the spell while its `spellframe` stays free
for a category; the crystal records the tuple and the loaders hydrate it like the frame Protocol.

## Ticket Contract
- ENTRY_GATE: owner's DECISION on the surface (name, tuple-or-single, interaction with a Protocol frame); routed
  on `attention_board.md`; a patch lane (binding pipeline, Phase 3, crystallizer) because it extends the
  resolution contract and the record.
- EXECUTION_BOUNDARY: `bind.py`, `spell.py`, `spellbook.py`/`spellbinder.py` (the public verbs), `spell_crystal.py`,
  `restore_engine.py`, `graft_runner.py`, `record_version.py` (MINOR), their tests, README, release note, docs, graph.
- DEPENDENCIES: the 0.2.8222 kind rule (tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md).
- EXIT_GATE: a spell bound with `implements=` and a string category resolves for the Protocol annotation and is
  grouped by the category; record round trip; red-to-green regressions; docs, notch, note, rebuild.
- FAILURE_ESCALATION: DECISION_REQUEST on the fingerprint question (does `implements=` change the spell id?).

## Scope Boundaries
- In scope: the new argument through bind/bind_inactive/SpellBinder, the record, the loaders, Phase 3 reading
  `implemented_protocols` (already the contract key source).
- Out of scope: the depth of the structural check (its own task).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: parked in the backlog at the owner's word (2026-10-03 19:00 local: follow-ups are separate tickets).

## Steps / Checklist
- [ ] Owner DECISION on the surface and the fingerprint rule.
- [ ] Patch lane; implementation; regressions (bind, Phase 3, crystal round trip); release note; docs; graph.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The argument, its record and hydration, regressions, docs.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/spellbook tests/integration/melder/crystallizer -q -n 4 -p no:cacheprovider`

## Risks / Rollback Notes
- If `implements=` enters the fingerprint, affected spells change id once; if it does not, two bindings differing
  only by contracts share an id - the DECISION decides.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-04T12:00:00Z
  TYPE: FACT
  CLAIM: Phase 3 already reads `Spell.implemented_protocols` as the contract-key source and `Bind._classify_spellframe`
  fills it with the frame Protocol only, so the argument is a binding-surface and record change, not a matcher change.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1269-1300
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:304-326
  IMPACT: the lane's cost is in the public verbs, the crystal and the loaders.
  NEXT: owner DECISION when the lane opens.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-10-04T12:00:00Z: DRAFT, parked in the backlog. Opened as a follow-up of the 0.2.8222 kind rule.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
