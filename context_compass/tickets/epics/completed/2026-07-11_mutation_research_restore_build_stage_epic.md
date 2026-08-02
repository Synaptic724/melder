# Epic: MutationResearch restore build stage (reload the MR from the record)

## Metadata
- Epic ID: EPIC-2026-07-11-mutation-research-restore-build-stage
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T14:28:53Z
- Updated: 2026-07-11T14:28:53Z
- Authored By: mutation_0 (owner-directed handoff spec; MR-side seams are DONE)

## Problem / Opportunity
The MR record is now real: the MutationResearchCrystal rides Phase-B composition
(research sets -> lanes -> full-object version records, residence partition, bounded
recent-transition window, snapshot addresses), re-emitted replace-on-emit after every
research mutation, and the MR root can rebuild itself from a recorded composition.
But `load_checkpoint` still treats MR as a REPORT stage: `_replay_mutation_research`
files two `*_recorded_not_restored_first_cut` shortfalls and builds nothing
(restore_engine.py:882-902). A checkpointed world that contained research unfolds
WITHOUT its research; the only recovery lane is MR's own virgin-registry hydration at
`activate()`, which reads the ACTIVE profile - correct for normal boots, blind to the
engine's folded truth during a restore. Owner directive 2026-07-11: "we gotta be able
to reload the MR" - convert the stage from report to BUILD, exactly like Nexus.

## MRP Alignment
One coherent slice per story: the config reload verb every other root already has;
the build stage on the existing canonical slot; the preflight/round-trip proof. No
story ships anything that needs rework to be trusted, and every unreplayable case
stays a named shortfall.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-11 ("make an epic properly for the melder_0
  agent... we gotta be able to reload the MR"); MR-side seams landed + owner-run
  green (build story evidence trail).
- EXECUTION_BOUNDARY: src/melder/crystallizer/crystal_loader_system/** +
  crystal_analysis/preflight/** + src/melder/mutation_research/mutation_configuration.py
  (the reload verb ONLY - the config is the reload-lane owner's convention surface)
  + matching tests. The MR root, research_set/, diff/, and the Phase-B twin are
  DONE - read them, call them, never edit them (mailbox mutation_0 on any seam
  mismatch instead).
- DEPENDENCIES: MR-side seams (all landed, owner-run green): MutationResearchCrystal
  Phase-B (`activated`, `configuration_payload`, `composition_payload`);
  `MutationResearch.load_recorded_composition(...)` (wholesale registry rebuild;
  guaranteed default set; re-emits after rebuild);
  `MutationResearch.activate(hydrate_from_record: bool)`;
  `MutationResearchConfiguration.describe_configuration_payload()`;
  `Crystallizer.describe_mutation_research_record()` (active-profile read).
- EXIT_GATE: full checkpoint round trip owner-run green - declare research ->
  checkpoint -> fresh boot -> load_checkpoint -> research present and continuable;
  the two first-cut shortfalls gone; report shows `mutation_research` built.
- FAILURE_ESCALATION: seam mismatch or payload-shape surprise -> mailbox NOTICE to
  mutation_0 with the folded payload evidence; never reshape MR payloads inside the
  engine.

## Stories (tranche order)
- [x] S1 (DONE 2026-07-11T20:30Z) MutationResearchConfiguration reload lane: `load_recorded_dictionary(...)`
      per the owner reload-lane law (recorded truth never defaults; per-key REPORTED
      backfill/reject outcome dict exactly like NexusConfiguration's; verb seals -
      freeze + activate - on return). Input is the twin's `configuration_payload`
      (value-coerced by `describe_configuration_payload()`; callables cannot appear).
      MR was excluded from the original reload-lane directive because it was a
      skeleton; that exclusion is now obsolete.
- [x] S2 (DONE 2026-07-11T20:30Z) build stage: `_replay_mutation_research` report -> BUILD on the existing
      canonical slot (Aether|Utility -> Crystallizer -> MR -> Nexus -> ...), mirroring
      `_replay_nexus` (restore_engine.py:904-962):
      - no recorded twin -> NO-OP (a world without research stays without it);
      - folded state "cleaned" -> honest shortfall, no rebuild (world sealed after
        its MR died);
      - else: S1 reload verb over `configuration_payload` (per-key shortfalls) ->
        root via the hosted accessor (`Aether()._get_mutation_research()`; the root
        is Aether-hosted, never free-constructed) -> `configure(...)` ->
        `activate(hydrate_from_record=False)` - MUST be False: the engine owns
        FOLDED truth and the fresh active profile is empty mid-replay; the root's
        own hydration lane is for normal boots only ->
        `load_recorded_composition(folded composition_payload)` - the root re-emits
        into the fresh profile on rebuild (re-recording covenant holds for free);
      - folded state "disabled" later-wins -> activate-then-deactivate (both acts
        are recorded history, Nexus precedent);
      - pre-Phase-B payloads (no/empty `composition_payload` key) -> config-only
        rebuild + honest `composition_not_recorded_pre_phase_b` shortfall;
      - `built_stack` push + `record_built("mutation_research")`; failure joins the
        all-or-nothing reverse teardown (root.cleanup()); DELETE both
        `*_recorded_not_restored_first_cut` shortfalls.
- [x] S3 (DONE 2026-07-11T21:20Z) admission + proof: (a) preflight strategy in the crystal_analysis/preflight
      family - MR composition consistency over the folded bundle (payload shape
      parses; per-set organization/residence agreement: every lane-held SHA resident,
      every residence points at a described lane; verdict warnings, blockers only on
      unparseable payload); (b) scope adjudication - conduit/frame-scope loads do NOT
      rebuild MR (world-scope root; reclassify to `expected_for_scope` exactly like
      frame_posture); (c) the round-trip integration test (declare -> lanes/attach ->
      checkpoint -> fresh boot via CrystallizerBootstrap -> research present, journal
      sequences continue without reuse, a later `activate()` hydration NO-OPs because
      the engine-restored registry is non-virgin).

## Goals / Non-goals
- Goals: a checkpointed world unfolds WITH its research; every unreplayable MR case
  is a named shortfall; MR behaves like every other build-stage root.
- Non-goals: editing MR internals (mutation_0's surface - seams only); formations
  carrying MR (world-scope only); the two OPEN OWNER DIALS below (mutation_0-side,
  additive payload changes if ruled - they do not gate this epic).

## Open Owner Dials (coordination, not blockers)
- Journal window: the twin carries a bounded recent-transition window (200/set);
  full history exists across the checkpoint SEQUENCE but not in one snapshot. If the
  owner rules "unbounded in twin", mutation_0 removes the bound - payload shape is
  unchanged (same keys), this epic is unaffected.
- Organization-snapshot ring: `network_snapshot_shas` lists addresses only; the
  undo-ring payloads are runtime-only today. If ruled in, mutation_0 adds them to
  the composition - additive key, this epic is unaffected.

## Acceptance Criteria
- Round trip owner-run green on 3.14t (S3c test): research declared pre-checkpoint is
  present, walkable, and continuable post-restore on a fresh boot.
- `describe_last_load` / restore report shows `mutation_research` under built stages;
  zero `first_cut` shortfalls remain; pre-Phase-B and cleaned-state cases report
  honestly.
- Conduit/frame-scope loads leave MR untouched with `expected_for_scope`
  adjudication.

## Risks / Mitigations
- Double-hydration fight (engine build vs root activation hydration) -> engine passes
  `hydrate_from_record=False`; root hydration only fires on VIRGIN registries, and an
  engine-restored registry is non-virgin - S3c asserts both.
- Emission-order surprise (rebuild re-emitting mid-replay) -> the Nexus precedent
  already re-records during replay by design; MR's `load_recorded_composition`
  emission lands in the fresh active profile identically.
- Payload drift between MR emits and engine folds -> the twin's `describe()` is the
  single shape contract; preflight strategy (S3a) catches drift as a verdict, and
  seam mismatches route to mutation_0 by mailbox, never engine-side reshaping.

## Decision Log
- 2026-07-11 owner: "we gotta be able to reload the MR" - report stage becomes build
  stage; epic authored by mutation_0 for melder_0 as the twin-over handoff.
- 2026-07-11 mutation_0 (recommendation adopted by owner direction): melder_0 owns
  this - restore-engine internals are his stage machine; MR exposed the seams and is
  done.

## Notes
- DATETIME: 2026-07-11T14:28:53Z
  TYPE: PLAN
  CLAIM: Epic authored from source evidence: the report-stage shortfalls
    (restore_engine.py:882-902), the Nexus build-stage precedent (904-962: reload
    verb -> public enable -> later-wins state replay -> built_stack), the fold slots
    (310-311, 654-657, 702), and the landed MR seams (root verbs + Phase-B twin +
    read facade). S1 is the only MR-package file touch (the config's reload verb,
    convention-owned by the reload-lane law).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:882-962
  - src/melder/crystallizer/crystals/mutation_research_crystal.py:40-77
  - src/melder/mutation_research/mutation_research.py:1-1
  IMPACT: melder_0 can execute without design work; every seam is named and landed.
  NEXT: melder_0 routes S1 when he picks up the lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T20:30:00Z
  TYPE: FACT
  CLAIM: S1 + S2 IMPLEMENTED per the handoff spec (patch
    mr_restore_build_stage_2026_07_11 authored FIRST). S1:
    MutationResearchConfiguration.load_recorded_dictionary - with_defaults
    backfill floor, recorded keys overwrite via set_property (single bool
    key, no coercion), {"rejected","backfilled"} outcome, SEALS via
    activate() (the config's emission factor re-records mid-replay per the
    Nexus covenant; also exactly what root activation requires -
    config.activated is its hard gate, source-verified
    mutation_research.py:357-360). S2: _replay_mutation_research is a
    BUILD stage - no twin=NO-OP; folded "cleaned"=shortfall
    (state names source-verified: RecordedUnitState
    enabled/disabled/cleaned, MR emits disabled from deactivate() at
    :445); reload verb w/ per-key shortfalls; root via the hosted
    accessor Aether()._get_mutation_research() (:1577);
    activate(configuration, hydrate_from_record=False); composition
    present -> load_recorded_composition, absent -> config-only +
    "composition_not_recorded_pre_phase_b"; "disabled" later-wins ->
    activate-then-deactivate; built_stack + record_built. BOTH first_cut
    shortfalls DELETED (grep-proven zero hits).
  EVIDENCE:
  - src/melder/mutation_research/mutation_configuration.py:280-352
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:883-965
  IMPACT: Checkpointed worlds now rebuild their research; S3 provides the
    admission view + the round-trip proof.
  TESTS: Not run (sandbox; replica rot on grown files - disk verified via
    file-tool). S3c round-trip + owner 3.14t run are the exit gate.
  NEXT: S3 - preflight MR-composition strategy, expected_for_scope
    adjudication, round-trip integration test; then unit tests for the
    reload verb + stage lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T21:20:00Z
  TYPE: FACT
  CLAIM: S3 IMPLEMENTED - epic code-complete. (a)
    MutationResearchCompositionStrategy (9th default preflight row,
    registered): blocker ONLY on unparseable shapes (composition/set/
    lanes/residence); warnings on organization/residence disagreement
    (lane-held sha unresident / lane mismatch / residence pointing at an
    undescribed lane); absent/empty composition = zero rows (the stage's
    pre-Phase-B shortfall owns that case). Composition shape
    source-verified: set={set_id,name,created_at,lanes:[lane],residence:
    {lane_id_by_sha}}, lane carries nodes:[{spell_sha,...}]. Engine
    _run_preflight bundle gains the mutation_research root (it never rode
    the bundle before). (b) LoadAdmission._adjudicate_for_scope
    reclassifies mutation_research_composition warnings to
    expected_for_scope on conduit/frame loads (frame_posture twin;
    world-scope root law). (c) round-trip integration test
    test_mutation_research_round_trips_through_checkpoints (declare lane
    + 2 spells -> create_checkpoint -> flush -> MR singleton reset +
    _fresh_boot -> reload_cached_checkpoint -> load_checkpoint -> built
    mutation_research==1, zero first_cut shortfalls, lanes/residence/walk
    present, post-restore register CONTINUES, later
    activate(hydrate_from_record=True) NO-OPs on the non-virgin
    registry). PLUS unit suites: 4-test reload-verb suite (overwrite/
    backfill/reject-both-lists semantics/frozen refusal) + 5-test
    strategy suite (clean/parse-blockers/3-warning drift matrix/default
    registration/scope adjudication).
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py:1-186
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:588-591
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:525-540
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:921-995
  IMPACT: Epic acceptance surface fully built: checkpointed worlds unfold
    WITH their research, admission adjudicates it, the round trip proves
    it. Exit gate = owner-run 3.14t green on the round trip + suites.
  TESTS: Not run (sandbox; replica rot on grown files - all edits
    disk-verified via file-tool sentinels; new files parsed clean).
  NEXT: owner run (covers this epic + S2 physical custody + the S1 lane
    in one sweep); on green: acceptance walks + closure + the batched
    patch-doc promotion/graph sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T21:50:00Z
  TYPE: FACT
  CLAIM: OWNER-DIRECTED TEST DEEPENING ("add tests too bro"): closed the
    coverage gaps the first pass left. (1) Engine MR-lane unit tests
    (pure windows, no runtime): no-twin NO-OP (no built row, no
    shortfall, first_cut vocabulary absent) + cleaned-world honest
    shortfall (test_crystal_loader_system.py:245-305). (2) Mediator
    LoadGate gating unit tests (test_transaction_mediator.py:335-460):
    gated bundle helper + holder-thread passthrough at begin_frame +
    foreign-root parking with resume-on-terminal-open + starved-root
    timeout naming the holding load. (3) S2 custody end-to-end
    integration: temp user module -> retention ON seal (crystal carries
    the text, asserted) -> file deleted + sys.modules evicted -> fresh
    boot -> load_checkpoint rebuilds through the synthetic lane with the
    named shortfall and the module import-resolvable again
    (test_crystallizer_restore_integration.py:995-1070). Also covers the
    epic's disabled-lane... NOT covered: the disabled later-wins lane
    still lacks a direct test (runtime-heavy deactivate-before-checkpoint
    variant); flagged as a follow-up row for the owner run's triage
    pass rather than claimed.
  EVIDENCE:
  - tests/unit/melder/crystallizer/crystal_loader_system/test_crystal_loader_system.py:245-305
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:335-460
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:995-1070
  TESTS: Not run (sandbox; disk verified via file-tool).
  NEXT: owner run.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T22:50:00Z
  TYPE: FACT
  CLAIM: OWNER RUN 1 TRIAGE (8 fails / 9702 passed) - all closed. (1)
    Round-trip blocker was MY strategy reading the set payload one level
    too shallow: describe_composition nests {organization, journal,
    network_snapshot_shas, network_versioner} - lanes/residence live
    INSIDE organization (source-verified research_set.py:1207-1239);
    strategy fixed + no-organization blocker lane added + test helper
    mirrors the real shape. (2) S2 retention integration test lacked
    `import sys`. (3) Pre-existing reload-lanes test taught the new
    retain_user_sources backfill row. (4) Drift-matrix expectation
    corrected to 4 rows (sha-moved contributes mismatch AND
    undescribed-lane). (5) Hydration test bundle taught the strategy's
    FIRST gate (owning spellbook must ride the bundle). (6) Cleaned-lane
    engine test taught the fold-honesty payload requirement for state
    kinds. (7) ENGINE HARDENING from the pre-existing report-stage test's
    failure: an ALREADY-ACTIVE MR root now deactivates before the stage
    reactivates from folded truth (configure refuses while active;
    live-world loads under the LoadGate make this real; both acts
    recorded - world-replacement semantics); that test REWRITTEN to the
    new cleaned-lane contract (old first_cut assertions retired with the
    stage). (8) test_campaign_view ordering flake = MR-internal
    nondeterminism -> NOTICE mailboxed to mutation_0 per the epic law
    (never reshape MR-side). ALSO consumed mutation_0's 15:22Z ruling:
    deactivate/disabled stays; disabled-lane test will document the
    bound-while-deactivated-restores-DECLARED nuance; network_versioner
    passes through untouched (strategy treats it as opaque).
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:1207-1239
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py:100-135
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:948-960
  TESTS: Not run post-triage (sandbox). Owner rerun requested - the 8
    should collapse; anything left is fresh evidence.
  NEXT: owner rerun; on green, closure walks for this epic + S2 custody.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T04:40:00Z
  TYPE: FACT
  CLAIM: CLOSED - owner runs GREEN (full tree + two --last-failed
    passes; the single remaining residency_view fail is mutation_0's
    own test, owner-routed to him). ACCEPTANCE WALK: (1) round trip
    owner-run green - research declared pre-checkpoint is present,
    walkable (spell_id vocabulary), and CONTINUABLE post-restore on a
    fresh boot (S3c test); disabled worlds restore deactivated with
    research intact (disabled-lane test, nuance documented); (2)
    restore report shows mutation_research under built stages; zero
    first_cut shortfalls anywhere (grep-proven); pre-Phase-B and
    cleaned states report honestly (unit lanes); (3) conduit/frame
    loads leave MR untouched with expected_for_scope adjudication
    (unit-proven). Vocabulary handoff executed same-day (spell_id sweep
    + compat warning lane). All coordination loops with mutation_0
    closed (mailbox consumed/deleted + closing NOTICE).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:921-1060
  IMPACT: MR is a build-stage root like every other; checkpointed
    worlds unfold WITH their research.
  NEXT: none (epic closed); promotion rides the batched pass.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Twin-over handoff: MR emits its full composition on every mutation and can rebuild
itself from a recorded payload; the restore engine still reports-not-restores MR.
Three stories make MR a build stage exactly like Nexus: the config reload verb, the
engine stage conversion (folded truth, hydrate_from_record=False, honest shortfalls
for pre-Phase-B/cleaned), and admission+round-trip proof. MR internals are mutation_0's
surface - consume seams, mailbox on mismatch. Two open owner dials (journal window,
snapshot-ring persistence) are additive and do not gate this epic.
