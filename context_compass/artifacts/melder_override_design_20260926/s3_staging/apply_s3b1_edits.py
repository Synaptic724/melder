"""S3b-1: stop building and serializing the unused override lane (design v2 S3b).

Usage: python apply_s3b1_edits.py <tree_root> [--check]

After S3a the many_only and generalized override doors run SitePlanOverrideRuntime over the
no-overrides rows, so the Phase-9 targeting/site-graph sections, the many_only OVERRIDES plan and
the manifests' "overrides" section are built at every conjure and never read. This removes them
from conjure (edits only; deleting the dead modules is the separate S3b-2 step).

Edit kinds:
    ("replace", old, new)  old must match exactly once, in the file's own line endings.
    ("cut", start, stop)   delete from `start` up to (not including) `stop`; stop=None cuts to
                           end of file, dropping the blank lines before `start`.
Every anchor is checked for every file before anything is written.
"""

import pathlib
import sys

SC = "src/melder/aether/spellbook/spell_compiler/"
ST = SC + "codegen_creation_system/strategies/"

EDITS = {
    SC + "artifact_processor/spell_artifact_processor_strategy_builder.py": [
        ("replace",
         "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_override_targeting_processor_strategy import (\n"
         "    SpellOverrideTargetingProcessorStrategy,\n"
         ")\n",
         ""),
        ("replace",
         "from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_site_graph_processor_strategy import (\n"
         "    SpellSiteGraphProcessorStrategy,\n"
         ")\n",
         ""),
        ("replace",
         "            - Current defaults are the 3 occurrence-derived processor\n"
         "              strategies plus runtime, existence-occurrence, injection,\n"
         "              site-graph, and override-targeting fitting strategies.\n"
         "            - The site-graph strategy runs directly after injection because\n"
         "              it maps injection dependency keys to site indexes.\n",
         "            - Current defaults are the 3 occurrence-derived processor\n"
         "              strategies plus runtime, existence-occurrence, and injection\n"
         "              fitting strategies.\n"
         "            - The site-graph and override-targeting strategies are not\n"
         "              registered (2026-09-26): override melds compile one plan per\n"
         "              override key set from the no-overrides step rows at the first\n"
         "              override meld (`SitePlanOverrideRuntime`), which builds its site\n"
         "              graph through `SpellSiteGraphProcessorStrategy.build_site_graph`,\n"
         "              so conjure no longer fits either section.\n"),
        ("replace",
         "        injection_strategy = SpellInjectionProcessorStrategy()\n"
         "        site_graph_strategy = SpellSiteGraphProcessorStrategy()\n"
         "        override_targeting_strategy = SpellOverrideTargetingProcessorStrategy()\n",
         "        injection_strategy = SpellInjectionProcessorStrategy()\n"),
        ("replace",
         "        self._strategies_by_name[injection_strategy.strategy_id] = injection_strategy\n"
         "        self._strategies_by_name[site_graph_strategy.strategy_id] = site_graph_strategy\n"
         "        self._strategies_by_name[\n"
         "            override_targeting_strategy.strategy_id\n"
         "        ] = override_targeting_strategy\n",
         "        self._strategies_by_name[injection_strategy.strategy_id] = injection_strategy\n"),
    ],
    SC + "codegen_planner/strategies/spell_many_only_codegen_plan_strategy.py": [
        ("replace",
         "            Builds the no-overrides and overrides lane plans via\n"
         "            `ManyOnlyCodegenPlanBuilder` (the artifact argument is unused),\n"
         "            assigns them to `plan`, and stamps plan metadata (selected strategy\n"
         "            id, discovery reason, model section names). Mutates `plan` in place;\n"
         "            returns nothing.\n",
         "            Builds the no-overrides lane plan via `ManyOnlyCodegenPlanBuilder`\n"
         "            (the artifact argument is unused), assigns it to `plan`, and stamps\n"
         "            plan metadata (selected strategy id, discovery reason, model section\n"
         "            names). `plan.overrides_plan` stays None: override melds compile one\n"
         "            plan per override key set from the no-overrides step rows at the\n"
         "            first override meld (2026-09-26). Mutates `plan` in place; returns\n"
         "            nothing.\n"),
        ("replace",
         "                Plan object populated in place with both lanes and metadata.\n",
         "                Plan object populated in place with the no-overrides lane and\n"
         "                metadata.\n"),
        ("replace",
         "        overrides_builder = ManyOnlyCodegenPlanBuilder(\n"
         "            state=state,\n"
         "            plan_variant=ManyOnlyCodegenPlanVariant.OVERRIDES,\n"
         "        )\n"
         "        plan.no_overrides_plan = no_overrides_builder.build()\n"
         "        plan.overrides_plan = overrides_builder.build()\n",
         "        plan.no_overrides_plan = no_overrides_builder.build()\n"),
    ],
    ST + "many_only/manifest/many_only_manifest.py": [
        ("replace",
         "The manifest captures both runtime lanes as pure data: the no-overrides lane\n"
         "as the exact Codegen IR payload the many_only compiler's public\n"
         "`codegen_ir` entrypoint consumes (steps rows + unrolled transient schema),\n"
         "and the overrides lane as the row/targeting/signature inputs the many_only\n"
         "override runtime rebuilds from at first meld.\n",
         "The manifest captures the no-overrides runtime lane as pure data: the exact\n"
         "Codegen IR payload the many_only compiler's public `codegen_ir` entrypoint\n"
         "consumes (steps rows + unrolled transient schema). Override melds compile one\n"
         "plan per override key set from those same rows at the first override meld, so\n"
         "the manifest carries no override section (version 4, 2026-09-26).\n"),
        ("replace",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import (\n"
         "    ManyOnlyCodegenCreationHelpers,\n"
         ")\n",
         ""),
        ("replace",
         "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_finalize_creation_context_step import (\n"
         "    ManyOnlyFinalizeCreationContextStep,\n"
         ")\n",
         ""),
        ("replace",
         "MANIFEST_VERSION = 3\n",
         "# Version 4: no override section; override melds compile from the no-overrides\n"
         "# rows (2026-09-26). Version-3 manifests fail validation and regenerate as cold\n"
         "# cache.\n"
         "MANIFEST_VERSION = 4\n"),
        ("replace",
         "            When required lane plans or the targeting shape are missing.\n"
         "    \"\"\"\n"
         "    no_overrides_plan = spell_codegen_plan.no_overrides_plan\n"
         "    if no_overrides_plan is None:\n"
         "        raise RuntimeError(\n"
         "            \"many_only manifest requires a no_overrides_plan.\"\n"
         "        )\n"
         "    overrides_plan = spell_codegen_plan.overrides_plan\n"
         "    if overrides_plan is None:\n"
         "        raise RuntimeError(\n"
         "            \"many_only manifest requires an overrides_plan.\"\n"
         "        )\n"
         "    override_targeting_shape = spell_codegen_model.override_targeting_shape\n"
         "    if override_targeting_shape is None:\n"
         "        raise RuntimeError(\n"
         "            \"many_only manifest requires override_targeting_shape.\"\n"
         "        )\n",
         "            When the no-overrides lane plan is missing.\n"
         "    \"\"\"\n"
         "    no_overrides_plan = spell_codegen_plan.no_overrides_plan\n"
         "    if no_overrides_plan is None:\n"
         "        raise RuntimeError(\n"
         "            \"many_only manifest requires a no_overrides_plan.\"\n"
         "        )\n"),
        ("replace",
         "    override_steps = tuple(overrides_plan.steps)\n"
         "    plan_rows = tuple(\n"
         "        ManyOnlyCodegenCreationHelpers.build_override_step_row(step)\n"
         "        for step in override_steps\n"
         "    )\n"
         "    plan_signature = (\n"
         "        ManyOnlyFinalizeCreationContextStep._build_override_plan_signature(\n"
         "            overrides_plan=overrides_plan,\n"
         "            plan_rows=plan_rows,\n"
         "        )\n"
         "    )\n"
         "\n"
         "    return {\n",
         "    return {\n"),
        ("replace",
         "        },\n"
         "        \"overrides\": {\n"
         "            \"lane_id\": overrides_plan.lane_id,\n"
         "            \"root_spell_id\": overrides_plan.root_spell_id,\n"
         "            \"step_spell_ids\": tuple(\n"
         "                step.spell.spell_index.selected_spell_id\n"
         "                for step in override_steps\n"
         "            ),\n"
         "            \"plan_rows\": plan_rows,\n"
         "            \"plan_signature\": plan_signature,\n"
         "            \"empty_shape_key\": (plan_signature, (), -1),\n"
         "            \"targets_by_spec\": serialize_targets_by_spec(\n"
         "                override_targeting_shape.targets_by_spec,\n"
         "            ),\n"
         "            \"specificity_by_spec\": dict(\n"
         "                override_targeting_shape.specificity_by_spec\n"
         "            ),\n"
         "        },\n"
         "    }\n",
         "        },\n"
         "    }\n"),
        ("cut", "def serialize_targets_by_spec(", "def validate_many_only_manifest("),
        ("replace",
         "            \"no_overrides\",\n"
         "            \"overrides\",\n"
         "    ):\n",
         "            \"no_overrides\",\n"
         "    ):\n"),
        ("replace",
         "    \"coerce_manifest_sequences\",\n"
         "    \"serialize_targets_by_spec\",\n",
         "    \"coerce_manifest_sequences\",\n"),
    ],
    ST + "generalized/manifest/generalized_manifest.py": [
        ("replace",
         "marshal-safe mapping holding every schema-only fact both runtime lanes need.\n",
         "marshal-safe mapping holding every schema-only fact the no-overrides runtime\n"
         "lane needs. Override melds compile one plan per override key set from the same\n"
         "rows at the first override meld, so there is no override section (version 4,\n"
         "2026-09-26).\n"),
        ("replace",
         "from typing import Any, Dict, Optional, Tuple\n",
         "from typing import Any, Dict, Optional\n"),
        ("replace",
         "# Version 3: rows carry `spell_has_disposal_methods` (bind-time spell truth)\n",
         "# Version 4: no override section; override melds compile from the no-overrides\n"
         "# rows (2026-09-26). Version-3 manifests fail validation and regenerate as cold\n"
         "# cache.\n"
         "# Version 3: rows carry `spell_has_disposal_methods` (bind-time spell truth)\n"),
        ("replace", "MANIFEST_VERSION = 3\n", "MANIFEST_VERSION = 4\n"),
        ("replace",
         "            When a required lane plan or targeting shape is missing.\n"
         "    \"\"\"\n"
         "    no_overrides_plan = spell_codegen_plan.no_overrides_plan\n"
         "    if no_overrides_plan is None:\n"
         "        raise RuntimeError(\n"
         "            \"generalized manifest requires a no_overrides_plan.\"\n"
         "        )\n"
         "    overrides_plan = spell_codegen_plan.overrides_plan\n"
         "    if overrides_plan is None:\n"
         "        raise RuntimeError(\n"
         "            \"generalized manifest requires an overrides_plan.\"\n"
         "        )\n"
         "    override_targeting_shape = spell_codegen_model.override_targeting_shape\n"
         "    if override_targeting_shape is None:\n"
         "        raise RuntimeError(\n"
         "            \"generalized manifest requires override_targeting_shape.\"\n"
         "        )\n",
         "            When the no-overrides lane plan is missing.\n"
         "    \"\"\"\n"
         "    no_overrides_plan = spell_codegen_plan.no_overrides_plan\n"
         "    if no_overrides_plan is None:\n"
         "        raise RuntimeError(\n"
         "            \"generalized manifest requires a no_overrides_plan.\"\n"
         "        )\n"),
        ("replace",
         "        \"no_overrides\": _build_no_overrides_lane_payload(\n"
         "            no_overrides_plan=no_overrides_plan,\n"
         "        ),\n"
         "        \"overrides\": _build_overrides_lane_payload(\n"
         "            overrides_plan=overrides_plan,\n"
         "            override_targeting_shape=override_targeting_shape,\n"
         "        ),\n"
         "    }\n",
         "        \"no_overrides\": _build_no_overrides_lane_payload(\n"
         "            no_overrides_plan=no_overrides_plan,\n"
         "        ),\n"
         "    }\n"),
        ("cut", "def _build_overrides_lane_payload(", "def build_no_overrides_executor_signature("),
        ("cut", "def build_override_plan_signature(", "def _enrich_phase11_row("),
        ("cut", "def serialize_targets_by_spec(", "def validate_generalized_manifest("),
        ("replace",
         "            \"no_overrides\",\n"
         "            \"overrides\",\n"
         "    ):\n",
         "            \"no_overrides\",\n"
         "    ):\n"),
    ],
}

LAZY_DOOR_EDITS = [
    ("replace",
     "        no_overrides_payload = manifest[\"no_overrides\"]\n"
     "        overrides_payload = manifest[\"overrides\"]\n",
     "        no_overrides_payload = manifest[\"no_overrides\"]\n"),
    ("replace",
     "        metadata[\"override_lane_id\"] = overrides_payload[\"lane_id\"]\n"
     "        metadata[\"override_root_spell_id\"] = overrides_payload[\"root_spell_id\"]\n"
     "        metadata[\"override_step_count\"] = len(overrides_payload[\"plan_rows\"])\n"
     "        metadata[\"override_steps_rows_signature\"] = (\n"
     "            overrides_payload[\"plan_signature\"][2]\n"
     "        )\n",
     ""),
]
EDITS[ST + "many_only/steps/many_only_lazy_door_step.py"] = list(LAZY_DOOR_EDITS)
EDITS[ST + "generalized/steps/generalized_lazy_door_step.py"] = list(LAZY_DOOR_EDITS)

EDITS[ST + "many_only/hydration/many_only_hydrator.py"] = [
    ("replace",
     "Codegen IR entrypoint (the manifest stores that IR verbatim). The override\n"
     "runtime is rebuilt through the bridged many_only finalize builder fed cached\n"
     "rows plus the live phase-5 path registry, mirroring the generalized family's\n"
     "hydration discipline.\n",
     "Codegen IR entrypoint (the manifest stores that IR verbatim). The override\n"
     "runtime is `SitePlanOverrideRuntime` over those same rows: one compiled plan\n"
     "per override key set, built at first use (2026-09-26), as in the generalized\n"
     "family.\n"),
    ("replace",
     "import threading\n"
     "from types import SimpleNamespace\n",
     "import threading\n"),
    ("replace",
     "from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (\n"
     "    SpellOverrideTargetRef,\n"
     ")\n"
     "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.artifacts.spell_override_targeting_codegen_creation import (\n"
     "    SpellOverrideTargetingCodegenCreation,\n"
     ")\n",
     ""),
    ("replace",
     "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_overrides_codegen_creation_compiler import (\n"
     "    compile_overrides_codegen_creation_executor,\n"
     ")\n",
     ""),
    ("replace",
     "    coerce_manifest_sequences,\n"
     "    validate_many_only_manifest,\n"
     ")\n"
     "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_finalize_creation_context_step import (\n"
     "    ManyOnlyFinalizeCreationContextStep,\n"
     ")\n",
     "    validate_many_only_manifest,\n"
     ")\n"),
    ("replace",
     "from melder.utilities.general_base.cleanable import Cleanable\n"
     "\n"
     "# Null model stand-in for the bridged override-runtime builder: it only reads\n"
     "# `graph_shape` when no explicit path registry is supplied.\n"
     "_NULL_MODEL = SimpleNamespace(graph_shape=None)\n",
     "from melder.utilities.general_base.cleanable import Cleanable\n"),
    ("cut", "def _resolve_live_path_registry(", None),
]

EDITS[ST + "generalized/hydration/generalized_hydrator.py"] = [
    ("replace",
     "    4. Build the family override runtime (process-wide shape source +\n"
     "       factory caches; per-spell bound-executor memo).\n",
     "    4. Build the family override runtime lazily at the first override meld:\n"
     "       `SitePlanOverrideRuntime` over the same no-overrides rows, one\n"
     "       compiled plan per override key set (2026-09-26).\n"),
    ("replace",
     "from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (\n"
     "    SpellOverrideTargetRef,\n"
     ")\n"
     "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_library import (\n"
     "    SpellOverrideTargetingCodegenCreation,\n"
     ")\n",
     ""),
    ("replace",
     "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_overrides_runtime import (\n"
     "    build_overrides_execute_runtime,\n"
     ")\n"
     "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_rows import (\n"
     "    build_runtime_rows,\n"
     ")\n",
     ""),
    ("replace",
     "    coerce_manifest_sequences,\n"
     "    validate_generalized_manifest,\n",
     "    validate_generalized_manifest,\n"),
    ("cut", "def _deserialize_targets_by_spec(", "def _build_lazy_overrides_door("),
    ("replace",
     "        Defer the overrides-lane hydration cost (runtime rows, override\n"
     "        targeting deserialization, root-instance-key resolution, and the\n"
     "        override execute-runtime build) from FIRST MELD to FIRST OVERRIDE\n"
     "        MELD, so override-free workloads never pay for the lane at all.\n",
     "        Defer the overrides-lane hydration cost (no-overrides row hydration,\n"
     "        root-instance-key resolution, and the key-set plan runtime build)\n"
     "        from FIRST MELD to FIRST OVERRIDE MELD, so override-free workloads\n"
     "        never pay for the lane at all.\n"),
    ("replace",
     "            Validated family manifest carrying the overrides lane payload.\n",
     "            Validated family manifest; its no-overrides rows feed the\n"
     "            override runtime.\n"),
]

EDITS["src/melder/utilities/caching_system/caching_system.py"] = [
    ("replace",
     "    # Version 13: each member of a collection parameter gets its own compiler\n",
     "    # Version 14: many_only and generalized manifests (version 4) carry no\n"
     "    # override section and conjure no longer fits the Phase-9 override\n"
     "    # targeting or site-graph sections; override melds compile one plan per key\n"
     "    # set from the no-overrides rows (2026-09-26). Version-13 bundles hold\n"
     "    # version-3 manifests that the family validators reject.\n"
     "    # Version 13: each member of a collection parameter gets its own compiler\n"),
    ("replace",
     "        13: \"collection_member_paths\",\n",
     "        13: \"collection_member_paths\",\n"
     "        14: \"override_site_plan_lanes\",\n"),
]


def _line_ending_at(data: str, index: int) -> str:
    """Return the terminator of the line containing `index` ("\\r\\n" or "\\n")."""
    end = data.find("\n", index)
    if end > 0 and data[end - 1] == "\r":
        return "\r\n"
    return "\n"


def _find_once(data: str, text: str, rel: str) -> tuple:
    """Locate `text` exactly once (either line-ending form) or exit naming the anchor."""
    hits = []
    for nl in ("\r\n", "\n"):
        variant = text.replace("\n", nl)
        count = data.count(variant)
        if count > 1:
            raise SystemExit(f"{rel}: anchor matched {count} times: {text[:70]!r}")
        if count == 1:
            hits.append((data.index(variant), variant))
    if not hits:
        raise SystemExit(f"{rel}: anchor not found: {text[:70]!r}")
    return hits[0][0], hits[0][1]


def _apply_one(data: str, edit: tuple, rel: str) -> str:
    """Apply one edit to `data` and return the new text."""
    kind = edit[0]
    if kind == "replace":
        _, old, new = edit
        index, variant = _find_once(data, old, rel)
        nl = _line_ending_at(data, index)
        return data[:index] + new.replace("\n", nl) + data[index + len(variant):]
    _, start, stop = edit
    start_index, _ = _find_once(data, start, rel)
    if stop is None:
        nl = _line_ending_at(data, start_index)
        return data[:start_index].rstrip("\r\n") + nl
    stop_index = data.find(stop, start_index)
    if stop_index < 0 or data.count(stop) != 1:
        raise SystemExit(f"{rel}: cut stop not unique after start: {stop!r}")
    return data[:start_index] + data[stop_index:]


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
