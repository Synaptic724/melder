

# Epic: index_binding_risks_and_gaps - what one binding per index risks and leaves open, labeled to investigate

## Metadata
- Epic ID: EPIC-2026-10-25-index_binding_risks_and_gaps
- Status: ready
- Owner: Mark (owner)
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-25T12:47:21Z
- Updated: 2026-10-25T14:58:20Z
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness - structure that is wrong or stuck (the owner, 2026-10-14)

## Problem / Opportunity
The owner asked (chat 2026-10-25): "you said there were possible risks too you should label those risks in an epic
and talk about the gaps here so we can remember them and investigate them".

S2 of EPIC-2026-10-17-correctness_defects landed at 0.2.8273: every version of a SpellIndex is bound the way its
first version was, so staging and index moves refuse another binding, a notch keeps the index's address and refuses
one another spell holds, records below 5.0.0 are refused and the creation cache is generation 24.

The first list labeled five risks and fourteen gaps. The owner cut it the same day (DECISION note): naming is
the caller's contract - a container like Autofac resolves exactly what was registered and does not babysit names - so
the naming items and the rule's own consequences are not gaps. What is left can break a running world or hide a
failure. Each label says how it is known: MEASURED (run with public calls), READ (read in source, not run), NOT RUN,
or CROSS-REF (owned by another ticket). Labels keep their first numbers so the notes still read.

Open, each with what it is, where it lives (lines on 0.2.8275), how to reproduce it, why it matters and the next
step:
- GAP-1 (p1, MEASURED on 0.2.8273 and 0.2.8275): checkpoint retention can delete a new world's checkpoints as soon
  as they are written. `enforce_cache_retention` keeps a profile folder's highest `checkpoint_number`s (100 files in
  these runs), but the number starts again at 1 in every new world, so a folder holding earlier worlds' checkpoints
  with higher numbers deletes the new ones and `list_cached_checkpoint_ids` stops listing them. The device's
  `default` folder holds 100 numbered 3 and 4 - 96 of them records 5.0.0 refuses to read, which the sort still keeps
  over live ones. Expert examples 02, 09, 24 and 27 (checkpoints numbered 1 and 2) fail with that folder copied in
  and pass without it; twenty runs of their own fill the folder and still pass. Not caused by S2; found at its
  landing.
  Where: src/melder/crystallizer/asset_management/crystallizer_cache.py:177-264 (`enforce_cache_retention`); its sort
  key `_creation_order` (229-252) reads `checkpoint_number` with no record-version check.
  Reproduce: artifacts/index_binding_risks_20261025/scripts/gap1_checkpoint_retention.sh, read-only on the repository
  (artifacts/index_binding_risks_20261025/runs/gap1_checkpoint_retention_0_2_8275.txt).
  Why it matters: a profile folder shared by worlds - earlier runs, other programs, tests - loses new checkpoints
  with no error, and a restore that needs them fails later.
  Next: a probe of two worlds writing one profile, then the fix options (an age key that is not a per-world
  counter; a record the reader refuses counted as dead weight).
- GAP-5 (p3, READ): Book teardown releases its frame claims by key, the one release not by spell_id; S2's plan item
  (d), a hardening, was not done.
  Where: src/melder/aether/spellbook/spellbook.py:472-479, inside `_cleanup_components` (407-559).
  Reproduce: none yet - read, not run.
  Why it matters: if any path leaves a key routed in a Book while another spell holds that key's claim, the Book's
  teardown frees an address it does not own.
  Next: a probe of teardown after splits, index moves and transfers; then release by spell_id.
- GAP-6 (p3, READ): four writers of the address maps sit outside S2's checks and set an address with no
  compare-and-set.
  Where: src/melder/aether/spellbook/spellbook.py:1796-1868 (`_reactivate_contracted_spell`, a borrower writing its
  lender's address back, line 1862); src/melder/aether/spellbook/spellbook.py:4674-4710 (`_restore_binding_key`, a
  refused notch putting a claim back with `update_lookup`, line 4710);
  src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1429-1553 (`_flip_registry_and_spellbooks`,
  the route moved at 1502 and 1510) and :982-1048 (`_rollback_spellbook_move`).
  Reproduce: none yet - read, not run.
  Why it matters: one binding per index should make each write land on the index's own address; nothing proves it.
  Next: one probe per writer.
- GAP-10 (p3, MEASURED on 0.2.8273 and 0.2.8275): four UX checks fail, as they did on 0.2.8256, and nobody owns
  them: test_beginner_example_runs_green[39_agent_inventory_pattern] (an assertion at its line 33);
  test_example_declares_its_surface[37_review_agent_bindings] (its header lacks 'VERIFY:');
  test_probe_two_visible_spells_may_not_share_a_name (the refusal it expects does not raise);
  test_probe_upgrade_to_normal_keeps_creations_and_registers (KeyError at frame 'payload').
  Where: UX_and_AIX_experiences/pytest_examples.
  Reproduce: pytest UX_and_AIX_experiences/pytest_examples on a copy with no crystallizer cache folder
  (artifacts/index_binding_risks_20261025/runs/ux_examples_0_2_8275_gil0.txt).
  Why it matters: a suite that is always red hides the next failure.
  Next: one look each - a stale check or a real regression.
- GAP-11 (p3, NOT RUN): the docs build has not run on S2's doc edits - the governed-change guide, the glossary, the
  README and the agent operations guide; sphinx is not on the device VM, and docs/tests passed 39 with 5 needing
  sphinx or files outside the checkout.
  Where: docs/expert/governed-change.md, docs/reference/glossary.md.
  Reproduce: the docs build where sphinx is installed.
  Why it matters: a broken page or cross-reference shows only when the docs are published.
  Next: build the docs where sphinx runs.

Tracked in their own tickets:
- GAP-7 (p3, CROSS-REF, open): the notch seam parks the outgoing version before it checks a target that is not
  parked - TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog, draft).
- GAP-8 (p2, CROSS-REF, FIXED at 0.2.8275): the meld-vs-notch race -
  TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout, landed by melder_0 (a lender's notch moves its
  ward-link borrowers inside its window, a failed fan-out undoes the notch, the race test's xfail deleted; M0-239).
- GAP-9 (p3, CROSS-REF, open): a changed binding hash does not revalidate the spell and its dependents -
  STORY-2026-10-18-revalidate_on_binding_change (backlog, draft); its store half,
  STORY-2026-10-25-creations_store_slots_by_binding, landed at 0.2.8274 (melder_3; M3-26).
- The stuck class-annotated consumer (a notch back does not revive it):
  EPIC-2026-10-25-dependency_watchers_listen_for_names.

Dropped on the owner's word (2026-10-25), listed so nobody files them again:
- RISK-1, RISK-3, RISK-4: the rule working as meant - another binding or a rename is a new spell, and a split version
  goes active only at a free address.
- RISK-2: his call 1 (records before 5.0.0 are refused), not a risk. RISK-5: one cold cache load after the upgrade.
- GAP-2, GAP-4 and the naming half of GAP-3: a meld or an injection answers what was registered - a class name, a
  spellframe, a Protocol, a version grant; a caller who wants a notch followed injects by the Protocol or the address.
- GAP-12, GAP-13, GAP-14: housekeeping outside the change (the graph's unreviewed prose, probe upkeep, a private-field
  read).

## MRP Alignment (Most Reasonable Product)
One binding per index made the index the stable handle a notch serves. What is left here can break a running
world or hide a failure: a cleanup that deletes new checkpoints, writers outside the new check, checks left red or
unrun.

## Ticket Contract
- ENTRY_GATE: the owner's ask (chat 2026-10-25); a board row routes here.
- EXECUTION_BOUNDARY: investigation first, read-only in src: one label at a time, its measurement under this epic's
  artifact folder and a verdict here; a fix lands as its own story with its own patch docs, tests, notch and rebuild.
  Labels owned by another ticket (CROSS-REF) are followed there and their verdict recorded here.
- DEPENDENCIES: tickets/stories/completed/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md (the change and its notes); EPIC-2026-10-25-dependency_watchers_listen_for_names (GAP-3's stuck
  half); the tickets GAP-7 to GAP-9 name.
- EXIT_GATE: every open label (GAP-1, GAP-5, GAP-6, GAP-10, GAP-11) has a verdict with evidence - fixed by a landed
  story, accepted by the owner, or documented; the CROSS-REF verdicts recorded; board and artifact sync.
- FAILURE_ESCALATION: DECISION_REQUEST for GAP-1's fix; CONFLICT when a fix needs a file another lane holds.

## Goals (Outcomes)
- What can break around one binding per index is investigated and decided.
- GAP-1, which can lose a user's checkpoints, comes first.

## Non-Goals (Explicit Exclusions)
- Re-deciding the rule itself: one binding per index stands (the owner, 2026-10-25).
- Working the CROSS-REF labels here: their tickets own them.

## Scope Boundaries
- In scope: the labels above and any the investigations add.
- Out of scope: fixes beyond one story per confirmed label.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: filed on the owner's ask (chat 2026-10-25) with every label stated and its evidence linked.

## Success Metrics
- Every label carries MEASURED, READ, NOT RUN or CROSS-REF and a next step; at exit, a verdict.

## Requirements (Functional + Non-Functional)
- Each investigation measures with public calls on the current tree, the GIL off and on, and says which reads are
  internal.

## Constraints / Assumptions
- READ labels (GAP-5, GAP-6) are UNKNOWN in behaviour until probed.

## Dependencies / External References
- tickets/tasks/backlog/2026-10-16_notch_seam_checks_incoming_before_parking_task.md (GAP-7)
- tickets/tasks/completed/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md (GAP-8, fixed)
- tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md (GAP-9)
- tickets/epics/2026-10-25_dependency_watchers_listen_for_names_epic.md (GAP-3's stuck half)

## Milestones (Track Progress)
- [ ] Milestone 1: GAP-1 probed with two worlds sharing a profile and its fix options with the owner.
- [ ] Milestone 2: every open label has a verdict recorded here.

## Stories (Required to Complete)
- [ ] Story: none filed yet - one per label when its investigation starts, on the owner's word.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: GAP-1 first - its two-world probe and a DECISION_REQUEST with the fix options.
- [ ] Task: GAP-5 and GAP-6 - one probe per writer.
- [ ] Task: GAP-10 and GAP-11 - the four failing UX checks and the docs build.
- [ ] Task: GAP-7 and GAP-9 - their verdicts recorded from their own tickets.
- [x] Task: GAP-8 - fixed at 0.2.8275 by its own task (M0-239).
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Every open label has a verdict with evidence, GAP-1's first.

## Risks / Mitigations
- None tracked here: what the first list called risks is the rule working as meant or the owner's call (the
  DECISION note of the cut).

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Each investigation: a probe with public calls, the GIL off and on, its runs beside the epic. Each fix story:
  symptom-named regression tests that fail before the fix and pass after it.

## Rollout / Adoption Plan
- One label at a time on the owner's word; fixes land as their own stories, each with its notch and rebuild.

## Open Questions
- The order after GAP-1: proposed GAP-10, then GAP-5 and GAP-6, then GAP-11.

## Decision Log
- 2026-10-25T12:47:21Z: filed on the owner's ask (chat 2026-10-25), from S2's research and landing.
- 2026-10-25T13:04:26Z: cut to what can break, on the owner's word (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/index_binding_risks_20261025/scripts/gap1_checkpoint_retention.sh (GAP-1's measurement)
  - artifacts/index_binding_risks_20261025/runs/gap1_checkpoint_retention_0_2_8273.txt
  - artifacts/index_binding_risks_20261025/runs/gap1_checkpoint_retention_0_2_8275.txt
  - artifacts/index_binding_risks_20261025/runs/ux_examples_0_2_8273_gil0.txt (GAP-10)
  - artifacts/index_binding_risks_20261025/runs/ux_examples_0_2_8275_gil0.txt
  - artifacts/index_binding_risks_20261025/runs/graph_walker_report_0_2_8273.txt (GAP-12)
  - artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8273.txt (GAP-2 to GAP-4)
  - artifacts/correctness_defects_20261017/scripts/run_with_alias.py (GAP-13)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: each investigation runs its measurement again; the folder goes when the epic closes, unless a fix
  story keeps a file as its regression evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the risks and gaps around one binding per SpellIndex
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and measurements; filed 2026-10-25T12:47:21Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-25T12:47:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Filed on the owner's ask (chat 2026-10-25). Five risks of the change and fourteen gaps are labeled from
    S2's notes - its research on the guards and writers, its plan (item (d) not done), the meld-identity map and its
    three gaps (gap 1 closed at 0.2.8269), its Risks section - and from what its landing measured. GAP-1 comes
    first: it can lose a user's checkpoints. Proposed order after it: RISK-2, GAP-2 and GAP-3, then the rest, each
    on the owner's word; the CROSS-REF labels are followed in their own tickets.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:430-475
  - context_compass/tickets/stories/completed/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:504-544
  - context_compass/tickets/stories/completed/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:658-686
  - context_compass/tickets/stories/completed/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:133-136
  IMPACT: Nothing the change risks or leaves open is lost; each label has a next step.
  NEXT: The owner's word on the order; GAP-1's two-world probe when he says go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:47:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: GAP-1 on 0.2.8273, on a /tmp copy of src and the UX examples, the GIL off. The device's own
    `default` profile folder holds 100 checkpoint files, checkpoint_number 3 (49) and 4 (51), record versions 3.0.0
    to 5.0.0 (96 below 5.0.0). Without a crystallizer cache folder, expert examples 02, 09, 24 and 27 pass and write
    5 files numbered 1 and 2. With the device folder copied in, all four fail at their `list_cached_checkpoint_ids`
    assertions and the folder is unchanged after the run: the new files were written and deleted. Twenty runs from an
    empty folder fill it to 100 files numbered 1 and 2 and still pass, as does a 21st at the cap. The retention sort
    (`_creation_order`) reads each file's `checkpoint_number` with no record-version check and treats the number as
    monotonic per profile; it starts again in each world.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:177-264
  - context_compass/artifacts/index_binding_risks_20261025/runs/gap1_checkpoint_retention_0_2_8273.txt:1-27
  - context_compass/artifacts/index_binding_risks_20261025/scripts/gap1_checkpoint_retention.sh:1-52
  - UX_and_AIX_experiences/04_expert/02_persistence_mesh_your_code_their_lanes.py:137-137
  IMPACT: A profile folder shared by worlds - other programs, earlier runs, other tests - can delete a new world's
    checkpoints at once; nothing reports it.
  NEXT: A probe of two worlds writing one profile, then the fix options for the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T12:47:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: GAP-2 to GAP-4 hold on 0.2.8273 (the meld-identity probe run again at the fix, the GIL off and on). With
    English and French bound under (Greeter, 'greeter'): meld(spell=English) and meld('English') raise KeyError at
    ('english', '__default__') before and after the notch; after the notch to French the class-annotated consumer
    raises UnresolvedInputError, the SpellMap(spell=English) consumer RuntimeError "SpellMap default could not be
    resolved" and the version-grant borrower KeyError at the address; after the notch back the SpellMap and the grant
    answer again and the class-annotated consumer stays refused. GAP-5 and GAP-6 are read, not run.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8273.txt:22-60
  - src/melder/utilities/helpers/general_helpers.py:404-457
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:771-794
  - src/melder/aether/spellbook/spellbook.py:407-559
  - src/melder/aether/spellbook/spellbook.py:1796-1868
  - src/melder/aether/spellbook/spellbook.py:4666-4702
  IMPACT: The naming gaps are the owner's calls; the writers need probes before any fix.
  NEXT: Wait for the owner's order.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T13:04:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Cut on the owner's word (chat 2026-10-25): "some of those gaps are just stupid ... does autofac baby sit when
    your [code] is named a specific way?" Naming is the caller's contract: a resolver answers what was registered -
    a class name, a spellframe, a Protocol, a version grant - and does not guess past it. So GAP-2, GAP-4 and the
    naming half of GAP-3 are not gaps; RISK-1, RISK-3 and RISK-4 are the rule working as meant, RISK-2 is his call
    1, RISK-5 is one cold load, and GAP-12 to GAP-14 are housekeeping outside the change. Open: GAP-1, GAP-5, GAP-6,
    GAP-10 and GAP-11; GAP-7 to GAP-9 stay with their tickets. Labels keep their first numbers.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-25_index_binding_risks_and_gaps_epic.md:31-75
  IMPACT: The epic holds only what can break a world or hide a failure.
  NEXT: The owner's go for GAP-1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T14:58:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Every open label is documented on 0.2.8275, on the owner's word (chat 2026-10-25: "put those into the epic
    and ensure they are documented and we'll stop there"): what it is, where it lives with current lines, how to
    reproduce it, why it matters and the next step. GAP-1 and GAP-10 were measured again on 0.2.8275, unchanged;
    GAP-6 gains a fourth writer found in this pass, the rollback of a failed transfer (`_rollback_spellbook_move`).
    GAP-8 is fixed: melder_0 landed its task at 0.2.8275 (M0-239). GAP-9's store half landed at 0.2.8274 (melder_3,
    M3-26); its revalidation story stays in the backlog. Messages M3-26, M0-238 and M0-239 consumed. The epic is
    parked: no investigation starts before the owner's go.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-25_index_binding_risks_and_gaps_epic.md:31-94
  - context_compass/artifacts/index_binding_risks_20261025/runs/gap1_checkpoint_retention_0_2_8275.txt:1-27
  - context_compass/artifacts/index_binding_risks_20261025/runs/ux_examples_0_2_8275_gil0.txt:1-14
  IMPACT: Anyone can pick up a label from the epic alone.
  NEXT: The owner's go; GAP-1 first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: what can break around one binding per SpellIndex - GAP-1, GAP-5, GAP-6, GAP-10 and GAP-11 open, each
  documented with where, how to reproduce, why and next; GAP-7 and GAP-9 open in their own tickets, GAP-8 fixed at
  0.2.8275. Filed 2026-10-25T12:47:21Z on the owner's ask, cut on his word, documented 2026-10-25T14:58:20Z.
- State: ready, melder_1, parked on the owner's word ("we'll stop there"): nothing fixed here. Measured on 0.2.8275:
  GAP-1 and GAP-10; read only: GAP-5, GAP-6; not run: GAP-11.
- Next: (1) the owner's go; (2) GAP-1's two-world probe and fix options; (3) the rest one at a time.

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
