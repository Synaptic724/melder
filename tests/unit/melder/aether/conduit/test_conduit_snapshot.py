from melder.spellbook.spellbook import Spellbook
from melder.spellbook.existence.existence import Existence


def test_conduit_snapshot_state_includes_spellbook_snapshot() -> None:
    """
    Purpose:
        Validate Conduit snapshot_state includes Spellbook snapshot data.
    Contract:
        - Conduit metadata is captured.
        - Spellbook snapshot is attached and detached from live maps.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot data is missing or leaks live state.
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

    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="snapshot-conduit")
    snapshot = conduit.snapshot_state()

    assert snapshot["conduit_id"] == conduit.id
    assert snapshot["spellbook_snapshot"]["spellbook_id"] == spellbook.id
    assert isinstance(snapshot["snapshot_id"], str)
    assert isinstance(snapshot["captured_at_ms"], int)

    spellbook_snapshot = snapshot["spellbook_snapshot"]
    spellbook_snapshot["local_spells"].clear()

    assert len(spellbook.spells) == 1
