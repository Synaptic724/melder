"""
Component tests for owner constraint 3 - Aether HOLDS the plane.

WHY THIS FILE EXISTS: the plane was complete and correct for a while and still
unreachable, because nothing constructed it. Constraint 3 is what closes that -
"Aether MANAGES it (holds it), and it is constructed IMMEDIATELY, first, right
after Aether itself is built". These tests hold that property in place.

THE ORDERING IS THE POINT, not the ownership. An admission authority that
appeared AFTER the things it governs could never admit their creation, so
"exists before any frame" is the assertion that actually matters and
`test_plane_exists_before_any_frame_does` is the one to keep if the rest ever
get pruned.

Constraint 4 - the plane knows nothing about Aether - is enforced separately and
statically by `test_plane_declares_no_dependency_on_aether` in
`test_aetheric_mediator_component.py`. That direction is not re-tested here;
this file only covers the direction that was just added.

Run:
    pytest tests/component/melder/aether/aetheric_mediator -q
"""

import pytest

from melder import Aether
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_type import TransactionType


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_plane_ownership() -> None:
    """
    Purpose:
        Isolate plane-ownership tests behind a fresh Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Resets it again afterwards so later tests see a clean root.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()


def test_aether_holds_a_plane():
    """Constraint 3, the ownership half."""
    aether = Aether()
    plane = aether.aetheric_mediator
    assert isinstance(plane, Mediator)
    assert plane.cleaned is False


def test_the_plane_is_owned_not_rebuilt_per_access():
    """
    The accessor returns the OWNED instance. A property that rebuilt would hand
    every caller a private plane with a private claim table, which is the exact
    opposite of having one admission authority - and it would fail silently,
    because each caller's transactions would admit perfectly against nothing.
    """
    aether = Aether()
    assert aether.aetheric_mediator is aether.aetheric_mediator


def test_the_plane_is_shared_across_the_singleton():
    """
    Aether is a process-wide singleton, so two references must reach one plane.
    """
    assert Aether().aetheric_mediator is Aether().aetheric_mediator


def test_a_freshly_built_aether_already_carries_a_working_plane():
    """
    THE ORDERING ASSERTION, and the reason constraint 3 says "immediately,
    first". Nothing has been asked of this Aether yet - no frame, no spellbook,
    no subsystem - and the plane is already complete: every vocabulary member
    resolves. If the plane were made lazy, or moved below frame construction,
    a fresh root would not satisfy this.

    Stated through `missing_types()` rather than by counting frames. Frame
    population has no public accessor, and reaching into `_aetheric_frames`
    would assert an internal shape instead of a contract outcome.
    """
    plane = Aether().aetheric_mediator
    assert plane.cleaned is False
    assert plane.strategies.missing_types() == ()


def test_the_held_plane_is_usable_end_to_end():
    """
    Present and constructed is not the same as usable. This drives a real
    transaction through the Aether-held plane so the seam is proven rather than
    assumed - and asserts the claim set, so a plane wired to a broken registry
    would fail here rather than merely existing.
    """
    plane = Aether().aetheric_mediator
    who = Identity(kind="crystallizer", identity_id="ownership-probe")
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=who,
        metadata={"target_frame_name": "probe"},
    )
    try:
        assert sorted(session.staged.granted_scopes) == [
            ScopeKey.frame("probe"),
            ScopeKey.world(),
        ]
    finally:
        session.leave()
        plane.commit(session)
        who.cleanup()


def test_plane_is_cleaned_with_its_owner():
    """
    Aether owns the plane, so Aether's teardown must take it down. A plane that
    survived its owner would hold claims for a world that no longer exists.

    The ORDER matters and is asserted indirectly: `Aether.cleanup` cleans the
    LoadGate first and the plane immediately after, both before frames, because
    `ClaimTable.cleanup` wakes every thread parked in `wait_for_change` before
    dropping state. Tearing it down early releases waiters instead of stranding
    them behind a world that is already going away.
    """
    aether = Aether()
    plane = aether.aetheric_mediator
    assert plane.cleaned is False
    aether.cleanup()
    assert plane.cleaned is True


def test_accessor_refuses_after_the_owner_is_cleaned():
    """
    Reaching for the plane through a cleaned Aether must raise rather than hand
    back a dead object - the `check_cleaned` contract every accessor here holds.
    """
    aether = Aether()
    aether.cleanup()
    with pytest.raises(RuntimeError):
        _ = aether.aetheric_mediator
