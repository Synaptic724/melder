# Component Patch: Finishing Examples

## Component Purpose and Boundary in Current Architecture
This slice adds the role-local example pack for `synaptic_finishing_developer`
and makes those examples mandatory baseline reads.

## Before/After Behavior Summary
Before:
- the role referenced only its skill docs
- the only nearby examples were the lighter `synaptic_python_developer`
  examples

After:
- the role owns a dedicated example pack
- the role `SKILLS.MD` lists those examples as mandatory baseline reads
- the examples model richer public-library docstrings, comments, and tests

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - role-local examples under `examples/python/`
- Outputs:
  - richer baseline role examples
  - baseline `SKILLS.MD` entries for example reads
- Error semantics:
  - none beyond onboarding drift if the examples are listed incorrectly

## State and Lifecycle Deltas
- add a new example folder under the role
- add example paths to role `SKILLS.MD`

## Dependency and Ordering Constraints
- examples should reflect the role-local documentation and testing skills
- examples should be more detailed than the source synaptic examples

## Validation Expectations
- example files exist
- `SKILLS.MD` lists them as active skills
- example content is richer than the borrowed synaptic examples

## Unknowns and Open Decisions
- UNKNOWN: whether the role should later add markdown walkthrough examples in
  addition to Python examples
