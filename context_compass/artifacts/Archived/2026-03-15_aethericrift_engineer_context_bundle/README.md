# AethericRift Engineer Context Bundle

## Purpose
This bundle is the packaged engineer-facing context set for the current
AethericRift / MutationResearch design state.

It exists so an engineer can consume one prepared context package instead of
reassembling the handoff from multiple source locations.

## Important Rule
This bundle is a packaged copy/reference set.

Canonical project truth still lives in the original source files in the repo.
This bundle is for engineer onboarding, transfer, and export convenience.

Current ownership model in this bundle:
- `AethericRiftSystem` is the canonical owner of Rift instances/state
- `Aether` hosts that system and facades access into it
- direct live-Rift retrieval, if exposed at all, is a system-governed path

## Included Package Roots

### `AethericRift/`
Top-level AR object and system docs, including:
- `AethericRiftSystem`
- `AethericRiftState`
- `StaticRiftSpace`
- `DynamicRiftSpace`
- profiles
- session/request-guard docs

### `MutationResearch/`
Top-level MutationResearch context and working-model docs.

### `utilized_ticket_artifacts/`
Important long-form architecture context:
- `Ticket - AethericRift and MutationResearch Unified Current Architecture.md`
- `Ticket - AethericRift Implementation Contract.md`
- `Ticket - AethericRift Philosophical Context and End-State Model.md`
- `Ticket - Dynamic Runtime Objects and Agent-Native System Evolution.md`

### `context_compass/tickets/artifacts/`
Implementation-facing AR object/model note:
- `aethericrift_v1_object_model_and_build_direction.md`

### `context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/`
Engineer-facing patch contracts:
- architecture patch
- component patches
- code-description patch

### `context_compass/tickets/stories/`
Current AR implementation story and packaging story.

### `context_compass/tickets/epics/`
Packaging epic for the engineer-context bundle lane.

### `context_compass/tickets/tasks/`
Current AR implementation tasks, patch-handoff task, and packaging task.

### `context_compass/`
Current `attention_board.md` and `artifact_board.md` snapshots for routing and
artifact-index context.

### Repo root
- `how_to_migrate.md` migration guide for moving this package into the main code repo

## Recommended Read Order
1. `utilized_ticket_artifacts/Ticket - AethericRift Philosophical Context and End-State Model.md`
2. `utilized_ticket_artifacts/Ticket - AethericRift and MutationResearch Unified Current Architecture.md`
3. `utilized_ticket_artifacts/Ticket - AethericRift Implementation Contract.md`
4. `context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md`
5. `context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md`
6. all component patches in the same patch directory
7. `context_compass/tickets/stories/2026-03-15_aethericrift_v1_workspace_runtime_story.md`
8. the `2026-03-15_*` implementation tasks
9. top-level `AethericRift/` docs as needed for object semantics
10. `MutationResearch/` docs as context for the later canonical mutation lane

## Why This Bundle Exists
The current AR design now depends on a real combination of:
- source-backed Melder substrate constraints
- long-form architecture reasoning
- patch-framework engineer contracts
- concrete story/task sequencing

This bundle keeps those together.

## Canonical Source Locations
- Repo root `AethericRift/`
- Repo root `MutationResearch/`
- Repo root `utilized_ticket_artifacts/`
- `codex/context_compass/tickets/artifacts/`
- `codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/`
- `codex/context_compass/tickets/stories/`
- `codex/context_compass/tickets/tasks/`
