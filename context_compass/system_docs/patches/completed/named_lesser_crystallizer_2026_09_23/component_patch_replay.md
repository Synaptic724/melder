# Hierarchy validation and public-verb replay

## Representation Reader
Use a bounded stateless analysis helper for hierarchy expansion/order, consumed by a new preflight
strategy and RestoreEngine. The record does not depend on this helper. Legacy missing state means
normal root. Reject pooled/cleaned states, missing/cyclic parents, mismatched Book/root edges,
conflicting shared support, multiple roots for one Book, and duplicate names in one recorded frame.

## Execution
Select the Book's normal root explicitly; never take the first arbitrary conduit row. After active
binds, conjure, parked members and selection enforcement, reconstruct lesser parents before children
via parent.create_lesser_conduit(name=...). Lessers must use default policy; reject unsupported values
before replay, preserving the existing normal-only policy mutation contract.
Record each built scope for rollback and each old-to-new id in the existing report. Shared unnamed
ancestors build once and remain outside Cloud. Creations are empty; application instance state is absent.

## Drivers and Admission
Both sequential and parallel drivers already call _replay_one_book; keep child reconstruction there.
Cross-Book plan barriers and link/cluster/contract order remain unchanged. Malformed topology blocks
mediated admission. Direct-engine replay must also refuse invalid child structure instead of silently
skipping it. Existing host name checks naturally see new named rows; skip_existing drops a colliding
lesser's name with a report and creates a new scope, preserving its structural identity separation.

## Version / Rollback
Schema major 3 fences old readers. No extra scheduler or restoration of original ULIDs. Both drivers
must tear down a partially reconstructed child tree using the existing build stack.
