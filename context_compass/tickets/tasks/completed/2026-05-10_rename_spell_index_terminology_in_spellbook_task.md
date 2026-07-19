# Completed: 2026-05-10T12:04:09Z
# Summary: Cleaned the remaining SpellIndex-derived `lineage` wording in `spellbook.py` and `ispellbook.py` and verified the two-file compile ring.
# Task: Rename Spell Index Terminology In Spellbook

## Metadata
- Task ID: TASK-2026-05-10-rename-spell-index-terminology-in-spellbook
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T11:34:36Z
- Updated: 2026-05-10T11:36:26Z

## Objective
Rename the remaining SpellIndex-derived `lineage` wording in `spellbook.py`
and `ispellbook.py` so those files stop teaching SpellIndex as lineage
authority when they really mean the SpellIndex container/key itself.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved `spellbook.py` +
  `ispellbook.py` as the next SpellIndex rename target after the
  SpellSystemStates slice.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/utilities/interfaces/ispellbook.py`
  - any direct tests that break only because of wording/error-message
    expectations in this slice
- DEPENDENCIES:
  - STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
  - the completed creation-gate and SpellSystemStates rename slices
- EXIT_GATE: the Spellbook/interface layer uses `index` wording consistently
  where it is really talking about `SpellIndex`, without drifting into
  unrelated outward AR/viewer surfaces.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one of these call sites is
  actually expressing a real lineage semantic instead of SpellIndex container
  semantics.

## Scope Boundaries
- In scope:
  - docstrings
  - comments
  - error messages
  - small helper wording around `SpellIndex` lookups
- Out of scope:
  - `spell_index.py`
  - `ispellindex.py`
  - outward AR/viewer/descriptor exposure
  - broad runtime API redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the bounded Spellbook/interface wording cleanup is landed
  and the focused compile check is green.

## Steps / Checklist
- [x] Rename SpellIndex-derived `lineage` wording in `spellbook.py`.
- [x] Rename SpellIndex-derived `lineage` wording in `ispellbook.py`.
- [x] Update any focused test expectations broken by the wording changes.
- [x] Run focused validation for the touched ring.

## Deliverables
- Spellbook SpellIndex wording uses `index` instead of `lineage`
- interface contract wording matches the same model

## Files / Paths Impacted
- src/melder/spellbook/spellbook.py
- src/melder/utilities/interfaces/ispellbook.py

## Validation
- Executed:
  - `python -m py_compile src/melder/spellbook/spellbook.py src/melder/utilities/interfaces/ispellbook.py`
- Result:
  - compile validation passed

## Risks / Rollback Notes
- Risk: some references in these two files are expressing real mutation/history
  semantics rather than simple SpellIndex-key semantics.
  Rollback: keep those specific phrases unchanged and record the reason.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No outward AR/viewer drift.
- [ ] No broad repo-wide rename outside the bounded Spellbook/interface layer.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-10T11:34:36Z
  TYPE: FACT
  CLAIM: The next SpellIndex rename surface is narrower than the
    SpellSystemStates slice. In `spellbook.py` and `ispellbook.py`, most of the
    remaining `lineage` references are in docstrings, comments, and a few local
    error strings that describe `SpellIndex.id` or the SpellIndex container
    itself rather than a separate mutation-lineage authority.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:374-378
  - src/melder/spellbook/spellbook.py:597-598
  - src/melder/spellbook/spellbook.py:1157-1221
  - src/melder/spellbook/spellbook.py:1269-1279
  - src/melder/utilities/interfaces/ispellbook.py:14-17
  - src/melder/utilities/interfaces/ispellbook.py:452-469
  - src/melder/utilities/interfaces/ispellbook.py:518-534
  IMPACT: This is a good bounded cleanup lane because it is mostly wording and
    should not require another wide caller/test rename like SpellSystemStates did.
  NEXT: patch the two files and run a focused validation pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T11:36:26Z
  TYPE: MEASURE
  CLAIM: The bounded Spellbook/interface wording cleanup is now landed. The
    remaining SpellIndex-derived `lineage` language in `spellbook.py` and
    `ispellbook.py` was reduced to `index` wording where those files were
    really describing `SpellIndex` keys, lookups, and version ownership rather
    than a separate lineage authority.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:374-403
  - src/melder/spellbook/spellbook.py:590-598
  - src/melder/spellbook/spellbook.py:959-1279
  - src/melder/spellbook/spellbook.py:1713-1785
  - src/melder/utilities/interfaces/ispellbook.py:14-17
  - src/melder/utilities/interfaces/ispellbook.py:452-534
  - src/melder/utilities/interfaces/ispellbook.py:693-752
  - validation_result:
    `python -m py_compile src/melder/spellbook/spellbook.py src/melder/utilities/interfaces/ispellbook.py`
  IMPACT: The next SpellIndex cleanup can move outward from the internal
    Spellbook layer without these two files still reinforcing the old
    lineage-first wording.
  NEXT: return the slice for review and decide whether the next target is the
    outward viewer/descriptor/static-command exposure layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task owns the SpellIndex wording cleanup in the Spellbook/interface layer
before we move outward into AR/viewer exposure.
