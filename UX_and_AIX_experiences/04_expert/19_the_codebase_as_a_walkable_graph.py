"""
TIER: expert (19)
GOAL: THE GRAPH DOCUMENTS. Expert 18 addressed prose by section. The two
      graph documents carry the same prose surface AND a real graph:
      nodes, edges, traversal, and blast radius - answered at import,
      with nothing conjured.

        md.__graph_network__    the graph
        md.__graph_details__    the prose about what the graph names

      THE ONE THAT CHANGES HOW YOU WORK
        graph.node_at(source_path, line)
      You have a traceback. You have `file.py:412`. That call turns a
      line number into the NODE that encloses it, and from there
      `impact()` tells you what else moves if you change it. Stack trace
      to blast radius without leaving the process.

      EVERY EDGE EXPLAINS ITSELF
        Edge(source, relation, target, cardinality, phase, origin, why)
      Two fields there are unusual and both are the point:
        `why`    - the justification for the edge, carried WITH it
        `origin` - `authored` or `derived`: did a human assert this, or
                   did a tool infer it?
      `origin` is a TRUST FILTER you can pass to `walk()` and `impact()`.
      Walk only `authored` when you need what someone meant; walk only
      `derived` when you need what the machine can prove. A graph that
      cannot tell you which is which forces you to trust all of it
      equally, which in practice means trusting none of it.

      AND GUESSES DO NOT SHIP. `edge_count` excludes extractor
      candidates - the leads over-generate roughly eightfold and never
      reach the adjacency table. What you walk is evidence.

      `walk()` YIELDS, AND THAT IS A CONTEXT BUDGET DECISION
      It is a generator "so an agent can stop at the first useful hop
      instead of materialising a subgraph it will discard" - expert 18's
      law again, one grain up. Breadth-first, so shallow relationships
      arrive first and stopping early stops at the RIGHT things.

      TWO GUARANTEES THAT MAKE A WALK SAFE
        - CYCLES ARE HANDLED. `borrows` and `used_by` run both ways, so
          the graph has cycles and every node is expanded at most once.
          An unguarded walk would not terminate.
        - AN EDGE TO AN UNKNOWN NODE IS STILL YIELDED, then not expanded.
          "The relationship is real even where the target is not
          described here." A graph that hid those edges would quietly
          understate what touches what.

      IMPACT IS MEASURED IN FILES
        impact(node_id) -> Impact(source, hops, nodes, edges)
      Ranked by PROXIMITY, nearest first. Not "here are 400 symbols" -
      here are the files, in the order you should look at them, in the
      unit you actually open and edit.

      AND THE TWO DOCUMENTS JOIN
        details_key(node_id)  -> the section key in the details document
        describe(node_id)     -> that section's text
      A node in the network document addresses prose in the other one.
      That is why they ship as a pair.
SURFACE EXERCISED: md.__graph_network__ / __graph_details__ -
                   node_count, edge_count, relations, node_ids, node,
                   find_nodes, nodes_in, node_at, edges_from, edges_to,
                   neighbors, walk, impact, details_key, describe
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


def main() -> None:
    graph = md.__graph_network__
    print("__graph_network__ ->", type(graph).__name__,
          " available =", graph.available)
    if not graph.available:
        print("   did not ship:", graph.reason)
        print("   it still ANSWERS - refused is not missing (expert 18)")
        return

    # THE SHAPE, BEFORE ANY TRAVERSAL. Note edge_count excludes extractor
    # candidates: what you can walk is evidence, not leads.
    print()
    print("nodes:", graph.node_count, " edges:", graph.edge_count,
          " (candidates excluded - guesses do not ship)")
    print("relations:", ", ".join(graph.relations))

    node_ids = graph.node_ids()
    assert len(node_ids) == graph.node_count
    print("node_ids():", len(node_ids), "sorted ids")

    # PICK A REAL NODE and read its record.
    start = node_ids[0]
    node = graph.node(start)
    print()
    print("node:", node.node_id)
    print(f"   {node.kind} {node.name!r} at {node.source}:{node.line}"
          f"  unsemantic={node.unsemantic}")

    # TRACEBACK -> NODE. This is the move worth remembering: a file and a
    # line become the thing that encloses them.
    enclosing = graph.node_at(node.source, node.line)
    assert enclosing is not None
    print()
    print(f"node_at({node.source!r}, {node.line}) ->", enclosing.node_id)
    print("   a stack-trace line, resolved to the node that owns it")

    # EVERY NODE DEFINED IN THAT FILE, in definition order.
    same_file = graph.nodes_in(node.source)
    assert any(n.node_id == node.node_id for n in same_file)
    print(f"nodes_in({node.source!r}) ->", len(same_file), "nodes")

    # EDGES EXPLAIN THEMSELVES. `why` carries the justification and
    # `origin` says whether a human asserted it or a tool derived it.
    outbound = graph.edges_from(start)
    inbound = graph.edges_to(start)
    print()
    print(f"edges_from: {len(outbound)}   edges_to: {len(inbound)}")
    for edge in outbound[:2]:
        print(f"   -{edge.relation}-> {edge.target}")
        print(f"      origin={edge.origin} phase={edge.phase} "
              f"cardinality={edge.cardinality}")
        if edge.why:
            print(f"      why: {edge.why[:60]}")

    # ONE STEP OUT, THEN A BOUNDED WALK. The walk is a GENERATOR - stop
    # when you have enough instead of building a subgraph you discard.
    neighbours = graph.neighbors(start, direction="both")
    print()
    print("neighbors(both):", len(neighbours))

    seen = 0
    for _ in graph.walk(start, depth=2, direction="both"):
        seen += 1
        if seen >= 5:
            break
    print("walk(depth=2): stopped after", seen, "hops - breadth-first,")
    print("   so the shallow relationships were the ones I got")

    # THE TRUST FILTER. Same walk, restricted to what a human asserted.
    authored = sum(1 for _ in graph.walk(start, depth=1, origin="authored"))
    derived = sum(1 for _ in graph.walk(start, depth=1, origin="derived"))
    print()
    print(f"depth-1 authored: {authored}   derived: {derived}")
    print("   a graph that cannot separate asserted from inferred makes")
    print("   you trust all of it equally, which means trusting none")

    # BLAST RADIUS, IN FILES, NEAREST FIRST.
    radius = graph.impact(start, depth=2)
    print()
    print("impact(depth=2) ->", len(radius), "files affected")
    for item in radius[:3]:
        print(f"   {item.hops} hop(s)  {item.source}"
              f"  ({len(item.nodes)} nodes, {item.edges} edges)")
    print("   ranked by proximity - the unit you actually open and edit")

    # THE PAIR JOINS. A node here addresses prose in the other document.
    key = graph.details_key(start)
    prose = graph.describe(start)
    print()
    print("details_key ->", key)
    print("describe    ->", len(prose), "chars of prose about that file")
    print("   which is why the two graph documents ship as a pair")

    print()
    print("a line number becomes a node; a node becomes a blast radius")
    print("edges carry their own justification and their own provenance")
    print("and the walk yields, so you can stop when you know enough")


if __name__ == "__main__":
    main()
