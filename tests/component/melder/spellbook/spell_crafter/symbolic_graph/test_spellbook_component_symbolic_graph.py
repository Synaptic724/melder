import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_symbolic_graph() -> None:
    """
    Purpose:
        Reset the Aether singleton for component symbolic graph tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
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
        Provide a Spellbook configured for component symbolic graph tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str):
    """
    Purpose:
        Retrieve a local Spell by its version id.
    Contract:
        - Returns the first spell whose SpellIndex.current matches spell_id.
    Args:
        spellbook: Spellbook to search.
        spell_id: Version id to match.
    Returns:
        Spell or None: Matching spell instance or None if not found.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.current == spell_id:
            return spell
    return None


def test_component_symbolic_graph_cleans_after_spell_cleanup() -> None:
    """
    Purpose:
        Validate symbolic graphs are cleaned when the owning Spell is cleaned.
    Contract:
        - Spell cleanup detaches the symbolic graph reference.
        - The original graph raises after cleanup.
        - Dependencies are also cleaned after spell cleanup.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with a DI dependency for symbolic graph creation.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected dependency.
            Contract:
                - Stores the service for diagnostics.
            Args:
                service: Injected BasicService instance.
            Returns:
                None.
            """
            self.service = service

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
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()

        graph = spell.symbolic_graph
        assert graph is not None
        deps = graph.dependencies
        assert deps
        dependency = deps[0]

        spell.cleanup()

        assert spell.symbolic_graph is None
        with pytest.raises(RuntimeError):
            _ = graph.dependencies
        with pytest.raises(RuntimeError):
            _ = dependency.param_name
    finally:
        spellbook.cleanup()


def test_component_symbolic_graph_detaches_when_crafter_cleans() -> None:
    """
    Purpose:
        Validate explicit SpellCrafter cleanup detaches symbolic graph access.
    Contract:
        - The original graph reference raises after crafter cleanup.
        - Spell.symbolic_graph returns None once the crafter is cleaned.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell for symbolic graph cleanup checks.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected dependency.
            Contract:
                - Stores the service for diagnostics.
            Args:
                service: Injected BasicService instance.
            Returns:
                None.
            """
            self.service = service

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
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()

        graph = spell.symbolic_graph
        assert graph is not None

        crafter = spell._crafter
        assert crafter is not None
        crafter.cleanup()

        with pytest.raises(RuntimeError):
            _ = spell.symbolic_graph
        with pytest.raises(RuntimeError):
            _ = graph.dependencies
    finally:
        spellbook.cleanup()
