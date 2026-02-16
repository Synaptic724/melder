# Task: CreationContext Codegen High-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-creationcontext-codegen-high-risk-discovery
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Investigate high-risk/high-reward strategy candidates for
`creation_context_codegen.py` that could materially reduce codegen overhead but
may require deeper architectural changes.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- Major template-matrix and compile-lifecycle redesign concepts.
- Out of scope:
- Unapproved public API breaks.
- Multi-module architecture changes without explicit user confirmation.

## Steps / Checklist
- [x] Define at least 2 high-risk candidates with explicit architecture impact.
- [x] For each candidate, document required safeguards and fallback plan.
- [x] Identify prerequisites for safe experiment execution (tests, observability, rollback hooks).
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- High-risk option brief per candidate with:
  - architecture impact,
  - migration risk,
  - measurable payoff hypothesis.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| CC-H1 | Replace runtime `compile(...)+exec(...)` template generation with closure factories created without dynamic source compilation. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420 | High reduction in codegen compile overhead and parser work; large implementation risk. |
| CC-H2 | Replace static matrix of global template constants with generated registry initialized from declarative route specs. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011 | High maintainability and startup improvements; high regression risk in route parity. |
| CC-H3 | Move codegen artifact production to a build-time or conjure-time cache layer and load precompiled code objects at runtime. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011 | Potentially large runtime startup and warm-path gains; complex invalidation requirements. |
| CC-H4 | Collapse hooks/no-hooks template families into one generalized executor lane with strategy callbacks for hook behavior. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420 | High code-size reduction and fewer template variants; higher behavioral coupling risk. |
| CC-H5 | Introduce profiler-guided specialization policy that compiles only high-frequency route variants and falls back to generic lane. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011 | High upside for real workloads if hit-distribution is skewed; high complexity and observability needs. |

Execution order:
1. CC-H2
2. CC-H1
3. CC-H3
4. CC-H4
5. CC-H5

## Ops Reference (Reuse)
1. Keep this lane discovery-first until explicitly promoted.
2. If promoted, run full pre/post benchmark gate and raise `DECISION_REQUEST` for keep/revert decision.
3. Execute one high-risk candidate per tranche.
4. Publish explicit `RESULT` note before moving to next candidate.

## Code-Line Evidence (Initial)
`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:312-317`
```python
exec(
    compile(source, source_name, "exec"),
    {},
    local_namespace,
)
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-380`
```python
lines = [
    "def _creation_context_no_overrides_only_template(",
    "        _spell,",
    "        _spell_id,",
    "        _owner_creations,",
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:933-940`
```python
_TEMPLATE_EXISTING_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="existing_creation",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
```

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If experimentation becomes implementation, enforce the story benchmark gate and `DECISION_REQUEST` rules.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: large redesign can break codegen contracts and raise regression odds.
- Mitigation: discovery only until explicit approval for bounded experiments.
- Rollback: design-stage only; if coded and gate fails, raise `DECISION_REQUEST` and wait for user decision.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Medium discovery tickets were turned in per user direction, so active CreationContext routing now starts this high-risk lane.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_medium_risk_discovery_task.md:1-132, context_compass/attention_board.md:16-28
  IMPACT: High-risk exploration is now the primary execution lane.
  NEXT: Start with `CC-H2` pre-tranche analysis and benchmark gate planning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Opened high-risk discovery lane for CreationContext codegen to isolate architectural options from low/medium implementation loops.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:1-123
  IMPACT: High-risk work can be evaluated deliberately without polluting near-term iteration cadence.
  NEXT: Document candidate redesigns with migration/fallback plans before any implementation ask.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: High-risk CreationContext lane is populated with five architectural options covering dynamic compile removal, matrix collapse, and artifact lifecycle redesign.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011
  IMPACT: High-risk lane now has concrete options and ordering for deliberate future experiments.
  NEXT: Keep high-risk lane discovery-only until low/medium lanes are exhausted or user reprioritizes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task captures high-risk candidate exploration only. Any promotion to code
changes requires explicit decision, compact scope, and full benchmark-gated
validation.
