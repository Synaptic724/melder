# Task: Cleanup Attention Artifact And Ticket State

## Metadata
- Task ID: TASK-2026-04-26-cleanup-attention-artifact-and-ticket-state
- Story:
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-04-26T20:03:06Z
- Updated: 2026-04-26T20:10:59Z
- Updated: 2026-05-02T23:48:49Z

## Objective
Clean up stale board and ticket state so the active routing surfaces are
compact, agent-assigned, and aligned with the current live work.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested cleanup of `artifact_board.md`,
  `attention_board.md`, and old ticket state, with a specific emphasis on
  stale items and missing agent-name data.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
  - directly affected live tickets whose metadata or notes are stale
- DEPENDENCIES:
  - `codex/context_compass/agent_onboarding/default/general/skills/ticketing.md`
  - `codex/context_compass/agent_onboarding/default/general/skills/active_pointerboard.md`
  - `codex/context_compass/agent_onboarding/default/general/skills/ticket_closure_attention_sync.md`
- EXIT_GATE: active routing is compact, live tickets have agent-name metadata,
  and old/stale board state is either removed or downgraded with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if cleanup would require
  deleting or rewriting durable history beyond stale routing/index state.

## Scope Boundaries
- In scope:
  - stale active rows/details in `attention_board.md`
  - overloaded or stale active associations in `artifact_board.md`
  - missing `Agent Name` metadata on live tickets touched by the board cleanup
- Out of scope:
  - redesigning ticket policy
  - deleting durable note history without evidence
  - broad cleanup across unrelated completed archives

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a bounded cleanup pass over
  the active boards and old ticket state.

## Steps / Checklist
- [ ] Identify stale board rows/details and missing live ticket agent names.
- [ ] Prune or compress stale `attention_board.md` state.
- [ ] Prune or compress stale `artifact_board.md` active links.
- [ ] Update directly affected live ticket metadata to carry `Agent Name`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- cleaned `attention_board.md`
- cleaned `artifact_board.md`
- corrected `Agent Name` metadata on directly affected live tickets

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_cleanup_attention_artifact_and_ticket_state_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md
- codex/context_compass/tickets/epics/2026-04-26_design_crystallizer_asset_provenance_epic.md
- codex/context_compass/tickets/tasks/2026-04-25_harden_codegen_system_thread_safety_typing_and_protocol_usage_task.md
- codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/attention_board.md`
  - `Get-Content codex/context_compass/artifact_board.md`

## Risks / Rollback Notes
- Risk: an over-aggressive cleanup could erase durable historical context that
  should remain as reference.
  Rollback: keep durable history intact and restrict changes to stale active
  routing/index state plus missing agent-name metadata.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-26T20:03:06Z
  TYPE: FACT
  CLAIM: The active boards currently carry stale or inconsistent state. The
    live attention board still routes two lanes under generic `codex`
    assignment instead of the current certified `codex_0`, and the active
    artifact board still holds a large number of old retained-reference rows
    under `Active Artifact Links`, which overloads the active index.
  EVIDENCE:
  - codex/context_compass/attention_board.md:22-27
  - codex/context_compass/artifact_board.md:17-80
  - codex/context_compass/tickets/tasks/2026-04-25_harden_codegen_system_thread_safety_typing_and_protocol_usage_task.md:1-12
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:1-12
  IMPACT: The cleanup should focus on live routing/index accuracy rather than
    broad historical rewriting.
  NEXT: prune stale active board state and normalize live ticket agent-name
    metadata.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T20:06:02Z
  TYPE: FACT
  CLAIM: The stale artifact drift is now concrete. `artifact_board.md`
    currently marks 29 off-board tickets as still active artifact owners, while
    only two live routed lanes actually still carry active artifact rows:
    the crystallizer epic and the ACL design task. Separately, the two oldest
    live tickets on the attention board are missing `Agent Name` metadata in
    their ticket headers.
  EVIDENCE:
  - codex/context_compass/artifact_board.md:21-490
  - codex/context_compass/attention_board.md:22-27
  - codex/context_compass/tickets/tasks/2026-04-25_harden_codegen_system_thread_safety_typing_and_protocol_usage_task.md:1-12
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:1-12
  IMPACT: The cleanup can stay narrow and mechanical: compress the active
    artifact section to live routed lanes only, and fill the missing live
    ticket `Agent Name` fields without rewriting broader history.
  NEXT: patch the active artifact section, normalize live agent-name metadata,
    and recheck the board state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T20:10:59Z
  TYPE: MEASURE
  CLAIM: The housekeeping pass is now landed. `artifact_board.md` was
    compressed from 741 lines to 300 lines by limiting active artifact owners
    to live routed tickets only, and the two stale live task headers now carry
    explicit `Agent Name: codex_0` metadata with board-aligned status.
  EVIDENCE:
  - codex/context_compass/artifact_board.md:1-39
  - codex/context_compass/attention_board.md:22-27
  - codex/context_compass/tickets/tasks/2026-04-25_harden_codegen_system_thread_safety_typing_and_protocol_usage_task.md:1-12
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:1-12
  IMPACT: The live routing/index surfaces are materially cleaner without
    deleting durable ticket history or rewriting closed artifact anchors.
  NEXT: return the cleanup for review and let the user decide whether any
    remaining old retained-reference history should be pruned further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T20:10:59Z
  TYPE: FACT
  CLAIM: The remaining artifact-board cleanup target is now exact, not
    speculative. One active ACL-task artifact row and eleven cleared-history
    rows point at files that are actually gone on disk, so those board rows are
    now dead references rather than retained history.
  EVIDENCE:
  - codex/context_compass/artifact_board.md:29-29
  - missing_artifact_rows:
    - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md -> tickets/artifacts/nexus_acl_builder_and_persistence_model.md
    - tickets/tasks/completed/2026-04-12_add_command_level_conduit_introspection_helpers_task.md -> system_docs/patches/active/command_level_conduit_introspection_helpers/architecture_patch.md
    - tickets/tasks/completed/2026-04-12_add_command_level_conduit_introspection_helpers_task.md -> system_docs/patches/active/command_level_conduit_introspection_helpers/component_patch_command_system.md
    - tickets/tasks/completed/2026-04-12_add_command_level_conduit_introspection_helpers_task.md -> system_docs/patches/active/command_level_conduit_introspection_helpers/component_patch_interfaces.md
    - tickets/tasks/completed/2026-04-12_implement_capability_room_manual_runtime_access_task.md -> tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
    - tickets/tasks/completed/2026-04-12_investigate_and_plan_capability_room_implementation_task.md -> tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
    - tickets/stories/completed/2026-04-12_investigate_capability_rift_space_runtime_model_story.md -> tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
    - tickets/epics/completed/2026-04-09_live_creation_visibility_probe_for_static_access_epic.md -> tickets/artifacts/2026-04-09_live_creation_visibility_probe_design.md
    - tickets/tasks/completed/2026-04-04_investigate_aethericframe_descriptor_refactor_task.md -> system_docs/patches/active/nexus_frame_descriptor_refactor/component_patch_frame_descriptor.md
    - tickets/tasks/completed/2026-03-16_plan_aethericrift_system_bootstrap_task.md -> tickets/artifacts/aethericrift_riftspace_interaction_architecture.md
    - tickets/tasks/completed/2026-04-19_investigate_and_plan_frame_viewer_projection_backed_rift_owned_migration_task.md -> tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
    - tickets/epics/completed/2026-04-12_capability_rift_space_runtime_model_epic.md -> tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
  IMPACT: These rows should be removed instead of preserved, because the board
    is now pointing at nonexistent files.
  NEXT: strip the dead artifact rows from `artifact_board.md` and remove the
    stale active ticket artifact reference.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T23:48:49Z
  TYPE: FACT
  CLAIM: The live attention board has drifted back into a mixed queue of
    unrelated active rows. It currently combines benchmark, ownership-fix, ACL,
    synthetic-module, and crystallizer lanes even though the user explicitly
    asked to clean the board and re-center the current routing on the
    crystallizer epic.
  EVIDENCE:
  - attention_board.md:27-41
  - attention_board.md:46-50
  - attention_board.md:120-124
  - attention_board.md:224-228
  - attention_board.md:250-254
  IMPACT: The cleanup can stay routing-only: keep the crystallizer runtime
    reorientation lanes on the live board, remove unrelated active rows/details,
    and preserve durable history in the tickets themselves.
  NEXT: rewrite the active items/details section around the crystallizer epic
    and its directly related tasks only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded housekeeping pass over `attention_board.md`,
`artifact_board.md`, and directly affected live ticket metadata.
