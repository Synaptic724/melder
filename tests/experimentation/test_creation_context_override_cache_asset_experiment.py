"""
Experiment rehydrating an override-bearing generic CreationContext from disk.

Purpose:
    Probe whether a saved creation-context-facing override artifact can be
    reloaded after clearing the live compiler artifact/context and still drive
    `conduit.meld(...)` with the same override shape.
"""

import gc
import sys
from pathlib import Path
from typing import Any, Dict

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.experimentation.creation_context_cache_asset_playground import (
    build_creation_context_override_cache_asset,
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


class _OverrideProvider:
    """
    Default provider used by the consumer before override substitution.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _OverrideConsumer:
    """
    Consumer with one uniquely targetable dependency parameter.
    """

    __slots__ = ("provider",)

    def __init__(self, provider: _OverrideProvider) -> None:
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
    Return one live spell by current spell id.
    """
    spell = spellbook._spell_id_pool.get(spell_id)
    if spell is None:
        raise AssertionError(f"Spell '{spell_id}' was not found in spell_id_pool.")
    return spell


def _snapshot(spell: Any) -> Dict[str, Any]:
    """
    Return a compact runtime/compiler snapshot for the spell.
    """
    artifact = spell._compiler_artifact
    return {
        "has_compiler_artifact": artifact is not None,
        "has_phase11_creation": (
            artifact is not None and artifact._spell_codegen_creation is not None
        ),
        "has_cached_context": spell._creation_context is not None,
        "context_switch_state": spell._creation_context_switch.state,
    }


def test_creation_context_override_cache_asset_experiment() -> None:
    """
    Rebuild an override-bearing generic CreationContext from a saved cache asset.

    Contract:
        - Uses dynamic mode.
        - Binds provider/consumer after conjure.
        - Saves a cache asset for one concrete override payload shape.
        - Clears live compiler/context state before reload.
        - Rehydrates a generic CreationContext from the saved asset.
        - Melds successfully with the same override shape.
    """
    frame_name = "creation-context-override-cache-asset-experiment"
    override_value = object()
    override_payload = {"*provider": override_value}
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        with spellbook.transaction("bind"):
            spellbook.bind(
                spell=_OverrideProvider,
                existence=Existence.unique,
                permissions="create",
            )
            consumer_id = spellbook.bind(
                spell=_OverrideConsumer,
                existence=Existence.many,
                permissions="create",
            )

        consumer_spell = _get_spell(spellbook, consumer_id)
        first_instance = conduit.meld(spell=consumer_id, spell_override=override_payload)
        assert isinstance(first_instance, _OverrideConsumer)
        assert first_instance.provider is override_value

        cache_asset = build_creation_context_override_cache_asset(
            spell=consumer_spell,
            override_payload=override_payload,
        )
        print("CREATION_CONTEXT_OVERRIDE_CACHE_ASSET_BEFORE_CLEAR")
        print(_snapshot(consumer_spell))

        cache_path = Path(
            "tests/experimentation/creation_context_override_cache_asset_experiment.json"
        )
        original_compiler_artifact = consumer_spell._compiler_artifact
        try:
            write_creation_context_cache_asset(
                cache_asset=cache_asset,
                path=cache_path,
            )
            loaded_cache_asset = read_creation_context_cache_asset(
                path=cache_path,
            )

            consumer_spell._cleanup_creation_context()
            consumer_spell._compiler_artifact = None
            print("CREATION_CONTEXT_OVERRIDE_CACHE_ASSET_AFTER_CLEAR")
            print(_snapshot(consumer_spell))

            rehydrated_context = load_creation_context_from_cache_asset(
                spell=consumer_spell,
                cache_asset=loaded_cache_asset,
                publish=True,
            )
            assert rehydrated_context is consumer_spell._creation_context
            print("CREATION_CONTEXT_OVERRIDE_CACHE_ASSET_AFTER_LOAD")
            print(_snapshot(consumer_spell))

            rebuilt_instance = conduit.meld(
                spell=consumer_id,
                spell_override=override_payload,
            )
            assert isinstance(rebuilt_instance, _OverrideConsumer)
            assert rebuilt_instance.provider is override_value
        finally:
            consumer_spell._compiler_artifact = original_compiler_artifact
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
    Execute the override cache-asset experiment directly and emit a marker.
    """
    test_creation_context_override_cache_asset_experiment()
    print("OK_CREATION_CONTEXT_OVERRIDE_CACHE_ASSET_EXPERIMENT")


if __name__ == "__main__":
    _run_experiment()
