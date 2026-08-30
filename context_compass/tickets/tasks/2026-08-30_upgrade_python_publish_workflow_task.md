# Task: Upgrade the Python package publication workflow

## Metadata
- Task ID: TASK-2026-08-30-upgrade-python-publish-workflow
- Story: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T15:55:48Z
- Updated: 2026-08-30T18:47:05Z

## Objective
Replace the minimal publication workflow with a release-gated Melder pipeline that
tests Python 3.14 runtimes, validates durable build assets and distributions, and
publishes to PyPI through OIDC only when the event commit is current `prod` HEAD.

## Ticket Contract
- ENTRY_GATE: Owner approved upgrading the existing staged workflow after comparison
  with the ContextCompass reference.
- EXECUTION_BOUNDARY: `.github/workflows/python-publish.yml`, the two cached
  build-asset fingerprint implementations and manifests, the system-document
  builder warning, one focused regression-test file, `.gitattributes`
  commentary, and ContextCompass tracking.
- DEPENDENCIES: Existing `pyproject.toml` dependency groups, build-asset runner,
  supported unit/component/integration test tiers, and PyPI trusted publishing.
- EXIT_GATE: The workflow remains structurally valid, cached-asset fingerprints
  are checkout-EOL independent, the build-asset check passes without the reported
  SyntaxWarning, and focused regression tests pass.
- FAILURE_ESCALATION: Stop on ambiguity in the PyPI environment name or on any
  validation result that requires changing package/runtime behavior.

## Scope Boundaries
- In scope:
  - exact current-prod commit gate for release and manual dispatch
  - Python 3.14 and 3.14t tests on Ubuntu and Windows
  - build-asset, wheel/sdist, version/tag, and installed-wheel verification
  - current official action major upgrades
  - OIDC-only PyPI publishing through the existing `pypi` environment
  - cross-platform source fingerprints for agent documentation and bind guard
  - removal of the system-document builder's invalid-escape warning
- Out of scope:
  - publishing a release
  - changing PyPI or GitHub environment configuration
  - changing runtime behavior, public APIs, versions, or dependencies
  - copying ContextCompass-specific payload/CLI checks

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Portable fingerprints, warning cleanup, deterministic
  regeneration, focused tests, the exact asset check, and diff hygiene pass.

## Steps / Checklist
- [x] Replace the minimal workflow with the tailored release pipeline.
- [x] Validate trigger/gate, job dependencies, action versions, and embedded scripts.
- [x] Inspect the exact diff and report remaining GitHub/PyPI configuration requirements.
- [x] Diagnose and correct Linux-only false staleness in cached build assets.
- [x] Add cross-platform fingerprint regression coverage and remove the invalid escape.
- [x] Regenerate assets and rerun the complete build-assets validation lane.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- A production-ready `python-publish.yml` for Melder.
- Checkout-EOL-independent source fingerprints for the two cached assets.
- Warning-clean build-asset source under Python 3.14.

## Files / Paths Impacted
- `.github/workflows/python-publish.yml`
- `.gitattributes`
- `src/melder/_build_assets/_agent_documentation/_builder.py`
- `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py`
- `src/melder/_build_assets/_bind_guard/_builder.py`
- `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`
- `src/melder/_build_assets/_system_documents/_builder.py`
- `tests/unit/melder/build_assets/test_build_asset_runner.py`
- `context_compass/attention_board.md`
- This task.

## Validation
- YAML structure and workflow semantic assertions: pass.
- Embedded Python syntax: pass (two heredocs).
- Real wheel/sdist verifier rehearsal: pass.
- Isolated installed-wheel runtime/document smoke: pass.
- Build-asset check and diff hygiene: pass.
- Cross-platform fingerprint regression: pass (`2 passed, 35 deselected`).
- Complete build-assets unit lane: pass (`116 passed`).
- Asset check with `SyntaxWarning` promoted to error: pass (three key matches).

## Risks / Rollback Notes
- A mismatched GitHub environment name breaks PyPI OIDC after all earlier jobs pass.
- A release workflow not present on GitHub's default branch may not receive release events.
- The prod gate intentionally rejects releases for tags not pointing at current prod HEAD.

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
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

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

## Context / Handoff Summary
The tailored workflow is implemented and locally rehearsed. The first promoted
Linux run exposed raw-checkout-byte fingerprints in agent documentation and bind
guard plus one invalid docstring escape. The fingerprints now canonicalize source
line endings, both real builders have regression coverage, manifests are restamped,
and the complete build-assets lane passes. GitHub's default branch must contain the
workflow, and a fresh Linux run after push is the remaining external proof.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
