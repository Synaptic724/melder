# Task: Investigate Phase Requirements Performance

- Completed: 2026-02-03
- Summary: Closed per user request; ranked candidates and experiment plan remain pending.

## Metadata
- Task ID: TASK-2026-02-01-requirements-phase-perf-investigation
- Story: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## Objective
Investigate why the "Phase requirements" step costs ~15.548ms in the latest
melder hotpath profile and identify candidate optimizations with measurable
impact hypotheses.

## Scope Boundaries
- In scope:
  - Reproduce and inspect the Phase requirements cost in the provided benchmark
    output.
  - Identify concrete hotspots and data flow within the requirements phase.
  - Propose candidate optimizations and an experiment plan to validate impact.
- Out of scope:
  - Implementing code changes.
  - Broad refactors unrelated to Phase requirements.
  - Changes to public API or behavior without a follow-up ticket.

## Steps / Checklist
- [x] Capture the benchmark evidence for Phase requirements (15.548ms) from the
      2026-02-01 run output provided by the user.
- [x] Locate the code path(s) that implement Phase requirements and map the
      call chain with file/symbol evidence.
- [x] Profile or trace Phase requirements in isolation (or via targeted
      instrumentation) to identify dominant sub-steps.
- [ ] Draft a ranked list of candidate savings with expected impact and risk.
- [ ] Define a minimal experiment plan to confirm savings before code changes.

## Deliverables
- Phase requirements investigation notes with:
  - Evidence citation (run output) and current cost.
  - Targeted timing test result: Phase requirements (ms): 16.677 (2026-02-01).
  - Call-chain map with file/symbol references.
  - Hotspot list and candidate optimization ideas.
  - Experiment plan with measurable success criteria.

## Files / Paths Impacted
- Evidence targets for Phase 1:
  - src/melder/spellbook/spellbook.py:_phase_requirements_factory
  - src/melder/spellbook/spell.py:run_phase_requirements
  - src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_requirements
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:build_requirements
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_resolve_parameter_annotations
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_build_parameter_requirements

## Validation
- Ran:
  - set PYTHONPATH=<local-workspace>\src &&
    <local-workspace>\.venv_new\Scripts\python.exe
    -m pytest -s -k test_phase_requirements_root_blueprints_timing
    benchmarks/testing_other_di/test_phase_requirements_root_blueprints_timing.py
- Output highlight:
  - Phase requirements (ms): 16.677
- Warning:
  - PytestCacheWarning: could not create cache path
- Recommended commands:
  - (None; timing test already executed.)

## Risks / Rollback Notes
- Risk: Misattributing time to the wrong sub-steps due to coarse profiling.
  Mitigation: Use targeted profiling or trace instrumentation for the phase.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Benchmark evidence shows Phase requirements at 15.548ms (user output on
2026-02-01). Targeted timing test (2026-02-01) measured Phase requirements at
16.677ms. Call chain mapped (see Files/Paths). Next: rank candidate savings
and define a minimal experiment plan for Phase 1. Closed per user request with
ranked candidates and experiment plan still outstanding.
