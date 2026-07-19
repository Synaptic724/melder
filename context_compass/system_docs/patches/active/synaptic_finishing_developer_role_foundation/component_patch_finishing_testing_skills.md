# Component Patch: Finishing Testing Skills

## Component Purpose and Boundary in Current Architecture
This slice defines the testing-family skills for the new role. Its focus is
deep contract testing that supports high-value docstrings and comments:
unit, component, integration, mocking, regression, and truthful reporting.

## Before/After Behavior Summary
Before:
- current synaptic testing docs cover pytest, unit/integration, mocking,
  regression, and evidence reporting
- QA layer covers broader strategy and release posture
- no role combines system-aware documentation depth with equally deliberate
  unit/component/integration finishing guidance

After:
- the new role has a testing family dedicated to deep contract coverage
- component tests are made explicit
- unit/component/integration boundaries are described from a finishing-role view

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - current role-local testing docs
  - QA strategy docs
  - documentation/test-alignment expectations
- Outputs:
  - deeper testing skill guidance for the new role
- Error semantics:
  - role should report `Not run.` when validation did not actually execute

## State and Lifecycle Deltas
- add new role-local testing skill docs under `skills/testing/`

## Dependency and Ordering Constraints
- testing skills must stay aligned to the role’s documentation mission
- component tests should be distinct from unit and integration guidance

## Validation Expectations
- testing docs explicitly cover:
  - unit tests
  - component tests
  - integration tests
  - mocking
  - regression
  - truthful evidence reporting

## Unknowns and Open Decisions
- UNKNOWN: whether this role should later own performance-test guidance or stay
  limited to documentation-aligned contract testing
