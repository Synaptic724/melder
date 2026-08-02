

# Epic: Author graph semantics

## Metadata
- Epic ID: EPIC-2026-08-02-author-graph-semantics
- Status: in_progress
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:06Z
- Updated: 2026-08-02T17:10:00Z

## Problem / Opportunity
The source graph's mechanical tier self-heals on every extraction. The authored
tier does not exist until somebody writes it, and until then the graph can say
what exists but not what any of it is for.

## MRP Alignment (Most Reasonable Product)
Authoring semantics per package, in the order the work is actually done, rather
than attempting the whole graph at once.

## Ticket Contract
- ENTRY_GATE: the graph is current.
- EXECUTION_BOUNDARY: descriptors only. No source changes.
- DEPENDENCIES: none.
- EXIT_GATE: every story below closed; `graph_walker.py --report` shows 0 stale.
- FAILURE_ESCALATION: DECISION_REQUEST when a node's purpose is not establishable.

## Goals (Outcomes)
- Every graph node carries authored meaning, or is explicitly recorded as not
  worth authoring.

## Non-Goals (Explicit Exclusions)
- Generating semantics automatically. It was tested against a labelled corpus and
  the most valuable fields are not derivable; see the story requirements.
- Refactoring source to make it more derivable.

## Success Metrics
- `graph_walker.py --report`: UNSEMANTIC and SEMANTICS_STALE both at 0.

## Stories (Required to Complete)
| `src/melder/aether/spellbook` | 211 | 0 |
| `src/melder/aether/aetheric_frame` | 69 | 0 |
| `src/melder/nexus/rift` | 55 | 0 |
| `src/melder/crystallizer/crystal_analysis` | 45 | 0 |
| `src/melder/nexus/acl` | 39 | 0 |
| `src/melder/aether/aetheric_mediator` | 38 | 0 |
| `src/melder/aether/conduit` | 31 | 0 |
| `src/melder/crystallizer/crystals` | 23 | 0 |
| `src/melder/utilities/synchronization` | 12 | 0 |
| `src/melder/mutation_research/research_set` | 11 | 0 |
| `src/melder/utilities/custom_exceptions` | 11 | 0 |
| `src/melder/crystallizer/asset_management` | 8 | 0 |
| `src/melder/utilities/helpers` | 8 | 0 |
| `src/melder/crystallizer/crystal_loader_system` | 7 | 0 |
| `src/melder/nexus/configuration` | 7 | 0 |
| `src/melder/nexus/frame_descriptor` | 7 | 0 |
| `src/melder/utilities/data_structures` | 7 | 0 |
| `src/melder/_build_assets/_agent_documentation` | 6 | 0 |
| `src/melder/nexus` | 6 | 0 |
| `src/melder/utilities/ai_native_support_tools` | 6 | 0 |
| `src/melder/_build_assets/_bind_guard` | 5 | 0 |
| `src/melder/mutation_research/diff` | 5 | 0 |
| `src/melder/utilities/general_base` | 5 | 0 |
| `src/melder/_build_assets/_system_documents` | 4 | 0 |
| `src/melder/aether` | 4 | 0 |
| `src/melder/crystallizer` | 4 | 0 |
| `src/melder/crystallizer/persistence` | 4 | 0 |
| `src/melder/mutation_research/group_diff` | 3 | 0 |
| `src/melder/mutation_research` | 3 | 0 |
| `src/melder/utilities/caching_system` | 3 | 0 |

Total nodes needing work: 647

## Progress (bootstrap_0)
- 2026-08-02T17:10:00Z: 29 of 30 stories CLOSED. Census 1163 AUTHORED /
  0 SEMANTICS_STALE / 38 UNSEMANTIC over 1201 nodes (96.8%), from 531 authored
  (44.7%) when the epic opened.
- The remaining story is `src/melder/aether/aetheric_mediator` (38 nodes) and it
  is HELD, not blocked-by-difficulty. That package is helper_f's active build
  lane (`aetheric_mediator_core`, in validation awaiting the owner's 3.14t run).
  Authoring semantics for a subsystem still under construction produces prose
  that reads as verified truth about a shape that has not settled, which is worse
  than leaving the nodes honestly UNSEMANTIC. A QUESTION was sent to helper_f
  2026-08-02T16:35:00Z offering two resolutions - I hold until their lane lands,
  or they author it while closing that lane and have the design intent in hand.
  Default is hold. This is the epic's EXIT_GATE gap and it is deliberate.
- SCOPE ADDITION beyond the generated story list: the tool's `--min-nodes 3`
  skipped single-node packages, which orphaned the subsystem roots (Aether,
  Nexus, Crystallizer, MutationResearch) - arguably the highest-value nodes in
  the tree. Those were authored anyway. A further 17 nodes appeared mid-epic when
  an extractor re-run picked up new source files; those were authored too, so
  "29 of 30 stories" understates the coverage.
- TOOLING DEFECT FOUND AND FIXED mid-epic (see the crystal_analysis story for the
  full record): the staleness detector was inert repo-wide because
  `semantics_authored_against` was being stamped with the FILE's `source_sha256`
  instead of the node's own `span_sha256`, and the descriptors carried no
  `span_sha256` at all. `graph_walker.py` therefore reported 0 stale because it
  could not compare, not because nothing was stale. Now fixed and PROVEN: during
  the spellbook story the detector correctly fired on two classes authored 30
  minutes earlier whose source another agent had edited underneath them.
- OPEN GAP, recorded for the tooling handoff rather than patched here:
  `extract_graph.py` computes `span_sha256` for `ast.ClassDef` only, so authored
  MODULE nodes still cannot go stale. The file's `source_sha256` is already in
  the descriptor and is the natural span for a module node.

## Notes
- Generated by `graph_semantics_tickets.py`. Re-running updates rather than duplicates.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
One story per package with unauthored or stale semantics. Work a subsystem at a
time; the stories are ordered by how much is outstanding.
