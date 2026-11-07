# Frame posture serialization order

<!-- BEGIN ENTRY: "Project SystemState before primitive strings" -->
## Control flow
When an activated dynamic frame freezes with a frame name, its existing snapshot loop
first recognizes SystemState and writes .name as a plain string. Other primitive values
and None retain the existing pass-through; other objects retain existing str conversion.
The emit gate, lock release before emission, ordering and exception behavior stay.

## Validation
Use a real activated recorder to inspect the emitted twin before serialization and a
real checkpoint/replay to check plain stored names. Test automatic and dynamic gates,
including ownership transfer, and retain old numeric/pickle input compatibility.
<!-- END ENTRY: "Project SystemState before primitive strings" -->