# Epic: Utilities / sync / config / ownership / teardown bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-utilities-sync-ownership
- Status: ready
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T20:50:00Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
47 bugs in this subsystem (0 Critical, 27 High, 18 Medium, 2 Low). Utility collections/weak-refs/schedulers/guards, synchronization primitives & creation gates, configuration & builders, ownership transfer, LoadGate/loader admission, cross-subsystem partial-activation teardown. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- None in this subsystem (highest severity is High).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_utilities_appendix.md
  - codex/2026-07-17_melder_bug_audit_utilities_appendix_2.md
  - codex/2026-07-17_melder_bug_audit_configuration_builders.md
  - codex/2026-07-17_melder_bug_audit_configuration_builders_appendix.md
  - codex/2026-07-17_melder_bug_audit_ownership_transfer_appendix.md
  - codex/2026-07-17_melder_bug_audit_loadgate_loader_admission_appendix.md
  - codex/2026-07-17_melder_bug_audit_partial_activation_teardown_appendix.md
  - codex/2026-07-17_melder_bug_audit_synchronization_residual_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_f; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 47 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
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
- In scope: src/melder/utilities/**; src/melder/**/configuration/**; src/melder/**/load*/**
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
- [ ] Story: STORY-utilities_sync_ownership-01 - BUG-074-077 (utilities_appendix): AbstractElasticPool resurrects an object after cleanup; utility collection lifecycle.
- [ ] Story: STORY-utilities_sync_ownership-02 - BUG-078 + BUG-093 ONLY (utilities_appendix_2). STRIPPED per owner-directed source-verified triage 2026-07-18: BUG-090 (hash fallback DOCUMENTED in __hash__ docstring; sole caller never keys by wrapper), BUG-091 (residual-wave documented; daemon-bounded), BUG-092 (reusable mode has ZERO one_time_use=False callers in src - dead code) - see codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md FINAL VERDICTS.
- [ ] Story: STORY-utilities_sync_ownership-03 - BUG-079-084 (configuration_builders): Required Nexus tokens bypassable; first frame-posture bind drops cache config; reconfiguring an active Aether leaves stale config.
- [ ] Story: STORY-utilities_sync_ownership-04 - BUG-094-101 (configuration_builders_appendix): Failed Crystallizer bootstrap abandons configuration; finalized ACL configs mutable; persistent crystal twins mutable; failed Nexus.enable corrupts active state.
- [ ] Story: STORY-utilities_sync_ownership-05 - BUG-180-187 (ownership_transfer_appendix): Rejected target collision deletes the target; transfers leave stale `_spell` refs; recording-hook failure escapes after commit; include_dependencies neither fail-fast nor atomic; cluster maps retain former owner.
- [ ] Story: STORY-utilities_sync_ownership-06 - BUG-230-236 (loadgate_loader_admission_appendix): Concurrent cleanup/acquisition leave a cleaned LoadGate acquired; failed restore leaves unconfigured Aether; rollback leaves Aether pointing at a cleaned root; cluster-stage failure leaves replayed cluster.
- [ ] Story: STORY-utilities_sync_ownership-07 - BUG-237-242 (partial_activation_teardown_appendix): Successful Aether rebootstrap leaves Spellbook bound elsewhere; failed boot poisons retry with an orphan host; Nexus publication failure leaves conjure committed.
- [ ] Story: STORY-utilities_sync_ownership-08 - BUG-263-265 (synchronization_residual_appendix): CreationGateController cleanup races registration; UnitOfWork permits cancellation after the callable has committed; synchronization residuals.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-utilities_sync_ownership-01 (BUG-074-077)
- [ ] Task: Complete story STORY-utilities_sync_ownership-02 (BUG-078, BUG-090-093)
- [ ] Task: Complete story STORY-utilities_sync_ownership-03 (BUG-079-084)
- [ ] Task: Complete story STORY-utilities_sync_ownership-04 (BUG-094-101)
- [ ] Task: Complete story STORY-utilities_sync_ownership-05 (BUG-180-187)
- [ ] Task: Complete story STORY-utilities_sync_ownership-06 (BUG-230-236)
- [ ] Task: Complete story STORY-utilities_sync_ownership-07 (BUG-237-242)
- [ ] Task: Complete story STORY-utilities_sync_ownership-08 (BUG-263-265)
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
  - Utility collections/weak-refs/schedulers/guards, synchronization primitives & creation gates, configuration & builders, ownership transfer, LoadGate/loader admission, cross-subsystem partial-activation teardown.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 47 audited bugs (0 Critical, 27 High, 18 Medium, 2 Low) are grouped into this subsystem epic for helper_f; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_f a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_f starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T20:05:00Z
  TYPE: FACT
  CLAIM: Pre-work triage of all 47 bugs complete (owner-directed full-context read; see
    codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md for per-bug
    verdicts). 43 KEEP - dominated by five design families (pool-lifecycle root BUG-076
    before 008/009; snapshot/deep-detach 083/096/098/179; validate-before-publish
    081/099/240/241; the transfer-rollback campaign 180-187 as ONE transaction rework;
    teardown-vs-in-flight 263/264/265). CONTESTED by the audit's own residual wave and
    frozen pending owner ruling: 090/091/092/230 (+156/157 in the sibling epic).
    RECLASSIFY-PROPOSED: 090 (no caller keys tables by wrapper - verify then exclude),
    092 (reusable SafeGuard mode has zero internal callers - exclude or delete the mode).
    COORDINATION: 096/231-235/238/241 touch crystallizer files owned by helper_0's lane -
    DECISION note + coordination before any edit. BUG-237 flagged high-value: test
    fixtures actively MASK the Spellbook._aether staleness (manual cache patching).
  EVIDENCE:
  - codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md:1-999
  IMPACT: The epic starts with an evidence-ranked queue instead of manifest order; the
    contested four cannot burn effort before the owner rules.
  NEXT: Owner reviews triage; claim follows once the conduit epic's KEEP stories land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T20:50:00Z
  TYPE: DECISION
  CLAIM: SOURCE-VERIFIED STRIP executed on owner directive. THIS EPIC: BUG-090/091/092
    STRIPPED from Story 02 (090: documented hash-fallback + zero key-usage reach; 092:
    dead reusable mode, zero callers; 091: residual-wave documented, daemon-bounded).
    BUG-230 CONFIRMED REAL against current load_gate.py (cleaned-yet-held window between
    the pre-condition cleaned check and the holder write; fix = re-check under the
    condition, the file's own wait_for_passage tombstone pattern). BUG-076 CONFIRMED and
    aggravated: acquire/release carry NO terminal handling at all - post-cleanup use
    silently resurrects instead of failing loud, violating the loud-by-contract posture;
    it is the family root for conduit-epic BUG-008/009. Remaining epic scope: 44 bugs
    across 8 stories. Crystallizer-file coordination flags unchanged (096/231-235/238/241
    -> helper_0).
  EVIDENCE:
  - codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md
  - src/melder/utilities/synchronization/sync_weak_ref.py
  - src/melder/utilities/general_base/abstract_elastic_pool.py:204-258
  IMPACT: 47 -> 44 real bugs, zero contested; queue is evidence-ranked.
  NEXT: Claim follows the conduit epic's KEEP work; 076 family root is the opener here.
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
Remediation epic for the 47 utilities sync ownership bugs from the 2026-07-17 audit, owned by helper_f.
Status ready. Start with the Critical findings (none - begin with Highs),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
