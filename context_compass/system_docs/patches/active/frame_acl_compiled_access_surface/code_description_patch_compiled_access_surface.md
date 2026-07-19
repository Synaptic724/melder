# code_description_patch_compiled_access_surface

## Trigger justification
This slice turns the ACL lane from validated config into effective consumer-facing
output for downstream frame-link/view work.

## Control-flow description
1. typed ACL config is validated
2. compiler reads payload-backed descriptor records plus reusable profiles
3. compiler emits one compiled access surface
4. `FrameLinkContract` is shaped from that effective output

## Validation focus points
- record consumption
- derived access output
- frame-link contract shaping
