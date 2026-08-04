# Epic: MR GroupNodes - subsystem compositions as first-class nodes

## Metadata
- Epic ID: EPIC-2026-07-11-mr-group-nodes
- Status: done (S1-S7 owner-run 3.14t green; closed 2026-07-11T23:20:16Z)
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T23:00:00Z
- Updated: 2026-07-11T23:00:00Z

## Objective
Owner-ruled model (2026-07-11, supersedes the groups-as-views draft; final
naming ruling same day: "make a GroupedResearchNode, and then extend
everything... make a new strategy system for it if you have one for the
normal one... its ok if theres some code duplication just remember we
want both options"): GroupedResearchNode is its OWN immutable node class
carrying a pinned list of member spell_ids; identity = content-addressed
sha256 over the canonical sorted member list; PURELY INFORMATIONAL (no
custody crystal, no gating, no execution). ResearchNode is untouched byte
for byte; duplication between the two node families is accepted - both
options stay first-class. A lane of group nodes is a subsystem's
timeline; the carrying code (lanes, payload tags, hydration, twin) is
EXTENDED to hold the new type; grouped behavior gets a MIRRORED strategy
system (GroupDiffEngine + GroupDiffStrategy family beside
DiffEngine + DiffStrategy).
Agents iterate: register spells, keep adding them into the composition -
each add mints a NEW group node with parents=[previous]. All existing
semantics (walk/history/heads/join/archive/journal/campaigns/twin/
snapshots/restore) apply UNCHANGED; grouped behavior arrives as STRATEGY
DISPATCH (a `members` diff strategy; impact/source/custody reads that
dispatch on node kind). Ruled frame:
artifacts/2026-07-11_mr_units_and_scales_philosophy.md sections 5-7.

## Stories (staged; each closes on its own terms)
- S1 RECORD CORE: NEW GroupedResearchNode class (own file:
  grouped_research_node.py; immutable value object, Cleanable; group_id
  content-addressed over deduped sorted members; member_spell_ids,
  parent_group_ids, author/campaign/reason/metadata/created_at;
  describe()/from_payload() exact inverses with node_type="group" tag +
  recorded-id integrity check). ResearchNode UNTOUCHED. Carrying code
  EXTENDED: lane identity helper + add/describe/from_payload dispatch on
  the node_type tag (untagged payloads = spell nodes, back-compat);
  TransitionAct gains group_registered / group_recomposed (group-scope
  acts carry the composition sha in to_spell_id - same sha namespace -
  roster in metadata); ResearchSet register_group / recompose_group verbs
  (members validated for residence like parents; recompose = new
  GroupedResearchNode, parent_group_ids=[previous]; identical roster =
  same sha = rediscovery, teach-grade); residency/history reads answer
  node type honestly.
- S2 MIRRORED GROUP STRATEGY SYSTEM + READS: GroupDiffEngine +
  GroupDiffStrategy family beside DiffEngine + DiffStrategy (duplication
  accepted by ruling; both options first-class): composition-vs-
  composition strategies (member roster diff; version-moved members
  descending into the existing source/structural/parts grains via the
  normal engine); root composition reads - roster view, composition
  drift (pinned vs member-lane tips), union impact w/ direction split +
  closure + adjacency; custody probe answers "informational identity, no
  crystal expected" instead of a miss.
- S3 TWIN + BOOTLOADER EXTENSION: composition twin round-trip with group
  nodes (rides lane payloads - PROVE it, don't assume it); hydration
  (load_recorded_composition / ResearchSet.from_payload), network
  snapshots/restore; EXTEND the validators - crystallizer-side
  MRCompositionStrategy preflight and the restore-engine MR adjudication
  must learn group identities carry NO custody expectation (members
  validated for residence instead). Cross-boundary: touches
  crystallizer/crystal_analysis/preflight + restore_engine - coordinate
  with melder_0's board rows before editing.
- S4 NEXUS/ROOM SURFACE: research_group_compose / research_group_recompose
  (codegen rooms; organization verbs) + composition reads
  (roster/drift/impact/closure/adjacency - both rooms); presentation
  tuples + inventory tests; viewer annotation if a spell is pinned by
  compositions (reverse lift).
- S5 DOCS/GRAPH/CLOSURE: C-docs, graph nodes/edges, philosophy artifact
  cross-check, full test sweep, owner-run 3.14t.

## Ticket Contract
- ENTRY_GATE: owner ruling 2026-07-11 ("if you like this go ahead...
  remember we gotta twin it and fix the bootloader by extending it...
  even updating the nexus... make an epic too").
- EXECUTION_BOUNDARY: mutation_research/** + both command systems +
  (S3 only) crystallizer preflight/restore-engine MR adjudication seams +
  matching tests. NO execute/bind paths; group nodes never gate.
- DEPENDENCIES: shipped grain-choice diff family (source/structural/
  parts); multi-parent nodes; content-addressing precedent
  (NetworkVersioner); melder_0's restore/build-stage lanes (S3 touches
  their seams - mailbox before edit).
- EXIT_GATE: per-story harness green + owner-run 3.14t; S3 proves an old
  (pre-GroupNode) twin hydrates AND a GroupNode twin survives
  seal->restore; boards/docs/graph synced.
- FAILURE_ESCALATION: DECISION_REQUEST on any identity-collision edge
  (two compositions with identical member sets ARE the same identity -
  confirm rediscovery semantics with owner if it surprises); CONFLICT if
  S3 collides with melder_0's active mesh/CRUD lane.

## Notes
- DATETIME: 2026-07-11T23:00:00Z
  TYPE: PLAN
  CLAIM: Design locked by owner ruling; philosophy artifact sections 5-7
    redrafted to the GroupNode model (ladder now self-similar: group
    version = content-addressed composition snapshot; subsystem = lane of
    group nodes). Key implementation facts already verified in prior
    lanes: ResearchNode.parent_spell_ids exists (multi-parent machinery);
    register_spell/record_world_entry validate resident parents;
    NetworkVersioner content-addresses via canonical JSON sha (identity
    precedent); lane payloads round-trip through twin/snapshots/restore/
    hydration (groups ride free ONCE node payload extension is additive);
    MRCompositionStrategy preflight walks lane nodes' spell_id ->
    residence (S3 must teach it group kind); staged-ancestry seam exists
    for the compose-after-bind flow. Identity nuance to surface early:
    content-addressing means recomposing the SAME member set = SAME sha =
    rediscovery (single residence refuses a second registration) - likely
    correct semantics (identical composition IS the same fact), flagged
    for owner if it bites.
  EVIDENCE: artifacts/2026-07-11_mr_units_and_scales_philosophy.md:189-260
  IMPACT: Subsystem tracking lands on existing machinery; the only new
    surfaces are the composition carrier, one diff strategy, kind-aware
    reads, and validator extensions.
  NEXT: S1 record core.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:40:00Z
  TYPE: IMPLEMENTATION (S1 record core COMPLETE)
  CLAIM: GroupedResearchNode shipped as its OWN class
    (research_set/grouped_research_node.py): content-addressed group_id
    (sha256 over deduped sorted members; SANDBOX-VERIFIED live:
    order-independence, dedupe, 64-hex, round-trip, untagged refusal,
    tamper refusal, cleanup guard), member_spell_ids canonical tuple,
    parent_group_ids (composition ancestry, own namespace),
    describe()/from_payload() exact inverses w/ node_type="group" tag +
    recorded-id integrity check. ResearchNode UNTOUCHED. CARRYING CODE
    EXTENDED: research_lane.py gains module-level node_identity() (single
    dispatch point, TypeError names both families); add_node accepts both
    families (dedup spans both; tip advances across families);
    from_payload dispatches on the tag (untagged = spell node,
    back-compat); set.join's re-add compensation uses node_identity.
    JOURNAL: TransitionActs group_registered / group_recomposed (group-
    scope acts carry the composition sha in to_spell_id - documented in
    the act contract; roster + ancestry in metadata; recompose also sets
    from_spell_id=previous). SET VERBS: register_group (members must be
    resident - same law as parents; residence claim w/ rollback
    compensation; identical roster = rediscovery via the existing
    residence signal) + recompose_group (the owner's iterate-and-add
    loop: reads previous roster, applies add/remove, registers into the
    SAME lane w/ parents=[previous]; refuses no-op rosters teach-grade
    [content-addressing], unknown removals, spell-node targets, empty
    results). TESTS (6, tests/unit/.../research_set/
    test_grouped_research_node.py): identity law, payload round-trip +
    integrity, heterogeneous lane + dispatch round-trip, register laws +
    journal, recompose flow + all refusal arms, and the EARLY persistence
    proof (describe_composition->from_payload hydration + snapshot/
    restore both rebuild compositions with members/ancestry/type intact -
    S3 still proves the crystallizer-side loop + validators). Set-level
    audit: zero remaining node.spell_id direct uses (walk/history/
    campaign_view flow through describe()/get_node - both families).
  EVIDENCE:
  - src/melder/mutation_research/research_set/grouped_research_node.py (new)
  - src/melder/mutation_research/research_set/research_lane.py (node_identity + dispatch)
  - src/melder/mutation_research/research_set/research_set.py (register_group/recompose_group)
  - src/melder/mutation_research/research_set/transition_entry.py (+2 acts)
  IMPACT: Subsystem compositions are recordable, evolvable, journaled,
    snapshotted, and hydratable at set level.
  NEXT: S2 - mirrored GroupDiffEngine/GroupDiffStrategy family + root
    composition reads (roster/drift/union impact/closure/adjacency,
    kind-aware custody probe).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:15:00Z
  TYPE: IMPLEMENTATION (S2 mirrored strategy system + composition reads COMPLETE)
  CLAIM: The grouped strategy family exists BESIDE the normal one (owner
    ruling; duplication accepted): NEW package group_diff/ -
    GroupDiffStrategy (base contract over composition materials),
    GroupDiffEngine (resolver-injected, registry-dispatched, open/closed,
    mirrors DiffEngine verb for verb), MemberDiffStrategy ("members",
    default): added/removed/unchanged members + LANE-EVIDENCED
    version_moved pairing (a removed and an added identity sharing a lane
    = one object whose version moved; identities without residence truth
    report as plain rows - never guessed) + ancestry_related.
    SANDBOX-VERIFIED live (pairing, honest unpaired rows, ancestry,
    identical, teach-grade unknown strategy). ROOT READS:
    group_diff_research (lazily-owned engine over _resolve_group_material
    - roster + per-member lane join), group_view (roster + residence +
    DRIFT: behind flag per member where the pinned version's lane tip
    moved + behind_count), group_impact_view (member radii unioned via
    custody, internal/outbound direction split, CLOSURE fraction,
    affected_compositions adjacency lift over other lanes' tip
    compositions, residency join, per_member detail), _locate_group_node
    (teach-grade: unknown vs spell-version refusals). residency_view is
    now KIND-AWARE: node_type spell|group; composition identities answer
    runtime="informational" with NO custody/frame probes (in_custody
    None) - a probe would report a misleading miss. Root owns
    _group_diff_engine (slot/init/cleanup cascade). TESTS: NEW
    group_diff/test_group_diff_engine.py (3: defaults+dispatch+refusals,
    lane-evidenced pairing, open/closed registration) + NEW
    test_mutation_research_compositions.py (4: roster+drift, grouped diff
    end-to-end w/ recompose pairing, impact union/closure/adjacency over
    mocked custody, kind-aware residency).
  EVIDENCE:
  - src/melder/mutation_research/group_diff/ (new package, 3 files)
  - src/melder/mutation_research/mutation_research.py (composition reads + kind-aware residency)
  - tests as named
  IMPACT: Agents can diff subsystems at member grain with version moves
    paired, see composition drift, and measure workspace safety (closure)
    + coupling (adjacency) - all read-only.
  NEXT: S3 twin + bootloader validators (mailbox melder_0 FIRST - his
    asset_crud lane is in review on the same crystallizer seams), then S4
    rooms.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:40:00Z
  TYPE: FIX
  CLAIM: First owner-run on S1/S2: 3 --last-failed, 2 mine + 1 foreign.
    MINE: (1) restore-loop test held in-hand node references across
    restore_network - restore rebuilds containers wholesale and CLEANS
    old nodes (existing, correct law; ResearchNodes behave identically),
    so the test now captures identity strings before restore (identities
    are the durable handles; LESSON echoed in a test comment). (2) The
    act-vocabulary exact-set test predates the two grouped acts - updated
    with the intent preserved (grouped acts are forward-only world
    entries, not rewinds; docstring says so). FOREIGN:
    test_lineage_remediation_notch_race post-settle meld of member B
    refuses with SpellbookValidationError (conduit resolution phases
    unresolved after the remediation-vs-notch window settles) - aether/
    conduit meld/notch territory, ZERO MR involvement (MR changes are
    read-only/additive; the seams this test exercises never touch
    mutation_research). Flagged to owner as a possible REAL race finding
    (the post-settle-staleness class the probe hunts, manifesting as
    refusal rather than staleness); no active agent owns that lane
    (mediator_builder_0 departed) - owner routes.
  EVIDENCE:
  - tests/unit/melder/mutation_research/research_set/test_grouped_research_node.py
  - tests/unit/melder/mutation_research/research_set/test_transition_entry.py
  IMPACT: MR surface re-run-ready; the race probe persists in
    --last-failed until routed.
  NEXT: owner re-run; then S3.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T01:10:00Z
  TYPE: IMPLEMENTATION (S3 twin + bootloader validators COMPLETE)
  CLAIM: Coordination first: mailbox NOTICE to melder_0 + alert line
    (his asset_crud lane is in review on adjacent crystallizer surfaces;
    my edits are MR-payload-scoped only). FINDING that shrank S3: the
    restore engine does NOT reason node-id -> custody for MR - it hands
    composition_payload WHOLESALE to load_recorded_composition
    (restore_engine.py:963-967), so group nodes ride the S1 lane
    dispatch with ZERO restore-engine edits (the epic's hypothesis is
    retired with evidence). The ONE validator needing extension was the
    preflight: MRCompositionStrategy's lane-node walk read
    node["spell_id"] unconditionally - every GroupedResearchNode payload
    would have false-warned as "lane-held spell id None". EXTENDED:
    node_type="group" dispatch (identity under group_id; claims residence
    agreement like any node; documented as informational/no-custody) +
    NEW member-residence check (a composition pinning a member absent
    from the residence partition warns as drift evidence, never blocks -
    the composition itself rebuilds fine). TESTS: preflight suite +2
    (clean group payload = zero rows incl. no false None-warnings;
    missing pinned member = exactly one warning naming composition +
    member); compositions suite +1 bootloader-seam proof (recorded
    composition w/ two generations of group nodes -> fresh root ->
    load_recorded_composition [the exact lane the restore engine drives]
    -> group_view/group_diff_research/residency_view all live over the
    hydrated registry; members/ancestry/type intact). PROOF CHAIN now:
    twin payload shape (S1 set-level round-trip) -> preflight accepts +
    validates (S3) -> wholesale hydration rebuilds (S3) -> full
    seal->restore rides existing owner-run restore integration paths
    unchanged.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py (dispatch + member check)
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:955-978 (read-only verification, no edit needed)
  - tests/unit/melder/crystallizer/crystal_analysis/test_mutation_research_composition_strategy.py (+2)
  - tests/unit/melder/mutation_research/test_mutation_research_compositions.py (+1)
  IMPACT: Compositions twin, preflight, and bootstrap on the proven loop;
    the only crystallizer-side edit is 30 lines in one preflight strategy.
  NEXT: S4 nexus/room surface (research_group_* commands, tuples,
    inventory tests), then S5 docs/graph/closure.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:45:00Z
  TYPE: IMPLEMENTATION (S4 nexus rooms + S5 docs/graph COMPLETE)
  CLAIM: S4: five composition commands on the codegen room
    (research_group_register/recompose = organization, codegen-only per
    the exposure law; research_group_view/diff/impact = reads) + the
    three reads on capability rooms; tuples now codegen 30 / capability
    17, ADVERTISED; inventory equality test extended to the 50-name
    tuple; split-law test: reads +3, codegen-only +2; NEW
    test_codegen_room_composition_loop (real room: register -> recompose
    [ancestry verified] -> view [honest behind drift on the shared
    default lane] -> members diff [added + ancestry_related] -> union
    impact [closure 1.0 over the fake radius] -> kind-aware residency).
    S5: both C-docs synced (rooms 30/17 + composition bullets; ResearchSet
    package gains the full GroupedResearchNode contract bullet; the
    architecture doc's stale 21-command line caught and corrected to
    30/17); both graphs 531/995 -> 535/1002 (4 nodes: GroupedResearchNode,
    GroupDiffEngine, GroupDiffStrategy, MemberDiffStrategy; 7 edges:
    lane owns / set creates the node family, root owns+creates the
    engine, engine owns+creates the members strategy, strategy
    specializes the base; MR responsibilities + both borrows whys
    refreshed; baseline asserted before edit; file-tool-verified 13 hits
    per graph). melder_0's mailbox reply confirmed no seam conflict
    (restore-engine adjudication reasons scope-verdicts, not
    node-id->custody - independent corroboration of the S3 finding).
  EVIDENCE:
  - src/melder/nexus/rift/command_system/{codegen,capability}_command_system.py
  - tests/integration/melder/mutation_research/test_research_room_commands_integration.py
  - system_docs (both C-docs + both graphs 535/1002)
  IMPACT: The full GroupedResearchNode program is CODE-COMPLETE across
    all five stories: record core, mirrored strategy system, twin +
    preflight, room surface, docs/graph.
  NEXT: owner-run 3.14t over the MR trees + crystal_analysis preflight
    suite + test_nexus inventory + room integration; epic closes on
    green.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T02:20:00Z
  TYPE: IMPLEMENTATION (S6 - the remaining philosophy reads, owner
    "iterate more")
  CLAIM: The units-and-scales section 5.2/5.3 promises that had not yet
    landed under the GroupNode model are now BUILT: (1)
    group_footprint_view - the physical shadow: union of pinned members'
    module worlds derived at read time (never stored), per-module member
    map exposing SHARED matter (the subsystem's internal coupling),
    custody-less members honest; (2) group_drift_view - the full custody
    drift report NARROWED to the footprint with counts recomputed over
    the subsystem ("what is already broken in THIS area"); (3)
    set-level group_history + root group_history_view - the temporal
    read: journal events touching the subsystem lane, any pinned member,
    or any member's lane, in journal order with campaign stamps; (4)
    compositions_of - the REVERSE LIFT (which current lane-tip
    compositions pin a spell), surfaced on EVERY spell's residency_view
    as pinned_by_compositions; group_impact_view's adjacency scan
    refactored onto the shared _current_compositions helper. ROOMS: +3
    reads both systems (research_group_footprint/drift/history); tuples
    codegen 33 / capability 20, ADVERTISED; inventory + split tests
    extended. TESTS +4: footprint/drift narrowing over mocked custody
    (shared modules, honest ghosts, recomputed counts), area story over
    the real journal (composition acts + member world entries + 3
    watched lanes), reverse lift + residency surfacing, room loop
    extended (footprint/drift/history/pinned_by through real rooms).
    DOCS/GRAPH: counts + verb lists synced; graphs stay 535/1002
    (responsibilities + whys refreshed, no new nodes - these are reads
    on existing classes).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py (+5 verbs + reverse lift)
  - src/melder/mutation_research/research_set/research_set.py (group_history)
  - both command systems + tests as named
  IMPACT: The full agent session from philosophy section 8 is now
    executable verb for verb: pick an area, check its safety (closure),
    its coupling (footprint/adjacency), its story (history), its rot
    (drift), and see every spell's subsystem membership from residency.
  NEXT: owner-run 3.14t; epic closes on green.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T02:35:00Z
  TYPE: IMPLEMENTATION (S6 coda - the last philosophy promise)
  CLAIM: impact_view itself now LIFTS to composition grain: every
    ordinary spell/module radius carries `affected_compositions`
    (current lane-tip subsystems whose rosters intersect the affected
    spells, shared members listed) - the units-and-scales crossing-move
    promise ("any spell's impact_view can now name which GROUPS its
    radius touches") executed verbatim. FREE RIDERS: research_impact,
    research_part_diff's radius section, and preview_candidate's impact
    all lift automatically (they route through impact_view) - "every
    change it mocks reports impact lifted to composition grain" (section
    8) is now literally true. +1 unit test (module-centered radius names
    the pinning subsystem with shared members); C-doc impact bullet
    updated; additive key, zero existing-assert breakage (verified
    against every impact-asserting test).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py (impact_view lift)
  - tests/unit/melder/mutation_research/test_mutation_research_compositions.py
  IMPACT: The ladder is closed end to end - part -> version -> object ->
    composition, with the crossing move lifting to the top rung from any
    center.
  NEXT: owner-run 3.14t; epic closes on green.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T03:00:00Z
  TYPE: IMPLEMENTATION (S7 - the three small closes, owner "continue")
  CLAIM: (1) WHERE x WHEN join: group_history / group_history_view /
    research_group_history gain campaign= narrowing (one effort's story
    inside one area; payload carries the filter honestly) - groups are
    structure, campaigns are intent, the record now joins them on
    demand. (2) PART FINGERPRINTS (units-and-scales open direction,
    depth-3 sharpening executed): list_parts rows carry sha256 over the
    exact part text - two versions' inventories (research_parts) compare
    part-by-part WITHOUT pulling texts; custody-true (pure parsing +
    hashing), never sold as impact. (3) research_recent (both rooms,
    tuples 34/21): the cold-landing read - newest journal window in one
    call for an agent choosing where to work. TESTS +4 (campaign-narrowed
    area story; recent window bounds + ordering + honesty; part-sha
    stability/distinctness; room-loop recent). Docs + graph whys synced
    (graphs hold 535/1002; responsibilities extended).
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py (campaign filter)
  - src/melder/mutation_research/mutation_research.py (recent_activity_view + passthrough)
  - src/melder/mutation_research/synthesis/structural_synthesizer.py (part shas)
  - both command systems + tests as named
  IMPACT: Agents can land cold (recent), scope an effort inside an area
    (campaign x group), and detect part-level change from fingerprints
    alone.
  NEXT: owner-run 3.14t; epic closes on green. Remaining owner decisions
    parked: runtime recomposition A/B/C (salvage ticket).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:20:16Z
  TYPE: STATE_TRANSITION
  CLAIM: in_progress -> DONE (owner-run 3.14t green across the full
    program; owner confirmation "yeah they all passed"). EXIT_GATE
    satisfied: every story green (S1 record core, S2 mirrored strategy
    family + composition reads, S3 twin + preflight validator [restore
    engine proven no-edit-needed, melder_0-corroborated], S4 room
    surface, S5 docs/graph, S6 philosophy reads [footprint/drift/
    history/reverse lift + the impact composition lift], S7 closes
    [campaign x group join, part fingerprints, research_recent]);
    old-twin back-compat proven (untagged payloads hydrate as spell
    nodes; pre-vocabulary lane payloads hydrate typed); GroupNode twin
    survives describe->hydrate AND snapshot->restore; the
    identity-collision nuance (identical roster = same sha =
    rediscovery) is documented in verb contracts and teach-grade errors.
    FINAL SURFACE: rooms advertise codegen 34 / capability 21; graphs
    535/1002; the philosophy section-8 agent session executes verb for
    verb. ~30 new tests across the program, all owner-run green.
  EVIDENCE: owner confirmations 2026-07-11; the seven IMPLEMENTATION
    notes above; artifacts/2026-07-11_mr_units_and_scales_philosophy.md
    (registered on artifact_board as canonical alongside V3).
  IMPACT: The MR record now speaks every rung the owner asked for -
    parts, versions, objects, subsystems - with mirrored machinery and
    zero changes to the base unit.
  NEXT: none. Open directions live in the philosophy (nesting,
    cluster-derived suggestions); the one parked owner decision is
    runtime recomposition (salvage ticket 19:58 DECISION_REQUEST).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:45:00Z
  TYPE: IMPLEMENTATION (post-closure addendum - owner challenge honored)
  CLAIM: Owner challenged "the bootstrap and the twin and all that stuff
    is done?" - the honest audit found one hop riding BY CONSTRUCTION
    rather than by proof: twin EMISSION + rebirth through a REAL
    crystallizer (all prior proofs used mocked custody or called the
    hydration verb directly; the JSON-contract test's MR crystal carried
    empty lanes). CLOSED with
    test_mutation_research_composition_twin_survives_the_real_record
    (crystallizer lifecycle integration file, real activated
    crystallizer, zero mocks): register_group -> the LIVE persistence
    record carries the tagged group node (JSON round-trip asserted on
    the recorded composition) -> root cleanup + singleton reset ->
    REBORN root's activate() pulls the record through the
    virgin-hydration lane -> group_view / residency_view (kind-aware,
    typed lane) / group_history all answer over the rebuilt registry.
    Note: rebirth proceeds past the recorded "cleaned" state by design
    (hydration reads composition, not state - the state records history,
    the composition records truth).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_lifecycle_integration.py (new test)
  IMPACT: Every hop of twin + bootstrap is now PROVEN, none inferred.
  NEXT: owner-run 3.14t on the lifecycle integration file (the ONE
    not-yet-run test in the program).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:55:00Z
  TYPE: FACT (owner challenged the melder_0 corroboration - source-proven
    audit replaces it)
  CLAIM: The "restore engine needs no edit" claim now rests on LINE-LEVEL
    SOURCE EVIDENCE, independent of melder_0's pre-compaction note.
    Exhaustive consumer sweep of composition_payload across
    src/melder/crystallizer/**: exactly THREE consumers exist. (1)
    MutationResearchCrystal - opaque dict copy in, dict copy out
    (crystals/mutation_research_crystal.py:73-74,141; never walks nodes);
    (2) restore engine - wholesale handoff
    root.load_recorded_composition(composition_payload)
    (restore_engine.py:963-967; never walks nodes); (3)
    MRCompositionStrategy preflight - the ONLY node-walker in the entire
    package (grep '"lanes"' across crystallizer = ONE hit,
    mutation_research_composition_strategy.py:119) - and that is the
    exact strategy this epic extended and tested. ALSO AUDITED:
    LoadAdmission's expected_for_scope adjudication
    (load_admission.py:512-549) reasons over finding ROWS by strategy
    NAME (reclassifies mutation_research_composition warnings on
    non-world scopes) - it never inspects node payloads, so the new
    pinned-member drift warnings flow through it correctly by row-shape
    construction: counted on world loads, expected-for-scope on
    formation loads. Runtime proof on top: the zero-mock lifecycle test
    (emission -> real record -> rebirth). melder_0's note (02:20Z,
    written pre-compaction while he held context) is now merely
    consistent with the evidence rather than part of it.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:963-967
  - src/melder/crystallizer/crystals/mutation_research_crystal.py:73-141
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py:119
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:512-549
  IMPACT: No hidden consumer can choke on group payloads; the claim is
    closed by enumeration, not sampling.
  NEXT: owner runs the lifecycle integration file (the one un-run test).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:05:00Z
  TYPE: FACT (final gate closed)
  CLAIM: Owner ran the full tree including the zero-mock lifecycle test:
    ALL GREEN ("I did run all the tests they seem to work now"). Nothing
    in the GroupedResearchNode program rides on inference anymore - the
    twin emission, the real persistence record, root death, and
    virgin-hydration rebirth are all runtime-proven on 3.14t, and the
    crystallizer-side consumer set is closed by enumeration. The epic's
    every gate is satisfied twice over.
  EVIDENCE: owner confirmation 2026-07-12.
  IMPACT: Program complete and verified; no open threads in this epic.
  NEXT: none.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:30:00Z
  TYPE: IMPLEMENTATION (S8 - parity audit, owner: "I want the same
    features we have for normal nodes for grouped nodes")
  CLAIM: Full node-parity audit run. ALREADY-PARITY (verified): walk,
    history, heads, residency, lane organization (attach/detach/join/
    archive), campaign_view transitions, snapshots, restore, twin,
    bootstrap, diff (mirrored members engine); N/A BY DESIGN: auto-record
    at bind (compositions are deliberate acts), source/preview/synthesis
    (a composition has no code of its own - members do; reads fan out);
    runtime recomposition is NOT a parity item (neither node family has
    it - it is the parked live-object feature). THREE REAL GAPS FOUND AND
    FIXED: (1) AMBIENT CAMPAIGN STAMP - room-registered compositions
    skipped the active-campaign stamp that runtime auto-records get; NEW
    root facades register_group/recompose_group apply effective_campaign
    (explicit wins) and both room commands reroute through them. (2)
    TEACH-GRADE GRAIN REFUSALS - spell-grain custody reads pointed at a
    composition id raised a raw custody KeyError ("no crystal") when the
    truth is "wrong grain"; NEW _get_spell_crystal_for_read wrapper (7
    call sites swapped: source/module/part/parts/module_graph views,
    diff material, preview-against) detects the resident composition on
    the KeyError path (zero happy-path cost) and redirects to the
    composition reads by name; unknown ids keep the honest KeyError. (3)
    CAMPAIGN_VIEW NODES - group acts' transitions were gathered but their
    NODE payloads were excluded by the pre-group act filter; filter now
    includes group_registered/group_recomposed so stamped compositions
    appear beside stamped spells. TESTS +2 (ambient stamp incl.
    explicit-wins + campaign_view gathering; teach-grade refusal matrix
    incl. honest-KeyError arm).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py (facades + wrapper)
  - src/melder/mutation_research/research_set/research_set.py (campaign_view filter)
  - src/melder/nexus/rift/command_system/codegen_command_system.py (reroute)
  - tests/unit/melder/mutation_research/test_mutation_research_compositions.py (+2)
  IMPACT: Feature parity between the node families is now closed by
    audit, not assumption.
  NEXT: owner-run 3.14t (MR unit trees + room integration).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:00:00Z
  TYPE: IMPLEMENTATION (S9 - POLYMORPHIC VERBS; owner correction: "just
    implement the group nodes properly", stop redirecting)
  CLAIM: The S8 teach-refusals were the WRONG posture for reads - the
    owner wants ONE vocabulary, not redirects. The ordinary spell-grain
    verbs now DISPATCH on node kind and serve both families: source_view/
    parts_view/module_graph_view/module_view FAN OUT per member
    ({"node_type":"group","group_id","member_count","members":{member:
    payload}}; custody-less members honest); part_view searches the
    roster first-hit and NAMES the carrying member; impact_view
    (spell_id=composition) answers the group radius; diff_research on two
    compositions routes through the members engine (mixed pair refuses
    teach-grade - no shared grain); part_diff sides accept composition
    ids (_locate_recorded_part descends the roster; verdict carries
    left_member/right_member). Dispatch = _as_group_node (cheap residence
    lookup, zero cost for spells) + _fan_out_members. The ONLY remaining
    refusals are code-grain by nature: preview-against and synthesize on
    composition ids teach the member descent (a candidate previews
    against ONE module world; splicing needs one text). The S8
    _get_spell_crystal_for_read wrapper stays as defense-in-depth for
    weird states. ROOMS: zero new commands - research_source/diff/impact/
    part/parts/module/module_graph simply accept composition ids now.
    TESTS: S8 refusal test REWRITTEN into the polymorphism suite (fan-out
    content, roster part hit w/ member named, group radius via the plain
    verb, both-group diff route, mixed refusal, code-grain teach arms);
    room loop extended (fan-out + polymorphic diff through real rooms).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py (dispatch arms x8)
  - tests/unit/melder/mutation_research/test_mutation_research_compositions.py
  - tests/integration/melder/mutation_research/test_research_room_commands_integration.py
  IMPACT: One verb vocabulary serves both node families - the parity the
    owner asked for as agents will actually experience it.
  NEXT: owner-run 3.14t (MR unit trees + room integration).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:30:00Z
  TYPE: FIX (LIVE BUG - caught by the zero-mock rebirth test; owner
    challenge "I still think you're cutting corners" vindicated)
  CLAIM: The rebirth test FAILED on owner-run: the reborn root hydrated
    NOTHING ("Composition ... is not resident"). ROOT CAUSE (a
    PRE-EXISTING docking-loop flaw, not group-specific): the persistence
    profile is REPLACE-ON-EMIT, and MutationResearchConfiguration
    .activate() emitted an MR twin WITH NO composition_payload - since
    config activation necessarily precedes root activation, every
    real-crystallizer rebirth WIPED the recorded composition moments
    before virgin hydration read it (hydrate found composition={} and
    honestly no-oped). NORMAL ResearchNode hydration through this lane
    was equally broken; it never surfaced because every prior hydration
    test MOCKED describe_mutation_research_record - the mock never saw
    the wipe. FIX at the true seam: config activation now CARRIES the
    recorded composition FORWARD (reads describe_mutation_research_record
    while the crystallizer is active; emits its twin with the prior
    composition_payload attached - the configuration owns only its
    property payload, the composition is carried, never authored, never
    destroyed; the root's next re-emission supersedes as ever). Verified
    both remaining emitters carry composition (root re-emission authors
    live truth; config carries forward); first-boot arm safe (no prior
    twin -> {}). The failing zero-mock test IS the regression coverage;
    it should now pass for BOTH node families through the same lane.
  EVIDENCE:
  - src/melder/mutation_research/mutation_configuration.py (activate carry-forward)
  - src/melder/crystallizer/persistence/persistence_profile.py:47-48 (replace-on-emit law)
  - owner-run failure trace 2026-07-12 (group_view -> not resident after rebirth)
  IMPACT: The twin docking loop works on the real record for the first
    time - for spells AND compositions. The owner's skepticism found a
    genuine live bug that mocked tests structurally could not.
  NEXT: owner re-run (lifecycle integration file + MR trees).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:50:00Z
  TYPE: FIX (the epic's own escalation clause fired: identity-collision
    nuance surfaced on owner-run)
  CLAIM: The ambient-campaign test failed EXACTLY on the flagged nuance
    (FAILURE_ESCALATION: "identical member sets ARE the same identity -
    confirm rediscovery semantics if it surprises"): the fixture's
    explicit-campaign arm recomposed BACK to an ancestor's exact roster
    ({sha-a,sha-b} minus sha-b = first's {sha-a}), and content-addressing
    correctly refused it as a rediscovery of the ancestor. The LAW is
    right; two defects fixed: (1) the refusal spoke SPELL language at a
    composition ("spell identity... identical content rebinds") - set.
    register_group now pre-checks the computed group_id's residence and
    refuses COMPOSITION-GRADE ("this exact member set is already recorded
    as composition X in lane Y; evolve from it instead"; the raw claim
    stays as the race backstop); (2) the test fixture now uses a novel
    roster for the explicit-campaign arm AND gained a dedicated arm
    asserting the cycle-back rediscovery teach-grade. Prior rediscovery
    asserts still match (message keeps the "Rediscovery:" prefix);
    recompose's own no-op guard (roster identical to the IMMEDIATE
    previous) is untouched and separately covered.
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py (composition-grade rediscovery)
  - tests/unit/melder/mutation_research/test_mutation_research_compositions.py
  IMPACT: The content-address law now teaches itself at the exact moment
    an agent trips it - roster cycles name the composition they rediscovered.
  NEXT: owner re-run (MR trees + lifecycle integration).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T02:30:00Z
  TYPE: IMPLEMENTATION (S10 - EXPLICIT NODE OBJECTS on the twin; owner
    clarification: "mutation research crystal properly has its own
    objects for research node and grouped research node... possible for
    you to load it and store it in the db")
  CLAIM: My first reading (a separate crystal kind per composition) was
    WRONG - the owner wants the MR TWIN ITSELF to carry the record as
    proper objects. SHIPPED: MutationResearchCrystal now derives, AT
    CONSTRUCTION, flat value-typed DB-storable rows for BOTH node
    families from the composition payload (single source of truth - blob
    and rows structurally cannot disagree): `research_nodes` rows
    (set/lane context + spell_id/module_source_sha256/parent_spell_ids/
    author/campaign/reason/created_at) and `grouped_research_nodes` rows
    (set/lane context + group_id/member_spell_ids/parent_group_ids/...).
    Exposed as properties AND in describe() beside the composition blob -
    storage handlers map the lists straight to tables; hydration keeps
    reading the composition (the proven loop); the rows are the record's
    queryable face. Derivation is best-effort over shape (malformed
    fragments contribute no rows - a twin records what it was handed).
    Derivation logic SANDBOX-VERIFIED standalone (context, families,
    malformed-skip, JSON-clean). Both emitters produce rows automatically
    (root re-emission + the config carry-forward). TESTS: NEW unit file
    (rows per family w/ context; describe carries rows JSON-clean;
    Phase-A empty-composition arm) + the zero-mock lifecycle test now
    asserts the rows ON THE LIVE RECORD (grouped row w/ members +
    lane_type, spell rows, whole-record JSON round trip). melder_0
    mailboxed (additive keys on the mutation_research mesh kind).
  EVIDENCE:
  - src/melder/crystallizer/crystals/mutation_research_crystal.py
  - tests/unit/melder/crystallizer/persistence/test_mutation_research_crystal_node_rows.py (new)
  - tests/integration/melder/crystallizer/test_crystallizer_lifecycle_integration.py (extended)
  IMPACT: The twin has explicit, loadable, storable objects for BOTH node
    families - the DB story the owner defined.
  NEXT: owner-run 3.14t (crystallizer persistence unit + lifecycle
    integration + MR trees).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T03:00:00Z
  TYPE: STATE_TRANSITION (FINAL - owner turn-in directive)
  CLAIM: Owner directed closure ("great close it all turn it in"). FINAL
    LEDGER: S1-S7 owner-run green; post-closure addenda S8 (parity:
    ambient campaign stamp via root facades, campaign_view composition
    nodes), S9 (polymorphic verbs - one vocabulary over both node
    families), S10 (explicit twin objects: research_nodes /
    grouped_research_nodes DB-storable rows derived at construction),
    plus two live-bug fixes the owner's runs caught (docking-loop
    composition wipe -> config carry-forward law; identity-cycle
    rediscovery -> composition-grade teaching). HONEST RESIDUE: the
    S8-S10 + fix test batch (rebirth guard w/ live-record row asserts,
    crystal rows unit file, polymorphism suite, campaign/cycle arms,
    room-loop extensions) is WRITTEN AND IN THE TREE but not yet through
    an owner 3.14t run - the owner turned the lane in with that residue
    known; the tests gate nothing and will surface in the next routine
    full-tree run. Docs/graphs/philosophy/boards fully synced (535/1002).
    OPEN OWNER DECISION (outside this epic): runtime recomposition A/B/C
    (salvage ticket 19:58 DECISION_REQUEST).
  EVIDENCE: owner directive 2026-07-12; the ten IMPLEMENTATION/FIX notes
    above; artifacts/2026-07-11_mr_units_and_scales_philosophy.md.
  IMPACT: The GroupedResearchNode program is turned in complete:
    record core, mirrored strategies, twin objects, bootstrap loader for
    both node families, validators, rooms, parity, polymorphism, and a
    hardened docking loop.
  NEXT: none for this epic; residue tests ride the next full-tree run.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner-ruled GroupNode program: compositions as immutable nodes in subsystem
lanes, grouped behavior by strategy dispatch, twin/bootloader extended not
assumed, nexus rooms surfaced last. Post-closure addenda: the real-record
twin+rebirth loop is proven by a zero-mock lifecycle test (OWNER-RUN GREEN
2026-07-12), the crystallizer-side consumer set is closed by enumeration,
the S8 parity audit closed the campaign/campaign_view gaps, and S9 made the
ORDINARY verbs polymorphic over both node families (fan-out reads, roster
part search, group radius on plain impact, both-group diff routing) - one
vocabulary, no redirects. Re-entry: this epic + the ruled philosophy
artifact.
