# Epic: Codegen rooms hold the policy their profile states (D-10, D-11, D-20)

## Metadata
- Epic ID: EPIC-2026-10-25-codegen_room_policy_defects
- Status: in_progress
- Owner: Mark
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-25T00:16:54Z
- Updated: 2026-10-25T08:46:00Z
- Target Window: set by the owner once the three decision requests are answered
- Related Program/Initiative: the core-protection review (TASK-2026-10-08-review_core_protection_fork_aware_updates,
  completed 2026-10-10) and its governed-evolution contract (C1.4, C3.2, C6)

## Problem / Opportunity
The core-protection review left three p1 defects of the codegen rooms open, each in a draft backlog task, on the
owner's word (2026-10-10): "Keep the filesystem-access and dynamic-import gaps explicitly open until fixed and
verified".
- D-10: the `safe` profile documents that it denies writes, yet room code under it - and under every other
  profile - reads and writes any file the process can reach through the `open` builtin.
- D-11: under hybrid, the precision overlay and permissive, `__import__(...)` loads roots their import lists deny
  or leave out, because the import gate reads import statements only.
- D-20: `materialize_codegen` publishes a SyntheticModule over any live module name - Melder's own, the standard
  library's, an installed dependency's - and its failure and cleanup paths never put the displaced module back.
Codegen rooms are where agents build the subsystem they sit in (src_architecture, What Melder Is), and the ACL
profile is the structure that states what their code may do; a profile that does not hold the posture it states is
wrong structure. All three were measured at 66939dfe8 (2026-10-10); the tree is 0.2.8267 now, so each recorded
cause is UNKNOWN until re-measured. The owner's ask (chat 2026-10-24):
"focus on 2 and 3 make an epic for each and investigate them".

## MRP Alignment (Most Reasonable Product)
The profiles are the contract an agent or an owner reads before running code in a room. The MRP is a profile that
holds what it states - its file posture, its import roots and the names its room may publish - and a refusal that
names what was refused and why. In-process checks are defence in depth, never isolation (review contract C6.1),
and every fix is described that way.

## Ticket Contract
- ENTRY_GATE: the owner's ask recorded (Notes, DECISION); the three child tasks moved out of the backlog, assigned
  to melder_0 and routed on attention_board.md, one row each.
- EXECUTION_BOUNDARY: now, investigation: read-only on src/ and tests/; runs on a /tmp copy of the 0.2.8267 tree,
  the GIL off and on; scripts, runs and any new probe under artifacts/codegen_room_policy_20261025/; findings in
  each task's Notes, the synthesis and the decision requests here. After the owner's answers, task by task: patch
  docs before any src/ edit (patch_framework_gating), then the fix, its tests, docs, notch, release-note entry and
  the rebuild.
- DEPENDENCIES: the review's evidence pack (artifacts/core_protection_review_20261010/: probes, recorded outputs,
  README) and its contract (C1.4, C3.2, C3.4, C4.3, C6; the open D2); src_components (Component: Codegen Internal
  Engine, Component: Nexus Descriptor And ACL Managers, Component: RiftSpace Workstation And Command Surface,
  Subcomponent: SyntheticModule Runtime); tests_components.md is held by melder_2 until its turn-in (M2-38, Notes).
- EXIT_GATE: each child task closed with its acceptance criteria met, or closed on the owner's word; each Breaking
  change in the release note; src_architecture records each defect closed; board and artifact sync.
- FAILURE_ESCALATION: a DECISION_REQUEST per owner question (D-10's posture, D-11's option, D-20's namespace and
  builtins); CONFLICT when today's tree contradicts a task's recorded cause; BLOCKER when a file a fix needs is
  held by another lane.

## Goals (Outcomes)
- Each defect re-measured on 0.2.8267, the GIL off and on, its mechanism read at today's lines, and its owner
  question put with options, cost and a recommendation.
- After the answers: every profile holds the file and import posture it states, and a materialize never displaces
  a live module and leaves sys.modules as it found it on every exit.

## Non-Goals (Explicit Exclusions)
- An OS sandbox, read-only mounts or a separate agent process (the review's D2 item 4, the owner's decision).
- The contents of the allow and deny lists (D2), ProtocolCrafter's writers, and live in-place module replacement
  as a feature (the review's D7 keeps it an experiment lane).
- Calling any fix isolation (the C6.4 wording rule).

## Scope Boundaries
- In scope: D-10, D-11 and D-20 as their tasks define them, and whether today's tree changed any recorded cause.
- Out of scope: other codegen-room behaviour; writers outside the process (contract C6.3).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24),
  "focus on 2 and 3 make an epic for each and investigate them" - 2 being the three codegen-room p1 defects.

- from_state: blocked
- to_state: in_progress
- transition_reason: the owner certified a new session as melder_0 and directed it (chat 2026-10-25):
  "Go do the D-10 story first try that".

## Success Metrics
- The four reproducers and the five strict xfails run on 0.2.8267, the GIL off and on, and recorded in the tasks.
- Each owner question answered before its fix starts.
- After the fixes: the five strict xfail markers gone because their tests pass, and the probes report refusals.

## Requirements (Functional + Non-Functional)
- Functional: after the owner's answers, each task's acceptance criteria.
- Non-functional: room code that stays inside its posture pays no cost the fix does not measure and record; each
  refusal names the builtin, import root or module refused and the remedy.

## Constraints / Assumptions
- Device git is read-only for agents; the owner commits.
- Runs use /tmp copies of the tree only: cache writes land under the package root.
- UNKNOWN until re-measured: whether the 2026-10-10 causes hold at 0.2.8267.

## Dependencies / External References
- TASK-2026-10-08-review_core_protection_fork_aware_updates (completed) and its evidence pack,
  context_compass/artifacts/core_protection_review_20261010/README.md
- The three child tasks (Tasks).

## Milestones (Track Progress)
- [x] Milestone 1: re-measured - each reproducer and xfail run on 0.2.8267 and the cited code read (task Notes).
- [x] Milestone 2: decided - the owner answers the three questions (this epic's Notes).
- [ ] Milestone 3: fixed - each task lands with its patch docs, tests, notch, release-note entry and rebuild.

## Stories (Required to Complete)
- none: each defect is one deliverable and stays a task (Tasks).

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-10-10-deny-file-access-under-safe-codegen (D-10) - `open` under safe; the posture question.
      Closed 2026-10-25, notched 0.2.8270.
- [ ] Task: TASK-2026-10-10-enforce-import-policy-on-dynamic-imports (D-11) - `__import__` against the import
      lists; option A, B or both.
- [ ] Task: TASK-2026-10-10-refuse-materializing-over-live-modules (D-20) - the generation namespace and exits
      that restore sys.modules; room builtins for materialized code.
- [ ] Task: Verify Ticket Microcycle enforcement across the three tasks.

## Acceptance Criteria (Epic Done)
- The three child tasks closed with their acceptance criteria met, or closed on the owner's word.
- The release note carries each Breaking change; src_architecture records each defect closed.
- Board and artifact sync done at each closure.

## Risks / Mitigations
- A fix breaks a room workflow that relied on the old posture (Breaking): each task pins the posture the owner
  chooses with symptom-named tests, and the release note names the change.
- A guard inside SyntheticModule would also meet the crystallizer's restore, rebuild and graft lanes: the D-20
  task lists every publisher before the guard's place is chosen.
- Overstated protection: every document says defence in depth, not isolation (C6.4).

## Applicable Anti-Patterns
- [ ] No epic-state transition without task-level evidence.
- [ ] No closure while a child task is incomplete or unaccepted.
- [ ] No program claims without source evidence from task notes.
- [ ] No src/ edit before the owner's answer and the patch docs.

## Validation / Test Approach
- Reproducers, run on a /tmp copy, the GIL off and on: codegen_probe.py (D-10), codegen_probe2.py (D-11),
  probe_materialize.py and probe_materialize_fail.py (D-20), from the review's pack.
- Tests: the five strict xfails in tests/integration/melder/aether/test_codegen_core_boundary_integration.py and
  tests/unit/melder/aether/test_codegen_materialize_verb.py.
- Not run until recorded in the tasks' Notes.

## Rollout / Adoption Plan
- Each fix ships with a Breaking entry in the running release note for room code that relied on the old
  behaviour. No persisted state, cache generation or record version is expected to move (UNKNOWN until each
  design is written).

## Open Questions
- Answered on 2026-10-25 (Decision Log; Notes): D-10, D-11 and D-20, each with the recommended option.
- Answered: hybrid's `pathlib` route once `open` is denied (D-10) - B, `pathlib` moved to the permissive extras (the
  owner, chat 2026-10-25, "focus on B"). Put back to the owner in the patch doc: a frame that declares no
  generation namespace failing closed (D-20).

## Decision Log
- 2026-10-25: the epic opened on the owner's ask; its children are the three existing tasks.
- 2026-10-25: D-10 - deny `open` under safe, hybrid and precision (the owner).
- 2026-10-25: D-11 - A + B, a static refusal of the name plus a runtime `__import__` wrapper (the owner).
- 2026-10-25: D-20 - an ACL capability rule declares the namespace; filtered builtins (the owner).
- 2026-10-25: D-10's pathlib route - B: `pathlib` becomes a permissive extra, so hybrid refuses it (the owner).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/codegen_room_policy_20261025/ (this epic's scripts and runs)
  - artifacts/core_protection_review_20261010/probes/ (the reproducers and their 2026-10-10 outputs; the review's)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure; the review's pack stays with the review.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this epic; 2026-10-25.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested

## Notes
- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's ask (chat 2026-10-24), after melder_0 listed what it could take next:
    "focus on 2 and 3 make an epic for each and investigate them" - 2 being the three codegen-room p1
    defects D-10, D-11 and D-20. This epic reuses their three backlog tasks as its children (ticketing.md:
    search and reuse before creating), each moved to tickets/tasks/ and in_progress for melder_0 with its own
    board row. The investigation is read-only on src/ and tests/, runs on a /tmp copy of 0.2.8267 with the GIL
    off and on, and ends in one DECISION_REQUEST per task; no fix starts before the owner's answer and its
    patch docs.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:1-198
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:1-205
  - context_compass/tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md:1-220
  IMPACT: The defects are re-measured on today's tree before the owner is asked, so his answers rest on current code.
  NEXT: Run the four reproducers and the five strict xfails on the /tmp copy, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-38 (melder_2's NOTICE, 2026-10-24T23:21:55Z, consumed here): melder_2's lane
    (STORY-2026-10-24-testpypi_trusted_publishing_and_provenance) edits .github/workflows/release-candidate.yml,
    .github/scripts (testpypi_candidate.py, ci_policy.py, a new testpypi_provenance.py), a new .github/provenance/,
    tests/unit/github_workflows, .github/ci_cd, .github/BRANCH_WORKFLOW.md and system_docs/tests_components.md,
    with no src change, and rebuilds at its turn-in. melder_0 holds none of them. This epic's investigation
    touches none of them; a fix that adds tests updates tests_components.md after melder_2's turn-in or by
    arrangement with melder_2.
  EVIDENCE: context_compass/tickets/stories/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:29-36
  IMPACT: tests_components.md is not free for this epic until melder_2 turns in; a fix is the first step that needs it.
  NEXT: Check melder_2's board row before a fix updates tests_components.md.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T00:37:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered the epic's three decision requests in chat on 2026-10-25, each with the recommended
    option: D-10 deny `open` under safe, hybrid and precision (permissive and full_access stay open); D-11 A + B
    (a static refusal of the `__import__` name where an import list applies, plus a runtime `__import__` wrapper
    checking every root); D-20 an ACL capability rule declares the generation namespace and materialized code
    runs with the room's filtered builtins. Each task's DECISION note carries the one point its patch doc puts
    back to the owner (D-10 hybrid's pathlib route; D-11 A is static-only; D-20 a frame with no rule fails
    closed). Tranche order when the owner says go: D-10, D-11, D-20 - smallest to largest, each with its own
    patch docs, red tests, notch and rebuild.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:57-60
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:59-65
  - context_compass/tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md:58-63
  IMPACT: Milestone 2 is met; the epic moves to its fixes on the owner's go.
  NEXT: Ask the owner for the go on D-10 first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-39 (melder_2's NOTICE, 2026-10-25T00:40:40Z, consumed here): melder_2 turned in
    STORY-2026-10-24-testpypi_trusted_publishing_and_provenance (no src, no notch; its completion summary), and
    reports tests_components and tests_architecture updated with their indexes regenerated, the asset and
    bundle rebuild to follow.
    So the custody this epic recorded from M2-38 has ended: tests_components.md is free for this epic's fixes
    (re-read it before editing, and after melder_2's rebuild lands).
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:1-8
  IMPACT: A fix's tests_components entry no longer waits on melder_2.
  NEXT: Re-read tests_components.md at the first fix's test-doc step.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T01:29:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: BLOCKER
  CLAIM: The owner's go (chat 2026-10-25): "go ahead and do them one by one" - D-10, D-11, D-20 in that order.
    melder_0's implementation turn was stopped by the session's automated content filter, which withholds the
    response and forbids regenerating it; it is the third such stop on this epic's material, so melder_0 cannot
    carry the implementation in this session. Nothing in src/ was changed. The three tasks stay fully specified
    (the owner's decisions, acceptance criteria, files and the patch-doc plan in their Notes) for whoever takes
    them; the owner's go stands.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:1-263
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:1-267
  - context_compass/tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md:1-286
  IMPACT: The fixes are unstarted; the epic waits on an implementer.
  NEXT: The owner assigns the implementation to another agent or session.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:02:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner certified a new session as melder_0 (chat 2026-10-25) and directed "Go do the D-10 story
    first try that". The BLOCKER of 2026-10-25T01:29:39Z belonged to the earlier session and is lifted; the
    epic is in progress again. Tranche order and decisions stand: D-10 now, then D-11, then D-20, each with its
    patch docs before any src/ edit.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:217-236
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:233-262
  IMPACT: Milestone 3 starts with D-10; D-11 and D-20 rows wait on it.
  NEXT: D-10 patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:46:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: D-10 is closed, notched 0.2.8270: `open` is refused under safe, hybrid and precision and under the engine's
    no-projection default, `pathlib` is a permissive-only import root (the owner's B), every profile's file posture
    is pinned by tests and stated in its docstring, and the running note carries the section "Codegen rooms under the
    safe, hybrid and precision profiles refuse `open`". Milestone 3 is one of three. The tranche moves on: D-11 is
    ready (its blocker was D-10), D-20 waits for D-11. The running note's codegen section is the home for the D-11
    and D-20 Breaking entries, the same subject; this epic's artifact folder keeps D-10's runs and scripts beside the
    two tasks still to run.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-10_deny_file_access_under_safe_codegen_task.md:1-9
  - release_docs/next_version_release.md:177-205
  - context_compass/attention_board.md:121-122
  IMPACT: One of the epic's three defects is fixed; the next fix starts from the D-10 posture.
  NEXT: D-11 under the owner's one-by-one go: patch docs (A + B) first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
Scope: the three codegen-room p1 defects - D-10 `open` under safe, D-11 `__import__` past the import lists, D-20 a
materialize over live modules - each in its own child task. State: in_progress, melder_0. Milestones 1 (all three
re-measured on 0.2.8267) and 2 (the owner's three decisions, Notes) are met; milestone 3 is one of three: D-10 is
closed, notched 0.2.8270 (Note of 2026-10-25T08:46:00Z; its rebuild runs after its closure). Next: D-11, ready, under the
owner's one-by-one go - patch docs for A + B first - then D-20, blocked on D-11. The release note's codegen section
takes their Breaking entries.

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
