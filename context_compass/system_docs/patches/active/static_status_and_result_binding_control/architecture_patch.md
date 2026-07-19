# Static Status And Result Binding Control Architecture Patch

## Objective
Add the last two static usability refinements:
- spell status/explain helper
- explicit command result-binding reference-mode control

## Non-Goals
- No capability work.
- No broader viewer redesign.
- No batch status work.

## Changed Components
- `StaticCommandSystem`
- `CommandSystem`

## Boundary Contract
- static spell explainability stays on the static command surface
- command result-binding control stays on the base command execution seam
- no room semantics change

## Migration Order
1. add static status helper
2. add command binding override
3. update focused tests
