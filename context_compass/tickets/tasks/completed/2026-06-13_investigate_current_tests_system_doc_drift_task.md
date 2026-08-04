<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Investigate Current Tests System Doc Drift

## Metadata
- Task ID: TASK-2026-06-13-investigate-current-tests-system-doc-drift
- Story: none
- Epic: none
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p0
- Created: 2026-06-13T17:00:51Z
- Updated: 2026-06-13T17:00:51Z

## Objective
Explore the live test system and produce an evidence-backed inventory of
current drift across:
- `tests_architecture.md`
- `tests_components.md`

## Ticket Contract
- ENTRY_GATE: the source-doc graph lane is complete for the allowed
  non-mutation scope, and the user explicitly directed continuation, so the
  next bounded docs lane is tests-system drift rather than widening the source
  docs task.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/system_docs/tests_architecture.md`
  - `codex/context_compass/system_docs/tests_components.md`
  - live `tests/**`
  - supporting source-system docs only where test docs depend on them:
    `src_architecture.md`, `src_components.md`, `readable_src_graph.json`
  - `codex/context_compass/attention_board.md`
  - this task
- DEPENDENCIES:
  - `codex/context_compass/system_docs/tests_architecture.md`
  - `codex/context_compass/system_docs/tests_components.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/attention_board.md`
- EXIT_GATE:
  - at least one concrete tests-doc drift finding exists with evidence
  - the next bounded patch slice is explicit
  - unknown-first discipline is maintained
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  tests-doc drift cannot be bounded without crossing into a different docs
  program.

## Scope Boundaries
- In scope:
  - tests-system doc drift for test architecture and test components
  - evidence gathering from live `tests/**`
  - identifying the next bounded refresh slice
- Out of scope:
  - source-system graph population work already completed in the sibling task
  - mutation-research doc investigation
  - crystallizer doc investigation
  - broad rewrite before drift is evidenced

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly directed continued documentation work
  after the source-doc lane reached its non-mutation boundary.

## Steps / Checklist
- [ ] Re-read the key tests-system docs and note likely drift seams.
- [ ] Verify likely drift seams against live `tests/**` code.
- [ ] Record the first concrete drift findings in `## Notes`.
- [ ] Define the first bounded patch slice from those findings.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- evidence-backed tests-doc drift inventory
- explicit next patch slice

## Files / Paths Impacted
- `codex/context_compass/system_docs/tests_architecture.md`
- `codex/context_compass/system_docs/tests_components.md`
- `codex/context_compass/tickets/tasks/2026-06-13_investigate_current_tests_system_doc_drift_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "^## " codex/context_compass/system_docs/tests_architecture.md`
  - `rg -n "^## " codex/context_compass/system_docs/tests_components.md`

## Risks / Rollback Notes
- Risk: the tests docs may pull CI or external harness concerns that are not
  visible in-repo.
- Risk: the lane could widen into test implementation review instead of docs
  drift.
- Rollback: keep this task investigation-only until one bounded drift slice is
  explicit.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No tests-doc rewrite before concrete drift is recorded.
- [ ] No widening from tests docs back into source docs without a new note and
      explicit rationale.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - tests-system doc drift
  - tests architecture/components mismatch
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-13T17:00:51Z
  TYPE: PLAN
  CLAIM: The next bounded docs lane is tests-system drift. The source-doc graph
    lane is complete for the active non-mutation scope, so the right
    continuation is a sibling task focused on `tests_architecture.md`,
    `tests_components.md`, and live `tests/**` evidence.
  EVIDENCE:
  - user_instruction: `continue please`
  - codex/context_compass/tickets/tasks/2026-06-12_investigate_current_source_system_doc_drift_task.md
  IMPACT: This keeps continuation real without silently widening the finished
    source-doc task.
  NEXT: inspect the two tests docs against live `tests/**` and record the first
    concrete drift seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:02:33Z
  TYPE: FACT
  CLAIM: The first concrete tests-doc drift seam is stale inventory counts in
    `tests_architecture.md`. The doc still claims `unit=274`,
    `component=66`, `integration=76`, and `mocks=13`, but the live tree is now
    `unit=334`, `component=81`, `integration=88`, and `mocks=42`.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:75-79
  - validation_result: `unit 334`
  - validation_result: `component 81`
  - validation_result: `integration 88`
  - validation_result: `mocks 42`
  IMPACT: The tests architecture doc is materially understating current suite
    size, especially the mock corpus, so the current system shape is no longer
    accurately represented.
  NEXT: patch the inventory counts in `tests_architecture.md` and then look for
    the next bounded tests-doc seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:03:38Z
  TYPE: FACT
  CLAIM: The tests docs also understate the live subtree layout. The documented
    unit/component/integration mirrors omit the `crystallizer` and
    `mutation_research` test directories that currently exist under
    `tests/*/melder/`.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:104-109
  - codex/context_compass/system_docs/tests_components.md:128-151
  - validation_result: `tests/unit/melder -> aether, crystallizer, mutation_research, spellbook, utilities`
  - validation_result: `tests/component/melder -> aether, crystallizer, mutation_research, spellbook, utilities`
  - validation_result: `tests/integration/melder -> aether, conduit, crystallizer, live_sim, multithreading, mutation_research, spellbook`
  IMPACT: The tests docs are currently describing an older narrower mirror of
    the test tree than what actually exists, so readers will miss whole test
    subdomains.
  NEXT: patch the tests architecture/components catalog bullets to include the
    live subtree layout, then continue the tests-doc audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:05:01Z
  TYPE: FACT
  CLAIM: The tests mock corpus description is now too narrow. The live
    `tests/mocks` tree contains both `spellbook` and `crystallizer` fixture
    packs, but the current docs still frame the mock layer as a
    spellbook/scan-bind-only helper corpus.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:111-112
  - codex/context_compass/system_docs/tests_components.md:290-340
  - validation_result: `tests/mocks -> crystallizer/, spellbook/, SKILLS.MD`
  IMPACT: Readers are not told that crystallizer tests rely on a dedicated
    mock/harness subtree, so the test support surface is understated even after
    the tier catalogs are fixed.
  NEXT: patch the mock-corpus descriptions in the two tests docs to include the
    crystallizer support subtree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:06:11Z
  TYPE: FACT
  CLAIM: The CI-sharding unknown in the tests docs can be tightened. This
    checkout has no `.github/` directory or local workflow config at all, so
    the docs should stop implying that the next evidence target is in-repo CI
    files and instead state that no in-repo CI topology is available here.
  EVIDENCE:
  - validation_result: `NO_DOT_GITHUB`
  - README.md:25
  - roadmap.md:112-130
  IMPACT: The tests docs can replace a stale investigation-style unknown with a
    more accurate scope statement about local versus external CI evidence.
  NEXT: patch the tests-doc unknown/open-question wording to say there is no
    in-repo CI workflow evidence in this checkout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:08:02Z
  TYPE: FACT
  CLAIM: The active tests docs also have stale metadata after today's edits.
    Both `tests_architecture.md` and `tests_components.md` still show
    `Updated: 2026-04-13` even though they were modified in this lane.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:3-8
  - codex/context_compass/system_docs/tests_components.md:3-8
  IMPACT: The docs' own metadata is now behind their content, which weakens
    re-entry trust for future readers.
  NEXT: patch the two tests-doc `Updated` fields to `2026-06-13`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:10:24Z
  TYPE: MEASURE
  CLAIM: The local-evidence tests-doc cleanup tranche is landed. The stale tier
    counts are corrected, the tier subtree catalogs now include crystallizer
    and mutation_research, the mock corpus now includes crystallizer harness
    support, the CI unknowns now state that this checkout has no in-repo
    workflow evidence, both docs now show `Updated: 2026-06-13`, and both
    tests docs have `MISSING_COUNT 0` for referenced local paths.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:44-52
  - codex/context_compass/system_docs/tests_architecture.md:91-112
  - codex/context_compass/system_docs/tests_architecture.md:320-329
  - codex/context_compass/system_docs/tests_components.md:30-38
  - codex/context_compass/system_docs/tests_components.md:166-176
  - codex/context_compass/system_docs/tests_components.md:248-270
  - codex/context_compass/system_docs/tests_components.md:313-352
  - validation_result: `tests_architecture.md MISSING_COUNT 0`
  - validation_result: `tests_components.md MISSING_COUNT 0`
  IMPACT: The remaining unresolved tests-doc unknowns are now external-CI-only.
    Within this checkout, the bounded tests-doc drift seams found so far are
    fixed.
  NEXT: decide whether to stop at the external-evidence boundary or widen into a
    deeper tests-doc semantic review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:12:26Z
  TYPE: FACT
  CLAIM: A deeper local semantic seam remains in `tests_components.md`: the C2
    subcomponent map still only spells out Aether-oriented clusters plus the
    spellbook mock subset, even though the live tests include explicit
    crystallizer and mutation-research unit/component/integration clusters and
    a crystallizer mock harness subtree.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:217-424
  - tests/unit/melder/crystallizer/test_crystallizer.py
  - tests/unit/melder/crystallizer/test_synthetic_module.py
  - tests/unit/melder/mutation_research/test_mutation_research_root.py
  - tests/component/melder/crystallizer/test_spell_crystal_component.py
  - tests/component/melder/mutation_research/test_mutation_research_root_component.py
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py
  - tests/integration/melder/mutation_research/test_mutation_research_root_integration.py
  - tests/mocks/crystallizer/spell_crystal_harness.py
  - tests/mocks/crystallizer/synthetic_module_harness.py
  IMPACT: The top-level tier catalogs are now accurate, but the detailed C2 map
    is still skewed toward the older Aether/spellbook view of the test system.
  NEXT: add bounded C2 subcomponents for crystallizer and mutation-research
    clusters plus the crystallizer mock harness surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:14:03Z
  TYPE: MEASURE
  CLAIM: The deeper local tests-components patch is landed too. The C2 map now
    includes crystallizer and mutation-research unit/component/integration
    clusters plus the crystallizer mock harness surface, so the detailed test
    component map now matches the expanded tier catalogs instead of stopping at
    the older Aether/spellbook-only view.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:411-499
  IMPACT: Within this checkout, the tests-doc lane has moved past count and
    path cleanup into real component-map correction. The remaining unresolved
    drift is now the external-CI boundary unless we choose an even deeper
    semantic review.
  NEXT: update the routing board to the new tests-doc state and decide whether
    any further local semantic seam remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:37:17Z
  TYPE: FACT
  CLAIM: Another local tests-doc semantic seam remains: the shared support and
    experimentation surfaces are under-described. Live tests broadly use
    `tests/_frame_posture_test_support.py`, and crystallizer synthetic-module
    component/integration tests route through `tests/experimentation/*`, but
    the current docs barely or never name those helpers.
  EVIDENCE:
  - validation_result: widespread `from tests._frame_posture_test_support import ...` across unit/component/integration tests
  - tests/component/melder/crystallizer/test_synthetic_module_component.py
  - tests/integration/melder/crystallizer/test_synthetic_module_integration.py
  - validation_result: `tests/experimentation/*` inventory present in checkout
  IMPACT: The tests docs still present a narrower support-layer story than the
    live test suite actually uses, especially for frame-posture configuration
    and crystallizer synthetic-module experiments.
  NEXT: patch the tests architecture/components docs to include
    `_frame_posture_test_support.py` and the experimentation harness layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:40:33Z
  TYPE: MEASURE
  CLAIM: The shared-support patch is landed too. The tests architecture doc now
    names `_frame_posture_test_support.py` and the experimentation bench layer
    in its evidence/support story, and `tests_components.md` now includes those
    support surfaces in the shared-support component plus explicit C2 entries
    for frame-posture support and synthetic-module experiment benches.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:76-82
  - codex/context_compass/system_docs/tests_architecture.md:107-115
  - codex/context_compass/system_docs/tests_components.md:121-172
  - codex/context_compass/system_docs/tests_components.md:382-428
  IMPACT: The local tests-doc lane now covers not just tier counts and
    subtrees, but also the major shared support surfaces the live suite relies
    on.
  NEXT: decide whether any remaining local tests-doc seam is worth another
    bounded patch or whether the lane should now stop at the external-CI
    evidence boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:41:17Z
  TYPE: FACT
  CLAIM: One local consistency seam still remains in `tests_components.md`:
    the `Information Sources` list still reflects the older narrower readset
    and omits the support files and experimentation benches that now justify
    the shared-support and deeper C2 updates.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:624-638
  - codex/context_compass/system_docs/tests_components.md:121-172
  - codex/context_compass/system_docs/tests_components.md:382-428
  IMPACT: The component doc content is ahead of its cited evidence list, which
    weakens traceability even though the component map itself is now better.
  NEXT: patch the `Information Sources` list in `tests_components.md` to
    include the support-layer and new cluster evidence files already used.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T17:42:13Z
  TYPE: MEASURE
  CLAIM: The local-evidence tests-doc pass is now effectively exhausted. The
    stale counts, subtree catalogs, mock-corpus wording, CI local-evidence
    wording, metadata dates, deeper C2 clusters, and support-layer
    information-source gaps are all fixed. The remaining unresolved tests-doc
    unknown is external CI topology, and there is no in-repo workflow evidence
    in this checkout to resolve it further.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md
  - codex/context_compass/system_docs/tests_components.md
  - validation_result: `tests_architecture.md MISSING_COUNT 0`
  - validation_result: `tests_components.md MISSING_COUNT 0`
  - validation_result: `NO_DOT_GITHUB`
  IMPACT: Further work in this tests-doc lane would either need external CI
    evidence or a brand-new deeper review scope, not another obvious local
    drift fix.
  NEXT: keep this task as the tests-doc anchor and wait for user direction on
    whether to stop here or open another bounded docs lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:00:03Z
  TYPE: FACT
  CLAIM: Another local support-layer seam remains in the tests docs: the
    codegen/compiler helper surfaces are still under-described. Live tests
    repeatedly use `tests/_codegen_system_support.py`,
    `tests.component.melder.spellbook.compiler_test_helpers`, and
    `tests.component.melder.spellbook.spell_compiler_runtime_test_support`,
    but those helpers are still absent from the current shared-support story.
  EVIDENCE:
  - tests/_codegen_system_support.py
  - tests/component/melder/spellbook/compiler_test_helpers.py
  - tests/component/melder/spellbook/spell_compiler_runtime_test_support.py
  - validation_result: repeated imports across unit/component/integration tests
  IMPACT: The docs still understate the support layer for compiler/codegen test
    lanes even after the frame-posture and experimentation support pass.
  NEXT: patch the shared-support descriptions and source lists to include the
    codegen/compiler helper surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:02:40Z
  TYPE: FACT
  CLAIM: One more local consistency seam remains in the tests docs: the
    diagrams still lag the prose. The docs now describe frame-posture support,
    codegen/compiler helpers, and experimentation benches, but the current
    ASCII/Mermaid diagrams still only visualize viewer-matrix support plus the
    two Rift benches.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:280-317
  - codex/context_compass/system_docs/tests_components.md:548-588
  IMPACT: A re-entry reader scanning diagrams still gets an older narrower
    support-layer picture than the text now documents.
  NEXT: patch the tests architecture/components diagrams to include the newer
    support surfaces explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:04:18Z
  TYPE: MEASURE
  CLAIM: The diagram-fidelity patch is landed. The tests architecture and
    tests components diagrams now include frame-posture support,
    codegen/compiler helpers, and synthetic-module experiment benches, and the
    tests-components ASCII diagram now reflects that mocks feed both spellbook
    and crystallizer lanes.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:296-336
  - codex/context_compass/system_docs/tests_components.md:612-644
  IMPACT: The visual support-layer story now matches the prose. Within this
    checkout, the tests-doc lane is no longer leaving obvious local support
    surfaces out of either the text or the diagrams.
  NEXT: keep this task as the tests-doc anchor and wait for user direction if a
    new review axis is wanted beyond the external-CI boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:20:40Z
  TYPE: MEASURE
  CLAIM: The codegen/compiler support patch is landed. The tests architecture
    and tests components docs now include `_codegen_system_support.py`,
    `compiler_test_helpers.py`, and
    `spell_compiler_runtime_test_support.py` in their support-layer evidence,
    prose, and component mapping.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:74-84
  - codex/context_compass/system_docs/tests_architecture.md:108-117
  - codex/context_compass/system_docs/tests_architecture.md:320-330
  - codex/context_compass/system_docs/tests_components.md:123-173
  - codex/context_compass/system_docs/tests_components.md:435-446
  - codex/context_compass/system_docs/tests_components.md:624-636
  IMPACT: The local support-layer story now covers viewer, frame-posture,
    synthetic-module, and compiler/codegen helpers together instead of leaving
    compiler/codegen lanes implicit.
  NEXT: inspect whether the detailed tests-components map still under-describes
    the large spellbook compiler and legacy `spell_crafter` test clusters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:21:32Z
  TYPE: FACT
  CLAIM: The detailed tests-components map still under-describes the spellbook
    test surface. The live tree clearly splits into runtime/binding/config
    tests, current-surface `spell_compiler` tests, helper modules, and a still
    large legacy `spell_crafter` compatibility subtree, but the current C2 map
    still stops at the broad `tests/*/melder/spellbook/` directory level.
  EVIDENCE:
  - validation_result: directory inventory for `tests/unit/melder/spellbook`, `tests/component/melder/spellbook`, and `tests/integration/melder/spellbook`
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_system.py
  - tests/unit/melder/spellbook/spell_compiler/support/compiler_test_support.py
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py
  - tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system.py
  - tests/integration/melder/spellbook/test_spell_compiler_system_integration.py
  IMPACT: The tests docs still flatten one of the largest test subdomains even
    after the support-layer fixes, which makes spellbook/compiler coverage look
    less structured than it is.
  NEXT: add bounded spellbook runtime/compiler/legacy compatibility C2
    subcomponents and supporting evidence references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:22:41Z
  TYPE: MEASURE
  CLAIM: The spellbook cluster patch is landed too. `tests_components.md` now
    splits the broad spellbook bucket into explicit runtime/binding unit and
    component clusters, a dedicated spellbook compiler unit cluster, a
    spellbook compiler component cluster, and a spellbook integration cluster,
    with the retained legacy `spell_crafter` subtree called out as a
    compatibility surface instead of being left implicit.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:479-611
  IMPACT: The tests-components map now reflects the largest remaining local
    subdomain that was previously flattened into one broad spellbook bucket.
  NEXT: keep this task as the tests-doc anchor and wait for user direction if a
    new deeper review axis is wanted beyond the current local-evidence fixes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:55:39Z
  TYPE: FACT
  CLAIM: `tests_architecture.md` still carries an older narrower top-level test
    catalog even after the deeper tests-components fixes. Its C3 overview still
    frames the tiers mainly around `aether`, `spellbook`, and `utilities`, and
    its mock-corpus line still reads as spellbook-oriented, so the architecture
    doc now lags the more accurate tests-components map.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:219-227
  - codex/context_compass/system_docs/tests_architecture.md:237-241
  - codex/context_compass/system_docs/tests_components.md:181-188
  - codex/context_compass/system_docs/tests_components.md:332-340
  IMPACT: The tests architecture doc is now the narrower surface, not the
    components doc, so a re-entry reader still gets an outdated high-level test
    taxonomy there.
  NEXT: patch the tests-architecture C3/C2 overview bullets to align with the
    now-corrected tests-components picture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T18:58:10Z
  TYPE: MEASURE
  CLAIM: The shared-support purpose wording is now aligned in both tests docs.
    `tests_architecture.md` no longer frames that component as only
    descriptor/viewer/runtime fixtures, and `tests_components.md` now uses the
    same broader runtime-support framing that matches its responsibilities.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:233-234
  - codex/context_compass/system_docs/tests_components.md:121-124
  IMPACT: The support component’s one-line summary no longer lags its own
    detailed responsibilities, so quick scans and deeper reads now tell the
    same story.
  NEXT: keep the tests-doc task as the local-evidence anchor and wait for user
    direction if another review axis is wanted beyond the external-CI
    boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:06:38Z
  TYPE: FACT
  CLAIM: One bounded C1-map seam still remains in the tests docs: both
    `tests_architecture.md` and `tests_components.md` still list only
    `tests/mocks/spellbook/` in their key-path maps even though the mock corpus
    and information-source sections now explicitly include crystallizer harness
    files.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:296-304
  - codex/context_compass/system_docs/tests_components.md:676-684
  - codex/context_compass/system_docs/tests_components.md:748-750
  IMPACT: The detailed maps still under-represent the crystallizer mock support
    surface even after the broader mock-corpus prose was fixed.
  NEXT: patch the tests-doc C1 maps and the tests-architecture information
    sources to include the crystallizer mock harness surface explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:07:36Z
  TYPE: FACT
  CLAIM: `tests_architecture.md` still has an Aether-heavy C1 and evidence
    surface even after the tier taxonomy was widened. The doc now names
    crystallizer and mutation-research as real test subdomains, but its C1 key
    paths and `Information Sources` still lack representative files from those
    subdomains.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:289-305
  - codex/context_compass/system_docs/tests_architecture.md:342-369
  - tests/unit/melder/crystallizer/test_crystallizer.py
  - tests/component/melder/crystallizer/test_spell_crystal_component.py
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py
  - tests/unit/melder/mutation_research/test_mutation_research_root.py
  - tests/component/melder/mutation_research/test_mutation_research_root_component.py
  - tests/integration/melder/mutation_research/test_mutation_research_root_integration.py
  IMPACT: The architecture doc still cites a narrower evidence surface than the
    test system it now claims to summarize.
  NEXT: patch the tests-architecture C1 and information-source sections with
    representative crystallizer and mutation-research test paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:08:45Z
  TYPE: MEASURE
  CLAIM: The tests-architecture C1/evidence patch is landed too. The
    architecture doc now carries representative crystallizer and
    mutation-research test paths in both its key-path map and its information
    sources, so the architecture-level evidence surface now matches the wider
    tier taxonomy it already describes.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:296-310
  - codex/context_compass/system_docs/tests_architecture.md:365-379
  IMPACT: The tests architecture doc no longer summarizes a broader test system
    while citing only an Aether-heavy evidence slice.
  NEXT: keep this task as the tests-doc anchor and wait for user direction if a
    genuinely new local review axis is wanted beyond the external-CI boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:09:43Z
  TYPE: FACT
  CLAIM: `tests_architecture.md` still has one architecture-summary emphasis
    drift: it presents the dedicated Aether/Rift JSON benches as the single
    “most important recent integration addition,” but the local suite has also
    grown a broad support-layer and spellbook/compiler test surface that now
    deserves to be named in the same high-level summary.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:133-140
  - codex/context_compass/system_docs/tests_components.md:120-173
  - codex/context_compass/system_docs/tests_components.md:479-607
  IMPACT: The architecture doc still gives a too-narrow story of where the
    suite’s recent complexity and documentation weight actually moved.
  NEXT: patch the tests-architecture summary paragraph around the “most
    important recent integration addition” so it also names the wider
    spellbook/compiler support expansion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:10:50Z
  TYPE: MEASURE
  CLAIM: The tests-architecture summary patch is landed. The architecture doc
    now names both major recent growth areas in the live suite: the dedicated
    Aether/Rift JSON benches and the broader spellbook/compiler support
    expansion, including current-surface `spell_compiler` tests and retained
    legacy `spell_crafter` compatibility coverage.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:133-142
  IMPACT: The architecture summary no longer over-focuses on one integration
    harness lane while understating the broader support/compiler growth in the
    live test system.
  NEXT: keep this task as the tests-doc anchor and wait for user direction if a
    genuinely new review axis is wanted beyond the current local-evidence
    fixes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:17:31Z
  TYPE: FACT
  CLAIM: `tests_architecture.md` still has one deeper architecture-level map
    seam: its C2 overview remains Aether-centric and stops at broad
    `tests/*/melder/aether/*` plus Rift-bench bullets, while the components doc
    now proves explicit crystallizer, mutation-research, spellbook
    runtime/compiler, and crystallizer-mock subcomponents too.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:248-290
  - codex/context_compass/system_docs/tests_components.md:382-626
  IMPACT: The architecture doc still presents an older narrower subcomponent
    map than the deeper component doc and the live test tree now support.
  NEXT: patch the tests-architecture C2 overview bullets to reflect the newer
    crystallizer, mutation, spellbook, and mock subcomponent clusters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:18:46Z
  TYPE: MEASURE
  CLAIM: The tests-architecture C2 overview patch is landed. The architecture
    doc now lists explicit crystallizer, mutation-research, spellbook, and
    mock subcomponent clusters instead of stopping at the older Aether/Rift
    view.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:248-318
  IMPACT: The architecture-level subcomponent map now matches the broader
    components doc and live test tree much more closely.
  NEXT: inspect whether the tests-architecture C1 and evidence surface still
    under-represent the now-explicit spellbook/compiler subdomain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:19:27Z
  TYPE: FACT
  CLAIM: The tests-architecture C1 and evidence surface still under-represent
    the now-explicit spellbook/compiler subdomain. It carries spellbook helper
    files, but it still lacks representative spellbook runtime, component
    compiler, and integration compiler test paths even after the architecture
    overview and C2 map were widened.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:296-310
  - codex/context_compass/system_docs/tests_architecture.md:342-379
  - tests/unit/melder/spellbook/test_spellbook.py
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_system.py
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py
  - tests/integration/melder/spellbook/test_spell_compiler_system_integration.py
  IMPACT: The architecture doc now claims a broader spellbook/compiler story
    than its own key-path and evidence lists actually demonstrate.
  NEXT: patch the tests-architecture C1 and information-source sections with a
    small representative spellbook/compiler set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:20:15Z
  TYPE: MEASURE
  CLAIM: The tests-architecture spellbook/compiler evidence patch is landed
    too. The architecture doc now carries representative spellbook runtime and
    compiler test paths in both its key-path map and information sources, so
    the evidence surface matches the broader spellbook/compiler taxonomy it now
    describes.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:341-344
  - codex/context_compass/system_docs/tests_architecture.md:414-417
  IMPACT: The architecture doc no longer widens its spellbook/compiler story
    without also citing representative local evidence for that subdomain.
  NEXT: keep this task as the tests-doc anchor and wait for user direction if a
    genuinely new review axis is wanted beyond the current local-evidence
    fixes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:28:49Z
  TYPE: FACT
  CLAIM: `tests_architecture.md` still under-cites the retained legacy
    `spell_crafter` compatibility subtree. The architecture summary now names
    that legacy surface, but the architecture-level C1 and evidence lists still
    lack any representative legacy `spell_crafter` test paths.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:141-145
  - codex/context_compass/system_docs/tests_architecture.md:296-310
  - codex/context_compass/system_docs/tests_architecture.md:342-379
  - tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  - tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system.py
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py
  IMPACT: The architecture doc still names the legacy compatibility surface in
    prose without citing any representative local evidence for it.
  NEXT: patch the tests-architecture C1 and information-source sections with a
    minimal representative legacy `spell_crafter` trio.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:29:53Z
  TYPE: FACT
  CLAIM: `tests_components.md` still has a local C1-map imbalance. The doc now
    spells out large spellbook runtime/compiler clusters, but its C1 key-path
    list is still almost entirely Aether/support/mock oriented and does not yet
    cite any representative spellbook runtime, current-surface compiler, or
    legacy `spell_crafter` compatibility test files.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:664-683
  - codex/context_compass/system_docs/tests_components.md:479-608
  - tests/unit/melder/spellbook/test_spellbook.py
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_system.py
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py
  - tests/integration/melder/spellbook/test_spell_compiler_system_integration.py
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py
  IMPACT: The components doc currently describes a broad spellbook/compiler test
    surface without giving the C1 map the same representative coverage.
  NEXT: patch the tests-components C1 map with a minimal representative
    spellbook/compiler set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:30:41Z
  TYPE: FACT
  CLAIM: `tests_components.md` still has one local traceability seam after the
    C1 patch: its `Information Sources` list still omits the representative
    spellbook/runtime/compiler files that the document now uses to justify the
    broader spellbook clusters and legacy compatibility coverage.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:725-751
  - codex/context_compass/system_docs/tests_components.md:479-608
  IMPACT: The component map is now broader than its own cited evidence set.
  NEXT: patch the `tests_components.md` information-source list with a minimal
    representative spellbook/compiler set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:31:53Z
  TYPE: FACT
  CLAIM: One last local consistency seam remains in the tests docs: the
    diagrams still collapse the tier work into generic `unit/component/
    integration` boxes even though the prose and C2 map now explicitly split
    crystallizer, mutation-research, and spellbook/compiler clusters.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_architecture.md:367-397
  - codex/context_compass/system_docs/tests_components.md:696-728
  - codex/context_compass/system_docs/tests_components.md:460-607
  IMPACT: A re-entry reader scanning only the diagrams still gets a flatter
    taxonomy than the surrounding docs now describe.
  NEXT: patch the tests diagrams to annotate the tier boxes with the broader
    cluster mix already documented in prose.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:33:35Z
  TYPE: MEASURE
  CLAIM: The final local consistency sweep is clean. `tests_architecture.md`
    and `tests_components.md` both have `MISSING_COUNT 0` for referenced local
    paths, and the only remaining `UNKNOWN` entries are the explicit
    external-CI placeholders that are already marked blocked on external
    evidence.
  EVIDENCE:
  - validation_result: `tests_architecture.md MISSING_COUNT 0`
  - validation_result: `tests_components.md MISSING_COUNT 0`
  - codex/context_compass/system_docs/tests_architecture.md:47-53
  - codex/context_compass/system_docs/tests_components.md:33-40
  IMPACT: The local-evidence tests-doc lane is now genuinely exhausted. Any
    further work would require external CI evidence or a brand-new review axis,
    not another local drift fix.
  NEXT: keep this task as the durable tests-doc anchor and wait for user
    direction on whether to stop or open a different docs lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:37:43Z
  TYPE: FACT
  CLAIM: The detailed integration map is still incomplete. `tests_components.md`
    now has explicit integration clusters for Aether, crystallizer,
    mutation-research, and spellbook, but it still omits the live `conduit`,
    `live_sim`, and `multithreading` integration directories even though those
    directories contain real test suites in this checkout.
  EVIDENCE:
  - validation_result: directory inventory for `tests/integration/melder/conduit`
  - validation_result: directory inventory for `tests/integration/melder/live_sim`
  - validation_result: directory inventory for `tests/integration/melder/multithreading`
  - codex/context_compass/system_docs/tests_components.md:574-607
  IMPACT: The integration-tier taxonomy is still uneven: some integration
    subdomains are explicit while others remain flattened into a broad tier
    label.
  NEXT: read representative conduit/live_sim/multithreading integration files
    and add bounded C2 subcomponents for those clusters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:38:47Z
  TYPE: FACT
  CLAIM: The missing integration clusters are real and bounded. The live
    `conduit` integration suite centers on public API, lifecycle, existence,
    contracts, spellspace, and concurrency behavior; `live_sim` centers on a
    mini-application bootstrap and dynamic/automatic runtime flows; and
    `multithreading` centers on contracted resolution and spell-system-state
    behavior under threaded access.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_public_api.py
  - tests/integration/melder/live_sim/test_live_sim_dynamic.py
  - tests/integration/melder/multithreading/test_multithreading_spell_system_states.py
  IMPACT: The integration-tier C2 map can now add those clusters with
    evidence-backed purpose statements instead of leaving them flattened into a
    generic integration bucket.
  NEXT: patch `tests_components.md` with conduit/live_sim/multithreading
    integration subcomponents and key files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:39:41Z
  TYPE: MEASURE
  CLAIM: The missing integration-cluster patch is landed too.
    `tests_components.md` now has explicit integration subcomponents for
    conduit, live_sim, and multithreading alongside the already-landed Aether,
    crystallizer, mutation-research, and spellbook integration clusters.
  EVIDENCE:
  - codex/context_compass/system_docs/tests_components.md:579-629
  IMPACT: The integration-tier map is now balanced across the real
    integration subdomains present in this checkout instead of favoring only a
    subset of them.
  NEXT: run one final local seam scan and stop widening this lane unless a real
    new in-checkout drift seam still remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:41:02Z
  TYPE: DECISION
  CLAIM: By explicit user direction to keep continuing after the local
    tests-doc seams were exhausted, the next bounded docs lane should move to
    the example architecture/components/graph documents rather than inventing
    churn inside the now-clean live tests docs.
  EVIDENCE:
  - user_instruction: `continue`
  - local state: tests-doc lane reduced to external-CI-only unknown
  IMPACT: The tests-doc task remains the durable anchor for local tests-doc
    cleanup, while the next active docs task should target the example docs as
    template/reference surfaces.
  NEXT: create and route a new example-doc drift task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task continues the documentation program after the source-system graph
lane converged. It is intentionally bounded to the tests docs and their live
test-tree evidence.
