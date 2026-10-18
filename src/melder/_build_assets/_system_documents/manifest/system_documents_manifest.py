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
BUILT_FOR_VERSION = "0.2.8254"
SOURCE_SHA256 = "c774deafa8573345a5f1ecfabd695472ac541512c49130de03aeb6838aa501d5"
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
        'line_count': 5103,
        'content_sha256': '7ac6391d8cb9ba469d7190622c865b33c35632a4ea5fa5b7a0f8f7756d0bcbfa',
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
        'line_count': 12053,
        'content_sha256': '939fc43c469b67d7c6f03a6fdf5f820306006a3418562bfa11300a3a9b8e14af',
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
        'line_count': 28084,
        'content_sha256': 'e938782807c724518d2bc06adc7e10eeca85f9a380379505785a674728e2adf5',
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
        'line_count': 28084,
        'content_sha256': 'e938782807c724518d2bc06adc7e10eeca85f9a380379505785a674728e2adf5',
    },
}
