

- Completed: 2026-09-26T12:13:26Z
- Summary: Site-graph Phase-9 section, OverrideKeyResolver and a 4-world differential oracle shipped in the
  working tree; 31 new tests, no other outcome changed on 3.14t or GIL; owner accepted.

# Task: S1 - build the site graph and the override key resolver with a differential oracle

## Metadata
- Task ID: TASK-2026-09-26-build-site-graph-and-override-key-resolver
- Story: STORY-2026-09-26-implement-override-site-plan-lowering
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T11:28:08Z
- Updated: 2026-09-26T12:13:26Z

## Objective
Add the Phase-9 `site_graph_shape` section and a pure `OverrideKeyResolver`, and prove the resolver agrees
with today's targeting on a corpus of conjured graphs. No runtime behavior changes.

## Ticket Contract
- ENTRY_GATE: Patch docs in system_docs/patches/active/override_site_plan_2026_09_26/ read and mapped in
  Notes; owner confirmation of the file list below.
- EXECUTION_BOUNDARY: The files under "Files / Paths Impacted" only. Work in the VM copy first, then apply
  to the device tree. No emitter, executor, cache, version or asset change.
- DEPENDENCIES: architecture_patch.md, component_patch_spellcompiler_validation_pipeline.md,
  code_description_patch_override_key_resolver.md; the Phase-9 instance and injection processors.
- EXIT_GATE: new and updated tests pass on 3.14t and GIL; full unit suite passes on 3.14t; conjure cost of
  the extra pass measured; notes map each patch section to code and tests; task in review.
- FAILURE_ESCALATION: CONFLICT if today's targeting disagrees with the resolver outside the recorded
  collection difference; BLOCKER if the full suite regresses.

## Scope Boundaries
- In scope: the new section, strategy, resolver, model slot, strategy registration, tests.
- Out of scope: using the section at run time (S2/S3), manifests, Phase 5, docs promotion (story closure).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Story opened after owner approval; waiting for the S1 file-list confirmation.
- from_state: ready
- to_state: in_progress
- transition_reason: Owner confirmed the S1 file list ("ok continue send it"), 2026-09-26T11:32:14Z.
- from_state: in_progress
- to_state: review
- transition_reason: Exit gate met 2026-09-26T12:09:44Z (A/B suites on 3.14t, GIL runs, cost measured,
  closure mapping in Notes); applied to the device tree. Owner review pending.
- from_state: review
- to_state: done
- transition_reason: Owner accepted S1, 2026-09-26T12:13:26Z.

## Steps / Checklist
- [x] Map patch sections -> implementation -> validation in Notes.
- [x] Add `SpellSiteParam`, `SpellSite`, `SpellSiteGraphAnalysis` (value rows plus Cleanable analysis).
- [x] Add `SpellSiteGraphProcessorStrategy` and register it after the injection strategy.
- [x] Add `site_graph_shape` to `SpellCodegenModel` (slot, init, cleanup, section_names).
- [x] Add `OverrideKeyResolver` and `OverrideKeyResolution`.
- [x] Unit tests for the analysis/strategy and the resolver; update the processor core tests.
- [x] Component differential oracle against `SpellOverrideTargetingCodegenCreation`.
- [x] Run touched tests on 3.14t and GIL, the full unit suite on 3.14t; measure conjure cost.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The source and test files below, and validation results in Notes.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_site_graph_analysis.py (new)
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py (new)
- src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py
- src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/override_key_resolver.py (new)
- tests/unit/melder/spellbook/spell_compiler/test_spell_site_graph_processor.py (new)
- tests/unit/melder/spellbook/spell_compiler/test_override_key_resolver.py (new)
- tests/component/melder/spellbook/test_spellbook_component_override_key_oracle.py (new)
- tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py

## Validation
- Run 2026-09-26 (see Notes 11:54:20Z, 12:06:46Z, 12:09:44Z): VM A/B on 3.14t (full unit and component
  suites, S1 adds 31 passing tests, no other change), GIL (touched files, unit and component spellbook), device
  tree A/B (identical pre-existing failures from fable_0's in-flight task 5). Coverage: not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook/test_spellbook_component_override_key_oracle.py`
  - `pytest -q tests/unit`

## Risks / Rollback Notes
- New internal classes: the bind-guard manifest and packaged system documents need a build-asset rebuild
  at story closure (owner approval and coordination with melder_1 and fable_0).
- Rollback: unregister the strategy and remove the model slot.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - system_docs/patches/active/override_site_plan_2026_09_26/architecture_patch.md
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_spellcompiler_validation_pipeline.md
  - system_docs/patches/active/override_site_plan_2026_09_26/code_description_patch_override_key_resolver.md
  - artifacts/melder_override_design_20260926/s1_staging/ (staged sources, apply_s1_edits.py, s1_conjure_cost.py)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (s1_staging)
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Phase-9 site graph and override key resolution
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T11:28:08Z
  TYPE: PLAN
  CLAIM: S1 builds the site graph from the Phase-9 instance/injection sections and Phase-3 topologies (every
    parameter with position and kind), and the resolver per the code-description patch; the oracle compares
    resolver targets projected to (spell id, parameter) plus logical counts and error texts against today's
    `SpellOverrideTargetingCodegenCreation`. The prototype (v2_prototype.py) is the reference for walk, DP
    counts and cut fixpoint; production reads topology instead of `inspect`.
  EVIDENCE:
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_spellcompiler_validation_pipeline.md
  - artifacts/melder_override_design_20260926/v2_prototype.py:77-286
  IMPACT: Fixes S1's surface before code; S2/S3 consume the section without re-deriving it.
  NEXT: Owner confirms the file list; then map patch sections and implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T11:32:14Z
  TYPE: PLAN
  CLAIM: Patch consumption mapping (read order architecture -> component -> code description done).
    (1) architecture Invariant 5 / component "no runtime consumer" -> no emitter, executor, cache or version
    edit; validated by the unchanged full unit suite and today's targeting still serving melds.
    (2) component section fields -> SpellSiteParam/SpellSite/SpellSiteGraphAnalysis in
    data/spell_site_graph_analysis.py; validated by analysis unit tests and cleanup test.
    (3) component inputs/ordering -> SpellSiteGraphProcessorStrategy reading instance_shape, injection_shape
    and Phase-3 topologies, registered after spell_injection_processor; validated by strategy unit tests and
    the updated registry-order test. (4) model slot + section_names -> spell_codegen_model.py; validated by
    the updated model cleanup/section test. (5) code-description steps 1-8 -> OverrideKeyResolver in
    shared_assets/override_key_resolver.py; validated by resolver unit tests (forms, ranks, cuts incl. the
    Codex leak, conflicts, arity, error texts). (6) validation plan oracle -> component test comparing
    resolver targets (spell id, param) and logical counts with SpellOverrideTargetingCodegenCreation.
  EVIDENCE:
  - system_docs/patches/active/override_site_plan_2026_09_26/architecture_patch.md
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_spellcompiler_validation_pipeline.md
  - system_docs/patches/active/override_site_plan_2026_09_26/code_description_patch_override_key_resolver.md
  IMPACT: Every patch section has one implementation step and one validation step before code starts.
  NEXT: Implement the analysis module in the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:36:55Z
  TYPE: FACT
  CLAIM: S1 source written and applied to the VM copy only (CRLF preserved; staged copies in s1_staging/):
    SpellSiteParam/SpellSite/SpellSiteGraphAnalysis (slotted value rows, validated indexes, Cleanable
    section), SpellSiteGraphProcessorStrategy (iterative parents-first DFS over injection dependency keys,
    Phase-3 sockets for every parameter, source-only fallback when a topology is absent, DP path counts),
    OverrideKeyResolver (frontier PATH walk, UNIQUE via path counts, BROADCAST via name index, ARGS rank,
    cut fixpoint, winners/conflicts), model slot + section name, registration after injection. Smoke on
    p3_alias (3.14t): strategy order and sections as designed; D (shared) path count 2 and X under it 2;
    {"p", "p>d>x"} -> p>d>x inactive (Codex leak case); "*x" -> today's "matched 2 sockets"; a real override
    meld still runs through today's executors.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/s1_staging/spell_site_graph_analysis.py
  - artifacts/melder_override_design_20260926/s1_staging/spell_site_graph_processor_strategy.py
  - artifacts/melder_override_design_20260926/s1_staging/override_key_resolver.py
  - artifacts/melder_override_design_20260926/s1_staging/apply_s1_edits.py
  IMPACT: The section and resolver behave as the patch docs specify on a real conjured graph.
  NEXT: Write the unit tests, the processor-core test update and the component oracle.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T11:49:56Z
  TYPE: FACT
  CLAIM: Consumed mailbox M1-12 (melder_1 -> melder_0, 2026-09-26T11:33:02Z, NOTICE, no ACK requested),
    copied here before deletion: "re M0-21/M0-20: no overlap with S1. function_spell_ids is closed (owner
    accepted); it changed bind.py, binding profiles/strategy, InspectorUtility, spellbook_creation_system.py
    (conjure-end restage) and caching_system.py. Cache generation 12 is TAKEN (complete_bundle_restage):
    S2/S3 need 13, and should rebase on _stage_spell_payloads_at_conjure_end (non-full-hit conjure removes
    all payloads, re-stages live ids)." S1 touches none of those files. The story's generation-12 plan is
    stale: S2/S3 bump to 13.
  EVIDENCE: tickets/tasks/completed/2026-09-26_stabilize_function_spell_ids_across_processes_task.md
  IMPACT: No S1 conflict; S2/S3 patch docs must name cache generation 13 and rebase on the conjure-end
    restage.
  NEXT: Stage the S1 unit tests and the oracle into the VM copy and run them.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T11:49:56Z
  TYPE: FACT
  CLAIM: Re-onboarded after compaction (REONBOARD attestation, owner re-certified melder_0). Before
    re-onboarding, one scratchpad-only write occurred (oracle test draft in the cloud workspace); no
    repo, board or device file was touched before certification. Handoff summary corrected below.
  EVIDENCE: context_compass/agent_onboarding/default/general/skills/compaction_requirements.md:1-162
  IMPACT: Session state recovered from ticket, board and mailbox; the lane resumes at the tests.
  NEXT: Stage the S1 unit tests and the oracle into the VM copy and run them.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T11:50:36Z
  TYPE: FACT
  CLAIM: Consumed mailbox F0-6 (fable_0 -> melder_0, 2026-09-26T11:50:16Z, NOTICE, no ACK requested), copied
    here before deletion: "Owner ruled 2026-09-26: SpellContract/SpellMap override values may be anything and
    ride the normal overrides path; the keyword `spell_override` renames to `override`. fable_0's task 5
    records value-only refs in phase 9, makes rows ref-only, and resolves refs to live values at hydration in
    the NO-OVERRIDES lanes (small hunks in generalized_manifest_no_overrides_compiler.py,
    generalized_hydrator.py, the many_only and solo equivalents). Requirement for design v2 S2/S3: a contract
    payload value is a live operand read from the consumer's descriptor (like `ov["key"]`), never a
    literal; your U1 answer: the injection processor keeps a dependency parameter as `kind="dependency"` and
    adds `contract_key`." For S1 this matches the site graph: SpellSiteParam carries source_kind and
    contract_key from the injection source, and the resolver walks only dependency edges. U1 (contract vs
    dependency ordering) is answered: a contract-backed dependency stays a dependency edge.
  EVIDENCE: tickets/tasks/2026-09-26_live_contract_override_operands_task.md
  IMPACT: S2/S3 lowering must emit contract payloads as live descriptor reads; fable_0 edits the no-overrides
    hydrators and a phase-9 processor, so S2/S3 need a mailbox notice before touching those files. Whether
    task 5 edits spell_codegen_model.py (an S1 file) is UNKNOWN.
  NEXT: Before applying S1 to the device tree, diff spell_codegen_model.py and the builder against the VM copy
    baseline to catch concurrent edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T11:54:20Z
  TYPE: MEASURE
  CLAIM: New S1 tests pass on 3.14t in the VM copy: test_spell_site_graph_processor.py plus
    test_override_key_resolver.py 27 passed; test_spellbook_component_override_key_oracle.py 4 passed. The
    oracle compared all 46 keys today's targeting indexes across four conjured worlds (many tree 14,
    shared diamond 20, unresolved input 6, collection 6) plus 5 shared invalid keys and per-world extras;
    only "members>leaf" differs (today 1 target, the resolver 2), as recorded. Two test expectations were
    wrong and were fixed to match the patch contract, not the code changed: sibling sites come in reversed
    DFS post-order (root, b, a), which is what code-description step 2 specifies; `is_cleaned` is a
    property. The oracle's unresolved-input world now melds with override={"work": ...}.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_override_key_oracle.py:195-281
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py:221-260
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_spellcompiler_validation_pipeline.md:61-62
  IMPACT: The resolver matches today's key semantics, counts and error texts on real graphs; S1's
    remaining exit items are the processor-core test update, GIL runs, the full unit suite and conjure cost.
  NEXT: Update test_spell_artifact_processor_core.py for the new strategy and section.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:54:20Z
  TYPE: RISK
  CLAIM: Pre-existing behavior found by the oracle: in a collection, a many-existence dependency of the
    members is ONE shared object. Probe: CollectionRoot(members: list[IMember]) over MemberA(leaf: Leaf) and
    MemberB(leaf: Leaf), all many -> members[0].leaf is members[1].leaf is True. Cause: path ids are interned
    by (parent path id, parameter name), so both members sit on path "members" and both leaf dependencies
    get instance key (Leaf, id("members>leaf")); Existence.many yields one instance per path id, not per
    consumer. The site graph inherits this (Leaf site not shared, path count 2), and today's "members>leaf"
    keeps one row for the same reason. S1 does not change it; S2/S3 lowering over instance keys would
    preserve it. Whether this is intended is UNKNOWN and is the owner's call.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:118-150
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:131-190
  IMPACT: Behavior-preserving for S1; if the owner wants per-member many instances, that is a Phase-8/9
    path-keying change outside this story, and the S1 invariant "many sites have path count 1" does not
    hold for collection members' dependencies (the code does not assume it).
  NEXT: Ask the owner in the S1 review summary; continue S1 meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:06:46Z
  TYPE: MEASURE
  CLAIM: S1 A/B on one consistent VM tree (~/work/melder with S1 vs ~/work/melder_oldbase, identical except
    the nine declared files; PYTHONPYCACHEPREFIX set; repo docs/tool dirs synced so env failures vanish).
    3.14t, S1 vs base: unit spellbook 2137 vs 2110 (+27 new), aether 4124/4124, crystallizer 565/565,
    mutation_research 277/277, utilities 785+2s+7xf both, build_assets 116/116, unit root files 145/145,
    architecture_and_design 18, llm_support 28; component spellbook 730+1xf vs 726+1xf (+4 oracle), aether
    1186+1s+1xf both, mutation_research 40/40, utilities 41+23s both. All passed. The only failures seen,
    component crystallizer file_backed_morph x4, occur identically on both sides (environmental). GIL
    (3.14.7): the four touched files 11+16+5+4 passed; unit spellbook 2137 and component spellbook 730+1xf
    passed. Earlier failures in the stale copy were the environment: Windows __pycache__ files (method
    inspector source reads) and missing architecture_and_design/, .github/, context_compass/system_docs/.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/s1_staging/apply_s1_edits.py:1-201
  - tests/component/melder/spellbook/test_spellbook_component_override_key_oracle.py:195-281
  IMPACT: S1 adds 31 passing tests and changes no existing outcome on 3.14t or GIL.
  NEXT: Record the conjure-cost measure, then apply S1 to the device tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:06:46Z
  TYPE: MEASURE
  CLAIM: Conjure cost of the new pass (s1_conjure_cost.py: every Phase-9 strategy wrapped with a timer, 7
    fresh worlds per graph, disk caching off, medians; "setup" is bind plus conjure). 3.14t:
    shallow 0.034 ms of 4.50 ms (0.8%), wide 0.101/7.39 (1.4%), diamond 0.060/5.41 (1.1%), deep 4.35/56.9
    (7.6%; Phase 9 total 13.9 ms, 17 calls). GIL: 0.7%, 1.1%, 1.1%, 6.8% (deep 3.49/51.0). Cost is linear
    in instance keys: the deep root alone has 511 sites and all 17 per-spell graphs 1515; a profile puts
    about half of it in SpellSiteGraphAnalysis.__init__ (row validation and the three indexes), the rest in
    per-site param rows and the DFS. Many sites are physical objects, so this scales with objects built,
    not with shared-alias path enumeration (which S5 retires).
  EVIDENCE:
  - artifacts/melder_override_design_20260926/s1_staging/s1_conjure_cost.py:1-71
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_site_graph_analysis.py:282-341
  IMPACT: Small graphs pay about 1%; the deep many-graph pays 7% of setup. If that matters, S2 can drop the
    duplicate validation loop or build per-spell socket rows once; both are local to S1's files.
  NEXT: Send fable_0 the pre-edit notice for the two Phase-9 shared files, then apply S1 to the device tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:06:46Z
  TYPE: FACT
  CLAIM: The device tree is mid-edit by fable_0 (task 5): SpellOccurrenceContractAnalysis now requires
    contract_override_refs_by_occurrence but its processor does not pass it yet, so every conjure in a
    synced copy fails in Phase 9 ("plan_group ... missing 1 required keyword-only argument"), with or
    without S1 (identical failures in ~/work/melder_s1base and ~/work/melder_s1). The S1 delta against the
    current device tree is exactly the nine declared files, and the device copies of the three edited
    files are byte-identical to the VM baseline (apply_s1_edits.py on them reproduces the VM results).
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_occurrence_contract_analysis.py:8-81
  IMPACT: S1 can be applied to the device tree without conflict; a device-tree run stays blocked on
    fable_0's in-flight work and is not a signal about S1.
  NEXT: Notify fable_0 (M0-22), apply S1, verify the device files against the staged copies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T12:09:44Z
  TYPE: FACT
  CLAIM: S1 applied to the device tree after notice M0-22 to fable_0: three new src files and three new test
    files copied from s1_staging with cp -n (none existed), apply_s1_edits.py run against the repo root (each
    anchor matched once, CRLF kept). All nine device files are byte-identical to the validated VM copy. A/B on
    a fresh sync of the device tree (fable_0's task 5 in flight): unit spellbook 34 failed/2117 passed with
    S1 vs 34/2090 without; component spellbook 7/729 vs 7/725; component aether 70/1116 both. The failure
    sets are identical line for line; they come from the in-flight contract-override work (e.g. "Shared
    provider received 2 distinct descriptor override payloads"), not from S1.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:25-313
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:29-114
  IMPACT: S1 is in the working tree; its tests pass on the device state and it changes no other outcome
    there either. A green full-suite run on the device tree waits for fable_0's task 5.
  NEXT: Write the closure mapping and move the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:09:44Z
  TYPE: FACT
  CLAIM: Patch section -> code -> validation, as delivered. (1) architecture Invariant 5, no runtime
    consumer: no emitter, executor, cache, version or asset file touched; A/B suites unchanged. (2) component
    section fields: data/spell_site_graph_analysis.py (SpellSiteParam, SpellSite, SpellSiteGraphAnalysis with
    validation, indexes, idempotent cleanup) -> test_spell_site_graph_processor.py malformed-rows, cleanup,
    param-lookup tests. (3) inputs and ordering: strategies/spell_site_graph_processor_strategy.py (reversed
    DFS post-order, Phase-3 sockets for every parameter, source fallback, path counts) registered after
    spell_injection_processor -> graph-shape, shared, collection, every-parameter, fallback, missing-spec,
    process tests plus the updated registry-order test. (4) model slot and section_names:
    spell_codegen_model.py -> updated test_spell_codegen_model_cleanup_cleans_owned_sections_only (asserts
    site_graph_shape cleanup). (5) code-description steps 1-8: shared_assets/override_key_resolver.py ->
    test_override_key_resolver.py (16 tests: forms, error texts, ranks, P1 cut, P3 alias, validation under a
    cut, conflicts, positional arity, collection fan-out, purity). (6) validation-plan oracle ->
    test_spellbook_component_override_key_oracle.py (4 conjured worlds, 46 indexed keys, invalid keys, the
    recorded collection difference).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_site_graph_analysis.py:1-382
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py:1-362
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/override_key_resolver.py:1-334
  - tests/unit/melder/spellbook/spell_compiler/test_spell_site_graph_processor.py:1-308
  - tests/unit/melder/spellbook/spell_compiler/test_override_key_resolver.py:1-193
  - tests/component/melder/spellbook/test_spellbook_component_override_key_oracle.py:1-281
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py:154-289
  IMPACT: Every S1 patch section has shipped code and a passing test; the exit gate is met on the
    consistent tree (3.14t full unit and component A/B, GIL touched plus spellbook suites, cost measured).
  NEXT: Owner review of S1; open S2 (shared lowering for normal melds) after acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:13:26Z
  TYPE: DECISION
  CLAIM: Owner accepted S1 ("sure keep working on this thing don't stop until your done") and ruled on the
    RISK note: "a many is not meant to be shared like that" - one many-existence object shared by collection
    members is a defect, not intended behavior. S1 closes; the defect becomes its own task under the story,
    fixed before S2 so the lowering is built on correct instance keys. The standing instruction to continue
    without stopping is taken as confirmation to proceed step by step; each step still records its file list
    and patch docs in its ticket before code.
  EVIDENCE: tickets/tasks/completed/2026-09-26_build_site_graph_and_override_key_resolver_task.md
  IMPACT: S1 done; next lane is the collection-member many-sharing fix, then S2-S6.
  NEXT: Closure sync, then open the defect task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Review. S1 is in the device working tree (nine declared files, uncommitted): site-graph section, strategy,
model slot, registration, OverrideKeyResolver, 27 unit tests, a 4-world differential oracle and the updated
processor-core test. Validated on 3.14t and GIL with no change to other outcomes; the extra Phase-9 pass costs
about 1% of setup on small graphs and 7% on the deep many-graph. Open for the owner: accept S1; decide whether
the shared many-dependency under collection members (RISK note 11:54:20Z) is intended. S2 uses cache
generation 13 (M1-12) and emits contract payloads as live reads (F0-6).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
