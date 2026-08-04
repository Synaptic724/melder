# Task: expand protocol crafter with AST source generation
- Completed: 2026-05-17T16:11:00Z
- Summary: Closed after the hardened AST-backed `ProtocolCrafter` slice was
  accepted for handoff. The bounded lane stays closed at the utility/test
  surface; production interface adoption remains a separate future pass.

## Metadata
- Task ID: TASK-2026-05-17-expand-protocol-crafter-ast-source-generation
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_0
- Priority: p1
- Created: 2026-05-17T15:29:24Z
- Updated: 2026-05-17T16:11:00Z

## Objective
Add AST-backed ProtocolCrafter workflows that can generate a complete protocol
module from a source file + class name, plus a joined-protocol workflow that
intersects matching attributes and methods across multiple classes.

## Ticket Contract
- ENTRY_GATE: active board row routes to this task and the current utility/test
  surface is evidenced in notes before implementation
- EXECUTION_BOUNDARY: `src/melder/utilities/ai_native_support_tools/protocol_crafter.py`
  and `tests/unit/melder/utilities/test_protocol_crafter.py`
- DEPENDENCIES: existing ProtocolCrafter behavior, current tests, and the user
  requirement that the result be a fully formed protocol file while still
  remaining compatible with `TYPE_CHECKING`-first downstream typing
- EXIT_GATE: new AST-backed single-class and multi-class generation paths exist,
  targeted unit tests cover them, and validation status is recorded truthfully
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if AST output cannot preserve the
  repo's typing/docstring constraints without making interface-shape guesses

## Scope Boundaries
- In scope:
  - add source-file/class-name entrypoints
  - build full protocol-module output with imports using AST assembly
  - add joined-protocol generation across multiple class targets
  - add focused unit tests for both new paths
- Out of scope:
  - adopting generated protocols into production interface files
  - broad naming-convention cleanup for existing interfaces
  - fixing unrelated mypy backlog groups

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user accepted the hardened AST-backed `ProtocolCrafter`
  utility slice for closure and handoff

## Steps / Checklist
- [x] inspect current ProtocolCrafter generation boundaries and decide what
      source-model data must come from AST rather than runtime reflection
- [x] implement AST-backed full-module generation for one class target
- [x] implement joined-protocol generation across multiple class targets
- [x] add focused unit tests covering single-class and joined-protocol output
- [x] run targeted pytest coverage for the touched utility
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- expanded `ProtocolCrafter` public API for AST-backed protocol-module output
- focused unit tests proving generated output shape

## Files / Paths Impacted
- `src/melder/utilities/ai_native_support_tools/protocol_crafter.py`
- `tests/unit/melder/utilities/test_protocol_crafter.py`

## Validation
- Ran: `python -m pytest -q tests/unit/melder/utilities/test_protocol_crafter.py`
- Result: `9 passed`
- Warnings:
  - import-time nogil warning from `src/melder/__init__.py`
  - pytest cache warning because `.pytest_cache` was not writable in this shell

## Risks / Rollback Notes
- Generated protocol shape may over-mirror private/internal members unless AST
  filtering is tightened deliberately.
- Joined-protocol intersection can drift into unsafe interface narrowing if we
  treat same-named members as compatible without signature comparison.
- If the AST path proves too lossy for current docstring/type fidelity, revert
  to the current runtime-only generator rather than landing a half-typed tool.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-05-17T15:29:24Z
  TYPE: FACT
  CLAIM: The current ProtocolCrafter supports runtime-reflection generation
    from a class or object plus append/remove helpers for existing interface
    files, but it does not currently offer source-file/class-name generation,
    full protocol-module assembly, or joined multi-class protocol generation.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:12-220
  - tests/unit/melder/utilities/test_protocol_crafter.py:46-147
  IMPACT: The existing utility is useful as a protocol-block scaffold, but it
    cannot yet produce the fuller interface-generation workflow the user asked
    for.
  NEXT: extend ProtocolCrafter with AST-backed source parsing and add tests for
    single-class and joined-protocol output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T15:46:51Z
  TYPE: FACT
  CLAIM: `ProtocolCrafter` now supports AST-backed source-file/class-name
    protocol-module generation, directory-based file emission with a
    tool-chosen interface filename, and joined-protocol generation across
    multiple class targets.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:195-334
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:1147-1835
  IMPACT: The utility is now strong enough to generate real interface modules
    from source shapes instead of only producing runtime-reflection stubs.
  NEXT: review whether `SpellBinder` should be the first production interface
    generated from this tool.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T15:46:51Z
  TYPE: MEASURE
  CLAIM: The focused `ProtocolCrafter` unit ring passed after adding coverage
    for AST-backed single-class generation, real `SpellBinder` generation, and
    joined-protocol generation.
  EVIDENCE:
  - tests/unit/melder/utilities/test_protocol_crafter.py:208-373
  IMPACT: The new behavior is covered by targeted tests rather than only manual
    spot checks.
  NEXT: return the implementation for review and decide whether to use it on
    the first production interface target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T15:59:44Z
  TYPE: FACT
  CLAIM: The enhancement pass tightened the generated module shape further:
    protocol modules now emit only the `typing` imports they actually use,
    source mode harvests public instance attributes assigned in `__init__`, and
    the custom renderer now keeps blank lines, docstring indentation, and
    parameter-default spacing stable instead of relying on raw `ast.unparse`
    formatting.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:1446-1549
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:1927-2185
  IMPACT: The generated protocol files are cleaner to inspect and closer to
    production-ready interface artifacts instead of just technically valid AST
    dumps.
  NEXT: inspect the regenerated `SpellBinder` output and decide whether to use
    the utility on the first real production interface target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:11:00Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted the hardened AST-backed `ProtocolCrafter`
    slice for closure and handoff. This ticket closes at the utility/test
    boundary without adopting the generated protocol output into production
    interface files.
  EVIDENCE:
  - user_instruction: "the protocol tickets are done you can close and hand
    those in"
  IMPACT: The task can move to `completed`, the active board row can be
    removed, and any future production interface adoption should start from a
    separate ticket instead of reopening this bounded tool lane.
  NEXT: move the task to `tickets/tasks/completed/` and add one closure anchor
    row on `attention_board.md`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Closed after the user accepted the hardened AST-backed `ProtocolCrafter` slice.
The landed boundary remains the utility/test surface only: source-driven
protocol-module generation, joined-protocol generation, and cleaner rendered
output. Production interface adoption, including any real `SpellBinder`
interface-file rollout, remains a separate future lane.
