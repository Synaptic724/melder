# Attention Board

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Capture evidence pointers while reading (do not wait for end-of-pass summaries).
- Keep entries short using: `TYPE`, `CLAIM`, `EVIDENCE`, `REREAD`, `NEXT`.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`); for single-line evidence use `start=end`.
- Append newest entries first under the matching active work item.
- Promote durable conclusions into the linked ticket after verification.

## Active Items
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| context_compass artifact reference cleanup | review | codex | none | walk through cleanup outcomes and confirm acceptance for closure | `context_compass/tasks/2026-02-14_context_compass_artifact_reference_cleanup_task.md` | 2026-02-14 | REQUIRED |
| phase testing epic | in_progress | codex | none | execute rank-2 task `TASK-2026-02-14-optimize-phase8-10-plan-row-builders` | `context_compass/epics/2026-02-14_phase_testing_epic.md` | 2026-02-14 | REQUIRED |
| optimize melder epic | ready | codex | none | execute discovery tasks in linked stories and append implementation tasks from findings | `context_compass/epics/2026-02-13_optimize_melder_epic.md` | 2026-02-14 | REQUIRED |
| optimize conjure paths | in_progress | codex | none | confirm acceptance for `TASK-2026-02-14-conjure-phase-unit-allocation-fastpath`, then execute `TASK-2026-02-14-conjure-activation-and-validation-scan-fastpath` | `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md` | 2026-02-14 | REQUIRED |
| optimize meld paths | in_progress | codex | none | review/confirm `TASK-2026-02-13-meld-dynamic-gate-fastdoor` acceptance, then close/move as directed | `context_compass/stories/2026-02-13_optimize_meld_paths_story.md` | 2026-02-14 | REQUIRED |
| optimize spellcrafter phases | ready | codex | none | run discovery task and produce hotspot-ranked candidates | `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md` | 2026-02-13 | REQUIRED |
| optimize creation context codegen | ready | codex | none | run discovery task and produce hotspot-ranked candidates | `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md` | 2026-02-13 | REQUIRED |
| optimize phase12 codegen | ready | codex | none | run discovery task and produce hotspot-ranked candidates | `context_compass/stories/2026-02-13_optimize_phase12_codegen_story.md` | 2026-02-13 | REQUIRED |

## Active Attention Details
- TYPE: FACT
- CLAIM: Rank-1 optimization task is now implemented and validated; warm 8-11 sample dropped from `34.993ms` to `27.829ms`, and warm cProfile sample dropped from `0.091s` to `0.083s`.
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:57-89`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-15`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15`
- REREAD: REQUIRED
- NEXT: Start `TASK-2026-02-14-optimize-phase8-10-plan-row-builders`.

- TYPE: FACT
- CLAIM: Optimization backlog ranking is complete and three scoped follow-up tasks were created from measured phase-testing outputs.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:47-82`, `context_compass/tasks/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:1-12`, `context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:1-12`, `context_compass/tasks/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:1-12`
- REREAD: REQUIRED
- NEXT: Start rank-1 optimization implementation task.

- TYPE: FACT
- CLAIM: Harness validation and baseline measurement execution are complete; a durable artifact now contains 1-4, 5-7 conduit/local, and 8-11 measurements plus warm 8-11 cProfile output.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-14`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:51-52`
- REREAD: REQUIRED
- NEXT: Continue `TASK-2026-02-14-discovery-phase-testing-optimization-backlog` with ranked hotspot candidates and follow-up task creation.

- TYPE: FACT
- CLAIM: Execution tasks were created for harness implementation and baseline measurement runs, providing a concrete unblock path for phase-testing ranking.
- EVIDENCE: `context_compass/tasks/2026-02-14_implement_phase_component_cprofile_harness_task.md:1`, `context_compass/tasks/2026-02-14_execute_phase_group_baseline_measurements_task.md:1`
- REREAD: REQUIRED
- NEXT: Implement `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` and run it with `pytest -q -s`.

- TYPE: FACT
- CLAIM: Phase-testing optimization-backlog discovery is blocked until measured outputs are attached; readiness gate and ranking schema are documented.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:6`, `context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:28`
- REREAD: REQUIRED
- NEXT: Confirm acceptance for discovery tickets, then implement/run harness baselines to produce measured artifacts.

- TYPE: FACT
- CLAIM: Phase 8-11 baseline discovery is documented and in review with per-spell chain contract, warm/cold variants, and execution-plan metric outputs.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_group_8_11_baseline_task.md:1`, `context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-testing-optimization-backlog`.

- TYPE: FACT
- CLAIM: Local 5-7 baseline discovery is documented and in review with target-scoped chain and scoped-size reporting contract.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:1`, `context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-group-8-11-baseline`.

- TYPE: FACT
- CLAIM: Conduit-wide 5-7 baseline discovery is documented and in review with lead-spell frame-scoped direct-call sequencing and ranking output fields.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:1`, `context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-group-5-7-local-baseline`.

- TYPE: FACT
- CLAIM: Phase 1-4 baseline discovery is documented and in review with full-spellbook default scope, optional single-spell diagnostic slice, and explicit warm/cold variant contract.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_group_1_4_baseline_task.md:1`, `context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline`.

- TYPE: FACT
- CLAIM: Harness discovery contract is documented and in review: four direct-call phase groups with no scheduler path, production-order gating, and standardized profile output schema.
- EVIDENCE: `context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md:34`, `context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:1`
- REREAD: REQUIRED
- NEXT: Confirm acceptance for `TASK-2026-02-14-discovery-phase-component-cprofile-harness`, then execute `TASK-2026-02-14-discovery-phase-group-1-4-baseline`.

- TYPE: FACT
- CLAIM: Artifact reference cleanup is implemented: legacy artifact links remapped to canonical index, placeholder files removed, and global reference scan is clean.
- EVIDENCE: `context_compass/tasks/2026-02-14_context_compass_artifact_reference_cleanup_task.md:1`, `context_compass/artifacts/README.md:1`
- REREAD: REQUIRED
- NEXT: Confirm acceptance and close the cleanup task.

- TYPE: FACT
- CLAIM: New user-directed migration requires renaming `codex_todo` to `context_compass`, adding generalized core/profile structure, and adding microcycle-config toggles.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_context_compass_rename_and_profile_config_task.md:1`, `context_compass/stories/completed/2026-02-14_context_compass_core_profile_packaging_story.md:1`
- REREAD: REQUIRED
- NEXT: none (accepted and closed; keep as historical anchor).

- TYPE: FACT
- CLAIM: Onboarding hardening patch is implemented across AGENTS/workflow/skills/behavioral docs/templates with microcycle gates, UNKNOWN-first defaults, and board-first routing.
- EVIDENCE: `context_compass/AGENTS.MD:437`, `context_compass/WORKFLOW.md:72`, `context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:1`, `context_compass/templates/task_template.md:22`
- REREAD: REQUIRED
- NEXT: none (accepted and closed; keep as historical anchor).

- TYPE: FACT
- CLAIM: Onboarding docs contain routing drift where `00_overview.md` is referenced as active state while compaction policy already declares `attention_board.md` canonical.
- EVIDENCE: `context_compass/CONTEXT_COMPACTION.md:8`, `context_compass/agent_onboarding/agent/general/skills/context_protocol.md:12`, `context_compass/agent_onboarding/agent/general/behavioral_guidelines/onboarding_summary.md:23`
- REREAD: REQUIRED
- NEXT: Keep as historical anchor; normalization has been implemented in the active onboarding hardening task.

- TYPE: FACT
- CLAIM: Phase-testing discovery scope now includes an explicit 8-11 baseline story/task, and missing discovery task files were created for spellcrafter, creation_context codegen, and phase12 codegen stories.
- EVIDENCE: `context_compass/epics/2026-02-14_phase_testing_epic.md:1`, `context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:1`, `context_compass/tasks/2026-02-14_discovery_phase_group_8_11_baseline_task.md:1`, `context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md:1`, `context_compass/tasks/2026-02-13_discovery_creation_context_codegen_task.md:1`, `context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md:1`
- REREAD: REQUIRED
- NEXT: Execute discovery tasks in phase-group order and append evidence-backed hotspots into linked story/task notes.

- TYPE: FACT
- CLAIM: Created `EPIC-2026-02-14-phase-testing` with discovery-first stories/tasks for direct phase component profiling (`cProfile`) without `PhaseScheduler`, workers, or `UnitOfWork`.
- EVIDENCE: `context_compass/epics/2026-02-14_phase_testing_epic.md:1`, `context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:1`, `context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md:1`
- REREAD: REQUIRED
- NEXT: Execute harness discovery task and lock toggle matrix for phase groups.

- TYPE: FACT
- CLAIM: Confirmed two foundational 5-7 tracks exist: conduit-wide and target-local; target-local uses single local-scope phase registrations per phase.
- EVIDENCE: `src/melder/spellbook/spellbook_creation_system.py:1063`, `src/melder/spellbook/spellbook_creation_system.py:1206`, `src/melder/spellbook/spellbook_creation_system.py:1165`
- REREAD: REQUIRED
- NEXT: Keep separate component baseline stories for conduit-wide 5-7 and local 5-7.

- TYPE: FACT
- CLAIM: Removed redundant conjure duplicate-id recheck from `_resolve_conjure_policy`; bind front-door duplicate SHA guard remains intact.
- EVIDENCE: `src/melder/spellbook/spellbook_creation_system.py:280`, `src/melder/spellbook/spellbook_creation_system.py:285`, `src/melder/spellbook/spellbook.py:2496`
- REREAD: REQUIRED
- NEXT: Confirm acceptance and continue `TASK-2026-02-14-conjure-activation-and-validation-scan-fastpath`.

- TYPE: FACT
- CLAIM: Implemented conjure phase-unit-allocation fastpath by consolidating eight per-spell phase factories behind one shared helper with preserved labels/metadata/args behavior.
- EVIDENCE: `src/melder/spellbook/spellbook_creation_system.py:1481`, `src/melder/spellbook/spellbook_creation_system.py:1666`, `tests/unit/melder/spellbook/test_spellbook.py:1343`, `tests/unit/melder/spellbook/test_spellbook.py:2111`
- REREAD: REQUIRED
- NEXT: Confirm task acceptance and move to activation/validation scan fastpath.

- TYPE: FACT
- CLAIM: Fixed `PhaseScheduler` worker-loop empty-queue exception handling (`QueueEmpty`) and added a regression test proving workers survive sparse long phases before phase-2.
- EVIDENCE: `src/melder/utilities/synchronization/phase_scheduler.py:5`, `src/melder/utilities/synchronization/phase_scheduler.py:399`, `tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:185`
- REREAD: REQUIRED
- NEXT: Continue conjure scheduler-path optimization discovery using this regression as a safety guard.

- TYPE: FACT
- CLAIM: Added `active_documentation` skill and enforced `## Notes` sections across active epic/story/task tickets.
- EVIDENCE: `context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1`, `context_compass/agent_onboarding/agent/general/SKILLS.md:20`, `context_compass/WORKFLOW.md:31`, `context_compass/epics/2026-02-13_optimize_melder_epic.md:122`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:115`, `context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md:133`
- REREAD: REQUIRED
- NEXT: Use per-ticket `Notes` as the primary in-flight evidence log while continuing optimization tasks.

- TYPE: FACT
- CLAIM: Conjure discovery completed with ranked hotspots; three follow-up implementation tasks were created and queued in story order.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md:1`, `context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md:1`, `context_compass/tasks/2026-02-14_conjure_phase_unit_allocation_fastpath_task.md:1`, `context_compass/tasks/2026-02-14_conjure_activation_and_validation_scan_fastpath_task.md:1`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:1`
- REREAD: REQUIRED
- NEXT: Confirm discovery acceptance, then start scheduler lifecycle reduction task.

- TYPE: FACT
- CLAIM: Conjure discovery task was activated with ticket-first evidence logging and has now been completed.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md:1`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute first follow-up optimization task in the same story.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-dynamic-gate-fastdoor` implementation is complete and in review; `Conduit.meld` now uses local alias fastdoor while preserving close/wait/ticket invariants.
- EVIDENCE: `src/melder/aether/conduit/conduit.py:2345`, `tests/unit/melder/aether/conduit/test_conduit_facade.py:746`, `tests/unit/melder/aether/conduit/test_conduit_facade.py:779`, `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md:1`
- REREAD: REQUIRED
- NEXT: Ask user to confirm acceptance, then move task to completed.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-validation-gate-microprofile` is accepted and closed; story flow now advances to dynamic gate fastdoor optimization.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`, `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:126`
- REREAD: REQUIRED
- NEXT: Execute dynamic gate invariants/discovery and implement fastdoor optimization.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-validation-gate-microprofile` implementation is complete; Meld now caches per-frame change-control managers while preserving per-call dirty-root checks.
- EVIDENCE: `src/melder/aether/conduit/meld/meld.py:130`, `src/melder/aether/conduit/meld/meld.py:459`, `tests/unit/melder/aether/conduit/meld/test_meld.py:1515`, `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`
- REREAD: REQUIRED
- NEXT: Use as closed anchor while executing dynamic gate fastdoor task.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-override-shape-hotpath` is completed and user-accepted; work now proceeds to validation-gate microprofile.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md:1`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:571`, `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py:388`, `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`
- REREAD: REQUIRED
- NEXT: Execute baseline profiling and safe micro-optimizations in `TASK-2026-02-13-meld-validation-gate-microprofile`.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-override-shape-hotpath` implementation is complete with cache-hit short-circuiting of grouped-target collection in `CreationContext` while preserving specialization-key semantics.
- EVIDENCE: `src/melder/aether/conduit/meld/creation_context/creation_context.py:571`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:582`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:653`, `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py:189`, `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py:388`, `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md:1`
- REREAD: REQUIRED
- NEXT: Keep implementation notes linked while executing the next task.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-input-resolution-keypath` is completed and user-accepted.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md:1`, `src/melder/aether/conduit/meld/meld.py:308`, `tests/unit/melder/aether/conduit/meld/test_meld.py:758`
- REREAD: REQUIRED
- NEXT: Move to `TASK-2026-02-13-meld-override-shape-hotpath`.

- TYPE: FACT
- CLAIM: Implemented non-string meld input keypath optimization by removing redundant pre-hash lookup work and preserving id-fallback semantics.
- EVIDENCE: `src/melder/aether/conduit/meld/meld.py:308`, `src/melder/aether/conduit/meld/meld.py:311`, `src/melder/aether/conduit/meld/meld.py:315`, `tests/unit/melder/aether/conduit/meld/test_meld.py:758`, `tests/unit/melder/aether/conduit/meld/test_meld.py:796`
- REREAD: REQUIRED
- NEXT: Keep as completed anchor evidence; active execution is validation-gate microprofile.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-contract-defaults-caching` was closed as out-of-scope for the current wave by user direction.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:124`
- REREAD: REQUIRED
- NEXT: Keep focus on remaining meld optimization tasks.

- TYPE: FACT
- CLAIM: Meld discovery leads are now converted into two active implementation tasks plus two completed tasks and one out-of-scope task.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md:1`, `context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md:1`, `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md:1`, `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md:1`, `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:124`
- REREAD: REQUIRED
- NEXT: Execute remaining tasks in order: validation-gate -> dynamic-gate.

- TYPE: FACT
- CLAIM: Meld-path discovery is documented with Conduit->Meld->CreationContext flow, ranked hotspots, and follow-up implementation tasks.
- EVIDENCE: `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:42`
- REREAD: REQUIRED
- NEXT: Active next implementation task is `TASK-2026-02-13-meld-validation-gate-microprofile`.

- TYPE: FACT
- CLAIM: New optimization wave scaffold exists as one epic plus five discovery-first stories with one discovery task per story.
- EVIDENCE: `context_compass/epics/2026-02-13_optimize_melder_epic.md:1`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:1`, `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:1`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:1`, `context_compass/stories/2026-02-13_optimize_phase12_codegen_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute discovery tasks and expand each story with implementation tasks ranked by measured impact/risk.

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| context_compass documentation integrity audit | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_context_compass_documentation_integrity_audit_task.md` | 2026-02-14 | HELPFUL |
| context_compass packaging migration | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_context_compass_rename_and_profile_config_task.md` | 2026-02-14 | HELPFUL |
| onboarding policy hardening | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_onboarding_policy_ticket_note_enforcement_task.md` | 2026-02-14 | HELPFUL |
| meld dynamic gate fastdoor | review | codex | none | waiting for user acceptance | `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md` | 2026-02-14 | HELPFUL |
| meld validation gate microprofile | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md` | 2026-02-14 | HELPFUL |
| meld override shape hotpath | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md` | 2026-02-14 | HELPFUL |
| meld input resolution keypath | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md` | 2026-02-13 | HELPFUL |
| meld contract defaults caching | blocked_out_of_scope | codex | user de-scoped this area for now | none | `context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md` | 2026-02-13 | HELPFUL |
| mutation research runtime wiring | blocked_out_of_scope | codex | user de-scoped this area for now | none | `context_compass/stories/2026-02-13_mutation_research_runtime_wiring_story.md` | 2026-02-13 | HELPFUL |
| resolution style matrix source of truth | closed | codex | none | none | `context_compass/stories/completed/2026-02-13_resolution_style_matrix_source_of_truth_story_completed.md` | 2026-02-13 | HELPFUL |
| spellstate advanced flag producers | closed | codex | none | none | `context_compass/stories/completed/2026-02-13_spellstate_advanced_flag_producers_story_completed.md` | 2026-02-13 | HELPFUL |
| revalidate src_architecture document | closed | codex | none | none | `context_compass/epics/2026-02-13_revalidate_src_architecture_document_epic.md` | 2026-02-13 | HELPFUL |
| revalidate src_components document | closed | codex | none | none | `context_compass/epics/2026-02-13_revalidate_src_components_document_epic.md` | 2026-02-13 | HELPFUL |
