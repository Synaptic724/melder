# Component patch: final release publication

## Purpose and boundary
Publish only a freshly qualified current-prod revision after verifying the produced distributions.

## Before and after
Before: the head check occurs once, followed by inline tests/build and publication. After: shared
checks still execute afresh for every release, and the publishing job rechecks prod after any
environment approval and immediately before upload. Early branch CI never substitutes for this run.

## Interface deltas
The build workflow accepts a release-tag string for version agreement and returns same-run build
artifacts. Release events and manual prod dispatch remain the publication entrypoints. Prerelease
events must not silently become final-release publication.

## State and lifecycle
Serialize publication across tags/manual dispatches. Retain immutable run artifacts. Package
archive readers and smoke-test environments must close/exit explicitly through context management.

## Failure semantics
Reject changed prod, mismatched checkout/tag/package versions, missing/tampered/unsafe package
members, unexpected distribution counts, failed runtime tests, and unsuccessful validation jobs.
No upload happens after a failed guard. Do not use skip-existing to conceal a mismatched package.

## Dependencies and ordering
Initial prod authorization -> fresh shared validation -> build and install verification ->
publication environment -> retrieve artifacts -> repeat distribution/prod checks -> PyPI upload.

## Validation expectations
Tests prove stale-prod refusal, tag/version agreement, archive boundaries, and fresh dependency
wiring. Build and smoke-test a real local wheel; do not dispatch publication as validation.

## Unknowns
A multi-day candidate schedule will need deliberate artifact retention and candidate metadata later.
