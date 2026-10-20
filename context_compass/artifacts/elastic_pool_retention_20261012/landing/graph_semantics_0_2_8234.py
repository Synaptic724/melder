"""
Author the 0.2.8234 lines on the AbstractElasticPool, ConduitPool, SpellSpacePool and Conduit graph nodes
(descriptors are indent=1 JSON with a trailing newline). Run after extract_graph and before graph_walker --accept
and assemble_graph.

Usage: python graph_semantics_0_2_8234.py <context_compass/system_docs/graph>
"""
import json
import pathlib
import sys
from typing import List

GRAPH = pathlib.Path(sys.argv[1])


def author(rel: str, node_id: str, *, role: str = "", replace: List[tuple] = (), add: List[str] = (),
           owns_replace: List[tuple] = (), owns_add: List[str] = ()) -> None:
    """Rewrite one node's authored fields in place; every replaced entry must exist exactly once."""
    path = GRAPH / rel
    raw = path.read_bytes().decode("utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) + "\n" == raw, f"{rel}: unexpected formatting"
    node = data["nodes"][node_id]
    if role:
        node["role"] = role
    for old, new in replace:
        assert node["responsibilities"].count(old) == 1, old
        node["responsibilities"][node["responsibilities"].index(old)] = new
    for line in add:
        assert line not in node["responsibilities"]
        node["responsibilities"].append(line)
    for old, new in owns_replace:
        assert node["owns_state"].count(old) == 1, old
        node["owns_state"][node["owns_state"].index(old)] = new
    for name in owns_add:
        assert name not in node["owns_state"]
        node["owns_state"].append(name)
    path.write_bytes((json.dumps(data, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print("authored", node_id)


author(
    "melder/utilities/general_base/abstract_elastic_pool.json",
    "melder.utilities.general_base.abstract_elastic_pool.AbstractElasticPool",
    role="Elastic object-pool base for expensive runtime shells: idle retention follows demand between a baseline "
         "and a ceiling.",
    replace=[(
        "stretches and decays advisory idle targets under changing demand",
        "records a miss as pressure; under pressure a return past the baseline raises the target to the idle count "
        "(up to max_idle) and trims only past max_idle; once settled the target decays one step per interval with "
        "catch-up, never below the baseline (0.2.8234)",
    )],
    add=[
        "keeps the within-baseline return to one append and compare, with no clock read and no lock",
        "trims the oldest surplus one decay step per return and destroys it outside the lock, re-pooling the rest "
        "of a trim when a destroy raises; a fixed-capacity pool evicts one per return without the clock",
    ],
    owns_replace=[("_last_expand_at", "_last_miss_at"), ("_last_decay_at", "_next_decay_at")],
    owns_add=["_decay_step"],
)
author(
    "melder/aether/conduit/conduit_pool.json",
    "melder.aether.conduit.conduit_pool.ConduitPool",
    replace=[(
        "destroys overflow lesser conduits through the permanent cleanup lane",
        "destroys surplus lessers (above the elastic target, or past max_idle under pressure) through the permanent "
        "cleanup lane, outside the pool lock (0.2.8234)",
    )],
    add=["records a miss when no idle lesser exists, so the elastic target follows the burst (0.2.8234)"],
)
author(
    "melder/aether/conduit/spell_space/spell_space_pool.json",
    "melder.aether.conduit.spell_space.spell_space_pool.SpellSpacePool",
    replace=[(
        "returns or destroys spellspaces according to fixed-capacity idle policy",
        "keeps returned spellspaces up to the elastic target and destroys the oldest surplus; records a miss when it "
        "builds one (0.2.8234)",
    )],
)
author(
    "melder/aether/conduit/conduit.json",
    "melder.aether.conduit.conduit.Conduit",
    add=["builds its SpellSpacePool and, as a normal root, its ConduitPool elastic: 20 idle always kept, up to 256 "
         "after a burst, decaying when quiet (0.2.8234)"],
)
