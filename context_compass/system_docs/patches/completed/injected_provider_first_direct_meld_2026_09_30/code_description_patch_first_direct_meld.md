# code_description_patch_first_direct_meld

## Metadata
- Patch ID: injected_provider_first_direct_meld_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T19:31:23Z
- Updated: 2026-09-30T19:31:23Z

<!-- BEGIN ENTRY: "first direct meld of an injected dependency" -->
## Control Flow
1. Consumer meld: the validation lane (`_ensure_resolution_resolvable`) runs the consumer's full target pass inside
   the consumer's rebuild window and lock; at its tail the pass flags the plan-less owned dependency D.
2. Direct meld of D: the door reads D's `resolution_required` (lock-free) and calls `_ensure_runtime_resolution_ready`.
3. The lane enters D's rebuild window, then D's lock, re-checks the flag, and - D being neither an existing
   creation nor its Phase 5 root - runs D's full target pass: Phase 5 publishes D's root blueprint, Phase 6 stamps
   D's root verdict, 8-11 build D's plan, and the tail flags D's own plan-less dependencies.
4. The lane confirms D's verdict, marks D complete and clears the flag; the window's exit publishes D's context.
5. `_execute_admitted` runs D's executor: it returns the instance the consumer's plan stored under D's id in the
   scope's store (unique_per_conduit, unique), or builds a new one (many).

## Edge / Error Semantics
- The flag write and D's own lane are serialized by D's lock: either D's lane already published a plan (no flag),
  or the flag precedes the lane (the lane clears it).
- A visibility failure in D's pass leaves invalid verdicts: SpellbookValidationError from the lane, flag kept,
  epoch bumped.
- Sibling lessers resolve through their root's conduit id, so D's first direct meld in either scope resolves D once;
  the other scope then builds its own instance from D's context.

## Invariants / Idempotency
- Flagging is idempotent: an already flagged dependency is skipped, with no second epoch bump.
- One compile per dependency: once D has a plan, later consumer passes never flag it again.

## Explicit Non-Goals
- Verdicts stay as local Phase 6 writes them; the flag, not the verdict, owes the work.
- Warm melds, the conduit-wide pass, bind, notch, transfer and the conjure cache do not change.
<!-- END ENTRY: "first direct meld of an injected dependency" -->
