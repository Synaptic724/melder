import pytest

from melder.spellbook.bind.spell_index import SpellIndex


def test_component_spell_index_tracks_versions_and_hash_stability() -> None:
    """
    Purpose:
        Validate SpellIndex tracks versions without changing hash identity.
    Contract:
        - Hash remains stable across updates.
        - Versions are recorded and current is updated.
    Returns:
        None.
    """
    index = SpellIndex("v1")
    initial_hash = hash(index)

    index.update("v2")
    index.update("v3")

    assert hash(index) == initial_hash
    assert index.current == "v3"
    assert index.has_version("v1") is True
    assert index.has_version("v2") is True
    assert index.has_version("v3") is True
    assert index.get_all_versions() == {"v1", "v2", "v3"}


def test_component_spell_index_cleanup_blocks_access() -> None:
    """
    Purpose:
        Validate cleanup prevents further access to SpellIndex.
    Contract:
        - Property access raises RuntimeError after cleanup.
    Returns:
        None.
    """
    index = SpellIndex("v1")
    index.cleanup()

    assert index.cleaned is True
    with pytest.raises(RuntimeError):
        _ = index.current
