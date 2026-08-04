# Task: replace fake surface protocols with real interfaces

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-replace-fake-surface-protocols-with-real-interfaces
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T12:58:52Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Remove the fake "surface" protocols and narrow file-local protocol shims that
were introduced instead of using the real shared interface boundaries. Replace
them with the truthful shared protocols that already exist or add the missing
shared protocol in the interface package when the boundary is real and absent.

## Ticket Contract
- ENTRY_GATE: user explicitly requested removal of the fake surface protocols
  and replacement with the real protocol boundaries
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/ispell.py`
  - `src/melder/utilities/interfaces/icreations.py`
  - `src/melder/spellbook/spell.py`
  - `src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py`
  - directly implicated shared interface files only if required by truthful replacement
- DEPENDENCIES:
  - existing spell/conduit/rift/shared-interface graph must remain truthful
- EXIT_GATE: the targeted fake surface protocols are removed or replaced with
  real shared protocol boundaries, with no new local shim protocols invented
- FAILURE_ESCALATION: raise `BLOCKER` if one targeted surface does not have an
  existing truthful protocol and the correct ownership boundary is ambiguous

## Scope Boundaries
- In scope:
  - fake shared "surface" protocols in the interfaces package
  - file-local protocol shims that should point at real shared interfaces
  - truthful shared protocol additions when the boundary is real and missing
- Out of scope:
  - unrelated repo-wide interface redesign
  - unrelated mypy cleanup outside the touched dependency ring

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user explicitly requested cleanup of the fake surface
  protocols and replacement with real interfaces

## Steps / Checklist
- [ ] inspect each fake surface protocol against the concrete class usage and existing interfaces
- [ ] decide which surfaces should be replaced by existing interfaces versus new shared protocols
- [ ] patch the shared interface files and dependent concrete/type-user files
- [ ] rerun focused validation on the touched ring
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- fake surface protocols removed or replaced with real shared protocol boundaries

## Files / Paths Impacted
- `src/melder/utilities/interfaces/ispell.py`
- `src/melder/utilities/interfaces/icreations.py`
- `src/melder/spellbook/spell.py`
- `src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py`
- directly implicated shared interface files only if needed by truthful replacement

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\component\melder\aether\conduit`

## Risks / Rollback Notes
- Medium risk. These fake surfaces are likely masking real interface-cycle or
  ownership problems, so a truthful fix may need small shared interface additions.

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
- DATETIME: 2026-05-18T12:58:52Z
  TYPE: PLAN
  CLAIM: The new lane is bounded to the fake surface protocols and the files
    that introduced or consume them. The first pass will inventory each fake
    surface against the concrete class methods and the existing interface tree
    before any replacement is attempted.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispell.py:31-178
  - src/melder/utilities/interfaces/icreations.py:8-43
  - src/melder/spellbook/spell.py:37-120
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:22-73
  IMPACT: This keeps the cleanup on real ownership and call surfaces instead of
    inventing another protocol layer.
  NEXT: inspect the existing interface files (`iaether`, `ispellbook`,
  `ispellsystemstates`, `icreations`, `ispellspace`, `iframeviewer`, `irift`)
  and compare them to the fake surface usage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:04:35Z
  TYPE: FACT
  CLAIM: The spell-side fake surfaces split into two categories. Some are
    pure duplication of real shared interfaces that already exist
    (`IAethericFrameConfiguration`, `ISpellbook`, `ISpellSystemStates`,
    `IRift`), while others exist because the current interface graph has hard
    cycles or missing first-class protocols (`CreationContext`, `SpellCrafter`,
    `ISpellSpace` owner, `FrameViewer` multiframe host).
  EVIDENCE:
  - src/melder/utilities/interfaces/ispell.py:31-178
  - src/melder/utilities/interfaces/iaethericframeconfiguration.py:1-147
  - src/melder/utilities/interfaces/ispellbook.py:1-400
  - src/melder/utilities/interfaces/ispellsystemstates.py:1-260
  - src/melder/utilities/interfaces/irift.py:1-215
  - src/melder/utilities/interfaces/icreations.py:8-43
  - src/melder/utilities/interfaces/ispellspace.py:1-78
  - src/melder/utilities/interfaces/iconduit.py:1-380
  - src/melder/spellbook/spell.py:37-120
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-220
  - src/melder/spellbook/spell_crafter/spell_crafter.py:1-260
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:22-73
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:150-1666
  IMPACT: The truthful fix is not "delete everything and widen to Any". It is:
    replace duplicate fake surfaces with the real existing interfaces, and
    create proper shared first-class protocols for the cycle-break cases rather
    than leaving nested or file-local shim protocols.
  NEXT: patch the shared interface tree by introducing proper first-class
    protocols for `CreationContext`, `SpellCrafter`, `SpellSpace` ownership,
    and the multiframe viewer host; then strip the fake surfaces from
    `ispell.py`, `icreations.py`, `spell.py`, and `view_multiframe.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T15:20:31Z
  TYPE: FACT
  CLAIM: The viewer-side local surfaces in `view_multiframe.py` are pure shim
    duplication now. `IRift` already exposes the frame-list methods the local
    `_RiftViewerSurface` repeats, and the only real gap is that `IFrameViewer`
    does not yet declare the borrowed private helper surface that
    `ViewMultiFrame` already calls on the concrete `FrameViewer`.
  EVIDENCE:
  - src/melder\aether\nexus\rift\frame_viewer\view_multiframe.py:22-87
  - src/melder\utilities\interfaces\irift.py:66-66
  - src/melder\utilities\interfaces\irift.py:291-300
  - src/melder\utilities\interfaces\iframeviewer.py:1-24
  - src/melder\aether\nexus\rift\frame_viewer\frame_viewer.py:1534-1666
  - src/melder\aether\nexus\rift\frame_viewer\frame_viewer.py:3955-4038
  IMPACT: This can be fixed cleanly by extending the real `IFrameViewer`
    protocol and deleting the local shim protocols instead of inventing a new
    surface type.
  NEXT: extend `IFrameViewer` with the borrowed helper surface and remove the
    local protocols from `view_multiframe.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded surface-protocol cleanup lane opened for the fake interface shims in
`ispell.py`, `icreations.py`, `spell.py`, and `view_multiframe.py`.
