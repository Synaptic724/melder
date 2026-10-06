"""Aether finds, lists and returns frames without creating them, and hosts can read what they compare against.

Host integrations such as MelderOps create frames by constructing Spellbooks and later need to find the frames
they created. Every other frame-scoped Aether call creates "default" when it is missing (and the first frame seals
the Aether configuration), so a host had to read Aether's private registry to look without creating. Since
0.2.8208 `Aether.find_frame`, `Aether.get_frame` and `Aether.list_frame_names` never create a frame, and the frame
and conduit accessors a host compares against (`AethericFrame.shared_spellbook_configuration`, `Conduit.spellbook`)
are public reads.
"""

import logging
import threading
from collections.abc import Iterator
from typing import List

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.spellbook.spellbook import Spellbook
from tests._codegen_system_support import reset_runtime_singletons


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Give every scenario a fresh Aether with no frames and clean the singletons afterwards."""
    reset_runtime_singletons()
    try:
        yield
    finally:
        reset_runtime_singletons()


def test_lookups_on_a_fresh_world_create_no_frame_and_leave_the_configuration_unsealed() -> None:
    """No lookup births "default": the registry stays empty and no configuration is installed or frozen."""
    aether = Aether()
    assert aether.list_frame_names() == ()
    assert aether.find_frame("default") is None
    with pytest.raises(ValueError, match="Aetheric frame 'default' does not exist"):
        aether.get_frame("default")
    assert aether.find_frame("anything") is None
    assert aether.list_frame_names() == ()
    assert aether.configuration is None


def test_a_spellbook_frame_is_found_and_returned_as_the_same_object() -> None:
    """The frame a Spellbook creates is the object both lookups return, under its own name."""
    Spellbook(aetheric_frame="ops")
    aether = Aether()
    frame = aether.find_frame("ops")
    assert frame is not None
    assert aether.get_frame("ops") is frame
    assert frame.name == "ops"
    assert aether.find_frame("default") is None


def test_list_frame_names_follows_registration_order_and_is_a_snapshot() -> None:
    """Names come back in creation order as a tuple that later creations do not change."""
    Spellbook(aetheric_frame="first")
    Spellbook()
    Spellbook(aetheric_frame="second")
    names = Aether().list_frame_names()
    assert names == ("first", "default", "second")
    Spellbook(aetheric_frame="third")
    assert names == ("first", "default", "second")
    assert Aether().list_frame_names() == ("first", "default", "second", "third")


def test_a_cleaned_frame_is_absent_from_every_lookup() -> None:
    """Once a frame is cleaned it is neither found, listed nor returned."""
    book = Spellbook(aetheric_frame="gone")
    aether = Aether()
    frame = aether.get_frame("gone")
    book.cleanup()
    frame.cleanup()
    assert aether.find_frame("gone") is None
    assert "gone" not in aether.list_frame_names()
    with pytest.raises(ValueError, match="Aetheric frame 'gone' does not exist"):
        aether.get_frame("gone")


def test_get_frame_error_says_how_to_create_or_probe_the_frame() -> None:
    """The not-found message keeps the familiar prefix and points at find_frame and Spellbook."""
    with pytest.raises(ValueError) as caught:
        Aether().get_frame("missing")
    message = str(caught.value)
    assert message.startswith("Aetheric frame 'missing' does not exist.")
    assert "find_frame" in message
    assert "Spellbook" in message


@pytest.mark.parametrize("bad_name", [None, 7, ("ops",)], ids=["none", "int", "tuple"])
def test_frame_lookups_refuse_a_name_that_is_not_a_string(bad_name: object) -> None:
    """A non-string frame name raises TypeError naming the call that received it."""
    aether = Aether()
    with pytest.raises(TypeError, match="find_frame"):
        aether.find_frame(bad_name)
    with pytest.raises(TypeError, match="get_frame"):
        aether.get_frame(bad_name)


def test_frame_lookups_on_a_cleaned_aether_raise_runtime_error() -> None:
    """A cleaned Aether refuses every frame lookup instead of reading a torn-down registry."""
    aether = Aether()
    aether.cleanup()
    with pytest.raises(RuntimeError):
        aether.find_frame("default")
    with pytest.raises(RuntimeError):
        aether.get_frame("default")
    with pytest.raises(RuntimeError):
        aether.list_frame_names()


def test_listing_while_other_threads_create_frames_never_raises() -> None:
    """Listing takes one copy of the registry, so concurrent frame creation never breaks it."""
    errors: List[BaseException] = []
    stop = threading.Event()

    def lister() -> None:
        try:
            while not stop.is_set():
                names = Aether().list_frame_names()
                assert len(names) == len(set(names))
        except BaseException as error:
            errors.append(error)

    def creator(offset: int) -> None:
        try:
            for index in range(10):
                Spellbook(aetheric_frame=f"frame-{offset}-{index}")
        except BaseException as error:
            errors.append(error)

    listener = threading.Thread(target=lister, daemon=True)
    creators = [threading.Thread(target=creator, args=(offset,), daemon=True) for offset in range(4)]
    listener.start()
    for thread in creators:
        thread.start()
    for thread in creators:
        thread.join(timeout=60)
    stop.set()
    listener.join(timeout=60)
    assert not listener.is_alive()
    assert not any(thread.is_alive() for thread in creators)
    assert errors == []
    expected = {f"frame-{offset}-{index}" for offset in range(4) for index in range(10)}
    assert expected <= set(Aether().list_frame_names())


def test_shared_spellbook_configuration_is_none_while_the_frame_does_not_share_it() -> None:
    """A frame whose posture does not share the rich configuration reports None after conjure."""
    Spellbook(aetheric_frame="private").conjure(name="root")
    frame = Aether().get_frame("private")
    assert frame.frame_configuration.shared_framewide_spellbook_configuration is False
    assert frame.shared_spellbook_configuration is None


def test_shared_spellbook_configuration_is_the_bound_configuration_when_shared() -> None:
    """With sharing on, the frame reports the rich configuration the first Book bound, by identity."""
    book = Spellbook(aetheric_frame="shared")
    book.configure_aether_frame(
        system_state="automatic", disposal=None, disposal_method_names=None,
        shared_framewide_spellbook_configuration=True,
    )
    book.conjure(name="root")
    frame = Aether().get_frame("shared")
    assert frame.frame_configuration.shared_framewide_spellbook_configuration is True
    assert frame.shared_spellbook_configuration is book.get_configuration()


def test_shared_spellbook_configuration_raises_once_the_frame_is_cleaned() -> None:
    """A cleaned frame refuses the read instead of reporting stale configuration."""
    book = Spellbook(aetheric_frame="short")
    frame = Aether().get_frame("short")
    book.cleanup()
    frame.cleanup()
    with pytest.raises(RuntimeError):
        _ = frame.shared_spellbook_configuration


def test_conduit_spellbook_is_the_conjuring_book_for_a_root_and_its_lessers() -> None:
    """A root and the lessers under it all resolve through the Book that conjured the root."""
    book = Spellbook(aetheric_frame="scopes")
    root = book.conjure(name="root")
    lesser = root.create_lesser_conduit()
    nested = lesser.create_lesser_conduit(name="nested")
    assert root.spellbook is book
    assert book.conduit is root
    assert lesser.spellbook is book
    assert nested.spellbook is book


def test_conduit_spellbook_raises_after_the_root_is_torn_down() -> None:
    """A torn-down root refuses the read."""
    root = Spellbook(aetheric_frame="teardown").conjure(name="root")
    root.cleanup()
    with pytest.raises(RuntimeError):
        _ = root.spellbook


def test_a_lookup_does_not_stand_in_for_frame_creation() -> None:
    """After a lookup finds nothing, the first Spellbook still creates the frame and seals the configuration."""
    aether = Aether()
    assert aether.find_frame("default") is None
    assert aether.configuration is None
    Spellbook()
    assert aether.find_frame("default") is not None
    assert aether.configuration is not None
    assert aether.configuration.frozen is True


def test_get_frame_logs_the_not_found_message(caplog: pytest.LogCaptureFixture) -> None:
    """The refusal is logged at ERROR with the same text the ValueError carries."""
    logger = logging.getLogger("melder.tests.frame_lookups")
    Aether().attach_logger(logger)
    with caplog.at_level(logging.ERROR, logger="melder.tests.frame_lookups"):
        with pytest.raises(ValueError):
            Aether().get_frame("missing")
    assert any("Aetheric frame 'missing' does not exist." in record.getMessage() for record in caplog.records)


def test_lookups_while_a_frame_is_created_and_cleaned_never_raise() -> None:
    """A frame cleaned while another thread looks it up reads as present or absent, never as an error."""
    errors: List[BaseException] = []
    stop = threading.Event()

    def reader() -> None:
        try:
            while not stop.is_set():
                frame = Aether().find_frame("churn")
                assert frame is None or isinstance(frame, AethericFrame)
                names = Aether().list_frame_names()
                assert names.count("churn") <= 1
        except BaseException as error:
            errors.append(error)

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    try:
        for _ in range(30):
            book = Spellbook(aetheric_frame="churn")
            frame = Aether().get_frame("churn")
            book.cleanup()
            frame.cleanup()
    finally:
        stop.set()
        thread.join(timeout=60)
    assert not thread.is_alive()
    assert errors == []
    assert Aether().find_frame("churn") is None


def test_a_second_spellbook_in_a_sharing_frame_adopts_the_reported_configuration() -> None:
    """The configuration the frame reports as shared is the one the next Spellbook in the frame adopts."""
    book = Spellbook(aetheric_frame="shared")
    book.configure_aether_frame(
        system_state="automatic", disposal=None, disposal_method_names=None,
        shared_framewide_spellbook_configuration=True,
    )
    book.conjure(name="root")
    shared = Aether().get_frame("shared").shared_spellbook_configuration
    assert shared is not None
    second = Spellbook(aetheric_frame="shared")
    assert second.get_configuration() is shared


def test_conduit_spellbook_follows_an_upgrade_to_its_new_spellbook() -> None:
    """An upgraded lesser reports the new Spellbook it now belongs to, which reports it back as its root."""
    book = Spellbook(aetheric_frame="grow")
    root = book.conjure(name="root", dynamic=True)
    lesser = root.create_lesser_conduit()
    assert lesser.spellbook is book
    lesser.upgrade_to_normal("promoted")
    assert lesser.spellbook is not book
    assert lesser.spellbook.conduit is lesser
