# Melder engineering drawings

This folder contains a compact visual descent through Melder:

1. C4 establishes the system boundary and external actors.
2. C3 opens Melder into its major runtime components and ownership planes.
3. C2 follows one meld request through its internal gates and lifetime stores.

The SVG drawings are the primary human-facing pictures. They are manually composed
engineering drawings with explicit coordinates and orthogonal connectors, similar to a
draw.io diagram. Each SVG has a Mermaid companion carrying the same semantic nodes and
relationships in a text-native form.

## Drawing inventory

| Level | Reader question | Engineering drawing | Mermaid companion |
| --- | --- | --- | --- |
| C4 | Where does Melder sit, and who interacts with it? | [C4 system context](svg/c4_system_context.svg) | [Mermaid](mermaid/c4_system_context.mmd) |
| C3 | Which components own definition, execution, access, continuity, and change? | [C3 runtime components](svg/c3_runtime_components.svg) | [Mermaid](mermaid/c3_runtime_components.mmd) |
| C2 | What happens inside one gated meld resolution? | [C2 meld resolution](svg/c2_meld_resolution.svg) | [Mermaid](mermaid/c2_meld_resolution.mmd) |

## Preview

### C4 — system context

![Melder C4 system context](svg/c4_system_context.svg)

### C3 — runtime components

![Melder C3 runtime components](svg/c3_runtime_components.svg)

### C2 — meld resolution

![Melder C2 meld resolution](svg/c2_meld_resolution.svg)

## Static-authoring contract

These diagrams are authored documentation, not source-derived topology.

- Source changes do not regenerate the SVG or Mermaid files.
- The build-asset runner does not rewrite them.
- `src_graph` is not an input and is not used to infer relationships.
- The SVG and Mermaid companion for one level must be updated in the same change.
- Behavioral detail must remain aligned with `src_architecture`, `src_components`,
  and the implementation they describe.

This keeps architectural judgment explicit. A parser can discover classes and some
inheritance edges, but it cannot reliably decide ownership, boundary intent, lifetime
authority, or why an interaction exists.

## Visual grammar

- Gold: process or lifecycle owner.
- Blue: definition and compilation.
- Green: runtime execution and resolved-object storage.
- Purple: governance, validation, and change control.
- Teal: mediated AR access.
- Orange: continuity, persistence, and evolution.
- Solid arrows: primary successful runtime collaboration.
- Dashed arrows: mediated access, governance, revalidation, recording, or refusal.

## Accessibility and maintenance

Every SVG must retain:

- a stable `viewBox`;
- `role="img"`;
- a `<title>` and `<desc>` referenced by `aria-labelledby`;
- readable text without requiring color alone;
- no scripts or external resources.

Every Mermaid companion must retain `accTitle` and `accDescr`. Before accepting a
change, parse the SVG as XML, render the Mermaid source, compare semantic parity, and
inspect the SVG at full and normal documentation widths.

