"""
Experiment: cleaning up a shared dependency must BREAK its dependents.

Purpose / expected behaviour (this is the point of invalidation on cleanup):
    A spell that is a dependency of other spells is cleaned up. The dependents
    must NOT keep resolving against the now-removed dependency -- they must become
    gated/invalid and FAIL to meld. A dependent that still resolves after its
    dependency was disposed is a correctness violation.

Method (dynamic mode):
    Bind three leaf dependencies (Dep1, Dep2, Dep3) and two consumers:
        * Root      depends on Dep1, Dep2, Dep3
        * OtherRoot depends on Dep1
    so Dep1 is a shared dependency of two roots.

    1. Compile + MELD BOTH roots successfully BEFORE cleanup (establish that they
       work and are cached).
    2. cleanup_spell(Dep1).
    3. Confirm both roots flip to gated on the SpellSystemStates plane.
    4. MELD BOTH roots again AFTER cleanup -- expected to BREAK (unresolvable).
    5. Control: notify_spell_changed(Dep1) to show the CCM meld-gate plane.

Asserts the purpose: both dependents meld before cleanup, both are gated after,
and both FAIL to resolve after. All evidence is printed before any assert.

This is an experimentation surface, not production runtime code.
"""

import gc
import sys
from typing import Any, Optional, Tuple

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


def _ensure_src_on_path() -> None:
    """Ensure the local `src/` tree is importable for direct execution."""
    if "src" not in sys.path:
        sys.path.insert(0, "src")
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_src_on_path()

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)


class _Dep1:
    """Shared leaf dependency that gets cleaned up."""

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _Dep2:
    """Second leaf dependency."""

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _Dep3:
    """Third leaf dependency."""

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _Root:
    """Consumer with three dependencies."""

    __slots__ = ("dep1", "dep2", "dep3")

    def __init__(self, dep1: _Dep1, dep2: _Dep2, dep3: _Dep3) -> None:
        self.dep1 = dep1
        self.dep2 = dep2
        self.dep3 = dep3


class _OtherRoot:
    """Second consumer that also depends on Dep1."""

    __slots__ = ("dep1",)

    def __init__(self, dep1: _Dep1) -> None:
        self.dep1 = dep1


def _make_dynamic_spellbook(frame_name: str) -> Spellbook:
    """Build one dynamic-mode spellbook with a deterministic worker count."""
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame_name, configuration=configuration)


def _get_spell(spellbook: Spellbook, spell_id: str) -> Any:
    """Return the live spell object for one current spell id."""
    spell = spellbook._spell_id_pool.get(spell_id)
    if spell is None:
        raise AssertionError(f"spell '{spell_id}' not found in _spell_id_pool")
    return spell


def _validity(spell: Any) -> Optional[str]:
    """Return the spell's SpellSystemState validity as a string, or None."""
    state = spell.system_state
    if state is None:
        return None
    return str(state.validity)


def _try_meld(conduit: Any, spell_id: str) -> Tuple[bool, str]:
    """
    Attempt to meld one spell.

    Returns:
        (resolved, detail): resolved=True with the created type name if meld
        succeeds; resolved=False with the exception text if meld breaks.
    """
    try:
        obj = conduit.meld(spell=spell_id)
        return (True, type(obj).__name__)
    except Exception as exc:
        return (False, f"{type(exc).__name__}: {exc}")


def test_cleanup_dependency_breaks_dependents_experiment() -> None:
    """
    Clean up a shared dependency and prove both dependents break afterwards.

    Contract:
        - Runs only in dynamic mode.
        - Prints every phase, then asserts the purpose: both dependents meld
          before cleanup, are gated after, and FAIL to resolve after.
    """
    frame_name = "cleanup-dependency-breaks-experiment"
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        conduit_id = conduit._id
        with spellbook.transaction("bind"):
            dep1_id = spellbook.bind(spell=_Dep1, existence=Existence.unique, permissions="create")
            dep2_id = spellbook.bind(spell=_Dep2, existence=Existence.unique, permissions="create")
            dep3_id = spellbook.bind(spell=_Dep3, existence=Existence.unique, permissions="create")
            root_id = spellbook.bind(spell=_Root, existence=Existence.unique, permissions="create")
            other_root_id = spellbook.bind(spell=_OtherRoot, existence=Existence.unique, permissions="create")

        root_spell = _get_spell(spellbook, root_id)
        other_root_spell = _get_spell(spellbook, other_root_id)
        dep1_spell = _get_spell(spellbook, dep1_id)

        # Build component graph + dependency edges on both planes (phase 5).
        compiler_system = SpellCompilerSystem()
        try:
            compiler_system.run_all_phases(spellbook, root_spell, conduit_id)
            compiler_system.run_all_phases(spellbook, other_root_spell, conduit_id)
        finally:
            compiler_system.cleanup()

        ccm = spellbook._aether._get_change_control_manager(spellbook._aetheric_frame_name)
        assert ccm is not None, "change control manager unavailable"

        # --- Phase A: confirm the dependency edges exist on both planes ---
        dep1_state = dep1_spell.system_state
        dep1_dependents_pre = set(dep1_state.direct_dependents) if dep1_state is not None else set()
        print("EXPERIMENT_A_GRAPH")
        print({
            "dep1_id": dep1_id,
            "root_id": root_id,
            "other_root_id": other_root_id,
            "dep1_sss_direct_dependents": dep1_dependents_pre,
        })

        # --- Phase B: MELD BOTH dependents BEFORE cleanup (must succeed) ---
        root_before = _try_meld(conduit, root_id)
        other_before = _try_meld(conduit, other_root_id)
        print("EXPERIMENT_B_MELD_BEFORE")
        print({
            "root_validity": _validity(root_spell),
            "other_root_validity": _validity(other_root_spell),
            "meld(root)_before": root_before,
            "meld(other_root)_before": other_before,
        })

        # --- Phase C: ACTION -- clean up the shared dependency Dep1 ---
        conduit.cleanup_spell(spell=dep1_spell)

        # --- Phase D: post-cleanup validity (expected gated) ---
        root_validity_after = _validity(root_spell)
        other_validity_after = _validity(other_root_spell)
        ccm_dirty_root = ccm.is_root_dirty(conduit_id, root_id)
        ccm_dirty_other = ccm.is_root_dirty(conduit_id, other_root_id)
        print("EXPERIMENT_D_POST_CLEANUP_STATE")
        print({
            "root_validity_after": root_validity_after,
            "other_root_validity_after": other_validity_after,
            "is_root_dirty(root)_after": ccm_dirty_root,
            "is_root_dirty(other_root)_after": ccm_dirty_other,
        })

        # --- Phase D2: MELD BOTH dependents AFTER cleanup (expected to BREAK) ---
        root_after = _try_meld(conduit, root_id)
        other_after = _try_meld(conduit, other_root_id)
        print("EXPERIMENT_D2_MELD_AFTER")
        print({
            "meld(root)_after": root_after,
            "meld(other_root)_after": other_after,
            "root_validity_post_meld": _validity(root_spell),
            "other_root_validity_post_meld": _validity(other_root_spell),
        })

        # --- Phase E: CONTROL -- manually trigger the CCM fan-out ---
        ccm.notify_spell_changed(dep1_id)
        print("EXPERIMENT_E_CONTROL_MANUAL_NOTIFY")
        print({
            "is_root_dirty(root)_after_notify": ccm.is_root_dirty(conduit_id, root_id),
            "is_root_dirty(other_root)_after_notify": ccm.is_root_dirty(conduit_id, other_root_id),
        })

        # --- Phase F: VERDICT ---
        both_melded_before = root_before[0] and other_before[0]
        both_gated_after = (
            "gated" in (root_validity_after or "").lower()
            and "gated" in (other_validity_after or "").lower()
        )
        both_broke_after = (not root_after[0]) and (not other_after[0])
        print("EXPERIMENT_F_VERDICT")
        print({
            "both_dependents_melded_before_cleanup": both_melded_before,
            "both_dependents_gated_after_cleanup": both_gated_after,
            "both_dependents_broke_after_cleanup": both_broke_after,
            "purpose_satisfied": both_melded_before and both_gated_after and both_broke_after,
        })

        # Assert the purpose (evidence already printed above).
        assert both_melded_before, (
            f"setup invalid: a dependent failed to meld before cleanup -- "
            f"root_before={root_before}, other_before={other_before}"
        )
        assert both_gated_after, (
            f"dependents were not gated after cleanup -- "
            f"root={root_validity_after}, other={other_validity_after}"
        )
        assert both_broke_after, (
            f"PURPOSE VIOLATED: a dependent still resolved after its dependency was "
            f"cleaned up; both were expected to break (unresolvable) -- "
            f"root_after={root_after}, other_after={other_after}"
        )
    finally:
        try:
            conduit.permanent_cleanup()
        finally:
            try:
                spellbook.cleanup()
            finally:
                Aether._reset_singleton_for_tests()
                aether2 = Aether()
                Spellbook._aether = aether2
                Conduit._aether = aether2
                gc.collect()


def _run_experiment() -> None:
    """Execute the experiment directly and emit a terminal marker."""
    test_cleanup_dependency_breaks_dependents_experiment()
    print("OK_CLEANUP_DEPENDENCY_BREAKS_DEPENDENTS_EXPERIMENT")


if __name__ == "__main__":
    _run_experiment()
