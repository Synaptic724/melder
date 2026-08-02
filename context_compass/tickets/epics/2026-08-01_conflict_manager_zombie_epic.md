# Epic: Adjudicate the zombie ChangeControlConflictManager

## Metadata
- Epic ID: EPIC-2026-08-01-conflict-manager-zombie
- Status: in_progress (investigation delivered 2026-08-02; awaiting owner DECISION)
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p3
- Created: 2026-08-01T00:05:04Z
- Updated: 2026-08-02T18:30:00Z
- Target Window: UNKNOWN
- Related Program/Initiative: EPIC-2026-07-31-aetheric-mediator-subsystem
  (the port that surfaced this)

## Problem / Opportunity

`ChangeControlConflictManager` is commonly described as "retired". IT IS NOT
RETIRED - IT IS A ZOMBIE. It is still fully alive as an object and completely
dead as a behaviour, which is the worse of the two states because it carries
cost and reads as functional.

STILL ALIVE (measured 2026-08-01):
- constructed per frame: `change_control_manager.py:204`
- occupies a `__slots__` entry: `:139`
- cleaned up on teardown: `:305-306`, `:323`
- exposed through a PUBLIC property: `:896-905`
- passed into the orchestrator: `:225`, `:972`
- imported and threaded into the mediator: `transaction_mediator.py:20`
- has its own live test file: `tests/unit/melder/aether/dev_ops/change_control_manager/test_conflict_manager.py`

COMPLETELY DEAD:
- `find_conflicts(...)` has ZERO call sites anywhere in `src/melder`. The only
  occurrence of the name is its own `def`.
- The orchestrator states the position outright: "the legacy in-flight conflict
  scan is retired and `conflict_manager` is accepted for SIGNATURE COMPATIBILITY
  ONLY" (`orchestrator.py:393-395`).

So the frame pays construction, a slot, cleanup, a public accessor, and
parameter threading through two layers, for a method nothing calls.

## The Real Question (not "should we delete it")

Deleting dead code is trivial and is NOT why this epic exists. The question is
whether RETIRING IT LOST A CAPABILITY, because conflict detection and claim
acquisition adjudicate DIFFERENT NOTIONS OF OVERLAP:

- `ChangeControlEmbargoManager` matches on exact SCOPE KEYS.
- `find_conflicts` matched on SCOPE HASHES:
  `req_hashes = self._normalize_hashes(request.scope_keys, request.scope_hashes)`
  then `req_hashes.intersection(active_hashes)`, with the method's own comment
  stating it is "intentionally conservative: hash overlap is enough".

Two requests could therefore carry DIFFERENT key strings while sharing a hash.
The old scan refused that pair; the claim table admits it. The current
documented behaviour makes this explicit and intentional - "Hash-only roots
admit independently even when their hashes overlap" - so this was a DECISION,
not an oversight. The epic's job is to establish whether it was the RIGHT
decision, and to write down the reasoning where the next reader can find it.

## Why This Matters Now

The `aetheric_mediator` port (EPIC-2026-07-31) DROPPED scope hashes entirely,
on the reasoning that DevOps carries them as advisory evidence that "carry no
claims" and nothing consumes them. THAT REASONING IS ONLY SOUND IF HASH-OVERLAP
DETECTION WAS GENUINELY UNNECESSARY. If this epic finds the retirement lost a
real guard, the new plane inherits the same gap by construction, and the
no-hashes decision must be revisited before it ships.

## Ticket Contract
- ENTRY_GATE: owner activation. Filed for later; not scheduled.
- EXECUTION_BOUNDARY: investigation and a recorded decision. Any deletion or
  revival is a follow-up, not this epic.
- DEPENDENCIES: none blocking.
- EXIT_GATE: a recorded owner DECISION on delete / revive / keep-as-is, with the
  capability question answered rather than assumed.
- FAILURE_ESCALATION: RAISE if hash-overlap detection turns out to be
  load-bearing - that would reopen a shipped design decision AND change the
  aetheric plane.

## Investigation Lanes
1. WHAT COULD HASHES CATCH THAT KEYS CANNOT? Find or construct a concrete case
   where two requests share a hash but not a key. If no such case can exist by
   construction, the retirement was free and the rest is bookkeeping.
2. WHY WAS IT RETIRED? Recover the reasoning - git history around the
   scope-acquisition landing, plus the `queue_competing_root_transactions`
   removal in the same lane. Was the scan removed because it was redundant, or
   because it was too conservative and blocked legitimate parallel work?
3. WHAT DO THE TESTS STILL ASSERT? `test_conflict_manager.py` is live and
   presumably green. Green tests over a method nothing calls prove the unit
   works in isolation, which is precisely the shape that keeps zombie code
   alive through reviews. Establish whether they guard anything real.
4. WHAT IS THE ACTUAL CARRYING COST? Construction per frame, slot, cleanup,
   public property, and two signatures. Small individually; the point is that
   it is paid on every frame forever for zero behaviour.
5. DOES THE PUBLIC PROPERTY HAVE CALLERS OUTSIDE `src/`? `conflict_manager` is
   public surface. Deleting it is an API change if anything reaches for it.

## Possible Outcomes (all legitimate)
- DELETE: remove the class, the slot, the property, the parameters, the tests.
- REVIVE: hash-overlap detection was load-bearing; reinstate it at admission and
  add hashes back to the aetheric plane.
- KEEP AS IS, DOCUMENTED: retain for a planned near-term consumer, with the
  zombie state written down so the next reader is not misled.

## Acceptance Criteria (Epic Done)
- Lane 1 answered concretely - a real hash-without-key-overlap case, or a proof
  none exists.
- A recorded owner DECISION among the three outcomes.
- The aetheric plane's no-hashes decision either CONFIRMED or REOPENED in
  EPIC-2026-07-31.
- If the outcome is KEEP, the zombie state is documented at the class so it
  stops being rediscovered.

## Risks / Mitigations
- RISK: someone deletes it as obvious dead code before lane 1 runs, discarding
  the capability question along with the class. MITIGATION: lane 1 is the gate;
  deletion is an outcome, not the starting assumption.
- RISK: the green unit tests are mistaken for evidence the behaviour is live.
  MITIGATION: lane 3 exists specifically to separate "the unit works" from
  "anything calls it".

## Applicable Anti-Patterns
- [ ] No deleting before the capability question is answered.
- [ ] No treating passing unit tests as proof a code path is reachable.
- [ ] No promoting "it is retired" to fact without a call-site check - the claim
      was already half wrong once.

## Validation / Test Approach
Not run - investigation stage.

## Open Questions
- Are scope hashes consumed by ANYTHING today, or did they become inert when the
  scan was retired? If inert, they are a second zombie in the same lane.
- `queue_competing_root_transactions` was removed in a related pass. Same
  reasoning, same lane? Worth confirming they were one decision.

## Decision Log
- 2026-08-01: Filed at owner request after the aetheric_mediator port found the
  "retired" description was inaccurate - the object is live, only the behaviour
  is dead.

## Notes
- DATETIME: 2026-08-01T00:05:04Z
  TYPE: FACT
  CLAIM: `ChangeControlConflictManager` is constructed, slotted, cleaned,
    publicly exposed, and threaded into two collaborators, while
    `find_conflicts` has ZERO call sites in `src/melder`. The orchestrator
    documents it as accepted "for signature compatibility only".
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:204
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:896-905
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:393-395
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/conflict_manager/conflict_manager.py:98
  IMPACT: "Retired" understates it. Live object, dead behaviour - the state that
    reads as functional to a reviewer while delivering nothing.
  NEXT: Lane 1 - can hash overlap exist without key overlap?
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-01T00:05:04Z
  TYPE: RISK
  CLAIM: The aetheric_mediator port dropped scope hashes citing "nothing
    consumes them". That reasoning depends on this epic's answer: if hash
    overlap detection was load-bearing, the new plane inherits the gap.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/transaction_request.py
  - context_compass/tickets/stories/2026-07-31_aetheric_mediator_core_story.md
  IMPACT: Couples the two epics. A REVIVE outcome reopens a shipped decision in
    the new plane before it goes anywhere near wiring.
  NEXT: Cross-reference from EPIC-2026-07-31 so the dependency is visible from
    both sides.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## INVESTIGATION (bootstrap_0, 2026-08-02T18:30:00Z)

Read-only. No code changed. Every "STILL ALIVE" line in the Problem section was
re-verified line by line and **all of them hold** - this epic's facts are
accurate as filed.

### Lane 1 - CAN HASH OVERLAP EXIST WITHOUT KEY OVERLAP? **YES. Demonstrably, and there is already a green test doing it.**

The mechanism is in `_normalize_hashes` (`conflict_manager.py:156-163`):

    if scope_hashes:
        return {hash_value for hash_value in scope_hashes if hash_value}
    ...
    return {sha256(key) for key in scope_keys if key}

**Supplied hashes WIN and the keys are then ignored entirely.** Derivation is the
fallback, not the rule. The same precedence is enforced upstream at
`transaction_manager.py:261-263`: hashes are derived from keys ONLY when the
caller supplied none.

And `scope_hashes` is not an internal detail - it is a **public parameter**:
- `Spellbook.begin_transaction(..., scope_hashes=...)` - `spellbook.py:4069`
- `Conduit.begin_transaction(..., scope_hashes=...)` - `conduit.py:2718`
- `TransactionMediator.begin_transaction(..., scope_hashes=...)` - `transaction_mediator.py:400`

So a caller can hand in any opaque strings they like, with any scope keys they
like. The two are not required to relate.

The concrete case Lane 1 asked for **already exists as a live integration test**,
`test_change_control_scope_hash_only_roots_admit_independently`
(`tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:219-260`):
two DIFFERENT spellbooks, two different conduits, identical `scope_hashes`, no
shared scope keys - and the test asserts **both admit**, 2 in flight. The old
`find_conflicts` would have reported that pair as conflicting
(`req_hashes.intersection(active_hashes)`); the claim table admits it.

**So the behaviour did change, and the change is deliberate and asserted.** The
test's own Contract states it: "Scope KEYS are the admission vocabulary; scope
hashes are advisory identity evidence and carry no claims."

### THE FINDING THAT REFRAMES THIS EPIC

The epic asks whether a capability was lost. The sharper answer is that
**`scope_hashes` is a PUBLIC API parameter that promises behaviour it does not
deliver.** The docstring on both public verbs reads, verbatim:

> `scope_hashes:` Optional normalized scope hashes **for conflict checks**.
> (`spellbook.py:4100-4101`, `conduit.py:2751-2752`)

There are no conflict checks. `request.scope_hashes` is READ at exactly two
lines in the entire source tree - `conflict_manager.py:121` and `:127` - both
inside `find_conflicts`, which has **zero call sites**. Everything else in the
~70 `scope_hashes` occurrences is plumbing: accept, normalize, store, expose.

This is the second zombie the epic's Open Questions suspected, and it is the
**worse** of the two:
- The CLASS is internal. It costs construction and a slot, and no user can see it.
- The PARAMETER is public surface with a written promise. A user who passes
  `scope_hashes` reads "for conflict checks", reasonably concludes they have
  declared an overlap, and receives no isolation - silently, with a green test
  guaranteeing the silence.

A dead internal class is waste. A public parameter that lies is a trap.

### Lane 2 - WHY WAS IT RETIRED? **Not recoverable. Recording that as the finding.**

`git log -S find_conflicts` surfaces three commits, none of which is the
retirement. The story that landed the scope-acquisition plane
(`2026-06-12_implement_scope_acquisition_control_plane_story.md`) was **deleted**
in commit `14a8ab77f` ("Delete deprecated ... files"), and recovering it from
`14a8ab77f^` yields no text matching conflict/hash/retire. The in-code statement
at `orchestrator.py:393-395` records the POSITION - "the legacy in-flight
conflict scan is retired and `conflict_manager` is accepted for signature
compatibility only" - but not the REASONING.

So the question "was it removed as redundant, or as too conservative?" cannot be
answered from history. It has to be decided on merits now. I am not going to
manufacture a reason and present it as recovered.

### Lane 3 - WHAT DO THE TESTS ACTUALLY GUARD? **Not the capability in question.**

`test_conflict_manager.py` holds four tests:
- `..._cleanup_is_idempotent_and_blocks_reuse` (:13) - cleanup mechanics
- `..._cleanup_rechecks_cleaned_inside_lock` (:34) - cleanup mechanics
- `..._find_conflicts_returns_empty_for_none_request` (:90) - null guard
- `..._detects_key_only_overlap_without_hashes` (:107) - **the KEY branch**

Three test teardown hygiene. The one that tests detection constructs BOTH
requests with `scope_hashes=()` and states in its own Contract: "The raw-key
branch is used even when scope_hashes are empty."

**Zero tests cover hash-overlap-without-key-overlap** - the exact capability this
epic exists to adjudicate. The suite is green and proves the unit works; it does
not protect the behaviour anyone would miss. This is precisely the shape the
epic's Risk section named, confirmed rather than assumed.

### Lane 4 - CARRYING COST, measured

- constructed per frame - `change_control_manager.py:204`
- TWO `__slots__` entries - `change_control_manager.py:139`, `transaction_mediator.py:123`
- **MANDATORY**: `transaction_mediator.py:185-186` raises `ValueError` if it is
  `None`, so a mediator cannot be constructed without one
- cleaned in two places - `change_control_manager.py:305-306` and `:323`,
  `transaction_mediator.py:254`
- public property - `change_control_manager.py:896-905`
- threaded through two signatures - `change_control_manager.py:225`, `:972`,
  `transaction_mediator.py:139`, `:1231`, `orchestrator.py:380`
- **`ChangeControlOrchestrator.admit_request` (`orchestrator.py:375`) references
  `conflict_manager` ZERO times in its body** - verified by AST, not by reading.

### Lane 5 - EXTERNAL CALLERS OF THE PUBLIC PROPERTY? **None.**

Zero property accesses across `src/`, `tests/` and `examples/`. Every textual
match is the module path `...change_control_manager.conflict_manager.conflict_manager`
in an import, not `x.conflict_manager` attribute access. Removing the property
is not an API break anywhere in this repository. I cannot speak for consumers
outside it.

### COUPLED RISK TO EPIC-2026-07-31 - **CONFIRMED, not reopened**

The aetheric plane dropped scope hashes on the reasoning that nothing consumes
them. **That reasoning is correct as stated**: nothing does consume them, because
the only consumer is unreachable. Verified the new plane carries none - a `hash`
grep over `aetheric_mediator/*.py` returns only Python object-hashing on
`Identity`, nothing scope-related.

The no-hashes decision stands. One caution worth carrying forward rather than a
change: DevOps did not get here by accepting hashes, it got here by continuing to
ACCEPT them publicly after they stopped meaning anything. The plane should hold
the line that a parameter it accepts must carry a claim.

### WHAT I DID NOT DO

The EXECUTION_BOUNDARY is investigation plus a recorded decision. I deleted
nothing and revived nothing. The DECISION is the owner's and this epic stays open
until it is recorded.

### MY READ, offered as input to that decision and not as the decision

The capability question resolves toward **DELETE**, because hash-only isolation
was never checkable: an opaque caller-supplied string asserts "I overlap
something" without naming what, whereas a scope key names it and can be
adjudicated. Keys are the better vocabulary and the claim table is the better
mechanism.

But deletion should be scoped to **the parameter, not just the class.** Removing
`ChangeControlConflictManager` while leaving `scope_hashes` accepted on
`Spellbook.begin_transaction` and `Conduit.begin_transaction` - still documented
"for conflict checks" - would be the worst of the three outcomes: it removes the
cheap half and leaves the public lie in place. If the answer is DELETE, the unit
of work is the parameter, its plumbing, the class, the property, the two
signatures, and the docstrings - together.

If the answer is KEEP, the acceptance criterion already says the zombie state
must be documented at the class. I would add: it must also be documented at the
two PUBLIC verbs, because that is where a user meets it.

### Evidence index (every path:line above was resolved against source)
`conflict_manager.py` 121, 127, 156-163; `transaction_manager.py` 261-263;
`transaction_mediator.py` 20, 123, 139, 185-186, 206, 254, 400, 1231;
`orchestrator.py` 29, 375-380, 393-395, 407; `change_control_manager.py` 139,
204, 225, 305-306, 323, 896-905, 972; `spellbook.py` 4069, 4100-4101;
`conduit.py` 2718, 2751-2752;
`tests/.../test_conflict_manager.py` 13, 34, 90, 107-138;
`tests/integration/.../test_aether_integration_change_control_transactions.py` 219-260.


## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary

Filed for later. Not active, no board row.

Do not open this by deleting the class. The class is the boring half. The real
question is in lane 1: conflict detection matched on HASHES and the claim table
matches on KEYS, which are different notions of overlap, so retiring the scan
may have narrowed what the plane refuses. Answer that first; deletion, revival,
or documented retention all follow from it.

This epic is COUPLED to EPIC-2026-07-31-aetheric-mediator-subsystem, which
dropped scope hashes on the assumption the answer is "nothing was lost".
