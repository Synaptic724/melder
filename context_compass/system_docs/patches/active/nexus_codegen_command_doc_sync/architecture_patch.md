# Architecture Patch: Nexus Codegen Command Doc Sync

## Patch Scope and Non-Goals
Scope:
- align the canonical documentation stack to the landed Nexus builder,
  codegen-system, and codegen-command runtime surfaces
- update `src_architecture.md`, `src_components.md`, `src_graph.json`, and
  `readable_src_graph.json` to reflect the current ownership and delegation
  model

Non-goals:
- changing runtime behavior
- redesigning ACL policy or codegen execution contracts beyond what is already
  evidenced in source
- widening into unrelated Nexus cleanup or test-expansion lanes

## Changed-Components Matrix
| Component | Current gap | Required doc delta |
|---|---|---|
| `NexusFrameBuilder` | missing from architecture/components/graph surfaces | add builder ownership, default dynamic posture, rooted create path, and graph node/edges |
| `FrameACLBuilder` | graph-only presence, limited long-form coverage | add family-draft/session role and commit/install contract to architecture/components docs |
| `CodegenSystem` | missing from architecture/components/graph surfaces | add internal engine ownership under `CodegenRiftSpace` with validator/namespace/compiler/executor/monitor composition |
| `CodegenCommandSystem` | under-described as a slim helper seam only | document attached `CodegenSystem` delegation and codegen-specific room-memory emission |

## Interface and Boundary Deltas
- `CodegenCommandSystem` MUST be described as the room-facing facade, not the
  full owner of validation/namespace/execution behavior.
- `CodegenSystem` MUST be described as the internal engine root owned by one
  `CodegenRiftSpace`.
- `NexusFrameBuilder` MUST be documented as a distinct authored-frame builder
  owned by `NexusFrameManager`, not collapsed into manager prose.
- `FrameACLBuilder` MUST be documented as one frame-local family-draft
  orchestrator over view/command/codegen chains, not only as a generic
  "builder exists" statement.
- The graph MUST carry node coverage and semantic edges for any newly
  documented runtime owners inside `src/melder/**`.

## Cross-Component Invariants
- `CodegenRiftSpace` owns one `CodegenSystem` and one `CodegenCommandSystem`.
- `CodegenCommandSystem` delegates `validate_codegen(...)` and
  `execute_codegen(...)` into the attached `CodegenSystem`.
- `CodegenSystem` owns namespace construction, validation, compilation,
  execution, and monitoring collaborators.
- `CodegenCommandSystem` owns the room-facing memory-emission wrapper for
  top-level codegen actions.
- `NexusFrameBuilder` defaults to `dynamic + ai_native_enabled + rift_enabled`
  and returns a rooted conduit through manager create.
- `FrameACLBuilder` owns exactly one active family draft at a time and commits
  into the owning `FrameACLContainer`.

## Migration/Rollout Order
1. land patch artifacts for architecture/components/code-description deltas
2. update `src_architecture.md` with the missing ownership/boundary narrative
3. update `src_components.md` with component and call-flow detail
4. expand/edit/recompress `src_graph.json`
5. regenerate `readable_src_graph.json`
6. validate section contracts and JSON integrity

## Rollback Strategy
- if evidence proves any claimed owner/boundary is wrong, keep the item
  `UNKNOWN` and revert the pending canonical doc delta before touching the graph
- if graph updates become inconsistent with architecture/components prose,
  roll back the graph edit and re-stage from the patch docs

## Validation Expectations and Evidence Plan
- architecture docs cite concrete source ranges for `CodegenSystem`,
  `CodegenCommandSystem`, `NexusFrameBuilder`, and `FrameACLBuilder`
- components docs include explicit component entries and call flows for the
  changed surfaces
- `src_graph.json` and `readable_src_graph.json` validate as JSON after update
- readable graph adds the missing node/edge coverage without duplicating prose

## Ticket Coverage Map
- task:
  - `tickets/tasks/2026-04-25_review_nexus_codegen_command_doc_sync_task.md`
- patch components:
  - `component_patch_nexus_frame_builder.md`
  - `component_patch_frame_acl_builder.md`
  - `component_patch_codegen_system.md`
  - `component_patch_codegen_command_system.md`
- conditional code descriptions:
  - `code_description_patch_codegen_system.md`
  - `code_description_patch_codegen_command_system.md`

## Unknowns and Decision Requests
- UNKNOWN: whether the canonical docs should explicitly describe every
  `codegen_system/validation/strategies/*` file individually in the first pass
  or keep them grouped under the validator subsystem
- UNKNOWN: whether `NexusFrameBuilder` needs a dedicated architecture mention
  or only a components/graph addition once the manager/builder split is made
  explicit
