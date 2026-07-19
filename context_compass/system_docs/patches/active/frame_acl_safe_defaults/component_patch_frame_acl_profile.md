# component_patch_frame_acl_profile

## Purpose
Fill the reusable ACL profile catalog with real named profiles and add version
metadata to the profile objects.

## Before
- builder seeds one generic default view/codegen profile
- their rulesets are empty placeholders
- ACL profiles have names but no explicit version metadata

## After
- builder seeds:
  - `safe`
  - `hybrid`
  - `permissive`
  for both view and codegen
- those profiles carry curated non-empty rule content
- ACL profiles expose explicit version metadata
- focused tests assert the named catalog

## Validation Focus
- named profile catalog content
- safe/hybrid/permissive rule ordering
- profile version metadata
