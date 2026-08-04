

# Task: Investigate MutationResearch wiring and design the git-for-spells system

## Metadata
- Task ID: TASK-2026-07-05-wire-mutation-research-git-system
- Story: seeded STORY-2026-07-11-build-mr-research-set-core (closed done) +
  EPIC-2026-07-11-mutation-research-restore-build-stage (melder_0)
- Status: done
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-05T22:17:45Z
- Updated: 2026-07-11T15:41:58Z
- Closed: 2026-07-11T15:41:58Z (exit gate satisfied and exceeded: owner picked the
  direction, the build story executed it to owner-accepted closure)

## Objective
Produce an evidence-backed wiring strategy for MutationResearch as Melder's internal
git-for-spells: what exists today in MR and the crystallizer persistence system, what the
V2 philosophies commit us to, and a concrete option map for how versions, staging,
promotion, and persistence should wire together.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-05 ("wire up mutation research ... figure out how we
  can make the git system"); board row active; onboarding certified (mutation_0).
- EXECUTION_BOUNDARY: read-only investigation across `src/melder/mutation_research/**`,
  `src/melder/crystallizer/persistence/**`, `src/melder/crystallizer/crystallizer.py`, and
  retained design artifacts. NO code edits in this task; output is strategy + options.
- DEPENDENCIES: artifacts/2026-07-01_mutation_research_philosophy_v2.md;
  artifacts/2026-07-01_crystallizer_philosophy_v2.md;
  artifacts/2026-07-03_persistence_design_detail.md;
  melder_0's epics (wire_crystallizer_into_melder Phase A, crystallizer_persistence draft).
- EXIT_GATE: strategy discussion (objective/constraints/facts/unknowns/options/tradeoffs/
  recommendation) recorded in notes and presented; owner picks a direction.
- FAILURE_ESCALATION: CONFLICT note if code contradicts the V2 philosophies;
  DECISION_REQUEST when the option choice materially shapes the runtime.

## Scope Boundaries
- In scope: MR runtime (root, Research, ResearchSpell/ResearchCreation, nodes, facades),
  crystallizer persistence (system/profile/crystal/cache/state + crystal twins incl.
  MutationResearchCrystal, SpellIndexCrystal, SpellCrystal), V2 design artifacts.
- Out of scope: implementation edits; melder_0's in-flight Phase A validation; compiler
  lanes; SpellIndex member-store seams (general_0's lane) beyond reading their contracts.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner directive is explicit approval to investigate immediately.

## Steps / Checklist
- [ ] Read the three design artifacts (intent layer).
- [ ] Read MutationResearch runtime code (current-state layer).
- [ ] Read crystallizer persistence code + MR/SpellIndex/Spell crystal twins.
- [ ] Note evidence-backed FACTs and UNKNOWNs per tranche.
- [ ] Produce STRATEGY_DISCUSSION with option map for the git system; present to owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Option map + recommendation for MR git-system wiring (in notes + owner-facing summary).
- Candidate story breakdown for the chosen direction (once owner picks).

## Files / Paths Impacted
- None (read-only task). Ticket and board rows only.

## Validation
- Not run. (No code changes in this task.)

## Risks / Rollback Notes
- Risk: design drift vs melder_0's live persistence work; mitigation: treat Phase A code as
  ground truth, philosophies as intent, and flag divergence as CONFLICT notes.
- Rollback: n/a (read-only).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none (reusing retained artifacts owned by prior lanes, read-only)
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-05T22:17:45Z
  TYPE: DECISION
  CLAIM: Investigation readset exceeds the 5-file expansion gate (~17 files across MR,
    crystallizer persistence, and design artifacts). Owner's 2026-07-05 directive
    ("go look at some of that shit ... wiring up mutation research ... make the git system")
    is taken as the explicit expansion confirmation for this bounded readset.
  EVIDENCE:
  - codex/context_compass/config/context_compass_config.yaml:95-96
  IMPACT: Legitimizes a broad read pass without a mid-pass stop; scope stays bounded to the
    two subsystems plus three retained artifacts.
  NEXT: Read the three design artifacts first (docs-before-code per context_protocol).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-05T22:50:00Z
  TYPE: FACT
  CLAIM: Current MR code is the May-model skeleton. Root is a working Aether-hosted
    singleton with config/activate lifecycle that already emits RecordedUnitState flips
    to the crystallizer; below it sit Research sessions keyed by SpellIndex.id and
    node-ledger lines (ResearchSpell/ResearchCreation) whose snapshot/apply hooks raise
    NotImplementedError. All of the below-root layer is on the V2 kill list.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:29-63
  - src/melder/mutation_research/mutation_research.py:326-350
  - src/melder/mutation_research/research/research.py:339-409
  - src/melder/mutation_research/research/spell/node/spell_mutation_node.py:163-181
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:183-189
  IMPACT: The root shell (lifecycle + session registry + crystallizer state emission) is
    reusable; everything under it gets replaced by V2 composition objects, not repaired.
  NEXT: Record the persistence-side facts, then draft the option map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T22:50:00Z
  TYPE: FACT
  CLAIM: The crystallizer persistence system is live and already carries every mechanic
    the MR git system needs to ride: profiles with replace-on-emit twin maps + a
    monotonic journal; incremental full-object checkpoints (capture_segment_since ->
    PersistenceCrystal) with FIFO retention; an atomic JSON file cache with
    flush/reload; a RecordedUnitState switch for MR; SpellIndexCrystal as the
    membership/selection map; SpellCrystal as L3 custody (bind facts + module source).
    MutationResearchCrystal is Phase-A (activation + config only) and its docstring
    explicitly marks composition fields as "the P5 seam, not a new object".
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:26-127
  - src/melder/crystallizer/persistence/persistence_profile.py:863-981
  - src/melder/crystallizer/persistence/persistence_system.py:702-773
  - src/melder/crystallizer/persistence/crystallizer_cache.py:10-38
  - src/melder/crystallizer/persistence/crystals/mutation_research_crystal.py:8-33
  - src/melder/crystallizer/persistence/crystals/spell_index_crystal.py:6-27
  IMPACT: MR composition persistence does not need new storage machinery in the first
    cut; it needs new twin payloads + emit verbs + journal kinds on the existing lane.
    The CRUD adapter contract (P1-P6) remains the separate host-owned layer underneath.
  NEXT: Surface the custody-retention tension (D4) before proposing the build order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T22:50:00Z
  TYPE: RISK
  CLAIM: Custody-retention tension: the profile is a live-world mirror - true removal
    evicts a spell's custody crystal (remove_spell_crystal), and only sealed checkpoint
    crystals retain history. Git semantics require EVERY VersionRecord to stay
    checkout-able (rematerialize source -> bind_inactive -> notch), including versions
    whose spells left the live world. Without a pinned object store, MR version history
    would dangle after removals.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:256-273
  - src/melder/crystallizer/persistence/persistence_system.py:511-555
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:114-119
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:155-159
  IMPACT: The MR composition dataset must pin crystal payloads per version (git's
    .git/objects role) rather than borrow live-profile custody; this is design decision
    D4 in the option map and shapes the twin schema.
  NEXT: Present STRATEGY_DISCUSSION to owner with the D1-D5 decision set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T22:50:00Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Option map presented to owner. Objective: MR as git porcelain (streams, version
    records, heads, query API, mutation-act orchestration) with crystallizer as object
    database + persistence. Constraints: V2 canon (MR owns no gates/persistence; melder
    mechanics bind_inactive/notch already solved), kill list applies, melder_0 owns the
    draft crystallizer_persistence epic (P1-P6 adapter contract) - coordinate before
    implementing in that seam. Decisions requested: D1 composition rebuild path
    (in-place replace vs parallel-then-swap), D2 MR dataset shape (one composite twin vs
    stream/version/head datasets), D3 first persistence lane (ride existing
    twin+journal+checkpoint machinery now, CRUD adapters layered later - recommended -
    vs adapters first), D4 version custody pinning (MR dataset pins crystal payloads -
    recommended), D5 kill-list removal timing (with S1 - recommended - vs deferred).
    Proposed build: S1 composition+query API, S2 twin/emit/journal seam, S3 hydration at
    activation, S4 mutation-act orchestration over bind_inactive/notch confirmation
    points, S5 CRUD adapters (P1-P6, with melder_0), S6 impact engine (later epic).
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:88-112
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:210-218
  - codex/context_compass/artifacts/2026-07-03_persistence_design_detail.md:30-46
  IMPACT: Owner direction on D1-D5 turns this task into a story/epic breakdown with a
    concrete first implementation slice.
  NEXT: Await owner picks on D1-D5; then draft the wiring epic + S1 story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T23:15:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Owner rejected the git framing of my first strategy pass ("this isn't git").
    The May philosophy is explicit: the git similarity ends at nodes/heads/merges. MR is
    a RESEARCH GRAPH OF CANDIDATE RUNTIME FUTURES - full-snapshot runtime/object history
    for agent-facing system evolution - asking "what system future exists now, which
    candidate should dominate, what structural parts move between futures", not "what
    source changed". V2's "internal git" line is a loose gloss on bookkeeping mechanics;
    it does not override the May identity (V2 supersedes only where CONFLICTING, and its
    own "is not" list includes "Git with different names" by inheritance).
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:29-47
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:429-453
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:11-14
  IMPACT: Strategy vocabulary and design center shift from porcelain/refs/object-db to
    lanes/candidate-futures/impact/promotion/recomposition. Substrate findings (twins,
    journal, checkpoints, custody pinning) survive unchanged.
  NEXT: Record the May-model mechanics the git frame under-weighted, then re-present.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T23:15:00Z
  TYPE: FACT
  CLAIM: May-model mechanics that must anchor the wiring design: (1) snapshot-first -
    mutation creates a real Spell with SHA immediately; promotion only decides meaning
    (lane head / dominant / pruned). (2) Lanes: many per conceptual object, ONE head per
    lane, roles dominant/experimental/merge; SpellIndex stays a runtime handle only.
    (3) Structural diff is the reasoning layer (methods/attrs/docs/comments), string
    diff only transport; SURGICAL MUTATION = agent selects structural parts from two
    nodes -> synthesizes a NEW node; merge always creates a new node with explicit
    parentage; historic-node merge allowed; rebase = recomposition on a new base.
    (4) Module integrity is the world-first problem: spell fingerprint != module truth;
    module versions get full-text SHA256; spells associate to module-version SHA, not
    canonical name; restricted vs unrestricted module-mutation postures; AST integrity
    sweep classifies blast radius (target_only/sibling_spell_impact/
    module_context_impact/mixed/unknown) and BLOCKS target-only promotion on
    sibling/unknown radius unless the agent widens the change set. (5) End-game runtime
    op: recomposition of live objects onto a chosen candidate future. (6) Multi-agent
    research campaigns are the intended scale. (7) branch_name freeform +
    optional BranchType enum (development/experiment/production/test) shared across
    spell+module mutation, stamped by grouped transactions. (8) IMPORTANT_CONSIDERATION
    keeps OPEN: meldability of non-active versions (head-only meldable is the leaning),
    linkable-but-not-meldable, research-fork vs runtime-fork (mutation_fork vs
    transfer), cross-conduit work-on semantics, world merge - do not freeze these.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:455-527
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:545-666
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:103-232
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:304-427
  - codex/context_compass/artifacts/IMPORTANT_CONSIDERATION.md:108-165
  - codex/context_compass/artifacts/IMPORTANT_CONSIDERATION.md:266-289
  - codex/context_compass/artifacts/2026-05-10_mutation_branch_type_enforcement.md:54-107
  IMPACT: The composition schema must carry lane roles, module-version SHA lineage,
    blast-radius verdicts, and branch typing from day one; the structural-diff/sweep
    engine rises in design priority because promotion POLICY depends on it.
  NEXT: Re-present the corrected strategy to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T23:45:00Z
  TYPE: FACT
  CLAIM: Full MR corpus read pass complete (newest = source of truth). Precedence stack:
    (1) V2 tool model 2026-07-01 = canon on conflict. (2) 2026-07-02 owner refinement in
    the persistence-loop artifact = freshest recorded intent: MR is a THIN API of derived
    in-memory objects OVER crystallizer custody + dependency graph, keyed by spell
    SHA256 (active/inactive, fork membership, diff, blast radius); MR re-derives
    nothing; BOTH MR and bind->crystal run ONLY in dynamic mode (Nexus+MR enabled) -
    narrowing V2 Duty 1's unconditional crystal-at-bind. (3) May philosophy where not
    conflicting = identity + depth (research graph of candidate futures; Not-Git;
    module-integrity sweep + blast-radius promotion policy; surgical mutation;
    recomposition). (4) IMPORTANT_CONSIDERATION + branch-type = governing OPEN
    questions + policy knobs. (5) March 2026 archived bundle = spirit layer:
    safe-lane/mutation-lane escalation, workspace-first lab, lifecycle states
    (proposed->...->closed), 7 control-plane gates (now REALIZED by the mediator/notch
    plane per V2 kill list - MR owns no gates), release-driven promotion, structured
    JSON payloads. Import-lifecycle addendum supplies the module-side mapping:
    content-addressed callsign store (callsign = module-version SHA; canonical alias =
    SpellIndex; alias repoint = notch; checkout = version-pin import; removal minimized
    to alias repoint + cold eviction).
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:43-91
  - codex/context_compass/artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:348-352
  - codex/context_compass/artifacts/2026-07-02_import_and_module_lifecycle_findings.md:186-208
  - codex/context_compass/artifacts/Archived/2026-03-15_aethericrift_engineer_context_bundle/MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md:138-169
  IMPACT: Two strategy corrections: (a) MR's composition is a DERIVED VIEW hydrated from
    crystallizer datasets, not an MR-owned store - persistence design centers on
    crystallizer P5 datasets + MR hydration; (b) the lane/head/merge-node graph shape is
    itself a PARKED DECISION_REQUEST (vs additive time-based union) on crystal_0's
    reframe ticket - S1 must build only the shared substrate (SHA-keyed VersionRecords
    with parentage/timestamps/index association + pinned source custody) unless the
    owner decides the graph model first.
  NEXT: Report corpus status to owner; request the merge/lane-model decision or approval
    to build the shared substrate first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-05T23:45:00Z
  TYPE: UNKNOWN
  CLAIM: Three supporting canon docs remain unread in full (their MR-relevant rules are
    quoted in the loop doc's canon map, but I have not verified them at source):
    ar_codegen_capability_surface_philosophy (residency ladder + agent acts),
    file_to_memory_bridge_mechanic (bind promotion boundary), crystallizer_configuration
    (hot-swap boundary / copy-mode policy). Archived crystallizer v1/v2/v3 also unread
    (already queued as a follow-up in crystal_0's epic).
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:289-316
  IMPACT: Low risk for the wiring strategy (rules captured secondhand in the canon map),
    but these must be read at source before implementing the codegen->materialize->bind
    seam (S4) or anything touching module publication boundaries.
  NEXT: Read them before S4 planning, or immediately if the owner wants zero gaps now.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-06T00:20:00Z
  TYPE: DECISION
  CLAIM: Owner direction (2026-07-05): (1) conduits/frames are OUT of the MR model -
    the tracking structure carries no conduit/frame dimension; (2) runtime activation
    (what a SpellIndex selects / whether a spell is active) is SEPARATE from change
    tracking - the tracking structure stores no active flags; (3) the digital-twin
    persistence system is the reference MODEL (pure-data, describe(), replace-on-emit,
    parent-edge keys) but is UNDER MIGRATION - see it, do not wire to it; (4) the
    immediate need is an initializable underlying data structure that contains/tracks
    the changes that happen BETWEEN specific versions - the foundation that makes the
    git-style system work.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/spellbook_crystal.py:8-48
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:20-99
  IMPACT: Reshapes S1 into a standalone MR substrate: per-lineage ledger (explicit init)
    holding SHA-keyed full-snapshot version entries + an ordered journal of transition
    edges (from_sha -> to_sha, act, actor, structural-delta + blast-radius slots).
    Edges-as-journal supports BOTH parked graph models (lane/head = named pointers over
    the journal; additive union = the journal itself), so the substrate does not
    pre-decide the parked merge/lane question. Twin-idiom payload seams (describe()/
    from_payload) keep it persistence-ready without touching the migrating system.
  NEXT: Present the MutationLedger/VersionEntry/TransitionEntry proposal; confirm the
    lineage keying (MR-minted lineage id with index association vs raw SpellIndex id).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T00:45:00Z
  TYPE: DECISION
  CLAIM: Owner design direction: git-FAMILIAR, not git-mechanics. Research lanes stay
    and are the branch analog - and the binding is INVERTED: the lane is the primary
    initialized container, and SPELLS ARE ADDED TO LANES ("when a user wants to
    understand a spell they made and the diffs, they add it to the research lane"),
    not lane-attached-to-spell. This replaces the per-lineage MutationLedger with a
    lane-first model: ResearchLane owns members; each membership tracks that spell's
    versions + transition journal within the lane; baseline = the spell's SHA at
    add-time. Multi-spell lanes align with the May campaign model (widening a mutation
    = adding the impacted sibling spells to the SAME lane) and V2's one-or-many index
    associations per stream. No conduits/frames; no activation state; twin-idiom
    payloads; standalone from the migrating persistence system.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:92-99
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:244-263
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:397-405
  IMPACT: Kills the global lineage-key question (the lane + membership defines tracking
    scope; durable identity is the SHA ancestry chain; index ids are only runtime-join
    associations). Remaining shape questions: per-member journal vs one lane-wide
    journal; whether one spell may be in multiple lanes concurrently.
  NEXT: Present the lane-first structure; get the journal-shape + multi-lane answers;
    then draft the build story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T01:10:00Z
  TYPE: DECISION
  CLAIM: Owner-locked mutation-act model: draw from git, do not BE git; NO
    rollback/forward verbs - the stream is forward-only and additive; history exists
    for UNDERSTANDING (diffs), not time travel. The act happens in the Nexus codegen
    room: agents tinker UNBOUND (execute_codegen builds per-call transaction context ->
    validate -> sandboxed namespace -> compile -> exec; workstation holds
    work-in-progress objects room-locally; nothing enters the world), then BIND when
    satisfied - and the bind is the moment a version becomes part of a research stream
    (lane association carried at/around the bind; `default` lane fallback). MR records
    only world-entry events (bound / staged via bind_inactive / promoted via notch /
    added-to-lane) - tinkering is already covered by room memory records and is NOT MR
    history. Returning to an old version = bind its source forward as a NEW version,
    not a rollback.
  EVIDENCE:
  - src/melder/nexus/rift/codegen_system/codegen_system.py:266-313
  - src/melder/nexus/rift/command_system/codegen_command_system.py:528-666
  - codex/context_compass/artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:115-122
  IMPACT: TransitionEntry act vocabulary shrinks to world-entry acts (no
    checkout/rollback acts); the MR record_version seam is the bind path (same
    confirmation points that emit custody twins), with the codegen-room
    materialize->bind step (crystal_0's wiring gap) as the eventual front door.
    Design is now converged enough to draft the build story.
  NEXT: Draft the build story for ResearchLane/LaneMember/VersionEntry/TransitionEntry
    + MR root verbs, pending owner green light.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T01:35:00Z
  TYPE: DECISION
  CLAIM: Owner-locked residency model completing the dev cycle: lane members span
    three residencies - ACTIVE (index-selected, live), PARKED (bind_inactive member,
    live but unselected), STORED (exists only in the crystallizer persistence layer /
    future DB behind the adapters - fetchable and loadable at any point). Rollback =
    selection change (notch to an older member, re-staged from storage when needed),
    recorded as a forward transition. Consequently VersionEntry must NOT pin full
    source payloads (MR is a thin API; custody lives with crystallizer): it carries
    SHA + module-version SHA + parents + metadata + a custody REFERENCE, and recall
    resolves through crystallizer (fetch custody -> rematerialize -> bind_inactive ->
    optional notch). Residency is a runtime+crystallizer JOIN at query time, never
    lane state. This REVISES the earlier D4 pin-payloads recommendation.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:155-168
  - codex/context_compass/artifacts/2026-07-03_persistence_design_detail.md:42-46
  - codex/context_compass/artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:82-91
  IMPACT: Lane structures stay thin and reference-based; a RETENTION CONTRACT lands on
    the crystallizer side (lane-referenced versions must remain fetchable even after
    live-world removal) - a coordination point with melder_0's migrating persistence
    lane, NOT something MR implements. RISK note: current live profile evicts custody
    on true removal; the migration/DB adapters must cover lane-referenced retention.
  NEXT: Owner green light -> draft build story for the lane structures + MR root verbs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T01:50:00Z
  TYPE: DECISION
  CLAIM: Owner refinement: lane commits have ZERO default runtime footprint. Research
    branches and their SHA256 commits do not require bind_inactive/parked residency or
    any runtime caching - the objects exist in the crystallizer persistence layer
    (db/cache/whatever) and that is enough. Runtime residency (parked or active) is an
    entirely optional, orthogonal, on-demand act ("technically we can bind it") taken
    only when someone wants a version LIVE. The SpellIndex holds what the runtime
    actually needs (the selected spell, plus a staged candidate mid-promotion at
    most); the lane holds full history as pure records. This aligns with the
    board-corrected SpellIndex model (one active spell; versions owned by MR).
  EVIDENCE:
  - codex/context_compass/attention_board.md:54-54
  IMPACT: Lane = pure bookkeeping over SHAs + custody references; no coupling between
    lane membership and index member-sets; recall = persistence fetch -> materialize
    -> bind (or stage+notch) as an explicit act recorded forward. Simplifies
    LaneMember (no parked-state tracking) and drops any index-membership maintenance
    from MR.
  NEXT: Owner go -> draft the build story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T02:05:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Pushback set raised to owner (at owner request) against the converged model:
    (P1) "it exists in the persistence layer, fetch anytime" is an IOU today - live
    profile EVICTS custody on true removal, checkpoint fetch is a ledger scan not a
    keyed lookup, DB adapters are a draft epic; proposed bridge = temporary minimal
    source pinning in lane records with explicit deprecation once adapters land.
    (P2) rollback-as-selection + forward binds creates real in-lane branching (new
    version parents onto the rolled-back node) - "what is the tip of this lane"
    becomes unanswerable without a per-member latest pointer, i.e. heads-lite sneaks
    back in and should just be accepted. (P3) manual add-to-lane only = orphan binds
    and a history with holes; proposed auto-record of every dynamic-mode bind into
    the default lane, explicit lanes as curated views. (P4) identical source rebind
    = same SHA; nodes must dedup and the journal must support transitions onto
    existing nodes. (P5) custody reference must carry spell SHA + module-version SHA
    or checkout can resurrect a spell against the wrong module world.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:256-273
  - src/melder/crystallizer/persistence/persistence_system.py:820-851
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:103-147
  IMPACT: P1 and P3 are decisions that change what gets built first; P2/P4/P5 are
    design commitments I intend to bake in unless overruled.
  NEXT: Owner rules on P1 (bridge pinning y/n) and P3 (auto-default-lane y/n).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T02:30:00Z
  TYPE: FACT
  CLAIM: Crystallizer migration CONFIRMED done on disk: crystals promoted to
    src/melder/crystallizer/crystals/ (family grew: crystallizer_crystal,
    cluster_crystal); asset_management/ hosts crystallizer_cache + NEW
    external_persistence_manager(+configuration) = the DB seam; crystal_loader_system/
    has real restore_engine/boot_mediator/load_plan/bootstrap_loader; crystal_analysis/
    grew custody + preflight strategy families. MutationResearchCrystal remains
    Phase-A shape (activated + configuration_payload) and its docstring names the
    docking contract: composition (streams/version records/heads/associations) rides
    THIS twin in Phase B - extend the twin, not a new object. Owner P1 ruling:
    migration done -> NO bridge pinning; each VersionEntry binds to a SpellCrystal
    (backend manages crystal active/inactive; user-side works with spells only); MR
    emits lanes + recent logs into the twin -> persistence layer.
  EVIDENCE:
  - src/melder/crystallizer/crystals/mutation_research_crystal.py:8-33
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1-1
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:1-1
  IMPACT: Docking design final: extend MutationResearchCrystal (Phase-B composition
    payload: lanes/members/version-entries/heads-lite + bounded recent-transition
    window), replace-on-emit through the existing sink -> journal -> checkpoints ->
    cache/DB; hydrate at MR activation. Build slices: S1 twin extension (coordinate
    w/ melder_0), S2 MR in-memory structures + root verbs + kill-list removal,
    S3 emission/hydration + dynamic-bind auto-default-lane seam, tests throughout.
    P2/P4/P5 commitments baked in; P3 default = auto-record into default lane.
    UNREAD before S3 wiring: external_persistence_manager + restore_engine internals.
  NEXT: Owner go -> draft the build story ticket and begin S2 structures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T03:00:00Z
  TYPE: DECISION
  CLAIM: Verb + model design converged through owner discussion: (1) lane = graph
    network describing ONE object's changes; lanes attach to lanes AT nodes (fork =
    attachment; the transitive network IS the object's story). (2) The graph network
    itself is version-controlled the same way (full metadata snapshots +
    repoint/restore; objects indestructible, organization versioned; repoint +
    re-attach instead of surgical undo). (3) Final verb surface: lane, track,
    attach/detach (onto= mandatory; ancestry only, never content), select (live
    pointer; matches selected_spell_id vocabulary), restore (network recovery),
    history, diff; bind stays bind. replace REJECTED (scope-blind in error messages;
    faint destruction connotation); link/unlink unavailable (conduit-contract
    collision). (4) NO merge/rebase primitives: content combination = compose in
    codegen workshop + bind with multi-parent record; attach covers the intuitive
    "move my line onto that base" organizational op; owner confirmed the click -
    commits are full objects, diffs are derived read-side features, never storage.
    OPEN (asked, not yet ruled): campaign-as-stamp-across-lanes vs multi-object lanes.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:455-471
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:545-568
  - codex/context_compass/artifacts/2026-07-01_mutation_research_philosophy_v2.md:170-179
  IMPACT: Design discussion is functionally complete; remaining owner ruling =
    campaign representation; then the converged model should be written up as a design
    artifact + build story (twin extension w/ melder_0 coordination, MR structures,
    emission/hydration).
  NEXT: Confirm campaign ruling; propose writing the design spec artifact + story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T03:40:00Z
  TYPE: DECISION
  CLAIM: Owner rulings this pass: (1) join semantics accepted - a joined lane is
    archived/closed, no further work from that container (objects remain; new lanes
    may attach at any node). (2) The existing MR placeholders (Research/ResearchSpell/
    nodes/MutationConduit/MutationFrame) confirmed senseless for this model -
    kill-list teardown proceeds. (3) NEW HARD INVARIANT - SINGLE RESIDENCE: a spell
    identity (binding-signature SHA256) may reside in exactly ONE lane across the
    entire graph network, never duplicated. Supersedes my earlier multi-lane
    membership position. Verb family also grew: join (divergence-aware finisher:
    fast-forward-analog auto; divergent requires reconcile-compose or explicit
    supersede) and archive (dead-end lanes leave current view, restorable); deletion
    exists only as persistence-layer admin redaction (dangling refs marked).
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:627-647
  IMPACT: MR needs a global residence registry (spell_sha -> lane_id) enforcing the
    partition; membership vs anchoring must be distinct (a child lane anchors AT a
    parent's node without owning it; lanes own only their novel SHAs) - this is what
    keeps parallel research legal under single residence. Identical-content rebind =
    residence collision surfaced as rediscovery (points at the existing lane).
    OPEN: does residence persist through archive (recommend yes - permanent identity
    residence; rediscovery points to archived lane) + the campaign-stamp ruling.
  NEXT: Present residence/overlay model; get archive-residence + campaign rulings;
    then write the design spec.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-06T04:15:00Z
  TYPE: PLAN
  CLAIM: Owner closed discussion -> build mode. Confirmed: MR package (2,910 LOC) is
    the May skeleton and represents nothing from the converged model. KEEP: root
    singleton (lifecycle/crystallizer docking/RecordedUnitState emissions) +
    configuration(+builder). KILL: research/* (Research/ResearchSpell/
    ResearchCreation/both nodes), mutation_conduit.py, mutation_frame.py; deprecate
    Conduit.get_mutation_research (conduit door out of model - public API flag).
    NEW owner object: ResearchSet = overarching container retaining all lanes;
    register_spell into it; walk graph; diffs. MR depends on crystallizer (objects
    represented in its persistence layer by default). SOLID architecture proposed:
    research_set/ package - ResearchSet (facade/orchestrator), ResearchLane,
    ResearchNode (pure-data), TransitionEntry, ResearchJournal (set-level monotonic
    log), ResidenceRegistry (partition invariant), NetworkVersioner (org snapshots +
    restore), diff/ strategy family (OCP, house strategy-builder idiom). Root keeps
    lifecycle + set registry (default set, profiles idiom) + emission seam (DIP: set
    emits detached payloads; only root touches crystallizer). Build slices: S1
    teardown+scaffold, S2 core structures+verbs+unit tests, S3 network versioning +
    join/archive, S4 crystallizer docking (twin Phase-B ext; mailbox melder_0 first)
    + hydration, S5 diff/walk reads. Defaults baked unless overruled: campaign stamp
    on TransitionEntry; residence permanent through archive.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:29-63
  - src/melder/aether/conduit/conduit.py:2948-2987
  IMPACT: Architecture awaiting owner ack; then convert lane to build story ticket and
    begin S1/S2.
  NEXT: Owner ack on architecture -> draft build story ticket -> S1 teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T15:41:58Z
  TYPE: DECISION
  CLAIM: TASK CLOSED with its build story. The design converged in these notes was
    built, validated (five owner-run 3.14t green passes), persisted, made reloadable
    (melder_0's executed epic), and recorded durably in
    artifacts/2026-07-11_mutation_research_philosophy_v3.md - the successor to every
    design decision this investigation captured.
  EVIDENCE:
  - codex/context_compass/tickets/stories/2026-07-11_build_mr_research_set_core_story.md:1-1
  IMPACT: The 2026-07-05 directive ("figure out how we can make the git system") is
    answered by a shipped system that is deliberately not git.
  NEXT: none (closed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner redirected mutation_0 from the parked doc-tail repair task (now in
tickets/tasks/backlog/) to MR wiring discovery. Full MR corpus read 2026-07-05
(March bundle -> May set -> V2 canon -> 2026-07-02/03 freshest layer). Corrected model:
MR = thin derived API over crystallizer custody+graph (dynamic-mode only), research
graph of candidate runtime futures, NOT git; promotion policy hangs on the
module-integrity/blast-radius engine; callsign version store maps module versions onto
SpellIndex/notch. Lane/head vs additive-union graph model is a PARKED owner decision
that now gates S1's shape. Three supporting docs (AR codegen surface, file bridge,
crystallizer config) still unread at source - required before S4. Awaiting owner:
graph-model decision or approval to build the shared substrate first.
