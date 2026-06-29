import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.synchronization.creation_gate_controller import CreationGateController
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_contracts() -> None:
    """
    Purpose:
        Ensure component contract tests start with a clean Aether singleton.
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


class _ConduitStub:
    """
    Purpose:
        Provide the minimal active-conduit surface for Spellbook contract tests.
    Contract:
        - Exposes conduit identity for borrower/provider mirror registration.
        - Exposes dynamic mode and CreationGateController fields required by
          spell ownership stamping paths.
    """
    def __init__(self, conduit_id: str = "owner", name: str = "owner") -> None:
        """
        Purpose:
            Initialize contract test conduit state.
        Contract:
            - Stores id/name and an empty creations map.
            - Enables dynamic mode for contract test realism.
        Args:
            conduit_id: Conduit identifier used by link-mirror bookkeeping.
            name: Human-readable conduit name.
        Returns:
            None.
        """
        self._id = conduit_id
        self._name = name
        self._creations = {}
        self.__dynamic_environment__ = True
        self._creation_gate_controller = CreationGateController()


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
    spellbook._conduit = _ConduitStub(conduit_id="borrower", name="borrower")
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


def test_component_spellbook_add_and_remove_contracted_spell_updates_maps() -> None:
    """
    Purpose:
        Validate contracted spell maps update on add and remove operations.
    Contract:
        - _add_contracted_spell populates contracted maps and version cache.
        - _remove_contracted_spell removes entries and clears versions.
    Returns:
        None.
    Raises:
        AssertionError: If contracted maps or caches are incorrect.
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

        key = spellbook._make_spell_key(
            spell.spellframe,
            spell.spell_name,
            spell.binding_name,
        )
        spell_map = spellbook._contracted_spells[conduit_id]
        lookup_map = spellbook._lookup_contracted_spells[conduit_id]
        versions_set = spellbook._contracted_spell_ids[conduit_id]

        assert spell_map[spell.spell_index] is spell
        assert lookup_map[key] is spell.spell_index
        assert spell_id in versions_set

        spellbook._remove_contracted_spell(spell_id, conduit_id)

        assert spellbook._contracted_spells[conduit_id] == {}
        assert key not in spellbook._lookup_contracted_spells[conduit_id]
        assert spell_id not in spellbook._contracted_spell_ids[conduit_id]
        assert len(spellbook._contracted_spell_ids[conduit_id]) == 0
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_contracted_spell_rejects_peer_collision() -> None:
    """
    Purpose:
        Validate contracted spells cannot collide across peer conduits.
    Contract:
        - Binding a second spell onto an active frame signature raises (framewide).
    Returns:
        None.
    Raises:
        AssertionError: If peer collisions are not rejected.
    """
    owner_a_book = _make_spellbook()
    owner_b_book = _make_spellbook()

    owner_a_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )

    try:
        # Framewide one-active-signature-per-frame: the peer collision for
        # (IService, primary) is rejected when the second spell binds on the
        # shared frame, before any contract is attempted.
        with pytest.raises(RuntimeError, match="already active in this frame"):
            owner_b_book.bind(
                spell=BasicLogger,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="primary",
            )
    finally:
        owner_b_book.cleanup()
        owner_a_book.cleanup()


def test_component_spellbook_remove_contracted_spell_raises_for_missing_conduit() -> None:
    """
    Purpose:
        Validate removal raises when the conduit maps are missing.
    Contract:
        - _remove_contracted_spell raises RuntimeError for unknown conduits.
    Returns:
        None.
    Raises:
        AssertionError: If removal does not raise for missing conduits.
    """
    spellbook = _make_spellbook()
    try:
        with pytest.raises(RuntimeError, match="No contracted spell maps"):
            spellbook._remove_contracted_spell("missing-id", "missing-conduit")
    finally:
        spellbook.cleanup()


def test_component_spellbook_clear_contracted_spells_for_conduit_clears_maps() -> None:
    """
    Purpose:
        Validate clearing contracted spells empties maps but keeps the contract.
    Contract:
        - _clear_contracted_spells_for_conduit leaves conduit entries empty.
        - Version cache for the conduit is cleared.
    Returns:
        None.
    Raises:
        AssertionError: If maps are not cleared.
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

        spellbook._clear_contracted_spells_for_conduit(conduit_id)

        assert spellbook._contracted_spells[conduit_id] == {}
        assert spellbook._lookup_contracted_spells[conduit_id] == {}
        assert spellbook._contracted_spell_ids[conduit_id] == set()
    finally:
        spellbook.cleanup()


def test_component_spellbook_clear_contracted_spells_for_conduit_raises_when_missing() -> None:
    """
    Purpose:
        Validate clearing raises when the conduit maps are missing.
    Contract:
        - _clear_contracted_spells_for_conduit raises RuntimeError for unknown conduits.
    Returns:
        None.
    Raises:
        AssertionError: If clearing does not raise for missing conduits.
    """
    spellbook = _make_spellbook()
    try:
        with pytest.raises(RuntimeError, match="No contracted spell maps"):
            spellbook._clear_contracted_spells_for_conduit("missing-conduit")
    finally:
        spellbook.cleanup()


def test_component_spellbook_remove_link_contract_removes_maps() -> None:
    """
    Purpose:
        Validate link contract removal drops all maps for a conduit.
    Contract:
        - _remove_link_contract removes entries from all contracted maps.
    Returns:
        None.
    Raises:
        AssertionError: If any contract map remains.
    """
    spellbook = _make_spellbook()
    conduit_id = "peer"

    try:
        spellbook._create_link_contract(conduit_id)
        spellbook._remove_link_contract(conduit_id)

        assert conduit_id not in spellbook._contracted_spells
        assert conduit_id not in spellbook._lookup_contracted_spells
        assert conduit_id not in spellbook._contracted_spell_ids
    finally:
        spellbook.cleanup()


def test_component_spellbook_remove_link_contract_raises_on_inconsistent_state() -> None:
    """
    Purpose:
        Validate inconsistent contract maps raise on removal.
    Contract:
        - _remove_link_contract raises RuntimeError when maps are inconsistent.
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
            spellbook._remove_link_contract(conduit_id)
    finally:
        spellbook.cleanup()


def test_component_spellbook_sever_link_contract_removes_maps() -> None:
    """
    Purpose:
        Validate severing a link contract clears and removes contracted maps.
    Contract:
        - _sever_link_contract clears spell maps then removes the contract entry.
    Returns:
        None.
    Raises:
        AssertionError: If contract maps remain after severing.
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

        spellbook._sever_link_contract(conduit_id)

        assert conduit_id not in spellbook._contracted_spells
        assert conduit_id not in spellbook._lookup_contracted_spells
        assert conduit_id not in spellbook._contracted_spell_ids
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_contracted_spell_tracks_multiple_versions() -> None:
    """
    Purpose:
        Validate contracted version cache tracks all versions on a SpellIndex.
    Contract:
        - _add_contracted_spell adds every version from the SpellIndex.
    Returns:
        None.
    Raises:
        AssertionError: If version cache is incomplete.
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
        initial_id = spell.spell_index.selected_spell_id
        next_id = f"{initial_id}-v2"
        spell.spell_index.update(next_id)

        spellbook._add_contracted_spell(spell, conduit_id)

        versions_set = spellbook._contracted_spell_ids[conduit_id]
        assert initial_id in versions_set
        assert next_id in versions_set
    finally:
        spellbook.cleanup()


def test_component_spellbook_remove_contracted_spell_removes_all_versions() -> None:
    """
    Purpose:
        Validate removing a contracted spell clears all its versions.
    Contract:
        - _remove_contracted_spell removes every version for the SpellIndex.
    Returns:
        None.
    Raises:
        AssertionError: If versions remain after removal.
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
        initial_id = spell.spell_index.selected_spell_id
        next_id = f"{initial_id}-v2"
        spell.spell_index.update(next_id)

        spellbook._add_contracted_spell(spell, conduit_id)
        spellbook._remove_contracted_spell(next_id, conduit_id)

        versions_set = spellbook._contracted_spell_ids[conduit_id]
        assert initial_id not in versions_set
        assert next_id not in versions_set
        assert len(versions_set) == 0
    finally:
        spellbook.cleanup()


def test_component_spellbook_find_contracted_spell_count_tracks_links() -> None:
    """
    Purpose:
        Validate contracted spell count tracks linked conduits.
    Contract:
        - _find_contracted_spell_count returns the number of contract entries.
    Returns:
        None.
    Raises:
        AssertionError: If the contract count is incorrect.
    """
    spellbook = _make_spellbook()
    try:
        assert spellbook._find_contracted_spell_count() == 0

        spellbook._create_link_contract("peer-a")
        spellbook._create_link_contract("peer-b")
        assert spellbook._find_contracted_spell_count() == 2

        spellbook._remove_link_contract("peer-a")
        assert spellbook._find_contracted_spell_count() == 1
    finally:
        spellbook.cleanup()
