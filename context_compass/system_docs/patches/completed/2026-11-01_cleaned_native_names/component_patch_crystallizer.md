# Crystallizer Persistence contract
<!-- BEGIN ENTRY: "Canonical recorded name with legacy reads" -->
## Purpose and boundary
RecordedUnitState, PersistenceProfile name serialization and RestoreEngine singleton guards.
## Before and after
Canonical Python name CLEANED keeps the value cleaned. Generic recorder state.name emits CLEANED.
Both replay stages MUST recognize exact cleaned and CLEANED as final cleaned intent.
## Interface and errors
Preserve raw journal keys, later-wins fold and both existing recorded-but-cleaned shortfall strings.
Retain major5 admission, enabled/disabled replay, public build verbs and rollback.
## State and lifecycle
Do not clean live hosted owners to satisfy a recorded state; skip recorded reconstruction exactly
as the existing legacy guard does. Twin retention and all ownership contracts remain.
## Failure delta
New canonical records must not bypass the no-reconstruction guard; old admitted records keep it.
## Dependencies and order
Both larger implementations were read fully before this patch; current hashes remain3306ab58/
b9134ea3. Change only declaration, direct member consumers and the two read guards/docs.
## Validation and unknowns
Prove canonical journal key/payload/describe emission plus valid-major5 old/new public cached
round trips and final-state ordering. A private replay mock alone cannot satisfy acceptance.
Exact public fixture selection remains pending and blocks that acceptance, not helper qualification.
<!-- END ENTRY: "Canonical recorded name with legacy reads" -->
