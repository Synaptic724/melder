"""Controlled real-meld regressions for shared context rebuild publication."""

from collections.abc import Iterator
from threading import Event, Thread, current_thread
from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
    SpellSystemStates,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import CompilerPhase5
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import SpellCompilerArtifact
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.synchronization.creation_gate import CreationGate
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests.mocks.spellbook.core_classes import BasicService


class _BlockingService:
    """Service whose construction can be held open by a test (in-flight reader)."""

    entered: Optional[Event] = None
    release: Optional[Event] = None

    def __init__(self) -> None:
        """Block inside construction while the test holds `release`."""
        entered = type(self).entered
        release = type(self).release
        if entered is not None and release is not None:
            entered.set()
            if not release.wait(10.0):
                raise TimeoutError("Test did not release the blocked construction.")


@pytest.fixture
def shared_runtime() -> Iterator[tuple[Conduit, Conduit, Spell]]:
    """Yield two linked live conduits sharing one warmed class spell.

    The owner has completed resolution; the peer has not. Every worker in a
    test must finish before this fixture performs terminal runtime cleanup.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book = Spellbook(configuration=configuration)
    peer_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="context-owner")
    peer = peer_book.conjure(dynamic=True, name="context-peer")
    try:
        owner.link(peer)
        cloud = aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("context-cluster")
        cloud.add_conduit_to_cluster(owner, "context-cluster")
        cloud.add_conduit_to_cluster(peer, "context-cluster")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("context-cluster").elect_leader(owner.id)
        assert isinstance(owner.meld(spell_id=spell_id), BasicService)
        yield owner, peer, owner_book._spells_by_id[spell_id]
    finally:
        peer.cleanup()
        owner.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs(
        monkeypatch: pytest.MonkeyPatch,
        shared_runtime: tuple[Conduit, Conduit, Spell],
) -> None:
    """A peer's phase-5/phase-11 gap cannot expose incomplete inputs to the owner.

    Both callers use the real public meld path. Only scheduling boundaries are
    wrapped: the peer pauses after normal phase 5, and the owner reports either
    parking at the shared index gate or completion. No runtime fields, switch
    tickets, compiler inputs or exceptions are fabricated by the reproduction.
    Timeouts are hang guards; the producer is released by the observed reader
    transition, never by sleeping and hoping the race occurred.
    """
    owner, peer, spell = shared_runtime
    index_gate = spell._creation_context._creation_gate
    phase5_finished = Event()
    release_phase11 = Event()
    reader_observed = Event()
    results: dict[str, object] = {}
    failures: list[BaseException] = []
    original_phase5 = CompilerPhase5.run_local
    original_admit = CreationGate.admit_ticket

    def pause_after_phase5(
            phase: CompilerPhase5,
            target: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """Pause only the peer after its real scoped invalidation has completed."""
        original_phase5(
            phase, target, artifact, spellbook, spell_system_states,
            conduit_id, cancel_event,
        )
        if target is spell and conduit_id == peer.id:
            phase5_finished.set()
            if not release_phase11.wait(10.0):
                raise TimeoutError("Test did not release the peer's phase-11 continuation.")

    def observe_admission(gate: CreationGate) -> None:
        """Report genuine parked admission; an open gate must finish the call first."""
        if (
                gate is index_gate
                and current_thread().name == "context-reader"
                and not gate.enabled
        ):
            reader_observed.set()
        original_admit(gate)

    def resolve(key: str, conduit: Conduit) -> None:
        """Collect the actual result or original failure from one real meld."""
        try:
            results[key] = conduit.meld(spell_id=spell.spell_id)
        except BaseException as error:
            failures.append(error)
        finally:
            if key == "owner":
                reader_observed.set()

    monkeypatch.setattr(CompilerPhase5, "run_local", pause_after_phase5)
    monkeypatch.setattr(CreationGate, "admit_ticket", observe_admission)
    writer = Thread(target=resolve, args=("peer", peer), name="context-writer")
    reader = Thread(target=resolve, args=("owner", owner), name="context-reader")
    reader_started = False
    try:
        writer.start()
        assert phase5_finished.wait(10.0), (
            f"Peer did not reach its phase-5 boundary: {failures!r}; results={results!r}"
        )
        reader.start()
        reader_started = True
        assert reader_observed.wait(10.0), "Owner neither parked nor completed."
        release_phase11.set()
        writer.join(10.0)
        reader.join(10.0)
        assert not writer.is_alive(), "Peer rebuild did not finish."
        assert not reader.is_alive(), "Owner meld remained parked after publication."
        assert failures == []
        assert isinstance(results["owner"], BasicService)
        assert results["owner"] is results["peer"]
    finally:
        release_phase11.set()
        # Teardown recovery only: a failed implementation must not leave a
        # blocked test worker running while the fixture cleans its owners.
        if reader_started and reader.is_alive():
            index_gate.open()
        writer.join(10.0)
        if reader_started:
            reader.join(10.0)


@pytest.fixture
def blocking_runtime() -> Iterator[tuple[Conduit, Conduit, Spell]]:
    """Yield two linked dynamic conduits sharing one warmed Existence.many spell.

    The owner has melded once; the peer has not, so the peer's first meld reruns
    phases 5-11 for the shared spell.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book = Spellbook(configuration=configuration)
    peer_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=_BlockingService,
        existence=Existence.many,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="blocking-owner")
    peer = peer_book.conjure(dynamic=True, name="blocking-peer")
    try:
        owner.link(peer)
        with peer.transaction("link", conduits=[peer, owner]):
            peer.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            )
        assert isinstance(owner.meld(spell_id=spell_id), _BlockingService)
        yield owner, peer, owner_book._spells_by_id[spell_id]
    finally:
        _BlockingService.entered = None
        _BlockingService.release = None
        peer.cleanup()
        owner.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def test_peer_rebuild_waits_for_owner_meld_already_executing(
        monkeypatch: pytest.MonkeyPatch,
        blocking_runtime: tuple[Conduit, Conduit, Spell],
) -> None:
    """A rebuild cannot replace the plan or clean the context while an admitted meld is executing.

    The owner's meld is held inside construction (it holds the spell-index ticket).
    The peer's first meld starts a rebuild window; the window must drain that ticket
    before Phase 5 runs. Observation points are the real drain call and Phase 5
    entry; nothing is timed.
    """
    owner, peer, spell = blocking_runtime
    entered = Event()
    release = Event()
    drain_started = Event()
    order: list[str] = []
    results: dict[str, object] = {}
    failures: list[BaseException] = []
    original_drain = CreationGate.close_and_drain
    original_phase5 = CompilerPhase5.run_local

    def observe_drain(gate: CreationGate, timeout: float = 30.0, interval: float = 0.1) -> None:
        """Report that the rebuild window started draining admitted melds."""
        drain_started.set()
        original_drain(gate, timeout=timeout, interval=interval)

    def observe_phase5(
            phase: CompilerPhase5,
            target: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """Record when Phase 5 replaces the shared plan."""
        if target is spell:
            order.append("phase5")
        original_phase5(
            phase, target, artifact, spellbook, spell_system_states,
            conduit_id, cancel_event,
        )

    def resolve(key: str, conduit: Conduit) -> None:
        """Collect the result or the original failure from one real meld."""
        try:
            results[key] = conduit.meld(spell_id=spell.spell_id)
            order.append(key)
        except BaseException as error:
            failures.append(error)

    monkeypatch.setattr(CreationGate, "close_and_drain", observe_drain)
    monkeypatch.setattr(CompilerPhase5, "run_local", observe_phase5)
    _BlockingService.entered = entered
    _BlockingService.release = release
    reader = Thread(target=resolve, args=("owner", owner), name="in-flight-reader")
    writer = Thread(target=resolve, args=("peer", peer), name="rebuilding-peer")
    try:
        reader.start()
        assert entered.wait(10.0), "Owner meld did not reach construction."
        # From here on only the owner's construction blocks; the peer's must not.
        _BlockingService.entered = None
        _BlockingService.release = None
        writer.start()
        assert drain_started.wait(10.0), "Peer rebuild did not start draining."
        # The drain cannot finish while the owner holds its ticket.
        assert order == []
        release.set()
        reader.join(10.0)
        writer.join(10.0)
        assert not reader.is_alive()
        assert not writer.is_alive()
        assert failures == []
        assert isinstance(results["owner"], _BlockingService)
        assert isinstance(results["peer"], _BlockingService)
        assert order.index("owner") < order.index("phase5")
    finally:
        release.set()
        reader.join(10.0)
        writer.join(10.0)
