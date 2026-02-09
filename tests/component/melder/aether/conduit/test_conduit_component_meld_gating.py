from __future__ import annotations

import threading

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_conduit_meld_gating() -> None:
    """
    Purpose:
        Ensure component Conduit meld gating tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component meld gating tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _make_dynamic_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for dynamic-mode component meld gating tests.
    Contract:
        - system_state is set to dynamic before Spellbook initialization.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_component_conduit_meld_blocks_dirty_root_change_control() -> None:
    """
    Purpose:
        Validate meld refuses to execute when change-control marks a root dirty.
    Contract:
        - Phase wiring builds the component-of index for the root.
        - ChangeControlManager marks the root dirty via notify_spell_changed.
        - Conduit.meld raises MeldExecutionError for the dirty root.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots do not block meld.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        conduit_id = conduit._id
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spell.run_all_phases(conduit_id)

        change_control_manager = spellbook._aether._get_change_control_manager(
            spellbook._aetheric_frame
        )
        assert change_control_manager is not None
        change_control_manager.notify_spell_changed(spell_id)
        assert change_control_manager.is_root_dirty(conduit_id, spell_id) is True

        with pytest.raises(MeldExecutionError, match="dirty"):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_component_conduit_meld_blocks_invalid_system_state() -> None:
    """
    Purpose:
        Validate meld rejects spells marked invalid by the system state.
    Contract:
        - SpellSystemState validity is set to invalid.
        - Conduit.meld raises SpellbookValidationError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid states are allowed to meld.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        state = spell.system_state
        assert state is not None
        state.set_validity(SpellValidity.invalid)

        with pytest.raises(SpellbookValidationError):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_component_conduit_meld_blocks_disabled_system_state() -> None:
    """
    Purpose:
        Validate meld rejects spells marked disabled by the system state.
    Contract:
        - SpellSystemState validity is set to disabled.
        - Conduit.meld raises SpellbookValidationError.
    Returns:
        None.
    Raises:
        AssertionError: If disabled states are allowed to meld.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        state = spell.system_state
        assert state is not None
        state.set_validity(SpellValidity.disabled)

        with pytest.raises(SpellbookValidationError):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_component_conduit_creation_gate_blocks_until_enabled() -> None:
    """
    Purpose:
        Validate CreationGate blocks melds until re-enabled.
    Contract:
        - disable_meld() blocks new meld calls.
        - enable_meld() releases blocked meld calls.
    Returns:
        None.
    Raises:
        AssertionError: If meld does not block or does not resume after enable.
    """
    spellbook = _make_dynamic_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        conduit.disable_meld()
        started = threading.Event()
        finished = threading.Event()
        result: dict[str, object] = {}

        def _worker() -> None:
            started.set()
            result["value"] = conduit.meld(spell=spell_id)
            finished.set()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        assert started.wait(0.5) is True
        assert finished.wait(0.05) is False

        conduit.enable_meld()
        assert finished.wait(0.5) is True
        assert isinstance(result["value"], BasicService)
    finally:
        conduit.cleanup()


def test_component_conduit_uses_devops_creation_gate_controller() -> None:
    """
    Purpose:
        Validate Conduit gate/controller wiring resolves through DevOpsManager.
    Contract:
        - Conduit uses the frame DevOps CreationGateController facade.
        - Root and lesser conduit gates are registered in the same controller.
        - Lesser conduit is indexed under the root conduit lineage id.
    Returns:
        None.
    Raises:
        AssertionError: If conduit gate wiring does not use DevOps controller.
    """
    spellbook = _make_dynamic_spellbook()
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root", automatic=False)
    lesser = None
    try:
        devops = spellbook._aether._get_devops_manager(spellbook._aetheric_frame)
        controller = devops.creation_gate_controller

        assert controller is not None
        assert conduit._creation_gate_controller is controller
        assert controller.get_conduit_gate(conduit._id) is conduit._creation_gate
        assert controller.get_root_conduit_id_for_conduit(conduit._id) == conduit._id

        lesser = conduit.create_lesser_conduit()
        assert lesser._creation_gate_controller is controller
        assert controller.get_conduit_gate(lesser._id) is lesser._creation_gate
        assert controller.get_root_conduit_id_for_conduit(lesser._id) == conduit._id
    finally:
        if lesser is not None:
            lesser.cleanup()
        conduit.cleanup()
