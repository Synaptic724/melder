"""Unit tests for spell-owned creation-context builder, factory, and runtime helpers."""

import threading
from types import SimpleNamespace

import pytest

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
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
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)


class _CleanupProbe:
    """Minimal cleanup double for replaced creation-context objects."""

    def __init__(self) -> None:
        """Start with cleanup not yet called."""
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True


class _CounterSwitchStub:
    """Minimal CounterSwitch double for factory publication tests."""

    def __init__(self, state: int = 0) -> None:
        """Store the current latch state."""
        self.state = state

    def selector(self) -> int:
        """Elect the first builder and return the current switch state."""
        if self.state == 0:
            self.state = 1
            return 1
        return self.state

    def advance(self, delta: int) -> None:
        """Move the latch state by the requested delta."""
        self.state += delta

    def cleanup(self) -> None:
        """Satisfy the spell cleanup contract without extra behavior."""
        return None


class _CreationGateStub:
    """Minimal spell-index creation gate for dynamic execution tests."""

    def __init__(self) -> None:
        """Start enabled and open with zero active tickets."""
        self.enabled = True
        self.closed = False
        self.register_calls = 0
        self.unregister_calls = 0
        self.wait_calls = 0

    def is_closed(self) -> bool:
        """Return whether the gate is terminally closed."""
        return self.closed

    def wait(self) -> None:
        """Record one wait call."""
        self.wait_calls += 1

    def register_ticket(self) -> None:
        """Record one in-flight ticket registration."""
        self.register_calls += 1

    def unregister_ticket(self) -> None:
        """Record one in-flight ticket release."""
        self.unregister_calls += 1


class _CreationGateControllerStub:
    """Minimal creation-gate controller for factory tests."""

    def __init__(self) -> None:
        """Start with no registered spell-index gates."""
        self.gates = {}

    def get_spell_index_gate(self, index_id: str):
        """Return an existing spell-index gate when one is already registered."""
        return self.gates.get(index_id)

    def create_spell_index_gate(self, index_id: str):
        """Create and store one spell-index gate."""
        gate = _CreationGateStub()
        self.gates[index_id] = gate
        return gate


class _OverrideSocketRef:
    """Hashable override-target probe for creation-context helper tests."""

    def __init__(
            self,
            node_id: str,
            param_name: str,
            param_path_id: int,
            socket_kind_value: int = 0,
    ) -> None:
        """Store stable socket-target metadata."""
        self.node_id = node_id
        self.param_name = param_name
        self.param_path_id = param_path_id
        self.socket_kind_value = socket_kind_value

    def __hash__(self) -> int:
        """Keep the probe usable as a dictionary key."""
        return hash(
            (
                self.node_id,
                self.param_name,
                self.param_path_id,
                self.socket_kind_value,
            )
        )


def _make_codegen_creation(
        *,
        resolve_route_key: str = "many",
        no_overrides_executor=None,
        fast_transient_no_overrides_enabled: bool = False,
) -> object:
    """Build the minimal codegen-creation payload consumed by CreationContextBuilder."""
    if no_overrides_executor is None:
        no_overrides_executor = lambda *args, **kwargs: "value"
    return SimpleNamespace(
        resolve_route_key=resolve_route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        no_overrides_executor=no_overrides_executor,
        override_targeting=None,
        override_no_mutation_plan_signature=None,
        override_no_mutation_path_registry=None,
        override_no_mutation_plan_rows=None,
        override_no_mutation_root_spell_id=None,
        override_no_mutation_spell_lookup=None,
        override_no_mutation_empty_shape_key=None,
        override_no_mutation_baseline_executor=None,
        override_mutation_plan_signature=None,
        override_mutation_path_registry=None,
        override_mutation_plan_rows=None,
        override_mutation_root_spell_id=None,
        override_mutation_spell_lookup=None,
        override_mutation_empty_shape_key=None,
        override_mutation_baseline_executor=None,
    )


def _make_spell(
        spell_id: str = "root",
        *,
        is_existing_creation: bool = False,
        user_created_object=None,
        resolve_route_key: str = "many",
        has_codegen_creation: bool = True,
        has_mutation_override: bool = False,
) -> object:
    """Build the minimal spell surface needed by creation-context tests."""
    artifact = SpellCompilerArtifact(spell_id)
    if has_codegen_creation:
        artifact._spell_codegen_creation = _make_codegen_creation(
            resolve_route_key=resolve_route_key,
        )
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
        has_mutation_override=has_mutation_override,
        _creation_context=None,
        _creation_context_factory=None,
        _creation_context_switch=_CounterSwitchStub(),
        _lock=threading.RLock(),
    )
    return spell


def test_creation_context_builder_requires_codegen_creation_for_constructed_spells() -> None:
    """Constructed spells should require a populated codegen-creation artifact before context build."""
    spell = _make_spell(has_codegen_creation=False)

    with pytest.raises(
            RuntimeError,
            match="spell_codegen_creation exists",
    ):
        CreationContextBuilder.build(spell)


def test_creation_context_builder_allows_existing_creation_route_without_codegen_creation() -> None:
    """Existing-creation spells should still build a spell-owned runtime context without codegen creation."""
    spell = _make_spell(
        is_existing_creation=True,
        user_created_object="existing-root",
        has_codegen_creation=False,
    )
    caller_creations = SimpleNamespace(_lock=threading.RLock())

    context = CreationContextBuilder.build(spell)

    assert context.execute_no_hooks(caller_creations) == "existing-root"


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
    """Factory build-and-bind should replace the spell-owned context, cleanup the superseded one, and normalize the latch to open state."""
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


def test_creation_context_execute_dynamic_mode_registers_and_unregisters_gate_ticket() -> None:
    """Dynamic execution should route through the spell-index gate around the compiled no-overrides lane."""
    spell = _make_spell(resolve_route_key="many")
    gate = _CreationGateStub()
    context = CreationContextBuilder.build(
        spell,
        dynamic_environment=True,
        creation_gate=gate,
        creation_gate_index_id="lineage:root",
    )
    context._execute_hooks_no_overrides_compiled = lambda caller_creations: (
        "created",
        True,
    )

    result = context.execute(SimpleNamespace(_lock=threading.RLock()))

    assert result == ("created", True)
    assert gate.register_calls == 1
    assert gate.unregister_calls == 1


def test_creation_context_split_override_payload_normalizes_root_args_and_rejects_invalid_shapes() -> None:
    """Creation-context override splitting should normalize list payloads to tuples and reject invalid `__args__` shapes."""
    spell = _make_spell(resolve_route_key="many")
    context = CreationContextBuilder.build(spell)

    targeted_payload, root_args = context._split_override_payload(
        spell=spell,
        override_payload={"__args__": [1, 2], "value": "override"},
    )

    assert targeted_payload == {"value": "override"}
    assert root_args == (1, 2)

    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        context._split_override_payload(
            spell=spell,
            override_payload={"__args__": "bad"},
        )


def test_creation_context_override_shape_helpers_cache_and_group_targets_by_spell_id() -> None:
    """Creation-context override helpers should reuse cached shape tuples and group socket refs by target spell id."""
    spell = _make_spell(resolve_route_key="many")
    context = CreationContextBuilder.build(spell)
    first_socket_ref = _OverrideSocketRef("root", "value_a", 7)
    second_socket_ref = _OverrideSocketRef("root", "value_b", 8)
    third_socket_ref = _OverrideSocketRef("dep", "value_c", 9)
    override_map = {
        first_socket_ref: "override-a",
        second_socket_ref: "override-b",
        third_socket_ref: "override-c",
    }

    first_shape = context._collect_override_socket_shape_cached(
        override_map=override_map,
    )
    second_shape = context._collect_override_socket_shape_cached(
        override_map=override_map,
    )
    grouped_targets = context._collect_override_targets_from_socket_shape(
        override_map=override_map,
        socket_shape=first_shape,
    )

    assert first_shape is second_shape
    assert first_shape == (
        ("dep", 9, "value_c", 0),
        ("root", 7, "value_a", 0),
        ("root", 8, "value_b", 0),
    )
    assert grouped_targets == {
        "dep": (third_socket_ref,),
        "root": (first_socket_ref, second_socket_ref),
    }
