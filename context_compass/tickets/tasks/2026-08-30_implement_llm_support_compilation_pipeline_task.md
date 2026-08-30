# Task: Implement the LLM support compilation pipeline

## Metadata
- Task ID: TASK-2026-08-30-implement-llm-support-compilation-pipeline
- Story: STORY-2026-08-30-llm-support-compilation-pipeline
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T22:07:25Z
- Updated: 2026-08-30T22:32:04Z

## Objective
Implement, generate, and validate the accepted three-corpus LLM support system
and its source/repository asset workflows.

## Ticket Contract
- ENTRY_GATE: Owner accepted the discovery design, check-only CI, and workflow rename.
- EXECUTION_BOUNDARY:
  `llm_support/`, `tests/unit/llm_support/`, `.gitattributes`,
  `.github/workflows/build-assets.yml` rename, and
  `.github/workflows/build-repo-assets.yml`.
- DEPENDENCIES: Discovery artifact, tracked corpus census, existing build-assets workflow.
- EXIT_GATE: Generated outputs/check mode/tests/workflows/EOL/diff gates pass.
- FAILURE_ESCALATION: Stop on data loss, unsupported encoding, count mismatch,
  nondeterminism, unexpected corpus inclusion, or workflow write permission.

## Scope Boundaries
- In scope:
  - stdlib builder, README, manifest, three bundles, three indexes
  - deterministic contract tests and repository validation
  - build-src-assets workflow rename
  - generic build-repo-assets check workflow
  - LF policy for llm_support
- Out of scope:
  - runtime/package behavior
  - auto-commit or pre-commit installation
  - changing accepted corpus membership without owner approval

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Builder, README, manifest, six generated files, tests,
  workflow rename/addition, and terminal validation all pass.

## Steps / Checklist
- [x] Implement pure classification/decoding/fingerprint/render/index/manifest helpers.
- [x] Implement atomic selective build, check, list, corpus, and slice CLI.
- [x] Add contract-dense unit tests.
- [x] Write the ContextCompass-first README.
- [x] Generate and inspect all committed outputs.
- [x] Rename and update build-src-assets workflow.
- [x] Add build-repo-assets workflow.
- [x] Validate deterministic no-op rebuild, stale/tamper refusal, workflows, and EOL/diff hygiene.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding before continuing.

## Deliverables
- Complete accepted llm_support tree and repository workflows.

## Files / Paths Impacted
- `llm_support/_builder.py`
- `llm_support/README.md`
- `llm_support/manifest.json`
- `llm_support/llm_full_src.txt`
- `llm_support/llm_full_src_index.md`
- `llm_support/llm_full_tests.txt`
- `llm_support/llm_full_tests_index.md`
- `llm_support/llm_full_other.txt`
- `llm_support/llm_full_other_index.md`
- `tests/unit/llm_support/test_builder.py`
- `.github/workflows/build-src-assets.yml`
- `.github/workflows/build-repo-assets.yml`
- `.gitattributes`
- ContextCompass tracking/artifact rows.

## Validation
- Builder contract suite: pass (28 tests).
- Workflow YAML parse and semantic assertions: pass (2 workflows).
- Repository asset check: pass (src, tests, other).
- Second build: all outputs unchanged; zero mtime changes.
- Corpus counts: src 584, tests 794, other 262.
- ContextCompass paths in other: zero.
- Existing source build-asset check: all three current.
- Generated EOL: LF-only; diff hygiene passes.

## Risks / Rollback Notes
- Roll back the builder, generated tree, test, LF rule, and workflow changes atomically.
- Do not retain outputs without their matching manifest/indexes.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [x] Applicable anti-pattern checks are clear or escalated.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: story acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - builder implementation and generated outputs
  - source/repository asset workflow separation
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical implementation evidence, validation, and next single step.

## Notes
- DATETIME: 2026-08-30T22:32:04Z
  TYPE: MEASURE
  CLAIM: Terminal validation passes. Builder suite is 28/28; both workflows
    parse; all three LLM corpora pass check mode and a second build rewrites
    nothing with zero mtime changes; source build assets remain current; other
    contains zero ContextCompass paths; all generated files are LF-only; and
    EOL-aware diff hygiene exits zero.
  EVIDENCE:
  - `tests/unit/llm_support/test_builder.py`
  - `llm_support/manifest.json`
  - `.github/workflows/build-src-assets.yml`
  - `.github/workflows/build-repo-assets.yml`
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  IMPACT: Builder, committed outputs, indexes, manifest, workflow separation,
    portability, and selective regeneration meet the accepted contract.
  NEXT: Move the implementation story/task and attention route to review; wait
    for owner acceptance before closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:30:41Z
  TYPE: MEASURE
  CLAIM: Final focused suite passes 28 tests, including workflow separation/
    names/gates/read-only permission/v7 actions/check commands. Both renamed
    and new GitHub workflow files parse successfully as YAML.
  EVIDENCE:
  - `tests/unit/llm_support/test_builder.py`
  - `.github/workflows/build-src-assets.yml`
  - `.github/workflows/build-repo-assets.yml`
  IMPACT: Builder and workflow contracts are green before final regeneration.
  NEXT: Regenerate stale tests/other corpora, prove check/no-op/slice/current
    counts, run source build-asset gate, and finish EOL/diff validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:28:49Z
  TYPE: BLOCKER
  CLAIM: Post-rename bootstrap discovery correctly sees the cached old
    `.github/workflows/build-assets.yml` path as missing before the rename is
    staged. Strict tracked-only mode should keep failing there, but explicit
    `--include-untracked` already models the working tree and must treat
    missing cached paths as unstaged deletions.
  EVIDENCE:
  - `llm_support/_builder.py:320-350`
  - `.github/workflows/build-src-assets.yml`
  IMPACT: Initial generation cannot include the accepted workflow rename until
    bootstrap mode handles this one working-tree state.
  NEXT: Skip missing cached paths only when include-untracked is explicit,
    report them as working_tree_deleted, test the behavior, and regenerate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T22:28:30Z
  TYPE: FACT
  CLAIM: Workflow separation is implemented. The existing file and all
    identifiers are renamed to `build-src-assets` with
    `BUILD_SRC_ASSETS_GATE`; the new generic `build-repo-assets` workflow
    runs on push/PR/manual, grants contents-read only, lists inputs, and checks
    LLM repository assets without write-back. Both use the repository-standard
    v7 checkout/setup actions.
  EVIDENCE:
  - `.github/workflows/build-src-assets.yml`
  - `.github/workflows/build-repo-assets.yml`
  - `.github/workflows/python-publish.yml:20-112`
  IMPACT: Package-internal and repository-wide generated truth now have
    separately named, maintainable gates.
  NEXT: Validate YAML structure/semantics, then run final builder tests,
    generation/check/no-op/EOL/diff gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:27:01Z
  TYPE: MEASURE
  CLAIM: Final-policy generation is current and idempotent. Check passes all
    three corpora; a second build reports all bundles/indexes and manifest
    unchanged with zero mtime changes; indexed slice returns the exact
    `src/melder/__version__.py` content. Generated sizes are 10.76 MB source,
    10.57 MB tests, and 2.26 MB other, plus compact 115/153/46 KB indexes.
  EVIDENCE:
  - `llm_support/manifest.json`
  - `llm_support/llm_full_src_index.md`
  - `llm_support/llm_full_tests_index.md`
  - `llm_support/llm_full_other_index.md`
  IMPACT: Selective generation, output proofs, no-op writes, and consumption
    operate correctly on the real repository.
  NEXT: Rename/configure build-src-assets and add the generic check-only
    build-repo-assets workflow, then validate workflow semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:26:25Z
  TYPE: MEASURE
  CLAIM: Owner-approved whole-ContextCompass exclusion passes all 27 focused
    tests. Final live corpus census is source 584/270,707 lines, tests 794/
    298,882 lines, and other 261/55,514 lines; 2,621 ContextCompass paths are
    routed to the single `context_compass_direct` exclusion.
  EVIDENCE:
  - `llm_support/_builder.py:1-890`
  - `tests/unit/llm_support/test_builder.py`
  - `llm_support/README.md`
  IMPACT: The feedback loop is eliminated and generated content has one stable,
    user-approved membership contract.
  NEXT: Regenerate all corpora under the final policy, then prove check/no-op/
    slice/output metadata before workflow authoring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:25:00Z
  TYPE: MEASURE
  CLAIM: Whole-ContextCompass exclusion recalculates `other` to 261 files/
    2.11 MB/55,514 lines and excludes 2,621 ContextCompass paths. Twenty-six
    tests pass; one classification case retains the superseded narrower
    placeholder reason for a ContextCompass `.gitkeep`.
  EVIDENCE:
  - `llm_support/_builder.py:20-115`
  - `tests/unit/llm_support/test_builder.py:45-110`
  IMPACT: Runtime policy is correct; one test expectation must reflect that the
    owner-approved ContextCompass exclusion has precedence over nested reasons.
  NEXT: Update that expected reason, rerun all 27 focused tests, and revise the
    discovery artifact's corpus contract/counts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T22:24:11Z
  TYPE: DECISION
  CLAIM: Owner authorized sidestepping ContextCompass for LLM bundle content.
    Exclude the entire `context_compass/` tree from `llm_full_other`; keep
    the authored llm_support README directing capable agents to ContextCompass
    directly.
  EVIDENCE:
  - Owner direction in the active conversation, 2026-08-30T22:24:11Z
  IMPACT: The feedback loop is eliminated completely, other becomes smaller and
    more current-purpose, and ContextCompass never gains a competing generated copy.
  NEXT: Simplify classification to one ContextCompass exclusion, update README/
    design/tests, recalculate counts, and regenerate other.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:22:57Z
  TYPE: CONFLICT
  CLAIM: The first post-build check proves a ContextCompass feedback loop:
    recording the successful generation in this required active ticket moves
    the `other` fingerprint immediately. Including mutable tickets, boards,
    artifacts, context packs, or top-level scratch makes it impossible to both
    follow the Ticket Microcycle and leave committed outputs current.
  EVIDENCE:
  - `llm_support/_builder.py --check --include-untracked`
  - `context_compass/tickets/tasks/2026-08-30_implement_llm_support_compilation_pipeline_task.md`
  IMPACT: `other` must retain ContextCompass policy, roles, tools, examples,
    and system documents while excluding its mutable work-state/history lanes.
  NEXT: Add explicit live-state/artifact/scratch exclusions, update README/
    design/tests, recalculate corpus counts, and regenerate all affected output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:22:16Z
  TYPE: MEASURE
  CLAIM: LF-only range handling passes the expanded 24-test builder suite, and
    the real bootstrap build completes: source 584 files, tests 794 (including
    the new builder contract suite), other 2,273. All three bundle/index pairs
    validate before the deterministic manifest is published last.
  EVIDENCE:
  - `tests/unit/llm_support/test_builder.py`
  - `llm_support/manifest.json`
  - `llm_support/llm_full_src.txt`
  - `llm_support/llm_full_tests.txt`
  - `llm_support/llm_full_other.txt`
  IMPACT: The complete repository asset set exists under the accepted policy.
  NEXT: Verify output sizes/proofs, check mode, no-op second build, unchanged
    mtimes, and exact slice behavior before adding workflows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:21:18Z
  TYPE: BLOCKER
  CLAIM: Initial generation wrote temporary-current src/tests bundle-index
    pairs and stopped before manifest publication while validating other. The
    historical mixed-encoding ticket contains a Unicode control character that
    `str.splitlines()` treats as a break; the builder's contract defines only
    literal LF as a physical line, so validation offsets diverged.
  EVIDENCE:
  - `llm_support/_builder.py:220-680`
  - `context_compass/tickets/tasks/completed/2026-05-20_lay_spell_compiler_foundation_task.md`
  IMPACT: No manifest claims the partial output is current. Line counting,
    validation, and slicing must all use literal LF splitting.
  NEXT: Replace broad Unicode splitlines semantics with LF-only semantics,
    rerun focused tests, then regenerate every corpus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:20:38Z
  TYPE: FACT
  CLAIM: The tested core and authored consumer contract are ready for real
    generation. Builder is 899 lines and compile-clean; README is 142 lines,
    begins with ContextCompass authority, documents all corpora/commands/
    exclusions/trust/CI behavior; the focused 23-test suite is green; and
    llm_support is pinned to LF.
  EVIDENCE:
  - `llm_support/_builder.py:1-899`
  - `llm_support/README.md:1-142`
  - `tests/unit/llm_support/test_builder.py:1-331`
  - `.gitattributes:43-50`
  IMPACT: Initial repository generation can proceed from tested contracts
    without touching runtime/package behavior.
  NEXT: Run the explicit include-untracked bootstrap build, inspect manifest/
    counts/sizes/index ranges, then require tracked-only check parity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:19:39Z
  TYPE: MEASURE
  CLAIM: The complete focused builder contract suite passes 23 tests. It covers
    corpus/exclusion policy, four encoding lanes plus mixed UTF-8/CP1252, binary
    refusal, bundle/index round-trip, idempotent writes, untracked opt-in,
    incremental rebuild, tamper repair, slice, and global-contract invalidation.
  EVIDENCE:
  - `tests/unit/llm_support/test_builder.py:1-390`
  IMPACT: The tested core is ready to receive its README/LF policy and generate
    real repository outputs.
  NEXT: Write the ContextCompass-first README and LF attribute, then perform the
    initial include-untracked generation and inspect all outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:19:13Z
  TYPE: BLOCKER
  CLAIM: Focused tests compile and all 18 no-temp cases pass. Five remaining
    tests fail before their bodies because pytest cannot enumerate the sandbox-
    blocked global `pytest-of-Mark` directory while creating `tmp_path`.
  EVIDENCE:
  - `tests/unit/llm_support/test_builder.py`
  - `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit/llm_support/test_builder.py`
  IMPACT: Builder assertions requiring temporary Git repositories remain
    unexecuted; no source correction follows from fixture setup failure.
  NEXT: Rerun the identical focused file with normal host temporary-directory access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T22:17:08Z
  TYPE: FACT
  CLAIM: Mixed decoding and Git tuple ordering are fixed; list mode now reports
    the expected 584-file/270,707-line source corpus. It also exposes a path-
    classification edge: pathlib gives `.gitignore`, `.gitattributes`, and
    `.gitkeep` an empty suffix, so suffix-only policy misroutes them.
  EVIDENCE:
  - `llm_support/_builder.py:20-115`
  - `llm_support/_builder.py:180-350`
  IMPACT: Dotfile inclusion/exclusion must be keyed by exact filename before
    corpus counts can be accepted.
  NEXT: Add exact filename sets for policy dotfiles/placeholders, keep the
    builder below 900 lines, and rerun list with explicit candidate diagnostics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T22:16:23Z
  TYPE: BLOCKER
  CLAIM: Correct Git classification reaches the measured historical encoding
    edge and fails before output. The file is mixed: valid UTF-8 E2-80-xx
    punctuation sequences plus isolated CP1252 E7 bytes for `ç`. Decoding the
    whole file as either strict UTF-8 or CP1252 is therefore wrong.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-05-20_lay_spell_compiler_foundation_task.md`
  - `llm_support/_builder.py:180-215`
  IMPACT: A lossless mixed decoder must preserve valid UTF-8 sequences and map
    only surrogate-escaped invalid bytes through CP1252/Latin-1.
  NEXT: Implement the bounded mixed fallback inside `decode_source`, keep the
    builder under 900 lines, and rerun compile/list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:15:27Z
  TYPE: BLOCKER
  CLAIM: The first live list run generated no outputs and exposed one tuple-
    ordering defect: `_tracked_entries` returned dictionary items as
    `(path, mode)` while `discover` consumes `(mode, path)`. All 4,303
    candidates therefore appeared as mode-string paths and were excluded.
  EVIDENCE:
  - `llm_support/_builder.py:250-340`
  IMPACT: Discovery is incorrect but no repository asset was written.
  NEXT: Return explicit `(mode, path)` tuples, rerun compile/list, and require
    measured corpus counts before writing tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T22:14:58Z
  TYPE: FACT
  CLAIM: The builder core is reduced from 980 to 884 physical lines without
    removing contracts, compiles successfully, remains stdlib-only, imports no
    Melder runtime, and implements classification, strict decoding,
    fingerprints, selective atomic build/check, list, corpus, and slice paths.
  EVIDENCE:
  - `llm_support/_builder.py:1-884`
  IMPACT: The single-file size gate is satisfied and focused behavioral tests
    can now be authored against a stable core.
  NEXT: Exercise list mode against the live repository, then add contract-dense
    unit tests before generating outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:13:53Z
  TYPE: BLOCKER
  CLAIM: The first stdlib builder draft compiles successfully but is 980
    physical lines, exceeding the repository's under-900-line single-file
    creation gate. No generated outputs or tests have been written from it.
  EVIDENCE:
  - `llm_support/_builder.py:1-980`
  IMPACT: The builder must be tightened before it can become the accepted
    implementation baseline.
  NEXT: Remove redundant prose/vertical expansion and consolidate small helpers
    without weakening contracts, then require fewer than 900 lines and clean compile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T22:09:30Z
  TYPE: CONFLICT
  CLAIM: The discovery artifact's exact working-byte source hash conflicts with
    its Windows/Linux identical-output requirement. This repository intentionally
    retains mixed Git EOL conventions, so the same committed text may be CRLF
    in one working tree and LF in another. Use detected source encoding plus
    normalized UTF-8/LF content SHA256 and byte count in bundles, indexes,
    fingerprints, and manifest.
  EVIDENCE:
  - `.gitattributes:1-46`
  - `src/melder/_build_assets/_agent_documentation/_builder.py:132-177`
  - `context_compass/artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md:145-260`
  IMPACT: Semantic text and encoding changes still move fingerprints, while
    checkout-only EOL spelling does not produce cross-platform churn.
  NEXT: Correct the discovery artifact's hash fields, then implement the builder
    against the portable normalized-content contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:07:25Z
  TYPE: PLAN
  CLAIM: Implement the accepted builder/test/README core first, then generate
    outputs, rename/add workflows, and finish with deterministic repository checks.
  EVIDENCE:
  - `context_compass/artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md:1-496`
  IMPACT: Large generated outputs are produced only after the generator contract is tested.
  NEXT: Implement the builder core and focused unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation is complete. The 886-line stdlib builder owns three selective
corpora, Markdown indexes, and one deterministic manifest; the 28-test suite,
real check/no-op/slice validation, source-asset check, LF/diff hygiene, and both
read-only workflows pass. ContextCompass is excluded from bundle inputs and
referenced directly by README. Await owner acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
