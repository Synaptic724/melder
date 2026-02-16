# Task: CreationContext Codegen Low-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-creationcontext-codegen-low-risk-discovery
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Identify low-risk, contract-safe efficiency candidates inside
`creation_context_codegen.py` that can be implemented in compact slices.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- Source emission assembly costs and deterministic key/allocation paths.
- Out of scope:
- Runtime semantics changes in `creation_context.py`.
- Public API or call-shape changes.

## Steps / Checklist
- [x] Build a low-risk candidate matrix (at least 3 items) with estimated upside.
- [x] Attach evidence pointers for each candidate and classify expected blast radius.
- [x] Define keep/revert guardrails per candidate before implementation.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Low-risk candidate matrix with:
  - candidate description,
  - expected gain vector,
  - risk rationale,
  - validation scope.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| CC-L1 | Replace route-key if/elif selector chains with small precomputed dispatch maps for template lookup. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283 | Low but measurable reduction in branch overhead on route selection doors; cleaner maintenance. |
| CC-L2 | Share one internal compile+exec helper between overrides-only and no-overrides-only template compilation paths. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358 | Low compile-path allocation reduction and reduced duplicate failure-path code. |
| CC-L3 | Reduce emitted-source assembly allocations by reusing static header/footer fragments and minimizing repeated indentation work. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:851-871 | Low compile-time object churn reduction during template source assembly. |
| CC-L4 | Precompute `source_name` format fragments for compile paths to reduce repeated string formatting churn. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:305-341 | Low reduction in compile-miss string allocation overhead. |
| CC-L5 | Prebind route-key specific template selectors in tiny dicts keyed by `(route, fast_flag)` to remove duplicate branch ladders in hooks/no-hooks lanes. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283 | Low runtime dispatch simplification with minimal behavior risk. |

Execution order:
1. CC-L1
2. CC-L2
3. CC-L3
4. CC-L4
5. CC-L5

## Ops Reference (Reuse)
1. Pre-test: unit + fast cprofile x2 + overrides cprofile x2.
2. Implement one candidate only.
3. Post-test: same cadence.
4. Compare against retained checkpoint.
5. Revert on any failure or non-winning delta.
6. Publish `RESULT: RETAINED` or `RESULT: REVERTED` with artifact path.

## Code-Line Evidence (Initial)
`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:203-211`
```python
if resolve_route_key == "existing_creation":
    return _TEMPLATE_EXISTING_INSTANCE_OVERRIDES_ONLY
if resolve_route_key == "many":
    return _TEMPLATE_MANY_INSTANCE_OVERRIDES_ONLY
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:312-317`
```python
exec(
    compile(source, source_name, "exec"),
    {},
    local_namespace,
)
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-880`
```python
_TEMPLATE_EXISTING_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="existing_creation",
        return_created=True,
    )
)
```

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If a candidate is implemented in this task, run the story benchmark gate.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: low-risk label can hide behavior-coupled assumptions.
- Mitigation: require concrete source evidence and keep UNKNOWN discipline.
- Rollback: if implemented candidate is non-winning, revert immediately per story gate.

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
  CLAIM: Opened low-risk discovery lane for CreationContext codegen so iterations can pull compact, contract-safe candidates from a pre-scoped queue.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:1-123
  IMPACT: Eliminates ad-hoc search churn and keeps iteration entry deterministic.
  NEXT: Populate candidate matrix with at least 3 low-risk options and evidence pointers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Initial low-risk candidate backlog is populated with three compact options focused on selector dispatch, compile helper deduplication, and source assembly allocation trimming.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420
  IMPACT: Low-risk lane is now immediately executable without additional discovery passes.
  NEXT: Execute CC-L1 first under the story benchmark gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the low-risk lane in the CreationContext discovery queue. It
should produce implementation-ready candidates that preserve current contracts
and use the existing benchmark keep/revert gate if code changes are attempted.
