# architecture_patch

## Metadata
- Patch ID: aethericrift_v1_workspace_runtime
- Status: draft
- Owner: codex
- Created: 2026-03-15T10:38:58Z
- Updated: 2026-03-15T10:38:58Z

## Patch Scope and Non-Goals
- Objective:
  Define the architecture delta required to build AethericRift v1 from the
  current agreed model: hidden-Aether substrate, public `Nexus` singleton
  entry, live `Rift` objects owning their immediate runtime state, AR-local
  Spellbook, root conduit, base `RiftSpace`, concrete `StaticRiftSpace` /
  `DynamicRiftSpace`, `RiftConfiguration`, target registries
  (`RiftAttribute` / `RiftMethod`), `RiftValidationSystem`, and
  static/dynamic room behavior.
- Non-goals:
  - MutationResearch implementation itself
  - transport/server adapters
  - stale February object model compatibility guarantees

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| aetheric_rift_core | add/modify | establish the public `Nexus` root, live Rift runtime object, and local substrate ownership | none |
| frame_examiner | add/modify | define the inspection/gathering tool used to populate room exposure from a configured frame | aetheric_rift_core |
| rift_space | add/modify | define the base room plus `StaticRiftSpace` / `DynamicRiftSpace` used by the operator | aetheric_rift_core |
| rift_targets | add/modify | define named workspace targets as `RiftAttribute` and `RiftMethod` | rift_space |
| rift_profiles | add/modify | align the profile stack to the current AR language | aetheric_rift_core |
| rift_validation_system | add/modify | parse, validate, and classify codegen against the workspace target model | rift_space |

## Interface and Boundary Deltas
- Boundary delta 1:
  `Aether` is hidden substrate and private host only, while `Nexus` is the
  public singleton root for Rift-domain behavior and `Rift` is the per-instance
  runtime object that owns one AR-local Spellbook and one root conduit as its
  local workspace substrate after activation.
- Boundary delta 1a:
  `Nexus` owns frame-name assignment policy for internal AR system frames, while
  each live Rift separately exposes one configured target frame by default.
- Boundary delta 1b:
  If direct live-Rift retrieval is exposed at all, it should be a
  system-governed/token-gated path mediated by `Nexus`, not a convenience
  getter on `Aether`.
- Boundary delta 2:
  `RiftSpace` is the operator-facing room and the normal place where work
  happens. “Workstation” behavior is facaded through the space rather than
  represented as a separate primary owning object.
- Boundary delta 3:
  The active workspace target model is `RiftAttribute` / `RiftMethod`, not the
  older `RefAttr` / `RefMethod` or an `ObjectRef`-centric model.
- Boundary delta 4:
  `StaticRiftSpace` means declared-target operation without conduit-backed local
  construction. `DynamicRiftSpace` means the root conduit can be used to
  materialize local helpers/objects/tools.
- Boundary delta 5:
  Frame-scoped services such as `ConduitCloud`, `MutationResearch`, and
  `DevOpsManager` remain owned by `AethericFrame`; AR may rely on them or
  surface their posture through profiles, but should not duplicate them as
  parallel AR manager layers.
- Boundary delta 6:
  `RiftConfiguration` selects which frame is exposed by default; the Rift then
  exposes conduits and other allowed objects from that frame into the room,
  while profiles decide what part of that exposed surface is visible/usable.
- Boundary delta 7:
  `FrameExaminer` is the read/inspection layer that gathers configured-frame
  conduits, services, and profile truth for the RiftSystem. Session/token
  behavior should stay in a narrow request-guard layer owned by the system.
- Boundary delta 8:
  `Aether` should stay out of the public Rift workflow and provide only the
  hidden substrate helpers such as configured-frame conduit enumeration
  (`_get_conduits_by_frame(...)`) for lower layers that need them.

## Cross-Component Invariants
- Invariant 1:
  Every room surface has one root conduit backing it, even in static mode.
- Invariant 2:
  The root conduit is hidden as a construction instrument in `StaticRiftSpace`
  and surfaced in `DynamicRiftSpace`.
- Invariant 3:
  Local workspace construction is not canonical mutation by default.
- Invariant 4:
  MutationResearch begins only when the work crosses into canonical iteration on
  durable runtime structure.
- Invariant 5:
  Workspace target registries are the declared target universe for AST/member
  validation.
- Invariant 6:
  AR reuses Melder's existing Spellbook/conduit lifecycle rather than inventing
  a second substrate lifecycle for room construction.
- Invariant 7:
  Frame targeting is configuration-driven and should not require a separate AR
  frame-scope subsystem.
- Invariant 8:
  Public Rift objects own the immediate runtime state they need; a separate
  public `RiftState` object is not required unless true persistence or
  rehydration later demands it.
- Invariant 9:
  Moving into `DynamicRiftSpace` should be modeled as a new Rift build/config
  path, not an in-place semantic mutation of a live static room.
- Invariant 10:
  `Aether` may privately host the Nexus singleton at boot, but public Rift
  ownership and access remain in `Nexus`, not in `Aether`.

## Migration and Rollout Order
1. Build `Nexus` as the public singleton root while keeping `Aether` hidden as
   substrate host.
2. Build `Rift` core ownership of local Spellbook + root conduit.
3. Build the `RiftSpace` base plus `StaticRiftSpace` target registries and
   cleanup model.
4. Build `RiftValidationSystem` against the declared target model.
5. Build profile objects and profile aggregation needed for exposure behavior.
6. Expose `StaticRiftSpace` first.
7. Expose `DynamicRiftSpace` local-construction path second.

## Rollback Strategy
- Rollback trigger:
  The AR implementation drifts back into the stale February object model or
  conflates local workspace construction with canonical mutation.
- Rollback steps:
  1. Re-read the long-form unified architecture ticket.
  2. Re-check the active top-level AR object set.
  3. Correct implementation docs before code continues.
- Post-rollback verification:
  The object language in implementation tasks matches the long-form AR ticket.

## Validation Expectations and Evidence Plan
- Validation item 1:
  Confirm the implemented object set matches the active top-level AR folder.
- Evidence source 1:
  top-level AR object docs plus unified architecture ticket
- Validation item 2:
  Confirm `simple` and `dynamic` semantics remain concretely different.
- Evidence source 2:
  `RiftSpace`, `RiftConfiguration`, and `RiftValidationSystem` docs
- Validation item 3:
  Confirm local workspace construction and canonical mutation remain separate
  concepts.
- Evidence source 3:
  unified architecture ticket and MutationResearch working model

## Ticket Coverage Map
- Epic:
  EPIC-2026-02-18-aethericrift-discovery-design
- Story:
  STORY-2026-02-25-aethericrift-implementation
- Tasks:
  TASK-2026-03-15-define-aethericrift-v1-patch-handoff

## Unknowns and Decision Requests
- UNKNOWN:
  Whether `RiftConduit` should remain a concrete wrapper object or just a
  workspace-facing reference/metadata layer over the real root conduit.
- UNKNOWN:
  How much session/occupancy state needs to be first-class in v1 versus left as
  future expansion.
- DECISION_REQUEST:
  None at the architecture boundary right now; the current patch scope is
  coherent enough to proceed into engineer handoff.

## Context / Handoff Summary
- What changed:
  The patch formalizes the currently settled AR v1 object model and mode split.
- What remains:
  MutationResearch implementation and stale February artifact rewrites remain
  outside this patch set.
- Next entrypoint:
  component patch docs for the AR core pieces.
