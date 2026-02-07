from __future__ import annotations

from importlib import import_module

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations


class _ConduitStub:
    """
    Minimal conduit stub for Creations construction tests.
    """

    def __init__(self, *, conduit_id: str, conduit_state: ConduitState) -> None:
        self._id = conduit_id
        self._conduit_state = conduit_state


def test_lesser_creations_module_is_removed() -> None:
    """
    Purpose:
        Verify the legacy LesserCreations module is removed.
    Contract:
        Importing `melder.aether.conduit.creations.lesser_creations` raises.
    """
    with pytest.raises(ModuleNotFoundError):
        import_module("melder.aether.conduit.creations.lesser_creations")


def test_unified_creations_accepts_lesser_conduit_state() -> None:
    """
    Purpose:
        Verify lesser conduits now use unified Creations.
    Contract:
        Creations initializes and stores entries when state is lesser.
    """
    conduit = _ConduitStub(conduit_id="lesser-1", conduit_state=ConduitState.lesser)
    creations = Creations(conduit)
    try:
        creations.add_creation("spell-1", object())
        creations.add_many_creations("spell-2", object())
        assert "spell-1" in creations._creations
        assert "spell-2" in creations._creations
    finally:
        creations.cleanup()


def test_unified_creations_exposes_no_lesser_transfer_api() -> None:
    """
    Purpose:
        Verify legacy lesser-upgrade transfer APIs are gone.
    Contract:
        Creations does not expose `transfer_data_and_clear`.
    """
    conduit = _ConduitStub(conduit_id="lesser-1", conduit_state=ConduitState.lesser)
    creations = Creations(conduit)
    try:
        assert not hasattr(creations, "transfer_data_and_clear")
    finally:
        creations.cleanup()

