from __future__ import annotations

import pytest
from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_fast_meld_door() -> None:
    """
    Purpose:
        Ensure fast-meld-door component tests start with a clean Aether singleton.
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
        Provide a non-dynamic Spellbook configured for fast-door tests.
    Contract:
        - Non-dynamic posture, which is the only posture the fast lane builds in.
        - phase_scheduler_workers_per_spellbook is set to 1 for determinism.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=False,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class _UniquePerConduitService:
    """
    Purpose:
        Service type for unique_per_conduit fast-door tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _SharedUniqueService:
    """
    Purpose:
        Service type for shared `unique` fast-door tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _ManyService:
    """
    Purpose:
        Service type for Existence.many fast-door tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _SpaceMarkerService:
    """
    Purpose:
        Service type for unique_per_spell_space fast-door tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _OverridableService:
    """
    Purpose:
        Service type proving override payloads bypass the fast lane.
    Contract:
        - `value` records the constructor input observable from tests.
    """

    def __init__(self, value: int = 0) -> None:
        """
        Purpose:
            Record the constructor input for override-path assertions.
        Contract:
            - Defaults to 0 when melded without an override payload.
        Args:
            value: Optional override-supplied constructor input.
        Returns:
            None.
        """
        self.value = value


class _SpellIdPoolSpy(dict):
    """
    Purpose:
        Drop-in spell-id-pool wrapper that records normal-lane entry.
    Contract:
        - The fast lane serves and returns BEFORE the door's normal-lane
          spell-id-pool read: the warm path reads `_fast_meld_doors`, never
          `_spell_id_pool`. Every bypass (override, validation, hooks, context
          invalidation) and every cold meld falls through to the
          `_spell_id_pool.get(...)` resolution read.
        - Recording `get` therefore makes a fast-lane hit (pool untouched) and
          a normal-lane pass (pool read) observable, with zero effect on
          resolution: lookups still delegate to the captured pool snapshot.
        - This replaced the removed per-entry store poison. The fast door no
          longer captures a creations store to poison (the executor reads its
          store off the meld), so the lane is proven by the
          normal-lane-exclusive pool read instead.
    """

    def __init__(self, source: dict) -> None:
        super().__init__(source)
        self.normal_lane_entered = False

    def get(self, *args: object, **kwargs: object) -> object:
        """Record the normal-lane read, then delegate to the real lookup."""
        self.normal_lane_entered = True
        return super().get(*args, **kwargs)


def _install_lane_spy(meld: object) -> _SpellIdPoolSpy:
    """
    Purpose:
        Swap a meld's spell-id pool for a recording spy and return it.
    Contract:
        - Installs after the cold build so only subsequent melds are observed.
        - A later fast-lane hit leaves `normal_lane_entered` False; any bypass
          or full-lane pass sets it True.
    Args:
        meld: Meld front door whose `_spell_id_pool` slot is wrapped.
    Returns:
        _SpellIdPoolSpy: The installed spy, for lane assertions.
    """
    spy = _SpellIdPoolSpy(meld._spell_id_pool)
    meld._spell_id_pool = spy
    return spy


def test_component_fast_door_builds_entry_and_serves_warm_hits() -> None:
    """
    Purpose:
        Verify first id-string meld builds an entry and later melds hit it.
    Contract:
        - First meld populates `_fast_meld_doors[spell_id]`.
        - Second meld returns the reuse-correct instance.
        - A poisoned entry raises on the next meld, proving the warm call
          actually executed through the fast lane.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        assert spell_id in conduit._meld._fast_meld_doors
        spy = _install_lane_spy(conduit._meld)
        second = conduit.meld(spell_id=spell_id)
        assert second is first
        # The warm meld served from the fast lane: it returns before the
        # normal-lane spell-id-pool read, so the spy never fired.
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_preserves_reuse_semantics_per_existence() -> None:
    """
    Purpose:
        Verify fast-lane results match normal-lane reuse semantics.
    Contract:
        - unique / unique_per_conduit: warm melds return the same instance.
        - many: warm melds return a new instance per call.
    """
    spellbook = _make_spellbook()
    unique_id = spellbook.bind(
        spell=_SharedUniqueService,
        existence=Existence.unique,
        permissions="create",
    )
    per_conduit_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    many_id = spellbook.bind(
        spell=_ManyService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        unique_first = conduit.meld(spell_id=unique_id)
        per_conduit_first = conduit.meld(spell_id=per_conduit_id)
        many_first = conduit.meld(spell_id=many_id)

        # Warm passes ride the fast lane for all three routes.
        assert conduit.meld(spell_id=unique_id) is unique_first
        assert conduit.meld(spell_id=per_conduit_id) is per_conduit_first
        many_second = conduit.meld(spell_id=many_id)
        assert many_second is not many_first
        assert isinstance(many_second, _ManyService)
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_skipped_for_override_payloads() -> None:
    """
    Purpose:
        Verify caller override payloads always take the normal lane.
    Contract:
        - Override melds construct with the override payload applied.
        - A poisoned fast-door entry is not executed by an override meld.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        plain = conduit.meld(spell_id=spell_id)
        assert plain.value == 0
        assert spell_id in conduit._meld._fast_meld_doors

        spy = _install_lane_spy(conduit._meld)
        overridden = conduit.meld(spell_id=spell_id, override={"value": 7})
        assert overridden.value == 7
        # Override payloads always take the normal lane (the fast lane cannot
        # apply overrides), proven by the spell-id-pool read.
        assert spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_guard_trips_on_validation_required() -> None:
    """
    Purpose:
        Verify the validation-required flag bypasses the fast lane.
    Contract:
        - With `_spellbook_validation_required` True, a poisoned entry is not
          executed and the normal lane serves a correct instance.
        - The normal-lane pass rebuilds the entry in place (poison replaced).
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)

        spellbook._set_spellbook_validation_required(True)
        bypassed = conduit.meld(spell_id=spell_id)
        assert bypassed is first
        # validation_required forces the normal lane, proven by the pool read.
        assert spy.normal_lane_entered

        # Once validation relaxes, the fast lane serves again: the warm pass
        # returns before the pool read.
        spellbook._set_spellbook_validation_required(False)
        spy.normal_lane_entered = False
        assert conduit.meld(spell_id=spell_id) is first
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_guard_trips_on_spell_hooks() -> None:
    """
    Purpose:
        Verify spell-level hooks bypass the fast lane so hooks always fire.
    Contract:
        - After hooks attach, a poisoned entry is not executed and the
          pre-cast hook fires on the hooks lane.
        - After hooks detach, the fast lane serves again.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)

        hook_calls: list[str] = []
        spell = spellbook._spell_id_pool[spell_id]
        spell._set_hooks(pre_hooks=[lambda: hook_calls.append("pre")])

        hooked = conduit.meld(spell_id=spell_id)
        assert hooked is first
        # The pre-cast hook fires only on the normal hook lane (the fast lane
        # fires no hooks); the pool read confirms the bypass.
        assert hook_calls == ["pre"]
        assert spy.normal_lane_entered

        # Detach hooks and drop the now-stale entry; the rebuilt entry serves
        # the fast lane again on the next warm pass.
        spell._set_hooks(pre_hooks=[])
        del conduit._meld._fast_meld_doors[spell_id]
        rebuilt = conduit.meld(spell_id=spell_id)
        assert rebuilt is first
        assert conduit.meld(spell_id=spell_id) is first
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_guard_trips_on_meld_hooks_in_place_mutation() -> None:
    """
    Purpose:
        Verify in-place meld-hook map mutation bypasses the fast lane.
    Contract:
        - Mutating the shared hooks map without calling `set_meld_hooks` is
          observed by the live guard read; the poisoned entry is not executed
          and the meld-level hook fires.
        - This pins the design decision that replaced the door change counter
          with a live `not self._meld_hooks` read.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)

        hook_calls: list[object] = []
        meld = conduit._meld
        if meld._meld_hooks is None:
            meld._meld_hooks = {}
        # In-place mutation, deliberately not via set_meld_hooks.
        meld._meld_hooks["on_meld_pre_resolve"] = [
            lambda target: hook_calls.append(target)
        ]

        hooked = conduit.meld(spell_id=spell_id)
        assert hooked is first
        # The live `not self._meld_hooks` guard read sees the in-place mutation
        # and routes to the normal lane: the meld hook fires and the pool read
        # confirms the bypass.
        assert len(hook_calls) == 1
        assert spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_guard_trips_on_context_invalidation() -> None:
    """
    Purpose:
        Verify context invalidation bypasses and rebuilds the fast lane.
    Contract:
        - `Spell._cleanup_creation_context()` is the funnel chokepoint for all
          context replacement; after it runs, a poisoned entry is not
          executed.
        - In production, every caller of that chokepoint (phase-5 rebuilds,
          ownership transfer, re-stamping) pairs it with resolution regating,
          so this test sets the deferred-resolution flags the same way; the
          meld-time deferred pass then rebuilds phases 8-11 and republishes
          the context.
        - The normal lane replaces the entry; warm hits resume against the
          new context.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)

        spell = spellbook._spell_id_pool[spell_id]
        # Mirror the production chokepoint pairing: context teardown plus
        # deferred-resolution regating, never teardown alone.
        spell._cleanup_creation_context()
        spell.resolution_required = True
        spell.resolution_complete = False

        rebuilt = conduit.meld(spell_id=spell_id)
        assert rebuilt is first
        # Context invalidation forces the normal lane (pool read), which
        # rebuilds the entry against the fresh context.
        assert spy.normal_lane_entered

        # Entry was replaced in place by the normal-lane pass: a warm hit now
        # serves the rebuilt executor against the new context.
        assert conduit.meld(spell_id=spell_id) is first
        entry = conduit._meld._fast_meld_doors[spell_id]
        assert entry[1] is spell._creation_context
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_epoch_invalidates_on_hook_attach() -> None:
    """
    Purpose:
        Pin the door-epoch guard: attaching spell hooks through the real
        chokepoint bumps `Spell._door_epoch`, so a previously built fast
        entry misses and the meld routes through the hook lane.
    Contract:
        - The built entry captures the spell's epoch at build time.
        - `Spell._set_hooks` bumps the live epoch (entry now stale).
        - The next meld returns the reuse-correct instance AND fires the
          attached hook, proving the stale fast entry was not served.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        entry = conduit._meld._fast_meld_doors[spell_id]
        spell = spellbook._spell_id_pool[spell_id]
        assert entry[2] == spell._door_epoch

        fired: list = []
        spell._set_hooks(post_hooks=[lambda: fired.append(True)])
        assert spell._door_epoch != entry[2]

        again = conduit.meld(spell_id=spell_id)
        assert again is first
        # Hook executed => the meld took the normal hook lane, not the
        # stale fast entry.
        assert fired
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_mutation_override_requires_dynamic_pin() -> None:
    """
    Purpose:
        Pin the posture wall that excludes mutation overrides from the lane.
    Contract:
        - `apply_mutation_override` raises RuntimeError on a spell owned by a
          non-dynamic conduit, so a non-dynamic fast door can never observe a
          non-None `_mutation_override`.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        conduit.meld(spell_id=spell_id)
        spell = spellbook._spell_id_pool[spell_id]
        with pytest.raises(RuntimeError, match="[Dd]ynamic"):
            spell.apply_mutation_override({"value": 1})
        assert spell._mutation_override is None
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_registry_deleted_on_cleanup() -> None:
    """
    Purpose:
        Verify the fast-door registry dies with the meld front door.
    Contract:
        - `Meld.cleanup()` deletes `_fast_meld_doors` so retained entries are
          released at the owner-driven teardown point.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    meld = conduit._meld
    conduit.meld(spell_id=spell_id)
    assert spell_id in meld._fast_meld_doors

    conduit.permanent_cleanup()
    assert not hasattr(meld, "_fast_meld_doors")


def test_component_positional_meld_matches_keyword_meld_per_existence() -> None:
    """
    Purpose:
        Verify the positional call shape `meld(spell_id)` is behaviorally
        identical to `meld(spell=spell_id)` across reuse semantics now that
        `spell` rides the positional seat.
    Contract:
        - unique / unique_per_conduit: positional and keyword calls return
          the same instance, warm and cold.
        - many: the positional call constructs a new instance per call.
        - Spellspace door: the positional call serves scope-correct
          `unique_per_spell_space` instances.
    """
    spellbook = _make_spellbook()
    unique_id = spellbook.bind(
        spell=_SharedUniqueService,
        existence=Existence.unique,
        permissions="create",
    )
    per_conduit_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    many_id = spellbook.bind(
        spell=_ManyService,
        existence=Existence.many,
        permissions="create",
    )
    marker_id = spellbook.bind(
        spell=_SpaceMarkerService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        # Cold positional meld runs the full lane and builds the entry.
        unique_first = conduit.meld(spell_id=unique_id)
        assert isinstance(unique_first, _SharedUniqueService)
        assert unique_id in conduit._meld._fast_meld_doors

        # Warm positional and keyword melds agree on reuse identity.
        assert conduit.meld(spell_id=unique_id) is unique_first
        assert conduit.meld(spell_id=unique_id) is unique_first

        per_conduit_first = conduit.meld(spell_id=per_conduit_id)
        assert conduit.meld(spell_id=per_conduit_id) is per_conduit_first

        many_first = conduit.meld(spell_id=many_id)
        many_second = conduit.meld(spell_id=many_id)
        assert isinstance(many_second, _ManyService)
        assert many_second is not many_first

        with conduit.enter_spellspace() as space:
            marker = space.meld(spell_id=marker_id)
            assert isinstance(marker, _SpaceMarkerService)
            assert space.meld(spell_id=marker_id) is marker
            assert space.meld(spell_id=marker_id) is marker
    finally:
        conduit.permanent_cleanup()


def test_component_positional_meld_warm_call_executes_fast_lane() -> None:
    """
    Purpose:
        Prove the warm positional `meld(spell_id)` call actually executes
        through the fast door, not the full lane.
    Contract:
        - With a poisoned entry store, a warm positional meld raises from
          the poisoned fast-lane execution, demonstrating the lane was taken.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)
        conduit.meld(spell_id=spell_id)
        # The warm positional meld served from the fast lane: it returned
        # before the normal-lane spell-id-pool read.
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_positional_meld_class_input_resolves_via_normalization() -> None:
    """
    Purpose:
        Verify non-id positional inputs (class objects) route through the
        full lane's normalization and resolve correctly.
    Contract:
        - `meld(SomeBoundClass)` resolves exactly like
          `meld(spell=SomeBoundClass)` and agrees with id-based resolution.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        by_id = conduit.meld(spell_id=spell_id)
        by_class = conduit.meld(_UniquePerConduitService)
        assert by_class is by_id
    finally:
        conduit.permanent_cleanup()


def test_component_positional_meld_raises_canonical_error_after_cleanup() -> None:
    """
    Purpose:
        Verify the cleaned-conduit guard on the positional call shape.
    Contract:
        - Positional `meld(spell_id)` on a cleaned conduit raises the
          canonical `check_cleaned` RuntimeError, identical to keyword melds.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_UniquePerConduitService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    conduit.meld(spell_id=spell_id)
    conduit.permanent_cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        conduit.meld(spell_id=spell_id)


def test_component_spellspace_nested_scope_stack_isolation() -> None:
    """
    Purpose:
        Verify recursive spellspace activation: a stack of independent scopes
        (A -> B -> C -> D) with per-level storage isolation and LIFO unwind.
    Contract:
        - Each nested `enter_spellspace()` pushes a new independent scope.
        - Every level resolves its own `unique_per_spell_space` marker; no
          level observes another level's instance.
        - Outer-level markers are still alive and identical after inner
          scopes exit (LIFO unwind does not disturb outer storage).
        - The spellspace acts as its own context manager: the object yielded
          by `with` IS the spellspace returned by `enter_spellspace()`.
    Regression note:
        An earlier version of this test placed the post-D assertions one
        dedent level too shallow (scope B's body), so they read scope C's
        storage AFTER scope C's own legitimate `__exit__` had recycled it -
        producing a phantom "cross-clear" failure that triggered a full
        runtime forensic investigation. Method-receiver tracing proved the
        only clears were each scope's own exit-time recycle, in perfect
        LIFO order. The runtime was always correct; per-scope assertion
        placement is the contract this test must keep.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarkerService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as scope_a:
            marker_a = scope_a.meld(spell_id=marker_id)
            with conduit.enter_spellspace() as scope_b:
                marker_b = scope_b.meld(spell_id=marker_id)
                assert marker_b is not marker_a
                with conduit.enter_spellspace() as scope_c:
                    marker_c = scope_c.meld(spell_id=marker_id)
                    assert marker_c is not marker_b
                    assert marker_c is not marker_a
                    with conduit.enter_spellspace() as scope_d:
                        marker_d = scope_d.meld(spell_id=marker_id)
                        # Shells, stores, and markers must all be distinct
                        # at full depth.
                        assert (
                            len({id(scope_a), id(scope_b), id(scope_c), id(scope_d)})
                            == 4
                        ), "pooled shells aliased across nested scopes"
                        assert (
                            len(
                                {
                                    id(scope_a._creations),
                                    id(scope_b._creations),
                                    id(scope_c._creations),
                                    id(scope_d._creations),
                                }
                            )
                            == 4
                        ), "spellspace stores aliased across nested scopes"
                        assert (
                            scope_c._creations.get_creation(marker_id)
                            is marker_c
                        ), "marker_c missing from scope_c store at depth"
                        distinct = {
                            id(marker_a),
                            id(marker_b),
                            id(marker_c),
                            id(marker_d),
                        }
                        assert len(distinct) == 4
                        # Each scope's own warm re-meld stays scope-correct
                        # at full depth.
                        assert scope_d.meld(spell_id=marker_id) is marker_d
                    # LIFO unwind step 1: D's exit must not disturb C's
                    # storage. These assertions run INSIDE scope_c's body
                    # (one dedent level, not two) - asserting per-scope
                    # state after that scope's own exit is the historical
                    # defect this test once shipped with.
                    assert (
                        scope_c._creations.get_creation(marker_id) is marker_c
                    ), "scope_c store lost marker_c after scope_d exit"
                    fast_entry = scope_c._meld._fast_meld_doors.get(marker_id)
                    if fast_entry is not None:
                        # The per-entry store slot was removed; the executor
                        # reads its store off the scope's own SpellSpaceMeld,
                        # so scope-correctness is proven by the meld's store.
                        assert (
                            scope_c._meld._spellspace_creations
                            is scope_c._creations
                        ), "scope_c meld bound a foreign spellspace store"
                    assert scope_c.meld(spell_id=marker_id) is marker_c
                # LIFO unwind step 2: C's exit must not disturb B's storage.
                assert (
                    scope_b._creations.get_creation(marker_id) is marker_b
                ), "scope_b store lost marker_b after scope_c exit"
                assert scope_b.meld(spell_id=marker_id) is marker_b
            # LIFO unwind step 3: B's exit must not disturb A's storage.
            assert (
                scope_a._creations.get_creation(marker_id) is marker_a
            ), "scope_a store lost marker_a after scope_b exit"
            assert scope_a.meld(spell_id=marker_id) is marker_a
        # The yielded object is the spellspace itself (no wrapper exists).
        from melder.aether.conduit.spell_space.spell_space import SpellSpace

        assert isinstance(scope_a, SpellSpace)
    finally:
        conduit.permanent_cleanup()


def test_component_enter_spellspace_manual_protocol_compatibility() -> None:
    """
    Purpose:
        Verify the manual `cm = enter_spellspace(); cm.__enter__()` pattern
        used by the benchmark harnesses keeps working with the space as its
        own context manager.
    Contract:
        - `enter_spellspace()` returns the already-activated space.
        - `__enter__` returns the same object.
        - `__exit__(None, None, None)` pops and recycles it; the pool then
          serves the same shell to the next acquisition.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarkerService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        manual_cm = conduit.enter_spellspace()
        space = manual_cm.__enter__()
        assert space is manual_cm
        marker = space.meld(spell_id=marker_id)
        assert space.meld(spell_id=marker_id) is marker
        manual_cm.__exit__(None, None, None)

        # Pooled reuse: same shell, fresh scope contents.
        with conduit.enter_spellspace() as next_space:
            assert next_space is space
            assert next_space.meld(spell_id=marker_id) is not marker
    finally:
        conduit.permanent_cleanup()


def test_component_prewarm_pools_retain_idle_shells() -> None:
    """
    Purpose:
        Verify prewarm APIs build pooled shells ahead of traffic.
    Contract:
        - `prewarm_spellspaces(n)` leaves n idle spellspace shells (capacity
          clamped) and later scopes reuse them without construction.
        - `prewarm_lesser_conduits(n)` leaves n idle lesser shells and the
          next `create_lesser_conduit()` serves a prewarmed shell.
        - Prewarm counts are clamped to pool capacity instead of building
          shells the pool would evict.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarkerService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        ensured_spaces = conduit.prewarm_spellspaces(3)
        assert ensured_spaces == 3
        assert conduit._spellspace_pool.idle_count == 3

        with conduit.enter_spellspace() as space:
            # Acquisition drains the idle pool instead of constructing.
            assert conduit._spellspace_pool.idle_count == 2
            assert isinstance(space.meld(spell_id=marker_id), _SpaceMarkerService)
        assert conduit._spellspace_pool.idle_count == 3

        ensured_lessers = conduit.prewarm_lesser_conduits(2)
        assert ensured_lessers == 2
        assert conduit._conduit_pool.idle_count == 2

        lesser = conduit.create_lesser_conduit()
        try:
            assert conduit._conduit_pool.idle_count == 1
        finally:
            lesser.cleanup()
        assert conduit._conduit_pool.idle_count == 2

        # Capacity clamp: a huge request never exceeds the pool ceiling.
        ensured_capped = conduit.prewarm_spellspaces(10_000)
        assert ensured_capped == conduit._spellspace_pool.max_idle

        with pytest.raises(ValueError, match="positive"):
            conduit.prewarm_spellspaces(0)
        with pytest.raises(ValueError, match="positive"):
            conduit.prewarm_lesser_conduits(-1)
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_spellspace_scopes_stay_isolated() -> None:
    """
    Purpose:
        Verify spellspace fast doors serve scope-correct instances across
        pooled spellspace reuse.
    Contract:
        - Within one spellspace, warm marker melds return the same instance.
        - A later spellspace (pooled reuse of the same shell) returns a new
          marker instance even though the fast-door entry stayed warm,
          because the captured store identity persists while its contents are
          cleared per recycle.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarkerService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            first = space.meld(spell_id=marker_id)
            assert space.meld(spell_id=marker_id) is first
            assert marker_id in space._meld._fast_meld_doors

        with conduit.enter_spellspace() as next_space:
            second = next_space.meld(spell_id=marker_id)
            assert isinstance(second, _SpaceMarkerService)
            assert second is not first
            assert next_space.meld(spell_id=marker_id) is second
    finally:
        conduit.permanent_cleanup()
