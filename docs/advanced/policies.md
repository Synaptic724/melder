# Read ward policy before changing it

Prerequisite: [linking and permissions](../intermediate/permissions.md).
`Conduit.policy` reports the current ward policy. The policy controls contract
direction and how per-spell restrictions are applied.

The five modes are `default`, `whitelist_all`, `block_all`, `inbound_only`, and
`outbound_only`. Use their names or enum members; an enum's integer `.value` is
not its string name.

## Diagnose the refusal boundary

The saved policy lesson checks three conditions: the frame must be dynamic, the
conduit must be normal, and restrictive policy changes can be refused while
contracts exist. A policy change does not silently tear down existing relationships.

Read the current relationships, end the contracts deliberately if that is the
intended application operation, then apply the policy. Use the existing
[severing guide](../intermediate/ownership.md) for the relationship's lifecycle.
