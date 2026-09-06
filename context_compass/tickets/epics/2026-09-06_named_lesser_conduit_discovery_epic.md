# Epic: Named lesser conduits as discoverable live scopes

## Metadata
- Epic ID: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: in_progress
- Owner: codex
- Agent Name: codex_1
- Priority: p2
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-06T17:44:52Z
- Target Window: Owner-approved design first; implementation not yet authorized.

## Problem / Opportunity
Applications may need to locate a particular request, session, job, or other live scope without
maintaining their own conduit registry. A lesser conduit borrows binding definitions but can own
scoped creations. Naming should make that existing owner discoverable without promoting it into
a normal root, creating another Spellbook, or changing its instance lifetimes.

The value is shared scope discovery and operational tracking. It is not a new lifetime model,
automatic cleanup, asset ownership, or a substitute for keeping a direct reference when that is enough.
For a strictly local synchronous scope, a name adds little. It becomes useful when separate parts
of an application or inspection tools need to locate the same active scope.

## MRP Alignment
Define naming, lookup, ownership, pooling and projection/persistence semantics as one coherent
contract. Do not ship an index that outlives the scope or silently turns ephemeral lessers into roots.

## Ticket Contract
- ENTRY_GATE: Owner requested an epic and cross-system discovery; existing naming evidence is recorded.
- EXECUTION_BOUNDARY: Planning and source-backed discovery across conduit/frame/cloud/pooling,
  Crystallizer, Nexus, DevOps, consumers, tests and public documentation.
- DEPENDENCIES: Four draft stories below and the linked cross-system discovery task.
- EXIT_GATE: Agreed contracts, approved implementation, verified stories and owner acceptance.
- FAILURE_ESCALATION: No runtime edits until naming/mode/lifecycle and persistence decisions are approved.

## Goals
- Optional names identify live lesser conduits without changing their lesser status or existing lifetimes.
- ConduitCloud can locate an eligible named lesser as the same live object.
- Returning a lesser to its pool unregisters its discovery entry and clears its assigned name.
- Establish whether naming/discovery should work in automatic and dynamic mode; the owner is open to both.
- Make Nexus, Crystallizer and other consumers distinguish discoverable scopes from structural roots.

## Non-Goals
- Autofac-style InstancePerMatchingLifetimeScope or a new Existence mode.
- Scope promotion, new bindings, peer links, or compiler changes solely to obtain a name.
- A new lease/handle/snapshot protocol, distributed discovery, or post-cleanup object-use guarantees.
- Silent changes to frame root accounting, permissions, recording policy, or release workflows.

## Current Verified Baseline
- Normal roots are named and frame-unique. conjure() defaults to default; both automatic and dynamic
  roots are discoverable through the frame-owned cloud.
- Upgrade(name) creates a named normal root and requires dynamic mode.
- Lesser creation currently accepts logger only. The name setter permits unregistered labels,
  but this is not integrated with creation, cloud registration or pool-name reset.
- ConduitCloud borrows frame root-only maps, so its existing registry is not a generic scope directory.
- SpellSpace has no naming API. Scope storage is selected by Existence and identities, not names.
- Three naming/upgrade integration tests and an isolated name/lookup probe passed.
- Evidence owner: tickets/tasks/2026-09-06_named_conduit_semantics_task.md.

## Requirements
- Preserve the unnamed creation path and existing meld paths; naming work belongs at scope boundaries.
- Decide the namespace explicitly: frame-wide uniqueness versus parent-qualified names is still open.
- A cloud lookup returns a borrowed live conduit; it does not extend the owner's lifetime.
- Scope registration is not root registration and does not grant normal-conduit operations.
- Name publication must follow successful scope acquisition; cleanup/pool return must remove it before reuse.
- A collision or failed acquisition must not strand a registered name or corrupt the pool/parent relation.
- Root cleanup, explicit lesser cleanup, permanent destruction and upgrade each need defined index transitions.
- Any Nexus/Crystallizer inclusion, filtering and replay policy must be explicit, not an incidental effect
  of broadening an existing enumeration.

## Cross-System Impact Map (Source-Backed Initial Discovery)

| Surface | Current evidence | Design implication |
| --- | --- | --- |
| Conduit / pool | Names survive pooled reuse; setter then rejects the next name. | Clear/unregister on release; set/publish the new name on acquisition. |
| Frame / Cloud | Cloud borrows root maps; Aether APIs read those maps directly. | Separate scope discovery from root ownership and preserve explicit root queries. |
| Automatic / dynamic | Both modes create lessers and expose root cloud lookup. | Recommend discovery in both modes without changing graph-mutation gates. |
| Nexus records | Name/state/parent/root fields and separate root/cloud counts already exist. | Reuse those meanings; update publication/removal on named-scope transitions. |
| Nexus commands | ACL-checked named lookup ends at root-only Aether; static raw access is refused. | Decide explicit lesser-aware lookup without bypassing existing permissions. |
| Crystallizer | Only dynamic normal conduits emit; replay selects one conduit per book. | Recommend keeping named lessers ephemeral for this feature. |
| Restore collisions | Admission/replay call cloud.has_conduit_name. | Choose whether live lesser names reserve the same namespace as restored roots. |
| Clusters / transfer | Cluster membership requires normal; transfer enumerates root Aether ids. | Naming grants neither membership nor root/Spellbook ownership. |

Detailed source ranges and the two-mode pool probe are in the cross-system discovery task.

## Recommended Contract (Not Yet Owner-Approved)
- Optional named lesser discovery in both automatic and dynamic mode.
- Frame-wide unique active cloud names, reusable after the old scope unregisters. This preserves
  unambiguous bare-name lookup; parent-qualified names remain an alternative if the owner wants repeats.
- Root ownership, existing Existence modes, dynamic mutation gates and static-room restrictions remain.
- Lesser names remain live-process addresses, not persistence instructions or restart-stable scope identities.
- Keep Crystallizer's lesser exclusion; test the expanded-name collision behavior explicitly.
- Cloud lookup returns the live borrowed Conduit, not a new object, lease or ownership transfer.

## Decisions Before Implementation
1. Confirm both-mode naming/discovery rather than dynamic-only.
2. Confirm frame-wide active-name uniqueness versus parent-qualified names.
3. Decide cloud listing/root-filter behavior and the existing post-creation name setter contract.
4. Confirm ephemeral-only Crystallizer semantics and same-namespace restore collision rules.
5. Decide whether pooled Nexus records are removed or retained as unnamed pooled shells, and whether
   capability/codegen raw-name helpers broaden to named lessers through an ACL-preserving resolver.

## Stories
- [ ] STORY-2026-09-06-named-conduit-directory-lifecycle
  - tickets/stories/2026-09-06_named_conduit_directory_lifecycle_story.md
- [ ] STORY-2026-09-06-named-conduit-crystallizer-contract
  - tickets/stories/2026-09-06_named_conduit_crystallizer_contract_story.md
- [ ] STORY-2026-09-06-named-conduit-nexus-consumers
  - tickets/stories/2026-09-06_named_conduit_nexus_consumers_story.md
- [ ] STORY-2026-09-06-named-conduit-validation-docs
  - tickets/stories/2026-09-06_named_conduit_validation_docs_story.md

## Cross-Cutting Tasks
- Prior naming evidence: tickets/tasks/2026-09-06_named_conduit_semantics_task.md (review).
- Initial impact discovery: tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md (review).

## Milestones
- [x] Capture the existing naming/registration/lifetime findings.
- [x] Initial cross-system trace distinguishes discovery changes from root/persistence/permission boundaries.
- [ ] Obtain owner decisions on modes, namespace and ephemeral-scope recording/replay.
- [ ] Create precise implementation tasks and required patch contracts after decisions.
- [ ] Implement, verify, document and obtain acceptance.

## Acceptance Criteria
- Automatic/dynamic behavior and name uniqueness are documented and tested according to the agreed policy.
- Named lesser lookup returns the intended scope without root promotion or instance-lifetime changes.
- Cleanup removes discovery immediately; pool reuse does not inherit an earlier logical scope's name.
- Roots, names, ids and hierarchy remain coherent through duplicate attempts, nesting and upgrades.
- Crystallizer/Nexus/DevOps/root-only consumers retain their intended semantics.
- No speculative hot-path checks, unapproved snapshots, or changes to the compiler/lifetime model.
- Documentation and focused/full validation evidence match the implemented contract.

## Risks / Open Decisions
- Broadening the root map changes frame ownership and every root enumeration consumer.
- A discoverable lesser may be mistaken for a bindable/linkable root by commands or clients.
- Pooled conduit identity can outlive one logical scope; stale labels/projections/records need careful handling.
- Persisting a named ephemeral scope may require a different replay contract from structural root snapshots.
- Names do not make user-owned objects thread-safe or keep a scope alive after owner cleanup.
- The existing public name setter, type/empty-name rules and post-creation naming need a consistent contract.

## Validation / Rollout
Use targeted source traces and isolated probes during discovery. Later validate naming and cleanup
in both modes, duplicate names, parent/child teardown, pool reuse, lookup and existing lifetime behavior.
Add projection/record/replay tests only for the selected semantics. No benchmark claims without measurement.
No commits, pushes, asset regeneration or runtime implementation are authorized by this planning epic.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner authorized the epic and cross-subsystem discovery, not implementation.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-06T17:17:54Z
  TYPE: DECISION
  CLAIM: Owner wants an epic with value assessment, potential automatic/dynamic support,
    unregister/clear-on-pool behavior and Crystallizer/Nexus/other-subsystem implications.
    These are design candidates; implementation approval has not been given.
  EVIDENCE:
  - tickets/tasks/2026-09-06_named_conduit_semantics_task.md
  - Owner's epic/discovery request in the current conversation.
  IMPACT: Preserve prior findings and investigate the whole lifecycle before selecting implementation.
  NEXT: Trace discovery versus root ownership, then Nexus and Crystallizer consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:44:52Z
  TYPE: DECISION_REQUEST
  CLAIM: Initial impact discovery supports optional discovery in both modes, with active frame-wide
    names and ephemeral lesser lifetimes as the recommended contract. Nexus already has suitable
    fields but needs lifecycle-consistent publication; Crystallizer should keep lesser exclusion
    unless the owner explicitly wants child replay. Existing root queries and permission gates stay.
  EVIDENCE:
  - tickets/tasks/2026-09-06_named_conduit_cross_system_discovery_task.md
  - tickets/stories/2026-09-06_named_conduit_directory_lifecycle_story.md
  - tickets/stories/2026-09-06_named_conduit_crystallizer_contract_story.md
  - tickets/stories/2026-09-06_named_conduit_nexus_consumers_story.md
  IMPACT: The feature has a bounded value proposition and a cross-system contract. It is not yet
    authorized for implementation; five explicit choices are listed above.
  NEXT: Owner selects naming/discovery semantics, then implementation tasks can be defined precisely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Noting Behavior
Keep program choices and cross-story implications here; detailed source evidence stays in the discovery task.

## Context / Handoff Summary
Initial discovery is recorded, with exact source locations in the cross-system task and four draft stories.
Two-mode probing confirmed labels persist across pool reuse today. Proposed feature is naming/discovery,
not tagged lifetime selection; both modes and ephemeral lesser names are recommended but not yet approved.
Resolve the Decisions Before Implementation section before runtime edits or new implementation tasks.
