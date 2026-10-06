# component_patch_nexus_root

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-30T00:19:44Z

<!-- BEGIN ENTRY: "Nexus: no reconfiguration while active" -->
## Before
- `Nexus.configure` replaces the installed configuration under the Nexus lock with no active check; the live Nexus
  then reads the replacement (unfrozen) at every Rift validation. `activate(configuration)` replaces it too.
  EVIDENCE: src/melder/nexus/nexus.py:803-878.

## After
- Both refuse with RuntimeError while Nexus is active ("Cannot reconfigure Nexus while it is active. Deactivate it
  first."), matching Crystallizer and MutationResearch. `activate(configuration)` with the installed object, or
  `activate()` with none, is unchanged. Deactivated Nexus accepts a new configuration as before.
- The refusal compares identity: a second object with equal values is still a replacement.
- The only src caller of either verb, restore stage 4, deactivates an active Nexus first (see
  component_patch_crystallizer_restore.md, "RestoreEngine stage 4: active live Nexus"). Two unit tests that
  re-activated the live singleton with another policy as setup deactivate it first.

## Validation Expectations
- configure on an active Nexus raises and keeps the installed policy; after deactivate it succeeds; activate with
  a different configuration while active raises; activate with the installed configuration while active succeeds.
<!-- END ENTRY: "Nexus: no reconfiguration while active" -->
