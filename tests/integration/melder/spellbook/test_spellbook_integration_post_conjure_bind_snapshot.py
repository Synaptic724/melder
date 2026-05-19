import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.protocols import IService


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
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


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Provide a dynamic configuration for contract/link integration tests.
    Contract:
        - system_state is set to dynamic defaults.
        - phase_scheduler_workers_per_spellbook is configured.
    Returns:
        SpellbookConfiguration: A dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


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
        spell_states = spellbook._spell_system_states
        assert spell_states is not None
        spell_states.consume_dirty_indexes()

        with spellbook.binding_transaction():
            service_b_id = spellbook.bind(
                spell=ServiceB,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="b",
            )

        dirty_lineages = spell_states.consume_dirty_indexes()
        assert consumer_spell.spell_index.id in dirty_lineages

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


def test_post_conjure_bind_collection_dependencies_isolated_by_spellbook() -> None:
    """
    Purpose:
        Validate collection revalidation is scoped to the owning Spellbook.
    Contract:
        - Binding a new implementation gates list[Frame] consumers in the
          local Spellbook only.
        - Unlinked Spellbooks in the same frame are not gated.
    Returns:
        None.
    """
    spellbook_a = Spellbook(aetheric_frame="shared")
    spellbook_a.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook_b = Spellbook(aetheric_frame="shared")
    spellbook_b.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)

    class ServiceA:
        """
        Purpose:
            IService implementation bound in Spellbook A.
        Contract:
            - Declares no constructor parameters.
        """

    class ServiceAExtra:
        """
        Purpose:
            Second IService implementation for Spellbook A.
        Contract:
            - Declares no constructor parameters.
        """

    class ConsumerA:
        """
        Purpose:
            Consumer bound in Spellbook A.
        Contract:
            - Expects a list of IService implementations.
        Args:
            services: Collection of IService implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture IService implementations.
            Contract:
                - Stores the services list for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    class ServiceB:
        """
        Purpose:
            IService implementation bound in Spellbook B.
        Contract:
            - Declares no constructor parameters.
        """

    class ConsumerB:
        """
        Purpose:
            Consumer bound in Spellbook B.
        Contract:
            - Expects a list of IService implementations.
        Args:
            services: Collection of IService implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture IService implementations.
            Contract:
                - Stores the services list for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    spellbook_a.bind(
        spell=ServiceA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="a",
    )
    consumer_a_id = spellbook_a.bind(
        spell=ConsumerA,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook_b.bind(
        spell=ServiceB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="b",
    )
    consumer_b_id = spellbook_b.bind(
        spell=ConsumerB,
        existence=Existence.unique,
        permissions="create",
    )

    conduit_a = spellbook_a.conjure(name="conduit_a")
    conduit_b = spellbook_b.conjure(name="conduit_b")
    try:
        consumer_a_spell = conduit_a.get_spell_by_id(consumer_a_id, aetheric_frame_name="shared")
        consumer_b_spell = conduit_b.get_spell_by_id(consumer_b_id, aetheric_frame_name="shared")
        assert consumer_a_spell is not None
        assert consumer_b_spell is not None

        consumer_a_spell.run_phase_requirements()
        consumer_a_spell.run_phase_symbolic_graph()
        consumer_a_spell.run_phase_local_frame()

        consumer_b_spell.run_phase_requirements()
        consumer_b_spell.run_phase_symbolic_graph()
        consumer_b_spell.run_phase_local_frame()

        spellbook_a._spell_system_states.consume_dirty_indexes()

        with spellbook_a.binding_transaction():
            spellbook_a.bind(
                spell=ServiceAExtra,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="a2",
            )

        dirty_lineages = spellbook_a._spell_system_states.consume_dirty_indexes()
        assert consumer_a_spell.spell_index.id in dirty_lineages
        assert consumer_b_spell.spell_index.id not in dirty_lineages
    finally:
        conduit_a.cleanup()
        conduit_b.cleanup()


def test_post_conjure_contract_addition_marks_local_collection_consumers() -> None:
    """
    Purpose:
        Validate contracted spell additions gate local list[Frame] consumers.
    Contract:
        - Adding a contracted spell marks borrower list consumers dirty.
        - Owner spellbook consumers are not gated by borrower contracts.
    Returns:
        None.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    class OwnerService:
        """
        Purpose:
            IService provider owned by the owner Spellbook.
        Contract:
            - Declares no constructor parameters.
        """

    class OwnerConsumer:
        """
        Purpose:
            Consumer bound in the owner Spellbook for isolation checks.
        Contract:
            - Expects list[IService] implementations.
        Args:
            services: Collection of IService implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture IService implementations.
            Contract:
                - Stores the services list for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    class BorrowerConsumer:
        """
        Purpose:
            Consumer bound in the borrower Spellbook.
        Contract:
            - Expects list[IService] implementations.
        Args:
            services: Collection of IService implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture IService implementations.
            Contract:
                - Stores the services list for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    service_id = owner_book.bind(
        spell=OwnerService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="owner",
    )
    owner_consumer_id = owner_book.bind(
        spell=OwnerConsumer,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_consumer_id = borrower_book.bind(
        spell=BorrowerConsumer,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner_consumer_spell = owner.get_spell_by_id(owner_consumer_id)
        borrower_consumer_spell = borrower.get_spell_by_id(borrower_consumer_id)
        assert owner_consumer_spell is not None
        assert borrower_consumer_spell is not None

        owner_consumer_spell.run_phase_requirements()
        owner_consumer_spell.run_phase_symbolic_graph()
        owner_consumer_spell.run_phase_local_frame()

        borrower_consumer_spell.run_phase_requirements()
        borrower_consumer_spell.run_phase_symbolic_graph()
        borrower_consumer_spell.run_phase_local_frame()

        borrower_book._spell_system_states.consume_dirty_indexes()

        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )

        dirty_lineages = borrower_book._spell_system_states.consume_dirty_indexes()
        assert borrower_consumer_spell.spell_index.id in dirty_lineages
        assert owner_consumer_spell.spell_index.id not in dirty_lineages
    finally:
        borrower.cleanup()
        owner.cleanup()

