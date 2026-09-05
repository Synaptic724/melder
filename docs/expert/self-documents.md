# Read the runtime's own documentation

Prerequisite: ordinary Python and the [Melder vocabulary](../beginner/index.md).
The installed package carries addressable documentation objects:

| Object | Start with |
| --- | --- |
| `md.__architecture__` | System boundaries and execution flow |
| `md.__components__` | Component responsibilities and source locations |
| `md.__graph_network__` | Nodes, edges, traversal, and impact |
| `md.__graph_details__` | Detailed descriptions joined to the network |

## Address before reading

Check `available`, `reason`, and `addressing`. Survey with `keys()`, `groups()`, or
`index()`, narrow with `find()` or `search()`, then read one section with `get(key)`
or `reader(key)`. Return a `cite(key)` address when another reader needs to verify it.
`verify()` checks the shipped content against its recorded digest.

For a traceback, the graph lesson starts with `node_at(source_path, line)`, then
walks relationships and requests impact. Authored and derived edge provenance
answer different questions; retain that distinction when interpreting the graph.

## From map to implementation

The documents identify where to look. Read the relevant source before changing
runtime behavior; a useful map still describes the revision that produced it.
For source-controlled human diagrams, continue to [Architecture & Drawings](../reference/architecture.md).
