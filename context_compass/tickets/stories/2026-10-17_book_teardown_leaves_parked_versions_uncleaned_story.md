# Story: book_teardown_leaves_parked_versions_uncleaned - a Book's teardown retires its parked versions too

## Metadata
- Story ID: STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-17T21:13:35Z
- Updated: 2026-10-17T21:13:35Z

## User Narrative
As an agent who staged and separated versions in a Book and then tore the Book down, I want every version the Book
owned - the parked ones and an index only they hold included - retired with it, so that no version of a dead Book
still reads as live or refuses its own cleanup.

## Value / MRP Alignment
Melder's infrastructure cleans up its own state (owner ruling, src_architecture "Runtime Model"); a Spell and its
SpellIndex are Melder's records of a version. Today the parked versions of a torn-down Book stay uncleaned, and
`Spell.cleanup()` on one raises "Spellbook has already been cleaned." - a record that reads as live and can never be
retired.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; melder_1 has released spellbook.py (its rule-2
  hold); an active board row; a component patch for the Book teardown.
- EXECUTION_BOUNDARY: `Spellbook._cleanup_spells` (or the step of `_cleanup_components` that clears
  `_inactive_spells`): the local teardown of every parked version, as the parked branch of `_dispose_spell` runs it
  (`_spellbook_cleanup` set, then `Spell.cleanup()`), and `SpellIndex.cleanup()` of every index only parked versions
  hold, best-effort and logged like the active loop; regression tests; the system documents (the cleanup sequence,
  the Spellbook Core component) with their indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links); melder_1's release of
  spellbook.py (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).
- EXIT_GATE: probe T2 and T3 show French and the minted index cleaned after teardown and `French.cleanup()` returning;
  T1, T4 and T5 unchanged; regression tests pass with the GIL off and on; docs, notch and the rebuild with both
  checks OK.
- FAILURE_ESCALATION: CONFLICT while spellbook.py is held; DECISION_REQUEST if retiring a parked version turns out to
  need more than its local teardown.

## Requirements (Functional)
- Book teardown cleans every version the Book owns, active and parked, and every SpellIndex it owns, including an
  index only parked versions hold.
- A parked version's teardown is local: it is on no resolution map, in no lineage registration and in no frame lookup
  of its own, so only `Spell.cleanup()` (with `_spellbook_cleanup` set) and its index's cleanup run.
- After the teardown, `Spell.cleanup()` on any of the Book's versions returns without raising.

## Requirements (Non-Functional)
- The lock order stays: spell locks are taken under the Book lock, as the active loop takes them; nothing new runs
  user code.

## Scope Boundaries
- In scope: parked versions and parked-only indexes at Book teardown.
- Out of scope: frame claims (the two signature stories), borrowers' copies (the ward's teardown), the record (it
  already evicts the Book's custody in both locations and its index crystals).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes).

## Dependencies / Related Work
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the same probe's case T4 (a claim that outlives the
  Book) belongs there.

## Tasks (Implementation Checklist)
- [ ] Task: patch docs for the Book teardown; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After its root's teardown, a Book's parked version (on a shared index, or alone in a minted one) reads cleaned,
  its parked-only index reads cleaned, and `cleanup()` on the version returns.
- An active-only Book and a Book with managed versions tear down as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_book_teardown_cleans_its_parked_versions` and
  `test_book_teardown_cleans_an_index_only_parked_versions_hold`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `spell.cleaned` is False for a parked version of a torn-down Book, and
  `spell.cleanup()` raises RuntimeError "Spellbook has already been cleaned.".

## Risks / Mitigations
- Cleaning a parked Spell drops its factory and any compiled artifact; nothing can meld it once its Book is gone, so
  nothing is lost.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- none.

## Decision Log
- 2026-10-17T21:13:35Z: filed under EPIC-2026-10-17-correctness_defects from sweep A7 (Notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py (cases T1-T3, T5)
  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - parked versions and parked-only indexes at Book teardown
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:13:35Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T21:13:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `Spellbook._cleanup_spells` walks `_spells` - the active
    version of each index - unregistering, cleaning each Spell and its index; `_cleanup_components` then clears
    `_inactive_spells` without cleaning one of them, and an index only parked versions hold is never reached. The
    parked branch of `_dispose_spell` shows the teardown a parked version needs (`_spellbook_cleanup` set, then
    `Spell.cleanup()`). Afterwards a direct `Spell.cleanup()` routes to the Book (`_direct_removal_route`,
    `cleanup_and_remove_spell`), which raises "Spellbook has already been cleaned.". Probe T2: after the root's
    teardown English is cleaned and French, parked on its index, is not; `French.cleanup()` raises. T3: French
    separated into its own minted index - neither French nor that index is cleaned. T1 (active only) and T5 (the
    pools of an active and a parked managed version, both unregistered) are right. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:405-556
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py:1-231
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt:1-30
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt:1-30
  IMPACT: A dead Book's parked versions read as live and can never be retired.
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py; then patch docs for the Book teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
- Scope: Book teardown retires parked versions and parked-only indexes (Requirements). Defect proven on 0.2.8252
  (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py, which melder_1 holds.
- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

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
