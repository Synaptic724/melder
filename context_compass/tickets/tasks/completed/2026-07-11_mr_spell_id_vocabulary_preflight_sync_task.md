# Task: MR spell_id vocabulary sync in the preflight strategy (+ round-trip test)

## Metadata
- Task ID: TASK-2026-07-11-mr-spell-id-vocabulary-preflight-sync
- Story: follow-through of EPIC-2026-07-11-mutation-research-restore-build-stage
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T16:17:29Z
- Updated: 2026-07-11T16:17:29Z
- Authored By: mutation_0 (owner-directed: MR conformed to system vocabulary)

## Objective
OWNER RULING 2026-07-11: `spell_sha` was an MR vocabulary fork - the system word for
the binding-signature SHA256 is `spell_id` (spell.spell_id, get_spell_crystal(spell_id),
selected_spell_id). mutation_0 executed the full conformance sweep on the MR package,
tests, docs, and graph. The MutationResearchCrystal COMPOSITION PAYLOAD KEYS changed
with it, and your S3a preflight strategy (MRCompositionStrategy) plus possibly your
round-trip test read the old keys. Sync them.

## Ticket Contract
- ENTRY_GATE: owner directive ("go ahead and fix all that ... and make a ticket for
  him"); MR-side sweep landed same hour.
- EXECUTION_BOUNDARY: crystal_analysis/preflight/** (the MR composition strategy) +
  your MR round-trip/disabled-lane tests. MR internals unchanged beyond the renames -
  no seam behavior moved.
- DEPENDENCIES: MR sweep landed (see key map below).
- EXIT_GATE: preflight strategy green over NEW-key payloads; owner-run 3.14t green.
- FAILURE_ESCALATION: any key I missed -> mailbox mutation_0 with the payload path.

## The Key Map (old -> new, everywhere in the composition payload)
- Node payloads: `"spell_sha"` -> `"spell_id"`; `"parent_shas"` ->
  `"parent_spell_ids"`; `"module_sha"` -> `"module_source_sha256"`.
- Lane payloads: `"tip_sha"` -> `"tip_spell_id"`; `"anchor_sha"` ->
  `"anchor_spell_id"`.
- Residence payload: `"lane_id_by_sha"` -> `"lane_id_by_spell_id"` (your
  organization/residence agreement check reads this).
- Journal entry payloads: `"from_sha"` -> `"from_spell_id"`; `"to_sha"` ->
  `"to_spell_id"`; join metadata `"moved_shas"` -> `"moved_spell_ids"`; register
  metadata `"module_sha"` -> `"module_source_sha256"`.
- HONESTY CHANGE riding along: `restored` journal events no longer carry the network
  snapshot address in the (now typed) to_spell_id field - it moved to
  `metadata["snapshot_address"]`. If anything of yours reads restored events, update.
- UNCHANGED: `"network_snapshot_shas"` + `"network_versioner"` (organization snapshot
  addresses are shas of snapshots, not spell identities - owner-ruled keep), set/lane
  organization keys, journal `entry_count`/`next_sequence`.
- COMPAT NOTE: pre-sweep recorded payloads (checkpoints sealed before 2026-07-11
  ~16:00Z) still carry OLD keys. MR-side `from_payload`/hydration reads NEW keys only
  (owner accepted: the contract was hours old; no dual-read shim). If your preflight
  should stay tolerant of old sealed checkpoints, treat old-key payloads as a named
  warning, not a crash - your call, your strategy.

## Validation
- Your 9-test preflight suite + round-trip integration against freshly-emitted
  payloads; owner-run 3.14t.

## Notes
- DATETIME: 2026-07-12T02:10:00Z
  TYPE: FACT
  CLAIM: SYNCED + CLOSED (melder_0). Strategy reads the NEW keys
    (spell_id / lane_id_by_spell_id) with detail texts conformed to the
    spell-id vocabulary; COMPAT CALL taken per the handoff's offer:
    old-key payloads produce ONE named "pre_vocabulary_sweep_payload"
    warning and the agreement checks still run over the legacy values
    (old sealed checkpoints preflight honestly instead of crashing).
    Tests: helper + assertions moved to new keys; NEW
    test_pre_sweep_payloads_warn_but_still_check; the MR round-trip
    test's walk read moved spell_sha -> spell_id. Mailbox message
    consumed + alert cleared.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py:118-186
  - tests/unit/melder/crystallizer/crystal_analysis/test_mutation_research_composition_strategy.py
  TESTS: Not run (sandbox). Rides the owner sweep.
  NEXT: none (closed).
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Vocabulary conformance follow-through: MR now speaks spell_id like the rest of the
system; the composition payload keys moved with it; your preflight strategy and MR
round-trip tests are the only non-MR readers of those keys.
