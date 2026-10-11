"""
Author the 0.2.8232 responsibility lines on the Spellbook and Conduit graph nodes (descriptors are indent=1 JSON with a
trailing newline). Run before graph_walker --accept and assemble_graph.

Usage: python graph_semantics_0_2_8232.py <context_compass/system_docs/graph>
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path(sys.argv[1])


def author(rel: str, node_id: str, replace: dict[str, str], add: list[str]) -> None:
    path = GRAPH / rel
    raw = path.read_bytes().decode("utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) + "\n" == raw, f"{rel}: unexpected formatting"
    node = data["nodes"][node_id]
    lines = node["responsibilities"]
    for old, new in replace.items():
        assert lines.count(old) == 1, old
        lines[lines.index(old)] = new
    for line in add:
        assert line not in lines
        lines.append(line)
    path.write_bytes((json.dumps(data, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print("authored", node_id)


author(
    "melder/aether/spellbook/spellbook.json",
    "melder.aether.spellbook.spellbook.Spellbook",
    {
        "disposes a spell under the Book lock and reports the index the disposal destroyed (_dispose_spell); a spell "
        "already disposed raises RuntimeError (0.2.8231)":
        "disposes a spell under the Book lock and reports the index the disposal destroyed (_dispose_spell); a spell "
        "already disposed raises RuntimeError (0.2.8231), and a second disposal of a spell while one runs is refused "
        "through an id mark kept under the Book lock (0.2.8232)",
    },
    ["inspects objects holding its lock only for its own spells and asks the frames with no lock held, over a "
     "one-call copy of the frame's conduits (inspect_spell, 0.2.8232)"],
)
author(
    "melder/aether/conduit/conduit.json",
    "melder.aether.conduit.conduit.Conduit",
    {},
    ["looks up contracted spells over a one-call copy of the Book's contracted peer ids and inspects objects, both "
     "with no conduit lock held (find_contracted_spell, inspect_spell, 0.2.8232)"],
)
