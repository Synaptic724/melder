# Task: Name Melder's cache bundles `.meldercache` instead of `.melc`

## Metadata
- Task ID: TASK-2026-10-04-rename_cache_suffix_to_meldercache
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p2
- Created: 2026-10-04T13:11:56Z
- Updated: 2026-10-04T13:26:39Z

## Objective
Rename the cache bundle extension from `.melc` to `.meldercache` so a file under `__melder_cache__`
plainly reads as a Melder cache: the per-conduit creation caches and the build-asset caches.

## Ticket Contract
- ENTRY_GATE: The owner's chat request of 2026-10-04 ("rename the cache name we have from melc to
  .meldercache"). Active board row: meldercache_suffix. Patch docs under
  system_docs/patches/active/meldercache_suffix_2026_10_04/.
- EXECUTION_BOUNDARY: the two suffix constants and the present-tense `.melc` wording in src/; the
  tests and experimentation scripts that name the suffix; .gitignore; the CI forbidden-suffix list and
  its test; the pyproject comment; src_architecture, src_components and tests_architecture with
  their indexes; the version notch and the running release note; regenerated assets, graph and
  bundles. Historical mentions of `.melc` stay as written. No commit, push or PR.
- DEPENDENCIES: none. Other lanes rebuild the generated assets and bundles, so the rebuild runs last.
- EXIT_GATE: no code path writes or reads `.melc`; tests run or are reported Not run; asset, graph,
  index and bundle checks pass; the owner accepts.
- FAILURE_ESCALATION: Record BLOCKER if a check cannot pass or the shared tree is mid-change when
  the assets are rebuilt.

## Scope Boundaries
- In scope: the rename above, with old `.melc` files left alone (never read, never deleted).
- Out of scope: cache envelope format or generation changes; deleting user cache files; the
  ContextCompass package tooling (its graph extractor lists `.melc` as documentation only); renaming
  the experimentation ledger script or its MELC_NS_* variables.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-04T13:26:39Z) implemented, validated and rebuilt (Notes 4-6); owner acceptance
  remains.
- previous: draft -> in_progress on the owner's chat request (Notes 1-3).

## Steps / Checklist
- [x] Inventory every `.melc` reference (Note 1).
- [x] Rename the two suffix constants and the present-tense wording in src/.
- [x] Update tests and experimentation scripts; add a regression test that a legacy `.melc` bundle
      is never read.
- [x] Update .gitignore (keep `*.melc` as a legacy ignore), the CI forbidden suffixes and their test,
      and the pyproject comment.
- [x] Update the three system docs and their indexes; promote the patch.
- [x] Notch 0.2.8223 and add the release-note entry; post the notch notice.
- [x] Validate and report only what actually ran.
- [x] Rebuild assets, graph and llm_support bundles last, then run every --check.

## Deliverables
- `.meldercache` bundles for conduit creation caches and build-asset caches; updated tests,
  ignore rules, CI list, docs, release note and version; regenerated assets, graph and bundles.

## Files / Paths Impacted
- src/melder/utilities/caching_system/caching_system.py
- src/melder/utilities/caching_system/asset_cache.py
- src/melder/_build_assets/ (loader and builder docstrings; generated manifests and payloads)
- src/melder/aether/spellbook/spell_compiler/ (two docstrings)
- tests/ (unit, component, integration, experimentation files that name the suffix)
- .gitignore, .github/scripts/verify_distributions.py, pyproject.toml
- context_compass/system_docs/ (three docs, their indexes, the graph)
- src/melder/__version__.py, release_docs/next_version_release.md, llm_support/

## Validation
- 2026-10-04, device VM, uv CPython 3.14.7 free-threaded, pytest 9.1.1 (Notes 5-6):
  - Cache unit, component and integration files: 118 passed, 1 skipped (scratch copy).
  - tests/unit without llm_support and github_workflows: 8391 passed; the 21 failures were copy
    artifacts or the pre-rebuild stamp, and those files pass in the repo (165 passed, 1 skipped).
  - tests/unit/github_workflows: passed in the repo.
  - _build_asset_runner.py --check: OK x3; index checks: OK x4; llm_support --check: OK x3.
- Not run: the owner's Windows tiers; the full component and integration tiers.

## Risks / Rollback Notes
- Risk: an untracked tool still globs `*.melc`. Mitigation: the inventory covers tracked and
  untracked files; old files stay readable by hand.
- Rollback: restore the two constants and revert the text edits; caches regenerate either way.

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
  - system_docs/patches/active/meldercache_suffix_2026_10_04/architecture_patch.md
  - system_docs/patches/active/meldercache_suffix_2026_10_04/component_patch_caching_system.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: on closure, move the patch folder to system_docs/patches/completed/

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
- DATETIME: 2026-10-04T13:11:56Z
  TYPE: FACT
  CLAIM: Two constants own the suffix and every bundle path is built from them: the conduit cache
    derives `<cache_root>/<frame>/<conduit>` + BUNDLE_SUFFIX (temp file: suffix + `.tmp`), and the
    asset cache derives `__melder_cache__/__<asset>__/<asset>` + its BUNDLE_SUFFIX. Every other
    `.melc` mention is wording (docstrings, comments), test paths, .gitignore, the CI forbidden list,
    a pyproject comment or the system docs; history in completed tickets and artifacts is not edited.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:218-218
  - src/melder/utilities/caching_system/caching_system.py:268-272
  - src/melder/utilities/caching_system/caching_system.py:885-891
  - src/melder/utilities/caching_system/asset_cache.py:118-118
  - src/melder/utilities/caching_system/asset_cache.py:127-147
  - .gitignore:206-206
  - .github/scripts/verify_distributions.py:36-38
  IMPACT: Changing the two constants renames every bundle; the rest is wording, tests and ignore
    rules that must follow so nothing is committed or shipped under the new name.
  NEXT: Record the defaults.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T13:11:56Z
  TYPE: DECISION
  CLAIM: The owner's request is the confirmation. Defaults: both caches use `.meldercache`; old
    `.melc` files are neither read nor deleted (a missing bundle is a cold cache, and the 0.2.8223
    notch already makes every older bundle cold by its release stamp), so no generation bump;
    .gitignore keeps `*.melc` as a legacy ignore and the CI list forbids both suffixes; historical
    comments keep `.melc`; the ContextCompass graph tool is out of scope.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:747-750
  - src/melder/utilities/caching_system/caching_system.py:801-810
  - context_compass/tools/system_documents/python/extract_graph.py:74-76
  IMPACT: The first run after upgrading compiles cold once and writes `.meldercache`; leftover
    `.melc` files are inert and can be deleted by hand.
  NEXT: Record the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T13:11:56Z
  TYPE: PLAN
  CLAIM: Patch mapping: architecture_patch (suffix invariant, migration order) -> constants and wording
    in src/ -> unit/component tests on the new names plus a legacy-bundle regression; component_patch
    (before/after paths, ignore and CI rules) -> tests, .gitignore, CI list, pyproject -> the
    github_workflows suite. Then the docs and indexes, the notch and release note, targeted test runs,
    and last the asset runner, graph, indexes and llm_support with every --check.
  EVIDENCE:
  - context_compass/system_docs/patches/active/meldercache_suffix_2026_10_04/architecture_patch.md:1-33
  - context_compass/system_docs/patches/active/meldercache_suffix_2026_10_04/component_patch_caching_system.md:1-22
  IMPACT: One scripted pass with exact-count replacements keeps the diff small and reviewable.
  NEXT: Apply the source, test, rule and doc edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T13:15:32Z
  TYPE: FACT
  CLAIM: The rename is applied: both BUNDLE_SUFFIX constants are `.meldercache`; present-tense wording in
    src/ follows (historical `.melc` comments kept); tests and experimentation scripts use the new name,
    with a unit regression that a current-format `.melc` bundle is never read; .gitignore ignores both
    names; the distribution check forbids both; three system docs carry the name with handoff entries;
    version 0.2.8223 with its release-note section and board notch notice.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:218-218
  - src/melder/utilities/caching_system/asset_cache.py:118-118
  - tests/unit/melder/utilities/test_caching_system.py:467-492
  - .gitignore:206-209
  - .github/scripts/verify_distributions.py:36-38
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:460-468
  IMPACT: No code path names `.melc` any more; the next run writes `.meldercache` bundles.
  NEXT: Run the cache, build-asset and workflow tests on the device VM.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T13:19:46Z
  TYPE: MEASURE
  CLAIM: Device VM, uv CPython 3.14.7 free-threaded, pytest 9.1.1. In the repo: test_caching_system,
    test_build_asset_runner, test_cache_schema_version_integration and tests/unit/github_workflows gave
    557 passed and 12 failed; all 12 failed only in shutil.rmtree of pre-existing repo-local temp dirs,
    which this VM may not delete. From a scratch cwd test_caching_system gave 37 passed (the legacy
    regression included). In a scratch copy of src/ and tests/: the cache unit, component and
    integration files gave 118 passed, 1 skipped, writing only `.meldercache` bundles (conduit, bind
    guard, agent documentation); tests/unit without llm_support and github_workflows gave 8391 passed,
    21 failed: 18 need architecture_and_design/ and 2 need context_compass/system_docs/ (both absent
    from the copy), and 1 is the asset version stamp that the rebuild settles.
  EVIDENCE:
  - tests/unit/melder/utilities/test_caching_system.py:467-492
  - src/melder/utilities/caching_system/caching_system.py:268-272
  IMPACT: No failure traces to the rename; the asset stamp and the two system-document tests are
    re-run after the rebuild.
  NEXT: Rebuild the graph and the three indexes, then the build assets with --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T13:26:39Z
  TYPE: MEASURE
  CLAIM: Rebuilds and checks, device VM, CPython 3.14.7t: extract_graph --strict wrote 586 descriptors
    (0 skipped, 0 orphaned) and assemble_graph verified all 586 ranges; the three edited docs were
    re-indexed and all four index checks print OK. The in-place asset runner wrote two manifests, then
    stopped because this VM may not delete the payload files it replaces; it was re-run in a scratch
    copy of src/ and the system docs, the five changed outputs (same file set) were copied back, and
    _build_asset_runner.py --check in the repo prints only OK (v0.2.8223). In the repo the version,
    build-asset, architecture-docs and llm_support tests gave 165 passed, 1 skipped. llm_support was
    rebuilt (src 578, tests 1060, other 386 files) and --check --include-untracked prints only OK.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/system_docs/src_architecture_index.md:9-20
  IMPACT: Every gate this agent owns is met. Not run: the owner's Windows tiers and the full component
    and integration tiers.
  NEXT: The owner accepts or redirects; on acceptance, archive the patch folder and close the ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (Notes 4-6): both caches write `.meldercache`, nothing reads or deletes `.melc`, tests, ignore rules,
CI list, docs, version 0.2.8223 and the release note follow, and the assets, graph, indexes and bundles
are current. Owner-owed: acceptance (then archive the patch folder and close) and the Windows tiers.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
