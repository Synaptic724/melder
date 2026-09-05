# Component patch: CI validation

## Purpose and boundary
Validate a proposed merge or permanent-branch revision using reusable, read-only checks.

## Before and after
Before: source/repository asset workflows overlap push and PR events, support disabling checks, and
provide no runtime test gate. After: ci.yml owns triggering and aggregates explicit mandatory results.

## Interface deltas
- workflow_call for source assets, repository assets, runtime matrix, and distribution validation.
- CLI accepts explicit event metadata as data, never interpolated shell code.
- Named merge-ready status remains stable regardless of the number of matrix jobs.
- dev accepts feature work and same-repository synchronization. preprod requires same-repo dev;
  prod initially requires same-repo preprod. Dated candidate routing is a later explicit extension.

## State and lifecycle
No persistent runtime resources. Cancel superseded CI runs by PR/ref. Reusable workflows must not
share a concurrency key that cancels their caller or a final release run.

## Failure semantics
Missing JSON fields/results, invalid branch routes, failed/cancelled/timed-out/skipped mandatory jobs,
unsupported runtime, or stale assets fail closed. A package job may skip only for the dev stage.

## Dependencies and ordering
Independent checks run concurrently. merge-ready waits for all required results and evaluates them
even when a dependency fails. Package checks are mandatory for preprod/prod candidates.

## Validation expectations
Test the route/result truth tables, helper CLI exit codes, matrix and permissions wiring, and the
existing repository-builder workflow contract. Run unit/component/integration with Python 3.14t.

## Unknowns
Ruff/mypy baseline cleanliness remains outside initial hard enforcement.
