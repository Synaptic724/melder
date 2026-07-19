# Component Patch: Capability And Static Command Systems

## CapabilityCommandSystem

### Before
Nominal shell over `CommandSystem` with no meaningful room-owned public methods.

### After
Owns the broad manual-runtime room commands moved out of the base:
- topology mutation
- cluster operations
- direct `meld(...)`
- reuse-only `meld_existing_spell(...)`

Capability supported-method discovery should append these room-owned methods to
the shared base list.

## StaticCommandSystem

### Before
Inherited topology mutation and direct `meld(...)` from the base, then denied
them through deny lists and filtered them out of discovery.

### After
No longer inherits those moved capability-only methods.
Owns only static-safe spell access and status helpers directly, including:
- `get_spell_by_source_id(...)`
- `get_spell_by_index_id(...)`
- `get_spell_by_id(...)`
- `meld_existing_spell(...)`
- `describe_spell_status_by_source_id(...)`
- `describe_spell_status_by_id(...)`
- `describe_spell_status_by_index_id(...)`

Static supported-method discovery should reflect the true room-owned surface
without deny-list subtraction for moved methods.

## Validation Expectations
- Capability tests still prove topology/activation helpers exist and work there.
- Static tests prove moved capability-only helpers are absent and static-specific
  methods remain available.
