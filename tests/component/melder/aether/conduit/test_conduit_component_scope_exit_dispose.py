"""Contracts for `with conduit:` as a dispose scope and for finished pool returns.

Why component tests:
    Every contract runs through a real Spellbook, a conjured root, real lesser
    conduits and their pools, so the tests prove the public lifecycle rather
    than a hand-built store.

Contracts under test:
    - `with conduit:` disposes at block exit: a lesser goes back to its root's
      pool, a root is torn down; the block's own exception is never swallowed.
    - `enter_lesser_conduit()` makes a lesser for such a block, named or not.
    - A second soft cleanup of a pooled lesser does nothing.
    - A lesser's pool return disposes its descendants, then its SpellSpaces,
      then its own store.
    - Every exit finishes when a disposal method fails, then raises every
      failure as one ExceptionGroup; frame teardown logs a failing conduit.
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
from melder.utilities.logger.safe_logger import SafeLogger
from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)


class _Log:
    """
    Purpose:
        Record every disposal call of one test, in the order melder made them.
    Contract:
        `events` is replaced with a fresh list before each test by the fixture;
        `counts` numbers the objects of each kind so labels are stable.
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


class ConduitScoped:
    """unique_per_conduit object whose `close` records its disposal."""

    def __init__(self) -> None:
        """Take the next `conduit` label."""
        self.label = _Log.label("conduit")

    def close(self) -> None:
        """Record this object's disposal."""
        _Log.events.append(f"close:{self.label}")


class SpaceScoped:
    """unique_per_spell_space object whose `close` records its disposal."""

    def __init__(self) -> None:
        """Take the next `space` label."""
        self.label = _Log.label("space")

    def close(self) -> None:
        """Record this object's disposal."""
        _Log.events.append(f"close:{self.label}")


class FailingConduit:
    """unique_per_conduit object whose `close` records its disposal and then raises."""

    def __init__(self) -> None:
        """Take the next `failconduit` label."""
        self.label = _Log.label("failconduit")

    def close(self) -> None:
        """
        Record this object's disposal, then fail.

        Raises:
            RuntimeError: Always, naming this object.
        """
        _Log.events.append(f"close:{self.label}")
        raise RuntimeError(f"{self.label} close failed")


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
            "conduit": self._bind(ConduitScoped, Existence.unique_per_conduit),
            "space": self._bind(SpaceScoped, Existence.unique_per_spell_space),
            "failconduit": self._bind(FailingConduit, Existence.unique_per_conduit),
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


def test_with_on_a_lesser_disposes_it_and_returns_it_to_the_pool(world: _World) -> None:
    """At block exit the lesser's objects are disposed and the shell is reused by the next acquisition."""
    lesser = world.root.create_lesser_conduit()
    with lesser as held:
        assert held is lesser
        lesser.meld(spell_id=world.ids["conduit"])
        assert _Log.events == []

    assert _Log.events == ["close:conduit#1"]
    assert world.root.create_lesser_conduit() is lesser


def test_with_on_a_root_tears_the_root_down(world: _World) -> None:
    """A root used in `with` is permanently cleaned at block exit."""
    root = world.root
    with root:
        root.meld(spell_id=world.ids["conduit"])

    assert _Log.events == ["close:conduit#1"]
    assert root.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        root.check_cleaned()


def test_enter_lesser_conduit_returns_an_anonymous_lesser_released_at_exit(world: _World) -> None:
    """`enter_lesser_conduit()` yields a lesser whose block exit returns it to the pool."""
    with world.root.enter_lesser_conduit() as lesser:
        lesser.meld(spell_id=world.ids["conduit"])

    assert _Log.events == ["close:conduit#1"]
    assert world.root.create_lesser_conduit() is lesser


def test_enter_lesser_conduit_named_scope_is_retired_at_exit(world: _World) -> None:
    """A named lesser is discoverable inside the block and its name is released at exit."""
    aether = Aether()
    with world.root.enter_lesser_conduit(name="job") as lesser:
        assert aether.get_conduit_by_name("job") is lesser
        lesser.meld(spell_id=world.ids["conduit"])

    assert _Log.events == ["close:conduit#1"]
    with pytest.raises(ValueError):
        aether.get_conduit_by_name("job")
    assert world.root.create_lesser_conduit() is lesser


def test_with_keeps_the_block_error_and_still_returns_the_lesser(world: _World) -> None:
    """The block's exception propagates unchanged and the lesser is still disposed and pooled."""
    lesser = world.root.create_lesser_conduit()
    with pytest.raises(KeyError, match="boom"):
        with lesser:
            lesser.meld(spell_id=world.ids["conduit"])
            raise KeyError("boom")

    assert _Log.events == ["close:conduit#1"]
    assert world.root.create_lesser_conduit() is lesser


def test_with_raises_the_disposal_failure_chained_to_the_block_error(world: _World) -> None:
    """When both fail, the cleanup group rises with the block's error as its context; the lesser is pooled."""
    lesser = world.root.create_lesser_conduit()
    with pytest.raises(ExceptionGroup) as raised:
        with lesser:
            lesser.meld(spell_id=world.ids["failconduit"])
            raise KeyError("boom")

    assert isinstance(raised.value.__context__, KeyError)
    assert _causes(raised.value) == ["failconduit#1 close failed"]
    assert world.root.create_lesser_conduit() is lesser


def test_second_soft_cleanup_of_a_pooled_lesser_does_nothing(world: _World) -> None:
    """Cleaning a lesser twice pools it once, so two acquisitions get two different scopes."""
    lesser = world.root.create_lesser_conduit()
    lesser.cleanup()
    lesser.cleanup()

    first = world.root.create_lesser_conduit()
    second = world.root.create_lesser_conduit()
    assert first is lesser
    assert second is not lesser


def test_cleanup_inside_a_with_block_is_not_repeated_at_exit(world: _World) -> None:
    """An explicit cleanup inside the block leaves nothing for the exit to redo."""
    with world.root.create_lesser_conduit() as lesser:
        lesser.meld(spell_id=world.ids["conduit"])
        lesser.cleanup()

    assert _Log.events == ["close:conduit#1"]
    first = world.root.create_lesser_conduit()
    second = world.root.create_lesser_conduit()
    assert first is lesser
    assert second is not lesser


def test_lesser_pool_return_disposes_descendants_then_spaces_then_its_own_store(world: _World) -> None:
    """Children go first, then the lesser's SpellSpaces, then its own store - the permanent teardown order."""
    parent = world.root.create_lesser_conduit()
    child = parent.create_lesser_conduit()
    parent.meld(spell_id=world.ids["conduit"])
    child.meld(spell_id=world.ids["conduit"])
    space = parent.create_spellspace()
    space.meld(spell_id=world.ids["space"])

    parent.cleanup()

    assert _Log.events == ["close:conduit#2", "close:space#1", "close:conduit#1"]


def test_lesser_pool_return_with_a_failing_space_object_raises_after_returning(world: _World) -> None:
    """A failing SpellSpace object is reported, and the lesser and its space are both pooled."""
    lesser = world.root.create_lesser_conduit()
    space = lesser.create_spellspace()
    space.meld(spell_id=world.ids["failspace"])
    space.meld(spell_id=world.ids["space"])
    lesser.meld(spell_id=world.ids["conduit"])

    with pytest.raises(ExceptionGroup) as raised:
        lesser.cleanup()

    assert _causes(raised.value) == ["failspace#1 close failed"]
    assert _Log.events == ["close:space#1", "close:failspace#1", "close:conduit#1"]
    assert world.root.create_lesser_conduit() is lesser
    assert lesser.create_spellspace() is space


def test_lesser_pool_return_with_a_failing_own_object_raises_after_returning(world: _World) -> None:
    """A failing object in the lesser's own store is reported after the lesser is back in its pool."""
    lesser = world.root.create_lesser_conduit()
    lesser.meld(spell_id=world.ids["failconduit"])
    lesser.meld(spell_id=world.ids["conduit"])

    with pytest.raises(ExceptionGroup) as raised:
        lesser.cleanup()

    assert _causes(raised.value) == ["failconduit#1 close failed"]
    assert _Log.events == ["close:conduit#1", "close:failconduit#1"]
    assert world.root.create_lesser_conduit() is lesser


def test_child_disposal_failure_reaches_the_parent_and_both_are_pooled(world: _World) -> None:
    """A child that finished its own return with a failure does not keep its parent out of the pool."""
    parent = world.root.create_lesser_conduit()
    child = parent.create_lesser_conduit()
    child.meld(spell_id=world.ids["failconduit"])

    with pytest.raises(ExceptionGroup) as raised:
        parent.cleanup()

    assert _causes(raised.value) == ["failconduit#1 close failed"]
    assert world.root.create_lesser_conduit() is parent
    assert world.root.create_lesser_conduit() is child


def test_root_teardown_with_failing_objects_finishes_then_raises(world: _World) -> None:
    """Root teardown attempts every disposal, is fully cleaned, then raises both failures."""
    root = world.root
    root.meld(spell_id=world.ids["failconduit"])
    root.meld(spell_id=world.ids["conduit"])
    space = root.create_spellspace()
    space.meld(spell_id=world.ids["failspace"])

    with pytest.raises(ExceptionGroup) as raised:
        root.cleanup()

    assert sorted(_causes(raised.value)) == ["failconduit#1 close failed", "failspace#1 close failed"]
    assert _Log.events == ["close:failspace#1", "close:conduit#1", "close:failconduit#1"]
    assert root.cleaned is True


def test_root_teardown_raises_a_lesser_descendants_disposal_failure(world: _World) -> None:
    """A lesser's failing object, disposed during root teardown, reaches the root's caller."""
    root = world.root
    lesser = root.create_lesser_conduit()
    lesser.meld(spell_id=world.ids["failconduit"])

    with pytest.raises(ExceptionGroup) as raised:
        root.cleanup()

    assert _causes(raised.value) == ["failconduit#1 close failed"]
    assert root.cleaned is True


def test_frame_teardown_logs_a_failing_conduit_and_keeps_going(
        world: _World,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Frame teardown finishes when a conduit's teardown raises, and logs the failure."""
    logged: List[str] = []
    original_error = SafeLogger.error

    def record_error(self: SafeLogger, message: object, *args: object, **kwargs: object) -> object:
        """Record the logged message, then log it as usual."""
        logged.append(str(message))
        return original_error(self, message, *args, **kwargs)

    monkeypatch.setattr(SafeLogger, "error", record_error)
    world.root.meld(spell_id=world.ids["failconduit"])
    frame = world.root._aetheric_frame

    frame.cleanup()

    assert _Log.events == ["close:failconduit#1"]
    assert frame.cleaned is True
    assert any("frame teardown" in message for message in logged)
