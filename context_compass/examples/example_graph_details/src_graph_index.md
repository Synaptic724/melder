# src_graph_index

**EXAMPLE.** Real output from `assemble_graph.py` over a 575-file Python
project, trimmed to six rows. This index is emitted BY THE ASSEMBLER, not by
`index_document.py` - the graph is generated, so its index is a byproduct of
generation rather than a walk over authored headings. The two have different
shapes: this one is keyed by source path, an authored-document index is keyed
by heading breadcrumb.

Line ranges into `src_graph.md`. Emitted by the same pass that wrote the
document, so the ranges cannot have drifted from it.

Line numbers are 1-based and inclusive on both ends.

## Staleness proof

| field | value |
| --- | --- |
| document | `src_graph.md` |
| index_version | 1.0.0 |
| generated_at | 2026-08-01T14:42:28Z |
| line_count | 20261 |
| line_ending | lf |
| content_sha256 | `27632c5aeb84fc3319d19ff2141db02aaaba20bc5034c692e8099f744b99f6e4` |
| sections | 575 |

Recompute `line_count` and `content_sha256` before slicing. On any
mismatch the document was hand-edited: STOP, do not slice, reassemble.

## Sections

The `edges` column counts what the section's `### Edges out` table renders:
derived plus authored. It is not derived-only - 68% of relationships are not
derivable, so a derived-only count would omit exactly the edges that carry
design meaning.

| lines | source | nodes | edges |
| --- | --- | --- | --- |
| 11-26 | `src/melder/__architecture__.py` | 1 | 0 |
| 2991-3041 | `src/melder/aether/conduit/conduit.py` | 2 | 3 |
| 3525-3561 | `src/melder/aether/conduit/meld/conduit_meld.py` | 2 | 1 |
| 11268-11317 | `src/melder/aether/spellbook/spellbook.py` | 2 | 1 |
| 19440-19473 | `src/melder/utilities/general_base/sync.py` | 2 | 0 |
| 19733-19756 | `src/melder/utilities/interfaces/icleanable.py` | 2 | 0 |

## How this is consumed

Rows are ordered by source path, so a subsystem's files are contiguous - match
the directory prefix and read those ranges.

Never read `src_graph.md` in full. On this project it is 20,261 lines against a
602-line index, and a typical file's section is 20-40 lines.

Every row is keyed by a name - here the source path. No index in this system
uses a bare number as identity.

Inbound edges are not answerable from one section: each section carries only the
edges leaving its own file. Reverse lookup is the one query this layout does not
make cheap.

## References

- `agent_onboarding/default/engineer/skills/src_graph_usage.md` - reading
- `agent_onboarding/default/engineer/skills/src_graph_generation.md` - building
