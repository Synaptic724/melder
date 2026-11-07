

# Task: spellframe_ambiguity_validation_check - a Phase 4 or Phase 6 check for spells sharing a spellframe

## Metadata
- Task ID: TASK-2026-11-07-spellframe_ambiguity_validation_check
- Story: none - an epic-level task of EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: ready
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T10:22:44Z

## Objective
The owner's check (chat 2026-11-07): "a phase 4 or phase 6 check to see if multiple spells are bound with a
spellframe without a binding_name and that should help the user situation". His rule (chat 2026-11-07, "lets do
3"): (a) after T2, a consumer annotated with a class bound only under a spellframe is refused at conjure by a
Phase 4 error that names the frame - and its binding names - to ask by; (b) two spells at one address stay refused
on every path - two spells under one spellframe with no binding_name, and two spells of one name with neither -
with a check added wherever a path admits one. Each reports through the readable validation report with its remedy.

## Ticket Contract
- ENTRY_GATE: the owner's rule (Notes, 2026-11-07); a board row routes here; T2 landed, for part (a).
- EXECUTION_BOUNDARY: part (a), one Phase 4 strategy reading what Phase 3 records for a class annotation that only
  framed spells match; part (b), the paths that register or expose a spell at an address (bind, bind_inactive,
  index moves, contracted copies, scan), a check added only where one admits a second spell; their tests and docs;
  the release note and notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-11-07-spellframe_hides_the_concrete_class; T2 for part (a); none for part (b).
- EXIT_GATE: part (a) refuses with code, message and remedy naming the frame; part (b) pinned by regression tests on
  every path, any new check with code, message and remedy; tests pass, the GIL off and on.
- FAILURE_ESCALATION: DECISION_REQUEST when a path admits two spells at one address by design (a parked version, a
  borrowed copy), or when part (a) would refuse a world the owner wants to conjure.

## Scope Boundaries
- In scope: the check, its message and remedy, its tests and docs.
- Out of scope: changing Bind's address refusal.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the owner set the rule (chat 2026-11-07; Notes); part (a) waits for T2, part (b) for T1.

## Steps / Checklist
- [x] The owner confirms the situation and the severity (DECISION note, 2026-11-07T10:22:44Z).
- [ ] Part (a): the Phase 4 strategy, with a rich docstring, over what Phase 3 records for a class annotation that
      only framed spells match; the error names each frame and binding name to ask by.
- [ ] Part (b): read each path's address refusal; regression tests for both shapes on every path; a check where one
      is missing.
- [ ] Component tests for the flagged and the unflagged shapes; docs; release note; notch; rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The validation strategy, its tests and docs, the release-note entry.

## Files / Paths Impacted
- part (a): src/melder/aether/spellbook/spell_compiler/validation/strategies/ (a new Phase 4 strategy) and
  src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py (what the unresolved socket records)
- part (b): UNKNOWN until the paths are read - a check only where a path admits a second spell at an address

## Validation
- Not run.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest tests -q` and the same with `-X gil=1`

## Risks / Rollback Notes
- An error-severity check refuses worlds that conjure today; a warning reports through `validation_warnings=True`.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which spellframe situation the check flags
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-11-07T10:03:26Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T10:03:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Which situation the check flags. Melder already refuses two spells at one address - a second spell bound
    under `Greeter` with no binding name raises at bind - so "multiple spells under a spellframe without a binding
    name" cannot be registered today. Candidates: (1) one frame holding several spells while a consumer asks by the
    frame - today AMBIGUOUS_PROVIDER at that consumer; (2) a frame whose spells all carry binding names, so
    `meld(spellframe=...)` alone finds nothing; (3) after T2, a consumer asking by class for a class bound only
    under a frame - it compiles unresolved, and the check names the frame to ask by. Severity: error or warning.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt:1-51
  IMPACT: The rule decides the phase, the facts the strategy reads and whether worlds that conjure today refuse.
  NEXT: The owner's answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T10:22:44Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner set the rule (chat 2026-11-07): "sure 2 spells with the same name without differentiation, 2
    spells with the same spellframe without a binding_name, I think its called binding name, you can add these or
    extend various features for this, if we don't already have it you can place it where you need to, lets do 3".
    (a) Candidate 3 at error severity, in Phase 4 - the recommendation as put to him, not objected to: after T2 a
    consumer annotated with a class bound only under a spellframe is refused at conjure, the error naming the frame
    and binding names to ask by (today such a meld would raise UnresolvedInputError, "nothing registered provides
    it"). (b) Two spells at one address stay refused on every path: one spellframe with no binding_name (refused at
    bind, measured on 0.2.8277) and one name with no spellframe or binding_name (UNKNOWN - the architecture doc
    names bind's address claim and Phase 4's DUPLICATE_SPELL_NAME; not measured); a check goes in wherever a path
    admits one. Candidates 1 (already AMBIGUOUS_PROVIDER) and 2 (warning-only) are not taken.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt:1-51
  - context_compass/system_docs/src_architecture.md:2188-2192
  - context_compass/system_docs/src_architecture.md:2913-2919
  IMPACT: T3 has two parts: (a) depends on T2's strict model and needs Phase 3 to record the framed candidates of a
    class annotation it no longer matches; (b) is independent of T2 and is mostly verification plus tests.
  NEXT: T1's inventory first (it reads the matchers part (a) builds on); part (b) after T1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
- Scope: the owner's rule - (a) a Phase 4 error for a consumer annotated with a class bound only under a spellframe,
  naming the frame to ask by; (b) two spells at one address refused on every path, checked where missing.
- State: ready, melder_0. Part (a) waits for T2; part (b) can run after T1.
- Next: (1) T1's inventory; (2) part (b): the paths and their tests; (3) part (a) after T2; release note, notch,
  rebuild last.

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
