"""Unit tests for MutationResearch cleanup behavior."""

from __future__ import annotations

import importlib

import pytest

from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.mutations.mutation_research import MutationResearch

MODULE_PATH = "melder.spellbook.mutations.mutation_research"


class _WeakRefTarget:
    """
    Purpose:
        Provide a weakref-friendly instance for attach_* tests.
    Contract:
        - Instances are weak-reference compatible.
        - No behavior beyond identity is required.
    """


def test_import_module() -> None:
    """
    Purpose:
        Verify the mutation_research module imports successfully.
    Contract:
        - import_module resolves the module path without raising.
    Returns:
        None.
    Raises:
        AssertionError: If the module cannot be imported.
    """
    importlib.import_module(MODULE_PATH)


def test_mutation_research_cleanup_cleans_sessions_and_releases_associations() -> None:
    """
    Purpose:
        Validate MutationResearch cleanup cascades to sessions and releases external references.
    Contract:
        - cleanup() marks the manager and sessions as cleaned.
        - cleanup() cleans derived research lines and mutation nodes.
        - cleanup() nulls external associations (frame, target index, attached refs).
        - cleanup() is idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not release or cascade properly.
    """
    frame = object()
    manager = MutationResearch(frame)
    index = SpellIndex("spell-root")
    try:
        session = manager.create_session(index, name="session")
        spell_line = session.start_spell_research(index.current, name="spell-line")
        spell_line.attach_spell(_WeakRefTarget())
        spell_node = spell_line.begin_mutation(message="seed")
        spell_line.commit_mutation(spell_node)

        creation_line = session.start_creation_research("creation-1", name="creation-line")
        creation_line.attach_creation(_WeakRefTarget())
        creation_node = creation_line.begin_mutation(message="seed")
        creation_line.commit_mutation(creation_node)

        manager.cleanup()

        assert manager.cleaned is True
        assert session.cleaned is True
        assert spell_line.cleaned is True
        assert creation_line.cleaned is True
        assert spell_node.cleaned is True
        assert creation_node.cleaned is True
        assert manager._aetheric_frame is None
        assert manager._sessions_by_index is None
        assert session._target_index is None
        assert spell_line._spell_ref is None
        assert creation_line._creation_ref is None

        manager.cleanup()

        with pytest.raises(RuntimeError, match="has already been cleaned"):
            manager.list_sessions()
    finally:
        index.cleanup()
