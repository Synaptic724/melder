# Task: Measure an isolated normal-style override emitter before production changes

- Completed: 2026-09-26T13:45:56Z
- Summary: Measured gains and ten independent regressions accepted by lead. Turned in by the owner in the 2026-09-26 board cleanup (row agent updater_1);
  no further work; artifacts retained as reference.

## Metadata
- Task ID: TASK-2026-09-24-experiment-static-many-override-execution
- Epic: EPIC-2026-09-24-override-execution-performance
- Status: done
- Owner: codex
- Agent Name: updater_1
- Lead Agent: updater_0
- Priority: p1
- Created: 2026-09-24T10:33:26Z
- Updated: 2026-09-26T13:45:56Z

## Objective
Build an artifact-only prototype that retains the current constructor sequence but substitutes
named override operands into normal-style calls, then measure it against current execution.

## Ticket Contract
- ENTRY_GATE: OEP-007 compiler diagnosis delivered; lead OEP-008 assigns this bounded experiment.
- EXECUTION_BOUNDARY: New diagnostic files under artifacts/override_emission_prototype_20260924/,
  this task and ordinary coordination boards. Existing benchmark fixture/experiment may be imported.
  No production edits, new public APIs, build generation or branch pruning.
- DEPENDENCIES: Compiler captures, existing performance experiment and lead runtime_constraints.md.
- EXIT_GATE: Correctness/parity assertions, repeated timings, raw provenance and a bounded recommendation.
- FAILURE_ESCALATION: Report unsupported shapes or unsafe lowering explicitly; do not alter semantics
  or silently narrow a result labeled as general override support.

## Scope Boundaries
- In scope: Disposal-free many-only known argument layouts with named root/path/broadcast inputs.
- Out of scope: Generalized/scoped emitters, positional bug fixes, lifetime changes and production wiring.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Both measured variants passed parity; timing released and evidence sent for lead review.
- from_state: review
- to_state: done
- transition_reason: Owner turned in this dormant row in the 2026-09-26 shared-board cleanup (all 13 dormant rows,
  2026-09-26T13:45:56Z); closed by fable_0 with board and artifact sync.

## Steps / Checklist
- [x] Acknowledge OEP-008 and document the exact prototype seam/eligibility.
- [x] Build the isolated lowering with per-call values and unchanged constructor order/count.
- [x] Assert reference parity and alternate equal-count a-only/b-only shapes with changing values.
- [x] Measure matched warm public/executor calls where feasible; report preparation separately.
- [x] Send raw results and recommendation to updater_0, then stop this tranche at review.

## Deliverables
- Reproducible diagnostic code; exact unsupported boundaries; raw samples and source/runtime provenance.
- Same-work before/after observations, including unchanged ordinary no-override control.

## Files / Paths Impacted
- artifacts/override_emission_prototype_20260924/ and this task.
- Shared boards only through focused edits preserving peer work.

## Validation
Two seven-repeat variants each pass 19 graph cases and 64 shape/value alternations with identical
constructor sequences. Runtime/prototype hashes are stable. Ruff passes with codegen/typing exceptions
documented below. Timing slot released through OEP-012. Lead independently passed ten unchanged
many-only regressions and verified ten executor bodies/defaults/namespaces restored at the measured hash.

## Risks / Mitigations
- A prototype may bypass real gates: distinguish executor-only from public measurements explicitly.
- Do not capture supplied values into shape caches. Alternate shape and value correctness before timing.
- Keep every original constructor even when its result is replaced; pruning gains are outside this result.

## Applicable Anti-Patterns
- [x] No claimed production optimization from a diagnostic.
- [x] No mismatched constructor counts or swallowed unsupported cases in performance ratios.
- [x] No timing contention between the two collaborating agents.

## Done Checklist
- [x] Scope and code are reviewable; correctness and measurement evidence retained.
- [x] Lead received result and limitations; production remains unchanged.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/override_emission_prototype_20260924/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Preserve the proof for the production design decision.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Static operand emission, shape reuse and matched measurements.
- IF_UNKNOWN: none

## Noting Behavior
Record complete diagnostic tranches and exact evidence before sending mailbox findings.

## Notes
- DATETIME: 2026-09-24T10:33:26Z
  TYPE: DECISION
  CLAIM: updater_0 selects the bounded experiment recommended by updater_1 in OEP-007. This is
    authorized diagnosis under the epic; no production compiler change is being delegated.
  EVIDENCE:
  - tickets/epics/2026-09-24_override_execution_performance_epic.md:29-33
  - artifacts/override_compiler_investigation_20260924/compiler_findings.md
  IMPACT: Measured evidence will make the implementation proposal concrete without speculative speed claims.
  NEXT: Acknowledge assignment and record the diagnostic seam before writing the prototype.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:39:20Z
  TYPE: PLAN
  CLAIM: OEP-008 accepted. Intercept only the finalizer's completed override executor binding inside
    the diagnostic process. Retain the actual executor object/namespace and generate a replacement
    body from its ordered steps and exact prefiltered sockets. Switch its code/defaults between
    original and prototype outside each single-thread timing sample, preserving existing public
    gates, targeting and cache doors without a timed dispatch trampoline. Restore all objects on exit.
    Restrict to named scalar sockets, disposal-free many, no collections/contract payloads/positionals.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:673-766
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:336-542
  IMPACT: Paired public and executor-only samples can compare identical graphs and constructor work.
    Borrow only static targets/sockets; values remain per call. Record original preparation and
    extra prototype construction separately; no production cold-start speedup claim.
  NEXT: Build the artifact-only prototype and qualify identity, constructor order and a/b alternation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:46:07Z
  TYPE: MEASURE
  CLAIM: Shallow smoke passes ordered-construction and supplied-reference assertions plus 64
    alternating a/b calls without new shape compilation. Prototype code swaps the actual executor
    body with no timed trampoline. Full measurements are not yet run. Ruff passes with UP045
    excluded for Optional typing and S102 excluded because this is the authorized codegen experiment.
    OEP-009 received: retain prototype hashes, distinct public/executor measurements and review seams.
  EVIDENCE:
  - artifacts/override_emission_prototype_20260924/prototype.py
  - Lead's OEP-009 harness-audit message, 2026-09-24T10:37:17Z.
  IMPACT: Full graph qualification/timing can run serially. Samples now rotate cases and backend
    order with equal iterations per pair. First-case preparation reports whether a new shape bound;
    additional prototype generation is reported separately, not as a cold-start improvement.
  NEXT: Run seven-repeat shallow/wide/diamond/deep comparisons with runtime and prototype drift checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:48:42Z
  TYPE: MEASURE
  CLAIM: First full seven-repeat run passes all 19 graph cases and 64 alternating a/b values.
    Constructor sequence/count remains 3/9/5/511. Direct-keyword prototype public original-override
    speedups are shallow 1.50x, wide 1.89x, diamond 1.60x, deep 2.63x; normal controls stay within 1%.
    Runtime and prototype hashes are stable. Exact data/code are retained as keyword_results and
    keyword_prototype. This variant still uses keyword calls on every unchanged dependency node.
  EVIDENCE:
  - artifacts/override_emission_prototype_20260924/keyword_results.json
  - artifacts/override_emission_prototype_20260924/keyword_results.md
  - artifacts/override_emission_prototype_20260924/keyword_prototype.py
  IMPACT: Static emission alone substantially reduces the measured gap with identical constructor work.
    One final controlled variant uses normal positional calls only when every parameter is supplied
    and all kinds are POSITIONAL_OR_KEYWORD, retaining keyword emission for incomplete layouts.
  NEXT: Measure the actual normal-style positional layout before releasing the serial timing slot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:50:53Z
  TYPE: MEASURE
  CLAIM: Final seven-repeat positional-layout variant passes the same 19 cases and 64 changing
    a/b calls. Public original-override medians improve shallow 1.997->1.219 us (1.64x), wide
    3.505->1.548 us (2.26x), diamond 2.808->1.470 us (1.91x), deep 155.738->33.292 us (4.68x).
    Deep reaches about 95% of normal throughput while still executing all 511 constructors.
    Ordinary controls remain within 1%; runtime and prototype hashes are stable.
    OEP-011 received: lead has an independent parity/restoration runner ready.
  EVIDENCE:
  - artifacts/override_emission_prototype_20260924/results.json
  - artifacts/override_emission_prototype_20260924/results.md
  - artifacts/override_emission_prototype_20260924/prototype.py
  IMPACT: Default call layout plus exact operand substitution closes most of the measured deep gap
    without pruning. Wide all-root input remains 7.377 us publicly versus 1.260 us for its inner
    executor, so substantial front-end work remains in that shape. This is not a production patch.
  NEXT: Release timing to updater_0 for independent parity review and write the final interpretation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:55:08Z
  TYPE: DECISION
  CLAIM: OEP-013 confirms lead receipt of the timing handoff and starts independent review.
    Freeze prototype.py at measured SHA256 5dea8551293b1b8cc35ee3ad2c88c6dc7644343593a6ebcf7b91d8b1907feb1e.
    Final findings.md is complete; no further timing or code changes are planned in this tranche.
  EVIDENCE:
  - artifacts/override_emission_prototype_20260924/results.json
  - artifacts/override_emission_prototype_20260924/findings.md
  IMPACT: Lead review qualifies the exact measured implementation; prose can incorporate its result.
  NEXT: Consume the lead's independent parity/restoration result and leave the task in review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T11:00:31Z
  TYPE: MEASURE
  CLAIM: OEP-014 accepts discovery and reports independent candidate qualification: ten unchanged
    many-only input/error/manifest/eager-branch tests pass in 0.20 seconds. Ten installed executor
    bodies, keyword defaults and namespaces restore correctly. Measured and reviewed SHA256 match.
    Lead's joint proposal includes the measured public gains and explicit unsupported boundaries.
  EVIDENCE:
  - artifacts/override_execution_lead_20260924/prototype_review.json:1-6
  - artifacts/override_execution_lead_20260924/prototype_regressions.log:1-2
  - artifacts/override_execution_lead_20260924/joint_proposal.md
  IMPACT: This discovery tranche is complete and review-ready. No further experiments or production
    work proceed under this assignment; the owner decides the next implementation boundary.
  NEXT: Acknowledge OEP-014 with final findings and leave the task in review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Read artifacts/override_emission_prototype_20260924/findings.md and results.json.
Final positional layout gives public original-override gains 1.64x/2.26x/1.91x/4.68x for
shallow/wide/diamond/deep. The deep graph retains 511 constructors and reaches ~95% normal throughput.
Direct-keyword-call control and its exact generator are retained separately. OEP-012 releases the timing slot.
Lead's ten independent candidate tests pass with exact-hash and restoration checks. Joint proposal
is delivered. No production edits; this task remains in review for the owner decision.
