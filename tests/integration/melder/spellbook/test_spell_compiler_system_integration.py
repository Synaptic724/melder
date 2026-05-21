"""Integration tests for SpellCompiler and SpellCompilerSystem current surfaces."""

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.aether import Aether
from melder.aether.spellbook.existence.existence import Existence
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
def reset_aether_singleton_for_spell_compiler_integration() -> None:
    """Reset Aether around each compiler integration test."""
    reset_aether_runtime()
    yield
    reset_aether_runtime()


def _bind_service_collection(spellbook: Spellbook) -> tuple[str, str]:
    """Bind two IService implementations for integration collection scenarios."""
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
    "builder",
    [
        "leaf",
        "single",
        "collection",
        "spellmap",
    ],
)
def test_integration_spell_compiler_system_run_structural_phases_supports_core_shapes(
        builder: str,
) -> None:
    """run_structural_phases should work end-to-end for the core compiler surface shapes."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        if builder == "leaf":
            spell_id = spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
        elif builder == "single":
            spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

            class Consumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            spell_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        elif builder == "collection":
            _bind_service_collection(spellbook)

            class Consumer:
                def __init__(self, services: list[IService]) -> None:
                    self.services = services

            spell_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        else:
            spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")

            class Consumer:
                def __init__(self, config: BasicConfig = SpellMap(BasicConfig)) -> None:
                    self.config = config

            spell_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")

        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases(compiler_system, spellbook, spell)

        assert spell.requirements is not None
        assert spell.symbolic_graph is not None
        assert spell.resolution_frame is not None
        assert spell.validation_result_phase4 is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(
    "builder",
    [
        "leaf",
        "single",
        "collection",
        "spellmap",
    ],
)
def test_integration_spell_compiler_system_run_all_phases_supports_core_shapes(
        builder: str,
) -> None:
    """run_all_phases should work end-to-end for core integration shapes."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-run-all-{0}".format(builder)
    try:
        if builder == "leaf":
            spell_id = spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
        elif builder == "single":
            spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

            class Consumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            spell_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        elif builder == "collection":
            _bind_service_collection(spellbook)

            class Consumer:
                def __init__(self, services: list[IService]) -> None:
                    self.services = services

            spell_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        else:
            spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")

            class Consumer:
                def __init__(self, config: BasicConfig = SpellMap(BasicConfig)) -> None:
                    self.config = config

            spell_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")

        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_all_phases(compiler_system, spellbook, spell, conduit_id)

        conduit_state = spellbook._spell_system_states.get_conduit_resolution_state(conduit_id)
        assert conduit_state.get_spell_validity(spell_id) is SpellValidity.valid
        assert spell._compiler_artifact._execution_plan_phase11_no_overrides is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_full_pipeline_then_meld_returns_root_instance() -> None:
    """A full compiler-system pipeline should produce a meldable instance for a single dependency graph."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-meld-single"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_all_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        conduit = spellbook.conjure(name="root")
        try:
            result = conduit.meld(spell=consumer_id)
            assert isinstance(result, Consumer)
            assert isinstance(result.service, BasicService)
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_full_pipeline_then_meld_returns_collection_instance() -> None:
    """A full compiler-system pipeline should preserve collection DI through meld."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-meld-collection"
    try:
        _bind_service_collection(spellbook)

        class Consumer:
            def __init__(self, services: list[IService]) -> None:
                self.services = services

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_all_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        conduit = spellbook.conjure(name="root")
        try:
            result = conduit.meld(spell=consumer_id)
            assert isinstance(result, Consumer)
            assert len(result.services) == 2
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_full_pipeline_then_meld_returns_spellmap_instance() -> None:
    """A full compiler-system pipeline should preserve SpellMap default resolution through meld."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-meld-spellmap"
    try:
        spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, config: BasicConfig = SpellMap(BasicConfig)) -> None:
                self.config = config

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_all_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        conduit = spellbook.conjure(name="root")
        try:
            result = conduit.meld(spell=consumer_id)
            assert isinstance(result, Consumer)
            assert isinstance(result.config, BasicConfig)
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_post_conjure_local_phases_scope_to_new_target() -> None:
    """Local compiler phases should operate on a post-conjure newly bound target only."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        conduit_id = conduit._id
        try:
            spellbook.begin_transaction("bind")
            class Consumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
            spellbook.end_transaction("bind")
            consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
            assert consumer_spell is not None

            run_structural_phases(compiler_system, spellbook, consumer_spell)
            run_local_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)

            assert consumer_spell._compiler_artifact._entire_dag_blueprint_phase5 is not None
            assert set(consumer_spell._compiler_artifact._entire_dag_blueprint_phase5.keys()) == {consumer_id}
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_post_conjure_local_plan_phases_build_for_new_target_only() -> None:
    """Local post-conjure targets should build plan phases without touching unrelated live spells."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        conduit_id = conduit._id
        try:
            spellbook.begin_transaction("bind")
            class Consumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
            spellbook.end_transaction("bind")
            consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
            assert consumer_spell is not None

            run_structural_phases(compiler_system, spellbook, consumer_spell)
            run_local_foundational_phases(compiler_system, spellbook, consumer_spell, conduit_id)
            run_plan_phases(compiler_system, spellbook, consumer_spell)

            artifact = consumer_spell._compiler_artifact
            assert artifact._occurrence_plan_phase8 is not None
            assert artifact._injection_plan_phase9 is not None
            assert artifact._execution_plan_phase11_no_overrides is not None
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_local_scope_helpers_work_after_post_conjure_phase5() -> None:
    """Local scope helper methods should work after local post-conjure Phase 5."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        conduit_id = conduit._id
        try:
            spellbook.begin_transaction("bind")
            class Consumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
            spellbook.end_transaction("bind")
            consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
            assert consumer_spell is not None

            run_structural_phases(compiler_system, spellbook, consumer_spell)
            compiler_system.run_phase_root_blueprints_local(spellbook, consumer_spell, conduit_id)

            assert consumer_id in compiler_system.get_local_resolution_scoped_spell_ids(consumer_spell)
            assert consumer_id in compiler_system.get_local_resolution_scoped_root_ids(consumer_spell)
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_local_scope_spell_ids_include_dependency_closure() -> None:
    """Local Phase 5 should expose both the target spell id and its dependency closure."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        conduit_id = conduit._id
        try:
            spellbook.begin_transaction("bind")

            class Consumer:
                def __init__(self, service: BasicService) -> None:
                    self.service = service

            consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
            spellbook.end_transaction("bind")
            consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
            assert consumer_spell is not None

            run_structural_phases(compiler_system, spellbook, consumer_spell)
            compiler_system.run_phase_root_blueprints_local(spellbook, consumer_spell, conduit_id)

            assert len(compiler_system.get_local_resolution_scoped_spell_ids(consumer_spell)) >= 2
        finally:
            conduit.cleanup()
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_phase6_updates_conduit_state_for_root_and_dependency() -> None:
    """Full validation should publish valid conduit state for both root and dependency ids."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-phase6-state"
    try:
        service_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_all_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        conduit_state = spellbook._spell_system_states.get_conduit_resolution_state(conduit_id)
        assert conduit_state.get_spell_validity(consumer_id) is SpellValidity.valid
        assert conduit_state.get_root_validity(consumer_id) is SpellValidity.valid
        assert conduit_state.get_spell_validity(service_id) is SpellValidity.valid
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_run_all_phases_keeps_root_blueprint_available() -> None:
    """A full run should leave the root blueprint available for downstream runtime use."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-root-blueprint"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_all_phases(compiler_system, spellbook, consumer_spell, conduit_id)

        assert consumer_spell._compiler_artifact._root_blueprint_phase5 is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_phase7_registers_live_revalidator() -> None:
    """Phase 7 should install a live revalidator on the real change-control manager."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-phase7"
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


def test_integration_spell_compiler_system_root_identity_helper_reflects_live_phase5_state() -> None:
    """Root identity helper should report a real root as a root after Phase 5."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-root-identity"
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


def test_integration_spell_compiler_direct_compiler_structural_phases_work_on_live_spellbook() -> None:
    """Direct SpellCompiler structural phases should work on a live Spellbook spell."""
    spellbook = make_spellbook()
    compiler = SpellCompiler()
    try:
        spell_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")
        spell = get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        run_structural_phases_with_compiler(compiler, spellbook, spell)

        assert spell.requirements is not None
        assert spell.symbolic_graph is not None
        assert spell.resolution_frame is not None
    finally:
        spellbook.cleanup()


def test_integration_spell_compiler_system_clear_phase5_artifacts_then_rebuilds() -> None:
    """Clearing Phase 5 artifacts should still allow a full rebuild through the compiler system."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    conduit_id = "integration-rebuild-phase5"
    try:
        spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_all_phases(compiler_system, spellbook, consumer_spell, conduit_id)
        compiler_system.clear_phase5_artifacts(consumer_spell)

        assert consumer_spell._compiler_artifact._root_blueprint_phase5 is None

        compiler_system.run_phase_root_blueprints(spellbook, consumer_spell, conduit_id)
        assert consumer_spell._compiler_artifact._root_blueprint_phase5 is not None
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def test_integration_spell_compiler_system_cleanup_phase_artifacts_preserves_dependency_state() -> None:
    """cleanup_phase_artifacts should clear structural artifacts without losing spell dependency truth."""
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        service_id = spellbook.bind(spell=BasicService, existence=Existence.unique, permissions="create")

        class Consumer:
            def __init__(self, service: BasicService) -> None:
                self.service = service

        consumer_id = spellbook.bind(spell=Consumer, existence=Existence.unique, permissions="create")
        consumer_spell = get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        run_structural_phases(compiler_system, spellbook, consumer_spell)
        compiler_system.cleanup_phase_artifacts(consumer_spell)

        assert consumer_spell._compiler_artifact._requirements is None
        assert consumer_spell._compiler_artifact._symbolic_graph is None
        assert consumer_spell._compiler_artifact._resolution_frame is None
        assert set(consumer_spell.dependencies) == {service_id}
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()
