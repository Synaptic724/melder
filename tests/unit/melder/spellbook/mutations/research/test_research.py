"""Unit tests for Research cleanup behavior."""

from __future__ import annotations

import pytest

from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.mutations.research.research import Research


def test_research_cleanup_cleans_lines_and_nulls_target() -> None:
    """
    Purpose:
        Validate Research cleanup releases lineages and clears internal registries.
    Contract:
        - cleanup() marks the session as cleaned.
        - cleanup() cascades to spell/creation research lines and nodes.
        - cleanup() nulls external associations (target SpellIndex) and registries.
        - cleanup() is idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear owned or associated state.
    """
    index = SpellIndex("spell-root")
    session = Research(
        target_index=index,
        name="session",
        level=1,
        metadata={"source": "test"},
    )
    try:
        spell_line = session.start_spell_research(index.current, name="spell-line")
        spell_node = spell_line.begin_mutation(message="seed")
        spell_line.commit_mutation(spell_node)

        creation_line = session.start_creation_research("creation-1", name="creation-line")
        creation_node = creation_line.begin_mutation(message="seed")
        creation_line.commit_mutation(creation_node)

        session.cleanup()

        assert session.cleaned is True
        assert spell_line.cleaned is True
        assert creation_line.cleaned is True
        assert spell_node.cleaned is True
        assert creation_node.cleaned is True
        assert session._target_index is None
        assert session._spell_researches is None
        assert session._spell_research_ids is None
        assert session._creation_researches is None
        assert session._creation_research_ids is None
        assert session._metadata is None
        assert session._root_version is None
        assert session._level is None

        session.cleanup()

        with pytest.raises(RuntimeError, match="has already been cleaned"):
            session.list_spell_researches()
    finally:
        index.cleanup()
