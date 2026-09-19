# Preserve provider artifacts across resolution passes

Patch ID: provider_artifact_ownership_2026_09_19

<!-- BEGIN ENTRY: "Compiler: visibility and publication authority" -->
## Scope and non-goals
Repair canonical artifact publication under the current Spell/unique-object model. Preserve provider
usability through borrower validation and local consumer compilation. No external-object redesign,
lifetime expansion, disposal/transfer change, validation bypass or cache redesign.

## Changed-components matrix
| Component | Delta |
| --- | --- |
| SpellCompiler Phase 5 | Separate snapshot visibility from artifact publication targets |
| Resolution orchestration | No code change; existing rebuild scope defines publication authority |

## Interface and boundary deltas
The private attachment helper receives an explicit collection of publication spell IDs. Frame-wide
compilation publishes to owned-local IDs. Local compilation publishes only to its selected target.
Public bind, meld, validate and link signatures stay unchanged.

## Cross-component invariants
- Full visible dependency graphs MUST remain available for validation and consumer compilation.
- Borrowed provider Spells MUST NOT lose canonical artifacts through borrower publication.
- Local compilation MUST NOT invalidate dependencies whose plans it does not rebuild.
- Selected targets MUST still invalidate stale downstream artifacts and rebuild normally.
- Existing object identity/state, lifetime and permissions MUST remain unchanged.

## Migration and rollout
Reproduce native failures; add local-dependency and publication controls; update Phase 5; run compiler,
contract and original downstream acceptance where available; synchronize source docs/graph/build assets.

## Rollback
Revert the bounded Phase-5/helper contract and test/doc delta together. No data schema or persisted
configuration changes. Do not mask missing plans or silently compile borrowed providers as a fallback.

## Validation and evidence
Seven existing failures become green; six early controls stay green. Add same-book late-consumer
resolution and fresh construction checks. Preserve current visibility and owner-target invalidation.

## Ticket coverage
EPIC-2026-09-13-provider-artifact-ownership-and-existing-instance-planning ->
STORY-2026-09-13-provider-artifact-ownership -> TASK-2026-09-13-repair-provider-artifact-ownership.

## Unknowns
Original downstream environment availability must be checked. Full repository concurrency and unrelated
ownership transitions are outside this focused repair; do not claim their qualification from these tests.
<!-- END ENTRY: "Compiler: visibility and publication authority" -->
