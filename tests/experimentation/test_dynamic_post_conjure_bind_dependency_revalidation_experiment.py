"""
Dynamic-mode experiment for post-conjure bind and dependent creation.

Purpose:
    Reproduce the exact edge case under discussion:
    - conjure a dynamic conduit with no initial spells
    - bind provider/provider/consumer after conjure
    - meld the consumer
    - inspect compiler/runtime artifact state before and after the first create

This is an experimentation surface, not production runtime code.
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


class _ProviderA:
    """
    Provider with an explicit zero-arg constructor.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _ProviderB:
    """
    Second provider with an explicit zero-arg constructor.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _Consumer:
    """
    Consumer that depends on both late-bound providers.
    """

    __slots__ = ("provider_a", "provider_b")

    def __init__(
            self,
            provider_a: _ProviderA,
            provider_b: _ProviderB,
    ) -> None:
        self.provider_a = provider_a
        self.provider_b = provider_b


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
    Return the live spell object for one current spell id.
    """
    spell = spellbook._spell_id_pool.get(spell_id)
    if spell is None:
        raise AssertionError(f"Spell '{spell_id}' was not found in spell_id_pool.")
    return spell


def _artifact_snapshot(spell: Any) -> Dict[str, Any]:
    """
    Return a compact compiler-artifact snapshot for one live spell.
    """
    artifact = spell._compiler_artifact
    codegen_ir = artifact._codegen_ir
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
        "phase11_dirty": artifact._phase8_11_codegen_ir_dirty,
        "codegen_ir_phase2_5": (
            bool(codegen_ir.get("phase2_5")) if codegen_ir is not None else False
        ),
        "codegen_ir_phase8_11": (
            bool(codegen_ir.get("phase8_11")) if codegen_ir is not None else False
        ),
        "resolution_required": spell.resolution_required,
        "resolution_complete": spell.resolution_complete,
        "is_broken": spell.is_broken,
    }


def test_dynamic_post_conjure_bind_dependency_revalidation_experiment() -> None:
    """
    Run the post-conjure bind dependency experiment in dynamic mode.

    Contract:
        - Conjures a dynamic conduit before any spells are bound.
        - Binds two providers and one consumer after conjure.
        - Melds the consumer and verifies the injected providers are correct.
        - Prints artifact snapshots before and after the first create.
    """
    frame_name = "dynamic-post-conjure-bind-experiment"
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        with spellbook.transaction("bind"):
            provider_a_id = spellbook.bind(
                spell=_ProviderA,
                existence=Existence.unique,
                permissions="create",
            )
            provider_b_id = spellbook.bind(
                spell=_ProviderB,
                existence=Existence.unique,
                permissions="create",
            )
            consumer_id = spellbook.bind(
                spell=_Consumer,
                existence=Existence.unique,
                permissions="create",
            )

        provider_a_spell = _get_spell(spellbook, provider_a_id)
        provider_b_spell = _get_spell(spellbook, provider_b_id)
        consumer_spell = _get_spell(spellbook, consumer_id)

        before_snapshot = {
            "provider_a": _artifact_snapshot(provider_a_spell),
            "provider_b": _artifact_snapshot(provider_b_spell),
            "consumer": _artifact_snapshot(consumer_spell),
        }
        print("DYNAMIC_POST_CONJURE_BIND_EXPERIMENT_BEFORE")
        print(before_snapshot)

        created = conduit.meld(spell=consumer_id)

        after_snapshot = {
            "provider_a": _artifact_snapshot(provider_a_spell),
            "provider_b": _artifact_snapshot(provider_b_spell),
            "consumer": _artifact_snapshot(consumer_spell),
        }
        print("DYNAMIC_POST_CONJURE_BIND_EXPERIMENT_AFTER")
        print(after_snapshot)

        assert isinstance(created, _Consumer)
        assert isinstance(created.provider_a, _ProviderA)
        assert isinstance(created.provider_b, _ProviderB)
        assert after_snapshot["consumer"]["phase11_creation"] is True
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
    Execute the experiment directly and emit a terminal marker.
    """
    test_dynamic_post_conjure_bind_dependency_revalidation_experiment()
    print("OK_DYNAMIC_POST_CONJURE_BIND_DEPENDENCY_REVALIDATION_EXPERIMENT")


if __name__ == "__main__":
    _run_experiment()
