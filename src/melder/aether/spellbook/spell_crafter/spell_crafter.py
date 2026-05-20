from typing import Any, Dict, Optional

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_1 import (
    CompilerPhase1,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_10 import (
    CompilerPhase10,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_11 import (
    CompilerPhase11,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_12 import (
    CompilerPhase12,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_2 import (
    CompilerPhase2,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_3 import (
    CompilerPhase3,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_4 import (
    CompilerPhase4,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_5 import (
    CompilerPhase5,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_6 import (
    CompilerPhase6,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_7 import (
    CompilerPhase7,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_8 import (
    CompilerPhase8,
)
from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_9 import (
    CompilerPhase9,
)
from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
)
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.interfaces.ispellvalidationsystem import ISpellValidationSystem
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class SpellCrafter:
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

    __slots__ = (
        "_phase_1",
        "_phase_2",
        "_phase_3",
        "_phase_4",
        "_phase_5",
        "_phase_6",
        "_phase_7",
        "_phase_8",
        "_phase_10",
        "_phase_9",
        "_phase_11",
        "_phase_12",
    )

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
        self._phase_1 = CompilerPhase1()
        self._phase_2 = CompilerPhase2()
        self._phase_3 = CompilerPhase3()
        self._phase_4 = CompilerPhase4()
        self._phase_5 = CompilerPhase5()
        self._phase_6 = CompilerPhase6()
        self._phase_7 = CompilerPhase7()
        self._phase_8 = CompilerPhase8()
        self._phase_10 = CompilerPhase10()
        self._phase_9 = CompilerPhase9()
        self._phase_11 = CompilerPhase11()
        self._phase_12 = CompilerPhase12()

    def run_phase_requirements(
            self,
            spell: ISpell,
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
            spell: ISpell,
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spell_validator: ISpellValidationSystem,
            spell_system_states: Optional[ISpellSystemStates],
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
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
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
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
            spellbook: ISpellbook,
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
            spellbook: ISpellbook,
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: Optional[ISpellSystemStates],
    ) -> None:
        """
        Run compiler phase 8 (occurrence plan).

        Purpose:
            Build occurrence plans from resolved blueprints and phase-6 status.

        Contract:
            - Requires phase-6 validation output where applicable.
            - Stores computed occurrence plans for subsequent injection planning.
            - Supports optional cancellation during graph expansion and hashing.

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
        self._phase_8.run(
            spell,
            artifact,
            spellbook,
            spell_system_states,
        )

    def run_phase_injection_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Phase 9 - Injection plan compilation.
            
            Compiles an InjectionPlan for spells using Phase-8 occurrence plans.
            Existing-creation spells are treated as a no-op.
            
            Purpose:
                Precompute dependency-to-parameter wiring so meld can inject without
                recomputing occurrence-driven dependency paths at runtime.
            
            Contract:
                - Requires Phase 8 artifacts to be available.
                - Builds plan only when an occurrence plan is attached for this spell.
                - Replaces any existing InjectionPlan for this spell.
                - Does not mutate the occurrence plan.
            
            Args:
                conduit_id:
                    Conduit identifier used to scope resolution artifacts.
                cancel_event:
                    Optional cancellation signal shared across the scheduler.
            
            Returns:
                None.
            
            Raises:
                ValueError:
                    If conduit_id is empty.
                RuntimeError:
                    If Phase 8 artifacts are missing for this spell, or if the
                    root blueprint is missing for this spell.
                OperationCancelledError:
                    If cancel_event signals cancellation.
            
            Threading:
                - Not thread-safe; expected to run under spellbook phase scheduling.
            
            Lifecycle:
                - Replaces any prior InjectionPlan reference for this spell.
                - Prior plan objects are cleaned during SpellCrafter teardown.
        """
        self._phase_9.run(
            spell,
            artifact,
        )

    def run_phase_patch_maps(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
            Phase 10 - Patch map compilation.
            
            Compiles override and mutation patch maps for spells using
            Phase-5 blueprints. Existing-creation spells are treated as a no-op.
            
            Purpose:
                Precompute override and mutation targeting so meld can apply
                TargetSpec overrides without scanning the blueprint every call.
            
            Contract:
                - Requires Phase 5 artifacts to be available.
                - Builds maps only when a blueprint is attached for this spell.
                - Replaces any existing patch maps for this spell.
                - Does not mutate the root blueprint.
            
            Args:
                conduit_id:
                    Conduit identifier used to scope resolution artifacts.
                cancel_event:
                    Optional cancellation signal shared across the scheduler.
            
            Returns:
                None.
            
            Raises:
                ValueError:
                    If conduit_id is empty.
                RuntimeError:
                    If Phase 5 artifacts are missing or the root blueprint is missing
                    for this spell.
                OperationCancelledError:
                    If cancel_event signals cancellation.
            
            Threading:
                - Not thread-safe; expected to run under spellbook phase scheduling.
            
            Lifecycle:
                - Replaces any prior patch map references for this spell.
                - Prior map objects are cleaned during SpellCrafter teardown.
        """
        self._phase_10.run(
            spell,
            artifact,
        )

    def run_phase_execution_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
    ) -> None:
        """
        Run compiler phase 11 (execution plan).

        Purpose:
            Build final execution plans for spell invocation from all prior phase
            artifacts and spellbook context, then materialize the phase-12
            no-overrides executor from the artifact handoff.

        Contract:
            - Requires phase-8 to phase-10 outputs for complete plan synthesis.
            - Stores phase-11 execution plans on the artifact for downstream
              runner/executor compilation.
            - Preserves the internal phase-11/12 split, but keeps the front
              execution-plan entrypoint execution-ready by immediately compiling
              the phase-12 no-overrides executor after phase 11 completes.
            - Honors cancellation while constructing runtime execution structure.

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
        self._phase_11.run(
            spell,
            artifact,
            spellbook,
        )
        self._phase_12.compile_no_overrides_executor(
            spellbook,
            spell,
            artifact,
        )

    def compile_phase12_no_overrides_executor(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Compile the phase-12 no-overrides executor directly from artifact state.

        Purpose:
            Delegate to phase-12 executor synthesis using current phase-11 artifact
            state.

        Contract:
            - Requires phase-11 artifacts already present and compatible.
            - Writes the no-overrides executor and signature cache into the
              provided artifact.

        Args:
            spellbook:
                Spellbook providing explicit spell lookup context for payload
                compile fallback.
            spell:
                Spell whose executor is being compiled.
            artifact:
                Compiler artifact containing phase-11 execution-plan inputs.

        Returns:
            None.
        """
        self._phase_12.compile_no_overrides_executor(
            spellbook,
            spell,
            artifact,
        )

    def compile_phase12_no_overrides_executor_from_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            execution_plan: ExecutionPlan,
    ) -> None:
        """
        Compile the phase-12 no-overrides executor from a provided execution plan.

        Purpose:
            Build and cache a callable executor for an already-selected
            execution plan without recomputing plan state.

        Contract:
            - Uses the supplied plan directly and reuses artifact-owned runtime
              context.
            - Validates and updates signature cache metadata before writing the
              compiled callable.

        Args:
            spell:
                Spell for which executor code is being generated.
            artifact:
                Compiler artifact receiving the cached compiled callable.
            execution_plan:
                Concrete execution plan used to generate the executor.

        Returns:
            None.
        """
        self._phase_12.compile_no_overrides_executor_from_plan(
            spell,
            artifact,
            execution_plan,
        )

    def compile_phase12_no_overrides_executor_from_payload(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            no_overrides_payload: Dict[str, Any],
    ) -> None:
        """
        Compile the phase-12 no-overrides executor from raw payload data.

        Purpose:
            Synthesize a no-overrides executor and cache it using payload-provided
            execution-plan fields.

        Contract:
            - Allows direct compilation in payload-driven runners where the full
              execution-plan object is not pre-materialized.
            - Refreshes compile cache metadata according to the payload signature.

        Args:
            spellbook:
                Spellbook providing explicit spell lookup context for payload
                compilation.
            spell:
                Spell for which executor code is being generated.
            artifact:
                Compiler artifact receiving the compiled callable.
            no_overrides_payload:
                Serialized execution plan payload passed into phase-12.

        Returns:
            None.
        """
        self._phase_12.compile_no_overrides_executor_from_payload(
            spellbook,
            spell,
            artifact,
            no_overrides_payload,
        )
