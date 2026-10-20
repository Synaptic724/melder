

# Story: Runnable managed-pool examples for every mode and lifecycle step, proven by pytest

## Metadata
- Story ID: STORY-2026-10-18-managed_spell_ux_examples
- Epic: EPIC-2026-10-18-managed_spell_examples_and_docs
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T21:14:51Z
- Updated: 2026-10-18T22:07:09Z
- Completed: 2026-10-18T22:07:09Z
- Summary: Seven intermediate lessons (42-48) teach managed spell pools end to end - the three modes, leasing
  by meld, injection and lease, release, resets, refusals, inspection, teardown, a settings rebind and a
  transfer - with 34 contract probes; green on 3.14t, GIL off and on; the owner has the walkthrough.

## User Narrative
As a human or an agent learning Melder, I want runnable examples of managed spell pools - each pool mode and each
step of a managed object's life - so that I can see what Melder does and copy a working pattern.

## Value / MRP Alignment
The examples are the evidence the docs point at: runnable, `md.*` only, and executed by the verification harness,
so a regression breaks a test instead of a reader's trust.

## Ticket Contract
- ENTRY_GATE: S1's lifecycle map is recorded; the board row routes here.
- EXECUTION_BOUNDARY: new example files in `UX_and_AIX_experiences/02_intermediate/` (default tier), their entries
  in `UX_and_AIX_experiences/pytest_examples/`, and the tier's concept map if it lists every example; runs on a VM
  copy only.
- DEPENDENCIES: STORY-2026-10-18-managed_spell_lifecycle_map; the harness in `pytest_examples/`; a 3.14t
  interpreter in the VM.
- EXIT_GATE: the examples run green as scripts and under pytest on 3.14t; the owner has the pool-type and
  lifecycle walkthrough; findings recorded on the tier epic when there are any.
- FAILURE_ESCALATION: a needed deep import - DECISION_REQUEST (init-surface gap); a defect - file it; flaky queue
  timing - redesign the example around events, never retry until green.

## Requirements (Functional)
- One example per pool mode (elastic, limited_quantity, queue) and examples for the lifecycle steps S1 maps:
  lease, release, lease `with`, reset methods, refusals, inspection, teardown; transfer and rebind if S1 finds
  them teachable here.

## Requirements (Non-Functional)
- Header TIER / GOAL / SURFACE EXERCISED; `main()`; honest asserts; `import melder as md` only.
- Synaptic typing: Optional/Union, hints on every function, no `from __future__ import annotations`.
- Deterministic: no assert that depends on thread scheduling or wall-clock luck.

## Scope Boundaries
- In scope: new examples and their harness entries.
- Out of scope: rewriting existing examples or the harness.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: exit gate met - lessons and probes green on 3.14t (GIL off and on) and the owner has the
  walkthrough; routine closure by the assigned agent (owner acceptance at the epic).

## Dependencies / Related Work
- `UX_and_AIX_experiences/AGENTS.md`; `UX_and_AIX_experiences/pytest_examples/test_intermediate_examples.py`.

## Tasks (Implementation Checklist)
- [x] Read the harness (conftest, the intermediate runner, the example contract test) and two neighbouring
      examples for the house style.
- [x] Write the examples (lessons 42-48).
- [x] Add their harness coverage (`test_managed_spell_probes.py`, 34 rows; the concept map section).
- [x] Run them on 3.14t (GIL off and on); save the runs (`artifacts/.../runs/s2/`).
- [x] Report the pool types and the full lifecycle to the owner.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Every new example runs as a script and under the harness, green on 3.14t; the owner has the walkthrough.

## Validation / Test Plan
- `pytest UX_and_AIX_experiences/pytest_examples -v` on a VM copy of the tree, 3.14t.

## UX / API / Data Notes
- Tier: 02_intermediate unless S1 shows a reason otherwise.

## Risks / Mitigations
- Threads in the queue example: hand-offs by events, short fixed timeouts.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No example asserting behaviour that S1 did not evidence.

## Open Questions
- Resolved 2026-10-18: `tests_components.md` names `UX_and_AIX_experiences` only as a pytest
  `norecursedirs` entry and maps no harness component there, so no suite-map entry is needed.

## Decision Log
- 2026-10-18: seven lessons (42-48), not the six of S1's DECISION note: resets (45) and leases (46)
  became separate lessons so each lesson teaches one idea; 48 carries the dynamic settings rebind and transfer.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_spell_examples_20261018/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_2; synaptic_python_developer; prose; this story; 2026-10-18T21:14:51Z
- Published By: UNKNOWN (local backend; no hosting service)
- Independent Review: none requested yet

## Notes
- DATETIME: 2026-10-18T21:14:51Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Examples in 02_intermediate after S1; harness coverage alongside; runs on a VM copy of the tree.
  EVIDENCE: UX_and_AIX_experiences/AGENTS.md:1-44
  IMPACT: Keeps the examples inside the tier laws and the verification harness.
  NEXT: Wait for S1's lifecycle map.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T21:33:11Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Lessons 42-47 per S1's DECISION note, each asserting only S1-evidenced rows; contract probes in
    pytest_examples/test_managed_spell_probes.py; authored and run on the cloud 3.14t mirror (the device VM has no
    3.14), committed to the tree when green, then re-run on a fresh mirror of the tree.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md
  IMPACT: Examples and tests land together, green on 3.14t.
  NEXT: Write lesson 42 (elastic pool).
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T22:01:23Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Seven lessons, not six: 42 elastic pool, 43 limited_quantity, 44 queue, 45 reset methods, 46 leases,
    47 injection and request scopes, 48 settings rebind and transfer (dynamic). S1's plan (42-47) carried resets
    and leases in one lesson; they split so each lesson teaches one idea. Each asserts only rows S1 evidenced,
    and `pytest_examples/test_managed_spell_probes.py` pins them by name in 34 rows (9 parametrized bind
    refusals among them). The tier's concept map has a MANAGED SPELL POOLS section and a harness line.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/42_managed_spell_elastic_pool.py:1-146
  - UX_and_AIX_experiences/02_intermediate/43_managed_spell_limited_quantity.py:1-107
  - UX_and_AIX_experiences/02_intermediate/44_managed_spell_queue.py:1-126
  - UX_and_AIX_experiences/02_intermediate/45_managed_spell_reset_methods.py:1-135
  - UX_and_AIX_experiences/02_intermediate/46_managed_spell_leases.py:1-109
  - UX_and_AIX_experiences/02_intermediate/47_managed_spell_injection_and_request_scopes.py:1-124
  - UX_and_AIX_experiences/02_intermediate/48_managed_spell_settings_and_transfer.py:1-165
  - UX_and_AIX_experiences/pytest_examples/test_managed_spell_probes.py:1-514
  - UX_and_AIX_experiences/02_intermediate/_concept_map.txt:191-234
  IMPACT: Every mode and lifecycle step of S1's map has a lesson and a named probe row; S3's page links them.
  NEXT: Run the lessons and probes on a fresh mirror of the tree, GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T22:01:23Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green on CPython 3.14.6t, GIL off and on, on a fresh mirror of the tree at commit 5e3800c7a
    (__version__ 0.2.8256; the src .py manifest hashes alike on tree and mirror): the managed rows pass 55/55
    in both modes (34 probes, 7 lesson runs, 14 example-contract rows). The whole `pytest_examples` directory:
    609 passed, 17 failed in both modes - the same 17 the tree fails without this lane's files (554 passed).
    12 are the one-object refusals of EPIC-2026-10-18-spell_identity_is_the_code S1/S2 ("Spell ID collision
    detected" or "Conjure refused ... already registered"); 4 fail on premises that landing touches, cause
    UNKNOWN, not investigated (contract probe same_name_different_internals and expert probe
    two_visible_spells_may_not_share_a_name no longer raise; intermediate probe upgrade_to_normal raises
    KeyError "No spell found for frame='payload'"; beginner 39 agent_inventory_pattern asserts the root
    inventory); 1 is expert 37_review_agent_bindings' missing VERIFY header. None is in this lane's files.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/managed_rows_gil0.txt:1-63
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/managed_rows_gil1.txt:1-63
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/pytest_examples_all_gil0.txt:2808-2825
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/pytest_examples_all_gil1.txt:2808-2825
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/pytest_examples_all_base_tree_gil0.txt:2807-2824
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/base_tree_failures.xml:1-220
  IMPACT: S2's exit gate is met but for the owner walkthrough. The 17 pre-existing failures go to melder_0 as a
    NOTICE (their landing owns the 16 identity-area rows); this lane does not touch those lessons.
  NEXT: Give the owner the walkthrough of the pool types and the lifecycle; then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:07:09Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2 closed: exit gate met - lessons 42-48 run green as scripts (7/7) and under the harness (55/55
    managed rows) on 3.14.6t, GIL off and on; the owner has the walkthrough of the pool types and the lifecycle
    (chat, 2026-10-18 about 22:05Z, with one correction: the SpellBinder keyword is `timeout_seconds`); the wave is
    recorded on the tier epic (no init-surface gap). Routine closure by the assigned agent; ACCEPTANCE:
    delegated-routine (owner acceptance at the epic), VALIDATION: the runs below, CHILDREN: none, ROUTING: the
    board row moves to S3. Open with the owner: the root-held consumer teardown order.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/lessons_as_scripts_gil0.txt:1-49
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/lessons_as_scripts_gil1.txt:1-49
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/managed_rows_gil0.txt:1-63
  - context_compass/artifacts/managed_spell_examples_20261018/runs/s2/managed_rows_gil1.txt:1-63
  - context_compass/tickets/epics/2026-07-19_ux_aix_intermediate_experience_epic.md:1269-1294
  IMPACT: S3 links runnable, tested lessons for every mode and lifecycle step.
  NEXT: S3 - read docs/maintaining.md and the navigation and catalog files.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
State: done - lessons 42-48 and 34 contract probes in the tree, green on 3.14t, GIL off and on (runs under
artifacts/managed_spell_examples_20261018/runs/s2/); the owner has the walkthrough. The example directory's
17 failures predate this lane (identical without its files) and went to melder_0 (M2-16). Open with the owner:
the root-held consumer teardown order (S1 RISK; lesson 47 teaches the request-scope pattern). Next: S3.
Update this view in place. Preserve historical Notes/comments and link unchanged context/full evidence.

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
