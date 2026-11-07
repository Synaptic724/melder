

# Story: map_dependency_watchers_and_announcers - every dependency watcher and announcer measured

## Metadata
- Story ID: STORY-2026-10-25-map_dependency_watchers_and_announcers
- Epic: EPIC-2026-10-25-dependency_watchers_listen_for_names
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-25T02:26:33Z
- Updated: 2026-11-07T09:30:32Z

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
- from_state: ready
- to_state: in_progress
- transition_reason: the owner certified melder_0 and took this lane (chat 2026-11-07); the entry gate holds - the
  probe-and-purge story landed at 0.2.8269.

## Dependencies / Related Work
- EPIC-2026-10-25-dependency_watchers_listen_for_names
- The S2 story's meld-identity map (FACT notes of 2026-10-25T02:01:57Z).

## Tasks (Implementation Checklist)
- [x] Task: read the keying and announcing code in full and record the map.
- [x] Task: the matrix probe, run the GIL off and on, its run file in the artifact folder.
- [x] Task: the owner's strict-xfail regression tests for the key split in tests/component (2026-11-07).
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
  - artifacts/dependency_watchers_20261107/probes/probe_watcher_announcer_matrix.py (the S1 matrix probe; its D3
    cell melds twice since the matrix run)
  - artifacts/dependency_watchers_20261107/probes/run_probe_watcher_announcer_matrix.sh (its runner)
  - artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8277.txt
  - artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_D3_repeats_0_2_8277.txt
  - artifacts/dependency_watchers_20261107/runs/diag_class_annotated_consumer_after_notch_back_0_2_8277.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the fix story re-runs the matrix probe and keeps it as its evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - watcher keys, match keys and announced keys
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; filed 2026-10-25T02:26:33Z.
  melder_0 (synaptic_python_developer); S1 execution from 2026-11-07T08:53:20Z.
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
- DATETIME: 2026-11-07T08:53:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: melder_0 takes S1 on the owner's certification (chat 2026-11-07), which took this lane. The entry gate
    holds: STORY-2026-10-25-probe_and_purge_reach_every_version landed at 0.2.8269. The tree is 0.2.8277, ten
    notches past the 0.2.8267 the reproducer ran on, so the PLAN note's ranges are remeasured before they are
    cited and the reproducer runs again first, on 3.14t with the GIL off and on.
  EVIDENCE:
  - context_compass/attention_board.md:110-110
  - context_compass/system_docs/src_architecture.md:1207-1237
  - src/melder/__version__.py:12-12
  IMPACT: The board routes here; S1 runs now, read-only in src, its probe and runs under this story's artifacts.
  NEXT: Read the PLAN note's keying and announcing code in full at 0.2.8277, then re-run the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-11-07T08:58:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The keying split is in the 0.2.8277 source, read whole. A waiting socket - OVERRIDE_REQUIRED,
    UNRESOLVED_INPUT, AMBIGUOUS_INPUT or a NORMAL collection, never a NORMAL single socket - is watched under its
    annotation's name: dependency_key[0], the annotation (a collection's element) through normalize_frame_key with
    the default binding. Every announcer names the provider's ADDRESS frame key (the spellframe's name, else the
    spell's own): bind stages spell.key, the notch strategy stages the index's binding key, _add_contracted_spell
    marks spell.key[0], and the commit marker marks the frame keys staged, in the staging Book only. Phase 3
    matches by kind: a class annotation against the type key (spell_name), a Protocol against the recorded
    contracts and a Protocol definition, a string against type + contract (single) or the address label
    (collection). So watcher and announcement agree only where the kind's match key equals the provider's address
    frame - a class or single-name annotation with a provider bound bare; a Protocol annotation with a provider
    under that Protocol; a collection name with a provider under that category - and every other matching shape
    is announced under a key no watcher holds.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:883-926
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:974-1022
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:126-151
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1889-1928
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1625-1695
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:840-876
  - src/melder/aether/spellbook/spellbook.py:5718-5790
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:200-208
  - src/melder/aether/spellbook/spellbook.py:3323-3365
  - src/melder/utilities/helpers/general_helpers.py:381-417
  IMPACT: The root cause of the measured miss holds at 0.2.8277 and is general: it covers bind, notch and a borrowed
    copy alike, for every kind/shape pair above, so a fix belongs at the key, not per event.
  NEXT: Re-run the reproducer on 0.2.8277, the GIL off and on (.venv_new: 3.14.7, free-threaded build).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T08:58:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: HYPOTHESIS
  CLAIM: Three more candidate misses from the same reading, each UNKNOWN until the matrix probe measures it.
    (1) No announcer marks a watcher when a provider LEAVES: cleanup_spell takes no transaction and
    unregister_index reaches dependents only by registry edge (compute_impact_closure), which waiting sockets do
    not have - so an AMBIGUOUS_INPUT consumer whose competitor is disposed stays refused, against the docstring at
    spell_system_states.py:1908-1909. (2) Phase 4's BindingResolutionCycleStrategy draws edges to the annotation's
    name at the default binding while its nodes are spell addresses: a cycle through a provider under a spellframe
    or a non-default binding name has no edge (missed), and a spell whose address equals another class's annotated
    name can close a false one. (3) The 0.2.8267 reproducer's bare notch case cannot run as written: since 0.2.8273
    an index admits only versions bound its first version's way, so bind_inactive refuses French (bare, 'french')
    on English's bare index; the matrix stages versions at the index's binding (bare: an edited class of the same
    name).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1147-1259
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1900-1910
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:210-299
  - context_compass/system_docs/src_architecture.md:1162-1206
  IMPACT: If (1) and (2) hold, the matrix has a "provider leaves" column and a Phase 4 row beyond the arrival misses.
  NEXT: Measure (1)-(3) in the matrix probe; (3) shows first in the reproducer re-run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T09:00:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The 0.2.8267 reproducer on 0.2.8277 (.venv_new 3.14.7, free-threaded build; the GIL off and on agree line
    for line): framed - ByClass melds English, raises UnresolvedInputError once French is active, and after the
    notch back stays valid and unmarked with its UNRESOLVED_INPUT ('english', '__default__') socket, raising on
    every meld until rebound; framed_bind_later - English bound under Greeter after conjure leaves ByClass valid and
    unmarked, every meld raising; bare_bind_later - ByClass goes gated and melds English. All three as on 0.2.8267.
    bare - bind_inactive now refuses French on English's bare index (the 0.2.8273 binding check), so H3 holds: on a
    bare index every version keeps the class's own name, which a class annotation matches, so the notch-away cell
    is unreachable rather than passing.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/diag_class_annotated_consumer_after_notch_back_0_2_8277.txt:2-61
  - context_compass/artifacts/dependency_watchers_20261107/runs/diag_class_annotated_consumer_after_notch_back_0_2_8277.txt:63-122
  IMPACT: The miss is live at 0.2.8277 in both GIL modes; the matrix stages notch versions at the index's binding.
  NEXT: Write the matrix probe (one cell per process, the GIL off and on) under
    artifacts/dependency_watchers_20261107/probes, with an artifact-board row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T09:25:38Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The matrix probe - 39 cells, one process each, .venv_new 3.14.7 free-threaded build, the GIL off and on
    agreeing cell for cell; oracle: the consumer's LIVE meld against a FRESH dispose-and-bind of it - gives 22 MISS
    and 17 OK. The key split is 15 of the misses: a single, list[...] or override-only consumer waiting on a class or
    a name while the provider is bound, notched in or granted under a category or a Protocol frame (A2 A3 A5 A8 A9
    B2 B3 C1 C2 C4 C5 I2 F2 G2 G3); each such step's mark reads watch ['langs'] -> [] or watch ['greeter'] -> [].
    It works wherever the two names agree: a bare provider, a Protocol consumer with a provider under that Protocol,
    a collection by label (A1 A4 A6 A7 B1 B4 B5 C3 C6 F1 G1). Not yet taken up with the owner, one at a time on his
    direction: a transfer marks the source Book, not the target (H1 H2; the strategy stages source_spellbook_id);
    a disposed competitor leaves an AMBIGUOUS consumer refused (D1); a removed contract leaves the borrower building
    the copy (G4); a resolved single socket is never watched, so a competitor's arrival leaves it on the first
    provider (E1); Phase 4 refuses a world with no cycle when a category's name equals an annotated class's (P1a;
    control P1b). The meld door is not the cause: by spell_id, by class and by name the stuck consumer raises alike
    and the provider melds (scratch check, both GIL modes).
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8277.txt:4-572
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8277.txt:574-1143
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py:137-204
  IMPACT: The key split is the general root cause the FACT note named, measured across bind, notch and contract,
    single, collection and override-only sockets; five further misses wait for the owner, one at a time.
  NEXT: The owner's regression tests for the key split (DECISION below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T09:25:38Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's calls (chat 2026-11-07). (1) cleanup_spell (cell D3) is not a defect: "if a spell is cleaned it
    means its cleaned its fine thats not really a bug its a problem for the person using the meld i.e an agent" -
    the errors a consumer meets after its provider's cleanup_spell are the agent's (his 2026-10-14 runtime model).
    Raised with him, not yet answered: in one GIL-off run of six the consumer's second meld built a new object from
    the disposed definition. (2) Findings are taken one at a time, and each is filed as a GitHub issue on
    Synaptic724/melder only after he confirms it is a defect; there is no epic there yet (open #205-#207 differ by
    title). (3) "make regressions because my test suite should be catching this kinda stuff": the key split gets
    strict-xfail regression tests in tests/component now, the suite's convention for a known open defect. Tests
    only: no notch, no release-note entry and no asset rebuild (agent_contribution_guide.md). This widens the
    story's "no product tests" boundary for these tests alone; src stays read-only.
  EVIDENCE:
  - context_compass/special_instructions/agent_contribution_guide.md:17-24
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8277.txt:405-416
  - tests/component/melder/aether/test_aether_component_process_wide_spell_id_regime.py:199-212
  IMPACT: D3 leaves the matrix's defect list; the suite gains guards for the key split before any fix is designed.
  NEXT: Write the regression file and run it in .venv_new, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T09:30:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner's regressions landed and ran: 23 tests in tests/component (.venv_new 3.14.7 free-threaded build,
    the GIL off and on alike) - 9 passed (A1 A4 A6 A7 B1 B4 B5 F1 G1) and 14 strict xfails (A2 A3 A5 A8 A9 B2 B3 C1
    C2 C4 I2 F2 G2 G3), each failing only at its final assertion after its late twin (the same annotation, bound
    after the event) resolved the provider, the preconditions raising RuntimeError so no xfail can absorb a broken
    setup. Under --runxfail all 14 fail as the matrix measured ("ByClass melds raises UnresolvedInputError although
    English is live at the category address"; "ListByClass gathers [] after the notch back to English"). Strict on
    purpose: the fix flips them to failures until the markers go. Tests only: no notch, no release-note entry, no
    asset rebuild. The full suite: Not run. For the record, cell D3 (cleanup_spell, ruled not a defect) ten times
    per GIL mode: the first live meld always raises "RootResolutionBlueprint has already been cleaned."; the second
    raised "Cannot build CreationContext" in 19 of 20 runs and built the disposed English in one GIL-off run.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_waiting_consumer_wakes_for_its_provider.py:1-525
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_D3_repeats_0_2_8277.txt:1-21
  IMPACT: The suite now catches the key split in every shape the matrix measured; the fix design comes next.
  NEXT: Cost the fix options for the key split and put them on the epic as a DECISION_REQUEST; file the GitHub
    issue on the owner's go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T10:07:37Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner decided the key split (chat 2026-11-07) between the two options laid out in chat - (A) the
    wake-up also listens on the class name; (B) the Autofac-strict model, a framed spell reached through its frame
    and never by its class, as the class meld door already requires - "I prefer 2nd option", plus a Phase 4/6 check
    for spells sharing a spellframe. The key split moves to EPIC-2026-11-07-spellframe_hides_the_concrete_class
    (GitHub #208): under B every annotation's match key is its provider's address frame, so the wake-up keys agree
    by construction, and that epic's T2 rewrites this story's 14 strict xfails to the strict contract. This story
    keeps S1's other misses (H1/H2, D1, G4, E1, P1a) for the owner, one at a time.
  EVIDENCE:
  - context_compass/tickets/epics/2026-11-07_spellframe_hides_the_concrete_class_epic.md:144-146
  - context_compass/tickets/epics/2026-11-07_spellframe_hides_the_concrete_class_epic.md:177-196
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt:1-51
  IMPACT: S1's fix decision is made for the key split; the board row is in handoff for the remaining misses.
  NEXT: The owner's word on the next miss - H1/H2, the transfer marking the source Book.
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
- Scope: the watcher/announcer matrix and the root cause, read-only in src; on the owner's word (2026-11-07) also
  strict-xfail regression tests for the key split in tests/component.
- State: in_progress, melder_0. Done: the code map (FACT note), the reproducer and the 39-cell matrix on 0.2.8277
  (MEASURE notes: 22 MISS, 15 of them the key split), the regression file (9 passed, 14 strict xfails, both GIL
  modes). Ruled by the owner: cleanup_spell's after-effects are not a defect. Open with the owner, one at a time:
  the GitHub issue for the key split, then H1/H2, D1, G4, E1, P1a.
- Decided 2026-11-07: the key split goes the owner's option B in EPIC-2026-11-07-spellframe_hides_the_concrete_class
  (GitHub #208), whose T2 rewrites the 14 xfails.
- Next: (1) the remaining misses, one at a time on the owner's word - H1/H2 first; (2) close this story when each
  has a verdict.

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
