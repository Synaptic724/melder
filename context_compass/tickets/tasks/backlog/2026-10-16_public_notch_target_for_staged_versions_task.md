# Task: public_notch_target_for_staged_versions - a public way to notch to a staged version

## Metadata
- Task ID: TASK-2026-10-16-public_notch_target_for_staged_versions
- Story: none (standalone backlog task; found during S8 of EPIC-2026-10-14-managed_spell_quantity)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-16T11:42:41Z
- Updated: 2026-10-16T11:42:41Z

## Objective
Make the stage -> notch -> meld loop work on public API. `Conduit.notch_spell(spell_index=..., spell=...)` needs the
staged version's Spell object, and no public call returns a parked version's Spell: `Spellbook.find_spell_by_id` and
`Conduit.get_spell_by_id` answer a parked id with the index's live spell, and only the internal
`Spellbook._get_owned_spell` returns the parked one. The README's stage-notch-meld sketch passes `spell_v2` (and
`spell_v1` for the revert), which nothing public produces; docs/expert/governed-change.md stops its lesson before the
notch for that reason, and the 0.2.8248 release note shows the notch as a comment. Outcome: the owner picks the shape,
it is built, and the README and docs examples run as written.

## Ticket Contract
- ENTRY_GATE: the owner's choice in the DECISION_REQUEST below (a public API change); an active board row; a component
  patch for the chosen surface and the mapping note before the first `src/` edit.
- EXECUTION_BOUNDARY: `Conduit.notch_spell` and the Spellbook notch entry it calls, or the new lookup (per the
  choice); README's stage-notch-meld sketch; docs/expert/governed-change.md; new unit and integration tests; system
  docs with their indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: none. 0.2.8248 (S8) already wires versions staged before conjure, so the loop also works for them.
- EXIT_GATE: a probe runs the README loop as written (stage, notch, meld, revert) on public calls only; tests green
  with the GIL off and on; docs, release note, notch and both rebuild checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if the chosen shape changes the meaning of an existing argument; CONFLICT if the
  notch transaction's metadata (it reads `spell.spell_id` and `spell._key` before admission) cannot be built from an
  id alone without a new lookup.

## Scope Boundaries
- In scope: one public way to name the notch target; the README and docs examples; tests and docs.
- Out of scope: `find_spell_by_id`'s documented live-spell answer (other callers rely on it); `bind_inactive`'s
  return value (a spell id); `add_to_spell_index` / `remove_from_spell_index`, unless the owner extends the scope.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a draft from S8's finding (Notes); the owner's design choice comes first ("if you
  found more bugs just add tickets", 2026-10-16).

## Steps / Checklist
- [ ] The owner picks the shape (DECISION_REQUEST below).
- [ ] Component patch and mapping note; red tests (the README loop on public calls only), the change, green in both
      GIL modes.
- [ ] README sketch and docs/expert/governed-change.md run as written; system docs, graph, release note, notch,
      rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The chosen public notch target, its tests and a probe that runs the README loop.
- README and docs examples that run; system docs, release note, notch and rebuild.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py (`Conduit.notch_spell`) and src/melder/aether/spellbook/spellbook.py (the notch
  entry, or a new public lookup)
- README.md (the stage-notch-meld sketch); docs/expert/governed-change.md
- tests under tests/unit/melder/aether/conduit/ and tests/integration/melder/spellbook/

## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 -m pytest <the new tests>; python -X gil=1 -m pytest <the new tests>
  - python -X gil=0 <the README-loop probe>

## Risks / Rollback Notes
- A second way to name the target must refuse both or neither given, so a notch never picks one silently.
- Rollback: revert the notch's files; the private path keeps working for internal callers.

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
  - none yet. S8's release-note probe shows the private notch the public loop would replace; it is rowed under
    the epic's evidence folder: artifacts/managed_spell_quantity_20261015/probes/probe_s8_release_note_example.py
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the public notch target for a staged (parked) version
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T11:42:41Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T11:42:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: No public call returns a staged (parked) version's Spell, and `notch_spell` needs one. `Conduit.notch_spell`
    builds its transaction metadata from `spell.spell_id` and `spell._key` and passes the object to the Book's
    notch; `Spellbook.find_spell_by_id` (and `Conduit.get_spell_by_id` through it) answers a parked id with the
    live spell of its index, by its documented contract; `Spellbook._get_owned_spell` - internal - returns the exact
    version. So the README's stage-notch-meld sketch cannot run as written (`spell_v2` and `spell_v1` come from
    nowhere public), docs/expert/governed-change.md stops its lesson before the notch, the S8 integration tests and
    probes notch through `_get_owned_spell`, and the 0.2.8248 release note shows the notch as a comment. A completed
    task recorded the same gap on 2026-09-05.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/spellbook/spellbook.py:2029-2108
  - src/melder/aether/spellbook/spellbook.py:3290-3309
  - README.md:1068-1092
  - docs/expert/governed-change.md:16-25
  - release_docs/next_version_release.md:543-565
  - context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md:185-191
  IMPACT: A user can stage a version but cannot promote it without private access; the documented loop is a sketch.
  NEXT: The owner answers the DECISION_REQUEST below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T11:42:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Which public shape names the notch target? (A, recommended) `notch_spell(spell_index=..., spell=None, *,
    spell_id=None)` - exactly one of `spell` and `spell_id`, the id resolved to the exact owned version (active or
    parked) before the transaction starts; the smallest change, and it mirrors `meld(spell_id=...)`. (B) a public
    exact-version lookup beside `find_spell_by_id` (for example `find_version_by_id`, active or parked, None on a
    miss) that callers pass to `notch_spell` unchanged. (C) both. Either keeps `find_spell_by_id`'s live-spell
    answer, which other callers rely on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/spellbook/spellbook.py:2029-2108
  IMPACT: The choice fixes the public surface the README and docs examples will use.
  NEXT: Build the chosen shape after the owner answers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: one public way to notch to a staged version; the README and docs examples run as written.
- State: draft in the backlog; waits on the owner's choice (A, B or C; A recommended). Source revision 0.2.8248.
- Next: the owner answers; then patch, tests, change, docs, notch, rebuild.
- Limits: none run (Not run).

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
