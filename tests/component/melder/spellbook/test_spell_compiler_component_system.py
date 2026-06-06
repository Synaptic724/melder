"""Component tests for SpellCompiler and SpellCompilerSystem on current surfaces."""

from typing import Optional

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_compiler import SpellCompiler
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests.component.melder.spellbook.spell_compiler_runtime_test_support import (
    get_spell_by_version_id,
    make_spellbook,
    reset_aether_runtime,
    run_all_phases,
    run_foundational_phases,
    run_local_foundational_phases,
    run_plan_phases,
    run_structural_phases,
    run_structural_phases_with_compiler,
)
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_spell_compiler_component() -> None:
    """Reset Aether around each compiler component test."""
    reset_aether_runtime()
    yield
    reset_aether_runtime()


def _bind_basic_service_pair(spellbook: Spellbook) -> tuple[str, str]:
    """Bind two IService implementations for collection and frame tests."""
    class ServiceA:
        pass

    class ServiceB:
        pass

    service_a_id = spellbook.bind(
        spell=ServiceA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="a",
    )
    service_b_id = spellbook.bind(
        spell=ServiceB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="b",
    )
    return service_a_id, service_b_id


@pytest.mark.parametrize(
    ("builder", "expected_count", "expected_shape"),
    [
        ("leaf", 0, None),
        ("single", 1, "single"),
        ("collection", 1, "collection"),
        ("spellmap", 1, "spellmap"),
        ("contract", 1, "contract"),
    ],
)
def test_component_spell_compiler_system_structural_entry_surfaces(
        builder: str,
        expected_count: int,
        expected_shape: Optional[str],
) -> None:
    """Current compiler surfaces should build structural artifacts for core DI shapes."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        if builder == "leaf":
            class Leaf:
                pass

            spell_id = spellbook.bind(
                spell=Leaf,
                existence=Existence.unique,
                permissions="create",
            )
        elif builder == "single":
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )

            class SingleConsumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            spell_id = spellbook.bind(
                spell=SingleConsumer,
                existence=Existence.unique,
                permissions="create",
            )
        elif builder == "collection":
            _bind_basic_service_pair(spellbook)

            class CollectionConsumer:
                def __init__(self, services: list[IService]) -> None:
                    self.services = services

            spell_id = spellbook.bind(
                spell=CollectionConsumer,
                existence=Existence.unique,
                permissions="create",
            )
        elif builder == "spellmap":
            spellbook.bind(
                spell=BasicConfig,
                existence=Existence.unique,
                permissions="create",
            )

            class SpellMapConsumer:
                def __init__(self, config: BasicConfig = SpellMap(BasicConfig)) -> None:
                    self.config = config

            spell_id = spellbook.bind(
                spell=SpellMapConsumer,
                existence=Existence.unique,
                permissions="create",
            )
        elif builder == "contract":
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="primary",
            )

            class ContractConsumer:
                def __init__(
                    self,
                    service: SpellContract = SpellContract(
                        spellframe=IService,
                        binding_name="primary",
                    ),
                ) -> None:
                    self.service = service

            spell_id = spellbook.bind(
                spell=ContractConsumer,
                existence=Existence.unique,
                permissions="create",
            )
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)

        assert spell._compiler_artifact._requirements is not None
        assert spell._compiler_artifact._symbolic_graph is not None
        assert spell._compiler_artifact._resolution_frame is not None
        assert spell._compiler_artifact._validation_result_phase4 is not None
        assert spell._compiler_artifact._validated_phase4 is True
        assert len(spell.requirements.parameters) == expected_count
        if expected_shape is None:
            assert spell.dependencies == []
        elif expected_shape == "single":
            assert len(spell.dependencies) == 1
        elif expected_shape == "collection":
            assert len(spell.dependencies) >= 2
        elif expected_shape == "spellmap":
            assert len(spell.dependencies) == 1
        elif expected_shape == "contract":
            assert spell.dependencies == []
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_direct_structural_phases_match_system_surfaces() -> None:
    """Direct SpellCompiler structural execution should work on real spell and artifact state."""
    spellbook = make_spellbook()
    compiler = SpellCompiler()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases_with_compiler(compiler, spellbook, spell)

        assert spell._compiler_artifact._requirements is not None
        assert spell._compiler_artifact._symbolic_graph is not None
        assert spell._compiler_artifact._resolution_frame is not None
        assert spell._compiler_artifact._validation_result_phase4 is not None
    finally:
        spellbook.cleanup()


def test_component_spell_compiler_system_phase3_records_single_dependency_state() -> None:
    """Phase 3 should record direct dependency state for single DI."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)

        assert set(consumer_spell.dependencies) == {service_id}
        state = consumer_spell.system_state
        assert state is not None
        assert state.direct_dependencies == {service_id}
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase3_records_collection_dependencies() -> None:
    """Phase 3 should record collection DI dependencies for list[Frame]."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        service_a_id, service_b_id = _bind_basic_service_pair(spellbook)

        class Consumer:
            def __init__(self, services: list[IService]) -> None:
                self.services = services

        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)

        assert set(consumer_spell.dependencies) == {service_a_id, service_b_id}
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase3_records_spellmap_dependency() -> None:
    """Phase 3 should resolve SpellMap defaults through current compiler surfaces."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        config_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )

        class Consumer:
            def __init__(self, config: BasicConfig = SpellMap(BasicConfig)) -> None:
                self.config = config

        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)

        assert set(consumer_spell.dependencies) == {config_id}
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(
    ("default_value", "expected_kind"),
    [
        (SpellContract(spellframe=IService, binding_name="primary"), SocketKind.SPELL_CONTRACT),
    ],
)
def test_component_spell_compiler_system_phase3_records_contract_topology_only(
        default_value,
        expected_kind: SocketKind,
) -> None:
    """Contract sockets should appear in topology without adding DI dependencies."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        class Consumer:
            def __init__(self, socket=default_value) -> None:
                self.socket = socket

        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)

        assert consumer_spell.dependencies == []
        topology = consumer_spell._spell_system_states.get_local_topology(
            consumer_spell.spell_index,
        )
        assert topology is not None
        sockets = topology.get_sockets_for_param("socket")
        assert len(sockets) == 1
        assert sockets[0].socket_kind is expected_kind
        assert sockets[0].target_spell_ids == ()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase4_marks_healthy_spell_validated() -> None:
    """Phase 4 should mark a healthy spell validated and not broken."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)

        assert spell.validation_result_phase4 is not None
        assert spell._compiler_artifact._validated_phase4 is True
        assert spell.is_broken is False
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase4_preserves_required_hole_as_non_broken() -> None:
    """Phase 4 should surface required-hole diagnostics without breaking the spell."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        class NeedsInput:
            def __init__(self, value) -> None:
                self.value = value

        spell_id = spellbook.bind(
            spell=NeedsInput,
            existence=Existence.unique,
            permissions="create",
        )
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)

        assert spell.validation_result_phase4 is not None
        assert spell.is_broken is False
        assert spell._compiler_artifact._validated_phase4 is True
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase5_frame_wide_attaches_root_blueprint_and_index() -> None:
    """Frame-wide Phase 5 should attach root blueprint and system index."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase5"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        artifact = consumer_spell._compiler_artifact
        assert artifact._root_blueprint_phase5 is not None
        assert artifact._spell_system_index_phase5 is not None
        assert artifact._entire_dag_blueprint_phase5 is not None
        assert consumer_id in artifact._entire_dag_blueprint_phase5
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase5_local_scopes_to_dependency_closure() -> None:
    """Local Phase 5 should exclude unrelated visible spells from scoped artifacts."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase5-local"
    try:
        class Outside:
            pass

        service_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        outside_id = spellbook.bind(spell=Outside, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        for spell in list(spellbook._spells.values()):
            run_structural_phases(compiler_system, spellbook, spell)

        run_local_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        artifact = consumer_spell._compiler_artifact
        assert artifact._spell_system_index_phase5.get_node(consumer_id) is not None
        assert artifact._spell_system_index_phase5.get_node(service_id) is not None
        assert artifact._spell_system_index_phase5.get_node(outside_id) is None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase6_frame_wide_updates_conduit_state() -> None:
    """Frame-wide Phase 6 should publish valid spell and root state to the conduit resolution state."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase6"
    try:
        spell_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)
        run_foundational_phases(compiler_system, spellbook, spell, conduit_id)

        conduit_state = spellbook._spell_system_states.get_conduit_resolution_state(conduit_id)
        assert conduit_state.get_spell_validity(spell_id) is SpellValidity.valid
        assert conduit_state.get_root_validity(spell_id) is SpellValidity.valid
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase6_local_scopes_results_to_target_closure() -> None:
    """Local Phase 6 should publish results only to the scoped dependency closure."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase6-local"
    try:
        class Outside:
            pass

        service_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=Outside, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        service_spell = get_spell_by_version_id(spellbook, service_id)
        assert consumer_spell is not None
        assert service_spell is not None

        for spell in list(spellbook._spells.values()):
            run_structural_phases(compiler_system, spellbook, spell)

        compiler_system.run_phase_root_blueprints_local(spellbook, consumer_spell, conduit_id)
        compiler_system.run_phase_system_validation_local(spellbook, consumer_spell, conduit_id)

        assert consumer_spell.validation_result_phase6 is not None
        assert service_spell.validation_result_phase6 is consumer_spell.validation_result_phase6
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase7_frame_wide_registers_revalidator() -> None:
    """Frame-wide Phase 7 should register a conduit revalidator on the live change-control manager."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase7"
    try:
        spell_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)
        run_foundational_phases(compiler_system, spellbook, spell, conduit_id)

        manager = Spellbook._aether._get_change_control_manager(spellbook._aetheric_frame)
        assert conduit_id in manager._revalidate_fn_by_conduit
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase7_local_registers_revalidator() -> None:
    """Local Phase 7 should register a conduit revalidator on the live change-control manager."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase7-local"
    try:
        spell_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)
        compiler_system.run_phase_root_blueprints_local(spellbook, spell, conduit_id)
        compiler_system.run_phase_change_control_local(spellbook, spell, conduit_id)

        manager = Spellbook._aether._get_change_control_manager(spellbook._aetheric_frame)
        assert conduit_id in manager._revalidate_fn_by_conduit
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase8_builds_occurrence_plan() -> None:
    """Phase 8 should publish occurrence graph analysis on current compiler surfaces."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase8"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        compiler_system.run_phase_occurrence_plan(spellbook, consumer_spell)

        assert consumer_spell._compiler_artifact._occurrence_graph_analysis is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase8_occurrence_plan_root_identity_matches_target() -> None:
    """The occurrence graph analysis should carry the target spell id as its root identity."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase8-root-id"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        compiler_system.run_phase_occurrence_plan(spellbook, consumer_spell)

        assert (
            consumer_spell._compiler_artifact._occurrence_graph_analysis.root_spell_id
            == consumer_id
        )
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase9_builds_injection_plan() -> None:
    """Phase 9 should publish a fitted codegen model after occurrence analysis."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase9"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        compiler_system.run_phase_occurrence_plan(spellbook, consumer_spell)
        compiler_system.run_phase_injection_plan(consumer_spell)

        artifact = consumer_spell._compiler_artifact
        model = artifact._spell_codegen_model
        assert model is not None
        assert model.graph_shape is artifact._occurrence_graph_analysis
        assert model.injection_shape is not None
        assert model.injection_shape.root_spell_id == consumer_id
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize("builder", ["override"])
def test_component_spell_compiler_system_phase10_builds_codegen_plan_lanes(
        builder: str,
) -> None:
    """Phase 10 should publish planner-owned generalized lane plans."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase10-{0}".format(builder)
    try:
        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        run_plan_phases(compiler_system, spellbook, consumer_spell)

        artifact = consumer_spell._compiler_artifact
        plan = artifact._spell_codegen_plan
        assert plan is not None
        assert plan.no_overrides_plan is not None
        assert plan.overrides_plan is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase11_builds_execution_plans() -> None:
    """Phase 11 should publish the compiler-owned codegen creation artifact."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase11"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        run_plan_phases(compiler_system, spellbook, consumer_spell)

        artifact = consumer_spell._compiler_artifact
        creation = artifact._spell_codegen_creation
        assert creation is not None
        assert creation.resolve_route_key is not None
        assert creation.no_overrides_executor is not None
        assert creation.no_overrides_executor_signature is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_phase10_no_overrides_plan_root_identity_matches_target() -> None:
    """The no-overrides generalized lane plan should stay rooted on the target spell id."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-phase11-root-id"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        run_plan_phases(compiler_system, spellbook, consumer_spell)

        artifact = consumer_spell._compiler_artifact
        plan = artifact._spell_codegen_plan
        assert plan is not None
        assert plan.no_overrides_plan is not None
        assert plan.no_overrides_plan.root_spell_id == consumer_id
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()
@pytest.mark.parametrize(
    "helper_name",
    [
        "get_local_resolution_scoped_spell_ids",
        "get_local_resolution_scoped_root_ids",
    ],
)
def test_component_spell_compiler_system_local_scope_helpers_have_real_phase5_inputs(
        helper_name: str,
) -> None:
    """Local scope helpers should work against real local Phase 5 artifacts."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-local-scope"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        for spell in list(spellbook._spells.values()):
            run_structural_phases(compiler_system, spellbook, spell)
        compiler_system.run_phase_root_blueprints_local(spellbook, consumer_spell, conduit_id)

        result = getattr(compiler_system, helper_name)(consumer_spell)
        assert result
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_component_spell_compiler_system_root_identity_helper_reflects_live_phase5_state() -> None:
    """The root identity helper should return True for the live root and a bool for a dependency."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "component-root-identity"
    try:
        service_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        service_spell = get_spell_by_version_id(spellbook, service_id)
        assert consumer_spell is not None
        assert service_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        run_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        assert compiler_system.is_current_spell_phase5_root(consumer_spell) is True
        assert isinstance(compiler_system.is_current_spell_phase5_root(service_spell), bool)
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()
