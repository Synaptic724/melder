# Named lesser directory lifecycle

## Contract
Implement stage 1 of EPIC-2026-09-06-named-lesser-conduit-discovery. Names describe live scopes;
they do not change ownership, lifetime, permissions, compiler plans or root accounting.

## Boundaries and Interfaces
- Conduit.create_lesser_conduit keeps its positional logger and adds keyword-only name=None.
- ConduitCloud owns named-scope discovery independently of borrowed root maps used by clusters.
- Frame registration publishes normal-root names through the same directory admission authority.
- Graduation reuses the existing new-Book route and identity, with name reservation only during upgrade.
- Crystallizer child records and Nexus consistency are later stories. No packaged generation here.

## Invariants
- Only named active scopes enter the directory. Names are exact nonempty strings, frame-wide unique.
- Unnamed pool return adds one direct name conditional and no new call, lock, allocation or scan.
- Named return unregisters and clears its label before idle publication. Permanent teardown also retires it.
- Frame root maps and cluster inputs remain normal-only. Cloud list/count/id/name views cover named scopes.
- Callbacks/disposal do not run under the directory lock. Directory methods never acquire frame/ward locks.
- A borrowed discovery result conveys no lease or immunity from owner cleanup and later shell reuse.

## Migration and Rollback
First add focused regressions, then directory and root bridges, then acquire/retire/promotion.
Retain the old named entry until successful root registration replaces it atomically. Reserve only
the requested promotion name during setup; release the reservation in finally. Pre-attachment failure
restores the old lesser; post-attachment failure follows existing normal cleanup ownership.

## Coverage
Directory story -> naming component regressions, Cloud unit/component checks and existing graduation,
pool and hook suites. Later stories retain full persistence/projection/feature qualification.
