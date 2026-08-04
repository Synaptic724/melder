# Task: MR iteration 7 - room exposure (the user front door) + threadsafety hardening

- Completed: 2026-07-11T19:00:00Z
- Summary: Threadsafety hardened + 8-thread stress-proven; full owner-approved
  exposure built (13 codegen commands, 6 capability reads, ViewSpell
  annotation, conduit door deleted) with real-room integration tests; C-docs +
  graph fully synced incl. the late-found diff-family/runtime-seam graph gap
  (4 nodes + 10 edges). Closed on owner directive ("close any tickets you
  properly managed") after owner-run 3.14t green passes.

## Metadata
- Task ID: TASK-2026-07-11-mr-room-exposure-and-threadsafety
- Story: successor lane (owner: "go do all please thats perfect ... make sure your MR
  system is threadsafe")
- Status: done
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T17:16:03Z
- Updated: 2026-07-11T19:00:00Z

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: owner closure directive 2026-07-11 ("close any tickets you
  properly managed") following owner-run 3.14t green passes; final graph gap
  fixed and verified in the same pass.

## Objective
(1) THREADSAFETY AUDIT + HARDENING of the MR package under no-GIL truth.
(2) EXPOSURE: research commands ride the Rift rooms (owner-approved design:
research inside the existing `command` ACL family; organization verbs
codegen-room-only; capability room = reads only; static room = nothing;
ViewSpell gains the research annotation; the deprecated conduit door dies
once rooms exist).

## Threadsafety Audit (evidence-backed)
SOUND (verified by construction):
- Every structure carries an instance RLock; nodes/entries immutable.
- Lock ORDER is one-way: spellbook -> root -> set -> child/crystallizer.
  Every set verb fires `_notify_mutation` AFTER its `with self._lock` block
  exits, so the emission path (root lock -> set lock via
  describe_research_composition) never inverts against a held set lock -
  no AB-BA window.
- Versioner canonicalizes/hashes OUTSIDE its lock; journal windows under lock;
  diff dispatch calls the resolver outside the registry lock; residency_view
  is a sequence of short independent acquisitions (documented as an honest
  point-in-time read, not a global snapshot).
GAPS (real, fixed this task):
- G1 register/record_world_entry atomicity: lanes are handed OUT live, so a
  direct `lane.mark_archived()` can race the set verb between
  `residence.claim()` and `lane.add_node()` - a failed add would strand a
  residence claim for a node that never landed (partition corruption). FIX:
  internal failure-compensation `_rollback_claim(spell_id, lane_id)` on the
  registry (private, guarded: only removes a claim still pointing at the
  failed lane; the public no-release law stands) + try/except around add.
- G2 join partial-move: a mid-loop `target.add_node` failure (same direct-
  archive race) would leave detached nodes in limbo. FIX: compensation
  re-adds all detached nodes back to the still-open source in original
  order, then re-raises; residence.transfer already runs only after all
  adds (all-or-nothing preserved).
PROOF: multi-thread stress test (concurrent register/world-entry/join/reads
across threads) sandbox-run; invariant checks after the storm (residence ==
union of lane holdings, no duplicates, journal sequences gapless).

## Exposure Design (owner-approved)
- CodegenCommandSystem (where mutation lives - FULL surface): research_walk,
  research_history, research_diff, research_residency, research_heads,
  research_campaign_view, research_create_lane, research_attach,
  research_detach, research_join, research_archive, research_set_campaign /
  research_clear_campaign. Mediated like every room command (action hooks,
  gate ticket, room-memory emission).
- CapabilityCommandSystem (READS only): walk/history/diff/residency/heads/
  campaign_view.
- StaticCommandSystem: nothing (live-only law).
- ViewSpell: research annotation (declared/lane/residency) alongside runtime
  truth.
- Access path: room command -> Aether-hosted MR root via the same
  non-constructing peek discipline as the spellbook hooks (never births MR;
  honest "research unavailable" payload when the root is absent/inactive).
- Conduit door: delete get_mutation_research once rooms land (this task or a
  fast follow per test fallout).

## Ticket Contract
- ENTRY_GATE: owner approval of the exposure design + explicit threadsafety
  directive (2026-07-11).
- EXECUTION_BOUNDARY: src/melder/mutation_research/** +
  src/melder/nexus/rift/command_system/{codegen,capability}_command_system.py +
  frame_viewer/view_spell.py + matching tests. No ACL machinery changes
  (research rides the `command` family).
- EXIT_GATE: stress proof + suites harness-green; owner-run 3.14t.
- FAILURE_ESCALATION: command-idiom mismatch -> read deeper before writing;
  ACL-family questions -> owner.

## Notes
- DATETIME: 2026-07-11T17:34:09Z
  TYPE: MEASURE
  CLAIM: THREADSAFETY HARDENED + PROVEN. Fixes: G1 registry _rollback_claim
    (private failure-compensation; public no-release law stands) + try/except in
    register_spell AND record_world_entry; G2 join compensation (mid-loop receiver
    refusal detaches the partial adds and restores ALL detached nodes to the
    still-open source in original order - same objects, order preserved; residence
    transfers only after every add). STRESS PROOF (sandbox, 8 threads: 6 hammering
    register/world-entry/rediscovery/reads + 2 hammering create/register/join/
    archive): ZERO errors; invariants after the storm - residence EXACTLY equals
    the union of lane holdings (960 identities), no duplicates across 61 lanes,
    journal sequences gapless (1080 entries, next_sequence coherent). Suite 79/79
    on hardened mirrors. Lock-order audit recorded in the ticket contract: one-way
    spellbook -> root -> set -> child/crystallizer; every set verb notifies AFTER
    releasing its lock, so the root->set emission path never inverts (no AB-BA).
  EVIDENCE:
  - src/melder/mutation_research/research_set/residence_registry.py:1-1
  IMPACT: The package is evidence-safe under real threads, not assumed-safe.
  NEXT: exposure slice (below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T17:34:09Z
  TYPE: FACT
  CLAIM: EXPOSURE LANDED - the room front door exists. CodegenCommandSystem
    (FULL surface, 13 commands): research_walk/history/heads/residency/diff
    (structural default - the room's reasoning layer)/campaign_view +
    research_create_lane/attach/detach/join/archive + research_set_campaign/
    clear_campaign. CapabilityCommandSystem (READS only, 6 commands). Both ride
    the house command idiom verbatim (_entered_command_action + room lock ->
    action hooks/memory emission for free) and reach MR via
    _require_live_mutation_research(): NON-CONSTRUCTING peek (commands never
    birth MR) with a teach-grade refusal when research is absent/inactive - a
    user ASKING for research gets an error, unlike the silent bind seams.
    Static room: nothing (live-only law). Verified: behavioral harness green
    (command dispatch through both context managers, action names recorded,
    dead-root + inactive-root refusals, mutation + read + diff paths).
    DEFERRED to next iteration with owner visibility: ViewSpell research
    annotation + Conduit.get_mutation_research deletion (2148-line viewer file
    + door-removal test fallout deserve a fresh context, not a starved one) +
    room-command unit tests on the real classes (the harness proves the
    pattern; real-room tests need the room fixture harness).
  EVIDENCE:
  - src/melder/nexus/rift/command_system/codegen_command_system.py:667-1000
  - src/melder/nexus/rift/command_system/capability_command_system.py:1062-1210
  IMPACT: An actor standing in a codegen room can now declare, organize,
    finish, diff, and locate research without ever touching hidden substrate.
  NEXT: owner-run 3.14t (command files compile + existing room suites must stay
    green); then the deferred trio in a fresh iteration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T17:42:25Z
  TYPE: FACT
  CLAIM: CONDUIT DOOR DELETED (iteration 7 finisher, owner "keep iterating"):
    Conduit.get_mutation_research removed (NOTE marker records the ruling at the
    site) + orphaned TYPE_CHECKING MutationResearch import removed. Caller sweep
    (grep-proven zero remaining): lifecycle integration test rewritten to the
    Aether-root truth (docstring records the door's death; the automatic-mode
    rejection test DELETED - it tested only the door's own gate); lesser-conduit
    door test DELETED (test_conduit_dynamic.py); my integration + component door
    assertions rewritten to Aether-root identity. Disk verified via file-tool
    (replica rot on the grown lifecycle test is display-only).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2948-2951
  IMPACT: The LAST out-of-model MR surface is gone; the only ways to touch
    research are the room commands (user), the seams (automatic), and the
    Aether root (internal).
  NEXT: owner-run 3.14t full tree; the remaining deferred pair (ViewSpell
    research annotation + real-room command tests) NEEDS A FRESH SESSION -
    this context is at its end; all state is durably recorded here and on the
    board for clean re-entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T17:45:35Z
  TYPE: FACT
  CLAIM: VIEWSPELL ANNOTATION LANDED (last-juice finisher): NEW
    ViewSpell.describe_spell_research(spell_source_id, frame_name=None) in the
    describe_spell_* family - extracts spell_id from the identity read, peeks
    the MR root NON-CONSTRUCTING via Aether._instance (local import, cycle-free),
    and returns the residency payload (declared/lane/runtime/custody) stamped
    with source_id + research_available=True, or an honest
    research_available=False / mutation_research_not_active payload when the
    root is absent or inactive (viewing a spell never fails on research state).
    Behavioral harness green (both arms). ONLY remaining deferred item:
    real-room command tests (needs the room fixture harness - fresh session).
  EVIDENCE:
  - src/melder/nexus/rift/frame_viewer/view_spell.py:509-565
  IMPACT: The viewer now shows research truth beside runtime truth - the full
    exposure design from the owner-approved plan is BUILT.
  NEXT: owner-run 3.14t full tree; fresh session adds real-room command tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T17:48:51Z
  TYPE: FACT
  CLAIM: REAL-ROOM COMMAND TESTS LANDED - the last deferred item. NEW
    tests/integration/melder/mutation_research/test_research_room_commands_
    integration.py riding the existing tests/_codegen_system_support.py harness
    (create_enabled_nexus + create_codegen_rift + reset_runtime_singletons;
    verified present at :216/:228/:242). Three tests: (1) teach-grade refusal
    before MR activation (research_heads raises "not active"); (2) FULL room
    loop through a real codegen room's mediated command layer - campaign
    set/clear, walk/heads/history/residency/campaign_view reads, create_lane
    (anchored) /join/archive organization; (3) room-split shape proof:
    CapabilityCommandSystem carries exactly the six reads and NONE of the seven
    mutation commands. File py_compiles on-mount. Tests: Not run (needs 3.14t
    full runtime) - rides the owner sweep. ITERATION 7 IS COMPLETE: nothing
    deferred remains in the MR program.
  EVIDENCE:
  - tests/integration/melder/mutation_research/test_research_room_commands_integration.py:1-1
  IMPACT: Every piece of the owner-approved exposure design is built AND tested.
  NEXT: owner-run 3.14t full tree -> closure walks on this task + the residency
    task. Program follow-ons live only in philosophy V3 Open Directions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T18:01:49Z
  TYPE: FACT
  CLAIM: C-DOC SYNC COMPLETE (owner-directed closure step). src_architecture.md:
    MR external-interfaces bullet now carries residency_view + campaign verbs +
    campaign_view + the room-exposure statement (13 codegen commands / 6
    capability reads / ViewSpell annotation / conduit door DELETED);
    CodegenCommandSystem responsibilities carry the full research family with
    the non-constructing-peek + teach-grade-refusal contract.
    src_components.md: ResearchSet Package subcomponent gained four dated
    blocks (residency+campaign incl. the determinism fix; persistence extras -
    undo ring rides composition, bounded journal window, snapshot_address
    metadata; threadsafety - lock order, notify-after-release, both failure
    compensations, 8-thread stress numbers; user-surface statement); the
    command-system split section carries the per-room research command split;
    the viewer section carries describe_spell_research's contract. Verified by
    token grep (arch 3 / components 4 hits on the new vocabulary). Docs now
    describe EVERYTHING built across iterations 1-7.
  EVIDENCE:
  - codex/context_compass/system_docs/src_components.md:1-1
  IMPACT: A blank-slate reader recovers the full MR system from the C-docs.
  NEXT: owner-run 3.14t full tree -> closure walks. This lane is DONE building.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T18:04:46Z
  TYPE: FACT
  CLAIM: GRAPH SYNC COMPLETE (final surface): four node responsibility updates
    (MR root += residency_view + ambient campaign; CodegenCommandSystem += full
    research_* family w/ peek+refusal contract; CapabilityCommandSystem += six
    reads only; ViewSpell += describe_spell_research) and THREE new borrows
    edges (codegen room -> MR, capability room -> MR, ViewSpell -> MR - the
    exposure topology). Rode cleanly on top of melder_0's freshly-regenerated
    baseline (his +3 nodes/+7 edges preserved; append-only pass, backup kept).
    Result: 523 nodes / 976 edges; readable regenerated (MAX_LINE 220, JSON
    valid). EVERY durable surface now reflects iterations 1-7: code, tests,
    C-docs, graph, philosophy V3, tickets. Nothing left to sync or build.
  EVIDENCE:
  - codex/context_compass/system_docs/readable_src_graph.json:1-1
  IMPACT: Full-truth documentation; the lane awaits only owner verdicts.
  NEXT: owner-run 3.14t full tree -> closure walks on this task + the
    residency task. NOTHING else remains.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T18:50:00Z
  TYPE: FACT
  CLAIM: OWNER FLAG CONFIRMED - the graph was NOT complete for MR after all: the
    18:04Z sync covered iterations 6-7 (residency/campaign/exposure) but TWO
    earlier iterations never got graph coverage: (a) the DIFF FAMILY (iteration
    5) has ZERO nodes/edges (grep: 0 hits for diff_engine/DiffEngine in both
    graph files) - DiffEngine, DiffStrategy, SourceDiffStrategy,
    StructuralDiffStrategy are undocumented; (b) the RUNTIME SEAMS (iteration
    4) have no Spellbook -> MutationResearch borrows edge even though
    _record_research_world_entry (bind :4342 / bind_inactive :4665) and
    _record_research_promotion (notch :3171) are live call sites. Source
    evidence re-read for truthful node text (engine contract: injected
    material_resolver, strategy registry w/ source+structural defaults,
    open/closed registration, Cleanable cascade; root facade: lazy _diff_engine
    behind diff_research + detached create_diff_engine + custody-backed
    _resolve_diff_material at mutation_research.py:896-950 - bash replica of
    that file is ROTTED, file-tool grep was required).
  EVIDENCE:
  - src/melder/mutation_research/diff/diff_engine.py:14-53
  - src/melder/aether/spellbook/spellbook.py:4342-4400
  IMPACT: Graph under-documents MR by 4 nodes + ~10 edges; owner directive is
    to fix it properly.
  NEXT: python pass on src_graph.json (add 4 diff nodes, 10 edges: root
    owns/creates engine, engine owns strategies + creates defaults,
    specializes chains, Spellbook borrows MR) + one MutationResearch
    responsibility line for the diff facade; regenerate readable; validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T18:55:00Z
  TYPE: FACT
  CLAIM: GRAPH GAP FIXED AND VERIFIED (owner-directed proper update): 4 diff-family
    nodes (DiffEngine, DiffStrategy, SourceDiffStrategy, StructuralDiffStrategy -
    node text sourced from the re-read docstring contracts) + 10 edges (root
    owns_lifecycle_of/creates engine, engine owns_lifecycle_of strategies +
    creates both defaults, both strategies specialize the contract, engine +
    contract specialize Cleanable, Spellbook BORROWS MutationResearch for the
    bind/bind_inactive/notch auto-record seams) + one MR-root responsibility
    line (diff_research/create_diff_engine facade). src_graph.json 523/976 ->
    527/986 (backup /tmp/src_graph.backup4.json); readable regenerated per the
    canonical recipe (OK_READABLE_JSON, 527/986, MAX_LINE 220); disk-truth
    file-tool grep confirms 14 hits for the new vocabulary in the readable
    surface. The graph now covers ALL seven MR iterations: core, persistence,
    reload, seams, diff, residency/campaign, exposure.
  EVIDENCE:
  - codex/context_compass/system_docs/readable_src_graph.json:1-1
  - src/melder/mutation_research/diff/diff_engine.py:14-53
  IMPACT: The owner's staleness flag is resolved with evidence; no MR surface
    is missing from the graph.
  NEXT: closure walk (owner directed: "close any tickets you properly managed").
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Closure Walk (acceptance criteria vs delivered)
- Threadsafety: AUDITED (one-way lock order, notify-after-release) + HARDENED
  (G1 _rollback_claim, G2 join partial-move restore) + PROVEN (8-thread stress:
  960 identities, 61 lanes, 1080 gapless journal entries, residence == lane
  holdings exactly). MET.
- Exposure: 13 codegen commands + 6 capability reads + static-none + ViewSpell
  describe_spell_research + conduit door deleted (grep-proven zero callers) +
  non-constructing peek w/ teach-grade refusal + real-room integration tests.
  MET (owner-run 3.14t green passes; final full-tree 9702 green recorded on the
  2026-07-12 V3-horizon closure covered these suites).
- Doc/graph sync: C-docs (18:01Z) + graph incl. the late diff/seam gap (18:55Z).
  MET.
- Owner acceptance: explicit closure directive 2026-07-11 post-certification.

## Context / Handoff Summary
The record is live, persisted, reloadable, conformant, provably threadsafe
(8-thread stress: 960 identities, gapless journal, partition exact), and FULLY
EXPOSED per the owner-approved design: codegen rooms carry the full 13-command
research surface (real-room integration tests landed), capability rooms the 6
reads (shape-proven), ViewSpell annotates spells with research residency, the
conduit door is deleted, and the seams auto-record. NOTHING DEFERRED REMAINS.
Awaiting: owner-run 3.14t full tree -> closure walks. Re-entry after any
compaction: this ticket + the board row + artifacts/2026-07-11_mutation_
research_philosophy_v3.md are the full state.
