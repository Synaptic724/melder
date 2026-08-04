# Task: crystallizer doc residue - stale-line surgery (post-decomposition)

- Completed: 2026-07-11T10:53:53Z
- Summary: all nine crystallizer-scoped residue rows fixed (A1-A3 architecture
  doc, C1-C3 components doc, G1-G3 graph + readable regen at 520/965, max
  line 220); gate greps clean on real disk; zero non-crystallizer lines
  touched; owner accepted the walk 2026-07-11.

## Metadata
- Task ID: TASK-2026-07-11-crystallizer-doc-residue-stale-line-surgery
- Parent: none (follow-up residue from EPIC-2026-07-09-crystallizer-subsystem-decomposition, closed)
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-11T10:45:36Z
- Updated: 2026-07-11T10:45:36Z

## Problem / Opportunity
The 2026-07-10 decomposition promotion (S5) added dated current-truth sections to both
C-docs and rebuilt the graph, but older CRYSTALLIZER-scoped blocks in the same documents
still carry pre-decomposition claims that are now provably wrong (scaffold-only claims,
cache/engine custody on the ledger, dead `persistence/crystals/*` and `crystal_loader/*`
paths, pre-S1 SpellCrystal slots in the graph). Staleness law: wrong text gets fixed.
Owner scope ruling (2026-07-11): crystallizer residue ONLY - touch nothing else.

## Ticket Contract
- ENTRY_GATE: owner approval 2026-07-11 ("focus on crystallizer nothing else ...
  go ahead"); residue inventory evidenced from this session's full bundle read.
- EXECUTION_BOUNDARY: system_docs/src_architecture.md (crystallizer blocks only);
  system_docs/src_components.md (crystallizer component/subcomponent blocks only);
  system_docs/src_graph.json (2 crystallizer node fixes via the sanctioned inline
  recipe) + readable_src_graph.json regen. ZERO src/ changes, zero non-crystallizer
  doc lines.
- DEPENDENCIES: none.
- EXIT_GATE: every inventoried residue row fixed or explicitly deferred with reason;
  graph JSON-valid + readable regenerated/validated; owner acceptance walk.
- FAILURE_ESCALATION: graph JSON damage -> restore from git + CONFLICT note.

## Residue Inventory (CHECKLIST - every row ticked before closure)
- [x] A1 src_architecture.md coverage summary: dead paths -> current subsystem
      paths (asset_management/, crystal_loader_system/, crystal_analysis/,
      package-level crystals/). DONE 10:52Z.
- [x] A2 src_architecture.md evidence list: 5 dead paths replaced with 10 real
      ones (cache/twins/recorded_unit_state repointed; loader + analysis
      evidence added). DONE 10:52Z.
- [x] A3 src_architecture.md "Crystallizer Responsibilities": scaffold-only +
      bootstrap_manifest claims replaced with the three-children facade truth,
      carrier-law SpellCrystal line, and the bootstrap_loader.py pointer.
      DONE 10:52Z.
- [x] C1 src_components.md old crystallizer component body: 5 surgical cuts -
      record-vs-cache ownership, Crystallizer/PersistenceSystem Owned State
      slots, twin-family location, load_checkpoint live+mediated truth,
      Key Files list repointed (dead bootstrap_manifest row removed).
      DONE 10:55Z.
- [x] C2 src_components.md "SpellCrystal Manifest" subcomponent: carrier-law
      purpose/contract, `_analysis` data structure, real paths + analyzer
      Key File. DONE 10:55Z.
- [x] C3 src_components.md "SyntheticModule Runtime" subcomponent: dead Key
      File replaced with the restore_engine M3-consumer pointer. DONE 10:55Z.
- [x] G1 src_graph.json crystals package label -> "crystallizer.crystals"
      (sanctioned inline recipe; assert-guarded edit). DONE 10:58Z.
- [x] G2 src_graph.json SpellCrystal node: owns_state -> one carried
      CrystalAnalysisResult slot; responsibilities -> capture/delegate/carry
      (assert-guarded). DONE 10:58Z.
- [x] G3 readable regenerated per the canonical recipe. Handoff report:
      source=src_graph.json, output=readable_src_graph.json, BOTH JSON-valid
      (520 nodes / 965 edges each), MAX_LINE_LEN=220. DONE 10:59Z.

## Acceptance Criteria
- No crystallizer-scoped line in either C-doc or the graph contradicts the dated
  2026-07-10 decomposition sections or the real disk paths.
- Non-crystallizer content byte-untouched.

## Applicable Anti-Patterns
- [ ] Surgical fixes only where text is provably wrong; no drive-by rewrites.
- [ ] Historical ticket notes / dated SYNC notes stay append-only (not rewritten).
- [ ] Graph edits via the sanctioned inline recipe only; validate before declaring.
- [ ] "Not run." for anything not executed.

## Noting Behavior
- Task notes: tactical findings, per-row evidence, immediate next actions.

## Notes
- DATETIME: 2026-07-11T10:45:36Z
  TYPE: FACT
  CLAIM: Residue inventory above is evidenced from THIS session's post-certification
    full reads of both C-docs (chunked, complete) and the readable graph (complete,
    14 chunks) - file-tool reads, i.e. real disk. The dated 2026-07-10 sections at
    both doc tails carry current truth and are NOT touched; only the older
    contradicting crystallizer blocks are in scope. Facade-name lists in the
    architecture "External Interfaces" section were checked and are CURRENT
    (decomposition kept the public facade surface byte-compatible), so they are
    explicitly OUT of the inventory.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:615-627
  - codex/context_compass/system_docs/src_architecture.md:250-258
  - codex/context_compass/system_docs/src_components.md:634-791
  - codex/context_compass/system_docs/src_components.md:2504-2537
  - codex/context_compass/system_docs/readable_src_graph.json:1833-1840
  IMPACT: Fix list is closed and checklist-driven (S3 lesson: inventories are
    checklists); execution can proceed without further discovery.
  NEXT: A1-A3 architecture doc edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T11:00:00Z
  TYPE: FACT
  CLAIM: A1-A3 + C1-C3 + G1-G3 COMPLETE. Gate greps on real disk (file-tool):
    the dead-path tokens (persistence/crystals, persistence/crystallizer_cache,
    crystal_loader/bootstrap_manifest, scaffold-only) survive ONLY in (a) my own
    explanatory "is gone since 2026-07-10" notes, (b) one generic instruction
    line in graph_details_document.md unrelated to the crystallizer, and (c)
    retired patch-lane history under patches/completed/ (append-only, out of
    scope by law). Graph edits were assert-guarded against the exact stale
    values, replica freshness was verified via file-tool Grep + bash JSON parse
    agreement BEFORE editing, and post-edit file-tool Grep confirms the new
    strings on disk. Bash replica agreed throughout (no rot on these files this
    pass). Non-crystallizer content untouched. Execution: doc/graph validation
    only - no test-suite claim to make ("Not run." - no src changes exist to
    test).
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:206-260
  - codex/context_compass/system_docs/src_architecture.md:615-645
  - codex/context_compass/system_docs/src_components.md:644-806
  - codex/context_compass/system_docs/src_components.md:2504-2554
  IMPACT: Every crystallizer-scoped C-doc/graph line now agrees with the dated
    2026-07-10 decomposition sections and real disk paths; the docs no longer
    contradict themselves about the migration.
  NEXT: owner acceptance walk; on confirmation, close + completed/ move +
    deterministic board sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Owner-approved crystallizer-only doc/graph residue sweep after the closed decomposition
epic: two C-docs get surgical stale-line fixes, the graph gets two node fixes + readable
regen. No src changes. Resume from the Residue Inventory checklist.
