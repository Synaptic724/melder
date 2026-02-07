from typing import Optional

from melder.aether.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity


class _ResolutionStateStub:
    """
    Minimal ConduitResolutionState stub for RiskManager tests.

    Purpose:
        Provide a fixed per-spell validity response so RiskManager can
        compute resolution risk without building a full conduit state.
    Contract:
        - get_spell_validity returns the configured validity for any spell id.
    """

    def __init__(self, validity: SpellValidity) -> None:
        """
        Initialize the stub with a fixed validity.

        Args:
            validity: The validity to return from get_spell_validity.
        """
        self._validity: SpellValidity = validity

    def get_spell_validity(self, spell_id: str) -> Optional[SpellValidity]:
        """
        Return the fixed validity for any spell id.

        Args:
            spell_id: Spell id (ignored).
        Returns:
            Optional[SpellValidity]: The fixed validity.
        """
        return self._validity


class _SpellSystemStatesStub:
    """
    Minimal SpellSystemStates stub for RiskManager tests.

    Purpose:
        Provide a resolution state lookup without wiring full system states.
    Contract:
        - get_conduit_resolution_state returns the configured stub.
        - get_by_spell_id returns None (lineage lookup not needed here).
    """

    def __init__(self, resolution_state: _ResolutionStateStub) -> None:
        """
        Initialize the stub with a resolution state instance.

        Args:
            resolution_state: Stub resolution state to return.
        """
        self._resolution_state: _ResolutionStateStub = resolution_state

    def get_conduit_resolution_state(self, conduit_id: str) -> Optional[_ResolutionStateStub]:
        """
        Return the configured resolution state for any conduit id.

        Args:
            conduit_id: Conduit id (ignored).
        Returns:
            Optional[_ResolutionStateStub]: The configured resolution state.
        """
        return self._resolution_state

    def get_by_spell_id(self, spell_id: str) -> None:
        """
        Return None for spell id lookups.

        Args:
            spell_id: Spell id to lookup (ignored).
        Returns:
            None.
        """
        return None


class _SpellSystemStateStub:
    """
    Minimal SpellSystemState stub for structural validity lookups.

    Purpose:
        Provide a validity attribute for RiskManager structural checks.
    Contract:
        - validity is a SpellValidity value.
    """

    def __init__(self, validity: SpellValidity) -> None:
        """
        Initialize the stub with a validity value.

        Args:
            validity: Structural validity to expose.
        """
        self.validity: SpellValidity = validity


class _SpellIndexStub:
    """
    Minimal SpellIndex stub for RiskManager tests.

    Purpose:
        Provide lineage id and current spell id attributes.
    Contract:
        - id is the lineage identifier.
        - current is the current spell id.
    """

    def __init__(self, lineage_id: str, current_id: str) -> None:
        """
        Initialize the stub with lineage and current ids.

        Args:
            lineage_id: Lineage identifier for the spell.
            current_id: Current version id for the spell.
        """
        self.id: str = lineage_id
        self._current: str = current_id

    @property
    def current(self) -> str:
        """
        Return the current spell id.

        Returns:
            str: Current spell id.
        """
        return self._current


class _SpellStub:
    """
    Minimal spell stub for RiskManager tests.

    Purpose:
        Supply the attributes RiskManager reads for structural/resolution checks.
    Contract:
        - system_state returns a stub with a validity attribute.
        - spell_index provides lineage/current ids.
        - _cleaned is False for live spells.
    """

    def __init__(self, validity: SpellValidity) -> None:
        """
        Initialize the stub with a structural validity value.

        Args:
            validity: Structural validity to expose.
        """
        self._cleaned: bool = False
        self.spell_index: _SpellIndexStub = _SpellIndexStub("lineage-1", "spell-1")
        self._state: _SpellSystemStateStub = _SpellSystemStateStub(validity)

    @property
    def system_state(self) -> _SpellSystemStateStub:
        """
        Return the structural state stub.

        Returns:
            _SpellSystemStateStub: The state object with validity.
        """
        return self._state


class _SpellbookStub:
    """
    Minimal Spellbook stub for RiskManager tests.

    Purpose:
        Capture validation-required flag updates from RiskManager.
    Contract:
        - _spells and _contracted_spells are present for register_conduit.
        - _set_spellbook_validation_required records the latest value.
    """

    def __init__(self) -> None:
        """
        Initialize an empty spellbook stub.
        """
        self._spells: dict = {}
        self._contracted_spells: dict = {}
        self._spellbook_validation_required: Optional[bool] = None

    def _set_spellbook_validation_required(self, required: bool) -> None:
        """
        Record the validation-required flag.

        Args:
            required: New validation-required value.
        Returns:
            None.
        """
        self._spellbook_validation_required = bool(required)


def test_register_spell_structural_validity_clears_risk_when_valid() -> None:
    """
    Verify structural validity uses SpellSystemState for risk gating.

    Contract:
    - Structural validity of SpellValidity.valid clears structural risk.
    - With resolution validity also valid, spellbook validation-required is False.
    """
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()

    risk_manager.register_conduit("conduit-1", spellbook)
    spell = _SpellStub(SpellValidity.valid)
    risk_manager.register_spell("conduit-1", spell)

    assert spellbook._spellbook_validation_required is False


def test_register_spell_structural_invalid_marks_risk_required() -> None:
    """
    Verify structural invalidity marks the spellbook as requiring validation.

    Contract:
    - Structural validity of SpellValidity.invalid triggers validation-required
      even when resolution validity is valid.
    """
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()

    risk_manager.register_conduit("conduit-1", spellbook)
    spell = _SpellStub(SpellValidity.invalid)
    risk_manager.register_spell("conduit-1", spell)

    assert spellbook._spellbook_validation_required is True
