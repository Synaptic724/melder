

# Task: Creations runs every declared disposal method and reports every failure together

## Metadata
- Task ID: TASK-2026-09-27-aggregate-creations-disposal-method-failures
- Story: none
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T13:09:34Z
- Updated: 2026-09-27T13:54:57Z

## Objective
When one of an entry's declared disposal methods raises, Creations stops at that method and the remaining methods of
the entry never run. Owner direction (2026-09-27): collect the error of every failure and emit it. Investigate every
disposal-failure path in Creations, pin the fault with tests that fail on 0.2.79, then change disposal so every
declared method runs and all failures are reported together.

## Ticket Contract
- ENTRY_GATE: owner direction in chat (2026-09-27); this board row; patch docs written, linked and mapped in Notes
  before any src edit (the change alters error semantics).
- EXECUTION_BOUNDARY: src/melder/aether/conduit/creations/creations.py (disposal helpers) and any direct caller the
  investigation shows must change; creations unit tests; src_components, src_architecture, their indexes and the
  creations.py graph descriptor; the release note; `__version__`; build assets and LLM bundles for the notch.
- DEPENDENCIES: tickets/tasks/completed/2026-08-07_creations_disposal_all_methods_task.md (pinned the current
  stop-at-first-failure posture and left aggregation to the owner, who has now ruled).
- EXIT_GATE: new tests red on 0.2.79 and green after; creations, conduit and SpellSpace suites and the whole tree green
  on 3.14t, affected subsets on GIL; docs, indexes and graph current; notch, release note, assets and bundles; owner
  acceptance.
- FAILURE_ESCALATION: DECISION_REQUEST when aggregation needs a public error-contract choice the owner has not made;
  BLOCKER when the fault cannot be reproduced.

## Scope Boundaries
- In scope: how Creations invokes an entry's disposal methods and how their failures are collected and surfaced.
- Out of scope: disposal-order policy (fixed at bind), purge authority rules, teardown outside Creations.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction in chat, 2026-09-27 ("open a ticket to investigate creations disposal method
  failures and make tests to cover the fault then fix the problem").
- from_state: in_progress
- to_state: review
- transition_reason: Fix landed at 0.2.80 with tests red on 0.2.79 and green after; whole tree green on 3.14t,
  subsets on GIL; docs, graph, release note, assets and LLM bundles current. Awaiting owner acceptance.

## Steps / Checklist
- [x] Read the Creations disposal paths and their callers in full; record the fault with evidence.
- [x] Patch docs (architecture, component, code description); linked; mapping note.
- [x] Tests that fail on 0.2.79 for the fault.
- [x] Fix; creations, conduit, SpellSpace suites and the whole tree on 3.14t; GIL subsets.
- [x] Docs, indexes, graph descriptor; release note; `__version__` notch; NOTICEs; assets and LLM bundles.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Aggregated disposal-failure reporting in Creations, tests, docs, release note, notch.

## Files / Paths Impacted
- Exact list in the PLAN note before src edits.

## Validation
- Run on the VM worktree (equal to the device tree); logs in artifacts/creations_disposal_failures_20260927/:
  - regression_red_0279_vm.txt: the ten new tests red on 0.2.79
  - suites_post_change_vm.txt: 3.14.7t PYTHON_GIL=0 whole tests/ tree green except the environment-only PyYAML
    collection error; PYTHON_GIL=1 and the 3.14.7 GIL build green on the conduit and crystallizer subsets
  - suites_final_0280_vm.txt: version/asset/system-document set and disposal tests green on all three at 0.2.80
- Build assets --check OK on the device (v0.2.80); LLM bundles --check OK with --include-untracked.
- Coverage: Not run.

## Risks / Rollback Notes
- Running later disposal methods after an earlier one failed can touch a half-disposed object; the declared order is
  the user's contract, so the change keeps order and only stops skipping.
- Rollback is a revert of one change set.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behaviour claim cited to a search hit; every range covers the logic that was read.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/creations_disposal_failures_2026_09_27/
  - artifacts/creations_disposal_failures_20260927/
- DISPOSITION: promote_to_documentation (patch lane); retain_as_reference (suite logs, apply scripts)
- CLEANUP_TRIGGER: task closure

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
- DATETIME: 2026-09-27T13:09:34Z
  TYPE: DECISION
  CLAIM: Owner direction (chat, 2026-09-27): Creations should collect the error of every disposal-method failure and
    emit it; open this ticket, write tests that cover the fault, then fix it. The notch pipeline (release note,
    `__version__` +0.01, build assets and LLM bundles) is in scope from the start, as the owner approved last lane.
  EVIDENCE: tickets/tasks/completed/2026-08-07_creations_disposal_all_methods_task.md
  IMPACT: The stop-at-first-failure posture pinned on 2026-08-07 is now a fault to fix, not a contract to keep.
  NEXT: Read Creations' disposal helpers and their callers in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T13:09:34Z
  TYPE: FACT
  CLAIM: Device VM interpreter. Bare `python3` in a fresh device shell is the VM's system CPython 3.10.12
    (/usr/bin/python3). No directory on the default PATH is writable and there is no sudo, so it cannot be
    repointed. CPython 3.14.7 (free-threaded and GIL builds) is installed through uv; ~/.venv314t and ~/.venv314
    hold pytest. Every device command in this lane loads ~/.melder_env (3.14.7t first on PATH) and lane scripts
    assert Python >= 3.14, so a missed env load fails loudly instead of running 3.10.
  EVIDENCE: pyproject.toml:10-10
  IMPACT: No step of this lane runs on 3.10; the earlier read-only slip (a bundle --check) cannot repeat silently.
  NEXT: Read Creations' disposal helpers and their callers in full.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T13:12:24Z
  TYPE: FACT
  CLAIM: The fault, from the full read of creations.py. Every disposal path (cleanup, clear_all/reset_for_pool, purge,
    refused late publication) routes each object through `_attempt_cleanup`, which (1) returns at the FIRST failing
    method, so the object's later declared methods never run (`["close", "release"]` with close raising leaks the
    release); (2) returns `RuntimeError(f"...: {ex}")` without chaining, so the original exception's type and
    traceback are lost; (3) formats the object with `{item}` inside the handler, so a `__str__` that raises escapes
    `_attempt_cleanup` - cleanup's outer except then records one error but skips every remaining object, and
    clear_all and purge propagate it mid-loop. Per-object aggregation into ExceptionGroup already exists in all three
    callers; no src code inspects the group's shape (no except*). ClusterCreations only fronts a leader's Creations
    and disposes nothing itself. Tests pinning the old posture: the 2026-08-07 regression file's first-failure test
    and two private-helper tests in test_creations.py; the slot-guard test checks the chained cause of a single
    failure.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:241-262
  - src/melder/aether/conduit/creations/creations.py:182-239
  - src/melder/aether/conduit/creations/creations.py:264-354
  - src/melder/aether/conduit/creations/creations.py:407-453
  - src/melder/aether/conduit/creations/creations.py:650-752
  - src/melder/aether/conduit/creations/creations.py:1009-1044
  - src/melder/aether/conduit/creations/cluster_creations.py:9-130
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:179-211
  - tests/unit/melder/aether/conduit/creations/test_creations.py:497-515
  - context_compass/system_docs/src_components.md:2816-2824
  IMPACT: The fix is local to `_attempt_cleanup` plus its four call sites: run every method, collect one chained error
    per failing method, describe the object without trusting its `__str__`. Callers keep raising the ExceptionGroup
    they raise today, now carrying every failure.
  NEXT: Answer the owner's design question, then write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T13:14:30Z
  TYPE: PLAN
  CLAIM: Patch docs written, linked and read in order (architecture -> component -> code description). Mapping, patch
    section -> implementation step -> validation step:
    - later methods run -> `_attempt_cleanup` loops over every method and returns a list -> unit (cleanup, purge
      many bucket) and integration (real conduit teardown with Book names ["close", "release"]), red on 0.2.79.
    - one error per failing method, chained -> RuntimeError per failure with `__cause__` = the raised exception ->
      unit: two failing methods give two errors in declared order; cause identity.
    - safe text -> static helper `_describe_for_disposal_error` falls back when `str()` raises -> unit: a failing
      `__str__` on a failing object; cleanup and clear_all still dispose the other objects, red on 0.2.79.
    - callers -> `_dispose_many_creations`, `_dispose_disposable_registry`, `purge` extend lists; refusal chains one
      error or an ExceptionGroup -> unit per path.
    - pinned tests -> update test_first_failing_method_ends_disposal_for_that_entry and the two private-helper
      tests in test_creations.py (owner ruled on the posture).
    Baseline: suites_final_0279_vm.txt (12:28Z); src and tests in the VM worktree still equal the device (diff now).
    Files: src/melder/aether/conduit/creations/creations.py; tests/unit/melder/aether/conduit/creations/ (new
    regression file, two updated files); tests/integration/melder/conduit/ (new public-path test file).
  EVIDENCE:
  - context_compass/system_docs/patches/active/creations_disposal_failures_2026_09_27/architecture_patch.md:23-59
  - context_compass/system_docs/patches/active/creations_disposal_failures_2026_09_27/code_description_patch_creations_disposal.md:6-34
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/suites_final_0279_vm.txt:1-38
  IMPACT: Entry gate met; tests go first in the worktree.
  NEXT: Write the new tests in the worktree and prove them red on 0.2.79.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T13:16:52Z
  TYPE: MEASURE
  CLAIM: Ten new tests (8 unit, 2 integration) are red on unmodified 0.2.79 (3.14.7t, worktree equal to the device):
    later methods skipped (['close'] instead of every declared method) through cleanup, purge of a many bucket,
    refused publication, real conduit cleanup and real managed-spellspace exit; the reported error's __cause__ is None;
    an object whose `__str__` raises leaves the survivor undisposed in cleanup ([] instead of ['close']) and makes
    clear_all raise the bare RuntimeError from `__str__` instead of a group.
  EVIDENCE:
  - context_compass/artifacts/creations_disposal_failures_20260927/regression_red_0279_vm.txt:1-39
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_failure_aggregation_regression.py:1-245
  - tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py:1-120
  IMPACT: Each fault in the FACT note has a failing test; they must all pass after the fix on 3.14t and GIL.
  NEXT: Implement `_attempt_cleanup` and its callers in the worktree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T13:18:57Z
  TYPE: MEASURE
  CLAIM: Fix implemented in the worktree (creations.py, line endings preserved): `_attempt_cleanup` runs every method
    and returns one RuntimeError per failing method with `__cause__` set; new static helper
    `_describe_for_disposal_error` falls back to type name and id when `str()` raises; `_dispose_many_creations`,
    `_dispose_disposable_registry` and `purge` extend their lists; the refused publication chains one error or an
    ExceptionGroup of several; class and method docstrings state the per-method contract. Three tests that pinned the
    old posture were updated on the owner's ruling (the 2026-08-07 regression test now asserts the later method runs;
    the two private-helper tests expect a list). Creations unit folder plus both conduit disposal integration files:
    79 passed on 3.14.7t (the ten new tests included).
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:245-324 (worktree)
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:21-29 (worktree)
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:182-214 (worktree)
  - tests/unit/melder/aether/conduit/creations/test_creations.py:497-520 (worktree)
  IMPACT: The fault is fixed where it lives; callers keep raising the same group type with every failure inside.
  NEXT: Whole tree on 3.14t and the GIL subsets in the worktree, then copy to the device.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T13:25:11Z
  TYPE: MEASURE
  CLAIM: Post-change suites on the worktree. 3.14.7t PYTHON_GIL=0 whole tests/ tree green except the environment-only
    PyYAML collection error, after one more pinned test was updated: the component purge test
    (test_conduit_component_purge.py) expected marker 2's second method to be skipped; it now expects it to run
    (events 7 -> 8, same two errors in the same order). PYTHON_GIL=1 (conduit unit/component/integration,
    multithreading) and the 3.14.7 GIL build (conduit unit/component/integration, aether and crystallizer
    integration) green.
  EVIDENCE:
  - context_compass/artifacts/creations_disposal_failures_20260927/suites_post_change_vm.txt:1-44
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py:420-509 (worktree)
  IMPACT: The change is ready for the device tree; four test files moved with the contract, none failed elsewhere.
  NEXT: NOTICE the active agents, then copy the six files to the device after checking each target.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T13:26:08Z
  TYPE: FACT
  CLAIM: NOTICEs M0-58/59/60 sent to melder_1, fable_0 and melder_2 (alert lines added). The six files were copied from
    the worktree to the device after checking that each changed target still equalled its pre-change copy and that
    the two new test files did not exist; every copy compares byte-equal.
  EVIDENCE:
  - context_compass/mailbox_board.md:183-222
  - src/melder/aether/conduit/creations/creations.py:245-324
  IMPACT: The fix is live in the owner's tree at 0.2.79 until the notch; docs, graph, release note and assets next.
  NEXT: Read the system-document authoring instructions, then promote the patch lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T13:30:19Z
  TYPE: MEASURE
  CLAIM: Docs, graph, release note and notch. After reading the three authoring instructions (on-demand trigger):
    src_components (Creations invariants, failure modes, observability, the Disposal Pipeline contract, the purge
    flow, the C1 range, a handoff entry, three creations.py citations remapped 69-84 / 227-243 / 365-413),
    src_architecture (cleanup sequence, a "Disposal failures" invariant, failure mode, C1 range, handoff) and
    tests_components (Conduit Integration Cluster: the new integration file, its C1 entry, a Protects clause). The
    content-preservation diff shows only the replaced lines; indexes regenerated and --check OK (147/56/65); the
    citation recipe finds no out-of-bounds range (one pre-existing false positive: `.github/...` loses its dot to the
    regex). Pre-existing, not fixed: the Indexing sections of src_components and src_architecture still name the
    index tool path. Graph: re-extracted on the VM copy (--strict), the Creations node's stale responsibility
    replaced and the node accepted after the full read; stale count back to 145; reassembled (27,524 lines, 584
    sections, index verified); ten descriptors changed (creations, __version__, the eight asset modules).
    `__version__` 0.2.79 -> 0.2.80; release note header 0.2.80, a "Disposal runs every method and reports every
    failure" section, the packaged-docs bullet and the asset line (0.2.80).
  EVIDENCE:
  - context_compass/artifacts/creations_disposal_failures_20260927/apply/apply_docs.py:1-128
  - context_compass/artifacts/creations_disposal_failures_20260927/apply/apply_graph_semantics.py:1-27
  - src/melder/__version__.py:12-12
  - release_docs/0.2.77.md:68-83
  IMPACT: Canonical docs describe 0.2.80; the assets and LLM bundles must now be rebuilt from them.
  NEXT: Rebuild the build assets in the worktree, copy them to the device, then the LLM bundles on the device.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T13:33:57Z
  TYPE: MEASURE
  CLAIM: Assets, bundles and final suites at 0.2.80. Build assets rebuilt in the worktree (agent documentation 460,
    bind guard 619, system documents 4; no pair refused), converted to CRLF, --check OK, copied to the device after
    checking the device inputs equalled the worktree and its eight outputs equalled the VM backup
    (asset_backup_0279); the device --check is OK at v0.2.80. LLM bundles rebuilt on the device with
    --include-untracked (src 576, tests 1021, other 376) and --check OK with the flag; without it the tests corpus
    reads stale until the owner commits the two new test files. Final pass on 3.14.7t (GIL 0 and 1) and the 3.14.7
    GIL build: the version/asset/system-document set (288 passed, 1 skipped) and the creations, component purge and
    conduit integration tests (425 passed) green on all three; the whole tree ran green post-change.
  EVIDENCE:
  - context_compass/artifacts/creations_disposal_failures_20260927/suites_final_0280_vm.txt:1-11
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:1-82
  - llm_support/manifest.json:1-20
  IMPACT: Every EXIT_GATE item except owner acceptance is met.
  NEXT: Move the task to review and report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T13:33:57Z
  TYPE: RISK
  CLAIM: Related finding, deliberately NOT changed in this lane. When disposal fails on a managed SpellSpace exit,
    `recycle_from_managed_context` raises out of `reset_for_pool_unlocked()` before it restores temporary Meld hooks
    and returns the space to its pool, so that pooled SpellSpace is dropped (the store itself was already detached
    and emptied). `_cleanup_for_pool_reuse` likewise skips its registry discard and hook reset. Conduit pool return
    documents the matching posture on purpose ("soft retirement failures retain ownership for retry and never
    publish idle"), so whether a SpellSpace should still be recycled after a disposal failure is an owner decision.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:305-363
  - src/melder/aether/conduit/spell_space/spell_space.py:365-384
  - context_compass/system_docs/src_architecture.md:1291-1292
  IMPACT: Before and after this lane the same exception escapes; only pool capacity is lost, not correctness.
  NEXT: Ask the owner whether SpellSpace recycle should finish (restore hooks, return to pool) before re-raising.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T13:44:07Z
  TYPE: FACT
  CLAIM: Post-compaction ordering slip. At 13:34:24Z, before the REONBOARD attestation, melder_0 wrote this task's
    in_progress -> review transition, Validation and Handoff, the attention row (review/handoff) and its mailbox
    last_checked. REONBOARD then ran in full (root AGENTS.MD, execution contract, config, the SKILLS chain and every
    baseline doc, src_architecture whole, both indexes, the boards); this ticket and the board row were re-read and
    match, so the writes stand unchanged. Self-certified as melder_0 under the owner's standing rule; disclosed.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md:44-47
  - context_compass/attention_board.md:95-95
  - context_compass/mailbox_board.md:90-90
  IMPACT: The review state is correct but was written before re-certification; recorded so the trail shows it.
  NEXT: Record the SpellSpace decision request, then report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T13:44:07Z
  TYPE: DECISION_REQUEST
  CLAIM: SpellSpace after a disposal failure, from a full read of every path (refines the RISK note; nothing changed).
    Every Creations clear swaps the store empty BEFORE any disposal method runs, so when the ExceptionGroup escapes
    the space is as clean as after a successful clear and nothing is left to retry. The paths then diverge:
    (1) managed exit drops the space - off the thread stack, not pooled, untracked - and never cleans its Meld or
    Creations (left to GC; a later acquire builds a replacement, so pool capacity self-heals); (2) manual cleanup()
    keeps it registered and unreleased, so a second cleanup() or conduit teardown finishes it; (3) conduit pool
    return pops it from the registry before cleanup(), so a failing space is dropped uncleaned (logged); (4) the
    permanent lane stops at Creations.cleanup(), skipping Meld cleanup, the registry discard and the field deletes.
    Options: A keep as is; B finish the recycle or teardown (hook reset, registry discard and pool release; or Meld
    cleanup and deletes), then re-raise the same group; C destroy the space on failure, then re-raise.
    Recommendation: B. It leaves nothing to the GC (cleanup policy) and changes no error the caller sees; C costs a
    rebuild for no safety gain, because the store is already empty. B or C is its own lane at 0.2.81.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1073-1168
  - src/melder/aether/conduit/creations/creations.py:186-243
  - src/melder/aether/conduit/spell_space/spell_space.py:233-411
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:185-288
  - src/melder/aether/conduit/conduit.py:672-705
  - src/melder/aether/conduit/conduit.py:1074-1118
  IMPACT: Only (2) keeps the space where a retry can find it; (1) and (3) drop it uncleaned, and (4) leaves it
    half-destroyed unless the caller retries. Unchanged by 0.2.80: the same exception escapes before and after.
  NEXT: Owner picks A, B or C; B or C opens its own task with red tests first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T13:54:57Z
  TYPE: DECISION
  CLAIM: Owner reply to the SpellSpace DECISION_REQUEST (chat): scope exit (`with`) and pool return of SpellSpaces
    and Conduits must dispose everything under the normal scope cleanup contract; investigate first. The A/B/C
    choice moved to a new investigation task; acceptance of this task is still open.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:1-20
  IMPACT: This task's own scope is unchanged; the SpellSpace follow-up is tracked there, not here.
  NEXT: Owner acceptance of this task; the investigation proceeds in its own ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Done at 0.2.80 on the device tree, not committed: `Creations._attempt_cleanup` runs every declared disposal method,
returns one RuntimeError per failing method chained from what it raised, and describes objects without trusting
their `__str__`; cleanup, clear_all, purge and refused publication carry every failure. Two new test files (8 unit,
2 integration) were red on 0.2.79; three existing test files whose four tests pinned the old posture were updated on
the owner's ruling. Docs, indexes, graph, release note, notch, assets and bundles are current. Open for the owner:
acceptance. The SpellSpace-after-failure question moved to the scope-exit investigation task on the owner's
reply. After acceptance: archive the patch lane to system_docs/patches/completed/, close this task and sync
the boards.

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
