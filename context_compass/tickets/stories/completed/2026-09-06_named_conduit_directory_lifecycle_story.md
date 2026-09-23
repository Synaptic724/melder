# Story: Name lesser conduits without changing scope ownership

- Completed: 2026-09-23T11:55:35Z
- Summary: Owner-authorized named-lesser feature turn-in. Runtime, structural replay,
  Nexus, examples and canonical documentation are delivered; package assets remain held.
- Closure evidence: artifacts/named_lesser_finish_20260923/validation.md

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-directory-lifecycle
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: done
- Owner: codex
- Agent Name: codex_1, updater_0
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-23T11:55:35Z

## User Narrative
Stage 1 is implemented; 446 related tests pass. Review and validation receipt:
- tickets/tasks/completed/2026-09-22_implement_named_lesser_directory_lifecycle_task.md

2026-09-22 accepted direction: active names are unique across the frame, shared with normal roots;
discovery works in automatic and dynamic mode. Recording keeps its existing dynamic-mode policy.
Current source/lock/failure trace and implementation regression matrix:
- tickets/tasks/completed/2026-09-22_refresh_named_lesser_conduit_plan_task.md

As an application developer, I want to find an active named lesser conduit without maintaining
another registry or promoting the scope into a root.

## Value / MRP Alignment
Discovery is useful across independent application surfaces. Preserve the existing ownership and
instance-lifetime model while making scope boundaries consistently nameable and discoverable.

## Ticket Contract
- ENTRY_GATE: Accepted naming rules, current source trace and a scoped low-level patch/test contract.
- EXECUTION_BOUNDARY: Conduit/Cloud naming, acquire/cleanup/promotion and focused tests, with only
  necessary frame root-registration and Spellbook existing-conduit name-check bridges.
- DEPENDENCIES: Current discovery task; later Nexus/Crystallizer integration is separately sequenced.
- EXIT_GATE: Naming and removal work without altering root accounting or unnamed/meld behavior.
- FAILURE_ESCALATION: Resolve local name lifecycle correctness; catalogue later subsystem work separately.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Owner-authorized lifecycle implementation and focused regressions pass; review precedes turn-in.

## Requirements
- Optional name at lesser creation; preserve its current lesser capabilities and parent ownership.
- Naming/discovery works in automatic and dynamic mode without changing graph-mutation gates.
- Names are frame-wide unique across roots and other active named lessers.
- A lesser receives its optional name only through the creation call; later naming/renaming is excluded.
- Prewarming prepares unnamed shells. Initialize the chosen shell's name for the caller's scope at checkout.
- Only named conduits enter cloud discovery. Unnamed lessers skip cloud registration/unregistration.
- Unregister and clear a named lesser before pool return; reacquisition publishes only the new logical scope.
- Apply optional naming to both fresh and pooled acquisition because reuse does not rerun __init__.
- Define upgrade, permanent destruction, nested cleanup and failed acquisition/collision transitions.
- Existing root registration remains root-only; enumerate all current consumers before changing cloud lists.
- Preserve the necessary lifecycle points for the later Crystallizer/Nexus stories; do not implement
  their sinks, replay or projection coordination in this first low-level slice.
- Prewarmed idle shells are capacity, not active named structural scopes; do not replay their created objects.

## Source Orientation
- src/melder/aether/conduit/conduit.py:533-585, 1557-1648, 1960-2142, 2227-2385
- src/melder/aether/conduit/conduit.py:195-420, 1365-1384
- src/melder/aether/conduit/conduit.py:1161-1211
- src/melder/aether/conduit/conduit_pool.py:108-161
- src/melder/utilities/general_base/abstract_elastic_pool.py:114-190, 290-382
- src/melder/aether/aetheric_frame/aetheric_frame.py:160-196, 340-411
- src/melder/aether/aetheric_frame/conduit_cloud.py:321-605
- Prior evidence: tasks/2026-09-06_named_conduit_semantics_task.md.

## Tasks / Validation
Owner selected this as the first small implementation slice; see the epic's Implementation Catalogue.
Create its scoped patch and focused regressions without making later integration choices prerequisites.
Test both modes, optional names, collisions, concurrent name publication, cleanup, reuse and upgrade.
Include prewarmed-shell checkout and rejection of later lesser naming/renaming.
No new leases, wrappers, defensive snapshots, or checks added to every meld solely for naming.

## Promotion Acceptance Cases
- Unnamed -> normal X registers X for the same object/ID.
- Named X -> normal X keeps one entry and does not collide with itself.
- Named A -> normal B retires A and publishes B for the same object/ID.
- Collision with another conduit preserves original state and both existing owners.
- Pre-attachment failure restores the original lesser name and discovery entry.
- Post-attachment failure follows existing normal-conjure cleanup responsibility.
- Normal cleanup removes its current directory entry through the root bridge.
- These tests adapt naming around the delivered graduation route; they do not redesign Book ownership.

## Decisions and Remaining Work
- Implemented ordering: name assigned before activation; Cloud publication with parent attachment;
  retirement after disposal/detach and before pool publication. Advisory hook failures remain advisory.
- Live-restore coordination is tracked by the later Crystallizer story, not a gate for this slice.
- Cloud enumeration now covers named normal/lesser scopes; existing frame/Aether root maps stay root-only.

## Findings and Evidence
- Lesser initialization currently forces None. The pooled-name probe used the separate post-init setter,
  reproducing label persistence and rename rejection rather than supported named lesser construction.
- Root-name storage and ownership are tied together today; Aether lists/names/counts bypass the cloud facade.
- Required transition coverage: unnamed pooled shell -> named active at creation; active -> pool; pooled -> acquired;
  named lesser -> named normal; collision/failure; parent/root teardown.
- Publication ordering relative to activation/post-created hooks needs an explicit contract.
- Evidence: tasks/2026-09-06_named_conduit_cross_system_discovery_task.md.

## Notes
- DATETIME: 2026-09-06T17:37:21Z
  TYPE: FACT
  CLAIM: The two-mode pool probe confirms that resetting the existing name field is required;
    cloud registration alone is not a complete named-scope lifecycle.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:1588-1630
  IMPACT: Name lifecycle belongs in acquire/release/upgrade, not in every meld.
  NEXT: Resolve mode/namespace/setter choices before task-level implementation planning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:08:52Z
  TYPE: DECISION
  CLAIM: Owner selected named-only cloud discovery, accepting registration/unregistration overhead
    only for the named path. Release must remove the discovery entry and clear the name before the
    pool exposes the shell. Unnamed release skips unregistration. Both acquisition branches need
    naming treatment because pooled shells bypass the constructor.
  EVIDENCE:
  - Owner's 2026-09-07 clarification in this conversation.
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:1365-1384
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/aether/conduit/conduit_pool.py:136-161
  IMPACT: Preserve the unnamed path and define name/registration consistency across failure, hooks,
    setter use, upgrade and permanent destruction. Exact overhead is unmeasured.
  NEXT: Settle the namespace and assignment/publication contract before creating implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T11:14:34Z
  TYPE: DECISION
  CLAIM: Owner restricted naming to the lesser-creation call. The pool may already hold prepared
    unnamed shells, so name initialization belongs to the caller's new scope use. Later naming or
    renaming is excluded; internal release clears the name for a future acquisition.
  EVIDENCE:
  - Owner's creation-only naming clarification in this conversation.
  - src/melder/aether/conduit/conduit.py:1161-1211
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/aether/conduit/conduit_pool.py:106-161
  IMPACT: Do not design a public rename workflow or rely on __init__ running for every scope request.
    The live path uses specialized pool methods rather than base prepare_object.
  NEXT: Resolve the remaining namespace, publication and consumer contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:09:14Z
  TYPE: MEASURE
  CLAIM: The stage-1 lifecycle and promotion implementation passes 446 related tests. Named publication
    happens with parent attachment; return unregisters/clears only named scopes before idle publication.
    Cloud listing covers named scopes while frame/cluster ownership remains normal-only.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-22_implement_named_lesser_directory_lifecycle_task.md
  - artifacts/named_lesser_directory_20260922/qualified.xml
  IMPACT: Source is ready for review; later structural replay and projection work remain separate.
  NEXT: Review this slice before story turn-in or later integration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Stage 1 implemented and ready for review: creation-only names, named Cloud lookup, one conditional on
unnamed return, named retirement before pool reuse, and collision-safe promotion/name rollback.
446 related tests pass; implementation task has the source contract and complete validation receipt.
Crystallizer and Nexus remain required later stages; packaged generation remains held.

## Closure Transition
- from_state: review
- to_state: done
- transition_reason: Owner requested full finish and turn-in; qualification is complete.
