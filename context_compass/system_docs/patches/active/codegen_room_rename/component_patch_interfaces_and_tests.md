# Component Patch: Interfaces And Tests

## Components
- `interfaces.py`
- AR unit tests
- AR canonical docs

## Before
- AR-facing protocols and tests name the final room `dynamic`.
- Tests encode the current room selection and target-frame gating through that
  older name.

## After
- AR-facing protocols and tests use `codegen`.
- Compatibility coverage should ensure legacy AR config inputs still normalize.
- Docs must distinguish:
  - AR room name: `codegen`
  - lower frame/runtime posture: `dynamic`

## Validation Expectation
- AR unit tests pass with the new canonical name.
- At least one compatibility test covers legacy `"dynamic"` room input.
