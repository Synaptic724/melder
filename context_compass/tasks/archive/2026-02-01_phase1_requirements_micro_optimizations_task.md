# Task: Investigate Phase 1 Requirements Micro-Optimizations

- Completed: 2026-02-03
- Summary: Documented Phase 1 micro-optimization candidates with evidence and a verification plan.

## Metadata
- Task ID: TASK-2026-02-01-phase1-requirements-micro-optimizations
- Story: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## Objective
Identify low-risk, code-level optimizations inside Phase 1 requirements
extraction that reduce reflection and annotation processing cost without
changing Phase 1 semantics.

## Scope Boundaries
- In scope:
  - Code-path review of Phase 1 requirements extraction.
  - Identify concrete, localized micro-optimizations with evidence.
  - Produce a ranked shortlist with expected savings and risks.
- Out of scope:
  - Implementing code changes.
  - Caching semantics or cross-pass reuse policy changes.
  - Broad refactors or public API changes.

## Steps / Checklist
- [x] Map Phase 1 call path and identify highest-cost operations in code.
- [x] Audit annotation resolution flow for avoidable work.
- [x] Draft 3-5 concrete micro-optimizations with evidence and risks.
- [x] Define a minimal verification plan (non-cProfile; code-review + targeted
      runtime checks if needed).

## Deliverables
- Phase 1 micro-optimization notes with:
  - Evidence-backed hotspots in SpellRequirementsFinder.
  - Ranked list of candidate changes.
  - Risk notes and semantic constraints.
  - Minimal verification plan.

## Findings (Ranked Candidates)
1) Conditional annotation resolution per parameter (skip _resolve_parameter_annotations when no params need it).
   - Evidence: `_build_parameter_requirements` always calls `_resolve_parameter_annotations(call_target)` before iterating parameters.
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_build_parameter_requirements
   - Candidate: scan `signature.parameters` for string/ForwardRef or generic typing before calling `_resolve_parameter_annotations`.
   - Expected impact: UNKNOWN (hypothesis: reduces unnecessary `inspect.get_annotations` + normalization work).
   - Risk: low if the scan is conservative (only skip when no annotations require resolution).

2) Fast-path simple string annotations (skip AST parse for name-like strings).
   - Evidence: `_normalize_annotation` calls `_parse_annotation_expression` for every string annotation.
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_normalize_annotation
   - Candidate: detect simple names (e.g., `Foo`, `pkg.Foo`) and resolve directly via `_resolve_annotation_name`.
   - Expected impact: UNKNOWN (hypothesis: reduces AST parsing overhead on common cases).
   - Risk: medium; must preserve forward-ref parsing for complex strings (subscripts, unions).

3) Avoid repeated `get_origin/get_args` per parameter.
   - Evidence: `_classify_parameter` calls `_unwrap_optional` (which uses `get_origin/get_args`) and then re-calls `get_origin/get_args` on `base_annotation`.
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_classify_parameter
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_unwrap_optional
   - Candidate: inline optional-unwrapping and reuse a single `origin/args` tuple.
   - Expected impact: UNKNOWN (hypothesis: reduces per-parameter typing inspection).
   - Risk: low if logic is preserved.

4) Aggressive no-resolution fast path (return raw annotations when none require resolution).
   - Evidence: `_resolve_parameter_annotations` already has a `needs_resolution` check, but the caller still invokes it unconditionally.
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_build_parameter_requirements
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_resolve_parameter_annotations
   - Candidate: only call `_resolve_parameter_annotations` if at least one parameter annotation needs resolution.
   - Expected impact: UNKNOWN (hypothesis: skips inspect.get_annotations for common cases).
   - Risk: low if the pre-scan is accurate.

5) Fast DI-target heuristic for non-DI types.
   - Evidence: `_looks_like_di_target` runs `inspect.isclass` for each annotation that is not a string/ForwardRef.
     EVIDENCE: src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:_looks_like_di_target
   - Candidate: fast-path known non-DI types (builtins, typing.Any) before `inspect.isclass`.
   - Expected impact: UNKNOWN (hypothesis: reduces class introspection cost).
   - Risk: low if the non-DI set matches current semantics.

## Files / Paths Impacted
- Evidence targets:
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_build_parameter_requirements
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_resolve_parameter_annotations
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_normalize_annotation
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_classify_parameter
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_unwrap_optional
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/
    spell_requirements_finder.py:_looks_like_di_target

## Validation
- Not run.
- Recommended commands:
  - None (investigation-only ticket).

## Risks / Rollback Notes
- Risk: Micro-optimizations could change annotation resolution semantics.
  Mitigation: restrict to fast-paths that preserve existing outputs; verify
  with focused unit tests before any implementation.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Initial evidence shows Phase 1 spends time in reflection and annotation
resolution. Candidate optimization areas (to validate) include:
- _resolve_parameter_annotations resolves all annotations up front, even if
  only some parameters need string/ForwardRef/generic resolution.
- _normalize_annotation always parses string annotations through AST even for
  simple name references.
- _classify_parameter calls _unwrap_optional (get_origin/get_args) and then
  re-calls get_origin/get_args on the same annotation.
- _looks_like_di_target relies on inspect.isclass for every parameter.
Evidence targets listed above in spell_requirements_finder.py.
Next step: if you want implementation, pick the first candidate to land
and I will write a separate implementation ticket (with tests) per
AGENTS.MD.
