# Architecture patch: README coverage reporting

- Patch ID: readme_coverage_badges_2026_09_06
- Owner: TASK-2026-09-06-readme-status-badges

## Objective and non-goals
Produce real coverage in existing full test runs and expose it through Codecov and README badges.
Do not create another suite trigger, runtime change, release authority, or coverage threshold.

## Components and interfaces
The standalone test runner accepts an optional coverage XML destination. Runtime CI opts in.
Each matrix leg retains its report; one subsequent reporting job downloads all three and uploads
with CODECOV_TOKEN. CI and final-publication callers pass only that optional repository secret.
The README links the prod coverage history. codecov.yml disables extra status gates and PR comments.

## Invariants
Existing test tiers, exit status, GIL verification, timeouts, stage flags and release proofs remain.
The reporting job runs only after successful tests and not on fork PRs. Its failure is nonblocking.
Only reporting steps receive the Codecov token. No OIDC permission or publishing environment is added.
Coverage badge values come from reports, never a static success percentage.

## Migration and rollback
Implement helper/report outputs, reporting job/caller secret forwarding, config/badges/guide, then tests.
Owner enables Codecov and promotes the changes. A normal final release or manual prod runtime run
seeds the prod badge. Rollback removes reporting and its token forwarding; test gates stay intact.

## Validation
Test optional flags, exact suite/exit/GIL preservation, read-only test jobs, report artifact alignment,
Token isolation, fork refusal, nonblocking upload and unchanged release/source qualification checks.
Hosted Codecov authorization and the first actual coverage percentage require owner rollout.
