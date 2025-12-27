import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spellbook_conduit_definition() -> None:
    """
    Purpose:
        Ensure component Spellbook conduit-definition tests start with a clean Aether singleton.
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


class _ConduitStub:
    """
    Purpose:
        Provide a minimal conduit stub for Spellbook conduit-definition tests.
    Contract:
        - Captures ownership registration attempts for existing objects.
        - Can be configured to raise during registration to exercise error paths.
    """
    def __init__(
        self,
        conduit_id: str = "cid",
        name: str = "cname",
        raise_on_register: bool = False,
    ) -> None:
        """
        Purpose:
            Initialize the conduit stub.
        Contract:
            - Stores identifiers and registration behavior flags.
            - Initializes an empty creations map and registration log.
        Args:
            conduit_id: Conduit identifier to expose.
            name: Conduit name to expose.
            raise_on_register: When True, _register_to_creations raises after recording.
        Returns:
            None.
        """
        self._id = conduit_id
        self._name = name
        self._creations = {}
        self._raise_on_register = raise_on_register
        self.registered: list[tuple[object, object]] = []

    def _register_to_creations(self, spell: object, obj: object) -> None:
        """
        Purpose:
            Record a registration attempt for existing-object spells.
        Contract:
            - Appends (spell, obj) to the registered list.
            - Raises RuntimeError when configured to simulate failure.
        Args:
            spell: Spell instance being registered.
            obj: Existing object bound to the spell.
        Returns:
            None.
        Raises:
            RuntimeError: When raise_on_register is True.
        """
        self.registered.append((spell, obj))
        if self._raise_on_register:
            raise RuntimeError("registration-failed")


def _assert_owner_metadata(spell: object, conduit: _ConduitStub) -> None:
    """
    Purpose:
        Assert ownership metadata on a bound spell matches the conduit.
    Contract:
        - Validates owner conduit id, name, and creations reference.
    Args:
        spell: Spell instance whose ownership metadata should be set.
        conduit: Conduit stub providing expected ownership data.
    Returns:
        None.
    Raises:
        AssertionError: If ownership metadata does not match.
    """
    assert spell._owner_conduit_id == conduit._id
    assert spell._owner_conduit_name == conduit._name
    assert spell._owner_creations is conduit._creations
    assert spell.owned_spell is True


def test_component_spellbook_define_conduit_into_spells_stamps_ownership_and_registers_existing() -> None:
    """
    Purpose:
        Validate _define_conduit_into_spells stamps ownership and registers existing objects.
    Contract:
        - All local spells receive conduit ownership metadata.
        - Existing-object spells are registered into conduit creations.
    Returns:
        None.
    Raises:
        AssertionError: If ownership metadata or registrations are incorrect.
    """
    spellbook = _make_spellbook()
    existing = BasicService(marker="existing")

    try:
        class_spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        existing_spell_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
            binding_name="existing",
        )

        conduit = _ConduitStub(conduit_id="owner-id", name="owner-name")
        spellbook._define_conduit_into_spells(conduit)

        class_spell = _get_spell_by_version_id(spellbook, class_spell_id)
        existing_spell = _get_spell_by_version_id(spellbook, existing_spell_id)
        assert class_spell is not None
        assert existing_spell is not None

        _assert_owner_metadata(class_spell, conduit)
        _assert_owner_metadata(existing_spell, conduit)

        assert len(conduit.registered) == 1
        registered_spell, registered_obj = conduit.registered[0]
        assert registered_spell is existing_spell
        assert registered_obj is existing
    finally:
        spellbook.cleanup()


def test_component_spellbook_define_conduit_into_spells_continues_on_register_error() -> None:
    """
    Purpose:
        Validate conduit definition continues when existing-object registration fails.
    Contract:
        - Ownership metadata is still applied even if registration raises.
        - Registration attempts are recorded before the error is swallowed.
    Returns:
        None.
    Raises:
        AssertionError: If ownership metadata is missing or registration is not attempted.
    """
    spellbook = _make_spellbook()
    existing = BasicService(marker="existing")

    try:
        existing_spell_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )

        conduit = _ConduitStub(
            conduit_id="owner-id",
            name="owner-name",
            raise_on_register=True,
        )
        spellbook._define_conduit_into_spells(conduit)

        existing_spell = _get_spell_by_version_id(spellbook, existing_spell_id)
        assert existing_spell is not None
        _assert_owner_metadata(existing_spell, conduit)
        assert len(conduit.registered) == 1
        registered_spell, registered_obj = conduit.registered[0]
        assert registered_spell is existing_spell
        assert registered_obj is existing
    finally:
        spellbook.cleanup()


def test_component_spellbook_check_all_spells_raises_on_aether_collision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate _check_all_spells raises when Aether reports a collision.
    Contract:
        - RuntimeError is raised for a duplicate spell id in the Aether registry.
    Args:
        monkeypatch: Pytest fixture for patching Aether lookup behavior.
    Returns:
        None.
    Raises:
        AssertionError: If the collision is not detected.
    """
    spellbook = _make_spellbook()

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

        def _check_for_spell(version_id: str, frame: str) -> bool:
            """
            Purpose:
                Simulate a duplicate spell id detection for the bound spell.
            Contract:
                Returns True for the bound spell id within the spellbook frame.
            Args:
                version_id: Spell version id being checked.
                frame: Aether frame name provided by the caller.
            Returns:
                bool: True for the bound spell id, False otherwise.
            """
            return version_id == spell_id and frame == spellbook._aetheric_frame

        monkeypatch.setattr(spellbook._aether, "_check_for_spell", _check_for_spell)
        with pytest.raises(RuntimeError, match="already exists in the registry"):
            spellbook._check_all_spells()
    finally:
        spellbook.cleanup()


def test_component_spellbook_check_all_spells_passes_when_aether_reports_unique(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate _check_all_spells passes when Aether reports no collisions.
    Contract:
        - _check_all_spells completes without raising when no duplicates exist.
    Args:
        monkeypatch: Pytest fixture for patching Aether lookup behavior.
    Returns:
        None.
    Raises:
        AssertionError: If an unexpected error is raised.
    """
    spellbook = _make_spellbook()

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

        def _check_for_spell(_version_id: str, _frame: str) -> bool:
            """
            Purpose:
                Simulate no duplicate spell ids in Aether.
            Contract:
                Always returns False for uniqueness.
            Args:
                _version_id: Spell version id being checked.
                _frame: Aether frame name provided by the caller.
            Returns:
                bool: False to indicate no duplicates.
            """
            return False

        monkeypatch.setattr(spellbook._aether, "_check_for_spell", _check_for_spell)
        spellbook._check_all_spells()
    finally:
        spellbook.cleanup()
