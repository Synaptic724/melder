

- Completed: 2026-08-01T19:40:00Z
- Summary: `src_graph.md` + `src_graph_index.md` now replace the retired JSON pair,
  generated from `src` by the two-stage pipeline. FINAL STATE IS A CLEAN
  MECHANICAL BUILD: 575 sections, 1,188 nodes ALL MARKED UNSEMANTIC, 446 derived
  edges, 0 authored edges. Index verified (line_count 20,300 = 20,300,
  content_sha256 matches, all 575 ranges checked against their own headers).
- IMPORTANT, READ BEFORE TRUSTING THE NOTES BELOW: a mid-task migration DID carry
  531 node semantics and 997 authored edges across, and several notes below
  describe that work as shipped. It was subsequently WIPED on explicit owner
  instruction ("wipe that shit and remake it all"), and the graph was rebuilt
  clean from source. Those notes are retained as an accurate record of what was
  done and measured, NOT as a description of the current artifact. The authored
  tier is not in the graph.

# Task: Port src_graph from the JSON pair to the assembled Markdown format

## Metadata
- Task ID: TASK-2026-08-01-src-graph-markdown-port
- Story: none (standalone task)
- Status: done
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p1
- Created: 2026-08-01T18:40:00Z
- Updated: 2026-08-01T18:40:00Z

## Objective
Retire `readable_src_graph.json` + `src_graph.json` and stand up
`src_graph.md` + `src_graph_index.md` via the two-stage pipeline, WITHOUT losing
the 535 authored nodes and 997 authored edges the JSON pair carries.

## Ticket Contract
- ENTRY_GATE: owner instruction 2026-08-01 to delete the existing graph system,
  run the tools over `src`, and carry the existing content across. Feasibility
  established by source read + measured dry run before any repo write.
- EXECUTION_BOUNDARY:
  - `context_compass/system_docs/graph/` (new descriptor tree)
  - `context_compass/system_docs/src_graph.md`, `src_graph_index.md` (generated)
  - `context_compass/system_docs/readable_src_graph.json`, `src_graph.json` (retired)
  - one throwaway migration script, not committed to `tools/`
  - NO `src/` changes of any kind
- DEPENDENCIES: `tools/system_documents/python/extract_graph.py`,
  `assemble_graph.py`.
- EXIT_GATE: `src_graph_index.md` verifies against `src_graph.md`
  (`line_count` + `content_sha256`); authored-node migration reach reported with
  an explicit unmatched list; authored edges placed with orphans named; old JSON
  pair removed only AFTER verification passes.
- FAILURE_ESCALATION: BLOCKER if index verification fails. DECISION_REQUEST on
  any authored content that cannot be carried across.

## Patch Framework Gate
- NOT TRIGGERED, with reasoning recorded rather than assumed. `patch_framework_gating.md`
  fires on changes to architecture/component boundaries, lifecycle behaviour,
  policy/gating behaviour, or cross-component interaction contracts. This task
  changes zero `src/` code and alters no runtime contract; it replaces the
  storage format of a documentation artifact. No patch docs authored.

## Scope Boundaries
- In scope: graph artifact format migration and the one-time semantics carry-over.
- Out of scope: authoring NEW semantics for the ~653 nodes extraction finds that
  the hand-authored graph never covered; re-curating `include`; any `src/` edit.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner gave an explicit go-ahead after being shown the
  measured migration reach and the 836-edge exposure.

## Steps / Checklist
- [x] Confirm all source parses under the available interpreter
- [x] Dry-run extraction to a scratch path and measure migration reach
- [x] Read the assembler's authored-field contract from source
- [ ] Extract descriptors to the real path
- [ ] Migrate authored node semantics + authored edges into descriptors
- [ ] Assemble document + index
- [ ] Verify index against document
- [ ] Retire the JSON pair
- [x] Document each meaningful finding immediately in `## Notes`

## Deliverables
- `context_compass/system_docs/graph/**` descriptors carrying authored semantics
- `context_compass/system_docs/src_graph.md` + `src_graph_index.md`
- Migration residue report in `## Notes`

## Files / Paths Impacted
- context_compass/system_docs/graph/ (new)
- context_compass/system_docs/src_graph.md (new)
- context_compass/system_docs/src_graph_index.md (new)
- context_compass/system_docs/readable_src_graph.json (removed)
- context_compass/system_docs/src_graph.json (removed)

## Validation
- Not run (test suite). This task ships no `src/` change, so the pytest suite is
  not the relevant gate; the gate is index-vs-document verification, which IS
  run and recorded below.

## Risks / Rollback Notes
- RISK: deleting the JSON pair before migrating would destroy the only copy of
  836 non-derivable authored edges. MITIGATION: strict ordering - migrate,
  assemble, verify, and only then remove. Recorded because the owner's phrasing
  put deletion first.
- ROLLBACK: the JSON pair is in git history; `git checkout` restores it.

## Applicable Anti-Patterns
- [x] No hand-editing `src_graph.md` or `src_graph_index.md`.
- [x] No regenerating the document without the index.
- [x] No promoting an edge candidate to an edge without reading the code.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Notes
- DATETIME: 2026-08-01T18:40:00Z
  TYPE: FACT
  CLAIM: The naive two-script port would silently destroy most of the graph's
    value. `readable_src_graph.json` is NOT a generated artifact - all 535 of its
    nodes carry authored `role`/`responsibilities`/`owns_state`/`phases`, and its
    997 edges carry authored `why`/`cardinality`/`strength`/`phase`. Extraction
    emits mechanical tier only, so a fresh run yields 1,188 nodes ALL marked
    UNSEMANTIC. Measured re-derivable edges: 161 of 997
    (`specializes` + `implements`). 836 edges - 323 `uses`, 205
    `owns_lifecycle_of`, 157 `creates`, 119 `borrows` and the tail - do not exist
    in the source text at all and cannot be recovered by any parser.
  EVIDENCE:
  - context_compass/tools/system_documents/python/extract_graph.py:69-74
  - context_compass/agent_onboarding/default/engineer/skills/src_graph_generation.md:60-81
  IMPACT: 84% of authored edges at risk, worse than the skill's own 68% estimate
    because this graph is edge-richer than the reference it was measured against.
  NEXT: Establish whether the authored tier can be carried across mechanically.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T18:40:00Z
  TYPE: MEASURE
  CLAIM: Migration is viable at 99.3% for nodes. Against a scratch extraction of
    575 descriptors / 1,188 nodes: 529 of 535 authored nodes match a new node id
    EXACTLY, 2 more match on `(file, label)`, leaving only 4 unmatched. Both
    tools run clean on the available interpreter and all 575 source files parse,
    so the port can be executed here rather than deferred to an owner run.
  EVIDENCE:
  - context_compass/tools/system_documents/python/extract_graph.py:317-353
  IMPACT: Turns "start clean and lose it" into a one-time carry-over. After this
    single pass the merge contract protects the authored tier on every future
    re-run, so the migration is never needed again.
  NEXT: Extract to the real path, migrate, assemble.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T18:40:00Z
  TYPE: RISK
  CLAIM: The assembler's edge table is LOSSY relative to what a descriptor can
    hold. `render_descriptor` emits authored edges as `| from | relation | to |
    authored |` only - `why`, `cardinality`, `strength` and `phase` are never
    rendered. Migrated edges therefore survive on disk in the descriptors and in
    git, but are INVISIBLE in `src_graph.md`. `why` is the field that carries what
    a relationship actually means, so the reading surface loses the most
    valuable part of an authored edge.
  EVIDENCE:
  - context_compass/tools/system_documents/python/assemble_graph.py:141-154
  IMPACT: Not a reason to skip the migration - preserved-but-unrendered strictly
    beats deleted - but it is a gap in the new format worth an owner ruling.
  NEXT: Report to owner after the port; a renderer change is a separate ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T18:58:00Z
  TYPE: MEASURE
  CLAIM: PORT COMPLETE AND VERIFIED. 575 descriptors, 1,188 nodes, 1,443 edges
    (446 derived + 997 authored). `src_graph.md` is 23,075 lines with a 602-line
    index (2%). Index verified against the document by the procedure in
    `src_graph_usage.md`: `line_count` 23,075 = 23,075 and `content_sha256`
    matches, so the index is CURRENT and safe to slice. All 575 ranges were
    verified against their own headers by the assembler.
    MIGRATION RESULT: 531 of 535 authored nodes carried across (529 exact id,
    2 by file+label) and 997 of 997 authored edges placed into 347 descriptors -
    100% of the edge semantics, including all 323 `uses`, 205
    `owns_lifecycle_of`, 157 `creates` and 119 `borrows` that no parser can
    derive. Spot-checked `src/melder/nexus/rift/rift.py`: `Rift` renders role,
    4 responsibilities, 5 owns_state entries, 4 phases, and 7 edges correctly
    split 1 derived / 6 authored.
  EVIDENCE:
  - context_compass/system_docs/src_graph.md:20810-20863
  - context_compass/system_docs/src_graph_index.md
  IMPACT: The graph is now sliceable. A single-file query reads 20-50 lines
    instead of an unreadable 776 KB blob, and the authored tier is protected by
    the merge contract on every future `extract_graph.py` run.
  NEXT: Owner reviews the format.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T18:58:00Z
  TYPE: FACT
  CLAIM: ZERO GENUINE SEMANTIC LOSSES. The 4 old nodes that matched nothing were
    each investigated rather than written off. `melder.utilities.general_base.sync.ISync`
    is not a class at all - it is a module-level alias (`ISync = Sync`,
    sync.py:217), which the new extractor captures under Published aliases
    instead of as a node. The other three - `crystallizer.crystals`,
    `crystal_analysis.custody`, `crystal_analysis.preflight` - are DIRECTORIES,
    not source files. The new extractor is per-file by design and records
    package-level nodes separately in `_package_candidates.json`; per
    `src_graph_generation.md` whether a package deserves a node is an authored
    curation decision. So all 4 are representational differences, not lost prose.
  EVIDENCE:
  - src/melder/utilities/general_base/sync.py:217
  - context_compass/system_docs/graph/_package_candidates.json
  IMPACT: Migration reach is effectively 100%, not the 99.3% the node match rate
    suggested. Nothing needs manual re-authoring as a result of this port.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T18:58:00Z
  TYPE: RISK
  CLAIM: Two usability findings from actually driving the new format, both
    reportable rather than blocking. FIRST, 657 of 1,188 nodes are UNSEMANTIC -
    that is not regression, it is the coverage gap made VISIBLE. The old graph
    covered 535 nodes and simply omitted the rest, so its silence looked like
    completeness; the new one lists them and marks them unauthored. SECOND,
    pointing `index_document.py --slice` at `src_graph.md` emits hundreds of
    duplicate-section-name warnings, because every file section repeats the
    sub-headings `Nodes` / `Edges out` / `Edge candidates`. That is the WRONG
    door - `src_graph.md` carries its own assembler-emitted index and is
    addressed by source path, which is unique - but the tool answers anyway
    instead of refusing, so an agent can easily reach for it and drown in noise.
  EVIDENCE:
  - context_compass/tools/system_documents/index_document.py
  - context_compass/agent_onboarding/default/engineer/skills/src_graph_usage.md:19-34
  IMPACT: The UNSEMANTIC count is an honest backlog, not damage. The indexer
    overlap is a trap worth a guard - `index_document.py` could refuse a document
    that has a sibling `_index.md` it did not write.
  NEXT: Owner rules whether either warrants a follow-up ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T19:40:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING - authored tier deliberately DROPPED, graph rebuilt clean
    from source. The migration described in the notes above was real, measured,
    and verified (531 node semantics + 997/997 edges carried across), and it was
    then discarded on explicit owner instruction after the owner confirmed the
    graph should be tool-generated from `src` rather than reconstructed from the
    retired JSON. Final artifact: 1,188 nodes all UNSEMANTIC, 446 derived edges,
    0 authored edges. The 997 authored edges - `uses` 323, `owns_lifecycle_of`
    205, `creates` 157, `borrows` 119 - are NOT in the graph and cannot be
    regenerated, because no parser can recover them (measured at 21% vs 21%
    discrimination; see the handoff document).
  EVIDENCE:
  - context_compass/system_docs/src_graph.md
  - context_compass/system_docs/src_graph_index.md
  IMPACT: The graph is structurally complete and semantically empty. It covers
    1,188 nodes against the old graph's 535, and every one declares that its
    meaning has not been established. Semantics are now authored forward as
    needed, protected by the tier merge contract on every future re-run.
  NEXT: None. Authoring semantics is future work, not this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T19:40:00Z
  TYPE: FACT
  CLAIM: `extract_graph.py` was SYNCED from the context_compass library before
    the final build, so the shipped graph came from the current extractor rather
    than the stale vendored one. The local copy had been 14 lines behind and the
    library's was the newer, better version. `extract_graph.py`,
    `assemble_graph.py` and `index_document.py` are now all byte-identical to the
    library. The authored tier was snapshotted to a scratch file before the wipe
    and then DELETED at owner instruction; it exists in no repository.
  EVIDENCE:
  - context_compass/tools/system_documents/python/extract_graph.py
  IMPACT: Removes the silent-drift condition that produced the earlier build. Any
    future divergence is again undetected - see handoff Q2 in the
    context_compass repo.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Format migration for the source graph. The hand-authored JSON pair holds content
no tool can regenerate; the new Markdown format holds a better container and a
merge contract that stops the mechanical half rotting. This task puts the former
in the latter. Strict ordering matters: migrate and verify BEFORE deleting.
