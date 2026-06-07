"""Focused unit tests for the phase-11 codegen-creation contract."""

from types import SimpleNamespace
from typing import Any, Tuple

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_no_overrides_codegen_creation_step as no_overrides_step_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_overrides_codegen_creation_step as overrides_step_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step as many_only_no_overrides_step_module
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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_strategy import (
    GeneralizedCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_strategy import (
    ManyOnlyCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_creation_context_setup_step import (
    ManyOnlyCreationContextSetupStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step import (
    ManyOnlyNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_strategy import (
    SoloCodegenCreationStrategy,
)
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_no_overrides_codegen_creation_step as solo_no_overrides_step_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_overrides_codegen_creation_step as solo_overrides_step_module
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_creation_context_setup_step import (
    GeneralizedCreationContextSetupStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_finalize_creation_context_step import (
    GeneralizedFinalizeCreationContextStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_no_overrides_codegen_creation_step import (
    GeneralizedNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_overrides_codegen_creation_step import (
    GeneralizedOverridesCodegenCreationStep,
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


def _make_generalized_state(
        *,
        spell_codegen_model: Any,
        spell_codegen_plan: SpellCodegenPlan,
        spell_codegen_creation: SpellCodegenCreation,
) -> GeneralizedCodegenCreationState:
    """Build one generalized family state object for direct step tests."""
    return GeneralizedCodegenCreationState(
        spell_codegen_model=spell_codegen_model,
        spell_codegen_plan=spell_codegen_plan,
        spell_codegen_creation=spell_codegen_creation,
    )


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
        "generalized_codegen_creation",
    )


def test_codegen_creation_discovery_system_selects_solo_family() -> None:
    """The discovery system should route solo planner output to the solo creation family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_solo_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_solo_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "solo_codegen_creation",
    )


def test_codegen_creation_discovery_system_selects_many_only_family() -> None:
    """The discovery system should route many-only planner output to the many-only creation family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_many_only_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_many_only_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "many_only_codegen_creation",
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
    """The real strategy builder should expose solo, many-only, generalized, and fallback creation families."""
    builder = SpellCodegenStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "solo_codegen_creation",
        "many_only_codegen_creation",
        "generalized_codegen_creation",
        "generalized_no_overrides_codegen_creation",
    )
    assert isinstance(
        builder.get_strategy("solo_codegen_creation"),
        SoloCodegenCreationStrategy,
    )
    assert isinstance(
        builder.get_strategy("many_only_codegen_creation"),
        ManyOnlyCodegenCreationStrategy,
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
    plan = SimpleNamespace(
        plan_family_id="generalized",
        candidate_codegen_style_ids=("generalized_default",),
    )
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


def test_setup_step_records_route_and_transient_state() -> None:
    """The generalized setup step should keep route but no longer own fast-transient state."""
    step = GeneralizedCreationContextSetupStep()
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

    state = _make_generalized_state(
        spell_codegen_model=type(
            "ModelProbe",
            (),
            {"build_kind": "construct", "route_family": "many"},
        )(),
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    step.apply(state)

    assert state.resolve_route_key == "many"
    assert state.fast_transient_no_overrides_enabled is False


def test_many_only_setup_step_records_many_route() -> None:
    """The many-only setup step should now only resolve the many route."""
    step = ManyOnlyCreationContextSetupStep()
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=type(
            "LanePlanProbe",
            (),
            {},
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

    state = ManyOnlyCodegenCreationState(
        spell_codegen_model=type(
            "ModelProbe",
            (),
            {"build_kind": "construct", "route_family": "many"},
        )(),
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    step.apply(state)

    assert state.resolve_route_key == "many"


def test_no_overrides_step_records_base_executor_and_signature(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The generalized no-overrides step should pass through the transient schema path when present."""
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
        no_overrides_step_module.SharedCompilerExecutions,
        "build_fast_transient_schema",
        lambda fast_transient_plan: {"schema": fast_transient_plan},
    )
    monkeypatch.setattr(
        no_overrides_step_module.SharedCompilerExecutions,
        "build_no_overrides_codegen_creation_step_signature_row",
        lambda step: ("step", id(step)),
    )
    monkeypatch.setattr(
        no_overrides_step_module.SharedCompilerExecutions,
        "build_fast_transient_signature",
        lambda transient_schema: ("transient", transient_schema["schema"]),
    )
    monkeypatch.setattr(
        no_overrides_step_module.SharedCompilerExecutions,
        "normalize_instance_key",
        lambda instance_key: instance_key,
    )
    monkeypatch.setattr(
        no_overrides_step_module.SharedCompilerExecutions,
        "hash_codegen_signature",
        lambda *parts: "sig:{0}".format(len(parts)),
    )
    monkeypatch.setattr(
        no_overrides_step_module,
        "compile_no_overrides_codegen_creation_executor_from_plan",
        lambda *, plan, transient_schema: ("executor", plan.lane_id, transient_schema),
    )

    state = _make_generalized_state(
        spell_codegen_model=object(),
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    GeneralizedNoOverridesCodegenCreationStep().apply(state)

    assert creation.no_overrides_executor == (
        "executor",
        "no_overrides",
        {"schema": ("transient",)},
    )
    assert state.base_no_overrides_executor == (
        "executor",
        "no_overrides",
        {"schema": ("transient",)},
    )
    assert creation.metadata["no_overrides_executor_signature"] == "sig:4"
    assert creation.metadata["no_overrides_fast_transient_available"] is True


def test_many_only_no_overrides_step_records_transient_executor_and_signature(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The many-only no-overrides step should now own disposal-mode selection."""
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=type(
            "LanePlanProbe",
            (),
            {
                "lane_id": "many_only_no_overrides",
                "root_spell_id": "root",
                "root_instance_key": ("root", None),
                "steps": (
                    SimpleNamespace(spell=SimpleNamespace(has_disposal_methods=False)),
                    SimpleNamespace(spell=SimpleNamespace(has_disposal_methods=False)),
                ),
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
        many_only_no_overrides_step_module.SharedCompilerExecutions,
        "build_no_overrides_codegen_creation_step_signature_row",
        lambda step: ("step", id(step)),
    )
    monkeypatch.setattr(
        many_only_no_overrides_step_module.SharedCompilerExecutions,
        "normalize_instance_key",
        lambda instance_key: instance_key,
    )
    monkeypatch.setattr(
        many_only_no_overrides_step_module.SharedCompilerExecutions,
        "hash_codegen_signature",
        lambda *parts: "sig:{0}".format(len(parts)),
    )
    monkeypatch.setattr(
        many_only_no_overrides_step_module,
        "compile_no_overrides_codegen_creation_executor_from_plan",
        lambda *, plan, transient_schema=None: (
            "executor",
            plan.lane_id,
            transient_schema,
        ),
    )

    state = ManyOnlyCodegenCreationState(
        spell_codegen_model=object(),
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    ManyOnlyNoOverridesCodegenCreationStep().apply(state)

    assert creation.no_overrides_executor == (
        "executor",
        "many_only_no_overrides",
        None,
    )
    assert state.base_no_overrides_executor == (
        "executor",
        "many_only_no_overrides",
        None,
    )
    assert creation.metadata["no_overrides_disposal_mode"] == "disposal_free"


def test_overrides_step_records_override_runtime_state(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The generalized overrides step should write override runtime state onto the family object."""
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
        overrides_step_module.SharedCompilerExecutions,
        "build_phase11_step_ir_row",
        lambda step, include_override_metadata: {
            "step": step.spell.spell_index.current,
            "include_override_metadata": include_override_metadata,
        },
    )
    monkeypatch.setattr(
        overrides_step_module.SharedCompilerExecutions,
        "hash_codegen_signature",
        lambda *parts: ("sig", len(parts)),
    )
    monkeypatch.setattr(
        overrides_step_module,
        "compile_overrides_codegen_creation_executor",
        lambda **kwargs: ("override-executor", kwargs["root_spell_id"]),
    )

    family_state = _make_generalized_state(
        spell_codegen_model=state,
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    GeneralizedOverridesCodegenCreationStep().apply(family_state)

    assert family_state.override_targeting is not None
    assert family_state.override_root_spell_id == "root"
    assert family_state.override_path_registry == "PATH_REG"
    assert family_state.override_baseline_executor == (
        "override-executor",
        "root",
    )
    assert creation.metadata["override_lane_id"] == "overrides"


def test_general_creation_context_strategy_preserves_base_no_overrides_and_builds_override_runtime(
) -> None:
    """The generalized finalization step should preserve the base no-overrides executor and build the override runtime callable."""
    strategy = GeneralizedFinalizeCreationContextStep()
    creations = SimpleNamespace(get_creation=lambda spell_id: None)
    root_spell = SimpleNamespace(
        spell_id="root",
        spell_name="root",
        spell_index=SimpleNamespace(current="root"),
        _owner_creations=creations,
    )
    state = SimpleNamespace(
        build_kind="construct",
        route_family="many",
        spell_runtime_shape=SimpleNamespace(
            records_by_spell_id={"root": SimpleNamespace(spell=root_spell)}
        ),
        graph_shape=None,
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
    base_no_overrides_executor = lambda caller_creations, owner_creations=None, caller_creations_lock_held=False: "base-no-overrides"
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=base_no_overrides_executor,
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

    family_state = _make_generalized_state(
        spell_codegen_model=state,
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    family_state.resolve_route_key = "many"
    family_state.fast_transient_no_overrides_enabled = True
    family_state.override_targeting = "targeting"
    family_state.override_plan_signature = ("sig",)
    family_state.override_path_registry = "registry"
    family_state.override_plan_rows = ()
    family_state.override_root_spell_id = "root"
    family_state.override_spell_lookup = {"root": root_spell}
    family_state.override_empty_shape_key = (("sig",), (), -1)
    family_state.override_baseline_executor = "baseline"
    family_state.base_no_overrides_executor = base_no_overrides_executor

    strategy.apply(family_state)

    assert creation.no_overrides_executor is base_no_overrides_executor
    assert callable(creation.overrides_executor)
    assert creation.metadata["resolve_route_key"] == "many"
    assert creation.metadata["fast_transient_no_overrides_enabled"] is True


def test_solo_codegen_creation_strategy_builds_solo_owned_runtime_doors(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The solo phase-11 family should use solo-owned steps and publish narrow runtime metadata."""
    sentinel_no_overrides = object()
    sentinel_overrides = object()
    monkeypatch.setattr(
        solo_no_overrides_step_module,
        "compile_solo_no_overrides_codegen_creation_executor",
        lambda **kwargs: sentinel_no_overrides,
    )
    monkeypatch.setattr(
        solo_overrides_step_module,
        "compile_solo_overrides_codegen_creation_executor",
        lambda **kwargs: sentinel_overrides,
    )

    root_spell = SimpleNamespace(
        spell_id="root",
        spell_name="root",
        spell_index=SimpleNamespace(current="root"),
        spell=lambda: "instance",
        has_disposal_methods=False,
        disposal_method_names=(),
        is_existing_creation=False,
        _owner_creations=object(),
    )
    model = SimpleNamespace(
        build_kind="construct",
        route_family="many",
        graph_shape=SimpleNamespace(root_spell_id="root"),
        spell_runtime_shape=SimpleNamespace(
            spell_count=1,
            records_by_spell_id={
                "root": SimpleNamespace(
                    spell=root_spell,
                    has_disposal_methods=False,
                )
            },
        ),
    )
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=("generalized_solo_codegen_plan",),
        no_overrides_plan=SimpleNamespace(lane_id="solo_no_overrides"),
        overrides_plan=SimpleNamespace(lane_id="solo_overrides"),
        metadata={"selected_strategy_id": "generalized_solo_codegen_plan"},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={},
    )

    SoloCodegenCreationStrategy().apply(model, plan, creation)

    assert creation.no_overrides_executor is sentinel_no_overrides
    assert creation.overrides_executor is sentinel_overrides
    assert creation.metadata["resolve_route_key"] == "many"
    assert creation.metadata["fast_transient_no_overrides_enabled"] is True
    assert creation.metadata["creation_context_strategy"] == "solo_codegen_creation"
    assert creation.metadata["no_overrides_step_count"] == 1
    assert creation.metadata["override_step_count"] == 1
