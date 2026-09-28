"""Remove paths into the documentation tooling from src_architecture.md and src_components.md (LF files).

Usage (from context_compass/): python <this> <verified_at ISO-8601 UTC>. Every anchor must match once.
The index commands stay in the authoring instructions (relocated, not lost); patch-lane paths become the patch
id plus the migration file's name; bare skill-file names become "the authoring instructions".
"""
import pathlib
import sys

VERIFIED_AT = sys.argv[1]

ARCH_INDEXING_OLD = """## Indexing

This document is AUTHORED. Nothing generates its prose. Its only generated
companion is `src_architecture_index.md`, rebuilt in the SAME pass as any edit:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/src_architecture.md
```

Consume it by slicing rather than reading this document whole:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/src_architecture.md --slice "<section name>"
```

### Verifying the `path:line` citations in this document
"""

ARCH_INDEXING_NEW = """## Indexing

This document is AUTHORED. Nothing generates its prose. Its only generated
companion is its index, `src_architecture_index`, rebuilt in the SAME pass as
any edit. The index lists every section's line range and name, plus a staleness
proof of this document (`line_count`, `line_ending`, `content_sha256`). Consume
it by slicing a named section rather than reading this document whole, and
recompute the staleness proof before trusting any range.

Format rules the index depends on, and which this document obeys:
- exactly one H1 (the document title)
- the navigable unit is H2 `## <Concern>`, at consistent depth
- section names unique and stable - index rows are selected BY NAME
- NO container headings: every H2 here is a selectable concern, so there is no
  wrapper heading to select by mistake

An index records `line_count`, `content_sha256`, and `line_ending`. Insert one
line near the top and every range below it is wrong while the index still parses
and still returns content - the WRONG content, confidently. On mismatch: STOP,
regenerate, never eyeball an offset.

The commands that rebuild, slice and check the index belong to the documentation
tooling, which does not ship with this document (corrected 2026-09-28: this
section used to paste those commands and cite the tooling's own specification).

### Verifying the `path:line` citations in this document
"""

ARCH_TAIL_OLD = """range that merely brushes past a definition reads as verified without being it.

Verify before trusting any range:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/src_architecture.md --check
```

Format rules the index depends on, and which this document obeys:
- exactly one H1 (the document title)
- the navigable unit is H2 `## <Concern>`, at consistent depth
- section names unique and stable - index rows are selected BY NAME
- NO container headings: every H2 here is a selectable concern, so there is no
  wrapper heading to select by mistake

An index records `line_count`, `content_sha256`, and `line_ending`. Insert one
line near the top and every range below it is wrong while the index still parses
and still returns content - the WRONG content, confidently. On mismatch: STOP,
regenerate, never eyeball an offset.

Spec: `agent_onboarding/default/engineer/skills/system_document_build.md`

## DO NOT ASSUME / Unknowns Gate
"""

ARCH_TAIL_NEW = """range that merely brushes past a definition reads as verified without being it.

## DO NOT ASSUME / Unknowns Gate
"""

ARCH_EDITS = [
    (ARCH_INDEXING_OLD, ARCH_INDEXING_NEW),
    (ARCH_TAIL_OLD, ARCH_TAIL_NEW),
    (
        "Contract in `src_architecture_instructions.md`. It now carries exactly the 17\n",
        "Contract of its authoring instructions. It now carries exactly the 17\n",
    ),
    (
        "- 34 non-contract H2 sections were MOVED, NOT DELETED, to\n"
        "  `system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md`.\n",
        "- 34 non-contract H2 sections were MOVED, NOT DELETED, to the migration file\n"
        "  (`component_material_for_migration.md`) of patch lane `system_doc_recompose_2026_08_01`.\n",
    ),
    (
        "WHAT CHANGED (2026-08-02): CONFORMED to the revised\n"
        "`src_architecture_instructions.md`. One defect class was found here, and it was\n",
        "WHAT CHANGED (2026-08-02): CONFORMED to the revised\n"
        "authoring instructions. One defect class was found here, and it was\n",
    ),
    (
        "RETIRED artifacts; the replacement is `src_graph.md` + `src_graph_index.md` per\n"
        "`agent_onboarding/default/engineer/skills/src_graph_generation.md`.\n",
        "RETIRED artifacts; the replacement is `src_graph.md` + `src_graph_index.md`, built\n"
        "by the graph generation tooling.\n",
    ),
    (
        "## Context / Handoff Summary\n\n2026-09-27 scope exits (0.2.8203):",
        "## Context / Handoff Summary\n\n"
        "2026-09-28 portability: `## Indexing` no longer pastes the index tool's commands or cites the tooling's\n"
        "specification, and the handoff lines below name the recomposition patch lane by its id instead of a path\n"
        "into the tooling, so the packaged copy names nothing its reader cannot resolve. The 2026-09-27 \"still\n"
        "open\" item below is closed.\n\n"
        "2026-09-27 scope exits (0.2.8203):",
    ),
]

COMP_INDEXING_OLD = """## Indexing

This document is AUTHORED. Nothing generates its prose. Its only generated
companion is `src_components_index.md`, rebuilt in the SAME pass as any edit:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/src_components.md
```

Consume it by slicing, never by reading this document whole:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/src_components.md --slice "<section name>"
```

Verify before trusting any range:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/src_components.md --check
```

Heading discipline this document obeys, and why:
"""

COMP_INDEXING_NEW = """## Indexing

This document is AUTHORED. Nothing generates its prose. Its only generated
companion is its index, `src_components_index`, rebuilt in the SAME pass as any
edit. The index lists every section's line range and name, plus a staleness
proof of this document (`line_count`, `line_ending`, `content_sha256`). Consume
it by slicing, never by reading this document whole, and recompute the
staleness proof before trusting any range.

Heading discipline this document obeys, and why:
"""

COMP_EDITS = [
    (COMP_INDEXING_OLD, COMP_INDEXING_NEW),
    (
        "  graph, and it is also what `## C1 Code Map (Core)` is built from.\n\n"
        "Spec: `agent_onboarding/default/engineer/skills/system_document_build.md`\n",
        "  graph, and it is also what `## C1 Code Map (Core)` is built from.\n\n"
        "The commands that rebuild, slice and check the index belong to the documentation\n"
        "tooling, which does not ship with this document (corrected 2026-09-28: this\n"
        "section used to paste those commands and cite the tooling's own specification).\n",
    ),
    (
        "HOW TO READ THIS CATALOG. `src_components_instructions.md` defines a twelve-field\n"
        "contract for C3 component entries and says NOTHING about C2 entries, so the shape\n",
        "HOW TO READ THIS CATALOG. The authoring instructions define a twelve-field\n"
        "contract for C3 component entries and say NOTHING about C2 entries, so the shape\n",
    ),
    (
        "RANGES - which the inventory does not carry - were moved verbatim to\n"
        "`system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md`\n",
        "RANGES - which the inventory does not carry - were moved verbatim to the migration\n"
        "file (`component_material_for_migration.md`) of patch lane `system_doc_recompose_2026_08_01`\n",
    ),
    (
        "- `system_docs/patches/active/` - active patch lanes; component\n"
        "  and code-description patches are inputs to this document while a lane is open.\n",
        "- the documentation tooling's open patch lanes (they do not ship with this document) -\n"
        "  component and code-description patches are inputs to this document while a lane is open.\n",
    ),
    (
        "the Required Section Contract in `src_components_instructions.md`. The component\n",
        "the Required Section Contract of its authoring instructions. The component\n",
    ),
    (
        "  produces one-line index fragments. All of it went to\n"
        "  `system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md`,\n"
        "  unwrapped. NOTHING WAS DELETED.\n",
        "  produces one-line index fragments. All of it went to the migration file\n"
        "  (`component_material_for_migration.md`) of patch lane `system_doc_recompose_2026_08_01`,\n"
        "  unwrapped. NOTHING WAS DELETED.\n",
    ),
    (
        "WHAT CHANGED (2026-08-02): CONFORMED to the revised\n"
        "`src_components_instructions.md`. Four defect classes closed.\n",
        "WHAT CHANGED (2026-08-02): CONFORMED to the revised\n"
        "authoring instructions. Four defect classes closed.\n",
    ),
    (
        "  guaranteed miss, not a near miss. They were MOVED, NOT DELETED, to\n"
        "  `system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md`\n",
        "  guaranteed miss, not a near miss. They were MOVED, NOT DELETED, to the migration file\n"
        "  (`component_material_for_migration.md`) of patch lane `system_doc_recompose_2026_08_01`\n",
    ),
    (
        "- path: `src/melder/aether/conduit/meld/conduit_meld.py`\n"
        "  start_line: 1\n"
        "  end_line: 1039\n"
        "  loc: 1039\n"
        "  verified_at: 2026-09-26T20:10:34Z\n",
        "- path: `src/melder/aether/conduit/meld/conduit_meld.py`\n"
        "  start_line: 1\n"
        "  end_line: 1087\n"
        "  loc: 1087\n"
        f"  verified_at: {VERIFIED_AT}\n",
    ),
    (
        "## Context / Handoff Summary\n\n2026-09-28 SpellSpace probe (0.2.8204):",
        "## Context / Handoff Summary\n\n"
        "2026-09-28 portability and ConduitMeld docstrings (0.2.8205): `## Indexing` no longer pastes the index\n"
        "tool's commands or cites the tooling's specification; the C1 note, the companion list and the handoff\n"
        "lines name the recomposition patch lane by its id and the authoring instructions by role, not by path,\n"
        "so the packaged copy names nothing its reader cannot resolve. ConduitMeld's docstrings now name the store\n"
        "each lifetime uses, matching \"Live-creation probe scope\"; conduit_meld.py remeasured (1087).\n\n"
        "2026-09-28 SpellSpace probe (0.2.8204):",
    ),
]


def apply(path: str, edits: list) -> None:
    doc = pathlib.Path(path)
    text = doc.read_bytes().decode("utf-8")
    assert "\r" not in text
    for old, new in edits:
        assert text.count(old) == 1, (path, old[:70], text.count(old))
        text = text.replace(old, new)
        for line in new.split("\n"):
            assert len(line) <= 120, (path, len(line), line)
    doc.write_bytes(text.encode("utf-8"))
    print("edited", path)


apply("system_docs/src_architecture.md", ARCH_EDITS)
apply("system_docs/src_components.md", COMP_EDITS)
