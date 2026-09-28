# Object composition of `src/melder`

classes 612; with `__init__` 373; taking at least one package-class collaborator 155 (42% of those with an `__init__`); duplicate simple names 7; modules skipped 0

constructor parameters 1409, of which object collaborators 304 (22%) and plain data 1105

## Width: object collaborators per constructor (classes with an `__init__`)

| width | classes | share | ceiling if all singletons | ceiling if all transient |
| --- | ---: | ---: | ---: | ---: |
| 0 | 218 | 58% | 183 ns | 183 ns |
| 1 | 84 | 23% | 228 ns | 203 ns |
| 2 | 31 | 8% | 273 ns | 223 ns |
| 3-4 | 32 | 9% | 318 ns | 243 ns |
| 5-8 | 8 | 2% | 453 ns | 303 ns |
| 9-16 | 0 | 0% | 723 ns | 423 ns |
| 17+ | 0 | 0% | 1083 ns | 583 ns |

## Depth: longest collaborator chain below a class

| depth | classes |
| --- | ---: |
| 0 | 218 |
| 1 | 76 |
| 2 | 29 |
| 3 | 27 |
| 4 | 16 |
| 5 | 7 |

## Tree: distinct classes reachable through collaborators

| reachable classes | classes |
| --- | ---: |
| 0 | 218 |
| 1-2 | 89 |
| 3-5 | 21 |
| 6-10 | 32 |
| 11-20 | 13 |
| 21-50 | 0 |
| 51+ | 0 |

## Inheritance depth inside the package (MRO minus object and external bases)

| depth | classes |
| --- | ---: |
| 0 | 101 |
| 1 | 82 |
| 2 | 388 |
| 3 | 41 |

## Widest constructors (top 12)

| class | width | plain | module | collaborators |
| --- | ---: | ---: | --- | --- |
| SpellCodegenModel | 8 | 16 | aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py | Existence, SpellOccurrenceGraphAnalysis, SpellOccurrenceOrderAnalysis, SpellOccurrenceInstanceAnalysis, SpellOccurrenceContractAnalysis, SpellInjectionAnalysis, SpellSiteGraphAnalysis, SpellRuntimeAnalysis |
| Conduit | 7 | 8 | aether/conduit/conduit.py | Spellbook, SpellbookConfiguration, ConduitState, AethericFrame, Policies, CreationGateController, CreationGate |
| TransactionMediator | 6 | 2 | aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py | ChangeControlTransactionManager, ChangeControlConflictManager, ChangeControlEmbargoManager, ChangeControlOrchestrator, DevopsInformationRegistry, ChangeControlAdmissionResult |
| SpellSpaceMeld | 6 | 4 | aether/conduit/meld/spellspace_meld.py | SpellSpace, Creations, ConduitCreations, ConduitCreations, ClusterCreations, Spellbook |
| SpellValidationContext | 6 | 3 | aether/spellbook/spell_compiler/validation/spell_validation_context.py | Spell, Spellbook, SpellRequirements, SpellSymbolicGraph, SpellResolutionFrame, CancellationEvent |
| FrameACLProfile | 6 | 2 | nexus/acl/configurations/profiles/frame_acl_profile.py | FrameACLViewProfile, FrameACLCommandProfile, FrameACLCodegenProfile, FrameACLRuleSet, FrameACLRuleSet, FrameACLRuleSet |
| Spell | 5 | 10 | aether/spellbook/spell.py | SpellIndex, Existence, SpellType, Permissions, Spellbook |
| SpellResolutionProfile | 5 | 3 | aether/spellbook/spell_compiler/profiles/resolution_profile.py | Existence, SpellRequirements, SpellSymbolicGraph, SpellResolutionFrame, SpellValidationResult |
| ConduitWard | 4 | 1 | aether/conduit/conduit_ward/conduit_ward.py | Conduit, ConduitState, Policies, AethericFrame |
| Detail | 4 | 2 | aether/conduit/conduit_ward/contract/details.py | SpellIndex, Permissions, ContractTypes, DetailReason |
| IndexDetail | 4 | 2 | aether/conduit/conduit_ward/contract/details.py | SpellIndex, Permissions, ContractTypes, DetailReason |
| SpellSpace | 4 | 2 | aether/conduit/spell_space/spell_space.py | ConduitMeld, ConduitCreations, SpellSpacePool, SpellSpaceThreadState |

## Deepest chains (top 12)

| class | depth | tree | module |
| --- | ---: | ---: | --- |
| CodegenTransactionContext | 5 | 11 | nexus/rift/codegen_system/codegen_transaction_context.py |
| FrameProjectionSet | 5 | 11 | nexus/rift/projection/frame_projection_set.py |
| SpellSpaceMeld | 5 | 9 | aether/conduit/meld/spellspace_meld.py |
| CodegenCommandSystem | 5 | 9 | nexus/rift/command_system/codegen_command_system.py |
| ViewConduit | 5 | 9 | nexus/rift/frame_viewer/view_conduit.py |
| ViewSpell | 5 | 9 | nexus/rift/frame_viewer/view_spell.py |
| CodegenControlSurface | 5 | 8 | nexus/rift/codegen_system/namespace/codegen_control_surface.py |
| GeneralizedManifestState | 4 | 17 | aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_manifest_state.py |
| ManyOnlyCodegenCreationState | 4 | 17 | aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_state.py |
| SoloCodegenCreationState | 4 | 17 | aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_state.py |
| ManyOnlyCodegenPlanBuilder | 4 | 15 | aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py |
| SpellGeneralizedCodegenPlanBuilder | 4 | 15 | aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py |

## Largest trees (top 12)

| class | tree | width | depth | module |
| --- | ---: | ---: | ---: | --- |
| GeneralizedManifestState | 17 | 3 | 4 | aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_manifest_state.py |
| ManyOnlyCodegenCreationState | 17 | 3 | 4 | aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_state.py |
| SoloCodegenCreationState | 17 | 3 | 4 | aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_state.py |
| ManyOnlyCodegenPlanBuilder | 15 | 1 | 4 | aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py |
| SpellGeneralizedCodegenPlanBuilder | 15 | 1 | 4 | aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py |
| TransferOfOwnership | 14 | 3 | 3 | aether/conduit/conduit_ward/transfer/transfer_of_ownership.py |
| SpellCodegenModel | 14 | 8 | 3 | aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py |
| SpellDetailedProfile | 14 | 4 | 3 | aether/spellbook/spell_compiler/spell_examiner/profiles/detailed_profile.py |
| SpellValidationContext | 13 | 6 | 3 | aether/spellbook/spell_compiler/validation/spell_validation_context.py |
| SitePlanEmission | 12 | 3 | 4 | aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py |
| SpellGeneralProfile | 12 | 2 | 3 | aether/spellbook/spell_compiler/spell_examiner/profiles/general_profile.py |
| CodegenTransactionContext | 11 | 3 | 5 | nexus/rift/codegen_system/codegen_transaction_context.py |

