# Story: Remove holder ownership of `many` dependencies - a `many` belongs to the scope that built it

- Completed: 2026-10-24T22:06:33Z
- Summary: A disposal-bearing `many` dependency built for a slotted holder of any kind is recorded and disposed by the
  meld's innermost scope, like any `many`, and cleaning up a holder runs only its own disposal methods: the 0.2.8235
  placement and the 0.2.8238 holder record (`HolderDisposalEntry`, `adopt_children`) are removed. Notched 0.2.8267;
  release-note section "A `many` dependency belongs to the scope that built it, not to the object that holds it". The
  35 red tests are green and the full suite ran green, the GIL off and on. Rebuild last, after the closure.

## Metadata
- Story ID: STORY-2026-10-24-remove_many_child_holder_ownership
- Epic: EPIC-2026-10-20-reassess_many_child_disposal_ownership
- Status: done
- Owner: Mark
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-24T20:05:23Z
- Updated: 2026-10-24T22:06:33Z

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
- from_state: in_progress (implementation)
- to_state: done
- transition_reason: the EXIT_GATE is met but for its last item, the rebuild, which the turn-in order runs after
  this closure: the new tests red on 0.2.8265 and green with the change, the GIL off and on; the full suite run;
  the docstrings, system docs, tests docs, graph and release note written; notched 0.2.8267 (Notes of
  2026-10-24T20:28:58Z, 20:57:42Z, 21:50:43Z, 21:56:52Z and 22:05:36Z). Routine closure under the owner's go.
- from_state (earlier): draft
- to_state (earlier): in_progress
- transition_reason: the owner's go (chat 2026-10-24): "yeah so lets rip it out because it should behave like
  autofac not mysteriously cleanup transient objects".

## Dependencies / Related Work
- context_compass/tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md
- context_compass/tickets/epics/completed/2026-10-14_many_child_follows_holder_epic.md
- context_compass/tickets/epics/completed/2026-10-14_slotted_lifetime_ownership_fixes_epic.md

## Tasks (Implementation Checklist)
- [x] Patch remove_many_child_holder_ownership_2026_10_24 written and linked.
- [x] Tests rewritten to the new contract; red on 0.2.8265 with the GIL off and on.
- [x] The src change; the tests green with the GIL off and on; the full suite run.
- [x] Docstrings, `src_architecture.md`, `src_components.md` and indexes; the release note.
- [x] Notch, closure, board sync; the rebuild runs last, after the closure.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- The release note's example: a `unique` Repository first melded in a lesser request scope gets its `many`
  Connection from that scope, and the scope's end closes it; the root still serves the same Repository.
- Disposing a holder runs only its own methods; its `many` children are disposed when the store that built them
  ends, once each.
- A transfer moves the holder and not its children; a purge or probe of the child's spell counts every child the
  scope recorded.
- No `HolderDisposalEntry` or `adopt_children` remains in src or tests.
  - Reworded 2026-10-24T22:06:33Z (DECISION note): no code, emitted plan or store record uses either name; two unit tests
    guard their absence; the system docs and their packaged copies name them only as removed history.

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
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None open; managed pools stay as they are unless the owner widens the scope.

## Decision Log
- 2026-10-24T20:05:23Z: opened on the owner's go (epic DECISION note of 2026-10-24T19:58:35Z).
- 2026-10-24T21:56:52Z: no `--reconcile` - it would delete five other lanes' retired graph nodes too.
- 2026-10-24T22:06:33Z: the fourth acceptance criterion reworded to what can hold; closure under the owner's go.

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
- APPLIED (2026-10-24T22:06:33Z): the patch deltas are in src_architecture and src_components, and both folders are deleted at
  this closure (the committed runs and scripts stay in git history).

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

- DATETIME: 2026-10-24T20:57:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: With the change the 35 red tests pass: 156 passed of the six files, the GIL off and on. The first green
    run showed one test bug of this lane, not a code bug: `test_a_failing_child_disposal_surfaces_at_its_store_end_
    not_at_the_holder_purge` read `raised.value.exceptions`, but a root's teardown wraps each store's group in its
    own, so the failure is a leaf two levels down; the test now flattens the group (`_leaf_errors`, as the cluster
    tests do). Full suite on the working tree synced 2026-10-24T20:35Z (this change plus melder_0's in-progress
    cache-save fix), in four chunks because a background run does not survive the device call: 14,711 collected,
    0 failed both ways. GIL off: unit 9,712 passed (3 skipped, 7 xfailed), component 2,400 (43 skipped, 1 xfailed),
    integration 2,277 (2 skipped, 10 xfailed, 2 xpassed), experimentation 250 (4 skipped). GIL on: unit 9,712 (3, 7),
    component 2,420 (23 skipped, 1 xfailed), integration 2,277 (2 skipped, 9 xfailed, 3 xpassed), experimentation
    250 (4). The unit chunk needs `.github/`, `context_compass/` and `docs/` in the mirror (the CI-contract and
    document-builder tests read them); without them it fails 72 and errors 438 for missing files.
  EVIDENCE:
  - context_compass/artifacts/many_child_removal_20261024/runs/green_156_gil0.txt:1-6
  - context_compass/artifacts/many_child_removal_20261024/runs/green_156_gil1.txt:1-14
  - context_compass/artifacts/many_child_removal_20261024/runs/full_unit_gil0.txt:1-141
  - context_compass/artifacts/many_child_removal_20261024/runs/full_component_gil0.txt:1-38
  - context_compass/artifacts/many_child_removal_20261024/runs/full_integration_gil0.txt:1-36
  - context_compass/artifacts/many_child_removal_20261024/runs/full_experimentation_gil0.txt:1-8
  - context_compass/artifacts/many_child_removal_20261024/runs/full_unit_gil1.txt:1-149
  - context_compass/artifacts/many_child_removal_20261024/runs/full_component_gil1.txt:1-46
  - context_compass/artifacts/many_child_removal_20261024/runs/full_integration_gil1.txt:1-44
  - context_compass/artifacts/many_child_removal_20261024/runs/full_experimentation_gil1.txt:1-16
  IMPACT: The removal is green across the suite with the GIL off and on; nothing else in the suite depended on
    holder ownership.
  NEXT: Wait for melder_0's 0.2.8266 landing, then re-read and edit the system docs, the tests docs and the
    release note; notch; closure; rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:04:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: M3-2 consumed (melder_3, QUESTION): it will trim src_architecture.md and move component detail into
    src_components.md (STORY-2026-10-24-src_architecture_trim_to_spec, the owner's ask) after melder_0's F5, and
    offered to land before or after this lane. Answered M1-51: this lane lands first, right after melder_0's
    0.2.8266 - its doc edits are drafted and the code is green - and NOTICEs melder_3 when they are in, with the
    sections touched, so it rebases once on both landings. The order of the shared docs is melder_0, melder_1,
    melder_3.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-24_src_architecture_trim_to_spec_story.md:1-15
  IMPACT: One more writer on src_architecture.md and src_components.md; this lane edits them once, between
    melder_0's landing and melder_3's pass, and tells melder_3 exactly which sections moved.
  NEXT: Wait for melder_0's landing; then the doc edits, a NOTICE to melder_3, the notch and the release note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:17:38Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-216 consumed at re-onboarding (melder_0, NOTICE): melder_0 took 0.2.8266 (the best-effort cache save),
    so this lane notches 0.2.8267 unless another landing comes first. Landed in the working tree: `__version__.py`;
    the release note (header, a section before "Packaging and documentation", a packaging bullet, the rebuild
    line); src_architecture, src_components and both indexes (a new first invariant, failure modes, the code map and
    summaries; spellbook.py citations moved 20 lines); the reassembled graph (the caching_system, spellbook, spell
    and __version__ descriptors). This lane's six descriptors are untouched - `HolderDisposalEntry` retires at this
    lane's re-extract - and the bind-guard count is this lane's to state (M1-52: 629). melder_0 still owes its
    closure and its asset and LLM rebuild (--include-untracked); melder_3 trims src_architecture after this
    lane's turn-in.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  - context_compass/tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md:6-12
  IMPACT: The shared docs are this lane's to edit now; the edits are prepared against the landed text and applied
    after melder_0's rebuild has run, so its --check never runs over a half-applied edit.
  NEXT: Re-read the landed docs and build the text-anchored edit scripts; apply them once melder_0's row closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:47:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-219 and M2-32 consumed at re-onboarding. M0-219 (melder_0): its cache task is closed and its rebuild ran -
    the asset --check prints three OK lines at 0.2.8266 (the bind guard at 629, this lane's removal); the LLM check is
    OK for src and other and STALE for tests, because melder_2's CI edits rewrote three tests/unit/github_workflows
    files after that build; its patch folder moved to patches/completed/; the owner committed both lanes' src and
    melder_0's documents (3bedd65bb). M2-32 (melder_2, no src, no notch): it is editing one bullet in the release
    note's "Packaging and documentation" before the rebuild line, three C1 extents in tests_components.md and its
    index, pyproject.toml's description, README.md:44, docs/requirements.lock and .github, and NOTICEs when done.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:991-1052
  - context_compass/artifacts/cache_write_failure_20261024/runs/rebuild_checks_0_2_8266.txt:1-21
  - context_compass/tickets/tasks/2026-10-24_ci_lane_loose_ends_task.md:221-253
  IMPACT: src_architecture, src_components, their indexes and the graph are this lane's to edit now; the release
    note and tests_components wait for melder_2's done NOTICE and are re-read before this lane's edits; this
    lane's rebuild runs last with --include-untracked and covers melder_2's files too.
  NEXT: Apply the src_architecture and src_components edit scripts with a fresh stamp; regenerate and check both
    indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:50:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: src_architecture and src_components carry the removal (the two text-anchored scripts, stamp
    2026-10-24T21:49:23Z; both indexes regenerated, --check OK: 62 sections over 5,739 lines and 156 over 12,552).
    src_architecture: a new first invariant "A `many` belongs to the scope that built it"; the meld step 4, the
    transfer sequence, the Runtime Model's defect example and the transfer-default invariant; "Holder records" and
    "Holder-owned many children" marked REMOVED (the specializer's decline kept); two Breaking failure modes in place
    of the 0.2.8235 fix and the 0.2.8238 purge entry; the bind-guard count 629; the code map (bind_guard_manifest 651,
    site_plan_lowering 2105, conduit 7909, transfer_of_ownership 2225, creations 1680). src_components: the emitted
    line, the probe paragraph, the store selection, the emission bullet, one "Child registration" bullet in place of
    the two holder bullets, Ownership Transfer, the Creations Disposal Pipeline, the transfer flow, the bind-guard
    counts and the code map. Both docs: conduit.py citations past `transfer_spell_ownership` (def 4273) moved two
    lines (10 and 7), each checked on its def or call line; src_components' creations.py citations, stale before,
    point at `cleanup`, `_attempt_cleanup`, `_describe_for_disposal_error` and the two dispose methods; a handoff
    entry each. `HolderDisposalEntry` and `adopt_children` remain only as removed history.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1178-1208
  - context_compass/system_docs/src_architecture.md:2567-2587
  - context_compass/system_docs/src_architecture.md:5074-5085
  - context_compass/system_docs/src_components.md:5090-5113
  - context_compass/system_docs/src_components.md:7596-7600
  - context_compass/system_docs/src_components.md:11888-11900
  - src/melder/aether/conduit/conduit.py:4273-4273
  IMPACT: The architecture and component maps describe the code as it now runs; melder_3 can rebase its trim on
    them and applies it after this lane's turn-in.
  NEXT: NOTICE melder_3 with the sections touched; notch 0.2.8267; re-extract and reassemble the graph.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:56:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Notched 0.2.8267 (`__version__` read as 0.2.8266 first). The graph: re-extracted (--strict, exit 0, nothing
    skipped); the authored edits in five descriptors (Creations' role and its holder responsibility, SitePlanEmission's
    registration line rewritten and its adoption line dropped, TransferOfOwnership's move line, the generalized
    compiler's and hydrator's decline lines); Creations re-read against creations.py (`__init__` fields, `purge`,
    extract/restore) and accepted, the others left in their prior states; re-extracted again to undo the walker's
    indent=2 rewrite (the stamp kept); assembled - 593 sections, 1,230 nodes, 1,419 edges, 28,193 lines - and the
    --check verified all 593 ranges. src_graph.md names neither `adopt_children` nor `HolderDisposalEntry`.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/system_docs/graph/melder/aether/conduit/creations/creations.json:93-103
  - src/melder/aether/conduit/creations/creations.py:1129-1240
  IMPACT: The version and the generated graph match the source of this change set; the rebuild packages them.
  NEXT: Wait for melder_2's done NOTICE (M2-32), then re-read and edit the tests docs and the release note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:56:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: No `--reconcile` in this lane. The walker reports six retired nodes, not one: `HolderDisposalEntry` and five
    from earlier lanes (`ManyOnlyCodegenPlanTargetKind`; dag_index's `SocketRef`, `DagIndex`, `DagTargetingEngine`,
    `DagIndexBuilder`). `reconcile` takes no node filter and deletes every retired node's prose, so running it would
    destroy five other lanes' retained semantics without their adjudication. `HolderDisposalEntry` stays under its
    descriptor's `nodes_retired`; the assembler renders no retired node, so it is absent from src_graph.md and its
    packaged payload. Adjudication: a deletion, not a move - drop it at the next reconcile that covers all six.
  EVIDENCE:
  - context_compass/tools/system_documents/python/graph_walker.py:306-350
  - context_compass/system_docs/graph/melder/aether/conduit/creations/creations.json:195-230
  IMPACT: The story's plan said reconcile once with one retired node; that step is dropped, and nothing of this lane's
    remains in the assembled graph.
  NEXT: Wait for melder_2's done NOTICE (M2-32).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:03:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-34 consumed (melder_2, NOTICE): its CI task is closed (no src, no notch). It edited, 21:52-21:53Z, the
    release note (one bullet before the rebuild line, "Melder declares one runtime dependency, ..."), tests_components
    (a Repository Tooling Protects bullet, three github_workflows C1 extents, a handoff entry; index regenerated),
    .github/ci_cd/ and BRANCH_WORKFLOW.md; its bullet stays in the running note under 0.2.8267, and this lane's
    rebuild covers its files and the stale tests corpus (M0-219). Before that edit: the release note's example and
    claims were run on the working tree's src (0.2.8267), GIL off and on - the example's asserts hold; melding the
    holder first at the root keeps the connection open through a lesser and the root's end closes it; a transfer
    leaves the connection with the old owner, whose teardown closes it, and with `include_dependencies=True` it moves
    and only the target's teardown closes it.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_ci_lane_loose_ends_task.md:1-20
  - context_compass/artifacts/many_child_removal_20261024/runs/release_note_claims_gil0.txt:1-12
  - context_compass/artifacts/many_child_removal_20261024/runs/release_note_claims_gil1.txt:1-12
  IMPACT: The release note and tests_components are this lane's to edit now; both scripts are re-checked against the
    landed text first (melder_2's handoff entry moves the tests_components handoff anchor).
  NEXT: Re-read the release note and tests docs, adapt the anchors, apply both, regenerate the tests indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:05:36Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The release note and the tests docs carry the removal (stamp 2026-10-24T22:04:25Z). Release note: header
    `# Melder 0.2.8267`; "A `many` dependency is disposed with the object that holds it" replaced by "A `many`
    dependency belongs to the scope that built it, not to the object that holds it" (Breaking change lead, the
    Connection/Repository example, the remedies, purge/probe/transfer, what stays the same, the specializer); in
    "Packaging and documentation" the two holder bullets and the bind-guard bullet (629) corrected, melder_2's bullet
    kept, a documentation bullet added, the rebuild line at 0.2.8267. tests_components: the lowering and door-held
    entries, the component cluster entry (24 tests) and the two integration entries (2 and 10 tests; 36 collected),
    three key-file swaps, 863 modules, six C1 extents (511, 1468, 402, 197, 440, 878), three Information Sources
    lines and a handoff entry naming melder_0's two uncatalogued 0.2.8266 modules; tests_architecture: component 172
    `.py`, 170 `test_*.py`, 863 in the three tiers (recounted from disk: unit 518/515, integration 185/178), a handoff
    entry. All four system indexes regenerated or checked: OK.
  EVIDENCE:
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:213-277
  - release_docs/next_version_release.md:1378-1382
  - release_docs/next_version_release.md:1483-1491
  - context_compass/system_docs/tests_components.md:3914-3931
  - context_compass/system_docs/tests_architecture.md:477-481
  - context_compass/system_docs/tests_architecture.md:923-928
  IMPACT: Every document the change set owes is written; what remains is the closure, the board and artifact sync,
    and the rebuild.
  NEXT: Record the acceptance DECISION and the closure, move the story to completed/, sync the boards, then rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:06:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The fourth acceptance criterion ("No `HolderDisposalEntry` or `adopt_children` remains in src or tests")
    cannot hold as written and is reworded to what the change guarantees: no code, emitted plan or store record uses
    either name. A whole-tree search finds them only in two unit tests that assert the emitted miss source no longer
    contains `adopt_children`, and in the packaged system-document payloads under src/melder/_build_assets/, which
    the rebuild regenerates from the docs - where they appear as removed history (the code map, the REMOVED
    invariants, the handoff entries); the assembled graph names neither.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py:1444-1444
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py:373-373
  - context_compass/system_docs/src_architecture.md:1786-1793
  IMPACT: The criterion now states the property the tests and the search prove, not an absence the history in the
    docs makes impossible.
  NEXT: Record the closure.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:06:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closure. The EXIT_GATE is met but for the rebuild, which runs after this pass: the new tests failed on
    0.2.8265 and pass with the change, the GIL off and on, and the full suite ran green both ways (MEASURE notes of
    20:28:58Z and 20:57:42Z); the patch was consumed (PLAN note of 20:08:15Z) and its deltas promoted into
    src_architecture and src_components (FACT note of 21:50:43Z); the graph is reassembled (21:56:52Z); the tests docs
    and the release note are written and notched 0.2.8267 (22:05:36Z). Acceptance: routine completion under the
    owner's go (the epic's DECISION note of 19:58:35Z); no independent review was requested; the criteria hold, the
    fourth as reworded above. Board row and detail removed, closed anchor added; the patch folder (merged) and the
    runs folder deleted per their dispositions. Not run: the owner's own checks.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md:423-441
  - release_docs/next_version_release.md:213-277
  IMPACT: The story is turned in; the epic stays open for the owner's word.
  NEXT: Rebuild last and record it here as a MEASURE; NOTICE melder_0, melder_2 and melder_3; tell the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T22:16:06Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuild, last (22:12-22:14, Python 3.14.7 free-threaded, from the repository root): the asset runner, run in a
    /tmp mirror of src/ and the system documents (the connected folder refuses the unlink its payload writer does),
    rewrote eight files under src/melder/_build_assets/ for 0.2.8267 - the bind guard at 629 entries, the system
    documents and the graph adjacency from the edited docs - copied back byte-equal, the mirror then equal to the
    repository; its --check in the repository prints three OK lines, before and after the bundles. The LLM builder
    (--include-untracked) wrote src (585 files), tests (1,145) and other (412), melder_2's stale tests corpus
    included, and its --check prints OK for all three. The packaged graph payload and adjacency name neither
    `HolderDisposalEntry` nor `adopt_children`. No .git/index.lock appeared.
  EVIDENCE:
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:17-19
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:22-22
  - context_compass/artifacts/minted_index_registry_20261018/scripts/rebuild_s4_assets.py:1-122
  IMPACT: The change set is complete: the assets and bundles carry 0.2.8267 and every check is OK.
  NEXT: NOTICE melder_3 (apply its trim), melder_0 and melder_2; tell the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

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
- State: done (2026-10-24T22:06:33Z), melder_1. src, tests, docstrings, the two guides, src_architecture, src_components, the
  tests docs, the graph and the release note carry it; notched 0.2.8267; the patch and runs folders deleted.
- Next: none in this story - rebuilt last with every check OK (MEASURE note); NOTICEs sent to melder_0, melder_2
  and melder_3; the epic stays open for the owner's word.

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
