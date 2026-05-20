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
        self._phase_12.compile_no_overrides_executor_from_payload(
            spell,
            artifact,
            no_overrides_payload,
        )
