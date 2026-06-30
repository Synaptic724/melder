"""
Experiment: does cleaning up a shared dependency force its dependents to recheck?

Scenario (dynamic mode only):
    Bind three leaf dependencies (Dep1, Dep2, Dep3) and two consumers:
        * Root      depends on Dep1, Dep2, Dep3
        * OtherRoot depends on Dep1
    so Dep1 is a shared dependency of two roots ("a dependency for other things").

    Compile both roots so the dependency edges exist on BOTH control planes:
        * SpellSystemStates : Dep1.system_state.direct_dependents
        * ChangeControlManager : component_of[Dep1_id] -> {Root_id, OtherRoot_id}
          (built by compiler phase 5 via rebuild_component_of)

    cleanup_spell(Dep1) -- Dep1 is a sole-member active index, so cleanup destroys
    the index -> _destroy_spell_index -> SpellSystemStates.unregister_index, which
    calls compute_impact_closure([Dep1_index]).

    Then OBSERVE, with no manual nudging, whether the two dependent roots are forced
    to recheck on each plane, and whether meld(Root) is gated. Finally, as a CONTROL,
    manually call ChangeControlManager.notify_spell_changed(Dep1_id) to prove the CCM
    fan-out works when it is actually triggered.

This is an experimentation surface, not production runtime code. It prints a verdict;
it does not hard-assert the contested outcome.
"""

import gc
import sys
from typing import Any, Optional

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


def _ensure_src_on_path() -> None:
    """
    Ensure the local `src/` tree is importable for direct experiment execution.
    """
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
    """First leaf dependency (the shared one that gets cleaned up)."""

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
    """Second consumer that also depends on Dep1 (so Dep1 has two dependents)."""

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


def test_cleanup_dependency_forces_dependent_recheck_experiment() -> None:
    """
    Clean up a shared dependency and observe whether its dependents recheck.

    Contract:
        - Runs only in dynamic mode.
        - Prints graph / baseline / post-cleanup / control snapshots and a verdict.
        - Asserts only setup invariants, never the contested outcome.
    """
    frame_name = "cleanup-dependency-recheck-experiment"
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
        ccm_pre = ccm.describe()
        print("EXPERIMENT_A_GRAPH")
        print({
            "dep1_id": dep1_id,
            "root_id": root_id,
            "other_root_id": other_root_id,
            "dep1_sss_direct_dependents": dep1_dependents_pre,
            "ccm_component_of": ccm_pre.get("component_of_by_conduit"),
            "ccm_dirty_roots": ccm_pre.get("dirty_roots_by_conduit"),
        })

        # --- Phase B: pre-cleanup baseline ---
        root_validity_baseline = _validity(root_spell)
        other_validity_baseline = _validity(other_root_spell)
        print("EXPERIMENT_B_BASELINE")
        print({
            "root_validity": root_validity_baseline,
            "other_root_validity": other_validity_baseline,
            "is_root_dirty(root)": ccm.is_root_dirty(conduit_id, root_id),
            "is_root_dirty(other_root)": ccm.is_root_dirty(conduit_id, other_root_id),
            "root_resolution_required": root_spell.resolution_required,
            "root_resolution_complete": root_spell.resolution_complete,
        })

        # --- Phase C: ACTION -- clean up the shared dependency Dep1 ---
        conduit.cleanup_spell(spell=dep1_spell)

        # --- Phase D: post-cleanup AUTO observation (no manual nudging) ---
        root_validity_after = _validity(root_spell)
        other_validity_after = _validity(other_root_spell)
        ccm_dirty_root = ccm.is_root_dirty(conduit_id, root_id)
        ccm_dirty_other = ccm.is_root_dirty(conduit_id, other_root_id)
        ccm_post = ccm.describe()
        meld_outcome = None
        try:
            created = conduit.meld(spell=root_id)
            meld_outcome = f"meld succeeded -> {type(created).__name__}"
        except Exception as exc:
            meld_outcome = f"{type(exc).__name__}: {exc}"
        print("EXPERIMENT_D_POST_CLEANUP_AUTO")
        print({
            "root_validity_after": root_validity_after,
            "other_root_validity_after": other_validity_after,
            "is_root_dirty(root)_after": ccm_dirty_root,
            "is_root_dirty(other_root)_after": ccm_dirty_other,
            "ccm_dirty_roots_after": ccm_post.get("dirty_roots_by_conduit"),
            "root_resolution_required_after": root_spell.resolution_required,
            "meld(root)_outcome": meld_outcome,
        })

        # --- Phase E: CONTROL -- manually trigger the CCM fan-out ---
        ccm.notify_spell_changed(dep1_id)
        ccm_dirty_root_ctrl = ccm.is_root_dirty(conduit_id, root_id)
        ccm_dirty_other_ctrl = ccm.is_root_dirty(conduit_id, other_root_id)
        print("EXPERIMENT_E_CONTROL_MANUAL_NOTIFY")
        print({
            "is_root_dirty(root)_after_notify": ccm_dirty_root_ctrl,
            "is_root_dirty(other_root)_after_notify": ccm_dirty_other_ctrl,
        })

        # --- Phase F: VERDICT ---
        sss_auto = (root_validity_baseline != root_validity_after) or (
            other_validity_baseline != other_validity_after
        )
        ccm_auto = bool(ccm_dirty_root or ccm_dirty_other)
        ccm_works = bool(ccm_dirty_root_ctrl or ccm_dirty_other_ctrl)
        if ccm_auto:
            verdict = (
                "HYPOTHESIS SUPPORTED: cleanup auto-flags dependents on the CCM "
                "plane that meld gates on -> dependents are force-rechecked."
            )
        elif sss_auto and ccm_works:
            verdict = (
                "PARTIAL: cleanup flags dependents on the SpellSystemStates plane "
                "(compute_impact_closure), but NOT on the CCM plane meld gates on. "
                "The CCM fan-out only fires when notify_spell_changed is called "
                "(proven by the control). meld(root) is therefore NOT auto-gated."
            )
        elif sss_auto:
            verdict = (
                "PARTIAL: cleanup flags dependents on the SpellSystemStates plane "
                "only; CCM machinery did not flag even under manual control."
            )
        else:
            verdict = (
                "NOT FORCED: cleanup did not flag the dependents on either plane."
            )
        print("EXPERIMENT_F_VERDICT")
        print({
            "sss_auto_flagged": sss_auto,
            "ccm_auto_flagged": ccm_auto,
            "ccm_machinery_works_under_control": ccm_works,
            "verdict": verdict,
        })

        # Setup invariant only (never the contested outcome): the dependency graph
        # must have been built, otherwise the experiment proves nothing.
        assert dep1_dependents_pre or ccm_pre.get("component_of_by_conduit"), (
            "dependency graph was not built; experiment is inconclusive"
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
    test_cleanup_dependency_forces_dependent_recheck_experiment()
    print("OK_CLEANUP_DEPENDENCY_FORCES_DEPENDENT_RECHECK_EXPERIMENT")


if __name__ == "__main__":
    _run_experiment()
