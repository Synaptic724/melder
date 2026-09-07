# Architecture patch: qualify once, verify subsequent promotions

- Patch ID: ci_stage_qualification_2026_09_06
- Owner: TASK-2026-09-06-ci-validation-stage-design

## Boundaries
Full source qualification runs for PRs into dev/preprod, release-fix PRs into RC, manual CI and
the unchanged final publication chain. Ordinary ci.yml push triggers are removed. RC keeps its
dedicated branch-push workflow. No source/runtime behavior or publishing credentials change.

## Qualification identity
Full CI publishes a small JSON record only after all required jobs pass. It binds repository,
run ID/attempt, PR or manual event identity, actual checkout SHA/tree and full runtime/package checks.
Promotions compare the exact Git tree, including code, tests, configuration, dependencies and assets.
No mutable branch tip or unrelated successful run qualifies different contents.

## Stage flow
1. Feature to dev and dev to preprod: full matrix and normal checks.
2. Preprod to RC PR: lightweight hygiene and verified full preprod qualification.
3. RC push: current-head authorization, source proof, then existing build/TestPyPI/consumer chain.
4. RC to prod PR: lightweight hygiene and exact successful RC evidence.
5. Final publication: existing fresh full tests, build and final source/tag/prod checks.

## Changed contents and bootstrap
Release-fix PRs qualify their changed RC merge tree fully. Manual CI on the intended permanent branch
provides fresh full evidence when a historical run has no record or artifacts expired. A wrong tree,
missing record or completed failure is never converted into a skipped mandatory check.

## Ordering and timing
The final required CI status remains CI / merge-ready. Skips are accepted only for the validated
profile's optional jobs. Fast prod CI waits a bounded interval for a legitimately pending RC run;
wrong source/repository/workflow and completed failures refuse immediately.

## Rollout and rollback
Promote this change through dev and preprod so the new full-run record exists before lightweight
promotion. Use manual CI to establish evidence for an already-selected branch when needed.
Rollback profile flags, required-result aggregation and proof callers together.

## Validation
Exercise each stage, failed/cancelled/skipped required jobs, identity/tree/attempt mismatch,
old artifacts, unrelated PRs, release-fix qualification, pending wait timeout and final publisher wiring.

## Stable no-GIL compatibility matrix (owner-approved extension)
Read the supported >= major.minor floor from pyproject.toml. Discover released stable versions in
GitHub's official python-versions manifest, choose the latest patch for each qualifying minor and
require free-threaded distributions for Linux x64, Windows x64 and macOS arm64. Refuse missing,
malformed, empty or incomplete discovery. No static fallback and no prerelease qualification.

The shared runtime workflow and RC admission call one discovery helper. Every test/install matrix
job explicitly selects a free-threaded interpreter; runtime checks continue proving GIL-off state.
Build the universal distribution once on a supported free-threaded interpreter selected from
pyproject.toml. Test/coverage/consumer artifacts include the selected Python version to avoid clashes.
Persist each discovery result with the run. Final publication discovers fresh supported runtimes;
historical source-tree qualification remains evidence from its recorded full-CI run.

## Checkout identity correction (PR 147)
Git can report committed CRLF blobs as modified under later text/eol=lf attributes even when
the checkout bytes and mode are identical. A porcelain flag alone is not source mutation proof.
Require the index to match HEAD and inspect raw working-tree deltas. Only unchanged regular-file
mode plus an exact unfiltered blob hash may clear an M delta; real edits and structural changes
remain failures. Do not normalize files, ignore directories or ignore whitespace differences.

## Coverage reporting across partial reruns
GitHub preserves the event SHA/ref across attempts of one run. Coverage may reuse a successful
cell's earlier report within that same run when only another cell is rerun. Select the newest
available report for each exact current OS/Python cell, never another run. Coverage artifacts
are emitted only after successful tests; JUnit remains available for failed tests. This reporting
exception does not relax package/publication artifacts or full-CI proof identity.
