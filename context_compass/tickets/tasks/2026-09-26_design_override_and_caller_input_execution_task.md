

# Task: Design override execution and caller-supplied inputs as one contract (alternative to joint alpha)

## Metadata
- Task ID: TASK-2026-09-26-design-override-and-caller-input-execution
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: none (epic-level design task)
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T00:14:30Z
- Updated: 2026-09-26T11:23:09Z

## Objective
Produce a source-grounded design that (1) lets a constructor declare parameters the caller always
supplies (Package, Conduit, greenlet, Spectrum) so conjure accepts them and meld requires them, and
(2) makes supplied overrides remove construction work instead of substituting values afterwards.
Compare it against joint_alpha_proposal.md and recommend one path with tradeoffs.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("go back to the original issue ... we can probably do better").
- EXECUTION_BOUNDARY: Read src/, tests/ and existing artifacts. Write only this ticket and
  artifacts/melder_override_design_20260926/. No src/, tests/, canonical doc, version or asset edits.
- DEPENDENCIES: joint_alpha_proposal.md, compact_structure_proposal.md, native_runtime_boundary.md,
  required_caller_inputs findings.md, melder_1's regression matrix, the completed slot-guard fix.
- EXIT_GATE: Design artifact with evidence-backed current-behavior claims, a comparison with joint
  alpha, decisions the owner must make, and an implementation sequence; task in review.
- FAILURE_ESCALATION: DECISION_REQUEST for semantic policy choices; CONFLICT where source contradicts
  a proposal; no behavior claim from documents or search hits alone.

## Scope Boundaries
- In scope: Phase 1/3 parameter classification, Phases 8-11 occurrence/injection/targeting/planning/
  emission, CreationContext dispatch, ConduitMeld/SpellSpaceMeld doors, override semantics, caller inputs.
- Out of scope: Production edits, hook standardization, existing-object ownership redesign, the
  comptime IR epic, cache-format changes beyond what the design must name.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed melder_0 to design a better alternative, 2026-09-26T00:14:30Z.
- from_state: in_progress
- to_state: review
- transition_reason: Design artifact written; D1-D4 raised, 2026-09-26T00:22:28Z.
- from_state: review
- to_state: in_progress
- transition_reason: Owner reopened the override performance lane ("go back to the real overrides issue ...
  overrides are 20% of the speed of normal resolution ... make a sound structural strategy"), 2026-09-26T08:58:44Z.
- from_state: in_progress
- to_state: review
- transition_reason: design_v2.md written after the owner's "ok go ahead and get started"; Q1-Q5 raised, 2026-09-26T11:06:53Z.
- from_state: review
- to_state: in_progress
- transition_reason: Owner approved the E1-E4 prototype experiment ("yeah sure go ahead give it a go"), 2026-09-26T11:11:51Z.
- from_state: in_progress
- to_state: review
- transition_reason: E1-E4 prototype results written (prototype_results.md); Q1-Q5 still open, 2026-09-26T11:23:09Z.

## Steps / Checklist
- [x] Read joint_alpha_proposal.md, structural_plan.md, compact_structure_proposal.md,
      native_runtime_boundary.md, semantics_findings.md and the caller-input findings.
- [x] Read the current physical-graph producers (Phase 9 instance/injection rows) and targeting.
- [x] Read the ordinary and override emitters' step order and reuse handling.
- [x] Read Phase 1/3 classification for caller inputs and OVERRIDE_REQUIRED (via probe and findings).
- [x] Write the design artifact and the joint-alpha comparison.
- [x] Record owner decisions as DECISION_REQUEST notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/melder_override_design_20260926/design.md (superseded from "The design" onward)
- artifacts/melder_override_design_20260926/design_v2.md
- artifacts/melder_override_design_20260926/prototype_results.md (E1-E4; prototype v2_prototype.py, v2_experiment.py)

## Files / Paths Impacted
- None in src/ or tests/. This ticket and its artifact directory only.

## Validation
- Not run.

## Risks / Rollback Notes
- Prototype results describe artifact adapters, not production; cite source for current behavior.
- updater_0/updater_1 own the epic's discovery tasks; this task reads their artifacts and does not edit them.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_override_design_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Override execution semantics; caller-supplied constructor inputs.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:14:30Z
  TYPE: PLAN
  CLAIM: Joint alpha's native claim protocol (non-blocking claims, release-before-wait, retry, claim
    records) exists to break the store/Spell inversion, which the shipped slot guards already remove with
    an acyclic consumer-first lock order. Its runtime alias activation makes operand choice depend on live
    store state. Test the hypothesis that a static per-input-shape plan executed top-down under slot guards
    gives deterministic semantics with far less machinery. Caller inputs join as unprovided sockets.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:61-106
  - artifacts/override_structural_discovery_20260924/native_runtime_boundary.md:72-104
  - artifacts/required_caller_inputs_20260924/findings.md:99-135
  IMPACT: If source supports it, the design drops the claim subsystem and the conditional alias program.
  NEXT: Read Phase 9 instance/injection rows and the override targeting strategy in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:17:13Z
  TYPE: FACT
  CLAIM: The physical construction graph already exists upstream: the occurrence analyzer collapses each
    shared spell to one expansion and the instance processor keys shared sites (spell_id, None) and many
    sites per path. The Phase-5 socket overlay does not collapse: it walks every logical path, and override
    targeting then builds exact-path keys for every socket ref. This runs at conjure with or without
    overrides. Probe (3.14.7t, caching off): a binary unique chain of 15 sites yields 32,766 root socket
    refs and 0.31 s conjure (0.08 s at 13 sites): cost grows ~4x per two levels while work stays linear.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:719-785
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:127-215
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:435-500
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:51-110
  - artifacts/melder_override_design_20260926/current_behavior_results_314t.json
  IMPACT: The design can reuse the existing physical graph and must remove path enumeration from Phase 5
    and targeting; selectors can be resolved by walking named edges, never by enumerating paths.
  NEXT: Record the probe's ordinary-reuse, supplied-dependency and caller-input results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:17:13Z
  TYPE: MEASURE
  CLAIM: Same probe, current source: (1) ordinary meld of Root(many)->Middle(unique)->Leaf(many) twice
    builds Leaf twice though Middle is reused (eager bottom-up plan, no override involved); (2) supplying
    a and b to Consumer(a, b, c) still constructs A and B, then passes the supplied objects (identity kept);
    (3) Task(work: Package) with Package unbound fails conjure in Phase 3 ("no DI candidate").
  EVIDENCE:
  - artifacts/melder_override_design_20260926/current_behavior_probe.py:60-140
  - artifacts/melder_override_design_20260926/current_behavior_results_314t.json
  IMPACT: Wasted construction is a property of the bottom-up step order, not only of overrides, so the
    fix belongs in the shared lowering; caller inputs are blocked before any meld-time path can help.
  NEXT: Read the ordinary emitter's step order and reuse block to confirm the bottom-up cause in source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:19:24Z
  TYPE: FACT
  CLAIM: The generalized plan emits steps in Kahn topological order (providers first, spell-id tie-break),
    one step per instance key, so every shared step is checked for reuse only after its dependencies were
    already built. That is the source-level cause of the ordinary Leaf waste. A top-down (consumer-first)
    lowering cannot simply nest `with guard:` blocks inline: CPython 3.14.7 compiles 21 nested `with`
    blocks but rejects 40 ("too many statically nested blocks"), so shared-site miss branches must be
    separate emitted functions while hit paths stay inline.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:103-171
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1500-1600
  IMPACT: The design lowers each shared site as inline hit + out-of-line miss function; many sites stay
    inline under their physical parent. Nesting depth no longer tracks graph depth.
  NEXT: Write design.md: static per-shape plan, top-down lowering under slot guards, caller-input sockets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:22:28Z
  TYPE: DECISION
  CLAIM: Design written. Recommend: static plan per override key shape over the existing physical graph,
    lowered top-down (inline hit, out-of-line miss under the shipped slot guards); the empty shape is the
    ordinary meld. Caller inputs become a provider-less socket declared per binding. Drops joint alpha's
    claim protocol, live-state operand selection and selector-state machine; removes Phase-5 path
    enumeration so conjure is linear. Sequence S1 caller inputs -> S2 rows/selectors -> S3 ordinary
    lowering (parity gate) -> S4 shapes -> S5 qualification.
  EVIDENCE: artifacts/melder_override_design_20260926/design.md:1-204
  IMPACT: One lowering replaces the separate override compilers; no new concurrency protocol is needed.
  NEXT: Owner decides D1-D4 (next note); S1 can start independently once D1 is chosen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:22:28Z
  TYPE: DECISION_REQUEST
  CLAIM: D1 caller-input declaration surface (per-binding keyword recommended; optional auto-classification
    of unbindable kernel types). D2 reuse never changes operands (revises item-4 (a) for runtime reuse;
    static cuts keep (a)). D3 two live PATH rules on one physical input are a shape error (replaces item-5
    (c)). D4 accept depth-first constructor order and fewer throwaway constructions in ordinary melds.
  EVIDENCE: artifacts/melder_override_design_20260926/design.md:166-179
  IMPACT: D1 gates S1; D2-D4 gate S3/S4 and the regression matrix rows R4b, R4c, R5c, R5d.
  NEXT: Owner answers D1-D4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:58:44Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Lane reopened. Owner goal: a sound structural strategy for implementing the override fix, starting
    from joint_alpha_proposal.md (Codex) and understanding where the 5x gap to ordinary resolution comes from.
    D1 is settled by the shipped S1 (automatic UNRESOLVED_INPUT socket, no per-binding keyword); D2-D4 remain
    open. Scope stays read-only on src/ until the owner approves a strategy. Mailbox M1-9 answered (M0-15):
    melder_1 owns an inspect.signature src lane; no file overlap with this read-only work.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:1-150
  - artifacts/melder_override_design_20260926/design.md:166-204
  - tickets/stories/completed/2026-09-26_unresolved_input_sockets_story.md
  IMPACT: The strategy must be grounded in a measured cost breakdown of the current override path, which
    neither proposal has: joint alpha's evidence is semantic/mechanism proofs and design.md measured nothing.
  NEXT: Read the epic's current structural design and the baseline/compiler measurement artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T09:00:20Z
  TYPE: FACT
  CLAIM: Where an override meld spends its time, from source (many_only; generalized has the same targeting
    artifact). Per call, execute_with_overrides splits __args__, then targeting maps each RAW KEY to socket
    rows and builds a NEW socket-keyed override_map and socket_shape: one key hits a last-call cache only if
    the VALUE is the same object; two to four keys build a sorted (key, id(value)) signature; every other
    call loops keys, ranks specificity, compares equal-rank values with `!=`, builds the map and sorts shape
    rows. The executor cache is then keyed by that socket_shape (identity fast path fails whenever the tuple
    is rebuilt), and the executor body reads values back out of the socket-keyed map per step. So the stable
    thing (the caller's key set) is re-derived per call from the unstable thing (the values). Prior
    measurements (09-24, before slot guards) split this: shallow override public 1.997us vs executor 1.047us;
    wide with 8 root keys 9.44us public vs 3.12us executor; deep is executor-dominated (154us vs 32us normal).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:243-470
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/artifacts/spell_override_targeting_codegen_creation.py:210-427
  - src/melder/aether/conduit/meld/conduit_meld.py:259-580
  - artifacts/override_emission_prototype_20260924/results.md:1-48
  IMPACT: The 5x has three separable causes: per-call targeting (front end), an interpreted executor body,
    and construction of supplied branches. A plan keyed by the raw key set can read values by literal key
    (`ov["a"]`) and remove the first two without any semantic change; pruning is the third and is semantic.
  NEXT: Measure the current (0.2.54, slot-guard) split on 3.14t: public vs targeting-only vs executor-only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T09:09:11Z
  TYPE: MEASURE
  CLAIM: Current gap re-measured on 0.2.54 (3.14.7t, VM copy, automatic, disk cache off, 7 repeats, existing
    experiment test_melder_creation_overrides_performance.py). Override throughput vs normal: shallow 21.8%,
    wide 20.4%, diamond 21.1%, deep 22.5% (one fresh root key); wide with all 8 root keys 8.1%. Key control:
    empty_tuple (override=() -> no keys, no targeting, generic override executor) is already 19.7-23.2%, e.g.
    deep 110.7us vs 25.7us normal. So the interpreted override executor body alone accounts for the 5x on
    every graph; per-key targeting adds on top (wide 7.0us with 8 keys vs 2.8us with 1).
  EVIDENCE:
  - artifacts/melder_override_design_20260926/perf_0254_314t/automatic/results.md
  - artifacts/melder_override_design_20260926/perf_0254_314t/automatic/results.json
  IMPACT: Fixing targeting alone cannot close the gap; the executor lowering is the primary lever and pruning
    is secondary for these transient graphs.
  NEXT: Paused for the owner-directed conjure validation_warnings task; resume with the executor/targeting
    split probe (public vs targeting-only vs executor-only).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T09:15:57Z
  TYPE: FACT
  CLAIM: Mailbox F0-1 consumed (fable_0, NOTICE, no ACK requested). Owner approved fable_0's compiler tranche:
    one leaf serialize/hash/freeze implementation under spell_compiler/shared_assets/, with
    phases/shared_compiler_executions.py and codegen_creation_schema_helpers.py delegating (three helpers),
    plus a phase-8 key-path change. fable_0 edits shared_compiler_executions.py only after the
    missing_dependency_sockets hunks (landed, story closed 08:54:37Z); caching_system.py and generation 11
    are untouched; byte-compatible for deterministic signatures (no generation bump).
  EVIDENCE: tickets/stories/2026-09-26_signature_determinism_and_phase8_digest_story.md
  IMPACT: Any override prototype touching shared_compiler_executions.py or phase-8 keys must rebase on
    fable_0's tranche; the conjure validation_warnings task touches neither file.
  NEXT: Resume this lane with the executor/targeting split probe after conjure_validation_warnings.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T10:13:36Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Lane resumed after closing TASK-2026-09-26-add-conjure-validation-warnings-flag. Owner wants to talk
    about overrides before more work. Proposed next step (not started): executor/targeting split probe -
    time public override meld vs targeting-only vs executor-only on shallow/wide/diamond/deep, read-only.
  EVIDENCE: tickets/tasks/completed/2026-09-26_add_conjure_validation_warnings_flag_task.md
  IMPACT: Keeps the lane read-only until the owner and melder_0 agree on the probe and strategy framing.
  NEXT: Discuss override strategy with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T10:27:11Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner directs a deep read of the epic and the Codex (updater_0/updater_1) work before any strategy.
    Epic re-read corrects my framing: the owner's primary goal is STRUCTURAL - supplied dependencies must
    not be constructed (5 deps, 3 supplied -> build 2 + consumer; deep both-branches supplied -> 1 of 511).
    The owner already rejected the emission-only prototype (all constructors kept; 41.8/53.3/41.6/95.3% of
    normal) as the endpoint (decision 2026-09-24T11:16:08Z). So pruning is the objective, not a
    "secondary, semantic" lever as I wrote at 09:09Z; instruction cost is the second objective.
  EVIDENCE:
  - tickets/epics/2026-09-24_override_execution_performance_epic.md:15-35
  - tickets/epics/2026-09-24_override_execution_performance_epic.md:254-268
  IMPACT: Any strategy I propose must be judged first on construction-demand pruning with correct shared
    semantics, then on per-call cost; a faster eager executor does not meet the epic.
  NEXT: Read joint_alpha_proposal.md, compact_structure_proposal.md, native_runtime_boundary.md,
    structural_plan.md, semantics_findings.md, then the tasks' notes; verify key claims in source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:27:11Z
  TYPE: FACT
  CLAIM: Joint alpha, as written (document claims, not yet source-verified by me): (1) one compact physical
    construction graph shared by ordinary and override execution (each physical site once; shared providers
    have several incoming edges; many children belong to their physical parent socket); (2) a prepared
    request program per selector/operand layout: exact-path selectors advance (selector, prefix) states over
    named edges, OR-merged at shared sites, PATH>UNIQUE>BROADCAST kept, UNIQUE counted over declared
    logical paths without storing them; each physical parameter keeps guarded ranked candidate operands
    plus a conditional default edge; (3) generated direct constructor calls with only remaining guards;
    (4) a native claim prelude, consumer-first, that settles reuse hit/miss for demanded shared sites
    before any constructor, using nonblocking per-entry claims with release-all-before-wait and retry
    (no replay after user code). Contract items 1-8: whole supplied dep cuts demand; param override keeps
    owner; validate selectors even under cut ancestors; rules below a supplied/reused constructor are
    inactive and cannot influence another path; normalize surviving aliases, reject incompatible equal-rank
    inputs; keep root refusal of override-on-reuse; retained unresolved descriptor fails honestly; no
    constructor replay. Evidence cited: 42 scenario evaluations vs an expanded oracle; 6->3, 511->256->1;
    depth-64 synthetic graph = 65 sites; 7+1 native adapter cases; 12 lock-order controls showing the
    store/unique-Spell inversion (since fixed by slot guards, 2026-09-25). No native throughput measured.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:1-150
  - artifacts/override_occurrence_discovery_20260924/compact_structure_proposal.md:1-236
  - artifacts/override_structural_discovery_20260924/native_runtime_boundary.md:1-180
  - artifacts/override_structural_discovery_20260924/structural_plan.md:1-247
  - artifacts/override_structural_discovery_20260924/semantics_findings.md:1-147
  IMPACT: The proposal has three separable parts - compact graph + selector program (compiler), pruned
    direct emission, and a new native claim protocol - each needing its own verification against today's
    source (which changed since 09-24: slot guards 09-25, unresolved inputs 09-26).
  NEXT: Read structural_findings.md and the discovery task notes; then verify the current-behavior claims.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:27:54Z
  TYPE: FACT
  CLAIM: History of the epic, from its artifacts (document claims; behavior still to be source-checked):
    (1) 09-24 baseline (updater_1): override 20-25% of normal; empty-tuple override already ~20% (deep
    153.7us vs 32.0us); 8 wide root keys 8.6%; constructor counts unchanged by supplying (3/9/511).
    (2) compiler diagnosis (updater_1): Phase 10 builds both variants from one ordered model but only
    normal keeps the fast call layout; Phase 11 override emission passes only targeted-spell ids and counts,
    so the executor re-derives parameter identity at runtime (SocketRef reads, name compares, kwargs dicts,
    per-step store selection, result dict). (3) emission-only prototype: same constructors, normal-style
    lowering + exact socket substitution -> 41.8/53.3/41.6/95.3% of normal (deep 4.68x); public front end
    still large on small/wide graphs (wide all-root 7.38us public vs 1.26us executor). Owner rejected it as
    the endpoint and chose structural pruning (09-24T11:16). (4) structural discovery: logical paths vs
    physical sites; row-slice shows 6->3, 511->256->1; counterexamples (ghost Token when expanding aliases
    then grouping; a rule under a replaced path leaks into the surviving alias; secondary-path descendant
    rules ignored); static alias model failed two lead counterexamples (rules under a reused parent);
    conditional model (guarded ranked candidates + conditional default edges) passes 20 cases. (5) compact
    graph + selector-state program + generated direct calls (42 evals, 511->1, depth-64 = 65 sites), then a
    native claim prelude and direct-publication adapter (8 cases). (6) melder pair 09-25: lock inversion
    confirmed and fixed by slot guards; contract matrix with owner-recorded choices item 4 (a) inactive path,
    item 5 (c) identity then == for scalars; carried: item-7 per-family wording, R5d probe, R7c, nested
    unresolved contract. (7) my design.md (09-26) proposed dropping the claim protocol and live-state operand
    choice (D2 conflicts with the recorded item 4 (a) for runtime reuse).
  EVIDENCE:
  - artifacts/override_execution_performance_20260924/findings.md:1-76
  - artifacts/override_compiler_investigation_20260924/compiler_findings.md:1-164
  - artifacts/override_emission_prototype_20260924/findings.md:1-116
  - artifacts/override_occurrence_discovery_20260924/structural_findings.md:1-321
  - artifacts/override_execution_lead_20260924/runtime_constraints.md:1-140
  - artifacts/melder_override_contract_20260925/regression_matrix.md:1-136
  - tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md:320-400
  - artifacts/melder_override_design_20260926/design.md:1-204
  IMPACT: The problem has two independent halves - wasted construction (structural, owner's goal) and
    per-call instruction cost (front end + executor). Joint alpha addresses both but couples them to a new
    lock protocol whose original motivation (the inversion) is gone since 09-25.
  NEXT: Read the two Codex discovery task tickets' notes for the iterations and dead ends.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:28:19Z
  TYPE: FACT
  CLAIM: Codex iteration path (from both discovery tasks' notes, 09-24): row-slice over current phase-9 rows
    (11 scenes, simple cuts OK) -> found alias asymmetry in NATIVE behavior (confirmed by public Meld only:
    secondary-path descendant rule ignored 91->13; a rule under the replaced primary path changes the
    surviving secondary alias) -> static alias plan with permanent winners (9 cases) -> lead counterexamples
    under a REUSED parent (rule below a reused CachedParent conflicts/outranks FreshParent's rule) ->
    conditional plan: all ranked candidates guarded by construction demand + conditional default edges
    (20 cases, 91/conflict/91 and 91/21/91 transitions) -> compact physical graph + selector states instead
    of expanded logical paths (42 evals, depth-64 in 65 sites) -> reuse decisions must be SETTLED before
    choosing operands, so a consumer-first claim prelude (12 cases) -> native claim protocol to avoid the
    store/Spell inversion (entry claims, release-before-wait) -> integrated adapters (7 + 8 cases). Every
    step was an artifact-side interpreter or adapter over prevalidated fixtures; none touched production,
    none measured throughput. The claim protocol exists because conditional operand choice depends on live
    reuse state (a descendant's inputs depend on which parents are reused this call).
  EVIDENCE:
  - tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md:98-706
  - tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md:91-771
  IMPACT: The protocol's complexity is a consequence of one policy choice (item 4 (a) applied to RUNTIME
    reuse: rules below a reused parent are inactive and cannot affect another path). The other big parts
    (physical sites, selector states, pruned direct emission) are independent of that choice.
  NEXT: Read the compact plan/emitter/prelude/direct-adapter code to see what the lowering actually emits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:29:27Z
  TYPE: FACT
  CLAIM: Read the prototype code. CompactPlan is a boolean guard program over physical sites: per site a
    demand guard and a construct guard (shared: demand AND NOT reuse[spell]); per (site, parameter) a list of
    ranked candidate operands, each guarded (PATH state reaching it AND constructing; UNIQUE/BROADCAST:
    constructing); a child edge is live when constructing AND NOT supplied. Exact paths advance
    (rule, prefix) states over physical edges, OR-merged; UNIQUE counts declared paths by DP. bind() picks the
    highest active rank and compares equal-rank values with `!=`. The emitter lowers to straight-line direct
    calls with literal raw-key reads; for many-only shapes it is exactly `n4=C4(); n0=C0(a=raw['a'], d=n4)`.
    The claim prelude runs consumer-first over ALL demanded shared sites BEFORE any constructor, calling
    select(site) which acquires and HOLDS a per-entry claim (hits included) until the whole call finishes;
    contention releases everything and retries (up to 32). Why: a shared descendant's operand choice depends
    on the reuse outcome of every ancestor on every alias, and a depth-first build would construct the
    descendant before some of those ancestors' reuse is known; holding claims freezes those outcomes.
  EVIDENCE:
  - artifacts/override_occurrence_discovery_20260924/compact_alias_plan.py:40-311
  - artifacts/override_occurrence_discovery_20260924/compact_alias_emitter.py:23-178
  - artifacts/override_occurrence_discovery_20260924/compact_five_generated.py:1-14
  - artifacts/override_occurrence_discovery_20260924/compact_claim_prelude.py:19-122
  - artifacts/override_structural_discovery_20260924/native_compact_direct_adapter.py:36-130
  IMPACT: The claim protocol is the price of item 4 (a) applied to RUNTIME reuse (reuse-dependent operands),
    and it puts a per-entry lock on every warm shared hit plus serialization of melds sharing a site for the
    whole call. If operands depend only on the static shape (my D2), decisions need no freezing: today's slot
    guards with recheck suffice and warm hits stay lock-free. That is the one owner decision the whole
    architecture turns on. Everything else in joint alpha (physical sites, selector states, pruned direct
    emission) is compatible with either answer.
  NEXT: Re-run the Codex probes on current source (VM copy, receipts kept out of the mount) to see which
    of their proofs and native observations still hold after slot guards and unresolved inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T10:32:04Z
  TYPE: MEASURE
  CLAIM: Re-ran the Codex probes on current source (0.2.54 + today's conjure flag; VM copy of src/tests and
    both artifact dirs, 3.14.7t; receipts written only in the copy). confirm_native_aliases, probe_semantics,
    graph_slice_probe, compact_alias_probe, native_compact_probe, native_compact_direct_probe, entry_claim_probe
    and native_admission_probe all pass; semantics_observations, native_alias_confirmation, results.json,
    native_compact(_direct)_results are identical to the 09-24 receipts apart from hashes/timings. So every
    current-behavior defect they recorded still exists (secondary-alias rule ignored 91->13, rule under a cut
    primary path leaks into the surviving alias, nested missing contract passes the SpellContract descriptor,
    supplied Space-scoped dependency still refused on the Conduit door, reused shared parent still rebuilds
    transient children in ordinary melds). native_lock_probe now fails in competing_publication_case because
    the root takes the slot guard instead of the store lock its instrumentation waits on (the inversion it
    documented is fixed; my 09-25 regression cases cover it).
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/confirm_native_aliases.py:20-55
  - artifacts/override_structural_discovery_20260924/native_lock_probe.py:207-260
  IMPACT: Codex's problem statement is still accurate against today's code; nothing shipped since 09-24
    resolved any of it. Their proofs remain valid evidence for the representation (sites + selector states).
  NEXT: Record the policy fork the architecture depends on, then report the synthesis to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:32:04Z
  TYPE: DECISION_REQUEST
  CLAIM: The architecture turns on how runtime reuse interacts with override rules. Three cases:
    P1 static cut (rule below a SUPPLIED dependency): inactive - joint alpha and my design agree (item 4 (a)).
    P2 a rule targets a shared site's own parameter and that site is already stored: today BOTH families raise
    MeldExecutionError ("Overrides were supplied for a spell instance that already exists"); joint alpha's
    conditional plan guards those candidates by `constructing`, so they silently become inactive (a behavior
    change not listed in its contract - item 6 keeps only the ROOT refusal). P3 a rule below a reused parent
    reaches a shared descendant another live path still builds: joint alpha = inactive (operand depends on this
    call's reuse outcomes, which forces the settled-claim prelude); alternative = active (operand depends only
    on the key shape; slot guards + recheck suffice, warm hits stay lock-free). Equality: keep item 5 (c).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2717-2749
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1985-2025
  - artifacts/override_occurrence_discovery_20260924/compact_alias_plan.py:230-261
  - artifacts/override_occurrence_discovery_20260924/compact_claim_prelude.py:40-122
  IMPACT: P3 decides whether a new claim protocol is needed at all; P2 decides whether the existing
    targeted-reuse refusal survives. Item 4 (a) was recorded "without objection" and did not separate them.
  NEXT: Owner discussion of P2/P3 with the synthesis; no strategy is final before that.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T10:40:10Z
  TYPE: DECISION
  CLAIM: Owner direction (chat): structural solution, not a quick fix; the common override is a plain reference
    passed to the ROOT object's constructor parameters, so the design biases toward that and treats nested
    paths, broadcast/unique selectors and aliased shared descendants as outliers. melder_0's reading, to confirm
    with the owner: P2 keep today's error (a rule targeting an already-stored shared object raises); P3 operands
    depend only on the key shape (a rule below a reused parent stays active for the shared object it reaches),
    so no claim protocol - outliers must not impose locks on the common path. Outliers use the same graph and
    lowering with correct deterministic semantics; they are not tuned first. Item 5 (c) equality stays.
  EVIDENCE: tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md (DECISION_REQUEST 10:32:04Z)
  IMPACT: The root-input shape becomes the design center: static cuts at root sockets, one prepared plan per
    root key set, direct emitted calls, literal-key reads; the selector/alias machinery is secondary.
  NEXT: Confirm the outlier interpretation with the owner, then write the structural strategy (design v2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:43:37Z
  TYPE: FACT
  CLAIM: Why supplied dependencies are still constructed, from current source and a fresh capture (0.2.54,
    3.14t, capture_codegen.py re-run in the VM copy). Shallow Root(a, b) with override {"a": obj}: the
    generated override executor builds A (step 0) and B (step 1) unconditionally, then for the root compares
    `single_override_socket_2.param_name != 'a'` at RUNTIME to decide whether to use A or the override, so A is
    built and discarded. Cause: (1) Phase 10 produces one fixed step list per root (every instance, providers
    first) shared by all shapes; (2) the override emitter writes "one direct step-resolution block per metadata
    row" - it never drops a row; (3) the finalizer reduces the key-set's targets to per-step COUNTS before
    emission (build_overrides_codegen_creation_step_target_counts_from_rows), so the emitted code cannot know
    which parameter is supplied, cannot hard-wire it, and cannot prune the dependency's block. The key set is
    known when the executor is compiled (it is cached per socket shape), so this is a codegen defect, not a
    missing runtime capability. Keys are validated (parse + match count) during per-call targeting; supplied
    VALUES are never checked - they go straight into kwargs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:678-828
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:269-335
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:758-860
  - artifacts/override_compiler_investigation_20260924/002_shallow_root_one_reused.py:1-110
  IMPACT: The structural fix is at compile time per key set: the plan must know which sockets are supplied
    and drop their dependency blocks (unless another edge needs them). No runtime check is needed for that.
  NEXT: Explain to the owner; propose key-name validation once per key set and no value validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T10:47:11Z
  TYPE: DECISION
  CLAIM: Owner: overrides favor speed over correctness - a supplied object is trusted as-is (no type or shape
    check; a "potato" passed where a "tomato" is expected fails wherever the user's code fails). This matches
    current value handling and is a hard design constraint: no per-call validation of supplied values, and no
    readiness/descriptor checks on supplied edges. Key-name checking (typos, unknown paths) is a separate
    question; melder_0 proposes it once per key set at plan compile, zero per-call cost.
  EVIDENCE: tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md (FACT 10:43:37Z)
  IMPACT: The per-call override path reduces to: find the compiled plan for the key set, run it. Everything
    else (cuts, operand placement, key checks) is compile-time per key set.
  NEXT: Write design v2 (root-input centered, static operands, per-key-set plans, one lowering) for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:53:16Z
  TYPE: FACT
  CLAIM: Re-onboarded after compaction; certified melder_0. Mailbox F0-3 consumed (fable_0, NOTICE, no ACK):
    owner-approved emission gate (option B) landed - `Spellbook._emit_spell_cache` stages nothing and returns
    False when either `build_package` returns None; both builders now return `Optional[Dict]`; three pure
    helpers on `CodegenCreationSchemaHelpers`. (Message deleted before this copy was written; content is
    reproduced here in full.)
  EVIDENCE: tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md
  IMPACT: Design v2's caching section must build on the gated emission path: a per-key-set plan that holds
    non-replayable payloads must not be emitted to the .melc, and any override implementation touching
    `_emit_spell_cache` rebases on fable_0's hunk.
  NEXT: Record the Phase-9 physical-graph reads.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T10:53:16Z
  TYPE: FACT
  CLAIM: Phase 9 already holds the compact physical graph design v2 needs, keyed exactly as a root-input plan
    wants. (1) Instances: a shared existence gets one key (spell_id, None) with a canonical occurrence (min by
    (spell_id, path)); many gets one key per occurrence path. (2) Injection: per instance key, one
    SpellInjectionParamSource per parameter - kind dependency (dependency_keys already mapped to instance
    keys, override_key = param name, is_collection from Phase-3 topology), unresolved_input / override_required
    (no dependency keys, override_key = param name, position and parameter_kind kept), contract payloads
    merged. A shared instance takes its edges from the canonical occurrence only. (3) Override targeting is
    the path-expanded part: it iterates Phase-5 root_blueprint.socket_refs (one ref per logical path per
    socket), keys each by its formatted path (specificity 3), and maps both "**name" (1) and "*name" (2) to
    every ref with that name, so UNIQUE and BROADCAST share one target tuple and the unique-count check is
    left to call time.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:131-215
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:119-301
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:43-123
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_override_targeting_analysis.py:6-142
  IMPACT: A root key "a" resolves to (root_instance_key, "a") in injection_shape with no path machinery, and
    its dependency_keys are the cut candidates. Nested/broadcast/unique selectors can be resolved by walking
    named edges over the same rows; the logical-path targeting section is only needed by today's runtime
    targeting and is the conjure-time cost to retire.
  NEXT: Read the runtime targeting parser (bare-key meaning, path format) and the Phase-10 plan builders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:54:48Z
  TYPE: FACT
  CLAIM: The override call chain today, end to end (many_only; read in full). ConduitMeld.meld normalizes the
    payload (dict as-is, list/tuple -> {"__args__": [...]}, so override=() is a non-None payload), then calls
    creation_context._overrides_executor(meld, map)[0] on the no-hooks lane; CreationContext only adds the
    dynamic-mode gate ticket. The finalize step's execute_with_overrides closure splits "__args__" (root
    positional values), runs targeting, then looks up an executor by (plan_signature, socket_shape,
    root_positional_arity) with a one-slot last-shape cell compared by tuple IDENTITY. Targeting parses each
    raw key with TargetSpec.parse: "**n" broadcast, "*n" unique, anything else a PATH of param names from
    the root, so a bare "a" is the root parameter a and "a>b" is param b of a's provider. Unknown PATH keys,
    zero/multiple UNIQUE matches and zero BROADCAST matches raise RuntimeError, wrapped in
    MeldExecutionError("Failed to apply overrides."). Equal-rank conflicts compare values with `!=`.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:259-578
  - src/melder/aether/conduit/meld/meld.py:1506-1575
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:238-309
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:243-560
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/artifacts/spell_override_targeting_codegen_creation.py:210-427
  - src/melder/aether/spellbook/spell_compiler/dag/target_spec.py:66-129
  IMPACT: The public contract design v2 must preserve is small: the payload forms, the three key grammars
    (bare/`>` path from the root, `*`, `**`), PATH > UNIQUE > BROADCAST, the three not-found errors and the
    equal-rank conflict. All of it is a function of the KEY SET plus value equality for conflicts, so it can
    be decided once per key set; only the equal-rank `!=` check needs the values (item 5 (c)).
  NEXT: Read the Phase-10 plan data (many_only plan, generalized lane plan) and family selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:58:17Z
  TYPE: MEASURE
  CLAIM: Captured today's emitted executors (0.2.54 + today's src, 3.14.7t, VM copy, caching off; new probe
    wraps both compile seams - many_only/solo use executor_code_cache, generalized uses executor_factory_cache).
    (1) The NORMAL many-only lowering is already the target shape: `v0 = t0(); v1 = t1(); v2 = t2(v0, v1)`,
    positional, no dicts. (2) The many-only OVERRIDE executor for {"a"} is 95 lines: builds A and B, then
    `if single_override_socket_2.param_name != 'a'` at run time, kwargs dict, instance_results dict, KeyError
    guards. (3) Generalized normal: shared site is inline hit + guarded miss, but its many child X is built
    BEFORE the hit check, so a warm meld builds X and discards it. (4) Constructor counts: many_shallow {"a"}
    builds A anyway; gen_mixed {"s"} builds X (S's only child) with S supplied; {"a"} builds A; gen_diamond
    {"l"} builds L; "l>s" on a stored S reuses S for R and passes the value to L.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/codegen_capture_v2.py:1-200
  - artifacts/melder_override_design_20260926/capture_v2_0254_314t/000_many_shallow_normal.py:1-17
  - artifacts/melder_override_design_20260926/capture_v2_0254_314t/002_many_shallow_override_a.py:1-95
  - artifacts/melder_override_design_20260926/capture_v2_0254_314t/003_gen_mixed_normal_cold.py:1-53
  - artifacts/melder_override_design_20260926/capture_v2_0254_314t/005_gen_mixed_override_s.py:1-150
  - artifacts/melder_override_design_20260926/capture_v2_0254_314t/capture.json
  IMPACT: Design v2 does not need a new lowering style: an override plan is the normal lowering run over a
    pruned step list with literal operands (`t2(ov["a"], v1)`), plus consumer-first placement of many
    children under shared miss branches (fixes the ordinary X waste too).
  NEXT: Read caching (creation cache/manifests) for how override executors persist, then write design_v2.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T11:00:39Z
  TYPE: FACT
  CLAIM: Three facts the design depends on. (1) Persistence: the .melc manifest (package v2) stores the
    override lane as plan_rows, plan_signature, empty_shape_key and the PATH-EXPANDED targets_by_spec plus
    specificity_by_spec; per-shape override executors are never persisted - they are compiled in-process at
    first meld and held in closure dicts. fable_0's gate returns None for non-replayable contract payloads.
    Cache generation is 11. (2) P2 precisely: `_raise_override_on_existing_instance` raises when the stored
    site is the root and the payload is non-None ("root spell that already exists"), or when the stored site
    has targeted overrides ("spell instance that already exists"). (3) MEASURE: root positional overrides
    over DI-injected parameters fail today - Root(a: A, b: B) melded with (s,), [s] or {"__args__": (s,),
    "b": s} raises MeldExecutionError from TypeError "got multiple values for argument 'a'", because the
    executor passes `*args` plus the dependency kwargs for the same parameters.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py:1-146
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:1-137
  - src/melder/utilities/caching_system/caching_system.py:138-151
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2717-2751
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1587-1675
  - artifacts/melder_override_design_20260926/root_args_probe.py:1-32
  IMPACT: Design v2 changes the manifest's override section (drop targets_by_spec, add the selector index)
    under cache generation 12, keeps per-key-set executors in-process, keeps both P2 messages, and treats
    root `__args__` as supplying the first N positional parameters (a fix for a path that errors today).
  NEXT: Write artifacts/melder_override_design_20260926/design_v2.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:02:24Z
  TYPE: FACT
  CLAIM: The Phase-5 overlay emits one SocketRef per Phase-3 topology socket at every (node, path) it
    reaches, so EVERY constructor parameter is targetable, not only DI edges. Probe (3.14t): Root(a: A,
    timeout: int = 5, *, name: str = "x") accepts {"timeout": 9}, {"name": "y"}, {"*timeout": 9} and
    {"**name": "z"}; {"nosuch": 1} and {"a>nosuch": 1} raise MeldExecutionError("Failed to apply overrides.")
    wrapping "No sockets found for override path". Collection members share one path id under their socket
    (visited key is (target_id, socket_path_id)), and targeting stores one ref per path string, so a PATH
    through a collection keeps only the last member ref (UNKNOWN whether any test covers this).
    Other readers of socket_refs (located by search, not yet read): Phase-6 socket_ref_sanity_strategy,
    the Phase-8 occurrence analyzer (:435) and shared_compiler_executions (:156, :296).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:435-500
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:5-60
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:43-123
  - artifacts/melder_override_design_20260926/plain_param_probe.py:1-27
  IMPACT: The site graph's per-site parameter table must come from the Phase-3 topology sockets (all
    parameters, with position and kind), not from injection param_sources (DI kinds only). Retiring the
    Phase-5 overlay is a separate later step gated on those three readers.
  NEXT: Write design_v2.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:06:53Z
  TYPE: DECISION
  CLAIM: design_v2.md written (455 lines). Recommendation: a site graph per root built from Phase-9 rows
    (every constructor parameter from the Phase-3 topology, a name index, DP path counts; no path lists);
    one plan per override key set compiled on first use (parse, resolve, rank, static cuts, demand,
    unresolved inputs and P2 marks decided at compile; no value checks); one lowering for normal and
    override melds (only demanded sites, literal `ov["a"]` reads, shared sites as inline hit + out-of-line
    miss under the existing slot guards, children only inside the miss); per call `plans.get(tuple(ov))`.
    No claim protocol (P3). Cache generation 12. Build order S1 site graph + oracle -> S2 normal lane
    (parity gate) -> S3 key-set plans, retire ~8.1k lines of override emitters -> S4 unresolved inputs in
    the plan -> S5 retire the Phase-5 overlay -> S6 qualification, each behind a patch lane.
  EVIDENCE: artifacts/melder_override_design_20260926/design_v2.md:1-455
  IMPACT: Addresses all eight current defects in section 2 of the design with one mechanism; the
    behavior changes the owner must accept are listed as B1-B8.
  NEXT: Owner reviews design_v2.md and answers Q1-Q5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T11:06:53Z
  TYPE: DECISION_REQUEST
  CLAIM: Q1 confirm P2 (rule on a stored shared site keeps today's error) and P3 (operands fixed per key
    set; no claim protocol). Q2 confirm K1 (key names validated once per key set; no value checks).
    Q3 accept B2 (ordinary melds stop building children of stored shared objects; cold-build constructor
    order changes). Q4 accept B5 (root positional payloads over DI parameters work) and B7 (a PATH through
    a collection applies to every member). Q5 approve the build order and open the S1 patch lane.
  EVIDENCE: artifacts/melder_override_design_20260926/design_v2.md:447-455
  IMPACT: Q1-Q2 fix the semantics S1/S3 implement; Q3-Q4 are the user-visible changes; Q5 starts code work.
  NEXT: Owner answers Q1-Q5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:09:56Z
  TYPE: PLAN
  CLAIM: Owner asked whether design v2 was run. It was not: the evidence is captures and probes of CURRENT
    behavior plus prior partial results (Codex emission-only prototype: normal-style lowering with every
    constructor kept reached 41.8/53.3/41.6/95.3% of normal on shallow/wide/diamond/deep through public
    meld; wide all-root input still 7.377us public vs 1.260us executor, i.e. front-end cost). v2's
    throughput, pruning and nested-guard behavior are UNKNOWN until measured. Proposed prototype
    (artifact-only, VM copy, no src edits): E1 generate v2 plans from a live conjured root's plan steps
    and install the dispatcher in the context's override slot at run time; E2 throughput on the existing
    experiment graphs (normal / current override / v2 for one root key, all root keys, empty tuple;
    3.14t and GIL, 7 repeats); E3 constructor counts and result identity on the capture graphs and the
    epic examples; E4 threaded cold melds through nested shared misses (one construction per slot, no
    deadlock). Root keys and conduit-store shared sites first; outlier selectors after.
  EVIDENCE:
  - artifacts/override_emission_prototype_20260924/findings.md:8-30
  - artifacts/override_emission_prototype_20260924/findings.md:95-106
  - artifacts/melder_override_design_20260926/design_v2.md:420-431
  IMPACT: Q1-Q5 can be answered with measured behavior instead of targets.
  NEXT: Owner go-ahead for the E1-E4 prototype.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:23:09Z
  TYPE: FACT
  CLAIM: E1 built: v2_prototype.py (564 lines, artifact-only) builds the site graph from a live conjured
    root (Phase-9 model + Phase-10 steps), compiles one plan per key set (PATH walk, `*` via DP path
    counts, `**` via name index, root `__args__`, P1 cut fixpoint, P2 hit errors, E1 guard, static
    unresolved-input raise) and emits consumer-first code with out-of-line shared misses under the
    existing slot guards; SlotSwitch swaps the spell's CreationContext slots at run time. Scope: many and
    unique_per_conduit sites, many root. v2_experiment.py runs E2-E4 against today's executors.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/v2_prototype.py:1-564
  - artifacts/melder_override_design_20260926/v2_experiment.py:1-436
  IMPACT: design_v2's core claims can be measured through the public meld without touching src/.
  NEXT: Record E3/E2/E4 results.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T11:23:09Z
  TYPE: MEASURE
  CLAIM: E3 (40 calls, 7 graphs, today vs v2 in fresh worlds; identical on 3.14t and GIL): every difference
    is a predicted change. Supplied branches never built (epic_five 3-of-5 supplied: 6 -> 3 objects; tree4
    both halves: 15 -> 1); X no longer built under a stored S (B2); positional payloads work (B5); the
    Codex leak is gone ({"p": o, "p>d>x": v}: today builds P and gives q's D x=v; v2 does neither, B3);
    unresolved inputs raise before anything is built (B6); supplying Task with an unresolved input works
    (today builds Task anyway and fails). Unchanged: bad-key errors, UNIQUE "matched 2 sockets", P2 errors.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/prototype_results.md:31-61
  - artifacts/melder_override_design_20260926/prototype_results_0254/e3_314t.json
  - artifacts/melder_override_design_20260926/prototype_results_0254/e3_314gil.json
  IMPACT: B1-B7 are observed behavior now, not predictions; Q3/Q4 can be answered from these rows.
  NEXT: Record E2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T11:23:09Z
  TYPE: MEASURE
  CLAIM: E2 (public meld, 7-repeat medians, % of today's normal; 3.14t / GIL): root-key overrides 76-88%
    (one key) and 79-106% (all keys) on shallow/wide/diamond vs today's 9-25%; deep 8-level path 97/94%
    vs 23/22%; deep one root key 190/185%, both 5780/4998% (0.44/0.40 us vs 111/91 us); normal melds
    101-107% on small graphs, 136/138% with a stored shared child, but deep normal 98/95% (R5, cause
    UNKNOWN). Remaining small-graph gap (shallow 452 vs 334 ns) is outside the plan: the override door
    skips the fast door (~65 ns) and dispatch costs ~76 ns (plan direct 111 ns < normal plan 134 ns).
    `override=()` 54-67% on small graphs (normalization + arity wrapper). First-use compile: deep normal
    plan 8.45 ms, key-set plan 4.27 ms; small graphs under 0.2 ms.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/prototype_results.md:62-149
  - artifacts/melder_override_design_20260926/prototype_results_0254/e2_deep_314t.json
  - artifacts/melder_override_design_20260926/prototype_door_breakdown.py:1-36
  IMPACT: The structural design meets the epic's goal on these graphs; the rest of the gap is door and
    dispatch cost (an override fast door and (keys, arity) dispatch are follow-ups, not design changes).
  NEXT: Record E4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T11:23:09Z
  TYPE: MEASURE
  CLAIM: E4: 200 rounds x 8 threads per variant and build, fresh lesser conduit each round, P and Q shared
    with slow constructors, nested misses (Root -> P -> Q) racing Root2 (Q only) and cut calls ({"p"}):
    0 failures for today and v2 on 3.14t and GIL (no duplicate construction, one P/Q identity, no thread
    alive after 20 s). Median round 3.41 vs 3.35 ms (3.14t), 0.93 vs 1.04 ms (GIL). A spy run confirmed v2
    plans served the threads. Hold-time cost at scale (R2) is not measured.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/prototype_results.md:120-138
  - artifacts/melder_override_design_20260926/prototype_results_0254/e4_314t.json
  - artifacts/melder_override_design_20260926/prototype_e4_slot_check.py:1-22
  IMPACT: No evidence of deadlock or double construction from consumer-first nested guards; supports P3
    without a claim protocol for these shapes.
  NEXT: Owner reviews prototype_results.md with design_v2.md and answers Q1-Q5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
State (2026-09-26T11:23:09Z): in review. design_v2.md is the current proposal (design.md superseded from "The design"
onward); prototype_results.md holds the E1-E4 measurements of an artifact-only prototype
(v2_prototype.py, v2_experiment.py) run through the public meld in the VM copy on 3.14t and GIL.
Results: supplied branches never built; root-key overrides 76-106% of normal on small graphs (today 9-25%);
deep supplied subtrees faster than normal; normal melds equal or faster except deep (-2 to -5%, R5); no
threading failures in 200x8 rounds. Remaining small-graph gap is door/dispatch cost (follow-ups).
Open: Q1-Q5 (last DECISION_REQUEST). Next on approval: open the S1 patch lane.
Validation: probes and prototype only; no production code changed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
