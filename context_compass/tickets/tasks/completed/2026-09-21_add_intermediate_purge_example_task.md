# Task: Teach early object disposal with an intermediate purge lesson

- Completed: 2026-09-21T00:59:08Z
- Summary: Added intermediate purge lesson 39, curriculum/catalog links, verified downloads and refreshed assets.

## Metadata
- Task ID: TASK-2026-09-21-add-intermediate-purge-example
- Story: none
- Status: done
- Owner: codex
- Agent Name: workflows_0
- Priority: p2
- Created: 2026-09-21T00:34:45Z
- Updated: 2026-09-21T00:59:08Z

## Objective
Add a runnable intermediate Read the Docs lesson for the new purge API, grounded in the release
notes and current implementation, with normal curriculum links and downloadable source.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requests the lesson; role and example-directory instructions are read.
- EXECUTION_BOUNDARY: New intermediate lesson, collection/catalog metadata, curriculum links and
  related authored guide text; generated local docs and bounded validation evidence.
- DEPENDENCIES: Current purge contract, existing example harness, catalog and documentation builder.
- EXIT_GATE: Lesson demonstrates early disposal correctly, remains md.*-only, appears in the
  intermediate curriculum/downloads, and relevant example/documentation checks pass.
- FAILURE_ESCALATION: Record runtime or build defects separately; preserve concurrent runtime and
  canonical system-document edits by updater_0 and muse.

## Scope Boundaries
- In scope: A practical saved example, public-facing lesson explanations and catalog integration.
- Out of scope: Runtime/API changes, new dependencies, hosted deployment, commits or publication.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Requested lesson and publication inputs are complete; all scoped acceptance checks pass.

## Steps / Checklist
- [x] Read release notes, example instructions and documentation-maintenance guidance.
- [x] Trace current purge contracts and inspect neighboring lesson/build/harness patterns.
- [x] Implement the lesson and its curriculum/catalog links.
- [x] Execute the lesson and relevant existing documentation/example checks.
- [x] Inspect generated page/downloads and record final delivery evidence.

## Deliverables
- New runnable intermediate purge lesson using import melder as md.
- Catalog registration and contextual intermediate guide links.
- Validation evidence with any limitations stated explicitly.

## Validation
- Standalone purge assertions pass; all 38 intermediate harness examples and 39 documentation tests pass.
- Strict HTML build passes for 295 pages; site checker verifies 35,679 local links and source fidelity.
- New page, catalog/curriculum routes, stable downloads and both collection ZIP copies are verified.
- Scoped correctness lint and whitespace checks pass. Source assets are current; the other corpus
  was regenerated and final src/tests/other freshness checks pass.
- One non-fatal pytest cache-write warning is recorded. No hosted deployment or full runtime suite was run.

## Risks / Rollback Notes
- purge defaults to removing all retained entries for the selected spell; single removal needs an instance.
- many creations require configured disposal to be retained; application references remain ordinary Python refs.
- Other agents are updating purge assets and source documentation concurrently; use targeted edits.

## Applicable Anti-Patterns
- [x] No runtime behavior inferred solely from release prose or symbol names.
- [x] No deep melder imports, hidden substrate teaching, or reference-based meld teaching calls.
- [x] No hand-edited generated pages or claimed hosted publication.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/intermediate_purge_20260921/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain concise lesson/build evidence; transient build files are disposable at accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record source contract findings and validation outcomes before the next work tranche.

## Notes
- DATETIME: 2026-09-21T00:34:45Z
  TYPE: FACT
  CLAIM: The next-version release draft introduces Conduit.purge and SpellSpace.purge, with
    default all-retained removal and instance-only purge_all=False. Intermediate has 37 saved
    lessons. The site consumes an explicit catalog and reciprocal curriculum links; examples
    must use md.* public names and quoted names for human-facing meld calls.
  EVIDENCE:
  - release_docs/next_version_release.md:5-88
  - UX_and_AIX_experiences/AGENTS.md:1-44
  - docs/maintaining.md:52-70
  - docs/catalog.toml:53-95
  IMPACT: Add lesson 38 with source-verified assertions and normal catalog/curriculum integration.
  NEXT: Trace purge's implementation and read the neighboring lifecycle lessons and publication tools.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:46:32Z
  TYPE: DECISION
  CLAIM: The intermediate concept map records lesson 38 as explicitly withdrawn. Preserve that
    historical number and add the purge lesson as 39 instead. Existing lessons use disposal callbacks
    and public md.* surfaces; the harness discovers numbered scripts. The retained docs-env provides
    Sphinx 9.1.0 on Python 3.14.7 free-threading, so no owner environment changes are needed.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/_concept_map.txt:143-166
  - UX_and_AIX_experiences/02_intermediate/30_config_disposal_and_the_frozen_law.py:21-58
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_examples.py:15-17
  IMPACT: Use 39_purge_unneeded_objects.py and the existing isolated docs interpreter. Runtime
    assertions still require source tracing; release-note intent alone is not implementation evidence.
  NEXT: Verify system-document indexes and read the purge call path plus remaining publication inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:46:32Z
  TYPE: FACT
  CLAIM: Current source forwards instance/name selectors from the public facades through shared
    discovery and concrete scope policy. Single-many retirement compares identity, removes paired
    disposal metadata and preserves siblings; full purge removes the selected bucket and returns
    its count. SpellSpace always uses its local store. Conduit's context manager holds a lock;
    it does not clean the conduit, so the lesson must call cleanup explicitly in finally.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4121-4204
  - src/melder/aether/conduit/conduit.py:1432-1488
  - src/melder/aether/conduit/meld/conduit_meld.py:143-258
  - src/melder/aether/conduit/meld/spellspace_meld.py:168-234
  - src/melder/aether/conduit/creations/creations.py:429-632
  IMPACT: A retained many-buffer lesson can prove single removal, default all removal, zero after
    retirement, continued melding, local spell-space isolation and no repeat disposal at teardown.
  NEXT: Add lesson 39, its catalog/curriculum links and concise guide/concept-map references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:48:46Z
  TYPE: MEASURE
  CLAIM: Added lesson 39 and catalog, curriculum, scope-guide, level-index and concept-map links.
    Standalone execution on Python 3.14.7 free-threading passed: one object removed, two remaining
    objects removed by name, remelding succeeds, spell-space isolation holds, and all six buffers
    receive exactly one disposal call across purge and final cleanup.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/39_purge_unneeded_objects.py:1-116
  - context_compass/artifacts/intermediate_purge_20260921/lesson.log:1-5
  IMPACT: The requested teaching behavior is executable. Validate discovery in the shared harness
    and the generated site's links/downloads before delivery; no hosted publication is implied.
  NEXT: Run the existing intermediate harness and documentation input/tests, then build the site.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:50:15Z
  TYPE: MEASURE
  CLAIM: All 38 intermediate examples pass in the shared harness (0.97s), including the new
    purge lesson. Pytest reported one non-fatal sandbox warning while writing its optional cache.
    All 39 documentation tests pass, and navigation/input validation accepts 295 pages and 54
    assets. The existing docs environment is sufficient; no dependency installation was needed.
  EVIDENCE:
  - context_compass/artifacts/intermediate_purge_20260921/intermediate.log:1-8
  - context_compass/artifacts/intermediate_purge_20260921/docs-tests.log:1-6
  - context_compass/artifacts/intermediate_purge_20260921/docs-check.log:1-1
  IMPACT: Runtime lesson discovery and document assembly are validated. Strict rendering and
    output/source fidelity still need verification; prior runtime/coverage results are not rerun here.
  NEXT: Build strict HTML, inspect the lesson/downloads, and check relevant derived assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:52:01Z
  TYPE: FACT
  CLAIM: Scoped correctness Ruff and source-asset checks pass. The repository builder reports src
    and tests current and only the other corpus stale after the documentation/example edits.
    Its default discovery is tracked-file based; register only the new lesson with intent-to-add,
    then rebuild/check only other. This does not stage lesson content or create a commit.
  EVIDENCE:
  - context_compass/artifacts/intermediate_purge_20260921/source-assets-check.log:1-3
  - context_compass/artifacts/intermediate_purge_20260921/corpora-check.log:1-6
  - docs/maintaining.md:150-158
  IMPACT: Refresh the changed derived documentation bundle without rewriting unrelated source/test corpora.
  NEXT: Register the lesson for discovery and regenerate the other corpus while strict HTML finishes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-21T00:59:08Z
  TYPE: MEASURE
  CLAIM: Final delivery checks pass. Strict HTML emits 295 pages and the site checker validates
    35,679 links with matching sources. Targeted audit proves the new lesson is intermediate 39,
    reciprocally linked to scopes, included in full contents/catalog, and byte-identical in the
    generated script downloads and collection ZIPs. Catalog totals are 38 intermediate/134 overall.
    Only the other corpus required rebuilding (360 inputs); final checks pass for all three corpora.
  EVIDENCE:
  - context_compass/artifacts/intermediate_purge_20260921/publication-audit.json:1-9
  - context_compass/artifacts/intermediate_purge_20260921/html-build.log:1-1
  - context_compass/artifacts/intermediate_purge_20260921/site-check.log:1-1
  - context_compass/artifacts/intermediate_purge_20260921/all-corpora-final-check.log:1-3
  IMPACT: The requested intermediate lesson is complete and ready for the repository's normal
    publication flow. Existing tests provide runtime and documentation evidence; no hosted claim is made.
  NEXT: none for implementation; owner can include these local changes in the normal commit/publish flow.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed intermediate lesson 39, Purge unneeded objects, using only the public md.* API and quoted
meld names. It proves single/all purge, counts, remelding, scope isolation and final disposal.
Catalog, curriculum, scopes guide, level summary and concept map are linked; withdrawn lesson 38
is preserved. All 38 intermediate examples, 39 docs tests, strict HTML, links/downloads and asset
freshness checks pass. The new lesson is intent-to-add only; no content is staged and no commit or
hosted publication occurred. NEXT: none for this completed example delivery.
