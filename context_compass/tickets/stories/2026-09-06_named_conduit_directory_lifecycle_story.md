# Story: Name lesser conduits without changing scope ownership

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-directory-lifecycle
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1, updater_0
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-07T11:46:34Z

## User Narrative
As an application developer, I want to find an active named lesser conduit without maintaining
another registry or promoting the scope into a root.

## Value / MRP Alignment
Discovery is useful across independent application surfaces. Preserve the existing ownership and
instance-lifetime model while making scope boundaries consistently nameable and discoverable.

## Ticket Contract
- ENTRY_GATE: Remaining epic decisions on modes, namespace, publication and consumers are approved.
- EXECUTION_BOUNDARY: Conduit/frame/cloud discovery, scope acquisition/cleanup/upgrade and focused tests.
- DEPENDENCIES: Cross-system discovery task; Nexus/Crystallizer decisions before rollout.
- EXIT_GATE: Naming and removal work without altering root accounting or unnamed/meld behavior.
- FAILURE_ESCALATION: No runtime implementation while mode/namespace/lifecycle decisions are unresolved.

## Requirements
- Optional name at lesser creation; preserve its current lesser capabilities and parent ownership.
- Choose automatic/dynamic support explicitly; no automatic graph mutation is implied by directory writes.
- Decide frame-wide versus parent-qualified names and collisions with roots/other active lessers.
- A lesser receives its optional name only through the creation call; later naming/renaming is excluded.
- Prewarming prepares unnamed shells. Initialize the chosen shell's name for the caller's scope at checkout.
- Only named conduits enter cloud discovery. Unnamed lessers skip cloud registration/unregistration.
- Unregister and clear a named lesser before pool return; reacquisition publishes only the new logical scope.
- Apply optional naming to both fresh and pooled acquisition because reuse does not rerun __init__.
- Define upgrade, permanent destruction, nested cleanup and failed acquisition/collision transitions.
- Existing root registration remains root-only; enumerate all current consumers before changing cloud lists.
- Coordinate successful creation-time name/parent publication with required Crystallizer structural emission.
- On release, remove the named scope from current structural recording as well as cloud discovery before
  the shell is reusable; preserve enough identity before clearing the name and detaching parent state.
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
Create exact implementation tasks after the cross-system findings and owner decisions.
Test both modes, optional names, collisions, concurrent name publication, cleanup, reuse and upgrade.
Include prewarmed-shell checkout and rejection of later lesser naming/renaming.
No new leases, wrappers, defensive snapshots, or checks added to every meld solely for naming.

## Open Questions
- Namespace, name validation and publication ordering; creation-only lesser naming is settled.
- Whether cloud enumeration broadens by default or exposes explicit root/all-scope views.

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

## Context / Handoff Summary
Draft design scope only. The existing setter label is not a supported discovery/pool lifecycle yet.
Named-only discovery and conditional unregister/name reset before pool reuse are owner-confirmed.
Creation-only naming is owner-confirmed; prewarmed shells receive a name only for the requested use.
Owner additionally requires named-lesser structural persistence. Coordinate record emission/removal with
creation/release and the shared-book hierarchy. Remaining mode, namespace and integration details precede implementation.
