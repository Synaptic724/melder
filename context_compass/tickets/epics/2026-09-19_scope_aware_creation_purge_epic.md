# Epic: Purge creations through their authorized calling scope

## Metadata
- Epic ID: EPIC-2026-09-19-scope-aware-creation-purge
- Status: draft
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-20T00:53:18Z
- Updated: 2026-09-20T00:56:30Z
- Target Window: future owner-approved implementation
- Related Program/Initiative: Meld, Conduit, SpellSpace and Creations lifecycle

## Current Authorization
PLANNING ONLY. The owner explicitly requested this epic before any implementation, followed by
regeneration of Melder build assets. Do not add purge methods, runtime behavior, or feature tests in
this pass. This record captures the requested feature and the investigation needed before building it.

## Problem / Opportunity
The owner wants `purge` as the lifecycle counterpart to `meld`: remove a target's retained creations
from the appropriate existing store, using the real caller's scope to determine deletion authority.
Both Conduit and SpellSpace should expose the operation, with Meld owning shared targeting/routing
logic. A caller must not gain authority over broader-scope instances merely because Meld can find them.

## MRP Alignment (Most Reasonable Product)
Reuse existing identity lookup and Creations lifecycle machinery while making deletion scope explicit.
The feature must distinguish finding an object from being authorized to retire it, especially when
lesser conduits, spellspaces and shared instances use broader resolution targets.

## Ticket Contract
- ENTRY_GATE: This epic records owner intent. Before implementation, read the scoped component/source
  owners, settle open scope and lifecycle details, create bounded stories/tasks and patch contracts.
- EXECUTION_BOUNDARY: Future Conduit/SpellSpace purge entry points, Meld targeting and caller context,
  authorized Creations removal/disposal, required coordination and behavioral validation.
- DEPENDENCIES: Existing Existence vocabulary, creation-store ownership, scope identity, removal and
  disposal behavior. Reuse those systems; verify their source before claiming the implementation shape.
- EXIT_GATE: All approved scope rules pass positive and refusal tests; stores and reuse paths agree;
  documentation/assets reflect the final API and the owner accepts the completed feature.
- FAILURE_ESCALATION: Record unresolved root authority, instance multiplicity or disposal semantics
  before coding. Do not silently broaden deletion, bypass existing ownership, or invent a new scope.

## Goals (Outcomes)
- Provide purge through Conduit and SpellSpace with shared orchestration owned by Meld.
- Identify the selected registration using the existing Meld lookup machinery, without constructing it.
- Carry the actual originating scope into purge so routing does not erase caller authority.
- Remove only creations in the permitted storage scope for the target's Existence.
- Preserve registration, compiled definitions and the ability to meld again according to normal rules.
- Respect existing disposal/ownership contracts and keep live lookup and cleanup records consistent.

## Non-Goals (Explicit Exclusions)
- Implementing this feature during epic creation or build regeneration.
- Unbinding Spells, deleting SpellIndex versions, removing source custody or erasing research history.
- Purging an entire frame, conduit tree or dependency graph as an implicit side effect.
- Redesigning existing-object ownership, disposal policy, Existence or registration uniqueness.
- A new scope system, replacement cache framework, release or version bump.

## Scope Boundaries
- In scope: the caller/target/store policy below and the existing lifecycle paths needed to enforce it.
- Out of scope: unrelated lifecycle proposals and automatic cascading deletion not explicitly approved.
- Selector shape, instance selection within many buckets, return value and failure behavior are design
  questions to settle in discovery; the word purge alone does not settle them.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Owner requested an epic recording the idea and explicitly prohibited implementation.

## Owner-Requested Scope Rules

| Existence | Purge target scope | Calling authority |
| --- | --- | --- |
| many | The calling local conduit's creations, or the calling SpellSpace's creations | Local to that originating scope; do not widen to another conduit/spellspace |
| unique_per_spell_space | That SpellSpace | Preserve the specific spellspace identity; never infer another one |
| unique_per_conduit | That conduit | Preserve the applicable conduit identity when called through either facade |
| unique_per_conduit_cluster | Root scope | The root scope itself must originate the request |
| unique | Root scope | The root scope itself must originate the request |
| unique_per_conduit_lineage | Not specified by the owner yet | Must be decided before supporting this mode; do not silently copy the cluster rule |

The first five rows are the owner's requested behavior, not claims about current purge support.
`unique_per_conduit_cluster` and `unique_per_spell_space` are the existing enum spellings for the
owner's "unique per cluster" and "unique per spellspace" terms. The enum also declares lineage scope;
that additional mode remains an explicit question rather than an inferred permission.

## Requirements (Functional + Non-Functional)
- Capture the originating Conduit or SpellSpace before forwarding into Meld. Retain caller identity
  separately from any resolved owner/root used to locate the creation.
- Enforce root-only authority before mutating storage or invoking disposal. Delegation from a lesser
  scope must not make the root look like the original caller.
- Resolve the target registration through existing lookup conventions without invoking meld itself,
  executing a constructor, or creating an instance solely to delete it.
- Conduit and SpellSpace should delegate shared decisions to Meld; storage mutation belongs to the
  relevant Creations owner rather than ad hoc edits to private dictionaries in each facade.
- Define how live records, disposal metadata and any cached reuse references are retired together.
  A successful purge must not leave a reuse path returning a removed creation.
- Keep unrelated scopes and unrelated creations intact. Dependent Python objects may still hold
  references; deletion must not pretend those references have been rewritten or garbage-collected.
- Reuse existing configured disposal behavior and external-object ownership boundaries. Confirm the
  precise per-target retirement contract before promising disposal ordering or error recovery.
- Coordinate purge versus concurrent meld, reset, cleanup, transfer and scope reuse using existing
  synchronization mechanisms where suitable. No per-meld overhead is justified merely by this epic.
- Qualify subsequent meld behavior: an eligible factory may create again; an externally supplied
  object must not accidentally become constructible through purge.
- Respect cleaned scopes and any required explicit SpellSpace context; do not fabricate a scope.

## Required Reading Before Discovery / Implementation
Read architecture orientation, verify indexes, then take the relevant component slices before source.
Documents are navigation and intent; read the actual implementations before changing behavior.

- `system_docs/src_components_index.md`: Conduit Runtime; Creations and SpellSpace; Meld Resolution
  Runtime; ConduitWard and Contracts; ConduitCluster; Creations Disposal Pipeline; SpellSpace Thread State.
- `system_docs/src_graph_index.md`: verify and slice the owners found through those components.
- `src/melder/aether/spellbook/existence/existence.py`: all six modes; do not equate cluster and lineage.
- `src/melder/aether/conduit/conduit.py`: public entry forwarding, root/lesser identity and cleanup.
- `src/melder/aether/conduit/spell_space/spell_space.py`: owned scope, direct calls, reset and cleanup.
- `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`: existing active-scope semantics.
- `src/melder/aether/conduit/meld/meld.py`: shared selection, scope routing and reusable resolution policy.
- `src/melder/aether/conduit/meld/conduit_meld.py`: conduit-specific storage/reuse entry paths.
- `src/melder/aether/conduit/meld/spellspace_meld.py`: spellspace-specific routing and reuse paths.
- `src/melder/aether/conduit/creations/creations.py`: live/disposal records, individual removal, locking.
- `src/melder/aether/conduit/creations/conduit_creations.py`: conduit/root store ownership.
- `src/melder/aether/conduit/creations/cluster_creations.py`: actual cluster-store responsibility.
- `src/melder/aether/conduit/conduit_cluster.py`: cluster membership, root/owner and sharing behavior.
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`: creation transfer ownership.
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`: only as needed to trace reuse
  references after deletion; follow concrete callers rather than inventing invalidation work.
- Current test architecture/component indexes and existing scoped disposal/reuse/transfer tests before
  designing regressions. Source-read findings should identify the exact test files, not assume coverage.

## Dependencies / Related Work
- Existing-object lifecycle redesign remains separate and backlogged:
  `tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md`.
- The non-resolvable registration epic is complete. Purge must define what selecting such a target
  means without reopening its construction or ownership policy:
  `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`.

## Milestones (Track Progress)
- [x] M0: Record owner intent and explicit no-implementation boundary.
- [ ] M1: Discover store routing, caller identity and existing targeted removal/disposal contracts.
- [ ] M2: Settle root terminology, lineage mode, many selection and error/return semantics.
- [ ] M3: Create approved implementation stories/tasks, patch contracts and meaningful failing regressions.
- [ ] M4: Implement the approved scope routing and Creations retirement contract.
- [ ] M5: Qualify concurrency/reuse/lifecycle behavior and update documentation/assets before acceptance.

## Stories (Proposed; Not Created or Authorized Yet)
- [ ] Discover and settle caller authority and per-Existence routing.
- [ ] Implement Conduit/SpellSpace forwarding and shared Meld purge targeting.
- [ ] Implement scoped retirement through Creations and required reuse coordination.
- [ ] Qualify scope isolation, disposal/concurrency behavior and public documentation.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Create this epic before rebuilding existing Melder assets.
- [ ] Retain source-backed decisions and exact reading pointers through later implementation.
- Current planning/build-only task:
  `tickets/tasks/2026-09-19_draft_purge_epic_and_refresh_assets_task.md`.

## Acceptance Criteria (Feature Complete)
- Both public facades expose the approved purge operation through shared Meld orchestration.
- Every approved Existence row removes only its permitted scope's matching creations.
- A non-root caller cannot purge unique or cluster-shared root creations, even through delegation.
- Root calls can purge their authorized target; sibling and unrelated scope instances remain intact.
- Live lookup, cleanup tracking and supported cached reuse paths agree after success or failure.
- Concurrency and disposal behavior match the explicitly settled contract; no duplicate disposal or
  silent wrong-scope deletion occurs.
- Subsequent meld and supplied-object behavior remain consistent with current registration policy.
- No required design decision is hidden behind a guessed default; owner accepts final behavior.

## Validation / Test Approach
No purge tests or implementation run in this planning pass. Future behavioral matrix:
- Cross caller kinds (root conduit, lesser conduit, explicit SpellSpace) with every Existence mode.
- Root-only positive cases and non-root refusals, including a SpellSpace attached to a root conduit.
- Same target present in multiple scopes, repeated many creations and absent/already-purged targets.
- Disposal metadata, ordering, disposal failure, external-object rules and successful re-meld.
- Warm reuse and concurrent purge/meld/reset/cleanup/transfer using deterministic synchronization.
- No constructor invocation during purge and no accidental registration/history deletion.

## Risks / Mitigations
- Owner/root lookup can erase the originating caller: carry both identities and test delegated refusals.
- Cluster and lineage are distinct modes: settle both explicitly rather than relying on similar names.
- Removing a live record alone can leave disposal or reuse entries: trace both stores and their consumers.
- Disposal failures or in-flight construction can make partial removal ambiguous: define the contract first.

## Applicable Anti-Patterns
- [x] No feature implementation during this planning/build request.
- [ ] No root privilege inferred merely from reaching a root-owned store.
- [ ] No global purge, unbind or dependency cascade hidden in a local operation.
- [ ] No disposal-policy redesign or new cache system without a demonstrated need.

## Open Questions
- What precisely identifies "root scope" for unique and cluster rules: owning/root conduit, lineage
  root, cluster leader, or another existing authority? Verify actual ownership before selecting a check.
- Does a SpellSpace attached to a root conduit count as a root-origin caller, or must the Conduit
  itself initiate root-only purges? Preserve caller kind until this is explicitly settled.
- What should unique_per_conduit_lineage do?
- Does a target purge remove all locally tracked many instances, one explicit instance, or support both?
- How does a conduit call identify a required SpellSpace; what happens without explicit scope context?
- Exact selector signature, absent-target outcome, return payload and disposal-error behavior.
- Confirm target-only disposal and external-instance behavior without implying removal of references
  already held by other application objects or cascading through dependent registrations.

## Decision Log
- Owner named the feature purge and wants it as meld's counterpart for retained creations.
- Owner selected Conduit and SpellSpace entry points, with Meld owning shared logic and caller context.
- Owner supplied the five scope rules above and explicitly prohibited implementation in this pass.
- Existing enum adds a sixth lineage mode; its purge rule remains undecided.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none; build evidence belongs to the planning/build task.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: future accepted feature closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: read the scoped source owners before implementing; open policy questions remain above.

## Notes
- DATETIME: 2026-09-20T00:53:18Z
  TYPE: DECISION
  CLAIM: Owner requested this planning-only epic followed by build-asset regeneration. Preserve
    caller scope for local many/conduit/spellspace purges and root-only unique/cluster authority.
    No feature implementation is authorized by this request.
  EVIDENCE:
  - This epic's Current Authorization and Owner-Requested Scope Rules record the user's instruction.
  - src/melder/aether/spellbook/existence/existence.py:63-114
  IMPACT: Future work has an explicit scope matrix; lineage/root/multiplicity questions remain visible.
  NEXT: Finish the separate existing-asset rebuild, then await owner direction for purge discovery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- Build follow-through complete: the linked task records regenerated source assets and passing
  source/repository freshness checks for 0.2.43. This is not purge feature implementation.
- [ ] Feature implementation and validation delivered in a later authorized pass.
- [ ] Owner accepts the completed feature and recorded lifecycle limits.

## Noting Behavior
Keep program decisions and scope rules here; future child tasks own source findings and test evidence.

## Context / Handoff Summary
Draft idea only. Purge is intended to retire selected creations through Conduit/SpellSpace -> Meld ->
the authorized store. Preserve actual caller context. The five owner rules are recorded; root identity,
root-attached SpellSpace authority, lineage mode and many-instance selection require later decisions.
Do not implement on the strength of this epic-creation request. The linked planning/build task has
completed existing-asset regeneration and freshness checks; await owner direction for further work.
