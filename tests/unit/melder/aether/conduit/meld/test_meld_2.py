"""Additional contract tests for Meld resolution and registration helpers."""
from threading import RLock
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.meld import Meld
from melder.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.helpers.general_helpers import SpellInputUtils

try:
    from melder.aether.conduit.creations.lesser_creations import LesserCreations
except Exception:
    LesserCreations = None


class _SpellIndexStub:
    """
    Minimal spell index stub for Meld helper coverage.
    """

    def __init__(self, current: str) -> None:
        """
        Initialize the stub with a current spell id.

        Args:
            current: Spell version id used by error messages.
        """
        self.current = current
        self.id = f"lineage-{current}"


class _SpellStub:
    """
    Minimal spell stub for Meld resolution and registration tests.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: str = "Spell",
        spellframe: str = "frame",
        existence: Existence = Existence.unique,
        owner_creations: Any | None = None,
        owner_conduit_id: str = "conduit-1",
        owner_conduit_name: str = "Conduit",
        aetheric_frame: str = "default",
        is_existing_creation: bool = False,
        user_created_object: Any | None = None,
        is_class_spell: bool = False,
        is_method_spell: bool = False,
        is_lambda_spell: bool = False,
        has_disposal_methods: bool = True,
        disposal_method_names: list[str] | None = None,
        has_mutation_override: bool = False,
    ) -> None:
        """
        Initialize the stub with the attributes Meld expects.

        Args:
            spell_id: Unique identifier for the spell.
            spell_name: Human-readable spell name.
            spellframe: Spellframe string identifier.
            existence: Existence policy for the spell.
            owner_creations: Optional owner creations container.
            owner_conduit_id: Owning conduit id for MeldContext metadata.
            owner_conduit_name: Owning conduit name for MeldContext metadata.
            aetheric_frame: Aetheric frame name for MeldContext metadata.
            is_existing_creation: True when the spell wraps a pre-created object.
            user_created_object: The pre-created instance if applicable.
            is_class_spell: True for class-based spells.
            is_method_spell: True for method-based spells.
            is_lambda_spell: True for lambda-based spells.
            has_disposal_methods: Whether the spell declares disposal methods.
            disposal_method_names: Optional list of disposal method names.
            has_mutation_override: Whether mutation overrides are present.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.existence = existence
        self.spell_index = _SpellIndexStub(current=spell_id)
        self._owner_creations = owner_creations
        self._owner_conduit_id = owner_conduit_id
        self._owner_conduit_name = owner_conduit_name
        self.aetheric_frame = aetheric_frame
        self.is_existing_creation = is_existing_creation
        self.user_created_object = user_created_object
        self.is_class_spell = is_class_spell
        self.is_method_spell = is_method_spell
        self.is_lambda_spell = is_lambda_spell
        self.has_mutation_override = bool(has_mutation_override)
        self.has_disposal_methods = bool(has_disposal_methods)
        if disposal_method_names is None:
            self.disposal_method_names = ["cleanup"] if self.has_disposal_methods else []
        else:
            self.disposal_method_names = list(disposal_method_names)
        self._pre_hooks: list[Callable[..., Any]] = []
        self._activation_hooks: list[Callable[..., Any]] = []
        self._post_hooks: list[Callable[..., Any]] = []
        self._hooks_enabled: bool = False
        self.spell_type = "stub"
        self._lock = RLock()
        self._cleaned = False

    def check_cleaned(self) -> None:
        """
        Verify the stub spell has not been cleaned.

        Raises:
            RuntimeError: When the stub is flagged as cleaned.
        """
        if self._cleaned:
            raise RuntimeError("Spell has been cleaned.")


class _SpellbookStub:
    """
    Minimal spellbook stub exposing lookup maps for Meld.
    """

    def __init__(
        self,
        *,
        spells: dict[Any, _SpellStub] | None = None,
        contracted_spells: dict[str, dict[Any, _SpellStub]] | None = None,
        lookup_spells: dict[tuple[str, str], Any] | None = None,
        lookup_contracted_spells: dict[str, dict[tuple[str, str], Any]] | None = None,
    ) -> None:
        """
        Initialize the stubbed spellbook lookups.

        Args:
            spells: Local spell map keyed by spell index.
            contracted_spells: Contracted spell maps keyed by conduit id.
            lookup_spells: Local lookup map keyed by (frame, binding).
            lookup_contracted_spells: Contracted lookup maps per conduit.
        """
        self._spells = spells or {}
        self._contracted_spells = contracted_spells or {}
        self._lookup_spells = lookup_spells or {}
        self._lookup_contracted_spells = lookup_contracted_spells or {}
        self._spells_by_id = {}
        self._contracted_spells_by_id = {}
        self._spellbook_validation_required = True
        self._spell_id_pool: 'Dict[str, SpellIndex]' = {}


class _ConduitStub:
    """
    Minimal conduit stub for Creations and LesserCreations.
    """

    def __init__(self, conduit_id: str, conduit_state: ConduitState) -> None:
        """
        Initialize the stub conduit.

        Args:
            conduit_id: Conduit identifier.
            conduit_state: ConduitState for the creations manager.
        """
        self._id = conduit_id
        self._logger = MagicMock()
        self._conduit_state = conduit_state
        self._active_spellspace = None

    def get_active_spellspace(self) -> Any | None:
        """
        Return the active spellspace when configured.
        """
        return self._active_spellspace


def _make_meld(*, creations: Any | None = None, spellbook: _SpellbookStub | None = None) -> Meld:
    """
    Build a Meld instance with stubs.

    Args:
        creations: Optional creations container.
        spellbook: Optional spellbook stub.

    Returns:
        Meld: The constructed Meld instance.
    """
    effective_creations = creations or MagicMock()
    conduit = getattr(effective_creations, "_conduit", None)
    conduit_id = getattr(conduit, "_id", "conduit-1")
    return Meld(
        creations=effective_creations,
        spellbook=spellbook or _SpellbookStub(),
        conduit_id=conduit_id,
        resolution_conduit_id=conduit_id,
    )


def _make_creations() -> Creations:
    """
    Build a real Creations manager using a stub conduit.

    Returns:
        Creations: Initialized creations manager.
    """
    conduit = _ConduitStub("conduit-1", ConduitState.normal)
    return Creations(conduit)


def _make_lesser_creations(parent: Creations | None = None) -> Any:
    """
    Build a LesserCreations manager using a stub conduit.

    Args:
        parent: Optional parent Creations manager.

    Returns:
        LesserCreations: Initialized lesser creations manager.
    """
    if LesserCreations is None:
        pytest.skip("LesserCreations is removed in current codegen branch.")
    conduit = _ConduitStub("conduit-1", ConduitState.lesser)
    return LesserCreations(conduit, parent)


def test_resolve_spell_by_name_uses_name_key() -> None:
    """
    Verify spell_name-only resolution uses name-derived lookup keys.

    Contract:
        - spell_name-only resolution consults the lookup map built from name keys.
    """
    spell = _SpellStub(spell_id="spell-1", spell_name="MySpell")
    frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
        spellframe=None,
        spell_name="MySpell",
        binding_name=None,
    )
    lookup_key = (frame_key, bind_key)
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={spell_index: spell},
        lookup_spells={lookup_key: spell_index},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell(
        spell=None,
        spell_name="MySpell",
        spellframe=None,
        binding_name=None,
    ) is spell


def test_resolve_spell_with_spell_object_uses_normalized_key() -> None:
    """
    Verify spell-object resolution uses normalized spell keys.

    Contract:
        - normalize_spell_key determines lookup keys for spell objects.
    """
    class _SampleSpell:
        """
        Sample spell class for normalization tests.
        """

    spell = _SpellStub(spell_id="spell-1")
    frame_key, bind_key = SpellInputUtils.normalize_spell_key(
        spell=_SampleSpell,
        spellframe=None,
        binding_name="Primary",
    )
    lookup_key = (frame_key, bind_key)
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={spell_index: spell},
        lookup_spells={lookup_key: spell_index},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell(
        spell=_SampleSpell,
        spell_name=None,
        spellframe=None,
        binding_name="Primary",
    ) is spell


def test_resolve_spell_with_spellframe_uses_frame_key() -> None:
    """
    Verify spellframe-based resolution uses frame normalization.

    Contract:
        - spellframe normalization drives lookup key selection.
    """
    class _Frame:
        """
        Sample frame class for lookup normalization.
        """

    spell = _SpellStub(spell_id="spell-1")
    frame_key, bind_key = SpellInputUtils.normalize_spell_key(
        spell=None,
        spellframe=_Frame,
        binding_name="alpha",
    )
    lookup_key = (frame_key, bind_key)
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={spell_index: spell},
        lookup_spells={lookup_key: spell_index},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell(
        spell=None,
        spell_name=None,
        spellframe=_Frame,
        binding_name="alpha",
    ) is spell


def test_resolve_spell_lookup_missing_raises_keyerror() -> None:
    """
    Verify lookup resolution raises when the key is missing.

    Contract:
        - Missing lookup keys raise KeyError.
    """
    meld = _make_meld(spellbook=_SpellbookStub())
    with pytest.raises(KeyError, match="No spell found for frame"):
        meld._resolve_spell(
            spell=None,
            spell_name="Missing",
            spellframe=None,
            binding_name=None,
        )


def test_resolve_spell_by_lookup_key_finds_contracted_spell() -> None:
    """
    Verify lookup-key resolution finds contracted spells.

    Contract:
        - Contracted lookup maps are consulted after local lookup misses.
    """
    spell = _SpellStub(spell_id="spell-2")
    frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
        spellframe=None,
        spell_name="Contracted",
        binding_name=None,
    )
    lookup_key = (frame_key, bind_key)
    spell_index = object()
    spellbook = _SpellbookStub(
        spells={},
        lookup_spells={},
        contracted_spells={"peer": {spell_index: spell}},
        lookup_contracted_spells={"peer": {lookup_key: spell_index}},
    )
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell_by_lookup_key(lookup_key) is spell


def test_create_meld_context_wires_overrides_and_lock_flag() -> None:
    """
    Verify _create_meld_context wires overrides and lock flags.

    Contract:
        - overrides are stored on the context.
        - caller_creations_lock_held is passed through.
    """
    spell = _SpellStub(spell_id="spell-1")
    meld = _make_meld(creations=object())
    context = meld._create_meld_context(
        spell,
        overrides={"x": 1},
        caller_creations_lock_held=True,
    )
    try:
        assert context.root_spell is spell
        assert context.overrides == {"x": 1}
        assert context.caller_creations is meld._creations
        assert context.caller_creations_lock_held is True
    finally:
        context.cleanup()


def test_execute_hooks_runs_all_hooks() -> None:
    """
    Verify _execute_hooks runs every hook in order.

    Contract:
        - All hooks are invoked once.
    """
    calls: list[str] = []

    def first() -> None:
        """
        Record the first hook invocation.
        """
        calls.append("first")

    def second() -> None:
        """
        Record the second hook invocation.
        """
        calls.append("second")

    Meld._execute_hooks([first, second], "pre_cast")
    assert calls == ["first", "second"]


def test_execute_hooks_wraps_error() -> None:
    """
    Verify _execute_hooks wraps hook failures.

    Contract:
        - HookExecutionError is raised with the phase name.
    """
    def boom() -> None:
        """
        Raise a hook error for testing.
        """
        raise ValueError("boom")

    with pytest.raises(HookExecutionError, match="pre_cast"):
        Meld._execute_hooks([boom], "pre_cast")


def test_execute_activation_hooks_passes_instance() -> None:
    """
    Verify activation hooks receive the resolved instance.

    Contract:
        - activation hooks are called with the instance argument.
    """
    seen: list[Any] = []

    def hook(instance: Any) -> None:
        """
        Record the instance passed to the hook.
        """
        seen.append(instance)

    instance = object()
    Meld._execute_activation_hooks([hook], instance)
    assert seen == [instance]


def test_execute_activation_hooks_wraps_error() -> None:
    """
    Verify activation hook failures raise HookExecutionError.

    Contract:
        - activation failures are wrapped with phase information.
    """
    def boom(_: Any) -> None:
        """
        Raise an activation hook error.
        """
        raise RuntimeError("bad activation")

    with pytest.raises(HookExecutionError, match="activation"):
        Meld._execute_activation_hooks([boom], object())


def test_select_creations_per_conduit_prefers_caller() -> None:
    """
    Verify per-conduit existences prefer caller creations.

    Contract:
        - caller creations are selected for per-conduit lifetimes.
    """
    caller_creations = object()
    owner_creations = object()
    meld = _make_meld(creations=caller_creations)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell, spell.existence) is caller_creations


def test_select_creations_per_conduit_does_not_fall_back_to_owner() -> None:
    """
    Verify per-conduit selection does not fall back to owner creations.

    Contract:
        - caller routing is preserved even when caller creations are missing.
    """
    owner_creations = object()
    meld = _make_meld()
    meld._creations = None
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell, spell.existence) is None


def test_select_creations_shared_prefers_owner() -> None:
    """
    Verify shared existences prefer owner creations.

    Contract:
        - owner creations are selected for shared lifetimes.
    """
    caller_creations = object()
    owner_creations = object()
    meld = _make_meld(creations=caller_creations)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
    )
    assert meld._select_creations_for_spell(spell, spell.existence) is owner_creations


def test_select_creations_shared_does_not_fall_back_to_caller() -> None:
    """
    Verify shared selection does not fall back to caller creations.

    Contract:
        - owner routing is preserved even when owner creations are missing.
    """
    caller_creations = object()
    meld = _make_meld(creations=caller_creations)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=None,
    )
    assert meld._select_creations_for_spell(spell, spell.existence) is None


def test_raise_override_on_existing_instance_no_overrides() -> None:
    """
    Verify override checks are skipped when overrides are empty.

    Contract:
        - no exception is raised for empty overrides.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1")
    meld._raise_override_on_existing_instance(spell=spell, overrides=None)
    meld._raise_override_on_existing_instance(spell=spell, overrides={})


def test_raise_override_on_existing_instance_raises() -> None:
    """
    Verify override reuse rejects overrides for existing instances.

    Contract:
        - non-empty overrides raise MeldExecutionError.
    """
    meld = _make_meld()
    spell = _SpellStub(spell_id="spell-1")
    with pytest.raises(MeldExecutionError, match="already exists"):
        meld._raise_override_on_existing_instance(spell=spell, overrides={"x": 1})


def test_legacy_registration_helpers_removed_from_meld() -> None:
    """
    Verify legacy registration helpers are removed from Meld.

    Contract:
        - Registration now flows through runtime/creations paths, not private helper methods.
    """
    meld = _make_meld(creations=_make_creations())
    assert not hasattr(meld, "_register_to_creations")
    assert not hasattr(meld, "_register_spellspace_to_creations")
    assert not hasattr(meld, "_register_to_lesser_creations")
    assert not hasattr(meld, "_register_spellspace_to_lesser_creations")


def test_dispatch_meld_runtime_missing_crafter_raises() -> None:
    """
    Verify dispatch fails when spell runtime artifacts are missing.

    Contract:
        - Missing spell crafter raises RuntimeError during fast-route checks.
    """
    meld = _make_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        is_class_spell=True,
    )
    spell._crafter = None
    with pytest.raises(RuntimeError, match="Spell crafter is missing"):
        meld._dispatch_meld_runtime(
            spell,
            overrides=None,
        )


def test_register_spellspace_creation_registers_instance() -> None:
    """
    Verify spellspace registration stores the instance in the spellspace bucket.

    Contract:
        - Creations.register_spellspace_creation stores and returns the instance.
    """
    creations = _make_creations()
    conduit = creations._conduit
    spellspace = SimpleNamespace(id="space-1", owner_conduit=conduit)
    conduit._active_spellspace = spellspace
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique_per_spell_space)
    instance = object()

    creations.register_spellspace_creation(
        spellspace_id=spellspace.id,
        spell_id=spell.spell_id,
        item=instance,
    )

    stored = creations.get_spellspace_creation("space-1", spell.spell_id)
    assert stored is not None
    assert stored.value is instance


def test_add_many_creations_records_instance_without_disposal() -> None:
    """
    Verify many creations are recorded even when disposal methods are absent.

    Contract:
        - add_many_creations appends to list slots in the shared creations map.
    """
    creations = _make_creations()
    spell_id = "spell-1"
    creations.add_many_creations(
        key=spell_id,
        item=object(),
        has_disposal_methods=False,
        disposal_methods=[],
    )

    assert spell_id in creations._creations
    assert isinstance(creations._creations[spell_id], list)
    assert len(creations._creations[spell_id]) == 1


def test_get_existing_creation_from_creations_ignores_spellspace_slots() -> None:
    """
    Verify singleton lookup helper does not read spellspace-only entries.

    Contract:
        - _get_existing_creation_from_creations returns None when only spellspace data exists.
    """
    creations = _make_creations()
    conduit = creations._conduit
    spellspace = SimpleNamespace(id="space-1", owner_conduit=conduit)
    conduit._active_spellspace = spellspace
    spell = _SpellStub(spell_id="spell-1", existence=Existence.unique_per_spell_space)
    creations.register_spellspace_creation(
        spellspace_id=spellspace.id,
        spell_id=spell.spell_id,
        item=object(),
    )
    meld = _make_meld(creations=creations)
    assert (
        meld._get_existing_creation_from_creations(
            spell_id=spell.spell_id,
            creations=creations,
        )
        is None
    )


def test_get_active_spellspace_for_creations_owner_mismatch_allowed() -> None:
    """
    Verify active spellspace lookup does not reject owner mismatches.

    Contract:
        - Active spellspace lookup returns the configured spellspace.
    """
    creations = _make_creations()
    conduit = creations._conduit
    other_conduit = _ConduitStub("conduit-2", ConduitState.normal)
    conduit._active_spellspace = SimpleNamespace(id="space-1", owner_conduit=other_conduit)
    meld = _make_meld(creations=creations)
    assert meld._get_active_spellspace_for_creations(creations) is conduit._active_spellspace


def test_register_to_creations_helper_is_removed() -> None:
    """
    Verify legacy non-spellspace registration helper no longer exists.

    Contract:
        - Meld does not expose _register_to_creations.
    """
    meld = _make_meld(creations=_make_creations())
    assert not hasattr(meld, "_register_to_creations")


def test_lesser_creations_type_removed_in_codegen_branch() -> None:
    """
    Verify LesserCreations is removed from the current codegen branch.

    Contract:
        - Import fallback resolves to None.
    """
    assert LesserCreations is None
