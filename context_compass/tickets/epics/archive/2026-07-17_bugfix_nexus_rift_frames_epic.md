# Epic: Nexus / Rift / frames / ACL / commands bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-nexus-rift-frames
- Status: ready
- Owner: cowork
- Agent Name: helper_1
- Priority: p1
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T08:57:34Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
57 bugs in this subsystem (0 Critical, 23 High, 30 Medium, 4 Low). Nexus + managed frames + projections, Rift lifecycle & room state, FrameViewer helpers, Frame ACL builders/validators, capability command surface, frame profile validation. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- None in this subsystem (highest severity is High).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_nexus_spellbook_devops_wave.md
  - codex/2026-07-17_melder_bug_audit_nexus_spellbook_appendix.md
  - codex/2026-07-17_melder_bug_audit_rift_viewer_event_memory.md
  - codex/2026-07-17_melder_bug_audit_nexus_projection_chain_appendix.md
  - codex/2026-07-17_melder_bug_audit_nexus_projection_chain_appendix_2.md
  - codex/2026-07-17_melder_bug_audit_rift_room_state_appendix.md
  - codex/2026-07-17_melder_bug_audit_nexus_rift_lifecycle_appendix.md
  - codex/2026-07-17_melder_bug_audit_frame_cloud_cluster_appendix.md
  - codex/2026-07-17_melder_bug_audit_frame_acl_builder_appendix.md
  - codex/2026-07-17_melder_bug_audit_frame_viewer_helpers_appendix.md
  - codex/2026-07-17_melder_bug_audit_command_surface_memory_appendix.md
  - codex/2026-07-17_melder_bug_audit_frame_profile_version_validation_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_1; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 57 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
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
- In scope: src/melder/nexus/**
- Out of scope: unrelated modules, public API redesign, performance passes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Bug membership, severities, and evidence are FACT-sourced from the audit manifests; the epic is routable and ready for its owning agent to begin (Critical/High first).

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
- [ ] Story: STORY-nexus_rift_frames-01 - BUG-050-054 (nexus_spellbook_devops_wave): Concurrent frame creation bypasses the Nexus frame cap; duplicate scan aliases split-brain Spellbook maps; audit-failure claim leaks; bind abort commits.
- [ ] Story: STORY-nexus_rift_frames-02 - BUG-055-059 (nexus_spellbook_appendix): Concurrent frame links bypass target budget; failed foreign bind_inactive leaves unreachable state; foreign-index notch corrupts two Spellbooks; ACL bundle over-refresh.
- [ ] Story: STORY-nexus_rift_frames-03 - BUG-102-106 (rift_viewer_event_memory): FrameViewer assembles a heterogeneous view; viewer event/memory retention.
- [ ] Story: STORY-nexus_rift_frames-04 - BUG-107-109 (nexus_projection_chain_appendix): Public frame config install mutates default projection state.
- [ ] Story: STORY-nexus_rift_frames-05 - BUG-120-121 (nexus_projection_chain_appendix_2): Projection chain residuals.
- [ ] Story: STORY-nexus_rift_frames-06 - BUG-123-130 (rift_room_state_appendix): Concurrent independent room actions suppress each other; room-state lifecycle.
- [ ] Story: STORY-nexus_rift_frames-07 - BUG-165-169 (nexus_rift_lifecycle_appendix): Failed Rift registration destroys caller-owned state; concurrent last-Rift removal partially commits.
- [ ] Story: STORY-nexus_rift_frames-08 - BUG-194-200 (frame_cloud_cluster_appendix): Cluster delete leaves scoped grants; cleaned clustered root leaves impossible state; concurrent joins bypass one-cluster exclusivity; cloud/Aether snapshot desync.
- [ ] Story: STORY-nexus_rift_frames-09 - BUG-221-229 (frame_acl_builder_appendix): Stale fluent builders control later drafts; callback failure commits a revision; nested rule-condition aliasing; container/draft lock order; finalized-config mutability.
- [ ] Story: STORY-nexus_rift_frames-10 - BUG-246-250 (frame_viewer_helpers_appendix): Projection refresh leaves returned frame helpers stale; retained-helper lifetimes; static inventories.
- [ ] Story: STORY-nexus_rift_frames-11 - BUG-254-255 (command_surface_memory_appendix): Codegen command discovery and frame-independent room memory.
- [ ] Story: STORY-nexus_rift_frames-12 - BUG-262 (frame_profile_version_validation_appendix): Named-version production-path contradiction in frame profile validation.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-nexus_rift_frames-01 (BUG-050-054)
- [ ] Task: Complete story STORY-nexus_rift_frames-02 (BUG-055-059)
- [ ] Task: Complete story STORY-nexus_rift_frames-03 (BUG-102-106)
- [ ] Task: Complete story STORY-nexus_rift_frames-04 (BUG-107-109)
- [ ] Task: Complete story STORY-nexus_rift_frames-05 (BUG-120-121)
- [ ] Task: Complete story STORY-nexus_rift_frames-06 (BUG-123-130)
- [ ] Task: Complete story STORY-nexus_rift_frames-07 (BUG-165-169)
- [ ] Task: Complete story STORY-nexus_rift_frames-08 (BUG-194-200)
- [ ] Task: Complete story STORY-nexus_rift_frames-09 (BUG-221-229)
- [ ] Task: Complete story STORY-nexus_rift_frames-10 (BUG-246-250)
- [ ] Task: Complete story STORY-nexus_rift_frames-11 (BUG-254-255)
- [ ] Task: Complete story STORY-nexus_rift_frames-12 (BUG-262)
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
  - Nexus + managed frames + projections, Rift lifecycle & room state, FrameViewer helpers, Frame ACL builders/validators, capability command surface, frame profile validation.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 57 audited bugs (0 Critical, 23 High, 30 Medium, 4 Low) are grouped into this subsystem epic for helper_1; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_1 a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_1 starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T09:27:30Z
  TYPE: FACT
  CLAIM: helper_1 claimed this epic and re-verified the Story-01/02 tranche against CURRENT
    source (audit was a read-only 2026-07-17 snapshot). Four findings still reproduce:
    BUG-051 (High) frame-cap race - `_validate_frame_budget` counts `_frames_by_name` + this
    call's names but ignores other threads' `_creating_frame_names` reservations, and the
    publish step revalidates only name-collision, never budget; two concurrent creates both
    pass a cap of 1. BUG-055 (High) target-frame-link race - the Rift attach path does
    validate -> create-contract -> increment as three unserialized ops on Nexus
    `_target_frame_ref_counts` with NO Nexus lock (unlike `add_rift`, which holds `self._lock`
    across validate+register). BUG-059 (High) `install_configuration` fires
    `_notify_acl_changed` 4x (once inside each of the 3 `insert_head_*` + one final), publishing
    mixed old/new family revisions and running 4 drain/recompile cycles for one bundle.
    BUG-050 (Medium) `_validate_active_rift_budget` gates on `len(_rifts_by_id)`, never
    `rift.is_active`, so inactive Rifts consume the active cap.
  EVIDENCE:
  - src/melder/nexus/nexus_frame_manager.py:272-303
  - src/melder/nexus/nexus_frame_manager.py:869-903
  - src/melder/nexus/rift/rift.py:430-445
  - src/melder/nexus/nexus.py:2631-2667
  - src/melder/nexus/nexus.py:2829-2838
  - src/melder/nexus/nexus.py:2669-2690
  - src/melder/nexus/acl/frame_acl_container.py:452-467
  - src/melder/nexus/acl/frame_acl_container.py:542-621
  IMPACT: Two process-wide budget invariants (frame cap, target-frame cap) are unenforceable
    under 3.14t real threading, plus a torn multi-notify ACL publish. Proposed fixes are
    root-cause, not defensive guards: count in-flight reservations inside the existing
    `_lock` (051); atomic check-and-increment under the Nexus lock (055); single-notify
    bundle install via no-notify insert cores (059); count/enforce active Rifts, incl. the
    activation transition (050).
  UNKNOWN / DECISION_REQUEST: BUG-052/053/054/056/058 (also Story 01/02) carry evidence in
    src/melder/aether/spellbook/** and .../dev_ops/** - OUTSIDE this epic's declared
    src/melder/nexus/** scope, and may overlap helper_f's conduit_binding_meld epic and
    helper_1's devops_transactions epic. Per FAILURE_ESCALATION they need a DECISION_REQUEST +
    owner confirm before any cross-subsystem fix.
  NEXT: Owner picks the first fix tranche (recommend BUG-051 + BUG-050 first - both fully
    self-contained in nexus_frame_manager.py / nexus.py), then implement + regression tests.
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
Remediation epic for the 57 nexus rift frames bugs from the 2026-07-17 audit, owned by helper_1.
Status ready. Start with the Critical findings (none - begin with Highs),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
