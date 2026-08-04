# Epic: Add Overrides-Enabled Configuration and Spell Gate

## Metadata
- Epic ID: EPIC-2026-05-11-add-overrides-enabled-configuration-and-spell-gate
- Status: in_progress
- Owner: codex
- Agent Name: mojo_0
- Priority: p0
- Created: 2026-05-11T11:02:33Z
- Updated: 2026-05-11T11:14:47Z
- Target Window: 2026-Q2
- Related Program/Initiative: Override-free compile path preparation

## Problem / Opportunity
The current runtime assumes spell overrides are available whenever callers pass
`spell_override`, and spell-level mutation overlays only gate on dynamic mode.
That is too wide for the intended optimization direction. We want a
configuration-owned default that can flow into bound spells, so later work can
prune override-specific compile/runtime work when a spell does not allow
overrides.

This first slice is intentionally small. It does not rework Phase 10-12 yet.
It adds the configuration bit, ensures it reaches `Spell`, and enforces the
policy at the two user-visible entry points already in play:

- `Spell.apply_mutation_override(...)` / `clear_mutation_override(...)`
- `Meld.meld(..., spell_override=...)`

## MRP Alignment (Most Reasonable Product)
The MRP is not "optimize all phases now." The MRP is:

- one config-owned default posture for override enablement
- one spell-owned effective flag
- one consistent runtime gate so disabled spells fail fast when override
  behavior is requested

That gives the later compiler-path optimization work a stable policy seam
instead of forcing it to infer behavior from ad hoc callsites.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the first implementation slice:
  config item in `Configuration`, spell-owned switch, mutation-override gate,
  and `Meld.meld()` rejection when overrides are disabled.
- EXECUTION_BOUNDARY: implement only the small control-plane/runtime-gate slice;
  do not yet change Phase 10-12 planning behavior.
- DEPENDENCIES:
  - `src/melder/spellbook/configuration/configuration.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/spell.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - matching unit tests under `tests/unit/melder/`
- EXIT_GATE: config default exists, spell effective flag exists, mutation
  overrides are gated on dynamic mode + overrides-enabled, and `Meld.meld()`
  rejects override payloads for override-disabled spells.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the small slice requires
  touching later compiler phases or broad contract/mutation semantics.

## Goals (Outcomes)
- Add `overrides_enabled` to the Spellbook configuration surface.
- Ensure the flag survives Spellbook -> Aether frame posture translation.
- Add a spell-owned effective override flag seeded from configuration.
- Gate spell mutation overrides on both dynamic mode and overrides-enabled.
- Reject `spell_override` in `Meld.meld()` when the resolved spell has
  overrides disabled.

## Non-Goals (Explicit Exclusions)
- Skipping Phase 10 patch-map compilation.
- Collapsing Phase 11 variant generation.
- Reworking `CreationContextBuilder` assembly.
- Perf benchmarking or broad compiler optimization in this slice.

## Scope Boundaries
- In scope:
  - config property + fluent helper
  - aether-frame posture propagation
  - spell-owned flag
  - runtime gates in Spell and Meld
  - focused unit tests
- Out of scope:
  - phase pipeline pruning
  - override executor removal
  - mutation-research redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked to start with the small control-plane
  change before broader compile-path optimization work.

## Success Metrics
- The new configuration property is present and defaults to enabled.
- Existing and newly bound spells get a consistent effective flag.
- Disabled spells reject `spell_override` through `Meld.meld()`.
- Disabled spells reject mutation overlay APIs even in dynamic mode.

## Requirements (Functional + Non-Functional)
- Functional:
  - `Configuration` exposes `overrides_enabled`
  - `AethericFrameConfiguration` carries the new posture field
  - `Spell` stores the effective flag
  - `apply_mutation_override(...)` and `clear_mutation_override(...)` reject
    when overrides are disabled
  - `Meld.meld()` rejects override payloads for override-disabled spells
- Non-functional:
  - default remains enabled
  - no changes to later compiler phases in this slice
  - no handwaving around config fallback behavior

## Constraints / Assumptions
- The user chose enabled-by-default after considering the earlier disabled
  default.
- This slice should be safe even before later phase-compiler pruning lands.
- Existing runtime behavior for override-enabled spells must remain intact.

## Dependencies / External References
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`
- `codex/context_compass/tickets/epics/2026-05-11_investigate_aot_creation_context_override_disable_and_no_overrides_compiler_path_epic.md`

## Milestones (Track Progress)
- [ ] Milestone 1: add config + frame posture field
- [ ] Milestone 2: add spell flag and runtime gates
- [ ] Milestone 3: land focused unit coverage for the new gates

## Stories (Required to Complete)
- [ ] Story: add overrides-enabled configuration and frame posture propagation
- [ ] Story: add spell-owned effective flag and mutation override gate
- [ ] Story: gate `Meld.meld()` override payloads by spell policy

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: patch config/frame/spell/meld seams
- [ ] Task: update focused unit tests
- [ ] Task: verify no regression in default-enabled behavior

## Acceptance Criteria (Epic Done)
- `Configuration` exposes an enabled-by-default `overrides_enabled` property.
- `Spell` has a usable effective flag.
- Mutation override APIs fail fast when the spell disallows overrides.
- `Meld.meld()` fails fast when `spell_override` is passed to an
  override-disabled spell.

## Risks / Mitigations
- Risk: spells bound before conjure keep stale config-default state.
  Mitigation: refresh the effective flag during conduit ownership stamping.
- Risk: frame posture translation diverges from Spellbook configuration.
  Mitigation: thread the new property through `AethericFrameConfiguration`.
- Risk: default-enabled behavior regresses.
  Mitigation: keep the flag enabled by default and add targeted tests.

## Applicable Anti-Patterns
- [ ] No later-phase compiler pruning mixed into this first slice.
- [ ] No hidden override side doors left ungated in Spell or Meld.
- [ ] No behavior changes for override-enabled spells without tests.

## Validation / Test Approach
- Focused unit coverage for:
  - `Configuration`
  - `AethericFrameConfiguration`
  - `Spell` mutation override gates
  - `Meld.meld()` override gate
- Not run yet.

## Rollout / Adoption Plan
- Land the config and runtime gate slice first.
- Then use the flag as the control point for later Phase 10-12 pruning work.

## Open Questions
- Whether later per-spell explicit override policy should be user-facing or
  remain internal.
- Whether the frame posture flag will later influence Nexus/AR behavior or stay
  spell/runtime only.

## Decision Log
- 2026-05-11T11:02:33Z: Opened the small implementation slice requested by the
  user before broader compile-path work.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-11T11:02:33Z
  TYPE: FACT
  CLAIM: The current config/spell/runtime seams are already narrow enough for
    a bounded first patch. `Configuration` already owns runtime posture flags,
    `AethericFrameConfiguration` is the posture object that floats to Aether,
    `Spell` already owns dynamic-environment and mutation-overlay state, and
    `Meld.meld()` already centralizes `spell_override` admission before runtime
    execution.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py:86-99
  - src/melder/spellbook/configuration/configuration.py:447-458
  - src/melder/spellbook/configuration/configuration.py:879-905
  - src/melder/aether/aetheric_frame_configuration.py:18-33
  - src/melder/spellbook/spell.py:171-184
  - src/melder/spellbook/spell.py:1574-1666
  - src/melder/aether/conduit/meld/meld.py:224-331
  - src/melder/aether/conduit/meld/meld.py:1372-1438
  IMPACT: We can land the control-plane gate without widening into later phase
    compiler work yet.
  NEXT: patch config, frame posture, spell flag, and meld frontdoor in one
    bounded implementation pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-11T11:12:22Z
  TYPE: MEASURE
  CLAIM: The first override-policy control-plane slice is landed. `Configuration`
    now exposes `overrides_enabled` with default `True`, the default survives the
    Spellbook-to-frame posture translation, `Spell` now carries an effective
    `overrides_enabled` flag refreshed on conduit ownership stamping, mutation
    overrides now fail fast when overrides are disabled, and `Meld.meld()` now
    rejects `spell_override` when the resolved spell disables overrides. The
    focused unit ring for configuration, frame posture, spell behavior, and
    meld gating is green.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py:86-99
  - src/melder/spellbook/configuration/configuration.py:215-257
  - src/melder/spellbook/configuration/configuration.py:448-458
  - src/melder/spellbook/configuration/configuration.py:715-762
  - src/melder/aether/aetheric_frame_configuration.py:18-33
  - src/melder/aether/aetheric_frame_configuration.py:42-88
  - src/melder/spellbook/spell.py:171-184
  - src/melder/spellbook/spell.py:947-1001
  - src/melder/spellbook/spell.py:1612-1674
  - src/melder/aether/conduit/meld/meld.py:323-331
  - tests/unit/melder/spellbook/configuration/test_configuration.py:1-136
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:1-190
  - tests/unit/melder/spellbook/test_spell.py:1-1358
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1-1100
  IMPACT: The later Phase 10-12 pruning work now has a real policy seam to
    branch on instead of having to infer override posture from ad hoc runtime
    behavior.
  NEXT: if we continue, the next slice should use this flag to skip late
    override-specific compiler artifacts for override-disabled spells.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-11T11:14:20Z
  TYPE: FACT
  CLAIM: The first focused unit ring passed, but the broader component config
    lane exposed one policy mismatch: `overrides_enabled` was treated as a
    required explicit property during validation even though the intended
    contract is "enabled unless explicitly turned off." That means validation
    needs to seed the implicit default before required-property checks rather
    than forcing every fluent caller to set the flag manually.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:189-210
  - src/melder/spellbook/configuration/configuration.py:225-242
  IMPACT: The runtime policy is still correct, but the config contract needs
    one more fix so existing fluent configuration paths continue to work under
    the enabled-by-default semantics.
  NEXT: patch `Configuration.validate()` to apply the implicit default before
    required-property validation, then rerun the failing component file and the
    focused unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-11T11:14:47Z
  TYPE: MEASURE
  CLAIM: The enabled-by-default config contract is now corrected. Validation
    seeds `overrides_enabled=True` when callers omit it, so fluent config
    chains that set the rest of the required properties still finalize
    cleanly. The previously failing component config file now passes, and the
    original focused unit ring still passes after the fix.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py:223-242
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:189-210
  IMPACT: The first override-policy slice now matches the intended API
    contract: enabled unless explicitly turned off, without forcing extra
    boilerplate on existing configuration callers.
  NEXT: the next implementation slice can safely focus on Phase 10-12 pruning
    against this flag.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche
  order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic is the first implementation slice for override gating. It should
stop at config/frame/spell/meld control points and avoid changing the late
compiler phases until the policy seam is in place and working.
