# Diagram Contract

<!--
Audience: contributor
Depth: source-bridge
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: none
Source anchors: architecture_and_design/manifest.json
-->

Each architecture picture has one canonical Mermaid source under `source/` and one
generated SVG under `rendered/`. The source is reviewed; the SVG is consumed.

## Authoring Rules

- Use stable `flowchart` or `sequenceDiagram` syntax, not experimental Mermaid C4 syntax.
- Answer one reader question per picture.
- State the scope and directly label relationships.
- Include `accTitle` and `accDescr` in every Mermaid source.
- Keep color secondary to labels, boundaries, line styles, and ordering.
- Explain the same architectural fact in the Markdown page that embeds the SVG.

## Rendering

Use Mermaid CLI `11.15.0` and the checked-in configuration:

```text
mmdc -i diagrams/source/system_context.mmd \
     -o diagrams/rendered/system_context.svg \
     -c diagrams/mermaid-config.json \
     -b "#ffffff"
```

The manifest-backed tool renders every registered pair and refreshes hashes:

```text
python tools/architecture_docs.py render --mmdc <path-to-mmdc>
python tools/architecture_docs.py check
```

The tool is documentation-only and does not add a Melder runtime dependency.
