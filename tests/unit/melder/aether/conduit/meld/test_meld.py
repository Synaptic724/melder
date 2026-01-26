"""Contract tests for Meld resolution, gating, and activation flow."""
from threading import RLock
from typing import Any, Callable, Iterable, Dict
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.meld import Meld
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)


class _SpellIndexStub:
    """
    Minimal spell index stub with current/id fields.

    This is enough for Meld error messages and change-control checks.
    """

    def __init__(self, current: str, lineage_id: str | None = None) -> None:
        """
        Initialize a stub spell index with current and lineage identifiers.

        Args:
            current: The current version id for the spell.
            lineage_id: Optional lineage id for the spell; defaults to a derived value.
        """
        self.current = current
        self.id = lineage_id or f"lineage-{current}"


class _SystemStateStub:
    """
    Minimal spell system state stub for validity gating tests.

    Tracks validity and any state flags, plus set_validity calls.
    """

    def __init__(
        self,
        *,
        validity: SpellValidity,
        flags: Iterable[Any] | None = None,
    ) -> None:
        """
        Initialize a stub system state with validity and optional flags.

        Args:
            validity: Initial SpellValidity value.
            flags: Optional iterable of state flags.
        """
        self.validity = validity
        self.flags = set(flags or [])
        self.set_validity_calls: list[SpellValidity] = []

    def set_validity(self, value: SpellValidity) -> None:
        """
        Update validity and record the change.

        Args:
            value: The new validity value.
        """
        self.validity = value
        self.set_validity_calls.append(value)


class _TrackingLock:
    """
    Simple re-entrant lock that exposes a locked flag for tests.
    """

    def __init__(self) -> None:
        """
        Initialize the tracking lock.
        """
        self._lock = RLock()
        self._count = 0

    def acquire(self) -> None:
        """
        Acquire the underlying lock and update the count.
        """
        self._lock.acquire()
        self._count += 1

    def release(self) -> None:
        """
        Release the underlying lock and update the count.
        """
        self._count -= 1
        self._lock.release()

    def __enter__(self) -> "_TrackingLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()

    @property
    def locked(self) -> bool:
        """
        Return True when the lock is currently held.
        """
        return self._count > 0


class _SpellStub:
    """
    Minimal spell stub with fields used by Meld.

    Provides lifecycle hooks, existence settings, and state gating metadata.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: str = "Spell",
        spellframe: str = "frame",
        existence: Existence = Existence.unique,
        system_state: _SystemStateStub | None = None,
        spell_system_states: Any | None = None,
        spellbook: Any | None = None,
        is_broken: bool = False,
        is_existing_creation: bool = False,
        user_created_object: Any | None = None,
        is_class_spell: bool = False,
        is_method_spell: bool = False,
        is_lambda_spell: bool = False,
        has_disposal_methods: bool = True,
        disposal_method_names: list[str] | None = None,
        owner_creations: Any | None = None,
        owner_conduit_id: str = "conduit-1",
        owner_conduit_name: str = "Conduit",
        aetheric_frame: str = "default",
        spell_index: _SpellIndexStub | None = None,
        spell_type: str = "test",
        validity_after_run: SpellValidity | None = None,
        broken_after_run: bool | None = None,
    ) -> None:
        """
        Initialize a stub spell with the requested properties.

        Args:
            spell_id: Unique spell identifier.
            spell_name: Human-readable spell name.
            spellframe: Spell frame identifier.
            existence: Existence scope for the spell.
            system_state: Optional system state for validity gating.
            spell_system_states: Optional system state registry for resolution gating.
            spellbook: Optional spellbook stub for resolution phase execution.
            is_broken: Whether the spell is broken.
            is_existing_creation: Whether the spell is an existing-creation spell.
            user_created_object: Pre-created instance for existing-creation spells.
            is_class_spell: Whether the spell is class-based.
            is_method_spell: Whether the spell is method-based.
            is_lambda_spell: Whether the spell is lambda-based.
            has_disposal_methods: Whether the spell declares disposal methods.
            disposal_method_names: Optional list of disposal method names.
            owner_creations: Owner creations container.
            owner_conduit_id: Owning conduit id.
            owner_conduit_name: Owning conduit name.
            aetheric_frame: Aetheric frame name.
            spell_index: Spell index stub.
            spell_type: Spell type label used in error messages.
            validity_after_run: Validity to assign after structural phases.
            broken_after_run: Broken state to assign after structural phases.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.spell_index = spell_index or _SpellIndexStub(current=spell_id)
        self.existence = existence
        self.system_state = system_state
        self._spell_system_states = spell_system_states
        self._spellbook = spellbook
        self.is_broken = is_broken
        self.is_existing_creation = is_existing_creation
        self.user_created_object = user_created_object
        self.is_class_spell = is_class_spell
        self.is_method_spell = is_method_spell
        self.is_lambda_spell = is_lambda_spell
        self.has_disposal_methods = bool(has_disposal_methods)
        if disposal_method_names is None:
            self.disposal_method_names = ["cleanup"] if self.has_disposal_methods else []
        else:
            self.disposal_method_names = list(disposal_method_names)
        self._owner_creations = owner_creations
        self._owner_conduit_id = owner_conduit_id
        self._owner_conduit_name = owner_conduit_name
        self.aetheric_frame = aetheric_frame
        self.spell_type = spell_type
        self._lock = RLock()
        self._pre_hooks: list[Callable[..., Any]] = []
        self._activation_hooks: list[Callable[..., Any]] = []
        self._post_hooks: list[Callable[..., Any]] = []
        self._hooks_enabled: bool = False
        self.run_all_phases_calls = 0
        self.run_structural_phases_calls = 0
        self._validity_after_run = validity_after_run
        self._broken_after_run = broken_after_run

    def run_all_phases(self) -> None:
        """
        Record a run_all_phases call and apply post-run state mutations.
        """
        self.run_all_phases_calls += 1
        if self._validity_after_run is not None and self.system_state is not None:
            self.system_state.validity = self._validity_after_run
        if self._broken_after_run is not None:
            self.is_broken = self._broken_after_run

    def run_structural_phases(self) -> None:
        """
        Record a run_structural_phases call and apply post-run state mutations.
        """
        self.run_structural_phases_calls += 1
        if self._validity_after_run is not None and self.system_state is not None:
            self.system_state.validity = self._validity_after_run
        if self._broken_after_run is not None:
            self.is_broken = self._broken_after_run


class _SpellbookStub:
    """
    Minimal spellbook stub exposing the lookup maps Meld expects.
    """

    def __init__(
        self,
        *,
        spells: dict[Any, _SpellStub] | None = None,
        contracted_spells: dict[str, dict[Any, _SpellStub]] | None = None,
        lookup_spells: dict[tuple[str, str], Any] | None = None,
        lookup_contracted_spells: dict[str, dict[tuple[str, str], Any]] | None = None,
        aetheric_frame: str = "default",
        aether: Any | None = None,
    ) -> None:
        """
        Initialize stub spellbook maps.

        Args:
            spells: Local spell map keyed by spell index.
            contracted_spells: Contracted spell maps keyed by conduit id.
            lookup_spells: Local lookup map keyed by (frame, binding).
            lookup_contracted_spells: Contracted lookup maps per conduit.
            aetheric_frame: Aetheric frame name for change-control lookups.
            aether: Aether stub providing change-control managers.

        Notes:
            Builds spell_id lookup maps from the provided spell maps.
        """
        self._spells = spells or {}
        self._contracted_spells = contracted_spells or {}
        self._lookup_spells = lookup_spells or {}
        self._lookup_contracted_spells = lookup_contracted_spells or {}
        self._aetheric_frame = aetheric_frame
        self._aether = aether
        self._spells_by_id = {
            spell.spell_id: spell
            for spell in self._spells.values()
        }
        self._contracted_spells_by_id = {
            conduit_id: {
                spell.spell_id: spell
                for spell in spell_map.values()
            }
            for conduit_id, spell_map in self._contracted_spells.items()
        }
        self._spellbook_validation_required = True
        self._spell_id_pool: Dict[str, 'SpellIndex'] = {}


class _ChangeControlManagerStub:
    """
    Minimal change-control manager for dirty-root gating tests.
    """

    def __init__(self, *, dirty_roots: Iterable[str] | None = None) -> None:
        """
        Initialize the manager with a set of dirty root ids.

        Args:
            dirty_roots: Optional iterable of root ids marked dirty.
        """
        self._dirty_roots = set(dirty_roots or [])

    def is_root_dirty(self, root_id: str) -> bool:
        """
        Return True when the root id is marked dirty.

        Args:
            root_id: Spell root id to check.
        Returns:
            bool: True when the root id is dirty.
        """
        return root_id in self._dirty_roots


class _AetherStub:
    """
    Minimal Aether stub exposing a change-control manager.
    """

    def __init__(self, ccm: _ChangeControlManagerStub | None) -> None:
        """
        Initialize the stub with a change-control manager.

        Args:
            ccm: Change-control manager to return.
        """
        self._ccm = ccm

    def _get_change_control_manager(self, frame_name: str) -> _ChangeControlManagerStub | None:
        """
        Return the stored change-control manager.

        Args:
            frame_name: Aetheric frame name (unused in stub).
        Returns:
            Optional change-control manager.
        """
        return self._ccm


class _ConduitStub:
    """
    Minimal conduit stub for Creations spellspace tests.
    """

    def __init__(
        self,
        *,
        conduit_id: str,
        conduit_state: ConduitState,
        active_spellspace: Any | None = None,
    ) -> None:
        """
        Initialize a conduit stub with the required state.

        Args:
            conduit_id: Conduit id string.
            conduit_state: ConduitState enum value.
            active_spellspace: Optional active spellspace.
        """
        self._id = conduit_id
        self._logger = MagicMock()
        self._conduit_state = conduit_state
        self._active_spellspace = active_spellspace

    def get_active_spellspace(self) -> Any | None:
        """
        Return the currently active spellspace, if any.
        """
        return self._active_spellspace


class _SpellSpaceStub:
    """
    Minimal spellspace stub with id and owner conduit.
    """

    def __init__(self, *, spellspace_id: str, owner_conduit: _ConduitStub) -> None:
        """
        Initialize a stub spellspace with identity and ownership.

        Args:
            spellspace_id: Spellspace identifier.
            owner_conduit: Conduit that owns the spellspace.
        """
        self.id = spellspace_id
        self.owner_conduit = owner_conduit


class _ContextStub:
    """
    Minimal context stub for meld runtime cleanup checks.
    """

    def __init__(self) -> None:
        """
        Initialize the context stub.
        """
        self.cleaned = False

    def cleanup(self) -> None:
        """
        Mark the context as cleaned.
        """
        self.cleaned = True


def _make_meld(*, creations: Any | None = None, spellbook: _SpellbookStub | None = None) -> Meld:
    """
    Build a Meld instance with stubbed spellbook/creations.

    Args:
        creations: Optional creations container override.
        spellbook: Optional spellbook stub override.

    Returns:
        Meld: Meld instance ready for testing.
    """
    return Meld(
        creations=creations or MagicMock(),
        spellbook=spellbook or _SpellbookStub(),
    )


def _make_creations(
    *,
    conduit_id: str = "conduit-1",
    active_spellspace: Any | None = None,
) -> tuple[Creations, _ConduitStub]:
    """
    Build a Creations instance with a stub conduit.

    Args:
        conduit_id: Conduit id for the stub.
        active_spellspace: Optional active spellspace for the conduit.

    Returns:
        tuple[Creations, _ConduitStub]: Creations instance and backing conduit.
    """
    conduit = _ConduitStub(
        conduit_id=conduit_id,
        conduit_state=ConduitState.normal,
        active_spellspace=active_spellspace,
    )
    return Creations(False, [], conduit), conduit


def test_cleanup_clears_references_and_drops_runtime() -> None:
    """
    Verify Meld.cleanup releases references and drops the runtime reference.

    Contract:
        - Spellbook maps and creations references are cleared.
        - Runtime reference is dropped without invoking cleanup.
        - Meld hooks are cleared and removed.
    """
    class _RuntimeStub:
        """
        Minimal runtime stub that records cleanup calls.
        """

        def __init__(self) -> None:
            """
            Initialize the cleanup flag.
            """
            self.cleaned = False

        def cleanup(self) -> None:
            """
            Mark the runtime as cleaned.
            """
            self.cleaned = True

    meld = _make_meld()
    runtime = _RuntimeStub()
    hook_list: list[Callable[..., Any]] = [lambda: None]
    meld._runtime = runtime
    meld._meld_hooks = {"on_meld_pre_resolve": hook_list}

    meld.cleanup()

    assert runtime.cleaned is False
    assert hook_list == [hook_list[0]]
    assert meld._owned_spells is None
    assert meld._contracted_spells is None
    assert meld._lookup_owned_spells is None
    assert meld._lookup_contracted_spells is None
    assert meld._creations is None
    assert meld._runtime is None
    assert meld._meld_hooks is None


def test_meld_uses_comprehensive_path_when_spell_hooks_enabled() -> None:
    """
    Verify meld selects the comprehensive path when spell hooks are enabled.

    Contract:
        - _comprehensive_meld_with_hooks is called when spell._hooks_enabled is True.
        - _meld_without_hooks is not used in that case.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1")
    spell._hooks_enabled = True

    meld._resolve_spell = MagicMock(return_value=spell)
    meld._comprehensive_meld_with_hooks = MagicMock(return_value="result")
    meld._meld_without_hooks = MagicMock(return_value="without")

    assert meld.meld(spell="spell-1") == "result"
    meld._comprehensive_meld_with_hooks.assert_called_once_with(
        target_spell=spell,
        override_map=None,
    )
    meld._meld_without_hooks.assert_not_called()


def test_meld_uses_comprehensive_path_when_meld_hooks_present() -> None:
    """
    Verify meld selects the comprehensive path when meld-level hooks exist.

    Contract:
        - _comprehensive_meld_with_hooks is called when _meld_hooks is non-empty.
        - _meld_without_hooks is not used in that case.
    """
    meld = _make_meld()
    meld._meld_hooks = {"on_meld_pre_resolve": [lambda: None]}
    spell = _SpellStub(spell_id="spell-1")
    spell._hooks_enabled = False

    meld._resolve_spell = MagicMock(return_value=spell)
    meld._comprehensive_meld_with_hooks = MagicMock(return_value="result")
    meld._meld_without_hooks = MagicMock(return_value="without")

    assert meld.meld(spell="spell-1") == "result"
    meld._comprehensive_meld_with_hooks.assert_called_once_with(
        target_spell=spell,
        override_map=None,
    )
    meld._meld_without_hooks.assert_not_called()


def test_meld_uses_without_hooks_path_when_no_hooks() -> None:
    """
    Verify meld selects the minimal path when no hooks are configured.

    Contract:
        - _meld_without_hooks is called when there are no meld or spell hooks.
        - _comprehensive_meld_with_hooks is not used in that case.
    """
    meld = _make_meld()
    meld._meld_hooks = {}
    spell = _SpellStub(spell_id="spell-1")
    spell._hooks_enabled = False

    meld._resolve_spell = MagicMock(return_value=spell)
    meld._comprehensive_meld_with_hooks = MagicMock(return_value="with")
    meld._meld_without_hooks = MagicMock(return_value="result")

    assert meld.meld(spell="spell-1") == "result"
    meld._meld_without_hooks.assert_called_once_with(
        target_spell=spell,
        override_map=None,
    )
    meld._comprehensive_meld_with_hooks.assert_not_called()


def test_meld_requires_identity_source() -> None:
    """
    Verify meld rejects calls with no spell identity.

    Contract:
        - At least one of spell_name, spell, or spellframe is required.
    """
    meld = _make_meld()
    with pytest.raises(ValueError, match="requires at least one"):
        meld.meld()


def test_normalize_spell_override_none_returns_none() -> None:
    """
    Verify override normalization returns None for missing overrides.

    Contract:
        - None override payload stays None.
    """
    meld = _make_meld()
    assert meld._normalize_spell_override(None) is None


def test_normalize_spell_override_dict_returns_copy() -> None:
    """
    Verify dict overrides are shallow-copied.

    Contract:
        - Returned overrides equal the input mapping.
        - Returned mapping is a distinct object.
    """
    meld = _make_meld()
    payload = {"a": 1}
    normalized = meld._normalize_spell_override(payload)
    assert normalized == payload
    assert normalized is not payload


@pytest.mark.parametrize("payload", [[1, 2], ("a", "b")])
def test_normalize_spell_override_args_payloads(payload: list | tuple) -> None:
    """
    Verify positional overrides are normalized into __args__ lists.

    Contract:
        - list/tuple payloads map to {"__args__": [...]}.
    """
    meld = _make_meld()
    normalized = meld._normalize_spell_override(payload)
    assert normalized == {"__args__": list(payload)}


def test_normalize_spell_override_invalid_type_raises() -> None:
    """
    Verify override normalization rejects unsupported types.

    Contract:
        - Non dict/list/tuple overrides raise TypeError.
    """
    meld = _make_meld()
    with pytest.raises(TypeError, match="spell_override must be a dict"):
        meld._normalize_spell_override(object())


def test_resolve_spell_by_id_finds_owned_spell() -> None:
    """
    Verify spell_id resolution returns a local spell when present.

    Contract:
        - Owned spells are scanned and returned on match.
    """
    spell = _SpellStub(spell_id="spell-1")
    spellbook = _SpellbookStub(spells={object(): spell})
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell_by_id("spell-1") is spell


def test_resolve_spell_by_id_finds_contracted_spell() -> None:
    """
    Verify spell_id resolution returns contracted spells when local misses.

    Contract:
        - Contracted spells are scanned after owned spells.
    """
    spell = _SpellStub(spell_id="spell-2")
    spellbook = _SpellbookStub(
        spells={},
        contracted_spells={"peer": {object(): spell}},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell_by_id("spell-2") is spell


def test_resolve_spell_by_id_raises_when_missing() -> None:
    """
    Verify spell_id resolution raises when no spell exists.

    Contract:
        - Missing ids raise KeyError.
    """
    meld = _make_meld()
    with pytest.raises(KeyError, match="No spell found with spell_id"):
        meld._resolve_spell_by_id("missing")


def test_resolve_spell_by_lookup_key_prefers_local() -> None:
    """
    Verify lookup-key resolution returns local spells before contracted.

    Contract:
        - Local lookup takes precedence when both maps match.
    """
    lookup_key = ("frame", "binding")
    local_index = object()
    contracted_index = object()
    local_spell = _SpellStub(spell_id="local")
    contracted_spell = _SpellStub(spell_id="contracted")
    spellbook = _SpellbookStub(
        spells={local_index: local_spell},
        contracted_spells={"peer": {contracted_index: contracted_spell}},
        lookup_spells={lookup_key: local_index},
        lookup_contracted_spells={"peer": {lookup_key: contracted_index}},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell_by_lookup_key(lookup_key) is local_spell


def test_resolve_local_by_lookup_key_raises_when_owned_map_missing() -> None:
    """
    Verify local resolution raises when owned spell map is unavailable.

    Contract:
        - If lookup hits but owned map is None, raise RuntimeError.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={},
        lookup_spells={lookup_key: spell_index},
    )
    meld = _make_meld(spellbook=spellbook)
    meld._owned_spells = None
    with pytest.raises(RuntimeError, match="owned spell map is not available"):
        meld._resolve_local_by_lookup_key(lookup_key)


def test_resolve_local_by_lookup_key_raises_when_spell_missing() -> None:
    """
    Verify local resolution raises when the spell object is missing.

    Contract:
        - Lookup hits with missing spell triggers RuntimeError.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={},
        lookup_spells={lookup_key: spell_index},
    )
    meld = _make_meld(spellbook=spellbook)
    with pytest.raises(RuntimeError, match="no spell object found"):
        meld._resolve_local_by_lookup_key(lookup_key)


def test_resolve_contracted_by_lookup_key_raises_when_map_missing() -> None:
    """
    Verify contracted resolution raises when contracted map is unavailable.

    Contract:
        - Lookup hit with missing contracted map raises RuntimeError.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        contracted_spells={},
        lookup_contracted_spells={"peer": {lookup_key: spell_index}},
    )
    meld = _make_meld(spellbook=spellbook)
    meld._contracted_spells = None
    with pytest.raises(RuntimeError, match="contracted spell map is not available"):
        meld._resolve_contracted_by_lookup_key(lookup_key)


def test_resolve_contracted_by_lookup_key_raises_when_conduit_missing() -> None:
    """
    Verify contracted resolution raises when conduit spell map is absent.

    Contract:
        - Lookup hit with missing conduit map raises RuntimeError.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        contracted_spells={},
        lookup_contracted_spells={"peer": {lookup_key: spell_index}},
    )
    meld = _make_meld(spellbook=spellbook)
    with pytest.raises(RuntimeError, match="no contracted spell map is present"):
        meld._resolve_contracted_by_lookup_key(lookup_key)


def test_resolve_contracted_by_lookup_key_raises_when_spell_missing() -> None:
    """
    Verify contracted resolution raises when the spell object is missing.

    Contract:
        - Lookup hit with missing spell triggers RuntimeError.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        contracted_spells={"peer": {}},
        lookup_contracted_spells={"peer": {lookup_key: spell_index}},
    )
    meld = _make_meld(spellbook=spellbook)
    with pytest.raises(RuntimeError, match="no spell object found"):
        meld._resolve_contracted_by_lookup_key(lookup_key)


def test_fire_meld_hooks_invokes_hooks() -> None:
    """
    Verify meld hooks are invoked when registered.

    Contract:
        - _fire_meld_hooks executes the hook list for the name.
    """
    meld = _make_meld()
    calls: list[str] = []

    def hook(spell: _SpellStub) -> None:
        """
        Record hook invocation.
        """
        calls.append(spell.spell_id)

    meld.set_meld_hooks({"on_meld_pre_resolve": [hook]})
    spell = _SpellStub(spell_id="spell-1")

    meld._fire_meld_hooks("on_meld_pre_resolve", spell)

    assert calls == ["spell-1"]


def test_fire_meld_hooks_wraps_errors() -> None:
    """
    Verify hook exceptions are wrapped in HookExecutionError.

    Contract:
        - Hook errors raise HookExecutionError with hook details.
    """
    meld = _make_meld()

    def boom() -> None:
        """
        Raise a hook error for testing.
        """
        raise ValueError("bad hook")

    meld.set_meld_hooks({"on_meld_pre_resolve": [boom]})
    with pytest.raises(HookExecutionError, match="on_meld_pre_resolve"):
        meld._fire_meld_hooks("on_meld_pre_resolve")


def test_ensure_lineage_resolvable_skips_without_state() -> None:
    """
    Verify lineage gating is skipped without system state.

    Contract:
        - Missing system_state results in no revalidation.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1", system_state=None)

    meld._ensure_lineage_resolvable(spell)

    assert spell.run_structural_phases_calls == 0


def test_ensure_lineage_resolvable_revalidates_unknown_success() -> None:
    """
    Verify unknown validity triggers revalidation to valid.

    Contract:
        - run_structural_phases is called for unknown validity.
        - validation succeeds when validity becomes valid.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.unknown)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        validity_after_run=SpellValidity.valid,
    )

    meld._ensure_lineage_resolvable(spell)

    assert spell.run_structural_phases_calls == 1
    assert state.validity is SpellValidity.valid


def test_ensure_lineage_resolvable_marks_invalid_for_broken() -> None:
    """
    Verify broken spells are pinned invalid after revalidation.

    Contract:
        - broken spells trigger SpellbookValidationError and invalid state.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.unknown)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        is_broken=True,
    )

    with pytest.raises(SpellbookValidationError):
        meld._ensure_lineage_resolvable(spell)

    assert state.validity is SpellValidity.invalid


def test_ensure_lineage_resolvable_raises_when_not_valid_after_phases() -> None:
    """
    Verify revalidation fails when validity stays non-valid.

    Contract:
        - post-run validity must be valid or SpellbookValidationError raises.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.unknown)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        validity_after_run=SpellValidity.gated,
    )

    with pytest.raises(SpellbookValidationError):
        meld._ensure_lineage_resolvable(spell)

    assert spell.run_structural_phases_calls == 1


def test_gated_validation_required_returns_false_without_state() -> None:
    """
    Verify gated validation short-circuits without system state.

    Contract:
        - Missing system_state returns False.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1", system_state=None)
    assert meld._gated_validation_required(spell) is False


def test_gated_validation_required_returns_false_for_valid() -> None:
    """
    Verify valid lineages are not gated.

    Contract:
        - SpellValidity.valid returns False.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.valid)
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    assert meld._gated_validation_required(spell) is False


@pytest.mark.parametrize("validity", [SpellValidity.unknown, SpellValidity.gated])
def test_gated_validation_required_returns_true_for_unknown_or_gated(
    validity: SpellValidity,
) -> None:
    """
    Verify unknown and gated lineages require validation.

    Contract:
        - unknown/gated validity returns True.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=validity)
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    assert meld._gated_validation_required(spell) is True


@pytest.mark.parametrize("validity", [SpellValidity.invalid, SpellValidity.disabled])
def test_gated_validation_required_raises_for_invalid_or_disabled(
    validity: SpellValidity,
) -> None:
    """
    Verify invalid/disabled lineages are blocked.

    Contract:
        - invalid/disabled validity raises SpellbookValidationError.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=validity)
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    with pytest.raises(SpellbookValidationError):
        meld._gated_validation_required(spell)


def test_gated_validation_required_transfer_in_progress_raises() -> None:
    """
    Verify transfer-in-progress flags raise SpellbookValidationError.

    Contract:
        - transfer_in_progress flags block resolution for invalid/disabled lineages.
    """
    meld = _make_meld()
    state = _SystemStateStub(
        validity=SpellValidity.invalid,
        flags=[SpellState.transfer_in_progress],
    )
    spell = _SpellStub(spell_id="spell-1", system_state=state)

    with pytest.raises(SpellbookValidationError) as exc_info:
        meld._gated_validation_required(spell)

    assert "spell-1" in str(exc_info.value)


def test_gated_validation_required_blocks_dirty_root() -> None:
    """
    Verify dirty roots raise MeldExecutionError under change-control checks.

    Contract:
        - Dirty root ids trigger MeldExecutionError for unknown validity values.
    """
    dirty_roots = {"spell-1"}
    ccm = _ChangeControlManagerStub(dirty_roots=dirty_roots)
    aether = _AetherStub(ccm)
    spellbook = _SpellbookStub(aetheric_frame="default", aether=aether)
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=object())
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    spell._spellbook = spellbook

    with pytest.raises(MeldExecutionError, match="dirty under change-control"):
        meld._gated_validation_required(spell)


def test_get_existing_creation_unique_returns_instance() -> None:
    """
    Verify unique existence returns the cached creation.

    Contract:
        - Creations.unique returns the stored instance.
    """
    creations, _ = _make_creations()
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique)
    instance = object()
    creations.add_unique(spell.spell_id, instance)
    meld = _make_meld(creations=creations)

    assert meld._get_existing_creation(spell) is instance


def test_get_existing_creation_many_returns_none() -> None:
    """
    Verify many existence never reuses instances.

    Contract:
        - Existence.many always returns None.
    """
    creations, _ = _make_creations()
    spell = _SpellStub(spell_id="spell-1", existence=Existence.many)
    creations.add_many(spell.spell_id, object())
    meld = _make_meld(creations=creations)

    assert meld._get_existing_creation(spell) is None


def test_get_existing_creation_spellspace_requires_active_spellspace() -> None:
    """
    Verify spellspace existence requires an active spellspace.

    Contract:
        - Missing spellspace raises SpellSpaceScopeError.
    """
    creations, _ = _make_creations()
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique_per_spell_space)
    meld = _make_meld(creations=creations)

    with pytest.raises(SpellSpaceScopeError, match="active SpellSpace"):
        meld._get_existing_creation(spell)


def test_get_existing_creation_spellspace_owner_mismatch_raises() -> None:
    """
    Verify spellspace owner mismatch raises a scope error.

    Contract:
        - Active spellspace must belong to the same conduit.
    """
    creations, conduit = _make_creations()
    other_conduit = _ConduitStub(
        conduit_id="conduit-2",
        conduit_state=ConduitState.normal,
    )
    conduit._active_spellspace = _SpellSpaceStub(
        spellspace_id="space-1",
        owner_conduit=other_conduit,
    )
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique_per_spell_space)
    meld = _make_meld(creations=creations)

    with pytest.raises(SpellSpaceScopeError, match="belongs to a different conduit"):
        meld._get_existing_creation(spell)


def test_get_existing_creation_spellspace_returns_instance() -> None:
    """
    Verify spellspace existence returns the spellspace-scoped instance.

    Contract:
        - Matching spellspace bucket returns the instance.
    """
    creations, conduit = _make_creations()
    conduit._active_spellspace = _SpellSpaceStub(
        spellspace_id="space-1",
        owner_conduit=conduit,
    )
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique_per_spell_space)
    instance = object()
    creations.register_spellspace_creation("space-1", spell.spell_id, instance)
    meld = _make_meld(creations=creations)

    assert meld._get_existing_creation(spell) is instance


def test_meld_reuses_existing_instance_without_activation_hooks() -> None:
    """
    Verify meld reuse skips activation hooks and registration.

    Contract:
        - pre/post hooks execute.
        - activation hooks do not execute when reusing.
        - meld_by_spell_type and register_spell are not called.
    """
    meld = _make_meld()
    events: list[str] = []

    def pre_hook() -> None:
        """
        Record a pre-hook invocation.
        """
        events.append("pre")

    def post_hook() -> None:
        """
        Record a post-hook invocation.
        """
        events.append("post")

    def activation_hook(_: Any) -> None:
        """
        Record activation hooks to detect reuse.
        """
        events.append("activation")

    spell = _SpellStub(spell_id="spell-1")
    spell._pre_hooks = [pre_hook]
    spell._post_hooks = [post_hook]
    spell._activation_hooks = [activation_hook]
    spell._hooks_enabled = True

    meld._resolve_spell = MagicMock(return_value=spell)
    meld._get_existing_creation = MagicMock(return_value="reuse")
    meld._meld_by_spell_type = MagicMock()
    meld._register_spell = MagicMock()

    assert meld.meld(spell="spell-1") == "reuse"
    assert events == ["pre", "post"]
    meld._meld_by_spell_type.assert_not_called()
    meld._register_spell.assert_not_called()


def test_meld_creates_instance_and_runs_activation_hooks() -> None:
    """
    Verify meld creation path runs activation hooks and registration.

    Contract:
        - new instance path calls meld_by_spell_type.
        - activation hooks receive the created instance.
        - pre and post hooks still execute.
    """
    meld = _make_meld()
    events: list[str] = []

    def pre_hook() -> None:
        """
        Record a pre-hook invocation.
        """
        events.append("pre")

    def post_hook() -> None:
        """
        Record a post-hook invocation.
        """
        events.append("post")

    def activation_hook(instance: Any) -> None:
        """
        Record activation hooks with instance.
        """
        events.append(f"activation:{instance}")

    spell = _SpellStub(spell_id="spell-1")
    spell._pre_hooks = [pre_hook]
    spell._post_hooks = [post_hook]
    spell._activation_hooks = [activation_hook]
    spell._hooks_enabled = True

    meld._resolve_spell = MagicMock(return_value=spell)
    meld._get_existing_creation = MagicMock(return_value=None)
    meld._meld_by_spell_type = MagicMock(return_value="created")
    meld._register_spell = MagicMock()

    assert meld.meld(spell="spell-1", spell_override=[1, 2]) == "created"
    assert events == ["pre", "activation:created", "post"]
    meld._meld_by_spell_type.assert_called_once_with(
        spell,
        {"__args__": [1, 2]},
        caller_creations_lock_held=False,
    )
    meld._register_spell.assert_not_called()


def test_meld_unique_per_conduit_holds_creations_lock_during_construct() -> None:
    """
    Verify unique_per_conduit holds the caller creations lock during construction.

    Contract:
        - creations lock is held while _meld_by_spell_type runs.
        - caller_creations_lock_held is True for runtime invocations.
    """
    creations, _ = _make_creations()
    creations_lock = _TrackingLock()
    creations._lock = creations_lock
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique_per_conduit)
    spell._lock = _TrackingLock()
    meld = _make_meld(creations=creations)
    meld._resolve_spell = MagicMock(return_value=spell)
    meld._get_existing_creation = MagicMock(return_value=None)

    def _construct(
        _spell: _SpellStub,
        _overrides: dict[str, Any] | None,
        *,
        caller_creations_lock_held: bool = False,
    ) -> str:
        assert creations_lock.locked is True
        assert caller_creations_lock_held is True
        return "created"

    meld._meld_by_spell_type = MagicMock(side_effect=_construct)
    meld._register_spell = MagicMock()

    assert meld.meld(spell="spell-1") == "created"


def test_meld_shared_unique_holds_spell_lock_during_construct() -> None:
    """
    Verify shared unique existence holds the spell lock during construction.

    Contract:
        - spell lock is held while _meld_by_spell_type runs.
        - creations lock is not held during construction.
    """
    creations, _ = _make_creations()
    creations_lock = _TrackingLock()
    creations._lock = creations_lock
    spell_lock = _TrackingLock()
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique)
    spell._lock = spell_lock
    meld = _make_meld(creations=creations)
    meld._resolve_spell = MagicMock(return_value=spell)
    meld._get_existing_creation = MagicMock(return_value=None)

    def _construct(
        _spell: _SpellStub,
        _overrides: dict[str, Any] | None,
        *,
        caller_creations_lock_held: bool = False,
    ) -> str:
        assert spell_lock.locked is True
        assert creations_lock.locked is False
        assert caller_creations_lock_held is False
        return "created"

    meld._meld_by_spell_type = MagicMock(side_effect=_construct)
    meld._register_spell = MagicMock()

    assert meld.meld(spell="spell-1") == "created"


def test_meld_by_spell_type_existing_creation_returns_object() -> None:
    """
    Verify existing-creation spells return the pre-created object.

    Contract:
        - user_created_object is returned for existing-creation spells.
    """
    meld = _make_meld()
    instance = object()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=instance,
    )
    assert meld._meld_by_spell_type(spell, overrides=None) is instance


def test_meld_by_spell_type_existing_creation_requires_object() -> None:
    """
    Verify existing-creation spells require a user_created_object.

    Contract:
        - Missing user_created_object raises RuntimeError.
    """
    meld = _make_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=None,
    )
    with pytest.raises(RuntimeError, match="EXISTING_CREATION spell has no"):
        meld._meld_by_spell_type(spell, overrides=None)


def test_meld_by_spell_type_runtime_executes_and_cleans_context() -> None:
    """
    Verify runtime path executes and cleans the context.

    Contract:
        - runtime.execute is called for class/method/lambda spells.
        - context.cleanup is always called after execution.
    """
    meld = _make_meld()
    context = _ContextStub()
    meld._create_meld_context = MagicMock(return_value=context)
    meld._runtime = MagicMock()
    meld._runtime.execute = MagicMock(return_value="result")
    spell = _SpellStub(spell_id="spell-1", is_class_spell=True)

    assert meld._meld_by_spell_type(spell, overrides={"x": 1}) == "result"
    meld._runtime.execute.assert_called_once_with(context)
    assert context.cleaned is True


def test_meld_by_spell_type_runtime_cleans_context_on_error() -> None:
    """
    Verify runtime errors still trigger context cleanup.

    Contract:
        - context.cleanup runs even when runtime.execute raises.
    """
    meld = _make_meld()
    context = _ContextStub()
    meld._create_meld_context = MagicMock(return_value=context)
    meld._runtime = MagicMock()
    error = MeldExecutionError(
        spell_id="spell-1",
        spell_name="Spell",
        message="boom",
    )
    meld._runtime.execute = MagicMock(side_effect=error)
    spell = _SpellStub(spell_id="spell-1", is_class_spell=True)

    with pytest.raises(MeldExecutionError):
        meld._meld_by_spell_type(spell, overrides=None)

    assert context.cleaned is True


def test_meld_by_spell_type_unsupported_type_raises() -> None:
    """
    Verify unsupported spell types raise RuntimeError.

    Contract:
        - Non factory and non existing-creation spells are rejected.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1", spell_type="unknown")
    with pytest.raises(RuntimeError, match="Unsupported SpellType"):
        meld._meld_by_spell_type(spell, overrides=None)


def test_select_creations_for_spell_many_prefers_caller() -> None:
    """
    Verify Existence.many selects caller creations when available.

    Contract:
        - per-conduit lifetimes prefer caller creations.
    """
    caller_creations = object()
    owner_creations = object()
    meld = _make_meld(creations=caller_creations)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell) is caller_creations


def test_select_creations_for_spell_many_falls_back_to_owner() -> None:
    """
    Verify Existence.many falls back to owner creations when caller is missing.

    Contract:
        - per-conduit lifetimes use owner creations when caller creations are None.
    """
    owner_creations = object()
    meld = _make_meld()
    meld._creations = None
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell) is owner_creations


def test_select_creations_for_spell_spellspace_prefers_caller() -> None:
    """
    Verify Existence.unique_per_spell_space prefers caller creations.

    Contract:
        - spellspace lifetimes use caller creations when available.
    """
    caller_creations = object()
    owner_creations = object()
    meld = _make_meld(creations=caller_creations)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell) is caller_creations


def test_select_creations_for_spell_spellspace_falls_back_to_owner() -> None:
    """
    Verify Existence.unique_per_spell_space falls back to owner creations.

    Contract:
        - spellspace lifetimes use owner creations when caller is None.
    """
    owner_creations = object()
    meld = _make_meld()
    meld._creations = None
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell) is owner_creations


def test_resolve_instance_with_locks_many_constructs_and_returns_created() -> None:
    """
    Verify Existence.many constructs a new instance without reuse.

    Contract:
        - _meld_by_spell_type is called.
        - _register_spell is not called for non existing-creation spells.
        - created is True for Existence.many.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    spell = _SpellStub(spell_id="spell-1", existence=Existence.many)
    meld._meld_by_spell_type = MagicMock(return_value="created")
    meld._register_spell = MagicMock()
    meld._get_existing_creation = MagicMock(return_value="reuse")

    instance, created = meld._resolve_instance_with_locks(spell, overrides=None)

    assert instance == "created"
    assert created is True
    meld._meld_by_spell_type.assert_called_once_with(
        spell,
        None,
        caller_creations_lock_held=False,
    )
    meld._register_spell.assert_not_called()
    meld._get_existing_creation.assert_not_called()


def test_resolve_instance_with_locks_many_registers_existing_creation() -> None:
    """
    Verify Existence.many registers when the spell is an existing creation.

    Contract:
        - existing-creation spells are registered into creations for Existence.many.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        is_existing_creation=True,
        user_created_object=object(),
    )
    meld._meld_by_spell_type = MagicMock(return_value="created")
    meld._register_spell = MagicMock()

    instance, created = meld._resolve_instance_with_locks(spell, overrides=None)

    assert instance == "created"
    assert created is True
    meld._register_spell.assert_called_once_with(spell, "created", creations)


def test_resolve_instance_with_locks_spellspace_requires_creations() -> None:
    """
    Verify spellspace existences require caller creations.

    Contract:
        - Missing creations raise RuntimeError for spellspace lifetimes.
    """
    meld = _make_meld()
    meld._creations = None
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
        owner_creations=None,
    )
    with pytest.raises(RuntimeError, match="Caller creations are required"):
        meld._resolve_instance_with_locks(spell, overrides=None)


def test_resolve_instance_with_locks_shared_with_no_creations_uses_none() -> None:
    """
    Verify shared lifetimes can proceed without creations references.

    Contract:
        - _get_existing_creation is called with creations=None.
        - Instance construction proceeds when no cached instance is found.
    """
    meld = _make_meld()
    meld._creations = None
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=None,
        is_class_spell=True,
    )
    meld._get_existing_creation = MagicMock(return_value=None)
    meld._meld_by_spell_type = MagicMock(return_value="created")
    meld._register_spell = MagicMock()

    instance, created = meld._resolve_instance_with_locks(spell, overrides=None)

    assert instance == "created"
    assert created is True
    meld._get_existing_creation.assert_called_once_with(spell, None)
    meld._meld_by_spell_type.assert_called_once()


def test_ensure_lineage_resolvable_raises_for_invalid_state() -> None:
    """
    Verify invalid lineage validity raises SpellbookValidationError.

    Contract:
        - Invalid validity raises without attempting revalidation.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.invalid)
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    with pytest.raises(SpellbookValidationError):
        meld._ensure_lineage_resolvable(spell)


def test_ensure_lineage_resolvable_raises_for_disabled_state() -> None:
    """
    Verify disabled lineage validity raises SpellbookValidationError.

    Contract:
        - Disabled validity raises without attempting revalidation.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.disabled)
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    with pytest.raises(SpellbookValidationError):
        meld._ensure_lineage_resolvable(spell)


def test_gated_validation_required_unknown_without_dirty_raises() -> None:
    """
    Verify unknown validity values still raise validation errors when not dirty.

    Contract:
        - Unknown validity falls through to SpellbookValidationError when
          change-control reports the root as clean.
    """
    ccm = _ChangeControlManagerStub(dirty_roots=set())
    aether = _AetherStub(ccm)
    spellbook = _SpellbookStub(aetheric_frame="default", aether=aether)
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=object())
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    spell._spellbook = spellbook

    with pytest.raises(SpellbookValidationError):
        meld._gated_validation_required(spell)


def test_gated_validation_required_change_control_error_falls_back() -> None:
    """
    Verify change-control lookup errors do not mask validation failures.

    Contract:
        - Exceptions in change-control lookup fall through to validation errors.
    """
    class _FailingAether:
        """
        Change-control stub that raises on manager lookup.
        """

        def _get_change_control_manager(self, frame_name: str) -> None:
            """
            Raise to simulate change-control lookup failure.
            """
            raise RuntimeError("ccm lookup failed")

    spellbook = _SpellbookStub(aetheric_frame="default", aether=_FailingAether())
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=object())
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    spell._spellbook = spellbook

    with pytest.raises(SpellbookValidationError):
        meld._gated_validation_required(spell)


def test_cleanup_drops_runtime_without_invoking_cleanup() -> None:
    """
    Verify Meld.cleanup drops the runtime reference without invoking cleanup.

    Contract:
        - runtime.cleanup is not called.
        - runtime reference is dropped.
    """
    class _RuntimeStub:
        """
        Runtime stub that raises on cleanup.
        """

        def cleanup(self) -> None:
            """
            Raise if cleanup is invoked.
            """
            raise RuntimeError("cleanup should not be called")

    meld = _make_meld()
    meld._runtime = _RuntimeStub()

    meld.cleanup()

    assert meld._runtime is None


def test_resolve_spell_by_id_raises_when_maps_missing() -> None:
    """
    Verify spell-id resolution raises when maps are unavailable.

    Contract:
        - Missing maps still raise KeyError for unknown spell ids.
    """
    meld = _make_meld()
    meld._owned_spells = None
    meld._contracted_spells = None
    with pytest.raises(KeyError, match="No spell found with spell_id"):
        meld._resolve_spell_by_id("missing")
