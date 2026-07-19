# Task: source drift at load-time preflight

- Completed: 2026-07-11T19:25:00Z
- Summary: Closed on owner directive ("go ahead and finish your 3 lanes")
  after source re-verification: SourceDriftStrategy live
  (source_drift_strategy.py:14, registered in persistence_analyzer:31),
  UserSourceIntegrityStrategy narrowed (its own docstring :22 records the
  move). Promotion executed: stale 8th-row drift text fixed in
  src_components S2, 10-row default set documented in the new three-lane
  sections of both C-docs, preflight graph node role updated to rows
  8-10; patch dir -> completed/. Tests: Not run by me (sandbox) - the
  tamper-only + drift-matrix suites ride the owner's tree runs.

## Metadata
- Task ID: TASK-2026-07-12-source-drift-preflight
- Parent: follow-through of the closed S3 story (describe_source_drift
  existed as an on-demand view only)
- Status: closed (owner-directed finish 2026-07-11)
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-12T06:10:00Z
- Updated: 2026-07-12T06:10:00Z

## Problem / Opportunity
physical_module_fingerprints ships in every crystal, but only
retention-ON modules were drift-checked at load - retention-OFF worlds
restored blind to divergence. A restore should say "your tree diverged
from this sealed world" before it builds anything.

## Notes
- DATETIME: 2026-07-12T06:10:00Z
  TYPE: FACT
  CLAIM: IMPLEMENTED (patch source_drift_preflight_2026_07_12 authored
    first). NEW SourceDriftStrategy ("source_drift", 10th default
    preflight row): every fingerprint re-hashes against its recorded
    path (CRLF-safe read_text) - drift = warning
    "user_source_drifted_since_seal" (live file wins; notice, never
    refusal), absent backing file = honest warning (import may still
    resolve via sys.path), unreadable = info, unchanged = silent;
    (module, path) pairs deduplicate across crystals.
    UserSourceIntegrityStrategy NARROWED to record self-consistency only
    (retained-text tamper blocker; its drift/absent branches removed -
    the double-report overlap is gone; unused Path import dropped).
    Tests: tamper-only rewrite + new every-fingerprint drift matrix with
    cross-crystal dedupe over tmp files.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/preflight/source_drift_strategy.py:1-141
  - src/melder/crystallizer/crystal_analysis/preflight/user_source_integrity_strategy.py
  - tests/unit/melder/crystallizer/crystal_analysis/test_user_source_retention.py
  TESTS: Not run (sandbox; disk verified via file-tool sentinels).
    Rides the next owner sweep. NOTE for the sweep: every restore now
    disk-reads each fingerprinted module once at preflight - if a
    monster world makes that noticeable, a config knob is the escape
    hatch (not built; YAGNI until measured).
  NEXT: owner sweep green -> close + promote with the seams patch.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Load-time drift coverage for every fingerprinted module regardless of
retention; integrity strategy narrowed to tamper; 10th preflight row.
