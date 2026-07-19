# Epic: Package bootstrap & Python-compat bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-package-python-compat
- Status: in_progress
- Owner: cowork
- Agent Name: helper_0
- Priority: p0
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T09:20:17Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
5 bugs in this subsystem (1 Critical, 3 Medium, 1 Low). Package import/bootstrap on advertised Python versions and the standalone Package/Pack helper. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- BUG-001 - `import melder` crashes on Python 3.13 (an advertised version): TYPE_CHECKING-only imports used in eager annotations without deferred-annotation handling. Showstopper on 3.13.

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_python313_compatibility.md
  - codex/2026-07-17_melder_bug_audit_package_helper_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_0; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 5 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
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
- In scope: pyproject.toml; src/melder/crystallizer/asset_management/asset_management_system.py; src/melder/**/package/**
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
- [ ] Story: STORY-package_python_compat-01 - BUG-001 (python313_compatibility): CRITICAL: package import fails on 3.13 from TYPE_CHECKING-only names used in eager annotations. DECISION REQUIRED on the fix path (see Decision Log).
- [ ] Story: STORY-package_python_compat-02 - BUG-266-269 (package_helper_appendix): Standalone Package/Pack helper defects (no non-test callers found - isolated).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-package_python_compat-01 (BUG-001)
- [ ] Task: Complete story STORY-package_python_compat-02 (BUG-266-269)
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
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: DECISION_REQUEST
  CLAIM: BUG-001 fix path is a real fork with product implications. Option A: set `requires-python = ">=3.14"` (matches the free-threaded target; smallest change). Option B: keep `>=3.13` and restructure the TYPE_CHECKING imports so annotations do not eval eagerly. NOTE: `from __future__ import annotations` is BANNED by the synaptic_python_developer profile, so it is NOT an option here. Owner decision required before implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a until an artifact (e.g., a fix design note) is produced.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - Package import/bootstrap on advertised Python versions and the standalone Package/Pack helper.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 5 audited bugs (1 Critical, 3 Medium, 1 Low) are grouped into this subsystem epic for helper_0; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_0 a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_0 starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T09:20:17Z
  TYPE: DECISION
  CLAIM: Claimed by helper_0 (attention_board in_progress). First story STORY-2026-07-17-bug001-package-import-python313 created for BUG-001; it is BLOCKED on an owner product decision (declare 3.14+ vs make code run on 3.13). BUG-001 root cause confirmed vs current source; no source changed.
  EVIDENCE:
  - tickets/stories/2026-07-17_bug001_package_import_python313_story.md:1-45
  IMPACT: The critical import bug is gated on the owner's Python-support call; BUG-266-269 remain unblocked.
  NEXT: Owner picks Option A or B on BUG-001.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T12:50:51Z
  TYPE: DECISION
  CLAIM: BUG-001 fix APPLIED via Option A (owner choice 2026-07-18): pyproject.toml requires-python/classifier/description to 3.14. No source code changed. Story STORY-2026-07-17-bug001-package-import-python313 to review, pending a user suite run on 3.14t.
  EVIDENCE:
  - pyproject.toml:8-10
  IMPACT: The epic's sole Critical (BUG-001) is remediated pending validation; BUG-266-269 remain open.
  NEXT: User validates import on 3.14t; then start BUG-266-269.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T13:31:38Z
  TYPE: FACT
  CLAIM: BUG-266..269 (package helper) FIXED at root cause in package.py and verified by a before/after repro (original reproduces all four; fixed resolves all four). Regression test added at tests/unit/melder/utilities/helpers/test_package_helper_bug266_269_regression.py. Story STORY-2026-07-17-bug266-269-package-helper -> review. With BUG-001 (Option A) also applied, all 5 package_python_compat bugs are remediated pending the user's 3.14t suite run.
  EVIDENCE:
  - src/melder/utilities/helpers/package.py:446-495
  - codex/2026-07-17_melder_bug_audit_package_helper_appendix.md:10-107
  IMPACT: This epic is functionally complete pending validation; ready to move toward closure after the suite run.
  NEXT: User runs the package suite on 3.14t; then close the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order (Critical->High->Medium->Low).
- Reference story/task evidence (and the audit report line ranges) instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
Remediation epic for the 5 package python compat bugs from the 2026-07-17 audit, owned by helper_0.
Status ready. Start with the Critical findings (BUG-001),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
