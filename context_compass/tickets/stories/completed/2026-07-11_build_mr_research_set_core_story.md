

# Story: Build the MutationResearch ResearchSet core (SOLID, crystallizer-docking-ready)

## Metadata
- Story ID: STORY-2026-07-11-build-mr-research-set-core
- Epic: none (program seed; spawned EPIC-2026-07-11-mutation-research-restore-build-stage for melder_0)
- Status: done
- Owner: cowork
- Agent Name: mutation_0
- Priority: p0
- Created: 2026-07-11T12:51:03Z
- Updated: 2026-07-11T15:41:58Z
- Closed: 2026-07-11T15:41:58Z (owner acceptance: "yeah close it if we're done")

## User Narrative
As the project owner, I want the converged MR model built as a SOLID, standalone core -
ResearchSet as the overarching container of research lanes with the agreed verb surface -
so agents can formally declare, organize, and understand spell change, with crystallizer
twin docking added later (MutationResearchCrystal Phase-B).

## Value / MRP Alignment
Replaces the senseless May skeleton with the owner-converged model. MRP: core structures,
invariants, and lifecycle correct first; persistence docking and diff engine layer on
without rework.

## Ticket Contract
- ENTRY_GATE: owner design convergence + explicit build go (2026-07-05..11 discussion,
  recorded in TASK-2026-07-05-wire-mutation-research-git-system).
- EXECUTION_BOUNDARY: src/melder/mutation_research/** (teardown + new research_set/
  package + root rewire) and tests/**/mutation_research/** (+ removal of dead
  spellbook/mutations test tree). NO crystallizer edits; NO twin extension (deferred by
  owner); Conduit.get_mutation_research left in place (deprecation flagged only).
- DEPENDENCIES: crystallizer for docking LATER (owner: MR depends on crystallizer;
  objects represented in its persistence layer by default). None for this story's code.
- EXIT_GATE: package compiles; new unit tests authored (user-run 3.14t validation);
  owner walkthrough of the verb surface.
- FAILURE_ESCALATION: CONFLICT note if teardown breaks non-MR surfaces beyond the
  flagged test tree; DECISION_REQUEST on any verb-semantics ambiguity found mid-build.

## Requirements (Functional)
- ResearchSet: register_spell, create_lane, attach/detach, join (divergence-aware,
  collapse dial, force supersede), archive, walk, history, heads, describe,
  network snapshot/restore. Guaranteed "default" lane.
- ResearchLane (one object's line; open->joined|archived), ResearchNode (pure data,
  crystal_id REQUIRED), TransitionEntry+TransitionAct (forward-only journal events,
  campaign stamp), ResearchJournal (monotonic, filtered reads), ResidenceRegistry
  (single-residence partition; permanent through archive; rediscovery errors name the
  existing lane), NetworkVersioner (content-addressed org snapshots, bounded ring).
- Root: sets-by-name registry with guaranteed "default" set; killed session/facade APIs
  removed; lifecycle + RecordedUnitState emissions preserved.

## Requirements (Non-Functional)
- SOLID per owner directive; house rules: Cleanable + RLock + del-teardown, no
  dataclasses, rich contract docstrings, typing mandatory (Optional/Union, no PEP 604),
  no module-level state, methods ~50-60 LOC.
- describe()/from_payload seams on every structure (twin docking readiness).
- Journal is append-only and SURVIVES network restore.

## Scope Boundaries
- In scope: teardown (research/, mutation_conduit.py, mutation_frame.py, dead tests),
  research_set/ package, root rewire, new unit tests.
- Out of scope: MutationResearchCrystal Phase-B extension + emission/hydration (owner
  deferred); diff engine (next story); bind/notch seam wiring; impact engine.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner explicit "go ahead and implement all this" (2026-07-11).

## Tasks (Implementation Checklist)
- [x] S1 teardown: delete research/, mutation_conduit.py, mutation_frame.py + dead tests
- [x] S2 core structures: transition_act/entry, research_node, lane_state, research_lane,
      research_journal, residence_registry, network_versioner, research_set
- [x] S2 root rewire: sets registry, killed APIs removed
- [x] S4 persistence wiring (owner pulled IN-scope 2026-07-11): twin Phase-B extension +
      root emission seam + hydration verb (restore engine untouched; MR stays a report
      stage)
- [x] S2 unit tests authored (56 harness-green sandbox; validation user-run on 3.14t)
- [x] compile check recorded (mirror-verified where replicas rotted; see notes)
- [x] Enforce Ticket Microcycle across the work.

## Acceptance Criteria
- Old skeleton gone; new package present and compiling; root exposes sets registry.
- Invariants demonstrably enforced in tests: single residence + rediscovery naming,
  join divergence guard + force + collapse, archive permanence, journal monotonicity +
  restore-survival, network snapshot determinism + ring cap.
- Owner confirms verb surface feels right.

## Validation / Test Plan
- Unit tests per class + facade flows. Not run (sandbox is not 3.14t); owner runs
  `pytest tests/unit/melder/mutation_research -q` on 3.14t.

## Risks / Mitigations
- Risk: hidden importers of killed modules. Mitigation: repo-wide grep before deletion
  (done: only dead tests + package-internal references).
- Risk: verb semantics drift from discussion. Mitigation: ticket notes are the spec;
  DECISION_REQUEST on ambiguity.

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN/HYPOTHESIS.
- [ ] No status transition without evidence-backed reason.
- [ ] No closure without acceptance confirmation and board sync.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Story notes: cross-slice synthesis + gate transitions; tactical detail stays in the
  parent investigation task's design-decision notes.

## Notes
- DATETIME: 2026-07-11T12:51:03Z
  TYPE: PLAN
  CLAIM: Build proceeds on the converged spec recorded in
    tickets/tasks/2026-07-05_wire_mutation_research_git_system_investigation_task.md
    (design decisions 2026-07-05..11: lane-first model, single residence, forward-only
    journal, verbs lane/register_spell/attach/detach/join/archive/select-later/restore,
    network self-versioning, zero-runtime-footprint commits, crystal-bound nodes).
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-07-05_wire_mutation_research_git_system_investigation_task.md:1-1
  IMPACT: Single source of spec truth; this story executes it.
  NEXT: S1 teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T13:00:54Z
  TYPE: FACT
  CLAIM: REONBOARD cycle completed at owner request (synaptic_python_developer_onboarding
    workflow) and certified (AGENT_NAME: mutation_0, CERTIFY: APPROVED). Source-doc bundle
    read: src_architecture.md (1792, full), src_components.md (3564, full),
    readable_src_graph.json TARGETED regions only (MR nodes 1290-1329, MR edges 3520-3564,
    crystallizer/persistence nodes 1820-1883, Aether ownership edges 1893-1909) - full
    byte-read of the 742KB graph would force immediate re-compaction; escalation per
    engineer SKILLS on-demand rule raised to owner in-session. Owner re-confirmed the
    research_set/ + diff/ folder structure verbatim and the S1 kill list; owner asked to
    retrace the converged design and DISCUSS before building. Preflight re-verified on
    disk: MR package = 5 root files + research/ subtree (no __init__.py anywhere); dead
    test tree confirmed at tests/unit/melder/spellbook/mutations/** +
    tests/component/melder/spellbook/mutations/test_research_component.py; root tests at
    tests/{unit,component,integration}/melder/mutation_research/ (matrix + integration
    reference the dying session API and need rewrite with the root rewire).
  EVIDENCE:
  - codex/context_compass/system_docs/readable_src_graph.json:1297-1327
  - src/melder/mutation_research/mutation_research.py:399-429
  IMPACT: Onboarding gate satisfied; design record + blast radius fresh; build blocked
    only on the owner discussion the owner just requested.
  NEXT: Owner design walkthrough -> resolve remaining dials -> S1 teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T13:46:01Z
  TYPE: DECISION
  CLAIM: Owner rulings at build-go: defaults accepted (join keep-history default +
    collapse dial + force supersede; auto-default-lane; select DEFERRED to the seam
    slice; campaign stamp + permanent residence baked). Persistence wiring pulled
    IN-scope ("you can also wire into the persistence system"). Single-residence
    re-affirmed ("we do not want the same spell_id (this is the sha)"). Owner bet
    confirmed by source: SpellCrystal adopts spell.spell_id as its manifest id, so the
    node's spell_sha IS the custody-crystal reference - no separate crystal_id field.
  EVIDENCE:
  - src/melder/crystallizer/crystals/spell_crystal.py:149-151
  IMPACT: ResearchNode carries spell_sha + module_sha + parents only; Phase-B twin
    extension authorized now instead of deferred.
  NEXT: implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T13:46:01Z
  TYPE: FACT
  CLAIM: BUILD LANDED. S1: research/** + mutation_conduit.py + mutation_frame.py +
    dead test trees (tests/{unit,component}/melder/spellbook/mutations/**) deleted
    (delete permission granted via harness after mount refused rm). S2: research_set/
    package authored - transition_entry.py (TransitionAct world-entry vocabulary, NO
    rollback acts + immutable TransitionEntry), research_node.py (reference-based,
    spell_sha=custody key), research_journal.py (monotonic append-only, bounded
    describe window, from_payload continues minting), residence_registry.py (single
    residence, permanent, rediscovery names holder, all-or-nothing transfer),
    research_lane.py (LaneState open->joined|archived + ordered full-object records +
    anchor + detach_nodes join mechanic), network_versioner.py (content-addressed org
    snapshots, canonical-JSON SHA256, FIFO ring, dedupe), research_set.py (facade:
    create_lane/register_spell/attach/detach/join/archive/walk/history/heads/
    snapshot_network/restore_network/describe_composition/from_payload; on_mutation
    callback = DIP emission seam). Root rewired: sets registry w/ guaranteed default
    set, session/facade APIs gone, _emit_research_composition (single crystallizer
    touchpoint; guards root-active + crystallizer live), load_recorded_composition
    hydration verb; activate() re-emits composition. Persistence: MutationResearchCrystal
    Phase-B additive (composition_payload); MutationResearchConfiguration gained
    describe_configuration_payload() (activate() refactored onto it);
    Conduit.get_mutation_research docstring-flagged deprecated. Tests: 7 research_set
    unit files + 4 root files rewritten to the new surface (root/matrix/integration/
    component).
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:1-1
  - src/melder/mutation_research/mutation_research.py:1-1
  - src/melder/crystallizer/crystals/mutation_research_crystal.py:40-77
  IMPACT: The converged MR model exists in code, persistence-wired, standalone-testable.
  NEXT: verification record (below), then owner 3.14t run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T13:46:01Z
  TYPE: MEASURE
  CLAIM: Verification (sandbox Py3.10; NOT the owner 3.14t bar): (1) research_set
    package compiles on-mount; full behavioral smoke GREEN via stub package tree
    (register/rediscovery/anchored lanes/parent gating/clean join/divergence
    refusal/force/collapse residence split/archive rules/walk-history-heads/restore
    with journal survival/hydration roundtrip with sequence continuity/hook cadence).
    (2) 56/56 research_set unit tests green under a pytest-raises shim harness.
    (3) Replica-rot fault (known mount class): grown/rewritten files read
    NUL-tailed/truncated on the bash mount while file-tool disk is intact
    (mutation_research.py 1861 NULs @19603; config + crystal + matrix/component/
    integration tests truncated). Verified via context-mirror heredoc py_compile:
    root, config-method harness (executed), crystal harness (executed), matrix,
    component, integration ALL SYNTAX OK. Root-level unit tests (MagicMock aether)
    and integration/component suites: Not run (need real deps / 3.14t) - owner runs
    pytest tests/{unit,component,integration}/melder/mutation_research -q.
  EVIDENCE:
  - tests/unit/melder/mutation_research/research_set/test_research_set.py:1-1
  IMPACT: Core engine behaviorally proven pre-handoff; remaining risk concentrated in
    the thin root registry + harness suites, exactly where the owner run lands.
  NEXT: owner 3.14t verdicts -> triage or acceptance walk; then graph/C-doc sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T13:48:15Z
  TYPE: MEASURE
  CLAIM: OWNER-RUN 3.14t GREEN: "they all passed" (2026-07-11) across the full MR test
    program - 7 research_set unit files + rewritten root unit + matrix + component +
    integration suites. Zero triage fallout. The exit-gate validation bar is met; story
    closure awaits the owner acceptance walk.
  EVIDENCE:
  - tickets/stories/2026-07-11_build_mr_research_set_core_story.md:1-1
  IMPACT: The converged MR core + persistence wiring is validated on the real runtime;
    remaining lane work is documentation sync (graph + C-docs) and the follow-on slices
    (diff engine; runtime seam w/ select + staged/promoted acts).
  NEXT: Owner acceptance walk -> closure + doc/graph sync, or straight into the next
    slice per owner direction.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T14:01:35Z
  TYPE: FACT
  CLAIM: ITERATION 2 LANDED (owner "keep going"). (1) DOC/GRAPH SYNC: src_graph.json
    surgically rebuilt via sandbox python (backup kept at /tmp; 7 dead MR nodes + 15
    dead edges removed; 7 research_set nodes + 16 edges added incl. MR->ResearchSet
    ownership, MR->Crystallizer emission seam, and Cleanable specializations; MR root
    node re-described) -> 520 nodes / 966 edges; readable regenerated per canonical
    recipe (source src_graph.json, output readable_src_graph.json, MAX_LINE_LEN 220,
    OK_READABLE_JSON); disk truth verified via file-tool grep (ResearchSet present,
    MutationConduit zero). Both C-docs synced: architecture (coverage/evidence/external-
    interface verb surface/C1 map/unknown+open-question statuses) and components
    (unknowns block, frame no-mutation-dimension ruling, MutationResearch Root
    subcomponent rewritten, NEW ResearchSet Package subcomponent added, dead
    MutationConduit/MutationFrame facade subcomponents deleted); zero stale references
    remain outside intentional sync notes. (2) DIFF SLICE: diff/ package authored -
    diff_strategy.py (DiffStrategy ABC), strategies/source_diff_strategy.py (per-module
    verdicts: unified diffs where text exists both sides - synthetic modules always
    carry source_text; honest fingerprint-only verdicts otherwise - physical text
    retention is melder_0's opt-in S2 lane; added/removed orientation left->right),
    diff_engine.py (injected material resolver + OCP registry, teach-grade errors).
    Root wiring: diff_research(left,right,strategy="source") + create_diff_engine() +
    _resolve_diff_material (crystallizer.get_spell_crystal(sha).describe() ->
    sources/fingerprints; RAISES on dead/inactive custody - no fabricated material);
    _diff_engine slot + cleanup cascade. Tests: 2 new diff unit files (12 cases,
    harness-green 12/12 in sandbox) + 2 root diff-wiring tests added (mock custody
    side-effects + dead-custody refusal) - root additions Not run (3.14t).
  EVIDENCE:
  - codex/context_compass/system_docs/src_components.md:2570-2624
  - src/melder/mutation_research/diff/diff_engine.py:1-1
  IMPACT: Docs/graph no longer lie about MR; the "diffs are derived, never storage"
    read exists end to end from custody material.
  NEXT: owner runs the diff + updated root suites on 3.14t; then the runtime-seam
    slice (select + staged/promoted acts over notch/bind_inactive) is the remaining
    program item.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T14:15:34Z
  TYPE: FACT
  CLAIM: ITERATION 3 LANDED (owner "keep iterating"; iteration-2 verdicts owner-run
    GREEN "its all good passed"). (1) STRUCTURAL DIFF - the May reasoning layer:
    strategies/structural_diff_strategy.py (AST shapes per module: module docstring,
    added/removed/changed functions and classes; per-callable aspect flags
    signature_changed [decorators+args+returns+async] / docstring_changed /
    body_changed [docstring-stripped ast.dump SHA256]; parse errors loud naming the
    failing side; fingerprint-only modules land in text_unavailable_modules, never
    judged; comments/whitespace correctly invisible). Registered as an engine default
    alongside "source". (2) TWIN DOCKING COMPLETE - hydration-at-activation: NEW
    additive read facade describe_mutation_research_record() on PersistenceProfile ->
    PersistenceSystem -> Crystallizer (recorded MR twin describe() dict or None; twin
    never escapes; melder_0 mailboxed second NOTICE - his first was already consumed);
    MutationResearch.activate(hydrate_from_record=True default) rebuilds a VIRGIN
    registry (exactly one untouched default set: 1 lane, 0 nodes, journal seq <= 1)
    from the recorded composition; live research NEVER clobbered (non-virgin skips;
    re-records at next emission); opt-out kwarg; emission ordering preserved
    (hydrate BEFORE the activation re-emit). Tests: test_structural_diff_strategy.py
    (6) + engine default-family/dispatch updates + 3 root hydration tests (virgin
    hydrates / live wins / opt-out). VERIFIED sandbox: 19/19 diff suite harness-green
    (one test-shape mismatch found+fixed: report flattens to changed_functions:{name:
    aspects}); hydration + facade logic behavioral-harness green; replica rot on
    Edit-grown files handled via patched sandbox mirrors as before. Root/facade
    additions on real classes: Not run (3.14t owner run).
  EVIDENCE:
  - src/melder/mutation_research/diff/strategies/structural_diff_strategy.py:1-1
  - src/melder/crystallizer/crystallizer.py:505-527
  IMPACT: The record now survives the full loop - declare -> emit -> die -> boot ->
    hydrate -> continue - and agents can reason about candidate futures structurally,
    not textually.
  NEXT: owner 3.14t run (diff/ + updated root file); remaining program item = the
    runtime-seam slice (select + staged/promoted acts; BLOCKED on general_0's
    _apply_notch/member-store seams landing - coordinate before starting).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T14:28:53Z
  TYPE: FACT
  CLAIM: ITERATION 4 LANDED - THE RUNTIME-SEAM SLICE (owner: iteration-3 all passed;
    "general_0 is not active, ignore general_0" = unblocked; owner also confirmed
    _apply_notch is REAL on disk - the owner-side swap landed, only cross-conduit
    fan-out remains open in that lane). (1) Vocabulary: TransitionAct gained `staged`
    (bind_inactive world entry) + `promoted` (notch selection move; journal-only).
    (2) ResearchSet seam verbs: record_world_entry (ATOMIC idempotent under the set
    lock: resident -> quiet None; fresh -> full registration with staged|registered
    act; runtime never fails on research bookkeeping) + record_promotion (journal-only
    forward event; NO organization snapshot; undeclared target -> teach-grade KeyError).
    (3) Root facades: record_world_entry -> bool; record_promotion with world-entry
    CATCH-UP (undeclared to_sha auto-declares staged first). (4) SPELLBOOK HOOKS at
    the three confirmation points, mirroring the custody emission seams: active bind
    (gated _is_dynamic_posture, independent of crystallizer recording), bind_inactive
    tail (structurally dynamic-only), _apply_notch post-lock (outgoing id -> new id;
    idempotent-notch early-return correctly skips). Liveness gates peek
    aether._mutation_research WITHOUT constructing it (bind path never births MR);
    no-op unless root exists + activated. P3 ruling (auto-default-lane, no orphan
    binds) is now LIVE wiring, not just a verb. Tests: vocab update + 2 set-level +
    2 root-level + 1 integration (dynamic bind auto-declares; real Aether).
    VERIFIED sandbox: 58/58 research_set suite (mirrors patched with identical
    deltas) + typed-harness for root facades + spellbook helpers (gate matrix:
    no-aether/no-root/live paths + catch-up ordering registered->staged->promoted).
    Spellbook/root/integration additions on real classes: Not run (3.14t owner run).
    C-docs updated (acts list + seam verbs + auto-record note in external interfaces).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3097-3140
  - src/melder/mutation_research/research_set/research_set.py:1-1
  IMPACT: The MR program is functionally COMPLETE for this story: declare (manual +
    automatic at bind/stage/notch), organize, finish, version the organization,
    persist, hydrate, and read (walk/history/heads + source/structural diffs).
  NEXT: owner 3.14t run (full tree recommended - spellbook.py was touched:
    tests/unit/melder/mutation_research + the spellbook/notch suites); then the
    twin-over handoff decision with melder_0 (recommendation in chat: melder_0
    absorbs MR as a restore-engine BUILD stage using the public seams
    load_recorded_composition + describe_mutation_research_record; MR-side work done).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (acceptance walk 2026-07-11T15:41Z: criteria
      vs reality, open directions named)
- [x] Acceptance criteria confirmed by user ("all passed, so we're good on now?" ->
      walk -> "yeah close it if we're done")
- [x] Applicable anti-pattern checks clear: no implementation from UNKNOWN; every
      transition evidence-backed; closure with acceptance + board sync.

- DATETIME: 2026-07-11T15:41:58Z
  TYPE: DECISION
  CLAIM: STORY CLOSED on owner acceptance after FIVE owner-run 3.14t green passes
    (core program, iter-2 docs/diff, iter-3 structural+docking, iter-4 seams, iter-5
    finishers + campaign_view determinism fix in the 9702-test full tree). Delivered
    beyond original scope: persistence wiring, hydration, reload handoff epic
    (executed by melder_0), runtime seams, diff family, campaign views, philosophy V3.
    Open directions live in artifacts/2026-07-11_mutation_research_philosophy_v3.md;
    the parent investigation task closes with this story.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-11_mutation_research_philosophy_v3.md:1-1
  IMPACT: The MR program of 2026-07-05 is complete and durable.
  NEXT: none (lane closed; mutation_0 departs).
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner-approved build of the MR ResearchSet core - LANDED + owner-run GREEN three times
(core program, iteration 2, iteration 3). crystal_id==spell_sha confirmed at source.
ITERATION 2: graph (520/966) + C-docs synced; diff/ slice (source strategy).
ITERATION 3: structural (AST) diff strategy + twin docking (read facade chain +
virgin-registry hydration at activation). ITERATION 4: runtime-seam slice - staged/
promoted acts + idempotent record_world_entry/record_promotion + spellbook hooks at
bind/bind_inactive/notch (general_0 inactive per owner; _apply_notch is real).
FIX (2026-07-11T15:39:33Z, from melder_0's 22:40Z NOTICE - consumed): campaign_view
node ordering was NONDETERMINISTIC (owner full-tree run, 9702 tests: nodes flipped
["sha-b","sha-a"]). Root cause: lane iteration sorted by ULID - same-millisecond
ULIDs tie-break on their RANDOM component. Fix is semantic, not cosmetic: nodes now
come back in DECLARATION ORDER (journal-driven walk over registered/staged entries;
holder resolved via residence at read time), which is deterministic by construction
and is the campaign's actual story; journaled-but-absent declarations (e.g. restored
past them) report honestly as missing_from_current_organization instead of hiding.
Verified: 60/60 suite + 200-round determinism sweep in sandbox; the exact failing
assertion now cannot flip. Also acked from the same NOTICE: engine hardening
(already-active root deactivates before stage reactivation - world-replacement
semantics, both acts recorded) is compatible with the root contract as built.
DECISION (2026-07-11T15:22:25Z, owner-routed melder_0 question): deactivate()/disabled
STAYS - shared RecordedUnitState vocabulary (Nexus parity) + the run-without-declaring
kill switch for the auto-recording seams; melder_0's activate->rebuild->deactivate
replay stands as built. Nuance on record for his disabled-lane test: a spell bound in
a pre-seal deactivated window seals undeclared but restores DECLARED (MR builds before
books; rediscovery keeps everything else duplicate-free) - accepted, arguably more
truthful, documented as expected behavior. Mailboxed as ACK 15:22:25Z.
ITERATION 5 (2026-07-11T15:22:25Z, owner "keep going"; melder_0 executed the handoff
epic same-day - S1/S2/S3 marked done, tests finishing): DIAL RULINGS + FINISHERS.
Dial 1 RESOLVED KEEP-BOUNDED: a config knob would add a required property and break
validate()/existing green tests + melder_0's landed reload backfill behavior; owner
P1 precedent ("lanes + recent logs") holds - window stays 200, full history rides the
checkpoint sequence. Dial 2 IMPLEMENTED: the undo ring (NetworkVersioner payload)
rides describe_composition ("network_versioner" additive key) and from_payload
rebuilds it - restore_network now reaches pre-death organization states after
hydration/reload. module_sha backfill REJECTED with rationale (per-bind describe()
cost buys nothing; custody carries module truth under the same id). NEW READ:
ResearchSet.campaign_view(campaign) - stamped nodes + transitions + involved lanes
gathered across the network, side-effect free. PHILOSOPHY V3 ARTIFACT authored:
artifacts/2026-07-11_mutation_research_philosophy_v3.md (canonical built-model
record; supersedes V2/May machinery, inherits their identity layer). Sandbox: 60/60
research_set suite harness-green (undo-ring roundtrip + campaign view included).
Pending 3.14t: the two new set verbs ride the existing suite paths.
58/58 prior + harnesses green in sandbox; spellbook/root/integration additions pending
owner 3.14t (run the FULL tree - spellbook.py touched). Replica-rot handled via context
mirrors throughout. TWIN-OVER HANDOFF AUTHORED (owner-directed, 2026-07-11T14:28:53Z):
tickets/epics/2026-07-11_mutation_research_restore_build_stage_epic.md for melder_0
(S1 config reload verb / S2 report->build engine stage mirroring _replay_nexus /
S3 preflight + world-scope adjudication + round trip); melder_0 mailboxed (HANDOFF).
Open owner dials recorded in the epic (journal window bound; snapshot-ring
persistence) - additive, do not gate. Possible MR-side follow-ons = the two dials,
module_sha backfill at declaration, campaign views, MR philosophy v3 artifact,
borrower fan-out recording when the cross-conduit slice lands.
