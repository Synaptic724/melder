from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.existence.existence import Existence


def _install_fresh_aether() -> None:
    """
    Purpose:
        Install a fresh Aether singleton for Spellbook and Conduit.
    Contract:
        - Resets the Aether singleton (which cleans up the previous one and its Nexus), creates a new one - and with
          it the Nexus that `Spellbook()` reaches through `Nexus()` - and binds Spellbook._aether and
          Conduit._aether to it.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """
    Purpose:
        Isolate each test from the Aether and Nexus singletons an earlier test in the same worker left behind.
    Contract:
        - Installs a fresh Aether before the test and again after it. Without this, a preceding teardown that reset
          the singletons without re-creating them left no initialized Nexus, and `Spellbook()` raised ValueError
          ("Nexus must be initialized with an Aether instance") in a parallel full run.
    Returns:
        Iterator[None]: Yields once, around the test.
    """
    _install_fresh_aether()
    yield
    _install_fresh_aether()


def test_spellbook_snapshot_state_returns_detached_maps() -> None:
    """
    Purpose:
        Validate snapshot_state returns detached registry copies.
    Contract:
        - Local spell maps are copied and safe to mutate.
        - Snapshot metadata fields are populated.
    Returns:
        None.
    Raises:
        AssertionError: If the snapshot leaks live state.
    """
    spellbook = Spellbook()

    class BasicService:
        """
        Purpose:
            Provide a minimal bindable class for snapshot testing.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service.
            Contract:
                - No side effects beyond construction.
            Returns:
                None.
            """
            return None

    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    snapshot = spellbook.snapshot_state()
    local_spells = snapshot["local_spells"]
    local_spells.clear()

    lookup_spells = snapshot["lookup_spells"]
    lookup_spells.clear()

    assert len(spellbook.spells) == 1
    assert len(spellbook._lookup_spells) == 1
    assert snapshot["spellbook_id"] == spellbook.id
    assert isinstance(snapshot["snapshot_id"], str)
    assert isinstance(snapshot["captured_at_ms"], int)
    assert spell_id in snapshot["spell_ids"]
    assert snapshot["contracted_spells"] == {}
    assert snapshot["lookup_contracted_spells"] == {}
    assert snapshot["contracted_spell_ids"] == {}
