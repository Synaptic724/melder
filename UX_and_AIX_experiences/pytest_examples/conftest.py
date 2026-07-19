"""
Per-test world isolation for the example harness - the exact pattern the
component suite uses: reset the Aether singleton and rebind the class
seams before AND after every test.
"""
import pytest

from melder import Aether, Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_world_per_example() -> None:
    """
    Purpose:
        Every example/probe runs in a FRESH world - no shared frames, no
        root-conduit name collisions across tests.
    Contract:
        - Mirrors tests/component .../cleanup_frame_truth fixture exactly.
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
