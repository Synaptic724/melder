"""tests/integration/melder/spellbook/test_spellbook_integration_self_dependency.py

A constructor that takes its own class is refused through the readable validation report (2026-09-26):
the spell by name, the parameter, and the fix, reported once. Before, conjure aborted in Phase 3 with
PhaseExecutionError "DagNode cannot depend on itself" and a late dynamic bind raised a bare ValueError at meld.
"""
from typing import Iterator, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_singletons_for_self_dependency() -> Iterator[None]:
    """Reset Nexus + Aether around each test for singleton isolation."""
    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class Node:
    """Constructor that takes its own class."""

    def __init__(self, parent: "Node", name: str) -> None:
        """Store the parent."""
        self.parent = parent


class Tree:
    """Consumer of the self-referencing spell."""

    def __init__(self, root: Node) -> None:
        """Store the root."""
        self.root = root


class Branch:
    """Collection parameter of its own class."""

    def __init__(self, children: list["Branch"]) -> None:
        """Store the children."""
        self.children = children


class Leaf:
    """Self-typed parameter with a default: plain, never injected."""

    def __init__(self, parent: Optional["Leaf"] = None) -> None:
        """Store the optional parent."""
        self.parent = parent


class Unrelated:
    """A spell with no dependencies."""

    def __init__(self) -> None:
        """Construct nothing."""


NODE_LINE = ("Spell 'Node' depends on itself: its constructor parameter 'parent' resolves to this same spell. "
             "Remove that parameter or give it a default. [SELF_DEPENDENCY]")


def _book(tag: str, *classes: type) -> Spellbook:
    """Build one dynamic spellbook on its own frame and bind `classes` as many-existence spells."""
    frame = f"intg-self-dependency-{tag}"
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    for cls in classes:
        book.bind(spell=cls, existence=Existence.many, permissions="create")
    return book


def test_conjure_refuses_self_referencing_constructor_with_readable_report() -> None:
    """The spell is refused by name, parameter and fix, once; its validation result keeps both codes."""
    book = _book("single", Node)
    try:
        with pytest.raises(SpellbookValidationError) as raised:
            book.conjure(dynamic=True, name="root")
        message = str(raised.value)
        assert message.startswith("Spellbook validation failed. Broken spells: Node.")
        assert NODE_LINE in message
        assert "[CIRCULAR_DEPENDENCY]" not in message
        assert "DagNode" not in message
        codes = {issue.code for issue in raised.value.broken_spells[0].validation_result_phase4.issues}
        assert {"SELF_DEPENDENCY", "CIRCULAR_DEPENDENCY"} <= codes
    finally:
        book.cleanup()


def test_conjure_refuses_self_collection_parameter() -> None:
    """A list of its own class is refused the same way."""
    book = _book("collection", Branch)
    try:
        with pytest.raises(SpellbookValidationError) as raised:
            book.conjure(dynamic=True, name="root")
        assert ("Spell 'Branch' depends on itself: its constructor parameter 'children' resolves to this same "
                "spell.") in str(raised.value)
    finally:
        book.cleanup()


def test_conjure_names_the_self_referencing_spell_beside_its_consumer() -> None:
    """The self-referencing spell carries its own reason when another spell consumes it."""
    book = _book("consumer", Node, Unrelated, Tree)
    try:
        with pytest.raises(SpellbookValidationError) as raised:
            book.conjure(dynamic=True, name="root")
        message = str(raised.value)
        assert NODE_LINE in message
        assert "Unrelated" not in message
    finally:
        book.cleanup()


def test_self_typed_parameter_with_default_conjures() -> None:
    """A default makes the parameter plain, so nothing is refused."""
    book = _book("default", Leaf)
    try:
        conduit = book.conjure(dynamic=True, name="root")
        conduit.cleanup()
    finally:
        book.cleanup()


def test_late_dynamic_bind_raises_readable_report() -> None:
    """Binding a self-referencing class after conjure raises the report, not a bare ValueError.

    Depending on the frame posture the structural phases run at that bind or at the spell's first meld;
    either way the user gets the same SpellbookValidationError.
    """
    book = _book("late", Unrelated)
    try:
        conduit = book.conjure(dynamic=True, name="root")
        with pytest.raises(SpellbookValidationError) as raised:
            book.bind(spell=Node, existence=Existence.many, permissions="create")
            conduit.meld(spell=Node, override={"parent": None, "name": "n"})
        assert "Spell 'Node' depends on itself" in str(raised.value)
        conduit.cleanup()
    finally:
        book.cleanup()
