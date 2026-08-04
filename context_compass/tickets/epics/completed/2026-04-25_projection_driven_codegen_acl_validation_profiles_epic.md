# Epic: Projection-Driven Codegen ACL Validation Profiles
- Completed: 2026-04-25T19:08:31Z
- Summary: Closed after the projection-driven codegen ACL validation slice
  landed and validated green, including deeper reflection handling,
  recursive-codegen posture, and the new `full_access` profile.

## Metadata
- Epic ID: EPIC-2026-04-25-projection-driven-codegen-acl-validation-profiles
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T17:51:02Z
- Updated: 2026-04-25T19:08:31Z
- Target Window: 2026-Q2
- Related Program/Initiative: Codegen ACL composition and validation

## Problem / Opportunity
The codegen runtime already has the right lower authority:
- `CodegenProjection`
- `FrameACLCodegenConfiguration`
- `CompiledFrameACLAccessSurface`

But the current `CodegenSystem` is not consuming that authority deeply enough.
Today:
- `CodegenValidator` is still mostly static and returns
  `codegen_validation_not_implemented` when a script passes the current checks.
- the import strategy blocks all imports, regardless of selected codegen
  profile
- the builtin strategy uses one hardcoded denylist instead of ACL/profile truth
- the namespace configuration still reflects the old
  `rift/space/target/frame_name` contract instead of the later
  `viewer/command/workstation/codegen` direction
- the compiled access surface does not yet answer validator-facing questions
  like import posture, builtin denylist, or dunder/reflection posture

The opportunity is to make codegen validation genuinely projection-driven:
- extend the existing codegen ACL profile system
- compile validator-facing codegen answers into the existing compiled access
  surface
- let `CodegenValidator` consume the projection directly
- keep permissive codegen useful for real work instead of over-restricting
  ordinary Python

## MRP Alignment (Most Reasonable Product)
The MRP is not a fake Python jail.

The MRP is:
- keep ordinary Python useful for real agent work
- govern the parts we can inspect well
- derive validation posture from the real ACL projection
- keep permissive genuinely permissive
- keep safe/hybrid/precision composable later without inventing a second policy
  model

## Ticket Contract
- ENTRY_GATE: the user explicitly approved implementation of projection-driven
  codegen ACL validation and import/builtin/meta controls.
- EXECUTION_BOUNDARY: codegen ACL profiles, compiler output, validator
  strategies, namespace contract, and focused unit coverage only.
- DEPENDENCIES:
  - `src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py`
  - `src/melder/aether/nexus/acl/configurations/profiles/codegen/`
  - `src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py`
  - `src/melder/aether/nexus/acl/frame_acl_compiler.py`
  - `src/melder/aether/nexus/acl/validator/frame_acl_validator.py`
  - `src/melder/aether/nexus/rift/projection/codegen_projection.py`
  - `src/melder/aether/nexus/rift/codegen_system/validation/`
  - `src/melder/aether/nexus/rift/codegen_system/namespace/`
  - `tests/unit/melder/aether/test_nexus.py`
- EXIT_GATE: codegen validation and namespace behavior are driven by the
  selected projection/profile, permissive allows broad work, safe/hybrid/
  precision enforce the intended import/builtin/meta limits, and the focused
  unit ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the selected projection model
  proves insufficient and the work would require a second policy system or a
  broader ACL redesign.

## Goals (Outcomes)
- Extend codegen ACL profiles with import/builtin/meta controls using the
  existing ruleset model.
- Compile validator-facing codegen answers into the existing compiled access
  surface.
- Make `CodegenValidator` accept valid scripts instead of returning
  `not_implemented`.
- Keep ordinary Python usable while validating imports, dangerous builtins,
  dunder access, and reflection/meta behavior.
- Move the namespace contract to `viewer`, `command`, `workstation`, `codegen`.

## Non-Goals (Explicit Exclusions)
- Full runtime sandboxing.
- Re-authorizing `viewer` / `command` method surfaces through codegen ACL.
- Broader AR or room-mode redesign.
- New public codegen APIs beyond the existing `validate_codegen(...)` /
  `execute_codegen(...)` surface.

## Scope Boundaries
- In scope:
  - codegen profile rule additions
  - compiled access surface extensions
  - validator strategy refactor
  - namespace contract update
  - focused tests
- Out of scope:
  - raw `viewer` / `command` ACL redesign
  - sentinel / external supervision systems
  - product-side buffering/orchestration semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an implementation epic for
  projection-driven codegen validation profiles and import policy.

## Success Metrics
- One active epic owns the codegen ACL validation lane.
- Projection-driven validation replaces the current static/hardcoded behavior.
- Valid scripts are accepted under the selected profile instead of returning
  `codegen_validation_not_implemented`.

## Requirements (Functional + Non-Functional)
- Functional:
  - support profile-driven imports
  - support profile-driven import allow/deny lists
  - support profile-driven builtin deny lists
  - support profile-driven dunder/reflection posture
  - support a broad permissive profile
  - move the namespace to `viewer` / `command` / `workstation` / `codegen`
- Non-functional:
  - no second policy authority
  - no broad bans on normal Python work patterns
  - composable rules for later profile refinement

## Stories (Required to Complete)
- [ ] Story: extend codegen ACL profile and compiled-surface answers for imports, builtins, and meta behavior
- [ ] Story: refactor validator and namespace wiring to consume the projection-driven codegen answers
- [ ] Story: add focused unit coverage for safe, hybrid, permissive, and precision validation behavior

## Open Questions
- Which stdlib import roots should ship in `hybrid` versus `permissive` by
  default?
- Whether `precision` should stay close to `hybrid` initially or carry a
  distinct stricter import list immediately.

## Decision Log
- 2026-04-25: the selected `CodegenProjection` and its compiled ACL surface are
  the source of truth; no second execution-policy system should be introduced.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T17:51:02Z
  TYPE: FACT
  CLAIM: The existing codegen ACL stack already has the right ownership split:
    reusable profiles, applied frame-local codegen configurations, and a
    compiled access surface. The missing work is consuming that stack in the
    codegen runtime rather than inventing another policy model.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:1-380
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile.py:1-223
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:1-200
  IMPACT: This lane should extend and consume the existing ACL machinery rather
    than replacing it.
  NEXT: stage the focused story/task and patch docs, then implement the
    profile/compiler/validator slice directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: MEASURE
  CLAIM: The first implementation slice is now landed and green. The runtime
    no longer relies on a hardcoded codegen validator stub; it now consumes
    the compiled codegen ACL surface for import, builtin, dunder, and
    reflection posture, and the namespace contract is aligned to the agreed
    room-tool shape.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:90-141
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:186-249
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:33-178
  IMPACT: The epic has moved from abstract design into reviewable runtime
    implementation.
  NEXT: decide whether the next lane is deeper codegen ACL composition or
    closure of this focused validation-profile slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The next obvious refinement tranche is also landed. The slice now
    includes explicit reflection-policy validation and a genuinely narrower
    `precision` import posture on top of the initial projection-driven
    import/builtin/dunder work.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:142-163
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_reflection_policy_strategy.py:1-89
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:44-62
  IMPACT: The epic now owns a more complete codegen ACL validation slice rather
    than only the first compiler/namespace landing.
  NEXT: decide whether to close this epic or continue into deeper codegen ACL
    features such as additional meta/inspection policy or direct recursive-codegen posture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: Recursive codegen posture is now implemented inside the same epic.
    The selected projection now governs whether nested codegen calls are
    available, and the namespace exposes a dedicated wrapper rather than the
    raw internal system.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:164-185
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_control_surface.py:1-138
  IMPACT: The epic now owns a fuller codegen ACL slice than the original
    import/builtin-only landing.
  NEXT: decide whether the next lane is closure or deeper meta-policy work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The epic now also includes a deeper reflection-policy pass plus a new
    `full_access` profile above `permissive`. That gives the codegen ACL ladder
    a real unconstrained top-end while keeping the stricter profiles usable and
    composable.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:186-207
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/full_access_profile.py:1-114
  IMPACT: The epic has moved beyond the initial projection wiring into a fuller
    ACL/profile design slice.
  NEXT: decide whether to close this epic or continue into even deeper
    meta/inspection policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic owns the projection-driven codegen ACL validation lane.
