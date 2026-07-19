# code_description_patch_graph_document_workflow

## Metadata
- Patch ID: graph_details_document_workflow
- Component: graph document workflow
- Status: in_progress
- Owner: codex
- Created: 2026-04-19T19:19:24Z
- Updated: 2026-04-19T19:19:24Z

## Trigger Justification
- Why this artifact is required for this component:
  - the user explicitly requested a precise expand-edit-compress workflow for
    the graph document rather than loose prose guidance

## Control-Flow Description (Pseudocode Level)
1. Read the compressed canonical `system_docs/src_graph.json`.
2. Deserialize the entire file and write one expanded whole-document working
   copy under the active patch lane.
3. Edit the expanded whole-document patch copy only.
4. Validate the expanded copy as JSON and validate node/relation contract rules.
5. Serialize the expanded copy back into compressed canonical storage.
6. Reflow the compressed canonical JSON into `system_docs/readable_src_graph.json`
   at `220` characters per line without changing JSON structure.
7. Keep the expanded patch copy only as temporary patch-lane working state.

## Edge/Error and Rollback Semantics
- Edge case 1:
  - node ids remain stable while labels, roles, and edges evolve
- Error behavior 1:
  - malformed JSON blocks recompression back into canonical storage
- Rollback behavior:
  - keep the last valid compressed canonical file and discard invalid expanded patch copies

## Invariants and Idempotency Expectations
- Invariant 1:
  - canonical storage remains compressed JSON in `system_docs/src_graph.json`
- Invariant 2:
  - readable consumption remains available in `system_docs/readable_src_graph.json`
- Invariant 3:
  - expanded editing always uses one whole-document patch copy
- Idempotency condition 1:
  - expanding and recompressing without semantic edits preserves the same graph content

## Explicit Non-Goals
- Non-goal 1:
  - partial in-place edits to the compressed canonical storage file
- Non-goal 2:
  - per-node sidecar documents for graph editing

## Validation Focus Points
- Validation item 1:
  - canonical and expanded graph files both parse as JSON
- Validation item 2:
  - readable graph files parse as JSON and remain within width contract

## Context / Handoff Summary
- What changed:
  - the graph-details workflow is defined as a whole-document
    expand-edit-compress cycle plus readable JSON regeneration
- Remaining unknowns:
  - future automation around scaffold generation
- Next entrypoint:
  - `system_docs/graph_details_document.md`
