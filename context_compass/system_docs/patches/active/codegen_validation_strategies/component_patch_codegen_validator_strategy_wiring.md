# Component Patch: Codegen Validator Strategy Wiring

## Before
- `CodegenValidator` is a syntax-only object.
- Strategy tasks are staged but unused.

## After
- `CodegenValidator` owns the strategy family and runs it in order:
  1. syntax parse
  2. AST structure
  3. import policy
  4. builtins policy
  5. name resolution
  6. attribute access
- First failing rule returns a validation result immediately.

## Validation Expectations
- Existing syntax failure tests stay green.
- New validator policy tests prove each rule family is live.

