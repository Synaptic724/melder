# Task: investigate spell ownership and decomposition
- Completed: 2026-05-20T10:17:06Z
- Summary: Closed after mapping `Spell` as a hub object and proving that the first truthful decomposition slice should start with compiler foundation work rather than immediately removing `Spellbook` or live `SpellCrafter` behavior.

## Metadata
- Task ID: TASK-2026-05-20-investigate-spell-ownership-and-decomposition
- Story: none
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-20T09:32:43Z
- Updated: 2026-05-20T10:17:06Z

## Objective
Map the current `Spell` responsibility clusters and ownership seams so we can
stage a real decomposition cut that removes `Spellbook` and spell-crafter
machinery from `Spell` without guessing.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to switch focus to `Spell` and wants an
  investigation first because this is a hard refactor.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell.py`
  - direct collaborators that `Spell` owns or references for lifecycle,
    crafting, and creation-context behavior
  - adjacent interface/runtime seams only when needed to explain the current
    ownership picture
- DEPENDENCIES:
  - no production edits in this lane
  - no speculative redesign beyond source-backed responsibility clusters
- EXIT_GATE:
  - the real `Spell` responsibility clusters are explicit
  - the current `Spellbook` and spell-crafter ownership seams are explicit
  - the first bounded refactor cut is recommended
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the decomposition picture is
  still ambiguous after bounded source reads.

## Scope Boundaries
- In scope:
  - `Spell` fields and methods
  - where `Spell` still references `Spellbook`
  - where `Spell` owns or creates spell-crafter / creation-context machinery
  - whether creation context can remain while the machinery moves out
- Out of scope:
  - implementing the decomposition
  - broader spellbook or bind rewrites in this lane
  - unrelated conduit/cloud cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly chose `Spell` as the next hard
  refactor target and asked for investigation first.

## Steps / Checklist
- [ ] read `spell.py` in bounded chunks
- [ ] read the direct collaborator seams `Spell` owns or references
- [ ] group `Spell` behavior into responsibility clusters
- [ ] identify the first bounded decomposition cut
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- evidence-backed map of the current `Spell` ownership surface
- recommendation for the first bounded `Spell` decomposition cut

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-20_investigate_spell_ownership_and_decomposition_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "_spellbook|_crafter|_creation_context|_creation_context_factory|SpellCrafter|CreationContext" src/melder/aether/spellbook/spell.py`

## Risks / Rollback Notes
- Low risk because this lane is investigation only.

## Applicable Anti-Patterns
- [ ] No implementation disguised as investigation.
- [ ] No speculative ownership claims without direct file evidence.
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
- DATETIME: 2026-05-20T09:32:43Z
  TYPE: PLAN
  CLAIM: The user already named the likely fault lines: `Spell` still
    references `Spellbook`, still owns spell-crafter machinery, and may be
    allowed to keep creation-context state but not the machinery that builds
    it. This lane exists to prove that ownership map before any decomposition
    is proposed.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next read pass should stay on `spell.py` and its direct owned
    collaborators until the responsibility clusters are explicit.
  NEXT: size and read `spell.py`, then read the direct collaborator seams it
    owns or references for crafting and creation-context behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T09:37:28Z
  TYPE: FACT
  CLAIM: `Spell` is currently a hub object, not a thin record. It stores the
    owning `Spellbook`, stores frame-level spell-system state derived from that
    spellbook, owns the spell-owned `CreationContextFactory`, owns the cached
    `CreationContext`, lazily creates and owns `SpellCrafter`, and exposes a
    long phase-facade surface that just forwards compiler/validation work into
    that crafter. So the current object mixes bind-time metadata, runtime
    ownership state, runtime context publication, and compiler/phase
    orchestration in one class.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:330-390
  - src/melder/aether/spellbook/spell.py:619-691
  - src/melder/aether/spellbook/spell.py:758-783
  - src/melder/aether/spellbook/spell.py:1131-1626
  IMPACT: The first decomposition cut should not be framed as a single
    “remove Spellbook” move. The actual split points are:
    1) spellbook/state ownership,
    2) crafter ownership and phase façade,
    3) creation-context factory ownership.
  NEXT: read the direct collaborator contracts to see which of those seams can
    be cut first without dragging the rest with it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:41:17Z
  TYPE: FACT
  CLAIM: The hardest part of the decomposition is not that `Spell` itself
    reads `_spellbook` everywhere. Inside `Spell`, the direct spellbook use is
    tiny. The real coupling is structural:
    1) the `ISpell` protocol itself exposes `_spellbook`, `_crafter`,
       `_creation_context`, `_creation_context_factory`, and the whole
       phase-facade API as part of Spell’s contract, and
    2) `SpellCrafter` immediately grabs `spell._spellbook` and later reuses
       `self._spell._spellbook` all over the phase pipeline for validators,
       frame-name access, spell lookup pools, and phase wiring.
    So removing `Spellbook` or crafter ownership from `Spell` is really a
    `Spell` + `ISpell` + `SpellCrafter` contract cut, not just a field delete.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispell.py:102-140
  - src/melder/utilities/interfaces/ispell.py:393-424
  - src/melder/utilities/interfaces/ispell.py:457-764
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:259-265
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:300-351
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1160-1160
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1290-1290
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3175-3175
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3283-3283
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4225-4225
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4519-4519
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4638-4638
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4682-4682
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5250-5250
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5328-5328
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5604-5605
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5651-5652
  IMPACT: The first decomposition cut should probably target one cluster at a
    time:
    - either reduce `ISpell`/`Spell` exposure of crafter-facing phase methods,
    - or separate creation-context factory ownership from Spell before trying to
      remove spellbook entirely.
  NEXT: inspect the direct spellbook-side interactions with `Spell` and decide
    which cluster is the smallest truthful first cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:43:47Z
  TYPE: DECISION
  CLAIM: The first bounded `Spell` decomposition cut should be the
    creation-context machinery, not the spellbook field and not the whole
    crafter surface. Reason: the spellbook field on `Spell` is locally thin,
    but the crafter seam is broad and protocol-heavy. By contrast, the
    creation-context machinery is a smaller cluster:
    `Spell` owns `_creation_context_factory` and `_creation_context_switch`,
    `CreationContextFactory` directly mutates those spell internals, and `Meld`
    only relies on three spell-owned surfaces for hot-path context access:
    `_creation_context_switch`, `_creation_context`, and
    `_get_or_build_creation_context()`. If you are okay with `Spell` keeping
    the context but not the machinery that builds it, this is the cleanest
    first extraction target.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:360-375
  - src/melder/aether/spellbook/spell.py:619-691
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:1-65
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:210-293
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:113-133
  - src/melder/aether/conduit/meld/meld.py:340-386
  - src/melder/utilities/interfaces/icreationcontextfactory.py:1-65
  - src/melder/utilities/interfaces/ispell.py:111-114
  - src/melder/utilities/interfaces/ispell.py:205-223
  IMPACT: A truthful next implementation lane would move factory/switch
    ownership out of `Spell` first, while leaving `Spell` as the owner of the
    live `CreationContext` handle if desired. Removing the spellbook field or
    crafter ownership first is a larger structural tranche.
  NEXT: if you want the next pass, inspect candidate owners for the
    creation-context machinery and decide whether it belongs under `Meld`,
    another runtime helper, or a dedicated spell-runtime companion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:48:11Z
  TYPE: FACT
  CLAIM: After reading `spell_crafter.py` directly, the core diagnosis holds:
    `SpellCrafter` is already the runtime compiler, but it is also the
    spell-scoped artifact store and orchestration shell. It owns a large field
    set for Phase 1-11 artifacts, plan signatures, cached executors, and
    codegen IR; it captures `spell._spellbook` and `spell._spell_system_states`
    at construction; and then it repeatedly tunnels back through
    `self._spell._spellbook` for frame name, validators, lookup pools,
    contracted maps, and change-control phase wiring. So the “runtime compiler”
    concept already exists, but it is fused to spell-owned mutable state and a
    spellbook bridge.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:142-225
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:235-351
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:382-603
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1138-1290
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3175-3283
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4220-4292
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4516-4682
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5250-5652
  IMPACT: Any serious `Spell` cleanup has to start by splitting `SpellCrafter`
    into logic versus artifact ownership. Otherwise moving it just relocates
    the blob.
  NEXT: stop at this checkpoint unless you want the next read tranche to map
    candidate owners for `SpellCrafter` artifact state versus compile logic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Fresh investigation-only lane for `Spell` ownership and decomposition.
