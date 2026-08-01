# Task: FINDING-3 - an overridden meld registers the override-built object as the singleton

## Metadata
- Task ID: TASK-2026-08-01-override-singleton-contamination
- Status: review
- Owner: cowork
- Agent Name: examples_0
- Priority: p2
- Parent: EPIC-2026-08-01-ux-aix-harness-red-remediation
- Created: 2026-08-01T11:18:00Z
- Updated: 2026-08-01T12:58:00Z

## Problem / Opportunity
1 red, and the most interesting one. A deep `spell_override` on a `unique` graph
constructs the intermediate singleton around the injected object and REGISTERS it
as the canonical instance. Every later plain meld reuses the contaminated object.
The example asserts the opposite.

## Context
`spell_override` is sold as the surgical form: inject a fixture or variant into the
middle of a real graph at meld time without rebinding. If that injection silently
becomes the process-wide singleton, "without rebinding anything" is not the whole
truth - the effect outlives the call that made it.

## Ticket Contract
- ENTRY_GATE: red reproduced; registration on the override lane confirmed in source
  rather than inferred. MET.
- EXECUTION_BOUNDARY: under ruling (a) the example only; under ruling (b) the
  phase-11 generalized override runtime, which is system-impacting and requires
  patch docs first.
- DEPENDENCIES: owner ruling.
- EXIT_GATE: the red is green AND the lesson states the true rule, whichever way it
  is ruled.
- FAILURE_ESCALATION: BLOCKER if a runtime change would alter meld semantics beyond
  the override lane.

## Applicable Anti-Patterns
- Changing the assert to match observed behavior while leaving the lesson's prose
  teaching the opposite. The prose is the deliverable here, not the assert.

## Requirements
- Functional: whichever rule stands must be stated in the lesson body, not just
  satisfied by an assertion.
- Non-functional: no change to the non-override resolution hot path.

## Acceptance Criteria
- [ ] Owner has ruled (a) behavior correct, or (b) behavior changes.
- [ ] Lesson prose matches the ruled behavior.
- [ ] Example green on an owner 3.14t run.
- [ ] If (b): patch docs exist and canonical docs are updated.

## Risks / Mitigations
- RISK: (b) is a meld-semantics change with wide blast radius. MITIGATION: patch
  framework gating, and scope strictly to the override lane.
- RISK: (a) leaves a real footgun undocumented elsewhere. MITIGATION: if (a), the
  rule should also land in the canonical docs, not only in a tier lesson.

## Validation Plan
Owner harness run; if (b), also the full unit + component meld surfaces.

## Notes

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: FACT
  CLAIM: Mechanism confirmed in source, not inferred from the failure. The example
    binds `Credentials`, `Transport` and `MailPipeline` all `existence="unique"`.
    The overridden meld builds `Transport` around the injected `test_credentials`
    and registers it, because the generalized override runtime carries
    `must_register` step flags and calls `register_spell_instance_prebound`. The
    later `conduit.meld(spell=Transport)` therefore REUSES the fixture-carrying
    singleton, and `plain.credentials.source` is "test-fixture", not "vault".
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/02_deep_spell_override_paths.py:43-53
    - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:39,70,514-515
  IMPACT: The failing assert is the CORRECT observation of a real rule. What is
    wrong is the lesson's claim that "Untouched melds keep the DI-built world",
    which holds for `many` but not for singleton lifetimes.
  NEXT: Owner ruling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Two compliant paths; I lean (a) but weakly, and the reason matters.
    (a) BEHAVIOR IS CORRECT. Under `unique`, the first meld that constructs the
    singleton wins, and an overridden meld is still a construction. Fix the example:
    either meld plainly first, or bind as `many`, and REWRITE the lesson to teach
    the contamination rule explicitly - it is a sharp edge users must know about.
    Cheap, zero runtime risk, and turns a red into a better lesson than the original.
    (b) BEHAVIOR IS WRONG. An override is a caller-local substitution and should not
    be promoted into shared singleton storage; the override lane would skip
    registration for overridden nodes. Philosophically cleaner - "surgical" should
    mean local - but it is a meld-semantics change under the patch framework with
    real blast radius.
    The argument FOR (b) that I cannot dismiss: injecting a test fixture once and
    silently poisoning the application singleton for the process is the kind of
    failure that surfaces at 3am, and the README's pitch is that Melder catches
    that class of problem at conjure rather than at 3am.
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/02_deep_spell_override_paths.py:1-13
  IMPACT: (a) is a lesson rewrite. (b) is a runtime change requiring patch docs.
  NEXT: OWNER RULING. No edit until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Artifact Links (Optional)
- none yet; ruling (b) requires patch docs before implementation.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

- DATETIME: 2026-08-01T13:05:00Z
  TYPE: DECISION
  CLAIM: RULED (a) BY THE OWNER'S SCOPE LOCK, AND I AM RECONCILING MY OWN TICKET
    RATHER THAN LEAVING IT LYING. The note above says "NEXT: OWNER RULING. No edit
    until then" - and then I edited. That is not a bypass: the owner's scope lock
    ("the runtime is internal and correct; your job is examples") IS ruling (a),
    because it removes (b) - a meld-semantics change - from my lane entirely. But
    the ticket still read `blocked on owner` after I had acted, which is exactly
    the ticket-vs-reality drift this system exists to prevent, so it is corrected
    here instead of being left for a future reader to trip over.
    IMPLEMENTED (a): the lesson now TEACHES the contamination rule rather than
    denying it - under `unique` the overridden meld BUILDS the singleton and
    registers it, so the fixture outlives the call. The rule as written in the
    lesson: "an override is surgical in WHERE it reaches, not in HOW LONG it
    lasts", with the escape hatch (bind `many` if the fixture must not escape).
    The module docstring's false promise was corrected in the same pass.
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/02_deep_spell_override_paths.py:1-13
    - tickets/epics/2026-08-01_ux_aix_harness_red_remediation_epic.md
  IMPACT: Acceptance criterion 1 is met by the scope lock, not by a separate
    ruling. Criterion 4 (patch docs) is now N/A - no runtime change was made.
  NEXT: Owner 3.14t harness run. Green closes this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Mechanism proven in source. The failing assertion was a correct observation of real
behavior; the lesson's prose was what was false, and the lesson now teaches the real
rule. Ruled (a) via the owner's scope lock - no runtime change, no patch docs needed.
Awaiting the owner harness run only.
