# Code-description patch: candidate identity and upload ordering

## Candidate path
Interpreter setup runs without a forced GIL-off environment. PYTHON_GIL=0 is applied only when
running runtime tests or installed-package probes after setup, including the shared package builder.

1. Verify the triggering event/ref and checkout commit identify release_candidate in this repository.
2. Reuse the package builder/version checks; full source tests already guard the promotion PR.
3. Record commit/tree/version/run/attempt and the exact built wheel/sdist digest pair.
4. Before TestPyPI upload, recheck branch identity and compare existing remote version files.
   Refuse conflicting names/hashes/sizes; upload only absent files, or verify an identical retry.
5. On all three supported OSes, download the exact TestPyPI wheel using pip with its recorded SHA256,
   install into a fresh environment, and probe imports/assets/runtime lifecycle outside the checkout.
6. Only after all three probes succeed, retain the reports and report candidate-ready.

## Production path
1. Run existing final-release event/checkout/tag/prod authorization.
2. Verify the prod promotion merge's source/tree has successful exact-SHA candidate qualification.
3. Run the existing fresh final source/runtime/package checks and local wheel probe.
4. Enter the existing pypi environment and download this final run attempt's distributions.
5. Repeat candidate qualification/source-tree verification, then the existing live tag/prod guard
   last; only then upload this final run's verified files. Do not rerun the full suite through TestPyPI.

## Failure and rollback semantics
Untrusted event/JSON/filename data is never interpolated into shell commands. Git/process/network
operations use explicit argument vectors and fixed service hosts. Every boundary is fail-closed;
no absent-evidence default, silent version rewrite, blind skip-existing, or fallback artifact source.
Network retries are bounded and only for index propagation/transient reads, not failed package tests.

## Non-goals
No automatic candidate movement, no candidate version rewrite, and no release scheduler in this slice.
