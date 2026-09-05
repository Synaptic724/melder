# Component patch: Crystallizer ordered disposal capture and replay

## Purpose and boundary
The passive recorder carries resolved bind values; loader drivers rebuild through public runtime verbs.
Only SpellCrystal, RestoreEngine (including its existing report), and GraftRunner change here.

## Before / after
- Before: crystal capture sorts names; staged restore and parked/merge graft omit them.
- After: every existing bind path receives the ordered recorded names, with normal book composition.
- Before: member/selection joins assume recorded SHA equals the newly bound identity.
- After: restore translates changed IDs through its existing report; graft carries actual bind results.

## Interface deltas
Persisted field names and list shapes remain unchanged. RestoreReport.identity_map may additionally
contain changed Spell SHA translations; unchanged content IDs need no entry. Graft report keys stay
unchanged. Internal fresh-anchor handoff carries the resulting SpellIndex instead of rediscovering it.

## State and lifecycle
No new long-lived registry, lock, or runtime owner. Crystal retains detached ordered values by its
existing persistence contract. Graft borrows the new index only for the call; merge retains a local
selected-result ID. Restore uses its existing locked report map and normal cleanup/rollback lifecycle.

## Failure modes
Preserve missing/unhydratable-member shortfalls, resident refusal/skip policy, and all-or-nothing restore.
Failed or skipped merge selections are not adopted. Old sorted lists cannot recover discarded order.

## Dependency and ordering
Configuration reload precedes new binds. Every new bind applies its receiving book's authoritative
block order. Record changed identity before subsequent anchor/selection/contract reads. Exact staged
member reads use the existing owned-member seam; all structural mutations stay on public verbs.

## Validation
Capture/property/JSON retain non-alphabetical names. Same-policy cache restore preserves both priorities,
active/staged membership, and actual cleanup. Changed-host fresh/merge grafts park correctly and adopt
only the requested successfully grafted selection. Test changed-ID restore joins and driver parity.

## Open decisions
None for the approved scope. Process-wide unique-spell copy restrictions remain unchanged and separately
tracked; do not remove existing xfails for that unrelated design boundary.
