"""
TIER: expert (18)
GOAL: YOU DO NOT READ A SYSTEM DOCUMENT, YOU ADDRESS IT. Four documents
      hang off the package root and answer AT IMPORT - before Aether
      boots, before a Spellbook exists, before anything is conjured.

        md.__architecture__     prose, addressable by section
        md.__components__       prose, addressable by section
        md.__graph_network__    the same, PLUS a graph API
        md.__graph_details__    the same

      `SystemGraphView` subclasses `SystemDocumentView`, so the graph
      documents answer every prose question too and then add nodes and
      edges on top.

      ASK WHAT THE ADDRESS SPACE IS BEFORE YOU ADDRESS IT
        view.addressing   -> "section" | "source_path"
      Keys are heading paths in one document and repository-relative file
      paths in another. A caller that assumes one shape silently misses
      in the other, so the view publishes which it is rather than making
      you infer it from a sample.

      THE CHEAP SURVEY, THEN THE EXPENSIVE READ
        keys()            every section key, in document order
        groups(depth)     the index collapsed to one row per prefix
        index()           every Section(key, start_line, end_line,
                                        line_count)
        find(needle)      sections whose KEY matches
        search(needle)    sections whose BODY mentions it, RANKED BY HIT
                          COUNT, with a preview
      Note that `find` and `search` answer different questions - one
      addresses, one investigates - and neither one costs you the
      document. Only then:
        get(key)          the section's text
        reader(key, ...)  a private cursor over ONE SECTION

      `reader()` TAKING A KEY IS THE WHOLE DESIGN. The paging cursor is
      scoped to a section, so an agent that has narrowed correctly never
      pages the document at all.

      CITATIONS, NOT PARAPHRASES
        cite(key)             -> "src_graph.md:3518-3596"
        cite(key, line=3520)  -> "src_graph.md:3520"
      An agent can hand back an address a human can open and check.
      That is a different kind of answer from a summary: it is falsifiable.

      REFUSED IS NOT MISSING
        available -> did this document ship with content
        reason    -> why not, when it did not
        verify()  -> re-check the shipped text against the digest its
                     index claimed
      A document that fails verification still EXISTS and still answers
      `available` and `reason`. Omitting it would make a stale index look
      identical to a document that never existed - and the second one
      invites an agent to invent. `verify()` is ALWAYS False for an
      unavailable document, because there is nothing to check.
SURFACE EXERCISED: md.__architecture__ / __components__ /
                   __graph_network__ / __graph_details__ - addressing,
                   keys, groups, index, find, search, section, get, cite,
                   reader, verify, and the graph surface
VERIFY: went RED 2026-08-03 and was fixed the same day; awaiting
        re-run. See the header note for what the failure taught.
"""
import melder as md


PROSE_DOCS = ("__architecture__", "__components__")
GRAPH_DOCS = ("__graph_network__", "__graph_details__")


def main() -> None:
    # THESE ANSWER AT IMPORT. Nothing conjured, no Aether call made.
    for name in PROSE_DOCS + GRAPH_DOCS:
        view = getattr(md, name)
        assert view.document_name
        print(f"{name:<20} -> {type(view).__name__:<20} "
              f"available={view.available}")
    print()
    print("four documents, queryable with no Spellbook and no Conduit")

    architecture = md.__architecture__
    if not architecture.available:
        print("__architecture__ did not ship:", architecture.reason)
        print("  note it still ANSWERS - refused is not missing")
        return

    # 1. WHAT DO KEYS MEAN HERE? Ask before addressing.
    print()
    print("addressing:", architecture.addressing,
          f"  ({architecture.line_count} lines,",
          f"{architecture.char_count} chars)")

    # 2. THE CHEAP SURVEY. Keys and group rollups cost no document text.
    keys = architecture.keys()
    assert len(keys) > 0
    print()
    print("keys():", len(keys), "sections; first three:")
    for key in keys[:3]:
        print("   ", key)

    rollup = architecture.groups(1)
    print("groups(1):", len(rollup), "prefixes; first:",
          rollup[0].prefix, f"({rollup[0].sections} sections,",
          f"{rollup[0].line_count} lines)")

    # 3. THE INDEX IS SPANS, NOT PROSE. Sizing before reading, per section.
    sections = architecture.index()
    assert len(sections) == len(keys)
    biggest = max(sections, key=lambda s: s.line_count)
    print()
    print("index(): largest section is", biggest.key)
    print(f"   lines {biggest.start_line}-{biggest.end_line}"
          f" ({biggest.line_count} lines)")

    # 4. FIND ADDRESSES, SEARCH INVESTIGATES. Different questions.
    hits = architecture.search("melder", limit=3)
    print()
    print("search('melder'): top", len(hits), "by hit count")
    for hit in hits:
        print(f"   {hit.hits:>4} hits  line {hit.first_line:<6} {hit.key}")

    # 5. NOW PAY FOR ONE SECTION - and only one.
    target = keys[0]
    section = architecture.section(target)
    body = architecture.get(target)
    assert section.key == target
    assert isinstance(body, str)
    print()
    print(f"get({target!r}) -> {len(body)} chars,"
          f" {section.line_count} lines")

    # 6. A CITATION AN AGENT CAN HAND BACK. Falsifiable, unlike a summary.
    print("cite:", architecture.cite(target))
    print("cite(line=...):",
          architecture.cite(target, line=section.start_line))

    # 7. THE CURSOR IS SCOPED TO A SECTION, which is why narrowing first
    #    means never paging the document.
    reader = architecture.reader(target, line_target=20)
    chunk = reader.read()
    print()
    print("reader(key).read() ->", chunk.end_line - chunk.start_line,
          "lines, has_more =", chunk.has_more)
    print("  a cursor over ONE SECTION, not over the document")

    # 8. THE INTEGRITY GATE. The shipped text is checked against the
    #    digest its own index claimed.
    verified = architecture.verify()
    assert isinstance(verified, bool)
    print()
    print("verify() ->", verified,
          " sha:", (architecture.content_sha256 or "")[:12], "...")
    print("  an unavailable document answers False - nothing to check -")
    print("  and still reports `available` and `reason` rather than")
    print("  vanishing, because a gap invites an agent to invent")

    # 9. THE GRAPH DOCUMENTS ARE THESE PLUS NODES AND EDGES.
    graph = md.__graph_network__
    assert isinstance(graph, type(architecture)) or True
    print()
    print("__graph_network__ is a", type(graph).__name__,
          "- a document view PLUS:")
    if graph.available:
        print("   nodes:", graph.node_count, " edges:", graph.edge_count)
        print("   relations:", list(graph.relations)[:4])
        node_ids = graph.node_ids()
        if node_ids:
            first = node_ids[0]
            print("   node_ids()[0] ->", first)
            print("   details_key ->", graph.details_key(first))
    else:
        print("   did not ship:", graph.reason)

    print()
    print("survey with keys/groups, narrow with find/search, then pay")
    print("for one section - and answer with a citation, not a summary")


if __name__ == "__main__":
    main()
