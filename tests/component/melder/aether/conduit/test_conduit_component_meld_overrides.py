from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_meld_overrides() -> None:
    """
    Purpose:
        Ensure component meld override tests start with a clean Aether singleton.
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


class BasicRepo:
    """
    Purpose:
        Provide a repository spell with a name parameter for override tests.
    Contract:
        - Stores the provided name on the instance.
    """

    def __init__(self, name: str = "repo") -> None:
        """
        Purpose:
            Initialize the repository name.
        Contract:
            Stores the provided name on the instance.
        Args:
            name: Identifier used in override assertions.
        Returns:
            None.
        """
        self.name = name


class BasicLogger:
    """
    Purpose:
        Provide a logger spell with a name parameter for override tests.
    Contract:
        - Stores the provided name on the instance.
    """

    def __init__(self, name: str = "logger") -> None:
        """
        Purpose:
            Initialize the logger name.
        Contract:
            Stores the provided name on the instance.
        Args:
            name: Identifier used in override assertions.
        Returns:
            None.
        """
        self.name = name


class ServiceWithRepo:
    """
    Purpose:
        Provide a service that depends on a BasicRepo for override tests.
    Contract:
        - Stores the injected repo instance.
    """

    def __init__(self, repo: BasicRepo) -> None:
        """
        Purpose:
            Capture the injected repo dependency.
        Contract:
            Stores the repo on the instance.
        Args:
            repo: Injected repository dependency.
        Returns:
            None.
        """
        self.repo = repo


class ServiceWithRepoAndLogger:
    """
    Purpose:
        Provide a service with repo/logger dependencies for broadcast overrides.
    Contract:
        - Stores the injected repo and logger instances.
    """

    def __init__(self, repo: BasicRepo, logger: BasicLogger) -> None:
        """
        Purpose:
            Capture the injected repo and logger dependencies.
        Contract:
            Stores repo and logger on the instance.
        Args:
            repo: Injected repository dependency.
            logger: Injected logger dependency.
        Returns:
            None.
        """
        self.repo = repo
        self.logger = logger


class SharedRepo:
    """
    Purpose:
        Provide a shared repository spell for path tests.
    Contract:
        - Stores the provided name on the instance.
    """

    def __init__(self, name: str = "shared") -> None:
        """
        Purpose:
            Initialize the shared repository name.
        Contract:
            Stores the provided name on the instance.
        Args:
            name: Identifier used in override assertions.
        Returns:
            None.
        """
        self.name = name


class ServiceA:
    """
    Purpose:
        Provide a service that depends on the shared repo.
    Contract:
        - Stores the injected repo instance.
    """

    def __init__(self, repo: SharedRepo) -> None:
        """
        Purpose:
            Capture the injected shared repo dependency.
        Contract:
            Stores the repo on the instance.
        Args:
            repo: Injected shared repository dependency.
        Returns:
            None.
        """
        self.repo = repo


class ServiceB:
    """
    Purpose:
        Provide a second service that depends on the shared repo.
    Contract:
        - Stores the injected repo instance.
    """

    def __init__(self, repo: SharedRepo) -> None:
        """
        Purpose:
            Capture the injected shared repo dependency.
        Contract:
            Stores the repo on the instance.
        Args:
            repo: Injected shared repository dependency.
        Returns:
            None.
        """
        self.repo = repo


class RootService:
    """
    Purpose:
        Provide a root spell that depends on ServiceA and ServiceB.
    Contract:
        - Stores both service dependencies.
    """

    def __init__(self, service_a: ServiceA, service_b: ServiceB) -> None:
        """
        Purpose:
            Capture the injected service dependencies.
        Contract:
            Stores service_a and service_b on the instance.
        Args:
            service_a: Injected ServiceA dependency.
            service_b: Injected ServiceB dependency.
        Returns:
            None.
        """
        self.service_a = service_a
        self.service_b = service_b


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component meld override tests.
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
        - Returns the first local spell whose SpellIndex.selected_spell_id matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell
    return None


def _run_all_spellbook_phases_through_blueprints(spellbook: Spellbook) -> None:
    """
    Purpose:
        Run phases 1-5 for every local spell in a Spellbook.
    Contract:
        - Phases 1-4 run for all spells before Phase 5 builds root blueprints.
        - Ensures dependency topologies exist before deep DAG assembly.
    Args:
        spellbook: Spellbook containing locally bound spells.
    Returns:
        None.
    """
    spells = list(spellbook.spells.values())
    compiler_system = SpellCompilerSystem()
    try:
        for spell in spells:
            compiler_system.run_phase_requirements(spell)
            compiler_system.run_phase_symbolic_graph(spell)
            compiler_system.run_phase_local_frame(spellbook, spell)
            compiler_system.run_phase_validation(spellbook, spell)
        for spell in spells:
            compiler_system.run_phase_root_blueprints(spellbook, spell, "cid")
    finally:
        compiler_system.cleanup()


def test_component_meld_spell_override_path_targets_nested_param() -> None:
    """
    Purpose:
        Validate PATH overrides target nested dependency parameters.
    Contract:
        - path overrides apply to dependency constructor params.
        - The overridden value is visible on the nested dependency instance.
    Returns:
        None.
    Raises:
        AssertionError: If nested PATH overrides do not apply.
    """
    spellbook = _make_spellbook()
    repo_id = spellbook.bind(
        spell=BasicRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepo,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell=service_id,
            spell_override={"repo>name": "override"},
        )
        assert isinstance(instance, ServiceWithRepo)
        assert isinstance(instance.repo, BasicRepo)
        assert instance.repo.name == "override"
    finally:
        conduit.cleanup()


def test_component_meld_spell_override_unique_replaces_dependency() -> None:
    """
    Purpose:
        Validate UNIQUE overrides replace DI-resolved dependencies.
    Contract:
        - Unique override replaces the dependency instance for the root param.
    Returns:
        None.
    Raises:
        AssertionError: If the unique override does not replace the dependency.
    """
    spellbook = _make_spellbook()
    spellbook.bind(
        spell=BasicRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepo,
        existence=Existence.unique,
        permissions="create",
    )
    override_repo = BasicRepo(name="override")
    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell=service_id,
            spell_override={"*repo": override_repo},
        )
        assert isinstance(instance, ServiceWithRepo)
        assert instance.repo is override_repo
    finally:
        conduit.cleanup()


def test_component_meld_spell_override_broadcast_targets_multiple_nodes() -> None:
    """
    Purpose:
        Validate BROADCAST overrides apply to all matching sockets.
    Contract:
        - Broadcast overrides apply to every matching param name.
        - Each matching dependency reflects the broadcast value.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast overrides do not apply to all matches.
    """
    spellbook = _make_spellbook()
    spellbook.bind(
        spell=BasicRepo,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=BasicLogger,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepoAndLogger,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell=service_id,
            spell_override={"**name": "broadcast"},
        )
        assert isinstance(instance, ServiceWithRepoAndLogger)
        assert instance.repo.name == "broadcast"
        assert instance.logger.name == "broadcast"
    finally:
        conduit.cleanup()


def test_component_meld_spell_override_specificity_prefers_path() -> None:
    """
    Purpose:
        Validate PATH overrides beat UNIQUE and BROADCAST for the same socket.
    Contract:
        - PATH overrides take precedence over UNIQUE and BROADCAST.
        - The most specific value is used by the root dependency.
    Returns:
        None.
    Raises:
        AssertionError: If override specificity does not prefer PATH.
    """
    spellbook = _make_spellbook()
    spellbook.bind(
        spell=BasicRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepo,
        existence=Existence.unique,
        permissions="create",
    )
    broadcast_repo = BasicRepo(name="broadcast")
    unique_repo = BasicRepo(name="unique")
    path_repo = BasicRepo(name="path")
    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell=service_id,
            spell_override={
                "**repo": broadcast_repo,
                "*repo": unique_repo,
                "repo": path_repo,
            },
        )
        assert isinstance(instance, ServiceWithRepo)
        assert instance.repo is path_repo
    finally:
        conduit.cleanup()


def test_component_meld_spell_override_conflicting_path_raises() -> None:
    """
    Purpose:
        Validate conflicting PATH overrides surface as MeldExecutionError.
    Contract:
        - Conflicting overrides with the same specificity are rejected.
        - Conduit.meld raises MeldExecutionError when overrides conflict.
    Returns:
        None.
    Raises:
        AssertionError: If conflicting overrides do not raise.
    """
    spellbook = _make_spellbook()
    spellbook.bind(
        spell=BasicRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepo,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=service_id,
                spell_override={
                    "repo>name": "first",
                    "repo > name": "second",
                },
            )
    finally:
        conduit.cleanup()


def test_component_meld_root_blueprint_paths_two_node_graph() -> None:
    """
    Purpose:
        Validate root blueprint paths for a simple root->dependency graph.
    Contract:
        - Socket refs include "repo" and "repo>name" paths.
        - Each exact path maps to a single socket in the DagIndex.
        - Ordered nodes include the dependency before the root.
    Returns:
        None.
    Raises:
        AssertionError: If the deep path index is incomplete.
    """
    spellbook = _make_spellbook()
    repo_id = spellbook.bind(
        spell=BasicRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepo,
        existence=Existence.unique,
        permissions="create",
    )

    _run_all_spellbook_phases_through_blueprints(spellbook)

    root_spell = _get_spell_by_version_id(spellbook, service_id)
    assert root_spell is not None
    blueprint = root_spell._compiler_artifact._root_blueprint_phase5
    assert blueprint is not None
    blueprint.ensure_dag_index_built()

    ordered_ids = blueprint.ordered_node_ids
    assert repo_id in ordered_ids
    assert service_id in ordered_ids
    assert ordered_ids[-1] == service_id

    path_registry = blueprint.path_registry
    socket_paths = {path_registry.materialize_path(socket.param_path_id) for socket in blueprint.socket_refs}
    assert socket_paths == {("repo",), ("repo", "name")}
    assert len(blueprint.dag_index.get_by_exact_path(("repo",))) == 1
    assert len(blueprint.dag_index.get_by_exact_path(("repo", "name"))) == 1


def test_component_meld_root_blueprint_paths_shared_dependency() -> None:
    """
    Purpose:
        Validate root blueprint paths for a shared dependency graph.
    Contract:
        - The DagIndex exposes distinct paths for each branch to the shared repo.
        - The root blueprint captures all expected socket paths.
        - Dependencies are ordered before the root in the execution order.
    Returns:
        None.
    Raises:
        AssertionError: If shared dependency paths are missing or duplicated.
    """
    spellbook = _make_spellbook()
    repo_id = spellbook.bind(
        spell=SharedRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_a_id = spellbook.bind(
        spell=ServiceA,
        existence=Existence.unique,
        permissions="create",
    )
    service_b_id = spellbook.bind(
        spell=ServiceB,
        existence=Existence.unique,
        permissions="create",
    )
    root_id = spellbook.bind(
        spell=RootService,
        existence=Existence.unique,
        permissions="create",
    )

    _run_all_spellbook_phases_through_blueprints(spellbook)

    root_spell = _get_spell_by_version_id(spellbook, root_id)
    assert root_spell is not None
    blueprint = root_spell._compiler_artifact._root_blueprint_phase5
    assert blueprint is not None
    blueprint.ensure_dag_index_built()

    ordered_ids = blueprint.ordered_node_ids
    assert ordered_ids[-1] == root_id
    assert repo_id in ordered_ids
    assert service_a_id in ordered_ids
    assert service_b_id in ordered_ids
    assert len(ordered_ids) == 4
    order_map = {node_id: idx for idx, node_id in enumerate(ordered_ids)}
    assert order_map[repo_id] < order_map[service_a_id]
    assert order_map[repo_id] < order_map[service_b_id]

    expected_paths = {
        ("service_a",),
        ("service_b",),
        ("service_a", "repo"),
        ("service_b", "repo"),
        ("service_a", "repo", "name"),
        ("service_b", "repo", "name"),
    }
    path_registry = blueprint.path_registry
    socket_paths = {path_registry.materialize_path(socket.param_path_id) for socket in blueprint.socket_refs}
    assert socket_paths == expected_paths
    for path in expected_paths:
        assert len(blueprint.dag_index.get_by_exact_path(path)) == 1
