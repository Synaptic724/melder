"""Unit tests for MutationResearch cleanup behavior."""

from __future__ import annotations

import importlib
import types

import pytest

import melder.spellbook.mutations.mutation_research as mutation_research_module
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


def test_create_session_reuses_existing_and_supports_lookup(monkeypatch) -> None:
    """
    Purpose:
        Validate session creation, reuse, and lookup helpers.
    Contract:
        - create_session creates one Research session for a SpellIndex id.
        - repeated create_session on the same index returns the existing session.
        - get_session_for_index / get_session_by_index_id / list_sessions expose
          the same live session.
    Returns:
        None.
    Raises:
        AssertionError: If session orchestration is incorrect.
    """
    created = []

    class _FakeResearch:
        def __init__(self, target_index, name, level=None, metadata=None):
            self.target_index = target_index
            self.name = name
            self.level = level
            self.metadata = metadata
            self.cleaned = False
            created.append(self)

        def cleanup(self):
            self.cleaned = True

    monkeypatch.setattr(mutation_research_module, "Research", _FakeResearch)

    manager = MutationResearch(object())
    index = SpellIndex("spell-root")
    try:
        session_a = manager.create_session(index, name="alpha", level=3, metadata={"x": 1})
        session_b = manager.create_session(index, name="beta")

        assert session_b is session_a
        assert created == [session_a]
        assert session_a.name == "alpha"
        assert session_a.level == 3
        assert session_a.metadata == {"x": 1}
        assert manager.get_session_for_index(index) is session_a
        assert manager.get_session_by_index_id(index.id) is session_a
        assert manager.list_sessions() == [session_a]
    finally:
        manager.cleanup()
        index.cleanup()


def test_create_session_rejects_none_or_missing_index_id() -> None:
    """
    Purpose:
        Validate create_session input guards.
    Contract:
        - None target_index is rejected.
        - Targets without a non-empty id are rejected.
    Returns:
        None.
    Raises:
        AssertionError: If invalid inputs are accepted.
    """
    manager = MutationResearch(object())
    try:
        with pytest.raises(ValueError, match="target_index cannot be None"):
            manager.create_session(None)  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="non-empty 'id' attribute"):
            manager.create_session(types.SimpleNamespace(id=""))
    finally:
        manager.cleanup()


def test_remove_session_for_index_cleans_session_and_missing_cases_are_noop(monkeypatch) -> None:
    """
    Purpose:
        Validate session removal semantics.
    Contract:
        - remove_session_for_index cleans the removed session.
        - Missing or invalid indexes are ignored.
    Returns:
        None.
    Raises:
        AssertionError: If removal behavior is incorrect.
    """
    cleaned = []

    class _FakeResearch:
        def __init__(self, target_index, name, level=None, metadata=None):
            self.cleaned = False

        def cleanup(self):
            self.cleaned = True
            cleaned.append(True)

    monkeypatch.setattr(mutation_research_module, "Research", _FakeResearch)

    manager = MutationResearch(object())
    index = SpellIndex("spell-root")
    try:
        session = manager.create_session(index, name="session")
        manager.remove_session_for_index(types.SimpleNamespace(id="missing"))
        assert manager.get_session_for_index(index) is session

        manager.remove_session_for_index(index)
        assert cleaned == [True]
        assert manager.get_session_for_index(index) is None
        manager.remove_session_for_index(index)
    finally:
        manager.cleanup()
        index.cleanup()


def test_begin_spell_mutation_creates_or_reuses_spell_research_line(monkeypatch) -> None:
    """
    Purpose:
        Validate the high-level spell mutation entrypoint.
    Contract:
        - Existing spell research lines are reused when spell_id matches current.
        - Otherwise start_spell_research is used to create one.
        - begin_mutation return value is forwarded to the caller.
    Returns:
        None.
    Raises:
        AssertionError: If spell mutation orchestration is incorrect.
    """
    class _FakeSpellResearch:
        def __init__(self, spell_id):
            self.spell_id = spell_id
            self.begin_calls = []

        def begin_mutation(self, message=None, tags=None):
            self.begin_calls.append((message, tags))
            return {"spell_id": self.spell_id, "message": message, "tags": tags}

    class _FakeResearch:
        def __init__(self, target_index, name, level=None, metadata=None):
            self._spell_lines = []
            self.start_calls = []

        def cleanup(self):
            return None

        def list_spell_researches(self):
            return list(self._spell_lines)

        def start_spell_research(self, spell_id, name=None):
            self.start_calls.append((spell_id, name))
            line = _FakeSpellResearch(spell_id)
            self._spell_lines.append(line)
            return line

        def list_creation_researches(self):
            return []

        def start_creation_research(self, creation_id, name=None):
            raise AssertionError("creation path should not be used")

    monkeypatch.setattr(mutation_research_module, "Research", _FakeResearch)

    manager = MutationResearch(object())
    index = SpellIndex("spell-root")
    try:
        session = manager.create_session(index, name="session")
        existing = _FakeSpellResearch(index.current)
        session._spell_lines.append(existing)

        reused = manager.begin_spell_mutation(index, message="reuse", tags=["a"])
        assert reused == {"spell_id": index.current, "message": "reuse", "tags": ["a"]}
        assert session.start_calls == []

        session._spell_lines.clear()
        created = manager.begin_spell_mutation(index, research_name="new-line", message="create", tags=["b"])
        assert session.start_calls == [(index.current, "new-line")]
        assert created == {"spell_id": index.current, "message": "create", "tags": ["b"]}
    finally:
        manager.cleanup()
        index.cleanup()


def test_begin_creation_mutation_creates_or_reuses_creation_research_line(monkeypatch) -> None:
    """
    Purpose:
        Validate the high-level creation mutation entrypoint.
    Contract:
        - Existing creation research lines are reused when creation_id matches.
        - Otherwise start_creation_research is used to create one.
        - begin_mutation return value is forwarded to the caller.
    Returns:
        None.
    Raises:
        AssertionError: If creation mutation orchestration is incorrect.
    """
    class _FakeCreationResearch:
        def __init__(self, creation_id):
            self.creation_id = creation_id
            self.begin_calls = []

        def begin_mutation(self, message=None, tags=None):
            self.begin_calls.append((message, tags))
            return {"creation_id": self.creation_id, "message": message, "tags": tags}

    class _FakeResearch:
        def __init__(self, target_index, name, level=None, metadata=None):
            self._creation_lines = []
            self.start_calls = []

        def cleanup(self):
            return None

        def list_spell_researches(self):
            return []

        def start_spell_research(self, spell_id, name=None):
            raise AssertionError("spell path should not be used")

        def list_creation_researches(self):
            return list(self._creation_lines)

        def start_creation_research(self, creation_id, name=None):
            self.start_calls.append((creation_id, name))
            line = _FakeCreationResearch(creation_id)
            self._creation_lines.append(line)
            return line

    monkeypatch.setattr(mutation_research_module, "Research", _FakeResearch)

    manager = MutationResearch(object())
    index = SpellIndex("spell-root")
    try:
        session = manager.create_session(index, name="session")
        existing = _FakeCreationResearch("creation-1")
        session._creation_lines.append(existing)

        reused = manager.begin_creation_mutation(index, "creation-1", message="reuse", tags=["a"])
        assert reused == {"creation_id": "creation-1", "message": "reuse", "tags": ["a"]}
        assert session.start_calls == []

        session._creation_lines.clear()
        created = manager.begin_creation_mutation(
            index,
            "creation-2",
            research_name="new-creation",
            message="create",
            tags=["b"],
        )
        assert session.start_calls == [("creation-2", "new-creation")]
        assert created == {"creation_id": "creation-2", "message": "create", "tags": ["b"]}
    finally:
        manager.cleanup()
        index.cleanup()
