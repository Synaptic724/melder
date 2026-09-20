"""Verify local compiler calls share the persistent scheduler's current cancellation scope."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )
    from melder.utilities.synchronization.unit_of_work import UnitOfWork


class _LocalService:
    """Provide a dependency-free construction target for local revalidation."""


@pytest.fixture(params=(1, 4))
def local_runtime(request: pytest.FixtureRequest) -> Iterator[tuple[Spellbook, Conduit, str]]:
    """Own one real book and its persistent pool, cleaning the runtime after each case.

    Args:
        request: Supplies the worker count for single-worker and parallel-pool cases.

    Yields:
        The live book, conduit and service identity used by the local compiler pipeline.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", request.param)
    book = Spellbook(configuration=configuration)
    conduit = None
    try:
        spell_id = book.bind(spell=_LocalService, existence=Existence.many, permissions="create")
        conduit = book.conjure(dynamic=True)
        yield book, conduit, spell_id
    finally:
        if conduit is not None:
            conduit.cleanup()
        else:
            book.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def test_local_revalidation_recovers_after_previous_scheduler_failure(
    local_runtime: tuple[Spellbook, Conduit, str],
) -> None:
    """A real failed run must not cancel the next local validation or prevent subsequent meld."""
    book, conduit, spell_id = local_runtime
    scheduler = book._get_or_create_phase_scheduler(PhaseScheduler)

    def fail_previous_run() -> None:
        """Raise the original failure that cancels one completed scheduler run."""
        raise ValueError("previous run failed")

    def failure_factory() -> list[UnitOfWork]:
        """Create the failing unit only after the scheduler installs its run scope."""
        return [scheduler.create_unit_of_work(fail_previous_run)]

    scheduler.register_phase("previous_failure", failure_factory)
    with pytest.raises(PhaseExecutionError, match="previous run failed"):
        scheduler.run_all_phases()

    book._run_resolution_phases_for_target_spell(conduit.id, book._spells_by_id[spell_id])
    assert isinstance(conduit.meld(spell_id=spell_id), _LocalService)


@pytest.mark.parametrize(
    "phase_method",
    ("run_phase_root_blueprints_local", "run_phase_system_validation_local"),
)
def test_local_phase_body_observes_current_run_cancellation(
    local_runtime: tuple[Spellbook, Conduit, str],
    monkeypatch: pytest.MonkeyPatch,
    phase_method: str,
) -> None:
    """Cancellation raised during a local phase must stop its body before further work."""
    book, conduit, spell_id = local_runtime
    scheduler = book._get_or_create_phase_scheduler(PhaseScheduler)
    outcomes: list[str] = []

    def cancel_during_phase(
        self: SpellCompilerSystem,
        spellbook: Spellbook,
        spell: Spell,
        conduit_id: str,
        cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """Inject cancellation at phase entry and observe whether cooperative work stops."""
        assert cancel_event is not None
        scheduler.cancel()
        try:
            cancel_event.throw_if_set()
        except OperationCancelledError:
            outcomes.append("cancelled")
            raise
        outcomes.append("continued after cancellation")

    monkeypatch.setattr(SpellCompilerSystem, phase_method, cancel_during_phase)
    with pytest.raises(PhaseSchedulerError):
        SpellbookCreationSystem._run_target_foundational_resolution_phases(
            spellbook=book,
            conduit_id=conduit.id,
            target_spell=book._spells_by_id[spell_id],
            target_spell_id=spell_id,
            phase_scheduler_cls=PhaseScheduler,
        )
    assert outcomes == ["cancelled"]
