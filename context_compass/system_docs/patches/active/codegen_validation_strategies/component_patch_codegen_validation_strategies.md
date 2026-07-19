# Component Patch: Codegen Validation Strategies

## Before
- `CodegenValidator` only performs AST parse.
- No strategy files exist.
- Any valid syntax returns the not-implemented validation result.

## After
- Strategy files exist for:
  - AST structure
  - import policy
  - builtins policy
  - name resolution
  - attribute access
- `CodegenValidator` composes those strategies after AST parse.
- Concrete validation failures now surface through the validation result.

## Validation Expectations
- Syntax-invalid code fails first.
- Import statements fail.
- banned builtin usage fails.
- unknown namespace names fail.
- disallowed attribute access patterns fail.

