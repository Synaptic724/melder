import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure each transfer-ownership integration test starts on a clean Aether.
    Contract:
        - Resets the Aether singleton + rebinds Spellbook/Conduit._aether before and
          after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """Build a dynamic spellbook configuration with one scheduler worker."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_transfer_moves_spell_ownership_to_target() -> None:
    """
    Purpose:
        Verify ownership transfer moves a spell from source to target end-to-end after
        the footprint-discovery migration (conduit metadata -> envelope strategy -> ward).
    Contract:
        - The summary reports source/target/spell.
        - The spell's owning conduit becomes the target.
    Returns:
        None.
    Raises:
        AssertionError: If ownership does not move.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        summary = owner.transfer_spell_ownership(
            spell=spell_id,
            target_conduit=target,
        )

        assert summary["spell_id"] == spell_id
        assert summary["source"] == owner.id
        assert summary["target"] == target.id
        assert owner.get_conduit_by_spell_id(spell_id) is target
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_flips_meld_resolution_to_target() -> None:
    """
    Purpose:
        Verify meld resolution follows ownership after a transfer: the target can meld
        the spell and the source can no longer resolve it.
    Contract:
        - target.meld returns a built instance.
        - source.meld raises (the spell is no longer owned there).
    Returns:
        None.
    Raises:
        AssertionError: If resolution does not flip to the target.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)

        assert isinstance(target.meld(spell_id=spell_id), BasicService)
        with pytest.raises(KeyError, match="No spell found"):
            owner.meld(spell_id=spell_id)
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_moves_only_the_targeted_spell() -> None:
    """
    Purpose:
        Verify a transfer is selective: only the targeted spell moves; the source keeps
        its other owned spells (the footprint targets one lineage, not the whole conduit).
    Contract:
        - The transferred spell's owner becomes the target.
        - A second, untransferred spell remains owned by the source.
    Returns:
        None.
    Raises:
        AssertionError: If an untargeted spell is disturbed.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = owner_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        owner.transfer_spell_ownership(spell=service_id, target_conduit=target)

        assert owner.get_conduit_by_spell_id(service_id) is target
        assert owner.get_conduit_by_spell_id(config_id) is owner
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


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
