# Task: promote the two documented cloud seams to public verbs

- Completed: 2026-07-11T19:25:00Z
- Summary: Closed on owner directive ("go ahead and finish your 3 lanes")
  after source re-verification: AethericFrame.conduit_cloud
  (aetheric_frame.py:411) + ConduitCloud.has_cluster_name
  (conduit_cloud.py:379) live; grep confirms zero private cloud reads
  remain crystallizer-side (engine :1291/:1587-1590, admission
  :451/:474 all on public verbs). Promotion executed: stale
  _conduit_clusters seam line fixed in src_components S1 + three-lane
  sections added to both C-docs; patch dir -> completed/.
  Tests: Not run by me (sandbox) - the suites ride the owner's tree runs.

## Metadata
- Task ID: TASK-2026-07-12-public-cloud-seams
- Parent: follow-through of the closed S1 story (both seams flagged there)
- Status: closed (owner-directed finish 2026-07-11)
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-12T05:40:00Z
- Updated: 2026-07-12T05:40:00Z

## Problem / Opportunity
S1/S2 lanes documented two deliberate private reads as follow-ups:
`frame._conduit_cloud` (no public frame accessor) and cluster-existence
via `_conduit_clusters` membership (no public probe). Every new lane
kept paying that debt.

## Notes
- DATETIME: 2026-07-12T05:40:00Z
  TYPE: FACT
  CLAIM: IMPLEMENTED (patch public_cloud_seams_2026_07_12 authored
    first). AethericFrame.conduit_cloud property (check_cleaned) +
    ConduitCloud.has_cluster_name (lock-guarded, mirrors
    has_conduit_name). ALL crystallizer readers repointed (engine
    cluster replay + conjure skip lane; admission host preflight conduit
    + cluster checks); grep proves ZERO private cloud reads remain in
    crystallizer; seam comments retired with NOTE markers; the host
    preflight test stub moved to the public spelling (+ has_cluster_name).
    No behavior change - same objects, same answers.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py (has_cluster_name)
  - src/melder/aether/aetheric_frame/aetheric_frame.py (conduit_cloud)
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py
  - src/melder/crystallizer/crystal_loader_system/load_admission.py
  TESTS: Not run (sandbox). Rides the next owner sweep; existing loader
    unit + cluster integration suites exercise both verbs.
  NEXT: owner sweep green -> close + promote the small patch.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Two additive public verbs; all crystallizer cross-package cloud reads now
come through them; behavior identical.
