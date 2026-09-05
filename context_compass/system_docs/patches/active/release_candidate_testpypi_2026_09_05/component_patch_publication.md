# Component patch: production candidate provenance

## Before and after
Before: release-build produces the files sent directly to real PyPI after fresh checks.
After: fresh release validation/build remains mandatory, and real PyPI receives the retained,
TestPyPI-qualified candidate files after a fresh installed-candidate check and identity verification.

## Selection and immutable inputs
At release start, read release_candidate's exact commit/tree and require its tree to match the
selected prod checkout. Read the latest run for that exact commit from release-candidate.yml;
require the expected repository, branch, event, successful completion, and a positive run attempt.
Pin the run ID, attempt, and artifact name as job outputs. Every subsequent download uses them.

## Final gate
Verify candidate.json against the selected run/repository/commit/tree/version and inspect the
distribution contents. Recheck the selected run's successful attempt and live candidate branch.
Then retain the existing release-tag/prod check as the last remote Git identity read before upload.
If candidate, prod, or tag moved, any evidence expired/disappeared, or a rerun changed the selected
attempt, refuse publication. No fallback to another candidate or earlier run happens mid-release.

## Validation
Boundary-mocked tests cover missing/failed/pending/forged runs, changed attempts, head/tree/version
mismatch, missing artifacts, and final guard ordering. Parsed workflow checks preserve fresh runtime,
asset/build dependencies and environment isolation. Actual release publication is not a test.
