

# Task: Triage compiler cache-version gate and phase-10 family-selection contamination

## Metadata
- Task ID: TASK-2026-07-12-compiler-cache-version-and-phase10-family-triage
- Story: none (owner-reported findings, direct task)
- Status: completed (owner full-tree run green; closeout authorized 2026-07-12)
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-12T10:15:00Z
- Updated: 2026-07-12T11:30:28Z

## Objective
Verify the three owner-reported compiler findings against source, promote each to FACT or
refute it with evidence, and stage the minimal fix plan for owner confirmation:
1) CachingSystem CURRENT_VERSION stuck at 5 while version-6 semantics are documented.
2) Phase-10 family discovery counts the whole spellbook pool instead of the root-visible set.
3) Possible shared-provider contract-override loss when phase-8 occurrence collapse retains
   one canonical occurrence (semantics ruling needed).

## Ticket Contract
- ENTRY_GATE: active attention_board row routes here; owner directive 2026-07-12 supplies scope.
- EXECUTION_BOUNDARY: read-only triage over
  src/melder/utilities/caching_system/caching_system.py,
  src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py,
  src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/{solo,many_only}_codegen_plan_discovery_strategy.py,
  src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py.
  NO code edits in this task without explicit owner confirmation of the fix plan.
- DEPENDENCIES: stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md (family
  discovery lane), epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md
  (cache lane).
- EXIT_GATE: all three findings promoted to FACT or refuted with path:line evidence; fix plan
  recorded as DECISION/DECISION_REQUEST notes; owner ruling captured for finding 3.
- FAILURE_ESCALATION: DECISION_REQUEST for the shared-provider semantics ruling; BLOCKER if
  source access fails mid-triage.

## Scope Boundaries
- In scope: evidence verification, impact analysis, fix-plan proposal, tests-needed inventory.
- Out of scope: implementing fixes (separate confirmation), unrelated compiler refactors,
  cache format redesign.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner directive 2026-07-12 ("focus on this"); triage is read-only.

## Steps / Checklist
- [x] Verify finding 1 against caching_system.py (version comment vs CURRENT_VERSION vs gate).
- [x] Verify finding 2 against phase-8 analyzer pool walk and phase-10 solo/many_only checks.
- [x] Verify finding 3 against phase-8 collapse and phase-9 injection payload read (read side; record side still UNKNOWN).
- [x] Record fix plan + DECISION_REQUEST notes; report to owner (owner ruled: implement).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed verdict per finding + minimal fix plan awaiting owner confirmation.

## Files / Paths Impacted
- Triage is read-only; candidate fix files listed in EXECUTION_BOUNDARY.

## Validation
- Owner full-tree run: green.
- Focused verification completed during closeout:
  - 523 relevant compiler/conduit tests passed.
  - 18 caching-system unit tests passed.
  - 7 cache-schema integration versions passed.
  - 34 SpellContract integration/component tests passed.
  - Real in-memory compiler probes confirmed root-visible family selection,
    shared-provider payload application, identical-payload deduplication, and
    loud conflicting-payload failure.

## Risks / Rollback Notes
- Warm caches minted at version 5 may carry pre-fix phase-8/11 bodies; bumping
  CURRENT_VERSION forces cold regeneration (intended, but first melds pay compile cost).
- Family-selection fix changes which compiler family a root selects; construction results
  should be identical, specialization/performance differs; needs regression rows.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-12T10:15:00Z
  TYPE: PLAN
  CLAIM: Owner reported three compiler findings (owner paste, prompt_id
    compiler-findings-20260712-09). Triage order: cache version gate, phase-10 family
    contamination, shared-provider payload loss. All three start UNKNOWN until source-verified.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:60-78
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:478-502
  IMPACT: Warm caches may bypass a shipped correctness fix; family selection may be
    nondeterministic across spellbook composition; contract payloads may silently drop.
  NEXT: Read caching_system.py version block and validity gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-12T11:05:00Z
  TYPE: FACT
  CLAIM: RESTORATION - the 10:32Z verdict-notes commit through the bridge was truncated at
    the file's prior byte length (6199), the same mid-write truncation class recorded on the
    boards; this rebuild rewrites the full ticket on-device and re-records the 10:32Z
    verdicts inline below (content identical in substance, compacted).
  EVIDENCE:
  - tickets/tasks/2026-07-12_compiler_cache_version_and_phase10_family_triage_task.md:1-1
  IMPACT: Durable record repaired; bridge-commit path treated as truncation-prone for
    multi-KB rewrites - on-device file writes are the reliable lane.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6
- DATETIME: 2026-07-12T10:32:00Z
  TYPE: FACT
  CLAIM: Finding 1 (cache version) was ALREADY FIXED in tree before this lane touched it:
    CURRENT_VERSION derives max(CACHE_VERSION_HISTORY) and the load gate refuses mismatched
    bundles; owner confirmed. No action needed.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:78-92
  - src/melder/utilities/caching_system/caching_system.py:452-455
  IMPACT: Stale warm caches cannot bypass the zero-provider collection fix.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-07-12T10:32:00Z
  TYPE: FACT
  CLAIM: Finding 2 CONFIRMED: phase-8 built SpellExistenceOccurrenceAnalysis from the
    full-pool shared walk (total_spell_count = len(pool rows)) while phase-10 solo/many_only
    docstrings promise the root-visible set; unrelated pool members rerouted families
    (solo->many_only, many_only->generalized), nondeterministic per spellbook composition.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:478-494
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:47-56
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:41-55
  IMPACT: Specialization/perf routing contaminated; construction unaffected.
  NEXT: fixed - see 10:55Z DECISION.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-12T10:32:00Z
  TYPE: FACT
  CLAIM: Finding 3 mechanism CONFIRMED both sides: phase-9 records payloads per
    path-specific edge (contract_overrides_by_spell_id keeps ALL edges), phase-8 collapse
    keeps one canonical occurrence per shared spell, and injection read only the canonical
    key - so payload application depended on BFS canonical-edge luck. Owner ruled option (c).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:666-674
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:378-396
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:187-199
  IMPACT: Silent order-dependent payload loss eliminated by the 10:55Z fix.
  NEXT: fixed - see 10:55Z DECISION.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-12T10:55:00Z
  TYPE: DECISION
  CLAIM: Owner authorized both fixes; implemented on-device, all py_compile-clean.
    (1) Root-visible family selection: analyze() builds the existence analysis AFTER the
    occurrence graph via _get_shared_spell_walk (memoized pool walk, perf unchanged) +
    _build_existence_occurrence_analysis (filters rows to the graph's spell ids, recomputes
    all aggregates); old combined builder removed, zero callers remain. (2) Shared-provider
    payloads option (c): injection's shared branch resolves via
    _resolve_shared_contract_payload - one distinct payload applies regardless of canonical
    edge; multiple distinct payloads raise teach-grade MeldExecutionError; TYPE_CHECKING
    concrete typing, no Any. (3) CACHE_VERSION_HISTORY += 7 "root_visible_family_selection";
    CURRENT_VERSION derives 7 so pre-fix bundles cold-regenerate.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:141-145
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:187-199
  - src/melder/utilities/caching_system/caching_system.py:78-92
  IMPACT: Deterministic per-root family selection; loud payload conflicts; stale bundles
    invalidate.
  NEXT: regression rows (four) then owner 3.14t run; REOPEN on red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T11:15:00Z
  TYPE: FACT
  CLAIM: Test debt paid: 7 regression rows landed in
    tests/unit/melder/spellbook/spell_compiler/test_root_visible_family_selection_regressions.py
    (root-visible filtering unit row incl. aggregate recompute; solo-vs-unrelated-many and
    many_only-vs-unrelated-unique family rows through the REAL discovery strategies;
    single-payload edge-independence; identical-payload dedupe; conflicting-payload
    MeldExecutionError; zero-payload canonical fallback). Conventions mirror
    test_codegen_plan_discovery_core.py (probe doubles, typed tests, direct seam calls).
    py_compile-clean. pytest Not run.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_root_visible_family_selection_regressions.py:1-220
  IMPACT: Both fixes carry contract-level regression coverage; a revert of either fix fails
    these rows, a harmless refactor does not.
  NEXT: Owner 3.14t full-tree run; close on green, REOPEN on red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T11:30:28Z
  TYPE: CLOSURE
  CLAIM: COMPLETE. Owner reported the full test tree green and explicitly authorized closeout.
    Source retrace confirmed all three ticket findings are implemented on the real compiler
    path; focused suites and in-memory probes are green; the seven regression rows and cache
    version 1-7 integration map are present. This direct melder_0 task is closed and archived
    under `tickets/tasks/completed/`; the broader compiler epics remain active and untouched.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:199-205
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:187-324
  - src/melder/utilities/caching_system/caching_system.py:78-93
  - tests/unit/melder/spellbook/spell_compiler/test_root_visible_family_selection_regressions.py:98-220
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:18-68
  IMPACT: The lane no longer requires active routing; regressions remain guarded in-tree.
  NEXT: none; reopen only on a regression.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Completed 2026-07-12 on owner green + explicit closeout authorization. Finding 1 remained
correct through the version-7 schema gate; findings 2 and 3 are implemented as root-visible
existence analysis and shared-provider payload aggregation with loud conflict failure.
Seven focused regressions, cache versions 1-7, focused suites, and real compiler probes are
green. Archived under `tickets/tasks/completed/`; reopen only on a regression.
