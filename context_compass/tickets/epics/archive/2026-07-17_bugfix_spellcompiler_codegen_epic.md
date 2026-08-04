# Epic: SpellCompiler & codegen bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-spellcompiler-codegen
- Status: ready
- Owner: cowork
- Agent Name: helper_0
- Priority: p1
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T08:57:34Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
45 bugs in this subsystem (0 Critical, 17 High, 22 Medium, 6 Low). SpellCompiler runtime/front-end, validation & topology, artifact pipeline, introspection, codegen-creation (generalized/many-only/solo), shared executions, Spellbook creation system. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- None in this subsystem (highest severity is High).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_compiler_runtime_appendix.md
  - codex/2026-07-17_melder_bug_audit_validation_topology_lifetimes_wave.md
  - codex/2026-07-17_melder_bug_audit_validation_topology_appendix.md
  - codex/2026-07-17_melder_bug_audit_introspection_protocol_appendix.md
  - codex/2026-07-17_melder_bug_audit_compiler_artifact_pipeline_appendix.md
  - codex/2026-07-17_melder_bug_audit_validation_strategy_appendix.md
  - codex/2026-07-17_melder_bug_audit_compiler_frontend_appendix.md
  - codex/2026-07-17_melder_bug_audit_codegen_creation_values_appendix.md
  - codex/2026-07-17_melder_bug_audit_shared_compiler_failfast_appendix.md
  - codex/2026-07-17_melder_bug_audit_spellbook_creation_system_appendix.md
  - codex/2026-07-17_melder_bug_audit_codegen_retired_context_overwrite_appendix.md
  - codex/2026-07-17_melder_bug_audit_compiler_clear_phase5_context_appendix.md
  - codex/2026-07-17_melder_bug_audit_solo_codegen_manifest_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_0; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 45 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
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
- In scope: src/melder/aether/spellbook/spell_compiler/**; src/melder/aether/spellbook/spellbook_creation_system.py
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
- [ ] Story: STORY-spellcompiler_codegen-01 - BUG-021-025 (compiler_runtime_appendix): Fingerprints include process memory addresses; dynamic Conduit cleanup corrupts an in-flight admitted compile.
- [ ] Story: STORY-spellcompiler_codegen-02 - BUG-063-066 (validation_topology_lifetimes_wave): Owner cluster leave contracts shared spells; lesser-to-normal upgrade leaks pooled melds.
- [ ] Story: STORY-spellcompiler_codegen-03 - BUG-067-070 (validation_topology_appendix): Frame aggregation iterates a live Spellbook set under mutation; dirty-root revalidation erases unrelated valid plans.
- [ ] Story: STORY-spellcompiler_codegen-04 - BUG-114-119 (introspection_protocol_appendix): Removing one generated protocol can delete unrelated protocols; introspection/protocol lifecycle.
- [ ] Story: STORY-spellcompiler_codegen-05 - BUG-170-174 (compiler_artifact_pipeline_appendix): Individual artifact cleanup destroys Phase-5 assets; artifact map/IR staleness.
- [ ] Story: STORY-spellcompiler_codegen-06 - BUG-188-193 (validation_strategy_appendix): Mixed normal + SpellContract dependency cycles escape detection; validation strategy gaps.
- [ ] Story: STORY-spellcompiler_codegen-07 - BUG-201-205 (compiler_frontend_appendix): SpellMap override payload silently discarded; implicit-annotation DI admits invalid callable providers; requirements/front-end handoffs.
- [ ] Story: STORY-spellcompiler_codegen-08 - BUG-251-252 (codegen_creation_values_appendix): Codegen silently replaces arbitrary contract payloads (object->repr) and drops override emission.
- [ ] Story: STORY-spellcompiler_codegen-09 - BUG-253 (shared_compiler_failfast_appendix): Failed fused plan runs clean their compiler while the facade still reports success (UnitOfWork).
- [ ] Story: STORY-spellcompiler_codegen-10 - BUG-243-245 (spellbook_creation_system_appendix): Upgrade ownership discard, rejected-conjure rollback, ChangeControl teardown in the 3,228-line creation system.
- [ ] Story: STORY-spellcompiler_codegen-11 - BUG-276 (codegen_retired_context_overwrite_appendix): A retired cold door can overwrite a replacement CreationContext.
- [ ] Story: STORY-spellcompiler_codegen-12 - BUG-277 (compiler_clear_phase5_context_appendix): Clearing Phase-5 artifacts leaves the live CreationContext + warm door valid (stale meld executes).
- [ ] Story: STORY-spellcompiler_codegen-13 - BUG-280-281 (solo_codegen_manifest_appendix): Solo manifest hydration drops every static contract payload; Solo validator accepts impossible manifests.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-spellcompiler_codegen-01 (BUG-021-025)
- [ ] Task: Complete story STORY-spellcompiler_codegen-02 (BUG-063-066)
- [ ] Task: Complete story STORY-spellcompiler_codegen-03 (BUG-067-070)
- [ ] Task: Complete story STORY-spellcompiler_codegen-04 (BUG-114-119)
- [ ] Task: Complete story STORY-spellcompiler_codegen-05 (BUG-170-174)
- [ ] Task: Complete story STORY-spellcompiler_codegen-06 (BUG-188-193)
- [ ] Task: Complete story STORY-spellcompiler_codegen-07 (BUG-201-205)
- [ ] Task: Complete story STORY-spellcompiler_codegen-08 (BUG-251-252)
- [ ] Task: Complete story STORY-spellcompiler_codegen-09 (BUG-253)
- [ ] Task: Complete story STORY-spellcompiler_codegen-10 (BUG-243-245)
- [ ] Task: Complete story STORY-spellcompiler_codegen-11 (BUG-276)
- [ ] Task: Complete story STORY-spellcompiler_codegen-12 (BUG-277)
- [ ] Task: Complete story STORY-spellcompiler_codegen-13 (BUG-280-281)
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
  - SpellCompiler runtime/front-end, validation & topology, artifact pipeline, introspection, codegen-creation (generalized/many-only/solo), shared executions, Spellbook creation system.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 45 audited bugs (0 Critical, 17 High, 22 Medium, 6 Low) are grouped into this subsystem epic for helper_0; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_0 a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_0 starts the highest-severity story and re-verifies each finding against current source before fixing.
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
Remediation epic for the 45 spellcompiler codegen bugs from the 2026-07-17 audit, owned by helper_0.
Status ready. Start with the Critical findings (none - begin with Highs),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
