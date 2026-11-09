"""
Component regressions for two Rift races (GitHub #274, R4 and R5): a Rift is used by several agents at once, so its
own frame attach and projection refresh must leave Melder's records right when they overlap another attach or the
Rift's removal.

Each test reproduces one interleaving on a single thread by nesting the overlapping call inside the first one - in a
patched Nexus step or in a lock stand-in's first entry - so the order comes from the nesting, never from timing.
"""
import threading
from types import TracebackType
from typing import Callable, Dict, List, Optional, Tuple, Type

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.projection.frame_projection_set import FrameProjectionSet
from melder.nexus.rift.rift import Rift
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


class _Pricing:
    """A spell that gives the `default` frame descriptor truth, so a Rift can attach it."""

    def __init__(self) -> None:
        """
        Build the spell's one value.

        Returns:
            None.
        """
        self.rate: int = 100


class _RunBeforeFirstAcquireLock:
    """
    Stand-in for a Rift's `_lock` whose first entry runs one action before it acquires.

    Purpose:
        Reproduce on one thread a call that passed its outer `_cleaned` check, loaded the Rift's lock and then waited
        on it while another caller removed the Rift. The action - a full `Nexus.remove_rift` - runs inside the first
        `with self._lock` before the acquisition; the removal's own nested entries acquire plainly.

    Contract:
        - Wraps one real `RLock`; `__exit__` releases it and never suppresses the block's exception.
    """

    def __init__(self, action: Callable[[], None]) -> None:
        """
        Prepare an unheld `RLock` with the action pending.

        Args:
            action: What overtakes the waiting caller.

        Returns:
            None.
        """
        self._lock: threading.RLock = threading.RLock()
        self._action: Optional[Callable[[], None]] = action

    def __enter__(self) -> "_RunBeforeFirstAcquireLock":
        """
        Run the pending action once, then acquire.

        Returns:
            _RunBeforeFirstAcquireLock: This lock, as `with` binds it.
        """
        action, self._action = self._action, None
        if action is not None:
            action()
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None:
        """
        Release the matching acquisition; never suppress the block's exception.

        Args:
            exc_type: The exception type raised in the block, or None.
            exc: The exception raised in the block, or None.
            tb: Its traceback, or None.

        Returns:
            None.
        """
        self._lock.release()


def _reset_runtime_singletons() -> None:
    """
    Give every test a fresh Melder world.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    CommandSystem._aether = aether


@pytest.fixture(autouse=True)
def _isolated_runtime() -> None:
    """
    Reset the singletons around each test.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _build_world(*, link: bool) -> Tuple[Nexus, Rift]:
    """
    Build a dynamic `default` frame with descriptor truth, an enabled Nexus and one capability Rift.

    Args:
        link: Whether the Rift attaches `default` before the test runs.

    Returns:
        Tuple[Nexus, Rift]: The Nexus and the Rift.
    """
    configuration = SpellbookConfiguration(aether_frame="default")
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=True, rift_enabled=True)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(aetheric_frame="default", configuration=configuration)
    spellbook.bind(spell=_Pricing, existence=Existence.unique, permissions="create", spellframe="pricing")
    spellbook.conjure(name="pricing_root", dynamic=True)
    nexus = Nexus()
    nexus_configuration = nexus.create_configuration()
    nexus_configuration.with_rift_creation_enabled(True)
    nexus_configuration.with_direct_rift_access(True)
    nexus_configuration.with_target_frame_override(True)
    nexus_configuration.with_multiple_target_frames(True)
    nexus_configuration.with_max_target_frame_count(8)
    nexus_configuration.with_allowed_target_frame_names(("default",))
    nexus_configuration.with_nexus_frame_mode("indexed")
    nexus_configuration.with_max_nexus_frame_count(8)
    nexus.activate(nexus_configuration)
    rift = nexus.create_rift(
        configuration=nexus.create_rift_configuration().with_space_type(RiftSpaceType.capability),
        rift_name="pricing_rift",
    )
    if link:
        rift.create_frame_link("default")
    return nexus, rift


def test_two_attaches_of_one_frame_keep_one_contract_and_one_budget_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Two attaches of one frame on one Rift leave one contract and one target-frame budget count.

    Symptom (GitHub #274, R4): `create_frame_link` checked whether the frame was new, reserved a budget slot and wrote
    its contract with nothing ordering it against a second attach, so both reserved and the second overwrote the first:
    a contract never cleaned, a budget count of 2, and 1 left after `remove_rift` - the frame's slot leaked. Here the
    other attach runs to completion inside the first one's reservation.

    Returns:
        None.
    """
    nexus, rift = _build_world(link=False)
    original_reserve = Nexus._reserve_target_frame
    other_attaches: List[str] = []

    def reserve_then_let_another_attach_finish(self: Nexus, target_frame_name: str) -> None:
        original_reserve(self, target_frame_name)
        if not other_attaches:
            other_attaches.append(target_frame_name)
            rift.create_frame_link(target_frame_name)

    monkeypatch.setattr(Nexus, "_reserve_target_frame", reserve_then_let_another_attach_finish)

    rift.create_frame_link("default")

    assert other_attaches == ["default"]
    assert nexus._target_frame_ref_counts == {"default": 1}
    published = rift.get_frame_link_contract("default")
    assert rift.list_assigned_frame_names() == ("default",)

    nexus.remove_rift(rift.id)

    assert "default" not in nexus._target_frame_ref_counts
    assert published.cleaned is True


def test_attach_racing_rift_removal_gives_its_reservation_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    An attach whose Rift is removed after its budget reservation gives it back and raises the cleaned error.

    Symptom (GitHub #274, R4): the attach wrote its contract into a registry the removal had deleted, raising
    AttributeError, and its reservation was never given back, so the frame's budget slot leaked. Here the removal runs
    inside the attach's reservation.

    Returns:
        None.
    """
    nexus, rift = _build_world(link=False)
    rift_id = rift.id
    original_reserve = Nexus._reserve_target_frame

    def reserve_then_remove_the_rift(self: Nexus, target_frame_name: str) -> None:
        original_reserve(self, target_frame_name)
        self.remove_rift(rift_id)

    monkeypatch.setattr(Nexus, "_reserve_target_frame", reserve_then_remove_the_rift)

    with pytest.raises(RuntimeError, match="Rift has already been cleaned"):
        rift.create_frame_link("default")

    assert "default" not in nexus._target_frame_ref_counts


@pytest.mark.parametrize("window", ["before_apply", "while_waiting_on_lock"])
def test_refresh_racing_rift_removal_cleans_its_fresh_projection_sets(
        monkeypatch: pytest.MonkeyPatch,
        window: str,
) -> None:
    """
    A projection refresh whose Rift is removed before it applies cleans the projection sets it built and raises.

    Symptom (GitHub #274, R5): the fresh sets Nexus built for the refresh were installed nowhere and cleaned by no one
    when the Rift was removed first, and a removal while the refresh waited on the Rift lock made the apply raise
    AttributeError on the deleted registry. Both windows: the removal right after Nexus built the sets, and the removal
    inside the apply's lock entry.

    Args:
        window: Where the removal overtakes the refresh.

    Returns:
        None.
    """
    nexus, rift = _build_world(link=True)
    rift_id = rift.id
    original_build = Nexus.create_frame_projection_sets_for_rift
    built: List[Dict[str, FrameProjectionSet]] = []

    def build_then_maybe_remove(self: Nexus, *args: object, **kwargs: object) -> Dict[str, FrameProjectionSet]:
        projection_sets = original_build(self, *args, **kwargs)
        built.append(projection_sets)
        if window == "before_apply":
            self.remove_rift(rift_id)
        return projection_sets

    monkeypatch.setattr(Nexus, "create_frame_projection_sets_for_rift", build_then_maybe_remove)
    if window == "while_waiting_on_lock":
        rift._lock = _RunBeforeFirstAcquireLock(lambda: nexus.remove_rift(rift_id))

    with pytest.raises(RuntimeError, match="Rift has already been cleaned"):
        rift.refresh_runtime_projections()

    assert len(built) == 1
    assert built[0]
    assert all(projection_set.cleaned for projection_set in built[0].values())
