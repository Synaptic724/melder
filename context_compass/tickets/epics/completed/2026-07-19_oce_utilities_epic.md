# Epic: OCE - Utilities (classification + exposure + dead-code removal)

## Completion
- Completed: 2026-07-23T00:30:00Z (done_pending_owner_run)
- Summary: Utilities classification + agent surface complete - 11 custom_exceptions USER-BINDABLE
  (unguarded + agent pair); kernel primitives guarded + agent pair; base classes (Cleanable /
  Sync / AbstractElasticPool) deliberately UNGUARDED per the MRO law; context headers present.
  Owner ruled the NEEDS-TAG guard additions OVERKILL (that AC struck) and ruled KEEP `Package`
  (dead code, not deleted).
- TESTS NOT RUN by agent (3.10 sandbox): the owner 3.14t suite + the MRO-law regression are the
  outstanding gate. Filed done_pending_owner_run; reopen if the owner run goes red.

## Metadata
- Epic ID: EPIC-2026-07-19-oce-utilities
- Parent: EPIC-2026-07-19-object-contract-enrichment-program
- Status: ready
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-19T02:10:00Z
- Updated: 2026-07-19T02:10:00Z
- Stories:
  - STORY-2026-07-19-oce-utils-classification (S1)
  - STORY-2026-07-19-oce-utils-docstrings (S2)
  - STORY-2026-07-19-oce-utils-package-removal (S3)

## LAW: NO CODEGEN FOR DOCUMENTATION (owner ruling 2026-07-20, non-negotiable)

Inherited from the program epic and binding on every story and task under this
epic.

- Docstrings and comments are AUTHORED CONTENT. Write them BY HAND, one method
  at a time, after reading that method's body.
- FORBIDDEN: scripts, codemods, loops, or generated passes that insert or
  bulk-apply docstring text across multiple methods or files - including
  hand-written strings applied by a script, because the application step is what
  removes the read-before-write discipline.
- FORBIDDEN: mass edits to move a completion counter.
- REQUIRED: targeted single-file edits; on tool failure, fall back to a
  single-file targeted write against THAT ONE FILE only.
- Scripts stay allowed for READ-ONLY verification afterwards (stripped-AST diff,
  trapped-line scan, counting). Never for producing the text.

## Problem / Opportunity
Utilities is the ONLY subsystem where the guard is a genuine judgement call rather than a
fill. Everywhere else the question is "did we tag the kernel object" - here the question is
"is this ours or theirs". It holds all three base classes whose tagging would poison user
subclasses, all 11 exception types users must catch, the concurrency primitives the owner
wants exposed, and 933 lines of dead code.

It is therefore the epic that RATIFIES the classification vocabulary the other eight inherit.

## Subsystem Context Brief (read this, not the C-docs)
`utilities/` is Melder's substrate toolbox. Nothing here participates in binding or
resolution; everything here is used BY those layers. Eight packages:

- `general_base/` - `Cleanable` (the idempotent cleanup ABC nearly everything inherits),
  `Sync`, `AbstractElasticPool`. THE BASE CLASSES. Never guarded.
- `custom_exceptions/` - the 11 error types. `SpellbookValidationError` and
  `MeldExecutionError` are what users actually catch; `InternalRegistrationError` is what the
  guard itself raises.
- `synchronization/` - the concurrency primitives. Split by ownership: Melder owns the gates
  and the scheduler (`LoadGate`, `CreationGate`, `CreationGateController`, `PhaseScheduler`,
  `UnitOfWork`, `CancellationEvent(Signal)`, `PhaseLatch`, `TicketFlag`, `SyncWeakRef`);
  users may want the switches and the lock-ordering helper (`SafeGuard`, `CounterSwitch`,
  `FastSwitch`).
- `data_structures/weak_data_structures/` - `WeakConcurrentDict`/`List`/`Set`, `WeakRefNode`.
  General-purpose containers; a user may legitimately want these injected.
- `helpers/` - `IDBuilder`, `InitHelpers`, `EnumHelpers`, `SpellInputUtils`,
  `ClassSurfaceAstDescriber` (+3 TypedDicts), and `Package` (dead).
- `logger/` - `SafeLogger`, the one logging adapter.
- `caching_system/`, `ai_native_support_tools/` - `CachingSystem`, `ProtocolCrafter`.

Where this sits in the system: beneath everything. `InitHelpers` + `AetherUtilitySystem` +
`SafeLogger` form the logging resolution path every runtime object uses;
`PhaseScheduler` drives the conjure phases; `LoadGate` is constructed by Aether before any
frame can exist. Utilities has no boot position of its own - it is already there.

## MRP Alignment
Getting classification right here is what makes the guard trustworthy everywhere else. A
guard that refuses a user's own class is worse than no guard: it turns a correctness feature
into a bug report.

## Ticket Contract
- ENTRY_GATE: program epic contract + MRO law read; exemplar diff (S1 of oce-package-root)
  reviewed.
- EXECUTION_BOUNDARY: `src/melder/utilities/**`.
- DEPENDENCIES: THE OBJECT CONTRACT, THE MRO LAW.
- EXIT_GATE: every utilities class classified and marked; MRO-law regression green; owner
  ruling on `Package` deletion.
- FAILURE_ESCALATION: DECISION_REQUEST on any class whose classification is genuinely
  ambiguous - do NOT guess, the whole point of this epic is that guessing is what breaks it.

## Guard Classification (owner rulings 2026-07-19 applied)
BASE CLASS - never guarded (MRO law):
- `Cleanable`, `Sync`, `AbstractElasticPool`
- VERIFIED already clean 2026-07-19; this epic's job is to keep them that way and say WHY in
  the docstring so nobody "fixes" it later.

USER-BINDABLE - not guarded:
- All 11 exception types in `custom_exceptions/`
- `WeakConcurrentDict`, `WeakConcurrentList`, `WeakConcurrentSet`, `WeakRefNode`
- `CounterSwitch`, `FastSwitch` (owner: "counterswitch and fastswitch are fine")

MELDER KERNEL - guarded:
- Already tagged: `SafeGuard`, `LoadGate`, `CreationGate`, `CreationGateController`,
  `PhaseScheduler`, `UnitOfWork`, `CancellationEvent`, `CancellationEventSignal`,
  `SyncWeakRef`, `SafeLogger`, `CachingSystem`, `ProtocolCrafter`
- NEEDS TAG: `PhaseLatch`, `TicketFlag`, `IDBuilder`, `InitHelpers`, `EnumHelpers`,
  `SpellInputUtils`, `ClassSurfaceAstDescriber`
- The three `_WeakDict*View` classes are private iteration views, not reachable as bind
  targets; leave untagged and say so.

EXPOSURE (recommendation only - NOT edited by this epic):
Guarding and exporting are orthogonal. These are guarded AND should be exported, because a
user calls them directly rather than asking Melder to construct them:
`SafeGuard`, `IDBuilder`, `InitHelpers`, `EnumHelpers`.
These are unguarded AND should be exported: `CounterSwitch`, `FastSwitch`, the weak
containers, and all 11 exceptions.
DO NOT EXPOSE (owner): `Package`, and every remaining kernel primitive.
DELIVERY: send this list to `helper_f` via `mailbox_board.md` - the root export list belongs
to the active `melder_init_wheel_strategy` lane, not to this program.

## Goals
- Every utilities class carries an explicit, justified classification.
- The three base classes are documented as deliberately unguarded, with the MRO reason.
- `Package` removed or an explicit retention ruling recorded.

## Non-Goals
- No `__init__.py` edits (collision with helper_f's lane).
- No behavior changes to any primitive.

## Acceptance Criteria
- [ ] All ~47 utilities classes carry `Registration:` stating classification + reason.
- [ ] `Cleanable`, `Sync`, `AbstractElasticPool` remain untagged, each with an explicit
      "BASE CLASS - deliberately unguarded, tagging propagates through the MRO to user
      subclasses" note.
- [ ] The 7 NEEDS-TAG classes carry the sentinel.
- [ ] `__agent_purpose__` + `__ast_helper_access__` on all utilities classes.
- [ ] MRO-law regression: a test-defined `class UserThing(Cleanable)` binds successfully.
- [ ] `Package` deleted (or retention ruled) with its two test files.

## Risks / Mitigations
- Someone later "completes" the guard sweep by tagging `Cleanable` -> the docstring note and
  the MRO-law regression exist specifically to make that fail loudly.
- Exposing `CounterSwitch`/`FastSwitch` commits their API shape -> they are small and stable;
  if unsure, the exposure recommendation can be deferred without blocking classification.

## Validation Plan
- AST sweep over `utilities/**` proving classification coverage.
- MRO-law regression (both directions).
- Not run by agent. Owner runs on 3.14t.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: classification decided from owner rulings + measured guard state;
  three stories each sit inside the chunking law (47 classes / 3 stories).

## Applicable Anti-Patterns
- [ ] No tagging a base class.
- [ ] No guessing a classification - escalate instead.
- [ ] No editing the root export list from this epic.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Epic notes: classification rulings other epics will cite as precedent.

## Notes
- DATETIME: 2026-07-19T02:10:00Z
  TYPE: DECISION
  CLAIM: Classification vocabulary ratified here and inherited by the other eight child
    epics: BASE CLASS (never guarded, MRO law), USER-BINDABLE (not guarded, a user may
    legitimately ask Melder to inject it), MELDER KERNEL (guarded). Exposure is tracked as a
    SEPARATE axis because the two are orthogonal - `SafeGuard` is guarded and exported,
    `WeakConcurrentDict` is unguarded and exported, `LoadGate` is guarded and unexported.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:1-1
  - src/melder/utilities/synchronization/safeguard.py:9-9
  IMPACT: Removes the ambiguity that made "guard everything" look reasonable in the first
    draft of the program epic.
  NEXT: Execute S1 classification pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-21T22:44:00Z
  TYPE: FACT
  CLAIM: custom_exceptions cluster (all 11 files) brought to agent-surface contract BY HAND.
    Each already carried a Rank-5 docstring with a `Registration:` USER-BINDABLE classification;
    the missing piece on every one was the agent pair. Added `__ast_helper_access__ = "public"`
    and a hand-authored action-shaped `__agent_purpose__` to all 11; NO sentinel added
    (USER-BINDABLE per the ratified vocabulary). Docstrings were already correct and were NOT
    rewritten - editing them would be a drive-by.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/internal_registration_error.py:51-57
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:86-93
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:71-77
  IMPACT: The "agent_purpose + ast_access on all utilities classes" AC now holds for the whole
    custom_exceptions package (11/11); the USER-BINDABLE-unguarded AC holds (0 sentinels).
  MEASURE: `python -m py_compile` green on all 11; grep coverage 11/11 both attrs, 0 sentinels.
    Full AST sweep + MRO-law regression NOT run by agent - owner runs on 3.14t.
  NEXT: NEEDS-TAG kernel classes (PhaseLatch, TicketFlag, IDBuilder, InitHelpers, EnumHelpers,
    SpellInputUtils, ClassSurfaceAstDescriber): read each body, add sentinel + agent pair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-21T22:58:00Z
  TYPE: FACT
  CLAIM: Utilities agent-surface pass completed BY HAND. Added __ast_helper_access__ + a
    hand-authored __agent_purpose__ to the three kernel classes that had the sentinel but no
    agent surface: SyncWeakRef (internal), CachingSystem (internal), ProtocolCrafter (public).
    access values follow the established convention (exposed=public per SafeGuard/IDBuilder;
    internal machinery=internal per PhaseLatch). NO sentinels added or removed.
    DELIBERATE EXEMPTIONS (do NOT "fix" these):
    - Protocols ICleanable / IChannelLogger: docstrings already carry Registration + contexts;
      NOT adding valued class attrs to a runtime_checkable Protocol - that makes them structural
      members and changes the public typing contract (Non-Goal: no behavior change).
    - Private views _WeakDictKeysView/_ValuesView/_ItemsView and nested Cleanable._CleanupContext:
      internal, not bind-reachable, not agent-facing; owner steer "agents don't need to see
      everything" - left without the agent pair by design.
    - helpers/package.py (Package): dead code, S3 deletion lane - untouched pending owner ruling.
  EVIDENCE:
  - src/melder/utilities/synchronization/sync_weak_ref.py:102-108
  - src/melder/utilities/caching_system/caching_system.py:79-86
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:86-93
  IMPACT: Every public/kernel major class in utilities/** now carries the agent surface; the
    only ap<class-count files remaining are the four intentional exemptions above.
  MEASURE: py_compile green on the three edited files; re-sweep shows only the exemptions remain.
    Full AST sweep + MRO-law regression NOT run by agent - owner runs on 3.14t.
  NEXT: Owner decisions remain: (1) Package delete vs retain (S3); (2) owner ruled the guard
    NEEDS-TAG additions OVERKILL 2026-07-21, so AC "the 7 NEEDS-TAG classes carry the sentinel"
    should be struck. No further docstring work outstanding in utilities/**.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Utilities is the classification-defining epic: three base classes that must stay unguarded,
11 exceptions and 4 weak containers that are the user's, ~19 kernel primitives that are
Melder's, and 1,281 lines of dead `Package` code to remove. Exposure recommendations are
routed to helper_f's init lane rather than applied here.
