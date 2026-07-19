# code_description_patch_frame_acl_validator

## Trigger justification
This slice changes ACL validation semantics from frame-name-only checks to
typed configuration/rule-aware checks.

## Control-flow description
1. validate root config type and frame ownership
2. validate typed view/codegen child objects
3. validate ruleset operations against allowed operation families
4. validate supported spell payload floor values
5. record successful validation id

## Validation focus points
- operation-family mismatch errors
- invalid payload floor errors
- successful typed config validation
