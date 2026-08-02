# Epic: Boot melds - implicit conjure-time order of operations

## Metadata
- Epic ID: EPIC-2026-07-20-boot-melds
- Status: active (idea captured; NOT designed; awaiting pickup)
- Owner: UNASSIGNED
- Agent Name: -
- Priority: p3
- Created: 2026-07-20T22:40:00Z
- Updated: 2026-07-20T22:40:00Z

## Objective
Owner idea (2026-07-20, verbatim intent): objects that can be BOOTSTRAPPED via
the conduit itself - internalized "scripts" loaded so that when the conduit
conjures, an ORDER OF OPERATIONS happens IMPLICITLY instead of explicitly.
Spellbook-configured: the feature is enabled via configuration, and during
conjure it runs. Concretely: a set of spell_ids that get MELDED at conjure,
set up during BIND, with ordering either explicit (a number attached at bind)
or implicit (registration order). Gated behind a configuration flag - worlds
that never enable it are untouched.

## The Idea, In Full (what was said - not how to build it)
- A spell can be marked AT BIND TIME as a boot member: when this book's
  conduit conjures, that spell gets melded as part of the conjure itself.
- The boot set is ORDERED: the user can attach an explicit order number at
  bind, or omit it and take implicit registration order. The conjure then
  performs the melds in that order - an implicit order of operations the
  user no longer has to hand-write after every conjure.
- "Internalized scripts": because callables are already spells, a boot member
  that is a function spell gets CALLED at conjure - so the boot list can act
  as a startup script (steps as function spells, sequenced by order numbers)
  with no new machinery beyond the ordered-meld concept.
- The feature is OPT-IN via SpellbookConfiguration. Not configured = nothing
  changes anywhere.
- NAMING RULED (owner, 2026-07-20): plain words only - `boot` / `boot_order`
  at bind; a plainly named configuration flag (e.g. boot_melds_enabled).
  Fancy vocabulary explicitly rejected ("no human being understands what
  litany is... we're fucken idiots").

## Why This Is Interesting (the checkpoint angle - owner's headline)
Today a restored world comes back structurally perfect but COLD: the record
never serializes live instances (plain values, fresh identities, R-A
covenant), so nothing exists after a reload until someone hand-melds. Boot
membership declared at bind naturally rides the bind signature - the same
place existence/permissions already live in the SpellCrystal twin - so a
recorded world would carry its own WARMING RECIPE. Restore already replays
binds and conjure through public verbs; a rebuilt world would therefore
re-warm ITSELF, in recorded order, with fresh instances built by normal code
paths. Liveness restoration WITHOUT instance serialization. "This would make
checkpoints and reloading shit very interesting."

## Deliberately NOT Designed Here
Owner directive: capture the WHAT, not the HOW - "we don't really have a clue
how to implement this... we can't do it right now." No pipeline insertion
points, no data structures, no API signatures beyond the ruled plain naming.
The design pass happens when this epic is picked up with full context.

## Open Rulings For The Design Pass (questions only, no answers)
- Failure semantics: if boot meld N raises mid-conjure, what happens to the
  conjure, the conduit, and the single-conjure invariant?
- Existence eligibility: which existences may be boot members? (Spellspace-
  scoped needs an active spellspace; cluster-scoped needs an elected leader;
  neither exists at conjure time. "many" as a boot member = a fire-once
  side effect - meaningful or refused?)
- Duplicate explicit order numbers: refuse, or allow with a stable tiebreak?
- Dynamic worlds: boot fires AT conjure, but the order-of-operations law says
  contracts arrive AFTER conjure (link -> pull -> meld). What should a boot
  member with a SpellContract socket do - refuse, warn, defer?
- Where exactly in conjure the boot melds run, and how they interact with the
  held conjure window (melds are readers) - needs a probe, not an assumption.
- Restore interplay details: does the replayed conjure fire the boot list
  as-is (the elegant default), and does anything need recording beyond the
  bind-signature membership + order?
- Does the boot list belong in the intermediate curriculum once landed
  (implicit conjure behavior may be an advanced-tier teach)?

## Ticket Contract
- ENTRY_GATE: owner picks this up explicitly and a design pass produces a
  DECISION set for every open ruling above BEFORE any code.
- EXECUTION_BOUNDARY: not set (design pass will define it).
- DEPENDENCIES: SpellbookConfiguration freeze/settle point; bind signature ->
  SpellCrystal twin; restore engine conjure replay; conjure pipeline tail.
- EXIT_GATE: not set (design pass will define it).
- FAILURE_ESCALATION: DECISION_REQUEST to owner on every open ruling.

## Noting Behavior
- MEASURE/DECISION notes begin when the epic is picked up.

## Notes
- DATETIME: 2026-07-20T22:40:00Z
  TYPE: MEASURE
  CLAIM: Epic captured from owner idea (work-session 2026-07-20). Naming
    pre-ruled to plain `boot`/`boot_order` + configuration gate. Everything
    else intentionally open. UNASSIGNED by owner instruction.
  EVIDENCE:
  - conversation: owner idea + naming ruling, 2026-07-20
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## Context / Handoff Summary
Idea-stage epic. Read "The Idea, In Full" and the open rulings; do NOT invent
implementation shape from this document - the owner explicitly deferred design
until a context-heavy session picks it up.
