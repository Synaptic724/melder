# component_patch_aetheric_rift_core

## Component purpose and boundary in current architecture
`Nexus` is the public singleton owner of Rift registration, configuration, and
process-wide Rift policy. `Rift` is the top-level AR runtime/control object
created through `Nexus`. `Aether` remains hidden substrate and private host
only, while each live Rift owns the AR-local Spellbook, the root conduit, the
`RiftConfiguration`, the `RiftValidationSystem`, and active `RiftSpace`
instances.

## Before/after behavior summary
- Before:
  The active design had drift between an older Aether facade + separate
  state-shell split and the newer model where the Rift owns its local runtime
  state directly.
- After:
  `Nexus` owns registration/config/lifecycle policy and `Rift` becomes the live
  public object that owns the runtime state it actually needs, while still
  owning the local AR runtime substrate once activated.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  creation through `Nexus`, configuration inputs, workspace creation requests
- Outputs:
  `RiftSpace` instances, introspection/config state, root-conduit-backed
  runtime entry, and lazy-bound live Rift activation from shell state
- Error semantics:
  invalid configuration or impossible local substrate setup should fail early
  during Rift initialization

Concrete hidden substrate APIs to prefer:
- `Aether._ensure_frame(...)`
- `Aether._get_configuration(...)`
- `Aether._bind_configuration(...)`
- `Aether._add_conduit(...)`
- `Aether._get_conduits_by_frame(...)`
- `Aether._get_conduit_cloud(...)`
- `Aether._get_conduit_by_name(...)`
- `Aether._get_conduit_by_id(...)`

## State and lifecycle deltas
- Owns AR-local Spellbook
- Owns root conduit
- Owns active workspaces
- Owns the immediate runtime/config/frame-assignment state it needs
- Depends on `Nexus` for canonical Rift registration and any
  privileged direct live-Rift retrieval policy
- Depends on `Nexus` for session/request-guard state as well
- Depends on the AR system-frame names assigned by `Nexus`
- Reuses the normal Melder Spellbook/conjure/conduit lifecycle rather than
  inventing a second AR-only substrate lifecycle
- Closing the Rift should cleanup its local workspaces and substrate-owned local
  room machinery without pretending to own broader user runtime truth

## Failure mode deltas
- Misconfigured root substrate creation makes the Rift unusable at startup
- Stale object-language assumptions in implementation would corrupt later
  workspace semantics

## Dependency and ordering constraints
- Must exist before `RiftSpace`
- `Nexus` must exist before a public Rift can be created
- The assigned AR system-frame names must exist before a live Rift can attach
  its local substrate state
- Must establish local Spellbook and root conduit before dynamic local
  construction can work
- Must sit under `Nexus` public management while still using hidden `Aether`
  substrate services

## Validation expectations
- The implemented object should align with the top-level AR object docs
- The Rift should own its local substrate explicitly
- The Rift should own its own live runtime state rather than depend on a
  separate public state object
- The implementation should prefer the hidden `Aether` accessor surface over
  direct frame-internals reach-through
- `Aether` should not expose an ungated bypass getter that hands out live Rifts
  or publicly act as the Rift-domain root
- `_get_conduits_by_frame(...)` should be treated as a required substrate helper
  for configured-frame conduit exposure
- If persistence is later required, it should be added as a private record layer
  under `Nexus`, not as a separate public Rift-state object
- Token-gated activation should still activate the same public Rift type rather
  than forking a separate runtime object class
- Token names should be explicit:
  - `AethericRiftCreationToken`
  - `AethericRiftToken`

## Unknowns and open decisions
- Whether the Rift itself exposes small operator helpers directly versus
  delegating everything to `RiftSpace`
