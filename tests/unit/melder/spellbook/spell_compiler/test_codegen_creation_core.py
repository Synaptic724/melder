"""Focused unit tests for the phase-11 codegen-creation contract."""

from types import SimpleNamespace
from typing import Any, Tuple

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_general_creation_context_codegen_creation_strategy as general_creation_context_strategy_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_generalized_no_overrides_codegen_creation_strategy as no_overrides_strategy_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_generalized_overrides_codegen_creation_strategy as overrides_strategy_module
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscovery,
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_system import (
    CodegenCreationSystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_general_creation_context_codegen_creation_strategy import (
    SpellGeneralCreationContextCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_generalized_creation_context_setup_codegen_creation_strategy import (
    SpellGeneralizedCreationContextSetupCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_generalized_no_overrides_codegen_creation_strategy import (
    SpellGeneralizedNoOverridesCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.spell_generalized_overrides_codegen_creation_strategy import (
    SpellGeneralizedOverridesCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class _CleanupProbe:
    """Simple cleanup double used to prove previous-creation cleanup."""

    def __init__(self) -> None:
        self.cleanup_called = False

    def cleanup(self) -> None:
        self.cleanup_called = True


class _CreationStrategyProbe:
    """Minimal creation strategy double for facade tests."""

    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id

    def apply(
            self,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        _ = spell_codegen_model
        _ = spell_codegen_plan
        spell_codegen_creation.metadata[self.strategy_id] = True


class _StrategyBuilderProbe:
    """Minimal strategy-builder double for creation-system facade tests."""

    def __init__(self, strategies: Tuple[Any, ...]) -> None:
        self._strategies = strategies
        self.requested_strategy_ids: Tuple[str, ...] = ()
        self.cleanup_called = False

    def cleanup(self) -> None:
        self.cleanup_called = True

    def get_strategies(self, strategy_ids: Tuple[str, ...]) -> Tuple[Any, ...]:
        self.requested_strategy_ids = strategy_ids
        return self._strategies


class _DiscoveryProbe:
    """Minimal discovery-system double for creation-system facade tests."""

    def __init__(self, discovery: CodegenCreationDiscovery) -> None:
        self._discovery = discovery
        self.discovered_pair: Tuple[Any, Any] | None = None

    def discover(
            self,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
    ) -> CodegenCreationDiscovery:
        self.discovered_pair = (spell_codegen_model, spell_codegen_plan)
        return self._discovery


def test_codegen_creation_discovery_system_selects_generalized_chain_by_default() -> None:
    """The discovery system should extend the generalized chain with the final creation-context strategy."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_creation_context_setup_codegen_creation",
        "generalized_no_overrides_codegen_creation",
        "generalized_overrides_codegen_creation",
        "general_creation_context_codegen_creation",
    )


def test_codegen_creation_discovery_system_falls_back_to_no_overrides_chain() -> None:
    """The discovery system should still fall back to the no-overrides strategy for non-generalized plans."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=(),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "other_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_no_overrides_codegen_creation",
    )


def test_spell_codegen_strategy_builder_registers_extended_order() -> None:
    """The real strategy builder should expose the new finalizer plus the existing generalized strategies."""
    builder = SpellCodegenStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "general_creation_context_codegen_creation",
        "generalized_creation_context_setup_codegen_creation",
        "generalized_no_overrides_codegen_creation",
        "generalized_overrides_codegen_creation",
    )
    with pytest.raises(RuntimeError, match="missing strategy 'missing_creation'"):
        builder.get_strategy("missing_creation")


def test_spell_codegen_creation_cleanup_cleans_metadata() -> None:
    """The creation container should only carry the two runtime doors plus metadata."""
    creation = SpellCodegenCreation(
        selected_strategy_ids=("setup",),
        discovery_reason="reason",
        no_overrides_executor=lambda caller_creations: ("plain", True),
        overrides_executor=lambda caller_creations, overrides: ("override", False),
        metadata={"hello": "world"},
    )

    creation.cleanup()

    assert not hasattr(creation, "metadata")


def test_codegen_creation_system_build_requires_model_and_plan_first() -> None:
    """The creation facade should fail hard until both model and plan exist."""
    system = CodegenCreationSystem()
    missing_model = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": None,
            "_spell_codegen_plan": object(),
        },
    )()
    missing_plan = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": object(),
            "_spell_codegen_plan": None,
        },
    )()

    with pytest.raises(RuntimeError, match="artifact._spell_codegen_model first"):
        system.build(missing_model)
    with pytest.raises(RuntimeError, match="artifact._spell_codegen_plan first"):
        system.build(missing_plan)


def test_codegen_creation_system_build_runs_selected_strategy_chain_and_cleans_previous() -> None:
    """The creation facade should publish the new artifact and cleanup the superseded one."""
    system = CodegenCreationSystem()
    strategy_a = _CreationStrategyProbe("a")
    strategy_b = _CreationStrategyProbe("b")
    builder = _StrategyBuilderProbe((strategy_a, strategy_b))
    discovery = _DiscoveryProbe(
        CodegenCreationDiscovery(
            selected_strategy_ids=("a", "b"),
            discovery_reason="picked-by-test",
        )
    )
    previous_creation = _CleanupProbe()
    model = object()
    plan = object()
    artifact = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": model,
            "_spell_codegen_plan": plan,
            "_spell_codegen_creation": previous_creation,
        },
    )()
    system._strategy_builder = builder
    system._discovery_system = discovery

    system.build(artifact)

    creation = artifact._spell_codegen_creation
    assert isinstance(creation, SpellCodegenCreation)
    assert discovery.discovered_pair == (model, plan)
    assert builder.requested_strategy_ids == ("a", "b")
    assert creation.selected_strategy_ids == ("a", "b")
    assert creation.discovery_reason == "picked-by-test"
    assert creation.metadata["a"] is True
    assert creation.metadata["b"] is True
    assert previous_creation.cleanup_called is True


def test_setup_strategy_records_route_and_transient_scratch() -> None:
    """The setup strategy should store route and transient scratch for the finalizer."""
    strategy = SpellGeneralizedCreationContextSetupCodegenCreationStrategy()
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=type(
            "LanePlanProbe",
            (),
            {"fast_transient_plan": object()},
        )(),
        overrides_plan=None,
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={},
    )

    strategy.apply(
        type(
            "ModelProbe",
            (),
            {"build_kind": "construct", "route_family": "many"},
        )(),
        plan,
        creation,
    )

    assert creation.metadata["_resolve_route_key"] == "many"
    assert creation.metadata["_fast_transient_no_overrides_enabled"] is True


def test_no_overrides_strategy_records_base_executor_and_signature(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The no-overrides strategy should still produce the base executor scratch used by the finalizer."""
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=type(
            "LanePlanProbe",
            (),
            {
                "lane_id": "no_overrides",
                "root_spell_id": "root",
                "root_instance_key": ("root", None),
                "steps": (object(), object()),
                "fast_transient_plan": ("transient",),
            },
        )(),
        overrides_plan=None,
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={},
    )

    monkeypatch.setattr(
        no_overrides_strategy_module.SharedCompilerExecutions,
        "build_fast_transient_schema",
        lambda fast_transient_plan: {"schema": fast_transient_plan},
    )
    monkeypatch.setattr(
        no_overrides_strategy_module.SharedCompilerExecutions,
        "build_no_overrides_codegen_creation_step_signature_row",
        lambda step: ("step", id(step)),
    )
    monkeypatch.setattr(
        no_overrides_strategy_module.SharedCompilerExecutions,
        "build_fast_transient_signature",
        lambda transient_schema: ("transient", transient_schema["schema"]),
    )
    monkeypatch.setattr(
        no_overrides_strategy_module.SharedCompilerExecutions,
        "normalize_instance_key",
        lambda instance_key: instance_key,
    )
    monkeypatch.setattr(
        no_overrides_strategy_module.SharedCompilerExecutions,
        "hash_codegen_signature",
        lambda *parts: "sig:{0}".format(len(parts)),
    )
    monkeypatch.setattr(
        no_overrides_strategy_module,
        "compile_no_overrides_codegen_creation_executor_from_plan",
        lambda *, plan, transient_schema: ("executor", plan.lane_id, transient_schema),
    )

    SpellGeneralizedNoOverridesCodegenCreationStrategy().apply(
        object(),
        plan,
        creation,
    )

    assert creation.no_overrides_executor == (
        "executor",
        "no_overrides",
        {"schema": ("transient",)},
    )
    assert creation.metadata["_no_overrides_base_executor"] == (
        "executor",
        "no_overrides",
        {"schema": ("transient",)},
    )
    assert creation.metadata["_no_overrides_executor_signature"] == "sig:4"


def test_overrides_strategy_records_override_runtime_scratch(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The overrides strategy should write override runtime scratch into metadata for the finalizer."""
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=None,
        overrides_plan=type(
            "LanePlanProbe",
            (),
            {
                "lane_id": "overrides",
                "root_spell_id": "root",
                "steps": (
                    SimpleNamespace(
                        spell=SimpleNamespace(
                            spell_index=SimpleNamespace(current="root"),
                        )
                    ),
                ),
            },
        )(),
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={},
    )
    state = type(
        "ModelProbe",
        (),
        {
            "graph_shape": SimpleNamespace(path_registry="PATH_REG"),
            "override_targeting_shape": SimpleNamespace(
                targets_by_spec={
                    "root>svc": (
                        SpellOverrideTargetRef(
                            node_id="root",
                            param_path_id=1,
                            param_name="svc",
                            socket_kind_value=0,
                        ),
                    )
                },
                specificity_by_spec={"root>svc": 3},
            ),
        },
    )()

    monkeypatch.setattr(
        overrides_strategy_module.SharedCompilerExecutions,
        "build_phase11_step_ir_row",
        lambda step, include_override_metadata: {
            "step": step.spell.spell_index.current,
            "include_override_metadata": include_override_metadata,
        },
    )
    monkeypatch.setattr(
        overrides_strategy_module.SharedCompilerExecutions,
        "hash_codegen_signature",
        lambda *parts: ("sig", len(parts)),
    )
    monkeypatch.setattr(
        overrides_strategy_module,
        "compile_overrides_codegen_creation_executor",
        lambda **kwargs: ("override-executor", kwargs["root_spell_id"]),
    )

    SpellGeneralizedOverridesCodegenCreationStrategy().apply(
        state,
        plan,
        creation,
    )

    assert creation.metadata["_override_targeting"] is not None
    assert creation.metadata["_override_root_spell_id"] == "root"
    assert creation.metadata["_override_path_registry"] == "PATH_REG"
    assert creation.metadata["_override_baseline_executor"] == (
        "override-executor",
        "root",
    )


def test_general_creation_context_strategy_finalizes_two_runtime_doors(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The new fat finalizer should consume scratch and emit the two final runtime doors."""
    strategy = SpellGeneralCreationContextCodegenCreationStrategy()
    root_spell = SimpleNamespace(
        spell_id="root",
        spell_name="root",
        spell_index=SimpleNamespace(current="root"),
        _owner_creations=object(),
    )
    state = SimpleNamespace(
        build_kind="construct",
        route_family="many",
        spell_runtime_shape=SimpleNamespace(
            records_by_spell_id={"root": SimpleNamespace(spell=root_spell)}
        ),
    )
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=SimpleNamespace(
            lane_id="no_overrides",
            root_spell_id="root",
            fast_transient_plan=("transient",),
        ),
        overrides_plan=SimpleNamespace(
            lane_id="overrides",
            root_spell_id="root",
            steps=(),
        ),
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor="base-no-overrides",
        overrides_executor=None,
        metadata={
            "_resolve_route_key": "many",
            "_fast_transient_no_overrides_enabled": True,
            "_override_targeting": "targeting",
            "_override_plan_signature": ("sig",),
            "_override_path_registry": "registry",
            "_override_plan_rows": (),
            "_override_root_spell_id": "root",
            "_override_spell_lookup": {"root": root_spell},
            "_override_empty_shape_key": (("sig",), (), -1),
            "_override_baseline_executor": "baseline",
        },
    )

    monkeypatch.setattr(
        general_creation_context_strategy_module,
        "compile_creation_context_hooks_no_overrides_executor",
        lambda **kwargs: ("final-no-overrides", kwargs["no_overrides_executor"]),
    )
    monkeypatch.setattr(
        general_creation_context_strategy_module,
        "compile_creation_context_hooks_overrides_only_executor",
        lambda **kwargs: ("final-overrides", kwargs["execute_with_overrides"]),
    )

    strategy.apply(state, plan, creation)

    assert creation.no_overrides_executor == (
        "final-no-overrides",
        "base-no-overrides",
    )
    assert creation.overrides_executor[0] == "final-overrides"
    assert creation.metadata["creation_context_strategy"] == (
        "general_creation_context_codegen_creation"
    )
