# Task: Investigate Phase Root Blueprints Performance

- Completed: 2026-02-03
- Summary: Completed Phase root_blueprints performance investigation with ranked candidates and an experiment plan.

## Metadata
- Task ID: TASK-2026-02-01-root-blueprints-phase-perf-investigation
- Story: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## Objective
Investigate why the "Phase root_blueprints" step costs ~9.789ms in the latest
melder hotpath profile and identify candidate optimizations with measurable
impact hypotheses.

## Scope Boundaries
- In scope:
  - Reproduce and inspect the Phase root_blueprints cost in the provided
    benchmark output.
  - Identify concrete hotspots and data flow within the root_blueprints phase.
  - Propose candidate optimizations and an experiment plan to validate impact.
- Out of scope:
  - Implementing code changes.
  - Broad refactors unrelated to Phase root_blueprints.
  - Changes to public API or behavior without a follow-up ticket.

## Steps / Checklist
- [x] Capture the benchmark evidence for Phase root_blueprints (9.789ms) from
      the 2026-02-01 run output provided by the user.
- [x] Locate the code path(s) that implement Phase root_blueprints and map the
      call chain with file/symbol evidence.
- [x] Profile or trace Phase root_blueprints in isolation (or via targeted
      instrumentation) to identify dominant sub-steps.
- [x] Draft a ranked list of candidate savings with expected impact and risk.
- [x] Define a minimal experiment plan to confirm savings before code changes.

## Deliverables
- Phase root_blueprints investigation notes with:
  - Evidence citation (run output) and current cost.
  - Targeted timing test result: Phase root_blueprints (ms): 3.673 (2026-02-01).
  - Call-chain map with file/symbol references.
  - Hotspot list and candidate optimization ideas.
  - Experiment plan with measurable success criteria.

## Findings (Ranked Candidates)
1) Reduce per-spell blueprint construction for non-roots (high impact, high risk).
   - Evidence: `run_phase_root_blueprints` builds root blueprints, then iterates
     every spell and calls `build_blueprint_for_spell_id` for any spell without a
     blueprint (all non-root non-existing-creation spells).
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints
   - Candidate: gate per-spell blueprint construction based on whether downstream
     phases will actually run for that spell (requires semantics decision).
   - Expected impact: UNKNOWN (hypothesis: avoids N blueprint builds when many
     spells are not resolved in a given run).
   - Risk: high; changes when/which spells have Phase 5 artifacts.

2) Optimize socket overlay traversal (medium impact, medium risk).
   - Evidence: `_overlay_sockets_and_index` BFS walks topology sockets and for each
     socket does `PathRegistry.extend_path` + `DagIndex.add_socket` + BFS enqueue.
     EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:_overlay_sockets_and_index
   - Candidate: introduce local caching or batching of `extend_path` results for
     repeated (path_id, param_name) pairs to reduce dict lookups.
   - Expected impact: UNKNOWN (hypothesis: reduces repeated PathRegistry churn).
   - Risk: medium; must preserve PathRegistry id stability per (parent, segment).

3) Reduce redundant membership checks in snapshot filtering (low impact, low risk).
   - Evidence: `_filter_snapshot_to_visible_spells` computes `filtered_deps` as a
     subset of visible ids, then re-checks `if dep_id in all_spell_ids` inside the
     loop.
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:_filter_snapshot_to_visible_spells
   - Candidate: remove the redundant membership check; keep behavior identical.
   - Expected impact: UNKNOWN (minor).
   - Risk: low.

4) Reduce repeated `get_origin/get_args` in socket-agnostic loops (low impact, low risk).
   - Evidence: `PathRegistry.extend_path` and `DagIndex.add_socket` are invoked
     per socket; overhead is dominated by dict/list operations (profile evidence).
     EVIDENCE: src/melder/spellbook/spell_crafter/dag/dag_index.py:PathRegistry.extend_path
     EVIDENCE: src/melder/spellbook/spell_crafter/dag/dag_index.py:DagIndex.add_socket
   - Candidate: micro-optimizations in these hot methods (local aliasing,
     reduce tuple allocations) without semantic changes.
   - Expected impact: UNKNOWN (minor to moderate depending on socket volume).
   - Risk: low if behavior is preserved.

## Minimal Experiment Plan (Non-cProfile)
- Add a test-only wrapper or monkeypatch to count calls to:
  - `PathRegistry.extend_path`
  - `DagIndex.add_socket`
  - `SpellSystemRootBlueprintBuilder._overlay_sockets_and_index`
  - `SpellSystemRootBlueprintBuilder._build_single_root_dag`
- Use an existing phase timing test harness to run once and collect counts.
- Success criteria: reduced call counts or equivalent outputs with fewer
  allocations; behavior must remain identical in unit tests.

## Files / Paths Impacted
- Evidence targets for Phase 5:
  - src/melder/spellbook/spellbook.py:_phase_root_blueprints_factory
  - src/melder/spellbook/spell.py:run_phase_root_blueprints
  - src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py:build
  - src/melder/spellbook/spell_crafter/spell_crafter.py:_filter_snapshot_to_visible_spells
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:build_root_blueprints
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:_build_single_root_dag
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:_overlay_sockets_and_index
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:build_blueprint_for_spell_id
  - src/melder/spellbook/spell_crafter/dag/dag_index.py:PathRegistry.extend_path
  - src/melder/spellbook/spell_crafter/dag/dag_index.py:DagIndex.add_socket

## Validation
- Ran:
  - set PYTHONPATH=<local-workspace>\src &&
    <local-workspace>\.venv_new\Scripts\python.exe
    -m pytest -s -k test_phase_requirements_root_blueprints_timing
    benchmarks/testing_other_di/test_phase_requirements_root_blueprints_timing.py
- Output highlight:
  - Phase root_blueprints (ms): 3.673
- Warning:
  - PytestCacheWarning: could not create cache path
- Recommended commands:
  - (None; timing test already executed.)

## Risks / Rollback Notes
- Risk: Misattributing time to the wrong sub-steps due to coarse profiling.
  Mitigation: Use targeted profiling or trace instrumentation for the phase.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Benchmark evidence shows Phase root_blueprints at 9.789ms (user output on
2026-02-01). Targeted timing test (2026-02-01) measured Phase root_blueprints
at 3.673ms. Call chain mapped (see Files/Paths). Next: rank candidate savings
and define a minimal experiment plan for Phase 5. Ranked candidates and a
non-cProfile experiment plan are now captured above; next step is to select
which candidate(s) to implement.
