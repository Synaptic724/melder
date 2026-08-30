import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
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


def test_bind_conjure_and_meld_resolves_direct_dependency() -> None:
    """
    Purpose:
        Validate direct constructor dependency resolution through the DI pipeline.
    Contract:
        - A dependency spell is resolved by annotation.
        - The resolved dependency instance is attached to the service.
    Returns:
        None.
    Raises:
        AssertionError: If dependency resolution does not inject the same instance.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell for resolution testing.
        Contract:
            Stores a stable marker to distinguish instances.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the dependency with a marker.
            Contract:
                Sets marker to "dep".
            Returns:
                None.
            """
            self.marker = "dep"

    class _Service:
        """
        Purpose:
            Provide a service spell that depends on _Dependency.
        Contract:
            Stores the resolved dependency on the instance.
        """
        def __init__(self, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the dependency for assertions.
            Contract:
                Stores the dependency on the instance.
            Args:
                dep: Resolved dependency instance.
            Returns:
                None.
            """
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    dep_id = spellbook.bind(
        spell=_Dependency,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell_id=service_id)
        dependency = conduit.meld(spell_id=dep_id)
        assert service.dep is dependency
        assert dependency.marker == "dep"
    finally:
        conduit.cleanup()


def test_meld_resolves_multiple_dependencies_and_reuses_singletons() -> None:
    """
    Purpose:
        Validate resolution of multiple constructor dependencies.
    Contract:
        - Each dependency is resolved by annotation.
        - Unique dependencies are reused across multiple service melds.
    Returns:
        None.
    Raises:
        AssertionError: If dependency instances are not reused as expected.
    """
    class _DepA:
        """
        Purpose:
            Provide a first dependency spell.
        Contract:
            Stores a stable identifier for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the dependency marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _DepB:
        """
        Purpose:
            Provide a second dependency spell.
        Contract:
            Stores a stable identifier for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the dependency marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    class _Service:
        """
        Purpose:
            Provide a service spell with multiple dependencies.
        Contract:
            Stores the resolved dependencies for assertions.
        """
        def __init__(self, dep_a: _DepA, dep_b: _DepB) -> None:
            """
            Purpose:
                Capture multiple dependencies for assertions.
            Contract:
                Stores both dependencies on the instance.
            Args:
                dep_a: First dependency instance.
                dep_b: Second dependency instance.
            Returns:
                None.
            """
            self.dep_a = dep_a
            self.dep_b = dep_b

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    dep_a_id = spellbook.bind(
        spell=_DepA,
        existence=Existence.unique,
        permissions="create",
    )
    dep_b_id = spellbook.bind(
        spell=_DepB,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=service_id)
        second = conduit.meld(spell_id=service_id)
        dep_a = conduit.meld(spell_id=dep_a_id)
        dep_b = conduit.meld(spell_id=dep_b_id)
        assert first is not second
        assert first.dep_a is dep_a
        assert second.dep_a is dep_a
        assert first.dep_b is dep_b
        assert second.dep_b is dep_b
    finally:
        conduit.cleanup()


def test_meld_resolves_dependency_chain_and_reuses_nodes() -> None:
    """
    Purpose:
        Validate chained dependency resolution across multiple layers.
    Contract:
        - Repo depends on Logger, Service depends on Repo.
        - Unique dependencies are reused across explicit meld calls.
    Returns:
        None.
    Raises:
        AssertionError: If nested dependencies are not reused.
    """
    class _Logger:
        """
        Purpose:
            Provide a logging dependency spell.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the logger marker.
            Contract:
                Sets marker to "log".
            Returns:
                None.
            """
            self.marker = "log"

    class _Repo:
        """
        Purpose:
            Provide a repository spell that depends on _Logger.
        Contract:
            Stores the resolved logger instance.
        """
        def __init__(self, logger: _Logger) -> None:
            """
            Purpose:
                Capture the logger for assertions.
            Contract:
                Stores the logger on the instance.
            Args:
                logger: Logger dependency instance.
            Returns:
                None.
            """
            self.logger = logger

    class _Service:
        """
        Purpose:
            Provide a service spell that depends on _Repo.
        Contract:
            Stores the resolved repository instance.
        """
        def __init__(self, repo: _Repo) -> None:
            """
            Purpose:
                Capture the repo for assertions.
            Contract:
                Stores the repo on the instance.
            Args:
                repo: Repository dependency instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    logger_id = spellbook.bind(
        spell=_Logger,
        existence=Existence.unique,
        permissions="create",
    )
    repo_id = spellbook.bind(
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell_id=service_id)
        repo = conduit.meld(spell_id=repo_id)
        logger = conduit.meld(spell_id=logger_id)
        assert service.repo is repo
        assert repo.logger is logger
        assert logger.marker == "log"
    finally:
        conduit.cleanup()
