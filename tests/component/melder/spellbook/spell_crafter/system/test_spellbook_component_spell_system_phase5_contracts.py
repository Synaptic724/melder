from __future__ import annotations

from typing import Any, Dict, Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import (
    Depth3Layer2A,
    Depth3Layer2B,
    Depth3LeafA,
    Depth3LeafB,
    Depth3Root,
    get_depth_3_classes,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spell_system_phase5_contracts() -> None:
    """
    Purpose:
        Ensure component Phase-5 contract tests start with a clean Aether singleton.
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


def _make_dynamic_configuration() -> Configuration:
    """
    Purpose:
        Build a dynamic Configuration for contract-focused component tests.
    Contract:
        - dynamic_defaults are applied.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Configuration: Configured dynamic configuration.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bind_graph(
    spellbook: Spellbook,
    classes: Iterable[type],
) -> Dict[type, str]:
    """
    Purpose:
        Bind a dependency graph and return ids keyed by class.
    Contract:
        - Each class is bound as a unique spell with create permissions.
        - Spellframes match class names for forward-ref DI resolution.
        - Returned mapping contains an entry for every class.
    Args:
        spellbook: Spellbook used to bind the classes.
        classes: Iterable of classes to bind in order.
    Returns:
        Dict[type, str]: Mapping of class to spell id.
    """
    ids: Dict[type, str] = {}
    for cls in classes:
        spell_id = spellbook.bind(
            spell=cls,
            existence=Existence.unique,
            permissions="create",
            spellframe=cls.__name__,
        )
        ids[cls] = spell_id
    return ids


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> Any:
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
        Any: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def _run_spell_to_phase5(spell: Any) -> None:
    """
    Purpose:
        Advance a spell through Phase 5 artifacts for component assertions.
    Contract:
        - Runs Phases 1-5 in order.
        - Phase 5 requires Phase 4 to succeed.
    Args:
        spell: Spell instance to advance.
    Returns:
        None.
    """
    spell.run_phase_requirements()
    spell.run_phase_symbolic_graph()
    spell.run_phase_local_frame()
    spell.run_phase_validation()
    spell.run_phase_root_blueprints("cid")


def test_component_phase5_includes_contracted_dependency_in_index_and_blueprint() -> None:
    """
    Purpose:
        Validate Phase 5 includes contracted dependencies in system artifacts.
    Contract:
        - Contracted dependency spell ids appear in the system index.
        - Root blueprints include contracted dependency nodes.
        - Contracted dependencies are not treated as roots.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are missing from Phase-5 artifacts.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
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

    owner = None
    borrower = None
    try:
        service_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=BasicService.__name__,
        )

        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        borrower_book.begin_binding_transaction()
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_book.end_binding_transaction()
        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)

        crafter = consumer_spell._crafter
        assert crafter is not None
        index = crafter.spell_system_index_phase5
        assert index is not None
        assert consumer_id in index.nodes
        assert service_id in index.nodes
        consumer_node = index.get_node(consumer_id)
        service_node = index.get_node(service_id)
        assert consumer_node is not None
        assert service_node is not None
        assert consumer_node.dependencies == {service_id}

        blueprints = crafter._entire_dag_blueprint_phase5
        assert blueprints is not None
        assert set(blueprints) == {consumer_id}
        blueprint = crafter.root_blueprint_phase5
        assert blueprint is not None
        assert set(blueprint.dag.nodes) == {consumer_id, service_id}
        assert blueprint.ordered_node_ids[-1] == consumer_id
    finally:
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_component_phase5_contract_dependencies_generate_nested_socket_paths() -> None:
    """
    Purpose:
        Validate nested socket paths span contracted dependency graphs.
    Contract:
        - Contracted dependency graphs populate deep socket paths.
        - Root blueprints include the contracted dependency DAG.
    Returns:
        None.
    Raises:
        AssertionError: If nested socket paths or DAG nodes are missing.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on Depth3Root.
        Contract:
            - Declares a Depth3Root dependency for DI.
        Args:
            root: Injected Depth3Root instance.
        """

        def __init__(self, root: Depth3Root) -> None:
            """
            Purpose:
                Capture the injected Depth3Root dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                root: Injected Depth3Root dependency.
            Returns:
                None.
            """
            self.root = root

    owner = None
    borrower = None
    try:
        depth_ids = _bind_graph(owner_book, get_depth_3_classes())
        root_id = depth_ids[Depth3Root]
        layer2_a_id = depth_ids[Depth3Layer2A]
        layer2_b_id = depth_ids[Depth3Layer2B]
        leaf_a_id = depth_ids[Depth3LeafA]
        leaf_b_id = depth_ids[Depth3LeafB]

        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=root_id,
                conduit=owner,
                permissions="create",
            )

        borrower_book.begin_binding_transaction()
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_book.end_binding_transaction()
        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)

        crafter = consumer_spell._crafter
        assert crafter is not None
        blueprint = crafter.root_blueprint_phase5
        assert blueprint is not None
        assert set(blueprint.dag.nodes) == {
            consumer_id,
            root_id,
            layer2_a_id,
            layer2_b_id,
            leaf_a_id,
            leaf_b_id,
        }
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {
            ("root",),
            ("root", "left"),
            ("root", "right"),
            ("root", "left", "left"),
            ("root", "left", "right"),
            ("root", "right", "left"),
            ("root", "right", "right"),
        }
    finally:
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_component_phase5_contracts_exclude_uncontracted_remote_spells() -> None:
    """
    Purpose:
        Validate Phase 5 excludes uncontracted remote spells while including contracted ones.
    Contract:
        - Contracted spell ids appear in the system index and DAG.
        - Uncontracted remote spell ids are filtered out.
    Returns:
        None.
    Raises:
        AssertionError: If filtering or contracted inclusion fails.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    remote_book = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
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
            Provide a spell bound only in the remote Spellbook.
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

    owner = None
    borrower = None
    try:
        service_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=BasicService.__name__,
        )
        remote_id = remote_book.bind(
            spell=RemoteOnly,
            existence=Existence.unique,
            permissions="create",
        )

        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )

        with borrower_book.binding_transaction() as txn:
            consumer_id = txn.bind(
                spell=Consumer,
                existence=Existence.unique,
                permissions="create",
            )
        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)

        crafter = consumer_spell._crafter
        assert crafter is not None
        index = crafter.spell_system_index_phase5
        assert index is not None
        assert consumer_id in index.nodes
        assert service_id in index.nodes
        assert remote_id not in index.nodes

        blueprint = crafter.root_blueprint_phase5
        assert blueprint is not None
        assert remote_id not in blueprint.dag.nodes
    finally:
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()
