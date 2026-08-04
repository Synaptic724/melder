# Epic: Crystallizer & persistence bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: in_progress
- Owner: cowork
- Agent Name: helper_0
- Priority: p0
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T16:16:39Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
47 bugs in this subsystem (1 Critical, 32 High, 13 Medium, 1 Low). Crystallizer capture/restore, persistence chain, profile cache, external mesh, graft, and configuration. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- BUG-159 - Retention deletes unchanged live state but reports the checkpoint id as stored (data loss).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_crystallizer_persistence.md
  - codex/2026-07-17_melder_bug_audit_persistence_chain_appendix.md
  - codex/2026-07-17_melder_bug_audit_crystallizer_appendix.md
  - codex/2026-07-17_melder_bug_audit_crystal_analysis_import_appendix.md
  - codex/2026-07-17_melder_bug_audit_crystallizer_graft_impact_appendix.md
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md
  - codex/2026-07-17_melder_bug_audit_crystal_carrier_analysis_appendix.md
  - codex/2026-07-17_melder_bug_audit_external_mesh_appendix.md
  - codex/2026-07-17_melder_bug_audit_persistence_restore_identity_appendix.md
  - codex/2026-07-17_melder_bug_audit_graft_user_world_appendix.md
  - codex/2026-07-17_melder_bug_audit_crystallizer_configuration_residual_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_0; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
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
- In scope: src/melder/crystallizer/**; src/melder/**/persistence/**; external persistence manager / SQLite adapter
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
- [ ] Story: STORY-crystallizer_persistence-01 - BUG-013-020 (crystallizer_persistence): Sealed-payload mutability, synthetic-exec leaks, all-or-nothing restore rollback, import/bootstrap history, same-ms checkpoint races.
- [ ] Story: STORY-crystallizer_persistence-02 - BUG-026-027 (persistence_chain_appendix): Imported history does not rebase the live journal; profile clear/delete has no ledger-generation reset.
- [ ] Story: STORY-crystallizer_persistence-03 - BUG-028-030 (crystallizer_appendix): External formation storage cannot isolate profiles; synthetic restore ignores recorded module deps.
- [ ] Story: STORY-crystallizer_persistence-04 - BUG-085-089 (crystal_analysis_import_appendix): Unexecuted packages lose relative-import deps; corrupt cached checkpoint treated as valid; identity rewrite on synthetic code.
- [ ] Story: STORY-crystallizer_persistence-05 - BUG-139-145 (crystallizer_graft_impact_appendix): Source-drift dedup hides conflicting sealed sources; preflight admits invalid source records; drifted graft anchor loses parked members.
- [ ] Story: STORY-crystallizer_persistence-06 - BUG-158-164 (persistence_profile_cache_appendix): CRITICAL BUG-159 retention data loss; targeted checkpoint policy-twin emission; failed remote graft reports success; chain verification certifies reordered journals.
- [ ] Story: STORY-crystallizer_persistence-07 - BUG-206-207 (crystal_carrier_analysis_appendix): Retained user-source custody can seal two source versions; carrier/analysis snapshot coherence.
- [ ] Story: STORY-crystallizer_persistence-08 - BUG-215-220 (external_mesh_appendix): Emission tap misses record lanes; strict uploads block the non-blocking path; record/tap not linearized; concurrent formation writes lost.
- [ ] Story: STORY-crystallizer_persistence-09 - BUG-256-257 (persistence_restore_identity_appendix): Restore discards contract dependency provenance; relationship identity translation.
- [ ] Story: STORY-crystallizer_persistence-10 - BUG-258-260 (graft_user_world_appendix): Later source failure suppresses a valid graft/restore; merge adoption reuses a rejected member; per-member graft reporting.
- [ ] Story: STORY-crystallizer_persistence-11 - BUG-274-275 (crystallizer_configuration_residual_appendix): Frozen configuration schema remains mutable; rejected configuration replacement poisons retry.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-crystallizer_persistence-01 (BUG-013-020)
- [ ] Task: Complete story STORY-crystallizer_persistence-02 (BUG-026-027)
- [ ] Task: Complete story STORY-crystallizer_persistence-03 (BUG-028-030)
- [ ] Task: Complete story STORY-crystallizer_persistence-04 (BUG-085-089)
- [ ] Task: Complete story STORY-crystallizer_persistence-05 (BUG-139-145)
- [ ] Task: Complete story STORY-crystallizer_persistence-06 (BUG-158-164)
- [ ] Task: Complete story STORY-crystallizer_persistence-07 (BUG-206-207)
- [ ] Task: Complete story STORY-crystallizer_persistence-08 (BUG-215-220)
- [ ] Task: Complete story STORY-crystallizer_persistence-09 (BUG-256-257)
- [ ] Task: Complete story STORY-crystallizer_persistence-10 (BUG-258-260)
- [ ] Task: Complete story STORY-crystallizer_persistence-11 (BUG-274-275)
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
  - Crystallizer capture/restore, persistence chain, profile cache, external mesh, graft, and configuration.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 47 audited bugs (1 Critical, 32 High, 13 Medium, 1 Low) are grouped into this subsystem epic for helper_0; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_0 a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_0 starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T13:55:19Z
  TYPE: FACT
  CLAIM: Epic claimed by helper_0 (ready -> in_progress). CRITICAL BUG-159 FIXED at root cause: verify_checkpoint_chain now fails closed with an explicit `restorable` flag (True only for a fully intact baseline chain); a retention-truncated survivor is restorable=False, so the integrity gate no longer certifies a chain that would restore a world missing the evicted state. Owner-directed fail-closed classification (audit option 3) over compaction/baseline-pinning. Story STORY-2026-07-17-bug159-checkpoint-retention-restorability -> review. Verified via a 7-scenario logic simulation in-container; pytest Not run (melder root chain needs 3.14t). RESIDUAL (flagged): retention still evicts and the restore engine is not re-wired to the gate; loss-prevention (compaction) is a recommended owner follow-up. The rest of story 06 (BUG-158,160-164) and the remaining crystallizer_persistence stories are still open.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:1120-1266
  - tests/unit/melder/crystallizer/persistence/test_checkpoint_chain_integrity.py
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:30-48
  IMPACT: Removes the silent data-loss-on-restore certification; the sole Critical is remediated pending the user's 3.14t suite run.
  NEXT: User runs the persistence suite on 3.14t; then continue story 06 Highs (BUG-162, BUG-164) and the rest of the lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T14:01:22Z
  TYPE: FACT
  CLAIM: HIGH BUG-164 (chain verification certified reordered journals as intact) FIXED at root cause in the crystal codec: PersistenceCrystal.__init__ now rejects non-monotonic, duplicate, or out-of-range journal sequences (ValueError), so a reordered/duplicated import can never enter the ledger or replay the wrong chronology; empty-window markers stay exempt. Verified with the REAL codec in-container (stdlib-only deps) across 9 cases including the reordered-cached-item import path. Story STORY-2026-07-17-bug164-journal-sequence-integrity -> review. Story 06 now has its Critical (159) and one High (164) done; BUG-158,160,161,162,163 remain.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_crystal.py:127-160
  - tests/unit/melder/crystallizer/persistence/test_persistence_crystal_artifact.py
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:139-160
  IMPACT: Malformed imported history can no longer pass the integrity path and replay wrong state.
  NEXT: User runs the persistence suite on 3.14t; continue with story 06 Highs (BUG-162) or BUG-158.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T14:11:45Z
  TYPE: FACT
  CLAIM: HIGH BUG-162 (failed remote graft store reported as shipped) FIXED at root cause: AssetManagementSystem.store_index_graft now honors store_unit's outcome and raises RuntimeError when the only remote store failed (lenient mode swallowed it), because the graft lane has no local durable fallback - so a caller can no longer discard its sole copy believing it shipped. Story STORY-2026-07-17-bug162-graft-store-failure-truth -> review. Story 06 now has 159 (Critical), 164 and 162 (High) done; BUG-158,163 (High/Medium) and 160,161 (Medium) remain.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/asset_management_system.py:819-841
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:356-402
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:93-114
  IMPACT: The graft lane no longer reports a durable write when its only remote store failed.
  NEXT: User runs the asset-management suite on 3.14t; continue with BUG-158 (High) then the Mediums.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T15:58:33Z
  TYPE: FACT
  CLAIM: HIGH BUG-158 (targeted checkpoint emitted its policy twin into the active profile) FIXED at root cause: PersistenceSystem.record now takes an optional profile_name and Crystallizer._emit_policy_twin forwards it, so create_checkpoint(profile_name=X) emits the policy twin into X's window instead of the active profile. Named checkpoints are self-describing again and the active profile no longer receives stray journal traffic; activation and auto-cadence seals keep active-profile behavior (None default). Story STORY-2026-07-17-bug158-targeted-checkpoint-policy-twin -> review. Story 06 Highs (158,162,164) and Critical (159) are DONE; only Mediums 160,161,163 remain in story 06.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:439-490,1500-1510
  - src/melder/crystallizer/persistence/persistence_system.py:214-244
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:7-28
  IMPACT: Profile-scoped checkpoints keep their recording-policy provenance; no cross-profile leakage.
  NEXT: User runs the crystallizer suite on 3.14t; then story 06 Mediums (160,161,163) or the next story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T16:02:55Z
  TYPE: FACT
  CLAIM: MEDIUM BUG-161 (explicit graft storage disabled by the automatic-upload knob) FIXED: added ExternalPersistenceManager.has_store_handler (presence-only) and gated store_index_graft on it instead of store_enabled, so an explicit graft store ships whenever a handler is attached, regardless of upload_on_flush. Composes with BUG-162 (store lane present at the gate). Story STORY-2026-07-17-bug161-graft-store-gating -> review. Story 06: 159(Crit),158/162/164(High),161(Med) DONE; only BUG-160 and BUG-163 (Medium) remain.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:314-345
  - src/melder/crystallizer/asset_management/asset_management_system.py:804-818
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:70-91
  IMPACT: Read-only-flush configurations can perform explicit graft writes again.
  NEXT: User runs the asset-management suite on 3.14t; finish story 06 with BUG-160 and BUG-163.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-18T16:09:15Z
  TYPE: FACT
  CLAIM: MEDIUM BUG-160 (valid non-object JSON aborts cache retention) FIXED at root cause: CrystallizerCache._creation_order now guards the payload with isinstance(dict) before .get(), so a list/null/scalar JSON file sorts as dead weight and reclaims first instead of raising AttributeError and wedging FIFO cleanup. VERIFIED with a real before/after cache repro in-container (original raises; fixed reclaims dead weight, keeps newest). Story STORY-2026-07-17-bug160-cache-retention-non-object-json -> review. Story 06: only BUG-163 (Medium) remains.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:201-224
  - tests/unit/melder/crystallizer/persistence/test_crystallizer_cache.py
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:50-68
  IMPACT: A single malformed-but-parseable cache file can no longer block a profile's cleanup.
  NEXT: User runs the cache suite on 3.14t; finish story 06 with BUG-163.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T16:16:39Z
  TYPE: FACT
  CLAIM: MEDIUM BUG-163 (normal same-window removal produces a false restore shortfall) FIXED: RestoreEngine._fold_chain now suppresses the journal_entry_without_captured_payload shortfall when a later same-window same-key tombstone explains the missing payload (record-then-remove churn), while still flagging genuine gaps. Verified via a 5-scenario logic repro. RESIDUAL (flagged): the pure subtree-sweep case (spellbook_removed parent, no per-child spell_removed) still files a shortfall and needs parent-edge provenance - owner decision. Story STORY-2026-07-17-bug163-same-window-removal-false-shortfall -> review. *** STORY 06 (BUG-158..164) IS NOW COMPLETE: 159(Crit), 158/162/164(High), 160/161/163(Med) all fixed with regressions, pending the user's 3.14t suite run. ***
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:631-676
  - src/melder/crystallizer/persistence/persistence_profile.py:1041-1133,690
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:116-137
  IMPACT: Routine record-then-remove churn no longer emits misleading incomplete-restore diagnostics.
  NEXT: User runs the restore-engine + persistence suites on 3.14t to accept story 06; then start the next story (e.g. 01 or 08 Highs).
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
Remediation epic for the 47 crystallizer persistence bugs from the 2026-07-17 audit, owned by helper_0.
Status ready. Start with the Critical findings (BUG-159),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
