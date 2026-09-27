# Component patch: RiftSpace Workstation And Command Surface - conduit id lookups (2026-09-27)

## Before
- `CommandSystem._get_conduit_by_id_locked` tried Aether's root lookup, then walked every root ward itself.
- `StaticCommandSystem` resolved spell owners through Aether's private `_get_conduit_by_id`.

## After
- CommandSystem: after its ACL gates, `Aether.get_conduit_by_id` (LIVE); on ValueError it keeps its messages:
  `_get_required_runtime_frame` for a missing frame, then "Conduit id 'I' was not found in frame 'F'.".
- StaticCommandSystem: `Aether.get_root_conduit_by_id` (owners are roots), same behaviour.

## Interface / state / failure deltas
- None visible to Rift callers; ACL gating and messages are unchanged.

## Validation expectations
- Named-lesser Nexus command tests and command-system suites green unchanged.
