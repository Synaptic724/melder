import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_live_sim() -> None:
    """
    Purpose:
        Ensure live-sim integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before each test.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after each test for isolation.
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
