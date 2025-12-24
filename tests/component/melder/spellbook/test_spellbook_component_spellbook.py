import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spellbook() -> None:
    """
    Purpose:
        Ensure component Spellbook tests start with a clean Aether singleton.
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


class _SpellSystemStatesStub:
    """
    Purpose:
        Capture lineage registrations for Spellbook bind operations.
    Contract:
        - register_lineage records SpellIndex and spell references in order.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize an empty registry of lineage registrations.
        Contract:
            - registered_lineages starts empty.
        Returns:
            None.
        """
        self.registered_lineages: list[tuple[object, object]] = []

    def register_lineage(self, spell_index: object, spell: object) -> None:
        """
        Purpose:
            Record a lineage registration from Spellbook.bind.
        Contract:
            - Appends (spell_index, spell) to registered_lineages.
        Args:
            spell_index: SpellIndex registered for the lineage.
            spell: Underlying spell callable/class registered.
        Returns:
            None.
        """
        self.registered_lineages.append((spell_index, spell))


class _ConduitStub:
    """
    Purpose:
        Provide a minimal conduit stub for Spellbook bind ownership flows.
    Contract:
        - Tracks registration calls for existing creations.
    """
    def __init__(self, conduit_id: str = "cid", name: str = "cname") -> None:
        """
        Purpose:
            Initialize the conduit stub.
        Contract:
            - Stores identifiers and initializes registration tracking.
        Args:
            conduit_id: Conduit identifier to expose.
            name: Conduit name to expose.
        Returns:
            None.
        """
        self._id = conduit_id
        self._name = name
        self._creations = {}
        self.registered: list[tuple[object, object]] = []

    def _register_to_creations(self, spell: object, obj: object) -> None:
        """
        Purpose:
            Record registration of existing creations.
        Contract:
            - Appends (spell, obj) to the registered list.
        Args:
            spell: Spell instance being registered.
            obj: Existing object bound to the spell.
        Returns:
            None.
        """
        self.registered.append((spell, obj))


def test_component_spellbook_bind_registers_lineage_and_states() -> None:
    """
    Purpose:
        Validate Spellbook.bind registers lineage and uses spell system states.
    Contract:
        - register_lineage receives the SpellIndex and original spell callable.
        - The bound Spell references the injected SpellSystemStates instance.
    Returns:
        None.
    Raises:
        AssertionError: If lineage or state wiring is incorrect.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

        assert len(states.registered_lineages) == 1
        registered_index, registered_spell = states.registered_lineages[0]
        assert registered_spell is BasicService
        assert registered_index in spellbook.spells

        bound_spell = _get_spell_by_version_id(spellbook, spell_id)
        assert bound_spell is not None
        assert bound_spell._spell_system_states is states
        assert bound_spell.spell_index.current == spell_id
    finally:
        spellbook.cleanup()


def test_component_spellbook_bind_existing_object_registers_to_creations() -> None:
    """
    Purpose:
        Validate binding an existing object registers it to a conjured conduit.
    Contract:
        - _register_to_creations is invoked for existing-object spells.
        - The bound Spell is stamped with owner metadata.
    Returns:
        None.
    Raises:
        AssertionError: If ownership or registration is missing.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states
    conduit = _ConduitStub(conduit_id="owner-id", name="owner-name")
    spellbook._conduit = conduit
    spellbook._conjured = True
    existing = BasicService(marker="existing")

    try:
        spell_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )

        assert len(conduit.registered) == 1
        registered_spell, registered_obj = conduit.registered[0]
        assert registered_obj is existing

        bound_spell = _get_spell_by_version_id(spellbook, spell_id)
        assert bound_spell is not None
        assert registered_spell is bound_spell
        assert bound_spell.user_created_object is existing
        assert bound_spell.owned_spell is True
        assert bound_spell._owner_conduit_id == conduit._id
        assert bound_spell._owner_conduit_name == conduit._name
    finally:
        spellbook.cleanup()


def test_component_spellbook_bind_updates_spell_versions_cache() -> None:
    """
    Purpose:
        Validate bind keeps the local spell version cache warm.
    Contract:
        - _spell_versions includes the newly bound spell id.
    Returns:
        None.
    Raises:
        AssertionError: If _spell_versions is not updated.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        assert spellbook._spell_versions is not None
        assert spell_id in spellbook._spell_versions
    finally:
        spellbook.cleanup()


def test_component_spellbook_bind_after_conjure_sets_owner_metadata() -> None:
    """
    Purpose:
        Validate binding after conjure stamps owner metadata on new spells.
    Contract:
        - New spells receive owner conduit id/name and owned_spell flag.
        - No creation registration occurs for class-based spells.
    Returns:
        None.
    Raises:
        AssertionError: If ownership metadata is missing or incorrect.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states
    conduit = _ConduitStub(conduit_id="owner-id", name="owner-name")
    spellbook._conduit = conduit
    spellbook._conjured = True

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        assert conduit.registered == []

        bound_spell = _get_spell_by_version_id(spellbook, spell_id)
        assert bound_spell is not None
        assert bound_spell.user_created_object is None
        assert bound_spell.owned_spell is True
        assert bound_spell._owner_conduit_id == conduit._id
        assert bound_spell._owner_conduit_name == conduit._name
    finally:
        spellbook.cleanup()
