from threading import RLock
from types import SimpleNamespace
from typing import Any, Callable, Dict

from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.conduit_meld import ConduitMeld
from melder.aether.conduit.meld.spellspace_meld import SpellSpaceMeld
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class _SpellIndexStub:
    """
    Minimal spell index stub with stable current and lineage ids.
    """

    def __init__(self, current: str) -> None:
        """
        Initialize one spell index stub.
        """
        self.selected_spell_id = current
        self.id = "lineage-{0}".format(current)


class _SpellbookStub:
    """
    Minimal spellbook stub exposing the maps used by concrete meld subclasses.
    """

    def __init__(self) -> None:
        """
        Initialize empty spellbook lookup maps.
        """
        self._spells: dict[Any, Any] = {}
        self._contracted_spells: dict[str, dict[Any, Any]] = {}
        self._lookup_spells: dict[tuple[str, str], Any] = {}
        self._lookup_contracted_spells: dict[str, dict[tuple[str, str], Any]] = {}
        self._spells_by_id: dict[str, Any] = {}
        self._contracted_spells_by_id: dict[str, dict[str, Any]] = {}
        self._spell_id_pool: dict[str, Any] = {}
        self._spellbook_validation_required = False
        # Mirror the real Spellbook staged-cache flag the meld doors check
        # inline before entering the emit helper. False means the helper is
        # never called, matching the common no-cache-staged posture.
        self._cache_emit_required = False


class _CreationContextStub:
    """
    Minimal creation context stub for concrete meld subclass tests.
    """

    def __init__(
            self,
            *,
            no_hooks_no_overrides_result: Any = None,
            no_hooks_overrides_result: Any = None,
            hooks_no_overrides_result: tuple[Any, bool] = (None, False),
            hooks_overrides_result: tuple[Any, bool] = (None, False),
    ) -> None:
        """
        Initialize one public creation-context stub with tracked calls.
        """
        self._cleaned = False
        self.calls: list[str] = []
        self.last_caller_creations: Any = None
        self.last_overrides: Any = None
        self._no_hooks_no_overrides_result = no_hooks_no_overrides_result
        self._no_hooks_overrides_result = no_hooks_overrides_result
        self._hooks_no_overrides_result = hooks_no_overrides_result
        self._hooks_overrides_result = hooks_overrides_result
        # Mirror the real CreationContext door-facing surface: the meld doors
        # branch on `_dynamic_environment` and, in non-dynamic mode, dispatch
        # the executor slots directly. The stub executors delegate through
        # `self.execute_no_hooks` (late-bound attribute read) so call
        # recording and per-test monkeypatching of `execute_no_hooks` keep
        # working, and they return `(instance, created)` tuples to match the
        # real two-tuple executor contract.
        self._dynamic_environment = False

        def _stub_no_overrides_executor(
                caller_creations: Any,
                root_creations: Any = None,
        ) -> tuple[Any, bool]:
            return (self.execute_no_hooks(caller_creations, None), True)

        def _stub_overrides_executor(
                caller_creations: Any,
                overrides: dict[str, Any] | None,
                root_creations: Any = None,
        ) -> tuple[Any, bool]:
            return (self.execute_no_hooks(caller_creations, overrides), True)

        def _stub_no_overrides_instance_executor(
                caller_creations: Any,
        ) -> Any:
            # Instance-only twin (dual-door contract): bare instance, no
            # (instance, created) tuple.
            return self.execute_no_hooks(caller_creations, None)

        self._no_overrides_executor = _stub_no_overrides_executor
        self._no_overrides_instance_executor = (
            _stub_no_overrides_instance_executor
        )
        self._overrides_executor = _stub_overrides_executor

    def execute_no_hooks(
            self,
            caller_creations: Any,
            overrides: dict[str, Any] | None = None,
            root_creations: Any = None,
    ) -> Any:
        """
        Simulate the public no-hooks door.
        """
        if overrides is None:
            self.calls.append("no_hooks_no_overrides")
            self.last_caller_creations = caller_creations
            self.last_overrides = None
            return self._no_hooks_no_overrides_result
        self.calls.append("no_hooks_overrides")
        self.last_caller_creations = caller_creations
        self.last_overrides = overrides
        return self._no_hooks_overrides_result

    def execute(
            self,
            caller_creations: Any,
            overrides: dict[str, Any] | None = None,
            root_creations: Any = None,
    ) -> tuple[Any, bool]:
        """
        Simulate the public hook-aware door.
        """
        if overrides is None:
            self.calls.append("hooks_no_overrides")
            self.last_caller_creations = caller_creations
            self.last_overrides = None
            return self._hooks_no_overrides_result
        self.calls.append("hooks_overrides")
        self.last_caller_creations = caller_creations
        self.last_overrides = overrides
        return self._hooks_overrides_result


class _SpellStub:
    """
    Minimal spell stub carrying only the fields the concrete meld subclasses use.
    """

    def __init__(
            self,
            *,
            spell_id: str,
            existence: Existence = Existence.unique,
            owner_creations: Any | None = None,
            owner_conduit_id: str = "conduit-1",
            spell_name: str = "Spell",
            is_existing_creation: bool = False,
            user_created_object: Any | None = None,
            creation_context: Any | None = None,
            requires_spellspace_request: bool | None = None,
            hooks_enabled: bool = False,
    ) -> None:
        """
        Initialize one spell stub for direct subclass contract checks.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name
        self.spellframe = "frame"
        self.spell_index = _SpellIndexStub(current=spell_id)
        self.existence = existence
        self._owner_creations = owner_creations
        self._owner_conduit_id = owner_conduit_id
        self._owner_conduit_name = "Conduit"
        self.aetheric_frame = "default"
        self._lock = RLock()
        self._cleaned = False
        self._hooks_enabled = hooks_enabled
        self._pre_hooks: list[Callable[..., Any]] = []
        self._activation_hooks: list[Callable[..., Any]] = []
        self._post_hooks: list[Callable[..., Any]] = []
        self._creation_context = creation_context
        self._creation_context_factory = None
        # fast_state mirrors the real CounterSwitch hot-path slot the meld
        # doors read instead of the `state` property.
        self._creation_context_switch = SimpleNamespace(
            state=2 if creation_context is not None else 0,
            fast_state=2 if creation_context is not None else 0,
        )
        self.is_existing_creation = is_existing_creation
        self.user_created_object = user_created_object
        self.mutation_override = None
        # Mirror the real Spell storage slot read directly by the meld doors.
        self._mutation_override = None
        # Mirrors the live Spell fast-door contract: the meld lanes capture
        # the door epoch before execution (epoch-consolidated guard trim).
        self._door_epoch = 0
        if requires_spellspace_request is None:
            requires_spellspace_request = (
                existence is Existence.unique_per_spell_space
            )
        self.requires_spellspace_request = requires_spellspace_request
        self.resolution_required = False
        self.resolution_complete = True
        self._compiler_artifact = SpellCompilerArtifact(spell_id)
        self.spell = lambda: None

    def _get_or_build_creation_context(self) -> Any:
        """
        Return the cached creation context or build through the configured factory.
        """
        if self._creation_context is not None and not self._creation_context._cleaned:
            return self._creation_context
        if self._creation_context_factory is None:
            raise RuntimeError("CreationContextFactory is not configured.")
        creation_context = self._creation_context_factory.get_or_build_for_spell(self)
        self._creation_context = creation_context
        self._creation_context_switch.state = 2
        self._creation_context_switch.fast_state = 2
        return creation_context


class _SpellSpaceStub:
    """
    Minimal spellspace stub with identity fields used by SpellSpaceMeld.
    """

    def __init__(self, *, spellspace_id: str, owner_conduit_id: str) -> None:
        """
        Initialize one spellspace stub.
        """
        self.id = spellspace_id
        self.owner_conduit_id = owner_conduit_id


def _seed_spell(spellbook: _SpellbookStub, spell: _SpellStub) -> None:
    """
    Seed all direct-id spellbook maps for one spell.
    """
    spellbook._spells[spell.spell_index] = spell
    spellbook._spells_by_id[spell.spell_id] = spell
    spellbook._spell_id_pool[spell.spell_id] = spell


def _make_conduit_meld(
        *,
        conduit_id: str = "conduit-1",
        spellbook: _SpellbookStub | None = None,
) -> tuple[ConduitMeld, ConduitCreations, _SpellbookStub]:
    """
    Build one conduit-facing meld instance and its conduit-owned creations store.
    """
    effective_spellbook = spellbook or _SpellbookStub()
    creations = ConduitCreations(conduit_id=conduit_id)
    meld = ConduitMeld(
        conduit_creations=creations,
        spellbook=effective_spellbook,
        conduit_id=conduit_id,
        resolution_conduit_id=conduit_id,
    )
    return meld, creations, effective_spellbook


def _make_spellspace_meld(
        *,
        conduit_id: str = "conduit-1",
        spellspace_id: str = "space-1",
        spellbook: _SpellbookStub | None = None,
) -> tuple[SpellSpaceMeld, Creations, ConduitCreations, _SpellbookStub]:
    """
    Build one spellspace-facing meld instance and both creations stores.
    """
    effective_spellbook = spellbook or _SpellbookStub()
    owner_creations = ConduitCreations(conduit_id=conduit_id)
    spellspace_creations = Creations(
        owner_conduit_id=conduit_id,
        id=spellspace_id,
    )
    spellspace = _SpellSpaceStub(
        spellspace_id=spellspace_id,
        owner_conduit_id=conduit_id,
    )
    meld = SpellSpaceMeld(
        spellspace=spellspace,
        spellspace_creations=spellspace_creations,
        conduit_creations=owner_creations,
        root_creations=owner_creations,
        cluster_creations=ClusterCreations(),
        spellbook=effective_spellbook,
        conduit_id=conduit_id,
        resolution_conduit_id=conduit_id,
    )
    return meld, spellspace_creations, owner_creations, effective_spellbook


def test_conduit_meld_init_stores_conduit_creations() -> None:
    """
    Verify ConduitMeld keeps the conduit-owned creations reference.
    """
    meld, creations, _spellbook = _make_conduit_meld()
    assert meld._conduit_creations is creations


def test_conduit_meld_cleanup_drops_conduit_creations() -> None:
    """
    Verify ConduitMeld cleanup removes its subclass-owned creations reference.
    """
    meld, _creations, _spellbook = _make_conduit_meld()
    meld.cleanup()
    assert not hasattr(meld, "_creations")


def test_conduit_meld_meld_no_hooks_uses_conduit_creations_for_unique_per_conduit() -> None:
    """
    Verify ConduitMeld routes no-hook unique_per_conduit work through conduit storage.
    """
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=creations,
        creation_context=context,
    )
    _seed_spell(spellbook, spell)
    assert meld.meld(spell="spell-1") == "instance"
    assert context.calls == ["no_hooks_no_overrides"]
    assert context.last_caller_creations is meld


def test_conduit_meld_meld_no_hooks_overrides_uses_conduit_creations() -> None:
    """
    Verify ConduitMeld routes override-capable no-hook work through conduit storage.
    """
    meld, creations, spellbook = _make_conduit_meld()
    context = _CreationContextStub(no_hooks_overrides_result="instance")
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=creations,
        creation_context=context,
    )
    _seed_spell(spellbook, spell)
    assert meld.meld(spell="spell-1", spell_override=[1, 2]) == "instance"
    assert context.calls == ["no_hooks_overrides"]
    assert context.last_caller_creations is meld
    assert context.last_overrides == {"__args__": [1, 2]}


def test_conduit_meld_hooks_lane_fires_activation_only_when_created() -> None:
    """
    Verify ConduitMeld activation hooks only fire when the compiled door reports created.
    """
    meld, creations, spellbook = _make_conduit_meld()
    events: list[str] = []

    def activation(instance: Any) -> None:
        events.append("activation:{0}".format(instance))

    context = _CreationContextStub(hooks_no_overrides_result=("created", True))
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=creations,
        creation_context=context,
        hooks_enabled=True,
    )
    spell._activation_hooks = [activation]
    _seed_spell(spellbook, spell)

    assert meld.meld(spell="spell-1") == "created"
    assert events == ["activation:created"]


def test_conduit_meld_rejects_spellspace_request_in_meld() -> None:
    """
    Verify ConduitMeld refuses spellspace-request spells on the conduit-facing door.
    """
    meld, _creations, spellbook = _make_conduit_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        spell_name="BasicService",
        existence=Existence.unique_per_spell_space,
    )
    _seed_spell(spellbook, spell)

    with pytest.raises(
            RuntimeError,
            match=r"BasicService.*spell_id=spell-1.*must be built from a spellspace",
    ):
        meld.meld(spell="spell-1")


def test_conduit_meld_existing_spell_returns_unique_per_conduit_creation() -> None:
    """
    Verify ConduitMeld returns a live unique_per_conduit object from conduit storage.
    """
    meld, creations, spellbook = _make_conduit_meld()
    live_instance = object()
    creations.add_creation("spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld_existing_spell(spell="spell-1") is live_instance


def test_conduit_meld_existing_spell_uses_owner_creations_for_unique() -> None:
    """
    Verify ConduitMeld reuses owner creations for shared unique routes.
    """
    meld, _creations, spellbook = _make_conduit_meld()
    owner_creations = ConduitCreations(conduit_id="owner")
    live_instance = object()
    owner_creations.add_creation("spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
        owner_conduit_id="owner",
    )
    _seed_spell(spellbook, spell)

    assert meld.meld_existing_spell(spell="spell-1") is live_instance


def test_conduit_meld_existing_spell_returns_existing_creation_object() -> None:
    """
    Verify ConduitMeld returns the user-created object for existing-creation spells.
    """
    meld, _creations, spellbook = _make_conduit_meld()
    live_object = object()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=live_object,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld_existing_spell(spell="spell-1") is live_object


def test_conduit_meld_existing_spell_rejects_many_lifecycle() -> None:
    """
    Verify ConduitMeld still rejects the ambiguous many lifecycle on existing-only lookup.
    """
    meld, _creations, spellbook = _make_conduit_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
    )
    _seed_spell(spellbook, spell)

    with pytest.raises(RuntimeError, match="Existence.many"):
        meld.meld_existing_spell(spell="spell-1")


def test_conduit_meld_has_live_creation_returns_true_for_many_bucket() -> None:
    """
    Verify ConduitMeld reports many buckets as live when any items exist.
    """
    meld, creations, spellbook = _make_conduit_meld()
    creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
    )
    _seed_spell(spellbook, spell)

    assert meld.has_live_creation(spell="spell-1") is True


def test_conduit_meld_describe_live_creation_status_reports_unique_per_conduit() -> None:
    """
    Verify ConduitMeld reports conduit-scoped storage for unique_per_conduit.
    """
    meld, creations, spellbook = _make_conduit_meld(conduit_id="conduit-1")
    creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    _seed_spell(spellbook, spell)

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


def test_conduit_meld_describe_live_creation_status_reports_owner_route() -> None:
    """
    Verify ConduitMeld reports owner-creations storage for shared lifetimes.
    """
    meld, _creations, spellbook = _make_conduit_meld(conduit_id="caller")
    owner_creations = ConduitCreations(conduit_id="owner")
    owner_creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
        owner_conduit_id="owner",
    )
    _seed_spell(spellbook, spell)

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


def test_conduit_meld_describe_live_creation_status_reports_existing_creation() -> None:
    """
    Verify ConduitMeld reports existing-creation status from the user object.
    """
    meld, _creations, spellbook = _make_conduit_meld()
    live_object = object()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=live_object,
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "existing_creation",
        "storage_owner_conduit_id": None,
        "active_spellspace_id": None,
        "creation_count": 1,
    }


def test_conduit_meld_describe_live_creation_status_rejects_spellspace_request() -> None:
    """
    Verify ConduitMeld refuses spellspace-request status probes.
    """
    meld, _creations, spellbook = _make_conduit_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        spell_name="BasicService",
        existence=Existence.unique_per_spell_space,
    )
    _seed_spell(spellbook, spell)

    with pytest.raises(
            RuntimeError,
            match=r"BasicService.*spell_id=spell-1.*must be built from a spellspace",
    ):
        meld.describe_live_creation_status(spell="spell-1")


def test_spellspace_meld_init_stores_both_creations_surfaces() -> None:
    """
    Verify SpellSpaceMeld keeps both spellspace-local and owner-conduit creations.
    """
    meld, spellspace_creations, owner_creations, _spellbook = _make_spellspace_meld()
    assert meld._spellspace_creations is spellspace_creations
    assert meld._conduit_creations is owner_creations
    assert meld._spellspace_id == "space-1"


def test_spellspace_meld_cleanup_drops_subclass_references() -> None:
    """
    Verify SpellSpaceMeld cleanup deletes spellspace-specific fields.
    """
    meld, _spellspace_creations, _owner_creations, _spellbook = _make_spellspace_meld()
    meld.cleanup()
    assert not hasattr(meld, "_spellspace")
    assert not hasattr(meld, "_spellspace_creations")
    assert not hasattr(meld, "_conduit_creations")


def test_spellspace_meld_meld_uses_spellspace_creations_for_spellspace_scope() -> None:
    """
    Verify SpellSpaceMeld routes unique_per_spell_space work through spellspace-local storage.
    """
    meld, spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
        owner_creations=spellspace_creations,
        creation_context=context,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld(spell="spell-1") == "instance"
    assert context.last_caller_creations is meld


def test_spellspace_meld_meld_uses_owner_creations_for_unique_per_conduit() -> None:
    """
    Verify SpellSpaceMeld routes unique_per_conduit work through owner conduit storage.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=owner_creations,
        creation_context=context,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld(spell="spell-1") == "instance"
    assert context.last_caller_creations is meld


def test_spellspace_meld_meld_uses_owner_creations_for_many_scope() -> None:
    """
    Verify SpellSpaceMeld routes many-scope work through owner conduit storage.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    context = _CreationContextStub(no_hooks_no_overrides_result="instance")
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        owner_creations=owner_creations,
        creation_context=context,
        requires_spellspace_request=False,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld(spell="spell-1") == "instance"
    assert context.last_caller_creations is meld


def test_spellspace_meld_hooks_lane_uses_spellspace_creations_for_activation() -> None:
    """
    Verify SpellSpaceMeld hook flow still uses spellspace-local storage for spellspace scope.
    """
    meld, spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    events: list[str] = []

    def activation(instance: Any) -> None:
        events.append("activation:{0}".format(instance))

    context = _CreationContextStub(hooks_no_overrides_result=("created", True))
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
        owner_creations=spellspace_creations,
        creation_context=context,
        hooks_enabled=True,
    )
    spell._activation_hooks = [activation]
    _seed_spell(spellbook, spell)

    assert meld.meld(spell="spell-1") == "created"
    assert context.last_caller_creations is meld
    assert events == ["activation:created"]


def test_spellspace_meld_existing_spell_returns_spellspace_creation() -> None:
    """
    Verify SpellSpaceMeld returns the live spellspace-scoped object.
    """
    meld, spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    live_instance = object()
    spellspace_creations.add_creation("spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld_existing_spell(spell="spell-1") is live_instance


def test_spellspace_meld_existing_spell_returns_owner_conduit_creation() -> None:
    """
    Verify SpellSpaceMeld reuses owner conduit storage for unique_per_conduit.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    live_instance = object()
    owner_creations.add_creation("spell-1", live_instance)
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld_existing_spell(spell="spell-1") is live_instance


def test_spellspace_meld_existing_spell_returns_existing_creation_object() -> None:
    """
    Verify SpellSpaceMeld returns the user-created object for existing-creation spells.
    """
    meld, _spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    live_object = object()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=live_object,
    )
    _seed_spell(spellbook, spell)

    assert meld.meld_existing_spell(spell="spell-1") is live_object


def test_spellspace_meld_has_live_creation_true_for_spellspace_creation() -> None:
    """
    Verify SpellSpaceMeld reports spellspace-local live state correctly.
    """
    meld, spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    spellspace_creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    _seed_spell(spellbook, spell)

    assert meld.has_live_creation(spell="spell-1") is True


def test_spellspace_meld_has_live_creation_false_when_spellspace_creation_missing() -> None:
    """
    Verify SpellSpaceMeld reports missing spellspace-local live state correctly.
    """
    meld, _spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    _seed_spell(spellbook, spell)

    assert meld.has_live_creation(spell="spell-1") is False


def test_spellspace_meld_describe_live_creation_status_reports_spellspace_scope() -> None:
    """
    Verify SpellSpaceMeld reports spellspace-local status payloads.
    """
    meld, _spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": False,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique_per_spell_space",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "spellspace",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": "space-1",
        "creation_count": 0,
    }


def test_spellspace_meld_describe_live_creation_status_reports_owner_conduit_scope() -> None:
    """
    Verify SpellSpaceMeld reports owner conduit storage for unique_per_conduit.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    owner_creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique_per_conduit",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "owner_conduit",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": "space-1",
        "creation_count": 1,
    }


def test_spellspace_meld_describe_live_creation_status_reports_owner_conduit_many() -> None:
    """
    Verify SpellSpaceMeld reports owner conduit many-scope payloads.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    owner_creations.add_many_creations("spell-1", object())
    owner_creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        requires_spellspace_request=False,
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "many",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "owner_conduit_many",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": None,
        "creation_count": 2,
    }


def test_spellspace_meld_describe_live_creation_status_reports_owner_route() -> None:
    """
    Verify SpellSpaceMeld reports owner-creations storage for shared lifetimes.
    """
    meld, _spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    owner_creations = ConduitCreations(conduit_id="owner")
    owner_creations.add_creation("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
        owner_conduit_id="owner",
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "owner_creations",
        "storage_owner_conduit_id": "owner",
        "active_spellspace_id": None,
        "creation_count": 1,
    }


def test_spellspace_meld_describe_live_creation_status_reports_existing_creation() -> None:
    """
    Verify SpellSpaceMeld reports existing-creation payloads.
    """
    meld, _spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    live_object = object()
    spell = _SpellStub(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=live_object,
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "unique",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "existing_creation",
        "storage_owner_conduit_id": None,
        "active_spellspace_id": None,
        "creation_count": 1,
    }
