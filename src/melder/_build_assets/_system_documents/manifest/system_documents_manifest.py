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
BUILT_FOR_VERSION = "0.2.8253"
SOURCE_SHA256 = "929d2b0e8c48f6fae99b2b94a051cca26d7e2eca59c93e3b00048b5d6f4834cb"
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
        'line_count': 5034,
        'content_sha256': '7387dcb52dbd08e73dcf43cee38b16c1a97b4e66f30a3fc15f5dc55ff1e63907',
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
        'line_count': 12008,
        'content_sha256': 'de93c9d4033a723211761dd1f266fd2e16dbb0f06a99ab9e82cd640e14ff8fbc',
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
        'line_count': 28082,
        'content_sha256': '0c90fb5a79da3d5b50f71b49cd895a2ee4d0aa5563d6b27c1494856dee936669',
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
        'line_count': 28082,
        'content_sha256': '0c90fb5a79da3d5b50f71b49cd895a2ee4d0aa5563d6b27c1494856dee936669',
    },
}
