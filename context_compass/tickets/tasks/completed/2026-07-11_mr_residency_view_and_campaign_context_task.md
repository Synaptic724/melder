# Task: MR iteration 6 - residency view (query-time join) + ambient campaign context

- Completed: 2026-07-11T19:00:00Z
- Summary: residency_view (declared/runtime/custody join; verdicts
  active|parked|stored|declared_only|unknown; total read) + ambient campaign
  stamping landed; the owner-ruled spell_id vocabulary sweep executed
  package-wide incl. payload keys, coordinated with melder_0 (his preflight
  sync closed); the one sweep straggler (residency test regex) fixed. Closed
  on owner directive after owner-run 3.14t green passes.

## Metadata
- Task ID: TASK-2026-07-11-mr-residency-view-and-campaign-context
- Story: successor lane to STORY-2026-07-11-build-mr-research-set-core (closed done)
- Status: done
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T15:45:00Z
- Updated: 2026-07-11T19:00:00Z

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: owner closure directive 2026-07-11 ("close any tickets you
  properly managed") following owner-run 3.14t green passes (--last-failed
  triage left zero failures on this lane; remaining failures were melder_0's
  EPM work, since closed on his side).

## Objective
Build the two unbuilt promises from Philosophy V3: (1) the RESIDENCY VIEW - the
model says active/parked/stored is "a query-time join, never lane state", but no
verb performs that join; (2) AMBIENT CAMPAIGN CONTEXT - the runtime seams
auto-record with campaign=None, so multi-agent campaign stamping only works on
manual declarations today.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-11 ("keep iterating on mutation_0 on MR")
  immediately after the build story closed owner-accepted.
- EXECUTION_BOUNDARY: src/melder/mutation_research/** + matching tests. Runtime
  truth is READ through existing public/idiomatic surfaces
  (AethericFrame.find_index_for_spell, SpellIndex.selected_spell_id,
  Crystallizer.get_spell_crystal); no spellbook/crystallizer edits.
- DEPENDENCIES: none (both features ride landed seams).
- EXIT_GATE: sandbox harness green + owner-run 3.14t green; ticket/board synced.
- FAILURE_ESCALATION: DECISION_REQUEST on any residency-semantics ambiguity.

## Design
- residency_view(spell_sha, set_name="default") on the root:
  - declared side from the set (residence + lane name/state);
  - runtime side by scanning frames: find_index_for_spell(sha) -> found and
    selected_spell_id == sha -> "active"; found and not selected -> "parked";
  - custody probe via get_spell_crystal (KeyError -> absent; inactive/cleaned
    crystallizer -> honest None "unavailable", never a raise on a read);
  - runtime rollup: active | parked | stored (custody only) | declared_only |
    unknown. Total function - no input raises except empty sha.
- Ambient campaign: root slot `_active_campaign` + set_active_campaign /
  clear_active_campaign / active_campaign; the root facades
  (record_world_entry / record_promotion - i.e. every runtime auto-record)
  stamp it when no explicit campaign is given. Set-level verbs keep explicit
  campaign args (the set never reaches up to the root).

## Validation
- Sandbox: research_set suite + typed harnesses for the new root verbs.
- Owner-run 3.14t: tests/unit/melder/mutation_research (+ integration file
  gains one residency case).

## Notes
- DATETIME: 2026-07-11T15:45:00Z
  TYPE: PLAN
  CLAIM: Join sources verified at source: AethericFrame._selected_spell_registry
    is a live per-conduit view of the spellbook's _spell_ids (active + staged),
    find_index_for_spell resolves the owning SpellIndex, and
    selected_spell_id distinguishes active from parked
    (aetheric_frame.py:689-742). Custody presence rides the existing
    get_spell_crystal facade.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:689-742
  IMPACT: No new runtime surfaces needed; the view composes existing reads.
  NEXT: implement root verbs + tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T15:49:50Z
  TYPE: FACT
  CLAIM: BOTH FEATURES LANDED. (1) residency_view(spell_sha, set_name) on the root:
    declared truth (residence + lane name/state), runtime truth (frame scan via
    find_index_for_spell; selected_spell_id == sha -> "active", member-not-selected ->
    "parked"), custody probe (get_spell_crystal; KeyError -> False, dead crystallizer ->
    honest None). Verdict rollup active|parked|stored|declared_only|unknown; total
    read (only empty sha refuses); dead-aether/dead-frame guards degrade cleanly.
    Helpers _locate_live_membership + _probe_custody keep methods in LOC bounds.
    (2) Ambient campaign: root _active_campaign slot + set/clear/active_campaign
    verbs; record_world_entry/record_promotion gained campaign params - explicit wins,
    else ambient stamp - so every runtime auto-record (bind/stage/notch) carries the
    campaign until cleared; catch-up declarations stamp too. Set-level verbs unchanged
    (explicit-only; the set never reaches up). Tests: 3 root unit (ambient precedence
    + full verdict matrix + custody-unavailable honesty) + 1 integration (real bind ->
    active w/ frame+index named). VERIFIED sandbox: behavioral harness green (ambient
    precedence incl. explicit override + empty-campaign refusal; all five verdicts;
    None-custody degradation; dead-aether guard). Root additions on real classes:
    Not run (3.14t owner run).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1-1
  - src/melder/aether/aetheric_frame/aetheric_frame.py:689-742
  IMPACT: The three-residencies story is now a callable verb, and campaign membership
    no longer depends on remembering to pass a stamp.
  NEXT: owner-run 3.14t (tests/unit/melder/mutation_research + integration file).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T15:55:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING - `spell_sha` is a vocabulary fork; the system word for the
    binding-signature SHA256 is `spell_id` (spell.spell_id, get_spell_crystal(spell_id),
    selected_spell_id). MR must conform. Full identity-vocabulary inventory of the MR
    package, with rename disposition:
    (1) spell_sha -> spell_id EVERYWHERE it means the spell identity: ResearchNode
        field/property/ctor, ResearchLane node maps + has_node/get_node/detach_nodes
        params, ResidenceRegistry claim/transfer/residence_of/is_resident params,
        ResearchSet register_spell/record_world_entry/history/walk payload fields,
        root record_world_entry/record_promotion/residency_view/diff material
        ("spell_sha" material key -> "spell_id").
    (2) PAYLOAD KEYS (persisted twin contract): "spell_sha" -> "spell_id",
        residence "lane_id_by_sha" -> "lane_id_by_spell_id" - REQUIRES melder_0 sync
        (his S3a preflight strategy validates residence/lane agreement over these
        keys; his reload stage itself is passthrough).
    (3) Journal endpoints from_sha/to_sha -> from_spell_id/to_spell_id, WITH one
        honesty fix: `restored` events currently carry a NETWORK SNAPSHOT address in
        to_sha - that moves to metadata["snapshot_address"] so the renamed fields
        never lie about their type.
    (4) Lane pointers tip_sha/anchor_sha -> tip_spell_id/anchor_spell_id;
        parent_shas -> parent_spell_ids.
    (5) module_sha: NOT a spell identity - it is the module-version source
        fingerprint; custody vocabulary is source_sha256/physical fingerprints ->
        rename to module_source_sha256 (pending owner taste).
    (6) NetworkVersioner snapshot_sha/network_snapshot_shas: content addresses of
        ORGANIZATION payloads, not spell identities - KEEP (no confusion with
        spell_id; they are literally shas of snapshots).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:1-1
  - src/melder/crystallizer/crystallizer.py:505-532
  IMPACT: Rename-only sweep across mutation_research/** + its tests + composition
    payload contract + graph/C-doc rows; melder_0 mailbox required for (2)/(3).
  NEXT: owner confirms sweep scope (recommend FULL conform incl. payload keys now,
    while the contract is one day old) -> execute in one pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T16:17:29Z
  TYPE: FACT
  CLAIM: VOCABULARY SWEEP EXECUTED (owner: "go ahead and fix all that"). Full
    conform per the 15:55Z inventory: spell_sha -> spell_id (package-wide incl.
    payload keys), parent_shas -> parent_spell_ids, module_sha ->
    module_source_sha256 (node/set files only - module_sha is a SUBSTRING of
    _module_shape in the structural strategy, caught pre-corruption), from/to_sha ->
    from/to_spell_id, tip/anchor_sha -> *_spell_id, node_shas -> node_spell_ids,
    entries_for_sha -> entries_for_spell_id, touches_sha -> touches_spell_id,
    lane_id_by_sha -> lane_id_by_spell_id, moved_shas -> moved_spell_ids,
    attach_at_sha/at_sha -> *_spell_id (ordered - overlap), left/right_sha ->
    *_spell_id (diff family), spellbook hook params conformed. HONESTY FIX riding
    along: restored journal events carry the network snapshot address in
    metadata["snapshot_address"] instead of the typed endpoint field.
    KEPT (owner-ruled): network snapshot addresses (shas of org payloads, not spell
    identities). Docs swept: philosophy V3 + src_components (arch had no tokens);
    graph: 10 MR nodes + edge text swept via backup-verified python pass, readable
    regenerated (520/966, MAX_LINE 220, JSON valid, zero stale tokens). VERIFIED:
    79/79 full suite harness-green on swept mirrors; residual grep clean (one
    test_diff_engine miss caught + fixed; right_shape/module_shape false positives
    confirmed untouched on disk). NO COMPAT SHIM: pre-sweep sealed checkpoints carry
    old keys; hydration reads new keys only (contract was hours old) - compat
    posture delegated to melder_0's preflight (his call, documented in his ticket).
    melder_0 handoff: tickets/tasks/2026-07-11_mr_spell_id_vocabulary_preflight_
    sync_task.md (full key map + compat note) + mailbox HANDOFF + alert.
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:1-1
  - tickets/tasks/2026-07-11_mr_spell_id_vocabulary_preflight_sync_task.md:1-1
  IMPACT: MR speaks the system's language; no vocabulary fork survives.
  NEXT: owner-run 3.14t (full MR trees; spellbook hooks re-touched) + melder_0's
    sync task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T16:27:30Z
  TYPE: FACT
  CLAIM: POST-SYNC VERIFICATION COMPLETE (melder_0 closed his sync task 02:10Z with
    the right compat call: new keys + one named pre_vocabulary_sweep_payload warning
    with agreement checks still running over legacy values). Tree-wide stale-token
    grep across src/melder + tests: MY sweep is CLEAN - remaining hits are (a)
    melder_0's intentional legacy-compat reads + compat-test fixtures (correct by
    design), (b) false-positive substrings (from_shared/_shape), and (c) ONE genuine
    flag: his brand-new impact_engine.py speaks spell_sha (blast_radius_of_spell
    param + payload keys) - his V3-horizon surface, zero external callers yet;
    NOTICE mailboxed 16:27:30Z so the fork does not re-grow on his side. No
    messages pending for me. Lane is run-ready.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:225-257
  IMPACT: Vocabulary conformance is complete and coordinated on every surface that
    speaks it; nothing gates the owner run.
  NEXT: owner-run 3.14t full tree (spellbook hooks + my sweep + melder_0's sync in
    one pass); then this task's closure walk.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T17:16:03Z
  TYPE: FACT
  CLAIM: OWNER --last-failed RUN TRIAGE (12 failures): ELEVEN are melder_0's EPM lane
    (ExternalPersistenceManagerConfiguration.validate() now raises upload_on_flush-
    without-handler on configs that attach only store/download/list handlers - his
    fresh generic-mesh/bridge work - plus reload_profile_from_external outcome
    "inserted" returning a list where the test compares >= int). ONE was MINE:
    test_root_residency_view_is_honest_without_custody still asserted
    pytest.raises(match="spell_sha") - the empty-input guard regex survived the sweep
    because the rotted-replica census under-reported and I trusted authorship memory
    over the miss. FIXED via replace_all on the root unit test; tree-wide grep now
    ZERO stale spell_sha tokens across every MR surface + spellbook. Lesson recorded:
    census on Edit-grown files is untrustworthy - always finish a sweep with a
    disk-truth grep per file, not memory.
  EVIDENCE:
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:1-1
  IMPACT: My side of the run is clean; the remaining 11 failures are melder_0's EPM
    validate/outcome regressions (owner is routing him).
  NEXT: owner rerun after melder_0's fix; then closure walk.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Walk (acceptance criteria vs delivered)
- residency_view: query-time join over declared truth (residence + lane),
  runtime truth (frame scan; selected vs member), custody probe (honest None on
  a dead crystallizer); five verdicts; total read (only empty id refuses). MET.
- Ambient campaign: root set/clear/active_campaign; every runtime auto-record
  stamps it; explicit stamps win; set-level verbs stay explicit-only. MET.
- Vocabulary conformance (owner ruling folded into this lane): spell_id
  everywhere incl. persisted payload keys; melder_0's preflight synced + closed;
  tree-wide zero stale tokens after the 17:16Z straggler fix. MET.
- Validation: sandbox harness green; owner-run 3.14t green passes (this lane's
  single --last-failed failure fixed; subsequent full-tree runs green). MET.
- Owner acceptance: explicit closure directive 2026-07-11 post-certification.

## Context / Handoff Summary
Successor lane after the build story closed: residency query-time join + ambient
campaign stamping, both MR-owned, both riding landed seams. LANDED 15:49Z; harness
green in sandbox. 15:55Z owner ruling executed 16:17Z: full spell_sha -> spell_id
conformance sweep (code/tests/docs/graph/payload keys) + melder_0 handoff ticket for
his preflight strategy (SYNCED + CLOSED by him 02:10Z; compat warning lane). Post-sync
verification 16:27Z: tree clean; one NOTICE to melder_0 re: impact_engine.py spell_sha
vocabulary (his fresh surface). 17:16Z: owner --last-failed triage - my ONE failure
(residency test match regex missed by the sweep) FIXED, zero stale tokens tree-wide;
remaining 11 = melder_0's EPM lane. Owner rerun pending.
