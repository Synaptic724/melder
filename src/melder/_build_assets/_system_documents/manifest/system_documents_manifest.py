"""
GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.

The four package-root system documents melder publishes, as minified
JSON hardcopy envelopes. Consumed by
`_build_assets/_system_documents/system_documents.py`, which builds one
`StaticSystemDocument` per entry.

`POPULATED` reports which documents carry real content and which are
still structured templates. Check it rather than pattern-matching prose.

There is NO .melc cache for this asset - see the builder for why.

Regenerate with:
    python src/melder/_build_assets/_build_asset_runner.py
"""

MANIFEST_VERSION = "1.0.0"
BUILT_FOR_VERSION = "0.1.1"
SOURCE_SHA256 = "0ebb2e9dfddf9db64b4c4f07e11cecc5648d5c3a419bea09f609af76e3ce1d00"
DOCUMENT_COUNT = 4

READ_ORDER = (
    '__architecture__',
    '__components__',
    '__graph_network__',
    '__graph_details__',
)

POPULATED = {
    '__architecture__': False,
    '__components__': False,
    '__graph_network__': False,
    '__graph_details__': False,
}

DOCUMENTS = {
    '__architecture__': {
        'title': 'Melder Architecture',
        'summary': 'C4-level system document. Boundaries, entrypoints, boot and configuration sequencing, execution lifecycle.',
        'source': 'context_compass/system_docs/src_architecture.md',
        'populated': False,
        'line_count': 34,
        'char_count': 989,
        'json': '{"m":"# Melder Architecture\\n\\n> TEMPLATE. Structure is final; content is not yet populated.\\n> Source of record: `context_compass/system_docs/src_architecture.md`.\\n\\nRead order: architecture -> components -> graph network -> graph details.\\n\\n## 1. System Boundary\\n\\nWhat is inside melder, what is the caller\'s, and what is neither.\\n\\n## 2. Entrypoints\\n\\n`Aether()`, `Spellbook`, `conjure(...)`, `Nexus`, `Crystallizer`,\\n`MutationResearch` - what each one is the door to.\\n\\n## 3. Boot Sequence\\n\\nWhat `import melder` does, in order, and what it deliberately does not do.\\nFrames are NOT created at boot; the first Spellbook births the frame it names.\\n\\n## 4. Configuration Sequencing\\n\\nWhich configuration must be frozen before which verb, and why activation is a\\ndistinct step from construction.\\n\\n## 5. Execution Lifecycle\\n\\nbind -> conjure -> meld -> cleanup, and where each phase can refuse.\\n\\n## 6. Concurrency Posture\\n\\nWhat free-threaded 3.14t changes, which objects are shared, and which are\\nper-caller.\\n"}',
    },
    '__components__': {
        'title': 'Melder Components',
        'summary': 'Subsystem inventory. What each component owns, what it hands off to, and which are guarded kernel machinery.',
        'source': 'context_compass/system_docs/src_components.md',
        'populated': False,
        'line_count': 36,
        'char_count': 879,
        'json': '{"m":"# Melder Components\\n\\n> TEMPLATE. Structure is final; content is not yet populated.\\n> Source of record: `context_compass/system_docs/src_components.md`.\\n\\nEach entry answers: what does it own, what does it hand off to, and may an\\nagent drive it directly?\\n\\n## Aether\\n\\nThe global singleton root and the hidden substrate it boots.\\n\\n## Spellbook\\n\\nThe binding authority. Registration, validation, and the single conjure.\\n\\n## Conduit\\n\\nThe runtime scope. Resolution, child scopes, request scope, dynamic linking.\\n\\n## Nexus / Rift\\n\\nThe public AR surface over the substrate: rooms, viewers, ACL, codegen.\\n\\n## Crystallizer\\n\\nPersistence: capture, checkpoint, restore, and the external mesh seam.\\n\\n## MutationResearch\\n\\nVersion lanes, research sets, and derived diffs over recorded material.\\n\\n## Utilities\\n\\nSynchronization primitives, weak containers, caching, and the AI-native\\nsupport tools.\\n"}',
    },
    '__graph_network__': {
        'title': 'Melder Graph Network',
        'summary': "The dependency graph's shape: nodes, edges, and how a resolution walk traverses it.",
        'source': 'context_compass/system_docs/src_graph.json',
        'populated': False,
        'line_count': 21,
        'char_count': 638,
        'json': '{"m":"# Melder Graph Network\\n\\n> TEMPLATE. Structure is final; content is not yet populated.\\n> Source of record: `context_compass/system_docs/src_graph.json`.\\n\\nNOTE for whoever populates this: the source is MINIFIED - one line of roughly\\n750,000 characters. Line-based paging cannot bound it, so any reader over this\\ndocument must set a character budget. `readable_src_graph.json` is the\\nline-shaped variant of the same data.\\n\\n## Node Kinds\\n\\nWhat a node represents and what identity it carries.\\n\\n## Edge Kinds\\n\\nNormal DI sockets versus late-bound contract sockets.\\n\\n## Traversal\\n\\nHow a resolution walk orders the graph, and where it can refuse.\\n"}',
    },
    '__graph_details__': {
        'title': 'Melder Graph Details',
        'summary': 'Per-node detail: sockets, existence, permissions, and the compiled resolution plan.',
        'source': 'context_compass/system_docs/readable_src_graph.json',
        'populated': False,
        'line_count': 16,
        'char_count': 402,
        'json': '{"m":"# Melder Graph Details\\n\\n> TEMPLATE. Structure is final; content is not yet populated.\\n> Source of record: `context_compass/system_docs/readable_src_graph.json`.\\n\\n## Per-Node Detail\\n\\nSockets, existence, permissions, and spellframe for one node.\\n\\n## Compiled Plan\\n\\nWhat the compiler produced for a node and which strategy family claimed it.\\n\\n## Diagnostics\\n\\nWhere to look when a node refuses to resolve.\\n"}',
    },
}
