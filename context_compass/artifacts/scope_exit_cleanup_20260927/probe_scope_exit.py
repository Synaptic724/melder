"""Probe: what each Conduit and SpellSpace exit or pool return disposes, and what a failure does.

Run from the repository root of a worktree with the 3.14 environment loaded:
    PYTHONPATH=src:. python <this file>

Every case builds a fresh Aether, binds recorder classes whose `close` logs a
disposal event, drives one exit path and prints what it observed. Nothing here
changes melder; read-only observation of the current tree.
"""

import sys
from typing import Callable, Dict, List, Optional

import melder
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.logger.safe_logger import SafeLogger
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Recorder:
    """Shared event log for one case; reset before every case."""

    events: List[str] = []
    counters: Dict[str, int] = {}
    logged_errors: List[str] = []

    @classmethod
    def reset(cls) -> None:
        """Clear the event log, counters and captured logger errors."""
        cls.events = []
        cls.counters = {}
        cls.logged_errors = []

    @classmethod
    def label(cls, kind: str) -> str:
        """Return the next label for one kind of object."""
        cls.counters[kind] = cls.counters.get(kind, 0) + 1
        return f"{kind}#{cls.counters[kind]}"


class SpaceScoped:
    """unique_per_spell_space object with a recording `close`."""

    def __init__(self) -> None:
        self.label = Recorder.label("space")

    def close(self) -> None:
        Recorder.events.append(f"close:{self.label}")


class ManyItem:
    """many object with a recording `close`."""

    def __init__(self) -> None:
        self.label = Recorder.label("many")

    def close(self) -> None:
        Recorder.events.append(f"close:{self.label}")


class ConduitScoped:
    """unique_per_conduit object with a recording `close`."""

    def __init__(self) -> None:
        self.label = Recorder.label("conduit")

    def close(self) -> None:
        Recorder.events.append(f"close:{self.label}")


class FailingSpace:
    """unique_per_spell_space object whose `close` records and then raises."""

    def __init__(self) -> None:
        self.label = Recorder.label("failspace")

    def close(self) -> None:
        Recorder.events.append(f"close:{self.label}")
        raise RuntimeError(f"{self.label} close failed")


class FailingConduit:
    """unique_per_conduit object whose `close` records and then raises."""

    def __init__(self) -> None:
        self.label = Recorder.label("failconduit")

    def close(self) -> None:
        Recorder.events.append(f"close:{self.label}")
        raise RuntimeError(f"{self.label} close failed")


class World:
    """One fresh Aether, a dynamic book with the recorder spells, and its root conduit."""

    def __init__(self) -> None:
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        configuration = SpellbookConfiguration()
        set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
        configuration.set_property("disposal", True)
        configuration.set_property("disposal_method_names", ["close"])
        configuration.load_default_dictionary()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        self.book = Spellbook(configuration=configuration)
        self.ids: Dict[str, str] = {
            "space": self.book.bind(spell=SpaceScoped, existence=Existence.unique_per_spell_space, permissions="create"),
            "many": self.book.bind(spell=ManyItem, existence=Existence.many, permissions="create"),
            "conduit": self.book.bind(spell=ConduitScoped, existence=Existence.unique_per_conduit, permissions="create"),
            "failspace": self.book.bind(spell=FailingSpace, existence=Existence.unique_per_spell_space, permissions="create"),
            "failconduit": self.book.bind(spell=FailingConduit, existence=Existence.unique_per_conduit, permissions="create"),
        }
        self.root = self.book.conjure(dynamic=True, name="root")

    def close(self) -> None:
        """Tear the world down and reset the singleton."""
        try:
            if not self.root._cleaned:
                self.root.cleanup()
        finally:
            Aether._reset_singleton_for_tests()


def describe_group(error: BaseException) -> str:
    """Return a one-line description of a raised error or group."""
    if isinstance(error, BaseExceptionGroup):
        inner = ", ".join(
            f"{type(e).__name__}(cause={type(e.__cause__).__name__ if e.__cause__ else None})"
            for e in error.exceptions
        )
        return f"{type(error).__name__}[{inner}]"
    return f"{type(error).__name__}({error})"


def idle(pool: object) -> int:
    """Return the number of idle objects in a melder pool."""
    return len(pool._idle)


def p1_managed_with_normal(world: World) -> Dict[str, object]:
    """Managed `with` exit on the normal path."""
    pool = world.root._spellspace_pool
    idle_before = idle(pool)
    with world.root.enter_spellspace() as space:
        space.meld(spell_id=world.ids["space"])
        space.meld(spell_id=world.ids["many"])
        space.meld(spell_id=world.ids["conduit"])
        idle_during = idle(pool)
    idle_after = idle(pool)
    with world.root.enter_spellspace() as again:
        same_shell = again is space
    return {
        "events_after_exit": list(Recorder.events),
        "idle_before/during/after": (idle_before, idle_during, idle_after),
        "next_lease_same_shell": same_shell,
    }


def p2_managed_with_failing(world: World) -> Dict[str, object]:
    """Managed `with` exit when one space object's `close` raises."""
    pool = world.root._spellspace_pool
    idle_before = idle(pool)
    raised: Optional[BaseException] = None
    space = None
    try:
        with world.root.enter_spellspace() as space:
            space.meld(spell_id=world.ids["failspace"])
            space.meld(spell_id=world.ids["space"])
    except BaseException as error:
        raised = error
    return {
        "raised": describe_group(raised) if raised else None,
        "events": list(Recorder.events),
        "idle_before/after": (idle_before, idle(pool)),
        "space_in_pool": space in pool._idle,
        "space_cleaned": space._cleaned,
        "space_meld_cleaned": space._meld._cleaned,
        "space_store_entries": len(space._creations._creations),
    }


def p3_stale_handle(world: World) -> Dict[str, object]:
    """A handle kept after `with` exit melds again; the next lease of that shell reads it."""
    with world.root.enter_spellspace() as space:
        first = space.meld(spell_id=world.ids["space"])
    events_after_first_exit = list(Recorder.events)
    stale_error: Optional[str] = None
    stale_obj = None
    try:
        stale_obj = space.meld(spell_id=world.ids["space"])
    except BaseException as error:
        stale_error = describe_group(error)
    with world.root.enter_spellspace() as next_lease:
        same_shell = next_lease is space
        served = next_lease.meld(spell_id=world.ids["space"])
    return {
        "events_after_first_exit": events_after_first_exit,
        "stale_meld_error": stale_error,
        "stale_meld_label": getattr(stale_obj, "label", None),
        "next_lease_same_shell": same_shell,
        "next_lease_served_label": served.label,
        "next_lease_got_stale_object": served is stale_obj,
        "first_is_stale": first is stale_obj,
        "events_after_second_exit": list(Recorder.events),
    }


def p4_manual_cleanup(world: World) -> Dict[str, object]:
    """Manual create_spellspace() + cleanup(), normal and failing, then a retry."""
    registry = world.root._spellspace_registry
    pool = world.root._spellspace_pool
    space = world.root.create_spellspace()
    space.meld(spell_id=world.ids["space"])
    space.cleanup()
    normal = {
        "events": list(Recorder.events),
        "registered_after": space in registry,
        "pooled_after": space in pool._idle,
    }
    Recorder.reset()
    failing_space = world.root.create_spellspace()
    failing_space.meld(spell_id=world.ids["failspace"])
    failing_space.meld(spell_id=world.ids["space"])
    raised: Optional[BaseException] = None
    try:
        failing_space.cleanup()
    except BaseException as error:
        raised = error
    failing = {
        "raised": describe_group(raised) if raised else None,
        "events": list(Recorder.events),
        "registered_after": failing_space in registry,
        "pooled_after": failing_space in pool._idle,
    }
    retry_error: Optional[str] = None
    try:
        failing_space.cleanup()
    except BaseException as error:
        retry_error = describe_group(error)
    failing["retry_error"] = retry_error
    failing["registered_after_retry"] = failing_space in registry
    failing["pooled_after_retry"] = failing_space in pool._idle
    return {"normal": normal, "failing": failing}


def p5_with_lesser(world: World) -> Dict[str, object]:
    """`with lesser:` - lock context or lifecycle scope?"""
    lesser = world.root.create_lesser_conduit()
    with lesser as held:
        held.meld(spell_id=world.ids["conduit"])
    after_block = list(Recorder.events)
    still_usable = lesser.meld(spell_id=world.ids["conduit"]).label
    lesser.cleanup()
    return {
        "events_after_with_block": after_block,
        "meld_after_block": still_usable,
        "events_after_explicit_cleanup": list(Recorder.events),
    }


def p6_lesser_return_order(world: World) -> Dict[str, object]:
    """Lesser pool return with an open manual space and a named child: what is disposed, in what order."""
    root_pool = world.root._conduit_pool
    idle_before = idle(root_pool)
    parent = world.root.create_lesser_conduit()
    child = parent.create_lesser_conduit(name="probe-child")
    parent.meld(spell_id=world.ids["conduit"])
    child.meld(spell_id=world.ids["conduit"])
    manual = parent.create_spellspace()
    manual.meld(spell_id=world.ids["space"])
    parent.cleanup()
    return {
        "events_in_order": list(Recorder.events),
        "parent_pooled": parent in root_pool._idle,
        "child_pooled": child in root_pool._idle,
        "root_idle_before/after": (idle_before, idle(root_pool)),
    }


def p7_lesser_return_failing_space(world: World) -> Dict[str, object]:
    """Lesser pool return when an open manual space holds a failing object."""
    lesser = world.root.create_lesser_conduit()
    manual = lesser.create_spellspace()
    manual.meld(spell_id=world.ids["failspace"])
    manual.meld(spell_id=world.ids["space"])
    lesser.meld(spell_id=world.ids["conduit"])
    raised: Optional[BaseException] = None
    try:
        lesser.cleanup()
    except BaseException as error:
        raised = error
    return {
        "raised": describe_group(raised) if raised else None,
        "logged_errors": list(Recorder.logged_errors),
        "events": list(Recorder.events),
        "lesser_pooled": lesser in world.root._conduit_pool._idle,
        "space_pooled": manual in lesser._spellspace_pool._idle,
        "space_cleaned": manual._cleaned,
    }


def p8_lesser_return_failing_own(world: World) -> Dict[str, object]:
    """Lesser pool return when its own store holds a failing object, then a retry."""
    lesser = world.root.create_lesser_conduit()
    lesser.meld(spell_id=world.ids["failconduit"])
    lesser.meld(spell_id=world.ids["conduit"])
    raised: Optional[BaseException] = None
    try:
        lesser.cleanup()
    except BaseException as error:
        raised = error
    first = {
        "raised": describe_group(raised) if raised else None,
        "events": list(Recorder.events),
        "still_child_of_root": lesser._id in world.root._conduit_ward._lesser_conduits,
        "state": str(lesser._conduit_state),
        "pooled": lesser in world.root._conduit_pool._idle,
    }
    retry_error: Optional[str] = None
    try:
        lesser.cleanup()
    except BaseException as error:
        retry_error = describe_group(error)
    first["retry_error"] = retry_error
    first["pooled_after_retry"] = lesser in world.root._conduit_pool._idle
    return first


def p9_root_cleanup_failing(world: World) -> Dict[str, object]:
    """Root permanent cleanup with a failing conduit object and a failing manual-space object."""
    world.root.meld(spell_id=world.ids["failconduit"])
    world.root.meld(spell_id=world.ids["conduit"])
    manual = world.root.create_spellspace()
    manual.meld(spell_id=world.ids["failspace"])
    raised: Optional[BaseException] = None
    try:
        world.root.cleanup()
    except BaseException as error:
        raised = error
    return {
        "raised": describe_group(raised) if raised else None,
        "logged_errors": list(Recorder.logged_errors),
        "events": list(Recorder.events),
        "root_cleaned": world.root._cleaned,
    }


def p10_lesser_cleaned_inside_its_space(world: World) -> Dict[str, object]:
    """A lesser cleaned while one of its managed spaces is still open on this thread."""
    lesser = world.root.create_lesser_conduit()
    raised: Optional[BaseException] = None
    space = None
    try:
        with lesser.enter_spellspace() as space:
            space.meld(spell_id=world.ids["space"])
            lesser.cleanup()
    except BaseException as error:
        raised = error
    return {
        "raised_at_with_exit": describe_group(raised) if raised else None,
        "events": list(Recorder.events),
        "lesser_pooled": lesser in world.root._conduit_pool._idle,
        "space_in_lesser_pool": space in lesser._spellspace_pool._idle,
    }


CASES: List[Callable[[World], Dict[str, object]]] = [
    p1_managed_with_normal,
    p2_managed_with_failing,
    p3_stale_handle,
    p4_manual_cleanup,
    p5_with_lesser,
    p6_lesser_return_order,
    p7_lesser_return_failing_space,
    p8_lesser_return_failing_own,
    p9_root_cleanup_failing,
    p10_lesser_cleaned_inside_its_space,
]


def main() -> int:
    """Run every case in a fresh world and print its observations."""
    assert sys.version_info >= (3, 14), sys.version
    original_error = SafeLogger.error

    def recording_error(self: SafeLogger, message: object, *args: object, **kwargs: object) -> object:
        Recorder.logged_errors.append(str(message))
        return original_error(self, message, *args, **kwargs)

    SafeLogger.error = recording_error
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} melder={melder.__file__}")
    try:
        for case in CASES:
            Recorder.reset()
            world = World()
            try:
                result = case(world)
            except BaseException as error:
                result = {"CASE_CRASHED": describe_group(error)}
            finally:
                world_errors: List[str] = []
                try:
                    world.close()
                except BaseException as error:
                    world_errors.append(describe_group(error))
            print(f"== {case.__name__}")
            for key, value in result.items():
                print(f"   {key}: {value}")
            if world_errors:
                print(f"   world_close_error: {world_errors}")
    finally:
        SafeLogger.error = original_error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
