"""Direct unit tests for the codegen_creation object layer."""

from types import SimpleNamespace
from typing import Any, Dict, Tuple

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_no_overrides_codegen_creation_strategy as no_overrides_strategy_module
import melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_overrides_codegen_creation_strategy as overrides_strategy_module
import melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_mutation_overrides_codegen_creation_strategy as mutation_strategy_module
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.codegen_creation_discovery_system import (
    CodegenCreationDiscovery,
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.codegen_creation_system import (
    CodegenCreationSystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_creation_context_setup_codegen_creation_strategy import (
    SpellGeneralizedCreationContextSetupCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_mutation_overrides_codegen_creation_strategy import (
    SpellGeneralizedMutationOverridesCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_no_overrides_codegen_creation_strategy import (
    SpellGeneralizedNoOverridesCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_overrides_codegen_creation_strategy import (
    SpellGeneralizedOverridesCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class _CleanupProbe:
    """Simple cleanup double used to prove previous-creation cleanup."""

    def __init__(self) -> None:
        """Start with cleanup not yet called."""
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True


class _CreationStrategyProbe:
    """Minimal creation strategy double for facade tests."""

    def __init__(self, strategy_id: str) -> None:
        """Store the stable strategy id."""
        self.strategy_id = strategy_id

    def apply(
            self,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """Write one visible marker onto the output artifact."""
        _ = spell_codegen_model
        _ = spell_codegen_plan
        spell_codegen_creation.metadata[self.strategy_id] = True


class _StrategyBuilderProbe:
    """Minimal strategy-builder double for creation-system facade tests."""

    def __init__(self, strategies: Tuple[Any, ...]) -> None:
        """Store the strategy tuple returned by resolution."""
        self._strategies = strategies
        self.requested_strategy_ids: Tuple[str, ...] = ()
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True

    def get_strategies(self, strategy_ids: Tuple[str, ...]) -> Tuple[Any, ...]:
        """Return the configured strategies and record the requested ids."""
        self.requested_strategy_ids = strategy_ids
        return self._strategies


class _DiscoveryProbe:
    """Minimal discovery-system double for creation-system facade tests."""

    def __init__(self, discovery: CodegenCreationDiscovery) -> None:
        """Store the discovery result returned during build."""
        self._discovery = discovery
        self.discovered_pair: Tuple[Any, Any] | None = None

    def discover(
            self,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
    ) -> CodegenCreationDiscovery:
        """Return the configured discovery result and record the input pair."""
        self.discovered_pair = (spell_codegen_model, spell_codegen_plan)
        return self._discovery


def test_codegen_creation_discovery_system_selects_generalized_chain_by_default() -> None:
    """The discovery system should choose the full generalized chain for generalized plans."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            mutation_overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_creation_context_setup_codegen_creation",
        "generalized_no_overrides_codegen_creation",
        "generalized_overrides_codegen_creation",
        "generalized_mutation_overrides_codegen_creation",
    )
    assert discovery.discovery_reason == (
        "default_generalized_plan_codegen_creation_chain"
    )


def test_codegen_creation_discovery_system_falls_back_to_no_overrides_chain() -> None:
    """The discovery system should fall back to the no-overrides creation strategy when the plan is not generalized."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=(),
            no_overrides_plan=None,
            overrides_plan=None,
            mutation_overrides_plan=None,
            metadata={"selected_strategy_id": "other_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_no_overrides_codegen_creation",
    )
    assert discovery.discovery_reason == "fallback_no_overrides_creation_strategy"


def test_spell_codegen_strategy_builder_registers_default_order() -> None:
    """The real codegen-creation strategy builder should expose the stable default strategy order."""
    builder = SpellCodegenStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "generalized_creation_context_setup_codegen_creation",
        "generalized_no_overrides_codegen_creation",
        "generalized_overrides_codegen_creation",
        "generalized_mutation_overrides_codegen_creation",
    )
    with pytest.raises(RuntimeError, match="missing strategy 'missing_creation'"):
        builder.get_strategy("missing_creation")


def test_spell_codegen_creation_cleanup_cleans_override_targeting_and_metadata() -> None:
    """The creation container should cleanup owned override-targeting state and clear metadata."""
    override_targeting = _CleanupProbe()
    creation = SpellCodegenCreation(
        selected_strategy_ids=("setup",),
        discovery_reason="reason",
        resolve_route_key="many",
        fast_transient_no_overrides_enabled=True,
        no_overrides_executor=object(),
        no_overrides_executor_signature="sig",
        override_targeting=override_targeting,
        override_no_mutation_plan_signature=("a",),
        override_no_mutation_path_registry=object(),
        override_no_mutation_plan_rows=(),
        override_no_mutation_root_spell_id="root",
        override_no_mutation_spell_lookup={},
        override_no_mutation_empty_shape_key=("k",),
        override_no_mutation_baseline_executor=object(),
        override_mutation_plan_signature=("b",),
        override_mutation_path_registry=object(),
        override_mutation_plan_rows=(),
        override_mutation_root_spell_id="root",
        override_mutation_spell_lookup={},
        override_mutation_empty_shape_key=("m",),
        override_mutation_baseline_executor=object(),
        metadata={"hello": "world"},
    )

    creation.cleanup()

    assert override_targeting.cleanup_called is True
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


def test_codegen_creation_system_build_publishes_creation_and_cleans_previous() -> None:
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


def test_spell_override_targeting_codegen_creation_from_analysis_and_apply_prechecked() -> None:
    """The override-targeting creation artifact should normalize analysis rows and cache single-key applications."""
    artifact = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id="root",
        targets_by_spec={
            "root>svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
            "**svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
                SpellOverrideTargetRef(
                    node_id="dep",
                    param_path_id=2,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
        },
        specificity_by_spec={
            "root>svc": 3,
            "**svc": 1,
        },
    )

    first_map, first_shape = artifact._apply_with_socket_shape_prechecked(
        spell_override={"root>svc": "value"},
    )
    second_map, second_shape = artifact._apply_with_socket_shape_prechecked(
        spell_override={"root>svc": "value"},
    )

    assert len(first_map) == 1
    assert first_shape == (("root", 1, "svc", 0),)
    assert second_map is first_map
    assert second_shape is first_shape


def test_spell_override_targeting_codegen_creation_detects_conflicting_same_specificity_rules() -> None:
    """The override-targeting creation artifact should reject conflicting equal-specificity multi-key applications."""
    artifact = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id="root",
        targets_by_spec={
            "*svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
            "root>svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
        },
        specificity_by_spec={
            "*svc": 2,
            "root>svc": 2,
        },
    )

    with pytest.raises(RuntimeError, match="Conflicting overrides"):
        artifact._apply_with_socket_shape_prechecked(
            spell_override={
                "*svc": "a",
                "root>svc": "b",
            },
        )


def test_creation_context_setup_strategy_resolves_route_key_and_transient_flag() -> None:
    """The setup strategy should derive route key and transient enablement from model and no-overrides plan truth."""
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
        mutation_overrides_plan=None,
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        resolve_route_key=None,
        fast_transient_no_overrides_enabled=False,
        no_overrides_executor=None,
        no_overrides_executor_signature=None,
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

    assert creation.resolve_route_key == "many"
    assert creation.fast_transient_no_overrides_enabled is True
    assert creation.metadata["resolve_route_key"] == "many"
    assert creation.metadata["fast_transient_no_overrides_enabled"] is True


def test_no_overrides_codegen_creation_strategy_publishes_executor_signature_and_metadata(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The no-overrides creation strategy should package the lane executor directly from the generalized lane plan."""
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
        mutation_overrides_plan=None,
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        resolve_route_key=None,
        fast_transient_no_overrides_enabled=False,
        no_overrides_executor=None,
        no_overrides_executor_signature=None,
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
    assert creation.no_overrides_executor_signature == "sig:4"
    assert creation.metadata["no_overrides_lane_id"] == "no_overrides"
    assert creation.metadata["no_overrides_root_spell_id"] == "root"
    assert creation.metadata["no_overrides_step_count"] == 2
    assert creation.metadata["no_overrides_fast_transient_available"] is True


def test_override_targeting_codegen_creation_resolves_and_caches_target_keys() -> None:
    """The override-targeting creation artifact should preserve path/unique/broadcast resolution and caching."""
    artifact = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id="root",
        targets_by_spec={
            "root>svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
            "*svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
            "**svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
                SpellOverrideTargetRef(
                    node_id="dep",
                    param_path_id=2,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
        },
        specificity_by_spec={
            "root>svc": 3,
            "*svc": 2,
            "**svc": 1,
        },
    )

    path_matches, path_level, path_shape = artifact._resolve_targets_for_raw_key(
        "root>svc"
    )
    unique_matches, unique_level, unique_shape = artifact._resolve_targets_for_raw_key(
        "*svc"
    )
    broadcast_matches, broadcast_level, broadcast_shape = artifact._resolve_targets_for_raw_key(
        "**svc"
    )
    cached_matches, cached_level, cached_shape = artifact._resolve_targets_for_raw_key(
        "root>svc"
    )

    assert len(path_matches) == 1
    assert path_level.value == 3
    assert path_shape == (("root", 1, "svc", 0),)
    assert len(unique_matches) == 1
    assert unique_level.value == 2
    assert unique_shape == (("root", 1, "svc", 0),)
    assert len(broadcast_matches) == 2
    assert broadcast_level.value == 1
    assert broadcast_shape == (
        ("dep", 2, "svc", 0),
        ("root", 1, "svc", 0),
    )
    assert cached_matches is path_matches
    assert cached_level is path_level
    assert cached_shape is path_shape


def test_override_targeting_codegen_creation_rejects_missing_and_ambiguous_targets() -> None:
    """The override-targeting creation artifact should fail hard on missing/ambiguous target rules."""
    artifact = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id="root",
        targets_by_spec={
            "*svc": (
                SpellOverrideTargetRef(
                    node_id="root",
                    param_path_id=1,
                    param_name="svc",
                    socket_kind_value=0,
                ),
                SpellOverrideTargetRef(
                    node_id="dep",
                    param_path_id=2,
                    param_name="svc",
                    socket_kind_value=0,
                ),
            ),
        },
        specificity_by_spec={"*svc": 2},
    )

    with pytest.raises(RuntimeError, match="No sockets found for override path"):
        artifact._resolve_targets_for_raw_key("root>missing")
    with pytest.raises(RuntimeError, match="matched 2 sockets"):
        artifact._resolve_targets_for_raw_key("*svc")


def test_override_targeting_codegen_creation_spec_key_rejects_unknown_kind() -> None:
    """The override-targeting creation artifact should reject unsupported parsed target kinds."""
    with pytest.raises(RuntimeError, match="Unsupported TargetSpecKind"):
        SpellOverrideTargetingCodegenCreation._spec_key(
            type("SpecProbe", (), {"kind": "bad", "param_name": "svc", "path": ()})()
        )


def test_overrides_codegen_creation_strategy_publishes_override_route_payload(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The overrides creation strategy should package the non-mutation override route onto the creation artifact."""
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
        mutation_overrides_plan=None,
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        resolve_route_key=None,
        fast_transient_no_overrides_enabled=False,
        no_overrides_executor=None,
        no_overrides_executor_signature=None,
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

    assert creation.override_targeting is not None
    assert creation.override_no_mutation_root_spell_id == "root"
    assert creation.override_no_mutation_path_registry == "PATH_REG"
    assert creation.override_no_mutation_baseline_executor == (
        "override-executor",
        "root",
    )
    assert creation.metadata["override_lane_id"] == "overrides"
    assert creation.metadata["override_root_spell_id"] == "root"
    assert creation.metadata["override_step_count"] == 1


def test_mutation_overrides_codegen_creation_strategy_publishes_mutation_route_payload(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The mutation-overrides creation strategy should package the mutation-aware override route onto the creation artifact."""
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=None,
        overrides_plan=None,
        mutation_overrides_plan=type(
            "LanePlanProbe",
            (),
            {
                "lane_id": "mutation_overrides",
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
        resolve_route_key=None,
        fast_transient_no_overrides_enabled=False,
        no_overrides_executor=None,
        no_overrides_executor_signature=None,
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
        metadata={},
    )
    state = type(
        "ModelProbe",
        (),
        {
            "graph_shape": SimpleNamespace(path_registry="PATH_REG"),
        },
    )()

    monkeypatch.setattr(
        mutation_strategy_module.SharedCompilerExecutions,
        "build_phase11_step_ir_row",
        lambda step, include_override_metadata: {
            "step": step.spell.spell_index.current,
            "include_override_metadata": include_override_metadata,
        },
    )
    monkeypatch.setattr(
        mutation_strategy_module.SharedCompilerExecutions,
        "hash_codegen_signature",
        lambda *parts: ("sig", len(parts)),
    )
    monkeypatch.setattr(
        mutation_strategy_module,
        "compile_overrides_codegen_creation_executor",
        lambda **kwargs: ("mutation-executor", kwargs["root_spell_id"]),
    )

    SpellGeneralizedMutationOverridesCodegenCreationStrategy().apply(
        state,
        plan,
        creation,
    )

    assert creation.override_mutation_root_spell_id == "root"
    assert creation.override_mutation_path_registry == "PATH_REG"
    assert creation.override_mutation_baseline_executor == (
        "mutation-executor",
        "root",
    )
    assert creation.metadata["override_mutation_lane_id"] == "mutation_overrides"
    assert creation.metadata["override_mutation_root_spell_id"] == "root"
    assert creation.metadata["override_mutation_step_count"] == 1


def test_codegen_creation_system_cleanup_cleans_builder_and_drops_owned_refs() -> None:
    """The creation facade cleanup should clean the builder and drop both owned references."""
    system = CodegenCreationSystem()
    builder = _StrategyBuilderProbe(())
    system._strategy_builder = builder
    system._discovery_system = object()

    system.cleanup()

    assert builder.cleanup_called is True
    assert not hasattr(system, "_strategy_builder")
    assert not hasattr(system, "_discovery_system")

