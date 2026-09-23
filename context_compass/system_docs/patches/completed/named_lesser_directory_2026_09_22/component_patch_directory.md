# ConduitCloud and frame registration

## Before
Cloud discovery aliases frame root maps. Root insertion and Cloud reads use different locks;
lesser scopes cannot join discovery without being mistaken for normal roots.

## After
Cloud owns name -> borrowed Conduit and id -> name maps, plus temporary promotion-name claims.
Root maps remain borrowed only for cluster services. All public discovery views use the named maps.
Internal publish/retire/claim/release operations share Cloud's existing RLock and remain leaf operations.
Name publication validates exact nonempty strings, refuses another identity and retires an old alias
for the same live object in one critical section. Retirement matches identity before removal.

Frame register_root_conduit publishes the root name before root-map insertion. Its unregister path
retires any directory entry even for a failed post-attachment root registration, then removes root
maps and DevOps ownership according to their existing contract. Frame cleanup clears Cloud last.

## Validation
Public lookups/list/count match; unnamed shells are absent; root/lesser collisions refuse in both
directions; concurrent same-name acquisitions admit one; frame isolation and cluster rejection hold.
Cloud cleanup releases directory references and clusters without disposing borrowed conduits.
