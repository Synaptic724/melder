# Task: MR iteration 8 - agent foresight kit (source, impact, module graph, codegen preview)

## Metadata
- Task ID: TASK-2026-07-11-mr-agent-foresight-kit
- Story: successor lane to the closed MR program (owner directive 2026-07-11:
  "go ahead and implement all this")
- Status: done (owner-run 3.14t green; closed 2026-07-11T19:54:20Z)
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T20:00:00Z
- Updated: 2026-07-11T19:54:20Z

## Objective
Give agents standing in rooms the foresight surface the owner asked for:
"take a codegen and mock and guess what happens next... blast radius of a
change... walk the graphs and understand the underlying module impacts...
return the code of these objects or the module to the agent."

Four slices, all READ-ONLY, all riding existing substrate:
1. SOURCE RETURN - research_source room command + ViewSpell.describe_spell_source:
   the code of a spell's root module or whole module world; custody text first
   (synthetic always recorded; user text when retained), live-disk fallback via
   the recorded module_path, honest text_unavailable otherwise.
2. IMPACT IN ROOMS - research_impact + research_source_drift: MR root gains
   impact_view that JOINS crystallizer blast radius with research residency
   (which spells, in which lanes, incl. parked candidates and campaign stamps).
3. MODULE GRAPH WALK - research_module_graph: the custody dependency view as a
   walkable payload (modules, direct deps, reverse importers, export surfaces,
   topological load order).
4. CODEGEN PREVIEW (codegen-room only) - research_preview(code,
   against_spell_id=None): validate via the attached CodegenSystem (no
   execute), AST-extract defined names + import roots, would-be diff vs the
   current version (DiffEngine gains a public diff_materials verb; candidate
   material synthesized from the raw code), would-be blast radius per touched
   module. Nothing executes, binds, or records.

## Ticket Contract
- ENTRY_GATE: owner approval of the full four-slice design incl. the
  impact_view residency-join and codegen-only preview placement (2026-07-11
  "ok yeah this all makes sense go ahead and implement all this").
- EXECUTION_BOUNDARY: src/melder/mutation_research/** (root facades + diff
  engine additive verb) + command_system/{codegen,capability}_command_system.py
  + frame_viewer/view_spell.py + matching tests. NO crystallizer edits (its
  facades are consumed as-is), NO ACL machinery changes, NO execute/bind paths.
- DEPENDENCIES: Crystallizer.analyze_impact / get_spell_crystal /
  describe_spell_crystals facades; CrystalAnalysisResult source carriers;
  the attached CodegenSystem validate lane; the house room-command idiom.
- EXIT_GATE: sandbox harness green on all four slices; owner-run 3.14t;
  C-docs + graph synced; ticket/board synced.
- FAILURE_ESCALATION: DECISION_REQUEST on any facade-shape ambiguity in the
  crystallizer read surfaces; CONFLICT if a read path would require
  constructing hidden roots.

## Exposure Split (standing law)
- Codegen rooms: all five commands (research_source, research_impact,
  research_module_graph, research_source_drift, research_preview).
- Capability rooms: the four reads (no preview - it takes code).
- Static rooms: nothing.
- All commands: _entered_command_action idiom + room lock + non-constructing
  peeks (MR root AND crystallizer) + teach-grade refusals.

## Validation
- Sandbox: typed-mirror harness per slice (root facades over fake
  crystallizer/custody; room commands over stub rooms; preview over real ast).
- Owner-run 3.14t: full MR trees + room integration file.

## Applicable Anti-Patterns
- [ ] No execute/bind/record paths in any foresight verb (read-only law).
- [ ] No constructing Crystallizer/MR from a read (non-constructing peeks only).
- [ ] No implementation from UNKNOWN or HYPOTHESIS.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; promote UNKNOWN to FACT only with evidence.

## Notes
- DATETIME: 2026-07-11T20:00:00Z
  TYPE: PLAN
  CLAIM: Exposure-gap verified before design: zero source-returning verbs in
    rooms/viewer, zero analyze_impact/describe_spell_crystals reach from
    nexus/ or mutation_research/ (grep-proven). Substrate confirmed present:
    ImpactEngine verbs (spells_touching_module, blast_radius_of_module/spell,
    describe_source_drift), custody source carriers
    (synthetic_module_sources, user_module_sources, dependency edges,
    export_surfaces, module_load_order). Build order: read the six consumer
    surfaces -> diff_materials verb -> root facades (source_view, impact_view,
    module_graph_view, preview_candidate) -> room commands -> viewer verb ->
    tests.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:137-319
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py:478-664
  IMPACT: All four slices are additive reads over proven surfaces.
  NEXT: bounded reads of the consumer surfaces (root diff seam, room command
    idiom, viewer idiom, crystallizer facade signatures).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T20:10:00Z
  TYPE: DECISION
  CLAIM: Consumer surfaces read; design locked. ROOT gains one "Foresight
    reads" section with five verbs: source_view(spell_id, module_name=None)
    (custody text: synthetic always, user when retained; live-disk fallback
    via recorded module_to_path w/ drift marker vs sealed fingerprint; honest
    text_unavailable), impact_view(spell_id|module_name, set_name) (EXACTLY
    one question; crystallizer.analyze_impact + residency JOIN per affected
    spell: declared/lane_name/lane_state/campaign via residence_of + get_lane
    + get_node.campaign - all verified public), module_graph_view(spell_id)
    (single-crystal world walk: modules, direct deps, LOCAL reverse edges,
    exports, load order - cross-record radius stays impact_view's job),
    source_drift_view() (analyze_impact() no-args passthrough),
    preview_candidate(code, against_spell_id=None, module_name=None) (AST
    defines/import-roots + candidate sha; would-be diff via NEW public
    DiffEngine.diff_materials with candidate material keyed to the against
    spell's root_module_name so module universes align; one-target-module
    radius; parse errors honest, never raising). ROOMS: codegen +5
    (research_source/impact/module_graph/source_drift/preview; preview
    composes optional validate_codegen when frame_name given - nested
    public-command depth counter already dedupes memory), capability +4
    (no preview). VIEWER: describe_spell_source routes through the SAME MR
    peek as describe_spell_research (one foresight door, honest
    mutation_research_not_active arm). Custody-unavailable posture: LOUD
    RuntimeError on source/impact/graph/drift (caller explicitly asked for
    recorded truth - diff precedent), never fabricated empties. CONCURRENCY
    NOTE: melder_0 promoted graph to 529/990 mid-lane; my closing graph sync
    rides his baseline append-only.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:558-619
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:154-317
  - src/melder/mutation_research/mutation_research.py:757-890
  IMPACT: Zero new subsystem edges beyond room/viewer->MR (existing) and
    MR->Crystallizer (existing); everything additive and read-only.
  NEXT: implement diff_materials -> root section -> rooms -> viewer -> tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T19:40:42Z
  TYPE: IMPLEMENTATION
  CLAIM: All four slices SHIPPED, all read-only, zero new subsystem edges.
    ROOT (mutation_research.py "Foresight reads" section):
    _require_live_custody (LOUD RuntimeError posture), source_view
    (recorded-first via synthetic/user_module_sources; live-disk fallback
    through module_to_path w/ sha-vs-sealed-fingerprint drift marker;
    honest unknown_module/text_unavailable), impact_view (exactly-one-center
    ValueError; analyze_impact radius preserved verbatim + `research`
    residency join), _residency_join (residence_of/get_lane/get_node.campaign;
    undeclared = declared:False), module_graph_view (modules sorted, direct
    deps, LOCAL reverse edges, exports, fingerprints, paths, load order),
    source_drift_view (no-args analyze_impact passthrough),
    preview_candidate (sha + AST defines/import-roots [top-level defs,
    absolute roots deduped]; against_spell_id adopts the against root module
    for source+structural diff_materials; module-centered impact; parse
    errors honest, never raising), _analyze_candidate. DIFF:
    DiffEngine.diff_materials (pre-resolved materials; resolver untouched;
    validates dicts; unknown strategy names known family). ROOMS: codegen +5
    (research_source/impact/module_graph/source_drift/preview; preview
    composes validate_codegen(code, frame_name=...) BEFORE entering its own
    command action when frame_name given, validation:None otherwise),
    capability +4 (no preview). NOTE: neither room's presentation-tuple
    (_CODEGEN_COMMAND_METHOD_NAMES/_CAPABILITY_COMMAND_METHOD_NAMES) lists
    ANY research_* command - matches the existing 13-command precedent, left
    consistent. VIEWER: describe_spell_source mirrors describe_spell_research
    exactly (same Aether._instance peek, same honest
    mutation_research_not_active arm). TESTS (WRITTEN, NOT RUN - owner runs
    3.14t): tests/unit/melder/mutation_research/test_mutation_research_foresight.py
    (12 tests: recorded-first, live-disk drift both arms, honest misses, loud
    dead-custody, one-center law, residency join incl. campaign stamp,
    reverse edges, drift passthrough, parse-error honesty, defines/roots,
    full against-version mock, module-centered preview);
    diff/test_diff_engine.py +2 (materials skip resolution w/ refusing
    resolver; validation + strategy naming); room integration file: split
    test now asserts ten capability reads + preview ABSENT, new
    test_codegen_room_foresight_loop (real codegen room, _FakeCrystallizer
    swapped onto root, full five-command loop incl. refusal-before-activation
    and validation:None). Foresight unit file py_compile-verified in
    sandbox; grown files could NOT be compile-checked there (bash replica
    rot re-confirmed: diff test replica truncated at line 147 mid-string,
    command-system replicas missing today's methods entirely - file-tool
    greps prove all real files intact; running pytest in sandbox would
    execute STALE copies, so no run attempted). DOCS+GRAPH: src_components.md
    (rooms invariant bullet split into research+foresight surfaces; root
    subcomponent gains foresight-reads contract bullet; USER SURFACE bullet
    13->18/six->ten + describe_spell_source), src_architecture.md (Aether MR
    verb list + rooms section updated same way), src_graph.json +
    readable_src_graph.json both still exactly 529/990 (melder_0 baseline,
    append-only ridden): MutationResearch + DiffEngine roles/responsibilities
    extended, 4 whys refreshed (codegen borrows, capability borrows [ten
    reads], ViewSpell borrows [+describe_spell_source], MR->Crystallizer
    uses [foresight facade consumption]) - file-tool-verified 4 hits per
    graph file.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1006-1529
  - src/melder/mutation_research/diff/diff_engine.py:146-203
  - src/melder/nexus/rift/command_system/codegen_command_system.py:1010-1181
  - src/melder/nexus/rift/command_system/capability_command_system.py:1215-1310
  - src/melder/nexus/rift/frame_viewer/view_spell.py:566-629
  - tests/integration/melder/mutation_research/test_research_room_commands_integration.py:113-233
  IMPACT: Agents in rooms can now read the code of any recorded world, see
    a residency-joined blast radius, walk module graphs, check drift, and
    mock a codegen candidate before anything executes - the owner's full
    foresight ask.
  NEXT: owner-run 3.14t (full MR trees + room integration file) is the only
    open gate; then move to completed/.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T19:55:00Z
  TYPE: FIX
  CLAIM: First owner-run (3.14t --last-failed, 3 selected) caught ONE real
    defect, mine: _FakeCrystallizer lacked emit_mutation_research_state, so
    MR cleanup (which emits RecordedUnitState.cleaned into live custody)
    blew up INSIDE reset_runtime_singletons at fixture teardown -
    AttributeError after _cleaned=True but before singleton bookkeeping
    reset, leaving a cleaned-but-initialized MR singleton that poisoned the
    two test_aether.py failures (pure pollution victims: the lazy accessor
    correctly refuses a cleaned root). Fix is double-walled: (1) the fake
    now carries emit_mutation_research_state (no-op, matching emit), (2) the
    test swaps the fake in ONLY for the command window and restores the
    REAL crystallizer in a finally, so the teardown/cleanup lane always
    talks to real custody regardless of what verbs MR grows later. LESSON
    (reusable): any fake swapped onto root._crystallizer must survive the
    CLEANUP lane, not just the read lane - or better, never be left
    installed at teardown.
  EVIDENCE:
  - tests/integration/melder/mutation_research/test_research_room_commands_integration.py (foresight loop, try/finally + fake verb)
  - src/melder/mutation_research/mutation_research.py:167 (the cleanup emission the fake missed)
  IMPACT: All three reported failures share this single root cause; no
    product-code defect surfaced.
  NEXT: owner re-run (same 3 via --last-failed, then the MR trees clean).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T19:54:20Z
  TYPE: STATE_TRANSITION
  CLAIM: in_review -> DONE. Owner re-ran 3.14t after the _FakeCrystallizer
    fix: "all passed" - the 3 --last-failed selections green (foresight
    room loop + the two pollution-victim aether tests self-healed exactly
    as diagnosed). EXIT_GATE fully satisfied: (1) harness green on all four
    slices (12 unit foresight + 2 diff_materials + split-law + room loop),
    (2) owner-run 3.14t green, (3) C-docs + both graphs synced (529/990
    held append-only on melder_0's baseline), (4) ticket/boards synced.
    Completed on its own terms: every slice of the owner's ask ("return
    the code... blast radius... walk the graphs... take a codegen and mock
    and guess what happens next") is live on the room/viewer surface,
    read-only by law, zero new subsystem edges.
  EVIDENCE: owner message 2026-07-11 ("great job all passed"); prior
    IMPLEMENTATION + FIX notes carry the full seam map.
  IMPACT: The MR program now has its agent-facing foresight surface; no
    follow-on lane opened (none requested).
  NEXT: none.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
CLOSED DONE 2026-07-11T19:54:20Z, owner-run green. Owner-approved foresight
kit shipped: source return (recorded-first w/ live-disk drift marker),
residency-joined impact, module graph walk, drift report, and the
codegen-only candidate preview ("mock what happens next") - root facades +
DiffEngine.diff_materials + codegen room +5 / capability room +4 /
ViewSpell.describe_spell_source, all read-only, riding the shipped MR +
crystallizer substrate with zero new subsystem edges. One test-fake defect
found and fixed on first run (fake must survive the cleanup lane; real
crystallizer restored in finally). Durable truth: this ticket + the synced
C-docs/graphs.
