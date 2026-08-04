# Story: decomposition doc + graph promotion (S5 - closure)

- Completed: 2026-07-10T09:10:00Z
- Summary: both C-docs carry the decomposed topology (dated sections +
  stale-line surgery); src_graph 520 nodes/965 edges with zero stale paths;
  readable regenerated + validated (max 220); patch lane -> completed/;
  philosophy-drift scoreboard recorded; owner accepted at epic closure.

## Metadata
- Story ID: STORY-2026-07-09-decomposition-doc-graph-promotion
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-10T08:00:00Z
- Updated: 2026-07-10T08:00:00Z

## Problem / Opportunity
The decomposition is built and 614/614 green, but the canonical C-docs still
describe the pre-S1 topology (PersistenceSystem owning caches, EPM at
crystallizer rank, engine seated on the ledger) and src_graph.json carries
stale paths for every moved module. Docs must match disk before closure.

## Ticket Contract
- ENTRY_GATE: S-test exit GREEN (owner full tree 614/614, 2026-07-10).
- EXECUTION_BOUNDARY: system_docs/src_components.md + src_architecture.md
  (stale-line surgery + one dated decomposition section each);
  src_graph.json node/edge authoring + path rewrites (inline-execution
  recipe - the sanctioned bash-write exception); readable_src_graph.json
  regen per canonical recipe; patch lane -> completed/; epic milestone sync.
- EXIT_GATE: both C-docs current; graph JSON-valid with the new subsystem
  nodes/edges and zero stale paths; readable regenerated + validated;
  patch lane relocated; closure walks prepared for owner acceptance.
- FAILURE_ESCALATION: graph JSON damage -> restore from git + CONFLICT.

## Tasks
- [x] T1: C-doc surgery DONE 08:20Z - components doc: ownership block
      rewritten (3 children + vocabulary + analysis service), EPM asset-owned,
      bootstrap path + absorbed-knob note, and the dated "Subsystem
      Decomposition" section (five identities, admission/verdict law,
      cross-subsystem laws); architecture doc: stale C1 crystallizer lines
      fixed + "Persistence Subsystem Topology" section appended (tree, laws,
      unchanged invariants).
- [x] T2: src_graph.json DONE 08:40Z - 11 dead scaffold nodes deleted
      (crystal_loader/* + asset_management/asset_* stubs the owner rm'd);
      7 id renames + file rewrites for every moved module; 5 scaffold
      crystal_analysis nodes refreshed to real truth; 6 new nodes
      (AssetManagementSystem, CrystalLoaderSystem, BootMediator, LoadPlan,
      custody + preflight packages); 3 stale ownership edges dropped
      (Crystallizer->EPM, PersistenceSystem->cache,
      PersistenceSystem-creates->engine); 15 edges added per the V3 edge law
      (owns/borrows/creates incl. the carrier-law triangle SpellCrystal ->
      CrystalAnalyzer -> CrystalAnalysisResult). 525/953 -> 520/965.
- [x] T3: readable regen DONE 08:45Z per canonical recipe. Handoff report:
      source=src_graph.json, output=readable_src_graph.json, BOTH JSON-valid
      (520 nodes / 965 edges each), readable MAX_LINE_LEN=220.
- [x] T4: patch lane -> system_docs/patches/completed/
      crystallizer_decomposition_2026_07_09/ (5 docs); epic milestones
      M-A..M-D ticked; epic Artifact Links re-pointed. DONE 08:50Z.
- [x] T5: closure walks prepared (delivered in the session report);
      philosophy-drift note below. DONE 08:55Z.

## Acceptance Criteria
- A fresh reader of the C-docs sees the decomposed topology, not the god
  object; the graph resolves every crystallizer file at its real path.

## Applicable Anti-Patterns
- [ ] Append-only enrichment where possible; surgical fixes only where the
      old text is now WRONG.
- [ ] Graph edits via the sanctioned inline recipe only; validate before
      declaring.

## Noting Behavior
- Story notes: per-task evidence + validation outputs.

## Notes
- DATETIME: 2026-07-10T08:00:00Z
  TYPE: PLAN
  CLAIM: S-test closed 614/614 (owner). S5 executes T1->T5 in order; the
    graph edit reuses the 2026-07-07 authoring approach (inline python,
    path-rewrite map + node/edge authoring, then readable reflow at 220
    cols).
  EVIDENCE:
  - codex/context_compass/tickets/stories/2026-07-09_test_repoint_sweep_story.md:1-999
  IMPACT: Epic closure becomes an owner acceptance walk away.
  NEXT: T1 C-doc surgery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-10T08:55:00Z
  TYPE: FACT
  CLAIM: S5 COMPLETE (T1-T5; see task ticks for the full inventory).
    PHILOSOPHY-DRIFT CLOSURE NOTE (V3 intents, honest scoreboard):
    INHABITED - the five identities exist at their real paths; carrier law
    enforced in code; verdict law standard on every mediated load (proven
    live by the SHA-refusal); ledger law (record owns in-process truth
    only, calls nobody); edge/lock laws hold; durable load state exists;
    physical fingerprints + export surfaces + topological load order
    recorded per analysis; the MR re-analysis seam (analyze_payload) is
    live; bite-size law satisfied (largest new subsystem file ~640 lines vs
    the 1500+ god object).
    STILL OPEN (deliberate, per V3 horizon): MR Phase B (composition
    persistence/hydration - next major lane), full physical source-text
    retention (fingerprint-only shipped; owner decision), env/asset layer
    (uv.lock validation - owner scope decision), load-scope maturity
    (host-precondition strategies, retargeting, skip_existing collision
    policy), first-party EPM adapter package.
  EVIDENCE:
  - codex/context_compass/system_docs/src_components.md:3382-3520
  - codex/context_compass/system_docs/src_architecture.md:1748-1800
  - codex/context_compass/system_docs/patches/completed/crystallizer_decomposition_2026_07_09/
  IMPACT: Docs, graph, philosophy, and code all tell one story; the epic
    awaits the owner's acceptance walk.
  NEXT: owner reviews the closure walk; on acceptance, move the 6 story
    tickets + epic to completed/ with board anchor sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Final story: make the canonical docs and graph tell the truth the code now
is, retire the patch lane, prepare closure walks.
