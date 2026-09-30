

# Task: Find out what the Aether record's missing spell-id regime does to a restored world

## Metadata
- Task ID: TASK-2026-09-30-investigate-aether-record-spell-id-regime
- Story: none; standalone investigation (read and probe; no tree edit without the owner's pick)
- Related: tickets/tasks/completed/2026-09-29_guard_melder_roots_for_host_collisions_task.md (FACT
  2026-09-29T23:55:15Z, where the gap was found)
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-30T15:55:22Z
- Updated: 2026-09-30T16:39:17Z

## Objective
Owner question (chat, 2026-09-30), about the follow-up the root-guards lane left open: "The Aether record doesn't
store the spell-id regime, so a world recorded with per-frame ids restores with process-wide ids. not sure what this
is go ahead and look into this please". Explain in plain terms what the spell-id regime is, what the Crystallizer's
Aether record carries, and what actually happens when a world recorded under per-frame spell ids is restored -
measured, not inferred - then say whether it matters and what a fix would look like.

## Ticket Contract
- ENTRY_GATE: this board row; the known starting FACT noted before any probe.
- EXECUTION_BOUNDARY: read-only in src/ (the regime's setting, sealing and reading in aether.py and
  aether_configuration.py, the spell-id path in bind.py and spellbook.py, the Crystallizer's Aether twin, restore
  stages 1-2); probes and logs under artifacts/aether_record_spell_id_regime_20260930/; runs in the VM mirror. No
  tree edit without the owner's pick.
- DEPENDENCIES: the root-guards lane (M1 sealed-regime guard, 0.2.8209), which this builds on.
- EXIT_GATE: what the regime is and where it is sealed and read (FACT with source ranges); what the record carries
  (FACT); what restoring a per-frame world does (MEASURE, probes in fresh processes); a DECISION_REQUEST with fix
  options; status review.
- FAILURE_ESCALATION: DECISION_REQUEST before any edit; BLOCKER if the VM cannot record and restore a world.

## Scope Boundaries
- In scope: the spell-id regime (AetherConfiguration.process_wide_unique_spell_ids), its recording and its restore;
  what it changes for spell ids, collisions and restore outcomes.
- Out of scope: other Aether policy fields; fixing anything before the owner picks.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-09-30T16:15:30Z) regime, record and restore read from source; four worlds recorded and
  restored in fresh processes; DECISION_REQUEST filed. Earlier: draft -> in_progress (2026-09-30T15:55:22Z, the
  owner's question).

## Steps / Checklist
- [x] Read how the regime is set, sealed and read (Aether, AetherConfiguration, bind and spell-id checks).
- [x] Read what the Crystallizer records for the Aether root and how restore replays it.
- [x] Probe: record a per-frame world (the same class bound in two frames), restore it in a fresh process.
- [x] Probe controls: a process-wide world; a restore into a live world that sealed its own regime first.
- [x] Explain it to the owner and file a DECISION_REQUEST with fix options.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed notes, probe scripts and results; a plain-language answer and fix options for the owner.

## Files / Paths Impacted
- None in the repository tree (investigation); artifacts only.

## Validation
- Not run.
- Recommended commands:
  - the probe commands recorded in the MEASURE notes

## Risks / Rollback Notes
- Read-only; nothing to roll back.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behaviour claim from a document or a search hit; read the code.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/aether_record_spell_id_regime_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the owner's turn-in of this ticket.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-30T15:55:22Z
  TYPE: FACT
  CLAIM: Starting point, recorded on 2026-09-29 in the root-guards lane from source: the Crystallizer's Aether
    twin carries only the logger half of AetherConfiguration (channel_logger_activation_enabled and two presence
    flags), and rebuilding a configuration from that record gives the default spell-id regime (process-wide). So
    a record never carries process_wide_unique_spell_ids. What that does to a restored world was not measured.
  EVIDENCE: tickets/tasks/completed/2026-09-29_guard_melder_roots_for_host_collisions_task.md:202-218
  IMPACT: If a per-frame world needs its regime to restore (the same class in two frames, say), restore may fail,
    change spell ids or merge what should stay apart; which one is UNKNOWN until read and probed.
  NEXT: Read the regime's setting, sealing and reading in aether.py and aether_configuration.py, then the spell-id
    path that consumes it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T15:59:35Z
  TYPE: FACT
  CLAIM: What the regime is, read from source. A spell_id is a SHA256 over the bind-time fingerprint with no frame
    in it, so the same class bound with the same parameters gets the same id in every frame.
    AetherConfiguration.process_wide_unique_spell_ids (default True) sets that id's scope. True: one id per
    process - once a second frame exists, bind's collision check and conjure's integrity preflight sweep every
    other frame too, so the same binding in a second frame is refused ("Spell ID collision" at bind, "Conjure
    refused" at conjure). False: one id per frame - the multi-tenant shape, where one class is bound
    independently in several isolated frames. The first frame born seals the regime from the installed
    configuration (frozen defaults when none is installed); since 0.2.8209 configure and activate refuse another
    regime while frames exist.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:320-355
  - src/melder/aether/aether.py:2480-2541
  - src/melder/aether/aether.py:2543-2605
  - src/melder/aether/aether.py:2719-2768
  - src/melder/aether/aether.py:1072-1119
  - src/melder/aether/spellbook/spellbook.py:5323-5338
  - src/melder/aether/spellbook/spellbook.py:2631-2721
  IMPACT: The regime decides whether the same binding may live in two frames at once, so a restore has to rebuild a
    world under the regime it was recorded under, or such a world cannot come back as it was.
  NEXT: Read what the record carries for the Aether root and how restore replays it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T15:59:35Z
  TYPE: FACT
  CLAIM: What the record carries and what restore does with it, read from source. The Aether root twin
    (AetherCrystal) is emitted by AetherConfiguration.activate, by the Crystallizer's activation catch-up (only
    when Aether is explicitly configured) and by the utility system's logger verbs; all three payloads hold only
    channel_logger_activation_enabled and two logger presence flags. from_recorded_payload builds a new
    configuration, whose constructor default regime is True, applies the logger flag and freezes it; the absent
    regime is not even listed as "missing". Restore stage 1 skips the record when the live Aether is already
    configured (shortfall live_aether_already_configured_recorded_payload_skipped); otherwise it activates the
    rebuilt configuration, so the first frame the restore births (stage 5) seals process-wide ids. Stage 6 rebuilds
    one book at a time - its active binds, its conjure, its staged binds - so book B binds after book A's conjure
    has registered A's ids.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:872-920
  - src/melder/aether/aether_configuration.py:421-485
  - src/melder/aether/aether_utility_system.py:204-256
  - src/melder/crystallizer/crystallizer.py:683-694
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1393
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1745-1858
  IMPACT: HYPOTHESIS: a per-frame world holding the same binding in two frames cannot be restored in a fresh process
    (book B's bind refused, the whole restore rolled back); a per-frame world without such a pair restores but runs
    process-wide afterwards; a process that configures per-frame before restoring gets the world back.
  NEXT: Probe those three cases plus a process-wide control, recording and restoring in separate processes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T16:05:04Z
  TYPE: MEASURE
  CLAIM: A per-frame world holding the same class in two frames does not fail to restore: it restores "complete"
    and has silently lost one frame's binding. Probe (VM mirror of 0.2.8212, 3.14.7t with the GIL off; record and
    restore in separate processes): per-frame ids installed, recording on, tenant_a and tenant_b each get a Book
    postured dynamic before its bind (configure_aether_frame), a TenantService bind and a conjure. The record holds
    2 frames, 2 books, 2 conduits and 2 spell indexes but ONE spell crystal, owned by tenant_b's book; its Aether twin
    carries the three logger fields only. The fresh-process restore reports status complete, spell_active 1 and no
    Aether shortfall, and the regime in force afterwards is process-wide (True): tenant_a's Book came back empty.
  EVIDENCE:
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s1_record.txt:1-1
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s1_record_custody.json:1-13
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s1_restore_plain.txt:1-2
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/regime_probe.py:27-91
  IMPACT: The owner-facing symptom is data loss reported as success, not a failed restore - worse than the
    ticket's first guess.
  NEXT: Read why the record kept one crystal (the recorder's custody keys).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T16:05:04Z
  TYPE: FACT
  CLAIM: Why one binding vanished: the recorder keys spell custody by spell_id alone. PersistenceProfile keeps one
    active and one inactive crystal map keyed by spell_id with replace-on-emit (a new crystal for the same id
    displaces and cleans the previous one; the journal names the id only); restore folds the journal into id-keyed
    custody, last write wins, and replays a Book's binds only for crystals whose spellbook_id names that Book. Under
    process-wide ids that key is unique by construction; under per-frame ids two frames can hold the same id, so the
    earlier frame's crystal is displaced at record time and its Book restores empty, with no shortfall. The missing
    regime flag is the smaller half of the gap.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:334-360
  - src/melder/crystallizer/persistence/persistence_profile.py:744-774
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1156-1240
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1956-1980
  IMPACT: Recording the regime alone would not bring a per-frame world back: restore would run per-frame again, but
    one frame's binding is already gone from the record. A real fix keys custody (and every spell_id-keyed record
    entry: removal, activity) per frame when ids are per frame, or refuses/flags per-frame worlds at record time.
    Whether other id-keyed stores (MutationResearch residence, research journals) share the flaw is UNKNOWN.
  NEXT: Controls: restore with per-frame ids installed first; a per-frame world with distinct classes; a
    process-wide control. Then the DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T16:15:30Z
  TYPE: MEASURE
  CLAIM: Controls, same VM mirror (0.2.8212, 3.14.7t, GIL off), record and restore in separate processes; the probe
    gained a second follow-up (bind the tenant class into tenant_a) after the S1 plain run. (1) The same-class
    per-frame record restored with per-frame ids installed first: complete, spell_active 1, per-frame ids in force,
    stage 1 reports live_aether_already_configured_recorded_payload_skipped, and binding the class into tenant_a is
    accepted - tenant_a came back empty, so the loss happens at record time whatever regime the restore runs under.
    (2) A per-frame world with different classes (TenantService in tenant_a, OtherService in tenant_b) records two
    crystals and restores complete with both; restored plainly it runs process-wide and binding TenantService into
    tenant_b is refused ("Spell ID collision"), which the recorded world allowed; with per-frame ids installed first
    the same bind is accepted. (3) Control, a process-wide world with different classes and no Aether
    configuration: no Aether twin is recorded at all, the restore is complete with both bindings under process-wide
    ids, and both follow-up binds are refused exactly as they were before recording.
  EVIDENCE:
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s1_restore_perframe_first.txt:1-3
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s3_record.txt:1-1
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s3_restore_plain.txt:1-3
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s3_restore_perframe_first.txt:1-3
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s2_record.txt:1-1
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s2_restore_plain.txt:1-3
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/regime_probe.py:93-140
  IMPACT: Two separate defects, both measured. The missing regime changes a restored per-frame world's behaviour (it
    comes back process-wide unless the host installs per-frame ids before restoring). Custody keyed by spell_id
    loses one frame's copy of a class bound in several frames at record time, and the restore still reports
    complete. Process-wide worlds round-trip correctly.
  NEXT: File the DECISION_REQUEST with the fix options and move the ticket to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T16:15:30Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner pick needed; nothing in src/ has changed. Options, smallest first:
    A. Record the regime. The Aether twin carries process_wide_unique_spell_ids (from the configuration seam and the
       utility system's root emission) and from_recorded_payload applies it, so restore stage 1 installs it before
       stage 5 births the frames. A live Aether already configured with the other regime gets a named shortfall
       instead of today's plain skip; a live world whose frames sealed the other regime is refused at stage 1 by
       the 0.2.8209 guard instead of restoring under the wrong regime. Fixes case (2), not case (1). Additive
       field: from_recorded_payload ignores unknown keys, so an older reader restores process-wide as today, and
       a newer reader of an older record keeps the default and can list the key under "missing" (record 3.1.0).
    B. Key spell custody per frame when ids are per frame: the recorder's two crystal maps, journal entries, removal
       and activity emissions, restore's fold and per-book bind order, graft - every spell_id-keyed record path.
       Fixes case (1). Record major bump (4.0.0) so an older reader refuses instead of folding two copies into
       one. The biggest change; whether MutationResearch residence and the impact reads share the key is UNKNOWN.
    C. Stop the silent loss: when a crystal displaces another Book's crystal with the same spell_id, record a named
       shortfall that restore reports (or refuse to record while one class sits in two frames under per-frame
       ids). Small; makes case (1) loud instead of fixing it.
    Recommendation: A and C now - small, and every restore then answers honestly; B only if recording
    multi-tenant per-frame worlds is a feature you want, since that is the shape per-frame ids exist for.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:421-485
  - src/melder/aether/aether_configuration.py:872-920
  - src/melder/aether/aether_utility_system.py:204-256
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1393
  - src/melder/crystallizer/persistence/persistence_profile.py:334-360
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1156-1240
  IMPACT: Until a pick lands, recording a per-frame world is unsafe when a class is bound in two frames, and every
    per-frame world restores process-wide unless the host installs per-frame ids first (today's workaround).
  NEXT: Owner picks A, B, C, a combination, or drops it; a pick opens a patch lane (source, notch, release note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T16:39:17Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner direction (chat): work this lane first, the injected-provider epic waits; the owner favours B
    (per-frame custody keys) as the full fix and asked to talk it through before any further work. melder_0's
    position: B is the part that makes a per-frame world recordable, but it is not a full fix on its own. Without
    A a fresh-process restore of a same-class per-frame world would run process-wide ids, the second frame's bind
    would collide ("Spell ID collision", as the measured follow-up bind was) and the all-or-nothing restore would
    roll back (HYPOTHESIS: inferred from that refusal and the documented rollback law, not measured). Full fix:
    A + B; C becomes unnecessary once nothing is overwritten. Open before patch docs: the custody key (spellbook id
    + spell_id, or frame + spell_id - retargeted loads rename frames), every spell_id-keyed record path (removal,
    activity, notch, transfer, graft, impact reads, MutationResearch: UNKNOWN until read), record version 4.0.0.
  EVIDENCE:
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s1_restore_plain.txt:1-2
  - context_compass/artifacts/aether_record_spell_id_regime_20260930/runs/s3_restore_plain.txt:1-3
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1745-1858
  IMPACT: The owner's scope choice decides the size of the change; nothing is edited until it is settled.
  NEXT: Owner confirms A + B as the scope; then a read-only survey of every spell_id-keyed record path, then patch
    docs with the exact file list for the owner's OK.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-30T15:55:22Z on the owner's question; in review since 2026-09-30T16:15:30Z.
Read-only: nothing in src/ changed. Answer: two defects. A per-frame world restores under process-wide ids because
the Aether twin carries no regime; and a class bound in two frames under per-frame ids loses one frame's copy at
record time (custody keyed by spell_id) while the restore reports complete. Process-wide worlds round-trip.
Workaround today: install per-frame ids before restoring (fixes the first defect only). Fix options A (record the
regime), B (per-frame custody keys) and C (flag or refuse the displacement) are in the DECISION_REQUEST;
recommendation A + C, and B if multi-tenant recording is wanted. Next: the owner's pick. Probe and runs:
artifacts/aether_record_spell_id_regime_20260930/ (regime_probe.py, runs/s1_*, s2_*, s3_*); the VM caches in
~/regime_runs are scratch outside the repository.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
