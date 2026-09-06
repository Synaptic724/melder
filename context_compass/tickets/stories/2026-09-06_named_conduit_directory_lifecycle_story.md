# Story: Name lesser conduits without changing scope ownership

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-directory-lifecycle
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-06T17:17:54Z

## User Narrative
As an application developer, I want to find an active named lesser conduit without maintaining
another registry or promoting the scope into a root.

## Value / MRP Alignment
Discovery is useful across independent application surfaces. Preserve the existing ownership and
instance-lifetime model while making scope boundaries consistently nameable and discoverable.

## Ticket Contract
- ENTRY_GATE: Epic decisions on modes, namespace, setter and pool lifecycle are approved.
- EXECUTION_BOUNDARY: Conduit/frame/cloud discovery, scope acquisition/cleanup/upgrade and focused tests.
- DEPENDENCIES: Cross-system discovery task; Nexus/Crystallizer decisions before rollout.
- EXIT_GATE: Naming and removal work without altering root accounting or unnamed/meld behavior.
- FAILURE_ESCALATION: No runtime implementation while mode/namespace/lifecycle decisions are unresolved.

## Requirements
- Optional name at lesser creation; preserve its current lesser capabilities and parent ownership.
- Choose automatic/dynamic support explicitly; no automatic graph mutation is implied by directory writes.
- Decide frame-wide versus parent-qualified names and collisions with roots/other active lessers.
- Define public post-creation setter behavior; no silently stale directory after naming.
- Unregister and clear names before pool return; reacquisition publishes only the new logical scope.
- Define upgrade, permanent destruction, nested cleanup and failed acquisition/collision transitions.
- Existing root registration remains root-only; enumerate all current consumers before changing cloud lists.

## Source Orientation
- src/melder/aether/conduit/conduit.py:533-585, 1557-1648, 1960-2142, 2227-2385
- src/melder/aether/conduit/conduit_pool.py:108-161
- src/melder/aether/aetheric_frame/aetheric_frame.py:160-196, 340-411
- src/melder/aether/aetheric_frame/conduit_cloud.py:321-605
- Prior evidence: tasks/2026-09-06_named_conduit_semantics_task.md.

## Tasks / Validation
Create exact implementation tasks after the cross-system findings and owner decisions.
Test both modes, optional names, collisions, concurrent name publication, cleanup, reuse and upgrade.
No new leases, wrappers, defensive snapshots, or checks added to every meld solely for naming.

## Open Questions
- Namespace and post-creation setter policy.
- Whether cloud enumeration broadens by default or exposes explicit root/all-scope views.

## Findings and Evidence
- The current pooled-name probe reproduces label persistence and rename rejection in both modes.
- Root-name storage and ownership are tied together today; Aether lists/names/counts bypass the cloud facade.
- Required transition coverage: unnamed -> named active; active -> pool; pooled -> acquired;
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

## Context / Handoff Summary
Draft design scope only. The existing setter label is not a supported discovery/pool lifecycle yet.
