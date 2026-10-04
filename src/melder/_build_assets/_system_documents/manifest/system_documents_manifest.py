"""
GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.

Indexes for melder's four package-root system documents.

This module carries the INDEXES - section names or source paths mapped to
line ranges, plus each document's integrity proof. The documents themselves
ship as `.md` package data in `../documents/` and are sliced on demand.

DOCUMENTS[name]['sections'] is an ordered tuple of (key, start, end), 1-based
and inclusive on both ends, matching the Context Compass index convention.

`available` is False when a pair could not be verified at build time; the
entry still exists and carries `reason`, so a stale index is distinguishable
from a document that was never there.

Regenerate with:
    python src/melder/_build_assets/_build_asset_runner.py
"""

MANIFEST_VERSION = "2.0.0"
BUILT_FOR_VERSION = "0.2.8222"
SOURCE_SHA256 = "aca100835c8c55dc8f7addc5f7a2286ee9ead260dce275969e7fa687033b305e"
DOCUMENT_COUNT = 4

READ_ORDER = (
    '__architecture__',
    '__components__',
    '__graph_network__',
    '__graph_details__',
)

DOCUMENTS = {
    '__architecture__': {
        'name': '__architecture__',
        'title': 'Melder Architecture',
        'summary': 'C4-level system map. Boundaries, entrypoints, boot and configuration sequencing, invariants, failure modes. Read this FIRST - it is orientation, and it is the one document meant to be read whole.',
        'source': 'context_compass/system_docs/src_architecture.md',
        'available': True,
        'addressing': 'section',
        'document_file': 'src_architecture.md',
        'payload_module': 'src_architecture_payload',
        'line_count': 3667,
        'content_sha256': '4dd4772b3c52716d630015862c4b8e24999c39ead31d4a7f690abc61654ad92b',
    },
    '__components__': {
        'name': '__components__',
        'title': 'Melder Components',
        'summary': 'Subsystem inventory - what each component owns, hands off to, and whether an agent may drive it. A LOOKUP TABLE, not orientation: read the index, then fetch only the sections your task touches.',
        'source': 'context_compass/system_docs/src_components.md',
        'available': True,
        'addressing': 'section',
        'document_file': 'src_components.md',
        'payload_module': 'src_components_payload',
        'line_count': 10721,
        'content_sha256': '8bafa87e7d1c44bdd61fa8ab71e32b0d0694bac80421cae92f61917943e2604c',
    },
    '__graph_network__': {
        'name': '__graph_network__',
        'title': 'Melder Graph Network',
        'summary': "The graph's SHAPE: every source file melder defines, with its node and edge counts. This is the index itself - enough to see the network and choose what to open, without opening anything.",
        'source': 'context_compass/system_docs/src_graph.md',
        'available': True,
        'addressing': 'source_path',
        'document_file': 'src_graph.md',
        'payload_module': 'src_graph_payload',
        'line_count': 27653,
        'content_sha256': '2fcb1a5e750e73bbfbf6c47cd58a3590d57de87f05d5b31ad472a38a58dc42af',
    },
    '__graph_details__': {
        'name': '__graph_details__',
        'title': 'Melder Graph Details',
        'summary': 'Per-source-file detail: nodes, edges out, why-lines, edge candidates, published aliases. Address by SOURCE PATH. Trust tiers differ per field - mechanical is derived, authored can be stale, candidates are guesses.',
        'source': 'context_compass/system_docs/src_graph.md',
        'available': True,
        'addressing': 'source_path',
        'document_file': 'src_graph.md',
        'payload_module': 'src_graph_payload',
        'line_count': 27653,
        'content_sha256': '2fcb1a5e750e73bbfbf6c47cd58a3590d57de87f05d5b31ad472a38a58dc42af',
    },
}
