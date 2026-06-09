import gc
import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import pytest


def _ensure_local_paths() -> None:
    """
    Ensure local source and benchmark helper paths are importable.

    Contract:
        - Adds the repository `src/` directory and the current benchmark
          directory to `sys.path` once each.
        - Supports both pytest execution and direct `python` execution.
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import melder_gauntlet_support as _support
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.general_base.cleanable import Cleanable


class _CountingLockProxy:
    """
    Count lock traffic for one owned runtime lock.

    Purpose:
        Wrap one live lock object without changing its semantics so the bench
        can report which owned runtime locks actually participate in one meld.

    Contract:
        - Delegates all lock behavior to the wrapped lock object.
        - Counts `__enter__`, `__exit__`, `acquire`, and `release` separately.
        - Leaves all other lock attributes and methods untouched through
          `__getattr__`.
    """

    __slots__ = ("_owner_label", "_inner_lock", "_counts")

    def __init__(
        self,
        *,
        owner_label: str,
        inner_lock: Any,
        counts: Dict[str, Dict[str, int]],
    ) -> None:
        """
        Bind the proxy to one owner label and one underlying lock object.

        Args:
            owner_label:
                Human-readable owner path used in the output report.
            inner_lock:
                Live lock object being wrapped.
            counts:
                Shared mutable counter map updated by this proxy.
        """
        self._owner_label = owner_label
        self._inner_lock = inner_lock
        self._counts = counts

    def _bump(self, operation: str) -> None:
        """
        Increment one counted operation for this lock owner.

        Args:
            operation:
                Counter bucket name such as `enter` or `acquire`.
        """
        owner_counts = self._counts.setdefault(
            self._owner_label,
            {"enter": 0, "exit": 0, "acquire": 0, "release": 0},
        )
        owner_counts[operation] += 1

    def __enter__(self) -> Any:
        """
        Enter the wrapped lock context and count that entry.
        """
        self._bump("enter")
        return self._inner_lock.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> Any:
        """
        Exit the wrapped lock context and count that exit.
        """
        self._bump("exit")
        return self._inner_lock.__exit__(exc_type, exc_value, traceback)

    def acquire(self, *args: Any, **kwargs: Any) -> Any:
        """
        Delegate acquire to the wrapped lock while counting the call.
        """
        self._bump("acquire")
        return self._inner_lock.acquire(*args, **kwargs)

    def release(self) -> Any:
        """
        Delegate release to the wrapped lock while counting the call.
        """
        self._bump("release")
        return self._inner_lock.release()

    def __getattr__(self, name: str) -> Any:
        """
        Forward unknown attributes to the wrapped lock.
        """
        return getattr(self._inner_lock, name)


def _wrap_lock_if_present(
    owner: Any,
    owner_label: str,
    lock_counts: Dict[str, Dict[str, int]],
) -> None:
    """
    Replace one owned `_lock` field with a counting proxy when present.

    Args:
        owner:
            Runtime object that may expose `_lock`.
        owner_label:
            Output label used for this owner in the report.
        lock_counts:
            Shared lock counter map.
    """
    if owner is None or not hasattr(owner, "_lock"):
        return
    current_lock = owner._lock
    if isinstance(current_lock, _CountingLockProxy):
        return
    owner._lock = _CountingLockProxy(
        owner_label=owner_label,
        inner_lock=current_lock,
        counts=lock_counts,
    )


def _instrument_runtime_locks(
    spellbook: Spellbook,
    conduit: Conduit,
    lesser: Conduit,
    lock_counts: Dict[str, Dict[str, int]],
) -> None:
    """
    Wrap the obvious owned runtime locks that can participate in one request meld.

    Args:
        spellbook:
            Shared spellbook used by the benchmark runtime.
        conduit:
            Root conduit.
        lesser:
            Lesser conduit used for the request-scope meld.
        lock_counts:
            Shared lock counter map.
    """
    _wrap_lock_if_present(spellbook, "spellbook._lock", lock_counts)
    _wrap_lock_if_present(conduit, "root_conduit._lock", lock_counts)
    _wrap_lock_if_present(conduit._meld, "root_conduit._meld._lock", lock_counts)
    _wrap_lock_if_present(conduit._creations, "root_conduit._creations._lock", lock_counts)
    _wrap_lock_if_present(lesser, "lesser_conduit._lock", lock_counts)
    _wrap_lock_if_present(lesser._meld, "lesser_conduit._meld._lock", lock_counts)
    _wrap_lock_if_present(lesser._creations, "lesser_conduit._creations._lock", lock_counts)
    _wrap_lock_if_present(
        spellbook._spell_system_states,
        "spellbook._spell_system_states._lock",
        lock_counts,
    )
    for spell in spellbook._spells.values():
        spell_label = f"spell:{spell.spell_name}:{spell.spell_id[:8]}._lock"
        _wrap_lock_if_present(spell, spell_label, lock_counts)
        system_state = spell.system_state
        if system_state is not None:
            _wrap_lock_if_present(
                system_state,
                f"spell_state:{spell.spell_name}:{spell.spell_id[:8]}._lock",
                lock_counts,
            )


def _make_check_cleaned_counter(
    check_counts: Dict[str, int],
) -> Callable[[Cleanable], None]:
    """
    Build one counted replacement for `Cleanable.check_cleaned`.

    Args:
        check_counts:
            Shared counter map keyed by `<class> <- <caller>`.

    Returns:
        Callable[[Cleanable], None]:
            Counted wrapper that still delegates to the original guard.
    """
    original = Cleanable.check_cleaned

    def counted(self: Cleanable) -> None:
        frame = inspect.currentframe()
        caller_name = "<unknown>"
        try:
            if frame is not None and frame.f_back is not None:
                caller_name = frame.f_back.f_code.co_name
            label = f"{self.__class__.__name__} <- {caller_name}"
            check_counts[label] = check_counts.get(label, 0) + 1
        finally:
            del frame
        original(self)

    return counted


def _copy_lock_counts(
    counts: Dict[str, Dict[str, int]],
) -> Dict[str, Dict[str, int]]:
    """
    Copy only the non-zero lock counters for reporting.

    Args:
        counts:
            Shared mutable lock counter map.

    Returns:
        Dict[str, Dict[str, int]]:
            Detached snapshot containing only non-zero owner rows.
    """
    copied: Dict[str, Dict[str, int]] = {}
    for owner_label, owner_counts in counts.items():
        non_zero = {
            key: value
            for key, value in owner_counts.items()
            if value > 0
        }
        if non_zero:
            copied[owner_label] = non_zero
    return copied


def _copy_check_counts(
    counts: Dict[str, int],
) -> Dict[str, int]:
    """
    Copy only the non-zero `check_cleaned()` counters for reporting.

    Args:
        counts:
            Shared mutable `check_cleaned()` counter map.

    Returns:
        Dict[str, int]:
            Detached snapshot containing only non-zero rows.
    """
    return {
        key: value
        for key, value in counts.items()
        if value > 0
    }


def _print_single_meld_report(label: str, report: Dict[str, Any]) -> None:
    """
    Print one compact single-meld counter report.

    Args:
        label:
            Human-readable phase label.
        report:
            Structured report payload for one meld call.
    """
    print(f"[single-meld] {label} result_type={report['result_type']}")
    print(
        "[single-meld] "
        f"{label} check_cleaned_total={report['check_cleaned_total']}"
    )
    for key, value in sorted(
        report["check_cleaned_counts"].items(),
        key=lambda item: (-item[1], item[0]),
    ):
        print(f"[single-meld] {label} check_cleaned {key} = {value}")
    for owner_label, owner_counts in sorted(report["lock_counts"].items()):
        parts = [f"{key}={value}" for key, value in sorted(owner_counts.items())]
        print(f"[single-meld] {label} lock {owner_label} | {' '.join(parts)}")


def _build_runtime() -> Tuple[Spellbook, Conduit, Dict[type, str]]:
    """
    Build one Melder runtime that matches the gauntlet object graph.

    Returns:
        Tuple[Spellbook, Conduit, Dict[type, str]]:
            Shared spellbook, rooted conduit, and spell-id map.
    """
    singleton_types = set(_support.SINGLETON_TYPES)
    outer_scoped_types = set(_support.OUTER_SCOPED_TYPES)
    request_scoped_types = set(_support.REQUEST_SCOPED_TYPES)

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="single-meld-lock-bench")
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids: Dict[type, str] = {}
    for cls in _support.ALL_CLASSES:
        if cls in singleton_types:
            existence = Existence.unique
        elif cls in outer_scoped_types:
            existence = Existence.unique_per_conduit
        elif cls in request_scoped_types:
            existence = Existence.unique_per_spell_space
        else:
            existence = Existence.many
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )

    conduit = spellbook.conjure(name="single-meld-lock-bench", dynamic=False)
    return spellbook, conduit, spell_ids


def _capture_one_meld_report(
    *,
    resolver: Callable[[], Any],
    lock_counts: Dict[str, Dict[str, int]],
    check_counts: Dict[str, int],
) -> Dict[str, Any]:
    """
    Execute one meld call and snapshot the instrumented counters.

    Args:
        resolver:
            Zero-arg callable that executes exactly one representative meld.
        lock_counts:
            Shared mutable lock counter map.
        check_counts:
            Shared mutable `check_cleaned()` counter map.

    Returns:
        Dict[str, Any]:
            Structured result payload for one meld call.
    """
    lock_counts.clear()
    check_counts.clear()
    resolved = resolver()
    return {
        "result_type": type(resolved).__name__,
        "check_cleaned_total": sum(check_counts.values()),
        "check_cleaned_counts": _copy_check_counts(check_counts),
        "lock_counts": _copy_lock_counts(lock_counts),
    }


@pytest.mark.timeout(3600)
def test_melder_single_meld_lock_and_check_cleaned() -> None:
    """
    Count one representative request-root meld's lock and cleaned-guard traffic.

    Purpose:
        Produce a focused report for the actual one-meld path the user asked
        about instead of reusing whole-gauntlet aggregate totals.

    Contract:
        - Builds the same object graph family used by the gauntlet.
        - Opens lesser-conduit and spellspace scope outside the measured
          window so scope churn does not pollute the per-meld counts.
        - Measures:
          - first request-root meld in that scope
          - second request-root meld in the same scope
        - Restores `Cleanable.check_cleaned` before teardown.
    """
    spellbook, conduit, spell_ids = _build_runtime()
    lock_counts: Dict[str, Dict[str, int]] = {}
    check_counts: Dict[str, int] = {}
    original_check_cleaned = Cleanable.check_cleaned

    lesser = conduit.create_lesser_conduit()
    request_cm = lesser.enter_spellspace()
    space = request_cm.__enter__()

    try:
        _instrument_runtime_locks(spellbook, conduit, lesser, lock_counts)
        Cleanable.check_cleaned = _make_check_cleaned_counter(check_counts)

        def resolve_request_root() -> Any:
            return space.meld(spell=spell_ids[_support.RequestRoot])

        first_report = _capture_one_meld_report(
            resolver=resolve_request_root,
            lock_counts=lock_counts,
            check_counts=check_counts,
        )
        second_report = _capture_one_meld_report(
            resolver=resolve_request_root,
            lock_counts=lock_counts,
            check_counts=check_counts,
        )
    finally:
        Cleanable.check_cleaned = original_check_cleaned
        request_cm.__exit__(None, None, None)
        lesser.cleanup()
        conduit.cleanup()
        Aether._reset_singleton_for_tests()
        gc.collect()

    _print_single_meld_report("request_root_first", first_report)
    _print_single_meld_report("request_root_second", second_report)

    if first_report["result_type"] != "RequestRoot":
        raise AssertionError("First request-root meld returned the wrong type.")
    if second_report["result_type"] != "RequestRoot":
        raise AssertionError("Second request-root meld returned the wrong type.")
    if first_report["check_cleaned_total"] <= 0:
        raise AssertionError("Expected at least one check_cleaned() call in first meld.")
    if second_report["check_cleaned_total"] <= 0:
        raise AssertionError("Expected at least one check_cleaned() call in second meld.")

