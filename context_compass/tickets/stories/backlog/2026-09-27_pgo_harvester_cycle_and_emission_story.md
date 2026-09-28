# Story: PGO harvester - PGO=true turns the cycle on, a spell that finishes its cycle emits its harvest and keeps it

## Metadata
- Story ID: STORY-2026-09-27-pgo-harvester-cycle-and-emission
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T23:54:47Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want one switch (PGO on) that arms a harvester: every spell's creation context runs its
PGO cycle (the probe window), and when a spell finishes its cycle it actively emits what it harvested - after
the cycle, off the warm path - into a durable, spell-based slot and to the areas that consume it (the DevOps
station report, the sink model that already exists, other holders of the same spell), and then regenerates
itself, so that the whole thing happens dynamically per spell while the process lives.

## Value / MRP Alignment
This is the spine the other stories hang on: the probe body (window), the capture (fields), the report (a
consumer of the emission), versioning (what the spell does with its harvest), persistence (where the durable
state may also go). It is spell-based because the CreationContext is spell-owned (`spell._creation_context`,
published through `_creation_context_switch`) and the meld doors hold the context and re-read its executor
slots per call - so a spell can change what builds it in place, without the doors noticing. Emission after the
cycle keeps the warm path clean; the sink model (value-only twins pushed at confirmation points, no-ops while
inactive) is the pattern for sharing without coupling.

## Ticket Contract
- ENTRY_GATE: owner's pick; patch docs (architecture: the PGO cycle and emission; component: Meld Resolution
  Runtime (creation context), Spellbook Configuration, DevOps Control Plane; code description: cycle end,
  emission, regeneration ordering) before src.
- EXECUTION_BOUNDARY: `SpellbookConfiguration` (the PGO switch and window sizes), `creation_context.py`
  (cycle state, the emission call, the durable profile reference), `Spell` (a value-only profile slot), the
  DevOps registry (the fact family the emission writes), the emitter hydrators (probe variant publish),
  tests.
- DEPENDENCIES: STORY-2026-09-27-probe-creation-context-harvest (the window and counters);
  STORY-2026-09-27-creation-context-versioning (what happens after the emission).
- EXIT_GATE: PGO off is byte-identical; PGO on runs one cycle per spell, emits once at cycle end off the
  warm path, the durable slot holds the profile, the registry has the fact, the report reads it; a rebuilt
  context restarts its cycle; suites green; cost within the probe bound.
- FAILURE_ESCALATION: DECISION_REQUEST on the emission's consumers (which areas) and on cycle restart
  policy; BLOCKER if cycle end cannot run outside every build lock.

## Requirements (Functional)
- PGO switch on the configuration (`pgo_enabled`, default False) plus window size and timed-mode flags;
  frozen with the configuration like every other property.
- Cycle: a context published with PGO on starts in the probe version; the window counts creations; the cycle
  ends at the trigger point (N creations, or a natural window if it comes first).
- Cycle end, on the thread that completed the last creation and after that creation returned: build the
  value-only profile, store it in the spell's profile slot (durable for the spell's life), report it to the
  DevOps registry as a fact, hand it to the sink model if the crystallizer is active (no-op otherwise), then
  swap the plain (or regenerated) executors into the same slots.
- Sharing: in a dynamic world the context is shared by every conduit that melds the spell, so one harvest
  serves them all; in automatic worlds each book's context harvests its own.
- Restart: a rebuild (structural or resolution) starts the new context plain, and with PGO on it re-arms one
  cycle; a reset verb re-arms explicitly.

## Requirements (Non-Functional)
- Emission never runs under a build lock or inside a rebuild window; it runs after the creation that ended
  the window has been returned to the caller.
- PGO off: no cycle state exists and nothing is emitted; differential test.
- Profile is value-only (JSON-able); no user object identities.

## Scope Boundaries
- In scope: the switch, the cycle state on the context, cycle end and emission, the durable slot, the
  registry fact, the sink hand-off, restart/reset, tests, docs.
- Out of scope: the probe body itself (its story), the report rendering (its story), what the regenerated
  version contains (versioning and style stories), cross-process persistence (its story).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's direction (2026-09-27T23:54:47Z); opens when the owner picks it.

## Dependencies / Related Work
- src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110 (spell-owned context; self-
  replacing slots; doors re-read slots per call)
- src/melder/aether/conduit/meld/creation_context/creation_context.py:189-240 (`load_cached(...,
  publish=True)`: publication through `spell._creation_context_switch`, previous context cleaned)
- src/melder/aether/spellbook/spell.py:483-490 (`_creation_context`, `_creation_context_switch`)
- src/melder/crystallizer/crystallizer.py:1471-1560 (`emit_spell_activity`, `emit`: the sink model - no-ops
  while inactive)
- STORY-2026-09-27-probe-creation-context-harvest; STORY-2026-09-27-creation-context-versioning;
  STORY-2026-09-27-creation-profile-report
- STORY-2026-09-28-harvest-driven-phase-regeneration (the second part: what the emission triggers)

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how the cycle state, the profile reference and the emission call land on `CreationContext`
      (slots, executor variant, guard, cleanup ordering) and where cycle end can run outside every lock; patch docs.
- [ ] Task: implement the switch, the cycle and the emission with a stub consumer (registry fact) behind PGO=false.
- [ ] Task: wire the sink hand-off and the restart/reset rules; component tests over a dynamic world with two
      conduits sharing one context.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- With PGO on, a spell melded N times emits exactly one profile at the Nth creation, after it returned; the
  spell's slot and the registry hold it; the executors are plain (or regenerated) from the N+1th meld; PGO
  off is identical to today.

## Validation / Test Plan
- Unit tests on cycle state and emission ordering; component tests on a dynamic world with two conduits; the
  differential matrix; a VM cost run of the cycle against the probe bound.

## UX / API / Data Notes
- `SpellbookConfiguration.pgo_enabled` (name to settle with the owner); the profile is readable through the
  report story's describe verb.

## Risks / Mitigations
- Emission on the warm path -> after the creation returns, on the completing thread, never under a lock.
- Two threads end the window together -> the swap is idempotent (same executors), the emission is guarded by
  a one-shot flag on the context.
- A cycle that never ends (a spell melded fewer than N times) -> natural windows end it; a reset verb
  exists.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Which areas receive the emission beyond the spell slot and the registry: the crystallizer sink, Nexus
  viewers, other books holding the same spell in automatic worlds?
- Does the cycle restart after every rebuild, or only when the structural snapshot says the shape changed?
- Is the durable state the spell's slot only, or also the cache manifest (persisted-profiles story)?

## Decision Log
- 2026-09-27T23:54:47Z (owner): PGO mode - turn it on, harvest, implement the result in a durable, spell-
  based state so it happens dynamically; a harvester armed by PGO=true; a spell that finishes its cycle
  actively emits its data after the cycle and shares it with some areas; every idea must fit the
  creation_context object.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and runs shared by the epic; new runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - PGO switch; harvester cycle; emission; durable spell slot; sharing
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:54:47Z
  TYPE: FACT
  CLAIM: The CreationContext is spell-owned and published through `spell._creation_context_switch`; its executor
    slots are self-replacing and the meld doors hold the context, re-reading the slots per call - so a version
    swap in place needs no door invalidation, while replacing the context object bumps the door epoch through
    cleanup. `load_cached(..., publish=True)` is the existing publication path from prebuilt executors.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:189-240
  - src/melder/aether/spellbook/spell.py:483-490
  IMPACT: The harvester's swap is an in-place slot write at cycle end; the regenerated version needs no rebuild
    window unless the plan itself changes shape.
  NEXT: owner picks; the investigation task maps cycle state and emission onto the context's slots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-27T23:54:47Z: DRAFT. Collected from the owner's direction (PGO mode, harvester, emission after the cycle,
durable spell-based state); not routed. Opens when the owner picks it.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
