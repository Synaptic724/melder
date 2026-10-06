# architecture_patch

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-30T00:19:44Z

## Patch Scope and Non-Goals
- Objective: a host that embeds Melder next to another Melder user (MelderOps) gets honest root configuration: a
  spell-id regime that cannot be misreported, a live Nexus that cannot be reconfigured under its Rifts, a refused
  dynamic conjure that leaves its frame untouched, and a public value snapshot of each root configuration so
  policies can be compared without private access.
- Non-goals: other failures after conjure settlement (validation errors, bad policy strings) still leave the
  frame settled, as today; Crystallizer activation still records nothing that already exists (no world walk, by
  design); Crystallizer and MutationResearch guards are unchanged (they already refuse while active).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Aether Singleton (Global Runtime) | modify | configure/activate installed a regime that was not in force | none |
| Crystallizer Root, Persistence Record, And Module-World Surfaces | modify (stage 4 only) | stage 1 unchanged (the record never carries the regime); stage 4 must deactivate an active Nexus under M2 | Aether, Nexus |
| AR Runtime Surface (Nexus, Rift, RiftSpace) | modify | a live Nexus accepted a replacement policy | none |
| Spellbook Core (Binding and Conjure) | modify | a refused dynamic conjure settled the frame first | none |
| Aether Root Configuration Assembly (and the Crystallizer, MutationResearch, Nexus configurations) | modify | no public read of a policy's values | none |

## Interface and Boundary Deltas
- Additions: `get_configuration_dictionary() -> Dict[str, object]` on AetherConfiguration, CrystallizerConfiguration,
  MutationResearchConfiguration and NexusConfiguration.
- New refusals (RuntimeError): `Aether.configure` / `Aether.activate` with a configuration whose
  `process_wide_unique_spell_ids` differs from the sealed regime while any frame exists; `Nexus.configure`, and
  `Nexus.activate(configuration)` with another object, while Nexus is active.
- Changed ordering: `Spellbook.conjure` refuses the active-Crystallizer configuration discipline before settling
  frame posture (same message, same exception type).
- Restore stage 1: unchanged (the recorded root configuration never carries the regime, so it always matches a
  live Aether that stage 1 configures; see component_patch_crystallizer_restore.md).
- Restore stage 4: deactivates an active live Nexus before activating the reloaded configuration, as stage 3 does
  for MutationResearch.

## Cross-Component Invariants
- While any frame exists, the installed Aether configuration's `process_wide_unique_spell_ids` equals the regime
  in force (sealed at the first frame). Before the first frame, any regime may be installed.
- A root that is active keeps its installed policy object: Crystallizer, MutationResearch and now Nexus refuse
  replacement until deactivated.
- A conjure refused by a precondition that does not depend on compilation has no posture side effect.
- `get_configuration_dictionary()` is a lock-guarded snapshot of present properties; values are borrowed (loggers
  and resolvers by reference), never serialized or copied deeply; it never freezes or validates.

## Migration Order
1. M4 value snapshots (pure additions). 2. M1 Aether guard plus restore stage 1. 3. M2 Nexus guard. 4. M3 conjure
ordering. One notch each at landing (0.2.8209-0.2.8212).

## Rollback
Each fix is independent: revert its hunk and its tests. M4 has no dependants inside Melder; MelderOps' F1 needs it.

## Ticket Coverage Matrix
| patch section | ticket |
|---|---|
| all | tickets/tasks/2026-09-29_guard_melder_roots_for_host_collisions_task.md |
