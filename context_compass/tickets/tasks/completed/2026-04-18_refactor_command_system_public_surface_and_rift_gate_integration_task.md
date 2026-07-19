# Task: Refactor Command System Public Surface And Rift Gate Integration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-refactor-command-system-public-surface-and-rift-gate-integration
- Story: STORY-2026-04-18-command-surface-cleanup-and-rift-gate-entry
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T19:42:55Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Clean up the live command surface so top-level command methods use explicit
RiftGate entry and real policy checks instead of magic wrapping and fake no-op seams.

## Ticket Contract
- ENTRY_GATE: the command audit recorded concrete evidence for the cleanup and
  the user approved implementation.
- EXECUTION_BOUNDARY: `CommandSystem`, `StaticCommandSystem`, and directly
  affected tests only.
- DEPENDENCIES:
  - tickets/stories/2026-04-18_command_surface_cleanup_and_rift_gate_entry_story.md
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/command_system/static_command_system.py
  - tests/unit/melder/aether/test_command_system_direct.py
  - tests/unit/melder/aether/test_static_command_system_direct.py
- EXIT_GATE: the magic wrapper and `_command_memory_call_depth` are gone,
  public-to-public chaining is removed where needed, and the focused command
  validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the slice requires widening
  into workstation or viewer gate work to stay correct.

## Scope Boundaries
- In scope:
  - command wrapper removal
  - explicit top-level command gate entry
  - command private-helper cleanup
  - fake policy-hook cleanup
  - focused tests
- Out of scope:
  - workstation gate integration
  - broad viewer gate integration

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested implementation after the audit proved
  the current command wrapper is structural sludge.

## Steps / Checklist
- [x] Remove the `__getattribute__` command wrapper and `_command_memory_call_depth`.
- [x] Refactor public-to-public command chaining into private helpers where required for top-level gating.
- [x] Replace fake no-op policy seams with real checks/predicates.
- [x] Port the focused direct command tests.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- explicit top-level command RiftGate integration
- cleaner command/private helper split
- real policy checks instead of empty hooks

## Files / Paths Impacted
- src/melder/aether/nexus/rift/command_system/command_system.py
- src/melder/aether/nexus/rift/command_system/static_command_system.py
- tests/unit/melder/aether/test_command_system_direct.py
- tests/unit/melder/aether/test_static_command_system_direct.py

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/aether/nexus/rift/command_system/capability_command_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_nexus.py`
- `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_nexus.py`
- Result: `121 passed`

## Risks / Rollback Notes
- Risk: hidden method chaining may survive in corners and still imply nested entry.
- Rollback: none planned; this is explicitly a no-compat cleanup slice.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The remaining hook-style assertion leftovers were removed too. The
    base command surface now uses concrete class-level deny sets plus concrete
    assertion methods, and the static room expresses its denials through those
    explicit sets instead of empty/no-op hook bodies.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:2248-2376
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:1-56
  IMPACT: The command family no longer carries the dead policy-hook leftovers
    the user kept pointing out.
  NEXT: hold for review unless the next lane is workstation gate cleanup.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The last fake policy predicates are now gone. The base command surface
    uses direct concrete assertion methods for permissive policy, and the
    static room keeps explicit deny assertions where mode-specific failures
    need real messages.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:2248-2368
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:25-80
  IMPACT: The command family no longer carries the dead `*_allows_*` seam
    garbage the user flagged.
  NEXT: hold for review unless the next lane is workstation gate integration.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The explicit command-action path still emits `IRiftMemory` records
    through the room-owned `RiftMemorySystem`; memory emission was not lost
    when the magic wrapper was removed.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:1718-1839
  - tests/unit/melder/aether/test_command_system_direct.py:386-430
  IMPACT: Command memory reporting remains wired through `RiftSpace.memory_system`
    while the gate entry logic is now explicit.
  NEXT: keep that path as the command-memory seam if/when workstation/viewer
    follow-ons are implemented.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The touched command/static-command methods now carry deeper contract
    docstrings instead of the earlier shallow one-liners.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:822-1158
  - src/melder/aether/nexus/rift/command_system/command_system.py:1500-1716
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:1-260
  IMPACT: The command cleanup now matches the Synaptic Python documentation bar
    more honestly.
  NEXT: hold for review unless the user wants more command/workstation/viewer
    cleanup in the next slice.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The command surface now uses explicit top-level command-action entry
    instead of `__getattribute__` wrapping. The magic wrapper, call-depth
    state, and the capability no-op override are gone; the shared base now uses
    real policy checks and the static surface keeps explicit deny methods where
    the message needs to remain mode-specific.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:1-2200
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:1-560
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:1-19
  IMPACT: The command surface is now understandable without magic wrapper state.
  NEXT: hold for review before widening into workstation/viewer gate work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: MEASURE
  CLAIM: The focused command cleanup ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/aether/nexus/rift/command_system/capability_command_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_nexus.py` -> 121 passed
  IMPACT: The bounded command-only slice is stable enough to review.
  NEXT: wait for user acceptance or the next bounded lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T19:42:55Z
  TYPE: FACT
  CLAIM: The current command wrapper combines two unrelated concerns
    (top-level memory emission and top-level RiftGate entry) and relies on
    object-wide call-depth state because the public command methods chain into
    other public command methods heavily.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:133-1658
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:124-154
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:436-451
  IMPACT: The proper fix is to clean the command surface itself, not extend the
    current wrapper pattern.
  NEXT: implement the command cleanup and explicit top-level gate entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task refactors the command surface before any workstation/viewer gate
work is attempted.