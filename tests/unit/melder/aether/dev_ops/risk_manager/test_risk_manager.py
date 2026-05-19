import threading
from typing import Optional

from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity


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


def test_init_rejects_none_spell_system_states() -> None:
    """Verify RiskManager rejects a missing SpellSystemStates dependency."""
    import pytest

    with pytest.raises(ValueError, match="spell_system_states cannot be None"):
        RiskManager(None)


def test_cleanup_clears_tracking_and_is_idempotent() -> None:
    """Verify cleanup clears tracking state and is safe to call twice."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    spell = _SpellStub(SpellValidity.valid)

    risk_manager.register_conduit("conduit-1", spellbook)
    risk_manager.register_spell("conduit-1", spell)

    risk_manager.cleanup()
    risk_manager.cleanup()

    assert risk_manager._conduit_states == {}
    assert risk_manager._lineage_conduits == {}
    assert not hasattr(risk_manager, '_spell_system_states')
    assert not hasattr(risk_manager, '_lock')


def test_cleanup_rechecks_cleaned_inside_lock() -> None:
    """Verify the inner cleanup re-check under concurrent teardown."""

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    risk_manager._lock = _CoordinatedLock()
    failures = []

    def _run_cleanup():
        try:
            risk_manager.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = threading.Thread(target=_run_cleanup, name="risk-cleanup-first")
    second = threading.Thread(target=_run_cleanup, name="risk-cleanup-second")

    first.start()
    assert risk_manager._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert risk_manager._cleaned is True
    assert not hasattr(risk_manager, '_lock')


def test_register_conduit_ignores_invalid_inputs() -> None:
    """Verify empty conduit ids or None spellbooks are ignored."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)

    risk_manager.register_conduit("", _SpellbookStub())
    risk_manager.register_conduit("conduit-1", None)

    assert risk_manager._conduit_states == {}


def test_register_and_unregister_conduit_manage_lineage_membership() -> None:
    """Verify conduit registration seeds lineage membership and unregister removes it."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    local_spell = _SpellStub(SpellValidity.valid)
    contracted_spell = _SpellStub(SpellValidity.valid)
    contracted_spell.spell_index = _SpellIndexStub("lineage-2", "spell-2")
    spellbook._spells = {"local": local_spell}
    spellbook._contracted_spells = {"peer": {"contracted": contracted_spell}}

    risk_manager.register_conduit("conduit-1", spellbook)

    assert risk_manager._conduit_states["conduit-1"].lineages == {"lineage-1", "lineage-2"}
    assert risk_manager._lineage_conduits["lineage-1"] == {"conduit-1"}
    assert risk_manager._lineage_conduits["lineage-2"] == {"conduit-1"}

    risk_manager.unregister_conduit("conduit-1")

    assert "conduit-1" not in risk_manager._conduit_states
    assert "lineage-1" not in risk_manager._lineage_conduits
    assert "lineage-2" not in risk_manager._lineage_conduits


def test_register_and_unregister_spell_ignore_missing_inputs_and_missing_state() -> None:
    """Verify spell registration/removal no-op on invalid inputs or missing conduit state."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spell = _SpellStub(SpellValidity.valid)

    risk_manager.register_spell("", spell)
    risk_manager.register_spell("conduit-1", None)
    risk_manager.unregister_spell("", spell)
    risk_manager.unregister_spell("conduit-1", None)

    assert risk_manager._conduit_states == {}


def test_register_spell_handles_cleaned_spell_and_missing_lineage() -> None:
    """Verify register_spell returns when lineage information is unavailable."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    cleaned_spell = _SpellStub(SpellValidity.valid)
    cleaned_spell._cleaned = True

    risk_manager.register_spell("conduit-1", cleaned_spell)

    assert risk_manager._conduit_states["conduit-1"].lineages == set()


def test_register_spell_handles_missing_resolution_state_current_lookup() -> None:
    """Verify register_spell tolerates a failing current-id lookup during pre-clear."""

    class _BrokenCurrentIndex:
        def __init__(self) -> None:
            self.id = "lineage-broken"
            self._reads = 0

        @property
        def current(self):
            self._reads += 1
            if self._reads == 1:
                raise RuntimeError("broken current")
            return "spell-broken"

    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    spell = _SpellStub(SpellValidity.valid)
    spell.spell_index = _BrokenCurrentIndex()

    risk_manager.register_spell("conduit-1", spell)

    assert "lineage-broken" in risk_manager._conduit_states["conduit-1"].lineages


def test_unregister_spell_removes_lineage_and_refreshes_flag() -> None:
    """Verify unregister_spell removes lineages and clears conduit membership."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    spell = _SpellStub(SpellValidity.invalid)

    risk_manager.register_conduit("conduit-1", spellbook)
    risk_manager.register_spell("conduit-1", spell)
    assert spellbook._spellbook_validation_required is True

    risk_manager.unregister_spell("conduit-1", spell)

    assert risk_manager._conduit_states["conduit-1"].lineages == set()
    assert "lineage-1" not in risk_manager._lineage_conduits
    assert spellbook._spellbook_validation_required is False


def test_validity_change_callbacks_update_risk_sets() -> None:
    """Verify structural and resolution callbacks update risk state and flags."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    spell = _SpellStub(SpellValidity.valid)

    risk_manager.register_conduit("conduit-1", spellbook)
    risk_manager.register_spell("conduit-1", spell)
    assert spellbook._spellbook_validation_required is False

    risk_manager.on_structural_validity_change("lineage-1", SpellValidity.invalid)
    assert "lineage-1" in risk_manager._conduit_states["conduit-1"].risky_structural
    assert spellbook._spellbook_validation_required is True

    risk_manager.on_structural_validity_change("lineage-1", SpellValidity.valid)
    risk_manager.on_resolution_validity_change("conduit-1", "spell-1", SpellValidity.invalid)
    assert "spell:spell-1" in risk_manager._conduit_states["conduit-1"].risky_resolution
    assert spellbook._spellbook_validation_required is True


def test_resolution_change_falls_back_to_spell_key_when_lineage_unknown() -> None:
    """Verify resolution changes track a spell-key fallback when lineage lookup misses."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    risk_manager.on_resolution_validity_change("conduit-1", "missing-spell", SpellValidity.invalid)

    assert "spell:missing-spell" in risk_manager._conduit_states["conduit-1"].risky_resolution


def test_unregister_conduit_handles_empty_id_and_missing_lineage_bucket() -> None:
    """Verify unregister_conduit ignores empty ids and missing lineage indexes safely."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    spell = _SpellStub(SpellValidity.valid)

    risk_manager.register_conduit("conduit-1", spellbook)
    risk_manager.register_spell("conduit-1", spell)
    risk_manager.unregister_conduit("")

    risk_manager._lineage_conduits.pop("lineage-1", None)
    risk_manager.unregister_conduit("conduit-1")

    assert "conduit-1" not in risk_manager._conduit_states


def test_register_and_unregister_spell_ignore_missing_state_paths() -> None:
    """Verify spell registration/removal return safely when conduit state is absent."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spell = _SpellStub(SpellValidity.valid)

    risk_manager.register_spell("missing-conduit", spell)
    risk_manager.unregister_spell("missing-conduit", spell)

    assert risk_manager._conduit_states == {}


def test_unregister_spell_ignores_cleaned_spell_without_lineage() -> None:
    """Verify unregister_spell returns when the spell has no resolvable lineage."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    cleaned_spell = _SpellStub(SpellValidity.valid)
    cleaned_spell._cleaned = True

    risk_manager.unregister_spell("conduit-1", cleaned_spell)

    assert risk_manager._conduit_states["conduit-1"].lineages == set()


def test_validity_change_callbacks_ignore_empty_inputs() -> None:
    """Verify validity-change callbacks return safely on empty identifiers."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    risk_manager.on_structural_validity_change("", SpellValidity.invalid)
    risk_manager.on_resolution_validity_change("", "spell-1", SpellValidity.invalid)
    risk_manager.on_resolution_validity_change("conduit-1", "", SpellValidity.invalid)

    assert spellbook._spellbook_validation_required is False


def test_iter_spellbook_spells_swallows_lookup_errors() -> None:
    """Verify spell iteration tolerates broken spellbook maps."""

    class _BrokenSpellbook:
        @property
        def _spells(self):
            raise RuntimeError("broken spells")

        @property
        def _contracted_spells(self):
            return None

    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)

    assert risk_manager._iter_spellbook_spells(_BrokenSpellbook()) == []


def test_resolve_lineage_id_from_spell_id_returns_lineage_when_present() -> None:
    """Verify version-id lookup returns the stored lineage id when present."""

    class _State:
        def __init__(self, spell_index_id: str) -> None:
            self.spell_index_id = spell_index_id

    class _States(_SpellSystemStatesStub):
        def get_by_spell_id(self, spell_id: str):
            return _State("lineage-from-state")

    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    risk_manager = RiskManager(_States(resolution_state))

    assert risk_manager._resolve_lineage_id_from_spell_id("spell-1") == "lineage-from-state"


def test_internal_helpers_cover_unknown_and_safe_paths() -> None:
    """Verify helper fallbacks for unknown/cleaned/safe validity paths."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    spell = _SpellStub(SpellValidity.valid)
    cleaned_spell = _SpellStub(SpellValidity.valid)
    cleaned_spell._cleaned = True

    assert risk_manager._resolve_lineage_id(cleaned_spell) is None
    assert risk_manager._resolve_lineage_id_from_spell_id("missing") is None
    assert risk_manager._get_structural_validity(cleaned_spell) is SpellValidity.cleaned

    spell._state = None
    assert risk_manager._get_structural_validity(spell) is SpellValidity.unknown
    no_resolution_states = _SpellSystemStatesStub(None)
    risk_manager_without_resolution = RiskManager(no_resolution_states)
    assert (
        risk_manager_without_resolution._get_resolution_validity("missing-conduit", spell)
        is SpellValidity.unknown
    )
    assert risk_manager._get_resolution_validity("conduit-1", cleaned_spell) is SpellValidity.unknown

    risk_manager._update_structural_risk("missing-conduit", "lineage-1", SpellValidity.invalid)
    risk_manager._update_resolution_risk("missing-conduit", "lineage-1", SpellValidity.invalid)

    assert RiskManager._is_risky(None) is True
    assert RiskManager._is_risky(SpellValidity.valid) is False
    assert RiskManager._is_risky(SpellValidity.invalid) is True


def test_refresh_spellbook_flag_ignores_missing_spellbook_and_swallow_errors() -> None:
    """Verify spellbook flag refresh no-ops or swallows exceptions safely."""
    resolution_state = _ResolutionStateStub(SpellValidity.valid)
    states = _SpellSystemStatesStub(resolution_state)
    risk_manager = RiskManager(states)
    spellbook = _SpellbookStub()
    risk_manager.register_conduit("conduit-1", spellbook)

    risk_manager._conduit_states["conduit-1"].spellbook = None
    risk_manager._refresh_spellbook_flag("conduit-1")

    failing_spellbook = _SpellbookStub()
    failing_spellbook._set_spellbook_validation_required = lambda required: (_ for _ in ()).throw(RuntimeError("boom"))
    risk_manager._conduit_states["conduit-1"].spellbook = failing_spellbook
    risk_manager._refresh_spellbook_flag("conduit-1")
