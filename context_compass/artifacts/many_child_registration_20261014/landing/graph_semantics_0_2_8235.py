"""
Author the 0.2.8235 lines on the SitePlanEmission, generalized_manifest_no_overrides_compiler and generalized_hydrator
graph nodes (descriptors are indent=1 JSON with a trailing newline). Run after extract_graph and before
graph_walker --accept and assemble_graph. (TASK-2026-10-14-fix_many_child_follows_holder)

Usage: python graph_semantics_0_2_8235.py <context_compass/system_docs/graph>
"""
import json
import pathlib
import sys
from typing import List

GRAPH = pathlib.Path(sys.argv[1])
BASE = "melder/aether/spellbook/spell_compiler/codegen_creation_system/"
NODE = "melder.aether.spellbook.spell_compiler.codegen_creation_system."


def author(rel: str, node_id: str, *, replace: List[tuple] = (), add: List[str] = ()) -> None:
    """Rewrite one node's authored responsibilities in place; every replaced entry must exist exactly once."""
    path = GRAPH / rel
    raw = path.read_bytes().decode("utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) + "\n" == raw, f"{rel}: unexpected formatting"
    node = data["nodes"][node_id]
    for old, new in replace:
        assert node["responsibilities"].count(old) == 1, old
        node["responsibilities"][node["responsibilities"].index(old)] = new
    for line in add:
        assert line not in node["responsibilities"]
        node["responsibilities"].append(line)
    path.write_bytes((json.dumps(data, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print("authored", node_id)


author(
    BASE + "shared_assets/site_plan_lowering.json",
    NODE + "shared_assets.site_plan_lowering.SitePlanEmission",
    add=["registers a disposal-bearing many site in the store that owns its context (holder-owned many children, "
         "0.2.8235): many_store, the meld's innermost scope, at the top level; c{i} inside shared site i's miss, so a "
         "slotted holder's many children are recorded and disposed with the holder's owner; a miss emits no "
         "innermost-scope prologue"],
)
author(
    BASE + "strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.json",
    NODE + "strategies.generalized.compilers.generalized_manifest_no_overrides_compiler",
    add=["decides which graphs the straight-line specializer can express: rows_feed_many_into_non_many_step is True "
         "when a many row feeds a non-many row, whose child only the site plan builds in the holder's first build "
         "(0.2.8235)"],
)
author(
    BASE + "strategies/generalized/hydration/generalized_hydrator.json",
    NODE + "strategies.generalized.hydration.generalized_hydrator",
    replace=[(
        "optionally installs the singleton warm-tail specializer, which deopts to the normal plan",
        "optionally installs the singleton warm-tail specializer, which deopts to the normal plan; it keeps the plain "
        "door for graphs with no capturable step, a root-only capture on a short-circuiting route, or a many step "
        "feeding a non-many step (0.2.8235)",
    )],
)
