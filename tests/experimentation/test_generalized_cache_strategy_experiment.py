"""
Experiment exercising the generalized_cache phase-11 family end to end.

Purpose:
    Prove the manifest-first family on a live runtime. Generalized planner
    output now routes to the generalized_cache family directly through
    phase-11 discovery, so this experiment:
    - conjures a dynamic conduit and binds a small dependency graph,
    - melds through both lanes and asserts the new family produced the doors,
    - exports the family cache package and round-trips it through marshal,
    - clears the live CreationContext and reloads it through the family
      codec (which hydrates through the same single hydrator the live path
      used),
    - melds again through both lanes and asserts behavior parity.

This is an experimentation surface, not production runtime code.
"""

import gc
import marshal
import sys
from typing import Any

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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.generalized_cache_creation_cache import (
    build_package,
    load_creation_context,
    load_creation_context_lazy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.manifest.generalized_cache_manifest import (
    MANIFEST_METADATA_KEY,
)
from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    executor_factory_cache_size,
)


class _Leaf:
    """
    Shared no-dependency spell (Existence.unique).
    """

    def __init__(self) -> None:
        self.tag = "leaf"


class _Root:
    """
    Per-meld root spell (Existence.many) with one DI dependency and one
    overridable plain parameter.
    """

    def __init__(self, leaf: _Leaf, label: str = "default") -> None:
        self.leaf = leaf
        self.label = label


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


def test_generalized_cache_strategy_experiment() -> None:
    """
    Run the generalized_cache family end to end against a live conduit.

    Contract:
        - Uses dynamic mode and post-conjure binding.
        - Live melds must run through generalized_cache doors (the family now
          claims generalized plans directly in phase-11 discovery).
        - The codec package must survive a real marshal round-trip.
        - Reloaded doors must reproduce live lane behavior for both the
          no-overrides and overrides lanes.
    """
    frame_name = "generalized-cache-strategy-experiment"
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = _make_dynamic_spellbook(frame_name)
    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        with spellbook.transaction("bind"):
            leaf_spell_id = spellbook.bind(
                spell=_Leaf,
                existence=Existence.unique,
                permissions="create",
            )
            root_spell_id = spellbook.bind(
                spell=_Root,
                existence=Existence.many,
                permissions="create",
            )
        _ = leaf_spell_id

        # ------------------------------------------------------------------
        # Live melds through the generalized_cache family.
        # ------------------------------------------------------------------
        live_plain = conduit.meld(spell=root_spell_id)
        assert isinstance(live_plain, _Root)
        assert live_plain.label == "default"

        live_overridden = conduit.meld(
            spell=root_spell_id,
            spell_override={"label": "patched"},
        )
        assert isinstance(live_overridden, _Root)
        assert live_overridden.label == "patched"
        assert live_overridden is not live_plain
        assert live_overridden.leaf is live_plain.leaf

        root_spell = _get_spell(spellbook, root_spell_id)
        artifact = root_spell._compiler_artifact
        creation = artifact._spell_codegen_creation
        assert creation is not None
        assert creation.metadata.get("creation_context_strategy") == (
            "generalized_cache_codegen_creation"
        )
        assert creation.selected_strategy_ids == (
            "generalized_cache_codegen_creation",
        )
        manifest = creation.metadata.get(MANIFEST_METADATA_KEY)
        assert manifest is not None
        assert manifest["route_key"] == "many"
        print("GENERALIZED_CACHE_LIVE")
        print(
            {
                "discovery_reason": creation.discovery_reason,
                "no_overrides_steps": creation.metadata.get(
                    "no_overrides_step_count"
                ),
                "override_steps": creation.metadata.get("override_step_count"),
                "fast_transient": creation.metadata.get(
                    "no_overrides_fast_transient_available"
                ),
            }
        )

        # ------------------------------------------------------------------
        # Export, marshal round-trip, clear, reload through the codec.
        # ------------------------------------------------------------------
        package = build_package(root_spell)
        decoded_package = marshal.loads(marshal.dumps(package))
        assert decoded_package["family_id"] == package["family_id"]
        assert decoded_package["spell_id"] == package["spell_id"]

        root_spell._cleanup_creation_context()
        assert root_spell._creation_context is None

        factory_cache_size_before_load = executor_factory_cache_size()
        reloaded_context = load_creation_context(
            root_spell,
            decoded_package,
            publish=True,
        )
        assert reloaded_context is root_spell._creation_context
        assert root_spell._creation_context_switch.state >= 2
        print("GENERALIZED_CACHE_RELOAD")
        print(
            {
                "factory_cache_before": factory_cache_size_before_load,
                "factory_cache_after": executor_factory_cache_size(),
            }
        )

        # ------------------------------------------------------------------
        # Behavior parity through the reloaded doors.
        # ------------------------------------------------------------------
        reloaded_plain = conduit.meld(spell=root_spell_id)
        assert isinstance(reloaded_plain, _Root)
        assert reloaded_plain.label == "default"
        assert reloaded_plain is not live_plain
        assert reloaded_plain.leaf is live_plain.leaf

        reloaded_overridden = conduit.meld(
            spell=root_spell_id,
            spell_override={"label": "reloaded"},
        )
        assert isinstance(reloaded_overridden, _Root)
        assert reloaded_overridden.label == "reloaded"
        assert reloaded_overridden.leaf is live_plain.leaf

        assert executor_factory_cache_size() >= 1

        # ------------------------------------------------------------------
        # Lazy load: zero hydration at publish, hot-door swap on first meld.
        # ------------------------------------------------------------------
        root_spell._cleanup_creation_context()
        lazy_context = load_creation_context_lazy(
            root_spell,
            marshal.loads(marshal.dumps(package)),
            publish=True,
        )
        assert lazy_context is root_spell._creation_context
        cold_no_overrides_door = lazy_context._no_overrides_executor
        cold_overrides_door = lazy_context._overrides_executor

        lazy_plain = conduit.meld(spell=root_spell_id)
        assert isinstance(lazy_plain, _Root)
        assert lazy_plain.label == "default"
        assert lazy_plain.leaf is live_plain.leaf
        # First meld must have swapped the hot doors into the context slots.
        assert lazy_context._no_overrides_executor is not cold_no_overrides_door
        assert lazy_context._overrides_executor is not cold_overrides_door

        lazy_overridden = conduit.meld(
            spell=root_spell_id,
            spell_override={"label": "lazy"},
        )
        assert isinstance(lazy_overridden, _Root)
        assert lazy_overridden.label == "lazy"
        print("GENERALIZED_CACHE_LAZY")
        print(
            {
                "hot_swap_no_overrides": (
                    lazy_context._no_overrides_executor
                    is not cold_no_overrides_door
                ),
                "hot_swap_overrides": (
                    lazy_context._overrides_executor is not cold_overrides_door
                ),
            }
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
