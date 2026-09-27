# Architecture patch: Aether conduit lookups say what they cover (2026-09-27)

Patch id: aether_conduit_lookup_api_2026_09_27. Ticket:
tickets/tasks/2026-09-27_implement_aether_conduit_lookup_api_task.md (epic
EPIC-2026-09-27-aether-conduit-lookup-api,
eleven stories). Owner decisions recorded in the epic Notes, 2026-09-27.

## Scope and non-goals
Objective: every Aether conduit lookup states its coverage in its name, and Aether can reach any conduit.
- ROOT coverage keeps today's behaviour under `*_root_*` names.
- `get_conduit_by_name` answers over NAMED scopes (named roots and active named lessers, any depth).
- `get_conduit_by_id` answers over LIVE conduits (roots and every attached lesser, named or anonymous).
- `ConduitCloud.list_conduits()` returns the Cloud's NAMED scopes as objects.
Non-goals:
- No change to named-lesser lifecycle, pooling, Cloud registration or root registration.
- No change to the Nexus/FrameViewer methods that share these names; only their internal id lookups move.
- No cross-frame search; lookups stay frame-scoped.

## Changed components
| component | change | component patch |
| --- | --- | --- |
| Aether Singleton (Global Runtime) | eight renames, two reused lookups, shared frame resolver | component_patch_aether_singleton.md |
| AethericFrame Services (ConduitCloud Registry) | `list_conduits()` | component_patch_aetheric_frame_services.md |
| ConduitWard and Contracts | snapshot ward walk; TransferOfOwnership uses root names | component_patch_conduit_ward_and_contracts.md |
| RiftSpace Workstation And Command Surface | CommandSystem id lookup delegates; StaticCommandSystem uses root names | component_patch_riftspace_workstation_and_command_surface.md |
| AR Runtime Surface (Nexus, Rift, RiftSpace) | StaticFrameViewer owner lookup delegates | component_patch_ar_runtime_surface.md |

## Interface and boundary deltas (Aether; every lookup keeps `aetheric_frame_name: str = "default"`)
| before | after |
| --- | --- |
| `list_conduit_ids` (roots) | `list_root_conduit_ids` |
| `list_conduit_names` (roots) | `list_root_conduit_names` |
| `count_conduits` (roots) | `count_root_conduits` |
| `has_conduit_id` (roots) | `has_root_conduit_id` |
| `has_conduit_name` (roots) | `has_root_conduit_name` |
| `find_conduit_id_by_name` (roots) | `find_root_conduit_id_by_name` |
| `get_conduit_by_name` (roots) | `get_root_conduit_by_name`; `get_conduit_by_name` now NAMED |
| `get_conduit_by_id` (roots) | `get_root_conduit_by_id`; `get_conduit_by_id` now LIVE |
| `_get_conduit_by_name` / `_get_conduit_by_id` | `_get_root_conduit_by_name` / `_get_root_conduit_by_id` |
- Retired from Aether with no alias: the six generic names other than `get_conduit_by_name` / `get_conduit_by_id`.
- Additive: `ConduitCloud.list_conduits() -> Tuple[Conduit, ...]`.
- Error deltas: a non-string `aetheric_frame_name` raises TypeError on all ten lookups (before: a misleading
  ValueError or a raw unhashable-type TypeError); not-found ValueErrors name the searched frame.

## Cross-component invariants
- A name resolves to the same object through `Aether.get_conduit_by_name` and the frame's Cloud.
- For every live root, `get_conduit_by_name(root.name)`, `get_conduit_by_id(root.id)` and the root lookups return
  the same object as before this patch.
- Pooled idle shells and cleaned scopes never resolve; lookups grant no lease and take no lock beyond the Cloud's
  leaf lock (NAMED) or none (LIVE, snapshot walk).
- Frame resolution is `_get_existing_frame`: "default" always resolves (lazy), a custom frame must exist.
- TransferOfOwnership stays ROOT-only (lessers own only the lifecycle of what they create).

## Migration and rollout order
1. ConduitWard snapshot walk and ConduitCloud.list_conduits (additive, no caller change).
2. Aether: frame resolver, renames, reused lookups.
3. Callers: TransferOfOwnership, StaticCommandSystem (root names); CommandSystem, StaticFrameViewer (LIVE).
4. Tests: unit and integration migrations, new regression and contract tests.
5. Canonical docs, indexes, graph, user doc, release note ("Breaking change" bullets), one 0.01 notch.

## Rollback
Revert the change set as one unit; the hard rename leaves no partial state worth keeping.

## Validation and evidence plan
| change | validation |
| --- | --- |
| renames | unit tests on the root family (migrated), retired-name absence test |
| NAMED lookup | integration regression test (automatic and dynamic; nested; retired on return), red on 0.2.78 |
| LIVE lookup | unit (root map, ward delegation, missing) + integration (anonymous and nested lessers) |
| frame resolver | parametrized TypeError test over all ten lookups; not-found message names the frame |
| ward walk | deterministic mutation-during-walk test and deleted-ward skip test |
| callers | existing TransferOfOwnership, Nexus command and viewer suites unchanged and green |

## Ticket coverage map
Epic EPIC-2026-09-27-aether-conduit-lookup-api; eleven stories (eight renames, NAMED lookup, LIVE lookup, Cloud
listing); one implementation task tickets/tasks/2026-09-27_implement_aether_conduit_lookup_api_task.md.

## Unknowns and decision requests
- None open. Asset/LLM-bundle regeneration follows whatever the suites require (recorded in the task).
