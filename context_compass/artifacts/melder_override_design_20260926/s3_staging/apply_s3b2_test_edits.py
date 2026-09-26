"""S3b-2 test updates: remove tests of deleted modules; move cache tests to the manifest path.

Usage: python apply_s3b2_test_edits.py <tree_root> [--check]

Per file: PRUNE drops top-level defs (by name, or every def that references a given module alias)
and the imports that bind the listed names, by AST line ranges in the file's own line endings;
then EDITS apply anchored replacements (engine of apply_s3b1_edits.py, plus "replace_all").
DELETE removes test files whose only subject is retired code.
"""

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one, _find_once, _line_ending_at

UT = "tests/unit/melder/spellbook/spell_compiler/"
UB = "tests/unit/melder/spellbook/"
CT = "tests/component/melder/spellbook/"

DELETE = [
    UT + "test_spell_codegen_cache_rehydration_exec.py",
    CT + "test_spellbook_component_override_key_oracle.py",
    "tests/experimentation/creation_context_cache_asset_playground.py",
    "tests/experimentation/test_creation_context_cache_asset_experiment.py",
    "tests/experimentation/test_creation_context_override_cache_asset_experiment.py",
]

PRUNE = {
    UT + "test_codegen_creation_core.py": {
        "defs": [
            "_make_generalized_state",
            "test_no_overrides_step_records_base_executor_and_signature",
            "test_overrides_step_records_override_runtime_state",
            "test_general_creation_context_strategy_preserves_base_no_overrides_and_builds_override_runtime",
        ],
        "imports": [
            "no_overrides_step_module", "overrides_step_module",
            "SpellOverrideTargetRef", "SpellOverrideTargetingCodegenCreation", "GeneralizedCodegenCreationState",
            "GeneralizedFinalizeCreationContextStep", "GeneralizedNoOverridesCodegenCreationStep",
            "GeneralizedOverridesCodegenCreationStep",
        ],
    },
    UT + "test_codegen_creation_compilers_core.py": {
        "defs": ["_make_overrides_step_row", "_OverrideSocketRef"],
        "referencing": ["overrides_compiler_module"],
        "imports": ["overrides_compiler_module"],
    },
    UT + "test_ordered_disposal_compiler.py": {
        "imports": [
            "generalized_overrides", "many_overrides", "_build_inner_no_overrides_executor",
            "_build_no_overrides_subpackage", "ManyOnlyCodegenCreationHelpers", "RLock",
        ],
    },
    UT + "test_codegen_creation_discovery_core.py": {
        "defs": ["test_fallback_no_overrides_codegen_creation_discovery_strategy_returns_fallback_result"],
        "imports": ["FallbackNoOverridesCodegenCreationDiscoveryStrategy"],
    },
    UT + "test_spell_artifact_processor_data_migrations.py": {
        "defs": ["test_override_targeting_analysis_replaces_override_patch_map_summary"],
        "imports": ["SpellOverrideTargetingAnalysis", "SpellOverrideTargetRef"],
    },
    UT + "test_spell_strategy_migrations.py": {
        "defs": [
            "test_override_targeting_processor_strategy_ports_patch_map_target_rows",
            "test_override_targeting_processor_strategy_helper_methods_port_patchmap_key_rules",
        ],
        "imports": ["SpellOverrideTargetingProcessorStrategy", "SocketKind", "TargetSpecKind"],
    },
    UT + "shared_assets/test_contract_override_refs.py": {
        "defs": ["test_legacy_package_builds_subpackages_for_an_object_payload_plan"],
        "imports": ["spell_codegen_creation_cache", "List"],
    },
    UB + "test_cache_runtime_verification.py": {
        "defs": [
            "test_resolve_route_key_for_spell_maps_supported_spell_routes",
            "test_resolve_route_key_for_spell_rejects_unknown_existence",
            "test_has_fast_transient_no_overrides_reflects_cached_schema",
        ],
    },
    CT + "test_codegen_signature_determinism.py": {
        "imports": ["build_legacy_package"],
    },
}

NO_FAMILY_TEST = (
    "    with pytest.raises(RuntimeError, match=\"could not select a creation discovery result\"):\n"
    "        CodegenCreationDiscoverySystem().discover(\n"
    "            object(),\n"
    "            SpellCodegenPlan(\n"
    "                processor_strategy_ids=(),\n"
    "                plan_strategy_ids=(),\n"
    "                no_overrides_plan=None,\n"
    "                overrides_plan=None,\n"
    "                metadata={\"selected_strategy_id\": \"other_plan\"},\n"
    "            ),\n"
    "        )\n"
)
FALLBACK_BODY = (
    "    discovery = CodegenCreationDiscoverySystem().discover(\n"
    "        object(),\n"
    "        SpellCodegenPlan(\n"
    "            processor_strategy_ids=(),\n"
    "            plan_strategy_ids=(),\n"
    "            no_overrides_plan=None,\n"
    "            overrides_plan=None,\n"
    "            metadata={\"selected_strategy_id\": \"other_plan\"},\n"
    "        ),\n"
    "    )\n"
    "\n"
    "    assert discovery.selected_strategy_ids == (\n"
    "        \"generalized_no_overrides_codegen_creation\",\n"
    "    )\n"
)
MANIFEST_MODULE = "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache"

EDITS = {
    UT + "test_codegen_creation_core.py": [
        ("replace",
         "def test_codegen_creation_discovery_system_falls_back_to_no_overrides_chain() -> None:\n"
         "    \"\"\"The discovery system should still fall back to the no-overrides strategy for non-generalized plans.\"\"\"\n"
         + FALLBACK_BODY,
         "def test_codegen_creation_discovery_system_rejects_a_plan_no_family_claims() -> None:\n"
         "    \"\"\"A plan none of the three families claims fails discovery: there is no fallback family (2026-09-26).\"\"\"\n"
         + NO_FAMILY_TEST),
        ("replace",
         "    \"\"\"The real strategy builder should expose solo, many-only, generalized, and fallback creation families.\"\"\"\n",
         "    \"\"\"The real strategy builder should expose the solo, many-only and generalized creation families.\"\"\"\n"),
        ("replace",
         "        \"generalized_codegen_creation\",\n"
         "        \"generalized_no_overrides_codegen_creation\",\n"
         "    )\n",
         "        \"generalized_codegen_creation\",\n"
         "    )\n"),
    ],
    UT + "test_codegen_creation_discovery_core.py": [
        ("replace",
         "    \"\"\"The phase-11 discovery builder should register the solo, many-only, generalized, and fallback strategies in order.\"\"\"\n",
         "    \"\"\"The phase-11 discovery builder should register the solo, many-only and generalized strategies in order.\"\"\"\n"),
        ("replace",
         "        \"generalized_codegen_creation_discovery\",\n"
         "        \"fallback_no_overrides_codegen_creation_discovery\",\n"
         "    )\n",
         "        \"generalized_codegen_creation_discovery\",\n"
         "    )\n"),
        ("replace",
         "    assert isinstance(\n"
         "        builder.get_strategy(\"fallback_no_overrides_codegen_creation_discovery\"),\n"
         "        FallbackNoOverridesCodegenCreationDiscoveryStrategy,\n"
         "    )\n",
         ""),
    ],
    CT + "spell_compiler/test_codegen_discovery_pipeline_component.py": [
        ("replace",
         "from typing import Any, Tuple\n",
         "from typing import Any, Tuple\n"
         "\n"
         "import pytest\n"),
        ("replace",
         "def test_component_codegen_creation_discovery_system_uses_fallback_chain_for_non_generalized_plan() -> None:\n"
         "    \"\"\"The real phase-11 discovery system should still fall back to the no-overrides chain for non-generalized planner output.\"\"\"\n"
         + FALLBACK_BODY
         + "    assert discovery.discovery_reason == \"fallback_no_overrides_creation_strategy\"\n",
         "def test_component_codegen_creation_discovery_system_rejects_a_plan_no_family_claims() -> None:\n"
         "    \"\"\"The real phase-11 discovery system has no fallback family: an unclaimed plan fails (2026-09-26).\"\"\"\n"
         + NO_FAMILY_TEST),
        ("replace",
         "                metadata={\"selected_strategy_id\": \"other_plan\"},\n"
         "            ),\n"
         "            \"_spell_codegen_creation\": None,\n"
         "        },\n"
         "    )()\n"
         "\n"
         "    system.build(artifact)\n"
         "\n"
         "    assert artifact._spell_codegen_creation.selected_strategy_ids == (\n"
         "        \"generalized_no_overrides_codegen_creation\",\n"
         "    )\n"
         "    assert artifact._spell_codegen_creation.metadata[\"component_creation_applied\"] == (\n"
         "        \"generalized_no_overrides_codegen_creation\"\n"
         "    )\n",
         "                metadata={\"selected_strategy_id\": \"generalized_codegen_plan\"},\n"
         "            ),\n"
         "            \"_spell_codegen_creation\": None,\n"
         "        },\n"
         "    )()\n"
         "\n"
         "    system.build(artifact)\n"
         "\n"
         "    assert artifact._spell_codegen_creation.selected_strategy_ids == (\n"
         "        \"generalized_codegen_creation\",\n"
         "    )\n"
         "    assert artifact._spell_codegen_creation.metadata[\"component_creation_applied\"] == (\n"
         "        \"generalized_codegen_creation\"\n"
         "    )\n"),
    ],
    UT + "test_ordered_disposal_compiler.py": [
        ("replace",
         "@pytest.mark.parametrize(\"family\", [\"generalized\", \"many_only\"])\n"
         "@pytest.mark.parametrize(\"overrides\", [False, True])\n"
         "def test_family_executors_register_current_lists(family: str, overrides: bool) -> None:\n"
         "    \"\"\"Both non-solo families and override lanes register exact live lists across repeated compilation.\"\"\"\n",
         "@pytest.mark.parametrize(\"family\", [\"generalized\", \"many_only\"])\n"
         "def test_family_executors_register_current_lists(family: str) -> None:\n"
         "    \"\"\"Both non-solo families register exact live lists across repeated compilation.\n"
         "\n"
         "    Override melds build from the same no-overrides rows (SitePlanOverrideRuntime); their\n"
         "    registration is covered in shared_assets/test_site_plan_lowering.py.\n"
         "    \"\"\"\n"),
        ("replace",
         "                plan = ManyOnlyCodegenPlanBuilder(\n"
         "                    state=model,\n"
         "                    plan_variant=(ManyOnlyCodegenPlanVariant.OVERRIDES if overrides\n"
         "                                  else ManyOnlyCodegenPlanVariant.NO_OVERRIDES),\n"
         "                ).build()\n"
         "                compiler = many_overrides if overrides else many_no\n",
         "                plan = ManyOnlyCodegenPlanBuilder(\n"
         "                    state=model, plan_variant=ManyOnlyCodegenPlanVariant.NO_OVERRIDES,\n"
         "                ).build()\n"
         "                compiler = many_no\n"),
        ("replace",
         "                plan = SpellGeneralizedCodegenPlanBuilder(\n"
         "                    state=model,\n"
         "                    plan_variant=(SpellGeneralizedCodegenPlanVariant.OVERRIDES if overrides\n"
         "                                  else SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES),\n"
         "                ).build()\n"
         "                compiler = generalized_overrides if overrides else generalized_no\n"
         "            if overrides:\n"
         "                executor = compiler.compile_overrides_codegen_creation_executor(\n"
         "                    execution_plan=plan, override_targets_by_spell_id={},\n"
         "                    any_overrides_present=False, path_registry=model.graph_shape.path_registry,\n"
         "                    plan_rows=(\n"
         "                        [ManyOnlyCodegenCreationHelpers.build_override_step_row(step) for step in plan.steps]\n"
         "                        if family == \"many_only\" else None\n"
         "                    ),\n"
         "                    root_spell_id=\"root\", spell_lookup=pool,\n"
         "                )\n"
         "            else:\n"
         "                executor = compiler.compile_no_overrides_codegen_creation_executor_from_plan(plan=plan)\n"
         "            store = _make_recording_creations()\n"
         "            # The generic override executor uses the real store's lock contract.\n"
         "            store._lock = RLock()\n"
         "            result = executor(_meld_for(store), {}, None) if overrides else executor(_meld_for(store))\n"
         "            assert result == \"root:base\"\n",
         "                plan = SpellGeneralizedCodegenPlanBuilder(\n"
         "                    state=model, plan_variant=SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES,\n"
         "                ).build()\n"
         "                compiler = generalized_no\n"
         "            executor = compiler.compile_no_overrides_codegen_creation_executor_from_plan(plan=plan)\n"
         "            store = _make_recording_creations()\n"
         "            assert executor(_meld_for(store)) == \"root:base\"\n"),
        ("replace",
         "    \"\"\"A marshal-safe cache keeps ordered values, while stored-code hydration binds fresh live lists.\"\"\"\n",
         "    \"\"\"A marshal-safe manifest keeps ordered values, while row hydration binds fresh live lists.\"\"\"\n"),
        ("replace",
         "        package = marshal.loads(marshal.dumps({\n"
         "            \"no_overrides\": _build_no_overrides_subpackage(no_overrides_plan=plan),\n"
         "        }))\n"
         "        fresh_pool = {spell_id: _spell(spell_id, list(names)) for spell_id in pool}\n"
         "        fresh_pool[\"root\"]._spellbook = SimpleNamespace(_spell_id_pool=fresh_pool)\n"
         "        executor = _build_inner_no_overrides_executor(fresh_pool[\"root\"], package)\n",
         "        payload = marshal.loads(marshal.dumps(\n"
         "            generalized_manifest._build_no_overrides_lane_payload(no_overrides_plan=plan),\n"
         "        ))\n"
         "        fresh_pool = {spell_id: _spell(spell_id, list(names)) for spell_id in pool}\n"
         "        executor = hydrate_no_overrides_executor(\n"
         "            rows=payload[\"steps_rows\"],\n"
         "            transient_schema=payload[\"transient_schema\"],\n"
         "            root_instance_key=payload[\"root_instance_key\"],\n"
         "            root_spell_id=payload[\"root_spell_id\"],\n"
         "            spell_lookup=fresh_pool,\n"
         "        )\n"),
        ("replace",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (\n"
         "    CodegenCreationSchemaHelpers,\n"
         ")\n",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (\n"
         "    CodegenCreationSchemaHelpers,\n"
         ")\n"
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (\n"
         "    hydrate_no_overrides_executor,\n"
         ")\n"
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.manifest import (\n"
         "    generalized_manifest,\n"
         ")\n"),
    ],
    UT + "test_spell_strategy_migrations.py": [
        ("replace", "        self.override_targeting_shape = None\n", ""),
    ],
    UT + "test_spell_artifact_processor_core.py": [
        ("replace",
         "    override_targeting_shape = _CleanupTracker()\n    site_graph_shape = _CleanupTracker()\n",
         "    site_graph_shape = _CleanupTracker()\n"),
        ("replace", "        override_targeting_shape=override_targeting_shape,\n", ""),
        ("replace",
         "        \"override_targeting_shape\",\n        \"site_graph_shape\",\n",
         "        \"site_graph_shape\",\n"),
        ("replace", "    assert override_targeting_shape.cleanup_called is True\n", ""),
    ],
    UT + "shared_assets/test_contract_override_refs.py": [
        ("replace",
         "(owner option B) is retired: both package builders package every plan.\n",
         "(owner option B) is retired: the manifest package builder packages every plan (the legacy\n"
         "non-manifest codec is retired too, 2026-09-26).\n"),
    ],
    UB + "test_cache_runtime_verification.py": [
        ("replace",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation import spell_codegen_creation_cache as creation_context_cache_codec\n",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets import manifest_creation_cache\n"),
        ("replace",
         "        spellbook\n"
         "    )\n"
         "    return spellbook\n",
         "        spellbook\n"
         "    )\n"
         "    return spellbook\n"
         "\n"
         "\n"
         "def _give_manifest(spell: _RecordingSpell) -> None:\n"
         "    \"\"\"Mark the stub's phase-11 creation as manifest-first, as every codegen family is.\"\"\"\n"
         "    spell._compiler_artifact._spell_codegen_creation.metadata[\n"
         "        manifest_creation_cache.MANIFEST_METADATA_KEY\n"
         "    ] = {}\n"),
        ("replace",
         "def test_emit_spell_cache_returns_false_when_package_build_fails(\n",
         "def test_emit_spell_cache_returns_false_without_a_manifest() -> None:\n"
         "    \"\"\"A creation without a manifest has no cache payload (the legacy codec is retired).\"\"\"\n"
         "    caching_system = _StubCachingSystem()\n"
         "    spellbook = _make_spellbook_stub(\n"
         "        live_spell_ids=(),\n"
         "        caching_enabled=True,\n"
         "        caching_system=caching_system,\n"
         "    )\n"
         "    spell = _RecordingSpell()\n"
         "    spell._spellbook = spellbook\n"
         "\n"
         "    assert Spellbook._emit_spell_cache(spellbook, spell) is False\n"
         "    assert caching_system.has_spell_payload(spell.spell_id) is False\n"
         "    assert spellbook._cache_emit_required is False\n"
         "\n"
         "\n"
         "def test_emit_spell_cache_returns_false_when_package_build_fails(\n"),
        ("replace_all",
         "    monkeypatch.setattr(\n"
         "        creation_context_cache_codec,\n"
         "        \"build_package\",\n",
         "    _give_manifest(spell)\n"
         "    monkeypatch.setattr(\n"
         "        manifest_creation_cache,\n"
         "        \"build_package\",\n",
         3),
        ("replace_all",
         "    monkeypatch.setattr(\n"
         "        creation_context_cache_codec,\n"
         "        \"load_creation_context\",\n",
         "    monkeypatch.setattr(manifest_creation_cache, \"is_manifest_package\", lambda payload: True)\n"
         "    monkeypatch.setattr(\n"
         "        manifest_creation_cache,\n"
         "        \"load_creation_context_lazy\",\n",
         2),
    ],
    UB + "test_spellbook_creation_system_resolution_fastpath.py": [
        ("replace",
         "    monkeypatch.setattr(\n"
         "        \"melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache.load_creation_context\",\n"
         "        _fake_load_creation_context,\n"
         "    )\n",
         "    monkeypatch.setattr(\n"
         f"        \"{MANIFEST_MODULE}.is_manifest_package\",\n"
         "        lambda payload: True,\n"
         "    )\n"
         "    monkeypatch.setattr(\n"
         f"        \"{MANIFEST_MODULE}.load_creation_context_lazy\",\n"
         "        _fake_load_creation_context,\n"
         "    )\n"),
    ],
    CT + "test_codegen_signature_determinism.py": [
        ("replace",
         "        \"override_steps_rows_signature\": metadata.get(\"override_steps_rows_signature\"),\n",
         ""),
        ("replace",
         "    if creation.metadata.get(MANIFEST_METADATA_KEY) is not None:\n"
         "        return build_manifest_package(spell)\n"
         "    return build_legacy_package(spell)\n",
         "    if creation.metadata.get(MANIFEST_METADATA_KEY) is None:\n"
         "        raise RuntimeError(\"Every codegen family publishes a manifest; this spell has none.\")\n"
         "    return build_manifest_package(spell)\n"),
        ("replace",
         "    Return the no-overrides step rows of a cache package, manifest-first or legacy.\n",
         "    Return the no-overrides step rows of a manifest cache package.\n"),
        ("replace",
         "    if \"manifest\" in package:\n"
         "        return tuple(package[\"manifest\"][\"no_overrides\"][\"steps_rows\"])\n"
         "    return tuple(package[\"no_overrides\"][\"steps_rows\"])\n",
         "    return tuple(package[\"manifest\"][\"no_overrides\"][\"steps_rows\"])\n"),
    ],
}


def _names_in(node: ast.AST) -> set:
    """Every identifier a node reads (Name ids and the root of attribute chains)."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _prune(data: str, spec: dict, rel: str) -> str:
    """Drop the listed top-level defs and import bindings by line range.

    Lines keep their own endings (some test files mix CRLF and LF), so list index i - 1 is AST line i.
    """
    lines = re.findall(r"[^\n]*\n|[^\n]+$", data)
    tree = ast.parse(data.replace("\r\n", "\n"))
    drop_defs = set(spec.get("defs", ()))
    referencing = set(spec.get("referencing", ()))
    drop_imports = set(spec.get("imports", ()))
    removals = []
    replacements = {}
    found_defs = set()
    found_imports = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if node.name in drop_defs or (referencing and _names_in(node) & referencing):
                start = min([d.lineno for d in node.decorator_list] + [node.lineno])
                removals.append((start, node.end_lineno))
                found_defs.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            bound = [(a.asname or a.name.split(".")[0], a) for a in node.names]
            hit = [b for b, _ in bound if b in drop_imports]
            if not hit:
                continue
            found_imports.update(hit)
            keep = [a for b, a in bound if b not in drop_imports]
            if not keep:
                removals.append((node.lineno, node.end_lineno))
            elif isinstance(node, ast.ImportFrom):
                names = [a.name + (f" as {a.asname}" if a.asname else "") for a in keep]
                end = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
                if node.lineno == node.end_lineno:
                    text = [f"from {node.module} import {', '.join(names)}{end}"]
                else:
                    text = [f"from {node.module} import ({end}"] + [f"    {n},{end}" for n in names] + [f"){end}"]
                replacements[(node.lineno, node.end_lineno)] = text
            else:
                raise SystemExit(f"{rel}: cannot partially drop a plain import at line {node.lineno}")
    missing = (drop_defs - found_defs) | (drop_imports - found_imports)
    if missing:
        raise SystemExit(f"{rel}: prune targets not found: {sorted(missing)}")
    for (start, end), text in sorted(replacements.items(), reverse=True):
        lines[start - 1:end] = text
    for start, end in sorted(removals, reverse=True):
        stop = end
        while stop < len(lines) and lines[stop].strip() == "":
            stop += 1
        if stop >= len(lines):
            del lines[start - 1:]
            while lines and lines[-1].strip() == "":
                lines.pop()
        else:
            del lines[start - 1:stop]
    return "".join(lines)


def _replace_all(data: str, edit: tuple, rel: str) -> str:
    """Replace every occurrence of `old` and require exactly `count` of them."""
    _, old, new, count = edit
    for nl in ("\r\n", "\n"):
        variant = old.replace("\n", nl)
        if data.count(variant) == count:
            return data.replace(variant, new.replace("\n", nl))
    raise SystemExit(f"{rel}: replace_all expected {count} matches: {old[:60]!r}")


def main() -> None:
    """Check everything, then prune, edit and delete (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    missing = [rel for rel in DELETE if not (root / rel).is_file()]
    if missing:
        raise SystemExit(f"deletion targets missing: {missing}")
    pending = {}
    for rel in sorted(set(PRUNE) | set(EDITS)):
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        if rel in PRUNE:
            data = _prune(data, PRUNE[rel], rel)
        for edit in EDITS.get(rel, ()):
            data = _replace_all(data, edit, rel) if edit[0] == "replace_all" else _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))
    for rel in DELETE:
        if not check:
            (root / rel).unlink()
        print(("checked delete " if check else "deleted ") + rel)


if __name__ == "__main__":
    main()
