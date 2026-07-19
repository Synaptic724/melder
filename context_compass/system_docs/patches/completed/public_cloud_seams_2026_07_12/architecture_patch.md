# Architecture Patch: public cloud seams (promote two documented privates)

- Patch ID: public_cloud_seams_2026_07_12
- Ticket: follow-through of the closed S1 story (both seams were flagged
  there as documented-private with "follow-up: public accessor")
- Status: active

## Objective
Promote the two cross-package seams the S1/S2 lanes had to document as
deliberate private reads into real public verbs, and repoint every
reader:
- AethericFrame.conduit_cloud (property) - the frame-owned cloud; the
  restore engine and the admission host preflight currently read
  `frame._conduit_cloud` directly.
- ConduitCloud.has_cluster_name(name) - the cluster-existence probe;
  admission preflight and the engine's cluster skip lane currently read
  `_conduit_clusters` membership directly.

## Non-goals
No behavior change anywhere: same objects, same answers - only the
access spelling and the retired "documented private seam" comments.

## Interface Deltas (additive)
- AethericFrame.conduit_cloud -> ConduitCloud (check_cleaned property).
- ConduitCloud.has_cluster_name(cluster_name: str) -> bool (lock-guarded
  membership read, mirroring has_conduit_name).
- Readers repointed: restore_engine (cluster replay lane + conjure skip
  lane), load_admission._preflight_host (conduit + cluster checks),
  UserSourceIntegrityStrategy untouched (no cloud reads).

## Rollback
Delete the two verbs, restore the private reads + comments.
