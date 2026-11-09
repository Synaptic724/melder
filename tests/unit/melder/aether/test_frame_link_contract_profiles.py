import threading
from operator import attrgetter, methodcaller
from types import MemberDescriptorType, TracebackType
from typing import Callable, Optional, Tuple, Type

import pytest

from melder.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


class _LockReadHook:
    """
    Stand-in for the `_lock` slot of a per-test `FrameLinkContract` subclass that runs one armed callback first.

    Purpose:
        Reproduce on one thread the free-threaded window between a caller's outer `_cleaned` check and its load of
        `self._lock`: the armed callback (a complete `cleanup()`) runs inside the caller's next `_lock` read, before
        the slot is read, so the caller then loads `_lock` from a contract another cleanup has just torn down. The
        order comes from that nesting, never from timing (GitHub #271).

    Contract:
        - Reads, writes and deletes go to the real `FrameLinkContract._lock` slot.
        - `arm(callback)` makes the next read run `callback` first. The callback is disarmed before it runs, so the
          reads it makes itself (the nested cleanup's own `with self._lock`) read the slot plainly.
    """

    def __init__(self, slot: MemberDescriptorType) -> None:
        """
        Wrap the real slot descriptor, unarmed.

        Args:
            slot: `FrameLinkContract.__dict__["_lock"]`, the descriptor that stores the contract's lock.

        Returns:
            None.
        """
        self._slot: MemberDescriptorType = slot
        self._callback: Optional[Callable[[], None]] = None

    def arm(self, callback: Callable[[], None]) -> None:
        """
        Run `callback` at the start of the next `_lock` read.

        Args:
            callback: What overtakes the reader between its outer check and its lock load.

        Returns:
            None.
        """
        self._callback = callback

    def __get__(self, instance: Optional[FrameLinkContract], owner: Optional[type] = None) -> object:
        """
        Run the armed callback once, then read the real slot.

        Args:
            instance: The contract whose `_lock` is read, or None for class access.
            owner: The class the attribute was looked up on.

        Returns:
            object: The stored lock, or this hook for class access.

        Raises:
            AttributeError: When the slot is empty because a cleanup deleted `_lock`.
        """
        if instance is None:
            return self
        callback, self._callback = self._callback, None
        if callback is not None:
            callback()
        return self._slot.__get__(instance, owner)

    def __set__(self, instance: FrameLinkContract, value: object) -> None:
        """
        Store `value` in the real slot, as `__init__` does.

        Args:
            instance: The contract being written.
            value: The lock to store.

        Returns:
            None.
        """
        self._slot.__set__(instance, value)

    def __delete__(self, instance: FrameLinkContract) -> None:
        """
        Empty the real slot, as a `del self._lock` does.

        Args:
            instance: The contract being written.

        Returns:
            None.
        """
        self._slot.__delete__(instance)


def _contract_with_lock_read_hook() -> Tuple[FrameLinkContract, _LockReadHook]:
    """
    Build a live contract whose `_lock` is read through a fresh, unarmed `_LockReadHook`.

    Returns:
        Tuple[FrameLinkContract, _LockReadHook]: The contract - a subclass that inherits every method unchanged - and
        its hook.
    """
    hook = _LockReadHook(FrameLinkContract.__dict__["_lock"])

    class _LockReadHookedContract(FrameLinkContract):
        """`FrameLinkContract` whose `_lock` slot is read through `hook`; nothing else differs."""

        __slots__ = ()
        _lock = hook

    contract = _LockReadHookedContract(rift_id="rift-1", frame_name="ops", metadata={"rift_name": "pricing_rift"})
    return contract, hook


class _CleanupBeforeAcquireLock:
    """
    Stand-in for a contract's `_lock` whose first entry runs a complete `cleanup()` before it acquires.

    Purpose:
        Reproduce on one thread a read that loaded `_lock` and then waited on it while a concurrent cleanup tore the
        contract down: by the time the read holds the lock, the contract is cleaned and its state deleted. The nested
        entry (the cleanup's own `with self._lock`) acquires without running the cleanup again (GitHub #271).

    Contract:
        - Wraps one real `RLock`; `__exit__` releases it and never suppresses the block's exception.
    """

    def __init__(self, contract: FrameLinkContract) -> None:
        """
        Borrow the contract and prepare an unheld `RLock` with the cleanup pending.

        Args:
            contract: The contract whose `_lock` this object replaces.

        Returns:
            None.
        """
        self._contract: FrameLinkContract = contract
        self._lock: threading.RLock = threading.RLock()
        self._cleanup_pending: bool = True

    def __enter__(self) -> _CleanupBeforeAcquireLock:
        """
        Run the pending cleanup once, then acquire.

        Returns:
            _CleanupBeforeAcquireLock: This lock, as `with` binds it.
        """
        if self._cleanup_pending:
            self._cleanup_pending = False
            self._contract.cleanup()
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


def test_frame_link_contract_defaults_to_frame_name_selection() -> None:
    """
    Verify one per-frame contract defaults every ACL family to `frame_name`.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    assert contract.frame_name == "ops"
    assert contract.get_selected_contract_names() == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }
    assert contract.get_selected_contract_name() == "ops"


def test_frame_link_contract_properties_and_snapshot_views_are_detached() -> None:
    """
    Verify metadata and selection snapshots are detached.

    Returns:
        None.
    """
    metadata = {"mode": "safe"}
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
        metadata=metadata,
    )

    metadata["mutated"] = True
    selection_snapshot = contract.get_selected_contract_names()
    selection_snapshot["view"] = "mutated"

    assert contract.contract_id
    assert contract.rift_id == "rift-1"
    assert contract.frame_name == "ops"
    assert contract.metadata == {"mode": "safe"}
    assert contract.get_selected_contract_names() == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }


def test_frame_link_contract_rejects_invalid_inputs() -> None:
    """
    Verify the one-frame contract rejects malformed inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="rift_id cannot be empty"):
        FrameLinkContract(rift_id="", frame_name="ops")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameLinkContract(rift_id="rift-1", frame_name="")


def test_frame_link_contract_describe_and_clone_include_selection() -> None:
    """
    Verify describe and clone preserve per-frame selection.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    description = contract.describe()
    clone = contract.clone()

    assert description["frame_name"] == "ops"
    assert description["selected_contract_names"] == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }
    assert clone.frame_name == "ops"
    assert clone.get_selected_contract_names() == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }


def test_frame_link_contract_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify a second cleanup caller that passed the outer check returns at the inner `_cleaned` recheck.

    The handshake holds the first caller inside the lock until the second has passed the outer check and is about
    to block, then marks the contract cleaned, as a cleanup racing in from elsewhere would. Both callers must
    finish without raising - without the inner recheck they would clear state that is already gone - and the
    contract must read cleaned. The callers are ordered by the handshake, not by timing: the earlier hand-made
    lock could lose its signal and failed on CI (GitHub #206; TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    def _mark_cleaned() -> None:
        """Mark the contract cleaned while the first caller holds the lock and the second waits for it."""
        contract._cleaned = True

    handshake = CleanupRecheckHandshake(on_holder_ready=_mark_cleaned)
    contract._lock = handshake.lock

    handshake.run(contract.cleanup)

    assert contract.cleaned is True


def test_frame_link_contract_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    contract.cleanup()
    contract.cleanup()

    assert contract.cleaned is True


def test_frame_link_contract_cleanup_tears_down_owned_state() -> None:
    """
    Verify a real cleanup clears the selection and metadata maps and deletes the owned fields, as documented.

    The in-lock recheck test above marks the contract cleaned by hand, so its callers return before any teardown;
    this one runs the actual teardown. The maps are held from before the cleanup, so the test can see they were
    cleared and not merely dropped (GitHub #206 requirement 3).

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1", frame_name="ops", metadata={"rift_name": "pricing_rift"})
    selection = contract._selected_contract_names
    metadata = contract._metadata

    contract.cleanup()

    assert contract.cleaned is True
    assert selection == {}
    assert metadata == {}
    for field_name in ("_id", "_rift_id", "_frame_name", "_selected_contract_names", "_metadata"):
        with pytest.raises(AttributeError):
            getattr(contract, field_name)


@pytest.mark.parametrize(
    "read",
    [
        pytest.param(attrgetter("contract_id"), id="contract_id"),
        pytest.param(attrgetter("rift_id"), id="rift_id"),
        pytest.param(attrgetter("frame_name"), id="frame_name"),
        pytest.param(attrgetter("metadata"), id="metadata"),
        pytest.param(methodcaller("get_selected_contract_names"), id="get_selected_contract_names"),
        pytest.param(methodcaller("get_selected_contract_name"), id="get_selected_contract_name"),
        pytest.param(methodcaller("describe"), id="describe"),
        pytest.param(methodcaller("clone"), id="clone"),
    ],
)
def test_frame_link_contract_reads_raise_cleaned_runtime_error_after_cleanup(
        read: Callable[[FrameLinkContract], object],
) -> None:
    """
    Verify every public read of a cleaned contract raises the documented `RuntimeError`.

    Args:
        read: One public property or method read of the contract.

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1", frame_name="ops", metadata={"rift_name": "pricing_rift"})
    contract.cleanup()

    with pytest.raises(RuntimeError, match="FrameLinkContract has already been cleaned"):
        read(contract)


def test_frame_link_contract_concurrent_cleanup_tears_down_once_and_both_callers_return() -> None:
    """
    Verify two concurrent cleanups tear the contract down once and both return, with the GIL off as on.

    The handshake holds the first caller inside the lock until the second has passed the outer check and is about to
    block, then lets the first run the real teardown. The second must return at the in-lock recheck: had it torn
    down again it would raise on the state the first deleted, and the handshake reports any caller's error. A third
    call afterwards returns too (GitHub #206 requirement 3).

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1", frame_name="ops", metadata={"rift_name": "pricing_rift"})
    selection = contract._selected_contract_names
    handshake = CleanupRecheckHandshake()
    contract._lock = handshake.lock

    handshake.run(contract.cleanup)

    assert contract.cleaned is True
    assert selection == {}
    with pytest.raises(RuntimeError, match="FrameLinkContract has already been cleaned"):
        contract.describe()
    contract.cleanup()


def test_frame_link_contract_cleanup_after_concurrent_teardown_raises_no_missing_lock_error() -> None:
    """
    A `cleanup()` that passed its outer `_cleaned` check while another cleanup ran to completion returns quietly.

    Symptom (GitHub #271): cleanup ended with `del self._lock`, so a second caller past its outer check but not yet
    holding the lock raised `AttributeError: ... object has no attribute '_lock'` instead of returning at the
    in-lock recheck - Cleanable's idempotence broken on free-threaded builds. The hook runs the first cleanup inside
    the second caller's `_lock` read, which is exactly that interleaving with no thread to time.

    Returns:
        None.
    """
    contract, hook = _contract_with_lock_read_hook()
    hook.arm(contract.cleanup)

    contract.cleanup()

    assert contract.cleaned is True
    # check_cleaned() names the runtime class, here the hooked subclass.
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        contract.frame_name


@pytest.mark.parametrize(
    "read",
    [
        pytest.param(methodcaller("get_selected_contract_names"), id="get_selected_contract_names"),
        pytest.param(methodcaller("get_selected_contract_name"), id="get_selected_contract_name"),
        pytest.param(methodcaller("describe"), id="describe"),
        pytest.param(methodcaller("clone"), id="clone"),
    ],
)
@pytest.mark.parametrize("window", ["before_lock_load", "while_waiting_on_lock"])
def test_frame_link_contract_locked_read_racing_cleanup_raises_cleaned_error_not_attribute_error(
        read: Callable[[FrameLinkContract], object],
        window: str,
) -> None:
    """
    A lock-guarded read overtaken by a concurrent cleanup raises the documented `RuntimeError`, not `AttributeError`.

    Symptom (GitHub #271): these four reads check `_cleaned` and then take `_lock` - the lock cleanup sets `_cleaned`
    and deletes the state under - but did not check again under it. Overtaken before its lock load, a read raised
    `AttributeError: ... no attribute '_lock'`; overtaken while it waited on the lock, it raised `AttributeError` for
    the deleted selection or ids. Cleanable's pattern (check, acquire, check again under the lock) gives the
    documented error in both windows.

    Args:
        read: One lock-guarded read of the contract.
        window: Where the cleanup overtakes the read: before its lock load, or while it waits on the lock.

    Returns:
        None.
    """
    if window == "before_lock_load":
        contract, hook = _contract_with_lock_read_hook()
        hook.arm(contract.cleanup)
    else:
        contract = FrameLinkContract(rift_id="rift-1", frame_name="ops", metadata={"rift_name": "pricing_rift"})
        contract._lock = _CleanupBeforeAcquireLock(contract)

    # check_cleaned() names the runtime class, which is the hooked subclass in the first window.
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        read(contract)

    assert contract.cleaned is True
