# Story: spell-index graft lane (index + members into a LIVE book)

- Completed: 2026-07-11T19:25:00Z
- Summary: Closed on owner directive ("go ahead and finish your 3 lanes")
  after source re-verification: GraftRunner (graft_runner.py:21),
  capture_index_graft (profile :783 / system :456 / facade :621),
  graft_index facade (:647), Spellbook.conduit (spellbook.py:5412), and
  the shared user_world_rebuild lane (:19) all live; both follow-ups
  were already executed (zero remain). Promotion executed: graft lane +
  shared rebuild lane documented in the new three-lane sections of both
  C-docs; graph gains GraftRunner + user_world_rebuild nodes and 4 edges
  (529/990, readable regenerated + validated); patch dir -> completed/.
  Tests: Not run by me (sandbox) - the round-trip/overlap/skip/
  multi-member-park integration suites ride the owner's tree runs.

## Metadata
- Story ID: STORY-2026-07-12-spell-index-graft
- Parent: owner-approved candidate pinned on the closed horizon epic
  (Decision Log: graft unit = the SPELL_INDEX - all members, custody,
  selection; normal re-integration verbs aimed at a live host book)
- Status: closed (owner-directed finish 2026-07-11)
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-12T06:40:00Z
- Updated: 2026-07-12T06:40:00Z

## Pinned Design (source-verified seams)
1. CAPTURE: PersistenceProfile.capture_index_graft(index_id) -> graft
   record {record_version, index_id, index_payload (twin describe),
   members: {spell_id: {payload, custody_state}}} - reads
   _spell_index_crystals_by_index_id + both custody maps per member.
   System passthrough + Crystallizer facade (activation-gated). Storage
   is the USER'S choice: the record is a plain versioned dict - ship it
   through the generic mesh (kind of your choosing) or formations.
2. RESTORE: crystal_loader_system/graft_runner.py - GraftRunner(record,
   host_spellbook, skip_resident=False).run():
   - RecordVersion gate; host book must be conjured (public
     Spellbook.conduit accessor - NEW, retiring the seam like
     public_cloud_seams did).
   - OVERLAP RULE (the pinned open question, resolved conservatively):
     any member already RESIDENT in the host frame
     (frame.find_index_for_spell) -> REFUSE by default;
     skip_resident=True skips that member with a shortfall. NEVER
     mutates an existing index (general_0's unfinished add/remove seams
     stay untouched - grafts only create FRESH indexes via bind).
   - Selected member binds ACTIVE first (bind creates the fresh index
     and selects it - no notch needed); parked members ride
     conduit.bind_inactive onto the new live index (the engine's exact
     staged lane against a host book).
   - Hydration v1: the normal import lane
     (RestoreEngine._import_qualified_target static); retained-text
     rebuild for graft members = flagged follow-up (needs the engine's
     user-world lane extracted; not v1).
   - No LoadGate: a graft IS normal user-verb activity (bind/
     bind_inactive per-verb transactions), not a world replay.
   - Report: {status, live_index_id, members_bound, members_parked,
     skipped_resident, shortfalls, identity {recorded->live index id}}.
   - Emissions free: bind/bind_inactive auto-record into the active
     profile (re-recording covenant).
3. Facade: Crystallizer.capture_index_graft(index_id) +
   Crystallizer.graft_index(record, host_spellbook, skip_resident=False)
   (live-object facade precedent: create_spell_crystal takes a Spell).

## Acceptance Criteria
- Capture from book A -> graft into a LIVE book B (any frame): fresh
  index exists in B, selected member callable, parked members parked.
- Resident member refuses by default; skip_resident skips + shortfall.
- Zero mutation of existing indexes anywhere.

## Notes
- DATETIME: 2026-07-12T06:40:00Z
  TYPE: FACT
  CLAIM: Investigation complete: index twins keyed by index_id in the
    profile (:128); engine member lanes fully mapped
    (restore_engine.py:1341-1475 - bind creates the index, bind_inactive
    parks, notch only on divergence); residence probe =
    frame.find_index_for_spell (:758); Spellbook lacks a public conduit
    accessor (only the _conduit slot) - added in this lane.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1341-1475
  - src/melder/aether/aetheric_frame/aetheric_frame.py:758
  NEXT: patch doc -> capture -> runner -> facades -> tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T07:20:00Z
  TYPE: FACT
  CLAIM: IMPLEMENTED per the pinned design (patch
    spell_index_graft_2026_07_12 authored FIRST). (1) Spellbook.conduit
    public property (retires the _conduit seam for borrowers). (2)
    PersistenceProfile.capture_index_graft(index_id) - versioned graft
    record {graft_kind, index_id, index_payload, members {spell_id:
    {payload, custody_state}}, members_without_custody} + system
    passthrough. (3) crystal_loader_system/graft_runner.py - GraftRunner
    (single-use, Cleanable): RecordVersion gate + graft_kind refusal;
    unconjured-host refusal; overlap rule via
    host_frame.find_index_for_spell (refuse-by-default / skip_resident
    skips w/ shortfall "member_resident_in_host_skipped"); selected
    member binds ACTIVE (fresh index, selection free), parked members
    bind_inactive onto it; hydration v1 = import lane w/ honest
    shortfalls (retained-text rebuild = FLAGGED FOLLOW-UP); no LoadGate
    (user-verb activity). (4) Facades capture_index_graft + graft_index
    (live-object precedent). (5) Integration round trip: capture from
    book A -> graft into a live book B on ANOTHER frame (fresh index,
    member resolvable) + overlap refusal + skip_resident lane (the
    single-member skip surfaces as the no-anchor structural refusal -
    documented as the honest outcome).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:1-388
  - src/melder/crystallizer/persistence/persistence_profile.py (capture)
  - src/melder/crystallizer/crystallizer.py (both facades)
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py (round trip)
  TESTS: Not run (sandbox; disk verified via file-tool, runner parsed
    clean). Rides the owner sweep with the two review slices.
  NEXT: owner sweep -> close; follow-ups flagged: retained-text
    hydration for graft members; multi-member park integration variant.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T07:50:00Z
  TYPE: FACT
  CLAIM: FOLLOW-UP #1 EXECUTED (owner: keep going; general_0
    owner-confirmed departed - his lanes are unowned, noted on the
    mailbox check-in; the graft's fresh-index-only law STANDS as the
    technical choice regardless): retained-text hydration for graft
    members. NEW crystal_loader_system/user_world_rebuild.py -
    rebuild_absent_user_modules(spell_id, crystal, on_built,
    on_shortfall) extracts the S2 rebuild mechanics into ONE shared lane
    (live-file-wins, sys.modules skip, dot-depth parents-first,
    SyntheticModule lifecycle, honest shortfalls); the engine's
    _rebuild_user_world now DELEGATES via callbacks (identical
    built-stack + report semantics, order preserved); GraftRunner._hydrate
    gains the same failure->rebuild->single-retry arc (grafted synthetic
    modules persist as normal user activity - no all-or-nothing stack;
    _import_target extracted static). Laws live in exactly one place now.
    FOLLOW-UP #2 EXECUTED same pass: multi-member park integration test
    (test_multi_member_index_graft_parks_the_staged_members, integration
    :1679) - source index with an ACTIVE selected member + a PARKED
    bind_inactive member; capture carries both (parked custody_state
    "inactive"); graft into a live host on another frame reports
    members_bound==1 + members_parked==1 + zero shortfalls; the fresh
    host index holds BOTH ids with the recorded selection (has_spell /
    selected_spell_id asserts). ZERO follow-ups remain in this lane.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/user_world_rebuild.py:1-113
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py (retry arc)
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py (delegation)
  TESTS: Not run (sandbox; both new/edited files parse clean; wiring
    grep-verified 5 refs/3 files). The existing S2 delete-tree round
    trip now exercises the SHARED lane through the engine path.
  NEXT: owner sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Graft = capture one index's full membership+custody as a versioned dict,
re-integrate into a live host book through bind/bind_inactive only;
conservative overlap rule; fresh-index-only law protects general_0's
seams.
