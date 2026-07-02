"""
Deopt-matrix integration tests for generalized singleton specialization.

Purpose:
    Exercise the invalidation events the patch lane
    (generalized_singleton_specialization_2026_07_01) declares as deopt/
    rebuild surfaces - hook attach on a captured dep, creation-context
    rebuild (root and captured dep), ownership transfer, and concurrent
    melds through the specialization window - and prove the flag-ON posture
    is observationally identical to flag-OFF for every one of them.

Method:
    Each scenario runs twice on fresh runtimes (flag OFF, then flag ON) and
    returns a fact map of observable outcomes (identity relations, error
    types, hook fires). The test asserts the maps are EQUAL: the
    specialization stage may only change speed, never results ("wrong
    speculation is a slow path, never a wrong result").

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

import threading
from typing import Any, Callable, Dict, List, Tuple

import pytest
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    configure_frame_posture_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_specialization_deopt_matrix() -> None:
    """
    Purpose:
        Ensure deopt-matrix tests start and end on a clean Aether singleton.
    Contract:
        - Resets the singleton and rebinds Spellbook/Conduit._aether before
          and after each test.
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
        Reset the Aether singleton between the OFF and ON posture runs.
    Contract:
        - Mirrors the autouse fixture so each posture gets a fresh frame.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    fresh_aether = Aether()
    Spellbook._aether = fresh_aether
    Conduit._aether = fresh_aether


def _make_spellbook(*, specialization_enabled: bool, dynamic: bool) -> Spellbook:
    """
    Purpose:
        Build one Spellbook in either posture with the flag pre-set.
    Contract:
        - dynamic=False uses the standard component posture; dynamic=True uses
          the dynamic defaults required by transfer_spell_ownership.
        - The flag is set before construction (hydration-time read).
    Args:
        specialization_enabled: Flag posture for this runtime.
        dynamic: Frame/conduit posture selector.
    Returns:
        Spellbook: Configured spellbook.
    """
    configuration = SpellbookConfiguration()
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
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


class _UniqueDep:
    """
    Purpose:
        `unique` capture-target dependency with an identity marker.
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


class _SecondUniqueDep:
    """
    Purpose:
        Second `unique` capture target so the capture set has width two.
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


class _ManyRoot:
    """
    Purpose:
        `many` root over both unique deps (specialization surface).
    Contract:
        - Route "many" always enters the inner executor body.
    """

    def __init__(self, u1: _UniqueDep, u2: _SecondUniqueDep) -> None:
        """
        Purpose:
            Record injected deps for identity-threading assertions.
        Contract:
            - u1/u2 are stored unmodified.
        Args:
            u1: First captured dependency.
            u2: Second captured dependency.
        Returns:
            None.
        """
        self.u1 = u1
        self.u2 = u2


def _bind_graph(spellbook: Spellbook) -> Dict[str, str]:
    """
    Purpose:
        Bind the canonical capture graph into one spellbook.
    Contract:
        - Mixed existences route the root to the generalized family with a
          two-step `unique` capture set.
    Args:
        spellbook: Target spellbook.
    Returns:
        Dict[str, str]: name -> spell_id map.
    """
    return {
        "u1": spellbook.bind(
            spell=_UniqueDep,
            existence=Existence.unique,
            permissions="create",
        ),
        "u2": spellbook.bind(
            spell=_SecondUniqueDep,
            existence=Existence.unique,
            permissions="create",
        ),
        "root": spellbook.bind(
            spell=_ManyRoot,
            existence=Existence.many,
            permissions="create",
        ),
    }


def _run_posture(
        scenario: Callable[[Spellbook, Conduit, Dict[str, str]], Dict[str, object]],
        *,
        specialization_enabled: bool,
        dynamic: bool = False,
) -> Dict[str, object]:
    """
    Purpose:
        Run one scenario on a fresh runtime under one flag posture.
    Contract:
        - Builds spellbook + conduit, warms the root so flag-ON runtimes pass
          through the specialization window BEFORE the scenario's invalidation
          event fires, runs the scenario, and tears everything down.
    Args:
        scenario: Callable receiving (spellbook, conduit, ids) and returning
            the scenario's observable fact map.
        specialization_enabled: Flag posture.
        dynamic: Conduit posture (transfer scenarios need True).
    Returns:
        Dict[str, object]: The scenario's fact map.
    """
    _reset_runtime()
    spellbook = _make_spellbook(
        specialization_enabled=specialization_enabled,
        dynamic=dynamic,
    )
    ids = _bind_graph(spellbook)
    conduit = spellbook.conjure(name="root", dynamic=dynamic)
    try:
        for _ in range(3):
            assert conduit.meld(spell=ids["root"]) is not None
        return scenario(spellbook, conduit, ids)
    finally:
        try:
            conduit.permanent_cleanup()
        finally:
            try:
                spellbook.cleanup()
            finally:
                _reset_runtime()


def _assert_posture_parity(
        scenario: Callable[[Spellbook, Conduit, Dict[str, str]], Dict[str, object]],
        *,
        dynamic: bool = False,
) -> Dict[str, object]:
    """
    Purpose:
        Run one scenario in both postures and require identical fact maps.
    Contract:
        - Equality of the OFF and ON maps is THE specialization correctness
          contract: deopt paths may be slower, never observably different.
    Args:
        scenario: Scenario callable (see `_run_posture`).
        dynamic: Conduit posture for both runs.
    Returns:
        Dict[str, object]: The (shared) fact map for further assertions.
    """
    facts_off = _run_posture(
        scenario, specialization_enabled=False, dynamic=dynamic,
    )
    facts_on = _run_posture(
        scenario, specialization_enabled=True, dynamic=dynamic,
    )
    assert facts_off == facts_on, (
        f"posture divergence: OFF={facts_off} ON={facts_on}"
    )
    return facts_on


def test_integration_deopt_hook_attach_on_captured_dep() -> None:
    """
    Purpose:
        Hook attach on a captured dep (real epoch-bump chokepoint) must leave
        root results identical in both postures.
    Contract:
        - `Spell._set_hooks` bumps the dep's `_door_epoch`, so every later
          specialized-body guard pass deopts; roots must keep threading the
          LIVE dep instance, and direct dep melds must fire the hook.
    """
    def scenario(
            spellbook: Spellbook,
            conduit: Conduit,
            ids: Dict[str, str],
    ) -> Dict[str, object]:
        live_u1 = conduit.meld(spell=ids["u1"])
        fired: List[bool] = []
        spellbook._spell_id_pool[ids["u1"]]._set_hooks(
            post_hooks=[lambda: fired.append(True)],
        )
        root_a = conduit.meld(spell=ids["root"])
        root_b = conduit.meld(spell=ids["root"])
        direct_u1 = conduit.meld(spell=ids["u1"])
        return {
            "roots_fresh": root_a is not root_b,
            "dep_live_after_bump": root_a.u1 is live_u1 and root_b.u1 is live_u1,
            "direct_dep_identity": direct_u1 is live_u1,
            "hook_fired_on_direct_meld": bool(fired),
        }

    facts = _assert_posture_parity(scenario)
    assert facts["roots_fresh"] is True
    assert facts["dep_live_after_bump"] is True


def test_integration_deopt_context_rebuild_on_root() -> None:
    """
    Purpose:
        Rebuilding the ROOT's creation context (production chokepoint pairing)
        must re-hydrate cleanly and keep results identical in both postures.
    Contract:
        - `_cleanup_creation_context` + deferred-resolution regating mirrors
          every production caller; the next meld rebuilds phases 8-11 and
          republishes doors (flag-ON re-enters the specialization window).
    """
    def scenario(
            spellbook: Spellbook,
            conduit: Conduit,
            ids: Dict[str, str],
    ) -> Dict[str, object]:
        live_u1 = conduit.meld(spell=ids["u1"])
        root_spell = spellbook._spell_id_pool[ids["root"]]
        root_spell._cleanup_creation_context()
        root_spell.resolution_required = True
        root_spell.resolution_complete = False
        rebuilt_a = conduit.meld(spell=ids["root"])
        rebuilt_b = conduit.meld(spell=ids["root"])
        return {
            "rebuild_serves": rebuilt_a is not None and rebuilt_b is not None,
            "roots_fresh": rebuilt_a is not rebuilt_b,
            "dep_survives_rebuild": rebuilt_a.u1 is live_u1,
            "context_republished": root_spell._creation_context is not None,
        }

    facts = _assert_posture_parity(scenario)
    assert facts["dep_survives_rebuild"] is True


def test_integration_deopt_context_rebuild_on_captured_dep() -> None:
    """
    Purpose:
        Rebuilding a CAPTURED DEP's creation context must deopt the root body
        without changing results in either posture.
    Contract:
        - The dep's context teardown bumps its door epoch; captured guards
          fail from then on; the root keeps threading whatever instance the
          runtime currently serves for the dep.
    """
    def scenario(
            spellbook: Spellbook,
            conduit: Conduit,
            ids: Dict[str, str],
    ) -> Dict[str, object]:
        pre_u1 = conduit.meld(spell=ids["u1"])
        dep_spell = spellbook._spell_id_pool[ids["u1"]]
        dep_spell._cleanup_creation_context()
        dep_spell.resolution_required = True
        dep_spell.resolution_complete = False
        post_u1 = conduit.meld(spell=ids["u1"])
        root_after = conduit.meld(spell=ids["root"])
        return {
            "dep_identity_stable": post_u1 is pre_u1,
            "root_threads_current_dep": root_after.u1 is post_u1,
            "root_serves": root_after is not None,
        }

    facts = _assert_posture_parity(scenario)
    assert facts["root_threads_current_dep"] is True


def test_integration_deopt_transfer_spell_ownership_parity() -> None:
    """
    Purpose:
        Ownership transfer of a captured dep (dynamic mode) must produce
        identical observable outcomes in both postures.
    Contract:
        - Transfer routes through change-control dirty roots -> revalidation
          -> context rebuild -> epoch bump; whether the post-transfer source
          melds succeed or raise is a transfer-lane contract, NOT this
          patch's - this test only pins that specialization does not change
          that outcome in any way (result identities or error type).
    """
    def scenario(
            spellbook: Spellbook,
            conduit: Conduit,
            ids: Dict[str, str],
    ) -> Dict[str, object]:
        # Mirror the transfer-footprint convention: the target conduit
        # belongs to a SECOND spellbook (flag posture irrelevant: no binds).
        target_book = _make_spellbook(
            specialization_enabled=False,
            dynamic=True,
        )
        target = target_book.conjure(name="transfer-target", dynamic=True)
        facts: Dict[str, object] = {}
        try:
            conduit.transfer_spell_ownership(
                spell=ids["u1"],
                target_conduit=target,
            )
            try:
                root_after = conduit.meld(spell=ids["root"])
                dep_now = conduit.meld(spell=ids["u1"])
                facts["outcome"] = "served"
                facts["root_threads_current_dep"] = root_after.u1 is dep_now
            except Exception as exc:
                facts["outcome"] = "raised"
                facts["error_type"] = type(exc).__qualname__
        finally:
            try:
                target.permanent_cleanup()
            finally:
                target_book.cleanup()
        return facts

    _assert_posture_parity(scenario, dynamic=True)


def test_integration_concurrent_melds_through_specialization_window() -> None:
    """
    Purpose:
        Hammer the root with concurrent melds from cold through the
        specialization window; both postures must be error-free with
        identical identity semantics.
    Contract:
        - The specializer runs post-success on the leader under a non-blocking
          lock; followers never wait and never observe a wrong result.
        - All roots are fresh instances; every root threads the ONE live
          unique dep; the published slot settles to a stable door.
    """
    def scenario(
            spellbook: Spellbook,
            conduit: Conduit,
            ids: Dict[str, str],
    ) -> Dict[str, object]:
        thread_count = 4
        melds_per_thread = 200
        errors: List[str] = []
        dep_ids_seen: List[int] = []
        root_ids_seen: List[int] = []
        seen_lock = threading.Lock()
        barrier = threading.Barrier(thread_count)

        def worker() -> None:
            local_dep_ids: List[int] = []
            local_root_ids: List[int] = []
            try:
                barrier.wait()
                for _ in range(melds_per_thread):
                    root = conduit.meld(spell=ids["root"])
                    local_dep_ids.append(id(root.u1))
                    local_root_ids.append(id(root))
            except Exception as exc:
                with seen_lock:
                    errors.append(type(exc).__qualname__)
                return
            with seen_lock:
                dep_ids_seen.extend(local_dep_ids)
                root_ids_seen.extend(local_root_ids)

        threads = [
            threading.Thread(target=worker) for _ in range(thread_count)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        root_spell = spellbook._spell_id_pool[ids["root"]]
        context = root_spell._creation_context
        settled = context._no_overrides_executor
        conduit.meld(spell=ids["root"])
        return {
            "errors": tuple(sorted(set(errors))),
            "single_dep_identity": len(set(dep_ids_seen)) == 1,
            "total_melds": len(root_ids_seen),
            "slot_settled": context._no_overrides_executor is settled,
        }

    facts = _assert_posture_parity(scenario)
    assert facts["errors"] == ()
    assert facts["single_dep_identity"] is True
    assert facts["total_melds"] == 800
