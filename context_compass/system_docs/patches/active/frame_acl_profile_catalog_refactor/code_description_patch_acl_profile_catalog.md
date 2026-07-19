# code_description_patch_acl_profile_catalog

## Trigger justification
This slice reorganizes the reusable ACL profile catalog so the profile ladder is
explicit and inspectable.

## Control-flow description
1. manager-owned builder still seeds the same named profile ladder
2. named profile modules become explicit
3. rules/rulesets remain object-based and reusable
4. focused ACL profile tests validate the new package layout

## Validation focus points
- package/module layout
- named profile visibility
- import rewiring
