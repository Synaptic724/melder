# Story: Prove and explain named scope lifecycle guarantees

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-validation-docs
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-06T17:17:54Z

## User Narrative
As a library user, I want clear examples and dependable naming/cleanup semantics so I can replace
an application-maintained scope registry without inheriting hidden lifecycle problems.

## Ticket Contract
- ENTRY_GATE: Owner-approved contracts and implementation tasks exist for all affected stories.
- EXECUTION_BOUNDARY: Focused tests, examples, public/system docs and necessary generated outputs.
- DEPENDENCIES: Directory/lifecycle, Crystallizer and Nexus/consumer stories.
- EXIT_GATE: Evidence-backed documentation and meaningful lifecycle/consumer tests are accepted.
- FAILURE_ESCALATION: Do not skip failing contracts, claim unrun coverage or broaden implementation silently.

## Acceptance / Validation Topics
- Name assignment, uniqueness, missing lookup and optional-name behavior in each selected mode.
- Root versus lesser capabilities and unchanged Existence-based ownership/sharing.
- Concurrent creation/collision/lookup versus cleanup at the documented ownership boundary.
- Pool return removes the old name; reacquisition does not expose stale name/projection/record state.
- Upgrade and parent/root destruction preserve directory/root accounting and cleanup exactly once.
- Nexus/Crystallizer consumers follow their selected inclusion/exclusion and replay contracts.
- Explain when naming is useful and when a direct reference is simpler.
- Explicitly distinguish cloud names from Autofac-style matching-lifetime tags.

## Documentation Targets
- Human examples under UX_and_AIX_experiences and relevant docs curriculum pages.
- Public architecture drawings if scope/discovery boundaries change.
- Canonical component/architecture documentation and graph descriptors where actual wiring changes.
- Regenerate only the affected build assets after implementation, never during design-only discovery.

## Tasks / Rollout
Implementation/test/doc tasks are created after discovery and owner decisions; this story is a draft scope.
Existing naming evidence is retained in tasks/2026-09-06_named_conduit_semantics_task.md.

## Concrete Baseline / Future Test Matrix
- Existing integration evidence: upgrade/name lookup, duplicate root name, and default root name (3 passed).
- Baseline probe: a setter label survives pool reuse and rejects reassignment in both modes.
  The new feature must reverse that outcome; do not promote the baseline observation into a desired-behavior test.
- Future cases: names with/without pooling, multiple parents/frames, collisions with live roots and
  lessers, acquisition-hook failures, same/different-name upgrades, explicit and parent cleanup.
- Root-only Aether/cluster behavior versus broader directory behavior; unchanged creation-store routing.
- Nexus active/pooled/removed records, names and ACL-filtered lookup.
- Crystallizer-off/on exclusion or approved inclusion, and live-host root-name collisions on restore.

## Notes
- DATETIME: 2026-09-06T17:37:21Z
  TYPE: PLAN
  CLAIM: Preserve current naming tests and add future contract tests around actual scope transitions
    and consumer outcomes, not attribute-presence assertions or renamed-scope lifetime assumptions.
  EVIDENCE:
  - tasks/2026-09-06_named_conduit_semantics_task.md
  - tasks/2026-09-06_named_conduit_cross_system_discovery_task.md
  IMPACT: No runtime change is justified merely to satisfy a speculative test.
  NEXT: Derive exact tests from owner-approved naming/pooling/projection contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Draft validation contract. No new testing suite, documentation rewrite or asset rebuild is authorized yet.
