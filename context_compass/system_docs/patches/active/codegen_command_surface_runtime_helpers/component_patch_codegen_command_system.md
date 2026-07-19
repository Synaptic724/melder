# Component Patch: CodegenCommandSystem

## Before
`CodegenCommandSystem` owned only:
- `validate_codegen(...)`
- `execute_codegen(...)`

and otherwise exposed whatever happened to live on the shared base.

## After
`CodegenCommandSystem` explicitly owns the selected slim helper set:
- conduit lookup/discovery:
  - `get_conduit_cloud`
  - `get_conduit_by_id`
  - `get_conduit_by_name`
  - `list_conduit_ids`
  - `list_conduit_names`
  - `count_conduits`
  - `find_conduit_id_by_name`
- limited runtime/contract helpers:
  - `list_clusters`
  - `get_links`
  - `get_contracted_conduits`
  - `get_spell_in_contracts`
  - `get_spells_in_contract_by_conduit_name`
  - `describe_spells_in_conduit`
  - `find_spell_id`
  - `find_spell_key`
  - `get_spell_permissions`
- target helpers:
  - `get_target_attribute`
  - `get_target_method`
  - `execute_target_method`
- codegen placeholders:
  - `validate_codegen`
  - `execute_codegen`

## Validation Expectations
- `list_supported_command_methods()` exposes exactly the selected helper set
  plus the two codegen placeholders.
- Focused codegen tests cover the selected helper names and the placeholder
  behavior.
