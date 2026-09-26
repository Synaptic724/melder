"""Apply the S1 edits to spell_codegen_model.py, the processor strategy builder and the processor core test.

All three files use CRLF line endings; every replacement is written with the file's own line ending and
must match exactly once. Usage: python apply_s1_edits.py <repo_root> [src] [tests] (default: both).
"""
import pathlib
import sys

BASE = "src/melder/aether/spellbook/spell_compiler/artifact_processor/"

MODEL_EDITS = [
    (
        "    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis import (\n"
        "        SpellRuntimeAnalysis,\n"
        "    )\n",
        "    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis import (\n"
        "        SpellRuntimeAnalysis,\n"
        "    )\n"
        "    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (\n"
        "        SpellSiteGraphAnalysis,\n"
        "    )\n",
    ),
    (
        "        - `order_shape`, `instance_shape`, and `contract_shape` are processor-\n"
        "          owned sections populated by processor strategies.\n",
        "        - `order_shape`, `instance_shape`, and `contract_shape` are processor-\n"
        "          owned sections populated by processor strategies.\n"
        "        - `site_graph_shape` is the processor-owned physical site graph\n"
        "          (one site per instance key, full parameter tables, path counts)\n"
        "          that override key resolution walks instead of logical paths.\n",
    ),
    (
        "        \"override_targeting_shape\",\n"
        "        \"spell_runtime_shape\",\n"
        "        \"existence_occurrence_shape\",\n"
        "        \"node_count\",\n",
        "        \"override_targeting_shape\",\n"
        "        \"site_graph_shape\",\n"
        "        \"spell_runtime_shape\",\n"
        "        \"existence_occurrence_shape\",\n"
        "        \"node_count\",\n",
    ),
    (
        "            override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = None,\n",
        "            override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = None,\n"
        "            site_graph_shape: Optional[SpellSiteGraphAnalysis] = None,\n",
    ),
    (
        "              `injection_shape`, `override_targeting_shape`, and\n"
        "              `spell_runtime_shape` are\n",
        "              `injection_shape`, `override_targeting_shape`,\n"
        "              `site_graph_shape`, and `spell_runtime_shape` are\n",
    ),
    (
        "        self.override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = (\n"
        "            override_targeting_shape\n"
        "        )\n",
        "        self.override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = (\n"
        "            override_targeting_shape\n"
        "        )\n"
        "        self.site_graph_shape: Optional[SpellSiteGraphAnalysis] = site_graph_shape\n",
    ),
    (
        "              `override_targeting_shape`, and\n"
        "              `spell_runtime_shape`.\n",
        "              `override_targeting_shape`, `site_graph_shape`, and\n"
        "              `spell_runtime_shape`.\n",
    ),
    (
        "        if self.override_targeting_shape is not None:\n"
        "            try:\n"
        "                self.override_targeting_shape.cleanup()\n"
        "            except Exception:\n"
        "                pass\n",
        "        if self.override_targeting_shape is not None:\n"
        "            try:\n"
        "                self.override_targeting_shape.cleanup()\n"
        "            except Exception:\n"
        "                pass\n"
        "        if self.site_graph_shape is not None:\n"
        "            try:\n"
        "                self.site_graph_shape.cleanup()\n"
        "            except Exception:\n"
        "                pass\n",
    ),
    (
        "        del self.override_targeting_shape\n",
        "        del self.override_targeting_shape\n"
        "        del self.site_graph_shape\n",
    ),
    (
        "            \"override_targeting_shape\",\n"
        "            \"spell_runtime_shape\",\n",
        "            \"override_targeting_shape\",\n"
        "            \"site_graph_shape\",\n"
        "            \"spell_runtime_shape\",\n",
    ),
]

BUILDER_EDITS = [
    (
        "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy import (\n"
        "    SpellRuntimeProcessorStrategy,\n"
        ")\n",
        "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy import (\n"
        "    SpellRuntimeProcessorStrategy,\n"
        ")\n"
        "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_site_graph_processor_strategy import (\n"
        "    SpellSiteGraphProcessorStrategy,\n"
        ")\n",
    ),
    (
        "            - Current defaults are the 3 occurrence-derived processor\n"
        "              strategies plus runtime, injection, and override-targeting\n"
        "              fitting strategies.\n",
        "            - Current defaults are the 3 occurrence-derived processor\n"
        "              strategies plus runtime, existence-occurrence, injection,\n"
        "              site-graph, and override-targeting fitting strategies.\n"
        "            - The site-graph strategy runs directly after injection because\n"
        "              it maps injection dependency keys to site indexes.\n",
    ),
    (
        "        injection_strategy = SpellInjectionProcessorStrategy()\n",
        "        injection_strategy = SpellInjectionProcessorStrategy()\n"
        "        site_graph_strategy = SpellSiteGraphProcessorStrategy()\n",
    ),
    (
        "        self._strategies_by_name[injection_strategy.strategy_id] = injection_strategy\n",
        "        self._strategies_by_name[injection_strategy.strategy_id] = injection_strategy\n"
        "        self._strategies_by_name[site_graph_strategy.strategy_id] = site_graph_strategy\n",
    ),
]


def apply(path: pathlib.Path, edits: list) -> None:
    raw = path.read_bytes().decode("utf-8")
    if "\r\n" not in raw or raw.replace("\r\n", "").count("\n"):
        raise SystemExit(f"{path}: expected a pure CRLF file")
    text = raw
    for old, new in edits:
        old_crlf = old.replace("\n", "\r\n")
        new_crlf = new.replace("\n", "\r\n")
        count = text.count(old_crlf)
        if count != 1:
            raise SystemExit(f"{path}: anchor matched {count} times:\n{old}")
        text = text.replace(old_crlf, new_crlf)
    path.write_bytes(text.encode("utf-8"))
    print(f"edited {path}")


TEST_PATH = "tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py"

TEST_EDITS = [
    (
        "        \"spell_injection_processor\",\n"
        "        \"spell_override_targeting_processor\",\n",
        "        \"spell_injection_processor\",\n"
        "        \"spell_site_graph_processor\",\n"
        "        \"spell_override_targeting_processor\",\n",
    ),
    (
        "    override_targeting_shape = _CleanupTracker()\n"
        "    spell_runtime_shape = _CleanupTracker()\n",
        "    override_targeting_shape = _CleanupTracker()\n"
        "    site_graph_shape = _CleanupTracker()\n"
        "    spell_runtime_shape = _CleanupTracker()\n",
    ),
    (
        "        override_targeting_shape=override_targeting_shape,\n"
        "        spell_runtime_shape=spell_runtime_shape,\n",
        "        override_targeting_shape=override_targeting_shape,\n"
        "        site_graph_shape=site_graph_shape,\n"
        "        spell_runtime_shape=spell_runtime_shape,\n",
    ),
    (
        "        \"override_targeting_shape\",\n"
        "        \"spell_runtime_shape\",\n"
        "        \"existence_occurrence_shape\",\n",
        "        \"override_targeting_shape\",\n"
        "        \"site_graph_shape\",\n"
        "        \"spell_runtime_shape\",\n"
        "        \"existence_occurrence_shape\",\n",
    ),
    (
        "    assert override_targeting_shape.cleanup_called is True\n"
        "    assert spell_runtime_shape.cleanup_called is True\n",
        "    assert override_targeting_shape.cleanup_called is True\n"
        "    assert site_graph_shape.cleanup_called is True\n"
        "    assert spell_runtime_shape.cleanup_called is True\n",
    ),
]


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1])
    targets = sys.argv[2:] or ["src", "tests"]
    if "src" in targets:
        apply(root / BASE / "spell_codegen_model.py", MODEL_EDITS)
        apply(root / BASE / "spell_artifact_processor_strategy_builder.py", BUILDER_EDITS)
    if "tests" in targets:
        apply(root / TEST_PATH, TEST_EDITS)
