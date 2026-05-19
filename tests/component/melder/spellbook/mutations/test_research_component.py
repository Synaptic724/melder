"""Component tests for Research orchestration through MutationResearch."""

from __future__ import annotations

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.mutation_research.mutation_research import MutationResearch


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each component test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


def test_mutation_research_component_drives_real_session_lines_and_promotion() -> None:
    """
    Purpose:
        Validate the real mutation-research runtime path across manager,
        session, line, and node objects.
    Contract:
        - Existing session lines are reused through ``MutationResearch``.
        - Default spell/creation line names are session-scoped and deterministic.
        - Begun mutation nodes can be committed back onto the reused real lines.
        - Local promotion bookkeeping still records an event when index updates
          are intentionally skipped.
    Returns:
        None.
    Raises:
        AssertionError: If the live orchestration is incorrect.
    """
    manager = MutationResearch(object())
    index = SpellIndex("spell-root")
    try:
        session = manager.create_session(index, name="session", metadata={"owner": "test"})
        spell_line = session.start_spell_research(index.current)
        creation_line = session.start_creation_research("creation-1")

        assert spell_line.name == "session:spell:spell-root"
        assert creation_line.name == "session:creation:creation-1"

        spell_node = manager.begin_spell_mutation(index, message="spell-seed", tags=["alpha"])
        creation_node = manager.begin_creation_mutation(
            index,
            "creation-1",
            message="creation-seed",
            tags=["beta"],
        )

        spell_line.commit_mutation(spell_node)
        creation_line.commit_mutation(creation_node)

        assert session.list_spell_researches() == [spell_line]
        assert session.list_creation_researches() == [creation_line]
        assert session.get_spell_research(spell_line.id) is spell_line
        assert session.get_creation_research(creation_line.id) is creation_line
        assert spell_line.get_head() is spell_node
        assert creation_line.get_head() is creation_node
        assert spell_node.metadata == {"message": "spell-seed", "tags": ["alpha"]}
        assert creation_node.metadata == {"message": "creation-seed", "tags": ["beta"]}

        session.promote_spell_version(
            "spell-v2",
            update_index=False,
            propagate_to_runtime=False,
            drop_legacy_creations=True,
        )

        assert index.current == "spell-root"
        assert session.root_version == "spell-v2"
        assert session.metadata["promotions"] == [
            {
                "new_spell_id": "spell-v2",
                "update_index": False,
                "propagate_to_runtime": False,
                "drop_legacy_creations": True,
                "index_update_success": False,
            }
        ]
    finally:
        manager.cleanup()
        index.cleanup()
