"""September plan, tests part 2: contract tests for admission, rebuild windows and build failure (2026-09-26).

Usage: python apply_sept_tests.py <repo_root>   (after apply_sept_test_stubs.py)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import append_block, create_file, replace_block

root = pathlib.Path(sys.argv[1])
concrete = root / "tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py"
factory_tests = root / "tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py"
rebuild_tests = root / "tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_rebuild.py"
spell_tests = root / "tests/unit/melder/spellbook/test_spell.py"
component = root / "tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py"

# =============================================================== Meld doors (unit)
replace_block(concrete,
'''from threading import RLock''',
'''from threading import Event, RLock, Thread''')
replace_block(concrete,
'''from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)''',
'''from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.utilities.synchronization.creation_gate import CreationGate''')
append_block(concrete, '''

class _ObservedGate(CreationGate):
    """CreationGate that reports when a caller starts admission."""

    def __init__(self) -> None:
        super().__init__()
        self.admitting = Event()

    def admit_ticket(self) -> None:
        """Signal entry, then run the real visibility-first admission."""
        self.admitting.set()
        super().admit_ticket()


def _make_dynamic_spell(
        creations: Any,
        context: _CreationContextStub,
        gate: CreationGate,
        *,
        hooks_enabled: bool = False,
) -> _SpellStub:
    """Build a spell stub under dynamic ownership (spell-index gate present)."""
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=creations,
        creation_context=context,
        hooks_enabled=hooks_enabled,
    )
    spell._creation_gate = gate
    return spell


def test_conduit_meld_dynamic_no_hooks_holds_one_index_ticket_through_execution() -> None:
    """A dynamic meld holds exactly one index ticket while its executor runs, and none after."""
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    gate = CreationGate()
    spell = _make_dynamic_spell(creations, context, gate)
    _seed_spell(spellbook, spell)
    counts: list[int] = []
    original = context.execute_no_hooks

    def _recording(caller_creations: Any, overrides: Any = None, root_creations: Any = None) -> Any:
        """Record the live ticket count seen by the executor."""
        counts.append(gate.active_ticket_count())
        return original(caller_creations, overrides, root_creations)

    context.execute_no_hooks = _recording
    assert meld.meld(spell="spell-1") == "instance"
    assert counts == [1]
    assert gate.active_ticket_count() == 0


def test_conduit_meld_dynamic_door_parks_before_reading_context_while_gate_frozen() -> None:
    """A frozen spell-index gate parks a dynamic meld before it touches the context."""
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    gate = _ObservedGate()
    spell = _make_dynamic_spell(creations, context, gate)
    _seed_spell(spellbook, spell)
    gate.close()
    results: list[Any] = []

    def _resolve() -> None:
        """Run the meld on a worker thread."""
        results.append(meld.meld(spell="spell-1"))

    worker = Thread(target=_resolve, name="parked-meld")
    worker.start()
    try:
        assert gate.admitting.wait(timeout=5.0)
        # Admission cannot return while the gate is closed, so the context
        # has not been read and its executor has not run.
        assert context.calls == []
    finally:
        gate.open()
        worker.join(timeout=5.0)
    assert not worker.is_alive()
    assert results == ["instance"]
    assert context.calls == ["no_hooks_no_overrides"]


def test_conduit_meld_dynamic_executor_failure_releases_ticket() -> None:
    """An executor failure propagates and still releases the held index ticket."""
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub()
    gate = CreationGate()
    spell = _make_dynamic_spell(creations, context, gate)
    _seed_spell(spellbook, spell)

    def _failing(caller_creations: Any, overrides: Any = None, root_creations: Any = None) -> Any:
        """Fail inside execution."""
        raise ValueError("constructor failed")

    context.execute_no_hooks = _failing
    with pytest.raises(ValueError, match="constructor failed"):
        meld.meld(spell="spell-1")
    assert gate.active_ticket_count() == 0


def test_conduit_meld_dynamic_hooks_lane_admits_once_and_reports_created() -> None:
    """The dynamic hooks lane runs the executor slot under one ticket and fires activation on create."""
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    gate = CreationGate()
    spell = _make_dynamic_spell(creations, context, gate, hooks_enabled=True)
    activations: list[Any] = []
    spell._activation_hooks.append(lambda instance: activations.append(instance))
    _seed_spell(spellbook, spell)
    counts: list[int] = []
    original = context.execute_no_hooks

    def _recording(caller_creations: Any, overrides: Any = None, root_creations: Any = None) -> Any:
        """Record the live ticket count seen by the executor."""
        counts.append(gate.active_ticket_count())
        return original(caller_creations, overrides, root_creations)

    context.execute_no_hooks = _recording
    assert meld.meld(spell="spell-1") == "instance"
    assert counts == [1]
    assert activations == ["instance"]
    assert "hooks_no_overrides" not in context.calls
    assert gate.active_ticket_count() == 0


def test_spellspace_meld_dynamic_no_hooks_holds_one_index_ticket_through_execution() -> None:
    """The SpellSpace door admits the spell-index ticket the same way as the conduit door."""
    meld, spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    gate = CreationGate()
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        owner_creations=owner_creations,
        creation_context=context,
    )
    spell._creation_gate = gate
    _seed_spell(spellbook, spell)
    counts: list[int] = []
    original = context.execute_no_hooks

    def _recording(caller_creations: Any, overrides: Any = None, root_creations: Any = None) -> Any:
        """Record the live ticket count seen by the executor."""
        counts.append(gate.active_ticket_count())
        return original(caller_creations, overrides, root_creations)

    context.execute_no_hooks = _recording
    assert meld.meld(spell="spell-1") == "instance"
    assert counts == [1]
    assert gate.active_ticket_count() == 0


def test_meld_execute_admitted_rechecks_deferred_resolution_without_holding_ticket() -> None:
    """A spell that became resolution_required while parked is resolved with no ticket held."""
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    gate = CreationGate()
    spell = _make_dynamic_spell(creations, context, gate)
    spell.resolution_required = True
    seen: list[int] = []

    def _resolve_deferred(target: Any) -> None:
        """Stand in for the deferred 8-11 path and record the ticket count it sees."""
        seen.append(gate.active_ticket_count())
        target.resolution_required = False

    meld._ensure_runtime_resolution_ready = _resolve_deferred
    assert meld._execute_admitted(spell, gate, None, False) == "instance"
    assert seen == [0]
    assert gate.active_ticket_count() == 0


def test_meld_rebuild_window_is_noop_without_gate_and_freezes_dynamic_gate() -> None:
    """Automatic spells get a no-op window; dynamic spells get a freeze/drain window over their gate."""
    meld, creations, _spellbook = _make_conduit_meld()
    automatic = _SpellStub(
        spell_id="spell-a",
        existence=Existence.unique_per_conduit,
        owner_creations=creations,
    )
    assert not isinstance(meld._rebuild_window(automatic), CreationContextRebuild)
    gate = CreationGate()
    dynamic = _make_dynamic_spell(creations, _CreationContextStub(), gate)
    window = meld._rebuild_window(dynamic)
    assert isinstance(window, CreationContextRebuild)
    with window:
        assert gate.enabled is False
    assert gate.enabled is True
''')

# =============================================================== Factory (unit)
replace_block(factory_tests,
'''        self._creation_context_switch = CounterSwitch(state=switch_state)
        self._lock = RLock()''',
'''        self._creation_context_switch = CounterSwitch(state=switch_state)
        # Mirror the real Spell fields added for rebuild windows.
        self._creation_context_failure: Optional[BaseException] = None
        self._creation_gate: Optional[Any] = None
        self._lock = RLock()''')
append_block(factory_tests, '''

def _raise_build(
        target: Any,
        *,
        dynamic_environment: bool = False,
        creation_gate: Optional[Any] = None,
        creation_gate_index_id: Optional[str] = None,
) -> Any:
    """Fail the way the builder does when the phase-11 plan is absent."""
    _ = (target, dynamic_environment, creation_gate, creation_gate_index_id)
    raise RuntimeError("Cannot build CreationContext before spell_codegen_creation exists.")


def test_get_or_build_for_spell_failed_leader_records_cause_and_releases_claim(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed leader records its cause on the spell and returns the switch to idle."""
    spell = _SpellStub(creation_context=None, switch_state=0)
    monkeypatch.setattr(CreationContextBuilder, "build", _raise_build)
    factory = CreationContextFactory(creation_gate_controller=CreationGateController())

    with pytest.raises(RuntimeError, match="spell_codegen_creation") as raised:
        factory.get_or_build_for_spell(spell)

    assert spell._creation_context_failure is raised.value
    assert spell._creation_context_switch.state == 0
    assert spell._creation_context is None


def test_get_or_build_for_spell_follower_woken_by_failed_leader_reports_cause(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A follower woken with nothing published raises chained from the leader's recorded cause."""
    cause = RuntimeError("plan missing")
    spell = _SpellStub(creation_context=None)
    spell._creation_context_switch = _SwitchStub(state=1, selector_return=0)
    spell._creation_context_failure = cause
    builder = _BuilderStub()
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(creation_gate_controller=CreationGateController())

    with pytest.raises(RuntimeError, match="selected builder failed") as raised:
        factory.get_or_build_for_spell(spell)

    assert raised.value.__cause__ is cause
    assert builder.build_calls == []


def test_get_or_build_for_spell_waiting_follower_wakes_when_leader_fails(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A follower parked on the pending switch wakes and reports the failure instead of hanging."""
    spell = _SpellStub(creation_context=None, switch_state=0)
    leader_building = Event()
    fail_leader = Event()

    def _slow_failing_build(
            target: Any,
            *,
            dynamic_environment: bool = False,
            creation_gate: Optional[Any] = None,
            creation_gate_index_id: Optional[str] = None,
    ) -> Any:
        """Hold the leader inside the build until the test lets it fail."""
        _ = (target, dynamic_environment, creation_gate, creation_gate_index_id)
        leader_building.set()
        if not fail_leader.wait(timeout=5.0):
            raise TimeoutError("test did not release the leader")
        raise RuntimeError("leader build failed")

    monkeypatch.setattr(CreationContextBuilder, "build", _slow_failing_build)
    factory = CreationContextFactory(creation_gate_controller=CreationGateController())
    errors: dict[str, BaseException] = {}

    def _call(key: str) -> None:
        """Resolve on a worker thread and keep the raised error."""
        try:
            factory.get_or_build_for_spell(spell)
        except BaseException as error:
            errors[key] = error

    leader = Thread(target=_call, args=("leader",), name="leader")
    leader.start()
    assert leader_building.wait(timeout=5.0)
    assert spell._creation_context_switch.state == 1
    follower = Thread(target=_call, args=("follower",), name="follower")
    follower.start()
    fail_leader.set()
    leader.join(timeout=5.0)
    follower.join(timeout=5.0)
    assert not leader.is_alive()
    assert not follower.is_alive()
    assert str(errors["leader"]) == "leader build failed"
    assert isinstance(errors["follower"], RuntimeError)
    assert spell._creation_context_switch.state == 0


def test_get_or_build_for_spell_success_clears_recorded_failure(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A successful leader clears a failure recorded by an earlier build."""
    built_context = _ContextStub()
    spell = _SpellStub(creation_context=None, switch_state=0)
    spell._creation_context_failure = RuntimeError("earlier failure")
    _patch_creation_context_builder(monkeypatch, _BuilderStub(build_result=built_context))
    factory = CreationContextFactory(creation_gate_controller=CreationGateController())

    assert factory.get_or_build_for_spell(spell) is built_context
    assert spell._creation_context_failure is None
    assert spell._creation_context_switch.state == 2


def test_resolve_spell_index_gate_is_none_in_automatic_mode() -> None:
    """Automatic ownership has no spell-index gate."""
    spell = _SpellStub()
    factory = CreationContextFactory(creation_gate_controller=CreationGateController())

    assert factory.resolve_spell_index_gate(spell) is None


def test_resolve_spell_index_gate_returns_the_shared_gate_in_dynamic_mode() -> None:
    """Dynamic ownership returns the controller's gate for the spell's index, creating it once."""
    spell = _SpellStub()
    controller = CreationGateController()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )

    gate = factory.resolve_spell_index_gate(spell)

    assert gate is not None
    assert gate is controller.get_spell_index_gate(spell.spell_index.id)
    assert factory.resolve_spell_index_gate(spell) is gate
''')

# =============================================================== CreationContextRebuild (unit, new file)
create_file(rebuild_tests, '''"""Contract tests for CreationContextRebuild, the rare-path rebuild window (2026-09-26)."""
from threading import Event, RLock, Thread
from types import SimpleNamespace, TracebackType
from typing import Any, Optional, Self

import pytest

from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.creation_gate import CreationGate


class _FactoryStub:
    """Factory stub that publishes a context the way the real leader does."""

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def get_or_build_for_spell(self, spell: Any) -> Any:
        """Publish a fresh context and open the switch."""
        self.calls.append(spell)
        spell._creation_context = SimpleNamespace(built_for=spell.spell_id)
        spell._creation_context_switch.advance(2 - spell._creation_context_switch.state)
        return spell._creation_context


class _SpellStub:
    """Spell stub carrying the fields the rebuild window reads and writes."""

    def __init__(
            self,
            index_id: str,
            *,
            gate: Optional[CreationGate] = None,
            plan_present: bool = True,
            context: Any = None,
    ) -> None:
        self.spell_id = f"spell-{index_id}"
        self.spell_index = SimpleNamespace(id=index_id)
        self._creation_gate = gate if gate is not None else CreationGate()
        self._creation_context = context
        self._creation_context_failure: Optional[BaseException] = RuntimeError("stale failure")
        self._creation_context_switch = CounterSwitch(state=2 if context is not None else 0)
        self._creation_context_factory = _FactoryStub()
        self.is_existing_creation = False
        self._compiler_artifact = SimpleNamespace(
            _spell_codegen_creation=object() if plan_present else None,
        )
        self.resolution_required = False
        self.resolution_complete = True


class _RecordingLock:
    """RLock stand-in recording the order of acquisitions across gates."""

    def __init__(self, name: str, log: list[str]) -> None:
        self._name = name
        self._log = log
        self._inner = RLock()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Record then acquire."""
        self._log.append(self._name)
        return self._inner.acquire(blocking, timeout)

    def release(self) -> None:
        """Release the inner lock."""
        self._inner.release()

    def __enter__(self) -> Self:
        self._inner.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        _ = (exc_type, exc_value, traceback)
        self._inner.release()


def test_enter_waits_for_admitted_tickets_then_freezes_and_clears_failure() -> None:
    """Entering drains tickets already admitted, leaves the gate frozen and clears the old failure."""
    spell = _SpellStub("a")
    gate = spell._creation_gate
    gate.admit_ticket()
    entered = Event()
    window = CreationContextRebuild((spell,))

    def _enter() -> None:
        """Enter the window on a worker thread."""
        window.__enter__()
        entered.set()

    producer = Thread(target=_enter, name="producer")
    producer.start()
    try:
        assert not entered.wait(timeout=0.2)
        assert gate.enabled is False
    finally:
        gate.unregister_ticket()
    producer.join(timeout=5.0)
    assert entered.is_set()
    assert spell._creation_context_failure is None
    window.__exit__(None, None, None)
    assert gate.enabled is True


def test_exit_publishes_context_from_present_plan_before_reopening() -> None:
    """A successful window publishes the rebuilt context, then reopens the gate."""
    spell = _SpellStub("a")
    with CreationContextRebuild((spell,)):
        assert spell._creation_gate.enabled is False
    assert spell._creation_context_factory.calls == [spell]
    assert spell._creation_context.built_for == "spell-a"
    assert spell._creation_context_switch.state == 2
    assert spell._creation_gate.enabled is True


def test_exit_leaves_spell_without_plan_unpublished_and_resolution_flags_alone() -> None:
    """No plan means no publication; resolution flags are not rewritten by the window."""
    spell = _SpellStub("a", plan_present=False)
    with CreationContextRebuild((spell,)):
        pass
    assert spell._creation_context_factory.calls == []
    assert spell._creation_context is None
    assert spell.resolution_required is False
    assert spell.resolution_complete is True


def test_exit_keeps_context_the_window_did_not_reset() -> None:
    """A spell still holding a context is not rebuilt."""
    existing = object()
    spell = _SpellStub("a", context=existing)
    with CreationContextRebuild((spell,)):
        pass
    assert spell._creation_context is existing
    assert spell._creation_context_factory.calls == []


def test_failure_inside_window_records_cause_resets_switch_and_reopens() -> None:
    """A producer failure is recorded on unpublished spells, the switch idles and the gate reopens."""
    spell = _SpellStub("a")
    spell._creation_context_switch.advance(1)
    error = RuntimeError("phase failed")
    with pytest.raises(RuntimeError, match="phase failed"):
        with CreationContextRebuild((spell,)):
            raise error
    assert spell._creation_context_failure is error
    assert spell._creation_context_switch.state == 0
    assert spell._creation_gate.enabled is True


def test_gate_frozen_before_the_window_stays_frozen_after_it() -> None:
    """The window restores the prior posture: a gate it found disabled is not reopened."""
    gate = CreationGate(enabled=False)
    spell = _SpellStub("a", gate=gate)
    with CreationContextRebuild((spell,)):
        pass
    assert gate.enabled is False


def test_gate_transition_locks_taken_in_index_order_and_released() -> None:
    """Overlapping producers serialize on gate locks taken in stable index-id order."""
    log: list[str] = []
    spell_b = _SpellStub("b")
    spell_a = _SpellStub("a")
    spell_b._creation_gate._lock = _RecordingLock("b", log)
    spell_a._creation_gate._lock = _RecordingLock("a", log)
    with CreationContextRebuild((spell_b, spell_a)):
        pass
    assert log[:2] == ["a", "b"]
    released: list[bool] = []

    def _probe() -> None:
        """Acquire both gate locks from another thread without blocking."""
        for spell in (spell_a, spell_b):
            got = spell._creation_gate._lock.acquire(blocking=False)
            released.append(got)
            if got:
                spell._creation_gate._lock.release()

    worker = Thread(target=_probe)
    worker.start()
    worker.join(timeout=5.0)
    assert released == [True, True]


def test_drain_failure_on_entry_unwinds_and_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    """A drain failure releases the gate lock, restores posture and raises the original error."""
    spell = _SpellStub("a")
    gate = spell._creation_gate

    def _failing_drain(timeout: float = 30.0, interval: float = 0.1) -> None:
        """Simulate a drain timeout."""
        _ = (timeout, interval)
        raise RuntimeError("drain timed out")

    monkeypatch.setattr(gate, "close_and_drain", _failing_drain)
    with pytest.raises(RuntimeError, match="drain timed out"):
        with CreationContextRebuild((spell,)):
            pytest.fail("window body must not run")
    assert gate.enabled is True
    acquired: list[bool] = []
    worker = Thread(target=lambda: acquired.append(gate._lock.acquire(blocking=False)))
    worker.start()
    worker.join(timeout=5.0)
    assert acquired == [True]
''')

# =============================================================== Spell (unit)
replace_block(spell_tests,
'''    assert spell._dynamic_environment is True
    assert spell._creation_context_factory is not None''',
'''    assert spell._dynamic_environment is True
    assert spell._creation_context_factory is not None
    assert spell._creation_gate is gate.get_spell_index_gate(spell.spell_index.id)
    assert spell._creation_gate is not None


def test_configure_creation_context_factory_leaves_gate_unset_in_automatic_mode() -> None:
    """Automatic ownership has no spell-index gate, so meld doors keep the unticketed lane."""
    spell = _make_spell()
    spell._configure_creation_context_factory(
        dynamic_environment=False,
        creation_gate_controller=CreationGateController(),
    )

    assert spell._creation_gate is None
    assert spell._creation_context_failure is None


def test_cleanup_creation_context_factory_drops_borrowed_gate() -> None:
    """Dropping the factory drops the borrowed gate reference with it; the gate stays usable."""
    spell = _make_spell()
    controller = CreationGateController()
    spell._configure_creation_context_factory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )
    gate = spell._creation_gate

    spell._cleanup_creation_context_factory()

    assert spell._creation_gate is None
    assert gate is controller.get_spell_index_gate(spell.spell_index.id)
    gate.admit_ticket()
    gate.unregister_ticket()''')

# =============================================================== Component: in-flight reader is drained
replace_block(component,
'''from tests.mocks.spellbook.core_classes import BasicService''',
'''from tests.mocks.spellbook.core_classes import BasicService


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
                raise TimeoutError("Test did not release the blocked construction.")''')
append_block(component, '''

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
''')
