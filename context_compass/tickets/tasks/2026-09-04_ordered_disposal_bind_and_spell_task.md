# Task: Resolve ordered book and per-spell disposal names at bind

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-bind-and-spell
- Story: STORY-2026-09-04-ordered-disposal-binding
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T11:37:10Z

## Objective
Each new Spell receives one ordered list composed from its own names and the book's names,
using the configured priority. Hash that same sequence and retain it directly on Spell.

## Ticket Contract
- ENTRY_GATE: Configuration task is verified, patch contract is read/mapped, and board routes here.
- EXECUTION_BOUNDARY: Spellbook bind/bind_inactive, Bind matching/fingerprinting, Spell metadata,
  existing conjure metadata expectation, and focused bind/Spell tests.
- DEPENDENCIES:
  `tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`
- EXIT_GATE: Both priority values, independent binds, missing/duplicate names, list ownership,
  and ordered SHA behavior are verified through real supported binding paths.
- FAILURE_ESCALATION: Record an actual registration/identity conflict; do not silently change
  index semantics, remove disposal from SHA, or move matching to conjure.

## Scope Boundaries
- In scope: the three binding/Spell files plus necessary existing integrity expectations/tests.
- Out of scope: compiler rewrite, disposal mutation after creation, new matching families.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Shared-name correction is implemented; 2,807 selected producer/runtime tests
  pass on Windows 3.14t. Replay and final docs/assets continue under their existing tasks.

## Required Reading and Evidence
Use the component index's Spellbook Core and Binding Pipeline slices, then the graph index
for selected files. Read source completely before editing; ranges below are entry anchors.
- `src/melder/aether/spellbook/spellbook.py:4754-4970` (inactive bind)
- `src/melder/aether/spellbook/spellbook.py:5030-5304` (active bind)
- `src/melder/aether/spellbook/spellbook.py:6539-6561` (existing frozenset expectation)
- `src/melder/aether/spellbook/bind/bind.py:229-485` (forwarding/matching/Spell construction)
- `src/melder/aether/spellbook/bind/bind.py:489-633` (inspector and SHA)
- `src/melder/aether/spellbook/spell.py:287-603` (storage and cleanup)
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:67-132`
- `src/melder/aether/spellbook/spellbinder.py:641-661` (existing passthrough)
- `src/melder/aether/spellbook/spellbinder.py:826-870` (finalize forwarding)

## Composition Contract
- False/default: spell-only names first, then the complete matching book block in book order.
- True: the matching book block first, then spell-only names in their supplied order.
- Names shared with the book belong only to the book block in BOTH modes.
- Retain only names in the existing class profile; keep their first occurrence.
- Use list membership for the small result. No additional set or per-instance reflection.
- Empty or omitted Spell names leave book names applicable. Both empty yields an empty list.
- Matching and has_disposal_methods are established once at Spell creation.
- Spell stores the resolved list directly; no defensive copy or extra setter is required.

## Steps / Checklist
- [x] Forward both inputs and priority through active and inactive bind paths.
- [x] Remove/retire the first-bind candidate latch and its relevant init/cleanup/slot wiring.
- [x] Compose/filter once in Bind; use that same result for SHA and Spell construction.
- [x] Replace Spell's frozenset disposal storage with direct list storage.
- [x] Retire the obsolete frozenset-specific conjure expectation without adding private-mutation guards.
- [x] Preserve inspector parity using the same resolved ordered inputs.
- [x] Update focused tests and docstrings; record evidence before consumer work starts.

## Deliverables
- Independent ordered disposal metadata for every bound Spell and consistent bind identity.
- Real bind tests for both priority modes and fluent SpellBinder passthrough.

## Files / Paths Impacted
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/spell.py`
- Existing tests under `tests/unit/melder/spellbook/bind/` and relevant Spell unit tests.
- `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`
- `tests/component/melder/spellbook/test_spellbook_component_bind.py`
- Focused new order/hash regression test if existing modules cannot host it clearly.

## Validation
- Latest clarified-overlap run: 2,807 selected producer/compiler/Creations/conduit tests passed
  in 9.00s on Windows Python 3.14.0 free-threaded, GIL disabled. This includes 10 new cases.
- Passed: 397 producer tests plus 356 configuration/surrounding binding tests on Windows 3.14t.
- Runner: .venv_new/Scripts/python.exe. All four producer patch indexes and scoped diff checks pass.
- Full suite, other platforms, full cache/restore/graft validation, and generated assets: Not run.
- Canonical document promotion and generated-asset refresh remain in the existing docs/assets task.
- Book [flush, close], Spell [close, stop, flush]: False -> [stop, flush, close];
  True -> [flush, close, stop]. Test missing names and duplicates in either group.
- Bind two different Spells with distinct explicit names; the first must not configure the second.
- Verify class-profile behavior remains unchanged for non-class and inherited-only cases.
- Run a real bind in fresh supported processes with different PYTHONHASHSEED values using
  a stable source-defined class. Earlier discovery tested only a generic hash pattern.
- Test that reordering the final names affects SHA and changing only unmatched names does not.

## Risks / Rollback Notes
Fingerprints intentionally reflect execution order. Do not promise historical hash stability
for unordered inputs or add compatibility shims without a concrete requirement.

## Applicable Anti-Patterns
- [x] No configuration override-only model or default-True assumption.
- [x] No new getter/probe/locking scheme; no runtime policy mutation support.

## Done Checklist
- [x] Binding changes and focused tests complete; source evidence and results recorded.
- [ ] Phase 2 dependencies updated; owner acceptance precedes final closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch_index.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_binding.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_binding_index.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_binding_pipeline.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_binding_pipeline_index.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_binding_order.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_binding_order_index.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted program closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: source selection, ordered matching, Spell ownership, SHA
- IF_UNKNOWN: none

## Noting Behavior
Record tactical findings with evidence and one NEXT action; keep settled policy unchanged.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Current first-bind latching and frozenset storage are the producer corrections.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:5136-5159`
  - `src/melder/aether/spellbook/bind/bind.py:396-475`
  - `src/melder/aether/spellbook/spell.py:434-435`
  IMPACT: Downstream tasks can consume one resolved list and its established presence flag.
  NEXT: After configuration verification, read the full binding implementations and patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T08:55:51Z
  TYPE: PLAN
  CLAIM: Continue on codex_features2 in melder_private. The prior configuration change is
    present in commit 1d300462a and has no local source diff. Product scope is Spellbook,
    Bind, and Spell plus their targeted tests. Holistic method/metadata reads already exist;
    complete source-file reads are still required before editing these larger modules.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1128-1157`
  - `context_compass/tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`
  - git branch/log/status and measured producer counts, 2026-09-05T08:55:51Z.
  IMPACT: Preserve unrelated .gitignore and other-agent documentation/CI work. Do not commit,
    push, change branch rules, or implement later runtime/replay phases.
  NEXT: Read Bind (876 lines), Spell (1,656), and Spellbook (6,816) in explicit chunks;
    then write the producer contracts and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

### Producer read baseline
- Bind SHA256: 40952842850327c688ce519dc7c445c49614a0c4c388747e0a417282b0fb5e9d.
- Spell SHA256: a1658208382de2616cf7b6fcab3cfe7201e6210c1567e04f6f05fe13ef0169e9.
- Spellbook SHA256: f262441e20aba07291982d5474ce79ef66da862d909e4c6b05150fe974cba052.
- Whole-file reads complete: Bind 1-876, Spell 1-1656, Spellbook 1-6816.
- All three SHA256 values still match the read baseline. No producer source edit yet.

- DATETIME: 2026-09-05T08:57:39Z
  TYPE: FACT
  CLAIM: Complete Bind/Spell reads confirm the minimal producer seam: matching occurs before
    sha256_profile and Spell construction; Spell stores names once and deletes its reference
    at cleanup. Hook, context-factory, gate, cache, and mutation machinery does not need changes.
    Spellbook initialization separately owns the first-bind latch targeted for removal.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:229-631`
  - `src/melder/aether/spellbook/spell.py:287-603`
  - `src/melder/aether/spellbook/spellbook.py:171-364`
  IMPACT: Preserve all unrelated runtime synchronization. The inspector remains a hash helper
    over resolved ordered inputs; do not introduce a separate disposal mutation protocol.
  NEXT: Finish the complete Spellbook read before editing its lifecycle/forwarding sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:09:22Z
  TYPE: FACT
  CLAIM: All three producer files are read completely and their hashes match. The latch
    has exactly the known slot/init/core-cleanup, active/inactive selection, and conjure
    expectation contacts. The rest of Spellbook borrows or moves existing Spells without
    recomposing disposal policy. Exact parked-member lookup is _get_owned_spell; public
    find_spell_by_id resolves the index's active member for any member id.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:171-364`
  - `src/melder/aether/spellbook/spellbook.py:705-737`
  - `src/melder/aether/spellbook/spellbook.py:1972-2031`
  - `src/melder/aether/spellbook/spellbook.py:3154-3175`
  - `src/melder/aether/spellbook/spellbook.py:4754-5295`
  - `src/melder/aether/spellbook/spellbook.py:6473-6598`
  IMPACT: Change only the producer data path; preserve admission, lookup/index selection,
    ownership transfer, and existing-Spell lifecycle. Tests for staged metadata must inspect
    the exact owned member and explicitly dispose staged test objects during teardown.
  NEXT: Extend the patch contract and add focused producer tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:09:22Z
  TYPE: MEASURE
  CLAIM: Producer baseline passed: 370 tests across Bind unit, Spell unit, and the two
    selected Spellbook component files before any producer source edits.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/bind/test_bind.py tests/unit/melder/spellbook/test_spell.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py -q -p no:cacheprovider
  - Result: 370 passed in 0.81s, exit 0.
  IMPACT: Existing producer behavior has a green baseline; old frozenset expectations must
    be updated to the approved list contract, not protected by production compatibility branches.
  NEXT: Read the affected test helpers/assertions, then stage the new order/hash regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:14:26Z
  TYPE: PLAN
  CLAIM: Producer architecture, both component contracts, and control-flow contract are
    written, indexed, and read in order. Mapping: Spellbook forwarding/latch retirement ->
    independent active/staged tests; Bind composition/SHA -> order/filter/duplicate/hash-seed
    tests; Spell storage -> constructor reference/default-list tests and conjure list acceptance.
  EVIDENCE:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch.md:19-56`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_binding.md:1-37`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_binding_pipeline.md:1-35`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_binding_order.md:1-33`
  IMPACT: The producer entry gate is satisfied. Existing transaction/index code stays intact.
    No runtime metadata copies, caches, or replay paths are changed in this task.
  NEXT: Add the focused regression module, prove the red baseline, then patch the three producers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:29:27Z
  TYPE: PLAN
  CLAIM: REONBOARD is complete and the owner recertified codex_1. The active branch remains
    codex_features2. Producer contracts and the new test module are present; no producer
    source diff exists yet. Other agents have active CI, documentation, and corpus changes.
  EVIDENCE:
  - `context_compass/attention_board.md`
  - `context_compass/mailbox_board.md`
  - git status --short and git branch --show-current, 2026-09-05T09:29:27Z.
  IMPACT: Resume this producer slice only. Preserve unrelated work, and do not commit or push.
  NEXT: Reopen the producer patch contracts and source seams, then verify the staged red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:32:47Z
  TYPE: MEASURE
  CLAIM: The staged producer regressions fail against the unchanged producers: 24 failed
    in 1.80s. Failures expose discarded book names, shared first-bind names, frozenset storage,
    unchanged SHA on reordered inputs, and wrong actual method order. The three source hashes
    still match the recorded complete-read baseline. Relevant component/graph/test slices and
    all four producer contracts were reread; graph source prose remains stale as already recorded.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/component/melder/spellbook/test_ordered_disposal_binding.py -q -p no:cacheprovider --tb=line
  - `src/melder/aether/spellbook/bind/bind.py:229-631`
  - `src/melder/aether/spellbook/spell.py:287-603`
  - `src/melder/aether/spellbook/spellbook.py:4754-5295`
  IMPACT: Patch mapping is unchanged: forwarding/latch -> independent binds; composition/SHA
    -> order/filter/identity cases; direct Spell list storage -> ownership/default tests.
    Staged red cases also hit old same-id collisions; do not patch unrelated runtime gates.
  NEXT: Apply the three-producer correction and update obsolete frozenset test expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:36:45Z
  TYPE: FACT
  CLAIM: Implemented the three-producer correction. Spellbook forwards both groups and priority
    without a shared latch; Bind resolves a list in selected group order before hashing and
    construction; Spell retains the list and initializes a fresh empty default. Removed the
    obsolete conjure frozenset/flag recheck. Updated old test expectations and added three
    constructor/cleanup ownership cases. No synchronization or consumer implementation changed.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:229-447`
  - `src/melder/aether/spellbook/spell.py:288-442`
  - `src/melder/aether/spellbook/spellbook.py`
  - `tests/unit/melder/spellbook/test_spell.py`
  IMPACT: The patch is ready for focused verification; no passing result is claimed yet.
  NEXT: Run the new producer regressions plus the existing four-file producer baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:38:04Z
  TYPE: MEASURE
  CLAIM: The five-file producer suite passes: 397 tests in 2.57s (370 existing and
    27 new cases). This includes real cleanup order, active/staged binds before and after
    conjure, both priorities, raw configuration, constructor ownership, and subprocess SHA
    agreement across three hash seeds. Product diff review shows only the planned metadata path.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/component/melder/spellbook/test_ordered_disposal_binding.py tests/unit/melder/spellbook/bind/test_bind.py tests/unit/melder/spellbook/test_spell.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py -q -p no:cacheprovider --tb=short
  - Result: 397 passed in 2.57s, exit 0.
  IMPACT: The producer contract passes. This does not establish complete compiler-cache,
    persistence, graft/replay, or cross-platform guarantees for later tasks.
  NEXT: Verify the configuration and surrounding binding tests, check whitespace, then hand off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:40:08Z
  TYPE: MEASURE
  CLAIM: Surrounding verification adds 356 passing tests in 1.09s to the 397 producer cases.
    Configuration/default/reload, Spellbook, SpellBinder, Scan, and creation-system resolution
    fastpath tests pass. Product diff --check and all four producer patch-index checks pass.
    No compiler, Creations, replay, synchronization, or generated asset implementation changed.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/unit/melder/aether/test_configuration_reload_lanes.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/test_spellbinder.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py -q -p no:cacheprovider --tb=short
  - Result: 356 passed in 1.09s, exit 0.
  - `src/melder/aether/spellbook/bind/bind.py:422-447`
  - `src/melder/aether/spellbook/spell.py:434-441`
  - `src/melder/aether/spellbook/spellbook.py:4840-4865`
  - `src/melder/aether/spellbook/spellbook.py:5136-5161`
  IMPACT: Producer task is in review, not closed. Generated proofs from other lanes may
    precede this source/test change; full-feature and release validation are not claimed.
  NEXT: Owner reviews this slice; prepare compiler/Creations propagation under its own task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:44:06Z
  TYPE: MEASURE
  CLAIM: Final combined verification passes all 753 selected tests in one run (3.12s, exit 0)
    after test annotation/import cleanup. Scoped source/test/ticket/board whitespace checking
    passes. The source and test diffs were reread. The task, story, epic, and route now agree.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/component/melder/spellbook/test_ordered_disposal_binding.py tests/unit/melder/spellbook/bind/test_bind.py tests/unit/melder/spellbook/test_spell.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/unit/melder/aether/test_configuration_reload_lanes.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/test_spellbinder.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py -q -p no:cacheprovider --tb=short
  - Result: 753 passed in 3.12s, exit 0.
  IMPACT: No source changes remain in this producer slice. Acceptance/closure and later
    consumer/replay/documentation/asset work are still pending, not implicitly completed.
  NEXT: Review this slice and resume the compiler propagation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:28:11Z
  TYPE: DECISION
  CLAIM: Owner approved the clarified overlap rule after REONBOARD and recertified codex_1.
    The book owns every shared name; its complete matching block keeps configuration order
    whether placed first (True) or last (False/default). Spell-only names keep their own order.
    Earlier False-mode first-occurrence-across-groups decisions are superseded.
  EVIDENCE:
  - Owner clarification and implementation approval, active conversation, 2026-09-05.
  - `context_compass/tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md:691-702`
  IMPACT: Reopen this producer task before replay. Keep matching at bind, the same Spell-owned
    result list, bind-time hashing, current class-profile scope, and existing runtime consumers.
  NEXT: Read current Bind and order regressions, revise the patch contracts, then prove the new rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:28:11Z
  TYPE: PLAN
  CLAIM: Current Bind (909 lines), configuration (1,242), and producer tests (281) are read
    completely. Bind's current first-group loop permits False-mode overlap retention.
    Patch mapping: complete book block -> bind overlap/hash assertions; insertion boundary
    -> active/staged/fluent and actual cleanup assertions; same-policy replay -> idempotence
    tests through fresh binds. Configuration setter documentation will describe placement only.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:422-454`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1128-1157`
  - `tests/component/melder/spellbook/test_ordered_disposal_binding.py:95-258`
  IMPACT: One result list suffices. Match book names first, then insert distinct spell names
    at position zero or the list end. No additional metadata collection, helper, or runtime call.
  NEXT: Stage the corrected behavioral expectations and show the failing baseline before source edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:28:11Z
  TYPE: MEASURE
  CLAIM: Corrected producer expectations reproduce the overlap defect: 9 failed and 25 passed
    against unchanged source. Failures cover default-mode binding, staged binding before/after
    conjure, fluent binding, actual cleanup, shared-name fingerprints, and repeat composition.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/component/melder/spellbook/test_ordered_disposal_binding.py -q -p no:cacheprovider --tb=short
  - Result: 9 failed, 25 passed in 1.53s; all failures expose old False-mode ordering.
  IMPACT: The regression suite distinguishes the new contract from the prior first-group behavior.
  NEXT: Patch Bind's existing loop and the configuration setter documentation, then rerun this suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:34:03Z
  TYPE: MEASURE
  CLAIM: Bind now establishes the book block first and inserts only distinct spell-only names
    at its front/back boundary. The same list is hashed and stored; no runtime path changes.
    The corrected producer suite passes 34 tests, including 10 new overlap/idempotence cases.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:425-462`
  - `tests/component/melder/spellbook/test_ordered_disposal_binding.py:95-352`
  - Command: .venv_new/Scripts/python.exe -m pytest tests/component/melder/spellbook/test_ordered_disposal_binding.py -q -p no:cacheprovider --tb=short
  - Result: 34 passed in 1.44s, exit 0.
  IMPACT: Shared explicit names no longer displace the book block in False mode. Same-policy
    recomposition preserves order/SHA. This is not yet a complete crystal or graft validation.
  NEXT: Run surrounding producer/runtime tests and refresh the changed patch indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:35:27Z
  TYPE: FACT
  CLAIM: The 2,807-case surrounding suite has six failures, all from one outdated runtime
    expected-order literal shared by solo/generalized/many-only and override variants.
    Actual metadata already follows the new rule. The complete 129-line regression file
    retains list identity, actual invocation, repeated meld, and reverse dependency assertions.
  EVIDENCE:
  - `tests/integration/melder/conduit/test_ordered_disposal_runtime.py:80-129`
  - Result: 6 failed, 2801 passed in 8.27s; each failure is the old False-mode expected list.
  IMPACT: Correct the test expectation, not the compiler or cleanup implementation. An earlier
    attempted run named a nonexistent test_conduit.py and collected no tests; the directory-based
    command above is the real verification run.
  NEXT: Update that single order literal and rerun the same surrounding suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:37:10Z
  TYPE: MEASURE
  CLAIM: Final selected verification passes 2,807 tests in 9.00s on Windows Python 3.14.0
    free-threaded with GIL disabled. The corrected integration expectation preserves all
    existing compiler-family, override, repeated-meld, reference, and dependency-order checks.
    Scoped diff --check passes; all four changed patch indexes regenerated successfully.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook tests/component/melder/spellbook tests/unit/melder/aether/conduit/creations tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/integration/melder/conduit -q -p no:cacheprovider --tb=short
  - Result: 2807 passed in 9.00s, exit 0.
  - `src/melder/aether/spellbook/bind/bind.py:425-462`
  - `tests/integration/melder/conduit/test_ordered_disposal_runtime.py:80-129`
  IMPACT: The overlap correction is in review. No consumer/lock/identity-map changes, commit,
    push, full-suite/cross-platform claim, or generated source/corpus refresh belongs to this result.
  NEXT: Resume crystal/replay with the book-owned block semantics, then final docs/assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implemented/in review: book owns overlap order in BOTH modes; False places its block last,
True first. Bind builds one list, and existing consumers keep that established order/reference.
Production change is Bind's existing composition loop plus configuration setter documentation;
tests add 10 cases and strengthen staged/fluent overlap coverage. No per-Meld checks, copies, or locks.
2,807 selected tests pass, including actual cleanup and same-policy order/SHA idempotence.
Resume crystal/replay, then canonical docs/assets and final verification. No commits or pushes.
