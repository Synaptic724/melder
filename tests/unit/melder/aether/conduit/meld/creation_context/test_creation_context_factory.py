"""Direct factory contract tests for CreationContextFactory."""
from threading import RLock
from types import SimpleNamespace
from typing import Any, Optional

import pytest

from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)


class _ContextStub:
    """Simple context stub with cleanup tracking."""

    def __init__(self) -> None:
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        self.cleanup_calls += 1


class _BuilderStub:
    """Minimal builder stub for factory tests."""

    def __init__(self, *, build_result: Any = None, cleanup_error: Optional[Exception] = None) -> None:
        self.build_result = build_result
        self.cleanup_error = cleanup_error
        self.build_calls: list[dict[str, Any]] = []
        self.cleanup_calls = 0

    def build(
            self,
            spell: Any,
            *,
            dynamic_environment: bool = False,
            creation_gate: Optional[Any] = None,
            creation_gate_index_id: Optional[str] = None,
    ) -> Any:
        self.build_calls.append(
            {
                "spell": spell,
                "dynamic_environment": dynamic_environment,
                "creation_gate": creation_gate,
                "creation_gate_index_id": creation_gate_index_id,
            }
        )
        if self.build_result is None:
            return SimpleNamespace(_spell=spell)
        return self.build_result

    def cleanup(self) -> None:
        self.cleanup_calls += 1
        if self.cleanup_error is not None:
            raise self.cleanup_error


def _patch_creation_context_builder(
        monkeypatch: pytest.MonkeyPatch,
        builder: _BuilderStub,
) -> None:
    def _build(
            spell: Any,
            *,
            dynamic_environment: bool = False,
            creation_gate: Optional[Any] = None,
            creation_gate_index_id: Optional[str] = None,
    ) -> Any:
        return builder.build(
            spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
        )

    monkeypatch.setattr(CreationContextBuilder, "build", _build)


class _SpellStub:
    """Minimal spell stub exposing the contract used by factory tests."""

    def __init__(
            self,
            *,
            spell_id: str = "spell-1",
            creation_context: Optional[Any] = None,
            switch_state: int = 0,
    ) -> None:
        self.spell_id = spell_id
        self.spell_name = spell_id
        self.spell_index = SimpleNamespace(current=spell_id, id=f"index-{spell_id}")
        self.existence = Existence.unique
        self.is_existing_creation = False
        self.user_created_object = None
        self.execution_plan_dispatch_route = None
        self._owner_creations = SimpleNamespace(_creations={}, _lock=RLock())
        self._spellbook = SimpleNamespace(_spell_id_pool={})
        self._crafter = object()
        self._creation_context = creation_context
        self._creation_context_switch = CounterSwitch(state=switch_state)
        self._lock = RLock()


class _SwitchStub:
    """Minimal switch stub exposing the factory contract surface."""

    def __init__(self, *, state: int, selector_return: int) -> None:
        self.state = state
        self._selector_return = selector_return
        self.advance_calls: list[int] = []

    def selector(self) -> int:
        return self._selector_return

    def advance(self, amount: int) -> None:
        self.advance_calls.append(amount)
        self.state += amount


def test_init_requires_creation_gate_controller() -> None:
    """Verify factory rejects a missing CreationGateController."""
    with pytest.raises(ValueError, match="creation_gate_controller cannot be None"):
        CreationContextFactory(creation_gate_controller=None)  # type: ignore[arg-type]


def test_cleanup_creation_context_helper_noops_on_none_and_swallows_errors() -> None:
    """Verify detached-context cleanup helper is best-effort."""
    CreationContextFactory._cleanup_creation_context(None)

    context = _ContextStub()
    CreationContextFactory._cleanup_creation_context(context)
    assert context.cleanup_calls == 1

    class _FailingContext:
        def cleanup(self) -> None:
            raise RuntimeError("boom")

    CreationContextFactory._cleanup_creation_context(_FailingContext())


def test_resolve_or_create_spell_index_gate_reuses_existing_gate() -> None:
    """Verify factory reuses existing spell-index gates instead of recreating them."""
    controller = CreationGateController()
    existing_gate = controller.create_spell_index_gate("index-1")
    factory = CreationContextFactory(creation_gate_controller=controller)

    resolved = factory._resolve_or_create_spell_index_gate("index-1")

    assert resolved is existing_gate
    assert factory._created_spell_index_ids == set()


def test_resolve_or_create_spell_index_gate_creates_new_gate_and_tracks_id() -> None:
    """Verify factory creates and tracks a new spell-index gate when one is missing."""
    controller = CreationGateController()
    factory = CreationContextFactory(creation_gate_controller=controller)

    resolved = factory._resolve_or_create_spell_index_gate("index-2")

    assert resolved is controller.get_spell_index_gate("index-2")
    assert factory._created_spell_index_ids == {"index-2"}


def test_resolve_runtime_gate_for_spell_returns_none_in_automatic_mode() -> None:
    """Verify automatic mode does not inject runtime gate metadata."""
    spell = _SpellStub()
    factory = CreationContextFactory(
        dynamic_environment=False,
        creation_gate_controller=CreationGateController(),
    )

    assert factory._resolve_runtime_gate_for_spell(spell) == (None, None)


def test_resolve_runtime_gate_for_spell_dynamic_returns_gate_and_index_id() -> None:
    """Verify dynamic mode resolves and returns shared spell-index gate metadata."""
    spell = _SpellStub(spell_id="spell-dynamic")
    controller = CreationGateController()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )

    gate, index_id = factory._resolve_runtime_gate_for_spell(spell)

    assert index_id == spell.spell_index.id
    assert gate is controller.get_spell_index_gate(index_id)
    assert factory._created_spell_index_ids == {index_id}


def test_build_for_spell_passes_dynamic_gate_metadata_to_builder(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify build_for_spell forwards dynamic gate metadata into the builder."""
    spell = _SpellStub(spell_id="spell-build")
    builder = _BuilderStub(build_result="built-context")
    _patch_creation_context_builder(monkeypatch, builder)
    controller = CreationGateController()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )

    result = factory.build_for_spell(spell)

    assert result == "built-context"
    assert builder.build_calls[0]["spell"] is spell
    assert builder.build_calls[0]["dynamic_environment"] is True
    assert builder.build_calls[0]["creation_gate_index_id"] == spell.spell_index.id
    assert builder.build_calls[0]["creation_gate"] is controller.get_spell_index_gate(spell.spell_index.id)


def test_get_or_build_for_spell_returns_cached_context_for_follower_path(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify follower-path get-or-build returns the already published context."""
    cached_context = _ContextStub()
    spell = _SpellStub(creation_context=cached_context, switch_state=2)
    builder = _BuilderStub(build_result=_ContextStub())
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    assert factory.get_or_build_for_spell(spell) is cached_context
    assert builder.build_calls == []


def test_get_or_build_for_spell_builds_and_advances_switch_for_leader_path(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify leader-path get-or-build publishes a new context and advances the latch."""
    built_context = _ContextStub()
    spell = _SpellStub(creation_context=None)
    spell._creation_context_switch = _SwitchStub(state=0, selector_return=1)
    builder = _BuilderStub(build_result=built_context)
    _patch_creation_context_builder(monkeypatch, builder)
    controller = CreationGateController()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )

    result = factory.get_or_build_for_spell(spell)

    assert result is built_context
    assert spell._creation_context is built_context
    assert spell._creation_context_switch.advance_calls == [1]
    assert builder.build_calls[0]["creation_gate_index_id"] == spell.spell_index.id


def test_get_or_build_for_spell_returns_cached_context_for_non_leader_non_open_state(
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
    assert builder.build_calls == []


@pytest.mark.parametrize(("start_state", "expected_state"), [(0, 2), (5, 2)])
def test_set_creation_context_switch_open_normalizes_state(
        start_state: int,
        expected_state: int,
) -> None:
    """Verify switch-open normalization drives the CounterSwitch state to 2."""
    spell = _SpellStub(switch_state=start_state)

    CreationContextFactory._set_creation_context_switch_open(spell)

    assert spell._creation_context_switch.state == expected_state


def test_rebuild_for_spell_delegates_to_build_and_bind(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify rebuild simply delegates to build-and-bind for the target spell."""
    spell = _SpellStub()
    builder = _BuilderStub(build_result="rebuilt")
    _patch_creation_context_builder(monkeypatch, builder)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )

    result = factory.rebuild_for_spell(spell)

    assert result == "rebuilt"
    assert builder.build_calls[0]["spell"] is spell


def test_index_id_for_spell_returns_spell_index_id() -> None:
    """Verify spell-index-id helper returns the stable SpellIndex id."""
    spell = _SpellStub(spell_id="spell-index")
    factory = CreationContextFactory(creation_gate_controller=CreationGateController())
    try:
        assert factory._index_id_for_spell(spell) == spell.spell_index.id
    finally:
        factory.cleanup()

