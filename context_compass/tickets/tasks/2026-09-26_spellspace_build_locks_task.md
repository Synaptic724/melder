

# Task: Can first builds of spellspace-scoped objects skip their build locks when the spellspace is thread-confined?

## Metadata
- Task ID: TASK-2026-09-26-spellspace-build-locks
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: review
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T21:16:14Z
- Updated: 2026-09-26T21:31:35Z

## Objective
Find out, with source evidence and a measured prototype, whether the first build of a `unique_per_spell_space`
object can skip the two lock pairs it takes today (the slot guard and the store leaf lock) without weakening any
guarantee. Each gauntlet cycle does two such builds (marker and root), about 0.3 us on Windows. Three questions:
1. Is a spellspace confined to one thread for melds, for both managed (`enter_spellspace`) and manual or registered
   spaces? Is that documented, enforced, or only assumed?
2. Which locks does a first spellspace-scoped build take, where are they emitted, and what does each protect
   (build once, lock order, purge, refusal to publish into a cleaned store)?
3. What would a lock-free confined path need (how the path is selected, purge and cleanup interplay), and what does
   it save on the VM?
Output: FACT and MEASURE notes plus a DECISION_REQUEST with a design sketch and the file owners. An implementation,
if chosen, is its own task behind patch docs and melder_0's agreement (his emission lane).

## Ticket Contract
- ENTRY_GATE: owner direction (~21:15Z) "ok cool so lets move on then and look at those"; the lifecycle part of lever
  1 closed as measured (tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1085-1149).
- EXECUTION_BOUNDARY: read-only on src/ and benchmarks/. Prototypes run on the VM copy (tree_0270, refreshed when
  needed). Artifacts go under artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/.
- DEPENDENCIES: melder_0 owns site-plan emission, the hydrators and the meld doors (spellspace_meld.py). The owner of
  creations.py is UNKNOWN. The confinement contract is the owner's decision.
- EXIT_GATE: the three questions answered with evidence; a measured prototype gain; a DECISION_REQUEST to the owner.
- FAILURE_ESCALATION: CONFLICT if some kind of spellspace is not confined; BLOCKER if build-once cannot hold without
  the lock.

## Scope Boundaries
- In scope: SpellSpace, SpellSpacePool, SpellSpaceThreadState, the SpellSpaceMeld first-build path, Creations
  (slot_guard, add_creation, purge, cleanup refusal) and the emitted spellspace-scoped build code.
- Out of scope: src or benchmark edits; conduit-scoped (lesser) builds, whose shared scopes keep their locks; the
  lifecycle bookkeeping (closed).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: All three questions are answered with source evidence, including read step 3 (creations.py and
  both emitters in full). The nested-lock prototype is measured, and the updated DECISION_REQUEST is with the owner.

## Steps / Checklist
- [x] Read the spellspace confinement contract: managed and manual spaces, the per-thread stack, recycle, purge.
- [x] Read the first-build path for unique_per_spell_space: door, executor or site plan, slot_guard, publication.
- [x] Read what relies on those locks: purge, cleanup refusal, lock order.
- [ ] VM prototype (no tree edit) of a lock-free confined path; A/B with probe_steps3 (1 and 2 threads) and the
      concurrency suites. Partial: the nested-lock removal was timed at 1 and 2 threads. The lock-free confined
      path was not prototyped because it needs a new thread rule. Suites belong to an implementation task.
- [x] DECISION_REQUEST with a design sketch and the file owners.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/ (probes, runs, design sketch)

## Files / Paths Impacted
- context_compass/ tickets, boards and artifacts only.

## Validation
- Not run.

## Risks / Rollback Notes
- A manual or registered spellspace might legitimately be used from more than one thread; then a lock-free path
  must be limited to spaces that are provably confined.
- Build-once, purge ordering and the refusal to publish into a cleaned store depend on the slot guard today.
- The 2026-09-25 lock design (consumer-first build locks, store lock as a leaf) must stay deadlock-free.
- No rollback needed: no tree edits.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No lock is called removable on the strength of a docstring alone: the source and a concurrency test decide.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/
  - artifacts/gauntlet_runtime_speed_20260926/lever1/owner_windows_parts2_20260926_2110.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure; the owner confirms retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T21:16:14Z
  TYPE: PLAN
  CLAIM: Order of work:
    1. Read the confinement contract in spell_space.py, spell_space_pool.py and spell_space_thread_state.py,
       covering managed and manual spaces.
    2. Read the first-build path: spellspace_meld.py (door), the site-plan emission of a spellspace-scoped step,
       and creations.py (slot_guard, add_creation, purge, the cleaned-store refusal).
    3. Only if (1) and (2) allow it, prototype a confined lock-free path on the VM copy and A/B it.
    melder_0 gets a NOTICE before anything leaves the VM, since emission and the doors are his files.
  EVIDENCE:
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1085-1135
  - artifacts/gauntlet_runtime_speed_20260926/lever1/lifecycle_cprofile_vm.txt:6-7
  IMPACT: Discovery only; the owner decides after the DECISION_REQUEST.
  NEXT: Read the spellspace confinement contract in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:18:46Z
  TYPE: FACT
  CLAIM: Two findings from the source and the generated code.
    - Confinement covers the managed enter/exit lane, not melds. The contract as written: the pool hands a space
      to one thread, it lives on that thread's stack, and the LIFO-validated exit runs lock-free. Nothing forbids
      or checks melds into a space from another thread while it is active, and SpellSpace.meld has no active-scope
      check (the earlier RISK). The slot guard is therefore what keeps unique_per_spell_space build-once today
      when two threads meld into the same space. Dropping it is a contract change, the owner's call.
    - Every first build of a slotted object takes the same slot guard twice. The creation-context door
      (unique_per_conduit and spellspace templates) takes the store's slot guard, rechecks and calls the executor.
      The site-plan executor then reads the store again, and its root-site miss takes the same RLock again
      (re-entrant) and rechecks before building and publishing with a direct dict set. Per first build that is
      two nested acquisitions of one lock and three lookups where one acquisition and two lookups decide the same
      thing. This explains 9 RLock pairs per cycle with two builds against 5 without (cProfile).
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:21-93
  - src/melder/aether/conduit/spell_space/spell_space.py:305-363
  - src/melder/aether/conduit/creations/creations.py:1068-1104
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:505-600
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1367-1377
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/site_plans_session_marker.txt:1-117
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/door_templates_conduit_spellspace.txt:1-45
  IMPACT: The nested second acquisition is a contract-free saving on every slotted first build (session, marker and
    root in a gauntlet cycle), whatever the confinement answer, because it is the same lock taken by the same
    thread. It lives in melder_0's emission (the door compiler and the site-plan lowering), so any change there
    is a handoff or a NOTICE. Removing the one remaining guard for spellspace builds needs the owner to restrict
    melds into a space to the thread that entered it.
  NEXT: Size the nested-lock saving on the VM with a prototype copy (door lock dropped for the conduit and
    spellspace routes, which the site plan still locks), using probe_steps3 at 1 and 2 threads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:19:52Z
  TYPE: MEASURE
  CLAIM: Dropping the nested second acquisition saves about 0.3 us per worker_a cycle on the VM. The prototype copy
    (tree_proto) is tree_0270 with the door lock replaced by the unlocked recheck on the unique_per_conduit and
    spellspace no-overrides routes; the site plan still locks its root site. probe_steps3, warm caches, three
    interleaved rounds, trimmed means:
    - 1 thread: steps 7,122 -> 6,838 ns (-285, -4.0%); session first build -77, marker -73, root -89; request
      window 4,219 -> 4,027 (-191).
    - 2 threads: 9,623 -> 9,327 ns (-296); window 5,585 -> 5,399 (-186).
    - The lifecycle does not change, as expected.
    This measures time only. The prototype is not a safe shape: another executor behind those door routes that
    does not lock its root site would lose build-once.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/ab_door_lock_vm.txt:1-13
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/probe_steps3.py:1-105
  IMPACT: A contract-free saving of about 4% of a worker cycle exists. It needs one of two safe shapes, both in
    melder_0's emission:
    (a) the door keeps its lock, and the normal site plan skips its root-site guard when the door calls it;
    (b) the door drops its lock only for executors that declare they lock their root site (set at hydration).
    Removing the one remaining guard for spellspace builds (about 0.15 us more per cycle, estimated from the
    RLock pair cost) stays a contract change.
  NEXT: DECISION_REQUEST to the owner: hand (a)/(b) to melder_0, or do it with his agreement; and decide the
    spellspace thread contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:19:52Z
  TYPE: DECISION_REQUEST
  CLAIM: Spellspace build locks, outcome for the owner.
    (1) Recommended: remove the nested double lock on first builds. It is the same lock taken twice by the same
        thread, so no guarantee changes. It covers every slotted scope (per-conduit, spellspace, lineage, cluster),
        saves about 0.3 us per worker cycle on the VM (4%), and lives in melder_0's door compiler and site-plan
        lowering. Options: hand it to melder_0, or melder_2 does it with his agreement. Either way it needs the
        concurrency suites, a 30k soak and an owner Windows run.
    (2) Not recommended now: drop the remaining guard for spellspace-scoped builds. That requires a new rule, that
        only the thread that entered a spellspace may meld into it; today nothing forbids or checks it. It saves
        about 0.15 us more per cycle and ties into the open active-scope RISK (the docs promise a check the code
        does not make).
  EVIDENCE:
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:138-194
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/ab_door_lock_vm.txt:1-13
  IMPACT: The owner picks who implements (1) and whether (2) is ever wanted.
  NEXT: Report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:27:40Z
  TYPE: FACT
  CLAIM: Correction of this ticket's state. The 21:20:09Z write, made after a context compaction and before the
    REONBOARD attestation, moved the task to review and ticked read step 3 (purge, cleanup refusal, lock order).
    Step 3 was not done: Creations.purge and the cleaned-store refusal were not read, and what add_creation relies on
    was not recorded, so question 2 ("what does each lock protect") is not fully answered and the EXIT_GATE is not
    met. Status goes back to
    in_progress and step 3 is unticked. The 21:20:09Z fix of the DECISION_REQUEST evidence range (:144-174 ->
    :136-192) was correct and stays.
  EVIDENCE:
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:15-26
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:28-35
  IMPACT: The DECISION_REQUEST stands, but it cannot say "no guarantee changes" for purge and the cleaned-store
    refusal until creations.py is read. No tree edit was involved.
  NEXT: Read src/melder/aether/conduit/creations/creations.py in full and note what the slot guard and the store
    lock protect in purge, publication and cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:30:55Z
  TYPE: FACT
  CLAIM: What each lock protects, from creations.py and the two emitters read in full (question 2, read step 3).
    - The slot guard carries build-once: the one thread holding it across recheck, construct and publish is the only
      builder of that slot. It is an RLock, and its docstring names the door-plus-root-plan-step double take as
      intended ("a door and the root plan step ... can both take it"). The same thread re-entering adds no exclusion.
    - The store lock is not taken on the gauntlet's first builds. Objects without disposal methods publish with one
      lock-free dict store (add_creation's first branch; the site plan emits cN._creations[sid] = vN). Only
      disposal-bearing publishes, many appends, purge detach, extract/restore and whole-store swaps take it. The
      Objective's "slot guard and store leaf lock" premise is wrong for these builds: the second pair per build is
      the nested slot guard.
    - Purge takes the slot guard, then the store lock, so it waits for an in-flight build of the same slot and
      never removes a half-built entry.
    - The cleaned-store refusal does not use the slot guard. cleanup() detaches under the store lock and does not
      wait for builds. A disposal-bearing publish sees _cleaned under the store lock and is refused (object
      disposed, RuntimeError). A plain publish racing cleanup is a documented caller contract violation.
    - New: in the hooks lanes the door returns (instance, created). created=True is exact only because the door's
      guard and recheck let exactly one thread call the executor. The plan rechecks inside the executor and does
      not report whether it built.
    - The site plan builds a site's children before taking that site's guard ("A user constructor never runs under
      another site's build lock"). But the door takes the root's guard before calling the plan, so today the
      children's constructors run under the root's guard.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:44-67
  - src/melder/aether/conduit/creations/creations.py:182-239
  - src/melder/aether/conduit/creations/creations.py:356-405
  - src/melder/aether/conduit/creations/creations.py:407-453
  - src/melder/aether/conduit/creations/creations.py:455-530
  - src/melder/aether/conduit/creations/creations.py:650-812
  - src/melder/aether/conduit/creations/creations.py:1009-1044
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-694
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:884-920
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1293-1332
  IMPACT: The two safe shapes from the 21:19:52Z MEASURE differ.
    - (a) The door keeps its guard and a door-called plan skips its root-site guard. Nothing observable changes:
      build-once, purge waiting, the refusal, lock order and exact created flags all hold. It needs the root guard
      dropped only in plans every caller reaches under the door's guard. Whether any caller reaches the normal
      plan without the door (fast-door miss, override doors) is UNKNOWN.
    - (b) The door drops its guard for executors that lock their root site. This is safe only in the no-hooks
      lanes. In hook lanes, two racing first melds would both report created=True and fire creation hooks twice
      for one object. In no-hooks lanes it also moves a racing root purge's ordering point from door entry to the
      root-site guard (a valid order for an unordered race), and it stops holding the root's guard across child
      constructors.
    Either shape saves the measured ~0.3 us per worker cycle.
  NEXT: DECISION_REQUEST to the owner with the shape constraint, superseding the 21:19:52Z request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:31:35Z
  TYPE: DECISION_REQUEST
  CLAIM: Spellspace build locks, updated outcome for the owner (supersedes the 21:19:52Z request).
    (1) Recommended: remove the nested second take of the slot guard on first builds. It saves about 0.3 us per
        worker cycle on the VM (-4%). The safe shape: the door keeps its guard, and the plan skips its root-site
        guard wherever the door always holds it. Nothing observable changes. The simpler shape, where the door
        drops its guard, is safe only in the no-hooks lanes, because the door's guard is what keeps the hook
        lanes' "created" flag exact. The code is melder_0's (door compiler, site-plan lowering), and the
        slot_guard docstring in creations.py names the double take. Who implements: melder_0, or melder_2 with
        his agreement. Either way it needs patch docs, the concurrency suites, a 30k soak and an owner Windows run.
    (2) Not recommended now: dropping the remaining guard for spellspace builds needs a new rule (only the entering
        thread may meld into a space). It saves an estimated 0.15 us and ties into the open active-scope RISK.
  EVIDENCE:
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:170-194
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:235-281
  - artifacts/gauntlet_runtime_speed_20260926/spellspace_build_locks/ab_door_lock_vm.txt:1-13
  IMPACT: The owner picks who implements (1) and whether (2) is ever wanted. An implementation opens as its own task.
  NEXT: Report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:38:34Z
  TYPE: DECISION
  CLAIM: The owner answered the DECISION_REQUEST (~21:37Z): "just do it, melder_0 is done go and finish your work
    implement your 4% savings and implement everything you need to do, make it safe, we don't want unsafe code".
    melder_2 implements (1), the safe shape where the door keeps its guard, in its own task. (2), the spellspace
    thread rule, is not pursued.
  EVIDENCE: tickets/tasks/2026-09-26_spellspace_build_locks_task.md:283-302
  IMPACT: This discovery task has answered its questions and waits only for the owner's turn-in. Implementation is
    tracked in tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md.
  NEXT: Owner turns in this task when accepting the implementation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review with the owner. Spellspace confinement covers only the managed enter/exit lane. Melds into an active space
from another thread are neither forbidden nor checked, so the slot guard still carries build-once, and dropping it is a
contract change. Every first build of a slotted object takes the same slot guard twice (door, then the site plan's
root-site miss). The store lock is not taken for objects without disposal methods. Removing the nested take saves about
0.3 us per worker cycle on the VM (-4%). Safe shape: the door keeps its guard and the door-called plan skips its
root-site guard. The door-drops-guard shape is safe only in the no-hooks lanes (created-flag exactness). The code is
melder_0's. DECISION_REQUEST (last note): who implements, and whether a spellspace thread rule is ever wanted. Not run:
concurrency suites for a safe shape.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
