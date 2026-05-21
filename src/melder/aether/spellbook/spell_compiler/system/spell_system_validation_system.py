from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Sequence,
    ClassVar,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
        SpellSystemIndex,
    )
    from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
        SystemDiagnostic,
    )
    from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
        SpellSystemValidationStrategy,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_compiler.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.utilities.general_base.cleanable import Cleanable

@mypyc_attr(native_class=True)
class SpellSystemValidationSystem(Cleanable):
    """
    Orchestrates system-level validation strategies over Phase 5 artifacts and Phase 4 outcomes.

    Purpose:
        Aggregate system-level validation diagnostics and update lineage validity
        for all spells in the current frame.
    Contract:
        - Strategies are executed in the order provided at construction.
        - Diagnostics are collected and returned via SpellSystemValidationState.
        - When conduit_id is provided, per-conduit resolution validity is set
          to VALID when no error diagnostics exist, and to INVALID when any
          error diagnostics are present.
        - Global structural validity is not modified by this class.
    Threading:
        Callers are responsible for external synchronization when sharing inputs
        across threads. This class does not introduce additional locking.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_strategies",
    ]

    def __init__(self, strategies: Iterable[SpellSystemValidationStrategy]) -> None:
        """
        Initialize the system-level validation orchestrator.

        Contract:
            - Requires a concrete iterable of validation strategies.
            - Stores the strategy list by value for deterministic execution
              order during `validate(...)`.
        """
        super().__init__()
        if strategies is None:
            raise ValueError("strategies must not be None.")
        self._strategies: Optional[List[SpellSystemValidationStrategy]] = list(
            strategies
        )

    def cleanup(self) -> None:
        """
        Release the configured validation strategies.

        Contract:
            - Idempotent: safe to call multiple times.
            - Clears the owned strategy list and drops the reference.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._strategies is not None:
            self._strategies.clear()
        self._strategies = None

    def validate(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Dict[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            conduit_id: Optional[str] = None,
            spell_lookup: Optional[Mapping[str, Spell]] = None,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> SpellSystemValidationState:
        """
        Run system-level validation and update per-lineage validity.

        Purpose:
            Validate the system-level DAG artifacts produced in Phase 5 and
            record a frame-wide validation verdict.
        Contract:
            - Executes each configured strategy in order against shared inputs.
            - Collects diagnostics across strategies into a single list.
            - Auto-populates diagnostic source attribution when missing.
            - When conduit_id is provided, marks per-conduit resolution validity
              VALID on success or INVALID on error diagnostics.
            - Returns a validation state containing all diagnostics and nodes.
        Args:
            index: Frame-level spell system index to validate.
            blueprints: Root blueprints keyed by root spell id.
            phase4_results: Phase-4 validation artifacts keyed by spell id.
            broken_spell_ids: Set of spell ids flagged as broken in Phase 4.
            spell_system_states: Registry used for topology and resolution state.
            conduit_id:
                Optional conduit identifier. When provided, diagnostics and
                per-conduit resolution validity are recorded in
                ConduitResolutionState. Global structural validity is not
                modified here.
            spell_lookup: Optional mapping of visible spell version ids to spell objects.
            cancel_event: Optional cancellation signal for long-running validation.
        Returns:
            SpellSystemValidationState: Aggregated diagnostics and validity.
        Raises:
            ValueError: If required inputs are None.
            Exception: Propagates cancellation exceptions or strategy errors.
        """
        self.check_cleaned()
        if index is None:
            raise ValueError("index must not be None.")
        if blueprints is None:
            raise ValueError("blueprints must not be None.")
        if spell_system_states is None:
            raise ValueError("spell_system_states must not be None.")
        if self._strategies is None:
            raise RuntimeError("Validation strategies have been cleaned.")

        if spell_lookup is None:
            spell_lookup = {}

        diagnostics: List[SystemDiagnostic] = []

        for strategy in self._strategies:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            before_count = len(diagnostics)
            strategy.run(
                index=index,
                blueprints=blueprints,
                phase4_results=phase4_results,
                broken_spell_ids=broken_spell_ids,
                spell_system_states=spell_system_states,
                spell_lookup=spell_lookup,
                diagnostics=diagnostics,
                cancel_event=cancel_event,
            )
            if len(diagnostics) > before_count:
                source = type(strategy).__name__
                for diag in diagnostics[before_count:]:
                    if isinstance(diag, SystemDiagnostic) and diag.source is None:
                        diag._source = source

        has_error = any(
            diag.severity is SystemDiagnosticSeverity.ERROR for diag in diagnostics
        )

        if conduit_id is not None:
            self._record_conduit_resolution_state(
                spell_system_states=spell_system_states,
                conduit_id=conduit_id,
                index=index,
                blueprints=blueprints,
                diagnostics=diagnostics,
                has_error=has_error,
            )

        errors = [
            diag for diag in diagnostics if diag.severity is SystemDiagnosticSeverity.ERROR
        ]
        warnings = [
            diag
            for diag in diagnostics
            if diag.severity is SystemDiagnosticSeverity.WARNING
        ]

        return SpellSystemValidationState(
            is_valid=not has_error,
            errors=errors,
            warnings=warnings,
            nodes=index.nodes,
        )

    def _record_conduit_resolution_state(
            self,
            *,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            index: SpellSystemIndex,
            blueprints: Mapping[str, RootResolutionBlueprint],
            diagnostics: Sequence[SystemDiagnostic],
            has_error: bool,
    ) -> None:
        """
        Record per-conduit resolution validity and diagnostics.

        When errors exist, all spells/roots are marked invalid for this conduit.
        On success, all spells/roots are marked valid and the conduit state is
        marked clean with a validation timestamp.
        """
        if conduit_id is None:
            return

        validity = SpellValidity.invalid if has_error else SpellValidity.valid
        change_reason = (
            SpellStateChangeReason.validation_failed
            if has_error
            else SpellStateChangeReason.validation_passed
        )

        spell_ids = list(index.nodes.keys())
        root_ids = list(blueprints.keys())

        try:
            spell_system_states.bulk_set_conduit_spell_validity(
                conduit_id,
                {spell_id: validity for spell_id in spell_ids},
                change_reason=change_reason,
            )
            spell_system_states.bulk_set_conduit_root_validity(
                conduit_id,
                {root_id: validity for root_id in root_ids},
                change_reason=change_reason,
            )
            spell_system_states.record_conduit_diagnostics(conduit_id, diagnostics)
            if not has_error:
                import time
                spell_system_states.clear_conduit_dirty(conduit_id, time.time())
        except Exception:
            # Resolution state is best-effort; diagnostics still returned to caller.
            return

