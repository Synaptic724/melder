# Task: Sync Core Architecture And Components Docs

## Metadata
- Task ID: TASK-2026-04-02-sync-core-architecture-and-components-docs
- Story: none
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-02T21:45:12Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Update the canonical `src_architecture.md` and `src_components.md` documents so
they reflect the current live state of the Melder runtime after the Nexus/Rift
public-root refactor and the logging-provider migration.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a documentation sync so future
  re-entry reflects the current live runtime instead of older architecture
  assumptions.
- EXECUTION_BOUNDARY: source architecture/components documentation sync only.
- DEPENDENCIES:
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md
  - tickets/tasks/completed/2026-03-29_migrate_core_logging_to_aether_utility_system_task.md
  - tickets/tasks/completed/2026-03-30_migrate_nexus_rift_logging_to_aether_utility_system_task.md
  - tickets/tasks/completed/2026-03-30_remove_legacy_logger_factory_components_task.md
- EXIT_GATE: canonical source docs describe the current Nexus/Rift public-root
  model, frame-mode behavior, current room/event seam, and provider-based
  logging model accurately enough for re-onboarding.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the required documentation
  update would force broader canon decisions about unresolved future AR/workspace
  semantics.

## Scope Boundaries
- In scope:
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - current Nexus/Rift ownership and frame-mode semantics
  - current logging-provider model
  - explicit note of placeholder seams that are still not implemented
- Out of scope:
  - tests architecture/components docs
  - runtime code edits
  - patch-doc consolidation
  - new public API design beyond what is already live

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the canonical source architecture/components docs have
  been updated to the current live Nexus/Rift/logging/structure-profile model
  and reread for consistency, so this slice is ready for user review.

## Steps / Checklist
- [x] Route this documentation sync on the attention board.
- [x] Read the architecture/components doc instruction skills.
- [x] Re-read the current canonical source docs in bounded chunks.
- [x] Re-read the current live Nexus/Rift/logging seams in source/ticket notes.
- [x] Update `system_docs/src_architecture.md`.
- [x] Update `system_docs/src_components.md`.
- [x] Re-read the touched sections after writing.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated `codex/context_compass/system_docs/src_architecture.md`
- updated `codex/context_compass/system_docs/src_components.md`

## Files / Paths Impacted
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/tickets/tasks/2026-04-02_sync_core_architecture_and_components_docs_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `Get-Content codex/context_compass/system_docs/src_architecture.md`
  - `Get-Content codex/context_compass/system_docs/src_components.md`
  - `Select-String ... AetherUtilitySystem|Nexus|RiftSpace|StructureProfileBuilder|SpellExaminer`
  - `Select-String ... logger factory|IrisLoggerFactory|StdLoggerFactory`

## Risks / Rollback Notes
- Risk: docs overstate unfinished Rift/workspace behavior instead of marking
  the current placeholders clearly.
  Rollback: keep unresolved behavior explicitly marked as current seam/TODO
  rather than normalizing it into completed architecture.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-02T22:04:18Z
  TYPE: FACT
  CLAIM: The canonical source docs are now synchronized to the current live
    runtime in the areas that were materially stale for re-entry. The
    architecture doc now explains the hidden-substrate/public-AR split
    (`Aether` + `AetherUtilitySystem` + `Nexus` / `Rift` / `RiftSpace`), the
    provider-based logging model, and the structure/AI profile layer. The
    components doc now has matching C3/C2/C1 coverage for the AR runtime
    surface, the provider-hosted logging layer, and the structure-profile /
    introspection subsystem.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:247-320
  - codex/context_compass/system_docs/src_architecture.md:339-400
  - codex/context_compass/system_docs/src_architecture.md:414-481
  - codex/context_compass/system_docs/src_architecture.md:683-743
  - codex/context_compass/system_docs/src_architecture.md:888-903
  - codex/context_compass/system_docs/src_architecture.md:940-964
  - codex/context_compass/system_docs/src_architecture.md:1089-1101
  - codex/context_compass/system_docs/src_components.md:353-372
  - codex/context_compass/system_docs/src_components.md:489-564
  - codex/context_compass/system_docs/src_components.md:920-1034
  - codex/context_compass/system_docs/src_components.md:1624-1682
  - codex/context_compass/system_docs/src_components.md:1705-1718
  - codex/context_compass/system_docs/src_components.md:1823-1828
  - codex/context_compass/system_docs/src_components.md:1954-1994
  - codex/context_compass/system_docs/src_components.md:2027-2074
  - codex/context_compass/system_docs/src_components.md:2121-2129
  IMPACT: Re-onboarding can now recover the current live model without falling
    back to the older Aether-root/logger-factory mental model or missing the
    AR and structure-profile layers.
  NEXT: review the updated source docs with the user and tighten only if they
    want more detail or a harder line on any specific subsystem.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:45:12Z
  TYPE: PLAN
  CLAIM: The user wants the canonical source architecture/components docs synced
    to the current live runtime state before more Nexus/Rift design work
    continues. The specific drift areas are the Nexus/Rift public-root model,
    the provider-based logging system, and the current event/workspace seams.
  EVIDENCE:
  - user_instruction: "maybe we need to pause, and add this stuff into the architecture and component docs"
  - user_instruction: "update the logger changes in there too so you can properly understand where we are each time you reset"
  IMPACT: This should be handled as a documentation sync slice, not as an
    incidental side edit inside the existing Nexus task.
  NEXT: route this task on the attention board, then read the doc instruction
    skills and current canonical source docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:48:19Z
  TYPE: FACT
  CLAIM: The user clarified the specific documentation gaps that matter for
    re-entry. The source docs currently do not sufficiently cover the live AR
    surface (`AR` / `Rift` / `Nexus`), the logging-provider swap centered on
    `AetherUtilitySystem`, and the structure-profile side of the system
    including the structure profile models and the structure profile builder.
  EVIDENCE:
  - user_instruction: "we got nothing in there about AR/ Rift/ Nexus/ and logger swaps"
  - user_instruction: "and AetherUtility tool, and structure profile models and structure profile builder all that jazz"
  IMPACT: The doc sync must cover more than just the narrow Nexus frame-mode
    slice. It needs to restore the broader live-system picture that re-entry
    actually depends on.
  NEXT: read the source-doc instruction skills and current canonical source
    docs, then patch them around those specific missing concepts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:52:31Z
  TYPE: FACT
  CLAIM: The canonical source docs are materially stale in exactly the areas
    the user flagged. `src_architecture.md` still frames Aether as the global
    runtime root and still describes Spellbook logging as an optional logger
    factory upgrade, while the live runtime now has a provider-based
    `AetherUtilitySystem`, a public `Nexus` singleton with `Rift` objects under
    it, a real shared/indexed/one-per-workspace frame topology layer, and a
    separate structure-profile subsystem. `src_components.md` likewise has no
    component coverage for `Nexus`/`Rift` or the structure-profile builder/model
    layer, and its logging component still stops at `SafeLogger` + init helpers.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:249-255
  - codex/context_compass/system_docs/src_architecture.md:270-279
  - codex/context_compass/system_docs/src_architecture.md:290-299
  - codex/context_compass/system_docs/src_architecture.md:569-573
  - codex/context_compass/system_docs/src_components.md:395-438
  - codex/context_compass/system_docs/src_components.md:837-861
  - src/melder/aether/aether_utility_system.py:11-34
  - src/melder/aether/aether_utility_system.py:128-278
  - src/melder/aether/nexus/nexus.py:32-49
  - src/melder/aether/nexus/nexus.py:675-836
  - src/melder/aether/nexus/rift/rift.py:20-39
  - src/melder/aether/nexus/rift/rift.py:435-616
  - src/melder/aether/structure_profiles/structure_profile_builder.py:23-145
  - src/melder/aether/structure_profiles/structure_profile_models.py:71-176
  - src/melder/aether/structure_profiles/structure_profile_models.py:175-353
  IMPACT: The source docs need a real sync pass, not a wording tweak. If left
    alone, re-entry will keep loading the old Aether-root / logger-factory
    mental model and miss the current AR + structure-profile surfaces entirely.
  NEXT: patch the architecture and components docs around those specific live
    seams, then reread the touched sections for consistency.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:55:44Z
  TYPE: FACT
  CLAIM: The design-engineer patch-framework guidance changes how this sync
    should be executed. Because the doc update touches live architecture and
    component contracts, the canonical source docs should be brought back in
    line with the active patch lane rather than rewritten from memory. For
    this slice that means using the existing Nexus/Rift public-surface patch
    docs as design scaffolding. It does not automatically require a new patch
    set because we are synchronizing canon to already-landed runtime truth,
    not designing a new architecture delta.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:10-24
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:41-58
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/architecture_contexts.md:10-19
  - codex/context_compass/tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md:89-96
  IMPACT: The next investigation step is not arbitrary prose editing. It is
    reading the active Nexus/Rift patch artifacts and then merging their live
    truths into the canonical source docs without inventing new design.
  NEXT: read the active Nexus/Rift patch docs, then patch the canonical source
    architecture/components docs from those contracts plus current source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to sync the canonical source architecture/components docs to
the current live Melder runtime state after the Nexus/Rift and logging changes.
