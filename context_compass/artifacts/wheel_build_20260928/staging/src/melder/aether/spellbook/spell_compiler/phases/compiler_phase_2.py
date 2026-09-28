from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)



class CompilerPhase2:
    """
    Compiler phase 2 surface.

    Purpose:
        Expose the current symbolic-graph build behaviour through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-2 behaviour.
        - Does not own spell, artifact, or runtime collaborator lifecycle.
    """

    __slots__ = ()

    def run(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 2 - Build the symbolic dependency graph for this Spell.

        Responsibilities:
            * Consume Phase 1 requirements and construct a: class:`SpellSymbolicGraph` describing all constructor sockets.
            * Create one: class:`SpellSymbolicDependency` per constructor
              parameter that should be represented as a socket, including:
                  - plain (caller-supplied) parameters,
                  - normal DI sockets (single, collection, SpellMap),
                  - SpellContract sockets,
                * Store the symbolic graph on this compiler artifact
                  (`artifact._symbolic_graph`) for later phases.

        Contracts:
            * Phase 1 (requirements) must already have run successfully.
              This method will raise if requirements are missing; it does
              **not** auto-run Phase 1.
            * Does **not** build any concrete DAG or talk to SpellSystemStates.
            * Does **not** mutate the Spell. It only updates this compiler
              artifact's phase-2 state.
            * Does not return a value; consumers read
              `artifact._symbolic_graph`.

        Args:
            spell:
                Spell whose symbolic graph is being built.
            artifact:
                Compiler artifact receiving phase-2 output.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Raises:
            RuntimeError:
                If requirements are missing or the spell is missing, a bound
                current spell id.
        """
        artifact.check_cleaned()
        CompilerPhaseUtility.throw_if_cancelled(cancel_event)

        # Phase 2 is an explicit continuation from Phase 1 and must not infer
        # requirements.
        if artifact._requirements is None:
            raise RuntimeError(
                "SpellCrafter Phase 2: cannot build symbolic graph before "
                "Phase 1 requirements have completed."
            )

        # Versioned identity from SpellIndex.
        spell_id = spell.spell_index.selected_spell_id
        if spell_id is None:
            raise RuntimeError("SpellCrafter requires a bound spell current id.")

        deps: List[SpellSymbolicDependency] = []

        for param in artifact._requirements.parameters:
            di_shape: ParameterDIShape = param.di_shape
            contract_key = None

            # Only shapes that participate in the symbolic socket graph.
            if di_shape not in (
                    ParameterDIShape.SINGLE_BY_ANNOTATION,
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    ParameterDIShape.SPELLMAP_DEFAULT,
                    ParameterDIShape.PLAIN,
                    ParameterDIShape.SPELL_CONTRACT,
            ):
                # Shapes like IGNORE do not participate in sockets.
                continue

            # Map shape -> symbolic metadata.
            if di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                target_annotation = None
                is_collection = False
                spellmap_default = param.spellmap_default

            elif di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                target_annotation = param.collection_element_annotation
                is_collection = True
                spellmap_default = None

            elif di_shape is ParameterDIShape.PLAIN:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.SPELL_CONTRACT:
                # Contract socket.
                #
                # For now, we reuse the raw annotation as the "target" so that
                # later phases (5-7) can infer what this contract is over,
                # without committing to any specific resolution semantics yet.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None
                if isinstance(param.default_value, SpellContract):
                    contract_key = param.default_value.canonical_key

            else:
                # Should not happen given the filter above, but kept for
                # robustness.
                continue

            dep = SpellSymbolicDependency(
                spell_id=spell_id,
                param_name=param.name,
                position=param.position,
                di_shape=di_shape,
                is_optional=param.is_optional,
                target_annotation=target_annotation,
                is_collection=is_collection,
                spellmap_default=spellmap_default,
                contract_key=contract_key,
            )
            deps.append(dep)

        artifact._symbolic_graph = SpellSymbolicGraph(
            spell_id=spell_id,
            dependencies=deps,
        )
        # NOTE: the eager `capture_phase2_5_codegen_ir` export that used to
        # run here (and in phases 3-5) was removed: the snapshot had no
        # production readers and `reset_phase2_5_codegen_ir` discarded it at
        # the end of the same resolution pass. The capture helper remains in
        # SharedCompilerExecutions as the seam for a future incremental
        # recompile path; call it on demand if that path materializes.
