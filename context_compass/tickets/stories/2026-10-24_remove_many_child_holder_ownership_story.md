# Story: Remove holder ownership of `many` dependencies - a `many` belongs to the scope that built it

## Metadata
- Story ID: STORY-2026-10-24-remove_many_child_holder_ownership
- Epic: EPIC-2026-10-20-reassess_many_child_disposal_ownership
- Status: in_progress
- Owner: Mark
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-24T20:05:23Z
- Updated: 2026-10-24T20:05:23Z

## User Narrative
As an agent working inside Melder, I want a `many` dependency to be recorded and disposed by the scope that built
it, like any `many`, so that cleaning up a unique of any kind runs only its own dispose rule and Melder never
disposes transient objects because of the holder they were passed to (the owner, chat 2026-10-24: "it should
behave like autofac not mysteriously cleanup transient objects").

## Value / MRP Alignment
The structure records each disposal obligation where the object was built and nowhere else; nothing is inferred
from which holder received it. A holder's insides are its own dispose rule's business, and a scope's cleanup
disposes what that scope recorded - Autofac's model: a component is disposed when the scope that resolved it ends,
and nothing cascades from one object to its dependencies unless asked (`Owned<T>`).

## Ticket Contract
- ENTRY_GATE: the owner's decision in the epic (DECISION note of 2026-10-24T19:58:35Z); this story's board row;
  patch remove_many_child_holder_ownership_2026_10_24 written and linked before any src edit.
- EXECUTION_BOUNDARY: src - `creations.py` (`HolderDisposalEntry`, `adopt_children`, the holder branches of
  disposal, extract and restore), `site_plan_lowering.py` (child registration inside a miss, the adoption line) and
  docstrings in `conduit.py`, `transfer_of_ownership.py`, `generalized_manifest_no_overrides_compiler.py` and
  `generalized_hydrator.py`; tests - the four feature test files and the emission unit tests that assert the removed
  lines; docs - `src_architecture.md`, `src_components.md` and their indexes, the release note. Not managed pools'
  recorded children, not the opt-in specializer's decline, not cache or record formats.
- DEPENDENCIES: the epic's decision; the 0.2.8235-0.2.8238 history (completed 2026-10-14 epics).
- EXIT_GATE: the new tests red on 0.2.8265 and green after the change, GIL off and on; the full suite run; docs and
  release note updated; one notch; closure and board sync; rebuild last with both checks printing only OK.
- FAILURE_ESCALATION: DECISION_REQUEST to the owner if the removal reaches cache or record formats or managed pools;
  CONFLICT by mailbox if another lane holds a file in the boundary.

## Requirements (Functional)
- F1: A disposal-bearing `many` step built inside a slotted holder's first build registers in the meld's innermost
  scope (`many_store`: the spellspace store, else the melding conduit's store), as a `many` root does.
- F2: No store keeps a holder record: a holder's disposal value is its plain `(holder, methods)` tuple or nothing;
  `HolderDisposalEntry` and `Creations.adopt_children` are removed.
- F3: Cleaning up a holder - a whole-store disposal or a purge of it - runs only the holder's own disposal methods.
- F4: A `many` child stays an entry of its spell's bucket in the store that built it: that store's end disposes it,
  a purge or live-creation probe of the child's spell counts it, and an ownership transfer leaves it where it is.
- F5: Unchanged: managed pools' recorded children; the opt-in specializer's decline of graphs that feed a `many`
  step into a non-`many` step; direct `many` melds; record and cache formats.

## Requirements (Non-Functional)
- Warm `_site_plan_executor` bodies stay byte-identical (only misses change); no lock or lock-order edge is added;
  the store lock stays a leaf.
- Rich docstrings on everything touched; no banned patterns.

## Scope Boundaries
- In scope: the files and tests named in the Ticket Contract, the system docs, the release note.
- Out of scope: managed pools, the specializer decline, cluster and transfer behaviour other than the children
  they no longer carry, the stale `register_many` precondition (HYPOTHESIS in the correctness epic, 2026-10-24).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's go (chat 2026-10-24): "yeah so lets rip it out because it should behave like
  autofac not mysteriously cleanup transient objects".

## Dependencies / Related Work
- context_compass/tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md
- context_compass/tickets/epics/completed/2026-10-14_many_child_follows_holder_epic.md
- context_compass/tickets/epics/completed/2026-10-14_slotted_lifetime_ownership_fixes_epic.md

## Tasks (Implementation Checklist)
- [x] Patch remove_many_child_holder_ownership_2026_10_24 written and linked.
- [x] Tests rewritten to the new contract; red on 0.2.8265 with the GIL off and on.
- [ ] The src change; the tests green with the GIL off and on; the full suite run.
- [ ] Docstrings, `src_architecture.md`, `src_components.md` and indexes; the release note.
- [ ] Notch, closure, board sync, rebuild.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- The release note's example: a `unique` Repository first melded in a lesser request scope gets its `many`
  Connection from that scope, and the scope's end closes it; the root still serves the same Repository.
- Disposing a holder runs only its own methods; its `many` children are disposed when the store that built them
  ends, once each.
- A transfer moves the holder and not its children; a purge or probe of the child's spell counts every child the
  scope recorded.
- No `HolderDisposalEntry` or `adopt_children` remains in src or tests.

## Validation / Test Plan
- Component and integration tests for the new contract (symptom-named, per route: lesser, root spellspace, lesser
  spellspace, nested consumer, override meld, borrower, cluster member), the specializer control kept, the emission
  unit tests flipped; red on 0.2.8265, green after; `-X gil=0` and `-X gil=1`; then the whole suite.

## UX / API / Data Notes
- No public signature changes. Behaviour change (Breaking for code that relied on 0.2.8235-0.2.8265): a scope that
  builds a holder's `many` child disposes it when the scope ends, even while the holder lives on.

## Risks / Mitigations
- A holder kept past the scope that built its child now holds a disposed child: the owner's rule - the user's
  dispose rule or scope choice handles it; stated in the release note with the remedy (meld the holder where it
  lives).
- Missed emission paths (key-set plans, door-held roots, leasing managed misses): the unit tests cover each.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None open; managed pools stay as they are unless the owner widens the scope.

## Decision Log
- 2026-10-24T20:05:23Z: opened on the owner's go (epic DECISION note of 2026-10-24T19:58:35Z).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/remove_many_child_holder_ownership_2026_10_24/
  - artifacts/many_child_removal_20261024/
- DISPOSITION: the patch folder promote_to_documentation (merged into the canonical docs, then deleted);
  the runs folder delete_on_close
- CLEANUP_TRIGGER: the patch folder after its deltas merge into the canonical docs; the runs folder at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1; synaptic_python_developer; prose, implementation, tests, evidence.
- Published By: melder_1 to the local filesystem on the owner's machine; the owner commits.
- Independent Review: none claimed.

## Notes
- DATETIME: 2026-10-24T20:05:23Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Remove the feature in one change set at 0.2.8266 (or the next free notch): (1) patch docs; (2) tests to the
    new contract, red on 0.2.8265; (3) `site_plan_lowering.py` - a miss's disposal-bearing `many` children register
    through `many_store` with the innermost-scope prologue in the miss (the pre-0.2.8235 emission), the adoption
    line goes; (4) `creations.py` - `HolderDisposalEntry`, `adopt_children` and the holder branches go, extract and
    restore keep the plain rows; (5) docstrings; (6) system docs, release note, notch, closure, rebuild.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1543-1582
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1683-1772
  - src/melder/aether/conduit/creations/creations.py:1021-1106
  - src/melder/aether/conduit/creations/creations.py:1538-1760
  IMPACT: One reviewable change; warm plans unchanged; the four feature test files are replaced by tests of the
    new contract.
  NEXT: Write the patch and link it, then the failing tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T20:08:15Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch remove_many_child_holder_ownership_2026_10_24 read in order (architecture, component patches,
    code description) and mapped: (a) architecture "Boundary delta 1" and component_patch_site_plan_lowering ->
    `_emit_context` picks `many_store` for every non-leasing context, `_emit_miss` emits the prologue and no adoption
    line -> emission unit tests + component routes; (b) component_patch_creations -> `HolderDisposalEntry`,
    `adopt_children`, `_dispose_holder_entry` and the holder branches of disposal/extract/restore removed ->
    store unit tests + lifetime integration tests (purge, transfer, child-spell purge, failure surfacing);
    (c) "Invariant 3" -> warm executor bodies unchanged, checked by the existing emission tests; (d) the docstring
    deltas -> a whole-tree search for `HolderDisposalEntry`, `adopt_children`, 0.2.8235/0.2.8238 wording before landing.
  EVIDENCE:
  - context_compass/system_docs/patches/active/remove_many_child_holder_ownership_2026_10_24/architecture_patch.md:1-74
  - context_compass/system_docs/patches/active/remove_many_child_holder_ownership_2026_10_24/component_patch_creations.md:1-55
  IMPACT: Implementation and validation steps are tied to the patch sections before any code edit.
  NEXT: Mirror the tree under /tmp, then write the new tests and run them red on 0.2.8265.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T20:25:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-214 and M2-29 consumed at re-onboarding. M0-214: melder_0's two untracked regression test files fail by
    design on 0.2.8265 (9 of 9, the GIL off and on) until its cache-save fix lands, so a full-suite run of this lane
    counts those 9 as melder_0's, not this change's. M2-29: `llm_support/_builder.py` lists the git index and reads
    each listed file from the working tree, and melder_2's 23-file CI set waits for the owner's extraction; a commit
    must carry bundles rebuilt from exactly what it commits (stage first, then rebuild).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md:562-588
  - context_compass/tickets/tasks/2026-10-24_ci_python_315_and_release_test_rerun_task.md:341-366
  - context_compass/tickets/tasks/2026-10-24_ci_python_315_and_release_test_rerun_task.md:395-409
  IMPACT: The full-suite MEASURE keeps melder_0's 9 expected failures apart from this lane's; the turn-in rebuild
    checks the board row ci_python_315 first and is coordinated with the owner's staging.
  NEXT: Delete the four old feature test files, sync the /tmp mirror and run the new tests red on 0.2.8265.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T20:28:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The new and edited tests fail on 0.2.8265 for the removed behaviour, the GIL off and on (a /tmp mirror of
    the checkout; Python 3.14.7 free-threaded; pytest 9.1.1): 35 failed, 121 passed, the same 35 both ways.
    Component (19): on every route the scope that melded the holder ends and its `many` child stays open (closes 0)
    with that scope's bucket empty - the child sits in the holder's record; the nested per-conduit consumer, the
    override meld and the specializer case likewise. Integration (10): the borrower and the cluster member record
    nothing; a holder purge disposes the child too (events ['PerConduitHolder', 'Child']), a `many` purge of the
    child spell counts 1 of 2 and a move carries the child. Unit (6): the emitted misses still carry
    `c{i}.adopt_children(...)`, so the source checks fail and the trimmed fakes (and `_DisposalRecordingStore`,
    a FakeStore subclass) raise AttributeError. The four old feature test files are deleted.
  EVIDENCE:
  - context_compass/artifacts/many_child_removal_20261024/runs/red_0_2_8265_gil0.txt:1-1753
  - context_compass/artifacts/many_child_removal_20261024/runs/red_0_2_8265_gil1.txt:1-1761
  - tests/component/melder/aether/conduit/test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py:1-511
  - tests/integration/melder/conduit/test_conduit_integration_many_child_belongs_to_the_scope_that_built_it.py:1-197
  - tests/integration/melder/conduit/test_conduit_integration_holder_cleanup_leaves_its_many_children.py:1-419
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py:611-648
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py:1394-1468
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py:351-385
  IMPACT: The tests catch the feature on every route and verb the patch names; the change must turn all 35 green,
    the GIL off and on, and keep the 121 green.
  NEXT: The src change per the mapping note: `site_plan_lowering.py` (`_emit_context`, `_emit_miss`), then
    `creations.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T20:34:56Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The src change is written (patch sections (a), (b) and the docstring deltas; not yet run).
    `site_plan_lowering.py`: `_emit_context` registers every disposal-bearing many child through `many_store` and
    reports it for a miss too; `_emit_many` lost its `store` parameter (0.2.8235's) and emits
    `many_store.register_many`; `_emit_miss` emits the store selection after its unresolved-input check, before
    its children, and no adoption line; the class contract's two bullets became one registration rule. Leasing
    managed misses are untouched (`kids{i}`, `h{i}.adopt`). `creations.py`: `HolderDisposalEntry`,
    `_dispose_holder_entry` and `adopt_children` are gone; whole-store disposal and `_dispose_entry` dispatch
    over the two shapes; extract and restore carry plain unique rows. Docstrings in `conduit.py`,
    `transfer_of_ownership.py`, the generalized compiler and hydrator say a holder's `many` objects stay where
    they were recorded and the specializer decline is about unused builds alone.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:901-920
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1539-1626
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1676-1755
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1954-1970
  - src/melder/aether/conduit/creations/creations.py:56-92
  - src/melder/aether/conduit/creations/creations.py:463-544
  - src/melder/aether/conduit/creations/creations.py:1129-1241
  - src/melder/aether/conduit/creations/creations.py:1356-1560
  IMPACT: The removal is in place in src; warm `_site_plan_executor` bodies are untouched by construction (only
    miss bodies and the store change).
  NEXT: Sync the mirror and run the 156 tests, GIL off and on, then the full suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T20:40:53Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-215 and M2-30 (the ACKs to M1-49 and M1-50) consumed: neither agent holds a file of this lane.
    melder_0 lands first and takes 0.2.8266 with entries in src_architecture, src_components, their indexes and
    next_version_release.md, then rebuilds, so this lane notches above it (0.2.8267 if nothing else lands) and
    edits those docs only after re-reading them post-landing. melder_2's lane is closed: its CI set is in the working
    tree (tests_architecture.md, tests_components.md and their indexes among it - re-read before this lane's
    edits), and its three new .github/python/tests/ manifests are untracked, so the bundle rebuild that runs last
    must include them (--include-untracked, or after the owner stages them).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-10-24_ci_python_315_and_release_test_rerun_task.md:1-20
  IMPACT: The landing order is fixed: melder_0's 0.2.8266 first, then this lane's docs, notch, release note and
    rebuild; the tests system docs need this lane's entries for the deleted and added test files.
  NEXT: Finish the full suite (GIL off and on), then wait for melder_0's landing before the doc edits.
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
- Scope: remove holder ownership of `many` dependencies (0.2.8235 placement + 0.2.8238 adoption) on the owner's
  decision; a `many` belongs to the scope that built it.
- State: in_progress, melder_1; patch written and linked; the tests are red on 0.2.8265 (35 of 156, GIL off
  and on; MEASURE note); nothing edited in src yet.
- Next: (1) the src change (`site_plan_lowering.py`, then `creations.py`); (2) the tests green, GIL off and
  on, then the full suite; (3) docstrings, system docs, release note, notch, closure, rebuild.

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
