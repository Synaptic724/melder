from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.creations.creations import Creations
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration


def test_add_conduit_to_aether_raises_when_aether_none(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify _add_conduit_to_aether rejects missing Aether registration.

    Contract:
        - Raises RuntimeError when Conduit._aether is None.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If missing Aether does not raise.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    previous = Conduit._aether
    try:
        Conduit._aether = None
        with pytest.raises(RuntimeError, match="Aether is not initialized"):
            conduit._add_conduit_to_aether()
    finally:
        Conduit._aether = previous
        conduit.cleanup()


def test_remove_conduit_from_aether_raises_when_aether_none(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify _remove_conduit_from_aether rejects missing Aether registration.

    Contract:
        - Raises RuntimeError when Conduit._aether is None.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If missing Aether does not raise.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    previous = Conduit._aether
    try:
        Conduit._aether = None
        with pytest.raises(RuntimeError, match="Aether is not initialized"):
            conduit._remove_conduit_from_aether()
    finally:
        Conduit._aether = previous
        conduit.cleanup()


def test_add_conduit_to_aether_delegates(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify _add_conduit_to_aether delegates to Aether.

    Contract:
        - Aether receives _add_conduit with conduit and frame.

    Args:
        conduit_normal (Conduit): Normal conduit under test.
        aether_stub (MagicMock): Aether stub for delegation checks.

    Raises:
        AssertionError: If delegation call is missing.
    """
    aether_stub.reset_mock()

    conduit_normal._add_conduit_to_aether()

    aether_stub._add_conduit.assert_called_once_with(conduit_normal, "default")


def test_remove_conduit_from_aether_delegates(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify _remove_conduit_from_aether delegates to Aether.

    Contract:
        - Aether receives _remove_conduit with conduit and frame.

    Args:
        conduit_normal (Conduit): Normal conduit under test.
        aether_stub (MagicMock): Aether stub for delegation checks.

    Raises:
        AssertionError: If delegation call is missing.
    """
    aether_stub.reset_mock()

    conduit_normal._remove_conduit_from_aether()

    aether_stub._remove_conduit.assert_called_once_with(conduit_normal, "default")


def test_add_spells_to_aether_registers_spell_indices(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify _add_spells_to_aether registers SpellIndex keys.

    Contract:
        - SpellIndex keys are passed as a set to Aether.

    Args:
        conduit_normal (Conduit): Normal conduit under test.
        aether_stub (MagicMock): Aether stub for registration checks.

    Raises:
        AssertionError: If Aether registration is incorrect.
    """
    spell_a = SpellIndex("sha-1")
    spell_b = SpellIndex("sha-2")
    conduit_normal._spellbook._spells = {
        spell_a: MagicMock(),
        spell_b: MagicMock(),
    }
    aether_stub.reset_mock()
    try:
        conduit_normal._add_spells_to_aether()
        aether_stub._add_spells_to_aether.assert_called_once_with(
            conduit_normal._id,
            {spell_a, spell_b},
            "default",
        )
    finally:
        spell_a.cleanup()
        spell_b.cleanup()


def test_add_spells_to_aether_raises_when_aether_none(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify _add_spells_to_aether rejects missing Aether registration.

    Contract:
        - Raises RuntimeError when Conduit._aether is None.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If missing Aether does not raise.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    previous = Conduit._aether
    try:
        Conduit._aether = None
        with pytest.raises(RuntimeError, match="Aether is not initialized"):
            conduit._add_spells_to_aether()
    finally:
        Conduit._aether = previous
        conduit.cleanup()


def test_creations_configuration_returns_creations_for_lesser(
    conduit_lesser: Conduit,
    configuration_automatic: SpellbookConfiguration,
) -> None:
    """
    Verify _creations_configuration returns Creations for lesser conduits.

    Contract:
        - Lesser conduits receive Creations instances.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.

    Raises:
        AssertionError: If the returned type is not Creations.
    """
    creations = conduit_lesser._creations_configuration(configuration_automatic)
    try:
        assert isinstance(creations, Creations)
    finally:
        creations.cleanup()


def test_creations_configuration_returns_creations(
    conduit_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
) -> None:
    """
    Verify _creations_configuration returns Creations for normal conduits.

    Contract:
        - Normal conduits receive Creations instances.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.

    Raises:
        AssertionError: If the returned type is not Creations.
    """
    creations = conduit_normal._creations_configuration(configuration_automatic)
    try:
        assert isinstance(creations, Creations)
    finally:
        creations.cleanup()


def test_creations_configuration_raises_for_unknown_state(
    conduit_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
) -> None:
    """
    Verify _creations_configuration rejects unknown conduit states.

    Contract:
        - Raises RuntimeError for unsupported conduit states.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.

    Raises:
        AssertionError: If unsupported state does not raise.
    """
    previous = conduit_normal._conduit_state
    try:
        conduit_normal._conduit_state = None
        with pytest.raises(RuntimeError, match="Conduit state is unknown"):
            conduit_normal._creations_configuration(configuration_automatic)
    finally:
        conduit_normal._conduit_state = previous


def test_qualify_contracts_raises_when_cleaned(
    conduit_normal: Conduit,
) -> None:
    """
    Verify _qualify_contracts rejects cleaned conduits.

    Contract:
        - Cleaned conduits raise RuntimeError.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If cleaned conduits do not raise.
    """
    conduit_normal.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        conduit_normal._qualify_contracts()


def test_qualify_contracts_raises_for_lesser(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify _qualify_contracts rejects lesser conduits.

    Contract:
        - Only normal conduits can manage contracts.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If lesser conduits do not raise.
    """
    with pytest.raises(RuntimeError, match="Only normal conduits can create spell contracts"):
        conduit_lesser._qualify_contracts()


def test_qualify_contracts_raises_when_not_dynamic(
    conduit_normal: Conduit,
) -> None:
    """
    Verify _qualify_contracts rejects non-dynamic environments.

    Contract:
        - Dynamic mode is required for contract APIs.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If non-dynamic conduits do not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal._qualify_contracts()


def test_qualify_contracts_allows_dynamic_normal(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify _qualify_contracts allows dynamic normal conduits.

    Contract:
        - No exception is raised for dynamic normal conduits.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If qualification raises unexpectedly.
    """
    conduit_dynamic_normal._qualify_contracts()
