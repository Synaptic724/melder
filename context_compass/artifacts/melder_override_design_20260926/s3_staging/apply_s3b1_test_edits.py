"""S3b-1 test updates: tests that pinned the override lane conjure no longer builds.

Usage: python apply_s3b1_test_edits.py <tree_root> [--check]

Uses the edit engine of apply_s3b1_edits.py (same folder): every anchor must match exactly once,
in the file's own line endings, or nothing is written.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

UT = "tests/unit/melder/spellbook/spell_compiler/"
CT = "tests/component/melder/spellbook/"

SITE_GRAPH_IMPORT = (
    "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_site_graph_processor_strategy import (\n"
    "    SpellSiteGraphProcessorStrategy,\n"
    ")\n"
)
RESOLVER_IMPORT = (
    "from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (\n"
    "    OverrideKeyResolver,\n"
    ")\n"
)

EDITS = {
    UT + "test_spell_artifact_processor_core.py": [
        ("replace",
         "        \"spell_injection_processor\",\n"
         "        \"spell_site_graph_processor\",\n"
         "        \"spell_override_targeting_processor\",\n"
         "    )\n",
         "        \"spell_injection_processor\",\n"
         "    )\n"),
    ],
    UT + "test_spell_codegen_planner_core.py": [
        ("replace",
         "        (state, SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES),\n"
         "        (state, SpellGeneralizedCodegenPlanVariant.OVERRIDES),\n"
         "    ]\n"
         "    assert plan.no_overrides_plan == \"many_only:no_overrides\"\n"
         "    assert plan.overrides_plan == \"many_only:overrides\"\n",
         "        (state, SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES),\n"
         "    ]\n"
         "    assert plan.no_overrides_plan == \"many_only:no_overrides\"\n"
         "    # Override melds compile their own key-set plans from the no-overrides rows (S3b-1).\n"
         "    assert plan.overrides_plan is None\n"),
    ],
    CT + "test_spellbook_component_override_key_oracle.py": [
        ("replace",
         "the error raised. The one recorded difference: today's targeting keeps only the last member for a PATH\n"
         "through a collection; the resolver keeps every member.\n",
         "the error raised. The one recorded difference: today's targeting keeps only the last member for a PATH\n"
         "through a collection; the resolver keeps every member. Conjure no longer fits either Phase-9 section\n"
         "(S3b-1), so the oracle fits both on the conjured model itself; it retires with the targeting code.\n"),
        ("replace",
         RESOLVER_IMPORT,
         "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_override_targeting_processor_strategy import (\n"
         "    SpellOverrideTargetingProcessorStrategy,\n"
         ")\n"
         + SITE_GRAPH_IMPORT
         + RESOLVER_IMPORT),
        ("replace",
         "    assert selected is not None\n"
         "    return selected\n",
         "    assert selected is not None\n"
         "    _fit_override_sections(selected)\n"
         "    return selected\n"
         "\n"
         "\n"
         "def _fit_override_sections(spell: Spell) -> None:\n"
         "    \"\"\"Fit the two Phase-9 sections conjure no longer builds (S3b-1) on the conjured model.\"\"\"\n"
         "    artifact = spell._compiler_artifact\n"
         "    model = artifact._spell_codegen_model\n"
         "    SpellSiteGraphProcessorStrategy().process(spell, artifact, model)\n"
         "    SpellOverrideTargetingProcessorStrategy().process(spell, artifact, model)\n"),
    ],
    CT + "test_spellbook_component_override_required.py": [
        ("replace",
         "        plan = consumer._compiler_artifact._spell_codegen_plan\n"
         "        for variant in (plan.no_overrides_plan, plan.overrides_plan):\n",
         "        plan = consumer._compiler_artifact._spell_codegen_plan\n"
         "        variants = [plan.no_overrides_plan]\n"
         "        if family == \"many_only\":\n"
         "            # many_only plans no override lane since S3b-1: override melds compile from these rows.\n"
         "            assert plan.overrides_plan is None\n"
         "        else:\n"
         "            variants.append(plan.overrides_plan)\n"
         "        for variant in variants:\n"),
    ],
    CT + "test_spellbook_component_spell_crafter.py": [
        ("replace",
         "from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind\n",
         SITE_GRAPH_IMPORT
         + RESOLVER_IMPORT
         + "from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind\n"),
        ("replace",
         "        - A normal dependency produces an override patch target.\n",
         "        - A normal dependency is an override target (resolved through the\n"
         "          site graph since S3b-1).\n"),
        ("replace",
         "        override_targeting = model.override_targeting_shape\n"
         "\n"
         "        assert override_targeting is not None\n"
         "        assert \"*service\" in override_targeting.targets_by_spec\n"
         "\n"
         "        override_targets = override_targeting.targets_by_spec[\"*service\"]\n"
         "        assert len(override_targets) == 1\n"
         "        assert override_targets[0].param_name == \"service\"\n"
         "        assert override_targets[0].node_id == consumer_id\n",
         "        # Conjure no longer fits the override-targeting section (S3b-1); override keys resolve\n"
         "        # through the site graph the override runtime builds at the first override meld.\n"
         "        SpellSiteGraphProcessorStrategy().process(consumer_spell, artifact, model)\n"
         "        graph = model.site_graph_shape\n"
         "        resolution = OverrideKeyResolver.resolve(graph, (\"*service\",))\n"
         "        targets = resolution.targets_by_key[\"*service\"]\n"
         "        assert [(graph.sites[site].spell_id, name) for site, name in targets] == [\n"
         "            (consumer_id, \"service\"),\n"
         "        ]\n"),
    ],
    "tests/integration/melder/spellbook/test_cache_schema_version_integration.py": [
        ("replace",
         "    13: \"collection_member_paths\",\n",
         "    13: \"collection_member_paths\",\n"
         "    14: \"override_site_plan_lanes\",\n"),
    ],
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
