"""
Component tests: bind's cross-frame duplicate sweep against frame birth and frame cleanup
(cross_object_lock_gaps, 0.2.8231).

With two or more frames under process-wide spell ids (the default), every bind asks each other frame whether it
holds the new spell id (Aether._check_for_spell). Bind's transaction is the binding frame's own; frame birth takes
the aetheric plane's FRAME_CREATE claim and the Aether lock, frame detach the Aether lock - nothing the sweep holds.
The sweep walked the frame registry live, so a frame born or detached mid-sweep made bind raise "dictionary changed
size during iteration". These tests park the binding thread inside the sweep, right after frame-b answered (as it
releases frame-b's lock), and change the registry from the main thread through the public paths.
"""

import threading
from typing import Any, Callable, Dict, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class SweepRaceService:
    """Bound in frame-a while another frame is born or cleaned."""


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_sweep() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Returns:
        Iterator[None]: Control returns to the test between the two resets.
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


class _ParkBinderAfterAnswer:
    """
    Purpose:
        Frame-b's lock for one test. It delegates every acquire and release to the frame's real RLock and, the
        first time the binding thread releases it, parks that thread until the test has changed the frame registry.
        Releasing frame-b's lock is the moment frame-b has answered the sweep; every shape of the sweep passes it,
        and no lock or claim is skipped.
    """

    def __init__(self, real: Any, binder: threading.Thread, parked: threading.Event,
                 release: threading.Event) -> None:
        """
        Args:
            real: Frame-b's own RLock, which does the locking.
            binder: The thread whose bind is parked.
            parked: Set when the binder is parked.
            release: Set by the test once the registry has changed.
        """
        self._real = real
        self._binder = binder
        self._parked = parked
        self._release = release

    def acquire(self, *args: Any, **kwargs: Any) -> bool:
        """
        Returns:
            bool: What the real lock's acquire returns.
        """
        return self._real.acquire(*args, **kwargs)

    def release(self) -> None:
        """
        Release the real lock, then park the binder once.
        """
        self._real.release()
        self._park_binder_once()

    def __enter__(self) -> _ParkBinderAfterAnswer:
        """
        Returns:
            _ParkBinderAfterAnswer: This lock, held.
        """
        self._real.acquire()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """
        Release the real lock, then park the binder once.
        """
        self._real.release()
        self._park_binder_once()

    def _park_binder_once(self) -> None:
        """
        Park the binding thread the first time it gets here; any other thread passes through.
        """
        if threading.current_thread() is self._binder and not self._parked.is_set():
            self._parked.set()
            assert self._release.wait(timeout=30)


def _bind_with_registry_change_mid_sweep(
        monkeypatch: pytest.MonkeyPatch,
        book_a: Spellbook,
        frame_b: AethericFrame,
        change_registry: Callable[[], None],
) -> Dict[str, object]:
    """
    Purpose:
        Bind SweepRaceService into `book_a` on a worker thread, park that thread inside the cross-frame sweep after
        frame-b answered, run `change_registry` on this thread, then let the bind finish.
    Returns:
        Dict[str, object]: "spell_id" on success or "error" with the exception raised by bind.
    """
    parked, release = threading.Event(), threading.Event()
    outcome: Dict[str, object] = {}

    def bind() -> None:
        try:
            outcome["spell_id"] = book_a.bind(
                spell=SweepRaceService, existence=Existence.unique, permissions="create",
            )
        except Exception as exc:
            outcome["error"] = exc

    binder = threading.Thread(target=bind)
    monkeypatch.setattr(frame_b, "_lock", _ParkBinderAfterAnswer(frame_b._lock, binder, parked, release))
    binder.start()
    try:
        assert parked.wait(timeout=30), "the bind never reached frame-b in the cross-frame sweep"
        change_registry()
    finally:
        release.set()
        binder.join(timeout=30)
    assert not binder.is_alive()
    return outcome


def test_bind_succeeds_when_a_frame_is_born_during_the_cross_frame_sweep(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A tenant's first Spellbook births its frame while another frame's bind is sweeping: the bind registers its spell.
    """
    aether = Spellbook._aether
    book_a = Spellbook(aetheric_frame="frame-a")
    Spellbook(aetheric_frame="frame-b")
    born = []

    outcome = _bind_with_registry_change_mid_sweep(
        monkeypatch, book_a, aether.get_frame("frame-b"),
        lambda: born.append(Spellbook(aetheric_frame="frame-c")),
    )

    assert "error" not in outcome, outcome.get("error")
    assert book_a.find_spell_by_spell_id(outcome["spell_id"]) is not None
    assert aether.list_frame_names() == ("frame-a", "frame-b", "frame-c")


def test_bind_succeeds_when_another_frame_is_cleaned_during_the_cross_frame_sweep(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A frame torn down (cleaned and detached) while another frame's bind is sweeping counts as holding nothing.
    """
    aether = Spellbook._aether
    book_a = Spellbook(aetheric_frame="frame-a")
    Spellbook(aetheric_frame="frame-b")
    Spellbook(aetheric_frame="frame-x")
    frame_x = aether.get_frame("frame-x")

    outcome = _bind_with_registry_change_mid_sweep(
        monkeypatch, book_a, aether.get_frame("frame-b"), frame_x.cleanup,
    )

    assert "error" not in outcome, outcome.get("error")
    assert book_a.find_spell_by_spell_id(outcome["spell_id"]) is not None
    assert aether.find_frame("frame-x") is None
