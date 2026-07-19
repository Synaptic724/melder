# Component Patch: Record Contracts

## Before
- descriptor payloads own `profile_name` / `profile_version`
- records have no independent Nexus publication identity

## After
- records own:
  - `nexus_label`
  - `nexus_version`
- current default publication contract is:
  - `default`
  - `0.0.1`
- spell payload detail is represented inside the spell payload body instead of
  being mistaken for dataset identity
