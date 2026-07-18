import pytest

from melder.mutation_research.research_set.research_journal import (
    ResearchJournal,
)
from melder.mutation_research.research_set.transition_entry import (
    TransitionAct,
)


def test_journal_mints_monotonic_sequences() -> None:
    """
    Verify sequences start at 1 and advance without gaps or reuse.
    """
    journal = ResearchJournal()
    first = journal.record(TransitionAct.lane_created, "lane-1")
    second = journal.record(TransitionAct.registered, "lane-1", to_spell_id="sha-a")
    third = journal.record(TransitionAct.archived, "lane-2")

    assert [first.sequence, second.sequence, third.sequence] == [1, 2, 3]
    assert journal.latest_sequence == 3
    assert journal.entry_count == 3


def test_journal_lane_and_sha_filters() -> None:
    """
    Verify filtered reads select by subject lane and by touched identity.
    """
    journal = ResearchJournal()
    journal.record(TransitionAct.registered, "lane-1", to_spell_id="sha-a")
    journal.record(TransitionAct.registered, "lane-2", to_spell_id="sha-b")
    journal.record(
        TransitionAct.joined, "lane-1", from_spell_id="sha-a", to_spell_id="sha-b",
    )

    assert len(journal.entries_for_lane("lane-1")) == 2
    assert len(journal.entries_for_lane("lane-2")) == 1
    assert len(journal.entries_for_spell_id("sha-a")) == 2
    assert len(journal.entries_for_spell_id("sha-b")) == 2
    assert journal.entries_for_spell_id("sha-none") == []


def test_journal_reads_are_detached() -> None:
    """
    Verify list reads never expose the live store.
    """
    journal = ResearchJournal()
    journal.record(TransitionAct.lane_created, "lane-1")
    read = journal.entries()
    read.clear()

    assert journal.entry_count == 1


def test_journal_describe_bounds_recent_window() -> None:
    """
    Verify the persistence window bound keeps counts truthful.
    """
    journal = ResearchJournal()
    for index in range(5):
        journal.record(
            TransitionAct.registered, "lane-1", to_spell_id=f"sha-{index}",
        )

    payload = journal.describe(recent=2)

    assert len(payload["entries"]) == 2
    assert payload["entries"][-1]["to_spell_id"] == "sha-4"
    assert payload["entry_count"] == 5
    assert payload["next_sequence"] == 6


def test_journal_from_payload_continues_minting_without_reuse() -> None:
    """
    Verify a bounded-window rebuild never re-mints recorded sequences.
    """
    journal = ResearchJournal()
    for index in range(4):
        journal.record(
            TransitionAct.registered, "lane-1", to_spell_id=f"sha-{index}",
        )

    rebuilt = ResearchJournal.from_payload(journal.describe(recent=2))
    fresh = rebuilt.record(TransitionAct.archived, "lane-1")

    assert rebuilt.entry_count == 3
    assert fresh.sequence == 5


def test_journal_describe_from_payload_full_roundtrip() -> None:
    """
    Verify a full (unbounded) payload rebuilds byte-equal entries.
    """
    journal = ResearchJournal()
    journal.record(
        TransitionAct.registered,
        "lane-1",
        to_spell_id="sha-a",
        actor="agent",
        campaign="c1",
    )

    rebuilt = ResearchJournal.from_payload(journal.describe(recent=None))

    assert rebuilt.describe(recent=None) == journal.describe(recent=None)


def test_journal_cleanup_is_idempotent_and_guards_reads() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    journal = ResearchJournal()
    journal.record(TransitionAct.lane_created, "lane-1")
    journal.cleanup()
    journal.cleanup()

    assert journal.cleaned is True
    with pytest.raises(RuntimeError):
        journal.record(TransitionAct.archived, "lane-1")


def test_from_payload_refuses_reversed_or_reusable_sequences() -> None:
    """
    Regression (BUG-041): hydration accepted any `next_sequence >= 1`, so
    an entry at sequence 10 with `next_sequence=1` made the next public
    record REUSE sequence 1 after 10 (order became [(10, ...), (1, ...)]).
    Corrected behavior: non-ascending restored entries refuse loudly, and
    a too-low counter clears every hydrated entry.
    """
    journal = ResearchJournal()
    journal.record(TransitionAct.registered, "lane-1", to_spell_id="a")
    payload = journal.describe()
    payload["next_sequence"] = 1  # claims reuse of an existing sequence

    rebuilt = ResearchJournal.from_payload(payload)
    entry = rebuilt.record(
        TransitionAct.registered, "lane-1", to_spell_id="b",
    )

    assert entry.sequence == 2  # counter cleared the hydrated entry

    reversed_payload = journal.describe()
    reversed_payload["entries"] = list(reversed(payload["entries"]))
    journal.record(TransitionAct.registered, "lane-1", to_spell_id="c")
    two_entry_payload = journal.describe()
    two_entry_payload["entries"] = list(
        reversed(two_entry_payload["entries"])
    )
    with pytest.raises(ValueError, match="strictly ascending"):
        ResearchJournal.from_payload(two_entry_payload)
