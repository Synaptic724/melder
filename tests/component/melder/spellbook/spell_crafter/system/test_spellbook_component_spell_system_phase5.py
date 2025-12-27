import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spell_system_phase5() -> None:
    """
    Purpose:
        Ensure component Phase-5 tests start with a clean Aether singleton.
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


def _make_spellbook(*, frame: str = "default") -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component Phase-5 tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Args:
        frame: Optional Aether frame name for the Spellbook.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook(aetheric_frame=frame)
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
        spellbook: Spellbook to search.
        spell_id: Versioned spell id to match.
    Returns:
        Spell: The resolved spell or None.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.current == spell_id:
            return spell
    return None


def test_component_phase5_builds_system_index_and_root_blueprint() -> None:
    """
    Purpose:
        Validate Phase 5 produces system index nodes and root blueprints.
    Contract:
        - System index includes root and dependency nodes.
        - Root node is marked as root and depends on the service.
        - Root blueprint DAG contains both nodes with root last in order.
    Returns:
        None.
    Raises:
        AssertionError: If Phase-5 artifacts are missing or inconsistent.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
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
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
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
        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()
        consumer_spell.run_phase_validation()
        consumer_spell.run_phase_root_blueprints("cid")

        crafter = consumer_spell._crafter
        assert crafter is not None
        index = crafter.spell_system_index_phase5
        assert index is not None

        consumer_node = index.get_node(consumer_id)
        service_node = index.get_node(service_id)
        assert consumer_node is not None
        assert service_node is not None
        assert consumer_node.dependencies == {service_id}
        assert service_node.dependencies == set()
        assert consumer_node.is_root is True
        assert service_node.is_root is False

        blueprint = crafter.root_blueprint_phase5
        assert blueprint is not None
        assert blueprint.root_spell_id == consumer_id
        assert set(blueprint.dag.nodes) == {consumer_id, service_id}
        assert blueprint.ordered_node_ids[-1] == consumer_id
    finally:
        spellbook.cleanup()


def test_component_phase5_does_not_attach_root_blueprint_to_non_root() -> None:
    """
    Purpose:
        Validate Phase 5 assigns root blueprints only to root spells.
    Contract:
        - Root spell has a root blueprint.
        - Dependency spell does not receive a root blueprint or index.
    Returns:
        None.
    Raises:
        AssertionError: If non-root spells receive Phase-5 root artifacts.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
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
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
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

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        service_spell = _get_spell_by_version_id(spellbook, service_id)
        assert consumer_spell is not None
        assert service_spell is not None

        service_spell.run_phase_requirements()
        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()
        consumer_spell.run_phase_validation()
        consumer_spell.run_phase_root_blueprints("cid")

        consumer_crafter = consumer_spell._crafter
        service_crafter = service_spell._crafter
        assert consumer_crafter is not None
        assert service_crafter is not None
        assert consumer_crafter.root_blueprint_phase5 is not None
        assert service_crafter.root_blueprint_phase5 is None
        assert service_crafter.spell_system_index_phase5 is None
    finally:
        spellbook.cleanup()


def test_component_phase5_filters_out_non_visible_spells() -> None:
    """
    Purpose:
        Validate Phase 5 filters system snapshots to visible spells only.
    Contract:
        - Spells bound in another Spellbook and not contracted are excluded.
        - System index and blueprints exclude non-visible spell ids.
    Returns:
        None.
    Raises:
        AssertionError: If non-visible spells leak into Phase-5 artifacts.
    """
    frame = "component-phase5-visible"
    spellbook = _make_spellbook(frame=frame)
    other_book = _make_spellbook(frame=frame)

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
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
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    class RemoteOnly:
        """
        Purpose:
            Provide a spell bound only in the other Spellbook.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the remote-only spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
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
        remote_id = other_book.bind(
            spell=RemoteOnly,
            existence=Existence.unique,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()
        consumer_spell.run_phase_validation()
        consumer_spell.run_phase_root_blueprints("cid")

        crafter = consumer_spell._crafter
        assert crafter is not None
        index = crafter.spell_system_index_phase5
        assert index is not None
        assert remote_id not in index.nodes

        blueprints = crafter._entire_dag_blueprint_phase5
        assert blueprints is not None
        assert remote_id not in blueprints
    finally:
        spellbook.cleanup()
        other_book.cleanup()
