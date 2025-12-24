import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.helpers.general_helpers import SpellInputUtils
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


def test_component_spellbook_add_hooks_to_spell_attaches_lists() -> None:
    """
    Purpose:
        Validate hook lists are attached to spells via the private hook helper.
    Contract:
        - pre_hooks, activation_hooks, and post_hooks are stored on the Spell.
    Returns:
        None.
    Raises:
        AssertionError: If hooks are not assigned correctly.
    """
    spellbook = _make_spellbook()

    def pre_hook() -> None:
        """
        Purpose:
            Provide a pre-hook for Spellbook hook attachment.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    def activation_hook() -> None:
        """
        Purpose:
            Provide an activation hook for Spellbook hook attachment.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    def post_hook() -> None:
        """
        Purpose:
            Provide a post-hook for Spellbook hook attachment.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spellbook._add_hooks_to_spell(
            spell,
            pre_hooks=[pre_hook],
            activation_hooks=[activation_hook],
            post_hooks=[post_hook],
        )

        assert spell.pre_hooks == [pre_hook]
        assert spell.activation_hooks == [activation_hook]
        assert spell.post_hooks == [post_hook]
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_rejects_non_callable() -> None:
    """
    Purpose:
        Validate hook attachment rejects non-callable hooks.
    Contract:
        - _add_hooks_to_spell raises TypeError for non-callable hook entries.
    Returns:
        None.
    Raises:
        AssertionError: If non-callable hooks are accepted.
    """
    spellbook = _make_spellbook()
    bad_hook = object()

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        with pytest.raises(TypeError, match="pre_hooks"):
            spellbook._add_hooks_to_spell(spell, pre_hooks=[bad_hook])
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_rejects_non_spell() -> None:
    """
    Purpose:
        Validate hook attachment rejects non-Spell inputs.
    Contract:
        - _add_hooks_to_spell raises TypeError when the target is not an ISpell.
    Returns:
        None.
    Raises:
        AssertionError: If non-Spell inputs are accepted.
    """
    spellbook = _make_spellbook()
    try:
        with pytest.raises(TypeError, match="spell must be an instance"):
            spellbook._add_hooks_to_spell(object(), pre_hooks=[])
    finally:
        spellbook.cleanup()


def test_component_spellbook_make_spell_key_normalizes_inputs() -> None:
    """
    Purpose:
        Validate _make_spell_key uses normalized spell key parts.
    Contract:
        - Returned key matches SpellInputUtils.make_spell_key_from_parts.
    Returns:
        None.
    Raises:
        AssertionError: If key normalization does not match helper behavior.
    """
    spellbook = _make_spellbook()
    try:
        key = spellbook._make_spell_key("ISERVICE", "BasicService", "PRIMARY")
        expected = SpellInputUtils.make_spell_key_from_parts(
            spellframe="ISERVICE",
            spell_name="BasicService",
            binding_name="PRIMARY",
        )
        assert key == expected
    finally:
        spellbook.cleanup()


def test_component_spellbook_create_link_contract_raises_on_inconsistent_state() -> None:
    """
    Purpose:
        Validate inconsistent contract maps raise on creation.
    Contract:
        - _create_link_contract raises RuntimeError when maps are inconsistent.
    Returns:
        None.
    Raises:
        AssertionError: If inconsistent state does not raise.
    """
    spellbook = _make_spellbook()
    conduit_id = "peer"
    spellbook._contracted_spells[conduit_id] = {}

    try:
        with pytest.raises(RuntimeError, match="Inconsistent link contract state"):
            spellbook._create_link_contract(conduit_id)
    finally:
        spellbook.cleanup()


def test_component_spellbook_remove_contracted_spell_raises_when_missing_version() -> None:
    """
    Purpose:
        Validate removal raises when the version id is not present.
    Contract:
        - _remove_contracted_spell raises RuntimeError for unknown version ids.
    Returns:
        None.
    Raises:
        AssertionError: If removal does not raise for missing version ids.
    """
    spellbook = _make_spellbook()
    conduit_id = "peer"

    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spellbook._add_contracted_spell(spell, conduit_id)

        with pytest.raises(RuntimeError, match="not found"):
            spellbook._remove_contracted_spell("missing-version", conduit_id)
    finally:
        spellbook.cleanup()
