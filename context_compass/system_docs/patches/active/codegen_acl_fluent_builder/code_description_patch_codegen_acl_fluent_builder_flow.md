# Code Description Patch: Codegen ACL Fluent Builder Flow

## Control Flow
1. Caller asks the frame container for its stable `FrameACLBuilder`.
2. Caller starts `begin_codegen_change(...)`.
3. Generic builder creates one unlocked codegen draft revision.
4. Generic builder returns `FrameACLCodegenBuilder`.
5. Fluent builder mutates the active draft:
   - profile selection
   - precision profile selection
   - rule helpers
6. Caller commits through the fluent builder.
7. Generic builder installs the final `FrameACLCodegenConfiguration`.

## Error Semantics
- no active draft -> runtime error
- wrong family -> runtime error
- invalid profile/rule names -> fail fast
- empty merge batches -> value error

## Non-Goals
- No second persistence path
- No implicit auto-commit
- No hidden container mutation outside the existing builder lifecycle
