"""Append the D3 transfer-default regression tests (0.2.8239) to the transfer integration module of one tree."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edit_tool import apply

TREE = pathlib.Path(sys.argv[1])
MODULE = TREE / "tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py"

ANCHOR = (
    "        assert owner.get_conduit_by_spell_id(config_id) is owner\n"
    "    finally:\n"
    "        target.permanent_cleanup()\n"
    "        owner.permanent_cleanup()\n"
)

ADDITION = ANCHOR + '''

class _Closable:
    """
    Test object whose `close` is declared as its disposal method at bind.

    Contract:
        `closes` counts how many times Melder ran `close` on this object.
    """

    def __init__(self) -> None:
        """Start undisposed."""
        self.closes: int = 0

    def close(self) -> None:
        """Record one disposal."""
        self.closes += 1


class _SharedTool(_Closable):
    """`unique` spell whose ownership is transferred between roots."""


class _ToolUser(_Closable):
    """`unique_per_conduit` consumer of `_SharedTool` on the source root."""

    def __init__(self, tool: _SharedTool) -> None:
        """Keep the injected tool."""
        super().__init__()
        self.tool = tool


class _Report(_Closable):
    """Disposal-bearing `many` spell whose ownership is transferred between roots."""


def _bind_closable(book: Spellbook, spell: type, existence: Existence) -> str:
    """
    Bind one test class with `close` as its disposal method.

    Args:
        book: The Spellbook to bind into.
        spell: The class.
        existence: Its Existence.

    Returns:
        str: The spell id.
    """
    return book.bind(spell=spell, existence=existence, permissions="create", disposal_method_names=["close"])


def test_default_transfer_keeps_a_unique_as_one_object() -> None:
    """
    A default transfer carries the source's `unique` instance to the target.

    Contract (owner ruling 2026-10-14, 0.2.8239: `move_creations` defaults to True):
        - The report's options say `move_creations` is True.
        - The target serves the object the source's consumer already holds: one instance, not two.
        - The source's teardown leaves it open; the target's teardown disposes it once.

    Symptom (through 0.2.8238, when the default was False): the transfer took the instance out of the source store
    and moved it nowhere, so the target built a second instance beside the one the consumer kept, and the first one's
    `close` never ran.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    tool_id = _bind_closable(owner_book, _SharedTool, Existence.unique)
    user_id = _bind_closable(owner_book, _ToolUser, Existence.unique_per_conduit)
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        tool = owner.meld(spell_id=user_id).tool
        summary = owner.transfer_spell_ownership(spell=tool_id, target_conduit=target)
        assert summary["options"]["move_creations"] is True
        assert target.meld(spell_id=tool_id) is tool, "the target built a second instance of a transferred unique"
        owner.cleanup()
        assert tool.closes == 0, "the source's teardown disposed an instance the target now owns"
        target.cleanup()
        assert tool.closes == 1, "the target's teardown disposes the transferred instance exactly once"
    finally:
        target.cleanup()
        owner.cleanup()


def test_default_transfer_moves_a_tracked_many_object_to_the_target() -> None:
    """
    A default transfer moves the disposal-bearing `many` objects the source tracks for the spell.

    Contract (0.2.8239):
        - The source's teardown leaves the moved object open; the target's teardown disposes it once.

    Symptom (through 0.2.8238): the object was taken out of the source store and never disposed by either root.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    report_id = _bind_closable(owner_book, _Report, Existence.many)
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        report = owner.meld(spell_id=report_id)
        owner.transfer_spell_ownership(spell=report_id, target_conduit=target)
        owner.cleanup()
        assert report.closes == 0, "the source's teardown disposed an object that moved with the spell"
        target.cleanup()
        assert report.closes == 1, "the target's teardown disposes the moved object exactly once"
    finally:
        target.cleanup()
        owner.cleanup()


def test_transfer_without_move_creations_builds_a_new_instance_on_the_target() -> None:
    """
    Opt-out control: `move_creations=False` carries no instance.

    Contract:
        - Ownership still moves, and the target builds its own `unique` on its first meld; the caller chose not to
          move the source's objects (behaviour unchanged by 0.2.8239).
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    tool_id = _bind_closable(owner_book, _SharedTool, Existence.unique)
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        tool = owner.meld(spell_id=tool_id)
        owner.transfer_spell_ownership(spell=tool_id, target_conduit=target, move_creations=False)
        assert owner.get_conduit_by_spell_id(tool_id) is target
        assert target.meld(spell_id=tool_id) is not tool
    finally:
        target.cleanup()
        owner.cleanup()
'''

print(apply(str(MODULE), [(ANCHOR, ADDITION)]))
