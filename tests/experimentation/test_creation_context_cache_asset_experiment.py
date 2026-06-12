"""
Experiment rehydrating a generic CreationContext from a saved cache asset.

Purpose:
    Probe the narrow runtime seam around `CreationContext` by:
    - conjuring a dynamic conduit,
    - binding one spell after conjure,
    - generating the live creation-context-facing package once,
    - saving a cache asset to disk,
    - clearing the live phase-11/context state,
    - loading the cache asset back into a generic `CreationContext`,
    - and melding through the conduit again.

This is an experimentation surface, not production runtime code.
"""

import gc
import sys
from pathlib import Path
from typing import Any, Dict

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.experimentation.creation_context_cache_asset_playground import (
    build_creation_context_cache_asset,
    load_creation_context_from_cache_asset,
    read_creation_context_cache_asset,
    write_creation_context_cache_asset,
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


class _CachedRoot:
    """
    Single no-dependency spell for cache-asset rehydration.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


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
    Return one live spell by current spell id.
    """
    spell = spellbook._spell_id_pool.get(spell_id)
    if spell is None:
        raise AssertionError(f"Spell '{spell_id}' was not found in spell_id_pool.")
    return spell


def _artifact_snapshot(spell: Any) -> Dict[str, Any]:
    """
    Return a compact runtime/compiler snapshot for the spell.
    """
    artifact = spell._compiler_artifact
    return {
        "has_phase11_creation": artifact._spell_codegen_creation is not None,
        "has_phase10_plan": artifact._spell_codegen_plan is not None,
        "has_phase9_model": artifact._spell_codegen_model is not None,
        "has_phase8_occurrence": artifact._occurrence_graph_analysis is not None,
        "has_codegen_ir": artifact._codegen_ir is not None,
        "has_cached_context": spell._creation_context is not None,
        "context_switch_state": spell._creation_context_switch.state,
    }


def test_creation_context_cache_asset_experiment() -> None:
    """
    Rebuild a spell-owned CreationContext from a saved cache asset.

    Contract:
        - Uses dynamic mode.
        - Binds the spell after conjure.
        - Saves cache asset to a real file location.
        - Clears live phase-11/context state before reload.
        - Rehydrates a generic CreationContext from the saved asset.
        - Melds successfully without repopulating the phase-11 artifact.
    """
    frame_name = "creation-context-cache-asset-experiment"
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        with spellbook.transaction("bind"):
            root_spell_id = spellbook.bind(
                spell=_CachedRoot,
                existence=Existence.unique,
                permissions="create",
            )

        root_spell = _get_spell(spellbook, root_spell_id)
        first_instance = conduit.meld(spell=root_spell_id)
        assert isinstance(first_instance, _CachedRoot)

        cache_asset = build_creation_context_cache_asset(spell=root_spell)
        before_clear = _artifact_snapshot(root_spell)
        print("CREATION_CONTEXT_CACHE_ASSET_BEFORE_CLEAR")
        print(before_clear)

        # Anchor to this test file so the asset lands here regardless of the
        # pytest invocation directory (a CWD-relative path breaks when the
        # suite is run from inside tests/).
        cache_path = (
            Path(__file__).resolve().parent
            / "creation_context_cache_asset_experiment.json"
        )
        original_compiler_artifact = root_spell._compiler_artifact
        try:
            write_creation_context_cache_asset(
                cache_asset=cache_asset,
                path=cache_path,
            )
            loaded_cache_asset = read_creation_context_cache_asset(
                path=cache_path,
            )

            root_spell._cleanup_creation_context()
            root_spell._compiler_artifact = None

            after_clear = {
                "has_compiler_artifact": root_spell._compiler_artifact is not None,
                "has_cached_context": root_spell._creation_context is not None,
                "context_switch_state": root_spell._creation_context_switch.state,
            }
            print("CREATION_CONTEXT_CACHE_ASSET_AFTER_CLEAR")
            print(after_clear)

            rehydrated_context = load_creation_context_from_cache_asset(
                spell=root_spell,
                cache_asset=loaded_cache_asset,
                publish=True,
            )
            assert rehydrated_context is root_spell._creation_context

            after_load = {
                "has_compiler_artifact": root_spell._compiler_artifact is not None,
                "has_cached_context": root_spell._creation_context is not None,
                "context_switch_state": root_spell._creation_context_switch.state,
            }
            print("CREATION_CONTEXT_CACHE_ASSET_AFTER_LOAD")
            print(after_load)

            rebuilt_instance = conduit.meld(spell=root_spell_id)
            assert isinstance(rebuilt_instance, _CachedRoot)
        finally:
            root_spell._compiler_artifact = original_compiler_artifact
            try:
                cache_path.unlink(missing_ok=True)
            except Exception:
                pass

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
    Execute the cache-asset experiment directly and emit a terminal marker.
    """
    test_creation_context_cache_asset_experiment()
    print("OK_CREATION_CONTEXT_CACHE_ASSET_EXPERIMENT")


if __name__ == "__main__":
    _run_experiment()
