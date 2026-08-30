"""
Experiment forcing phase-1-to-phase-4 artifact wipe after dynamic late bind.

Purpose:
    Check whether meld can still recover after the spell-owned structural
    artifact objects are explicitly cleared post-conjure.

Scenarios:
    - one late-bound standalone spell
    - one late-bound provider/consumer pair
"""

import gc
import sys
from typing import Any, Dict

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


class _SoloRoot:
    """
    Standalone spell with no dependencies.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _PairProvider:
    """
    Provider used by the pair scenario.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _PairConsumer:
    """
    Consumer that depends on the late-bound provider.
    """

    __slots__ = ("provider",)

    def __init__(self, provider: _PairProvider) -> None:
        self.provider = provider


def _make_dynamic_spellbook(frame_name: str) -> Spellbook:
    """
    Build one dynamic-mode spellbook with deterministic worker count.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(
        aetheric_frame=frame_name,
        configuration=configuration,
    )


def _get_spell(spellbook: Spellbook, spell_id: str) -> Any:
    """
    Resolve one live spell by current spell id.
    """
    spell = spellbook._spell_id_pool.get(spell_id)
    if spell is None:
        raise AssertionError(f"Spell '{spell_id}' was not found in spell_id_pool.")
    return spell


def _artifact_snapshot(spell: Any) -> Dict[str, Any]:
    """
    Return a compact compiler-artifact snapshot for one spell.
    """
    artifact = spell._compiler_artifact
    return {
        "spell_name": spell.spell_name,
        "phase1_requirements": artifact._requirements is not None,
        "phase2_symbolic_graph": artifact._symbolic_graph is not None,
        "phase3_resolution_frame": artifact._resolution_frame is not None,
        "phase4_validation": artifact._validation_result_phase4 is not None,
        "phase5_root_blueprint": artifact._root_blueprint_phase5 is not None,
        "phase5_system_index": artifact._spell_system_index_phase5 is not None,
        "phase8_occurrence": artifact._occurrence_graph_analysis is not None,
        "phase9_model": artifact._spell_codegen_model is not None,
        "phase10_plan": artifact._spell_codegen_plan is not None,
        "phase11_creation": artifact._spell_codegen_creation is not None,
        "resolution_required": spell.resolution_required,
        "resolution_complete": spell.resolution_complete,
        "is_broken": spell.is_broken,
        "dependency_count": len(spell.dependencies),
    }


def _wipe_phase14(spell: Any) -> None:
    """
    Force-clear structural artifact objects for one spell.
    """
    spell._compiler_artifact.cleanup_phase_artifacts()


def test_forced_phase14_wipe_after_late_bind_single_spell_experiment() -> None:
    """
    Wipe structural artifacts for one standalone late-bound spell, then meld it.
    """
    frame_name = "forced-phase14-wipe-single-experiment"
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        with spellbook.transaction("bind"):
            root_spell_id = spellbook.bind(
                spell=_SoloRoot,
                existence=Existence.unique,
                permissions="create",
            )

        root_spell = _get_spell(spellbook, root_spell_id)
        print("FORCED_PHASE14_SINGLE_BEFORE_WIPE")
        print(_artifact_snapshot(root_spell))

        _wipe_phase14(root_spell)
        print("FORCED_PHASE14_SINGLE_AFTER_WIPE")
        print(_artifact_snapshot(root_spell))

        created = conduit.meld(spell_id=root_spell_id)
        print("FORCED_PHASE14_SINGLE_AFTER_MELD")
        print(_artifact_snapshot(root_spell))

        assert isinstance(created, _SoloRoot)
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


def test_forced_phase14_wipe_after_late_bind_pair_experiment() -> None:
    """
    Wipe structural artifacts for a late-bound provider/consumer pair, then meld the consumer.
    """
    frame_name = "forced-phase14-wipe-pair-experiment"
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        with spellbook.transaction("bind"):
            provider_id = spellbook.bind(
                spell=_PairProvider,
                existence=Existence.unique,
                permissions="create",
            )
            consumer_id = spellbook.bind(
                spell=_PairConsumer,
                existence=Existence.unique,
                permissions="create",
            )

        provider_spell = _get_spell(spellbook, provider_id)
        consumer_spell = _get_spell(spellbook, consumer_id)
        print("FORCED_PHASE14_PAIR_BEFORE_WIPE")
        print(
            {
                "provider": _artifact_snapshot(provider_spell),
                "consumer": _artifact_snapshot(consumer_spell),
            }
        )

        _wipe_phase14(provider_spell)
        _wipe_phase14(consumer_spell)
        print("FORCED_PHASE14_PAIR_AFTER_WIPE")
        print(
            {
                "provider": _artifact_snapshot(provider_spell),
                "consumer": _artifact_snapshot(consumer_spell),
            }
        )

        created = conduit.meld(spell_id=consumer_id)
        print("FORCED_PHASE14_PAIR_AFTER_MELD")
        print(
            {
                "provider": _artifact_snapshot(provider_spell),
                "consumer": _artifact_snapshot(consumer_spell),
            }
        )

        assert isinstance(created, _PairConsumer)
        assert isinstance(created.provider, _PairProvider)
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
    """
    Execute both forced-wipe experiments directly and emit a terminal marker.
    """
    test_forced_phase14_wipe_after_late_bind_single_spell_experiment()
    test_forced_phase14_wipe_after_late_bind_pair_experiment()
    print("OK_FORCED_PHASE14_WIPE_AFTER_LATE_BIND_EXPERIMENT")


if __name__ == "__main__":
    _run_experiment()
