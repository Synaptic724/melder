# architecture_patch

## Metadata
- Patch ID: graph_details_document_workflow
- Status: in_progress
- Owner: codex
- Created: 2026-04-19T19:19:24Z
- Updated: 2026-04-19T19:19:24Z

## Patch Scope and Non-Goals
- Objective:
  - define one canonical graph-details schema and compressed-storage workflow
  - define the required readable JSON consumption view regenerated from canonical storage
  - add canonical system docs for the workflow
  - add design-engineer authoring/maintenance and engineer reading/usage skills
  - add example files that demonstrate expanded-edit and compressed-storage forms
- Non-goals:
  - populate the full repo graph
  - add CI automation or graph generation scripts
  - replace `src_architecture.md` or `src_components.md` as the canonical prose layer

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| system_docs graph contract | add | establish one canonical graph schema, storage workflow, and readable consumption artifact | none |
| design_engineer graph authoring skill | add | teach graph creation and maintenance discipline | system_docs graph contract |
| engineer graph usage skill | add | teach graph reading and interpretation discipline | system_docs graph contract |
| examples/example_graph_details | add | provide stable example of expanded vs compressed graph files | system_docs graph contract |

## Interface and Boundary Deltas
- Boundary delta 1:
  - `src_architecture.md` and `src_components.md` remain the canonical long-form
    system explanation surfaces.
  - `src_graph.json` becomes the canonical relationship map for important system objects.
- Interface delta 1:
  - agents should maintain `src_graph.json` through an expand-edit-compress cycle.
  - compressed storage is canonical; `readable_src_graph.json` is the required readable end-state artifact; expanded patch copies are temporary working artifacts.

## Cross-Component Invariants
- There is one canonical graph storage file: `system_docs/src_graph.json`.
- There is one required readable graph consumption file: `system_docs/readable_src_graph.json`.
- The graph remains concise and relationship-first; it does not replace
  architecture/components narrative docs.
- Expanded graph editing happens on a whole-document patch copy, not via direct
  hand-editing of the compressed storage file.
- End-state graph updates regenerate the readable consumption file from the compressed canonical file.
- Graph node identity is stable and unique.

## Migration and Rollout Order
1. Add the canonical system docs and graph storage file.
2. Add the design-engineer and engineer skill docs.
3. Add the example graph-details files.
4. Update existing placeholder graph docs to redirect to the canonical files.

## Rollback Strategy
- Rollback trigger:
  - the schema or workflow proves too noisy or conflicts with the existing
    architecture/components doc model.
- Rollback steps:
  1. remove the new graph skill docs
  2. revert the canonical graph doc additions
  3. restore placeholder-only graph docs if needed
- Post-rollback verification:
  - confirm `src_architecture.md` and `src_components.md` remain the only
    graph-adjacent canonical docs

## Validation Expectations and Evidence Plan
- Validation item 1:
  - canonical and example JSON files parse successfully after compression
- Evidence source 1:
  - `ConvertFrom-Json` over canonical and example files
- Validation item 2:
  - SKILLS files route to the new graph docs
- Evidence source 2:
  - direct reads of updated SKILLS files and new skill docs

## Ticket Coverage Map
- Epic:
- Story:
- Tasks:
  - `tickets/tasks/2026-04-19_define_graph_details_document_and_agent_workflow_task.md`

## Unknowns and Decision Requests
- UNKNOWN:
  - whether future automation should seed graph node scaffolds automatically
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - this patch defines the graph-details contract as one canonical JSON file
    plus a readable JSON consumption view, a companion workflow doc, and aligned skill guidance
- What remains:
  - actual large-scale graph population is still future work
- Next entrypoint:
  - `system_docs/graph_details_document.md`
