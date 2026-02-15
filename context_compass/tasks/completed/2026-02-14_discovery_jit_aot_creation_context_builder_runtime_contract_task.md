# Task: Discovery - JIT/AOT CreationContext Builder Runtime Contract



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

## Objective
Define how CreationContext builder/factory contracts must change (or remain
strict) when late-phase artifacts are intentionally deferred in split mode.

## Scope Boundaries
- In scope:
- Builder preconditions, factory get-or-build behavior, spell switch semantics, meld call path usage.
- Out of scope:
- Implementing the runtime behavior change.

## Steps / Checklist
- [x] Document builder preconditions that currently require crafter artifacts.
- [x] Document factory and spell get-or-build ownership/ready-state behavior.
- [x] Document meld runtime points that consume spell-owned creation contexts.
- [x] Produce contract options: strict fail-fast, optional deferred build, or hybrid.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One contract matrix for builder/factory behavior under split mode.
- One recommendation with explicit compatibility impact.

## Contract Options Matrix (2026-02-15)
| Option | Builder/Factory Contract | Runtime Resolution Contract | Compatibility Impact | Risk |
|---|---|---|---|---|
| `strict_fail_fast` | Keep current builder precondition: non-existing creations require crafter artifacts before `CreationContext` build. Keep switch-based get-or-build semantics unchanged. | Caller must guarantee all required resolution artifacts exist before first context build. | Highest backward compatibility; no builder/factory behavior change. | Split mode ergonomics remain weak; likely forces eager resolution before first runtime use. |
| `deferred_optional_builder` | Make builder deferral-aware by allowing partial contexts without crafter artifacts; defer route/executor population until later. | Runtime must mutate/refresh context internals after deferred phases complete. | Largest contract shift; likely touches context execution semantics and lifecycle invariants. | High regression risk due to partial-context states and runtime mutation complexity. |
| `hybrid_rule_bound` (recommended) | Keep builder/factory strict contracts and switch ownership unchanged. Add explicit pre-build runtime resolution gate when spell indicates deferred resolution is required. | On first runtime access, run deferred resolution phases to materialize artifacts, then build context once using existing strict builder. If resolution remains invalid, fail fast. | Preserves current builder/factory internals while enabling split mode via orchestration gate. | Requires clear `resolution_required` lifecycle and one deterministic runtime gate point. |

### Recommendation
Use `hybrid_rule_bound`. The code paths already treat creation-context readiness as switch + crafter-artifact dependent, and meld execution reads compiled callables from the built context. Preserving strict builder/factory internals while introducing a runtime resolution gate before first build yields lower regression risk than partial-context mutation.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
- `src/melder/spellbook/spell.py`
- `src/melder/aether/conduit/meld/meld.py`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "Cannot build CreationContext|_get_or_build_creation_context|get_or_build_for_spell" src/melder/aether/conduit/meld/creation_context src/melder/spellbook/spell.py`
  - `rg -n "_creation_context_switch|_get_or_build_creation_context" src/melder/aether/conduit/meld/meld.py`

## Risks / Rollback Notes
- Risk: Weak contract mapping could leak hidden assumptions into runtime implementation.
- Rollback: discovery-only task; no contract mutation occurs here.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Builder/factory/spell/meld contracts currently assume first context build happens only after crafter-backed execution artifacts exist, while runtime resolution path can re-run conduit-scoped phases before creation-context access.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-86, src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:97-118, src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:173-193, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264, src/melder/spellbook/spell.py:469-497, src/melder/aether/conduit/meld/meld.py:345-373, src/melder/aether/conduit/meld/meld.py:569-618, src/melder/spellbook/spellbook.py:3152-3182, src/melder/spellbook/spellbook_creation_system.py:1374-1433
  IMPACT: Split-mode support should prioritize orchestration changes at runtime gate points, not deep builder/factory contract rewrites.
  NEXT: Record decision recommendation for `hybrid_rule_bound` and request user direction for implementation story/task breakdown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Recommend `hybrid_rule_bound`: keep strict builder/factory contracts and add a pre-build runtime resolution gate when `resolution_required` is true.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:31-44, src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-118, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264, src/melder/aether/conduit/meld/meld.py:569-618
  IMPACT: Preserves compatibility and minimizes low-level churn while still supporting deferred-resolution mode through controlled runtime gating.
  NEXT: Surface recommendation to user and, on approval, generate implementation tasks for runtime gate insertion + `resolution_required` lifecycle transitions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Task is activated as the next epic step after phase-order parity patch validation; deliverable is a decision-ready builder/factory contract options matrix for deferred-runtime mode.
  EVIDENCE: context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-110, context_compass/epics/2026-02-14_jit_aot_phase_split_configuration_epic.md:132-143
  IMPACT: Discovery flow resumes with concrete runtime-contract decision shaping, not code implementation.
  NEXT: Extract builder/factory/meld contract facts from source and produce strict vs deferred vs hybrid options with recommendation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Builder currently fails for non-existing creations when crafter artifacts are absent, while runtime consumers rely on spell/factory switch-based get-or-build behavior.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-86, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264, src/melder/spellbook/spell.py:469-497, src/melder/aether/conduit/meld/meld.py:345-373
  IMPACT: Split mode needs an explicit decision on whether builder preconditions remain strict or become deferral-aware.
  NEXT: Enumerate compatible design options and score tradeoffs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Discovery matrix and recommendation are complete. Next step is user decision on
`hybrid_rule_bound`, then implementation task breakdown for runtime gate + spell
`resolution_required` lifecycle behavior.


