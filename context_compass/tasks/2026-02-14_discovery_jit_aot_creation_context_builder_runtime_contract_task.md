# Task: Discovery - JIT/AOT CreationContext Builder Runtime Contract

## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define how CreationContext builder/factory contracts must change (or remain
strict) when late-phase artifacts are intentionally deferred in split mode.

## Scope Boundaries
- In scope:
- Builder preconditions, factory get-or-build behavior, spell switch semantics, meld call path usage.
- Out of scope:
- Implementing the runtime behavior change.

## Steps / Checklist
- [ ] Document builder preconditions that currently require crafter artifacts.
- [ ] Document factory and spell get-or-build ownership/ready-state behavior.
- [ ] Document meld runtime points that consume spell-owned creation contexts.
- [ ] Produce contract options: strict fail-fast, optional deferred build, or hybrid.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One contract matrix for builder/factory behavior under split mode.
- One recommendation with explicit compatibility impact.

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
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Builder currently fails for non-existing creations when crafter artifacts are absent, while runtime consumers rely on spell/factory switch-based get-or-build behavior.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-86, src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264, src/melder/spellbook/spell.py:469-497, src/melder/aether/conduit/meld/meld.py:345-373
  IMPACT: Split mode needs an explicit decision on whether builder preconditions remain strict or become deferral-aware.
  NEXT: Enumerate compatible design options and score tradeoffs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task is ready with concrete contract anchors. Next step is option matrix output
for builder/factory behavior in deferred-resolution mode.
