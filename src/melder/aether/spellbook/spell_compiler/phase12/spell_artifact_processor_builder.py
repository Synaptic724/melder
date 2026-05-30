from typing import Any, Dict

from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.phase12.spell_artifact_processor_state import (
    SpellArtifactProcessorState,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class SpellArtifactProcessorBuilder:
    """
    Build `SpellArtifactProcessorState` from the full spell/artifact truth
    surface.

    Purpose:
        Centralize the Phase 12 consumption step so all processor strategies
        see one coherent, fully populated state object instead of reaching into
        `Spell` and `SpellCompilerArtifact` ad hoc.

    Contract:
        - Consumes the full current artifact surface, not only the later-added
          shape profiles.
        - Borrows references to heavyweight artifacts instead of duplicating
          them.
        - Normalizes spell-owned runtime facts into one grouped dictionary.
        - Leaves later semantic interpretation to the processor and plan
          strategy layers.

    Ownership:
        - Owns no runtime/compiler artifacts.
        - Produces a compiler-owned `SpellArtifactProcessorState`.

    Threading:
        - Pure builder surface with no shared mutable state.
    """

    __slots__ = ()

    @staticmethod
    def build(
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> SpellArtifactProcessorState:
        """
        Build one processor state from one spell/artifact pair.

        Purpose:
            Gather the full currently relevant Phase 12 truth surface into one
            grouped state object that later processor strategies can consume.

        Contract:
            - Consumes much more than the summary profiles. It also carries
              structural, rooted, planning, and handoff artifacts.
            - Preserves heavyweight artifact references instead of copying
              them.
            - Normalizes spell-owned runtime facts that still matter to Phase
              12 even though they do not belong on the artifact.

        Args:
            spell:
                Spell supplying runtime-owned facts that still matter to Phase
                12.
            artifact:
                Compiler-owned artifact supplying the phase caches and plan
                surfaces Phase 12 must consume.

        Returns:
            SpellArtifactProcessorState:
                Fully populated Phase 12 processor state.

        Raises:
            RuntimeError:
                Propagated from lower-level spell/artifact access if callers
                invoke the builder against an invalid or partially cleaned
                surface.
        """
        spell_facts: Dict[str, Any] = {
            "spell": spell,
            "spell_id": spell.spell_id,
            "spell_name": spell.spell_name,
            "spell_type": spell.spell_type,
            "existence": spell.existence,
            "is_existing_creation": spell.is_existing_creation,
            "has_mutation_override": spell.has_mutation_override,
            "requires_spellspace_request": spell.requires_spellspace_request,
            "execution_plan_dispatch_route": spell.execution_plan_dispatch_route,
            "resolution_required": spell.resolution_required,
            "resolution_complete": spell.resolution_complete,
            "owner_conduit_id": spell._owner_conduit_id,
            "owner_conduit_name": spell._owner_conduit_name,
            "owner_creations": spell._owner_creations,
            "creation_context": spell._creation_context,
            "creation_context_factory": spell._creation_context_factory,
            "creation_context_switch": spell._creation_context_switch,
        }

        compiler_structural_artifacts: Dict[str, Any] = {
            "requirements": artifact._requirements,
            "symbolic_graph": artifact._symbolic_graph,
            "resolution_frame": artifact._resolution_frame,
            "validation_result_phase4": artifact._validation_result_phase4,
            "validated_phase4": artifact._validated_phase4,
            "validation_result_phase6": artifact._validation_result_phase6,
            "validated_phase6": artifact._validated_phase6,
            "validated": artifact._validated,
            "is_broken": artifact._is_broken,
        }

        compiler_rooted_artifacts: Dict[str, Any] = {
            "root_blueprint_phase5": artifact._root_blueprint_phase5,
            "entire_dag_blueprint_phase5": artifact._entire_dag_blueprint_phase5,
            "spell_system_index_phase5": artifact._spell_system_index_phase5,
            "requires_spellspace_request_phase5": (
                artifact._requires_spellspace_request_phase5
            ),
        }

        compiler_planning_artifacts: Dict[str, Any] = {
            "occurrence_plan_phase8": artifact._occurrence_plan_phase8,
            "injection_plan_phase9": artifact._injection_plan_phase9,
            "override_patch_map_phase10": artifact._override_patch_map_phase10,
            "mutation_patch_map_phase10": artifact._mutation_patch_map_phase10,
            "execution_plan_phase11": artifact._execution_plan_phase11,
            "execution_plan_phase11_no_overrides": (
                artifact._execution_plan_phase11_no_overrides
            ),
            "execution_plan_phase11_overrides": (
                artifact._execution_plan_phase11_overrides
            ),
        }

        compiler_handoff_artifacts: Dict[str, Any] = {
            "phase11_no_overrides_plan_signature": (
                artifact._phase11_no_overrides_plan_signature
            ),
            "phase11_no_overrides_transient_schema": (
                artifact._phase11_no_overrides_transient_schema
            ),
            "phase13_no_overrides_executor": artifact._phase13_no_overrides_executor,
            "phase13_no_overrides_executor_signature": (
                artifact._phase13_no_overrides_executor_signature
            ),
            "phase11_no_overrides_input_signature": (
                artifact._phase11_no_overrides_input_signature
            ),
            "phase11_no_overrides_fast_key": artifact._phase11_no_overrides_fast_key,
            "codegen_ir": artifact._codegen_ir,
            "phase8_11_codegen_ir_dirty": artifact._phase8_11_codegen_ir_dirty,
        }

        shape_profiles: Dict[str, Any] = {
            "requirements_shape_profile_phase1": (
                artifact._requirements_shape_profile_phase1
            ),
            "occurrence_shape_profile_phase8": (
                artifact._occurrence_shape_profile_phase8
            ),
            "injection_shape_profile_phase9": (
                artifact._injection_shape_profile_phase9
            ),
            "override_shape_profile_phase10": (
                artifact._override_shape_profile_phase10
            ),
            "execution_shape_profile_phase11": (
                artifact._execution_shape_profile_phase11
            ),
        }

        compiler_metrics: Dict[str, Any] = {
            "execution_plan_step_count_phase11": (
                artifact._execution_plan_step_count_phase11
            ),
            "execution_plan_unique_spell_count_phase11": (
                artifact._execution_plan_unique_spell_count_phase11
            ),
            "execution_plan_max_occurrence_depth_phase11": (
                artifact._execution_plan_max_occurrence_depth_phase11
            ),
            "execution_plan_max_dependency_count_phase11": (
                artifact._execution_plan_max_dependency_count_phase11
            ),
            "execution_plan_has_calln_phase11": (
                artifact._execution_plan_has_calln_phase11
            ),
            "execution_plan_has_contract_payloads_phase11": (
                artifact._execution_plan_has_contract_payloads_phase11
            ),
            "execution_plan_has_existing_creations_phase11": (
                artifact._execution_plan_has_existing_creations_phase11
            ),
        }

        return SpellArtifactProcessorState(
            spell_id=spell.spell_id,
            spell_name=spell.spell_name,
            spell_facts=spell_facts,
            compiler_structural_artifacts=compiler_structural_artifacts,
            compiler_rooted_artifacts=compiler_rooted_artifacts,
            compiler_planning_artifacts=compiler_planning_artifacts,
            compiler_handoff_artifacts=compiler_handoff_artifacts,
            shape_profiles=shape_profiles,
            compiler_metrics=compiler_metrics,
        )
