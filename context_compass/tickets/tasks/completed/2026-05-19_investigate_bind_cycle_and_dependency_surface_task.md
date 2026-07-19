# Task: Investigate Bind Cycle And Dependency Surface
- Completed: 2026-05-20T08:58:57Z
- Summary: Closed after proving the real bind seam was not a weakref swap but the factory/import direction, which led directly to the later top-level `SpellBinder` cut.

## Metadata
- Task ID: TASK-2026-05-19-investigate-bind-cycle-and-dependency-surface
- Story: none
- Epic: none
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-19T21:49:16Z
- Updated: 2026-05-20T08:58:57Z

## Objective
Determine the real cycle and dependency surface around `Bind` so the next cut
breaks one true ownership/import knot without widening into a fake cleanup
sweep.

## Ticket Contract
- ENTRY_GATE: this task is routed on `attention_board.md` and the first
  evidence-backed note is recorded before broader discovery continues.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/bind/bind.py`
  - immediate runtime seams that `Bind` directly owns or constructs
  - direct call sites in `Spellbook` / `Scan` / `Spell`
- DEPENDENCIES:
  - `src/melder/aether/spellbook/bind/bind.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/spellbook/bind/scan.py`
  - completed SpellExaminer rebuild tickets for prior context only
- EXIT_GATE: the current `Bind` cycle surface is explicit enough to stage the
  first bounded implementation slice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the apparent `Bind` cycle is
  actually rooted in wider Spellbook/SpellExaminer runtime ownership.

## Scope Boundaries
- In scope:
  - imports and stored dependencies directly owned by `Bind`
  - construction flows from `Bind` into `Spell`, `SpellIndex`, and
    `SpellExaminer`
  - nearby runtime seams that may force the cycle to stay alive
- Out of scope:
  - broad Spellbook refactors
  - crystallizer/provenance redesign
  - implementation outside the first true bounded cut

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to focus next on `Bind` as the
  next cycle-breaking target.

## Steps / Checklist
- [ ] Read `bind.py` in bounded chunks and map its owned dependencies.
- [ ] Read the immediate `Spellbook`, `Spell`, and `Scan` seams that call or
      are constructed by `Bind`.
- [ ] Identify the first truthful cycle-breaking cut for `Bind`.
- [ ] Summarize the implementation boundary before editing.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed map of the current `Bind` dependency surface
- recommendation for the first bounded cycle-breaking cut

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-19_investigate_bind_cycle_and_dependency_surface_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q <focused bind ring once the cut is staged>`

## Risks / Rollback Notes
- Risk: treating an old SpellExaminer lane as current truth and cutting the
  wrong seam.
  Rollback: re-ground the next step on direct source reads only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T21:49:16Z
  TYPE: PLAN
  CLAIM: This lane exists to map the current `Bind` dependency surface before
    touching code. The immediate goal is to isolate one real cycle or
    over-coupled ownership seam instead of assuming the old SpellExaminer lane
    still describes current runtime truth.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1-1
  - src/melder/aether/spellbook/spellbook.py:1-1
  - codex/context_compass/tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md:494-499
  IMPACT: The next read tranche should start from the source files, not the
    historical ticket conclusions, before staging any bind refactor.
  NEXT: read `bind.py` in bounded chunks, then inspect the direct Spellbook and
    Spell seams it owns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-19T21:49:16Z
  TYPE: FACT
  CLAIM: The obvious `Spellbook <-> Bind` concrete cycle is weaker than it
    sounds. `Spellbook` owns one concrete `Bind` and delegates binding and scan
    work into it, but `Bind` only stores an `ISpellbook` reference and `Scan`
    is only a metadata-to-bind adapter. The denser knot is inside `Bind`
    itself: it owns a concrete `SpellExaminer`, imports concrete profile
    classes, fingerprints those profiles directly, and constructs concrete
    `SpellIndex` and `Spell` objects in one pipeline.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:231-232
  - src/melder/aether/spellbook/spellbook.py:2794-2894
  - src/melder/aether/spellbook/spellbook.py:3002-3030
  - src/melder/aether/spellbook/bind/scan.py:184-281
  - src/melder/aether/spellbook/bind/bind.py:8-29
  - src/melder/aether/spellbook/bind/bind.py:60-82
  - src/melder/aether/spellbook/bind/bind.py:258-337
  IMPACT: The first truthful cycle-breaking cut is more likely to be inside the
    concrete profile/construction pipeline owned by `Bind`, not at the
    Spellbook delegation seam.
  NEXT: inspect the `Bind -> Spell -> profile` seam and isolate the smallest
    concrete dependency that can be reduced without redesigning the whole bind
    pipeline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-19T21:49:16Z
  TYPE: FACT
  CLAIM: Removing the stored `Spellbook` from `Bind` looks plausible because
    `Bind` only reads `self._spellbook` once, when it constructs the new
    `Spell`. The real catch is the `Spell` constructor contract: `Spell`
    requires `spellbook` at construction time and seeds spell-local runtime
    state from it immediately.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:62-80
  - src/melder/aether/spellbook/bind/bind.py:320-337
  - src/melder/aether/spellbook/spell.py:240-250
  - src/melder/aether/spellbook/spell.py:331-384
  IMPACT: The first viable cut is not "delete spellbook from Bind and do
    nothing else." The clean options are either:
    1) make `Spellbook` own final `Spell(...)` construction, or
    2) make `Bind` take `spellbook` only as a per-call constructor input
       instead of storing it as long-lived state.
  NEXT: inspect whether `Bind` can become a pure spell-construction planner or
    whether a smaller "no stored spellbook field" cut is the safer first step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T08:25:44Z
  TYPE: FACT
  CLAIM: `SpellBinder` does not weaken the `Spellbook` dependency in any
    meaningful way yet. It only reads the weakly held spellbook for liveness
    guards and then delegates `finalize()` straight back into
    `Spellbook.bind(...)`. That matters because `Spellbook.bind(...)` does far
    more than `Bind._bind_logic(...)`: transaction gating, Aether collision
    checks, lookup-key uniqueness, hook attachment, local registry insertion,
    version-cache warming, conjured-runtime stamping, and
    `SpellSystemStates` registration. Repointing `SpellBinder` from a weak
    `Spellbook` to a weak `Bind` would only be clean if `Bind` grew a new
    commit-level API that preserves all of those `Spellbook.bind(...)`
    semantics without duplicating them.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbinder.py:18-29
  - src/melder/aether/spellbook/spellbinder.py:96-170
  - src/melder/aether/spellbook/spellbinder.py:697-731
  - src/melder/aether/spellbook/spellbook.py:2100-2146
  - src/melder/aether/spellbook/spellbook.py:2893-2981
  - src/melder/aether/spellbook/bind/bind.py:58-77
  - src/melder/aether/spellbook/bind/bind.py:314-373
  IMPACT: Swapping the weakref target from `Spellbook` to `Bind` alone does
    not remove the real dependency surface. It either becomes a cosmetic import
    move or it forces `Bind` to absorb/forward the full `Spellbook.bind(...)`
    commit contract.
  NEXT: inspect whether the actual problem is import-direction only
    (`spellbook.py -> spellbinder.py`) or whether you want a real ownership cut
    where `Bind` becomes the commit surface for fluent binding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
New active lane for `Bind` cycle investigation. No source findings yet beyond
task setup; next step is the first bounded `bind.py` read.
