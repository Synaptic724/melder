import threading
import time
from typing import Any, Dict


class _DeleteCleanupProbe:
    """
    Minimal probe for lock-attribute deletion experiments.

    Purpose:
        Isolate Python object-reference behavior when a stored lock attribute is
        deleted during or after cleanup.

    Contract:
        - The probe owns exactly one `_lock` reference and one `_cleaned` flag.
        - `cleanup_delete_attribute()` deletes the lock attribute without first
          acquiring it so we can observe raw attribute-deletion semantics.
        - `cleanup_delete_inside_with()` deletes the lock attribute while the
          cleanup call itself is inside `with self._lock:`.
        - Worker methods intentionally use `with self._lock:` or a local lock
          snapshot so we can observe the difference between already-held or
          already-snapshotted references and fresh post-delete access.
    """

    __slots__ = ("_lock", "_cleaned")

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cleaned = False

    def cleanup_delete_attribute(self) -> None:
        """
        Delete the lock attribute without acquiring the lock first.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._lock

    def cleanup_delete_inside_with(self) -> None:
        """
        Delete the lock attribute while cleanup is inside `with self._lock:`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._lock

    def hold_lock_via_attribute(
            self,
            *,
            acquired_event: threading.Event,
            release_event: threading.Event,
            finished_event: threading.Event,
    ) -> None:
        """
        Acquire the lock through normal attribute access and hold it.

        Args:
            acquired_event:
                Set once the lock has been acquired.
            release_event:
                Wait target used to keep the holder inside the critical section.
            finished_event:
                Set after the holder exits the critical section.

        Returns:
            None.
        """
        with self._lock:
            acquired_event.set()
            release_event.wait(timeout=1.0)
        finished_event.set()

    def wait_on_snapshotted_lock(
            self,
            *,
            snapshotted_event: threading.Event,
            acquired_event: threading.Event,
            finished_event: threading.Event,
    ) -> None:
        """
        Snapshot the lock reference first, then wait to acquire it.

        Args:
            snapshotted_event:
                Set immediately after the local lock snapshot is taken.
            acquired_event:
                Set once the worker finally acquires the snapshotted lock.
            finished_event:
                Set after the worker exits the critical section.

        Returns:
            None.
        """
        lock = self._lock
        snapshotted_event.set()
        with lock:
            acquired_event.set()
        finished_event.set()

    def enter_via_attribute(self) -> str:
        """
        Enter the critical section through a fresh `self._lock` attribute read.

        Returns:
            str:
                Constant success marker when entry succeeds.
        """
        with self._lock:
            return "entered"


def _can_reacquire(lock: Any) -> bool:
    """
    Return whether another thread can still acquire the original lock object.

    Args:
        lock:
            Original lock object captured before attribute deletion.

    Returns:
        bool:
            True when a fresh thread can acquire and release the original lock.
    """
    result: Dict[str, bool] = {"acquired": False}

    def worker() -> None:
        acquired = lock.acquire(timeout=0.5)
        result["acquired"] = acquired
        if acquired:
            lock.release()

    thread = threading.Thread(target=worker, name="lock-reacquire-probe")
    thread.start()
    thread.join(timeout=1.0)
    return result["acquired"]


def _run_cleanup_inside_with_scenario() -> Dict[str, str]:
    """
    Observe deleting the lock attribute inside the cleanup `with` block itself.

    Returns:
        Dict[str, str]:
            Human-readable outcome summary.
    """
    probe = _DeleteCleanupProbe()
    original_lock = probe._lock

    probe.cleanup_delete_inside_with()

    reacquired = _can_reacquire(original_lock)
    assert reacquired is True
    assert hasattr(probe, "_lock") is False

    return {
        "deleted_attribute": "yes",
        "cleanup_returned": "yes",
        "original_lock_reacquired_after_cleanup": str(reacquired),
        "fresh_attribute_present_after_cleanup": str(hasattr(probe, "_lock")),
    }


def _run_active_holder_then_delete_scenario() -> Dict[str, str]:
    """
    Observe what happens when the attribute is deleted while another thread is holding the lock.

    Returns:
        Dict[str, str]:
            Human-readable outcome summary.
    """
    probe = _DeleteCleanupProbe()
    original_lock = probe._lock
    holder_acquired_event = threading.Event()
    holder_release_event = threading.Event()
    holder_finished_event = threading.Event()

    holder = threading.Thread(
        target=probe.hold_lock_via_attribute,
        kwargs={
            "acquired_event": holder_acquired_event,
            "release_event": holder_release_event,
            "finished_event": holder_finished_event,
        },
        name="holder-thread",
    )
    holder.start()
    holder_acquired_event.wait(timeout=1.0)
    assert holder_acquired_event.is_set()

    probe.cleanup_delete_attribute()
    assert hasattr(probe, "_lock") is False

    holder_release_event.set()
    holder.join(timeout=1.0)
    assert holder_finished_event.is_set()

    reacquired = _can_reacquire(original_lock)
    assert reacquired is True

    return {
        "deleted_attribute_while_holder_active": "yes",
        "holder_finished_normally": str(holder_finished_event.is_set()),
        "original_lock_reacquired_after_holder_exit": str(reacquired),
        "fresh_attribute_present_after_cleanup": str(hasattr(probe, "_lock")),
    }


def _run_snapshotted_waiter_then_delete_scenario() -> Dict[str, str]:
    """
    Observe what happens when a waiter already holds a local snapshot of the lock.

    Returns:
        Dict[str, str]:
            Human-readable outcome summary.
    """
    probe = _DeleteCleanupProbe()
    holder_acquired_event = threading.Event()
    holder_release_event = threading.Event()
    holder_finished_event = threading.Event()
    waiter_snapshotted_event = threading.Event()
    waiter_acquired_event = threading.Event()
    waiter_finished_event = threading.Event()

    holder = threading.Thread(
        target=probe.hold_lock_via_attribute,
        kwargs={
            "acquired_event": holder_acquired_event,
            "release_event": holder_release_event,
            "finished_event": holder_finished_event,
        },
        name="holder-thread",
    )
    waiter = threading.Thread(
        target=probe.wait_on_snapshotted_lock,
        kwargs={
            "snapshotted_event": waiter_snapshotted_event,
            "acquired_event": waiter_acquired_event,
            "finished_event": waiter_finished_event,
        },
        name="waiter-thread",
    )

    holder.start()
    holder_acquired_event.wait(timeout=1.0)
    assert holder_acquired_event.is_set()

    waiter.start()
    waiter_snapshotted_event.wait(timeout=1.0)
    assert waiter_snapshotted_event.is_set()

    time.sleep(0.05)
    assert waiter_acquired_event.is_set() is False

    probe.cleanup_delete_attribute()
    assert hasattr(probe, "_lock") is False

    holder_release_event.set()
    holder.join(timeout=1.0)
    waiter.join(timeout=1.0)

    assert holder_finished_event.is_set()
    assert waiter_acquired_event.is_set()
    assert waiter_finished_event.is_set()

    return {
        "waiter_snapshotted_before_delete": str(waiter_snapshotted_event.is_set()),
        "waiter_acquired_after_holder_release": str(waiter_acquired_event.is_set()),
        "waiter_finished_normally": str(waiter_finished_event.is_set()),
        "fresh_attribute_present_after_cleanup": str(hasattr(probe, "_lock")),
    }


def _run_fresh_access_after_delete_scenario() -> Dict[str, str]:
    """
    Observe the behavior of a fresh caller after the lock attribute is deleted.

    Returns:
        Dict[str, str]:
            Human-readable outcome summary.
    """
    probe = _DeleteCleanupProbe()
    probe.cleanup_delete_attribute()

    error_text = ""
    try:
        probe.enter_via_attribute()
    except AttributeError as error:
        error_text = str(error)

    assert error_text != ""

    return {
        "fresh_attribute_access_after_delete": "AttributeError",
        "error_text": error_text,
    }


def main() -> None:
    """
    Run the delete-lock cleanup experiment and print the observed behavior.
    """
    results = [
        ("cleanup_delete_inside_with", _run_cleanup_inside_with_scenario()),
        ("active_holder_then_delete", _run_active_holder_then_delete_scenario()),
        ("snapshotted_waiter_then_delete", _run_snapshotted_waiter_then_delete_scenario()),
        ("fresh_access_after_delete", _run_fresh_access_after_delete_scenario()),
    ]

    print("lock delete cleanup behavior experiment")
    print("-" * 48)
    for label, result in results:
        print(label)
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()


if __name__ == "__main__":
    main()
