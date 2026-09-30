# component_patch_root_configurations

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-29T23:43:57Z

<!-- BEGIN ENTRY: "Root configurations: value snapshot" -->
## Before
- Aether, Crystallizer, MutationResearch and Nexus configurations keep their values in a private `_properties`
  map; the only public reads are per-key (`get_property`, typed properties). A host comparing two policies (MelderOps)
  called `get_configuration_dictionary()`, which none of them define, and crashed.

## After
- Each exposes `get_configuration_dictionary() -> Dict[str, object]`: under its configuration lock, a new dict of
  the properties currently present, values by reference. Raises RuntimeError when cleaned. Does not validate,
  freeze or emit.

## Validation Expectations
- Snapshot equals the values set; mutating the returned dict does not change the configuration; two policies built
  the same way compare equal and differ after one setter; cleaned configuration raises.
<!-- END ENTRY: "Root configurations: value snapshot" -->
