# Code Description Patch: Codegen ACL Validation Flow

## Flow
1. `CodegenSystem` resolves `CodegenProjection`
2. compiled access surface carries codegen validation posture
3. `CodegenValidator` parses AST
4. strategies validate imports, builtins, dunder, reflection, and names
5. clean scripts return an accepted validation result
6. execution proceeds only after accepted validation

## Edge Cases
- profiles may deny all imports
- import allowlists and denylists compose by module root
- permissive may allow broader imports while still denying only the most
  obviously dangerous dynamic-code builtins if desired

## Non-Goals
- no full runtime containment
- no AST-based policing of every normal Python construct
