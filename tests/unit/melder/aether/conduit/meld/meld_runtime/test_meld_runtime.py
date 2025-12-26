"""Contract tests for MeldRuntime execution orchestration."""
from types import SimpleNamespace
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

import melder.aether.conduit.meld.meld_runtime.meld_runtime as runtime_module
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class _SystemStateStub:
    """
    Minimal system-state stub exposing a validity attribute.
    """

    def __init__(self, validity: SpellValidity) -> None:
        """
        Initialize the stub with a specific validity value.

        Args:
            validity: The SpellValidity to expose.
        """
        self.validity = validity


class _ChangeControlManagerStub:
    """
    Minimal change-control manager stub for dirty-root checks.
    """

    def __init__(self, *, is_dirty: bool, raise_on_call: bool = False) -> None:
        """
        Initialize with a fixed dirty flag and optional error behavior.

        Args:
            is_dirty: Whether the root should be reported as dirty.
            raise_on_call: Whether is_root_dirty should raise.
        """
        self._is_dirty = is_dirty
        self._raise_on_call = raise_on_call

    def is_root_dirty(self, root_id: str) -> bool:
        """
        Return whether the root is dirty or raise if configured.
        """
        if self._raise_on_call:
            raise RuntimeError("change-control failure")
        return self._is_dirty


class _AetherStub:
    """
    Minimal aether stub exposing change-control manager lookup.
    """

    def __init__(self, manager: Any, *, raise_on_call: bool = False) -> None:
        """
        Initialize with a manager to return or a failure mode.

        Args:
            manager: Change-control manager stub to return.
            raise_on_call: Whether the lookup should raise.
        """
        self._manager = manager
        self._raise_on_call = raise_on_call

    def _get_change_control_manager(self, frame: str) -> Any:
        """
        Return the configured manager or raise if configured.
        """
        if self._raise_on_call:
            raise RuntimeError("change-control lookup failed")
        return self._manager


class _SpellbookStub:
    """
    Spellbook stub exposing spell registries and optional aether.
    """

    def __init__(
        self,
        *,
        spells: Dict[SpellIndex, Any],
        contracted_spells: Optional[Dict[str, Dict[SpellIndex, Any]]] = None,
        aether: Any = None,
    ) -> None:
        """
        Initialize the spellbook stub with registries and aether.

        Args:
            spells: Mapping of SpellIndex to spell instance.
            contracted_spells: Optional lineage -> SpellIndex -> spell mapping.
            aether: Optional aether stub.
        """
        self._spells = spells
        self._contracted_spells = contracted_spells or {}
        self._aether = aether


class _SpellStub:
    """
    Spell stub exposing the fields used by MeldRuntime.execute.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: Optional[str] = None,
        aetheric_frame: str = "default",
        system_state: Any = None,
        system_state_error: Optional[Exception] = None,
        mutation_override: Any = None,
        mutation_override_error: Optional[Exception] = None,
        is_broken: bool = False,
        validated: bool = True,
        dependency_graph: Any = None,
        requirements: Any = None,
        resolution_frame: Any = None,
        crafter: Any = None,
        spellbook: Any = None,
        spell_system_states: Any = None,
        is_class_spell: bool = True,
        is_method_spell: bool = False,
        is_lambda_spell: bool = False,
    ) -> None:
        """
        Initialize the spell stub with explicit runtime attributes.

        Args:
            spell_id: Spell version identifier.
            spell_name: Optional human-readable name.
            aetheric_frame: Frame name used for change-control lookup.
            system_state: Optional system-state object.
            system_state_error: Optional exception for system_state access.
            mutation_override: Optional mutation override payload.
            mutation_override_error: Optional exception for mutation_override access.
            is_broken: Whether the spell is marked broken.
            validated: Whether the spell has been validated.
            dependency_graph: Optional DAG artifact.
            requirements: Optional requirements artifact.
            resolution_frame: Optional resolution frame artifact.
            crafter: Optional crafter object with root blueprint.
            spellbook: Optional spellbook stub for lookup building.
            spell_system_states: Optional system states registry.
            is_class_spell: Whether the spell is a class factory.
            is_method_spell: Whether the spell is a method factory.
            is_lambda_spell: Whether the spell is a lambda factory.
        """
        self.spell_index = SpellIndex(spell_id)
        self.spell_name = spell_name or spell_id
        self.aetheric_frame = aetheric_frame
        self._system_state = system_state
        self._system_state_error = system_state_error
        self._mutation_override = mutation_override
        self._mutation_override_error = mutation_override_error
        self.is_broken = is_broken
        self.validated = validated
        self.dependency_graph = dependency_graph
        self.requirements = requirements
        self.resolution_frame = resolution_frame
        self._crafter = crafter
        self._spellbook = spellbook
        self._spell_system_states = spell_system_states
        self.is_class_spell = is_class_spell
        self.is_method_spell = is_method_spell
        self.is_lambda_spell = is_lambda_spell

    @property
    def system_state(self) -> Any:
        """
        Return the configured system state or raise if configured.
        """
        if self._system_state_error is not None:
            raise self._system_state_error
        return self._system_state

    @property
    def mutation_override(self) -> Any:
        """
        Return the configured mutation override or raise if configured.
        """
        if self._mutation_override_error is not None:
            raise self._mutation_override_error
        return self._mutation_override


def _make_context(spell: Any, overrides: Any = None) -> SimpleNamespace:
    """
    Build a minimal MeldContext-like stub.

    Args:
        spell: Root spell to expose via context.root_spell.
        overrides: Optional overrides payload for the context.

    Returns:
        SimpleNamespace: Context stub with root_spell and overrides.
    """
    return SimpleNamespace(root_spell=spell, overrides=overrides)


def _make_socket_ref(node_id: str, param_name: str, param_path: tuple[str, ...]) -> SocketRef:
    """
    Build a SocketRef for override-map tests.

    Args:
        node_id: Spell id for the socket.
        param_name: Constructor parameter name.
        param_path: Param path tuple for targeting.

    Returns:
        SocketRef: Socket reference for override targeting.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=param_path,
        socket_kind=SocketKind.NORMAL,
    )


def _install_engine_mock(
    monkeypatch: pytest.MonkeyPatch,
    *,
    run_result: Any = None,
    run_error: Optional[Exception] = None,
) -> tuple[MagicMock, MagicMock]:
    """
    Patch MeldEngine to a MagicMock instance with controlled behavior.

    Args:
        monkeypatch: pytest monkeypatch fixture.
        run_result: Value to return from engine.run when no error is set.
        run_error: Optional exception to raise from engine.run.

    Returns:
        Tuple[MagicMock, MagicMock]: (engine class mock, engine instance mock).
    """
    engine_instance = MagicMock()
    if run_error is not None:
        engine_instance.run.side_effect = run_error
    else:
        engine_instance.run.return_value = run_result
    engine_cls = MagicMock(return_value=engine_instance)
    monkeypatch.setattr(runtime_module, "MeldEngine", engine_cls)
    return engine_cls, engine_instance


def _install_frame_mock(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[MagicMock, MagicMock]:
    """
    Patch ResolutionFrame to a MagicMock instance for override capture.

    Args:
        monkeypatch: pytest monkeypatch fixture.

    Returns:
        Tuple[MagicMock, MagicMock]: (frame class mock, frame instance mock).
    """
    frame_instance = MagicMock()
    frame_cls = MagicMock(return_value=frame_instance)
    monkeypatch.setattr(runtime_module, "ResolutionFrame", frame_cls)
    return frame_cls, frame_instance


def test_execute_rejects_none_context() -> None:
    """
    Verify execute rejects a None context.

    Contract:
        - context must not be None.
    """
    runtime = MeldRuntime()
    with pytest.raises(ValueError, match="context cannot be None"):
        runtime.execute(None)


def test_execute_rejects_none_root_spell() -> None:
    """
    Verify execute rejects a context with no root spell.

    Contract:
        - context.root_spell must not be None.
    """
    runtime = MeldRuntime()
    context = _make_context(spell=None)
    with pytest.raises(ValueError, match="context.root_spell cannot be None"):
        runtime.execute(context)


def test_execute_after_cleanup_raises_runtimeerror() -> None:
    """
    Verify execute fails after the runtime is cleaned.

    Contract:
        - execute raises RuntimeError once cleaned.
    """
    runtime = MeldRuntime()
    runtime.cleanup()
    context = _make_context(spell=_SpellStub(spell_id="spell-1"))
    with pytest.raises(RuntimeError, match="already been cleaned"):
        runtime.execute(context)


@pytest.mark.parametrize(
    "validity",
    [SpellValidity.invalid, SpellValidity.gated, SpellValidity.disabled],
)
def test_execute_blocks_invalid_system_state(validity: SpellValidity) -> None:
    """
    Verify invalid/gated/disabled system states block execution.

    Contract:
        - invalid/gated/disabled validity raises MeldExecutionError.
    """
    runtime = MeldRuntime()
    system_state = _SystemStateStub(validity)
    spell = _SpellStub(spell_id="spell-1", system_state=system_state)
    context = _make_context(spell=spell)
    with pytest.raises(MeldExecutionError, match=validity.name):
        runtime.execute(context)


def test_execute_ignores_system_state_access_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify system_state access errors do not block execution.

    Contract:
        - exceptions reading system_state are ignored.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(
        spell_id="spell-1",
        system_state_error=RuntimeError("system-state failure"),
    )
    context = _make_context(spell=spell)
    engine_cls, engine_instance = _install_engine_mock(monkeypatch, run_result="ok")
    assert runtime.execute(context) == "ok"
    engine_cls.assert_called_once()
    engine_instance.run.assert_called_once()


def test_execute_blocks_dirty_root() -> None:
    """
    Verify dirty-root gating blocks execution.

    Contract:
        - dirty root raises MeldExecutionError.
    """
    runtime = MeldRuntime()
    manager = _ChangeControlManagerStub(is_dirty=True)
    aether = _AetherStub(manager)
    spellbook = _SpellbookStub(spells={}, aether=aether)
    spell = _SpellStub(spell_id="spell-1", spellbook=spellbook)
    context = _make_context(spell=spell)
    with pytest.raises(MeldExecutionError, match="root is marked dirty"):
        runtime.execute(context)


def test_execute_ignores_change_control_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify change-control lookup errors are ignored.

    Contract:
        - errors in change-control lookup allow execution to proceed.
    """
    runtime = MeldRuntime()
    aether = _AetherStub(manager=None, raise_on_call=True)
    spellbook = _SpellbookStub(spells={}, aether=aether)
    spell = _SpellStub(spell_id="spell-1", spellbook=spellbook)
    context = _make_context(spell=spell)
    engine_cls, engine_instance = _install_engine_mock(monkeypatch, run_result="ok")
    assert runtime.execute(context) == "ok"
    engine_cls.assert_called_once()
    engine_instance.run.assert_called_once()


def test_execute_blocks_broken_spell() -> None:
    """
    Verify broken spells are rejected.

    Contract:
        - is_broken True raises MeldExecutionError.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1", is_broken=True)
    context = _make_context(spell=spell)
    with pytest.raises(MeldExecutionError, match="broken spell"):
        runtime.execute(context)


def test_execute_blocks_unvalidated_spell() -> None:
    """
    Verify unvalidated spells are rejected.

    Contract:
        - validated False raises MeldExecutionError.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1", validated=False)
    context = _make_context(spell=spell)
    with pytest.raises(MeldExecutionError, match="not been validated"):
        runtime.execute(context)


def test_execute_applies_graph_mutator_and_spell_overrider(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify blueprint overrides apply graph mutator and spell overrider.

    Contract:
        - GraphMutator.apply returns the execution blueprint.
        - SpellOverrider.apply returns the override_map.
        - Engine receives the execution blueprint and override_map.
    """
    runtime = MeldRuntime()
    root_blueprint = object()
    mutated_blueprint = object()
    override_map = {
        _make_socket_ref(
            node_id="spell-1",
            param_name="param",
            param_path=("param",),
        ): "value"
    }
    crafter = SimpleNamespace(_root_blueprint_phase5=root_blueprint)
    spell = _SpellStub(spell_id="spell-1", crafter=crafter, mutation_override={"x": "y"})
    context = _make_context(spell=spell, overrides={"param": "value"})

    mutator_instance = MagicMock()
    mutator_instance.apply.return_value = mutated_blueprint
    mutator_cls = MagicMock(return_value=mutator_instance)
    monkeypatch.setattr(runtime_module, "GraphMutator", mutator_cls)

    overrider_instance = MagicMock()
    overrider_instance.apply.return_value = override_map
    overrider_cls = MagicMock(return_value=overrider_instance)
    monkeypatch.setattr(runtime_module, "SpellOverrider", overrider_cls)

    engine_cls, _ = _install_engine_mock(monkeypatch, run_result="ok")
    runtime.execute(context)

    mutator_cls.assert_called_once_with(root_blueprint)
    mutator_instance.apply.assert_called_once_with({"x": "y"})
    overrider_cls.assert_called_once_with(mutated_blueprint)
    overrider_instance.apply.assert_called_once_with(context.overrides)
    assert engine_cls.call_args.kwargs["blueprint"] is mutated_blueprint
    assert engine_cls.call_args.kwargs["override_map"] == override_map


def test_execute_wraps_override_application_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify override application errors are wrapped in MeldExecutionError.

    Contract:
        - failures applying overrides raise MeldExecutionError with inner.
    """
    runtime = MeldRuntime()
    root_blueprint = object()
    crafter = SimpleNamespace(_root_blueprint_phase5=root_blueprint)
    spell = _SpellStub(spell_id="spell-1", crafter=crafter)
    context = _make_context(spell=spell, overrides={"param": "value"})

    mutator_instance = MagicMock()
    mutator_instance.apply.return_value = root_blueprint
    mutator_cls = MagicMock(return_value=mutator_instance)
    monkeypatch.setattr(runtime_module, "GraphMutator", mutator_cls)

    overrider_instance = MagicMock()
    overrider_instance.apply.side_effect = RuntimeError("override failure")
    overrider_cls = MagicMock(return_value=overrider_instance)
    monkeypatch.setattr(runtime_module, "SpellOverrider", overrider_cls)

    with pytest.raises(MeldExecutionError) as exc_info:
        runtime.execute(context)
    assert isinstance(exc_info.value.inner, RuntimeError)


def test_execute_uses_context_overrides_without_blueprint(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify context overrides are used when no blueprint exists.

    Contract:
        - ResolutionFrame receives merged overrides from context only.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1")
    context = _make_context(spell=spell, overrides={"__args__": (1, 2), "x": 3})
    frame_cls, _ = _install_frame_mock(monkeypatch)
    _install_engine_mock(monkeypatch, run_result="ok")
    runtime.execute(context)
    overrides = frame_cls.call_args.kwargs["overrides"]
    assert overrides["__args__"] == [1, 2]
    assert overrides["x"] == 3


def test_build_frame_overrides_merges_context_and_override_map() -> None:
    """
    Verify _build_frame_overrides merges context overrides and override_map.

    Contract:
        - __args__ is copied to a new list.
        - override_map values replace context values for the same param.
    """
    runtime = MeldRuntime()
    args = [1, 2]
    context_overrides = {"__args__": args, "x": "context"}
    root_id = "spell-1"
    override_map = {
        _make_socket_ref(root_id, "x", ("x",)): "override",
    }
    merged = runtime._build_frame_overrides(
        context_overrides=context_overrides,
        override_map=override_map,
        root_spell_id=root_id,
    )
    assert merged["__args__"] == [1, 2]
    assert merged["__args__"] is not args
    assert merged["x"] == "override"


def test_build_frame_overrides_ignores_non_dict_context_overrides() -> None:
    """
    Verify non-dict context overrides are ignored.

    Contract:
        - only override_map contributes when context_overrides is not a dict.
    """
    runtime = MeldRuntime()
    root_id = "spell-1"
    override_map = {
        _make_socket_ref(root_id, "x", ("x",)): "override",
    }
    merged = runtime._build_frame_overrides(
        context_overrides=["not", "a", "dict"],
        override_map=override_map,
        root_spell_id=root_id,
    )
    assert merged == {"x": "override"}


def test_build_frame_overrides_filters_non_root_or_deep_paths() -> None:
    """
    Verify _build_frame_overrides filters non-root or deep path overrides.

    Contract:
        - only root node overrides with single-segment paths are applied.
    """
    runtime = MeldRuntime()
    root_id = "spell-1"
    override_map = {
        _make_socket_ref(root_id, "x", ("x",)): "root",
        _make_socket_ref(root_id, "y", ("root", "y")): "deep",
        _make_socket_ref("other", "z", ("z",)): "other",
    }
    merged = runtime._build_frame_overrides(
        context_overrides={},
        override_map=override_map,
        root_spell_id=root_id,
    )
    assert merged == {"x": "root"}


def test_execute_builds_spell_lookup_from_spellbook(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify spell lookup includes spellbook and contracted spells.

    Contract:
        - lookup includes all spell indices from both registries.
    """
    runtime = MeldRuntime()
    spell_a = _SpellStub(spell_id="spell-a")
    spell_b = _SpellStub(spell_id="spell-b")
    spell_c = _SpellStub(spell_id="spell-c")
    spellbook = _SpellbookStub(
        spells={
            spell_a.spell_index: spell_a,
            spell_b.spell_index: spell_b,
        },
        contracted_spells={
            "lineage-1": {spell_c.spell_index: spell_c},
        },
    )
    spell = _SpellStub(spell_id="spell-1", spellbook=spellbook)
    context = _make_context(spell=spell)
    engine_cls, _ = _install_engine_mock(monkeypatch, run_result="ok")
    runtime.execute(context)
    lookup = engine_cls.call_args.kwargs["spell_lookup"]
    assert lookup[spell_a.spell_index.current] is spell_a
    assert lookup[spell_b.spell_index.current] is spell_b
    assert lookup[spell_c.spell_index.current] is spell_c


def test_execute_passes_system_states_to_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify system states are passed to the engine.

    Contract:
        - engine receives spell._spell_system_states.
    """
    runtime = MeldRuntime()
    system_states = object()
    spell = _SpellStub(spell_id="spell-1", spell_system_states=system_states)
    context = _make_context(spell=spell)
    engine_cls, _ = _install_engine_mock(monkeypatch, run_result="ok")
    runtime.execute(context)
    assert engine_cls.call_args.kwargs["system_states"] is system_states


def test_execute_cleans_engine_and_frame_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify engine and frame are cleaned on successful execution.

    Contract:
        - engine.cleanup and frame.cleanup are called in all cases.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1")
    context = _make_context(spell=spell)
    _, engine_instance = _install_engine_mock(monkeypatch, run_result="ok")
    _, frame_instance = _install_frame_mock(monkeypatch)
    runtime.execute(context)
    engine_instance.cleanup.assert_called_once()
    frame_instance.cleanup.assert_called_once()


def test_execute_cleans_engine_and_frame_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify engine and frame are cleaned when engine.run raises.

    Contract:
        - cleanup is called even when execution fails.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1")
    context = _make_context(spell=spell)
    error = RuntimeError("engine failure")
    _, engine_instance = _install_engine_mock(monkeypatch, run_error=error)
    _, frame_instance = _install_frame_mock(monkeypatch)
    with pytest.raises(RuntimeError, match="engine failure"):
        runtime.execute(context)
    engine_instance.cleanup.assert_called_once()
    frame_instance.cleanup.assert_called_once()


def test_execute_propagates_meld_execution_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify MeldExecutionError from the engine is propagated.

    Contract:
        - engine MeldExecutionError is not wrapped or suppressed.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1")
    context = _make_context(spell=spell)
    error = MeldExecutionError(
        spell_id="spell-1",
        spell_name="spell-1",
        message="engine failed",
    )
    _install_engine_mock(monkeypatch, run_error=error)
    with pytest.raises(MeldExecutionError, match="engine failed"):
        runtime.execute(context)


def test_execute_factory_spell_none_result_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify factory-style spells cannot return None.

    Contract:
        - None result for factory spells raises MeldExecutionError.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1", is_class_spell=True)
    context = _make_context(spell=spell)
    _install_engine_mock(monkeypatch, run_result=None)
    with pytest.raises(MeldExecutionError, match="returned None"):
        runtime.execute(context)


def test_execute_non_factory_none_result_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify non-factory spells may return None.

    Contract:
        - None result for non-factory spells is allowed.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(
        spell_id="spell-1",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    context = _make_context(spell=spell)
    _install_engine_mock(monkeypatch, run_result=None)
    assert runtime.execute(context) is None


def test_execute_uses_mutation_override_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify mutation_override payload is passed to GraphMutator.apply.

    Contract:
        - mutation_override dict is forwarded to GraphMutator.apply.
    """
    runtime = MeldRuntime()
    root_blueprint = object()
    crafter = SimpleNamespace(_root_blueprint_phase5=root_blueprint)
    payload = {"key": "value"}
    spell = _SpellStub(spell_id="spell-1", crafter=crafter, mutation_override=payload)
    context = _make_context(spell=spell)

    mutator_instance = MagicMock()
    mutator_instance.apply.return_value = root_blueprint
    mutator_cls = MagicMock(return_value=mutator_instance)
    monkeypatch.setattr(runtime_module, "GraphMutator", mutator_cls)

    overrider_instance = MagicMock()
    overrider_instance.apply.return_value = {}
    overrider_cls = MagicMock(return_value=overrider_instance)
    monkeypatch.setattr(runtime_module, "SpellOverrider", overrider_cls)

    _install_engine_mock(monkeypatch, run_result="ok")
    runtime.execute(context)
    mutator_instance.apply.assert_called_once_with(payload)


def test_execute_defaults_mutation_override_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify mutation_override access errors fall back to empty payload.

    Contract:
        - mutation_override errors lead to an empty payload.
    """
    runtime = MeldRuntime()
    root_blueprint = object()
    crafter = SimpleNamespace(_root_blueprint_phase5=root_blueprint)
    spell = _SpellStub(
        spell_id="spell-1",
        crafter=crafter,
        mutation_override_error=RuntimeError("mutation override failure"),
    )
    context = _make_context(spell=spell)

    mutator_instance = MagicMock()
    mutator_instance.apply.return_value = root_blueprint
    mutator_cls = MagicMock(return_value=mutator_instance)
    monkeypatch.setattr(runtime_module, "GraphMutator", mutator_cls)

    overrider_instance = MagicMock()
    overrider_instance.apply.return_value = {}
    overrider_cls = MagicMock(return_value=overrider_instance)
    monkeypatch.setattr(runtime_module, "SpellOverrider", overrider_cls)

    _install_engine_mock(monkeypatch, run_result="ok")
    runtime.execute(context)
    mutator_instance.apply.assert_called_once_with({})


def test_build_frame_overrides_ignores_non_root_override_map_entries() -> None:
    """
    Verify _build_frame_overrides ignores override_map entries for other nodes.

    Contract:
        - only root spell overrides are applied to the frame.
    """
    runtime = MeldRuntime()
    root_id = "spell-1"
    override_map = {
        _make_socket_ref("other", "x", ("x",)): "ignored",
    }
    merged = runtime._build_frame_overrides(
        context_overrides={},
        override_map=override_map,
        root_spell_id=root_id,
    )
    assert merged == {}


def test_build_frame_overrides_empty_inputs_return_empty() -> None:
    """
    Verify _build_frame_overrides returns empty when no inputs are provided.

    Contract:
        - empty context overrides and override_map yield an empty dict.
    """
    runtime = MeldRuntime()
    merged = runtime._build_frame_overrides(
        context_overrides=None,
        override_map={},
        root_spell_id="spell-1",
    )
    assert merged == {}


def test_execute_wraps_graph_mutator_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify GraphMutator failures are wrapped in MeldExecutionError.

    Contract:
        - GraphMutator.apply errors raise MeldExecutionError with inner exception.
    """
    runtime = MeldRuntime()
    root_blueprint = object()
    crafter = SimpleNamespace(_root_blueprint_phase5=root_blueprint)
    spell = _SpellStub(spell_id="spell-1", crafter=crafter, mutation_override={"x": "y"})
    context = _make_context(spell=spell, overrides={})

    mutator_instance = MagicMock()
    mutator_instance.apply.side_effect = RuntimeError("mutator failure")
    mutator_cls = MagicMock(return_value=mutator_instance)
    monkeypatch.setattr(runtime_module, "GraphMutator", mutator_cls)

    with pytest.raises(MeldExecutionError) as exc_info:
        runtime.execute(context)
    assert isinstance(exc_info.value.inner, RuntimeError)


def test_execute_allows_missing_spellbook(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify execution proceeds when the spell has no spellbook.

    Contract:
        - Missing spell._spellbook yields an empty spell_lookup.
    """
    runtime = MeldRuntime()
    spell = _SpellStub(spell_id="spell-1", spellbook=None)
    context = _make_context(spell=spell)
    engine_cls, _ = _install_engine_mock(monkeypatch, run_result="ok")

    assert runtime.execute(context) == "ok"
    lookup = engine_cls.call_args.kwargs["spell_lookup"]
    assert lookup == {}


def test_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called multiple times safely.

    Contract:
        - cleanup is idempotent and leaves cleaned=True.
    """
    runtime = MeldRuntime()
    runtime.cleanup()
    runtime.cleanup()
    assert runtime.cleaned is True


def test_execute_blueprint_ignores_non_dict_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify non-dict overrides are ignored when a blueprint is present.

    Contract:
        - Non-dict overrides fall back to {} before SpellOverrider.apply.
        - Execution proceeds using the override_map produced by SpellOverrider.
    """
    runtime = MeldRuntime()
    root_blueprint = object()
    mutated_blueprint = object()
    crafter = SimpleNamespace(_root_blueprint_phase5=root_blueprint)
    spell = _SpellStub(spell_id="spell-1", crafter=crafter, mutation_override={})
    context = _make_context(spell=spell, overrides=[])

    mutator_instance = MagicMock()
    mutator_instance.apply.return_value = mutated_blueprint
    mutator_cls = MagicMock(return_value=mutator_instance)
    monkeypatch.setattr(runtime_module, "GraphMutator", mutator_cls)

    overrider_instance = MagicMock()
    overrider_instance.apply.return_value = {}
    overrider_cls = MagicMock(return_value=overrider_instance)
    monkeypatch.setattr(runtime_module, "SpellOverrider", overrider_cls)

    engine_cls, _ = _install_engine_mock(monkeypatch, run_result="ok")
    assert runtime.execute(context) == "ok"
    overrider_instance.apply.assert_called_once_with({})
    assert engine_cls.call_args.kwargs["blueprint"] is mutated_blueprint


def test_build_frame_overrides_rejects_non_iterable_args() -> None:
    """
    Verify non-iterable __args__ values raise TypeError.

    Contract:
        - __args__ must be iterable when provided.
    """
    runtime = MeldRuntime()
    with pytest.raises(TypeError):
        runtime._build_frame_overrides(
            context_overrides={"__args__": 1},
            override_map={},
            root_spell_id="spell-1",
        )
