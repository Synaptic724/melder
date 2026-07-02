"""
Component tests for generalized singleton warm-tail specialization.

Purpose:
    Prove the config-gated specializer stage (patch lane
    generalized_singleton_specialization_2026_07_01) on SMALL REAL GRAPHS:
    wrapper install and slot swap, decline rules, flag-OFF equivalence,
    ON-vs-OFF differential semantics, constructor-error parity through the
    specialized body, and epoch-bump deopt semantics.

Contract map (what each test pins):
    - Install: flag ON + a "many" root over `unique` deps ends with the
      published context slot serving a door whose bound inner executor is the
      SPECIALIZED emitter output, and the slot settles (self-replacing swap
      happens exactly once).
    - Decline: zero-capture graphs and root-only-capture graphs on
      short-circuiting routes never serve a specialized inner.
    - Differential: identical workloads produce identical identity semantics,
      registration behavior, and errors in both flag postures.
    - Deopt: bumping one captured dep's `_door_epoch` preserves semantics and
      does not un-swap the specialized door (deopt is a per-call tail-call).

These tests require the 3.14t runtime (full melder package import).
"""

import sys


def _ensure_project_root_on_path() -> None:
    """
    Purpose:
        Make `tests.*` support imports resolve under plain CLI pytest runs.
    Contract:
        - Mirrors the efficacy probe's preamble: the suite-level conftest adds
          only `src/` to sys.path, so repo-root CLI execution needs "." added
          before the `tests._frame_posture_test_support` import resolves.
        - No-op when the project root is already importable (PyCharm runs).
    Returns:
        None.
    """
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_project_root_on_path()

from types import FunctionType
from typing import Dict, List, Optional, Tuple

import pytest
from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    SPECIALIZED_EXECUTOR_NAME,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_specialization() -> None:
    """
    Purpose:
        Ensure specialization component tests start with a clean Aether singleton.
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


def _reset_runtime() -> None:
    """
    Purpose:
        Reset the Aether singleton mid-test for sequential dual-posture runs.
    Contract:
        - Mirrors the autouse fixture's rebinding so a second Spellbook can be
          built inside one test after the first posture's runtime is torn down.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    fresh_aether = Aether()
    Spellbook._aether = fresh_aether
    Conduit._aether = fresh_aether


def _make_spellbook(specialization_enabled: bool) -> Spellbook:
    """
    Purpose:
        Provide a non-dynamic Spellbook with the specialization flag set.
    Contract:
        - Non-dynamic posture (the generalized family's production posture here).
        - phase_scheduler_workers_per_spellbook is 1 for determinism.
        - The flag is set BEFORE Spellbook construction; the hydrator reads it
          once at hydration time, so pre-construction set is the supported path.
    Args:
        specialization_enabled: Desired flag posture for this runtime.
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
    configuration.set_property(
        "generalized_singleton_specialization_enabled",
        specialization_enabled,
    )
    return Spellbook(configuration=configuration)


def _door_binds_executor_named(door: object, executor_name: str) -> bool:
    """
    Purpose:
        Detect which inner executor a published context door is bound to.
    Contract:
        - Route doors are template-factory outputs that bind their inner
          executor through default parameters (and wrapper shims through
          closure cells); this scans defaults, kwdefaults, and closure cells
          one level deep for a function named `executor_name`.
        - This introspection pins the patch's INSTALL contract (the slot must
          serve the specialized emitter output); it is not a behavior probe.
    Args:
        door: The published `_no_overrides_executor` slot value.
        executor_name: Emitter-assigned inner executor __name__ to look for.
    Returns:
        bool: True when the door binds an inner function with that name.
    """
    candidates: List[object] = list(getattr(door, "__defaults__", None) or ())
    kwdefaults = getattr(door, "__kwdefaults__", None)
    if kwdefaults:
        candidates.extend(kwdefaults.values())
    closure = getattr(door, "__closure__", None)
    if closure:
        for cell in closure:
            candidates.append(cell.cell_contents)
    return any(
        isinstance(value, FunctionType) and value.__name__ == executor_name
        for value in candidates
    )


class _UniqueDepOne:
    """
    Purpose:
        `unique` dependency (capture target) with an identity marker.
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


class _UniqueDepTwo:
    """
    Purpose:
        Second `unique` dependency (capture target) with an identity marker.
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


class _ManyRootOverUniques:
    """
    Purpose:
        `many` root over two `unique` deps - the canonical capture graph.
    Contract:
        - Route "many" always enters the inner executor, so this root's
          published door is the specialization surface under test.
    """

    def __init__(self, u1: _UniqueDepOne, u2: _UniqueDepTwo) -> None:
        """
        Purpose:
            Record injected deps for identity-threading assertions.
        Contract:
            - u1/u2 are stored unmodified.
        Args:
            u1: Shared unique dependency one.
            u2: Shared unique dependency two.
        Returns:
            None.
        """
        self.u1 = u1
        self.u2 = u2


class _PerConduitDep:
    """
    Purpose:
        `unique_per_conduit` dependency for the zero-capture graph.
    Contract:
        - Caller-varying store: NEVER capturable by the specializer.
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


class _ManyLeafDep:
    """
    Purpose:
        `many` leaf dependency (transient; never capturable).
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


class _ZeroCaptureRoot:
    """
    Purpose:
        `many` root whose deps contain NO `unique` rows (zero capture set).
    Contract:
        - The specializer must return the plain hot door unchanged for this
          graph (wrapper never installed).
    """

    def __init__(self, scoped: _PerConduitDep, leaf: _ManyLeafDep) -> None:
        """
        Purpose:
            Record injected deps for identity assertions.
        Contract:
            - scoped/leaf are stored unmodified.
        Args:
            scoped: Per-conduit dependency.
            leaf: Transient many dependency.
        Returns:
            None.
        """
        self.scoped = scoped
        self.leaf = leaf


class _UniqueRootOverMany:
    """
    Purpose:
        `unique` root over a `many` dep - root-only capture on a
        short-circuiting route.
    Contract:
        - The `unique` route door serves warm root hits from live storage
          BEFORE the inner executor runs, so a root-only specialized body is
          dead code; the specializer must decline it.
    """

    def __init__(self, leaf: _ManyLeafDep) -> None:
        """
        Purpose:
            Record the injected dep.
        Contract:
            - leaf is stored unmodified.
        Args:
            leaf: Transient many dependency.
        Returns:
            None.
        """
        self.leaf = leaf


class _FlakyRoot:
    """
    Purpose:
        `many` root whose constructor raises on demand AFTER specialization
        has installed, exercising the specialized body's error path.
    Contract:
        - `explode` is a class-level toggle: False constructs normally, True
          raises ValueError with a stable message.
        - Toggle state is test-managed and reset by the owning test.
    """

    explode: bool = False

    def __init__(self, u1: _UniqueDepOne) -> None:
        """
        Purpose:
            Construct normally or raise per the class toggle.
        Contract:
            - Raises ValueError("flaky root boom") when `explode` is True.
        Args:
            u1: Shared unique dependency.
        Raises:
            ValueError: When the class-level explode toggle is set.
        Returns:
            None.
        """
        if _FlakyRoot.explode:
            raise ValueError("flaky root boom")
        self.u1 = u1


def _bind_capture_graph(spellbook: Spellbook) -> Dict[str, str]:
    """
    Purpose:
        Bind the canonical capture graph (many root over two unique deps).
    Contract:
        - Mixed existences across >1 spell route the root to the generalized
          family with a non-empty `unique` capture set.
    Args:
        spellbook: Target spellbook.
    Returns:
        Dict[str, str]: name -> spell_id map for u1, u2, and root.
    """
    return {
        "u1": spellbook.bind(
            spell=_UniqueDepOne,
            existence=Existence.unique,
            permissions="create",
        ),
        "u2": spellbook.bind(
            spell=_UniqueDepTwo,
            existence=Existence.unique,
            permissions="create",
        ),
        "root": spellbook.bind(
            spell=_ManyRootOverUniques,
            existence=Existence.many,
            permissions="create",
        ),
    }


def _settled_root_slot(
        spellbook: Spellbook,
        conduit: Conduit,
        root_id: str,
) -> Tuple[object, object]:
    """
    Purpose:
        Warm one root and return its SETTLED published door slot.
    Contract:
        - Melds the root three times (cold hydrate + wrapper leader pass +
          margin), reads the slot, then proves stability across two more warm
          melds - the self-replacing swap must have happened at most once.
    Args:
        spellbook: Owning spellbook.
        conduit: Melding conduit.
        root_id: Root spell id to warm.
    Returns:
        Tuple[object, object]: (creation_context, settled slot value).
    """
    for _ in range(3):
        assert conduit.meld(spell=root_id) is not None
    spell = spellbook._spell_id_pool[root_id]
    context = spell._creation_context
    assert context is not None, "root context missing after warm melds"
    settled = context._no_overrides_executor
    for _ in range(2):
        conduit.meld(spell=root_id)
    assert context._no_overrides_executor is settled, (
        "published door slot did not settle after specialization window"
    )
    return context, settled


def test_component_specialization_flag_on_installs_specialized_door() -> None:
    """
    Purpose:
        Verify flag-ON capture graphs end with the specialized door published.
    Contract:
        - After warm melds the settled `_no_overrides_executor` slot binds an
          inner executor named SPECIALIZED_EXECUTOR_NAME (install + slot swap).
        - Reuse semantics hold: many root fresh per call; unique deps identity
          stable and threaded into every root construction.
    """
    spellbook = _make_spellbook(specialization_enabled=True)
    ids = _bind_capture_graph(spellbook)
    conduit = spellbook.conjure(name="root")
    try:
        _, settled = _settled_root_slot(spellbook, conduit, ids["root"])
        assert _door_binds_executor_named(settled, SPECIALIZED_EXECUTOR_NAME), (
            "flag-ON capture graph did not publish the specialized door"
        )
        first = conduit.meld(spell=ids["root"])
        second = conduit.meld(spell=ids["root"])
        assert second is not first
        assert second.u1 is first.u1
        assert second.u2 is first.u2
        assert conduit.meld(spell=ids["u1"]) is first.u1
    finally:
        conduit.permanent_cleanup()


def test_component_specialization_flag_off_keeps_generic_door() -> None:
    """
    Purpose:
        Verify the default OFF posture never publishes a specialized door.
    Contract:
        - Same capture graph, flag OFF: the settled slot binds NO inner named
          SPECIALIZED_EXECUTOR_NAME, and semantics match the ON posture.
    """
    spellbook = _make_spellbook(specialization_enabled=False)
    ids = _bind_capture_graph(spellbook)
    conduit = spellbook.conjure(name="root")
    try:
        _, settled = _settled_root_slot(spellbook, conduit, ids["root"])
        assert not _door_binds_executor_named(
            settled, SPECIALIZED_EXECUTOR_NAME
        ), "flag OFF must never publish a specialized door"
        first = conduit.meld(spell=ids["root"])
        second = conduit.meld(spell=ids["root"])
        assert second is not first
        assert second.u1 is first.u1
    finally:
        conduit.permanent_cleanup()


def test_component_specialization_declines_zero_capture_graph() -> None:
    """
    Purpose:
        Verify graphs with no `unique` rows never install the wrapper.
    Contract:
        - Flag ON + a many root over {unique_per_conduit, many} deps: the
          settled slot binds no specialized inner, and scoped-reuse semantics
          hold (per-conduit dep cached per scope, many leaf fresh per call).
    """
    spellbook = _make_spellbook(specialization_enabled=True)
    scoped_id = spellbook.bind(
        spell=_PerConduitDep,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    spellbook.bind(
        spell=_ManyLeafDep,
        existence=Existence.many,
        permissions="create",
    )
    root_id = spellbook.bind(
        spell=_ZeroCaptureRoot,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        _, settled = _settled_root_slot(spellbook, conduit, root_id)
        assert not _door_binds_executor_named(
            settled, SPECIALIZED_EXECUTOR_NAME
        ), "zero-capture graph must decline specialization"
        first = conduit.meld(spell=root_id)
        second = conduit.meld(spell=root_id)
        assert second is not first
        assert second.scoped is first.scoped
        assert second.leaf is not first.leaf
        assert conduit.meld(spell=scoped_id) is first.scoped
    finally:
        conduit.permanent_cleanup()


def test_component_specialization_declines_root_only_capture_route() -> None:
    """
    Purpose:
        Verify root-only capture on a short-circuiting route is declined.
    Contract:
        - Flag ON + a `unique` root over a `many` dep: the only capturable row
          is the root, and the `unique` route door short-circuits warm root
          hits before the inner executor, so the specializer must return the
          plain door (no specialized inner ever published).
        - Root identity stays stable across warm melds (door short-circuit).
    """
    spellbook = _make_spellbook(specialization_enabled=True)
    spellbook.bind(
        spell=_ManyLeafDep,
        existence=Existence.many,
        permissions="create",
    )
    root_id = spellbook.bind(
        spell=_UniqueRootOverMany,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        _, settled = _settled_root_slot(spellbook, conduit, root_id)
        assert not _door_binds_executor_named(
            settled, SPECIALIZED_EXECUTOR_NAME
        ), "root-only capture on a short-circuit route must decline"
        first = conduit.meld(spell=root_id)
        assert conduit.meld(spell=root_id) is first
    finally:
        conduit.permanent_cleanup()


def _collect_differential_facts(
        specialization_enabled: bool,
) -> Dict[str, object]:
    """
    Purpose:
        Run one identical workload under one flag posture and record facts.
    Contract:
        - Builds a fresh runtime, runs the capture graph plus a per-conduit
          scope check, and returns observable facts for cross-posture
          comparison; tears the runtime down and resets the singleton.
    Args:
        specialization_enabled: Flag posture for this run.
    Returns:
        Dict[str, object]: Fact map (identity booleans and frame-global reuse).
    """
    _reset_runtime()
    spellbook = _make_spellbook(specialization_enabled=specialization_enabled)
    ids = _bind_capture_graph(spellbook)
    scoped_id = spellbook.bind(
        spell=_PerConduitDep,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        root_a = conduit.meld(spell=ids["root"])
        root_b = conduit.meld(spell=ids["root"])
        u1_live = conduit.meld(spell=ids["u1"])
        lesser_one = conduit.create_lesser_conduit()
        try:
            scoped_a = lesser_one.meld(spell=scoped_id)
            scoped_b = lesser_one.meld(spell=scoped_id)
            u1_from_lesser = lesser_one.meld(spell=ids["u1"])
        finally:
            lesser_one.cleanup()
        lesser_two = conduit.create_lesser_conduit()
        try:
            scoped_c = lesser_two.meld(spell=scoped_id)
        finally:
            lesser_two.cleanup()
        return {
            "many_fresh": root_a is not root_b,
            "dep_threaded": root_a.u1 is root_b.u1 is u1_live,
            "dep2_threaded": root_a.u2 is root_b.u2,
            "scoped_cached": scoped_a is scoped_b,
            "scoped_isolated": scoped_c is not scoped_a,
            "unique_frame_global": u1_from_lesser is u1_live,
        }
    finally:
        try:
            conduit.permanent_cleanup()
        finally:
            try:
                spellbook.cleanup()
            finally:
                _reset_runtime()


def test_component_specialization_differential_flag_on_matches_off() -> None:
    """
    Purpose:
        Verify the ON posture is observationally equivalent to OFF.
    Contract:
        - Every recorded identity/registration fact must be True in BOTH
          postures and the fact maps must be equal: instance identity,
          dependency threading, scoped caching/isolation, and frame-global
          unique registration all survive specialization unchanged.
    """
    facts_off = _collect_differential_facts(specialization_enabled=False)
    facts_on = _collect_differential_facts(specialization_enabled=True)
    assert facts_off == facts_on, (
        f"posture divergence: OFF={facts_off} ON={facts_on}"
    )
    assert all(facts_off.values()), f"OFF posture violated semantics: {facts_off}"


def _collect_error_parity_facts(
        specialization_enabled: bool,
) -> Tuple[str, str]:
    """
    Purpose:
        Drive a constructor failure THROUGH the settled warm door and record
        the raised exception's type and message.
    Contract:
        - The flaky root succeeds first (letting flag-ON specialization
          install), then the class toggle makes its constructor raise; the
          raised exception surfaces through whichever body is published.
        - The toggle is always reset, and the runtime is torn down.
    Args:
        specialization_enabled: Flag posture for this run.
    Returns:
        Tuple[str, str]: (exception type qualname, exception message).
    """
    _reset_runtime()
    spellbook = _make_spellbook(specialization_enabled=specialization_enabled)
    spellbook.bind(
        spell=_UniqueDepOne,
        existence=Existence.unique,
        permissions="create",
    )
    flaky_id = spellbook.bind(
        spell=_FlakyRoot,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        for _ in range(3):
            assert conduit.meld(spell=flaky_id) is not None
        _FlakyRoot.explode = True
        try:
            with pytest.raises(Exception) as exc_info:
                conduit.meld(spell=flaky_id)
        finally:
            _FlakyRoot.explode = False
        assert conduit.meld(spell=flaky_id) is not None
        return type(exc_info.value).__qualname__, str(exc_info.value)
    finally:
        try:
            conduit.permanent_cleanup()
        finally:
            try:
                spellbook.cleanup()
            finally:
                _reset_runtime()


def test_component_specialization_constructor_error_parity() -> None:
    """
    Purpose:
        Verify constructor failures raise identically in both postures.
    Contract:
        - The specialized body's per-step error handling must surface the
          same exception type and message as the generic body, and the lane
          must recover (a later meld succeeds) in both postures.
    """
    off_type, off_message = _collect_error_parity_facts(
        specialization_enabled=False,
    )
    on_type, on_message = _collect_error_parity_facts(
        specialization_enabled=True,
    )
    assert on_type == off_type, (
        f"error type diverged: OFF={off_type} ON={on_type}"
    )
    assert on_message == off_message, (
        f"error message diverged: OFF={off_message!r} ON={on_message!r}"
    )
    assert "flaky root boom" in on_message


def test_component_specialization_deopt_epoch_bump_keeps_semantics() -> None:
    """
    Purpose:
        Verify guard-miss deopt: a captured dep's epoch bump degrades to the
        generic inner without changing results or un-swapping the door.
    Contract:
        - After specialization installs, bumping one captured dep's
          `_door_epoch` makes every specialized-body guard pass fail; melds
          must keep returning fresh roots threaded with the LIVE unique dep.
        - The published slot is untouched by deopt (per-call tail-call, not a
          de-install), so the same specialized door keeps serving.
    """
    spellbook = _make_spellbook(specialization_enabled=True)
    ids = _bind_capture_graph(spellbook)
    conduit = spellbook.conjure(name="root")
    try:
        context, settled = _settled_root_slot(spellbook, conduit, ids["root"])
        assert _door_binds_executor_named(settled, SPECIALIZED_EXECUTOR_NAME)
        live_u1 = conduit.meld(spell=ids["u1"])
        spellbook._spell_id_pool[ids["u1"]]._door_epoch += 1
        deopt_a = conduit.meld(spell=ids["root"])
        deopt_b = conduit.meld(spell=ids["root"])
        assert deopt_a is not deopt_b
        assert deopt_a.u1 is live_u1
        assert deopt_b.u1 is live_u1
        assert context._no_overrides_executor is settled, (
            "deopt must not un-swap the specialized door"
        )
    finally:
        conduit.permanent_cleanup()
