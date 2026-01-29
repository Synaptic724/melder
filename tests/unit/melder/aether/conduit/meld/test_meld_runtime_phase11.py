"""Phase 11 fast-path gate tests for MeldRuntime."""
from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest

import melder.aether.conduit.meld.meld_runtime.meld_runtime as runtime_module
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class _SpellbookStub:
    """
    Spellbook stub with minimal attributes for runtime tests.
    """

    def __init__(self) -> None:
        """
        Initialize with validation disabled and an empty spell pool.
        """
        self._spellbook_validation_required = False
        self._spell_id_pool: Dict[str, Any] = {}
        self._aether = SimpleNamespace(_get_change_control_manager=lambda _: None)


class _CrafterStub:
    """
    Crafter stub exposing Phase 5–11 artifacts.
    """

    def __init__(
        self,
        *,
        root_blueprint: Any,
        occurrence_plan: Any,
        injection_plan: Any,
        override_patch_map: Any,
        mutation_patch_map: Any,
        execution_plan: Any,
    ) -> None:
        """
        Store the provided artifacts.
        """
        self._root_blueprint_phase5 = root_blueprint
        self._occurrence_plan_phase8 = occurrence_plan
        self._injection_plan_phase9 = injection_plan
        self._override_patch_map_phase10 = override_patch_map
        self._mutation_patch_map_phase10 = mutation_patch_map
        self._execution_plan_phase11 = execution_plan

    @property
    def root_blueprint_phase5(self) -> Any:
        return self._root_blueprint_phase5

    @property
    def occurrence_plan_phase8(self) -> Any:
        return self._occurrence_plan_phase8

    @property
    def injection_plan_phase9(self) -> Any:
        return self._injection_plan_phase9

    @property
    def override_patch_map_phase10(self) -> Any:
        return self._override_patch_map_phase10

    @property
    def mutation_patch_map_phase10(self) -> Any:
        return self._mutation_patch_map_phase10

    @property
    def execution_plan_phase11(self) -> Any:
        return self._execution_plan_phase11


class _SpellStub:
    """
    Spell stub exposing the runtime attributes required by MeldRuntime.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        crafter: Optional[_CrafterStub],
        mutation_override: Optional[Dict[str, Any]] = None,
        hooks_enabled: bool = False,
    ) -> None:
        """
        Initialize the spell with explicit runtime attributes.
        """
        self.spell_index = SpellIndex(spell_id)
        self.spell_name = spell_id
        self.aetheric_frame = "frame"
        self._spellbook = _SpellbookStub()
        self._spellbook._spell_id_pool[spell_id] = self
        self._spell_system_states = None
        self._crafter = crafter
        self._mutation_override = mutation_override
        self._hooks_enabled = hooks_enabled
        self.is_broken = False
        self.validated = True
        self.dependency_graph = None
        self.requirements = None
        self.resolution_frame = None
        self.is_class_spell = True
        self.is_method_spell = False
        self.is_lambda_spell = False

    @property
    def mutation_override(self) -> Dict[str, Any]:
        """
        Return the configured mutation override payload.
        """
        return self._mutation_override or {}


class _ContextStub:
    """
    Meld context stub with root spell and overrides.
    """

    def __init__(self, *, root_spell: _SpellStub, overrides: Optional[Dict[str, Any]] = None) -> None:
        """
        Store the root spell and overrides.
        """
        self.root_spell = root_spell
        self.overrides = overrides or {}
        self.cancel_event = None


class _EngineStub:
    """
    Engine stub capturing which execution path is used.
    """
    last_instance: Optional["_EngineStub"] = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Store the init arguments for inspection.
        """
        self.args = args
        self.kwargs = kwargs
        self.run_called = False
        self.run_execution_called = False
        _EngineStub.last_instance = self

    def run(self) -> str:
        """
        Return a sentinel for the slow path.
        """
        self.run_called = True
        return "slow"

    def run_execution_plan(self, execution_plan: Any) -> str:
        """
        Return a sentinel for the Phase 11 fast path.
        """
        self.run_execution_called = True
        return "fast"

    def cleanup(self) -> None:
        """
        No-op cleanup for the stub.
        """
        return None


def _install_engine_stub(monkeypatch: pytest.MonkeyPatch) -> _EngineStub:
    """
    Replace the runtime MeldEngine with a stub implementation.
    """
    stub = _EngineStub
    monkeypatch.setattr(runtime_module, "MeldEngine", stub)
    return stub


def _set_override_helpers(
    monkeypatch: pytest.MonkeyPatch,
    *,
    override_map: Optional[Dict[Any, Any]] = None,
    mutation_blueprint: Optional[Any] = None,
) -> None:
    """
    Configure the override helper functions for the runtime module.
    """
    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_override_payload",
        lambda **_: override_map or {},
    )
    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_mutation_overrides",
        lambda **_: mutation_blueprint,
    )


def _make_artifacts(
    *,
    root_id: str,
    contract_overrides_occurrence: Optional[Dict[Any, Any]] = None,
    contract_overrides_spell_id: Optional[Dict[Any, Any]] = None,
) -> Dict[str, Any]:
    """
    Build stub artifacts for gating tests.
    """
    execution_plan = SimpleNamespace(root_spell_id=root_id)
    occurrence_plan = SimpleNamespace(
        root_spell_id=root_id,
        contract_overrides_by_occurrence=contract_overrides_occurrence or {},
        contract_overrides_by_spell_id=contract_overrides_spell_id or {},
    )
    injection_plan = object()
    return {
        "execution_plan": execution_plan,
        "occurrence_plan": occurrence_plan,
        "injection_plan": injection_plan,
    }


def test_phase11_gate_rejects_missing_execution_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate missing Phase 11 plan uses the slow path.
    Contract:
        - Missing execution_plan forces the slow path.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=None,
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


@pytest.mark.parametrize("artifact_key", ["occurrence_plan", "injection_plan"])
def test_phase11_requires_phase8_and_phase9(
    monkeypatch: pytest.MonkeyPatch,
    artifact_key: str,
) -> None:
    """
    Purpose:
        Validate missing Phase 8/9 artifacts disable the fast path.
    Contract:
        - Missing Phase 8 or Phase 9 artifacts force the slow path.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    artifacts[artifact_key] = None
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_root_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Reject Phase 11 when the execution plan root id mismatches.
    Contract:
        - The slow path is used when plan root differs from spell id.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="other")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_mutation_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate Phase 11 rejects mutation overrides.
    Contract:
        - Mutation override payloads force the slow path.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch, mutation_blueprint=object())
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter, mutation_override={"x": "y"})
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_context_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate Phase 11 rejects user overrides.
    Contract:
        - Any context overrides force the slow path.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell, overrides={"x": "y"})

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_override_map(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate Phase 11 rejects socket override maps.
    Contract:
        - Any override_map entries force the slow path.
    """
    _install_engine_stub(monkeypatch)
    socket_ref = SocketRef(
        node_id="root",
        param_name="dep",
        param_path=("root", "dep"),
        socket_kind=SocketKind.NORMAL,
    )
    _set_override_helpers(monkeypatch, override_map={socket_ref: "value"})
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate Phase 11 rejects hook-enabled spells.
    Contract:
        - Hook-enabled spells use the slow path.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter, hooks_enabled=True)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_contract_overrides_by_occurrence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate Phase 11 rejects contract overrides by occurrence.
    Contract:
        - Any contract override payload disables Phase 11.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(
        root_id="root",
        contract_overrides_occurrence={"occ": {"x": "y"}},
    )
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_rejects_contract_overrides_by_spell_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate Phase 11 rejects contract overrides by spell id.
    Contract:
        - Any contract override payload disables Phase 11.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(
        root_id="root",
        contract_overrides_spell_id={"root": [("occ", {"x": "y"})]},
    )
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"


def test_phase11_gate_allows_fast_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate Phase 11 runs when all gate conditions are satisfied.
    Contract:
        - Fast-path execution returns the fast sentinel.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "fast"
    assert _EngineStub.last_instance is not None
    assert _EngineStub.last_instance.run_execution_called
    assert not _EngineStub.last_instance.run_called


def test_phase11_gate_rejects_without_root_blueprint(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate Phase 11 is not used without a root blueprint.
    Contract:
        - The slow path is used when the root blueprint is missing.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=None,
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"
    assert _EngineStub.last_instance is not None
    assert _EngineStub.last_instance.run_called


def test_phase11_override_helper_failure_is_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Ensure override helper failures are wrapped as MeldExecutionError.
    Contract:
        - Exceptions from override helpers surface as MeldExecutionError.
    """
    _install_engine_stub(monkeypatch)
    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_override_payload",
        lambda **_: (_ for _ in ()).throw(RuntimeError("bad override")),
    )
    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_mutation_overrides",
        lambda **_: object(),
    )
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    with pytest.raises(MeldExecutionError):
        runtime.execute(context)


def test_phase11_gate_rejects_mutation_override_uses_slow_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure mutation overrides route to the slow path even with Phase 11 artifacts.
    Contract:
        - Fast path is skipped when mutation_override is non-empty.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch, mutation_blueprint=object())
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter, mutation_override={"x": "y"})
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"
    assert _EngineStub.last_instance is not None
    assert _EngineStub.last_instance.run_called
    assert not _EngineStub.last_instance.run_execution_called


def test_phase11_gate_rejects_context_overrides_uses_slow_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure context overrides force the slow path when Phase 11 artifacts exist.
    Contract:
        - Fast path is skipped when context overrides are supplied.
    """
    _install_engine_stub(monkeypatch)
    _set_override_helpers(monkeypatch)
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell, overrides={"x": "y"})

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"
    assert _EngineStub.last_instance is not None
    assert _EngineStub.last_instance.run_called


def test_phase11_gate_rejects_override_map_uses_slow_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure non-empty override maps force the slow path.
    Contract:
        - Fast path is skipped when override_map is non-empty.
    """
    _install_engine_stub(monkeypatch)
    socket_ref = SocketRef(
        node_id="root",
        param_name="dep",
        param_path=("root", "dep"),
        socket_kind=SocketKind.NORMAL,
    )
    _set_override_helpers(monkeypatch, override_map={socket_ref: "value"})
    artifacts = _make_artifacts(root_id="root")
    crafter = _CrafterStub(
        root_blueprint=object(),
        occurrence_plan=artifacts["occurrence_plan"],
        injection_plan=artifacts["injection_plan"],
        override_patch_map=object(),
        mutation_patch_map=object(),
        execution_plan=artifacts["execution_plan"],
    )
    spell = _SpellStub(spell_id="root", crafter=crafter)
    context = _ContextStub(root_spell=spell)

    runtime = MeldRuntime()
    result = runtime.execute(context)

    assert result == "slow"
    assert _EngineStub.last_instance is not None
    assert _EngineStub.last_instance.run_called
