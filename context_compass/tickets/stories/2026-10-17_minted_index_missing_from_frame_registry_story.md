# Story: minted_index_missing_from_frame_registry - the index remove_from_spell_index mints is known to the frame

## Metadata
- Story ID: STORY-2026-10-17-minted_index_missing_from_frame_registry
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-17T20:32:42Z
- Updated: 2026-10-17T20:32:42Z

## User Narrative
As an agent who separates a version into its own index with `remove_from_spell_index` - to keep it, try it on its
own or share it - I want the frame to know that index belongs to my conduit, so that the version's spell_id is found
by the frame-level lookups and other conduits can be granted it, parked or after a notch makes it active.

## Value / MRP Alignment
Which conduit owns which index is structure the frame records (its spell registry). An index a Book owns but the
frame does not list makes a live version - even an active one - unreachable by spell_id from the frame and
unshareable by spell_id, while the Book itself melds it.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; spellbook.py's (and, if the fix goes there,
  conduit.py's) holder releases it or carries the fix - melder_1, whose spell_id lookup fix meets this; an active
  board row; a component patch for the seam.
- EXECUTION_BOUNDARY: `Spellbook._apply_remove_from_index` (or the `Conduit.remove_from_spell_index` facade):
  register the minted index under the owning conduit in the frame registry once the Book is conjured, as a
  post-conjure `bind` registers its new index; regression tests; system docs with their indexes and the graph; the
  release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1's spell_id lookup fix: the frame step
  this story repairs comes before the Book step that fix changes).
- EXIT_GATE: the probe's M2 and M3 show the frame finding the minted index and its conduit, `get_spell_by_id` and
  `get_conduit_by_spell_id` answering, and the M3 grant accepted; regression tests pass with the GIL off and on;
  docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT if melder_1's lookup fix moves the frame step; DECISION_REQUEST if the owner wants a
  minted index registered only once it holds an active version.

## Requirements (Functional)
- After `remove_from_spell_index` on a conjured Book, the frame's spell registry lists the minted index under the
  Book's root conduit, so `find_index_for_spell` and `find_conduit_id_for_spell` find the separated version.
- That holds while the version stays parked and after a notch makes it active in the minted index; the existing
  destroy path keeps unregistering the index when it empties (`_destroy_spell_index`).

## Requirements (Non-Functional)
- No new lock or lock-order edge: the registration takes the frame lock alone, after the seam's Book-locked section,
  as the destroy path's unregistration does.

## Scope Boundaries
- In scope: the frame registration of the minted index.
- Out of scope: what `get_spell_by_id` answers once the conduit is found (melder_1's lookup fix); the binding
  signature an active version in a minted index takes (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes).

## Dependencies / Related Work
- melder_1's spell_id lookup fix (the owner's rule: a lookup by spell_id returns that spell or nothing).
- STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (the same family of index-membership records).

## Tasks (Implementation Checklist)
- [ ] Task: patch docs for the seam; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `remove_from_spell_index(spell_id=X)`: `frame.find_index_for_spell(X)` returns the minted index,
  `get_conduit_by_spell_id(X)` returns the owning root, and `get_spell_by_id(X)` no longer raises "Spell version
  <id> not found in any conduit." (what it returns is melder_1's rule).
- After a notch makes X active in the minted index: the same, and a borrower's `add_spell_to_contract(spell_id=X)`
  is accepted.
- After X moves back with `add_to_spell_index`, the emptied minted index is gone from the registry again.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_version_separated_into_its_own_index_is_found_by_spell_id`,
  `test_a_version_notched_active_in_its_own_index_can_be_granted_by_spell_id`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `get_spell_by_id` and `get_conduit_by_spell_id` raise ValueError for a
  version the conduit's own Book owns (parked or active), and a grant of it by spell_id raises the same error.

## Risks / Mitigations
- A walk over the frame registry now sees one more index per separated version; the walks are the existing ones.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- none.

## Decision Log
- 2026-10-17T20:32:42Z: filed under EPIC-2026-10-17-correctness_defects from sweep A3 (Notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py (cases M1-M3)
  - artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the frame's spell registry and the index remove_from_spell_index mints
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T20:32:42Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T20:32:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8251. `_apply_remove_from_index` mints `SpellIndex(initial_id=
    spell_id)` and repoints the spell without registering the new index in the frame's spell registry - the
    registration a post-conjure `bind` makes for its new index (`_register_single_spell_index`) - so
    `find_conduit_id_for_spell`, which walks that registry, cannot find the version. Probe: M1 (control) - French
    parked in English's index is found; M2 - French alone and parked in the minted index: `find_index_for_spell`
    None, `get_spell_by_id` and `get_conduit_by_spell_id` raise "Spell version <id> not found in any conduit."; M3 -
    French notched active there: the same, `meld(spell_id=French)` builds French, and a borrower's
    `add_spell_to_contract(spell_id=French)` raises that ValueError. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - src/melder/aether/spellbook/spellbook.py:5883-5888
  - src/melder/aether/spellbook/spellbook.py:4192-4237
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1288-1307
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py:1-149
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil0.txt:1-26
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil1.txt:1-26
  IMPACT: A live version its Book owns - active or parked - is unknown to its frame by spell_id and cannot be shared
    by spell_id.
  NEXT: The owner schedules the story; patch docs for the seam first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry under its owning
  conduit (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py (or conduit.py), which melder_1 holds; melder_1 is told by mailbox.
- Next: (1) the owner schedules it; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

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
