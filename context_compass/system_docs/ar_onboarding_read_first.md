# AR Onboarding Read First

## Purpose
This note is the shortest high-signal path back into the current AR runtime.
It exists because the AR lane now spans live code, canonical docs, retained
artifacts, and active tickets, and fresh onboarding should not have to
reconstruct that path from scratch.

## Read Order
1. [src_architecture.md](/<local-workspace>/codex/context_compass/system_docs/src_architecture.md)
   Read the C4 runtime story first.
2. [src_components.md](/<local-workspace>/codex/context_compass/system_docs/src_components.md)
   Read the concrete manager, room, workstation, and command surfaces next.
3. [readable_src_graph.json](/<local-workspace>/codex/context_compass/system_docs/readable_src_graph.json)
   Read the source wiring and ownership surface next.
4. [tests_architecture.md](/<local-workspace>/codex/context_compass/system_docs/tests_architecture.md)
   Read how the test tiers are organized.
5. [tests_components.md](/<local-workspace>/codex/context_compass/system_docs/tests_components.md)
   Read the shared harnesses and the static/capability Rift benches.
6. [attention_board.md](/<local-workspace>/codex/context_compass/attention_board.md)
   Read the current active lane and recently closed anchors.

## Key AR Epics
- [2026-04-10_rift_access_modes_static_capability_dynamic_epic.md](/<local-workspace>/codex/context_compass/tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md)
  Umbrella room-mode lane.
- [2026-04-11_precision_acl_targets_and_spell_access_epic.md](/<local-workspace>/codex/context_compass/tickets/epics/2026-04-11_precision_acl_targets_and_spell_access_epic.md)
  Precision ACL direction for viewer and command.
- [2026-04-12_capability_rift_space_runtime_model_epic.md](/<local-workspace>/codex/context_compass/tickets/epics/2026-04-12_capability_rift_space_runtime_model_epic.md)
  Capability room semantics.
- [2026-04-12_static_rift_integration_testbench_epic.md](/<local-workspace>/codex/context_compass/tickets/epics/2026-04-12_static_rift_integration_testbench_epic.md)
  Static-room integration depth.

## Key AR Artifacts
- [2026-04-12_capability_rift_space_runtime_model.md](/<local-workspace>/codex/context_compass/tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md)
  Current capability-room truth.
- [2026-04-11_precision_acl_targets_and_spell_access_model.md](/<local-workspace>/codex/context_compass/tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md)
  Current precision ACL target model.

## Current Runtime Truth
- `static` is the strict room: live-only spell-facing behavior, no topology
  mutation, no direct create-path activation.
- `capability` is the non-codegen broad manual-runtime room.
- `dynamic` currently shares the same broad manual-runtime posture as
  capability and is reserved for later codegen-oriented differentiation.
- `Nexus` is the public AR root.
- `FrameDescriptorManager` and `FrameACLManager` are first-class Nexus-owned
  manager layers.
- `RiftSpace` owns a room-local `Workstation`, `CommandSystem`, and event
  queue/configuration seam.

## Current Test Truth
- The suite is pytest-driven and runs from `tests/`.
- The test tiers are `unit`, `component`, and `integration`.
- The newest high-value AR harnesses live under
  `tests/integration/melder/aether/rift/`.

## Use
When onboarding a new pass focused on AR, start here, then branch into the
current active ticket cluster from the board.
