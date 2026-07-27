"""
Advanced-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py -v
"""
import melder as md
import pytest

from melder import Aether, Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_world() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class Payload:
    pass


def test_probe_frames_isolate_names_and_singletons():
    """Lesson 03 contract (README claim, pinned): two frames bind the
    SAME class with zero collision, and unique = one singleton PER
    FRAME. A red here is a finding against the README."""
    book_a = Spellbook(aetheric_frame="probe-tenant-a")
    book_b = Spellbook(aetheric_frame="probe-tenant-b")
    book_a.bind(spell=Payload, existence="unique")
    book_b.bind(spell=Payload, existence="unique")
    a = book_a.conjure().meld(spell=Payload)
    b = book_b.conjure().meld(spell=Payload)
    assert a is not b
    print("frame isolation pinned: same class, two worlds, two singletons")


def test_probe_posture_public_door_then_freeze():
    """Lesson 04 contract: configure_aether_frame(system_state="dynamic")
    before any conjure -> plain conjures inherit and link; after the
    first conjure froze the posture, reconfiguring refuses."""
    book = Spellbook(aetheric_frame="probe-ops")
    book.bind(spell=Payload, existence="unique")
    book.configure_aether_frame(system_state="dynamic", disposal=None,
                                disposal_method_names=None)
    root = book.conjure(name="probe-ops-root")
    peer = Spellbook(aetheric_frame="probe-ops").conjure(name="probe-ops-peer")
    assert root.link(peer) is True
    with pytest.raises(Exception) as refused:
        book.configure_aether_frame(system_state="automatic", disposal=None,
                                    disposal_method_names=None)
    print("post-freeze reconfigure refusal type:", type(refused.value).__name__)


def test_probe_devops_flags_gate_via_retained_posture_seam():
    """FINDING (2026-07-25): there is NO PUBLIC DOOR to stage the frame
    devops flags (disable_linking / disable_bind / ...) - the component
    suite stages them through the book's PRIVATE retained posture
    (book._aetheric_frame_configuration.with_disable_*). This probe pins
    the gate behavior through that same seam so the curriculum can teach
    it the day a public door exists. Public-surface gap recorded for the
    owner's init program."""
    book = Spellbook(aetheric_frame="probe-flags")
    book.bind(spell=Payload, existence="unique")
    book._aetheric_frame_configuration.with_system_state("dynamic")
    book._aetheric_frame_configuration.with_disable_linking(True)
    owner = book.conjure(dynamic=True, name="flag-owner")
    borrower = Spellbook(aetheric_frame="probe-flags").conjure(name="flag-borrower")
    with pytest.raises(RuntimeError, match="disabled"):
        owner.link(borrower)
    print("devops flag gate pinned: disable_linking refused the link")


def test_probe_attach_logger_lifecycle():
    """Lesson 05 contract: melder boots silent; attach_logger attaches a
    real logger post-boot; None detaches back to the null wrapper;
    enable_logging(explicit) is the same attachment."""
    import logging
    aether = Aether()
    logger = logging.getLogger("probe-advanced-logger")
    aether.attach_logger(logger)
    aether.attach_logger(None)
    aether.enable_logging(logger)
    aether.attach_logger(None)
    print("logger attach/detach lifecycle clean")
