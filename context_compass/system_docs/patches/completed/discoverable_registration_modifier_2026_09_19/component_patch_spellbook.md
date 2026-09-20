# Component Patch: Spellbook Core

<!-- BEGIN ENTRY: Spellbook native policy forwarding -->
## Purpose and Boundary
Spellbook owns active/parked registries and is the public binding surface above Bind.

## Before and After
Both bind APIs currently carry unrecognized kwargs as metadata. Consume resolvable explicitly and
forward it into Bind; report the resulting native value in describe_spells_in_spellbook.

## Interface Deltas
bind and bind_inactive gain resolvable: bool = True. Existing positional/keyword contracts remain valid.
Description rows gain the additive resolvable field. Fluent kwargs route to the same native parameter.

## State and Lifecycle
No new Spellbook state. The per-version flag lives on Spell. Parked members stay off the active pool.
Preserve transactional admission, frame-wide signature claims, ownership stamping and cleanup.

## Failure Deltas
Shared Bind validates the bool and target; no facade coercion. Existing collisions remain unchanged.

## Dependencies and Order
Binding Pipeline implements the native value. Tests then exercise real active and staged registrations.
No recording/replay field is silently inferred from the new description row; S6 owns that propagation.

## Validation
Check omitted/True/False metadata, ordinary description rows, inactive value retention and unchanged
active selection. Prove a fluent False choice does not leak into a later default bind.

## Unknowns
Construction planning for non-resolvable roots is later compiler work; S2 does not claim that behavior.
<!-- END ENTRY: Spellbook native policy forwarding -->
