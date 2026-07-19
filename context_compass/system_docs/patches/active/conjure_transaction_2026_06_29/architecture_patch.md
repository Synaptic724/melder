# architecture_patch

## Metadata
- Patch ID: conjure_transaction_2026_06_29
- Status: in_progress
- Owner: cowork
- Agent Name: mediator_builder_0
- Created: 2026-06-29T09:01:57Z
- Updated: 2026-06-29T09:01:57Z

## Patch Scope and Non-Goals
- Objective:
  - introduce a CONJURE change-control transaction so the spellbook -> conduit
    genesis is admitted through the mediator instead of riding the Spellbook
    `_lock` + `_conjured` invariant alone
  - the conjure transaction claims `scope:spellbook:<id>` EXCLUSIVE for the full
    creation pipeline, serializing conjure against bind, link, transfer, and
    every other spellbook-level transaction
  - envelope-only: the strategy claims scope; `SpellbookCreationSystem.conjure()`
    still performs the actual build inside the held window
  - no conduit scope at admission: the `conduit_id` is minted mid-pipeline and
    nothing can target the conduit until activation registers it
- Non-goals:
  - a frame-wide one-at-a-time conjure mutex (considered and explicitly deferred;
    spellbook-local is the chosen granularity, user decision 2026-06-29)
  - claiming the minted conduit scope mid-pipeline (optional future; spellbook-X
    already covers the whole window)
  - SpellSystemState / ConduitResolutionState transactions (separate effort)
  - meld/read-path changes; the existing structural seals stay unchanged

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| transaction request | modify | add `ChangeTransactionType.CONJURE` | none |
| conjure strategy | add | new envelope-only `ConjureTransactionStrategy` emitting the spellbook-X claim | strategy ABC |
| strategy builder | modify | register the conjure family for resolve/on_start/on_end | conjure strategy |
| devops identity | modify | spellbook identity declares `"conjure"` in `available_transactions` (the `supports_transaction` gate) | none |
| spellbook conjure | modify | wrap `conjure()` to open/commit the CONJURE transaction around the creation pipeline | strategy builder, identity |

## Interface and Boundary Deltas
- Interface delta 1: `ChangeTransactionType` gains `CONJURE = "conjure"`.
- Interface delta 2: the spellbook `DevopsIdentity.available_transactions`
  includes `"conjure"` so `begin_transaction` admits it.
- Interface delta 3: `ConjureTransactionStrategy.build_start_plan` emits
  `{scope:spellbook:<id>: EXCLUSIVE}`, `initiator="spellbook:<id>"`,
  `conduit_ids=()`; `on_start`/`on_end` are no-ops.
- Boundary delta 1: `Spellbook.conjure()` becomes a mediated transaction
  boundary; the creation pipeline runs inside the held spellbook-X claim. The
  `_lock` + `_conjured` invariant remain as belt-and-suspenders.
- Boundary delta 2: the strategy is envelope-only -- it makes no registry or
  runtime writes (mediator = DevOps admission only).

## Cross-Component Invariants
- A conjure holds `scope:spellbook:<id>` EXCLUSIVE from admission until
  commit/abort releases it.
- No bind/link/transfer/other spellbook-level transaction admits on that
  spellbook while a conjure holds it (EXCLUSIVE is incompatible with everything).
- Different spellbooks conjure in parallel (disjoint scope keys); conjure is a
  rare setup op, so spellbook-local serialization costs ~nothing.
- The conjure pipeline opens no nested mediator transaction (verified:
  `spellbook_creation_system.py` and the `spell_compiler` tree contain zero
  `transaction(`/`begin_transaction` calls), so a conjure root never trips the
  "nested root not allowed" rule.
- Double-conjure: a second attempt blocks on spellbook-X, wakes after the first
  commits, retries, and hits the existing `_conjured` guard -> clean RuntimeError
  rather than a lock-only race.

## Migration and Rollout Order
1. Add the `CONJURE` enum value (inert until used).
2. Add `ConjureTransactionStrategy` (spellbook-X plan; envelope no-ops).
3. Register conjure in the strategy builder.
4. Declare `"conjure"` in the spellbook identity `available_transactions`.
5. Wrap `Spellbook.conjure()` to open/commit the CONJURE transaction around
   `SpellbookCreationSystem.conjure()` (coordinate with general_0 -- hot file).
6. Tests: strategy claim-set + builder resolve; conjure-vs-bind serialization;
   two-spellbook parallel conjure; double-conjure clean raise.

## Rollback Strategy
- Rollback trigger: conjure regressions (deadlock, conjure wrongly denied,
  double-conjure misbehavior) in the spellbook or change-control unit rings.
- Rollback steps: revert the spellbook wrap first (restores lock-only conjure),
  then the builder/identity/strategy/enum commits for this patch id.
- Post-rollback verification: spellbook + change-control unit rings pass.

## Validation Expectations and Evidence Plan
- Unit: strategy emits `{scope:spellbook:<id>: X}`; builder resolves `"conjure"`;
  `on_start`/`on_end` no-ops.
- Integration/concurrency: conjure-vs-bind serialize on one spellbook; two
  spellbooks conjure in parallel; double-conjure -> one wins, the other raises
  cleanly.
- Runner: user-run `pytest` in the 3.14t venv (agent reports "Not run.").

## Ticket Coverage Map
- Epic: `tickets/epics/2026-06-20_implement_new_mediator_strategies_epic.md`
- Story/Task: to be added when the build slice opens.

## Unknowns and Decision Requests
- DECISION (user, 2026-06-29 chat): spellbook-local granularity, NOT frame-wide;
  conjure blocks bind/link and all spellbook-level ops; no conduit scope because
  the conduit does not exist yet at admission.
- UNKNOWN: whether to later add the minted-conduit claim mid-pipeline for the
  SpellSystemState/ConduitResolutionState effort; deferred.

## Context / Handoff Summary
- What changes: CONJURE becomes a mediated, spellbook-EXCLUSIVE transaction so
  the genesis is visible to the admission plane and serialized against
  spellbook-level work; envelope-only; conduit scope omitted by design.
- What remains: the state-record transactions (separate effort) and the optional
  minted-conduit claim.
- Cross-agent: the `Spellbook.conjure()` wrap lands in general_0's active
  `spellbook.py`; mailbox coordination precedes that edit.
