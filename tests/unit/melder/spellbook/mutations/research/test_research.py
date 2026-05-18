"""Unit tests for Research cleanup behavior."""

from __future__ import annotations

import pytest

import melder.mutation_research.research.research as research_module
from melder.spellbook.bind.spell_index import SpellIndex
from melder.mutation_research.research.research import Research


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
        assert not hasattr(session, '_target_index')
        assert not hasattr(session, '_spell_researches')
        assert not hasattr(session, '_spell_research_ids')
        assert not hasattr(session, '_creation_researches')
        assert not hasattr(session, '_creation_research_ids')
        assert not hasattr(session, '_metadata')
        assert not hasattr(session, '_root_version')
        assert not hasattr(session, '_level')

        session.cleanup()

        with pytest.raises(RuntimeError, match="has already been cleaned"):
            session.list_spell_researches()
    finally:
        index.cleanup()


def test_research_properties_and_metadata_detach() -> None:
    """
    Purpose:
        Validate the stable property surface before cleanup.
    Contract:
        - id is a non-empty string.
        - target_index and root_version mirror constructor state.
        - name and level round-trip constructor inputs.
        - metadata returns a detached shallow copy.
    Returns:
        None.
    Raises:
        AssertionError: If the property surface is incorrect.
    """
    index = SpellIndex("spell-root")
    session = Research(
        target_index=index,
        name="session",
        level=7,
        metadata={"source": "test"},
    )
    try:
        meta = session.metadata
        meta["source"] = "mutated"

        assert isinstance(session.id, str)
        assert session.id != ""
        assert session.target_index is index
        assert session.root_version == index.current
        assert session.name == "session"
        assert session.level == 7
        assert session.metadata == {"source": "test"}
    finally:
        session.cleanup()
        index.cleanup()


def test_start_spell_research_reuses_matching_lines_and_supports_lookup(monkeypatch) -> None:
    """
    Purpose:
        Validate spell-line orchestration on Research.
    Contract:
        - start_spell_research reuses an existing line when spell_id matches and
          name is compatible.
        - get_spell_research validates empty/missing ids.
        - list_spell_researches returns the live registered lines.
    Returns:
        None.
    Raises:
        AssertionError: If spell-line orchestration is incorrect.
    """
    created: list[object] = []

    class _FakeResearchSpell:
        def __init__(self, spell_id: str, *, name: str) -> None:
            self.id = f"spell-line-{len(created)}"
            self.spell_id = spell_id
            self.name = name
            self.cleaned = False
            created.append(self)

        def cleanup(self) -> None:
            self.cleaned = True

    monkeypatch.setattr(research_module, "ResearchSpell", _FakeResearchSpell)

    index = SpellIndex("spell-root")
    session = Research(target_index=index, name="session")
    try:
        line_a = session.start_spell_research(index.current, name="alpha")
        line_b = session.start_spell_research(index.current, name="alpha")
        line_c = session.start_spell_research(index.current)
        other = session.start_spell_research("spell-v2", name="beta")

        assert line_b is line_a
        assert line_c is line_a
        assert other is not line_a
        assert session.list_spell_researches() == [line_a, other]
        assert session.get_spell_research(line_a.id) is line_a
        assert session.get_spell_research(other.id) is other

        with pytest.raises(ValueError, match="research_id cannot be empty"):
            session.get_spell_research("")
        with pytest.raises(KeyError, match="Unknown spell research id"):
            session.get_spell_research("missing")
        with pytest.raises(ValueError, match="spell_id cannot be empty"):
            session.start_spell_research("")
    finally:
        session.cleanup()
        index.cleanup()


def test_start_creation_research_reuses_matching_lines_and_supports_lookup(monkeypatch) -> None:
    """
    Purpose:
        Validate creation-line orchestration on Research.
    Contract:
        - start_creation_research reuses an existing line when creation_id
          matches and name is compatible.
        - get_creation_research validates empty/missing ids.
        - list_creation_researches returns the live registered lines.
    Returns:
        None.
    Raises:
        AssertionError: If creation-line orchestration is incorrect.
    """
    created: list[object] = []

    class _FakeResearchCreation:
        def __init__(self, creation_id: str, *, name: str) -> None:
            self.id = f"creation-line-{len(created)}"
            self.creation_id = creation_id
            self.name = name
            self.cleaned = False
            created.append(self)

        def cleanup(self) -> None:
            self.cleaned = True

    monkeypatch.setattr(research_module, "ResearchCreation", _FakeResearchCreation)

    index = SpellIndex("spell-root")
    session = Research(target_index=index, name="session")
    try:
        line_a = session.start_creation_research("creation-1", name="alpha")
        line_b = session.start_creation_research("creation-1", name="alpha")
        line_c = session.start_creation_research("creation-1")
        other = session.start_creation_research("creation-2", name="beta")

        assert line_b is line_a
        assert line_c is line_a
        assert other is not line_a
        assert session.list_creation_researches() == [line_a, other]
        assert session.get_creation_research(line_a.id) is line_a
        assert session.get_creation_research(other.id) is other

        with pytest.raises(ValueError, match="research_id cannot be empty"):
            session.get_creation_research("")
        with pytest.raises(KeyError, match="Unknown creation research id"):
            session.get_creation_research("missing")
        with pytest.raises(ValueError, match="creation_id cannot be empty"):
            session.start_creation_research("")
    finally:
        session.cleanup()
        index.cleanup()


def test_start_research_lines_without_names_builds_session_scoped_defaults() -> None:
    """
    Purpose:
        Validate the default naming contract for new research lines.
    Contract:
        - New spell lines default to ``{session}:spell:{spell_id}``.
        - New creation lines default to ``{session}:creation:{creation_id}``.
        - The created lines are registered into their respective lists.
    Returns:
        None.
    Raises:
        AssertionError: If default names or registration are incorrect.
    """
    index = SpellIndex("spell-root")
    session = Research(target_index=index, name="session")
    try:
        spell_line = session.start_spell_research("spell-v2")
        creation_line = session.start_creation_research("creation-1")

        assert spell_line.name == "session:spell:spell-v2"
        assert creation_line.name == "session:creation:creation-1"
        assert session.list_spell_researches() == [spell_line]
        assert session.list_creation_researches() == [creation_line]
    finally:
        session.cleanup()
        index.cleanup()


def test_promote_spell_version_updates_index_root_version_and_metadata() -> None:
    """
    Purpose:
        Validate successful spell-version promotion semantics.
    Contract:
        - promote_spell_version updates SpellIndex.current when enabled.
        - root_version follows the promoted version.
        - promotion metadata records the operation outcome.
    Returns:
        None.
    Raises:
        AssertionError: If promotion state is incorrect.
    """
    index = SpellIndex("spell-root")
    session = Research(target_index=index, name="session", metadata={})
    try:
        session.promote_spell_version(
            "spell-v2",
            update_index=True,
            propagate_to_runtime=False,
            drop_legacy_creations=True,
        )

        assert index.current == "spell-v2"
        assert session.root_version == "spell-v2"
        promotions = session.metadata["promotions"]
        assert promotions == [
            {
                "new_spell_id": "spell-v2",
                "update_index": True,
                "propagate_to_runtime": False,
                "drop_legacy_creations": True,
                "index_update_success": True,
            }
        ]

        with pytest.raises(ValueError, match="new_spell_id cannot be empty"):
            session.promote_spell_version("")
    finally:
        session.cleanup()
        index.cleanup()


def test_promote_spell_version_uses_current_setter_fallback() -> None:
    """
    Purpose:
        Validate promotion fallback when the target index exposes ``current`` but
        no ``update(...)`` helper.
    Contract:
        - The ``current`` setter is used when ``update(...)`` is unavailable.
        - Promotion metadata records a successful index update.
    Returns:
        None.
    Raises:
        AssertionError: If fallback promotion behavior is incorrect.
    """
    class _Index:
        id = "lineage-1"

        def __init__(self) -> None:
            self._current = "spell-root"

        @property
        def current(self) -> str:
            return self._current

        @current.setter
        def current(self, value: str) -> None:
            self._current = value

    session = Research(target_index=_Index(), name="session", metadata={})
    try:
        session.promote_spell_version("spell-v2")

        assert session.target_index.current == "spell-v2"
        assert session.metadata["promotions"] == [
            {
                "new_spell_id": "spell-v2",
                "update_index": True,
                "propagate_to_runtime": True,
                "drop_legacy_creations": False,
                "index_update_success": True,
            }
        ]
    finally:
        session.cleanup()


def test_promote_spell_version_without_index_update_still_records_bookkeeping() -> None:
    """
    Purpose:
        Validate local promotion bookkeeping when index mutation is disabled.
    Contract:
        - The target SpellIndex is left untouched when ``update_index=False``.
        - The session still records the promotion event in metadata.
        - ``root_version`` advances to the promoted version for local tracking.
    Returns:
        None.
    Raises:
        AssertionError: If skipped-index promotion bookkeeping is incorrect.
    """
    index = SpellIndex("spell-root")
    session = Research(target_index=index, name="session", metadata={})
    try:
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
        session.cleanup()
        index.cleanup()


def test_promote_spell_version_records_failed_index_update(monkeypatch) -> None:
    """
    Purpose:
        Validate failed index-update fallback is recorded without aborting the session.
    Contract:
        - Failed update/current writes are recorded as index_update_success=False.
        - root_version still advances locally for research bookkeeping.
    Returns:
        None.
    Raises:
        AssertionError: If fallback recording is incorrect.
    """
    class _Index:
        id = "lineage-1"
        _current = "spell-root"

        @property
        def current(self) -> str:
            return self._current

        def update(self, new_id: str) -> None:
            raise RuntimeError("boom")

    session = Research(target_index=_Index(), name="session", metadata={})
    try:
        session.promote_spell_version("spell-v2")
        promotions = session.metadata["promotions"]
        assert promotions[0]["index_update_success"] is False
        assert session.root_version == "spell-v2"
    finally:
        session.cleanup()
