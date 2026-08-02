# Epic: Aether core control plane & logging bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-aether-core-logging
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p0
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T16:19:47Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
12 bugs in this subsystem (2 Critical, 5 High, 5 Medium). Aether/Nexus singleton control plane, link create/sever/change-control, AetherUtilitySystem, SafeLogger ownership & refresh. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- BUG-002 - Aether singleton initialization is not once-only (concurrent construction races the process root).
- BUG-003 - Nexus singleton initialization is not once-only (same class of root race).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_core_control_plane.md
  - codex/2026-07-17_melder_bug_audit_aether_logging_helpers.md
  - codex/2026-07-17_melder_bug_audit_logger_ownership_refresh_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_f; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 12 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
- DEPENDENCIES: The audit reports listed above; system_docs/src_architecture.md + src_components.md (read the relevant sections on-demand per engineer context_protocol); patch-framework gating for any system-impacting change.
- EXIT_GATE: Every listed bug is either fixed with a regression test proving the corrected behavior, or explicitly reclassified (duplicate / intentional) with evidence and owner acceptance; board + closure sync complete.
- FAILURE_ESCALATION: Raise DECISION_REQUEST for any fix that changes public API shape/semantics or crosses subsystem boundaries; BLOCKER if a fix cannot be made without violating a documented invariant; CONFLICT if the audit finding contradicts current source on re-read.

## Goals (Outcomes)
- All Critical and High findings in this subsystem fixed at root cause with regression tests.
- Medium/Low findings fixed or explicitly, evidencedly deferred with owner sign-off.
- No new invariant violations introduced; existing focused test suites stay green (user-run).

## Non-Goals (Explicit Exclusions)
- Feature work, redesign, or optimization beyond correcting the audited defects.
- Bugs in other subsystems (owned by their own epics).
- Re-litigating findings the audit already excluded as intentional/duplicate without new evidence.

## Scope Boundaries
- In scope: src/melder/aether/aether.py; src/melder/nexus/nexus.py; src/melder/utilities/logger/**
- Out of scope: unrelated modules, public API redesign, performance passes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Bug membership, severities, and evidence are FACT-sourced from the audit manifests; the epic is routable and ready for its owning agent to begin (Critical/High first).

## State Transition Event (2026-07-18T09:15:00Z)
- from_state: ready
- to_state: in_progress
- transition_reason: helper_f (onboarded + owner-certified this session) claimed the lane on user direction; board row flipped in_progress in the same pass. Starting Story 01 (Criticals BUG-002/003) with audit-report read + source re-verification.

## Success Metrics
- 100% of Critical + High bugs in this subsystem closed with a passing regression test each.
- 0 audit findings left in an undocumented state at closure.

## Requirements (Functional + Non-Functional)
- Root-cause fixes per technical_expertise: no blanket defensive guards; prove optionality via lifecycle/call-path evidence.
- Every touched function/class keeps a rich, accurate docstring; comments preserved/improved.
- Tests: pytest, unit-first; component/integration only where correctness cannot be proven by unit tests. Thread-safety is a first-class assertion target given 3.14t.
- Truthful validation: never claim tests/coverage ran unless actually run; otherwise report "Not run."

## Constraints / Assumptions
- Runtime is Python 3.14t (free-threaded, nogil); real threading, no multiprocessing; thread-safety is priority #1.
- synaptic_python_developer craft rules apply (Optional/Union not PEP 604; no `from __future__ import annotations`; TYPE_CHECKING-first; empty __init__.py; deterministic del-based cleanup; banned patterns).
- Audit env was CPython 3.13.5; reproductions may need the repo venv/import path.

## Dependencies / External References
- Audit reports listed under Problem/Opportunity.
- system_docs/src_architecture.md, system_docs/src_components.md, readable_src_graph.json (on-demand).

## Milestones (Track Progress)
- [ ] Milestone 1: Criticals closed - every Critical bug fixed + regression test green (user-run).
- [ ] Milestone 2: Highs closed - every High bug fixed + regression tests.
- [ ] Milestone 3: Mediums/Lows resolved or owner-accepted deferrals recorded.
- [ ] Milestone 4: Subsystem focused suites green (user-run) + docs/graph updated where boundaries changed.

## Stories (Required to Complete)
- [ ] Story: STORY-aether_core_logging-01 - BUG-002-007 (core_control_plane): CRITICAL BUG-002/003 non-once-only singleton init; link create/sever leaves half-created/asymmetric state; public Conduit.link bypasses change-control admission.
- [ ] Story: STORY-aether_core_logging-02 - BUG-146-149 (aether_logging_helpers): Concurrent first construction of AetherUtilitySystem races; one child cleanup failure permanently bricks the Aether utility system.
- [ ] Story: STORY-aether_core_logging-03 - BUG-278-279 (logger_ownership_refresh_appendix): Aether logger replacement abandons the displaced owned sink; Nexus same-sink refresh cleans the sink the replacement still owns.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-aether_core_logging-01 (BUG-002-007)
- [ ] Task: Complete story STORY-aether_core_logging-02 (BUG-146-149)
- [ ] Task: Complete story STORY-aether_core_logging-03 (BUG-278-279)
- [ ] Task: Re-verify each finding against current source before fixing (audit was read-only; some may already be partially addressed).
- [ ] Task: Verify Ticket Microcycle enforcement across active stories/tasks.

## Acceptance Criteria (Epic Done)
- Every listed bug id is fixed-with-test or documented as duplicate/intentional/deferred with owner acceptance.
- attention_board.md + artifact_board.md synced; epic moved to completed/ with summary.

## Risks / Mitigations
- Risk: cross-subsystem coupling means a fix here shifts behavior elsewhere. Mitigation: DECISION note + owner confirm before crossing boundaries.
- Risk: concurrency fixes are hard to test deterministically. Mitigation: controlled interleave/barrier probes as the audit used; mark thread-safety assertions explicitly.
- Risk: audit finding is stale vs current source. Mitigation: re-verify each before fixing; reclassify with evidence if not reproducible.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No "fix" from UNKNOWN/HYPOTHESIS - reproduce first, then fix at root cause.
- [ ] No defensive-guard sprawl to paper over a contract violation.

## Validation / Test Approach
- Reproduce each bug (deterministic probe/test) -> fix -> regression test asserts corrected behavior.
- Focused pytest per touched module; thread-safety via controlled interleaves. Coverage verified by the user (agents report "Not run" until then).

## Rollout / Adoption Plan
- Land fixes in small, reviewable, per-bug (or per-tight-group) changes; keep public API stable.

## Open Questions
- Are any listed findings already partially fixed since the 2026-07-17 audit snapshot? (Re-verify at story start.)

## Decision Log
- DATETIME: 2026-07-18T08:57:34Z
  DECISION: Epic scoped by subsystem so each owning agent keeps a tight, coherent context window. Bug membership and ranges are FACT-sourced from the 2026-07-17 audit MANIFEST + wave manifests. Fix order within the epic: Critical -> High -> Medium -> Low.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a until an artifact (e.g., a fix design note) is produced.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - Aether/Nexus singleton control plane, link create/sever/change-control, AetherUtilitySystem, SafeLogger ownership & refresh.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 12 audited bugs (2 Critical, 5 High, 5 Medium) are grouped into this subsystem epic for helper_f; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_f a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_f starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T09:15:00Z
  TYPE: PLAN
  CLAIM: helper_f claimed this epic (status in_progress; board row synced). Execution order per the
    epic decision log: Story 01 (BUG-002-007, core_control_plane) first, Criticals BUG-002/003 before
    the Highs, then Story 02 (BUG-146-149) and Story 03 (BUG-278-279). Each finding is re-verified
    against current source before any fix per the epic's re-verify task.
  EVIDENCE:
  - tickets/epics/2026-07-17_bugfix_aether_core_logging_epic.md:89-99
  - attention_board.md:60-60
  IMPACT: The lane is routed and owned; the next tranche is unambiguous for any re-entering agent.
  NEXT: Read codex/2026-07-17_melder_bug_audit_core_control_plane.md, then re-verify BUG-002/003
    against src/melder/aether/aether.py and src/melder/nexus/nexus.py and record FACT/CONFLICT notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T09:40:00Z
  TYPE: FACT
  CLAIM: BUG-002 re-verified CONFIRMED against current source. Aether.__new__ double-checks only
    ALLOCATION under the class RLock; Aether.__init__ tests `if not Aether._initialized` and runs the
    full construction body (Crystallizer, AetherUtilitySystem, LoadGate, Nexus, registries) with NO
    lock held. Two threads entering Aether() before the first sets `_initialized = True` (aether.py:138)
    both pass the line-107 test and construct subsystem graphs twice on the same instance,
    last-writer-wins - exactly the audit's `same_instance=True, crystallizers_created=2` repro.
  EVIDENCE:
  - src/melder/aether/aether.py:70-84
  - src/melder/aether/aether.py:107-144
  IMPACT: Process-root bootstrap can leak/replace Crystallizer, LoadGate, Nexus, and frame registries
    under concurrent first boot on 3.14t - Critical, foundation-level.
  NEXT: Fix by moving the initialized-check + body under Aether._lock (double-checked init); see the
    PLAN note below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T09:40:00Z
  TYPE: FACT
  CLAIM: BUG-003 re-verified CONFIRMED against current source. Nexus.__new__ locks allocation only;
    Nexus.__init__ tests `Nexus._initialized` (nexus.py:181) and runs the whole manager-graph body
    (RiftGateController, FrameACLManager, FrameDescriptorManager, NexusFrameManager, registries)
    outside Nexus._lock, setting `_initialized = True` only at nexus.py:216. Same race class as
    BUG-002; matches the audit's `gate_controllers_created=2` repro. The aether-None ValueError path
    (nexus.py:185-190) takes the lock only to reset bookkeeping, not to guard construction.
  EVIDENCE:
  - src/melder/nexus/nexus.py:129-137
  - src/melder/nexus/nexus.py:181-222
  IMPACT: Concurrent first Nexus() construction double-builds managers/registries with last-writer
    publication losing live state - Critical.
  NEXT: Same fix shape as BUG-002 under Nexus._lock, preserving the logger-refresh re-entry contract
    and the aether-None failure contract; see the PLAN note below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T09:40:00Z
  TYPE: PLAN
  CLAIM: Fix plan for BUG-002/003 (root cause, no defensive guards): make both __init__ bodies
    once-only via double-checked init under their existing class RLocks - fast-path return when
    `_initialized`, re-check under the lock, construct, set `_initialized = True` while still holding
    the lock; failure paths keep the existing instance/flag reset semantics. Deadlock-safety is
    evidenced: construction nesting is one-way Aether._lock -> Nexus._lock (aether.py:137) and no
    subsystem constructed inside either body calls Aether()/Nexus() back (grep of crystallizer,
    aether_utility_system, load_gate, rift_gate_controller, frame_acl_manager,
    frame_descriptor_manager, nexus_frame_manager ctors: zero hits). Nexus keeps its two contract
    lanes inside the lock: logger-only refresh when already initialized, ValueError reset when first
    init lacks aether. Docstring Threading sections updated to state the once-only guarantee.
    Regression tests: two deterministic barrier-interleave unit tests mirroring the audit probes
    (wrapped Crystallizer ctor for Aether, wrapped RiftGateController ctor for Nexus), each asserting
    exactly one construction and both threads receiving the same fully-initialized instance.
  EVIDENCE:
  - src/melder/aether/aether.py:107-144
  - src/melder/nexus/nexus.py:181-222
  IMPACT: Closes both Criticals at the root with no hot-path cost (fast path stays lock-free after
    first boot) and no public API change.
  NEXT: Owner confirms the edit plan; then implement in aether.py + nexus.py and add the two
    regression tests; report pytest as "Not run." unless actually executed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T12:55:11Z
  TYPE: FACT
  CLAIM: BUG-002 and BUG-003 IMPLEMENTED per the owner-confirmed plan. Aether.__init__ and
    Nexus.__init__ are now once-only: lock-free `_initialized` fast path, re-check + full
    construction under the class RLock, latch flipped while the lock is held, failure paths reset
    `_instance`/`_initialized` under the held lock. Nexus keeps both contract lanes inside the lock
    (logger-only refresh for already-initialized callers, ValueError + bookkeeping reset for a
    first init without aether). Docstring Contract/Threading sections updated on both methods (the
    stale "initializes the default frame eagerly" line corrected to the lazy-frames law). Two
    symptom-named regression suites added: barrier-choreographed interleave proving exactly one
    construction-body entry with both racing callers receiving the same fully built singleton,
    plus a sequential no-rebuild proof (Aether) and a missing-aether reset proof (Nexus). All four
    files byte-verified on device after commit; py_compile + AST lock-guard checks green in the
    sandbox. VALIDATION: pytest Not run - the reachable VM carries Python 3.10.12 and melder
    requires 3.13+/3.14t; the suites ride the owner's next run, REOPEN on red.
  EVIDENCE:
  - src/melder/aether/aether.py:86-171
  - src/melder/nexus/nexus.py:139-260
  - tests/unit/melder/aether/test_aether_singleton_init_once_only_regression.py:1-170
  - tests/unit/melder/aether/test_nexus_singleton_init_once_only_regression.py:1-168
  IMPACT: Both Criticals in this epic are closed-pending-owner-run; Story 01 continues with the
    Highs. BOARD NOTE: the 09:15Z claimed row was dropped by the 09:56Z board rewrite
    (write-fault class); repaired 12:55Z with an additive, md5-gated device-side write.
  NEXT: Re-verify BUG-004/005 (ConduitWard `_create_new_contract` half-created contract /
    `_remove_contract` asymmetric spellbook state after failure) against current source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T13:23:39Z
  TYPE: FACT
  CLAIM: BUG-004 re-verified CONFIRMED then IMPLEMENTED. Confirmed: `_create_new_contract` wrote the
    Contract into both ward registries + indexes BEFORE the two fallible spellbook bucket creates and
    re-raised without rollback - a failed public link left both wards reporting the link with only
    A's bucket existing. Fix (in-ward only, commit-last ordering): both bucket creates and Contract
    construction now run FIRST; ward publication is plain dict writes after every fallible step
    succeeds; rollback removes only buckets the call itself created (pre-existence = fault residue,
    tracked under both held ward locks) via `_remove_link_contract` - the exact inverse of a fresh
    empty bucket; rollback failures are logged best-effort and never mask the original error.
    Regression suite (self-contained fake harness mirroring the real four-map lockstep): audited
    second-create failure -> zero observable state + recoverability; own-side failure -> zero state;
    residue bucket survives rollback. VALIDATION: pytest Not run - rides the owner's 3.14t run.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:719-825
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_link_failure_atomicity_regression.py:1-321
  IMPACT: A failed link can no longer split topology truth from spellbook sharing truth.
  NEXT: BUG-005 fix awaits the DECISION_REQUEST below; BUG-006/007 re-verification after.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T13:23:39Z
  TYPE: DECISION_REQUEST
  CLAIM: BUG-005 (`_remove_contract` leaves asymmetric spellbook state when side B's sever raises
    after side A's succeeded) is re-verified CONFIRMED, but its honest fix crosses into
    spellbook.py, which the epic contract gates behind owner confirm. The destructive step is
    `_clear_contracted_spells_for_conduit` (per-spell unregister + SpellIndex detach + risk-manager
    unregister) - a severed side is NOT trivially restorable. Options:
    (A) RECOMMENDED: add one narrow seam pair to Spellbook - `_detach_link_contract(peer_id)`
        (pop the five maps in lockstep, return the payload; reversible, non-destructive) +
        `_reattach_link_contract(peer_id, payload)`. `_remove_contract` then detaches A, detaches B
        (on failure: reattach A, raise), passes the point of no return, deletes registries/indexes,
        and only THEN runs the destructive per-spell teardown on both detached payloads. True
        atomicity, ~2 small additive private methods in spellbook.py.
    (B) Ward-side capture/restore using existing verbs (`_create_link_contract` +
        `_add_contracted_spell` per captured spell): no new seams, but the ward must privately read
        the contracted map to capture, and restore replays heavier machinery (risk-manager +
        staged-key churn) - more moving parts under failure.
    (C) Commit-first reorder (registry deletes before bucket severs): no restore machinery, but a
        B-side sever failure then leaves an orphaned B bucket with no contract - trades one
        asymmetry for another, weakest.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:940-980
  - src/melder/aether/spellbook/spellbook.py:2878-2950
  IMPACT: Blocks the BUG-005 implementation only; the rest of the story continues.
  NEXT: Owner picks A/B/C (rec: A); on A, helper_f implements the seam pair + ward reorder + a
    symptom-named regression suite in the same shape as the BUG-004 one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T13:32:43Z
  TYPE: DECISION
  CLAIM: Owner ruled BUG-005 Option A ("do your ideas recommended", 2026-07-18). IMPLEMENTED:
    three additive private seams on Spellbook - `_detach_link_contract` (lockstep-guarded
    reversible pop of the five bucket maps; None when absent), `_reattach_link_contract`
    (exact restore; refuses to overwrite), `_destroy_detached_link_contract` (payload-driven
    mirror of the clear path: `_spell_id_pool` pops for selected ids, staged-key refresh,
    best-effort risk-manager unregisters). `_remove_contract` is now two-phase: detach A ->
    detach B (failure restores A exactly and re-raises; restore failures logged, never mask) ->
    commit via non-fallible residue-tolerant pops (ward registries + indexes) -> destroy both
    payloads best-effort-loud -> existing consumer invalidation + emissions unchanged. The old
    `_sever_link_contract` call pair is gone from `_remove_contract`; the verb itself remains for
    future callers. Regression suite: audited B-side failure -> contract intact both sides + A's
    bucket restored WITH borrowed-spell content + clean sever after disarm; clean sever destroys
    both sides (pool ids released); destroy failure is per-side best-effort and cannot resurrect
    topology. py_compile + AST phase-order checks green in sandbox. VALIDATION: pytest Not run -
    rides the owner's 3.14t run, REOPEN on red.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2951-3141
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:940-1105
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_sever_failure_atomicity_regression.py:1-380
  IMPACT: Story 01 has 4 of 6 bugs closed-pending-owner-run (BUG-002/003/004/005). A failed sever
    can no longer produce the audited asymmetric split-brain.
  NEXT: Re-verify BUG-006 (public Conduit.link bypasses change-control admission - the sever side
    already transacts; the link side must enter the registered link strategy) and BUG-007
    (CounterSwitch cleanup deletes `_tickets` after waking waiters) against current source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T13:59:23Z
  TYPE: FACT
  CLAIM: BUG-006 and BUG-007 re-verified CONFIRMED against fresh device stage, with owner
    constraints recorded verbatim before implementation. BUG-006: public `Conduit.link`
    (conduit.py:3936) mutates the ward directly under only the conduit lock while `sever_link`
    (conduit.py:4271) wraps the identical shape in a self-admitted `unlink` transaction; the
    `begin_transaction` LINK branch (conduit.py:2487-2506) is fully built - it even stamps
    `origin_surface: "conduit.link"` metadata - and is unreachable from the public verb. Owner
    constraint: "conduit link should be using mediator". BUG-007: `CounterSwitch.cleanup`
    (counter_switch.py:74-98) sets the event (waking parked `selector()` followers) then dels all
    four slots, so a woken follower's `return len(self._tickets)` (line 197) dies AttributeError.
    Owner constraint: CounterSwitch stays "as lockless as possible". Governing in-repo precedent:
    `LoadGate.cleanup` (load_gate.py:73-112) - retained terminal surfaces, no del posture, parked
    waiters re-check after waking.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3889-3963
  - src/melder/aether/conduit/conduit.py:2487-2506
  - src/melder/utilities/synchronization/counter_switch.py:74-98
  - src/melder/utilities/synchronization/load_gate.py:73-112
  IMPACT: Both remaining Story 01 bugs are confirmed live with the fix constraints pinned; no
    scope drift possible.
  NEXT: Implement both per the constraints (link -> mediator transaction mirroring sever_link;
    cleanup -> retained-terminal-surface release, hot paths untouched) + symptom-named suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T14:05:00Z
  TYPE: DECISION
  CLAIM: BUG-006 and BUG-007 IMPLEMENTED per the owner constraints. BUG-006: `link()` now wraps
    its ward mutation in `with self.transaction(ChangeTransactionType.LINK, conduits=[self,
    target_conduit])` - the exact `sever_link` shape: mediator admission BEFORE the conduit lock,
    ward `_link` inside the window, `success=False` finalization on ward failure; every pre-check
    (state/posture/dynamic/type/creation-context) stays ahead of admission so rejected calls never
    open a transaction; docstring gained an Admission section + denial Raises line. BUG-007:
    `cleanup()` is now a retained-terminal-surface release - serializes only on the EXISTING
    leader-claim lock (teardown-only; AST-verified `advance` has zero locks, `selector` has exactly
    the one pre-existing claim lock, and the >=2 fast path's first two statements are unchanged),
    clears tickets, zeroes the mirror, sets the event, marks cleaned, and DELETES NOTHING: all four
    slots stay alive per the LoadGate tombstone law. `selector()` re-checks `_cleaned` at its two
    cold spots (inside the claim lock, and post-wake) and returns terminal 0 - a post-cleanup
    claim can no longer clear the terminally set event and park followers forever. VALIDATION:
    BUG-007 suite (5 tests, real threads, gate-choreographed wake-after-teardown interleave)
    EXECUTED in the sandbox harness (py3.10 + Cleanable only): green on fixed code, red on old
    code reproducing the audited AttributeError('_tickets') deterministically. BUG-006 suite
    (3 tests: admission-order journal start->ward->end with origin_surface/conduit_ids metadata;
    denial blocks the ward mutation; ward failure ends success=False) rides the owner's 3.14t run
    with the rest: full-repo pytest Not run - REOPEN on red. py_compile green on all four files.
    TICKET WRITE-FAULT: the device epic was reverted to its pre-claim 08:57Z state at ~13:33Z
    (mtime evidence), dropping the whole note chain; repaired additively in this commit.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3889-3977
  - src/melder/utilities/synchronization/counter_switch.py:61-125
  - src/melder/utilities/synchronization/counter_switch.py:170-232
  - tests/unit/melder/aether/conduit/test_conduit_link_mediator_admission_regression.py:1-260
  - tests/unit/melder/utilities/synchronization/test_counter_switch_cleanup_waiter_release_regression.py:1-260
  IMPACT: Story 01 is 6 of 6 bugs closed-pending-owner-run (BUG-002/003/004/005/006/007). Next
    tranche is Story 02 (BUG-146-149, aether_logging_helpers).
  NEXT: Owner runs the suites on 3.14t; helper_f proceeds to Story 02 re-verification
    (AetherUtilitySystem construction race + child-cleanup bricking) on user direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T14:29:52Z
  TYPE: FACT
  CLAIM: CORRECTION of the 14:05Z note's "ticket write-fault" claim - NO revert ever happened.
    Root cause found while re-verifying Story 02: the device_stage_files bridge can serve STALE
    SNAPSHOT BYTES for a path while reporting the true current device mtime. Proof: staged
    aether.py (md5 77b0f439...) showed the pre-BUG-002-fix code while the LIVE device file
    (md5 bc1d65e8..., verified via device-side md5sum + full base64 pull through device_bash)
    carries the committed fix intact; a re-stage of the same path returned the same stale bytes.
    The 13:59Z staged epic was the same illusion: the device epic's 13:33Z mtime was MY OWN
    13:32Z-note commit, the mtime guard passed at 14:05Z proving no third-party wrote in the
    window, so the "additive repair" was a no-op re-commit plus the new notes - nothing was
    lost. Prior "board write-fault" incidents deserve the same suspicion: stale READS can make
    an agent "repair" a healthy file from an old base - the read path is the fault, and blind
    full-file repairs from stale bases CAUSE the drops they diagnose. LAW for this workflow:
    never use device_stage_files output as an edit base or diff base until its md5 matches a
    live device_bash md5sum of the same path; on mismatch, pull content through device_bash
    (base64/gzip) instead. Additive-repair discipline with mtime guards remains mandatory and
    is what contained the damage here. Also noted: nexus.py device md5 changed after my commit
    (b6bba0da... vs recorded b1bba550...) with the BUG-003 once-only fix INTACT - a legitimate
    concurrent edit by another lane (likely Story 03 logger work), not a revert.
  EVIDENCE:
  - src/melder/aether/aether.py (device md5 bc1d65e8 vs stale stage 77b0f439)
  - tickets/epics/2026-07-17_bugfix_aether_core_logging_epic.md (mtime-guard pass at 14:05Z)
  IMPACT: The 14:05Z note's fault attribution is corrected; the board row's revert claim is
    superseded by this note. All Story 02 edit bases below were md5-verified live-fresh before
    editing (aether.py via device_bash pull; the other two matched their stages).
  NEXT: Story 02 re-verification FACTs and implementation follow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T14:29:52Z
  TYPE: FACT
  CLAIM: Story 02 (BUG-146/147/148/149) re-verified - all four CONFIRMED against live-fresh
    source. BUG-146 (High): AetherUtilitySystem.__new__ publishes identity under
    _singleton_lock but __init__ checks `_initialized` and runs the whole body UNLOCKED
    (aether_utility_system.py:83-89) - two racing first constructors both enter, the delayed
    body resets `_channel_logger_resolver`/`_default_logger` and erases completed provider
    registrations (BUG-002's class, on the utility singleton). BUG-149 (High): Aether.cleanup
    sets `_cleaned = True` first, then cascades child cleanups, and resets
    `Aether._instance`/`_initialized` only AFTER every child succeeds; the except lane logs and
    re-raises WITHOUT reset (aether.py:192-234 live) - one child failure leaves the cleaned husk
    published, so every later Aether() returns it and dies on check_cleaned: process-wide brick.
    BUG-147 (Medium): SafeLogger.cleanup clears the sink but never sets `_cleaned`
    (safe_logger.py:68-84) - `.cleaned` stays False, check_cleaned never refuses. BUG-148
    (Medium): stdlib ERROR branch treats ANY truthy exc_info as `logger.exception(msg)`
    (safe_logger.py:270-276), discarding an explicitly supplied BaseException - outside an
    active handler the record carries (None, None, None).
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_aether_logging_helpers.md:7-88
  - src/melder/aether/aether_utility_system.py:64-89
  - src/melder/aether/aether.py:192-234
  - src/melder/utilities/logger/safe_logger.py:68-84
  - src/melder/utilities/logger/safe_logger.py:258-281
  IMPACT: Story 02 scope is pinned: two Highs (146/149) + two Mediums (147/148), no drift.
  NEXT: Implement all four (146: once-only init under _singleton_lock mirroring the
    BUG-002/003 shape; 149: finally-based singleton reset per the audit's expected remedy;
    147: idempotent cleanup + Cleanable latch; 148: forward BaseException instances on the
    stdlib error path, boolean True keeps active-context semantics) + symptom-named suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T14:29:52Z
  TYPE: DECISION
  CLAIM: Story 02 IMPLEMENTED - all four bugs fixed at root cause with regression suites.
    BUG-146: AetherUtilitySystem.__init__ is now double-checked once-only - lock-free
    `_initialized` fast path, re-check + full init body under `_singleton_lock`, latch flipped
    while the lock is held (exact BUG-002/003 shape; docstring Threading section added). No
    failure-reset lane needed: the body is non-fallible field initialization. BUG-149:
    Aether.cleanup's singleton reset (`_instance = None`, `_initialized = False`) moved to a
    `finally` on the child-cascade try - the child error is still logged and re-raised
    (fail-fast cascade semantics unchanged), but the cleaned husk is never republished and a
    later Aether() constructs a fresh root; docstring documents that a failed child keeps its
    own singleton/lifecycle state. BUG-147: SafeLogger.cleanup gains the idempotence guard and
    sets `_cleaned = True` terminally; emit surface stays a safe no-op via the null-logger
    path. BUG-148: stdlib ERROR branch now forwards `isinstance(exc_info, BaseException)` via
    `logger.error(msg, exc_info=exc_info)` (stdlib converts to the concrete tuple); boolean
    True keeps `logger.exception` active-context semantics; falsy stays plain error.
    VALIDATION: BUG-146 suite (gated Cleanable.__init__ choreography, per-entry release
    events reproducing the audit's delayed-second-constructor erasure) and BUG-147/148 suite
    (capture-handler stdlib records) EXECUTED in the sandbox harness (real modules + stub
    crystallizer, py3.10): 7/7 green on fixed code; red on old code with the exact audited
    symptoms ("init body ran 2 times", cleaned flag unset, record exc_info (None, None, None)).
    BUG-149 suite (Nexus-cleanup failure injection per the audit repro + healthy-lane guard)
    rides the owner's 3.14t run with the rest: full-repo pytest Not run - REOPEN on red.
    py_compile + AST shape checks green on all three sources.
  EVIDENCE:
  - src/melder/aether/aether_utility_system.py:70-106
  - src/melder/aether/aether.py:172-260
  - src/melder/utilities/logger/safe_logger.py:68-95
  - src/melder/utilities/logger/safe_logger.py:270-290
  - tests/unit/melder/aether/test_aether_utility_system_init_once_only_regression.py:1-210
  - tests/unit/melder/aether/test_aether_cleanup_failure_recovery_regression.py:1-120
  - tests/unit/melder/utilities/logger/test_safe_logger_lifecycle_and_exc_info_regression.py:1-180
  IMPACT: Stories 01 AND 02 are fully closed-pending-owner-run (10 of 12 epic bugs:
    BUG-002/003/004/005/006/007/146/147/148/149). Remaining: Story 03 (BUG-278/279, logger
    ownership/refresh) - NOTE nexus.py has drifted post-commit (md5 b6bba0da), suggesting
    another lane may already be working the Nexus logger surface; re-verify against live
    source and check the board before claiming.
  NEXT: Owner runs all suites on 3.14t; helper_f proceeds to Story 03 re-verification on
    user direction, coordinating via the board if another agent holds the logger lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T16:19:47Z
  TYPE: FACT
  CLAIM: Story 03 (BUG-278/279) re-verified - both CONFIRMED against live source (aether.py
    pulled fresh post-Story-02; nexus.py read live via device_bash after its concurrent-lane
    edit - the BUG-003 once-only fix is intact there and the logger drift is unrelated to the
    defect). BUG-278 (Medium, two lanes): `attach_logger` (aether.py:490) replaces `_logger`
    without retiring the displaced wrapper - attach cleanup-capable A then B orphans A
    forever (final cleanup only reaches the current slot); `enable_logging` automatic lane
    (aether.py:555-565) PUBLISHES the resolved wrapper before validating it, so a
    None-resolving provider raises with `_logger` already swapped to a null wrapper - the
    working logger is both destroyed and orphaned. BUG-279 (Medium): Nexus
    `_initialize_logging` (nexus.py:368) compares WRAPPER identity, but every refresh builds
    a distinct wrapper, so refreshing with the SAME raw sink cleans the prior wrapper and
    thereby terminally cleans the sink the replacement still owns (worse post-BUG-147: the
    sink's cleaned latch now also refuses reuse). No mailbox/board claim on this lane; clear
    to proceed.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_logger_ownership_refresh_appendix.md:1-100
  - src/melder/aether/aether.py:462-565
  - src/melder/nexus/nexus.py:333-390
  IMPACT: Final Story 03 scope pinned; the shared root cause is identity-vs-ownership
    confusion at the wrapper layer.
  NEXT: Fix both at the sink-identity level + validate-before-publish; symptom-named suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T16:19:47Z
  TYPE: DECISION
  CLAIM: Story 03 IMPLEMENTED - EPIC CODE-COMPLETE at 12 of 12 bugs fixed-with-regression-
    suite, all pending the owner's 3.14t validation run. BUG-278: `attach_logger` now
    resolves the next wrapper, retires the displaced wrapper best-effort ONLY when the
    underlying raw sinks differ (sink-identity aliasing law, mirroring BUG-279 - same-sink
    re-attachment is ownership-neutral), then publishes; `enable_logging`'s automatic lane
    validates the resolved wrapper BEFORE publication so a None resolution raises with the
    working logger untouched, and a successful automatic attach retires the displaced
    wrapper under the same sink-identity guard; both docstrings carry the new Contract
    lines. BUG-279: Nexus `_initialize_logging` gained the explicit same-sink fast lane
    (previous wrapper already owns the exact raw sink -> reuse, return) and the displaced-
    wrapper teardown now requires BOTH wrapper differ AND sink differ; the silent-fallback
    error lane is intentionally unchanged (audit excludes it). nexus.py was patched IN PLACE
    on device via md5-gated exact-block replace (base b6bba0da -> 0feb01a4) with device-side
    py_compile green - avoiding the stale-stage round trip entirely; aether.py went through
    the verified-base commit flow (0ebb08b0 -> a9979299, mtime-guarded, md5-verified,
    device-side py_compile green). Regression suites: BUG-278 (5 tests: displaced-sink
    retirement with final-teardown ledger, same-sink neutrality, detach-to-null retirement,
    failed-automatic preservation of the working logger, successful-automatic retirement)
    and BUG-279 (3 tests: audited same-sink refresh with post-refresh log-call proof,
    repeated-refresh neutrality, different-sink retirement) - both use a CleanupTrackingLogger
    stdlib subclass so SafeLogger's isinstance gate passes without protocol fakes.
    VALIDATION: py_compile green on all files (sandbox + device); full-path traces walked
    every lane old-vs-new (old code fails each symptom assert: orphaned sink counter 0->1
    expected, aether.logger None after failed enable, sink cleaned on same-sink refresh);
    pytest Not run - real Aether/Nexus boot requires 3.14t, rides the owner's run, REOPEN
    on red.
  EVIDENCE:
  - src/melder/aether/aether.py:462-608
  - src/melder/nexus/nexus.py:333-425
  - tests/unit/melder/aether/test_aether_logger_replacement_ownership_regression.py:1-230
  - tests/unit/melder/aether/test_nexus_same_sink_refresh_ownership_regression.py:1-135
  IMPACT: All three stories complete: BUG-002/003/004/005/006/007 (Story 01),
    BUG-146/147/148/149 (Story 02), BUG-278/279 (Story 03), plus the owner-run fallout task
    (conduit_ward test-double drift, 10 items). Epic exit now rests on the owner's 3.14t
    green run and closure walkthrough.
  NEXT: Owner runs the full suite set on 3.14t; on green, owner confirms Closure
    Confirmation checklist; on any red, REOPEN the matching story with the failure output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order (Critical->High->Medium->Low).
- Reference story/task evidence (and the audit report line ranges) instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
Remediation epic for the 12 aether core logging bugs from the 2026-07-17 audit, owned by helper_f.
Status ready. Start with the Critical findings (BUG-002; BUG-003),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
