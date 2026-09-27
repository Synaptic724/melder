"""Apply the regression and contract tests for the CreationContext cold-path fix (2026-09-26).

Usage: python apply_tests.py <repo_root>

Unskips the two owner-deferred September regressions, makes the component regression
observe the new waiting point (the spell's cold build path), updates the factory tests to
the lock-based contract and adds targeted cold-path tests. Same exact, line-normalized
block replacement as apply_fix.py.
"""
import pathlib
import sys
from collections import Counter


def replace_block(path: pathlib.Path, old: str, new: str, count: int = 1) -> None:
    raw = path.read_bytes().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    norm = [line.rstrip("\r\n") for line in lines]
    old_lines = old.split("\n")
    n = len(old_lines)
    hits = [i for i in range(len(norm) - n + 1) if norm[i:i + n] == old_lines]
    if len(hits) != count:
        raise SystemExit(f"{path}: expected {count} match(es), found {len(hits)}:\n{old_lines[0]}")
    for i in reversed(hits):
        endings = Counter(lines[j][len(norm[j]):] for j in range(i, i + n))
        ending = endings.most_common(1)[0][0] or "\n"
        last_ending = lines[i + n - 1][len(norm[i + n - 1]):]
        new_lines = [text + ending for text in new.split("\n")]
        new_lines[-1] = new.split("\n")[-1] + last_ending
        lines[i:i + n] = new_lines
    path.write_bytes("".join(lines).encode("utf-8"))
    print(f"patched {path} ({count})")


root = pathlib.Path(sys.argv[1])
integration = root / "tests/integration/melder/conduit/test_conduit_integration_concurrency.py"
component = root / "tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py"
factory_tests = root / "tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py"
spell_tests = root / "tests/unit/melder/spellbook/test_spell.py"

# --- 1. Unskip the September regressions -------------------------------------------------
replace_block(integration,
'''@pytest.mark.skip(
    reason="Deferred by project owner for release; shared-context revalidation investigation remains open."
)
def test_conduit_cluster_concurrent_meld_two_clusters_isolated() -> None:''',
'''def test_conduit_cluster_concurrent_meld_two_clusters_isolated() -> None:''')
replace_block(component,
'''@pytest.mark.skip(
    reason="Deferred by project owner; shared-context rebuild investigation remains open."
)
def test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs(''',
'''def test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs(''')

# --- 2. Component regression: observe the cold build path --------------------------------
replace_block(component,
'''from melder.aether.conduit.conduit import Conduit''',
'''from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)''')
replace_block(component,
'''    Both callers use the real public meld path. Only scheduling boundaries are
    wrapped: the peer pauses after normal phase 5, and the owner reports either
    parking at the shared index gate or completion. No runtime fields, switch''',
'''    Both callers use the real public meld path. Only scheduling boundaries are
    wrapped: the peer pauses after normal phase 5, and the owner reports parking
    at the shared index gate, entering the spell's cold build path (where it
    waits on the spell lock the peer's rerun holds across phases 5-11), or
    completion. No runtime fields, switch''')
replace_block(component,
'''    original_phase5 = CompilerPhase5.run_local
    original_admit = CreationGate.admit_ticket''',
'''    original_phase5 = CompilerPhase5.run_local
    original_admit = CreationGate.admit_ticket
    original_get_or_build = CreationContextFactory.get_or_build_for_spell''')
replace_block(component,
'''    def resolve(key: str, conduit: Conduit) -> None:''',
'''    def observe_cold_path(
            factory: CreationContextFactory,
            target: Spell,
    ) -> CreationContext:
        """Report the owner entering the cold build path while the peer rerun holds the spell lock."""
        if target is spell and current_thread().name == "context-reader":
            reader_observed.set()
        return original_get_or_build(factory, target)

    def resolve(key: str, conduit: Conduit) -> None:''')
replace_block(component,
'''    monkeypatch.setattr(CreationGate, "admit_ticket", observe_admission)''',
'''    monkeypatch.setattr(CreationGate, "admit_ticket", observe_admission)
    monkeypatch.setattr(CreationContextFactory, "get_or_build_for_spell", observe_cold_path)''')
replace_block(component,
'''        writer.join(10.0)
        if reader_started:
            reader.join(10.0)''',
'''        writer.join(10.0)
        if reader_started:
            reader.join(10.0)


def test_owner_meld_rebuilds_context_when_open_switch_has_empty_slot(
        shared_runtime: tuple[Conduit, Conduit, Spell],
) -> None:
    """An open switch beside an empty context slot takes the cold path instead of failing.

    A reset clears the spell's context slot before it resets the switch, so a meld
    door can read an open switch and then an empty slot. The door must build through
    the spell's cold path rather than raise "Spell returned no live CreationContext."
    The peer's first meld reruns phases 5-11, so the spell holds a freshly compiled
    phase-11 plan whatever the creation cache held (a full cache hit publishes a
    context without one). The instant is then reproduced without threads by
    emptying the slot of the published context, which is cleaned when the test ends.
    """
    owner, peer, spell = shared_runtime
    first = peer.meld(spell_id=spell.spell_id)
    assert owner.meld(spell_id=spell.spell_id) is first
    displaced = spell._creation_context
    assert displaced is not None
    assert spell._creation_context_switch.state >= 2
    spell._creation_context = None
    try:
        again = owner.meld(spell_id=spell.spell_id)
        assert again is first
        rebuilt = spell._creation_context
        assert rebuilt is not None
        assert rebuilt is not displaced
        assert spell._creation_context_switch.state == 2
    finally:
        displaced.cleanup()''')

# --- 3. Factory unit tests ------------------------------------------------------------------
replace_block(factory_tests,
'''def test_init_requires_creation_gate_controller() -> None:''',
'''class _PublishingLock:
    """Spell-lock stub: another cold caller publishes while this one waits to enter."""

    def __init__(self, spell: Any, published: Any) -> None:
        self._spell = spell
        self._published = published

    def __enter__(self) -> Self:
        self._spell._creation_context = self._published
        self._spell._creation_context_switch.advance(2)
        return self

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        _ = exc_type
        _ = exc_value
        _ = traceback


class _RecordingLock:
    """Spell-lock stub recording whether it is held."""

    def __init__(self) -> None:
        self.held = False
        self.enter_count = 0

    def __enter__(self) -> Self:
        self.held = True
        self.enter_count += 1
        return self

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        _ = exc_type
        _ = exc_value
        _ = traceback
        self.held = False


def test_init_requires_creation_gate_controller() -> None:''')
replace_block(factory_tests,
'''    """Verify leader-path get-or-build publishes a new context and advances the latch."""''',
'''    """Verify the cold path publishes a new context and opens the switch to state 2."""''')
replace_block(factory_tests,
'''    assert spell._creation_context_switch.advance_calls == [1]''',
'''    assert spell._creation_context_switch.advance_calls == [2]''')
replace_block(factory_tests,
'''def test_get_or_build_for_spell_returns_cached_context_for_non_leader_non_open_state(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify non-leader selector outcomes return the current cached spell context."""
    cached_context = _ContextStub()
    spell = _SpellStub(creation_context=cached_context)
    spell._creation_context_switch = _SwitchStub(state=1, selector_return=0)
    builder = _BuilderStub(build_result=_ContextStub())
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    assert factory.get_or_build_for_spell(spell) is cached_context
    assert builder.build_calls == []''',
'''def test_get_or_build_for_spell_returns_context_published_while_waiting_for_lock(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify a queued cold caller returns the context the first builder published."""
    published_context = _ContextStub()
    spell = _SpellStub(creation_context=None)
    spell._lock = _PublishingLock(spell, published_context)
    staged: list[Any] = []
    spell._spellbook = SimpleNamespace(
        _spell_id_pool={},
        _emit_spell_cache=lambda owner_spell: staged.append(owner_spell) or True,
    )
    builder = _BuilderStub(build_result=_ContextStub())
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    assert factory.get_or_build_for_spell(spell) is published_context
    assert builder.build_calls == []
    assert staged == []


def test_get_or_build_for_spell_open_switch_with_empty_slot_builds(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify an open switch beside an empty slot (a reset in progress) takes the cold path."""
    built_context = _ContextStub()
    spell = _SpellStub(creation_context=None, switch_state=2)
    builder = _BuilderStub(build_result=built_context)
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    assert factory.get_or_build_for_spell(spell) is built_context
    assert spell._creation_context is built_context
    assert spell._creation_context_switch.state == 2
    assert len(builder.build_calls) == 1


def test_get_or_build_for_spell_failed_build_leaves_spell_unpublished(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify a failed cold build publishes nothing and the next caller can build."""
    spell = _SpellStub(creation_context=None, switch_state=0)

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

    monkeypatch.setattr(CreationContextBuilder, "build", _raise_build)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    with pytest.raises(RuntimeError, match="spell_codegen_creation"):
        factory.get_or_build_for_spell(spell)
    assert spell._creation_context is None
    assert spell._creation_context_switch.state == 0

    built_context = _ContextStub()
    _patch_creation_context_builder(monkeypatch, _BuilderStub(build_result=built_context))
    assert factory.get_or_build_for_spell(spell) is built_context
    assert spell._creation_context_switch.state == 2


def test_get_or_build_for_spell_cold_path_waits_for_spell_lock_before_building(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify the cold path builds only after it acquires the spell lock."""
    built_context = _ContextStub()
    spell = _SpellStub(creation_context=None)
    lock = _BlockingContextLock()
    spell._lock = lock
    builder = _BuilderStub(build_result=built_context)
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )
    results: list[Any] = []

    def _resolve() -> None:
        """Run the cold path on a worker thread."""
        results.append(factory.get_or_build_for_spell(spell))

    worker = Thread(target=_resolve, name="cold-path-worker")
    worker.start()
    try:
        assert lock.entered.wait(timeout=5.0)
        assert builder.build_calls == []
        assert spell._creation_context is None
    finally:
        lock.release.set()
        worker.join(timeout=5.0)
    assert not worker.is_alive()
    assert results == [built_context]


def test_get_or_build_for_spell_stages_cache_after_releasing_spell_lock(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify cache staging runs outside the spell lock; staging takes the spellbook lock."""
    built_context = _ContextStub()
    spell = _SpellStub(creation_context=None)
    lock = _RecordingLock()
    spell._lock = lock
    held_at_staging: list[bool] = []
    spell._spellbook = SimpleNamespace(
        _spell_id_pool={},
        _emit_spell_cache=lambda owner_spell: held_at_staging.append(lock.held) or True,
    )
    builder = _BuilderStub(build_result=built_context)
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    assert factory.get_or_build_for_spell(spell) is built_context
    assert lock.enter_count == 1
    assert held_at_staging == [False]''')

# --- 4. Spell unit test ---------------------------------------------------------------------
replace_block(spell_tests,
'''def test_spell_does_not_expose_local_phase_facades() -> None:''',
'''def test_get_or_build_creation_context_open_switch_with_empty_slot_uses_factory() -> None:
    """An open switch beside an empty slot (a reset in progress) goes to the factory, never returns None."""
    spell = _make_spell()
    spell._creation_context = None
    spell._creation_context_switch.advance(2)

    class _Factory:
        """Factory stub recording cold-path calls."""

        def __init__(self) -> None:
            self.calls: list[object] = []

        def get_or_build_for_spell(self, owner: object) -> str:
            self.calls.append(owner)
            return "built-context"

    factory = _Factory()
    spell._creation_context_factory = factory

    assert spell._get_or_build_creation_context() == "built-context"
    assert factory.calls == [spell]


def test_spell_does_not_expose_local_phase_facades() -> None:''')
