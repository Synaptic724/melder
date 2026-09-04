# Code-description patch: CI and release gate flow

## Trigger justification
The change introduces branch policy and dependency-result gates, plus a publication ordering guard.

## Control flow
1. Read event payload from GITHUB_EVENT_PATH. Validate expected event/base/source repository fields.
2. For a PR, apply its base-specific route. For pushes/manual CI, require a supported permanent ref.
3. Emit whether the package gate is mandatory for this event.
4. Run independent reusable checks against the event checkout.
5. Evaluate the needs result map: every fixed mandatory job must be success. Packages must be success
   when required, otherwise success or intentionally skipped. Malformed/missing state fails.
6. For publication, require the selected event commit and checkout to equal fetched prod at entry.
7. Execute fresh checks and build; do not reuse a historical dev/preprod success as a substitute.
8. After publication environment admission, verify downloaded distributions and repeat the prod
   equality check as the last local step before upload.

## Edge/error and rollback semantics
Treat all metadata as input data. Unsupported routes/events fail; never silently default a package
requirement or release ref. A failed check reports diagnostics and nonzero exit. Failed artifact
qualification never reaches the upload action. Rollback is a coordinated caller/helper change.

## Invariants and idempotency
Read-only checks are repeatable; no helper rewrites assets or branches. Success aggregation requires
complete evidence rather than absence of an error. Concurrent CI cannot cancel a publication run.

## Non-goals
No automatic branch merging, actual package publication, or dated release creation in this foundation.

## Validation focus
Table-driven negative cases for missing/invalid metadata, wrong-repository dev heads, wrong branch
routes, every unsuccessful job result, intentional versus accidental package skips, and stale prod.
