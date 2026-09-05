# Share one instance across a cluster

Prerequisites: [dynamic linking](../intermediate/dynamic-linking.md) and
[permissions](../intermediate/permissions.md). A named cluster groups dynamic
conduits for `unique_per_conduit_cluster` resolution.

The saved cluster lesson remains **Intermediate 25**, its original location.
Its topic belongs here as well, so both guides point to the same lesson.

## Establish the sharing structure

The example binds a cluster bus with `create` permissions, conjures two named
conduits, and links them. It creates the cluster through the cloud, adds the owner,
elects the owner as leader, and then adds the second member.

Leader election matters: the shared creations store belongs to the elected leader.
Membership alone does not establish that store. Links matter too: the sharing
contracts use the relationship between the conduits.

The final assertion checks that both members resolve the **same bus object**.
Use that identity check when adapting the pattern, not merely the membership list.
