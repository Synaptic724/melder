# code_description_patch_default_acl_profiles

## Trigger justification
This slice changes the meaning of the seeded default ACL profiles. They stop
being empty placeholders and become the first real safe baseline.

## Control-flow description
1. reusable ACL profile builder seeds default view/codegen profiles
2. default profiles construct curated restrictive rulesets
3. focused ACL profile tests assert the seeded safe defaults

## Validation focus points
- default profile seeding
- safe rule content
- version metadata
