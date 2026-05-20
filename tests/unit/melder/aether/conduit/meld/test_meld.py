"""Contract tests for Meld resolution, gating, and activation flow."""
from contextvars import ContextVar
from threading import RLock
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Dict
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
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


class _ResolutionStateStub:
    """
    Minimal conduit resolution state stub for gating tests.
    """

    def __init__(self) -> None:
        """
        Initialize resolution validity containers and call tracking.
        """
        self._root_validity: Dict[str, SpellValidity] = {}
        self._spell_validity: Dict[str, SpellValidity] = {}
        self.root_set_calls: list[tuple[str, SpellValidity, Any]] = []
        self.spell_set_calls: list[tuple[str, SpellValidity, Any]] = []

    def get_root_validity(self, root_id: str) -> SpellValidity:
        """
        Return the stored root validity, defaulting to valid.
        """
        return self._root_validity.get(root_id, SpellValidity.valid)

    def get_spell_validity(self, spell_id: str) -> SpellValidity:
        """
        Return the stored spell validity, defaulting to valid.
        """
        return self._spell_validity.get(spell_id, SpellValidity.valid)

    def set_root_validity(self, root_id: str, validity: SpellValidity, *, change_reason: Any = None) -> None:
        """
        Record a root validity update.
        """
        self._root_validity[root_id] = validity
        self.root_set_calls.append((root_id, validity, change_reason))

    def set_spell_validity(self, spell_id: str, validity: SpellValidity, *, change_reason: Any = None) -> None:
        """
        Record a spell validity update.
        """
        self._spell_validity[spell_id] = validity
        self.spell_set_calls.append((spell_id, validity, change_reason))


class _SpellSystemStatesStub:
    """
    Minimal SpellSystemStates stub exposing resolution state.
    """

    def __init__(self, resolution_state: _ResolutionStateStub) -> None:
        """
        Initialize the stub with a resolution state.
        """
        self._resolution_state = resolution_state

    def get_conduit_resolution_state(self, conduit_id: str) -> _ResolutionStateStub:
        """
        Return the stored resolution state.
        """
        return self._resolution_state

    def unregister_index(self, spell_index: object) -> None:
        """
        Purpose:
            Provide a cleanup-compatible no-op for Spellbook cleanup.
        Contract:
            - Does not raise.
        Args:
            spell_index: SpellIndex to unregister (unused).
        Returns:
            None.
        """
        return None


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


_DEFAULT_SYSTEM_STATE = object()


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
        system_state: _SystemStateStub | None | object = _DEFAULT_SYSTEM_STATE,
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
        has_mutation_override: bool = False,
        owner_creations: Any | None = None,
        owner_conduit_id: str = "conduit-1",
        owner_conduit_name: str = "Conduit",
        aetheric_frame: str = "default",
        spell_index: _SpellIndexStub | None = None,
        spell_type: str = "test",
        validity_after_run: SpellValidity | None = None,
        broken_after_run: bool | None = None,
        creation_context: Any | None = None,
        resolution_required: bool = False,
        resolution_complete: bool = True,
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
                When None, a default stub registry is created.
            spellbook: Optional spellbook stub for resolution phase execution.
            is_broken: Whether the spell is broken.
            is_existing_creation: Whether the spell is an existing-creation spell.
            user_created_object: Pre-created instance for existing-creation spells.
            is_class_spell: Whether the spell is class-based.
            is_method_spell: Whether the spell is method-based.
            is_lambda_spell: Whether the spell is lambda-based.
            has_disposal_methods: Whether the spell declares disposal methods.
            disposal_method_names: Optional list of disposal method names.
            has_mutation_override: Whether meld-time mutation overrides exist.
            owner_creations: Owner creations container.
            owner_conduit_id: Owning conduit id.
            owner_conduit_name: Owning conduit name.
            aetheric_frame: Aetheric frame name.
            spell_index: Spell index stub.
            spell_type: Spell type label used in error messages.
            validity_after_run: Validity to assign after structural phases.
            broken_after_run: Broken state to assign after structural phases.
            creation_context: Optional spell-owned creation context cache.
            resolution_required: Deferred runtime-resolution requirement flag.
            resolution_complete: Deferred runtime-resolution completion flag.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.spell_index = spell_index or _SpellIndexStub(current=spell_id)
        self.existence = existence
        if system_state is _DEFAULT_SYSTEM_STATE:
            system_state = _SystemStateStub(validity=SpellValidity.valid)
        self.system_state = system_state
        if spell_system_states is None:
            spell_system_states = _SpellSystemStatesStub(_ResolutionStateStub())
        self._spell_system_states = spell_system_states
        self._spellbook = spellbook
        self._compiler_artifact = SpellCompilerArtifact(spell_id)
        self.spell = lambda: None
        self.execution_plan_dispatch_route = None
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
        self.has_mutation_override = bool(has_mutation_override)
        self._owner_creations = owner_creations
        self._owner_conduit_id = owner_conduit_id
        self._owner_conduit_name = owner_conduit_name
        self.aetheric_frame = aetheric_frame
        self.spell_type = spell_type
        self._lock = RLock()
        self._creation_context = creation_context
        self._creation_context_factory = None
        if creation_context is None:
            self._creation_context_switch = SimpleNamespace(state=0)
        else:
            self._creation_context_switch = SimpleNamespace(state=2)
        self._pre_hooks: list[Callable[..., Any]] = []
        self._activation_hooks: list[Callable[..., Any]] = []
        self._post_hooks: list[Callable[..., Any]] = []
        self._hooks_enabled: bool = False
        self.resolution_required = bool(resolution_required)
        self.resolution_complete = bool(resolution_complete)
        self.run_all_phases_calls = 0
        self.run_structural_phases_calls = 0
        self._validity_after_run = validity_after_run
        self._broken_after_run = broken_after_run
        self._cleaned = False

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

    def check_cleaned(self) -> None:
        """
        Verify the stub spell has not been cleaned.

        Raises:
            RuntimeError: When the stub is flagged as cleaned.
        """
        if self._cleaned:
            raise RuntimeError("Spell has been cleaned.")

    def _get_or_build_creation_context(self) -> Any:
        """
        Resolve or build the spell-owned creation context through a stub factory.

        Contract:
            - Returns cached context when present and not cleaned.
            - Uses `_creation_context_factory.get_or_build_for_spell(self)` on miss.
            - Publishes built context back onto `_creation_context`.
        """
        creation_context = self._creation_context
        if creation_context is not None and not creation_context._cleaned:
            return creation_context
        factory = self._creation_context_factory
        if factory is None:
            raise RuntimeError("CreationContextFactory is not configured.")
        creation_context = factory.get_or_build_for_spell(self)
        self._creation_context = creation_context
        self._creation_context_switch.state = 2
        return creation_context


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
        self._logger = MagicMock()

    def _run_resolution_phases_for_target_spell(
        self,
        conduit_id: str,
        target_spell: Any,
    ) -> None:
        """
        Local resolution-phase hook used by Meld tests.

        Contract:
            - Default stub behavior is a no-op.
            - Tests may replace this method with a MagicMock side effect.
        """
        return None

    def _run_deferred_resolution_phases_for_target_spell(
        self,
        conduit_id: str,
        target_spell: Any,
    ) -> None:
        """
        Local deferred resolution hook used by Meld runtime gate tests.

        Contract:
            - Default stub behavior is a no-op.
            - Tests may replace this method with a MagicMock side effect.
        """
        return None


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

    def is_root_dirty(self, conduit_id: str, root_id: str) -> bool:
        """
        Return True when the root id is marked dirty.

        Args:
            conduit_id: Conduit id scope for the check.
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
        self.get_change_control_manager_calls = 0

    def _get_change_control_manager(self, frame_name: str) -> _ChangeControlManagerStub | None:
        """
        Return the stored change-control manager.

        Args:
            frame_name: Aetheric frame name (unused in stub).
        Returns:
            Optional change-control manager.
        """
        self.get_change_control_manager_calls += 1
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

    def __init__(self, *, spellspace_id: str, owner_conduit_id: str) -> None:
        """
        Initialize a stub spellspace with identity and ownership.

        Args:
            spellspace_id: Spellspace identifier.
            owner_conduit_id: Conduit id that owns the spellspace.
        """
        self.id = spellspace_id
        self.owner_conduit_id = owner_conduit_id


class _ContextStub:
    """
    Minimal context stub for creation-context cleanup checks.
    """

    def __init__(self) -> None:
        """
        Initialize the context stub.
        """
        self.reset_called = False
        self.cleanup_called = False
        self.last_reset_payload: dict[str, Any] | None = None

    def reset(
        self,
        *,
        root_spell: Any | None = None,
        overrides: dict[str, Any] | None = None,
        caller_creations: Any | None = None,
        caller_creations_lock_held: bool = False,
    ) -> None:
        """
        Mark the context as reset.
        """
        self.reset_called = True
        self.last_reset_payload = {
            "root_spell": root_spell,
            "overrides": overrides,
            "caller_creations": caller_creations,
            "caller_creations_lock_held": caller_creations_lock_held,
        }

    def cleanup(self) -> None:
        """
        Mark the context as cleaned.
        """
        self.cleanup_called = True


class _CreationContextStub:
    """
    Minimal CreationContext stub exposing the four compiled execution doors.

    Contract:
        - Tracks invocation door and payloads for assertions.
        - Exposes `_cleaned` so Meld cache-miss logic can rebuild when needed.
        - Returns caller-configurable payloads per door.
    """

    def __init__(
        self,
        *,
        no_hooks_no_overrides_result: Any = "no-hooks-no-overrides",
        no_hooks_overrides_result: Any = "no-hooks-overrides",
        hooks_no_overrides_result: tuple[Any, bool] = ("hooks-no-overrides", False),
        hooks_overrides_result: tuple[Any, bool] = ("hooks-overrides", False),
        cleaned: bool = False,
    ) -> None:
        """
        Initialize one four-door CreationContext test stub.

        Args:
            no_hooks_no_overrides_result:
                Return value for no-hooks no-overrides calls.
            no_hooks_overrides_result:
                Return value for no-hooks overrides calls.
            hooks_no_overrides_result:
                Return tuple `(instance, created)` for hooks no-overrides calls.
            hooks_overrides_result:
                Return tuple `(instance, created)` for hooks overrides calls.
            cleaned:
                Whether this context should appear cleaned.
        """
        self._cleaned = cleaned
        self.calls: list[str] = []
        self.last_caller_creations: Any = None
        self.last_overrides: dict[str, Any] | None = None
        self._no_hooks_no_overrides_result = no_hooks_no_overrides_result
        self._no_hooks_overrides_result = no_hooks_overrides_result
        self._hooks_no_overrides_result = hooks_no_overrides_result
        self._hooks_overrides_result = hooks_overrides_result

    def _execute_no_hooks_no_overrides_compiled(self, caller_creations: Any) -> Any:
        """
        Simulate no-hooks no-overrides compiled door.
        """
        self.calls.append("no_hooks_no_overrides")
        self.last_caller_creations = caller_creations
        self.last_overrides = None
        return self._no_hooks_no_overrides_result

    def _execute_no_hooks_overrides_compiled(
            self,
            caller_creations: Any,
            overrides: dict[str, Any],
    ) -> Any:
        """
        Simulate no-hooks overrides compiled door.
        """
        self.calls.append("no_hooks_overrides")
        self.last_caller_creations = caller_creations
        self.last_overrides = overrides
        return self._no_hooks_overrides_result

    def _execute_hooks_no_overrides_compiled(
            self,
            caller_creations: Any,
    ) -> tuple[Any, bool]:
        """
        Simulate hooks no-overrides compiled door.
        """
        self.calls.append("hooks_no_overrides")
        self.last_caller_creations = caller_creations
        self.last_overrides = None
        return self._hooks_no_overrides_result

    def _execute_hooks_overrides_compiled(
            self,
            caller_creations: Any,
            overrides: dict[str, Any],
    ) -> tuple[Any, bool]:
        """
        Simulate hooks overrides compiled door.
        """
        self.calls.append("hooks_overrides")
        self.last_caller_creations = caller_creations
        self.last_overrides = overrides
        return self._hooks_overrides_result


def _make_meld(*, creations: Any | None = None, spellbook: _SpellbookStub | None = None) -> Meld:
    """
    Build a Meld instance with stubbed spellbook/creations.

    Args:
        creations: Optional creations container override.
        spellbook: Optional spellbook stub override.

    Returns:
        Meld: Meld instance ready for testing.
    """
    effective_creations = creations or MagicMock()
    conduit_id = getattr(effective_creations, "owner_conduit_id", "conduit-1")
    meld = Meld(
        creations=effective_creations,
        spellbook=spellbook or _SpellbookStub(),
        conduit_id=conduit_id,
        resolution_conduit_id=conduit_id,
    )
    meld._spell_compiler_system = SimpleNamespace(
        run_structural_phases=lambda spellbook, spell, cancel_event=None: spell.run_structural_phases(),
        is_current_spell_phase5_root=lambda spell: bool(
            getattr(spell._compiler_artifact, "_root_blueprint_phase5", None)
            and spell._compiler_artifact._root_blueprint_phase5.root_spell_id == spell.spell_index.current
        ),
        cleanup=lambda: None,
    )
    return meld


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
    return Creations(
        conduit_id=conduit._id,
        spellspace_stack=ContextVar(
            "spellspace_stack_{0}".format(conduit._id),
            default=[],
        ),
    ), conduit


def test_cleanup_clears_references() -> None:
    """
    Verify Meld.cleanup releases owned references.

    Contract:
        - Spellbook maps and creations references are cleared.
        - Meld hooks are cleared and removed.
    """
    meld = _make_meld()
    hook_list: list[Callable[..., Any]] = [lambda: None]
    meld._meld_hooks = {"on_meld_pre_resolve": hook_list}

    meld.cleanup()

    assert hook_list == [hook_list[0]]
    assert not hasattr(meld, '_owned_spells')
    assert not hasattr(meld, '_contracted_spells')
    assert not hasattr(meld, '_lookup_owned_spells')
    assert not hasattr(meld, '_lookup_contracted_spells')
    assert not hasattr(meld, '_creations')
    assert not hasattr(meld, '_meld_hooks')


def test_meld_no_hooks_uses_cached_context_no_overrides_door() -> None:
    """
    Verify no-hooks/no-overrides calls execute cached context fast door.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=context)
    spell._hooks_enabled = False
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "instance"
    assert context.calls == ["no_hooks_no_overrides"]
    assert context.last_caller_creations is creations
    assert context.last_overrides is None


def test_meld_no_hooks_uses_cached_context_overrides_door() -> None:
    """
    Verify no-hooks override calls use override door with normalized payload.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    context = _CreationContextStub(no_hooks_overrides_result="instance-with-overrides")
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=context)
    spell._hooks_enabled = False
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1", spell_override=[1, 2]) == "instance-with-overrides"
    assert context.calls == ["no_hooks_overrides"]
    assert context.last_overrides == {"__args__": [1, 2]}


def test_meld_no_hooks_empty_dict_override_uses_no_overrides_door() -> None:
    """
    Verify empty dict override payloads route through the no-overrides door.

    Contract:
        - Empty dict payload normalizes to `None`.
        - No-overrides compiled door executes.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=context)
    spell._hooks_enabled = False
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1", spell_override={}) == "instance"
    assert context.calls == ["no_hooks_no_overrides"]
    assert context.last_overrides is None


def test_meld_non_string_cache_hit_reuses_input_resolution_entry() -> None:
    """
    Verify non-string meld calls reuse the input-resolution cache entry.

    Contract:
        - First call resolves via `_resolve_spell`.
        - Second call with the same non-string identity key reuses cache.
        - `_resolve_spell` is called exactly once.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    meld._spellbook._spellbook_validation_required = False

    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    target_spell = _SpellStub(
        spell_id="spell-cache-hit",
        owner_creations=creations,
        creation_context=context,
    )
    target_spell._hooks_enabled = False

    spell_token = object()
    meld._resolve_spell = MagicMock(return_value=target_spell)

    first = meld.meld(spell=spell_token, spellframe="frame", binding_name="primary")
    second = meld.meld(spell=spell_token, spellframe="frame", binding_name="primary")

    assert first == "instance"
    assert second == "instance"
    meld._resolve_spell.assert_called_once_with(
        spell=spell_token,
        spell_name=None,
        spellframe="frame",
        binding_name="primary",
    )
    assert context.calls == ["no_hooks_no_overrides", "no_hooks_no_overrides"]


def test_meld_non_string_unhashable_input_uses_identity_fallback_cache_key() -> None:
    """
    Verify unhashable non-string inputs use the id-based fallback cache key.

    Contract:
        - Unhashable inputs do not raise during cache lookup.
        - Cache stores and reuses the id-based fallback key.
        - `_resolve_spell` is called once across two identical calls.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    meld._spellbook._spellbook_validation_required = False

    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    target_spell = _SpellStub(
        spell_id="spell-unhashable",
        owner_creations=creations,
        creation_context=context,
    )
    target_spell._hooks_enabled = False

    class _Unhashable:
        """
        Minimal unhashable object for cache-key fallback tests.
        """

        __hash__ = None

    unhashable_spell = _Unhashable()
    meld._resolve_spell = MagicMock(return_value=target_spell)

    first = meld.meld(spell=unhashable_spell)
    fallback_key = (None, id(unhashable_spell), id(None), None)
    assert first == "instance"
    assert fallback_key in meld._input_resolution_cache

    second = meld.meld(spell=unhashable_spell)
    assert second == "instance"
    meld._resolve_spell.assert_called_once_with(
        spell=unhashable_spell,
        spell_name=None,
        spellframe=None,
        binding_name=None,
    )
    assert context.calls == ["no_hooks_no_overrides", "no_hooks_no_overrides"]


def test_meld_hooks_lane_runs_activation_on_created_instance() -> None:
    """
    Verify hooks lane executes activation hooks only when context reports created.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    events: list[str] = []

    def pre_hook() -> None:
        events.append("pre")

    def post_hook() -> None:
        events.append("post")

    def activation_hook(instance: Any) -> None:
        events.append("activation:{0}".format(instance))

    context = _CreationContextStub(hooks_overrides_result=("created", True))
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=context)
    spell._hooks_enabled = True
    spell._pre_hooks = [pre_hook]
    spell._post_hooks = [post_hook]
    spell._activation_hooks = [activation_hook]
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1", spell_override={"x": 1}) == "created"
    assert context.calls == ["hooks_overrides"]
    assert events == ["pre", "activation:created", "post"]


def test_meld_hooks_lane_skips_activation_for_reused_instance() -> None:
    """
    Verify hooks lane skips activation hooks when context reports created=False.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    events: list[str] = []

    def pre_hook() -> None:
        events.append("pre")

    def post_hook() -> None:
        events.append("post")

    def activation_hook(instance: Any) -> None:
        events.append("activation:{0}".format(instance))

    context = _CreationContextStub(hooks_no_overrides_result=("reuse", False))
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=context)
    spell._hooks_enabled = True
    spell._pre_hooks = [pre_hook]
    spell._post_hooks = [post_hook]
    spell._activation_hooks = [activation_hook]
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "reuse"
    assert context.calls == ["hooks_no_overrides"]
    assert events == ["pre", "post"]


def test_meld_builds_context_on_cache_miss() -> None:
    """
    Verify meld calls CreationContextFactory when spell cache has no context.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    built_context = _CreationContextStub(no_hooks_no_overrides_result="built")
    factory = MagicMock()
    factory.get_or_build_for_spell.return_value = built_context
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=None)
    spell._creation_context_factory = factory
    spell._hooks_enabled = False
    spell._compiler_artifact._root_blueprint_phase5 = None
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "built"
    factory.get_or_build_for_spell.assert_called_once_with(spell)
    assert built_context.calls == ["no_hooks_no_overrides"]


def test_meld_rebuilds_context_when_switch_is_not_open() -> None:
    """
    Verify meld rebuilds spell context when CounterSwitch is not open.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    stale_context = _CreationContextStub(cleaned=True)
    fresh_context = _CreationContextStub(no_hooks_no_overrides_result="fresh")
    factory = MagicMock()
    factory.get_or_build_for_spell.return_value = fresh_context
    spell = _SpellStub(
        spell_id="spell-1",
        owner_creations=creations,
        creation_context=stale_context,
    )
    spell._creation_context_factory = factory
    spell._hooks_enabled = False
    spell._compiler_artifact._root_blueprint_phase5 = None
    spell._creation_context_switch.state = 0
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "fresh"
    factory.get_or_build_for_spell.assert_called_once_with(spell)
    assert fresh_context.calls == ["no_hooks_no_overrides"]


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


def test_normalize_spell_override_empty_dict_returns_none() -> None:
    """
    Verify empty dict payloads normalize to no-overrides (`None`).
    """
    meld = _make_meld()
    assert meld._normalize_spell_override({}) is None


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
    Verify local resolution fails naturally when owned spell map is unavailable.

    Contract:
        - If lookup hits but owned map is None, direct map access raises AttributeError.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={},
        lookup_spells={lookup_key: spell_index},
    )
    meld = _make_meld(spellbook=spellbook)
    meld._owned_spells = None
    with pytest.raises(AttributeError, match="has no attribute 'get'"):
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

def test_resolve_contracted_by_lookup_key_raises_when_conduit_missing() -> None:
    """
    Verify contracted resolution skips missing conduit spell maps.

    Contract:
        - Lookup hit with missing conduit map returns None.
    """
    lookup_key = ("frame", "binding")
    spell_index = object()
    spellbook = _SpellbookStub(
        contracted_spells={},
        lookup_contracted_spells={"peer": {lookup_key: spell_index}},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_contracted_by_lookup_key(lookup_key) is None


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


def test_set_meld_hooks_local_merge_adds_to_existing_hooks() -> None:
    """
    Verify local hook mode merges into the current effective map by default.

    Contract:
        - Existing hooks are preserved in local mode.
        - Incoming hooks append after existing hooks for the same name.
        - Local map is detached from the original shared map.
    """
    meld = _make_meld()
    shared_calls: list[str] = []
    local_calls: list[str] = []

    def shared_hook() -> None:
        shared_calls.append("shared")

    def local_hook() -> None:
        local_calls.append("local")

    shared_map = {"on_meld_pre_resolve": [shared_hook]}
    meld.set_meld_hooks(shared_map)
    meld.set_meld_hooks(
        {"on_meld_pre_resolve": [local_hook]},
        create_local_hooks=True,
    )

    assert meld._meld_hooks is not shared_map
    assert meld._meld_hooks["on_meld_pre_resolve"] == [shared_hook, local_hook]
    assert shared_map["on_meld_pre_resolve"] == [shared_hook]


def test_set_meld_hooks_local_overwrite_replaces_existing_hooks() -> None:
    """
    Verify local hook overwrite mode replaces the current effective map.

    Contract:
        - overwrite=True drops previously installed hooks.
        - Incoming hooks become the complete local map.
        - Local map is detached from the original shared map.
    """
    meld = _make_meld()

    def shared_hook() -> None:
        return None

    def local_hook() -> None:
        return None

    shared_map = {"on_meld_pre_resolve": [shared_hook]}
    meld.set_meld_hooks(shared_map)
    meld.set_meld_hooks(
        {"on_meld_post_resolve": [local_hook]},
        create_local_hooks=True,
        overwrite=True,
    )

    assert meld._meld_hooks is not shared_map
    assert "on_meld_pre_resolve" not in meld._meld_hooks
    assert meld._meld_hooks["on_meld_post_resolve"] == [local_hook]
    assert shared_map["on_meld_pre_resolve"] == [shared_hook]


def test_ensure_lineage_resolvable_skips_without_state() -> None:
    """
    Verify lineage gating fails validation when no structural state exists.

    Contract:
        - Missing system_state still triggers one structural rerun attempt.
        - The spell remains unrunnable and raises SpellbookValidationError.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1", system_state=None)

    with pytest.raises(SpellbookValidationError):
        meld._ensure_lineage_resolvable(spell)

    assert spell.run_structural_phases_calls == 1


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


def test_ensure_lineage_resolvable_missing_contract_raises() -> None:
    """
    Verify missing SpellContract providers raise MeldExecutionError.

    Contract:
        - SpellContract defaults without contracted providers raise.
    """
    spellbook = _SpellbookStub()
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=SpellValidity.valid)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        spellbook=spellbook,
    )

    class ContractConsumer:
        """
        Minimal consumer with a SpellContract dependency.
        """

        def __init__(self, service: Any = SpellContract(spellframe="svc", binding_name="primary")) -> None:
            self.service = service

    spell.spell = ContractConsumer

    with pytest.raises(MeldExecutionError, match="SpellContract could not be resolved"):
        meld._ensure_lineage_resolvable(spell)


def test_ensure_lineage_resolvable_wraps_contracted_lookup_failures() -> None:
    """
    Verify contract lookup failures are wrapped with spell/parameter context.

    Contract:
        - Unexpected contracted lookup failures raise MeldExecutionError.
        - Error payload includes the failing parameter name.
    """
    spellbook = _SpellbookStub()
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=SpellValidity.valid)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        spellbook=spellbook,
    )

    class ContractConsumer:
        def __init__(self, service: Any = SpellContract(spellframe="svc", binding_name="primary")) -> None:
            self.service = service

    spell.spell = ContractConsumer
    meld._resolve_contracted_by_lookup_key = MagicMock(side_effect=RuntimeError("lookup failed"))

    with pytest.raises(MeldExecutionError, match="param 'service'"):
        meld._ensure_lineage_resolvable(spell)


def test_ensure_lineage_resolvable_contract_forces_revalidation() -> None:
    """
    Verify resolved SpellContracts force resolution revalidation.

    Contract:
        - Contract presence gates resolution and triggers conduit revalidation.
    """
    contract = SpellContract(spellframe="svc", binding_name="primary")
    contract_key = contract.canonical_key
    provider = _SpellStub(spell_id="provider-1")
    spellbook = _SpellbookStub(
        contracted_spells={"peer-1": {provider.spell_index: provider}},
        lookup_contracted_spells={"peer-1": {contract_key: provider.spell_index}},
    )

    resolution_state = _ResolutionStateStub()
    spell_system_states = _SpellSystemStatesStub(resolution_state)
    state = _SystemStateStub(validity=SpellValidity.valid)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        spell_system_states=spell_system_states,
        spellbook=spellbook,
    )

    class ContractConsumer:
        """
        Consumer that requires a contracted provider.
        """

        def __init__(self, service: Any = contract) -> None:
            self.service = service

    spell.spell = ContractConsumer

    creations, _ = _make_creations(conduit_id="conduit-1")
    meld = _make_meld(creations=creations, spellbook=spellbook)

    def _run_resolution(conduit_id: str, target_spell: _SpellStub) -> None:
        assert target_spell is spell
        resolution_state.set_spell_validity(spell.spell_index.current, SpellValidity.valid)

    spellbook._run_resolution_phases_for_target_spell = MagicMock(side_effect=_run_resolution)

    meld._ensure_lineage_resolvable(spell)

    spellbook._run_resolution_phases_for_target_spell.assert_called_once_with("conduit-1", spell)
    assert any(call[1] is SpellValidity.gated for call in resolution_state.spell_set_calls)


def test_force_resolution_revalidation_uses_root_validity_for_root_blueprints() -> None:
    """
    Verify root spells gate root validity rather than spell validity.

    Contract:
        - Root blueprints drive `set_root_validity`.
        - `set_spell_validity` is not used for root spells.
    """
    resolution_state = _ResolutionStateStub()
    spell_system_states = _SpellSystemStatesStub(resolution_state)
    spell = _SpellStub(
        spell_id="spell-root",
        spell_system_states=spell_system_states,
    )
    spell._compiler_artifact._root_blueprint_phase5 = SimpleNamespace(
        root_spell_id=spell.spell_index.current
    )
    meld = _make_meld()
    meld._resolution_conduit_id = "conduit-1"

    meld._force_resolution_revalidation(spell)

    assert resolution_state.root_set_calls == [
        (
            spell.spell_index.current,
            SpellValidity.gated,
            SpellStateChangeReason.contract_unvalidated,
        )
    ]
    assert resolution_state.spell_set_calls == []


def test_get_resolution_validity_uses_root_validity_for_root_blueprints() -> None:
    """
    Verify root validity reads use the root-validity slot.

    Contract:
        - Root spells read `get_root_validity`.
        - Non-root spell validity is not consulted for root blueprints.
    """
    resolution_state = _ResolutionStateStub()
    resolution_state.set_root_validity(
        "spell-root",
        SpellValidity.gated,
        change_reason=SpellStateChangeReason.contract_unvalidated,
    )
    spell = _SpellStub(spell_id="spell-root")
    spell._compiler_artifact._root_blueprint_phase5 = SimpleNamespace(
        root_spell_id=spell.spell_index.current
    )
    meld = _make_meld()

    assert meld._get_resolution_validity(spell, resolution_state) is SpellValidity.gated


def test_iter_spell_contract_defaults_skips_non_contract_and_special_params() -> None:
    """
    Verify SpellContract default scanning skips self/cls/varargs and plain defaults.
    """
    contract = SpellContract(spellframe="svc", binding_name="primary")

    class ContractConsumer:
        def __init__(
                self,
                service: Any = contract,
                plain: int = 1,
                *args: Any,
                **kwargs: Any,
        ) -> None:
            self.service = service
            self.plain = plain

    spell = _SpellStub(spell_id="spell-1")
    spell.spell = ContractConsumer
    meld = _make_meld()

    assert meld._iter_spell_contract_defaults(spell) == [("service", contract)]


def test_iter_spell_contract_defaults_returns_empty_when_signature_unavailable() -> None:
    """
    Verify SpellContract default scanning returns empty when inspect.signature fails.
    """
    spell = _SpellStub(spell_id="spell-1")
    spell.spell = object()
    meld = _make_meld()

    assert meld._iter_spell_contract_defaults(spell) == []


def test_gated_validation_required_returns_false_without_state() -> None:
    """
    Verify gated validation requires structural rerun without system state.

    Contract:
        - Missing system_state returns True so structural validation runs.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1", system_state=None)
    assert meld._gated_validation_required(spell) is True


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


@pytest.mark.parametrize(
    "validity",
    [SpellValidity.invalid, SpellValidity.disabled, SpellValidity.cleaned],
)
def test_gated_validation_required_raises_for_invalid_or_disabled_or_cleaned(
    validity: SpellValidity,
) -> None:
    """
    Verify invalid/disabled/cleaned lineages are blocked.

    Contract:
        - invalid/disabled/cleaned validity raises SpellbookValidationError.
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


def test_gated_validation_required_reuses_cached_change_control_manager() -> None:
    """
    Verify change-control manager lookup is cached per frame.

    Contract:
        - First validation call resolves the frame manager once.
        - Subsequent calls reuse the cached manager.
    """
    ccm = _ChangeControlManagerStub(dirty_roots=set())
    aether = _AetherStub(ccm)
    spellbook = _SpellbookStub(aetheric_frame="default", aether=aether)
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=SpellValidity.valid)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        spellbook=spellbook,
    )

    assert aether.get_change_control_manager_calls == 0
    assert meld._gated_validation_required(spell) is False
    assert meld._gated_validation_required(spell) is False
    assert meld._gated_validation_required(spell) is False
    assert aether.get_change_control_manager_calls == 1


def test_gated_validation_required_ignores_change_control_errors() -> None:
    """
    Verify change-control failures fall back to the existing validity gate.

    Contract:
        - Non-MeldExecutionError failures from change-control are ignored.
        - Valid lineages still return False.
    """

    class _FailingChangeControlManager:
        def is_root_dirty(self, conduit_id: str, root_id: str) -> bool:
            raise RuntimeError("ccm unavailable")

    aether = _AetherStub(_FailingChangeControlManager())
    spellbook = _SpellbookStub(aetheric_frame="default", aether=aether)
    meld = _make_meld(spellbook=spellbook)
    state = _SystemStateStub(validity=SpellValidity.valid)
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=state,
        spellbook=spellbook,
    )

    assert meld._gated_validation_required(spell) is False


def test_meld_reuses_cached_context_without_factory_rebuild() -> None:
    """
    Verify cached clean context is reused without calling factory rebuild.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    context = _CreationContextStub(no_hooks_no_overrides_result="reuse")
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations, creation_context=context)
    spell._hooks_enabled = False
    factory = MagicMock()
    spell._creation_context_factory = factory
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "reuse"
    factory.get_or_build_for_spell.assert_not_called()
    assert context.calls == ["no_hooks_no_overrides"]


def test_meld_level_hooks_receive_expected_arguments() -> None:
    """
    Verify meld-level hooks receive spell and activation payload arguments.

    Contract:
        - on_meld_pre_resolve receives `(spell)`.
        - on_meld_activation receives `(spell, instance)` when created.
        - on_meld_post_resolve receives `(spell)`.
    """
    creations, _ = _make_creations()
    meld = _make_meld(creations=creations)
    spell = _SpellStub(spell_id="spell-1", owner_creations=creations)
    spell._hooks_enabled = True
    spell._creation_context = _CreationContextStub(
        hooks_no_overrides_result=("instance", True),
    )
    seen: list[tuple[Any, ...]] = []

    def on_pre_resolve(received_spell: Any) -> None:
        seen.append(("pre", received_spell))

    def on_activation(received_spell: Any, instance: Any) -> None:
        seen.append(("activation", received_spell, instance))

    def on_post_resolve(received_spell: Any) -> None:
        seen.append(("post", received_spell))

    meld.set_meld_hooks(
        {
            "on_meld_pre_resolve": [on_pre_resolve],
            "on_meld_activation": [on_activation],
            "on_meld_post_resolve": [on_post_resolve],
        }
    )
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "instance"
    assert seen == [
        ("pre", spell),
        ("activation", spell, "instance"),
        ("post", spell),
    ]


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


def test_ensure_lineage_resolvable_raises_for_cleaned_state() -> None:
    """
    Verify cleaned lineage validity raises SpellbookValidationError.

    Contract:
        - Cleaned validity raises without attempting revalidation.
    """
    meld = _make_meld()
    state = _SystemStateStub(validity=SpellValidity.cleaned)
    spell = _SpellStub(spell_id="spell-1", system_state=state)
    with pytest.raises(SpellbookValidationError):
        meld._ensure_lineage_resolvable(spell)


@pytest.mark.parametrize(
    "validity",
    [SpellValidity.invalid, SpellValidity.disabled, SpellValidity.cleaned],
)
def test_ensure_resolution_resolvable_blocks_invalid_disabled_cleaned(
    validity: SpellValidity,
) -> None:
    """
    Verify resolution validity blocks invalid/disabled/cleaned spells.

    Contract:
        - Resolution validity in {invalid, disabled, cleaned} raises.
    """
    resolution_state = _ResolutionStateStub()
    spell_system_states = _SpellSystemStatesStub(resolution_state)
    spell = _SpellStub(
        spell_id="spell-1",
        spell_system_states=spell_system_states,
    )
    resolution_state.set_spell_validity(spell.spell_index.current, validity)
    meld = _make_meld()
    meld._creations = None
    meld._resolution_conduit_id = "conduit-1"

    with pytest.raises(SpellbookValidationError):
        meld._ensure_resolution_resolvable(spell)


def test_ensure_runtime_resolution_ready_skips_when_not_required() -> None:
    """
    Verify deferred runtime-resolution gate is a no-op when not required.

    Contract:
        - `resolution_required=False` performs no deferred phase call.
        - Existing completion state remains unchanged.
    """
    spellbook = _SpellbookStub()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=False,
        resolution_complete=False,
    )

    meld._ensure_runtime_resolution_ready(spell)

    spellbook._run_deferred_resolution_phases_for_target_spell.assert_not_called()
    assert spell.resolution_required is False
    assert spell.resolution_complete is False


def test_ensure_runtime_resolution_ready_marks_not_required_when_complete() -> None:
    """
    Verify already-complete deferred resolution clears required flag without rerun.

    Contract:
        - `resolution_required=True` and `resolution_complete=True` does not call
          deferred phases.
        - Runtime gate normalizes state to `required=False`.
    """
    spellbook = _SpellbookStub()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=True,
    )

    meld._ensure_runtime_resolution_ready(spell)

    spellbook._run_deferred_resolution_phases_for_target_spell.assert_not_called()
    assert spell.resolution_required is False
    assert spell.resolution_complete is True


def test_ensure_runtime_resolution_ready_runs_deferred_and_marks_complete() -> None:
    """
    Verify runtime gate executes deferred phases and marks resolution complete.

    Contract:
        - Deferred phase hook runs once for the active resolution conduit id.
        - Success flips flags to `resolution_complete=True` and
          `resolution_required=False`.
    """
    spellbook = _SpellbookStub()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )

    meld._ensure_runtime_resolution_ready(spell)

    expected_conduit_id = meld._resolution_conduit_id
    spellbook._run_deferred_resolution_phases_for_target_spell.assert_called_once_with(
        expected_conduit_id,
        spell,
    )
    assert spell.resolution_complete is True
    assert spell.resolution_required is False


def test_ensure_runtime_resolution_ready_failure_reflags_and_reraises() -> None:
    """
    Verify deferred-resolution failures keep runtime gate required and incomplete.

    Contract:
        - Deferred phase exceptions propagate to caller.
        - Failure preserves `resolution_required=True` and
          `resolution_complete=False`.
    """
    spellbook = _SpellbookStub()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock(
        side_effect=RuntimeError("deferred resolution failed"),
    )
    meld = _make_meld(spellbook=spellbook)
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )

    with pytest.raises(RuntimeError, match="deferred resolution failed"):
        meld._ensure_runtime_resolution_ready(spell)

    expected_conduit_id = meld._resolution_conduit_id
    spellbook._run_deferred_resolution_phases_for_target_spell.assert_called_once_with(
        expected_conduit_id,
        spell,
    )
    assert spell.resolution_complete is False
    assert spell.resolution_required is True


def test_ensure_runtime_resolution_ready_requires_conduit_id() -> None:
    """
    Verify runtime gate hard-fails when no resolution conduit id is available.

    Contract:
        - Missing conduit id raises RuntimeError before deferred phases run.
        - Gate flags are left unchanged on this setup error.
    """
    spellbook = _SpellbookStub()
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock()
    meld = _make_meld(spellbook=spellbook)
    meld._resolution_conduit_id = None
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )

    with pytest.raises(RuntimeError, match="resolution conduit id"):
        meld._ensure_runtime_resolution_ready(spell)

    spellbook._run_deferred_resolution_phases_for_target_spell.assert_not_called()
    assert spell.resolution_required is True
    assert spell.resolution_complete is False


def test_meld_runs_deferred_runtime_resolution_before_context_build() -> None:
    """
    Verify meld executes deferred runtime gate before creation-context build.

    Contract:
        - Deferred phase hook executes before context build/execution.
        - Successful deferred pass allows compiled door execution.
        - Runtime flags normalize to complete/not-required.
    """
    creations, _ = _make_creations()
    spellbook = _SpellbookStub()
    spellbook._spellbook_validation_required = False
    call_order: list[str] = []

    def _run_deferred_resolution(conduit_id: str, target_spell: _SpellStub) -> None:
        """
        Record deferred phase invocation for ordering assertions.
        """
        assert conduit_id == "conduit-1"
        assert target_spell.spell_id == "spell-1"
        call_order.append("deferred")

    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock(
        side_effect=_run_deferred_resolution,
    )
    context = _CreationContextStub(no_hooks_no_overrides_result="resolved")

    def _execute_no_hooks_no_overrides(caller_creations: Any) -> Any:
        """
        Record compiled execution invocation after deferred runtime gate.
        """
        assert caller_creations is creations
        call_order.append("context")
        return "resolved"

    context._execute_no_hooks_no_overrides_compiled = _execute_no_hooks_no_overrides
    spell = _SpellStub(
        spell_id="spell-1",
        owner_creations=creations,
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )
    spell._get_or_build_creation_context = MagicMock(return_value=context)

    meld = _make_meld(creations=creations, spellbook=spellbook)
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    assert meld.meld(spell="spell-1") == "resolved"
    spellbook._run_deferred_resolution_phases_for_target_spell.assert_called_once_with(
        "conduit-1",
        spell,
    )
    spell._get_or_build_creation_context.assert_called_once()
    assert call_order == ["deferred", "context"]
    assert spell.resolution_complete is True
    assert spell.resolution_required is False


def test_meld_skips_context_build_when_deferred_runtime_resolution_fails() -> None:
    """
    Verify meld does not build context when deferred runtime gate fails.

    Contract:
        - Deferred runtime phase errors propagate from `meld`.
        - Context-build path is not entered after deferred failure.
        - Runtime flags remain required/incomplete.
    """
    spellbook = _SpellbookStub()
    spellbook._spellbook_validation_required = False
    spellbook._run_deferred_resolution_phases_for_target_spell = MagicMock(
        side_effect=RuntimeError("deferred gate failure"),
    )
    spell = _SpellStub(
        spell_id="spell-1",
        spellbook=spellbook,
        resolution_required=True,
        resolution_complete=False,
    )
    spell._get_or_build_creation_context = MagicMock()

    meld = _make_meld(spellbook=spellbook)
    meld._resolve_spell_by_id = MagicMock(return_value=spell)

    with pytest.raises(RuntimeError, match="deferred gate failure"):
        meld.meld(spell="spell-1")

    expected_conduit_id = meld._resolution_conduit_id
    spellbook._run_deferred_resolution_phases_for_target_spell.assert_called_once_with(
        expected_conduit_id,
        spell,
    )
    spell._get_or_build_creation_context.assert_not_called()
    assert spell.resolution_complete is False
    assert spell.resolution_required is True


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


def test_cleanup_does_not_depend_on_creation_context_factory() -> None:
    """
    Verify Meld.cleanup does not manage spell-owned creation-context factories.

    Contract:
        - Cleanup completes without a Meld-owned factory.
    """
    meld = _make_meld()

    meld.cleanup()

    assert meld._cleaned is True


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


def test_has_live_creation_returns_true_for_unique_per_conduit_creation() -> None:
    """
    Verify the probe returns True for an existing unique-per-conduit creation.

    Contract:
        - Reuses spell-id resolution.
        - Does not attempt creation-context build.
    """
    creations, _ = _make_creations()
    live_instance = object()
    creations.add_creation("spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    spell._get_or_build_creation_context = MagicMock()
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is True
    spell._get_or_build_creation_context.assert_not_called()


def test_meld_existing_spell_returns_live_unique_per_conduit_creation() -> None:
    """
    Verify `meld_existing_spell` returns the live unique-per-conduit object.

    Contract:
        - Reuses current live storage only.
        - Does not attempt creation-context build.
    """
    creations, _ = _make_creations()
    live_instance = object()
    creations.add_creation("spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    spell._get_or_build_creation_context = MagicMock()
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.meld_existing_spell(spell="spell-1") is live_instance
    spell._get_or_build_creation_context.assert_not_called()


def test_meld_existing_spell_raises_when_unique_per_conduit_not_live() -> None:
    """
    Verify `meld_existing_spell` fails when no live unique-per-conduit object exists.
    """
    creations, _ = _make_creations()
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    with pytest.raises(ValueError, match="Spell 'spell-1' is not live"):
        meld.meld_existing_spell(spell="spell-1")


def test_meld_existing_spell_uses_active_spellspace_bucket() -> None:
    """
    Verify `meld_existing_spell` supports unique-per-spell-space with an active scope.
    """
    conduit = _ConduitStub(
        conduit_id="conduit-1",
        conduit_state=ConduitState.normal,
    )
    spellspace = _SpellSpaceStub(
        spellspace_id="space-1",
        owner_conduit_id=conduit._id,
    )
    conduit._active_spellspace = spellspace
    creations = Creations(
        conduit_id=conduit._id,
        spellspace_stack=ContextVar(
            "spellspace_stack_{0}".format(conduit._id),
            default=[spellspace],
        ),
    )
    live_instance = object()
    creations.register_spellspace_creation("space-1", "spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.meld_existing_spell(spell="spell-1") is live_instance


def test_meld_existing_spell_rejects_many_lifecycle() -> None:
    """
    Verify `meld_existing_spell` fails fast for the ambiguous `many` lifecycle.
    """
    creations, _ = _make_creations()
    creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    with pytest.raises(
        RuntimeError,
        match="meld_existing_spell is not supported for Existence.many",
    ):
        meld.meld_existing_spell(spell="spell-1")


def test_has_live_creation_returns_false_when_unique_per_conduit_missing() -> None:
    """
    Verify the probe returns False when no unique-per-conduit creation exists.
    """
    creations, _ = _make_creations()
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is False


def test_has_live_creation_returns_true_when_many_bucket_is_non_empty() -> None:
    """
    Verify the probe treats any live `many` entries as available.
    """
    creations, _ = _make_creations()
    creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is True


def test_has_live_creation_uses_active_spellspace_bucket() -> None:
    """
    Verify the probe checks the active spellspace bucket for spellspace scope.
    """
    conduit = _ConduitStub(
        conduit_id="conduit-1",
        conduit_state=ConduitState.normal,
    )
    spellspace = _SpellSpaceStub(
        spellspace_id="space-1",
        owner_conduit_id=conduit._id,
    )
    conduit._active_spellspace = spellspace
    creations = Creations(
        conduit_id=conduit._id,
        spellspace_stack=ContextVar(
            "spellspace_stack_probe_{0}".format(conduit._id),
            default=[spellspace],
        ),
    )
    creations.register_spellspace_creation("space-1", "spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is True


def test_has_live_creation_returns_false_for_spellspace_without_active_scope() -> None:
    """
    Verify the probe returns False for spellspace scope when no scope is active.
    """
    creations, _ = _make_creations(active_spellspace=None)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is False


def test_has_live_creation_uses_owner_creations_for_shared_routes() -> None:
    """
    Verify shared existence routes inspect the owner creations container.
    """
    caller_creations, _ = _make_creations(conduit_id="caller")
    owner_creations, _ = _make_creations(conduit_id="owner")
    owner_creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=caller_creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is True


def test_has_live_creation_returns_existing_creation_state() -> None:
    """
    Verify existing-creation spells report live state from the user object.
    """
    creations, _ = _make_creations()
    live_object = object()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=live_object,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.has_live_creation(spell="spell-1") is True


def test_describe_live_creation_status_reports_query_conduit_scope() -> None:
    """
    Verify the richer status payload reports the caller-conduit scope.
    """
    creations, _ = _make_creations(conduit_id="conduit-1")
    creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique_per_conduit",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "caller_conduit",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": None,
        "creation_count": 1,
    }


def test_describe_live_creation_status_reports_owner_scope_for_shared_routes() -> None:
    """
    Verify the richer status payload reports owner-scope storage for shared routes.
    """
    caller_creations, _ = _make_creations(conduit_id="caller")
    owner_creations, _ = _make_creations(conduit_id="owner")
    owner_creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
        owner_conduit_id="owner",
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=caller_creations, spellbook=spellbook)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique",
        "query_conduit_id": "caller",
        "storage_scope_kind": "owner_creations",
        "storage_owner_conduit_id": "owner",
        "active_spellspace_id": None,
        "creation_count": 1,
    }


def test_describe_live_creation_status_reports_spellspace_gap_without_scope() -> None:
    """
    Verify the richer status payload reports missing active spellspace cleanly.
    """
    creations, _ = _make_creations(active_spellspace=None)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    spellbook = _SpellbookStub(spells={spell.spell_index: spell})
    meld = _make_meld(creations=creations, spellbook=spellbook)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": False,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique_per_spell_space",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "active_spellspace",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": None,
        "creation_count": 0,
    }


