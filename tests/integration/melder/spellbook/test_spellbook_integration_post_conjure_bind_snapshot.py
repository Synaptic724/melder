import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_post_conjure_snapshot() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
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
        Provide a Spellbook configured for post-conjure bind tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def test_post_conjure_bind_collection_dependencies_require_rerun() -> None:
    """
    Purpose:
        Validate collection DI dependencies are a snapshot until phases re-run.
    Contract:
        - Phase 3 dependencies include only spells bound at the time of the run.
        - Binding a new implementation after conjure does not update dependencies.
        - Re-running phases 1-3 updates dependencies to include the new spell.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class ServiceA:
        """
        Purpose:
            First IService implementation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Provide IService marker state.
            Contract:
                - Exposes tester attribute for protocol compatibility.
            """
            self.tester = "a"

    class ServiceB:
        """
        Purpose:
            Second IService implementation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Provide IService marker state.
            Contract:
                - Exposes tester attribute for protocol compatibility.
            """
            self.tester = "b"

    class Consumer:
        """
        Purpose:
            Spell consuming all IService implementations.
        Contract:
            - Expects a collection of IService implementations.
        Args:
            services: Collection of IService implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture the injected IService implementations.
            Contract:
                - Stores the services collection for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    service_a_id = spellbook.bind(
        spell=ServiceA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="a",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="post_conjure_snapshot")
    try:
        consumer_spell = conduit.get_spell_by_id(consumer_id)
        assert consumer_spell is not None

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert set(consumer_spell.dependencies) == {service_a_id}
        state = consumer_spell.system_state
        assert state is not None
        assert state.direct_dependencies == {service_a_id}

        with spellbook.binding_transaction():
            service_b_id = spellbook.bind(
                spell=ServiceB,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="b",
            )

        assert set(consumer_spell.dependencies) == {service_a_id}
        state = consumer_spell.system_state
        assert state is not None
        assert state.direct_dependencies == {service_a_id}

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert set(consumer_spell.dependencies) == {service_a_id, service_b_id}
        state = consumer_spell.system_state
        assert state is not None
        assert state.direct_dependencies == {service_a_id, service_b_id}
    finally:
        conduit.cleanup()
