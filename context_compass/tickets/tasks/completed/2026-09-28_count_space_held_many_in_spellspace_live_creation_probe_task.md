

# Task: Count space-held `many` objects in the SpellSpace live-creation probe

## Metadata
- Task ID: TASK-2026-09-28-count-space-held-many-in-spellspace-live-creation-probe
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-28T00:21:47Z
- Updated: 2026-09-28T00:59:57Z
- Completed: 2026-09-28T00:59:57Z
- Closure Basis: owner turn-in in chat (2026-09-28): "ok cool yeah fix the problem you have yourself and
  send it, finish off your fixes and turn in the remaining things please go ahead".

## Objective
Fix the follow-up the scope_exit_dispose lane found (RISK note, 2026-09-27T23:30:55Z): the live-creation probe
through a SpellSpace (`SpellSpaceMeld._describe_spell_live_creation_status`) reads `many` objects from the owner
conduit's store, but a disposal-bearing `many` melded through the space is stored in the space's own store, so
the probe can report 0 while the space holds one. The probe must report what the space actually holds. Owner
direction (chat, 2026-09-28): "fix the problem you have yourself and send it", then turn it in.

## Ticket Contract
- ENTRY_GATE: this board row; the owner's direction recorded; findings noted before any src edit; patch docs
  written and linked if the change alters a documented component contract.
- EXECUTION_BOUNDARY: src/melder/aether/conduit/meld/spellspace_meld.py (the probe) and whatever caller or
  sibling probe the reading shows must agree with it; its tests; src_components / src_architecture entries that
  describe the probe; graph descriptors; the release note; `__version__`; assets and bundles last.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md (RISK note).
- EXIT_GATE: a test red on 0.2.8203 and green after; probe and conduit/SpellSpace suites green on 3.14t (GIL 0
  and 1) and the GIL build; no meld hot-path change (or measured if one is touched); docs, graph, notch, release
  note, assets and bundles current; turned in on the owner's directive.
- FAILURE_ESCALATION: DECISION_REQUEST if what the probe should report is a contract choice the code does not
  settle; BLOCKER if the path cannot be exercised.

## Scope Boundaries
- In scope: the SpellSpace probe's `many` source, its tests and docs.
- Out of scope: storage routing itself (unchanged), the conduit-side probe unless it has the same defect,
  the portability of the system docs' Indexing sections, other lanes' graph nodes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner direction in chat (2026-09-28) to fix and ship the follow-up; the defect was found and
  recorded with evidence by the scope_exit_dispose lane.
- from_state: in_progress
- to_state: done
- transition_reason: Landed at 0.2.8204 with docs, graph, release note, assets and bundles current; final suites
  green on three interpreters; closed on the owner's turn-in directive (DECISION note 2026-09-28T00:59:15Z).

## Steps / Checklist
- [x] Read the probe, its callers and the `many` routing of every executor family through a SpellSpace door.
- [x] Red test on the current tree.
- [x] Fix, docstring, tests green; suites on three interpreters.
- [x] Docs, graph, notch, release note; assets and bundles last; turn in.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The SpellSpace door's live-creation probe reads `many` from the space's own store and reports
  "spellspace_many" with the space id (spellspace_meld.py; probe and class contracts updated).
- Tests: one unit test rewritten and one added (test_concrete_meld_subclasses.py), one component test added
  (test_conduit_component_spellspace_creations.py); all three red on 0.2.8203.
- `__version__` 0.2.8204 and a release-note section; src_components promoted (probe scope, store selection,
  two failure modes, flow step, C1, handoff); graph (SpellSpaceMeld and melder.__version__ accepted);
  build assets and LLM bundles rebuilt, both checks OK.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/spellspace_meld.py
- src/melder/__version__.py
- tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py
- tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py
- release_docs/next_version_release.md
- context_compass/system_docs/src_components.md and src_components_index.md
- context_compass/system_docs/graph/ (spellspace_meld.json, __version__.json authored; 8 asset descriptors
  re-extracted), src_graph.md and src_graph_index.md
- src/melder/_build_assets/ (agent_documentation, bind_guard, graph_adjacency, system_documents index and
  manifest, src_components and src_graph payloads)
- llm_support/ (src, tests and other bundles, their indexes, manifest.json)
- context_compass/system_docs/patches/completed/spellspace_probe_many_2026_09_28/
- context_compass/artifacts/spellspace_probe_many_20260928/

## Validation
- Red before / green after: the 3 new or rewritten tests failed on 0.2.8203 (red_0_2_8203.txt) and the two
  touched files passed after the fix, 50 tests (green_touched_gil0.txt); repro before and after.
- 0.2.8204 on the VM copy: every tests/ tree green on 3.14t GIL off (tests/unit/github_workflows not
  collectable there: no PyYAML); conduit set plus probe consumers 2442 passed with the GIL on and on the GIL
  build (suites_0_2_8204_vm.txt).
- Final after the rebuilds: version/asset/system-document set 288 passed, 1 skipped, on all three; conduit
  set 2442 on GIL off (suites_final_0_2_8204_vm.txt). Asset --check OK; LLM --check OK with
  --include-untracked.
- Benchmarks: not run - the probe is not on the meld path (FACT note 2026-09-28T00:32:23Z).
- Coverage: Not run.

## Risks / Rollback Notes
- The probe is diagnostic; resolution and storage are not changed. Rollback is a revert of one change set.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No behaviour claim cited to a search hit; every range covers the logic that was read.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/spellspace_probe_many_20260928/
  - system_docs/patches/completed/spellspace_probe_many_2026_09_28/architecture_patch.md
  - system_docs/patches/completed/spellspace_probe_many_2026_09_28/component_patch_meld_resolution_runtime.md
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch lane, archived to completed)
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
- DATETIME: 2026-09-28T00:21:47Z
  TYPE: DECISION
  CLAIM: Lane opened on the owner's direction (chat, 2026-09-28): fix the SpellSpace probe follow-up and ship it,
    then turn it in. Carried from the RISK note: the probe reads `many` from the owner conduit store while a
    disposal-bearing `many` melded through a space lives in the space store. A notch is taken at landing.
  EVIDENCE: context_compass/tickets/tasks/completed/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md:1-20
  IMPACT: Scope is one probe and what agrees with it; storage routing does not change.
  NEXT: Read the probe, its callers and the `many` routing of each executor family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:32:23Z
  TYPE: FACT
  CLAIM: Confirmed on 0.2.8203 (repro, 3.14t): melding a disposal-bearing `many` through a SpellSpace puts the
    instance in the space's store (bucket of 1), while the space door's probe reports is_live False, count 0,
    `owner_conduit_many` and `active_spellspace_id` None. Cause: the probe's `many` branch reads
    `self._conduit_creations`. Every emitter that registers a disposal-bearing `many` picks the innermost
    scope - `meld._spellspace_creations`, else `meld._conduit_creations` (solo both lanes, generalized
    manifest, site-plan lowering; many_only refuses disposal steps) - and `SpellSpaceMeld.purge` accepts
    `many` and only ever touches the space store. So the code settles the contract: through a space door,
    `many` lives in the space store, and the probe must read it there. No DECISION_REQUEST is needed.
    One unit test pins the wrong read: it seeds the owner conduit store and expects `owner_conduit_many`.
    The ConduitMeld probe reads its own conduit store, where its door puts `many`: no defect there.
    The probe runs only from the door's `describe_live_creation_status` / `has_live_creation` (no public
    SpellSpace probe; `Conduit.has_live_creation` uses the ConduitMeld); nothing on the meld path calls it.
  EVIDENCE:
  - src/melder/aether/conduit/meld/spellspace_meld.py:936-955
  - src/melder/aether/conduit/meld/spellspace_meld.py:180-236
  - src/melder/aether/conduit/meld/spellspace_meld.py:833-889
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:98-121
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:97-119
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:304-332
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:546-555
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1401-1409
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:44-53
  - src/melder/aether/conduit/meld/conduit_meld.py:994-1013
  - src/melder/aether/conduit/conduit.py:5003-5064
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:819-843
  - context_compass/artifacts/spellspace_probe_many_20260928/repro_0_2_8203.txt:1-5
  IMPACT: The fix is one branch of one diagnostic method plus its docstrings; storage routing, purge and the
    meld path do not change, so no benchmark is owed. The pinning unit test is rewritten, not deleted.
  NEXT: PLAN note with the exact files, then the patch docs and a red test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:33:13Z
  TYPE: PLAN
  CLAIM: melder_0 writes every file below. (1) spellspace_meld.py: the probe's `many` branch reads
    `self._spellspace_creations` and reports `storage_scope_kind` "spellspace_many", the owner conduit id and
    `active_spellspace_id` = this space (the same fields the `unique_per_spell_space` branch reports); the probe
    contract and the class contract say `many` is read from, tracked in and purged from the space's store.
    (2) Tests: in test_concrete_meld_subclasses.py rewrite the pinning test to seed the space store and expect
    "spellspace_many", and add one test that an owner-conduit `many` is not counted through the space door;
    in test_conduit_component_spellspace_creations.py add one end-to-end test (real conduit and space). Both
    red on 0.2.8203 first. (3) `__version__` notch at landing (read it; expected 0.2.8204). (4) Patch lane
    system_docs/patches/active/spellspace_probe_many_2026_09_28/ (architecture_patch, component patch for the
    Meld Resolution Runtime), promoted into src_components: a probe-scope paragraph and flow step, the
    "Known probe inaccuracy" failure mode removed, C1 remeasured, handoff. src_architecture and the test maps
    do not describe the probe and name neither test file, so they are unchanged. (5) Graph: extract, accept
    SpellSpaceMeld, assemble. (6) Release note section and header. (7) Assets and LLM bundles last.
    No benchmark: the probe is off the meld path.
  EVIDENCE:
  - src/melder/aether/conduit/meld/spellspace_meld.py:936-955
  - src/melder/aether/conduit/meld/spellspace_meld.py:971-983
  - context_compass/system_docs/src_components.md:2946-2950
  - context_compass/system_docs/src_components.md:6718-6726
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:819-843
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py:130-160
  IMPACT: One diagnostic branch changes; routing, purge, lifetimes and the meld path are untouched.
  NEXT: Write the patch docs, map them to the edits, then the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:34:10Z
  TYPE: DECISION
  CLAIM: Patch docs written and linked (architecture_patch 62 lines, component patch 55). Mapping to the edits:
    the component patch's After -> the probe's `many` branch and its contract lines in spellspace_meld.py;
    its Removed failure mode -> the src_components Creations and SpellSpace bullet; the architecture patch's
    invariant (a door's probe reads the store its meld writes and its purge retires) -> the Meld Resolution
    Runtime paragraph and the probe flow step; its Validation -> the unit and component tests and the logs in
    the lane's artifact directory. No code-description patch: the change is one store read in one branch.
  EVIDENCE:
  - context_compass/system_docs/patches/completed/spellspace_probe_many_2026_09_28/architecture_patch.md:1-65
  - context_compass/system_docs/patches/completed/spellspace_probe_many_2026_09_28/component_patch_meld_resolution_runtime.md:1-56
  IMPACT: Every edit in the PLAN note has a patch clause; nothing in the patch lacks an edit.
  NEXT: Write the red tests and run them on 0.2.8203.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:37:24Z
  TYPE: FACT
  CLAIM: Red, then fixed and landed. The 3 new tests failed on the 0.2.8203 source (2 unit on the old
    `owner_conduit_many` read; the component test counted the conduit's 1 object instead of the space's 2),
    then passed with the probe fix: test_concrete_meld_subclasses.py and the spellspace creations component
    file, 50 passed. The repro now reports is_live True, count 1, "spellspace_many" with the space id.
    Edits (apply scripts in the lane's artifact dir): the probe's `many` branch reads
    `self._spellspace_creations` and reports "spellspace_many" and the space id; the probe contract says so
    and dates the fix, and its lifetime lines now match the code (`unique` -> the Spell owner's store,
    lineage -> the lineage root, cluster -> the elected leader; the old text said all read `owner_creations`);
    the class contract gains one line. Tests name the fix date, not a version. `__version__` read at landing
    (0.2.8203) and set to 0.2.8204 at 00:37:03Z. Observed, not changed (not this lane's file):
    `ConduitMeld._describe_spell_live_creation_status`'s contract has the same "broad-lived existences read
    `owner_creations`" wording, while its code reads the lineage root and elected leader too.
  EVIDENCE:
  - src/melder/aether/conduit/meld/spellspace_meld.py:903-915
  - src/melder/aether/conduit/meld/spellspace_meld.py:949-969
  - src/melder/aether/conduit/meld/spellspace_meld.py:23-33
  - src/melder/__version__.py:12-12
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:819-880
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py:388-432
  - src/melder/aether/conduit/meld/conduit_meld.py:960-977
  - context_compass/artifacts/spellspace_probe_many_20260928/red_0_2_8203.txt:38-41
  - context_compass/artifacts/spellspace_probe_many_20260928/green_touched_gil0.txt:1-3
  - context_compass/artifacts/spellspace_probe_many_20260928/repro_after_fix.txt:1-5
  IMPACT: The fix is on the tree at 0.2.8204; suites, docs, graph, release note and assets follow.
  NEXT: NOTICE the landing, then run the conduit suites on three interpreters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:42:58Z
  TYPE: MEASURE
  CLAIM: Suites at 0.2.8204 on the VM copy (src and tests equal to the device): on 3.14t PYTHON_GIL=0 every
    tests/ tree passed - component 2230 (23 skipped, 1 xfailed), integration 1954, unit aether 4114, unit
    spellbook 2194, the other unit trees and experimentation 1917 - except package/asset tests, which wait for
    the rebuild, and tests/unit/github_workflows, which cannot be collected here (no PyYAML in the VM env). The
    conduit set plus the probe's consumers (nexus, static command system and frame viewer, two spellbook
    integration files) passed on PYTHON_GIL=1 and the GIL build: 2442 each.
  EVIDENCE:
  - context_compass/artifacts/spellspace_probe_many_20260928/suites_0_2_8204_vm.txt:1-10
  IMPACT: No regression from the probe change; the rebuild-dependent tests run after the assets.
  NEXT: Promote the patch into src_components and rebuild its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:47:30Z
  TYPE: FACT
  CLAIM: Docs and graph promoted. src_components: Meld Resolution Runtime gains "Live-creation probe scope" (each
    door reads the store its meld writes and its purge retires; the old SpellSpace `many` read CORRECTED), its
    store-selection responsibility is corrected against the code (`unique` -> the Spell owner's store, lineage ->
    lineage root, cluster -> elected leader, disposal-bearing `many` -> innermost scope; the old text put cluster
    and lineage in `spell._owner_creations`), the probe flow gains step 4, the Creations and SpellSpace "Known
    probe inaccuracy" failure mode is removed, spellspace_meld.py is remeasured (1045) and a handoff paragraph is
    added; index rebuilt (147 sections over 10165 lines), --check OK for all five indexed docs. Preservation: 11
    lines lost, each accounted for (5 removed failure mode, 3 rewritten bullet, 3 C1 fields). Graph: extraction
    --strict (skipped 0) re-hashed spellspace_meld, __version__ and 8 asset descriptors; SpellSpaceMeld's two
    responsibilities rewritten, then SpellSpaceMeld and melder.__version__ accepted after reading the source; no
    other authored field changed; a second extraction re-indented only; assemble wrote src_graph.md (27539 lines,
    584 ranges verified). Census 1059 -> 1061 AUTHORED, 143 -> 141 stale. No machine paths in the four docs.
    src_architecture and the test maps are unchanged: neither describes the probe.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3041-3053
  - context_compass/system_docs/src_components.md:3202-3208
  - context_compass/system_docs/src_components.md:6740-6743
  - context_compass/system_docs/src_components.md:9844-9850
  - context_compass/artifacts/spellspace_probe_many_20260928/doc_preservation/preservation_report.md:1-15
  - context_compass/artifacts/spellspace_probe_many_20260928/docs/edit_graph_descriptors.py:1-31
  - context_compass/artifacts/spellspace_probe_many_20260928/docs/graph_walker_report_after.txt:1-8
  - context_compass/system_docs/src_graph_index.md:156-156
  IMPACT: The canonical docs and graph describe the landed probe; the release note and assets remain.
  NEXT: Release-note section for 0.2.8204, header and packaging line.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:48:28Z
  TYPE: FACT
  CLAIM: Release note: header 0.2.8203 -> 0.2.8204; new section "Fixed: a SpellSpace's live-creation probe missed
    the `many` objects it holds" after the scope-exit section (what the probe reads now, why it was wrong, the
    payload values, and that `Conduit.has_live_creation`, other lifetimes and the meld path are unchanged); one
    packaging bullet for the probe-scope docs; the rebuild line says 0.2.8204. CRLF kept. The first wording said
    "Melder's diagnostics" call the space door's probe; only tests do, so it was reworded before any rebuild.
  EVIDENCE:
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:69-78
  - release_docs/next_version_release.md:88-90
  - context_compass/artifacts/spellspace_probe_many_20260928/docs/edit_release_note.py:1-50
  IMPACT: Every input of the asset and bundle builds is final.
  NEXT: Rebuild the assets in the VM copy, copy them over, --check on the device; then the LLM bundles.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:58:46Z
  TYPE: MEASURE
  CLAIM: Build outputs and final checks at 0.2.8204. Assets: built in the VM copy (the device folder refuses the
    builder's unlink), 7 outputs copied over, device --check OK for all three families; after the second doc
    pass (below) rebuilt again, 3 outputs changed and copied, --check OK. LLM bundles on the device with
    --include-untracked: run 1 wrote src, then replacing llm_full_tests.txt raised EACCES (the host held the
    file) and the builder could not unlink its temp; run 2 wrote all three bundles and manifest.json (the temp
    was renamed over the target, none left); after the second asset pass run 3 reported everything UNCHANGED;
    --check OK. Package/asset tests 288 passed (1 skipped) on 3.14t GIL 0 and 1 and the GIL build, twice; the
    conduit set 2442 on GIL 0 after the rebuild. Second doc pass: the Meld Resolution Runtime failure mode
    "SpellSpaceScopeError for unique_per_spell_space without an active spellspace (SpellSpaceThreadState:245)"
    contradicted the new probe paragraph; the conduit door raises RuntimeError "must be built from a
    spellspace" (meld, meld_existing_spell, describe_live_creation_status), so it was corrected and the handoff
    names it; preservation retaken: 15 lost lines, all accounted for. Rubric (self-scored from disk after the
    index rebuild; scope: the Meld Resolution Runtime entry and the Creations and SpellSpace failure modes):
    src_components 75/100 (B) - Fidelity 4 (touched claims checked by symbol; this pass found 2 stale claims
    in the entry, so untouched ones may drift too), Completeness 5 (all twelve fields, in order), Depth 4
    (older one-clause fields remain, e.g. Lifecycle/Cleanup), Addressability 3 (the C3 container heading),
    Join 3 (only spellspace_meld.py remeasured; conduit_meld.py carries a 2026-09-26 range), Mirror 3
    (tests_components not re-read; it names neither test file).
  EVIDENCE:
  - context_compass/artifacts/spellspace_probe_many_20260928/assets_0_2_8204.txt:1-13
  - context_compass/artifacts/spellspace_probe_many_20260928/llm_bundles_0_2_8204.txt:1-25
  - context_compass/artifacts/spellspace_probe_many_20260928/suites_final_0_2_8204_vm.txt:1-10
  - context_compass/artifacts/spellspace_probe_many_20260928/docs/edit_src_components_failure_mode.py:1-45
  - context_compass/artifacts/spellspace_probe_many_20260928/doc_preservation/preservation_report.md:1-19
  - src/melder/aether/conduit/meld/conduit_meld.py:537-542
  - context_compass/system_docs/src_components.md:3296-3302
  - context_compass/system_docs/src_components.md:3022-3331
  - context_compass/system_docs/src_components.md:3240-3240
  - context_compass/system_docs/src_components.md:206-206
  - context_compass/system_docs/src_components.md:7335-7339
  IMPACT: Everything the lane owns is current and checked; only closure remains.
  NEXT: Turn in under the owner's directive: summary, completed lanes, boards, release the file claims.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:59:15Z
  TYPE: DECISION
  CLAIM: Turned in on the owner's directive in chat (2026-09-28): "fix the problem you have yourself and send it,
    finish off your fixes and turn in the remaining things". Acceptance is that directive; the exit gate is
    met (red then green tests, suites on three interpreters, no meld-path change, docs, graph, notch 0.2.8204,
    release note, assets and bundles with both checks OK). Follow-ups for the owner, not done here: the
    ConduitMeld probe contract says broad-lived existences read `owner_creations` while its code reads the
    lineage root and elected leader too (docstring only; not this lane's file); the tool-path portability leak
    in the system docs' Indexing sections; fable_0's stale Meld, ConduitMeld and Spellbook graph nodes.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md:18-23
  - context_compass/tickets/tasks/completed/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md:33-35
  - src/melder/aether/conduit/meld/conduit_meld.py:970-977
  IMPACT: The ticket closes with every deliverable current; the three follow-ups stay recorded for the owner.
  NEXT: Close: summary, completed lanes (ticket and patch), boards, release the file claims, owner report.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
State (2026-09-28): done. At 0.2.8204 the SpellSpace door's live-creation probe reads `many` from the space's
own store - where every emitter registers a disposal-bearing `many` melded through a space and where the
space's purge retires it - and reports "spellspace_many" with the space id; it no longer counts the owner
conduit's `many`. The conduit probe, storage routing and the meld path are unchanged. Docs (src_components,
including two corrected Meld runtime claims), graph, release note, assets and bundles are current; suites
green on three interpreters. Follow-ups for the owner, not done here: the ConduitMeld probe contract's
lifetime wording (docstring only), the tool paths in the system docs' `## Indexing` sections, and fable_0's
stale Meld, ConduitMeld and Spellbook graph nodes.

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
