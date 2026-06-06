from typing import Optional

import pytest
import tests.component.melder.spellbook.compiler_test_helpers as compiler_test_helpers

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spell() -> None:
    """
    Purpose:
        Ensure component Spell tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_component_spell_symbolic_graph_records_dependency_shapes() -> None:
    """
    Purpose:
        Validate Phase 2 symbolic graph records DI shapes and metadata.
    Contract:
        - Parameters are classified into expected DI shapes.
        - Optional and collection flags match the parameter signatures.
    Returns:
        None.
    Raises:
        AssertionError: If symbolic dependency metadata is incorrect.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell with mixed DI and plain parameters.
        Contract:
            - Declares required, optional, collection, and plain parameters.
        Args:
            service: Required BasicService dependency.
            optional_service: Optional BasicService dependency.
            services: Collection of IService implementations.
            count: Plain parameter with a default.
        """
        def __init__(
            self,
            service: BasicService,
            services: list[IService],
            optional_service: Optional[BasicService] = None,
            count: int = 1,
        ) -> None:
            """
            Purpose:
                Capture injected dependencies and plain parameters.
            Contract:
                - Stores constructor inputs for diagnostics.
            Args:
                service: Required BasicService dependency.
                optional_service: Optional BasicService dependency.
                services: Collection of IService implementations.
                count: Plain parameter with a default.
            Returns:
                None.
            """
            self.service = service
            self.optional_service = optional_service
            self.services = services
            self.count = count

    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        compiler_test_helpers.run_phase_requirements(spell)
        compiler_test_helpers.run_phase_symbolic_graph(spell)

        graph = spell.symbolic_graph
        assert graph is not None
        deps_by_name = {dep.param_name: dep for dep in graph.dependencies}
        assert set(deps_by_name) == {"service", "optional_service", "services", "count"}

        service_dep = deps_by_name["service"]
        assert service_dep.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
        assert service_dep.is_optional is False
        assert service_dep.is_collection is False
        assert service_dep.target_annotation is BasicService

        optional_dep = deps_by_name["optional_service"]
        assert optional_dep.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
        assert optional_dep.is_optional is True
        assert optional_dep.is_collection is False
        assert optional_dep.target_annotation == Optional[BasicService]

        services_dep = deps_by_name["services"]
        assert services_dep.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
        assert services_dep.is_optional is False
        assert services_dep.is_collection is True
        assert services_dep.target_annotation is IService

        count_dep = deps_by_name["count"]
        assert count_dep.di_shape is ParameterDIShape.PLAIN
        assert count_dep.is_optional is True
        assert count_dep.is_collection is False
        assert count_dep.target_annotation is int
    finally:
        spellbook.cleanup()


def test_component_spell_resolution_properties_follow_real_phase_artifacts() -> None:
    """
    Purpose:
        Validate Spell resolution properties reflect real phase artifacts.
    Contract:
        - requirements and symbolic_graph are populated after Phases 1 and 2.
        - resolution_frame is populated after Phase 3.
        - dependencies list is populated after Phase 3.
    Returns:
        None.
    Raises:
        AssertionError: If properties do not reflect phase artifacts.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell that depends on BasicService for Phase 3 resolution.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """
        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                - Stores the service for assertions.
            Args:
                service: Injected BasicService instance.
            Returns:
                None.
            """
            self.service = service

    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        assert spell.requirements is None
        assert spell.symbolic_graph is None
        assert spell.resolution_frame is None

        compiler_test_helpers.run_phase_requirements(spell)
        assert spell.requirements is not None

        compiler_test_helpers.run_phase_symbolic_graph(spell)
        assert spell.symbolic_graph is not None

        compiler_test_helpers.run_phase_local_frame(spell)
        assert spell.resolution_frame is not None
        assert set(spell.dependencies) == {service_id}
    finally:
        spellbook.cleanup()


def test_component_spell_mutation_override_updates_real_system_state() -> None:
    """
    Purpose:
        Validate mutation overrides do not dirty or structurally invalidate the spell.
    Contract:
        - Applying an override updates the stored payload only.
        - Clearing the override removes the stored payload only.
        - SpellSystemStates change reasons and dirty-lineage tracking remain unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If mutation payload or system-state stability is incorrect.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spell._add_owned_conduit(
            "component-conduit",
            dynamic_environment=True,
            creation_gate_controller=CreationGateController(),
        )
        states = spellbook._spell_system_states
        states.consume_dirty_indexes()
        state = spell.system_state
        assert state is not None
        initial_reason = state.change_reason

        spell.apply_mutation_override({"mode": "overlay"})
        assert state.change_reason is initial_reason
        assert spell.has_mutation_override is True
        assert spell.mutation_override == {"mode": "overlay"}
        assert states.consume_dirty_indexes() == []

        spell.clear_mutation_override()
        assert state.change_reason is initial_reason
        assert spell.has_mutation_override is False
        assert spell.mutation_override is None
        assert states.consume_dirty_indexes() == []
    finally:
        spellbook.cleanup()


