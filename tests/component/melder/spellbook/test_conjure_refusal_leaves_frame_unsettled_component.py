"""
Component tests: a refused dynamic conjure leaves its frame as it was (0.2.8211).

WHY THIS EXISTS. With an active Crystallizer, a dynamic conjure is refused when spells were bound while the Book's
configuration was still mutable (the recorded world would persist binds that ran against unsettled
configuration). The refusal used to run AFTER conjure settled the frame posture, so a refused
`conjure(dynamic=True)` left an unsettled frame frozen dynamic - and every later conjure in that frame inherited
dynamic and was refused too, even a plain automatic one the discipline exempts. That is how a second Melder user
turning recording on (MelderOps' AI preset) could lock a host's frame. The refusal now runs on the mode settlement
WOULD produce, before settling.

Contract under test:
    1. after the refusal an unsettled frame is still unfrozen and automatic;
    2. an automatic conjure in that frame then succeeds and settles it automatic;
    3. a settled dynamic frame is still refused for an inheriting conjure (dynamic=False);
    4. the predicted mode equals the settled mode for every posture/flag combination, and predicting mutates nothing.
"""

from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class RefusalHostService:
    """Plain spell bound by the host Book before its configuration is finalized."""


class RefusalPeerService:
    """Plain spell bound by a peer Book whose configuration is finalized first."""


@pytest.fixture(autouse=True)
def reset_world_for_conjure_refusal() -> Iterator[None]:
    """Give each test fresh hosted roots, so every frame is born unsettled and recording is off."""

    def _reset() -> None:
        """Reset the hosted roots and rebind the static Aether references."""
        MutationResearch._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


def _turn_recording_on() -> None:
    """Activate the hosted Crystallizer with its default policy, as a second Melder user would."""
    policy = CrystallizerConfiguration().with_defaults()
    policy.activate()
    Crystallizer().activate(policy)


def _early_bound_book(frame_name: str) -> Spellbook:
    """Return a Book on `frame_name` that bound one spell while its configuration was still mutable."""
    book = Spellbook(aetheric_frame=frame_name)
    book.bind(spell=RefusalHostService, existence="many")
    return book


def test_refused_dynamic_conjure_leaves_an_unsettled_frame_unsettled() -> None:
    """The refusal no longer settles the frame dynamic on its way out."""
    book = _early_bound_book("refusal_host")
    _turn_recording_on()
    posture = Aether().get_frame("refusal_host").frame_configuration
    assert posture.frozen is False
    assert posture.system_state is SystemState.automatic

    with pytest.raises(RuntimeError, match="finalized BEFORE the first bind"):
        book.conjure(name="root", dynamic=True)

    assert Aether().get_frame("refusal_host").frame_configuration is posture
    assert posture.frozen is False
    assert posture.system_state is SystemState.automatic


def test_an_automatic_conjure_after_the_refusal_still_runs_automatic() -> None:
    """The discipline exempts automatic worlds, and the refused attempt no longer forces dynamic on them."""
    book = _early_bound_book("refusal_host")
    _turn_recording_on()
    with pytest.raises(RuntimeError, match="finalized BEFORE the first bind"):
        book.conjure(name="root", dynamic=True)

    conduit = book.conjure(name="root")

    posture = Aether().get_frame("refusal_host").frame_configuration
    assert conduit.spellbook is book
    assert posture.frozen is True
    assert posture.system_state is SystemState.automatic


def test_an_inheriting_conjure_in_a_settled_dynamic_frame_is_still_refused() -> None:
    """dynamic=False inherits a settled dynamic world, so the prediction must still say dynamic."""
    peer_configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(peer_configuration)
    peer_configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    peer_configuration.finalize()
    peer = Spellbook(configuration=peer_configuration)
    peer.bind(spell=RefusalPeerService, existence="many")
    peer.conjure(name="peer_root", dynamic=True)
    frame_name = peer_configuration.aether_frame
    posture = Aether().get_frame(frame_name).frame_configuration
    assert posture.frozen is True and posture.system_state is SystemState.dynamic

    book = _early_bound_book(frame_name)
    _turn_recording_on()
    with pytest.raises(RuntimeError, match="finalized BEFORE the first bind"):
        book.conjure(name="root")
    assert posture.system_state is SystemState.dynamic


@pytest.mark.parametrize("staged_state", [SystemState.automatic, SystemState.dynamic])
@pytest.mark.parametrize("frozen", [False, True])
@pytest.mark.parametrize("requested_dynamic", [False, True])
def test_the_predicted_mode_equals_the_settled_mode(
        staged_state: SystemState,
        frozen: bool,
        requested_dynamic: bool,
) -> None:
    """_effective_conjure_mode must agree with _settle_or_inherit_conjure_mode and mutate nothing."""
    book = Spellbook(aetheric_frame="prediction")
    frame = Aether().get_frame("prediction")
    posture = frame.frame_configuration
    posture.with_system_state(staged_state)
    if frozen:
        frame.freeze_frame_configuration()

    predicted = book._effective_conjure_mode(requested_dynamic)
    assert posture.frozen is frozen
    assert posture.system_state is staged_state

    settled = book._settle_or_inherit_conjure_mode(requested_dynamic)
    assert predicted is settled
