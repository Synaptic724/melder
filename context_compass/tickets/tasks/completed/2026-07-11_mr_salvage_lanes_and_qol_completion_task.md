# Task: MR iteration 9 - salvage lanes (lane types, surgical synthesis) + QoL completion (discoverability, test debt)

## Metadata
- Task ID: TASK-2026-07-11-mr-salvage-lanes-and-qol-completion
- Story: successor lane to the closed foresight kit (owner directive
  2026-07-11: "do the big lanes go upgrade shit and add tests too don't
  slack")
- Status: done (slices 1-4 owner-run green; slice 5 recomposition ruling PARKED with owner; closed 2026-07-11T23:20:16Z)
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T19:58:00Z
- Updated: 2026-07-11T19:58:00Z

## Objective
Finish what the foresight lane meant, then execute the two buildable salvage
directions from philosophy V3 Open Directions:

1. DISCOVERABILITY (correcting my own precedent call): the research family is
   invisible to `list_supported_command_methods` - an agent asking a room
   "what can you do" never learns the 18 research commands exist. Add the
   full family to both presentation tuples, split by room law; update every
   inventory test.
2. TEST DEBT: research_preview + frame_name (the composed validate_codegen
   verdict lane) and ViewSpell.describe_spell_source get real tests.
3. LANE TYPE CLASSIFICATION (salvaged May lane): optional enum vocabulary
   (development/experiment/production/test) on lanes; configuration toggle
   `lane_type_enforcement` (default False); when ON, a type-mixing join
   requires force=True (teach-grade refusal naming both types). Type rides
   describe/from_payload (back-compat: absent key defaults - `development`
   for the default lane, `experiment` otherwise), journal lane_created
   metadata, residency/impact join rows, and the room create_lane command.
4. SURGICAL SYNTHESIS (salvaged May lane): the missing verb over the shipped
   diff/report half. New `StructuralSynthesizer` (AST line-splice compose:
   pick named top-level functions/classes from a donor version, replace or
   append into the base version's root module source). Root verb
   `synthesize_candidate(base_spell_id, donor_spell_id, take_functions=,
   take_classes=, stage_ancestry=)` returns composed source + per-selection
   provenance + parents + a full preview_candidate payload. The MINT half
   rides a NEW ambient seam patterned exactly on campaigns:
   `stage_ancestry(parents)` / `clear_staged_ancestry()` / `staged_ancestry`
   - the next world entry (bind auto-record) consumes the staged parents
   ONE-SHOT and mints the multi-parent node (`record_world_entry` gains
   parent_spell_ids end to end; validation mirrors register_spell).
   Codegen-room commands: research_synthesize, research_stage_ancestry,
   research_clear_staged_ancestry (code-producing + ambient mutation =
   codegen-only by the exposure law).
5. RUNTIME RECOMPOSITION: DESIGN NOTE + DECISION_REQUEST ONLY (see Notes).
   It is the first verb that would break the read-only law (a selected
   future becomes live structure beyond notch); implementing it without an
   owner ruling on the mechanism would violate this program's own gates.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-11 ("do the big lanes... add tests
  too"); salvage scope pre-approved by the archived-lane ruling ("turn them
  in unless we can learn something from them").
- EXECUTION_BOUNDARY: src/melder/mutation_research/** (lane/set/config/root
  + NEW synthesis package) + command_system/{codegen,capability}
  presentation tuples + room commands + matching tests (incl. inventory
  tests in tests/unit/melder/aether/test_nexus.py and the capability JSON
  testbench if impacted). NO crystallizer edits. NO execute/bind paths
  (recomposition stays a design note).
- DEPENDENCIES: shipped foresight kit (preview/diff_materials); campaign
  ambient-context precedent; register_spell parent_spell_ids (already
  public); config reload backfill lane (new keys hydrate safely).
- EXIT_GATE: harness green on all slices; owner-run 3.14t; C-docs + graph
  synced (synthesis adds nodes/edges - append on the 529/990 baseline);
  ticket/boards synced; recomposition DECISION_REQUEST answered or parked
  by owner.
- FAILURE_ESCALATION: DECISION_REQUEST on recomposition mechanism;
  CONFLICT if enforcement or synthesis would require touching
  execute/bind paths.

## Applicable Anti-Patterns
- [ ] No execute/bind/record paths beyond the sanctioned ambient-ancestry
      consumption at the EXISTING world-entry seam.
- [ ] No constructing hidden roots from reads.
- [ ] Lane-type enforcement must never break existing payload hydration
      (absent key = safe default, never an error).
- [ ] Synthesis parse failures answer honestly, never raise.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.
- Append-only; promote UNKNOWN to FACT only with evidence.

## Notes
- DATETIME: 2026-07-11T19:58:00Z
  TYPE: PLAN
  CLAIM: Substrate read complete before build. FACTS: register_spell already
    validates + records parent_spell_ids (multi-parent = codegen-workshop
    composition, ITS OWN DOCSTRING) but record_world_entry (the bind
    auto-record seam) hardcodes parentless nodes + `"parent_spell_ids": []`
    journal metadata - the mint half of May's surgical flow has no path from
    the runtime seam; ambient campaign context (set/clear/active_campaign ->
    effective_campaign at both root seams) is the exact pattern staged
    ancestry copies. Lane payloads round-trip via describe/from_payload with
    permissive .get() reads - additive lane_type is hydration-safe; config
    load_recorded_dictionary backfills missing registry keys by contract -
    lane_type_enforcement is reload-safe. Join divergence law already
    refuses-unless-forced - type enforcement composes onto the same
    force=True escape hatch. Build order: config key -> lane enum ->
    set (create_lane type, join gate, record_world_entry parents,
    enforcement setter) -> root (propagation, staged ancestry, synthesize_
    candidate) -> synthesizer module -> room commands + presentation tuples
    -> inventory test fixes -> new tests -> docs/graph.
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:549-801,974-1099
  - src/melder/mutation_research/research_set/research_lane.py:11-27,502-581
  - src/melder/mutation_research/mutation_configuration.py:49-51,280-352
  - src/melder/mutation_research/mutation_research.py:602-754
  IMPACT: Everything additive; the only runtime-seam change is optional
    parent consumption at record_world_entry.
  NEXT: implement in the stated order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T19:58:00Z
  TYPE: DECISION_REQUEST (runtime recomposition - owner ruling needed)
  CLAIM: Recomposition = "recompose a live object onto a selected candidate
    future's structural shape" (May end-state; everything beneath it now
    exists: records, custody, diff, notch, synthesis). It is deliberately
    NOT implemented in this lane because it breaks the foresight read-only
    law and its mechanism needs an owner ruling. OPTIONS: (A) notch-adjacent
    - recomposition IS a bind of the candidate + notch to it (no new
    machinery; "recompose" becomes a guided codegen->bind->notch macro
    command; live instances migrate at next meld); (B) in-place structural
    swap - live instances get their class/module surface swapped to the
    candidate shape under a transaction (real new machinery: instance
    migration, mediator embargo, rollback story; highest power, highest
    risk); (C) parked - the macro flow in (A) is already achievable
    manually; write the runbook, build nothing. RECOMMENDATION: (A) first
    (cheap, rides proven seams, gives the verb a home), (B) only if live
    long-lived instances that cannot re-meld become a proven need.
  EVIDENCE: artifacts/2026-07-11_mutation_research_philosophy_v3.md:128-132
  IMPACT: Blocks only slice 5; slices 1-4 proceed regardless.
  NEXT: owner answers A/B/C (or defers).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T20:25:00Z
  TYPE: IMPLEMENTATION
  CLAIM: Slices 1-4 SHIPPED; slice 5 awaits the owner's A/B/C ruling.
    (1) DISCOVERABILITY: full research family added to BOTH presentation
    tuples (codegen 21, capability 10, grouped + commented); the one
    exact-equality inventory test (test_nexus.py
    test_codegen_command_system_lists_selected_runtime_helpers_only)
    extended to the 44-name tuple; every other inventory consumer is
    membership-only (capability JSON testbench verified membership-only);
    static rooms inherit nothing (all three systems extend CommandSystem
    directly - grep-proven). (2) TEST DEBT: research_preview+frame_name
    composed-validation lane asserted in the room loop (real
    validate_codegen: accepted verdict rides preview["validation"]);
    describe_spell_source covered by NEW
    tests/unit/melder/aether/test_view_spell_research_reads.py (both arms:
    honest mutation_research_not_active + live peek w/ module narrowing,
    class-level identity stub because ViewSpell is slotted).
    (3) LANE TYPES: LaneType enum (development/experiment/production/test)
    on ResearchLane (freeform default experiment; default lane development;
    describe/from_payload round-trip with pre-vocabulary back-compat by the
    same name rule); create_lane(lane_type=) through set + codegen room;
    lane_created journal metadata; history/residency_view/_residency_join
    rows all carry lane_type; config key lane_type_enforcement (default
    False, with_lane_type_enforcement builder verb, reload-lane
    backfill-safe) propagated by root at activate/hydrate/create_set via
    set_lane_type_enforcement; join gate fires BEFORE the divergence check,
    force=True supersedes, teach-grade error names both types.
    (4) SYNTHESIS: NEW src/melder/mutation_research/synthesis/
    structural_synthesizer.py (Cleanable, AST line-splice, decorators
    travel, replacements descending-span, additions tail-appended, unknown
    selections loud w/ available parts named, parse errors honest per
    side - VERIFIED LIVE in sandbox with a stubbed Cleanable: replace,
    add+replace w/ decorator, loud, honest all green); root
    synthesize_candidate (source_view-resolved texts, text_unavailable
    honest arm, full preview against base, parents reported,
    stage_ancestry=True arms the mint); ambient staged-ancestry seam
    (stage/clear/staged_ancestry; record_world_entry consumes ONE-SHOT
    under the root lock, re-stages on rediscovery); set.record_world_entry
    gains parent_spell_ids w/ register_spell's residence validation +
    journal metadata; rooms: research_synthesize/research_stage_ancestry/
    research_clear_staged_ancestry codegen-only. TESTS (WRITTEN; only new
    standalone files py_compile-checked - grown files ride owner-run):
    NEW test_structural_synthesizer.py (6), NEW test_lane_types.py (5),
    foresight file +4 (one-shot mint incl. rediscovery re-stage,
    synthesize compose+preview+stage, honest/loud arms, config
    propagation), NEW test_view_spell_research_reads.py (2), room
    integration: split test +3 codegen-only names + tuple-advertisement
    assert, foresight loop +lane_type row +validated-preview lane, NEW
    test_codegen_room_synthesis_loop (typed lane, compose via room,
    one-shot mint proven through research_history, restage/clear).
    DOCS+GRAPH: both C-docs synced (21-command family, discoverability
    law, lane-type + synthesis bullets, Key Files); both graphs
    529/990 -> 530/992 (StructuralSynthesizer node + MR owns/creates
    edges, MR/ResearchLane roles + responsibilities, codegen-borrows why;
    baseline guarded by assert before edit; file-tool-verified 7 hits per
    graph).
  EVIDENCE:
  - src/melder/mutation_research/synthesis/structural_synthesizer.py (new)
  - src/melder/mutation_research/mutation_research.py (staged ancestry + synthesize_candidate + propagation)
  - src/melder/mutation_research/research_set/{research_lane,research_set}.py
  - src/melder/mutation_research/mutation_configuration.py
  - src/melder/nexus/rift/command_system/{codegen,capability}_command_system.py
  - tests/... (files named above)
  IMPACT: The May surgical flow is complete end to end (compose -> preview
    -> execute -> multi-parent mint), lanes carry policy vocabulary with
    opt-in join enforcement, and the whole research surface is
    discoverable from inside a room.
  NEXT: owner-run 3.14t; owner ruling on the recomposition DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T20:45:00Z
  TYPE: FIX
  CLAIM: First owner-run flagged the config-registry law meeting the new
    key: validate() requires EVERY available_properties key, and the
    component activation matrix builds its bag property-by-property (no
    with_defaults), so all 10 params died on missing lane_type_enforcement.
    Swept the FULL radius, not just the reported site - five consumers:
    (1) component matrix: now sets both keys AND alternates enforcement on
    its own axis (case_index % 3), asserting propagation to the owned set
    at activation - the failure became coverage; (2-4) reload suite: all
    three backfilled-list expectations updated (recorded-both -> empty
    backfill; empty-record -> BOTH keys backfilled sorted; refused-key case
    -> new key rides backfilled alongside); (5) builder handoff matrix: the
    odd explicit lane sets both keys - which exposed that the BUILDER had
    no lane-type verb at all, so MutationResearchConfigurationBuilder
    gained with_lane_type_enforcement (API parity, not just a test fix).
    Verified permissive consumers unaffected: MRCompositionStrategy
    preflight reads named keys and ignores extras (lane_type passes
    through), the JSON-contract test's handcrafted crystal payload never
    validates against the registry, restore_engine's reload lane rides the
    with_defaults backfill floor by design, and the twin-emission test
    asserts type only.
  EVIDENCE:
  - src/melder/mutation_research/mutation_configuration_builder.py (new verb)
  - tests/component/melder/mutation_research/test_mutation_research_root_component.py
  - tests/unit/melder/mutation_research/test_mutation_configuration_reload.py
  - tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py
  IMPACT: The all-keys-required law stands unweakened; every construction
    path in the tree now satisfies it; enforcement propagation gained
    component-level coverage for free.
  NEXT: owner re-run.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T20:55:00Z
  TYPE: FIX
  CLAIM: Second owner-run: 3 failures, 2 mine + 1 foreign. MINE: both
    test_view_spell_research_reads tests died BEFORE the verb body -
    ViewSpell's public verbs are auto-wrapped by view_action_hooks, and
    _entered_view_action demands a bound frame view
    ("ViewSpell is not bound to a frame view", view_spell.py:1725), so my
    detached ViewSpell(frame_view=None) harness was structurally wrong.
    Fix: the fixture now binds a MagicMock frame helper (MagicMock
    context-managers through the hook); assertions unchanged. LESSON: a
    slotted viewer verb cannot be exercised detached - the action hook is
    part of the public contract. FOREIGN: test_asset_crud_completion
    store_cached_item TypeError is melder_0's in-progress
    asset_crud_completion lane (test speaks profile-scoped store; impl is
    still (checkpoint_id, cached_item)) - mailbox NOTICE + alert line sent,
    not my boundary.
  EVIDENCE:
  - tests/unit/melder/aether/test_view_spell_research_reads.py (fixture)
  - mailbox_board.md NOTICE to melder_0 2026-07-11T20:55:00Z
  IMPACT: My surface is re-run-ready; the remaining --last-failed entry
    belongs to melder_0's lane and will persist until he lands his impl.
  NEXT: owner re-run (expect 2/3 green; the asset-CRUD one is melder_0's).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T23:20:16Z
  TYPE: STATE_TRANSITION
  CLAIM: in_progress -> DONE. Slices 1-4 completed on their own terms and
    owner-run green across multiple runs (discoverability + inventory
    tests; preview-validation + viewer test debt; lane TYPE vocabulary +
    enforcement end to end; surgical synthesis + staged-ancestry mint).
    Slice 5 (runtime recomposition) closes as PARKED BY OWNER: the
    DECISION_REQUEST (19:58 note: A notch-macro / B in-place swap / C
    park; recommendation A) remains the ONE open MR design decision -
    whoever picks it up reads that note first. Config-registry and
    viewer-harness run findings were fixed in-lane (notes 20:45/20:55);
    the notch-race failure was owner-ruled out of lane.
  EVIDENCE: owner confirmations 2026-07-11; note trail above.
  IMPACT: The salvage program is finished; recomposition is a clean
    future entry point, not a dangling thread.
  NEXT: none (recomposition on owner ruling only).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Successor to the closed foresight kit: make the research family discoverable,
pay the two test debts, ship lane TYPE vocabulary + enforcement and the
surgical-synthesis verb + ambient ancestry mint, and put runtime
recomposition in front of the owner as a design decision. Re-entry: this
ticket + board row.
