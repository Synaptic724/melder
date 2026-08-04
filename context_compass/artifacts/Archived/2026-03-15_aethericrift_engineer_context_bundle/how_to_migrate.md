# How To Migrate AethericRift Context Into The Main Code Repo

## Purpose
This document explains how to move the packaged AethericRift / MutationResearch
design context from this planning repo into the normal repository where runtime
code will be written and maintained.

## Source Package
Use this bundle as the migration source:

- [engineer context bundle](<local-workspace>/codex/context_compass/artifacts/2026-03-15_aethericrift_engineer_context_bundle/README.md)

That bundle contains:
- copied `AethericRift/` top-level docs
- copied `MutationResearch/` top-level docs
- important `utilized_ticket_artifacts/`
- AR patch contracts
- current AR implementation story/tasks
- packaging epic/story/task
- current `attention_board.md` / `artifact_board.md` snapshots

## Canonical Design Inputs To Carry Over
These are the most important files to migrate first:

1. `utilized_ticket_artifacts/Ticket - AethericRift and MutationResearch Unified Current Architecture.md`
2. `codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md`
3. `codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md`
4. all component patches in
   `codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/`
5. `codex/context_compass/tickets/stories/2026-03-15_aethericrift_v1_workspace_runtime_story.md`
6. the current AR implementation tasks under
   `codex/context_compass/tickets/tasks/2026-03-15_*`

## Top-Level AR Docs To Carry Over
If you want the full top-level design context in the main repo, migrate:

- `AethericRift/README.md`
- `AethericRift/WORKING_PLAN.md`
- `AethericRift/objects/`
- `AethericRift/systems/`

Most important objects from that set:
- `aetheric_rift_system.md`
- `aetheric_rift_state.md`
- `aetheric_rift.md`
- `aetheric_space.md`
- `static_rift_space.md`
- `dynamic_rift_space.md`
- `rift_configuration.md`
- `rift_profile.md`
- `aetheric_frame_profile.md`
- `spellbook_rift_profile.md`
- `spell_rift_profile.md`
- `frame_examiner.md`
- `rift_attribute.md`
- `rift_method.md`
- `rift_validation_system.md`

Most important systems from that set:
- `request_guard.md`
- `identity_auth.md`
- `codegen_guardrails.md`
- `interaction_modes.md`
- `melder_wiring.md`

## MutationResearch Docs To Carry Over
Carry at least:

- `MutationResearch/README.md`
- `MutationResearch/WORKING_MODEL.md`
- `MutationResearch/systems/`

Most important from that set:
- `mutation_lifecycle.md`
- `control_plane_gates.md`
- `lane_contract.md`
- `codegen_bridge.md`
- `open_questions.md`

## Recommended Destination Layout
If the main repo already has runtime code, keep the migrated planning docs in a
clear documentation area rather than scattering them.

Recommended destination shape:

```text
docs/
  aetheric_rift/
    README.md
    objects/
    systems/
  mutation_research/
    README.md
    systems/
  architecture/
    Ticket - AethericRift and MutationResearch Unified Current Architecture.md
    aethericrift_v1_object_model_and_build_direction.md
  patches/
    aethericrift_v1_workspace_runtime/
      architecture_patch.md
      component_patch_*.md
      code_description_patch_*.md
```

If your main repo already has its own architecture directory conventions, map
these into that structure instead of forcing the exact layout above.

## Migration Order
1. Copy the unified architecture ticket.
2. Copy the AR v1 object-model note.
3. Copy the active AR patch directory.
4. Copy the top-level `AethericRift/` docs.
5. Copy the top-level `MutationResearch/` docs.
6. Copy the current AR implementation story/tasks if you want the full handoff
   trail in the target repo.
7. Re-link those docs to the target repo's actual code paths once the codebase
   layout is known.

## What To Treat As Historical Versus Active
Treat as active:
- the unified architecture ticket
- the AR v1 object-model note
- the active AR patch docs
- the `2026-03-15_*` AR implementation story/tasks
- the top-level AR/MR docs that match the new model

Treat as historical/reference only:
- older February AR implementation story/tasks
- older AR old-ticket files
- superseded design fragments that still exist only for traceability

## Important Current Design Decisions To Preserve
- `Aether` is the substrate root and manager.
- `AethericRiftSystem` is the root manager of Rifts.
- `AethericRiftState` is canonical per-Rift state.
- public `AethericRift` is shell -> register -> hydrate.
- AR system frame is distinct from configured target frame.
- `FrameExaminer` gathers configured-frame truth.
- `StaticRiftSpace` is the enforcement boundary.
- `DynamicRiftSpace` is the AST+hooks dynamic surface.
- profiles are exposure/setup policy with bottom-up override.
- `Aether` should expose `_get_conduits_by_frame(...)`.
- token names are:
  - `AethericRiftCreationToken`
  - `AethericRiftToken`

## After Migration
Once copied into the main repo:

1. Update any file-path references that still point back to this planning repo.
2. Decide what should become canonical docs versus temporary handoff docs.
3. Keep the patch docs until the implementation proves them out.
4. Only then merge the durable parts into the target repo's canonical
   architecture documentation.

## Minimal Practical Advice
If you want the fastest migration:

- copy the entire bundle directory
- then prune inside the target repo later

If you want the cleanest migration:

- copy only the files listed in “Canonical Design Inputs To Carry Over”
- then add top-level AR/MR docs selectively
