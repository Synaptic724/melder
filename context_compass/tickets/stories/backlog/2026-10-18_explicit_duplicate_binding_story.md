# Story: explicit_duplicate_binding - a bind that says so registers one object more than once

## Metadata
- Story ID: STORY-2026-10-18-explicit_duplicate_binding
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: draft
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T14:33:32Z
- Updated: 2026-10-18T15:01:53Z

## User Narrative
As an agent working in Melder, I want to register one object more than once when I say so - for example a
`Worker` class kept as a shared `unique` named `shared` and as a `many` named `fresh`, or three bindings of one
settings class - and call each by its name, so that I can keep several bindings of the same code while an
accidental second registration is still refused.

## Value / MRP Alignment
S1 makes the spell_id the object's code, so a second registration of the same object is refused. Today one class
binds once per binding name, because the binding name is hashed. Without an explicit path S1 would take that
away; with it, duplication is a choice the bind writes down and Melder records, not a side effect of a name.

## Ticket Contract
- ENTRY_GATE: the owner's choice of the form and the option's name (Open Questions); the epic's architecture patch
  and S1's patches updated for it and approved; the board row.
- EXECUTION_BOUNDARY: the duplicate option on `Spellbook.bind`, `Spellbook.bind_inactive`, the Conduit facades,
  `scan_bind` and `SpellBinder`; its place in the spell_id (S1's digest); the Spell's record of it; the
  SpellCrystal field and the restore and graft replay; the refusal text that names it. Not the binding manifest
  (S2), revalidation (S3), the one-registration refusals themselves (S4) or the migration (S5).
- DEPENDENCIES: S1 (lands with it); S2 (the binding manifest stays apart from the scope); S5 (the record version).
- EXIT_GATE: the acceptance criteria as regression tests with the GIL off and on; docs; S1's notch and rebuild.
- FAILURE_ESCALATION: DECISION_REQUEST for the form, the name and the binding-name default; CONFLICT if a needed
  file is held by another lane.

## Requirements (Functional)
- Pending the owner's choice. The recommended form (the epic's STRATEGY_DISCUSSION note of 2026-10-18T14:33:32Z):
- `duplicate_scope=<str>` on bind and bind_inactive, the Conduit facades, `scan_bind` and `SpellBinder`: the scope
  joins the spell_id - the SHA256 of the code and the scope - so each scope of one object is its own spell; no
  scope keeps the plain code id.
- The Spell keeps its scope and its plain code id, so the copies of one object can be listed together.
- The same object with the same scope twice is refused like any duplicate; an unscoped second registration is
  refused with a message that names the existing registration and the option.
- When no binding name is given, the binding name is the scope, so each copy has its own address and is melded
  by it.
- The record keeps the scope; restore and graft replay it through the bind verbs.

## Requirements (Non-Functional)
- Nothing at meld; one string more in the hash at bind.
- The scope is identity, not binding: it is not part of S2's binding manifest, and a binding change (S3) never
  moves it.

## Scope Boundaries
- In scope: the option on the bind verbs and their facades, the spell_id input, the Spell field, the record field
  and replay, the refusal text, tests and docs.
- Out of scope: a scoped block (`with spellbook.duplicate_scope(...)`), a strict switch refusing duplicates and
  stacked scan declarations - parked in EPIC-2026-10-18-identity_and_caching_configurables; old records holding
  one object twice (S5 restores the first, the owner's decision).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: parked in the backlog by the owner (the epic's DECISION note of 2026-10-18T15:01:53Z):
  duplicates are strictly refused for now; talked through later.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-spell_id_hashes_the_object_code (S1; lands with this story)
- STORY-2026-10-18-binding_manifest_hash (S2)
- STORY-2026-10-18-one_registration_per_object (S4; its refusal names this option)
- STORY-2026-10-18-spell_id_migration (S5; the record version)
- EPIC-2026-10-18-identity_and_caching_configurables (backlog; the scoped block and the strict switch)

## Tasks (Implementation Checklist)
- [ ] Task: the owner's choice of the form and the name.
- [ ] Task: the design in the epic's patch folder - the architecture patch's formula and one-object invariant, the
  Binding Pipeline component patch, the code-description patch's spell_id rule.
- [ ] Task: red regression tests, then the implementation with S1.
- [ ] Task: docs and the release-note entry with S1.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- `bind(spell=Worker, existence="unique", binding_name="shared")`, then `bind(spell=Worker, existence="many",
  duplicate_scope="fresh")`, give two spells: `meld(spell=Worker, binding_name="fresh")` builds a new Worker each
  time and `meld(spell=Worker, binding_name="shared")` returns the shared one.
- A second `bind(spell=Worker, ...)` with no scope is refused, naming the first registration and the option.
- The same scope twice is refused; a scoped copy's spell_id is the same across processes and GIL modes.
- A recorded world with scoped copies restores and grafts with each copy and its scope.

## Validation / Test Plan
- Symptom-named tests such as `test_a_second_bind_of_one_class_is_refused_without_a_scope`,
  `test_two_scopes_of_one_class_are_two_spells_called_by_name` and `test_a_scoped_copy_restores_with_its_scope`;
  the GIL off and on; the whole tree in a /tmp mirror before landing.

## UX / API / Data Notes
- A new keyword on the bind verbs (name pending), additive. With S1 it replaces the implicit way to bind one class
  twice - another binding name - which S1 removes; part of S1's Breaking entry.

## Risks / Mitigations
- A parameter typed with the class sees every copy: AMBIGUOUS_PROVIDER at conjure unless a SpellMap default picks
  one, as two binding names of one class do today; the message names the remedy.
- An unfiltered managed release of a class with two managed copies asks for `spell_id=`, as today.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Parked by the owner (the epic's DECISION note of 2026-10-18T15:01:53Z), open until he takes it up: the
  form - (1) an option whose scope joins the spell_id (recommended), (2) `duplicate=True` with the address in
  the spell_id, (3) a scoped block, (4) a Book setting (the epic's STRATEGY_DISCUSSION note of
  2026-10-18T14:33:32Z); the option's name; the binding name defaulting to the scope.

## Decision Log
- 2026-10-18T14:33:32Z: filed as S6 from the owner's direction (the epic's DECISION note of
  2026-10-18T14:14:10Z); four forms with him (the epic's STRATEGY_DISCUSSION note).
- 2026-10-18T15:01:53Z: parked in tickets/stories/backlog/ on the owner's word; S1 lands strictly unique (the epic's
  DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (the design goes into system_docs/patches/active/spell_identity_is_the_code_2026_10_18/)
- DISPOSITION: promote_to_documentation (the patch docs, at landing)
- CLEANUP_TRIGGER: at landing the design is promoted with S1's

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - one object bound more than once, on purpose
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T14:33:32Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T14:33:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction: "we do want the option for users to bind multiple objects twice like 3
    different versions of the configuration so a user can just call it ... by adding a configurable bind action
    such that we can capture that scope and still allow duplication but it has to be explicit" (chat 2026-10-18).
    The four forms, the code read for them and the recommendation are in the epic's STRATEGY_DISCUSSION note;
    the design joins S1's patches once the owner picks the form and the name.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:436-461
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:463-523
  IMPACT: This story lands with S1, or S1 removes today's way to bind one class twice with nothing in its place.
  NEXT: The owner's choice of the form and the name.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
- Scope: an explicit bind option that registers one object more than once, its scope recorded; lands with S1.
- State: draft, parked in the backlog (the owner, 2026-10-18): S1 lands with one object strictly one spell.
- Next: (1) the owner takes it up; (2) the four forms (the epic's STRATEGY_DISCUSSION note of
  2026-10-18T14:33:32Z) and his choice; (3) the design in the identity epic's patch folder.

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
