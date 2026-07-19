# Component Patch: ACL Profiles

## Before
- reusable base profiles exist only for:
  - view
  - codegen
- command has config objects but no real reusable profile family
- precision intent exists only as design, not as reusable profile assets
- rules and rulesets were previously flatter and easier to smear across layers

## After
- reusable base profiles exist for:
  - view
  - command
  - codegen
- each family also exposes a reusable `precision.py` profile asset
- shared rule primitives stay under `configurations/profiles/rules/`
- profile builder resolves:
  - base profiles
  - precision profiles

## Interface Deltas
- configs carry:
  - `profile_name/profile_version`
  - `precision_profile_name/precision_profile_version`
- profile builder grows:
  - command registries
  - precision registries for all three families

## State / Failure Deltas
- unknown base or precision profile names fail fast through the profile builder
- no new top-level selection dimension is introduced for Rift/Nexus
