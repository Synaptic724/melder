"""Unit tests porting blueprint-era intent onto the new strategy objects."""

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

import melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_codegen_plan_strategy as generalized_plan_strategy_module
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_contract_analysis import (
    SpellOccurrenceContractAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis import (
    SpellOccurrenceInstanceAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_instance_processor_strategy import (
    SpellOccurrenceInstanceProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_injection_processor_strategy import (
    SpellInjectionProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_order_processor_strategy import (
    SpellOccurrenceOrderProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_override_targeting_processor_strategy import (
    SpellOverrideTargetingProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy import (
    SpellRuntimeProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_codegen_plan_strategy import (
    SpellGeneralizedCodegenPlanStrategy,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpecKind
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)


class _ModelProbe:
    """Minimal mutable model double for processor strategy tests."""

    def __init__(self) -> None:
        """Initialize all strategy-owned sections and summary fields."""
        self.graph_shape = None
        self.order_shape = None
        self.instance_shape = None
        self.contract_shape = None
        self.injection_shape = None
        self.override_targeting_shape = None
        self.spell_runtime_shape = None
        self.node_count = 0
        self.shared_node_count = 0
        self.root_dependency_count = 0
        self.root_positional_override_relevant = False
        self.dependency_arity_histogram = ()
        self.target_spec_count = 0
        self.targeted_socket_count = 0
        self.targeted_spell_count = 0
        self.max_targets_per_spec = 0
        self.max_target_path_depth = 0
        self.override_shape_family = "unclassified"
        self.section_names = lambda: (
            "graph_shape",
            "order_shape",
            "instance_shape",
            "contract_shape",
            "injection_shape",
        )


class _PreviousCleanup:
    """Cleanup double used to verify best-effort replacement cleanup."""

    def __init__(self) -> None:
        """Start with cleanup not yet called."""
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True


class _PathRegistryProbe:
    """Minimal path-registry double for strategy tests."""

    def __init__(self, depths: Dict[int, int]) -> None:
        """Store formatted path names and depths by id."""
        self._depths = depths

    def depth(self, path_id: int) -> int:
        """Return the configured depth for the supplied path id."""
        return self._depths[path_id]

    def format_path(self, path_id: int) -> str:
        """Return a deterministic formatted path string."""
        return "path:{0}".format(path_id)

    def extend_path(self, path_id: int, param_name: str) -> int:
        """Return a deterministic child path id."""
        _ = param_name
        return path_id + 10


class _SpellIndexProbe:
    """Hashable spell-index double for contracted lookup tests."""

    def __init__(self, current: str) -> None:
        """Store current and lineage ids."""
        self.selected_spell_id = current
        self.id = "lineage:{0}".format(current)

    def __hash__(self) -> int:
        """Keep the probe usable as a dictionary key."""
        return hash((self.selected_spell_id, self.id))


def _make_runtime_spell(
        spell_id: str,
        *,
        existence: Existence,
        spell_name: Optional[str] = None,
        is_existing_creation: bool = False,
        call_target: Optional[Any] = None,
) -> Any:
    """Build a minimal spell double for runtime-processor tests."""
    if spell_name is None:
        spell_name = spell_id
    if call_target is None:
        call_target = object()
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_name,
        spell_index=SimpleNamespace(selected_spell_id=spell_id),
        spell=call_target,
        existence=existence,
        is_existing_creation=is_existing_creation,
        is_class_spell=not is_existing_creation,
        is_method_spell=False,
        is_lambda_spell=False,
        has_disposal_methods=False,
        disposal_method_names=(),
        user_created_object=None,
    )


def test_occurrence_order_processor_strategy_ports_occurrence_ordering_intent() -> None:
    """The order processor should derive a deterministic dependency-safe spell order."""
    strategy = SpellOccurrenceOrderProcessorStrategy()
    model = _ModelProbe()
    previous = _PreviousCleanup()
    model.order_shape = previous
    model.graph_shape = SimpleNamespace(
        occurrence_graph={
            ("root", 0): {"dep": [("dep", 1)]},
            ("dep", 1): {"leaf": [("leaf", 2)]},
            ("leaf", 2): {},
        }
    )

    strategy.process(object(), object(), model)

    assert model.order_shape.execution_order == ["leaf", "dep", "root"]
    assert model.node_count == 3
    assert previous.cleanup_called is True


def test_occurrence_order_processor_strategy_falls_back_cleanly_on_cycles() -> None:
    """The order processor should fall back to first-seen occurrences on cyclic graphs."""
    strategy = SpellOccurrenceOrderProcessorStrategy()

    order = strategy._build_execution_order(
        occurrence_graph={
            ("a", 0): {"dep": [("b", 1)]},
            ("b", 1): {"dep": [("a", 0)]},
        },
        fallback_occurrences=(("a", 0), ("b", 1)),
    )

    assert order == ["a", "b"]


def test_occurrence_instance_processor_strategy_ports_instance_and_sharedness_intent() -> None:
    """The instance processor should replace occurrence-plan sharedness and instance-key decisions."""
    strategy = SpellOccurrenceInstanceProcessorStrategy()
    model = _ModelProbe()
    previous = _PreviousCleanup()
    model.instance_shape = previous
    model.graph_shape = SimpleNamespace(
        root_spell_id="root",
        occurrence_graph={
            ("root", 0): {"dep": [("many", 2)]},
            ("shared", 1): {},
            ("many", 2): {},
            ("many", 3): {},
        },
        path_registry=SimpleNamespace(root_path_id=0),
    )
    spellbook = SimpleNamespace(
        _spell_id_pool={
            "root": _make_runtime_spell(
                "root",
                existence=Existence.unique_per_conduit,
            ),
            "shared": _make_runtime_spell(
                "shared",
                existence=Existence.unique,
            ),
            "many": _make_runtime_spell(
                "many",
                existence=Existence.many,
            ),
        }
    )
    spell = SimpleNamespace(_spellbook=spellbook)

    strategy.process(spell, object(), model)

    assert model.instance_shape.root_instance_key == ("root", None)
    assert model.instance_shape.instance_keys_by_spell_id["shared"] == [("shared", None)]
    assert model.instance_shape.instance_keys_by_spell_id["many"] == [
        ("many", 2),
        ("many", 3),
    ]
    assert model.instance_shape.canonical_occurrences_by_spell_id["shared"] == (
        "shared",
        1,
    )
    assert model.node_count == 3
    assert model.shared_node_count == 2
    assert previous.cleanup_called is True


def test_injection_processor_strategy_ports_injection_plan_intent() -> None:
    """The injection processor should derive per-instance injection summaries from occurrence/contract truth."""
    strategy = SpellInjectionProcessorStrategy()
    model = _ModelProbe()
    previous = _PreviousCleanup()
    model.injection_shape = previous
    model.graph_shape = SimpleNamespace(
        root_spell_id="root",
        occurrence_graph={
            ("root", 0): {"deps": [("dep", None), ("dep-2", 5)]},
            ("dep", None): {},
            ("dep-2", 5): {},
        },
    )
    model.instance_shape = SpellOccurrenceInstanceAnalysis(
        instance_keys_by_spell_id={
            "root": [("root", None)],
            "dep": [("dep", None)],
            "dep-2": [("dep-2", 5)],
        },
        canonical_occurrences_by_spell_id={
            "root": ("root", 0),
            "dep": ("dep", None),
        },
        root_instance_key=("root", None),
        shared_spell_ids={"root", "dep"},
    )
    model.contract_shape = SpellOccurrenceContractAnalysis(
        contract_overrides_by_occurrence={
            ("root", 0): {
                "__args__": ("x",),
                "cfg": "payload",
            }
        },
        contract_overrides_by_spell_id={
            "root": [(("root", 0), {"__args__": ("x",), "cfg": "payload"})]
        },
        contract_dependencies_complete=True,
    )
    # The injection processor reads collection-socket truth from the durable
    # phase-3 topology registry on the owning spellbook; a None topology is the
    # documented missing-topology path (no collection params inferred).
    injection_spell = SimpleNamespace(
        _spellbook=SimpleNamespace(
            _spell_system_states=SimpleNamespace(
                get_local_topology_by_id=lambda spell_id: None,
            ),
        ),
    )

    strategy.process(injection_spell, object(), model)

    assert model.root_dependency_count == 2
    assert model.root_positional_override_relevant is True
    assert model.dependency_arity_histogram == (
        (0, 1),
        (2, 1),
    )
    assert model.injection_shape.contract_payload_instance_count == 1
    assert previous.cleanup_called is True


def test_occurrence_contract_processor_strategy_ports_contract_payload_intent() -> None:
    """The contract processor should replace contract payload routing from the old occurrence-plan surface."""
    strategy = SpellOccurrenceContractProcessorStrategy()
    model = _ModelProbe()
    previous = _PreviousCleanup()
    model.contract_shape = previous
    contract = SpellContract(
        spellframe="iface",
        binding_name="primary",
        spell_override={"cfg": "payload"},
    )
    requirements = SimpleNamespace(
        parameters=(
            SimpleNamespace(
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=contract,
                name="svc",
            ),
        )
    )
    consumer_spell = SimpleNamespace(
        spell_id="consumer",
        spell_name="consumer",
        spell_index=SimpleNamespace(selected_spell_id="consumer"),
        is_existing_creation=False,
        spell=object(),
        _compiler_artifact=SimpleNamespace(_requirements=requirements),
    )
    provider_index = _SpellIndexProbe("provider")
    provider_spell = SimpleNamespace(
        spell_id="provider",
        spell_name="provider",
        spell_index=provider_index,
    )
    spellbook = SimpleNamespace(
        _spell_id_pool={"consumer": consumer_spell},
        _lookup_contracted_spells={"peer": {contract.canonical_key: provider_index}},
        _contracted_spells={"peer": {provider_index: provider_spell}},
        _aetheric_frame_configuration=SimpleNamespace(system_state=SystemState.dynamic),
    )
    consumer_spell._spellbook = spellbook
    model.graph_shape = SimpleNamespace(
        occurrence_graph={("consumer", 0): {}},
        path_registry=_PathRegistryProbe({0: 0, 10: 1}),
    )

    strategy.process(consumer_spell, object(), model)

    assert model.contract_shape.contract_dependencies_complete is True
    assert model.contract_shape.contract_payload_count == 1
    assert model.contract_shape.contract_overrides_by_occurrence == {
        ("provider", 10): {"cfg": "payload"}
    }
    assert model.contract_payload_count == 1
    assert previous.cleanup_called is True


def test_occurrence_contract_processor_strategy_allows_missing_providers_only_in_dynamic_mode() -> None:
    """Missing SpellContract providers should stay incomplete in dynamic mode and fail in automatic mode."""
    strategy = SpellOccurrenceContractProcessorStrategy()
    contract = SpellContract(
        spellframe="iface",
        binding_name="primary",
        spell_override=("x", "y"),
    )
    requirements = SimpleNamespace(
        parameters=(
            SimpleNamespace(
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=contract,
                name="svc",
            ),
        )
    )
    consumer_spell = SimpleNamespace(
        spell_id="consumer",
        spell_name="consumer",
        spell_index=SimpleNamespace(selected_spell_id="consumer"),
        is_existing_creation=False,
        spell=object(),
        _compiler_artifact=SimpleNamespace(_requirements=requirements),
    )
    dynamic_spellbook = SimpleNamespace(
        _spell_id_pool={"consumer": consumer_spell},
        _lookup_contracted_spells={},
        _contracted_spells={},
        _aetheric_frame_configuration=SimpleNamespace(system_state=SystemState.dynamic),
    )
    consumer_spell._spellbook = dynamic_spellbook
    overrides_by_occurrence: Dict[Tuple[str, int], Dict[str, Any]] = {}
    overrides_by_spell_id: Dict[str, List[Tuple[Tuple[str, int], Dict[str, Any]]]] = {}

    complete = strategy._compile_contract_overrides_for_occurrence(
        occurrence=("consumer", 0),
        overrides_by_occurrence=overrides_by_occurrence,
        overrides_by_spell_id=overrides_by_spell_id,
        spell_lookup=dynamic_spellbook._spell_id_pool,
        spellbook=dynamic_spellbook,
        path_registry=_PathRegistryProbe({0: 0}),
    )

    assert complete is False
    assert overrides_by_occurrence == {}
    assert overrides_by_spell_id == {}

    automatic_spellbook = SimpleNamespace(
        _spell_id_pool={"consumer": consumer_spell},
        _lookup_contracted_spells={},
        _contracted_spells={},
        _aetheric_frame_configuration=SimpleNamespace(system_state=SystemState.automatic),
    )
    consumer_spell._spellbook = automatic_spellbook

    with pytest.raises(Exception, match="could not be resolved"):
        strategy._compile_contract_overrides_for_occurrence(
            occurrence=("consumer", 0),
            overrides_by_occurrence={},
            overrides_by_spell_id={},
            spell_lookup=automatic_spellbook._spell_id_pool,
            spellbook=automatic_spellbook,
            path_registry=_PathRegistryProbe({0: 0}),
        )


def test_override_targeting_processor_strategy_ports_patch_map_target_rows() -> None:
    """The override-targeting processor should derive path, unique, and broadcast target rows from rooted sockets."""
    strategy = SpellOverrideTargetingProcessorStrategy()
    model = _ModelProbe()
    previous = _PreviousCleanup()
    model.override_targeting_shape = previous
    root_blueprint = SimpleNamespace(
        socket_refs=(
            SimpleNamespace(
                node_id="root",
                param_path_id=1,
                param_name="svc",
                socket_kind=SimpleNamespace(value=SocketKind.NORMAL.value),
            ),
            SimpleNamespace(
                node_id="dep",
                param_path_id=2,
                param_name="svc",
                socket_kind=SimpleNamespace(value=SocketKind.NORMAL.value),
            ),
        ),
        path_registry=_PathRegistryProbe({1: 1, 2: 2}),
        ensure_dag_index_built=lambda: None,
    )
    model.override_targeting_shape = previous

    strategy.process(
        object(),
        SimpleNamespace(_root_blueprint_phase5=root_blueprint),
        model,
    )

    assert model.target_spec_count == 4
    assert model.targeted_socket_count == 2
    assert model.targeted_spell_count == 2
    assert model.max_targets_per_spec == 2
    assert model.max_target_path_depth == 2
    assert model.override_shape_family == "deep"
    assert previous.cleanup_called is True


def test_override_targeting_processor_strategy_helper_methods_port_patchmap_key_rules() -> None:
    """Override-targeting helpers should preserve the old target-key and family classification rules."""
    assert SpellOverrideTargetingProcessorStrategy._build_target_key(
        kind=TargetSpecKind.BROADCAST,
        param_name="svc",
    ) == "**svc"
    assert SpellOverrideTargetingProcessorStrategy._build_target_key(
        kind=TargetSpecKind.UNIQUE,
        param_name="svc",
    ) == "*svc"
    with pytest.raises(RuntimeError, match="Unsupported override target key kind"):
        SpellOverrideTargetingProcessorStrategy._build_target_key(
            kind="bad",
            param_name="svc",
        )

    assert SpellOverrideTargetingProcessorStrategy._override_shape_family(
        target_spec_count=0,
        max_targets_per_spec=0,
        max_target_path_depth=0,
    ) == "none"
    assert SpellOverrideTargetingProcessorStrategy._override_shape_family(
        target_spec_count=1,
        max_targets_per_spec=1,
        max_target_path_depth=1,
    ) == "simple"
    assert SpellOverrideTargetingProcessorStrategy._override_shape_family(
        target_spec_count=2,
        max_targets_per_spec=3,
        max_target_path_depth=1,
    ) == "wide"
    assert SpellOverrideTargetingProcessorStrategy._override_shape_family(
        target_spec_count=2,
        max_targets_per_spec=2,
        max_target_path_depth=4,
    ) == "deep"


def test_runtime_processor_strategy_ports_execution_runtime_rows() -> None:
    """The runtime processor should derive per-spell runtime rows from ordered spell ids."""
    strategy = SpellRuntimeProcessorStrategy()
    model = _ModelProbe()
    previous = _PreviousCleanup()
    model.spell_runtime_shape = previous
    model.order_shape = SimpleNamespace(
        execution_order=["dep", "root"],
    )
    spellbook = SimpleNamespace(
        _spell_id_pool={
            "dep": _make_runtime_spell("dep", existence=Existence.unique),
            "root": _make_runtime_spell(
                "root",
                existence=Existence.unique_per_conduit,
            ),
        }
    )
    spell = SimpleNamespace(_spellbook=spellbook)

    strategy.process(spell, object(), model)

    assert model.spell_runtime_shape.spell_count == 2
    assert tuple(model.spell_runtime_shape.records_by_spell_id.keys()) == (
        "dep",
        "root",
    )
    assert previous.cleanup_called is True


def test_runtime_processor_strategy_falls_back_to_graph_order_when_order_shape_is_missing() -> None:
    """The runtime processor should derive spell order from graph visibility when no order section exists."""
    strategy = SpellRuntimeProcessorStrategy()
    model = _ModelProbe()
    model.graph_shape = SimpleNamespace(
        occurrence_graph={
            ("root", 0): {},
            ("dep", 1): {},
            ("dep", 2): {},
        }
    )
    spellbook = SimpleNamespace(
        _spell_id_pool={
            "root": _make_runtime_spell("root", existence=Existence.unique),
            "dep": _make_runtime_spell("dep", existence=Existence.unique_per_conduit),
        }
    )
    spell = SimpleNamespace(_spellbook=spellbook)

    strategy.process(spell, object(), model)

    assert tuple(model.spell_runtime_shape.records_by_spell_id.keys()) == (
        "root",
        "dep",
    )


def test_runtime_processor_strategy_raises_when_visible_spell_id_is_missing() -> None:
    """The runtime processor should fail hard if graph/order truth references a spellbook-missing spell id."""
    strategy = SpellRuntimeProcessorStrategy()
    model = _ModelProbe()
    model.order_shape = SimpleNamespace(execution_order=["missing"])
    spellbook = SimpleNamespace(_spell_id_pool={})
    spell = SimpleNamespace(_spellbook=spellbook)

    with pytest.raises(RuntimeError, match="could not resolve spell_id 'missing'"):
        strategy.process(spell, object(), model)


def test_generalized_codegen_plan_strategy_ports_execution_plan_builder_intent(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The generalized planner strategy should delegate to the lane builder for both planner outputs."""
    state = SimpleNamespace(
        section_names=lambda: (
            "graph_shape",
            "order_shape",
            "instance_shape",
        )
    )
    artifact = object()
    plan = SpellCodegenPlan(
        processor_strategy_ids=("processor_a",),
        plan_strategy_ids=(),
        no_overrides_plan=None,
        overrides_plan=None,
        metadata={},
    )
    build_calls: List[Any] = []

    class _BuilderStub:
        """Minimal generalized lane-plan builder probe."""

        def __init__(self, *, state: Any, plan_variant: Any) -> None:
            """Record the requested planner variant."""
            build_calls.append(("init", plan_variant, state))
            self._plan_variant = plan_variant

        def build_dual(self) -> Any:
            """Return both lane payloads from one recorded dual build."""
            build_calls.append(("build_dual", self._plan_variant))
            return (
                "lane:{0}".format(
                    generalized_plan_strategy_module
                    .SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES
                ),
                "lane:{0}".format(
                    generalized_plan_strategy_module
                    .SpellGeneralizedCodegenPlanVariant.OVERRIDES
                ),
            )

    monkeypatch.setattr(
        generalized_plan_strategy_module,
        "SpellGeneralizedCodegenPlanBuilder",
        _BuilderStub,
    )

    SpellGeneralizedCodegenPlanStrategy().apply(state, artifact, plan)

    # The strategy now performs the SINGLE-PASS dual-variant build: one
    # builder init plus one build_dual call replaces the former two-build
    # protocol (patch lane generalized_singleton_specialization_2026_07_01).
    assert build_calls == [
        ("init", generalized_plan_strategy_module.SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES, state),
        ("build_dual", generalized_plan_strategy_module.SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES),
    ]
    assert plan.no_overrides_plan == "lane:no_overrides"
    assert plan.overrides_plan == "lane:overrides"
    assert plan.metadata["selected_strategy_id"] == "generalized_codegen_plan"
    assert plan.metadata["discovery_reason"] == "default_generalized_model_native_strategy"
    assert plan.metadata["model_sections"] == (
        "graph_shape",
        "order_shape",
        "instance_shape",
    )
