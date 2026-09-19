# Existing-instance Protocol admission

Patch ID: existing_instance_protocol_2026_09_19
Status: accepted scope; implementation pending.

<!-- BEGIN ENTRY: "Bind: supplied Protocol admission" -->
## Patch scope and non-goals
Reject incompatible existing providers at Bind using the current direct-public-member Protocol rule.
No new registration model, lifetime, disposal policy, compiler behavior or full static type checker.

## Changed-components matrix
| Component | Change | Preserved boundary |
| --- | --- | --- |
| Binding Pipeline | Check actual instance/other-profile values alongside class profiles | Spell/SpellIndex publication remains in the existing pipeline |
| Compiler and runtime | Qualification only | Declared-frame selection and supplied identity remain unchanged |

## Interface and boundary deltas
An incompatible existing-object declaration now raises TypeError during bind, naming its Protocol
and missing/non-callable members. Existing class errors remain compatible. No public signature changes.

## Cross-component invariants
- Both active and inactive binding MUST use the same admission seam.
- Existing values MUST remain unique-only and MUST NOT be constructed or constructor-injected.
- Successful admission MUST preserve the original supplied reference through dependency resolution.
- Callable providers and non-Protocol grouping retain their current contracts.

## Migration/rollout order
Write permanent regressions, repair Bind, validate native paths, update source/public docs, regenerate
graph/indexes and packaged/repository assets, verify generated consistency, then present for acceptance.

## Rollback strategy
Revert this gate/helper and related test/doc delta together; regenerate derived outputs. No persisted
schema or cache-plan policy changes are required because the check precedes accepted Spell publication.

## Validation expectations and evidence plan
Retained admission baseline plus actual-instance/staged/annotation/collection/map/contract paths,
class/factory/grouping/unique controls, relevant regression suite and generated-output checks.

## Ticket coverage map
| Epic | Story | Task |
| --- | --- | --- |
| EPIC-2026-09-13-existing-object-lifecycle-ownership | STORY-2026-09-19-existing-instance-protocol-admission | TASK-2026-09-19-repair-existing-instance-protocol-admission |

## Unknowns and decision requests
None blocking. Inherited Protocol members, annotation-only data, signature checking and mutation after
bind remain outside this repair; qualification does not claim continuous Protocol conformance.
<!-- END ENTRY: "Bind: supplied Protocol admission" -->
