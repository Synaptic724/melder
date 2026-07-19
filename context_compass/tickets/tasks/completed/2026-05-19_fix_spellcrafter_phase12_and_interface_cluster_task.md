# Task: fix spellcrafter phase12 and interface cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-19-fix-spellcrafter-phase12-and-interface-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T14:28:07Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current mixed mypy cluster spanning `phase12_overrides_executor.py`,
`spell_crafter.py`, `scan.py`, `imutationresearch.py`, and `iconduit.py`
while keeping interface changes truthful and staying bounded to the reported
error set.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded mixed mypy cluster across the
  SpellCrafter executor/runtime layer plus two public interfaces.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `src/melder/aether/spellbook/spell_crafter/spell_crafter.py`
  - `src/melder\aether\spellbook\bind\scan.py`
  - `src/melder\utilities\interfaces\imutationresearch.py`
  - `src/melder\utilities\interfaces\iconduit.py`
  - directly implicated support interfaces only if truthful contract evidence
    requires them
- DEPENDENCIES:
  - current Phase 12 override execution contract
  - current SpellCrafter owner/interface contract
  - current Conduit and MutationResearch public protocol contract
  - no shims, no fake surfaces, no unrelated redesign
  - raise to Mark directly if the contract becomes ambiguous or the lane needs
    to split
- EXIT_GATE:
  - the targeted reported errors in these files are gone
  - any interface changes remain truthful and bounded
  - focused validation confirms the lane
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the mixed cluster proves to
  contain more than one materially different contract decision

## Scope Boundaries
- In scope:
  - local Phase 12 optionality / return narrowing
  - local SpellCrafter return and mapping narrowing
  - scan permissions-argument contract alignment
  - missing parameter annotations in `imutationresearch.py` and `iconduit.py`
  - `INexus` name resolution in `iconduit.py` if that is the real seam
- Out of scope:
  - unrelated repo-wide mypy debt
  - broader MutationResearch or Conduit redesign

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected this exact mixed cluster as the next
  active lane.

## Steps / Checklist
- [ ] read the exact failing slices in the five reported files
- [ ] classify local optionality debt versus stale public contract drift
- [ ] split the lane only if the evidence shows a real contract boundary split
- [ ] patch the bounded file/interface fixes
- [ ] rerun focused mypy on the reported files
- [ ] rerun directly implicated unit tests when behavior-sensitive files move
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded SpellCrafter/Phase12/interface typing fix

## Files / Paths Impacted
- `src/melder/aether/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/spellbook/spell_crafter/spell_crafter.py`
- `src/melder\aether\spellbook\bind\scan.py`
- `src/melder\utilities\interfaces\imutationresearch.py`
- `src/melder\utilities\interfaces\iconduit.py`
- only if required by the truthful fix:
  - directly implicated support interfaces

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary <reported files>`

## Risks / Rollback Notes
- Medium risk. The cluster mixes local optionality with interface-level typing,
  so the main danger is widening a public contract in the wrong direction or
  letting the lane sprawl.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- DATETIME: 2026-05-19T14:28:07Z
  TYPE: FACT
  CLAIM: The next active lane is the mixed SpellCrafter/Phase12/interface mypy
    cluster. The first step is exact source-slice reading because the report
    mixes executor optionality, SpellCrafter returns, scan contract mismatch,
    and two public-interface annotation/name-definition buckets.
  EVIDENCE:
  - user_error_report: `phase12_overrides_executor.py`
  - user_error_report: `spell_crafter.py`
  - user_error_report: `scan.py`
  - user_error_report: `imutationresearch.py`
  - user_error_report: `iconduit.py`
  IMPACT: The lane may still stay bounded, but I need source evidence before
    deciding whether to split it.
  NEXT: read the exact failing slices in the five reported files and classify
    local debt versus public contract drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:28:07Z
  TYPE: FACT
  CLAIM: The mixed cluster stays bounded. `phase12_overrides_executor.py` is
    local optionality and `Any` narrowing around the execution-plan fallback,
    source compilation, and path-registry metadata helper. `spell_crafter.py`
    is mostly local too: two required spellbook returns, two `pickle.dumps`
    bytes returns, one overly concrete `Dict[...]` signature that should accept
    the already-published `IInjectionSpec` mapping, and one dependency-key
    return that needs a local tuple annotation. The interface bucket is real in
    two places: `ISpellbook.bind(...)` is too narrow on `permissions` for the
    `scan.py` caller, and `IMutationResearch` / `IConduit` still have missing
    parameter annotations plus one stale private `_nexus` name on the conduit
    protocol.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:372-409
  - src/melder/aether/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:628-689
  - src/melder/aether/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2558-2635
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:298-325
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1443-1463
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:2138-2165
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:2938-2955
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3540-3568
  - src/melder/aether/spellbook/bind/scan.py:268-276
  - src/melder/utilities/interfaces/ispellbook.py:125-160
  - src/melder/utilities/interfaces/imutationresearch.py:50-102
  - src/melder/mutation_research/mutation_research.py:377-428
  - src/melder/mutation_research/mutation_research.py:515-590
  - src/melder/utilities/interfaces/iconduit.py:1-40
  - src/melder/utilities/interfaces/iconduit.py:145-175
  - src/melder/utilities/interfaces/iconduit.py:647-660
  - src/melder/utilities/interfaces/iconduit.py:1362-1550
  IMPACT: I can patch this lane in one bounded pass without splitting it further.
  NEXT: patch the local Phase12/SpellCrafter narrowings plus the narrow
    `ISpellbook`, `IMutationResearch`, and `IConduit` interface fixes, then run
    focused mypy and the directly implicated unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:28:07Z
  TYPE: FACT
  CLAIM: The `spell._spellbook` optionality looks fake in the live contract.
    `Spell.__init__` already dereferences `self._spellbook` immediately to seed
    `_spell_system_states`, `Bind` always passes a real Spellbook, and the
    direct `Spell(...)` test constructions in the current unit tree already
    provide spellbook stubs. That makes the two `SpellCrafter` spellbook helper
    wrappers pointless overhead rather than meaningful abstraction.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:252-384
  - src/melder\aether\spellbook\bind\bind.py:321-334
  - src/melder\utilities\interfaces\ispell.py:95-100
  - src/melder\aether\spellbook\spell_crafter\spell_crafter.py:255-328
  - tests/unit/melder/spellbook/test_spell.py:72-209
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py:25-36
  IMPACT: We can remove the fake optional spellbook contract and the dead
    helper wrappers in the same bounded lane without widening runtime behavior.
  NEXT: make `Spell._spellbook` required in the runtime and interface, inline
    the pointless SpellCrafter spellbook unwrap helpers, then rerun focused
    mypy and the existing SpellCrafter/bind tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded mixed mypy lane for Phase 12 overrides, SpellCrafter, Scan,
MutationResearch interface, and Conduit interface.
