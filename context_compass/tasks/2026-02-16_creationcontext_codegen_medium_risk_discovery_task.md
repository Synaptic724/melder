# Task: CreationContext Codegen Medium-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-creationcontext-codegen-medium-risk-discovery
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Define medium-risk, medium-reward strategy candidates for
`creation_context_codegen.py` that can reduce compile or source-generation
overhead without changing public runtime contracts.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- Internal template strategy and compile lifecycle decisions.
- Out of scope:
- External API shape changes.
- Cross-module refactors that require architecture approval.

## Steps / Checklist
- [x] Identify at least 3 medium-risk strategy candidates with tradeoff analysis.
- [x] For each candidate, define measurable pre/post expectations and failure criteria.
- [x] Record candidate ordering by expected impact vs contract risk.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Ranked medium-risk candidate list with:
  - implementation boundaries,
  - expected impact,
  - `DECISION_REQUEST` triggers.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| CC-M1 | Convert import-time template compilation matrix into lazy-on-first-use compile/cache per route tuple. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283 | Medium startup/initialization improvement; slightly higher first-hit latency. |
| CC-M2 | Add internal template cache keyed by `(lane, route_key, fast_transient, return_created)` instead of static global per-combo symbols. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011 | Medium reduction in import-time compile fan-out and easier cache instrumentation. |
| CC-M3 | Merge overrides/no-overrides source-builder scaffolding into one parameterized builder to cut duplicate source assembly work. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:423-849 | Medium compile-prep reduction and smaller maintenance surface. |
| CC-M4 | Collapse `return_created` template duplication by generating one primary callable and wrapping return-shape adaptation externally. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011 | Medium reduction in template count and compile artifacts. |
| CC-M5 | Prioritize eager compilation only for commonly hit routes (`many`, `unique_per_conduit`) and defer rare routes (`spellspace`, `shared`) to lazy compile. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011 | Medium startup win with bounded runtime tradeoff. |

Execution order:
1. CC-M1
2. CC-M2
3. CC-M4
4. CC-M3
5. CC-M5

## Ops Reference (Reuse)
1. Pre-test: unit + fast cprofile x2 + overrides cprofile x2.
2. Execute one medium-risk candidate per tranche.
3. Post-test with same cadence.
4. Raise `DECISION_REQUEST` if candidate is non-winning or any validation fails; wait for user decision.
5. Record `RESULT` note and artifact path before selecting next candidate.

## Code-Line Evidence (Initial)
`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-296`
```python
def _compile_creation_context_overrides_only_template(
        *,
        resolve_route_key: str,
        return_created: bool,
) -> Callable[..., Any]:
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:343-349`
```python
source = _build_no_overrides_only_template_source(
    no_overrides_lines=no_overrides_lines,
)
local_namespace: dict[str, Any] = {}
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:989-996`
```python
_TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY_FAST = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="many",
        fast_transient_no_overrides_enabled=True,
        return_created=False,
    )
)
```

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If implementation is attempted, run story benchmark gate and raise `DECISION_REQUEST` on non-winning deltas.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: medium-risk candidates may alter compile-time architecture assumptions.
- Mitigation: keep slices compact and benchmark-gated before retention.
- Rollback: execute revert only when user selects revert after a `DECISION_REQUEST` note.

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
  CLAIM: Opened medium-risk discovery lane for CreationContext to pre-rank options that are larger than micro-tuning but still reviewable.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:1-123
  IMPACT: Provides a stable backlog for medium-reward attempts without re-discovery churn each iteration.
  NEXT: Populate ranked option list and define candidate acceptance metrics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Medium-risk CreationContext lane now contains five ranked candidates centered on compile-matrix laziness, template-cache shape, and source-builder deduplication.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1011
  IMPACT: Medium-risk lane can move directly into benchmark-gated experimentation without another broad discovery pass.
  NEXT: Execute CC-M1 first and capture pre/post checkpoint deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the medium-risk lane in the CreationContext discovery queue.
Outputs here should be implementable as compact slices with full benchmark
gates and explicit user-directed decision outcomes.
