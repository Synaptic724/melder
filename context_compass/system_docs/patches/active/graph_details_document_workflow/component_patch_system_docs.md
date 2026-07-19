# component_patch_system_docs

## Metadata
- Patch ID: graph_details_document_workflow
- Component: system_docs graph surfaces
- Status: in_progress
- Owner: codex
- Created: 2026-04-19T19:19:24Z
- Updated: 2026-04-19T19:19:24Z

## Component Purpose and Boundary
- Current boundary:
  - `src_graph_details.md` and `src_graph_network.md` are placeholders only.
- Target boundary:
  - `graph_details_document.md` defines the canonical schema and workflow.
  - `src_graph.json` stores the compressed canonical relationship map.
  - `readable_src_graph.json` stores the readable line-broken JSON consumption view.
  - the old placeholders become redirect stubs rather than competing contracts.

## Before/After Behavior Summary
- Before:
  - graph docs are placeholders with no canonical schema or maintenance workflow.
- After:
  - one canonical graph schema and expand-edit-compress workflow exist in
    system docs and storage.

## Interface Deltas
- Inputs:
  - machine-first graph data for important system objects
  - architecture/components docs as canonical long-form explanation surfaces
- Outputs:
  - compressed canonical graph storage
  - readable JSON consumption artifact
  - human-readable workflow doc explaining authoring and maintenance
- Error semantics:
  - stale or malformed graph edits should be blocked by whole-document JSON parse validation

## State and Lifecycle Deltas
- Owned state changes:
  - add canonical `system_docs/src_graph.json`
  - add required `system_docs/readable_src_graph.json`
  - add canonical `system_docs/graph_details_document.md`
- Lifecycle/cleanup changes:
  - expanded graph files are temporary patch working copies only

## Failure Mode Deltas
- New failure mode:
  - agents may try to hand-edit compressed storage directly and create malformed
    or partial graph updates
- Removed failure mode:
  - placeholder ambiguity about which graph doc is canonical
- Changed failure mode:
  - graph maintenance now has one explicit workflow instead of no workflow

## Dependency and Ordering Constraints
1. `graph_details_document.md` must define the schema before skill docs point to it.
2. `src_graph.json` must exist before examples and skills can demonstrate the workflow.

## Validation Expectations
- Test/validation item 1:
  - canonical `src_graph.json` parses after compression
- Evidence target 1:
  - `ConvertFrom-Json` parse of the canonical graph file
- Test/validation item 2:
  - `readable_src_graph.json` parses as JSON and stays within the configured line width

## Unknowns and Open Decisions
- UNKNOWN:
  - whether graph coverage should stay limited to important runtime objects
    permanently or later widen into a more exhaustive map
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - system docs now gain one canonical graph storage file, one readable graph
    consumption file, and one workflow doc
- Remaining risks:
  - graph verbosity and stale relationships if the node set grows too wide
- Next entrypoint:
  - `system_docs/readable_src_graph.json`
