"""S3b-2: delete the dead override lane, the legacy non-manifest codec and the fallback family.

Usage: python apply_s3b2_edits.py <tree_root> [--check]

Owner decision 2026-09-26 ("1 and 2"). After S3a/S3b-1 nothing reachable from conjure or meld imports
these modules; generation 14 already rejects bundles that could carry legacy payloads.

Edit kinds (engine shared with apply_s3b1_edits.py):
    ("replace", old, new)          old must match exactly once, in the file's own line endings.
    ("cut", start, stop)           delete from `start` up to `stop`; stop=None cuts to end of file.
    ("splice", start, stop, new)   replace from `start` up to (not including) `stop` with `new`.
Every anchor and every deletion target is checked before anything is written or removed.
"""

import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one, _find_once, _line_ending_at

SB = "src/melder/aether/spellbook/"
SC = SB + "spell_compiler/"
CCS = SC + "codegen_creation_system/"
ST = CCS + "strategies/"

DELETE = [
    ST + "many_only/compilers/many_only_overrides_codegen_creation_compiler.py",
    ST + "many_only/steps/many_only_overrides_codegen_creation_step.py",
    ST + "many_only/steps/many_only_finalize_creation_context_step.py",
    ST + "many_only/artifacts/spell_override_targeting_codegen_creation.py",
    ST + "generalized/compilers/generalized_overrides_codegen_creation_compiler.py",
    ST + "generalized/compilers/generalized_manifest_overrides_runtime.py",
    ST + "generalized/steps/generalized_overrides_codegen_creation_step.py",
    ST + "generalized/steps/generalized_finalize_creation_context_step.py",
    ST + "generalized/steps/generalized_no_overrides_codegen_creation_step.py",
    ST + "generalized/artifacts/spell_override_targeting_codegen_creation.py",
    ST + "generalized/generalized_codegen_creation_state.py",
    ST + "fallback_no_overrides/fallback_no_overrides_codegen_creation_strategy.py",
    CCS + "codegen_creation_discovery_system/strategies/fallback_no_overrides_codegen_creation_discovery_strategy.py",
    CCS + "codegen_creation/spell_codegen_creation_cache.py",
    SC + "artifact_processor/strategies/spell_override_targeting_processor_strategy.py",
    SC + "artifact_processor/data/spell_override_targeting_analysis.py",
    SC + "codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py",
]
EMPTIED_DIRS = [
    ST + "many_only/artifacts",
    ST + "generalized/artifacts",
    ST + "fallback_no_overrides",
]


def _splice(data: str, edit: tuple, rel: str) -> str:
    """Replace [start, stop) with `new` in the line ending of the start line."""
    _, start, stop, new = edit
    start_index, _ = _find_once(data, start, rel)
    stop_index = data.find(stop, start_index)
    if stop_index < 0 or data.count(stop) != 1:
        raise SystemExit(f"{rel}: splice stop not unique after start: {stop!r}")
    nl = _line_ending_at(data, start_index)
    return data[:start_index] + new.replace("\n", nl) + data[stop_index:]


EDITS = {
    SB + "spellbook.py": [
        ("replace",
         "            if (\n"
         "                    artifact._spell_codegen_creation.metadata.get(\n"
         "                        MANIFEST_METADATA_KEY\n"
         "                    )\n"
         "                    is not None\n"
         "            ):\n"
         "                # Manifest-first family output (generalized, solo, ...): the\n"
         "                # manifest already IS the cache payload, so export is a\n"
         "                # metadata read instead of a full both-lane recompile.\n"
         "                spell_payload = build_manifest_package(spell)\n"
         "            else:\n"
         "                from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (\n"
         "                    build_package,\n"
         "                )\n"
         "                spell_payload = build_package(spell)\n",
         "            if (\n"
         "                    artifact._spell_codegen_creation.metadata.get(\n"
         "                        MANIFEST_METADATA_KEY\n"
         "                    )\n"
         "                    is None\n"
         "            ):\n"
         "                # Every codegen family publishes a manifest; the legacy\n"
         "                # non-manifest codec is retired (2026-09-26), so a creation\n"
         "                # without one has no cache payload.\n"
         "                return False\n"
         "            # The manifest already IS the cache payload, so export is a\n"
         "            # metadata read instead of a full both-lane recompile.\n"
         "            spell_payload = build_manifest_package(spell)\n"),
    ],
    SB + "spellbook_creation_system.py": [
        ("replace", "from types import CodeType, FunctionType\n", ""),
        ("replace",
         "from melder.aether.conduit.meld.creation_context.creation_context import (\n"
         "    CreationContext,\n"
         ")\n",
         ""),
        ("replace",
         "            - When the payload already carries live executors, it publishes\n"
         "              directly through `CreationContext.load_cached(...)`.\n"
         "            - When the payload carries a legacy phase-11 cache package, it\n"
         "              delegates to the cache-load seam that rebuilds executors after\n"
         "              phases 1-7.\n",
         "            - Every codegen family publishes a manifest package; the legacy\n"
         "              non-manifest codec and executor payloads are retired\n"
         "              (2026-09-26). Any other payload raises RuntimeError, which the\n"
         "              caller treats as a cache miss, so the spell compiles normally.\n"),
        ("splice",
         "        if is_manifest_package(spell_payload):",
         "    def _emit_spell_payloads_for_conjure(",
         "        if not is_manifest_package(spell_payload):\n"
         "            raise RuntimeError(\n"
         "                \"Cached spell payload is not a manifest package \"\n"
         "                f\"(spell_id={spell.spell_id}); the spell compiles normally.\"\n"
         "            )\n"
         "        load_creation_context_lazy(\n"
         "            spell,\n"
         "            dict(spell_payload),\n"
         "            publish=True,\n"
         "        )\n"
         "\n"
         "    @staticmethod\n"),
        ("cut", "_EXISTING_OVERRIDE_MESSAGE = (", None),
    ],
    CCS + "spell_codegen_strategy_builder.py": [
        ("replace",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.fallback_no_overrides.fallback_no_overrides_codegen_creation_strategy import (\n"
         "    FallbackNoOverridesCodegenCreationStrategy,\n"
         ")\n",
         ""),
        ("replace",
         "            - The standalone generalized no-overrides strategy remains\n"
         "              registered as the fallback public creation strategy.\n",
         "            - There is no fallback strategy (retired 2026-09-26): plan\n"
         "              discovery always selects solo, many_only or generalized, and\n"
         "              each has its family here.\n"),
        ("replace",
         "        ] = generalized_codegen_creation_strategy\n"
         "        generalized_no_overrides_codegen_creation_strategy = (\n"
         "            FallbackNoOverridesCodegenCreationStrategy()\n"
         "        )\n"
         "        self._strategies_by_name[\n"
         "            generalized_no_overrides_codegen_creation_strategy.strategy_id\n"
         "        ] = generalized_no_overrides_codegen_creation_strategy\n",
         "        ] = generalized_codegen_creation_strategy\n"),
    ],
    CCS + "codegen_creation_discovery_system/codegen_creation_discovery_strategy_builder.py": [
        ("replace",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.fallback_no_overrides_codegen_creation_discovery_strategy import (\n"
         "    FallbackNoOverridesCodegenCreationDiscoveryStrategy,\n"
         ")\n",
         ""),
        ("replace",
         "        Populate the default phase-11 discovery strategy registry.\n"
         "        \"\"\"\n",
         "        Populate the default phase-11 discovery strategy registry.\n"
         "\n"
         "        Contract:\n"
         "            Registers the solo, many_only and generalized claims in that\n"
         "            order. The fallback no-overrides claim is retired (2026-09-26):\n"
         "            plan discovery always selects one of the three, and a plan none\n"
         "            of them claims fails discovery with RuntimeError.\n"
         "        \"\"\"\n"),
        ("replace",
         "        fallback_strategy = FallbackNoOverridesCodegenCreationDiscoveryStrategy()\n",
         ""),
        ("replace",
         "        ] = generalized_strategy\n"
         "        self._strategies_by_name[\n"
         "            fallback_strategy.strategy_id\n"
         "        ] = fallback_strategy\n",
         "        ] = generalized_strategy\n"),
    ],
    ST + "generalized/compilers/generalized_runtime_library.py": [
        ("replace",
         "    - OVERRIDES SHAPE EMITTER + TARGET PREFILTER: row-driven public emission\n"
         "      seams plus the path-registry target prefilter they depend on.\n",
         "    - The override lane is no longer bridged: override melds run\n"
         "      `SitePlanOverrideRuntime` (shared_assets), which imports the\n"
         "      no-overrides helpers directly (2026-09-26).\n"),
        ("replace",
         "    - the override runtime orchestration (shape dispatch, payload split,\n"
         "      socket grouping, process-wide shape caches)\n",
         ""),
        ("cut",
         "# --- overrides lane: runtime helpers + row-driven emission seams ------------",
         "# --- shared planner data labels ---------------------------------------------"),
        ("replace",
         "    \"EMPTY_OVERRIDE_VALUES\",\n"
         "    \"MISSING\",\n"
         "    \"SpellGeneralizedCodegenPlanTargetKind\",\n"
         "    \"SpellOverrideTargetingCodegenCreation\",\n"
         "    \"build_kwargs_with_overrides\",\n"
         "    \"build_overrides_codegen_creation_step_target_counts_from_rows\",\n"
         "    \"build_step_override_targets\",\n"
         "    \"build_step_override_values\",\n"
         "    \"build_transient_no_overrides_source\",\n"
         "    \"construct_spell_instance\",\n"
         "    \"construct_spell_instance_with_overrides\",\n"
         "    \"emit_overrides_codegen_creation_executor_shape_source\",\n"
         "    \"get_existing_creation\",\n"
         "    \"invoke_spell_with_kwargs\",\n"
         "    \"normalize_transient_schema\",\n"
         "    \"raise_meld_construction_error\",\n"
         "    \"raise_override_on_existing_instance\",\n",
         "    \"SpellGeneralizedCodegenPlanTargetKind\",\n"
         "    \"build_transient_no_overrides_source\",\n"
         "    \"construct_spell_instance\",\n"
         "    \"get_existing_creation\",\n"
         "    \"normalize_transient_schema\",\n"
         "    \"raise_meld_construction_error\",\n"),
    ],
    SC + "artifact_processor/spell_codegen_model.py": [
        ("replace",
         "    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (\n"
         "        SpellOverrideTargetingAnalysis,\n"
         "    )\n",
         ""),
        ("replace",
         "        - `site_graph_shape` is the processor-owned physical site graph\n"
         "          (one site per instance key, full parameter tables, path counts)\n"
         "          that override key resolution walks instead of logical paths.\n",
         "        - `site_graph_shape` is the physical site graph (one site per\n"
         "          instance key, full parameter tables, path counts). The default\n"
         "          processor chain does not fit it (2026-09-26); override melds\n"
         "          build their own through `SpellSiteGraphProcessorStrategy`.\n"),
        ("replace", "        \"override_targeting_shape\",\n        \"site_graph_shape\",\n        \"spell_runtime_shape\",\n        \"existence_occurrence_shape\",\n        \"node_count\",\n",
         "        \"site_graph_shape\",\n        \"spell_runtime_shape\",\n        \"existence_occurrence_shape\",\n        \"node_count\",\n"),
        ("replace",
         "        \"call_shape_family\",\n"
         "        \"target_spec_count\",\n"
         "        \"targeted_socket_count\",\n"
         "        \"targeted_spell_count\",\n"
         "        \"max_targets_per_spec\",\n"
         "        \"max_target_path_depth\",\n"
         "        \"root_positional_override_relevant\",\n"
         "        \"override_shape_family\",\n",
         "        \"call_shape_family\",\n"
         "        \"root_positional_override_relevant\",\n"),
        ("replace",
         "            override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = None,\n",
         ""),
        ("replace",
         "            target_spec_count: int = 0,\n"
         "            targeted_socket_count: int = 0,\n"
         "            targeted_spell_count: int = 0,\n"
         "            max_targets_per_spec: int = 0,\n"
         "            max_target_path_depth: int = 0,\n"
         "            root_positional_override_relevant: bool = False,\n"
         "            override_shape_family: str = \"unclassified\",\n",
         "            root_positional_override_relevant: bool = False,\n"),
        ("replace",
         "              `injection_shape`, `override_targeting_shape`,\n"
         "              `site_graph_shape`, and `spell_runtime_shape` are\n",
         "              `injection_shape`, `site_graph_shape`, and\n"
         "              `spell_runtime_shape` are\n"),
        ("replace",
         "        self.override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = (\n"
         "            override_targeting_shape\n"
         "        )\n",
         ""),
        ("replace",
         "        self.target_spec_count: int = target_spec_count\n"
         "        self.targeted_socket_count: int = targeted_socket_count\n"
         "        self.targeted_spell_count: int = targeted_spell_count\n"
         "        self.max_targets_per_spec: int = max_targets_per_spec\n"
         "        self.max_target_path_depth: int = max_target_path_depth\n",
         ""),
        ("replace",
         "        self.override_shape_family: str = override_shape_family\n",
         ""),
        ("replace",
         "              `instance_shape`, `contract_shape`, `injection_shape`,\n"
         "              `override_targeting_shape`, `site_graph_shape`, and\n"
         "              `spell_runtime_shape`.\n",
         "              `instance_shape`, `contract_shape`, `injection_shape`,\n"
         "              `site_graph_shape`, and `spell_runtime_shape`.\n"),
        ("replace",
         "        if self.override_targeting_shape is not None:\n"
         "            try:\n"
         "                self.override_targeting_shape.cleanup()\n"
         "            except Exception:\n"
         "                pass\n",
         ""),
        ("replace", "        del self.override_targeting_shape\n", ""),
        ("replace",
         "        del self.target_spec_count\n"
         "        del self.targeted_socket_count\n"
         "        del self.targeted_spell_count\n"
         "        del self.max_targets_per_spec\n"
         "        del self.max_target_path_depth\n",
         ""),
        ("replace", "        del self.override_shape_family\n", ""),
        ("replace",
         "            \"injection_shape\",\n"
         "            \"override_targeting_shape\",\n"
         "            \"site_graph_shape\",\n",
         "            \"injection_shape\",\n"
         "            \"site_graph_shape\",\n"),
    ],
    SC + "phases/shared_compiler_executions.py": [
        ("replace",
         "                \"target_spec_count\": spell_codegen_model.target_spec_count,\n",
         ""),
    ],
    ST + "many_only/many_only_codegen_creation_state.py": [
        ("replace",
         "from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence, Tuple\n",
         "from typing import TYPE_CHECKING, Any, Callable, Optional\n"),
        ("replace",
         "        \"base_no_overrides_executor\",\n"
         "        \"override_targeting\",\n"
         "        \"override_plan_signature\",\n"
         "        \"override_path_registry\",\n"
         "        \"override_plan_rows\",\n"
         "        \"override_root_spell_id\",\n"
         "        \"override_spell_lookup\",\n"
         "        \"override_empty_shape_key\",\n"
         "        \"override_baseline_executor\",\n"
         "        \"overrides_executor\",\n"
         "    ]\n",
         "        \"base_no_overrides_executor\",\n"
         "    ]\n"),
        ("replace",
         "            and initializes every family-local intermediate (root spell, base\n"
         "            no-overrides executor, the override-targeting fields, and the final\n"
         "            overrides executor) to None; the ordered steps populate them in\n"
         "            place.\n",
         "            and initializes the family-local intermediates (root spell and\n"
         "            base no-overrides executor) to None; the ordered steps populate\n"
         "            them in place. The override lane has no state here: override\n"
         "            melds compile their plans at meld time (2026-09-26).\n"),
        ("replace",
         "        self.base_no_overrides_executor: Optional[Callable[..., Any]] = None\n"
         "        self.override_targeting: Optional[Any] = None\n"
         "        self.override_plan_signature: Optional[Tuple[Any, ...]] = None\n"
         "        self.override_path_registry: Optional[Any] = None\n"
         "        self.override_plan_rows: Optional[Sequence[Dict[str, Any]]] = None\n"
         "        self.override_root_spell_id: Optional[str] = None\n"
         "        self.override_spell_lookup: Optional[Dict[str, Any]] = None\n"
         "        self.override_empty_shape_key: Optional[Tuple[Any, ...]] = None\n"
         "        self.override_baseline_executor: Optional[Callable[..., Any]] = None\n"
         "        self.overrides_executor: Optional[Callable[..., Any]] = None\n",
         "        self.base_no_overrides_executor: Optional[Callable[..., Any]] = None\n"),
    ],
    SC + "artifact_processor/data/spell_site_graph_analysis.py": [
        ("replace",
         "        A processor-owned section beside `injection_shape` and\n"
         "        `override_targeting_shape` in `SpellCodegenModel`.\n",
         "        A section beside `injection_shape` in `SpellCodegenModel`, fitted only\n"
         "        when a caller runs `SpellSiteGraphProcessorStrategy` on the model.\n"),
        ("replace",
         "        Phase 9 (artifact processor) of the conjure pipeline. Design step S1 of\n"
         "        the override site-plan lowering: nothing at run time reads it yet.\n",
         "        Built at the first override meld of a root by `SitePlanOverrideRuntime`\n"
         "        (design v2 S3), which resolves override keys against it; conjure does\n"
         "        not build it (2026-09-26).\n"),
    ],
    SC + "artifact_processor/strategies/spell_site_graph_processor_strategy.py": [
        ("replace",
         "        One of the `artifact_processor/strategies` family, registered directly\n"
         "        after `SpellInjectionProcessorStrategy`.\n",
         "        One of the `artifact_processor/strategies` family. Not in the default\n"
         "        processor chain since 2026-09-26: `SitePlanOverrideRuntime` calls\n"
         "        `build_site_graph` at the first override meld; `process` remains for\n"
         "        callers that fit the section on a model.\n"),
    ],
}


def main() -> None:
    """Check every target, then edit, delete and prune (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    missing = [rel for rel in DELETE if not (root / rel).is_file()]
    if missing:
        raise SystemExit(f"deletion targets missing: {missing}")
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _splice(data, edit, rel) if edit[0] == "splice" else _apply_one(data, edit, rel)
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))
    for rel in DELETE:
        if not check:
            (root / rel).unlink()
        print(("checked delete " if check else "deleted ") + rel)
    for rel in EMPTIED_DIRS:
        folder = root / rel
        leftovers = [p.name for p in folder.iterdir() if p.name != "__pycache__"] if folder.is_dir() else []
        if check:
            print(f"checked prune {rel} (other entries: {leftovers or 'none'})")
            continue
        if folder.is_dir() and not leftovers:
            shutil.rmtree(folder)
            print("pruned " + rel)


if __name__ == "__main__":
    main()
