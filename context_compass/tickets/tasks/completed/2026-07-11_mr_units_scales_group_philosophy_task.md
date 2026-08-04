# Task: MR units-and-scales philosophy (the group layer design frame)

## Metadata
- Task ID: TASK-2026-07-11-mr-units-scales-group-philosophy
- Story: owner directive 2026-07-11 ("hold on philosophy ticket first...
  help me form the philosophy go all out") - pauses the group BUILD until
  the philosophy is ruled on
- Status: done (owner ruled 2026-07-11; closed 2026-07-11T23:00:00Z)
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T21:10:00Z
- Updated: 2026-07-11T21:10:00Z

## Objective
Form the philosophy underneath ResearchGroup/ResearchGroupSet before any
code: what the units of the record are, at what scale each question gets
answered, how the module sits in blast radius at group grain, and how
deeply the record examines the inside of one object.

## Ticket Contract
- ENTRY_GATE: owner directive (explicit "philosophy ticket first").
- EXECUTION_BOUNDARY: artifacts/ + this ticket ONLY. No src changes, no
  test changes - the group build gets its own ticket after the ruling.
- EXIT_GATE: owner rules on the artifact's decision points (below); the
  build ticket inherits the ruled frame.
- FAILURE_ESCALATION: none (pure design lane).

## Decision Points for the Owner
1. GRAIN LAWS: change=parts, identity=objects, impact=modules, work=groups,
   intent=campaigns; each question answered at its own grain. (Section 3)
2. DEPTH FLOOR: the record examines one version down to top-level parts
   (custody-true parsing) and REFUSES statement/call-graph depth (the
   record never guesses). Part-fingerprint index recorded as a future
   depth-3 sharpening. (Section 4)
3. GROUPS ARE VIEWS: membership references lanes (never versions), overlap
   allowed, no gating, groups do not version (organizational acts journal
   instead). (Sections 2, 5)
4. TWO MEMBERSHIP MODES: extensional (curated lane list, primary) +
   intensional (module-prefix predicate resolved at root read-time);
   disagreement between them is surfaced as signal. (5.1)
5. THE PHYSICAL SHADOW READS: derived footprint, direction-split group
   impact (internal vs outbound), group CLOSURE as the workspace-safety
   number, group adjacency as the coupling map. (5.2)
6. STRUCTURE: ResearchGroup (one view) + ResearchGroupSet (per-set
   registry owned by ResearchSet); groups ride organization payloads,
   snapshots, restore, hydration; 4 new additive TransitionActs; exposure
   split organization-verbs=codegen / reads=both rooms. (Section 6)
7. NOT-LIST: not custody, not runtime clusters, not merge scopes, not
   ACLs. Nesting deferred (open direction with a typed-member entry
   path). (Sections 6, 7)
8. FULL-MODULE COMPARISON + THE CRYSTAL WELL (owner clarification
   2026-07-11): string diffs speak the WHOLE module's recorded text
   (synthetic AND user-retained), never just the bound class; diffs read
   recorded text only (live disk would compare a file with itself and lie
   about both versions); one direct MODULE DOSSIER verb queries the spell
   crystal for everything it knows about one module (text by kind,
   fingerprint, path, deps/importers, exports, drift). FOUND GAP riding
   this ruling: _resolve_diff_material reads synthetic_module_sources
   only - user-retained text never enters diff material (fingerprint-only
   rows where full text exists in custody). Small custody-true fix,
   independent of groups; can land immediately on approval. (Sections 3,
   4.1)

## Notes
- DATETIME: 2026-07-11T21:10:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Artifact drafted covering all three owner questions as one frame
    (units + scales). Key stances taken for ruling: two-hierarchy model
    (logical identity vs physical matter, joined at the version; impact =
    the crossing move); the ladder (parts have names not identities,
    versions have identities not names, objects have both, groups have
    membership); module = the only honest impact boundary in Python (finer
    claims are guesses; the record never guesses); groups as overlapping
    non-gating views with curated + structural membership; closure and
    adjacency as the agent workspace-selection story; groups persist as
    organization and journal forward.
  EVIDENCE: artifacts/2026-07-11_mr_units_and_scales_philosophy.md
  IMPACT: The group build ticket inherits whatever survives the ruling;
    the paused ResearchGroup implementation starts only after.
  NEXT: owner reads/rules; then open mr_research_groups build ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T23:00:00Z
  TYPE: STATE_TRANSITION
  CLAIM: in_review -> DONE (ruled). Rulings: points 1-2 (grain laws, depth
    floor) ACCEPTED as drafted and already partially executed (the
    module/part-grain reads lane shipped point 8's full-module comparison
    + crystal well + grain choice). Points 3-6 (groups-as-views,
    ResearchGroupSet registry, membership modes) REJECTED by the owner for
    the stronger GroupNode model: "having a concrete node with multiple
    spell_ids makes more sense... you get semantic behaviours that match
    our existing behaviours... provide a new strategy system for grouped
    behaviours." Artifact sections 5-7 REDRAFTED to the ruled model
    (content-addressed composition nodes, subsystem lanes, strategy
    dispatch, pinned members + explicit recompose + drift read, purely
    informational law, bootloader extension named). Closure/adjacency/
    direction-split impact survive as reads. Build tracked by
    tickets/epics/2026-07-11_mr_group_nodes_epic.md (S1 record core ->
    S2 strategies/reads -> S3 twin+bootloader validators -> S4 nexus
    rooms -> S5 docs/closure).
  EVIDENCE: artifacts/2026-07-11_mr_units_and_scales_philosophy.md (RULED header + sections 5-7)
  IMPACT: The philosophy lane completed on its own terms - a ruled frame
    the epic inherits verbatim.
  NEXT: none (epic owns the build).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
CLOSED RULED 2026-07-11T23:00:00Z. Grain laws + depth floor + comparison
laws + crystal well accepted (and largely shipped); groups-as-views
rejected for the owner's GroupNode model (composition = node, subsystem =
lane, behavior = strategy dispatch); artifact redrafted; build lives in
the mr_group_nodes epic.
