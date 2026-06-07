"""Focused spell-owned creation-context factory tests."""

import threading
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
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class _CleanupProbe:
    """Minimal cleanup double for replaced creation-context objects."""

    def __init__(self) -> None:
        self.cleanup_called = False

    def cleanup(self) -> None:
        self.cleanup_called = True


class _CounterSwitchStub:
    """Minimal CounterSwitch double for factory publication tests."""

    def __init__(self, state: int = 0) -> None:
        self.state = state

    def selector(self) -> int:
        if self.state == 0:
            self.state = 1
            return 1
        return self.state

    def advance(self, delta: int) -> None:
        self.state += delta

    def cleanup(self) -> None:
        return None


class _CreationGateStub:
    """Minimal spell-index creation gate for dynamic execution tests."""

    def __init__(self) -> None:
        self.enabled = True
        self.closed = False
        self.register_calls = 0
        self.unregister_calls = 0
        self.wait_calls = 0

    def is_closed(self) -> bool:
        return self.closed

    def wait(self) -> None:
        self.wait_calls += 1

    def register_ticket(self) -> None:
        self.register_calls += 1

    def unregister_ticket(self) -> None:
        self.unregister_calls += 1


class _CreationGateControllerStub:
    """Minimal creation-gate controller for factory tests."""

    def __init__(self) -> None:
        self.gates = {}

    def get_spell_index_gate(self, index_id: str):
        return self.gates.get(index_id)

    def create_spell_index_gate(self, index_id: str):
        gate = _CreationGateStub()
        self.gates[index_id] = gate
        return gate


def _make_codegen_creation() -> object:
    """Build the minimal codegen-creation payload consumed by CreationContextBuilder."""
    return SimpleNamespace(
        no_overrides_executor=(
            lambda caller_creations, owner_creations=None, caller_creations_lock_held=False: "value"
        ),
        overrides_executor=(
            lambda caller_creations, overrides, caller_creations_lock_held=False: "value"
        ),
        metadata={
            "resolve_route_key": "many",
        },
    )


def _make_spell(
        spell_id: str = "root",
        *,
        is_existing_creation: bool = False,
        user_created_object: Any = None,
        has_codegen_creation: bool = True,
) -> object:
    """Build the minimal spell surface needed by creation-context factory tests."""
    artifact = SpellCompilerArtifact(spell_id)
    if has_codegen_creation:
        artifact._spell_codegen_creation = _make_codegen_creation()
    spell = SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SimpleNamespace(current=spell_id, id="lineage:{0}".format(spell_id)),
        spell=lambda *args, **kwargs: "value:{0}".format(spell_id),
        existence=Existence.many,
        is_existing_creation=is_existing_creation,
        is_class_spell=not is_existing_creation,
        is_method_spell=False,
        is_lambda_spell=False,
        user_created_object=user_created_object,
        _owner_creations=SimpleNamespace(),
        _compiler_artifact=artifact,
        _creation_context=None,
        _creation_context_factory=None,
        _creation_context_switch=_CounterSwitchStub(),
        _lock=threading.RLock(),
    )
    return spell


def test_creation_context_factory_get_or_build_builds_once_and_reuses_cached_context(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Factory get-or-build should elect one builder, publish once, and reuse the cached spell-owned context."""
    build_calls = []

    def _fake_build(
            spell,
            *,
            dynamic_environment: bool = False,
            creation_gate=None,
            creation_gate_index_id=None,
    ):
        build_calls.append(
            (
                spell,
                dynamic_environment,
                creation_gate,
                creation_gate_index_id,
            )
        )
        return SimpleNamespace(kind="context-{0}".format(len(build_calls)))

    monkeypatch.setattr(
        CreationContextBuilder,
        "build",
        staticmethod(_fake_build),
    )

    controller = _CreationGateControllerStub()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )
    spell = _make_spell()

    first = factory.get_or_build_for_spell(spell)
    second = factory.get_or_build_for_spell(spell)

    assert first is second
    assert spell._creation_context is first
    assert spell._creation_context_switch.state == 2
    assert len(build_calls) == 1
    assert build_calls[0][1] is True
    assert build_calls[0][3] == "lineage:root"
    assert controller.gates["lineage:root"] is build_calls[0][2]


def test_creation_context_factory_build_and_bind_cleans_previous_context_and_opens_switch(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Factory build-and-bind should replace the spell-owned context and cleanup the superseded one."""
    built_context = SimpleNamespace(kind="built")
    monkeypatch.setattr(
        CreationContextBuilder,
        "build",
        staticmethod(lambda *args, **kwargs: built_context),
    )

    controller = _CreationGateControllerStub()
    factory = CreationContextFactory(
        dynamic_environment=False,
        creation_gate_controller=controller,
    )
    spell = _make_spell()
    previous_context = _CleanupProbe()
    spell._creation_context = previous_context
    spell._creation_context_switch = _CounterSwitchStub(state=1)

    result = factory.build_and_bind_for_spell(spell)

    assert result is built_context
    assert spell._creation_context is built_context
    assert previous_context.cleanup_called is True
    assert spell._creation_context_switch.state == 2


def test_creation_context_factory_resolves_dynamic_gate_metadata() -> None:
    """Dynamic mode should resolve and attach spell-index gate metadata through the factory."""
    spell = _make_spell(spell_id="spell-dynamic")
    controller = _CreationGateControllerStub()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )

    gate, index_id = factory._resolve_runtime_gate_for_spell(spell)

    assert index_id == spell.spell_index.id
    assert gate is controller.get_spell_index_gate(index_id)
    assert gate is not None
    assert factory._created_spell_index_ids == {index_id}


def test_creation_context_factory_allows_existing_creation_without_codegen_creation() -> None:
    """Existing-creation spells should still build through the factory without codegen creation."""
    spell = _make_spell(
        is_existing_creation=True,
        user_created_object="existing-root",
        has_codegen_creation=False,
    )
    factory = CreationContextFactory(
        creation_gate_controller=_CreationGateControllerStub(),
    )

    context = factory.build_for_spell(spell)

    assert context.execute_no_hooks(object()) == "existing-root"


def test_set_creation_context_switch_open_normalizes_state() -> None:
    """Switch normalization should always force the spell-owned latch to state 2."""
    spell = _make_spell()
    spell._creation_context_switch = _CounterSwitchStub(state=0)

    CreationContextFactory._set_creation_context_switch_open(spell)

    assert spell._creation_context_switch.state == 2
