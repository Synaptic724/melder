# Code-description patch: candidate identity and upload ordering

## Candidate path
1. Verify the triggering event/ref and checkout commit identify release_candidate in this repository.
2. Run the existing shared CI including package/version checks.
3. Record commit/tree/version/run/attempt and the exact built wheel/sdist digest pair.
4. Before TestPyPI upload, recheck branch identity and compare existing remote version files.
   Refuse conflicting names/hashes/sizes; upload only absent files, or verify an identical retry.
5. On both supported OSes, download the exact TestPyPI wheel using pip with its recorded SHA256,
   install into a fresh environment, and probe imports/assets/runtime lifecycle outside the checkout.
6. Only after both probes succeed, retain the complete qualified artifact and report candidate-ready.

## Production path
1. Run existing final-release event/checkout/tag/prod authorization.
2. Select one trusted successful candidate run for the matching current candidate commit/tree.
3. Download and validate its exact attempt's qualified artifact; preserve selection as outputs.
4. Run fresh final source/runtime/package checks and another candidate installation probe.
5. Enter the existing pypi environment. Download the pinned qualified artifact again.
6. Validate its record/distributions and current candidate run/branch; run the existing live tag/prod
   guard last; only then upload the retained candidate files to real PyPI.

## Failure and rollback semantics
Untrusted event/JSON/filename data is never interpolated into shell commands. Git/process/network
operations use explicit argument vectors and fixed service hosts. Every boundary is fail-closed;
no absent-evidence default, silent version rewrite, blind skip-existing, or fallback artifact source.
Network retries are bounded and only for index propagation/transient reads, not failed package tests.

## Non-goals
No automatic candidate movement, no candidate version rewrite, and no release scheduler in this slice.
