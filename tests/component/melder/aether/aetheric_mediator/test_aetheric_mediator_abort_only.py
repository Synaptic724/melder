"""
Component tests for the abort-only poison and the session lookup surface.

WHY THESE EXIST: `mark_abort_only` and the five `Mediator` lookup verbs were
added to mirror the DevOps plane and shipped with no tests of their own. The
poison in particular is the kind of mechanism that looks obviously correct and
fails on the second reader - it is sticky, it is first-writer-wins, and the bar
lives on the SESSION rather than the mediator so that a participant who never
learned about the failure still cannot commit past it. Each of those three is a
decision that could reasonably have gone the other way, so each gets a test that
would fail if it were quietly reversed.

Run:
    pytest tests/component/melder/aether/aetheric_mediator -q
"""

import threading

import pytest

from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_session import SessionStatus
from melder.aether.aetheric_mediator.transaction_type import TransactionType


@pytest.fixture(name="plane")
def _plane():
    """A real plane; every family is seeded by the registry itself."""
    built = Mediator(max_wait_seconds=0.25)
    try:
        yield built
    finally:
        built.cleanup()


def _who(identity_id: str) -> Identity:
    """Build a crystallizer-family identity."""
    return Identity(kind="crystallizer", identity_id=identity_id)


def _open(plane, who, frame_name="A"):
    """Open a frame-scoped formation load, which is the parent/child shape."""
    return plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=who,
        metadata={"target_frame_name": frame_name},
    )


# --------------------------------------------------------------------------
# The poison
# --------------------------------------------------------------------------

def test_abort_only_bars_commit_and_names_the_reason(plane):
    """
    The whole point: a marked session cannot commit, and the refusal carries the
    reason so the eventual failure is diagnosable rather than mysterious.
    """
    who = _who("one")
    session = _open(plane, who)
    plane.mark_active_session_abort_only(
        submitter=who, reason="preflight found a blocker"
    )
    session.leave()

    with pytest.raises(RuntimeError) as caught:
        plane.commit(session)
    assert "abort-only" in str(caught.value)
    assert "preflight found a blocker" in str(caught.value)

    plane.fail(session, reason="preflight found a blocker")
    assert session.status is SessionStatus.ABORTED


def test_abort_only_is_sticky_and_first_writer_wins(plane):
    """
    The FIRST detected failure is the diagnosis worth keeping. A later, vaguer
    reason overwriting it would lose the useful one - and several participants
    noticing the same failure is expected, not exceptional, so repeat marking
    must be harmless.
    """
    who = _who("one")
    session = _open(plane, who)
    try:
        plane.mark_active_session_abort_only(submitter=who, reason="first: real cause")
        plane.mark_active_session_abort_only(submitter=who, reason="second: vague")
        plane.mark_active_session_abort_only(submitter=who, reason="third: vaguer")
        assert session.abort_only_reason == "first: real cause"
        assert session.is_abort_only is True
    finally:
        session.leave()
        plane.fail(session, reason="first: real cause")


def test_marking_does_not_end_or_reshape_the_session(plane):
    """
    Marking records an intent about the ENDING; it must not end anything itself.
    The session stays OPEN and joinable so inner scopes can still leave cleanly -
    otherwise a caller deep in a call stack would strand every frame above it.
    """
    who = _who("one")
    session = _open(plane, who)
    try:
        depth_before = session.depth
        plane.mark_active_session_abort_only(submitter=who, reason="boom")
        assert session.status is SessionStatus.OPEN
        assert session.depth == depth_before
        # Still joinable, and the inner scope still leaves normally.
        joined = _open(plane, who)
        assert joined is session
        assert session.depth == depth_before + 1
        session.leave()
        assert session.depth == depth_before
    finally:
        session.leave()
        plane.fail(session, reason="boom")


def test_the_bar_lives_on_the_session_not_the_mediator(plane):
    """
    A participant that never learned about the failure must not be able to commit
    past it. Calling `session.mark_committing()` DIRECTLY - bypassing the
    mediator entirely - must still refuse, which is only true because the check
    is inside the session.
    """
    who = _who("one")
    session = _open(plane, who)
    try:
        session.mark_abort_only("detected downstream")
        session.leave()
        with pytest.raises(RuntimeError) as caught:
            session.mark_committing()
        assert "abort-only" in str(caught.value)
    finally:
        plane.fail(session, reason="detected downstream")


def test_marking_requires_a_real_reason(plane):
    """
    An undescribed poison is invisible residue - the same argument the rollback
    action makes for its mandatory description.
    """
    who = _who("one")
    session = _open(plane, who)
    try:
        for bad in ("", None, 123):
            with pytest.raises(ValueError):
                session.mark_abort_only(bad)
        assert session.is_abort_only is False
    finally:
        session.leave()
        plane.commit(session)


def test_marking_a_terminal_session_raises(plane):
    """
    Silently accepting a mark on a committed session would imply a guarantee
    that was never delivered - there is nothing left to prevent.
    """
    who = _who("one")
    session = _open(plane, who)
    session.leave()
    plane.commit(session)
    assert session.status is SessionStatus.COMMITTED
    with pytest.raises(RuntimeError):
        session.mark_abort_only("too late")


def test_marking_without_an_open_session_raises(plane):
    """
    Doing nothing quietly would let a caller believe it had poisoned a
    transaction it had not.
    """
    with pytest.raises(RuntimeError):
        plane.mark_active_session_abort_only(submitter=_who("nobody"), reason="x")


def test_unmarked_sessions_still_commit(plane):
    """The bar must not leak into the clean path."""
    who = _who("one")
    session = _open(plane, who)
    assert session.is_abort_only is False
    assert session.abort_only_reason is None
    session.leave()
    plane.commit(session)
    assert session.status is SessionStatus.COMMITTED


# --------------------------------------------------------------------------
# The lookup surface
# --------------------------------------------------------------------------

def test_lookups_are_empty_before_and_after_a_transaction(plane):
    """
    A finalised transaction is removed from the by-id map, so a live hit means
    the transaction genuinely has not ended.
    """
    who = _who("one")
    assert plane.has_active_session(who) is False
    assert plane.get_session_for_identity(who) is None
    assert plane.get_active_request(who) is None

    session = _open(plane, who)
    request_id = session.request.request_id
    assert plane.has_active_session(who) is True
    assert plane.get_session_for_identity(who) is session
    assert plane.get_session_by_request_id(request_id) is session
    assert plane.get_active_request(who) is session.request

    session.leave()
    plane.commit(session)
    assert plane.has_active_session(who) is False
    assert plane.get_session_by_request_id(request_id) is None


def test_lookups_are_per_identity(plane):
    """
    Sessions are keyed per identity, so one identity's transaction must be
    invisible to another's lookups even on the same thread.
    """
    one = _who("one")
    two = _who("two")
    session = _open(plane, one, frame_name="A")
    try:
        assert plane.has_active_session(one) is True
        assert plane.has_active_session(two) is False
        other = _open(plane, two, frame_name="B")
        try:
            assert plane.get_session_for_identity(two) is other
            assert plane.get_session_for_identity(one) is session
            assert other is not session
        finally:
            other.leave()
            plane.commit(other)
    finally:
        session.leave()
        plane.commit(session)


def test_by_request_id_is_cross_thread_but_by_identity_is_not(plane):
    """
    THE ASYMMETRY IS DELIBERATE. A blocked caller holding an id out of admission
    evidence needs to identify the HOLDER, who is on another thread by
    definition - so the by-id lookup crosses threads. The per-identity lookup
    must NOT, because reporting a session the caller may not touch would invite
    exactly the foreign-thread join the session refuses.
    """
    who = _who("one")
    session = _open(plane, who)
    request_id = session.request.request_id
    seen = {}

    def _observer():
        seen["by_id"] = plane.get_session_by_request_id(request_id) is session
        seen["by_identity"] = plane.get_session_for_identity(who)
        seen["has_active"] = plane.has_active_session(who)

    thread = threading.Thread(target=_observer)
    thread.start()
    thread.join(timeout=5.0)

    try:
        assert seen["by_id"] is True, "by-id must cross threads"
        assert seen["by_identity"] is None, "by-identity must not cross threads"
        assert seen["has_active"] is False
    finally:
        session.leave()
        plane.commit(session)


def test_by_request_id_rejects_a_malformed_id(plane):
    """An empty id is a caller bug, not a miss."""
    for bad in ("", None, 7):
        with pytest.raises(ValueError):
            plane.get_session_by_request_id(bad)


def test_lookup_reflects_the_seeded_claim_set(plane):
    """
    The lookup surface and the strategy layer have to agree: what the session
    reports as granted is what the family planned.
    """
    who = _who("one")
    session = _open(plane, who, frame_name="A")
    try:
        request = plane.get_active_request(who)
        assert request is not None
        assert sorted(session.staged.granted_scopes) == [
            ScopeKey.frame("A"),
            ScopeKey.world(),
        ]
    finally:
        session.leave()
        plane.commit(session)
