import logging
import sys
import time
from typing import Any, Dict, Tuple, Type

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import ISafeLogger
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from tests.mocks.spellbook.deep_layers import Depth9Root, get_depth_9_classes


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _build_test_logger() -> ISafeLogger:
    """
    Purpose:
        Build a SafeLogger that emits timing lines to stdout.
    Contract:
        - Uses a dedicated stdlib logger with a StreamHandler.
        - Returns a SafeLogger wrapper for consistent logging semantics.
    Returns:
        ISafeLogger: Safe logger that outputs to stdout.
    """
    logger = logging.Logger("phase_timing")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return InitHelpers.resolve_safe_logger(logger)


def _configure_scheduler(spellbook: Spellbook, workers: int) -> None:
    """
    Purpose:
        Configure the PhaseScheduler worker count for a Spellbook.
    Contract:
        - Sets the configuration property directly on the Spellbook.
    Args:
        spellbook: Spellbook instance to configure.
        workers: Worker count to set for phase scheduling.
    """
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", workers)


def _bind_classes(
        spellbook: Spellbook,
        classes: Tuple[Type[Any], ...],
        *,
        existence: Existence,
) -> Dict[Type[Any], str]:
    """
    Purpose:
        Bind a set of classes into a Spellbook.
    Contract:
        - Binds each class with the provided existence and create permission.
        - Returns a mapping of class -> spell_id.
    Args:
        spellbook: Spellbook to bind into.
        classes: Tuple of classes to bind.
        existence: Existence policy for bindings.
    Returns:
        Dict[Type[Any], str]: Mapping from class to spell_id.
    """
    spell_ids: Dict[Type[Any], str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


def _build_depth9_spellbook(frame_name: str, workers: int) -> Tuple[Spellbook, str]:
    """
    Purpose:
        Construct a depth-9 Spellbook fixture for phase timing.
    Contract:
        - Binds the depth-9 class set with unique existence.
        - Returns the Spellbook and root spell id.
    Args:
        frame_name: Aetheric frame name to use.
        workers: PhaseScheduler worker count to set.
    Returns:
        Tuple[Spellbook, str]: Spellbook instance and root spell id.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    _configure_scheduler(spellbook, workers)
    spell_ids = _bind_classes(
        spellbook,
        get_depth_9_classes(),
        existence=Existence.unique,
    )
    return spellbook, spell_ids[Depth9Root]


def _prepare_spellbook_for_phases(spellbook: Spellbook) -> None:
    """
    Purpose:
        Ensure the Spellbook is configured and bound to Aether before phase runs.
    Contract:
        - Validates and freezes configuration only if not already locked.
        - Binds configuration to Aether if needed.
        - Does not conjure a conduit or run phases.
    Args:
        spellbook: Spellbook to prepare for phase execution.
    """
    if not spellbook.is_configuration_locked():
        spellbook._validate_and_freeze_configuration()
        spellbook._bind_configuration_to_aether()


def _run_requirements_phase_only(spellbook: Spellbook) -> None:
    """
    Purpose:
        Execute Phase 1 (requirements) in isolation for timing.
    Contract:
        - Builds and runs a PhaseScheduler with only the requirements phase.
        - Cleans up the scheduler after execution.
        - Does not run any later phases.
    Args:
        spellbook: Spellbook that owns the phases.
    """
    scheduler = PhaseScheduler(
        spellbook=spellbook,
        configuration=spellbook.get_configuration(),
    )
    try:
        scheduler.register_phase(
            "requirements",
            lambda: spellbook._phase_requirements_factory(scheduler),
        )
        scheduler.run_all_phases()
    finally:
        try:
            scheduler.cleanup()
        except Exception:
            pass


def _run_root_blueprints_phase_only(spellbook: Spellbook, conduit_id: str) -> None:
    """
    Purpose:
        Execute Phase 5 (root_blueprints) in isolation for timing.
    Contract:
        - Builds and runs a PhaseScheduler with only the root_blueprints phase.
        - Requires Phases 1-4 to have completed for the Spellbook.
        - Cleans up the scheduler after execution.
    Args:
        spellbook: Spellbook that owns the phases.
        conduit_id: Conduit id used to scope phase artifacts.
    """
    scheduler = PhaseScheduler(
        spellbook=spellbook,
        configuration=spellbook.get_configuration(),
    )
    try:
        scheduler.register_phase(
            "root_blueprints",
            lambda: spellbook._phase_root_blueprints_factory(scheduler, conduit_id),
        )
        scheduler.run_all_phases()
    finally:
        try:
            scheduler.cleanup()
        except Exception:
            pass


def test_phase_requirements_root_blueprints_timing() -> None:
    """
    Purpose:
        Time Phase 1 (requirements) and Phase 5 (root_blueprints) in isolation
        for the depth-9 graph without cProfile instrumentation.
    Contract:
        - Logs timing lines via SafeLogger.
        - Does not assert on absolute performance thresholds.
    """
    logger = _build_test_logger()
    method_name = "test_phase_requirements_root_blueprints_timing"
    workers = 1

    spellbook_req, _ = _build_depth9_spellbook("profile-phase-requirements", workers)
    _prepare_spellbook_for_phases(spellbook_req)
    start = time.perf_counter()
    _run_requirements_phase_only(spellbook_req)
    requirements_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        f"Phase requirements (ms): {requirements_ms:.3f}",
        method_name,
    )

    spellbook_rb, _ = _build_depth9_spellbook("profile-phase-root-blueprints", workers)
    _prepare_spellbook_for_phases(spellbook_rb)
    spellbook_rb._run_structural_phases()
    spellbook_rb._define_disposal_metadata_on_spells()
    conduit_id = IDBuilder.create_id()
    start = time.perf_counter()
    _run_root_blueprints_phase_only(spellbook_rb, conduit_id)
    root_blueprints_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        f"Phase root_blueprints (ms): {root_blueprints_ms:.3f}",
        method_name,
    )

    assert requirements_ms >= 0.0
    assert root_blueprints_ms >= 0.0
