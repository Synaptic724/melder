"""Additional contract tests for Meld resolution and registration helpers."""
from contextvars import ContextVar
from threading import RLock
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
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
    conduit_id = getattr(effective_creations, "owner_conduit_id", "conduit-1")
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
    return Creations(
        conduit_id=conduit._id,
        spellspace_stack=ContextVar("spellspace_stack_conduit_1", default=[]),
    )


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


def test_resolve_spell_string_uses_spell_id_path() -> None:
    """
    Verify string spell inputs route through spell_id resolution.

    Contract:
        - String `spell` values are treated as spell ids.
    """
    spell = _SpellStub(spell_id="spell-1")
    spellbook = _SpellbookStub()
    spellbook._spell_id_pool["spell-1"] = spell
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell(
        spell="spell-1",
        spell_name=None,
        spellframe=None,
        binding_name=None,
    ) is spell


def test_resolve_spell_with_spell_name_and_spellframe_uses_name_as_spell_source() -> None:
    """
    Verify spell_name participates in normalization when spellframe is also provided.

    Contract:
        - `spell_name` becomes the spell source when `spell` is None.
        - `spellframe` remains part of the normalized lookup key.
    """
    spell = _SpellStub(spell_id="spell-1")
    frame_key, bind_key = SpellInputUtils.normalize_spell_key(
        spell="NamedSpell",
        spellframe="frame",
        binding_name="primary",
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
        spell_name="NamedSpell",
        spellframe="frame",
        binding_name="primary",
    ) is spell


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


def test_resolve_spell_by_id_prefers_spell_id_pool() -> None:
    """
    Verify spell_id resolution prefers the pooled spell map before other maps.

    Contract:
        - `_spell_id_pool` entries are returned first.
    """
    pooled_spell = _SpellStub(spell_id="spell-pooled")
    spellbook = _SpellbookStub()
    spellbook._spell_id_pool["spell-pooled"] = pooled_spell
    meld = _make_meld(spellbook=spellbook)
    assert meld._resolve_spell_by_id("spell-pooled") is pooled_spell


def test_meld_does_not_own_creation_context_factory() -> None:
    """
    Verify Meld no longer owns a creation-context factory.

    Contract:
        - Meld instance has no `_creation_context_factory` attribute.
        - CreationContextFactory ownership is on Spell.
    """
    meld = _make_meld(creations=object())
    assert hasattr(meld, "_creation_context_factory") is False


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


def test_legacy_runtime_helpers_removed_from_meld() -> None:
    """
    Verify removed runtime helper methods are no longer exposed on Meld.

    Contract:
        - Legacy runtime helper methods remain removed after CreationContext migration.
    """
    meld = _make_meld(creations=object())
    assert not hasattr(meld, "_create_meld_context")
    assert not hasattr(meld, "_dispatch_meld_runtime")
    assert not hasattr(meld, "_execute_meld_runtime_context")
    assert not hasattr(meld, "_select_creations_for_spell")
    assert not hasattr(meld, "_raise_override_on_existing_instance")
    assert not hasattr(meld, "_get_existing_creation_from_creations")
    assert not hasattr(meld, "_get_active_spellspace_for_creations")


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


def test_register_spellspace_creation_registers_instance() -> None:
    """
    Verify spellspace registration stores the instance in the spellspace bucket.

    Contract:
        - Creations.register_spellspace_creation stores and returns the instance.
    """
    creations = _make_creations()
    spellspace = SimpleNamespace(
        id="space-1",
        owner_conduit_id=creations.owner_conduit_id,
    )
    creations._spellspace_stack.set([spellspace])
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
