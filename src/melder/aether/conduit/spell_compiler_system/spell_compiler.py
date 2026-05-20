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
class SpellCompiler:
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
        Initialize the compiler-owned phase instances currently wired through
        phase 5.
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
        Run compiler phase 1 (requirements) for one spell.

        Purpose:
            Populate the phase-1 requirements artifact and cache it on the
            provided :class:`SpellCompilerArtifact`.

        Contract:
            - Does not consume local system state (phase 1 is spell-local only).
            - Honors cancellation via the optional signal while collecting
              requirements.
            - Leaves phase-2+ artifacts untouched for deferred execution.

        Args:
            spell:
                Spell to run requirements extraction against.
            artifact:
                Shared compiler artifact object that receives phase-1 data.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
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
        Run compiler phase 2 (symbolic graph construction).

        Purpose:
            Build and cache the symbolic graph from phase-1 requirements using
            the provided artifact.

        Contract:
            - Requires phase-1 requirements to be available on the artifact.
            - Produces symbolic constructor graph primitives that drive local
              DAG and dependency planning later.
            - Stores all phase-2 artifacts only on the shared artifact.

        Args:
            spell:
                Spell that currently owns the compiler artifact.
            artifact:
                Mutable compiler artifact receiving symbolic graph state.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
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
        Run compiler phase 3 (local frame + DAG).

        Purpose:
            Resolve local frame DAG artifacts for one conduit-spell context using
            the current spellbook and spell-system state view.

        Contract:
            - Requires phase-2 symbolic graph to exist on the artifact.
            - Writes resolved local-frame artifacts to the artifact for later
              validation and blueprint phases.
            - Uses the provided spell-system state to determine local
              visibility and topology constraints.

        Args:
            spell:
                Spell being compiled.
            artifact:
                Compiler artifact that stores phase-3 local frame artifacts.
            spellbook:
                Host spellbook context for local topology lookup.
            spell_system_states:
                Resolved system-state provider for visibility and topology
                queries.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
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
        Run compiler phase 4 (structural validation).

        Purpose:
            Execute phase-4 validation on the local frame artifacts and store
            the validation outcome for downstream behavior.

        Contract:
            - Accepts nullable spell-system state when phase-4 only needs static
              spell metadata.
            - May set broken-state signals on the artifact based on validation
              findings.
            - Keeps cancellation cooperative for long-running validations.

        Args:
            spell:
                Spell under validation.
            artifact:
                Shared compiler artifact to receive validation outputs.
            spell_validator:
                Validator implementation used by phase-4 checks.
            spell_system_states:
                Optional spell-system state provider used by validation rules.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
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
        self._phase_5.run(
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
            spell: ISpell,
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
        self._phase_6.run(
            spell,
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
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
        self._phase_7.run(
            spell,
            artifact,
            spellbook,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_change_control_local(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
            spell,
            artifact,
            spellbook,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_occurrence_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: Optional[ISpellSystemStates],
            cancel_event: Optional[CancellationEvent] = None,
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
            cancel_event=cancel_event,
        )

    def run_phase_injection_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run compiler phase 9 (injection plan).

        Purpose:
            Derive injection ordering and patch intent from previous planning data.

        Contract:
            - Requires phase-8 completion in normal execution order.
            - Produces immutable-like injector plans on the artifact for phase
              10 operations.
            - Uses cancellation token for long-running planning workloads.

        Args:
            spell:
                Spell for which to compile injection plans.
            artifact:
                Shared compiler artifact receiving phase-9 data.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_9.run(
            spell,
            artifact,
            cancel_event=cancel_event,
        )

    def run_phase_patch_maps(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run compiler phase 10 (patch map generation).

        Purpose:
            Convert injection plans into override and mutation patch maps used by
            runtime execution.

        Contract:
            - Requires phase-9 outputs to be present.
            - Emits patch-map artifacts consumed by phase-11 compilation.
            - Supports cooperative cancellation.

        Args:
            spell:
                Spell owning the compiler artifact.
            artifact:
                Compiler artifact receiving phase-10 patch maps.
            cancel_event:
                Optional cancellation signal for cooperative cancellation.

        Returns:
            None.
        """
        self._phase_10.run(
            spell,
            artifact,
            cancel_event=cancel_event,
        )

    def run_phase_execution_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Run compiler phase 11 (execution plan).

        Purpose:
            Build final execution plans for spell invocation from all prior phase
            artifacts and spellbook context.

        Contract:
            - Requires phase-8 to phase-10 outputs for complete plan synthesis.
            - Stores phase-11 execution plans on the artifact for downstream
              runner/executor compilation.
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
            cancel_event=cancel_event,
        )

    def compile_phase12_no_overrides_executor(
            self,
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
            spell:
                Spell whose executor is being compiled.
            artifact:
                Compiler artifact containing phase-11 execution-plan inputs.

        Returns:
            None.
        """
        self._phase_12.compile_no_overrides_executor(
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
            spell,
            artifact,
            no_overrides_payload,
        )
