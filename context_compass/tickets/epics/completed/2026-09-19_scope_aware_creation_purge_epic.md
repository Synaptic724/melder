# Epic: Purge creations through their authorized calling scope

## Completion
- Completed: 2026-09-21T00:37:37Z
- Summary: Accepted scoped purge with instance and explicit selectors, single/all disposal,
  270 focused tests, refreshed documentation and verified assets.

## Metadata
- Epic ID: EPIC-2026-09-19-scope-aware-creation-purge
- Status: done
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-20T00:53:18Z
- Updated: 2026-09-21T00:37:37Z
- Target Window: accepted and completed
- Related Program/Initiative: Meld, Conduit, SpellSpace and Creations lifecycle

## Current Authorization
IMPLEMENTATION AUTHORIZED (2026-09-20). The owner accepted the discovery plan and directed the
bounded implementation. Meld retains all scope discovery and caller authority checks; Creations
owns creation locking, removal and disposal only. Mirror the existing writer locks for each Existence.
Implementation record: tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md.

Accepted delivery: both instance and explicit-selector paths, plus single/all disposal, are implemented
and pass 270 focused tests. ConduitMeld and SpellSpaceMeld own scope policy; base Meld shares
class-inspection/selector discovery only. Creations handles removal and existing disposal. The owner
accepted turn-in, followed by canonical documentation/asset refresh and passing freshness checks.

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
- Two input choices: an instance inspected for its class before existing lookup, or explicit
  name/type/function/frame/id selectors. No automatic qualifier recovery is required.
- purge_all=True retires the selected binding's retained entries; False requires the actual instance
  and retires that object only. Both modes use the existing scope authority and disposal machinery.
- No public targeting of internal Spell metadata objects; the word spell in the owner's request
  refers to application objects. Reuse Meld's existing discovery instead of adding a runtime import.
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
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepted purge epic turn-in; final delivery and evidence are complete.

## Owner-Requested Scope Rules

| Existence | Purge target scope | Calling authority |
| --- | --- | --- |
| many | The calling local conduit's creations, or the calling SpellSpace's creations | Local to that originating scope; do not widen to another conduit/spellspace |
| unique_per_spell_space | That SpellSpace | Preserve the specific spellspace identity; never infer another one |
| unique_per_conduit | That conduit's Creations | That conduit itself; SpellSpace cannot delegate to it |
| unique_per_conduit_cluster | Elected cluster leader's Creations | The cluster leader conduit itself must originate the request |
| unique | Spellbook owner's/root conduit's Creations | The spell's owning conduit itself must originate the request |
| unique_per_conduit_lineage | Resolving lineage root's Creations | Only that lineage root conduit may originate the request |

These rows are requested behavior, not claims about current purge support.
`unique_per_conduit_cluster` and `unique_per_spell_space` are the existing enum spellings for the
owner's "unique per cluster" and "unique per spellspace" terms. On 2026-09-20 the owner explicitly
selected root-only lineage purge and ruled that SpellSpace purge touches only that space's own
Creations. A SpellSpace cannot delegate purge authority to any broader store, even when its owning
conduit is a spell owner, lineage root or cluster leader.

## Requirements (Functional + Non-Functional)
- Capture the originating Conduit or SpellSpace before forwarding into Meld. Retain caller identity
  separately from any resolved owner/root used to locate the creation.
- Enforce root-only authority before mutating storage or invoking disposal. Delegation from a lesser
  scope must not make the root look like the original caller.
- Resolve the target registration through existing lookup conventions without invoking meld itself,
  executing a constructor, or creating an instance solely to delete it.
- Conduit and SpellSpace should delegate shared decisions to Meld; storage mutation belongs to the
  relevant Creations owner rather than ad hoc edits to private dictionaries in each facade.
- Owner ruling (2026-09-20): extend Creations with a dedicated purge operation. Do not implement
  purge through extract_spell_creations or its transfer/restore payload format.
- Owner simplification (2026-09-20): resolve the Spell using Meld's mechanics, select the authorized
  store from Existence and caller scope, then call Creations.purge(spell). Keep the core in these
  existing layers; no global lookup fallback or new scope/compiler system.
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
- [x] Instance shortcut through inspected class and existing lookup; single-instance retirement.
- [x] M0: Record owner intent and explicit no-implementation boundary.
- [x] M1: Discover store routing, caller identity and existing targeted removal/disposal contracts.
- [x] M2: Settle root terminology, lineage mode, many selection and error/return semantics.
- [x] M3: Create the approved bounded implementation task, patch contracts and failing regressions.
- [x] M4: Implement both input paths, scope routing, Creations retirement and single/multiple disposal.
- [x] M5: Complete documentation/assets after source approval and verify freshness.

## Original Proposed Story Split (Implemented Through the Bounded Task)
- [x] Discover and settle caller authority and per-Existence routing.
- [x] Implement Conduit/SpellSpace forwarding and shared Meld purge targeting.
- [x] Implement scoped retirement through Creations and required reuse coordination.
- [x] Qualify scope isolation, disposal/concurrency behavior and public documentation.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Create this epic before rebuilding existing Melder assets.
- [x] Retain source-backed decisions and exact reading pointers through implementation.
- Current planning/build-only task:
  `tickets/tasks/completed/2026-09-19_draft_purge_epic_and_refresh_assets_task.md`.
- Completed discovery, awaiting owner closure:
  `tickets/tasks/completed/2026-09-20_discover_purge_scope_ownership_task.md`.
- Implementation in source review:
  `tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md`.

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
- [x] No root privilege inferred merely from reaching a root-owned store.
- [x] No global purge, unbind or dependency cascade hidden in a local operation.
- [x] No disposal-policy redesign or new cache system without a demonstrated need.

## Open Questions
- Resolved: unique uses the live Spell owner; cluster uses the elected leader's store; lineage uses
  the resolving lineage's root. The caller must be the appropriate conduit itself.
- Resolved: SpellSpace is strictly local; it cannot purge conduit/root/cluster creations.
- Implemented: all retained many entries for the selected binding, count return, zero for no entries
  and aggregated disposal failures. Default purge_all=True; False retires the supplied instance.
- Supplied objects remain reachable through Spell.user_created_object after a store clear. Preserve
  the Creations-only boundary and do not promise fresh reconstruction or redesign their ownership.
- Selective purge does not revoke existing Python references or implicitly cascade to consumers.
  Follow existing writer/lifecycle coordination; do not add a universal draining mechanism.

## Decision Log
- Owner named the feature purge and wants it as meld's counterpart for retained creations.
- Owner selected Conduit and SpellSpace entry points, with Meld owning shared logic and caller context.
- Owner supplied the five scope rules above and explicitly prohibited implementation in this pass.
- At intake the enum's sixth lineage mode was undecided; the 2026-09-20 ruling below settles it.
- 2026-09-20: Owner selected lineage-root-only purge and strictly local SpellSpace purge.
- 2026-09-20: Owner selected native Creations extension, then simplified orchestration to resolved
  Spell -> authorized store -> removal, mirroring Meld selection.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/purge_scope_discovery_20260920/plan.md
- Build and characterization logs belong to their linked tasks.
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

- DATETIME: 2026-09-20T21:43:07Z
  TYPE: DECISION
  CLAIM: Discovery is complete and owner direction keeps the implementation narrow: normal Meld
    selection resolves the Spell, caller/Existence determines authority and store, and a native
    Creations.purge(spell) removes/disposes that store's entries. SpellSpace stays strictly local;
    lineage, cluster and unique require the specific root, leader and Spell owner respectively.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-20_discover_purge_scope_ownership_task.md
  - artifacts/purge_scope_discovery_20260920/plan.md
  - artifacts/purge_scope_discovery_20260920/characterization_final.log:1-2
  IMPACT: Expected core changes are four existing files. The 38 passing discovery checks establish
    current routing/reuse behavior; they do not represent purge implementation or feature acceptance.
  NEXT: Implement the bounded plan when the owner directs that step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:26:14Z
  TYPE: FACT
  CLAIM: The bounded source implementation now includes multiple disposal for retained many
    instances through both facades. Creations shares its existing per-object cleanup mechanics,
    preserves ordering and aggregates failures; 226 focused source regressions pass.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md
  - artifacts/purge_implementation_20260920/multiple_disposal.log:1-5
  - src/melder/aether/conduit/creations/creations.py:228-320
  IMPACT: Source review is the current boundary. Actual-instance discovery remains deferred;
    documentation completion and generation wait for explicit owner code approval.
  NEXT: Owner reviews the source delivery before selecting the next tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:39:00Z
  TYPE: MEASURE
  CLAIM: Owner-requested reference discovery experiment passes 22 real-runtime cases. Normal Meld
    accepts instance references as name/frame/binding selectors; its lookup-only helper is reusable.
    Actual identity and scope membership are separate from that lookup. Named/frame qualifications
    remain necessary, and an arbitrary factory result does not identify its provider automatically.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md
  - artifacts/purge_implementation_20260920/instance_reference_discovery_final.log:1-26
  IMPACT: Future exact-instance purge can combine existing discovery with the original reference
    and identity checks inside the authorized store. No production instance support was implemented.
  NEXT: Discuss this bounded proposal before implementing the deferred reference-targeting tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:13:20Z
  TYPE: MEASURE
  CLAIM: Owner approved the two selector choices and implementation is complete at source level.
    Instance inputs inspect the class and enter existing lookup. Both concrete Meld doors retain
    scope authority; Creations owns paired single/all detachment, existing writer locks and disposal.
    All 270 focused tests and scoped lint pass; the public guide and docstrings are updated.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md
  - artifacts/purge_implementation_20260920/instance_purge_final.log:1-5
  - src/melder/aether/conduit/meld/meld.py:533-602
  - src/melder/aether/conduit/creations/creations.py:429-635
  IMPACT: No broader discovery machinery, regular meld change or asset generation was introduced.
    Canonical generated documentation remains deliberately held until source approval.
  NEXT: Owner reviews code before canonical documentation completion and regeneration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- Discovery/plan complete: the linked discovery task records source traces and 38 passing existing
  runtime characterization checks. The implementation subsequently added the two concrete Meld doors.
- Historical build follow-through: the planning/build task records freshness checks for 0.2.43.
  Those checks predate the current source refactors and do not establish current asset freshness.
- [x] Both selector paths and single/multiple-disposal source delivery: 270 focused tests pass.
- [x] Owner approves source before final documentation and asset regeneration.
- [x] Owner accepts the completed feature and recorded lifecycle limits.

## Noting Behavior
Keep program decisions and scope rules here; future child tasks own source findings and test evidence.

- DATETIME: 2026-09-21T00:37:37Z
  TYPE: DECISION
  CLAIM: Owner accepted purge epic turn-in. This ticket is complete; its retained evidence and
    any promoted patch contracts remain available through completed records.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md
  IMPACT: Close only the four accepted purge records. Other work remains routed separately.
  NEXT: none; this ticket is complete.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Both selector paths and single/multiple disposal are implemented; 270 focused source tests pass.
The active implementation task records the current code and evidence. ConduitMeld/SpellSpaceMeld
own scope policy; base Meld provides shared discovery; Creations owns retirement locks and existing
disposal mechanics. No extraction, global lookup fallback or public internal-Spell targeting.
SpellSpace stays strictly local; lineage/cluster/unique require their specific root/leader/owner.

Instance discovery is implemented as class inspection followed by existing lookup. Explicit selectors
remain a deliberate alternative; no reverse discovery index or automatic binding metadata recovery.
purge_all=False requires the supplied instance and removes only its entry from the authorized store.
Owner accepted turn-in. Canonical descriptions, affected source descriptors, indexes, graph and
source/repository assets are refreshed and checked. Validation evidence is retained and promoted
patch contracts archived. The next-version release draft is a separate deliverable; no release,
version bump, commit or push was performed by this closeout.
