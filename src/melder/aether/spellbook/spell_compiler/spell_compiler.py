from typing import TYPE_CHECKING, Any, Dict, Optional, ClassVar
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


from melder.aether.spellbook.spell_compiler.phases.compiler_phase_1 import (
    CompilerPhase1,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_2 import (
    CompilerPhase2,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import (
    CompilerPhase3,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_4 import (
    CompilerPhase4,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import (
    CompilerPhase5,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_6 import (
    CompilerPhase6,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_7 import (
    CompilerPhase7,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.codegen_creation_system import (
    CodegenCreationSystem,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
    SpellCodegenPlanner,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer import (
    SpellAnalyzer,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spell_compiler.validation.validation_system import (
        SpellValidationSystem,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )




class SpellCompiler(Cleanable):
    """
    Compiler-owned facade over the extracted spell compiler phase surfaces.

    Purpose:
        Provide one reusable compiler object that owns the instantiated phase
        surfaces for spell compilation work while leaving generic and shared
        helper behavior on the static helper classes.

    Contract:
        - Owns no spell-scoped phase state itself.
        - Owns reusable instances of the extracted phase classes currently
          wired into the compiler path (`1-5` in this tranche).
        - Delegates already-ported phase behavior through those instance-owned
          phase surfaces.
        - Does not instantiate the static helper classes.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_phase_1",
        "_phase_2",
        "_phase_3",
        "_phase_4",
        "_phase_5",
        "_phase_6",
        "_phase_7",
        "_spell_analyzer",
        "_artifact_processor",
        "_codegen_planner",
        "_codegen_creation_system",
    ]

    def __init__(self) -> None:
        """
            Create a new SpellCrafter for one bound: class: 'Spell`.
            
            Contract:
                - Captures shared spell-owned services needed by later phases, such
                  as the spell validator and spell-system-state view.
                - Starts with empty artifact caches for all later phases.
                - Allows callers that already built a resolution profile to avoid
                  duplicating the first requirements extraction step.
        """
        super().__init__()
        self._phase_1 = CompilerPhase1()
        self._phase_2 = CompilerPhase2()
        self._phase_3 = CompilerPhase3()
        self._phase_4 = CompilerPhase4()
        self._phase_5 = CompilerPhase5()
        self._phase_6 = CompilerPhase6()
        self._phase_7 = CompilerPhase7()
        self._spell_analyzer = SpellAnalyzer()
        self._artifact_processor = SpellArtifactProcessor()
        self._codegen_planner = SpellCodegenPlanner()
        self._codegen_creation_system = CodegenCreationSystem()

    def cleanup(self) -> None:
        """
        Clean up all compiler-owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._phase_1
        del self._phase_2
        del self._phase_3
        del self._phase_4
        del self._phase_5
        del self._phase_6
        del self._phase_7
        self._spell_analyzer.cleanup()
        del self._spell_analyzer
        self._artifact_processor.cleanup()
        del self._artifact_processor
        self._codegen_planner.cleanup()
        del self._codegen_planner
        self._codegen_creation_system.cleanup()
        del self._codegen_creation_system



    def run_phase_requirements(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
            Phase 1 - Analyze the Spell constructor and capture DI requirements.
            
            Responsibilities:
                * Inspect the bound Spell's constructor and classify every parameter
                  into a: class:`ParameterDIShape` (normal DI, SpellMap, contracts, etc.).
                * Build a: class:`SpellRequirements` object that records per-parameter
                  metadata (name, position, shape, optionality, annotations).
                * Store the requirements on this SpellCrafter (``_requirements``) for
                  later phases to consume.
            
            Contracts:
                * Must only be called for a Spell that is fully constructed and
                  attached to a Spellbook.
                * Does **not** call any other phases. The caller is responsible for
                  running phases in order.
                * Does **not** mutate the Spell, SpellSystemStates, or any DAG
                  structures. It only updates this SpellCrafter's internal state.
                * Does not return a value; consumers read "self._requirements".
        """
        self._phase_1.run(
            spell,
            artifact,
            cancel_event=cancel_event,
        )

    def run_phase_symbolic_graph(
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
                      - MutationContract sockets.
                * Store the symbolic graph on this SpellCrafter
                  (``_symbolic_graph``) for later phases.
            
            Contracts:
                * Phase 1 (requirements) must already have run successfully.
                  This method will raise if requirements are missing; it does
                  **not** auto-run Phase 1.
                * Does **not** build any concrete DAG or talk to SpellSystemStates.
                * Does **not** mutate the Spell. It only updates this
                  SpellCrafter's internal state.
                * Does not return a value; consumers read "self._symbolic_graph".
        """
        self._phase_2.run(
            spell,
            artifact,
            cancel_event=cancel_event,
        )

    def run_phase_local_frame(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
            Phase 3 - Build the local-frame DAG and constructor topology.
            
            Responsibilities:
                * Consume Phase 1 requirements and Phase 2 symbolic graph for the
                  bound Spell.
                * Resolve **normal** DI sockets (single, collection, SpellMap)
                  against the Spellbook and build a **local-frame DAG** where:
                      - the root node is this Spell's version id, and
                      - direct edges represent first-hop constructor dependencies.
                * Track, per constructor parameter, which dependency spell ids were
                  bound during resolution.
                * Build a: class:`SpellLocalTopology` snapshot that describes all
                  sockets (normal, SpellContract, MutationContract) and their
                  concrete targets where applicable.
                * Register both:
                      - direct dependency spell ids, and
                      - the local topology
                  into: class:`SpellSystemStates`.
            
            Socket semantics:
                * Normal DI shapes (single, collection, SpellMap) produce DAG nodes,
                  DAG edges, and concrete "target_spell_ids" entries in topology.
                * SpellContract and MutationContract sockets are **metadata-only** at
                  this phase:
                      - they appear in the symbolic graph and topology,
                      - they do **not** produce DAG edges or bound targets yet.
                * Plain parameters are **metadata-only** at this phase:
                      - they appear in the symbolic graph and topology,
                      - they do **not** produce DAG edges or bound targets.
            
            Contracts:
                * Phases 1 and 2 must already have completed successfully. If
                  requirements or symbolic graph are missing, this method raises
                  instead of auto-running earlier phases.
                * Assumes the bound Spell is attached to a Spellbook; direct
                  Spellbook map iteration is used for resolution.
                * Stores the local DAG and direct dependency list on the Spell via: meth:`Spell._add_build_details`, and keeps a: class:`SpellResolutionFrame` internally on this SpellCrafter.
                * Does not return a value; callers rely on:
                      - "self._resolution_frame" for ordering, and
                      - SpellSystemStates for dependencies and topology.
        """
        self._phase_3.run(
            spell,
            artifact,
            spellbook,
            spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_validation(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spell_validator: SpellValidationSystem,
            spell_system_states: Optional[SpellSystemStates],
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
            Phase 4 - Per-spell validation using SpellValidationSystem.
            
            Responsibilities:
                * Assume Phases 1-3 have completed for this Spell.
                * Delegate to: class:`SpellValidationSystem` to validate this spell
                  using:
                      - Phase 1 requirements,
                      - Phase 2 symbolic graph,
                      - Phase 3 resolution frame.
                * Cache the resulting: class:`SpellValidationResult 'and expose it
                  via: attr:`validation_result`, :attr:`validated`,
                  and: attr:`is_broken`.
                * Update global structural validity (SpellSystemState) when available,
                  including gating spells with missing SpellContract providers.
            
            Contracts:
                * Does **not** call Phases 1-3. If any of the required artifacts
                  are missing, this method raises.
                * Does **not** mutate the Spell or build any DAGs. It only records
                  validation outcome and diagnostics on this SpellCrafter.
                * If the SpellSystemState is no longer valid (unknown/gated/invalid),
                  the validation is re-run even if this phase is previously completed.
                * Returns "None"; callers rely on the stored validation result and
                  flags instead of a direct return value.
        """
        self._phase_4.run(
            spell,
            artifact,
            spell_validator,
            spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_root_blueprints(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run compiler phase 5 (root blueprint compilation).

        Purpose:
            Build conduit-scoped root resolution blueprints from validated local
            frame data.

        Contract:
            - Requires phase-3/-4 artifacts to be present.
            - Produces conduit-scoped blueprint maps and conduit index data on
              the artifact.
            - Honors cancellation while compiling potentially large blueprints.

        Args:
            spell:
                Spell owning the current artifact.
            artifact:
                Mutable compiler artifact storing phase-5 output.
            spellbook:
                Host spellbook context used for root and dependency expansion.
            spell_system_states:
                Spell-system state provider for visibility and topology checks.
            conduit_id:
                Conduit identifier to scope blueprint artifacts.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_5.run_frame_wide(
            spell,
            artifact,
            spellbook,
            spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_root_blueprints_local(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run the local-only variant of phase 5.

        Purpose:
            Build locally scoped root blueprints without re-computing global
            spellbook-wide plan state where possible.

        Contract:
            - Same artifact inputs as the frame-wide phase-5 path, but restricted
              to local scope.
            - Keeps local-only side effects in the artifact for
              local-system-validation and change-control wiring.

        Args:
            spell:
                Spell owning the compilation artifact.
            artifact:
                Compiler artifact receiving local blueprint artifacts.
            spellbook:
                Host spellbook context.
            spell_system_states:
                Spell-system state provider for local checks.
            conduit_id:
                Conduit identifier to scope local blueprint state.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_5.run_local(
            spell,
            artifact,
            spellbook,
            spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_system_validation(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run compiler phase 6 (system validation).

        Purpose:
            Validate system-level invariants across root blueprints for the given
            conduit and persist resulting validation artifacts.

        Contract:
            - Depends on phase-5 artifacts and spell-system state.
            - Stores phase-6 validation state for downstream phase gating.
            - Supports cancellation for heavy validation workloads.

        Args:
            spell:
                Spell under system validation.
            artifact:
                Shared compiler artifact used by downstream phases.
            spellbook:
                Spellbook context for spell-id and root-resolution queries.
            spell_system_states:
                System state provider required for validation checks.
            conduit_id:
                Conduit identifier used to scope validation diagnostics.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_6.run_frame_wide(
            artifact,
            spellbook,
            spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_system_validation_local(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run the local-only variant of phase 6.

        Purpose:
            Execute system validation for local roots only, while retaining the
            same diagnostics contract as conduit-wide phase 6.

        Contract:
            - Requires local phase-5 artifacts to be present.
            - Produces phase-6 validation state only for local roots.
            - Supports cooperative cancellation.

        Args:
            spell:
                Spell owning the local compilation artifact.
            artifact:
                Compiler artifact that stores local validation output.
            spellbook:
                Spellbook context for local root coverage.
            spell_system_states:
                System state provider required for local validation rules.
            conduit_id:
                Conduit identifier that scopes validation writes.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_6.run_local(
            spell,
            artifact,
            spellbook,
            spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_change_control(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Run compiler phase 7 (change-control integration).

        Purpose:
            Wire change-control structures and revalidation hooks for conduit scope.

        Contract:
            - Requires completed phase-5 outputs.
            - Registers component-of/update hooks with the active spellbook
              infrastructure.
            - Keeps cancellation token threaded for parity with phase scheduler.

        Args:
            spell:
                Spell being compiled.
            artifact:
                Shared compiler artifact receiving phase-7 side effects.
            spellbook:
                Host spellbook where change-control artifacts are registered.
            conduit_id:
                Conduit identifier to scope change-control handles.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_7.run_frame_wide(
            artifact,
            spellbook,
            conduit_id,
        )

    def run_phase_change_control_local(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Run local-only phase-7 integration.

        Purpose:
            Apply local change-control upserts and register a local revalidator
            path consistent with frame-wide behavior.

        Contract:
            - Operates on local phase-5 artifacts.
            - Uses the same phase-7 hook contract as full execution.
            - Leaves global structures untouched beyond local spellbook scope.

        Args:
            spell:
                Spell owning the local compilation artifact.
            artifact:
                Shared artifact receiving local phase-7 state.
            spellbook:
                Spellbook owning local change-control managers.
            conduit_id:
                Conduit identifier for local revalidation scope.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_7.run_local(
            artifact,
            spellbook,
            conduit_id,
        )

    def run_phase_occurrence_plan(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: Optional[SpellSystemStates],
    ) -> None:
        """
        Run compiler phase 8 (occurrence plan).

        Purpose:
            Run the analyzer-owned occurrence analysis seam as the new live
            phase-8 substitute.

        Contract:
            - Consumes the existing spell/artifact pair.
            - Publishes analyzer-owned occurrence graph truth onto the artifact.
            - Ignores the old spellbook/system-state inputs because the analyzer
              already reads through the spell/artifact relationship.

        Args:
            spell:
                Spell being planned.
            artifact:
                Compiler artifact receiving phase-8 occurrence plan data.
            spellbook:
                Spellbook context for instance lookup and blueprint reuse.
            spell_system_states:
                Optional spell-system state for dynamic planning conditions.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        _ = spellbook
        _ = spell_system_states
        self._spell_analyzer.analyze_occurrence(spell, artifact)

    def run_phase_injection_plan(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Run the processor seam as the new live phase-9 substitute.

            Purpose:
                Build the processor-owned `SpellCodegenModel` from the existing
                analyzer and compiler artifact truth.
        """
        self._artifact_processor.process(spell, artifact)

    def run_phase_patch_maps(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Run the planner seam as the new live phase-10 substitute.

            Purpose:
                Build the planner-owned `SpellCodegenPlan` from the
                processor-owned model already attached to the artifact.
        """
        _ = spell
        self._codegen_planner.build(artifact)

    def run_phase_execution_plan(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
    ) -> None:
        """
        Run the codegen-creation seam as the new live phase-11 substitute.

        Purpose:
            Build the compiler-owned `SpellCodegenCreation` artifact from the
            planner-owned plan and processor-owned model so runtime binders can
            consume the new spell-static handoff.

        Contract:
            - Consumes the already-built model and plan from the artifact.
            - Publishes the codegen-creation artifact onto the spell compiler
              artifact.
            - Leaves the old compiler-facing phase-13 facade present but out of
              the main live path.

        Args:
            spell:
                Spell being compiled into executable form.
            artifact:
                Compiler artifact to receive execution plans.
            spellbook:
                Spellbook context used for root resolution and overrides.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        _ = spell
        _ = spellbook
        self._codegen_creation_system.build(artifact)


