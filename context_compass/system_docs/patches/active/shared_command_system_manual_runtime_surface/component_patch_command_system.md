# Component Patch: CommandSystem

## Before
- shared command vocabulary covered selected-target getters, conduit/spell
  getters, conduit discovery queries, and workstation-target execution
- cloud/topology/manual-runtime operations lived only on lower runtime objects

## After
- base `CommandSystem` owns the shared manual-runtime command vocabulary for:
  - `get_conduit_cloud(...)`
  - `create_lesser_conduit(...)`
  - `create_cluster(...)`
  - `delete_cluster(...)`
  - `join_cluster(...)`
  - `leave_cluster(...)`
  - `list_clusters(...)`
  - `link(...)`
  - `sever_link(...)`
  - `get_links(...)`
- command-surface introspection is explicit through one helper that reports
  supported methods for the current room

## Contract
- shared manual-runtime methods resolve conduits through the existing command
  getter paths instead of inventing a parallel owner path
- query-only methods may remain callable in static when they do not mutate
  runtime topology
- topology-mutation methods are intended to be overridden by room-specific
  command systems when denied
- codegen-only command methods do not belong here
