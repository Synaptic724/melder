from typing import List, Optional

import pytest
from melder import Aether, Conduit
from melder.aether.conduit.meld.spellspace_meld import SpellSpaceMeld
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_input_fast_door() -> None:
    """
    Purpose:
        Ensure name/class fast-door component tests start with a clean Aether singleton.
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


@pytest.fixture
def door_calls(monkeypatch: pytest.MonkeyPatch) -> List[int]:
    """
    Purpose:
        Count entries into `SpellSpaceMeld.meld` so a spellspace warm hit is observable.
    Contract:
        - `door_calls[0]` is the number of door entries since the fixture was installed.
        - The real door still runs, so results are unchanged.
    Args:
        monkeypatch: pytest monkeypatch fixture.
    Returns:
        List[int]: One-element list holding the count.
    """
    calls = [0]
    original = SpellSpaceMeld.meld

    def counting(self: SpellSpaceMeld, *args: object, **kwargs: object) -> object:
        """Record one door entry, then run the real door."""
        calls[0] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SpellSpaceMeld, "meld", counting)
    return calls


def _make_spellbook(dynamic: bool = False) -> Spellbook:
    """
    Purpose:
        Provide a Spellbook whose frame posture is automatic (the only posture that mints) or dynamic.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1 for determinism.
    Args:
        dynamic: When True the frame posture is dynamic; nothing mints there.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=dynamic)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class PerConduitService:
    """
    Purpose:
        Service type for unique_per_conduit lane tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Returns:
            None.
        """
        self.marker = object()


class SharedService:
    """
    Purpose:
        Service type for frame-wide `unique` lane tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Returns:
            None.
        """
        self.marker = object()


class FreshService:
    """
    Purpose:
        Service type for Existence.many lane tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Returns:
            None.
        """
        self.marker = object()


class ConfigurableService:
    """
    Purpose:
        Service type for the dict override arm.
    Contract:
        - `value` records the constructor input observable from tests.
    """

    def __init__(self, value: int = 0) -> None:
        """
        Purpose:
            Record the constructor input for override-arm assertions.
        Args:
            value: Optional override-supplied constructor input.
        Returns:
            None.
        """
        self.value = value


class SpaceMarker:
    """
    Purpose:
        Object scoped to one spellspace.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Returns:
            None.
        """
        self.marker = object()


class BoundObject:
    """
    Purpose:
        Application object bound as an existing creation.
    Contract:
        - Melds return the bound object itself.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Create a plain object for binding as an existing creation.
        Returns:
            None.
        """
        self.value = 0


class AliasedService:
    """
    Purpose:
        Service bound under a spellframe that spells another spell's id.
    Contract:
        - Instances are distinguishable by type from `SharedService`.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Returns:
            None.
        """
        self.marker = object()


class _SpellIdPoolSpy(dict):
    """
    Purpose:
        Drop-in spell-id-pool wrapper that records a full-lane pass.
    Contract:
        - A warm hit of either registry returns before the door's pool read
          (`_spell_id_pool.get(...)`), so `normal_lane_entered` stays False on a hit
          and flips True on every miss, bypass or cold meld. The name/class full lane
          reads the pool right after its `_input_resolution_cache` read.
        - Lookups still delegate to the captured pool snapshot.
    """

    def __init__(self, source: dict) -> None:
        super().__init__(source)
        self.normal_lane_entered = False

    def get(self, *args: object, **kwargs: object) -> object:
        """Record the full-lane read, then delegate to the real lookup."""
        self.normal_lane_entered = True
        return super().get(*args, **kwargs)


def _install_lane_spy(meld: object) -> _SpellIdPoolSpy:
    """
    Purpose:
        Swap a meld door's spell-id pool for a recording spy and return it.
    Contract:
        - Install after the cold build so only later melds are observed.
    Args:
        meld: Meld door whose `_spell_id_pool` slot is wrapped.
    Returns:
        _SpellIdPoolSpy: The installed spy, for lane assertions.
    """
    spy = _SpellIdPoolSpy(meld._spell_id_pool)
    meld._spell_id_pool = spy
    return spy


def _poison_no_override_slot(context: object) -> None:
    """
    Purpose:
        Replace a context's no-override slot with a raising stub.
    Contract:
        - Any later call into that context's no-override door raises AssertionError,
          so a served meld proves the door was not entered.
    Args:
        context: The creation context captured in a fast-door entry.
    Returns:
        None.
    """

    def _door_must_not_run(meld: object) -> object:
        """Fail the test if the existing-object lane enters the door."""
        raise AssertionError("existing-object lane entered the no-override door")

    context._no_overrides_instance_executor = _door_must_not_run


def test_name_and_class_melds_mint_entries_and_serve_warm_hits() -> None:
    """
    Purpose:
        Verify the first meld by name and by class mints an entry and later ones hit it.
    Contract:
        - `conduit.meld("Name")` mints `_fast_input_doors["Name"]`; `conduit.meld(spell=Cls)`
          mints `_fast_input_doors[Cls]`; both point at the same spell and context.
        - Warm melds return the per-conduit object without the door's pool read.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    try:
        registry = conduit._meld._fast_input_doors
        assert registry == {}
        first = conduit.meld("PerConduitService")
        assert "PerConduitService" in registry
        assert PerConduitService not in registry
        assert conduit.meld(spell=PerConduitService) is first
        assert PerConduitService in registry
        name_entry = registry["PerConduitService"]
        class_entry = registry[PerConduitService]
        assert name_entry[0] is class_entry[0]
        assert name_entry[0].spell_id == spell_id
        assert name_entry[1] is class_entry[1]

        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("PerConduitService") is first
        assert conduit.meld(spell=PerConduitService) is first
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_warm_lane_keeps_existence_semantics_by_name_and_class() -> None:
    """
    Purpose:
        Verify warm name and class melds keep every existence's reuse rule.
    Contract:
        - unique and unique_per_conduit: the same object by name, by class and by id.
        - many: a new object of the right type per call, by name and by class.
    """
    spellbook = _make_spellbook()
    shared_id = spellbook.bind(spell=SharedService, existence=Existence.unique)
    per_conduit_id = spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    fresh_id = spellbook.bind(spell=FreshService, existence=Existence.many)
    conduit = spellbook.conjure(name="root")
    try:
        shared = conduit.meld("SharedService")
        per_conduit = conduit.meld(spell=PerConduitService)
        fresh = conduit.meld("FreshService")
        for _ in range(3):
            assert conduit.meld("SharedService") is shared
            assert conduit.meld(spell=SharedService) is shared
            assert conduit.meld(spell_id=shared_id) is shared
            assert conduit.meld("PerConduitService") is per_conduit
            assert conduit.meld(spell=PerConduitService) is per_conduit
            assert conduit.meld(spell_id=per_conduit_id) is per_conduit
            by_name = conduit.meld("FreshService")
            by_class = conduit.meld(spell=FreshService)
            by_id = conduit.meld(spell_id=fresh_id)
            assert type(by_name) is FreshService
            assert type(by_class) is FreshService
            assert type(by_id) is FreshService
            assert len({id(fresh), id(by_name), id(by_class), id(by_id)}) == 4
    finally:
        conduit.permanent_cleanup()


def test_key_spelling_is_the_callers_and_both_spellings_resolve_one_spell() -> None:
    """
    Purpose:
        Verify the registry is keyed by the string the caller passed while resolution stays case-insensitive.
    Contract:
        - `meld("SharedService")` and `meld("sharedservice")` return the same singleton.
        - Each spelling gets its own entry, both pointing at the same spell.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=SharedService, existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        shared = conduit.meld("SharedService")
        assert conduit.meld("sharedservice") is shared
        registry = conduit._meld._fast_input_doors
        assert registry["SharedService"][0] is registry["sharedservice"][0]
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("sharedservice") is shared
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_dict_override_arm_is_served_warm_by_name_and_class() -> None:
    """
    Purpose:
        Verify a name or class meld with a non-empty dict override rides the override arm.
    Contract:
        - After one plain meld minted the entry, `meld("Name", override={...})` applies the payload
          and returns before the door's pool read; a later plain meld keeps the default.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=ConfigurableService, existence=Existence.many)
    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.meld("ConfigurableService").value == 0
        assert conduit.meld(spell=ConfigurableService).value == 0
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("ConfigurableService", override={"value": 7}).value == 7
        assert conduit.meld(spell=ConfigurableService, override={"value": 9}).value == 9
        assert conduit.meld("ConfigurableService").value == 0
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_tuple_list_and_empty_override_payloads_take_the_door() -> None:
    """
    Purpose:
        Verify only a non-empty dict payload is served warm; other payload shapes go through the door.
    Contract:
        - A tuple, a list and an empty dict each enter the full lane (pool read) and still work.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=ConfigurableService, existence=Existence.many)
    conduit = spellbook.conjure(name="root")
    try:
        conduit.meld("ConfigurableService")
        for payload in ((("value", 3),), [("value", 4)], {}):
            spy = _install_lane_spy(conduit._meld)
            result = conduit.meld("ConfigurableService", override=payload)
            assert type(result) is ConfigurableService
            assert spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_existing_object_is_returned_by_name_and_class_without_the_door() -> None:
    """
    Purpose:
        Verify a bound existing object rides the existing-object arm on the name/class lane.
    Contract:
        - The entry's flag is set; the bound object is returned by name and by class.
        - With the captured context's no-override slot poisoned, the object is still returned,
          proving the door is not entered.
    """
    spellbook = _make_spellbook()
    bound = BoundObject()
    spellbook.bind(spell=bound, existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.meld("BoundObject") is bound
        assert conduit.meld(spell=BoundObject) is bound
        registry = conduit._meld._fast_input_doors
        assert registry["BoundObject"][3] is True
        assert registry[BoundObject][3] is True
        _poison_no_override_slot(registry["BoundObject"][1])
        assert conduit.meld("BoundObject") is bound
        assert conduit.meld(spell=BoundObject) is bound
    finally:
        conduit.permanent_cleanup()


def test_instances_callables_and_unhashable_inputs_never_mint() -> None:
    """
    Purpose:
        Verify the mint rule: only registered-name strings and classes become keys.
    Contract:
        - An instance passed as `spell` resolves by its class name and returns the right object,
          but mints nothing (an instance key would be per object and would keep it alive).
        - A lambda and an unhashable list raise the door's KeyError and mint nothing.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=SharedService, existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        shared = conduit.meld("SharedService")
        registry = conduit._meld._fast_input_doors
        before = dict(registry)
        assert conduit.meld(spell=SharedService()) is shared
        assert dict(registry) == before
        with pytest.raises(KeyError):
            conduit.meld(spell=lambda: None)
        with pytest.raises(KeyError):
            conduit.meld(spell=[1, 2])
        assert dict(registry) == before
    finally:
        conduit.permanent_cleanup()


def test_spellframe_and_binding_name_shapes_never_mint() -> None:
    """
    Purpose:
        Verify addressed melds (spellframe or binding_name given) keep the door path.
    Contract:
        - `meld(spellframe=Cls)` and `meld(spell=Cls, binding_name="__default__")` resolve and return
          the singleton but add no entry.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=SharedService, existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        shared = conduit.meld(spellframe=SharedService)
        assert conduit.meld(spell=SharedService, binding_name="__default__") is shared
        assert conduit._meld._fast_input_doors == {}
        assert conduit.meld("SharedService") is shared
        assert list(conduit._meld._fast_input_doors) == ["SharedService"]
    finally:
        conduit.permanent_cleanup()


def test_dynamic_world_never_mints() -> None:
    """
    Purpose:
        Verify a dynamic conduit takes its gated path and mints no name/class entry.
    Contract:
        - Repeated name and class melds on a dynamic conduit leave `_fast_input_doors` empty.
    """
    spellbook = _make_spellbook(dynamic=True)
    spellbook.bind(spell=SharedService, existence=Existence.unique)
    conduit = spellbook.conjure(name="root", dynamic=True)
    try:
        shared = conduit.meld("SharedService")
        for _ in range(3):
            assert conduit.meld("SharedService") is shared
            assert conduit.meld(spell=SharedService) is shared
        assert conduit._meld._fast_input_doors == {}
        assert conduit._meld._fast_meld_doors == {}
    finally:
        conduit.permanent_cleanup()


def test_spell_hooks_bypass_the_lane_and_the_entry_rebuilds_after_detach() -> None:
    """
    Purpose:
        Verify spell-level hooks bump the epoch so a stale name entry misses, and the full lane rebuilds it.
    Contract:
        - With a pre-cast hook attached, a name meld fires the hook and reads the pool (bypass).
        - After the hooks detach, the next name meld reads the pool once (rebuild) and later ones hit.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld("PerConduitService")
        spell = spellbook._spell_id_pool[spell_id]
        stale_epoch = conduit._meld._fast_input_doors["PerConduitService"][2]
        hook_calls: List[str] = []
        spell._set_hooks(pre_hooks=[lambda: hook_calls.append("pre")])
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("PerConduitService") is first
        assert hook_calls == ["pre"]
        assert spy.normal_lane_entered

        spell._set_hooks(pre_hooks=[])
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("PerConduitService") is first
        assert spy.normal_lane_entered
        assert conduit._meld._fast_input_doors["PerConduitService"][2] > stale_epoch
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("PerConduitService") is first
        assert not spy.normal_lane_entered
        assert hook_calls == ["pre"]
    finally:
        conduit.permanent_cleanup()


def test_meld_hooks_in_place_mutation_bypasses_the_lane() -> None:
    """
    Purpose:
        Verify the live `_meld_hooks` read routes a name meld to the full lane when hooks appear.
    Contract:
        - After an in-place mutation of the shared hooks map, the meld-level hook fires and the pool
          is read; the object is unchanged.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld("PerConduitService")
        spy = _install_lane_spy(conduit._meld)
        hook_calls: List[object] = []
        meld = conduit._meld
        if meld._meld_hooks is None:
            meld._meld_hooks = {}
        meld._meld_hooks["on_meld_pre_resolve"] = [lambda target: hook_calls.append(target)]
        assert conduit.meld("PerConduitService") is first
        assert len(hook_calls) == 1
        assert spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_context_invalidation_misses_and_the_full_lane_rebuilds_the_entry() -> None:
    """
    Purpose:
        Verify `Spell._cleanup_creation_context()` invalidates a name entry and the rebuild replaces it.
    Contract:
        - After the chokepoint (paired with deferred-resolution regating as production does), a name
          meld reads the pool and returns the same per-conduit object.
        - The replaced entry captures the fresh context; the next meld hits.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld("PerConduitService")
        spell = spellbook._spell_id_pool[spell_id]
        spell._cleanup_creation_context()
        spell.resolution_required = True
        spell.resolution_complete = False
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("PerConduitService") is first
        assert spy.normal_lane_entered
        entry = conduit._meld._fast_input_doors["PerConduitService"]
        assert entry[1] is spell._creation_context
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld("PerConduitService") is first
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_validation_required_flag_bypasses_the_lane() -> None:
    """
    Purpose:
        Verify the spellbook-wide validation flag routes name melds to the full lane while set.
    Contract:
        - With `_spellbook_validation_required` True the pool is read; cleared, the lane serves again.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=PerConduitService)
        spy = _install_lane_spy(conduit._meld)
        spellbook._set_spellbook_validation_required(True)
        assert conduit.meld(spell=PerConduitService) is first
        assert spy.normal_lane_entered
        spellbook._set_spellbook_validation_required(False)
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld(spell=PerConduitService) is first
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_removed_spell_is_not_served_from_a_stale_name_entry() -> None:
    """
    Purpose:
        Verify a removed spell's stale name entry misses and the meld fails exactly like the full lane.
    Contract:
        - After `cleanup_and_remove_spell`, a name meld with the stale entry still present raises the
          same exception type and message as the full lane with the entry removed.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    try:
        conduit.meld("PerConduitService")
        assert "PerConduitService" in conduit._meld._fast_input_doors
        spellbook.cleanup_and_remove_spell(spell_id)
        with pytest.raises(Exception) as stale_entry:
            conduit.meld("PerConduitService")
        conduit._meld._fast_input_doors.pop("PerConduitService", None)
        with pytest.raises(Exception) as full_lane:
            conduit.meld("PerConduitService")
        assert type(stale_entry.value) is type(full_lane.value)
        assert str(stale_entry.value) == str(full_lane.value)
    finally:
        conduit.permanent_cleanup()


def test_removed_name_cannot_be_rebound_after_conjure_in_an_automatic_world() -> None:
    """
    Purpose:
        Pin the posture wall the name registry relies on: in an automatic world a key never comes to
        resolve to a different spell after conjure.
    Contract:
        - After `cleanup_and_remove_spell`, `meld("svc")` raises the door's KeyError (the stale entry
          missed; nothing is served) and a bind under the same spellframe is refused by the frame
          posture, so no second holder of that name can exist in this world.
    """
    spellbook = _make_spellbook()
    old_id = spellbook.bind(spell=SharedService, spellframe="svc", existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        assert type(conduit.meld("svc")) is SharedService
        spellbook.cleanup_and_remove_spell(old_id)
        with pytest.raises(KeyError):
            conduit.meld("svc")
        with pytest.raises(RuntimeError, match="disabled after conjure"):
            spellbook.bind(spell=AliasedService, spellframe="svc", existence=Existence.unique)
        with pytest.raises(KeyError):
            conduit.meld("svc")
    finally:
        conduit.permanent_cleanup()


def test_name_equal_to_another_spells_id_never_aliases_the_id_lane() -> None:
    """
    Purpose:
        Verify the name registry and the id registry cannot serve each other's spells.
    Contract:
        - `AliasedService` is bound under a spellframe that spells `SharedService`'s id.
        - `meld(that_string)` resolves by name to `AliasedService`; `meld(spell_id=that_string)` resolves
          to `SharedService`; both warm hits keep their types and the two registries hold different spells
          under the same string.
    """
    spellbook = _make_spellbook()
    shared_id = spellbook.bind(spell=SharedService, existence=Existence.unique)
    spellbook.bind(spell=AliasedService, spellframe=shared_id, existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        by_name = conduit.meld(shared_id)
        by_id = conduit.meld(spell_id=shared_id)
        assert type(by_name) is AliasedService
        assert type(by_id) is SharedService
        meld = conduit._meld
        assert meld._fast_input_doors[shared_id][0] is not meld._fast_meld_doors[shared_id][0]
        spy = _install_lane_spy(meld)
        assert conduit.meld(shared_id) is by_name
        assert conduit.meld(spell_id=shared_id) is by_id
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_unknown_name_raises_the_doors_error_cold_and_warm() -> None:
    """
    Purpose:
        Verify an unregistered name raises the door's KeyError whether or not other entries exist.
    Contract:
        - `meld("Nope")` raises KeyError before and after another name has a warm entry; nothing mints for it.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=SharedService, existence=Existence.unique)
    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(KeyError):
            conduit.meld("Nope")
        conduit.meld("SharedService")
        with pytest.raises(KeyError):
            conduit.meld("Nope")
        assert "Nope" not in conduit._meld._fast_input_doors
    finally:
        conduit.permanent_cleanup()


def test_spellspace_name_and_class_lane_serves_scoped_objects(door_calls: List[int]) -> None:
    """
    Purpose:
        Verify `SpellSpace.meld` mints and serves name and class entries on the spellspace door.
    Contract:
        - The first `space.meld("SpaceMarker")` enters the door and mints; warm name and class melds
          return the same marker without entering the door.
        - A second spellspace builds its own marker through its own door.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=SpaceMarker, existence=Existence.unique_per_spell_space)
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            first = space.meld("SpaceMarker")
            assert door_calls[0] == 1
            assert "SpaceMarker" in space._meld._fast_input_doors
            assert space.meld("SpaceMarker") is first
            assert space.meld(spell=SpaceMarker) is first
            assert door_calls[0] == 2
            assert space.meld(spell=SpaceMarker) is first
            assert door_calls[0] == 2
        with conduit.enter_spellspace() as second_space:
            other = second_space.meld("SpaceMarker")
            assert type(other) is SpaceMarker
            assert other is not first
    finally:
        conduit.permanent_cleanup()


def test_spellspace_override_arm_and_instance_rule_mirror_the_conduit(door_calls: List[int]) -> None:
    """
    Purpose:
        Verify the spellspace lane serves the dict override arm and mints nothing for an instance input.
    Contract:
        - After one plain meld, `space.meld("ConfigurableService", override={...})` returns without the door.
        - `space.meld(spell=ConfigurableService())` resolves through the door and adds no entry.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=ConfigurableService, existence=Existence.many)
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            assert space.meld("ConfigurableService").value == 0
            entered = door_calls[0]
            assert space.meld("ConfigurableService", override={"value": 5}).value == 5
            assert door_calls[0] == entered
            before = dict(space._meld._fast_input_doors)
            assert space.meld(spell=ConfigurableService()).value == 0
            assert door_calls[0] == entered + 1
            assert dict(space._meld._fast_input_doors) == before
    finally:
        conduit.permanent_cleanup()


def test_input_registry_is_deleted_with_the_meld_door() -> None:
    """
    Purpose:
        Verify the name/class registry dies with the meld door.
    Contract:
        - `Meld.cleanup()` deletes `_fast_input_doors`, releasing the spell and context references
          the entries held.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=PerConduitService, existence=Existence.unique_per_conduit)
    conduit = spellbook.conjure(name="root")
    meld = conduit._meld
    conduit.meld("PerConduitService")
    assert "PerConduitService" in meld._fast_input_doors
    conduit.permanent_cleanup()
    with pytest.raises(AttributeError):
        meld._fast_input_doors
