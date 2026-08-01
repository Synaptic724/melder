# Task: Recompose src_architecture.md and src_components.md to the new spec

## Metadata
- Task ID: TASK-2026-08-01-system-doc-recomposition
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-08-01T19:12:00Z
- Updated: 2026-08-01T19:12:00Z

## Problem / Opportunity
The owner updated context_compass with a new documentation system. Both canonical
system docs predate it and satisfy neither the Required Section Contract nor the
new index mechanics.

## Ticket Contract
- ENTRY_GATE: owner directive; new standards read.
- EXECUTION_BOUNDARY: `system_docs/` only. No source edits.
- DEPENDENCIES: `src_architecture_instructions.md`, `src_components_instructions.md`,
  `system_document_build.md`, `src_graph_generation.md`, `src_graph_usage.md`.
- EXIT_GATE: both docs pass their contract; both indexes `--check` green; graph
  migrated to `src_graph.md` + `src_graph_index.md`.
- FAILURE_ESCALATION: BLOCKER if content would be lost rather than moved.

## Build Order
- [x] Read the new standards; confirm the old graph skills are retired.
- [x] Recompose `src_architecture.md`.
- [ ] Recompose `src_components.md` (consumes the migration file).
- [ ] Migrate the graph to `src_graph.md` + `src_graph_index.md`.

## Notes
- DATETIME: 2026-08-01T19:12:00Z
  TYPE: FACT
  CLAIM: THE SHIPPED .md INDEXES WERE STALE ON ARRIVAL. `--check` reported
    src_architecture_index.md at 229 lines against a live 2249, and
    src_components_index.md at 252 against 5381. They were generated against the
    STARTER docs that ship with the package, not against this repo's documents, so
    nothing could slice either doc until regenerated.
  EVIDENCE:
  - context_compass/system_docs/src_architecture_index.md
  - context_compass/system_docs/src_components_index.md
  IMPACT: Any agent trusting those indexes would have been refused by the tool -
    which is the tool behaving correctly. The failure mode to watch for is an
    agent reading a doc WHOLE because slicing refused, which is the cost the
    index exists to avoid.
  NEXT: Regenerate after each recomposition pass.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T19:12:00Z
  TYPE: IMPLEMENT
  CLAIM: `src_architecture.md` RECOMPOSED, 2249 -> 1752 lines. It now carries
    EXACTLY the 17 contract sections in contract order, one H1, no container
    headings.
    - `## Indexing` ADDED (did not exist).
    - `## Data Flows and Sequences` MOVED UP ahead of `## Operational Invariants`;
      it had sat after Failure Modes.
    - `## C1 Code Map` REBUILT: 134 entries, each carrying path/start_line/
      end_line/loc/verified_at MEASURED from disk. All resolved.
    - `## Table of Contents` REMOVED - the generated index replaces it, and a
      hand-maintained contents list is a second addressing surface that drifts.
    - 34 non-contract H2s MOVED, NOT DELETED, to the patch lane at
      `system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md`
      (1225 lines). Four had headings WRAPPED across two physical lines - the
      defect that produces one-line index fragments - and were unwrapped.
    TWO DEFECTS THE SCRIPT CAUGHT BEFORE WRITING, not after:
    (1) one C1 "path" was a DIRECTORY (`mutation_research/research_set/`) and
    cannot carry a line range; it was EXPANDED into its 8 real modules rather
    than given a plausible number, per the rule that an unverified range stays
    UNKNOWN instead of being invented. That is why 126 file entries became 134.
    (2) The first run aborted on that directory BEFORE any write, so the document
    was never left half-recomposed.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_architecture_index.md
  IMPACT: Index regenerated in the same pass: 36 sections over 1751 lines, all 36
    ranges validated against their own headings, `--check` OK, and a live
    `--slice "Operational Invariants"` returns 576-639 with its citation header.
    OPEN COVERAGE GAP, DELIBERATE AND BOUNDED: until the components pass lands,
    the migrated material is in NEITHER canonical document. Recorded in the
    architecture doc's own handoff summary so it cannot be discovered by accident.
  NEXT: `src_components.md`, consuming the migration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Acceptance Criteria
- Both docs match their Required Section Contract in order.
- Both indexes regenerate and `--check` green.
- No content deleted; migrated material lands in `src_components.md`.
- Graph replaced by `src_graph.md` + `src_graph_index.md`.

## Context / Handoff Summary
Architecture done and verified. Components next; it consumes the migration file
in the patch lane. Graph last - `src_graph.json` / `readable_src_graph.json` are
the retired artifacts.
