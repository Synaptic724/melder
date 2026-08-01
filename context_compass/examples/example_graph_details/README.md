# example_graph_details

Shape reference for the generated source graph.

The graph is **derived from source code**, not authored. Two files are produced
by `tools/system_documents/python/`, and neither ships with this package - a
fresh install has neither, and that is expected:

- `system_docs/src_graph.md` - one section per source file
- `system_docs/src_graph_index.md` - line ranges into it, plus staleness proof

## What a section looks like

Each source file gets one section, delimited by HTML comments naming the file.
Line ranges for every section live in the index; read the index and slice,
never scan the document for delimiters.

```markdown
<!-- BEGIN FILE: src/example/conduit/conduit.py -->

## src/example/conduit/conduit.py

- source_sha256: `f7611eac...`
- nodes: 2

### Nodes

#### `Conduit` (class)

- id: `example.conduit.conduit.Conduit`
- defined at: `src/example/conduit/conduit.py:78`
- extends: `Cleanable`
- role: Runtime scope holder for a bound spell set.
- owns_state: `_spells`, `_transaction`
- public methods: `bind`, `cleanup`, `begin_transaction`

### Edges out

| from | relation | to | origin |
| --- | --- | --- | --- |
| `example.conduit.conduit.Conduit` | specializes | `example.utilities.cleanable.Cleanable` | derived |
| `example.conduit.conduit.Conduit` | owns_lifecycle_of | `example.conduit.creations.Creations` | authored |

<!-- END FILE: src/example/conduit/conduit.py -->
```

The `BEGIN FILE` / `END FILE` comments are the section boundaries. They do not
render, and the index's ranges are measured against them - a section written
without them is not addressable.

## What is derived and what is authored

This distinction is the whole contract. Measured against a hand-authored graph
of 535 nodes and 997 edges:

| field | origin | recovery |
|---|---|---|
| `id`, `label`, `kind`, `file`, `lineno`, `bases`, `public_methods` | derived | 94% |
| `specializes`, `implements` | derived | 94%, targets resolved 99% |
| `creates` | **candidate only** | 57%, over-generated ~8x |
| `role`, `responsibilities`, `owns_state`, `phases` | authored | not derivable |
| `owns_lifecycle_of`, `uses`, `borrows` | authored | **not derivable** |

`owns_lifecycle_of`, `uses`, and `borrows` are syntactically identical - each is
"A holds a reference to B". Which one it is, is a design fact that appears
nowhere in the source text. That is 68% of all edges, and it is why the graph
has an authored layer at all.

A node marked **UNSEMANTIC** carries mechanical scaffold and no meaning yet. Its
structure is trustworthy; do not infer its purpose from its name.

## Two index shapes, do not confuse them

`src_graph.md` is GENERATED, so its index is emitted by `assemble_graph.py` in
the same pass - keyed by **source path**. Authored documents get their index
from `index_document.py` by walking headings - keyed by **heading breadcrumb**.

Running `index_document.py` against `src_graph.md` produces a heading-shaped
index of `## src/...` and `### Nodes` sections. It parses, but it is the wrong
artifact: it indexes the rendering rather than the files, and every section
named `Nodes` collides. The tool will warn about the collision.

## Index shape

```markdown
| lines | source | nodes | edges |
| --- | --- | --- | --- |
| 11-26 | `src/example/__init__.py` | 1 | 0 |
| 28-61 | `src/example/conduit/conduit.py` | 2 | 12 |
```

Every row is keyed by a name - here the source path. No index in this system
uses a bare number as identity: a row keyed by a number tells a reader nothing
about whether to read it.

## Files here

- `src_graph.md` - excerpt of a generated graph, three sections
- `src_graph_index.md` - real assembler output, six rows
- this README

## References

- `agent_onboarding/default/engineer/skills/src_graph_generation.md` - building
- `agent_onboarding/default/engineer/skills/src_graph_usage.md` - reading
- `agent_onboarding/default/engineer/skills/system_document_build.md` -
  the authored documents and their indexes
