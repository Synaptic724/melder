"""
Unit tests: AethericFrame membership reads against a racing cleanup and a binding Book (cross_object_lock_gaps,
0.2.8231).

`has_spell` and `spells_in_index` checked cleaned before taking the frame lock while `cleanup()` deleted the
registries under it (and then the lock itself), so a cleanup landing between the check and the lock surfaced as
AttributeError. They now check again under the lock, which cleanup keeps, and raise their documented RuntimeError.
The cleanup-safe probes that Aether's cross-frame sweep uses answer as an empty frame once the frame is cleaned.

The frame's cached-id registry holds LIVE references to each conjured Book's `_spell_ids`, which that Book writes
under its own lock. `spells_in_index` copied them element by element, so a bind into the Book mid-read raised "Set
changed size during iteration"; the frame now takes each set with one update call.
"""

import threading
from typing import Callable, Dict, Iterator, Set, Tuple
from unittest.mock import MagicMock, patch

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.spellbook.bind.spell_index import SpellIndex


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """
    Purpose:
        Reset the Aether singleton around each test.
    Returns:
        Iterator[None]: Control returns to the test between the two resets.
    """
    Aether._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()


@pytest.fixture
def mocked_frame_services() -> Iterator[None]:
    """
    Purpose:
        Mock the frame's heavy collaborators (as in test_aetheric_frame.py) while a test builds frames.
    Returns:
        Iterator[None]: Control returns to the test with the collaborators patched.
    """
    with patch("melder.aether.aetheric_frame.aetheric_frame.ConduitCloud") as mock_cloud, \
            patch("melder.aether.aetheric_frame.aetheric_frame.SpellSystemStates"), \
            patch("melder.aether.aetheric_frame.aetheric_frame.DevOpsManager"):
        mock_cloud.return_value._conduit_clusters = {}
        yield


@pytest.fixture
def frame_and_index(mocked_frame_services: None) -> Iterator[Tuple[AethericFrame, MagicMock]]:
    """
    Purpose:
        A frame holding one conduit's index with the versions v1 and v2; the index answers membership like a live
        SpellIndex.
    Returns:
        Iterator[Tuple[AethericFrame, MagicMock]]: The live frame and the index it holds.
    """
    live = AethericFrame(Aether(), "race_frame")
    index = MagicMock(spec=SpellIndex)
    index.spells_in_index.return_value = {"v1", "v2"}
    index._has_spell_unless_cleaned.side_effect = lambda spell_id: spell_id in {"v1", "v2"}
    live.register_conduit_spells("c1", {index}, {"v1", "v2"})
    yield live, index


class _IdSetPausingMidCopy(set):
    """
    Purpose:
        Stand in for a conjured Book's live `_spell_ids`. Iterating it element by element - the copy
        spells_in_index used to make - pauses after the first element, so the test can add an id in the middle of
        the frame's read, as that Book's own bind does under the Book's lock.
    """

    def __init__(self, ids: Set[str], paused: threading.Event, resume: threading.Event) -> None:
        """
        Args:
            ids: The initial spell_ids.
            paused: Set once an element-by-element read has taken the first element.
            resume: Released by the test after it added an id.
        """
        super().__init__(ids)
        self.paused = paused
        self.resume = resume

    def __iter__(self) -> Iterator[str]:
        """
        Yields:
            str: Each id; after the first one, waits until the test has added an id and released the read.
        """
        first = True
        for spell_id in set.__iter__(self):
            yield spell_id
            if first:
                first = False
                self.paused.set()
                assert self.resume.wait(timeout=30)


def _clean_after_first_check(monkeypatch: pytest.MonkeyPatch, frame: AethericFrame) -> None:
    """
    Purpose:
        Make the next `check_cleaned()` of `frame` pass the real check and then have another thread clean the frame
        completely before the caller goes on to take the frame lock - the interleaving of a racing cleanup.
    Args:
        monkeypatch: Restores `AethericFrame.check_cleaned` after the test.
        frame: The frame to clean.
    """
    real_check: Callable[[AethericFrame], None] = AethericFrame.check_cleaned
    fired = threading.Event()

    def check_then_clean(self: AethericFrame) -> None:
        real_check(self)
        if self is frame and not fired.is_set():
            fired.set()
            cleaner = threading.Thread(target=frame.cleanup)
            cleaner.start()
            cleaner.join(timeout=10)
            assert not cleaner.is_alive()

    monkeypatch.setattr(AethericFrame, "check_cleaned", check_then_clean)


def test_has_spell_raises_runtime_error_when_cleanup_lands_between_check_and_lock(
        monkeypatch: pytest.MonkeyPatch,
        frame_and_index: Tuple[AethericFrame, MagicMock],
) -> None:
    """
    A cleanup between has_spell's first check and its lock raises the documented RuntimeError, not AttributeError.
    """
    frame, _ = frame_and_index
    _clean_after_first_check(monkeypatch, frame)
    with pytest.raises(RuntimeError, match="cleaned"):
        frame.has_spell("v1")


def test_spells_in_index_raises_runtime_error_when_cleanup_lands_between_check_and_lock(
        monkeypatch: pytest.MonkeyPatch,
        frame_and_index: Tuple[AethericFrame, MagicMock],
) -> None:
    """
    A cleanup between spells_in_index's first check and its lock raises the documented RuntimeError.
    """
    frame, _ = frame_and_index
    _clean_after_first_check(monkeypatch, frame)
    with pytest.raises(RuntimeError, match="cleaned"):
        frame.spells_in_index()


def test_cleanup_safe_probes_answer_like_the_public_reads_on_a_live_frame(
        frame_and_index: Tuple[AethericFrame, MagicMock],
) -> None:
    """
    On a live frame the probes give the public answers: membership, the owning index (None for an id no index
    holds), the version set.
    """
    frame, index = frame_and_index
    assert frame._has_spell_unless_cleaned("v1") is True
    assert frame._has_spell_unless_cleaned("v9") is False
    assert frame._find_index_for_spell_unless_cleaned("v2") is index
    assert frame._find_index_for_spell_unless_cleaned("v9") is None
    assert frame._spells_in_index_unless_cleaned() == {"v1", "v2"}


def test_cleanup_safe_probes_answer_as_an_empty_frame_once_cleaned(
        frame_and_index: Tuple[AethericFrame, MagicMock],
) -> None:
    """
    Once the frame is cleaned the probes answer False, None and an empty set instead of raising, while the public
    reads keep raising RuntimeError.
    """
    frame, _ = frame_and_index
    frame.cleanup()
    assert frame._has_spell_unless_cleaned("v1") is False
    assert frame._find_index_for_spell_unless_cleaned("v1") is None
    assert frame._spells_in_index_unless_cleaned() == set()
    with pytest.raises(RuntimeError):
        frame.has_spell("v1")


@pytest.mark.parametrize("reader_name", ["spells_in_index", "_spells_in_index_unless_cleaned"])
def test_frame_id_read_returns_when_a_conjured_book_binds_mid_read(
        mocked_frame_services: None,
        reader_name: str,
) -> None:
    """
    A conjured Book adding to its `_spell_ids` while the frame reads its cached ids no longer makes the read raise
    "Set changed size during iteration": the read returns the ids from before or after the add.
    """
    paused, resume = threading.Event(), threading.Event()
    frame = AethericFrame(Aether(), "race_frame")
    book_ids = _IdSetPausingMidCopy({"v1", "v2"}, paused, resume)
    frame.register_conduit_spells("c1", set(), book_ids)
    outcome: Dict[str, object] = {}

    def read() -> None:
        try:
            outcome["ids"] = getattr(frame, reader_name)()
        except Exception as exc:
            outcome["error"] = exc

    reader = threading.Thread(target=read)
    reader.start()
    while reader.is_alive() and not paused.is_set():
        paused.wait(timeout=0.01)
    if paused.is_set():
        # The Book's bind, between two elements of an element-by-element copy.
        book_ids.add("v3")
    resume.set()
    reader.join(timeout=30)

    assert not reader.is_alive()
    assert "error" not in outcome, outcome.get("error")
    assert outcome["ids"] in ({"v1", "v2"}, {"v1", "v2", "v3"})
