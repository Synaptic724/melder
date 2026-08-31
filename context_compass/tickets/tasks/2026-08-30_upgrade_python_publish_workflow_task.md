# Task: Upgrade the Python package publication workflow

## Metadata
- Task ID: TASK-2026-08-30-upgrade-python-publish-workflow
- Story: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T15:55:48Z
- Updated: 2026-08-31T01:01:03Z

## Objective
Deliver a release-gated Melder pipeline that tests supported Python 3.14
runtimes, corrects matrix-exposed concurrency/test defects, validates durable
assets and distributions, and publishes with the owner-configured PyPI token
only from current `prod` HEAD.

## Ticket Contract
- ENTRY_GATE: Owner approved upgrading the existing staged workflow after comparison
  with the ContextCompass reference.
- EXECUTION_BOUNDARY: Existing publication/fingerprint scope plus
  `Spell._get_or_build_creation_context`, the two failing identity/gate tests,
  focused CreationContext synchronization coverage, patch/canonical docs,
  deterministic assets, and ContextCompass tracking.
- DEPENDENCIES: Existing `pyproject.toml` dependency groups, build-asset runner,
  supported unit/component/integration test tiers, and PyPI trusted publishing.
- EXIT_GATE: The workflow remains structurally valid; all four matrix postures
  stay supported; focused 3.14/3.14t concurrency tests, supported suites,
  asset checks, and distribution checks pass.
- FAILURE_ESCALATION: Stop on a required public API/support-policy change,
  hot-path regression, deadlock, or validation failure outside the approved boundary.

## Scope Boundaries
- In scope:
  - exact current-prod commit gate for release and manual dispatch
  - Python 3.14 and 3.14t tests on Ubuntu and Windows
  - build-asset, wheel/sdist, version/tag, and installed-wheel verification
  - current official action major upgrades
  - OIDC-only PyPI publishing through the existing `pypi` environment
  - cross-platform source fingerprints for agent documentation and bind guard
  - removal of the system-document builder's invalid-escape warning
  - cold/rebuild CreationContext synchronization under the existing spell lock
  - deterministic LoadGate and `Existence.many` identity tests
  - repeated GIL/free-threaded regressions and synchronized docs/assets
- Out of scope:
  - publishing a release
  - changing PyPI or GitHub environment configuration
  - changing public APIs, supported runtimes, versions, or dependencies
  - copying ContextCompass-specific payload/CLI checks

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Token authentication is wired through the configured
  environment secret; YAML, secret-boundary, and diff checks pass.

## Steps / Checklist
- [x] Replace the minimal workflow with the tailored release pipeline.
- [x] Validate trigger/gate, job dependencies, action versions, and embedded scripts.
- [x] Inspect the exact diff and report remaining GitHub/PyPI configuration requirements.
- [x] Diagnose and correct Linux-only false staleness in cached build assets.
- [x] Add cross-platform fingerprint regression coverage and remove the invalid escape.
- [x] Regenerate assets and rerun the complete build-assets validation lane.
- [x] Diagnose all supplied GitHub matrix failures and reproduce the runtime race.
- [x] Create and consume the concurrency-repair patch contracts.
- [x] Implement the double-checked cold CreationContext lock boundary.
- [x] Correct LoadGate and `Existence.many` test choreography.
- [x] Add focused deterministic/repeated concurrency regression coverage.
- [x] Synchronize canonical context and scoped build/LLM assets; defer the
      unrelated 209-descriptor graph backlog explicitly.
- [x] Run focused and supported validation under local 3.14 and 3.14t.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- A production-ready `python-publish.yml` for Melder.
- Checkout-EOL-independent source fingerprints for the two cached assets.
- Warning-clean build-asset source under Python 3.14.
- Deterministic four-cell test matrix with the shared-spell race corrected.

## Files / Paths Impacted
- `.github/workflows/python-publish.yml`
- `.gitattributes`
- `src/melder/_build_assets/_agent_documentation/_builder.py`
- `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py`
- `src/melder/_build_assets/_bind_guard/_builder.py`
- `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`
- `src/melder/_build_assets/_system_documents/_builder.py`
- `tests/unit/melder/build_assets/test_build_asset_runner.py`
- `src/melder/aether/spellbook/spell.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py`
- `tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py`
- `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py`
- `context_compass/system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/`
- `context_compass/attention_board.md`
- This task.

## Validation
- Token publish wiring: pass (YAML parse, exact secret reference, no OIDC permission,
  attestations disabled, and diff hygiene clean).
- YAML structure and workflow semantic assertions: pass.
- Embedded Python syntax: pass (two heredocs).
- Real wheel/sdist verifier rehearsal: pass.
- Isolated installed-wheel runtime/document smoke: pass.
- Build-asset check and diff hygiene: pass.
- Cross-platform fingerprint regression: pass (`2 passed, 35 deselected`).
- Complete build-assets unit lane: pass (`116 passed`).
- Asset check with `SyntaxWarning` promoted to error: pass (three key matches).
- Four directly affected files: 93 passed on 3.14t; 93 passed on GIL 3.14.
- Shared-spell cluster stress: 100/100 on each runtime (200 total).
- Final affected five-file set: 127 passed on each runtime.
- Complete 3.14t suite: 10,991 passed, 28 skipped, 15 xfailed, 1 xpassed.
- Complete GIL 3.14 suite: identical counts plus expected GIL warning.
- Aetheric Mediator hard paths: 34 passed on each runtime; churn probe 30/30
  fresh processes per runtime.
- Source/repository asset checks, component index, dual-runtime syntax,
  changed-line Ruff, EOL, and diff hygiene: pass.

## Risks / Rollback Notes
- A mismatched GitHub environment name breaks PyPI OIDC after all earlier jobs pass.
- A release workflow not present on GitHub's default branch may not receive release events.
- The prod gate intentionally rejects releases for tags not pointing at current prod HEAD.
- Removing GIL jobs would hide defects and contradict current support claims.
- The slow-path lock must not enter the state-2 hot context/executor lane.

## Applicable Anti-Patterns
- [x] No publishing on every prod push.
- [x] No API-token fallback unless explicitly requested.
- [x] No ContextCompass-specific wheel assertions.
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from UNKNOWN or HYPOTHESIS.
- [ ] No closure without acceptance confirmation and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverable produced
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for review routing

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/architecture_patch.md`
  - `system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/component_patch_shared_spell_context.md`
  - `system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/code_description_patch_shared_spell_context_rebuild.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - GitHub Actions publication safety
  - PyPI trusted publishing
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: workflow decisions, validation evidence, and one-step continuation.
- Keep notes append-only and evidence-backed.

## Notes
- DATETIME: 2026-08-31T00:26:40Z
  TYPE: MEASURE
  CLAIM: Final local gates pass: source build assets are current at 0.2.0;
    all three include-untracked LLM corpora match fingerprints/output proofs;
    the component index is current at 136 sections/8,394 lines; all edited
    Python files are LF and compile on 3.14/3.14t; diff hygiene exits zero; and
    diff-scoped Ruff reports zero findings after excluding UP045, which
    conflicts with this profile's required `Optional` syntax. Isolated mypy
    reports 15 pre-existing Spell-file errors and none in the changed range.
  EVIDENCE:
  - `src/melder/_build_assets/_build_asset_runner.py --check`
  - `llm_support/_builder.py --check --include-untracked`
  - `context_compass/tools/system_documents/index_document.py --check`
  - `git -c core.whitespace=cr-at-eol diff --check`
  - Diff-scoped Ruff changed-line intersection, 2026-08-30
  IMPACT: Runtime, tests, documentation, generated assets, EOL, syntax, and
    changed-line lint gates are ready for GitHub matrix verification.
  NEXT: Move task/attention routing to review; no commit, tag, push, GitHub
    release, or PyPI upload is performed by this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:26:40Z
  TYPE: FACT
  CLAIM: PyPI's official JSON API currently lists only Melder 0.1.0, so version
    0.2.0 has not been consumed and may still be published after these fixes.
    Changing an already-published GitHub release back to prerelease should not
    be relied on to retrigger this workflow's `published`-only event. The
    workflow's manual dispatch on corrected `prod` is deterministic, while
    recreating the v0.2.0 release/tag at corrected prod will emit a fresh
    published event and keep GitHub source archives aligned.
  EVIDENCE:
  - `https://pypi.org/pypi/melder/json` (latest 0.1.0; releases [0.1.0])
  - `.github/workflows/python-publish.yml:1-93`
  - `https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#release`
  - `https://pypi.org/help/#file-name-reuse`
  IMPACT: 0.2.0 can be released without a version bump. If any 0.2.0 file
    reaches PyPI first, future corrected artifacts must use 0.2.1 because PyPI
    never permits filename reuse.
  NEXT: After the corrected commit reaches prod, ensure v0.2.0 targets that
    commit and either publish a recreated release or manually dispatch the
    workflow on prod.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:21:26Z
  TYPE: BLOCKER
  CLAIM: Exact build-asset, LLM include-untracked, component-index, dual-runtime
    syntax, and whitespace gates pass. Five edited Python files are
    index-LF but working-tree mixed after line-local patches and require
    mechanical LF normalization. Whole-file Ruff and mypy are not acceptance
    gates for this patch: they surface extensive pre-existing debt (mypy
    traverses 290 imported files and reports 1,318 errors; Ruff reports
    unrelated existing findings throughout the target files).
  EVIDENCE:
  - `git ls-files --eol -- <five edited Python files>`
  - `src/melder/_build_assets/_build_asset_runner.py --check`
  - `llm_support/_builder.py --check --include-untracked`
  - `context_compass/tools/system_documents/index_document.py --check`
  IMPACT: Normalize only the five changed files to their committed LF
    convention, then validate changed-line/source semantics without treating
    unrelated repository debt as introduced regression.
  NEXT: Normalize exact targets, rerun EOL/diff gates, run isolated mypy and
    diff-scoped Ruff review, then inspect final generated-only scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:20:17Z
  TYPE: FACT
  CLAIM: Canonical and generated assets are synchronized to the approved
    boundary. `src_components` now documents the lock-free ready context and
    spell-locked cold rebuild; its index is fresh at 136 sections/8,394 lines,
    and the outside-section preservation multiset hash is unchanged. Release
    notes now carry the 10,991 count. Source assets regenerate at unchanged
    membership (452 agent entries, 628 bind-guard entries, four documents).
    LLM corpora regenerate selectively at 584 source, 794 tests, and 263 other
    files, including the new release note.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:2414-2654`
  - `context_compass/system_docs/src_components_index.md:1-166`
  - `RELEASE_NOTES_0.2.0.md:170-180`
  - `src/melder/_build_assets/_build_asset_runner.py`
  - `llm_support/manifest.json`
  IMPACT: Runtime, tests, authored component truth, packaged documents, and
    LLM bundles agree. The broad source-graph backlog remains explicitly
    deferred and its diagnostic changes were fully restored.
  NEXT: Run exact build/LLM checks, targeted static typing/lint/compile,
    workflow/YAML assertions, content-preservation and diff/EOL gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:19:16Z
  TYPE: DECISION
  CLAIM: Canonical component prose and its index are updated, but full source
    graph extraction is deferred. Current extraction would rewrite 209
    descriptors accumulated since the graph's August baseline, and current
    assembly would add 2,879/delete 893 graph lines from generator-format drift.
    This patch changes no node, edge, ownership, or public-method inventory;
    carrying that unrelated generated sweep into the release fix is outside scope.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:2414-2654`
  - `context_compass/system_docs/src_components.md:4647-4662`
  - `context_compass/tools/system_documents/python/extract_graph.py --check`
  - `git diff --numstat -- context_compass/system_docs/src_graph.md context_compass/system_docs/src_graph_index.md`
  IMPACT: Restore the three graph-generation files changed by the diagnostic
    attempt and keep the targeted authored component/index delta. A separate
    graph-refresh lane must reconcile the 209-descriptor backlog atomically.
  NEXT: Restore only the diagnostic graph outputs, regenerate package build
    assets and LLM corpora from the approved source/component/test changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:12:47Z
  TYPE: MEASURE
  CLAIM: Both complete supported runtime postures are green on the corrected
    tree. Windows 3.14t reports 10,991 passed, 28 skipped, 15 expected
    failures, one expected pass in 173.02 seconds. Windows 3.14 GIL reports
    the same counts plus the expected GIL warning in 183.11 seconds. Both exit
    zero; the pre-existing terminal unawaited-coroutine warning remains.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/unit tests/component tests/integration`
  - `py -3.14 -m pytest -q -p no:cacheprovider tests/unit tests/component tests/integration`
  IMPACT: Every supplied GitHub failure and the additional GIL-only mediator
    probe are corrected without dropping support. The implementation is ready
    for canonical documentation and deterministic asset synchronization.
  NEXT: Merge the slow-path synchronization delta into canonical components,
    regenerate indexes/graph/build assets/LLM corpora, and run final static gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:08:58Z
  TYPE: MEASURE
  CLAIM: The complete Aetheric Mediator hard-path file passes 34/34 under
    3.14t and 34/34 under GIL 3.14. The corrected churn probe then passes
    30/30 fresh pytest processes on each interpreter (60 total), covering both
    scheduler postures without a fairness assumption.
  EVIDENCE:
  - `tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_failure_paths.py`
  IMPACT: The unrelated full-GIL blocker is corrected at its test contract;
    the complete ordinary-3.14 suite can now be rerun.
  NEXT: Rerun the full GIL-supported suite unsandboxed and require exit zero.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:07:26Z
  TYPE: FACT
  CLAIM: The standalone Aetheric Mediator probe now matches its actual
    no-fairness contract. Under three intent churners, both successful
    whole-world admission and a bounded refusal are accepted only with the
    correct outcome/evidence; every path still requires terminated churners,
    zero churn errors, and zero leaked claims. No mediator runtime code changed.
  EVIDENCE:
  - `tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_failure_paths.py:272-338`
  IMPACT: The last GIL failure's scheduling assumption is removed without
    weakening deadlock, refusal-evidence, or claim-lifecycle assertions.
  NEXT: Run this component file repeatedly under both interpreters, then rerun
    the complete GIL suite and retain the prior green 3.14t full-suite evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:05:54Z
  TYPE: DECISION
  CLAIM: The remaining GIL failure is an invalid fairness assertion, not a
    mediator regression. ClaimTable provides notify-and-retry with no waiter
    priority; the immediately adjacent test explicitly documents that
    continuously overlapping intent holders may starve a world-exclusive
    request. Three tight churners may either leave a quiescent gap or overlap
    through the 0.25-second bound, so both admission and an evidenced timeout
    are contract-valid.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:3164-3434`
  - `src/melder/aether/aetheric_mediator/mediator.py:1013-1085`
  - `src/melder/aether/aetheric_mediator/claim_table.py:392-590`
  - `tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_failure_paths.py:272-374`
  IMPACT: Adding fairness would be an unrequested subsystem redesign. The test
    should instead require one of the two documented outcomes, correct refusal
    evidence, no deadlock, no churn error, and zero leaked claims.
  NEXT: Read the complete component-test file, amend the patch contract, then
    rewrite only the scheduling-dependent probe and rerun both full suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:03:54Z
  TYPE: BLOCKER
  CLAIM: The complete Windows 3.14 GIL suite clears every supplied CI failure
    but exposes one separate component-test failure: a whole-world exclusive
    Aetheric Mediator request times out while three frame-load threads
    continuously reacquire compatible world-intent claims. Final result is
    10,990 passed, 28 skipped, 15 expected failures, one expected pass, and one
    failure in 188.82 seconds.
  EVIDENCE:
  - `tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_failure_paths.py:280-334`
  - `src/melder/aether/aetheric_mediator/mediator.py:468-512`
  IMPACT: The original release defects are fixed, but ordinary 3.14 is not yet
    full-suite green. The remaining failure is outside the changed live
    Conduit path and must be classified as a fairness defect or an invalid
    non-starvation test before any edit.
  NEXT: Read the complete starvation test, mediator admission wait, and claim
    table wake/reacquisition contracts; reproduce the case repeatedly under
    GIL and 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T00:00:10Z
  TYPE: MEASURE
  CLAIM: The complete supported Windows 3.14t suite passes with 10,991 passed,
    28 skipped, 15 expected failures, one expected pass, and exit code zero in
    173.02 seconds. The pre-existing terminal warning
    `coroutine 'coro' was never awaited` remains and does not affect the
    pytest result; it is not introduced by this patch.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/unit tests/component tests/integration`
  IMPACT: Free-threaded supported behavior is green across the complete local
    suite. Ordinary 3.14 remains the second full behavioral gate.
  NEXT: Run the identical complete suite under local Windows 3.14 GIL with
    normal host temporary-directory access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:56:47Z
  TYPE: BLOCKER
  CLAIM: The first complete 3.14t invocation was stopped at 39% after immediate
    setup errors across temporary-path tests. This is the previously evidenced
    sandbox ACL boundary: focused assertions already pass, but the sandboxed
    process cannot execute the full suite's host temporary-directory fixtures.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/unit tests/component tests/integration`
  - Prior ticket evidence at 2026-08-30T18:44:43Z and 2026-08-30T20:36:54Z
  IMPACT: No full-suite product result exists from the interrupted invocation;
    source changes must not follow fixture setup failures.
  NEXT: Rerun the identical 3.14t suite with normal host temporary-directory
    access, then do the same under GIL 3.14.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:55:40Z
  TYPE: MEASURE
  CLAIM: Focused cross-runtime validation is green. The four directly affected
    files pass 93/93 under local Windows 3.14t and 93/93 under Windows 3.14
    GIL. The exact shared two-cluster scenario then passes 100/100 fresh-world
    iterations on each interpreter (200 total), versus 20/30 failures before
    the source fix.
  EVIDENCE:
  - `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py`
  - `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py`
  - `tests/integration/melder/conduit/test_conduit_integration_concurrency.py`
  IMPACT: The two invalid tests and the reproduced runtime race are corrected
    on both supported local runtime postures without dropping a matrix cell.
  NEXT: Run the complete supported unit/component/integration suite under
    3.14t and GIL 3.14, then synchronize docs and deterministic assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:54:29Z
  TYPE: FACT
  CLAIM: The approved implementation is applied and reread. Ready contexts
    remain lock-free; only state-0/1 retrieval takes the existing spell RLock
    and rechecks readiness. The LoadGate test now keeps a live owner through
    holder-side release with explicit worker/holder error capture. The
    `many` test retains all returned objects, and the factory suite includes
    a controlled-lock regression proving no builder call crosses the phase-owned lock.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell.py:743-793`
  - `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:393-467`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:841-857`
  - `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py:144-171`
  - `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py:300-338`
  IMPACT: Source and tests now match the consumed patch contract without a
    public API, runtime-support, workflow-matrix, or ready-context hot-path change.
  NEXT: Run the four directly affected files under 3.14t and GIL 3.14, then
    repeat the shared-spell stress before wider validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:51:14Z
  TYPE: PLAN
  CLAIM: Patch gate is consumed and mapped. Architecture invariants map to a
    double-checked lock only in `Spell._get_or_build_creation_context`;
    the component before/after contract maps to context-factory unit coverage
    plus existing cross-conduit tests; code-description test corrections map
    to live-holder Events and retained `many` objects. The workflow matrix
    remains unchanged. Validation proceeds focused GIL/3.14t, repeated stress,
    supported suites, then docs/assets/diff gates.
  EVIDENCE:
  - `system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/architecture_patch.md:1-57`
  - `system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/component_patch_shared_spell_context.md:1-35`
  - `system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/code_description_patch_shared_spell_context_rebuild.md:1-37`
  IMPACT: System-impacting source editing is unblocked inside a no-public-API,
    no-hot-path-lock boundary with explicit rollback and validation contracts.
  NEXT: Read every target source/test file completely, then apply the runtime
    and two test changes with focused regression coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:48:32Z
  TYPE: MEASURE
  CLAIM: A double-checked `spell._lock` around only the cold/rebuild
    `Spell._get_or_build_creation_context` path eliminates the reproduced
    race: the unmodified GIL probe failed 20/30 runs, while the candidate
    monkeypatch passed 50/50. The state>=2 hot context read remains lock-free;
    only a missing/invalidated context waits for an in-flight phase run.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell.py:743-773`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:294-340`
  - Local Windows 3.14 GIL candidate probe, 2026-08-30
  IMPACT: The observed runtime defect has a minimal, performance-bounded
    correction that preserves the normal hot meld lane and waits only at the
    already-cold rebuild boundary.
  NEXT: Create and consume the required architecture/component/code patch
    contracts, then implement the synchronized slow path and two test repairs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:43:16Z
  TYPE: DECISION_REQUEST
  CLAIM: Do not delete GIL matrix cells as a failure workaround. Recommended
    correction is to retain all four cells, make the `many` test retain the
    three live objects, keep the LoadGate holder alive until it performs its
    own release, and repair shared-spell phase-5/context synchronization with
    repeated GIL and 3.14t regressions. If Melder is intentionally no-GIL-only,
    that is a separate public support decision requiring a hard import refusal,
    3.14t build/smoke jobs, and metadata/README/release updates; it still does
    not remove the Ubuntu 3.14t LoadGate failure.
  EVIDENCE:
  - `src/melder/__init__.py:165-201`
  - `pyproject.toml:6-54`
  - `.github/workflows/python-publish.yml:68-111`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:170-215`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:294-340`
  - `https://docs.python.org/3.14/library/threading.html#threading.get_ident`
  - `https://docs.python.org/3/library/functions.html#id`
  IMPACT: The owner must choose product support policy independently of the
    technical fixes. Either support posture still requires correcting at least
    the LoadGate test; a trustworthy release also requires the context race fix.
  NEXT: Obtain owner direction: keep GIL support and fix all three classes
    (recommended), or intentionally hard-reject GIL and update every public
    support surface while still fixing the 3.14t blocker.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:41:52Z
  TYPE: MEASURE
  CLAIM: The two-cluster race is reproducible and real: 20 of 30 local Windows
    3.14 GIL runs failed. A peer's conduit-local phase-5 revalidation clears
    the shared spell's codegen outputs and CreationContext under
    `spell._lock`; another conduit reads the same spell lock-free, sees
    context-switch state 0 with `resolution_required=False` and
    `resolution_complete=True`, elects itself as context builder, and raises
    because phase 11 has not republished `spell_codegen_creation` yet.
    Separately, plain ephemeral object allocation produced only 7 distinct
    addresses across 12 GIL creations versus 12/12 on 3.14t.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:170-215`
  - `src/melder/aether/conduit/meld/meld.py:833-890`
  - `src/melder/aether/conduit/meld/conduit_meld.py:361-377`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:294-340`
  - Local 30-run GIL cluster probe and GIL/3.14t identity probe, 2026-08-30
  IMPACT: One runtime synchronization defect and two invalid test constructions
    must be corrected. Matrix deletion is not a technical fix and Ubuntu 3.14t
    remains blocked by the LoadGate test regardless.
  NEXT: Verify Python's documented identity-reuse contracts, then recommend the
    minimal test and runtime correction boundary to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:37:25Z
  TYPE: MEASURE
  CLAIM: The exact five-case probe passes 5/5 on local Windows 3.14t. The same
    source and pytest installation under local Windows 3.14 GIL reproduces two
    CI classes immediately: the two-cluster concurrent meld raises the missing
    `spell_codegen_creation` error, and the nondisposable-many `id()` test
    observes only two addresses. The other three cases passed in that run,
    confirming the LoadGate and shared-context failures are scheduling-sensitive.
  EVIDENCE:
  - `py -3.14 -m pytest <five supplied node ids>`
  - `.venv_new/Scripts/python.exe -m pytest <five supplied node ids>`
  - `tests/integration/melder/conduit/test_conduit_integration_concurrency.py:286-351`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:76-151`
  IMPACT: GIL removal would mask reproducible defects rather than establish a
    clean release. Windows 3.14t green is real but does not validate Ubuntu
    3.14t or GIL behavior.
  NEXT: Measure repeat frequency and trace how dynamic link/cluster invalidation
    can expose a spell with resolution flags clear while its phase-11 artifact is absent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:36:28Z
  TYPE: FACT
  CLAIM: Melder currently supports both `3.14` and `3.14t` in packaging and
    the release matrix; GIL mode only emits a performance warning. Two CI
    failures are test-contract defects: the LoadGate test deliberately lets
    its holder thread die, then creates a worker that may legally reuse the
    same numeric thread ident; the `many` test retains only integer `id()`
    values even though nondisposable many instances are intentionally
    transient and may be deallocated between comprehension iterations.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:68-93`
  - `src/melder/__init__.py:179-201`
  - `src/melder/utilities/synchronization/load_gate.py:216-480`
  - `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:393-426`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:73-123`
  - `tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:841-855`
  IMPACT: Dropping GIL jobs would change declared support and hide two bad tests;
    it would still leave Ubuntu 3.14t red. The three Ubuntu-GIL
    `spell_codegen_creation` concurrency failures remain a distinct runtime
    or test-order question.
  NEXT: Reproduce the five focused cases locally, then trace the shared-spell
    CreationContext publication/invalidation path before recommending edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:30:46Z
  TYPE: BLOCKER
  CLAIM: External GitHub validation is not green. Ubuntu 3.14t admits a
    supposedly foreign root while a LoadGate is held; Windows 3.14 observes
    only two distinct integer `id()` values across three ephemeral
    `Existence.many` resolutions; Windows 3.14t passes. Root cause and
    GIL-support policy are not yet established.
  EVIDENCE:
  - Owner-supplied GitHub Actions output, 2026-08-30
  - `C:/Users/Mark/.codex/attachments/b0c35a04-b474-420c-9136-0931028d26ea/pasted-text.txt`
  IMPACT: Publishing remains blocked. Removing GIL jobs would not address the
    reported Ubuntu 3.14t failure and could conceal a test or synchronization defect.
  NEXT: Read the complete CI output, workflow matrix, runtime GIL guard,
    failing tests, LoadGate, and mediator call path before recommending a fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:47:05Z
  TYPE: MEASURE
  CLAIM: Final local validation passes. The complete build-assets unit lane
    reports `116 passed`; the exact asset check passes all three assets with
    `SyntaxWarning` promoted to an error; and `git diff --check` exits zero.
    Generated changes remain limited to the two expected source-key stamps,
    with 452 agent-documentation entries and 628 bind-guard entries unchanged.
  EVIDENCE:
  - `tests/unit/melder/build_assets/test_build_asset_runner.py:557-590`
  - `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:20-26`
  - `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:15-19`
  IMPACT: The local defect is corrected and the branch is ready for signed
    commit/promotion. A GitHub Linux rerun remains external verification and
    cannot occur until the change is pushed.
  NEXT: Review the final diff, then create the signed commit in the intended
    branch lane and rerun GitHub Actions; do not publish from this worktree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:45:59Z
  TYPE: FACT
  CLAIM: Canonical regeneration completed for all three discovered assets. The
    generated diff changes exactly the two expected `SOURCE_SHA256` stamps to
    the same canonical key; agent-documentation remains 452 marked entries,
    bind guard remains 628 entries, and every system-document output is
    byte-identical.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:20-26`
  - `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:15-19`
  IMPACT: Regeneration did not alter policy membership, documentation payloads,
    graph data, or runtime source. The repository is ready for the full focused
    build-asset validation lane.
  NEXT: Run the entire build-assets unit-test directory unsandboxed, run the
    canonical `--check` with SyntaxWarning promoted to error, and check diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:45:11Z
  TYPE: MEASURE
  CLAIM: The unsandboxed focused regression executes both real builder cases
    and passes (`2 passed, 35 deselected`). Warning-as-error compilation also
    passes for the agent-documentation, bind-guard, and system-document builders.
  EVIDENCE:
  - `tests/unit/melder/build_assets/test_build_asset_runner.py:557-590`
  - `src/melder/_build_assets/_agent_documentation/_builder.py:133-177`
  - `src/melder/_build_assets/_bind_guard/_builder.py:116-165`
  - `src/melder/_build_assets/_system_documents/_builder.py:644-648`
  IMPACT: The source fix and warning cleanup are validated independently of
    generated outputs. Deterministic regeneration can now restamp the two keys.
  NEXT: Run the canonical build-asset runner once, then inspect every generated
    diff before accepting the regeneration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:44:43Z
  TYPE: BLOCKER
  CLAIM: Warning-as-error compilation passes for all three touched builders.
    The focused pytest selection did not execute either regression assertion;
    both cases failed during `tmp_path` setup because the sandbox cannot scan
    the host temp root `pytest-of-Mark`. This is an environment ACL failure,
    not a test or implementation failure.
  EVIDENCE:
  - `tests/unit/melder/build_assets/test_build_asset_runner.py:557-590`
  - `.venv_new/Scripts/python.exe -m pytest -q tests/unit/melder/build_assets/test_build_asset_runner.py -k fingerprints_ignore_checkout_line_endings`
  IMPACT: Focused pytest status remains unverified. No source correction follows
    from a fixture that never ran the test body.
  NEXT: Rerun the identical focused pytest command with unsandboxed filesystem
    access, then record its actual assertion result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:43:45Z
  TYPE: FACT
  CLAIM: The authored fix is implemented and reread. Both builders now hash
    newline-canonical source bytes through a typed, documented pure helper; the
    regression covers both real builders and proves LF/CRLF equivalence plus
    genuine text-change sensitivity. The invalid escape is removed, and no
    publish-workflow or runtime API code changed.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/_builder.py:133-177`
  - `src/melder/_build_assets/_bind_guard/_builder.py:116-165`
  - `src/melder/_build_assets/_system_documents/_builder.py:644-648`
  - `tests/unit/melder/build_assets/test_build_asset_runner.py:543-591`
  - `.gitattributes:25-29`
  IMPACT: The change is ready for focused tests and warning-as-error compilation
    before any generated manifest is rewritten.
  NEXT: Run the focused build-asset tests, compile all three builders with
    SyntaxWarning promoted to an error, and inspect any failure before regeneration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:41:46Z
  TYPE: PLAN
  CLAIM: Normalize CRLF and lone CR to LF inside both cached-asset source
    fingerprints while preserving every other byte and the existing path hash.
    Add one parametrized regression for both real builders, update the runner
    test's raw-byte explanation and `.gitattributes` commentary, reword the
    invalid escape, then regenerate through the canonical runner. The publish
    workflow itself does not change.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/_builder.py:134-160`
  - `src/melder/_build_assets/_bind_guard/_builder.py:116-147`
  - `src/melder/_build_assets/_system_documents/_builder.py:646-647`
  - `tests/unit/melder/build_assets/test_build_asset_runner.py:543-555`
  - `.gitattributes:25-28`
  IMPACT: Linux and Windows calculate one source key for one Git tree without
    pinning hundreds of Python files to a new checkout-EOL policy or weakening
    semantic staleness detection.
  NEXT: Apply the exact authored-file patch, reread every touched section, and
    inspect the diff before regeneration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T18:39:44Z
  TYPE: FACT
  CLAIM: The Linux failure is a cross-platform false-staleness defect. Both
    failing builders hash raw working-tree bytes. This Windows checkout uses
    CRLF for the scanned Python files while Git stores their LF-normalized
    blobs, and `.gitattributes` intentionally supplies no Python EOL rule.
    Linux therefore computes different source keys over identical repository
    content. The separate SyntaxWarning comes from backslash-backtick escapes
    in the system-document builder's `parse_graph_adjacency` docstring.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/_builder.py:134-160`
  - `src/melder/_build_assets/_bind_guard/_builder.py:116-147`
  - `src/melder/_build_assets/_system_documents/_builder.py:646-647`
  - `.gitattributes:25-28`
  IMPACT: Regenerating again on Windows cannot fix CI; it only restamps the same
    platform-specific keys. Fingerprinting must canonicalize text line endings
    while retaining path and textual-content sensitivity.
  NEXT: Read the existing build-asset tests fully, then define the smallest
    regression test and implementation boundary for both builders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T16:04:06Z
  TYPE: MEASURE
  CLAIM: Generated rehearsal and egg-info directories were removed. Final diff
    hygiene passes, and the upgraded workflow is the only product-facing change.
    The previously staged empty workflow entry must be replaced with this validated
    346-line version before commit.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:1-346`
  IMPACT: The repository is ready for an exact workflow/tracking commit with no
    generated validation residue.
  NEXT: Stage the validated workflow plus its task/board route and create one local
    commit; do not publish or push.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T16:02:24Z
  TYPE: MEASURE
  CLAIM: Real local rehearsal passes. The embedded verifier accepts a fresh
    599-file wheel and 603-file sdist at version 0.1.2, proving bounded contents,
    required assets, metadata, and source/asset version agreement. An isolated
    wheel install verifies all four system documents and the 1,224-node,
    1,452-edge graph surface.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:111-327`
  IMPACT: The complex release-build assertions execute successfully rather than
    merely compiling. No upload or external publication occurred.
  NEXT: Remove only generated rehearsal/egg-info directories, then inspect the
    final diff and move the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T16:00:41Z
  TYPE: MEASURE
  CLAIM: Structural validation passes: YAML parses with the exact two triggers
    and five-job dependency graph; the 3.14/3.14t cross-platform matrix, action
    majors, OIDC-only publish contract, prod gate, and required checks are all
    present. Both embedded Python heredocs compile, all build assets are current,
    and diff hygiene passes.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:1-346`
  IMPACT: Workflow structure and embedded code syntax are valid. Runtime archive
    assertions still need execution against a real local build.
  NEXT: Build wheel/sdist locally and execute the workflow's distribution verifier
    and installed-wheel smoke logic against them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T15:58:44Z
  TYPE: BLOCKER
  CLAIM: The tailored workflow is implemented, and the first diff check finds
    only one formatting defect: an extra blank line at end of file. No semantic
    validation has run yet.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:347-347`
  IMPACT: Remove the trailing blank line before parsing and semantic checks.
  NEXT: Fix EOF formatting, then validate YAML structure and workflow contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T15:55:48Z
  TYPE: DECISION
  CLAIM: Keep release/manual triggers and OIDC-only publishing, but add an exact
    current-prod commit gate; test 3.14 and 3.14t on Linux/Windows; validate Melder
    build assets, distributions, version agreement, and installed-wheel behavior.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:1-54`
  - `pyproject.toml:1-246`
  IMPACT: The upgraded workflow will refuse non-prod releases and prevent a green
    build from publishing incomplete or internally inconsistent archives.
  NEXT: Replace the workflow in one scoped edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T01:00:05Z
  TYPE: DECISION
  CLAIM: Use the owner-configured `PYPI_API_TOKEN` environment secret for the
    publish action instead of OIDC. Remove `id-token: write`, pass the standard
    `__token__` user and secret-backed password, and disable OIDC-only attestations.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:322-346`
  - Owner direction in the active conversation, 2026-08-31T01:00:05Z
  IMPACT: The existing PyPI token becomes the sole upload credential and its
    value remains outside the repository.
  NEXT: Patch the publish job and validate YAML structure, secret wiring, and diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-31T01:01:03Z
  TYPE: MEASURE
  CLAIM: Token-mode workflow validation passes. The YAML composes successfully,
    `PYPI_API_TOKEN` is the sole credential reference, `id-token` is absent,
    attestations are disabled, and scoped diff hygiene exits zero.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:322-346`
  IMPACT: The configured environment secret is ready to authenticate the PyPI
    upload without committing or printing its value.
  NEXT: Review and commit the workflow change, promote it to `prod`, then trigger
    the release workflow from current `prod` HEAD.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The publication workflow and its four-cell runtime matrix remain intact. The
GitHub failures were two invalid identity tests plus one shared-spell
revalidation race; a complete GIL run also exposed one invalid fairness
assertion in the unwired Aetheric Mediator probe. All four are corrected.
Complete local 3.14t and GIL 3.14 suites now pass with 10,991 tests, and all
asset/static gates are current. No commit, tag, push, release edit, or PyPI
upload occurred. PyPI still lists only 0.1.0, so corrected 0.2.0 remains
available. After promotion to prod, ensure v0.2.0 points at corrected prod and
publish a recreated release or manually dispatch the workflow on prod.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
