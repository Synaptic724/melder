# Component patch: CI profiles and source-proof workflow

## Before and after
Before: every promotion PR and dev/preprod/prod push runs the full three-platform suite.
After: PR route determines full runtime/package/source-proof requirements, and CI push triggers
are absent. Manual CI and release-fix PRs deliberately run full qualification.

## Profiles
- dev PR: full runtime, documentation and assets; package build optional as before.
- preprod PR: full runtime, documentation, assets and package build.
- preprod to RC PR: verified prior full preprod tree; heavy jobs skipped.
- RC to prod PR: exact successful candidate proof; heavy jobs skipped.
- release-fix to RC PR: full runtime, documentation, assets and package build.
- manual CI: full qualification for the selected permanent branch.

## Aggregation
Keep explicit slots for every job, including source-qualification. Missing or unknown slots fail.
Every required job must succeed; optional slots may succeed or be explicitly skipped, never fail.
Validate requirement flags against event-derived policy so an absent/malformed flag cannot waive checks.

## Source proof
The reusable verifier reads GitHub metadata, downloads one run/attempt-named artifact through
actions/download-artifact, then validates its record and refreshed run identity. Only full CI
records qualify source; light promotion CI cannot manufacture full-runtime evidence.
RC build/publication depend on successful source-qualification as well as head authorization.

## Publication
The existing Python publisher remains full and repeats its final candidate/tag/prod checks.
No write token or publishing environment is available to source-proof jobs.
