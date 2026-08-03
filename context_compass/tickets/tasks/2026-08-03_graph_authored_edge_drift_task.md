

# Task: Retire dead authored graph edges to the removed registration guard

## Metadata
- Task ID: TASK-2026-08-03-graph-authored-edge-drift
- Story: none (standalone task)
- Status: review
- Owner: cowork
- Agent Name: aether_0
- Priority: p1
- Created: 2026-08-03T12:24:13Z
- Updated: 2026-08-03T12:39:47Z

## Objective
Correct the two authored graph edges that point at
`melder.__melder_registration_guard__.MelderRegistrationGuard`, a class deleted
by EPIC-2026-07-22-internal-bind-guard-replacement, by editing the owning
DESCRIPTORS and reassembling. Record why the staleness detector reported this
node set 100% AUTHORED while carrying a provably dead edge.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row routing here; the dead edge
  confirmed absent from `src/` by grep, not inferred from documentation.
- EXECUTION_BOUNDARY:
  - `context_compass/system_docs/graph/melder/aether/spellbook/bind/bind.json`
  - `context_compass/system_docs/graph/melder/utilities/ai_native_support_tools/protocol_crafter.json`
  - regenerated `context_compass/system_docs/src_graph.md` + `src_graph_index.md`
  - NOTHING under `src/`. The shipped build assets carry the same false edges
    and are deliberately OUT of this boundary pending an owner ruling.
- DEPENDENCIES: EPIC-2026-07-22-internal-bind-guard-replacement (closed
  2026-07-27) is what removed the class. EPIC-2026-08-01-conflict-manager-zombie
  is the same defect class in a different subject and is awaiting an owner
  DECISION.
- EXIT_GATE: both descriptors truthful against source; graph and index
  reassembled in ONE pass; zero occurrences of the retired identifier in
  `context_compass/system_docs/`; index staleness proof recomputed green.
- FAILURE_ESCALATION: raise DECISION_REQUEST if correcting the edge requires
  authoring semantics that cannot be established by reading source.

## Scope Boundaries
- In scope: the two authored `edges_authored` entries; reassembly of the graph
  document and its index.
- Out of scope: regenerating `src/melder/_build_assets/_system_documents/`;
  re-authoring any other node's semantics; the `--accept` re-stamp of nodes
  whose prose was not changed; any fix to `graph_walker.py`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: dead edge confirmed against source by grep over `src/`;
  correct edge target confirmed to exist as an included node; board row created.
- from_state: in_progress
- to_state: review
- transition_reason: both descriptors corrected against source, graph and index
  reassembled in one pass, retired identifier absent from every live surface,
  index staleness proof recomputes green, and drift cleared on all seven files
  measured at the start of the lane. Awaiting acceptance.

## Steps / Checklist
- [x] Confirm the retired class is absent from `src/` (grep, not inference).
- [x] Read `bind.py` source to establish the real mechanism.
- [x] Confirm `protocol_crafter.py` has zero guard/sentinel references.
- [x] Confirm `melder._build_assets._bind_guard.bind_guard` exists as an
      included node so the replacement edge has a real target.
- [x] Correct `bind.json` authored edge.
- [x] Delete the false `protocol_crafter.json` authored edge.
- [x] Re-run `extract_graph.py` then `assemble_graph.py` (never one without the other).
- [x] Verify: retired identifier absent; index proof green.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding immediately in `## Notes`.

## Deliverables
- Two corrected descriptors.
- Regenerated `src_graph.md` and `src_graph_index.md`.
- A recorded explanation of the staleness blind spot for the tooling lane.

## Files / Paths Impacted
- context_compass/system_docs/graph/melder/aether/spellbook/bind/bind.json
- context_compass/system_docs/graph/melder/utilities/ai_native_support_tools/protocol_crafter.json
- context_compass/system_docs/src_graph.md
- context_compass/system_docs/src_graph_index.md

## Validation
- RUN, by me, this lane. No pytest was executed and none is claimed - this task
  changes no source, so the suite is not the relevant gate.
  - `extract_graph.py` + `assemble_graph.py`: completed. 589 sections, 1217
    nodes, 1450 edges, 25,586 lines; all 589 ranges verified against their own
    headers by the assembler.
  - Retired identifier across `context_compass/system_docs/`: 0 occurrences on
    every live surface. Five hits remain and are DELIBERATELY LEFT - see notes.
  - Index staleness proof recomputed against the written document:
    line_count 25586 == 25586, content_sha256 match, VERDICT GREEN.
  - `source_sha256` drift re-measured on the seven files sliced at the start of
    this session: 7/7 MATCH (was 5/7 DRIFT).
  - `graph_walker.py --report`: 1180 AUTHORED / 21 SEMANTICS_STALE / 16
    UNSEMANTIC / 0 RETIRED.
- NOT run and NOT claimed: `pytest`. Coverage: not measured.

## Risks / Rollback Notes
- Reassembly rewrites the whole document; rollback is `git checkout` of
  `system_docs/src_graph.md`, `src_graph_index.md`, and the two descriptors.
- Re-extraction refreshes the mechanical tier for EVERY descriptor, so the diff
  will be wider than the two files edited. That is expected and is the tier the
  script owns; authored prose is not touched.

## Applicable Anti-Patterns
- [ ] Hand-editing `src_graph.md` or `src_graph_index.md` instead of descriptors.
- [ ] Regenerating the document without the index, or the reverse.
- [ ] Promoting an edge candidate to an edge without reading the code.
- [ ] `--accept` re-stamping a node without re-reading its source.
- [ ] No status transition without evidence-backed transition reason.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.

## Notes
- DATETIME: 2026-08-03T12:24:13Z
  TYPE: FACT
  CLAIM: `melder.__melder_registration_guard__.MelderRegistrationGuard` does not
    exist anywhere in `src/`. Every occurrence is inside GENERATED artifacts. The
    live mechanism is the module-level function `assert_allowed`, which refuses
    when `(module, qualname)` is present in `INTERNAL_MANIFEST`, imported from
    the hand-written loader `melder._build_assets._bind_guard.bind_guard`.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:20-21
  - src/melder/aether/spellbook/bind/bind.py:53-97
  - src/melder/aether/spellbook/bind/bind.py:364
  - context_compass/system_docs/src_graph.md:5012
  IMPACT: An authored edge asserts a collaboration with a class that cannot be
    imported. Any agent reasoning about registration refusal from the graph is
    routed to a non-existent module.
  NEXT: Repoint the edge at the loader module node.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T12:24:13Z
  TYPE: FACT
  CLAIM: The `ProtocolCrafter -> MelderRegistrationGuard` edge is false in BOTH
    halves, not merely stale. `protocol_crafter.py` contains zero references to
    any guard, sentinel or `assert_allowed`. Its `why` text describes the
    retired `__melder_internal__` sentinel by which a class marked ITSELF
    internal. Under the replacement, membership is asserted EXTERNALLY by a
    generated manifest, so ProtocolCrafter is SUBJECT TO the guard and is not a
    user of it. There is no replacement edge to author - being listed in a
    manifest is not a dependency the listed class has.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:1-2710
  - src/melder/aether/spellbook/bind/bind.py:71-73
  IMPACT: Deleting is correct; repointing this one at the loader would invent a
    collaboration that does not exist.
  NEXT: Delete the edge outright.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T12:24:13Z
  TYPE: FACT
  CLAIM: THE STALENESS DETECTOR CANNOT SEE THIS CLASS OF DEFECT, and the reason
    is structural rather than a bug to patch. TWO independent blindnesses stack.
    (1) `graph_walker.py:94` reads BOTH sides of its comparison out of the
    descriptor - `stamp, current = node.get(STAMP), node.get("span_sha256", "")`
    - so it detects "authored prose predates the last extraction", NOT "source
    moved". With no re-extraction the census reports 100% AUTHORED however far
    `src/` has drifted; `--src` only powers the stranded-descriptor check. The
    census read 1201/1201 AUTHORED, 0 SEMANTICS_STALE, while carrying this dead
    edge. (2) Even after re-extraction this node stays green: the `Bind` class
    span is byte-identical on disk and in the descriptor (`2a6a804713a3ec16`),
    because the guard replacement landed at MODULE level - imports at :20-21,
    `_internal_identity_of` at :24, `assert_allowed` at :53 - all outside
    `class Bind`, which begins at :115. GENERALISED: any authored edge whose
    subject matter lives outside its node's own span is undetectable by
    span-scoped hashing, and edges are exactly the kind of claim that routinely
    describes something outside the node they hang off.
  EVIDENCE:
  - context_compass/tools/system_documents/python/graph_walker.py:94-96
  - context_compass/system_docs/graph/melder/aether/spellbook/bind/bind.json:38
  - src/melder/aether/spellbook/bind/bind.py:115
  IMPACT: The 100%-AUTHORED census on the graph-semantics epic cannot be read as
    evidence that authored prose matches source. It says extraction has not run
    since authoring, which is a different and much weaker claim.
  NEXT: Record for the tooling lane; do not attempt a walker fix under this
    ticket's boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T12:39:47Z
  TYPE: BLOCKER
  CLAIM: RESOLVED, but recorded because the next agent will hit it. Running
    `extract_graph.py` with `--out` pointed at the mounted repository fails with
    `OSError: [Errno 22] Invalid argument` on `write_text`, part-way through the
    run, inside
    `system_docs/graph/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/`.
    It is NOT a bad path: the targets already exist, `touch` on them succeeds,
    and the repo-relative path is 185 chars. It is NOT deterministic either -
    two runs failed on DIFFERENT files in that directory and the second got
    further (69 -> 182 descriptors written), so it is the mount choking under
    sustained small writes into a deep tree. WORKAROUND USED: copy the
    descriptor tree to sandbox-local storage, run extract + assemble there, then
    sync back only the files whose content actually differed (119 of 590) with a
    throttled retry loop. 119 written, 0 failed.
  EVIDENCE:
  - context_compass/tools/system_documents/python/extract_graph.py:571
  IMPACT: A partial extract leaves the descriptor tree half-refreshed. It is not
    corrupt - the tool refreshes only the mechanical tier and preserves authored
    prose, so re-running converges - but an agent who does not notice the
    traceback will assemble from a mixed tree and publish it.
  NEXT: None for this lane. If this recurs, do the work locally and sync back.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T12:39:47Z
  TYPE: MEASURE
  CLAIM: Regeneration complete and verified. Retired identifier: 0 occurrences
    on every live surface. Index proof GREEN (25,586 lines, sha match). Drift on
    the seven files measured at session start: 7/7 now MATCH, was 5/7 DRIFT.
    THE CENSUS NOW MEANS SOMETHING: it moved from 1201/1201 AUTHORED with 0 stale
    - which was vacuous, because nothing had re-extracted - to 1180 AUTHORED /
    21 SEMANTICS_STALE / 16 UNSEMANTIC. Those 21 are REAL drift that was always
    there and simply could not be seen, and they include `Conduit`, `Spellbook`,
    `Mediator`, `AetherConfiguration` and `ChangeControlConflictManager`. They
    are deliberately NOT `--accept`ed here: accepting without re-reading the
    source is the one anti-pattern the walker's own documentation calls out, and
    re-authoring 21 nodes is a different task with a different boundary.
  EVIDENCE:
  - context_compass/system_docs/src_graph_index.md:1-25
  IMPACT: The graph is safe to slice again, and the backlog it was hiding is now
    visible and countable rather than reported as zero.
  NEXT: Owner decides whether the 21 stale nodes become their own re-authoring
    lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T12:39:47Z
  TYPE: DECISION
  CLAIM: Five occurrences of the retired identifier remain under
    `system_docs/patches/active/*/src_graph.expanded.json` and are LEFT
    UNTOUCHED ON PURPOSE. Those are frozen snapshots taken by patch lanes dated
    2026-06-12 to 2026-07-18, when the class still existed. They are historical
    records, not consumption surfaces, and rewriting them would falsify the
    record of what the graph WAS. They are also outside this ticket's declared
    EXECUTION_BOUNDARY.
  EVIDENCE:
  - context_compass/system_docs/patches/active/graph_dangling_edge_repair_2026_07_18/src_graph.expanded.json
  IMPACT: A future grep for the retired name will hit these five. This note is
    what stops someone "finishing the job" by editing history.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Two authored edges name a class deleted on 2026-07-27. Both are being corrected
at the descriptor level and the graph reassembled; `src_graph.md` is generated
and is never hand-edited. The durable finding is the third note: the staleness
detector compares the descriptor against itself and hashes only class spans, so
it is structurally blind to a dead edge whose mechanism lives at module scope.
The same false claims are baked into the shipped build assets under
`src/melder/_build_assets/_system_documents/`, which is OUT of this task's
boundary and needs an owner ruling - it is the same defect class already open on
EPIC-2026-08-01-conflict-manager-zombie.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
