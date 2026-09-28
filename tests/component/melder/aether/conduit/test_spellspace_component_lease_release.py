"""Contracts for a SpellSpace's lease: released spaces refuse use and every exit finishes.

Why component tests:
    The contracts run through a real conduit, its SpellSpace pool and the
    per-thread managed stack, so they prove what callers of `enter_spellspace()`
    and `create_spellspace()` observe.

Contracts under test:
    - A space released to its pool (managed exit or manual cleanup) refuses
      `meld` and `purge` with SpellSpaceScopeError; a destroyed one refuses
      with the cleaned RuntimeError.
    - A second cleanup of a released space does nothing (no double pooling),
      including an explicit cleanup inside a managed block.
    - Managed exit, manual cleanup and permanent teardown finish their work when
      a disposal method fails, then raise the failures; the space is reusable.
    - A conduit cleaned inside its own managed space lets that block exit quietly.
    - A space destroyed inside its own managed block leaves the thread's stack,
      so the block exits quietly and later blocks see a clean stack.
"""

from collections.abc import Iterator
from typing import Dict, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)


class _Log:
    """
    Purpose:
        Record every disposal call of one test, in the order melder made them.
    Contract:
        Reset before each test by the fixture; `counts` keeps labels stable.
    """

    events: List[str] = []
    counts: Dict[str, int] = {}

    @classmethod
    def label(cls, kind: str) -> str:
        """
        Purpose: Return the next stable label for one kind of object.
        Args: kind: Short name of the object kind.
        Returns: str: "<kind>#<n>" for the n-th object of that kind.
        """
        cls.counts[kind] = cls.counts.get(kind, 0) + 1
        return f"{kind}#{cls.counts[kind]}"


class SpaceScoped:
    """unique_per_spell_space object whose `close` records its disposal."""

    def __init__(self) -> None:
        """Take the next `space` label."""
        self.label = _Log.label("space")

    def close(self) -> None:
        """Record this object's disposal."""
        _Log.events.append(f"close:{self.label}")


class ManyItem:
    """many object whose `close` records its disposal."""

    def __init__(self) -> None:
        """Take the next `many` label."""
        self.label = _Log.label("many")

    def close(self) -> None:
        """Record this object's disposal."""
        _Log.events.append(f"close:{self.label}")


class FailingSpace:
    """unique_per_spell_space object whose `close` records its disposal and then raises."""

    def __init__(self) -> None:
        """Take the next `failspace` label."""
        self.label = _Log.label("failspace")

    def close(self) -> None:
        """
        Record this object's disposal, then fail.

        Raises:
            RuntimeError: Always, naming this object.
        """
        _Log.events.append(f"close:{self.label}")
        raise RuntimeError(f"{self.label} close failed")


class _World:
    """
    Purpose:
        One dynamic book with the recorder spells bound and its conjured root.
    Contract:
        `ids` maps a short kind name to the bound spell id.
    """

    def __init__(self) -> None:
        """Bind the recorder spells and conjure the root conduit."""
        configuration = SpellbookConfiguration()
        set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
        configuration.set_property("disposal", True)
        configuration.set_property("disposal_method_names", ["close"])
        configuration.load_default_dictionary()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        self.book = Spellbook(configuration=configuration)
        self.ids: Dict[str, str] = {
            "space": self._bind(SpaceScoped, Existence.unique_per_spell_space),
            "many": self._bind(ManyItem, Existence.many),
            "failspace": self._bind(FailingSpace, Existence.unique_per_spell_space),
        }
        self.root: Conduit = self.book.conjure(dynamic=True, name="root")

    def _bind(self, spell: type, existence: Existence) -> str:
        """
        Purpose: Bind one recorder class.
        Args: spell: Class to bind. existence: Its lifetime.
        Returns: str: The bound spell id.
        """
        return self.book.bind(spell=spell, existence=existence, permissions="create")


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture
def world() -> Iterator[_World]:
    """
    Purpose: Give each test a fresh Aether, a fresh disposal log and a conjured world.
    Returns: Iterator[_World]: The world; the Aether is reset again afterwards.
    """
    _reset_aether()
    _Log.events = []
    _Log.counts = {}
    yield _World()
    _reset_aether()


def _causes(error: BaseException) -> List[str]:
    """
    Purpose: Flatten nested exception groups to the texts of each leaf's cause.
    Args: error: The raised exception or group.
    Returns: List[str]: One entry per failing disposal method, in group order.
    """
    if isinstance(error, BaseExceptionGroup):
        texts: List[str] = []
        for inner in error.exceptions:
            texts.extend(_causes(inner))
        return texts
    return [str(error.__cause__)]


def test_kept_handle_cannot_meld_after_managed_exit(world: _World) -> None:
    """A handle kept past the block refuses a warm meld instead of building into the idle shell."""
    with world.root.enter_spellspace() as space:
        space.meld(spell_id=world.ids["space"])

    with pytest.raises(SpellSpaceScopeError, match="released"):
        space.meld(spell_id=world.ids["space"])
    with pytest.raises(SpellSpaceScopeError, match="released"):
        space.meld("SpaceScoped")
    assert _Log.events == ["close:space#1"]


def test_kept_handle_cannot_purge_after_manual_cleanup(world: _World) -> None:
    """A manually cleaned space refuses purge."""
    space = world.root.create_spellspace()
    space.meld(spell_id=world.ids["many"])
    space.cleanup()

    with pytest.raises(SpellSpaceScopeError, match="released"):
        space.purge(spell_id=world.ids["many"])
    assert _Log.events == ["close:many#1"]


def test_reacquired_space_melds_again(world: _World) -> None:
    """Acquiring a released shell again, prewarmed or returned, makes it usable."""
    world.root.prewarm_spellspaces(1)
    with world.root.enter_spellspace() as first:
        first.meld(spell_id=world.ids["space"])
    with world.root.enter_spellspace() as second:
        assert second is first
        second.meld(spell_id=world.ids["space"])

    assert _Log.events == ["close:space#1", "close:space#2"]


def test_second_manual_cleanup_does_not_pool_the_space_twice(world: _World) -> None:
    """Cleaning a manual space twice pools it once, so two acquisitions get two spaces."""
    space = world.root.create_spellspace()
    space.cleanup()
    space.cleanup()

    first = world.root.create_spellspace()
    second = world.root.create_spellspace()
    assert first is space
    assert second is not space


def test_explicit_cleanup_inside_a_managed_block_is_not_repeated_at_exit(world: _World) -> None:
    """The exit after an explicit cleanup neither disposes again nor pools the space twice."""
    with world.root.enter_spellspace() as space:
        space.meld(spell_id=world.ids["space"])
        space.cleanup()

    assert _Log.events == ["close:space#1"]
    with world.root.enter_spellspace() as outer:
        with world.root.enter_spellspace() as inner:
            assert outer is not inner


def test_managed_exit_with_a_failing_object_raises_and_returns_the_space(world: _World) -> None:
    """Every object is disposed, the failure is raised, and the space goes back to its pool."""
    with pytest.raises(ExceptionGroup) as raised:
        with world.root.enter_spellspace() as space:
            space.meld(spell_id=world.ids["failspace"])
            space.meld(spell_id=world.ids["space"])

    assert _causes(raised.value) == ["failspace#1 close failed"]
    assert _Log.events == ["close:space#1", "close:failspace#1"]
    with world.root.enter_spellspace() as again:
        assert again is space


def test_managed_exit_failure_is_chained_to_the_block_error(world: _World) -> None:
    """With a failing block, the disposal group rises with the block's error as its context."""
    with pytest.raises(ExceptionGroup) as raised:
        with world.root.enter_spellspace() as space:
            space.meld(spell_id=world.ids["failspace"])
            raise KeyError("boom")

    assert isinstance(raised.value.__context__, KeyError)
    with world.root.enter_spellspace() as again:
        assert again is space


def test_block_error_passes_through_a_clean_managed_exit(world: _World) -> None:
    """The block's own exception propagates and the space is still disposed and pooled."""
    with pytest.raises(KeyError, match="boom"):
        with world.root.enter_spellspace() as space:
            space.meld(spell_id=world.ids["space"])
            raise KeyError("boom")

    assert _Log.events == ["close:space#1"]
    with world.root.enter_spellspace() as again:
        assert again is space


def test_manual_cleanup_with_a_failing_object_raises_and_returns_the_space(world: _World) -> None:
    """A failing manual cleanup still unregisters and pools the space before raising."""
    space = world.root.create_spellspace()
    space.meld(spell_id=world.ids["failspace"])

    with pytest.raises(ExceptionGroup) as raised:
        space.cleanup()

    assert _causes(raised.value) == ["failspace#1 close failed"]
    assert world.root.create_spellspace() is space


def test_permanent_teardown_with_a_failing_object_destroys_the_space(world: _World) -> None:
    """Root teardown destroys a space whose object failed, then reports the failure."""
    space = world.root.create_spellspace()
    space.meld(spell_id=world.ids["failspace"])

    with pytest.raises(ExceptionGroup) as raised:
        world.root.cleanup()

    assert _causes(raised.value) == ["failspace#1 close failed"]
    assert space.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        space.meld(spell_id=world.ids["space"])


def test_owner_cleaned_inside_its_own_managed_space_exits_quietly(world: _World) -> None:
    """Returning a lesser to its pool from inside its managed space leaves the block exit with nothing to do."""
    lesser = world.root.create_lesser_conduit()
    with lesser.enter_spellspace() as space:
        space.meld(spell_id=world.ids["space"])
        lesser.cleanup()

    assert _Log.events == ["close:space#1"]
    assert world.root.create_lesser_conduit() is lesser


def test_space_destroyed_inside_its_own_managed_block_leaves_the_thread_stack(world: _World) -> None:
    """A managed space destroyed inside its block drops off the thread's stack and its block exits quietly."""
    with world.root.enter_spellspace() as space:
        space.meld(spell_id=world.ids["space"])
        space.permanent_cleanup()
        assert world.root.get_active_spellspace() is None

    assert _Log.events == ["close:space#1"]
    assert space.cleaned is True
    with world.root.enter_spellspace() as next_space:
        assert world.root.get_active_spellspace() is next_space
    assert world.root.get_active_spellspace() is None
