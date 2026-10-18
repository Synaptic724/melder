# Story: spell_id_hashes_the_object_code - the spell_id is the SHA256 of the registered object's code

## Metadata
- Story ID: STORY-2026-10-18-spell_id_hashes_the_object_code
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: ready
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T11:45:58Z

## User Narrative
As an agent iterating on a class in Melder, I want its spell_id to change exactly when its code changes - a method
body, a parameter, a default, the constructor - and never for a docstring, a comment, a blank line or how it was
bound, so that every real edit is a new version I can stage and notch, and the same code is always the same spell.

## Value / MRP Alignment
Identity is structure. Today's hash misses method bodies (the epic's F1, F2, F5: an edited class is refused as a
collision) and folds in the bind call (the n-registrations bug). Hashing the object's code, and only that, fixes
both at the root.

## Ticket Contract
- ENTRY_GATE: the owner's calls on the epic's open edges (inherited code, class-level values, existing objects,
  local renames, scope); the epic's architecture patch and this story's component patch approved; the board row.
- EXECUTION_BOUNDARY: `Bind.sha256_profile` and `Bind.spell_id_inspector` (their inputs), the binding profile
  strategy (a code digest per class or function, computed once per object), the hash domain (a new version tag);
  its tests and docs. Not the binding manifest or the caches (S2), revalidation (S3), the refusals (S4) or the
  migration (S5).
- DEPENDENCIES: the epic; the prototype probes; S2 lands with it.
- EXIT_GATE: the prototype's cases P1-P10 and I1-I9 are regression tests passing with the GIL off and on and
  across hash seeds; bind's cost measured against today's; the docs and the graph.
- FAILURE_ESCALATION: DECISION_REQUEST for an edge the owner has not called; RISK if bind's cost regresses
  materially; CONFLICT if a needed file is held.

## Requirements (Functional)
- A class's spell_id hashes its module, qualname and bases (per the owner's inherited-code call) and, for every
  function its body defines - methods, the constructor, static and class methods, property accessors - the
  signature text (parameters, defaults, annotations; memory addresses removed) and the instruction stream with each
  operand resolved to its value; nested code (functions, lambdas, comprehensions) is hashed the same way.
- Line numbers, docstrings (the constant 3.14 flags with CO_HAS_DOCSTRING), comments and unused constants never
  enter it; raw bytecode is not hashed, because a docstring shifts every constant index in it.
- A function or lambda hashes its module, qualname, signature and instructions; a decorated function hashes the
  function it wraps (`inspect.unwrap`).
- An existing object hashes as the owner calls it (its class's code plus its data is the proposal).
- Nothing from the bind call enters it: spellframe, binding name, existence, disposal names, resolvable and the
  managed settings move to the binding manifest (S2).

## Requirements (Non-Functional)
- No source-file read at bind; the digest is computed once per class object (a class object's code does not
  change) and reused.
- Address-free and deterministic: byte-identical across processes, hash seeds and GIL modes.
- Bind's cost measured before and after on the gauntlet's bind-heavy worlds.

## Scope Boundaries
- In scope: Bind's fingerprint inputs, the binding profile's code digest, `spell_id_inspector`, tests and docs.
- Out of scope: the binding manifest and the caches (S2), revalidation (S3), the refusals (S4), the migration (S5).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: filed under EPIC-2026-10-18-spell_identity_is_the_code on the owner's direction (chat 2026-10-18); scope and owner set, the open questions named.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-binding_manifest_hash (lands with this story)
- STORY-2026-10-18-spell_id_migration

## Tasks (Implementation Checklist)
- [ ] Task: the owner's calls (the epic's Open Questions).
- [ ] Task: the component patch (Binding Pipeline: the code digest; the hash domain).
- [ ] Task: red regression tests from P1-P10 and I1-I9.
- [ ] Task: implement and measure bind's cost.
- [ ] Task: docs, graph, notch (with S2) and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- A changed method body, a parameter added to a method, a changed default, a renamed method and two lambdas with
  different bodies each give a different spell_id; a comment, a reworded or added docstring and blank lines give
  the same one.
- Binding the same class under two binding names gives one spell_id (S4 refuses the second registration).
- The ids are identical across processes and GIL modes.

## Validation / Test Plan
- Symptom-named tests such as `test_editing_a_method_body_changes_the_spell_id`,
  `test_a_docstring_or_comment_does_not_change_the_spell_id` and
  `test_two_lambdas_with_different_bodies_are_two_spells`; a subprocess test for stability across hash seeds; the
  epic's probes re-run on src/; the whole tree with the GIL off and on.

## UX / API / Data Notes
- **Breaking change** (with S5): every spell_id moves once; the same object always has the same spell_id.

## Risks / Mitigations
- Ids differ per Python version and under -O (compiled instructions): document it; the cache is already per
  interpreter.
- A closure's captured values are not code: decide with the owner if a factory-made class counts.
- Bind's cost: memoize per class object; measure.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- The epic's five calls, foremost inherited code and existing objects.

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (the design's probes are rowed under the epic)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: rows are added when this story produces its own artifacts

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T11:45:58Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T11:45:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence it starts from is the
    epic's FACT note and its probes. Nothing in src/ moves before this story's component patch is approved.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  IMPACT: The scope, requirements and acceptance above are the plan the patch docs refine.
  NEXT: the component patch after the owner's calls.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: the spell_id hashes the registered object's code only.
- State: ready (melder_0); waiting on the owner's calls and the patches.
- Next: the component patch after the owner's calls.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
