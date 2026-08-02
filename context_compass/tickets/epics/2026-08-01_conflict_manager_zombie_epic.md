# Epic: Adjudicate the zombie ChangeControlConflictManager

## Metadata
- Epic ID: EPIC-2026-08-01-conflict-manager-zombie
- Status: ready (filed for later per owner; NOT active, no board row)
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p3
- Created: 2026-08-01T00:05:04Z
- Updated: 2026-08-01T00:05:04Z
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
