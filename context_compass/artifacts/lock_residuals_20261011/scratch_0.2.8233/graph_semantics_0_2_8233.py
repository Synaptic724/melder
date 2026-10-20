"""
Author the 0.2.8233 lines on the Spell and Spellbook graph nodes (descriptors are indent=1 JSON with a trailing
newline). Run before graph_walker --accept and assemble_graph.

Usage: python graph_semantics_0_2_8233.py <context_compass/system_docs/graph>
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path(sys.argv[1])


def author(rel: str, node_id: str, add: list[str], owns: list[str]) -> None:
    path = GRAPH / rel
    raw = path.read_bytes().decode("utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) + "\n" == raw, f"{rel}: unexpected formatting"
    node = data["nodes"][node_id]
    for line in add:
        assert line not in node["responsibilities"]
        node["responsibilities"].append(line)
    for name in owns:
        assert name not in node["owns_state"]
        node["owns_state"].append(name)
    path.write_bytes((json.dumps(data, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print("authored", node_id)


author(
    "melder/aether/spellbook/spell.json",
    "melder.aether.spellbook.spell.Spell",
    ["on a direct cleanup removes itself through its Spellbook outside its own lock, serialized per spell by a removal "
     "lock nothing else takes, so Book teardown and conjure, which take its lock under the Book lock, never wait on "
     "it (_direct_removal_route, 0.2.8233)"],
    ["_removal_lock"],
)
author(
    "melder/aether/spellbook/spellbook.json",
    "melder.aether.spellbook.spellbook.Spellbook",
    ["re-checks under its lock a Book torn down while a removal waited for it (cleanup_and_remove_spell): a spell the "
     "teardown cleaned returns, anything else raises the cleaned-Book RuntimeError (0.2.8233)"],
    [],
)
