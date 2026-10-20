# Task: Investigate an upgraded lesser keeping holders whose dependencies the old root disposes

## Metadata
- Task ID: TASK-2026-10-14-investigate_upgrade_retained_holders_keep_old_dependencies
- Story: none - D6 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes (opened by
  TASK-2026-10-14-audit_slotted_lifetime_ownership, done)
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-14T18:40:43Z
- Updated: 2026-10-15T01:32:52Z

- Completed: 2026-10-15T01:32:52Z
- Summary: D6 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes: no defect. Graduation keeps retained objects for
  eventual disposal; the `upgrade_to_normal` docstring paragraph landed with 0.2.8236; a retained object referencing a
  disposed dependency is pending agent work under the owner's runtime model. No notch of its own. Turned in by owner
  directive.

## Objective
`upgrade_to_normal` keeps the lesser's store (its retained creations) and repoints its lineage and cluster
stores to its own, while the instances it melded before stay with their owners. Proven on 0.2.8235 (u6): the
per-conduit holder the upgraded conduit retains keeps the old lineage's instance, which the old root's teardown
disposes while the holder is still alive (the holder is disposed only at the upgraded conduit's teardown). The
same follows for `unique` dependencies the old root owns (not probed). Find what retained creations should mean
after an upgrade and lay out options for the owner's epic.

The owner's rule this is checked against: an instance and everything built for it share one owner's lifetime;
a dependency is not disposed under a live holder.

## Ticket Contract
- ENTRY_GATE: the epic's board row routes it; the reproducer is rerun on the current tree; red tests fail before
  any src edit; the epic's patch docs are written, linked and mapped.
- EXECUTION_BOUNDARY: the code paths below, the fix, its tests and docstrings (owner directive 2026-10-14: fix it
  under EPIC-2026-10-14-slotted_lifetime_ownership_fixes); system docs, release note and notch with the epic.
- DEPENDENCIES: TASK-2026-10-14-audit_slotted_lifetime_ownership (the probe and its runs);
  EPIC-2026-10-14-many_child_follows_holder (0.2.8235).
- EXIT_GATE: root cause recorded; red tests red before and green after the fix, GIL off and on; the probe case
  clean; no warm meld path change; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for every behaviour that is a design choice; BLOCKER if the reproducer no
  longer fails on the current tree (record it and stop).

## Scope Boundaries
- In scope: the defect named in the objective, its code paths and every caller that shares the cause.
- Out of scope: the fix itself; the other audit findings (their own tasks).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: opened from the audit with a reproducer that fails on 0.2.8235, GIL off and on (owner directive,
  chat 2026-10-14: "make a task to investigate it and then we'll turn it into an epic").
- from_state: ready
- to_state: in_progress
- transition_reason: the owner asked for D6 to be re-investigated first (chat 2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: re-investigated: not a defect (graduation contract and tests); a docstring clarification
  is proposed; the owner confirms the verdict (2026-10-14T18:56:30Z).
- from_state: review
- to_state: done
- transition_reason: the owner accepted the lane and directed the turn-in (owner, chat 2026-10-15: "ok cool turn it
  all in if your done").


## Steps / Checklist
- [x] Read `upgrade_to_normal`, `_conjure_existing_conduit` and the lineage repointing; record which retained
      instances can hold dependencies owned elsewhere.
- [x] Superseded by the verdict (no defect): no red test; existing tests pin both halves of the graduation
      contract.
- [x] Superseded by the verdict (no defect): options not needed. Lay out options (dispose retained holders at
      upgrade; carry their dependencies; refuse an upgrade that
      would strand them) for the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root cause with evidence, red tests, and fix options for the owner's epic.

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py` (upgrade_to_normal)
- `src/melder/aether/spellbook/spellbook.py` (_conjure_existing_conduit)
- `tests/` (red tests, when the investigation runs)

## Validation
- Reproducer run on 0.2.8235 (Python 3.14.7t, GIL off and on, identical): see Notes.
- Not run: anything else (the investigation has not started).
- Reproduce (from a tree root with src/ and tests/):
  `PYTHONPATH=src:. python context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py u6`

## Risks / Rollback Notes
- Investigation only; nothing to roll back.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Open Questions
- Answered by the re-investigation and the owner's runtime model (2026-10-14): an upgrade keeps the
  retained creations for eventual disposal; a retained object referencing an instance the old lineage
  disposed is pending agent work, not a defect.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/ (the probe and its runs, shared with the audit task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided when the owner's epic closes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - retained creations after upgrade_to_normal
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence; the whole ticket; initial revision
  2026-10-14T18:40:43Z; the reproducer is the audit's probe. The rule and the directive are the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:40:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Opened from TASK-2026-10-14-audit_slotted_lifetime_ownership with a reproducer: probe case(s)
    u6 fail the owner's rule on 0.2.8235 as described in the Objective, with identical output GIL off and
    on. The code paths below were read in full during the audit; the root-cause analysis, red tests and fix options
    are this task's work.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2351-2405
  - src/melder/aether/conduit/conduit.py:2406-2547
  - src/melder/aether/spellbook/spellbook.py:7180-7205
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:53-59
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-608
  IMPACT: The defect is real on today's tree; the owner can turn this task into an epic.
  NEXT: Rerun the reproducer on the current tree, then read the paths in Steps and record the root cause.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:55:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner turned the audit's tasks into one fix lane and put it first ("all these need to be fixed
    go ahead and target all these fixes since you have context first"); this task is now the epic's D6
    and covers the fix as well as the investigation (Ticket Contract updated).
    The owner asked for D6 to be re-investigated before any fix ("investigate D6 again just make sure").
  EVIDENCE: context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-159
  IMPACT: Investigation, red tests and the fix land here; docs, notes and the notch go with the epic's pass.
  NEXT: Re-read upgrade_to_normal, its tests and Creations' disposal order; record the verdict.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:56:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Re-investigated as the owner asked; D6 is not a defect, and the audit's reading was wrong. Graduation's
    contract is explicit and pinned by tests: the new root has no parent, "Old spell IDs are no longer resolvable;
    retained objects remain in their existing stores for eventual disposal" (`upgrade_to_normal`); the old root's
    teardown does not dispose the retained objects and the graduated root's does (graduation lifecycle test); old ids
    raise KeyError in the conduit and in its retained space (graduation configuration test). So after an upgrade no
    meld serves a retained holder: it is application-held state awaiting its owner's disposal. Each object is still
    owned and disposed by the object its lifetime names - the retained per-conduit holder by the graduated conduit, the
    lineage instance by the old lineage root - which is the owner's rule. What u6 shows is a reference from a retained
    object to an instance another owner ends first; that is the ecosystem behaviour the owner described ("melder is a
    runtime ecosystem not a static library"), the same as application code keeping any instance whose scope ended
    (purge: "References held by application code are not revoked"). This differs from the many-child bug, where Melder
    kept serving the holder whose child it had disposed. One real gap remains, in documentation only: the
    `upgrade_to_normal` docstring does not say that retained objects keep references to instances the old lineage and
    its roots own and dispose (the cross-scope teardown order `_dispose_disposable_registry` leaves to the conduit
    cascade no longer covers a graduated conduit). Proposed: say so in the docstring (folded into the epic's conduit.py
    change, no behaviour change) and close D6 as no defect.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2406-2547
  - src/melder/aether/conduit/creations/creations.py:419-466
  - tests/component/melder/aether/conduit/test_conduit_graduation_lifecycle.py:161-171
  - tests/component/melder/aether/conduit/test_conduit_graduation_configuration.py:114-136
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:53-59
  IMPACT: No fix for D6; one docstring paragraph; the epic's fixes are D1-D5.
  NEXT: Owner confirms the verdict (then D6 closes with the docstring change in the epic's notch); the lane moves to D1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:07:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: D6 aligned with the owner's runtime model (2026-10-14, promoted to src_architecture): the docstring paragraph
    landed with 0.2.8236, and the audit probe's u6 at 0.2.8240 is unchanged by design (the old root's teardown closes
    the lineage instance once; the retained holder is closed once, at the upgraded conduit's teardown). The 'one
    owner's lifetime' rule in the Objective was my framing; the owner's model makes a retained reference to a disposed
    dependency pending agent work, not a defect.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2476-2510
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:52-58
  - context_compass/system_docs/src_architecture.md:522-548
  IMPACT: D6 closes as no defect when the owner confirms.
  NEXT: The owner confirms; close with the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T01:32:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Turned in as no defect. The owner accepted the lane and directed the turn-in (owner, chat 2026-10-15: "ok
    cool turn it all in if your done"). The red-test and options steps were superseded by the verdict (no defect); the
    docstring paragraph landed with 0.2.8236.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2476-2510
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-33
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-25
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_0_2_8240.txt:1-40
  IMPACT: Closed; nothing of this task stays open.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (2026-10-15T01:32:52Z). Re-investigated at the owner's request: not a defect; the `upgrade_to_normal` docstring
paragraph landed with 0.2.8236. Turned in by owner directive with the epic.

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
