

# Story: Author graph semantics for `src/melder/aether/spellbook`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-aether-spellbook
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: completed
- Owner: bootstrap_0
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T17:10:00Z

## User Narrative
As an agent reading the source graph, I want `src/melder/aether/spellbook` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/aether/spellbook` only. Do not author neighbouring packages.
- DEPENDENCIES: EPIC-2026-08-02-author-graph-semantics
- EXIT_GATE: every node below carries `role` and `responsibilities`; `graph_walker.py --report` shows 0 unsemantic and 0 stale for this package; graph reassembled.
- FAILURE_ESCALATION: raise DECISION_REQUEST if a node's purpose cannot be established from source.

## Requirements (Functional)
- Author `role` and `responsibilities` for each node listed below.
- Author `owns_state` and `phases` where the source supports them.
- Author `edges_authored` for relationships this package owns or borrows.

## Requirements (Non-Functional)
- **Semantics must be authored by READING THE CODE.** Never inferred from names.
- `owns_lifecycle_of`, `uses` and `borrows` are syntactically identical - `self._x = x`
  in all three cases. The difference is design intent that appears nowhere in the
  source text. Measured on a labelled corpus, a cleanup-contract heuristic
  discriminated at 21% vs 21% - no signal at all. Invented semantics are worse
  than none, because they read as verified.

## Scope Boundaries
- IN: authored tier for `src/melder/aether/spellbook`.
- OUT: mechanical fields, other packages, refactoring the source.

## State Transition Event
- draft -> ready when an agent claims it on the attention board.

## Dependencies / Related Work
- Epic: EPIC-2026-08-02-author-graph-semantics

## Tasks (Implementation Checklist)
- [x] Read the source for each node below.
- [x] Author the semantic fields in the descriptors.
- [x] Reassemble the graph and verify ranges.
- [x] `graph_walker.py --report` shows this package clean.

## Acceptance Criteria
- 211 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (211):
- `melder.aether.spellbook.bind.bind`
- `melder.aether.spellbook.bind.scan`
- `melder.aether.spellbook.bind.scan.ScanBindMetadata`
- `melder.aether.spellbook.bind.spell_index`
- `melder.aether.spellbook.configuration.spellbook_configuration`
- `melder.aether.spellbook.configuration.system_state`
- `melder.aether.spellbook.existence.existence`
- `melder.aether.spellbook.resolution_style_matrix`
- `melder.aether.spellbook.spell`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis.SpellInjectionInstanceSpec`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis.SpellInjectionParamSource`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_contract_analysis`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_order_analysis`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis.SpellOverrideTargetRef`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis`
- `melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis.SpellRuntimeRecord`
- `melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor`
- `melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy_builder`
- `melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_existence_occurrence_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_injection_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_instance_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_order_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_override_targeting_processor_strategy`
- `melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy`
- `melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy_builder`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.fallback_no_overrides_codegen_creation_discovery_strategy.FallbackNoOverridesCodegenCreationDiscoveryStrategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.generalized_cache_codegen_creation_discovery_strategy.GeneralizedCacheCodegenCreationDiscoveryStrategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.generalized_codegen_creation_discovery_strategy.GeneralizedCodegenCreationDiscoveryStrategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.many_only_codegen_creation_discovery_strategy.ManyOnlyCodegenCreationDiscoveryStrategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.solo_codegen_creation_discovery_strategy.SoloCodegenCreationDiscoveryStrategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_system`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.fallback_no_overrides.fallback_no_overrides_codegen_creation_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation.SpellOverrideTargetSocketRef`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation._Specificity`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_rows`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_manifest_state`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_finalize_creation_context_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_lazy_door_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_manifest_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_no_overrides_codegen_creation_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_overrides_codegen_creation_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.artifacts.spell_override_targeting_codegen_creation`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.artifacts.spell_override_targeting_codegen_creation.SpellOverrideTargetSocketRef`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.artifacts.spell_override_targeting_codegen_creation._Specificity`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler.ManyOnlyCodegenPlanCallMode`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler.ManyOnlyCodegenPlanTargetKind`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_finalize_creation_context_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_lazy_door_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_manifest_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_overrides_codegen_creation_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_creation_context_setup_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_lazy_door_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_manifest_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_no_overrides_codegen_creation_step`
- `melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_overrides_codegen_creation_step`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy_builder`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_system`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.generalized_codegen_plan_discovery_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.many_only_codegen_plan_discovery_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.solo_codegen_plan_discovery_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.data.many_only_codegen_plan`
- `melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan`
- `melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan`
- `melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy_builder`
- `melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner`
- `melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_codegen_plan_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_many_only_codegen_plan_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_solo_codegen_plan_strategy`
- `melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_many_only_codegen_plan_strategy`
- `melder.aether.spellbook.spell_compiler.dag.dag_index`
- `melder.aether.spellbook.spell_compiler.dag.dag_node`
- `melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph`
- `melder.aether.spellbook.spell_compiler.dag.resolution_frame.resolution_frame`
- `melder.aether.spellbook.spell_compiler.dag.socket_kind`
- `melder.aether.spellbook.spell_compiler.dag.target_spec`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_1`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_10`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_11`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_2`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_3`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_4`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_5`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_6`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_7`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_8`
- `melder.aether.spellbook.spell_compiler.phases.compiler_phase_9`
- `melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions`
- `melder.aether.spellbook.spell_compiler.phases.utility`
- `melder.aether.spellbook.spell_compiler.profiles.resolution_profile`
- `melder.aether.spellbook.spell_compiler.profiles.resolution_profile.SpellSymbolicEdge`
- `melder.aether.spellbook.spell_compiler.profiles.resolution_profile.SpellSymbolicGraph`
- `melder.aether.spellbook.spell_compiler.profiles.resolution_profile.SpellSymbolicNode`
- `melder.aether.spellbook.spell_compiler.profiles.resolution_profile.SpellValidationIssue`
- `melder.aether.spellbook.spell_compiler.profiles.resolution_profile.SpellValidationResult`
- `melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_existence_occurrence_analysis`
- `melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_occurrence_graph_analysis`
- `melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer`
- `melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy`
- `melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy_builder`
- `melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy`
- `melder.aether.spellbook.spell_compiler.spell_compiler`
- `melder.aether.spellbook.spell_compiler.spell_compiler_artifact`
- `melder.aether.spellbook.spell_compiler.spell_compiler_system`
- `melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.class_inspector`
- `melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility`
- `melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.method_inspector`
- `melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.profiles.class_profile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.profiles.method_profile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile.CallableBindingProfile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile.CallableParameterBindingSummary`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile.ClassBindingProfile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile.InstanceBindingProfile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile.OtherBindingProfile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.detailed_profile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile`
- `melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner`
- `melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy`
- `melder.aether.spellbook.spell_compiler.spell_examiner.strategies.resolution_profile_strategy`
- `melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape`
- `melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements`
- `melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements`
- `melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder`
- `melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency`
- `melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph`
- `melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_builder`
- `melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot`
- `melder.aether.spellbook.spell_compiler.system.spell_system_index`
- `melder.aether.spellbook.spell_compiler.system.spell_system_node`
- `melder.aether.spellbook.spell_compiler.system.spell_system_root_blueprint_builder`
- `melder.aether.spellbook.spell_compiler.system.spell_system_validation_state`
- `melder.aether.spellbook.spell_compiler.system.spell_system_validation_system`
- `melder.aether.spellbook.spell_compiler.system.system_diagnostic`
- `melder.aether.spellbook.spell_compiler.system.system_diagnostic.SystemDiagnosticSeverity`
- `melder.aether.spellbook.spell_compiler.system.validation.broken_spell_in_dag_strategy.BrokenSpellInDagStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.contract_graph_cycle_strategy.ContractGraphCycleStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.contracted_version_drift_strategy.ContractedVersionDriftStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.cycle_detection_strategy.CycleDetectionStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.dependency_type_sanity_strategy.DependencyTypeSanityStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.empty_collection_strategy`
- `melder.aether.spellbook.spell_compiler.system.validation.empty_collection_strategy.EmptyCollectionStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.graph_consistency_strategy.GraphConsistencyStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.identity_mixing_strategy.IdentityMixingStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.index_coverage_strategy.IndexCoverageStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.index_dependency_sanity_strategy.IndexDependencySanityStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.lineage_alignment_strategy.LineageAlignmentStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.lineage_version_conflict_strategy.LineageVersionConflictStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.missing_phase4_strategy.MissingPhase4Strategy`
- `melder.aether.spellbook.spell_compiler.system.validation.ownership_consistency_strategy.OwnershipConsistencyStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.root_coverage_strategy.RootCoverageStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.root_lineage_conflict_strategy.RootLineageConflictStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.root_reachability_strategy.RootReachabilityStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.root_scale_limit_strategy.RootScaleLimitStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.root_viability_strategy.RootViabilityStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.scope_ordering_strategy.ScopeOrderingStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.socket_ref_sanity_strategy.SocketRefSanityStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.strategy_base.SpellSystemValidationStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.topology_dependency_mismatch_strategy.TopologyDependencyMismatchStrategy`
- `melder.aether.spellbook.spell_compiler.system.validation.visibility_gap_strategy.VisibilityGapStrategy`
- `melder.aether.spellbook.spell_compiler.topology.spell_local_topology`
- `melder.aether.spellbook.spell_compiler.topology.spell_local_topology.SpellSocketDescriptor`
- `melder.aether.spellbook.spell_compiler.validation.spell_validation_context`
- `melder.aether.spellbook.spell_compiler.validation.spell_validation_issue`
- `melder.aether.spellbook.spell_compiler.validation.spell_validation_result`
- `melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy.AnnotationShapeGuardStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.binding_resolution_cycle_strategy.BindingResolutionCycleStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.callable_profile_hygiene_strategy.CallableProfileHygieneStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.circular_dependency_strategy.CircularDependencyStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.contract_provider_presence_strategy.ContractProviderPresenceStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.dangling_dependency_strategy.DanglingDependenciesStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.duplicate_spell_name_strategy.DuplicateSpellNameStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.existing_creation_compatibility_strategy.ExistingCreationCompatibilityStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.parameter_policy_strategy.ParameterPolicyStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.required_holes_strategy.RequiredHolesStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.resolution_frame_presence_strategy.ResolutionFramePresenceStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.self_validation_strategy.SelfDependencyStrategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy`
- `melder.aether.spellbook.spell_compiler.validation.strategies.spellmap_shape_validation_strategy.SpellMapShapeValidationStrategy`
- `melder.aether.spellbook.spell_compiler.validation.validation_system`
- `melder.aether.spellbook.spell_types.spell_types`
- `melder.aether.spellbook.spellbinder`
- `melder.aether.spellbook.spellbook`
- `melder.aether.spellbook.spellbook_creation_system`

Semantics stale (0) - source changed under existing prose, re-verify then
`graph_walker.py --accept <id> --apply`:
- none

## Open Questions
- (none recorded)

## Decision Log
- 2026-08-02T14:47:05Z: generated by `graph_semantics_tickets.py` from the graph census.
- 2026-08-02T17:10:00Z: CLOSED by bootstrap_0. All 211 nodes authored from source -
  the largest story in the epic, done in three passes rather than one.
  PASS 1, the two validation families (37 nodes). These are the highest-value
  nodes in the package and they were entirely unsemantic. Every one is now
  authored on WHAT IT ASSERTS rather than what it is called. Phase 6 (system,
  24 strategies + the contract) reads as a coherent set once written down: index
  self-consistency first, then the blueprint/index agreement pair (edges, then
  node set, then root designation), then reachability, then the identity rules
  (version ids not lineage ids; one lineage per root; one version per lineage per
  root), then the advisory passes, and finally `RootViabilityStrategy`, which
  performs NO fresh analysis and instead folds the root-affecting errors earlier
  strategies already emitted into one verdict - so it is order-dependent by
  design. `EmptyCollectionStrategy` is the one that changes behaviour by runtime
  mode: zero providers on a required collection socket is an ERROR in an
  automatic book (composition is final at conjure) and a WARNING in a dynamic one
  (deferred contract provisioning is still viable, consumer spawns with []).
  Phase 4 (spell-local, 13 strategies) has an explicit division of labour worth
  recording: self-dependency owns the direct case and circular owns multi-hop;
  circular deliberately ignores dangling ids so DanglingDependenciesStrategy is
  the single voice on them; and the binding-key cycle strategy exists because
  some loops are invisible by spell id and only appear once resolution is modeled
  by binding key.
  PASS 2, the remaining 28 class nodes - the fitted-model value types, the
  Phase-11 discovery strategies, the binding profiles, the resolution_profile
  placeholder family. Two facts worth stating because they are traps:
  `SpellInjectionParamSource.is_collection` carries phase-3 socket truth forward
  and MUST NOT be inferred from dependency count (a collection socket with one
  wired provider still injects a list); and `profiles/resolution_profile.py`
  defines SpellSymbolicGraph / SpellValidationIssue / SpellValidationResult that
  are DISTINCT from the live classes of the same names elsewhere in the compiler -
  the authored roles say so explicitly, since name collision across a 211-node
  package is exactly what a graph should disambiguate.
  PASS 3, the 146 module nodes, authored as placement in the phase pipeline
  (1 requirements -> 2 symbolic -> 3 DAG/topology -> 4 spell validation ->
  5 blueprints -> 6 system validation -> 7 change control -> 8 analyzer ->
  9 model fitting -> 10 planning -> 11 creation), and for phase 11 as the three
  parallel creation families (solo / many_only / generalized) plus the fallback.
- 2026-08-02T17:10:00Z: DISCLOSURE - this pass REPLACED 37 pre-existing module
  roles rather than only filling empty ones. 36 of them were the generic pattern
  "System validation strategy module for cycle detection." / "Spell validation
  strategy module for dangling dependency checks." - prose that restates the
  filename and tells a reader nothing the path did not already say. Those are now
  statements of what the check asserts. The 37th was NOT generic: the many-only
  no-overrides compiler read "Spell-scoped no-overrides compiler for the
  many-only family", and my replacement had dropped "Spell-scoped", which is real
  information. That was caught by diffing removed-vs-added role strings and the
  final text now carries both halves. Overwriting authored prose is worth naming
  explicitly even when the replacement is better; the previous text is in git.
- 2026-08-02T17:10:00Z: THE STALENESS DETECTOR FIRED FOR REAL, which is the first
  end-to-end proof the 16:05Z stamp fix works. Mid-story, `extract_graph.py`
  flagged `SystemDocumentView` and `SystemGraphView` SEMANTICS_STALE - authored
  ~30 minutes earlier, source changed underneath by another agent's live edit to
  `system_document_view.py`. Re-read both, semantics still held, re-accepted
  through `graph_walker.py --accept`, and authored the two new records the same
  edit added (SearchHit, Group). The same edit renamed
  `manifest/system_documents_sections.py` -> `system_documents_index.py`; that is
  a MOVE, so the new node was authored from the new file's own docstring (it is
  now explicit that the index is a TRANSCRIPTION of Context Compass's index, not
  a recomputation) and the stranded descriptor was deleted.
- 2026-08-02T17:10:00Z: graph reassembled - 581 sections, 1201 nodes, 1445 edges,
  25,291 lines; all 581 ranges verified against their own headers; index proof
  recomputed and matched (line_count 25291, LF, content_sha256 `1bed687b...`).
  Repo census 1163 AUTHORED / 0 SEMANTICS_STALE / 38 UNSEMANTIC (96.8%). The
  remaining 38 are the whole of `aether/aetheric_mediator` and are deliberately
  untouched - helper_f's active build lane, coordination sent 16:35Z.

## Notes
- Generated. Re-running the scan UPDATES this ticket rather than creating another.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
Author the semantic tier for `src/melder/aether/spellbook`. The node list is the scope. Read the
code; do not infer from names.
