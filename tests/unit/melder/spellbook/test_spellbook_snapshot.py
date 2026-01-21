from melder.spellbook.spellbook import Spellbook
from melder.spellbook.existence.existence import Existence


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
    assert spell_id in snapshot["spell_versions"]
    assert snapshot["contracted_spells"] == {}
    assert snapshot["lookup_contracted_spells"] == {}
    assert snapshot["contracted_versions"] == {}
