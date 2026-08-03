# Epic: Adjudicate the zombie ChangeControlConflictManager

- Completed: 2026-08-03T12:25:00Z
- Summary: Owner ruled **KEEP AS IS, DOCUMENTED**. `ChangeControlConflictManager`
  is retired at admission - `find_conflicts` has zero call sites - and is
  retained deliberately for the CONCEPT it names: a conflict is an unsolvable
  clash requiring solutioning, a state the moded claim table cannot produce.
  Lane 2 was ANSWERED after bootstrap_0 marked it unrecoverable: the reasoning
  was never in git, it was in this package's own completed-ticket archive.
  The zombie state is now documented at the class, at all four public docstring
  sites, and in the four graph descriptors, and `src_graph.md` + its index were
  regenerated in the same pass. Zero occurrences of the false "for conflict
  checks" promise remain in `src/melder`.
- Status at closure: all four acceptance criteria met.

## Metadata
- Epic ID: EPIC-2026-08-01-conflict-manager-zombie
- Status: in_progress (investigation delivered 2026-08-02 by bootstrap_0, independently
  verified 2026-08-03 by super_tester_0; awaiting owner DECISION)
- Owner: cowork
- Agent Name: super_tester_0
- Priority: p3
- Created: 2026-08-01T00:05:04Z
- Updated: 2026-08-03T02:05:00Z

## State Transition Event
- from_state: review
- to_state: in_progress
- transition_reason: Owner directed super_tester_0 to claim this lane
  (2026-08-03). Reassignment is owner-directed, NOT protocol default -
  `bootstrap_0` is ACTIVE on the roster and authored the entire investigation
  below, which stands verbatim as the record of who did that work. `Owner:
  cowork` is unchanged: `owner` is executor identity, `agent_name` is assignment
  identity. Moved back to `in_progress` from `review` because verification
  surfaced NEW scope (see the 2026-08-03 notes) that changes the size of the
  DELETE work unit, so the epic is no longer merely awaiting a ruling.
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
- 2026-08-03: **OWNER DECISION: DELETE.** EXIT_GATE satisfied. The owner's
  rationale is the conceptual argument this lane had been missing, and it is
  recorded here because it outranks the mechanical evidence: **a conflict means
  a clash that is UNSOLVABLE and requires solutioning.** The claim table has no
  unsolvable state - every admission ends in admit, wait, or refuse-with-holder-
  evidence, and each of those is a resolved outcome. So "conflict" names a
  condition this design cannot produce. The object does not exist because it is
  dead code; it exists because it models a concept the system retired. Remove the
  object and its tests.
- 2026-08-03: SCOPE OF THE DELETE IS NOT YET SETTLED - see the DECISION_REQUEST
  note. Removing the public `scope_hashes` parameter is a public API change and
  `engineer/AGENTS.MD:198-208` plus `synaptic/AGENTS.MD:217-225` forbid changing
  public API shape without an explicit request. The owner ruled on the OBJECT and
  its TESTS; the parameter needs its own word.
- 2026-08-03: Owner directed `super_tester_0` to claim the lane. bootstrap_0's
  investigation was independently re-verified against source rather than
  inherited; all mechanism claims hold, two citation defects corrected, and one
  new scope class found (generated build assets). Recommendation is unchanged -
  DELETE, scoped to the parameter - and the owner DECISION is still outstanding.

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


## VERIFICATION (super_tester_0, 2026-08-03T02:05:00Z)

Read-only. Nothing changed under `src/`. I re-ran bootstrap_0's load-bearing
claims against source rather than inheriting them, because this epic's own
anti-pattern list says the "retired" claim was **already half wrong once**, and
another agent's notes are evidence of their reading, not of behaviour
(`unknowns_gate_reference.md:38-41`).

### bootstrap_0's mechanism findings: ALL HOLD

- `find_conflicts` has ZERO call sites. The only occurrence in `src/melder` is
  its own `def` at `conflict_manager.py:98`. (One other textual hit exists, in
  the generated `src_graph_payload.py:1050`, which is documentation - see below.)
- `request.scope_hashes` is READ at exactly TWO lines tree-wide,
  `conflict_manager.py:121` and `:127`, both inside `find_conflicts`.
- Supplied hashes WIN and keys are then ignored: `_normalize_hashes` returns the
  supplied set at `:156-157` and only derives SHA256 from keys as the fallback at
  `:158-164`. Hash overlap also SHORT-CIRCUITS - `:129` appends and `continue`s
  before the key check at `:132` ever runs.
- The conflict manager is MANDATORY on the mediator:
  `transaction_mediator.py:185-186` raises `ValueError("conflict_manager must not
  be None.")`, and `_conflict_manager` occupies a `__slots__` entry at `:123`.

### CORRECTION 1 - the docstring lie is in FOUR places, not two

bootstrap_0 cited `spellbook.py:4100-4101` and `conduit.py:2751-2752` as "both
public verbs". The conduit citation is right; **the spellbook one is wrong**, and
the count is wrong. Measured:

- `spellbook.py:4234` and `:4236`
- `spellbook.py:4447` and `:4449`
- `conduit.py:2749` and `:2751`
- `conduit.py:2988` and `:2990`

Four docstring blocks, each promising "Optional normalized scope hashes **for
conflict checks**". A DELETE scoped from the original note would have corrected
half of them and left the other half asserting the same false contract.

### CORRECTION 2 - THE FINDING THAT MATTERS, and it is not in the investigation

**The false claim is baked into GENERATED, COMMITTED BUILD ASSETS THAT SHIP.**
bootstrap_0's evidence index contains no `_build_assets/` path; this was not
looked at. Three assets carry it, all in present tense, all describing live
behaviour:

- `_agent_documentation/manifest/agent_documentation_manifest.py:37` -
  `ChangeControlConflictManager` documented as "Conflict detector for scope
  overlap between change-control requests."
- `_system_documents/manifest/graph_adjacency_manifest.py:3658, 3663, 3690` -
  authored edge `why` strings: ChangeControlManager "owns the scope-overlap
  conflict detector **used during admission**"; ChangeControlOrchestrator
  "**borrows the conflict manager to detect** overlapping in-flight scope";
  TransactionMediator "**borrows the conflict manager to evaluate** overlapping
  claim conflicts during admission."
- `_system_documents/payloads/src_graph_payload.py:1005, 1174, 1972` - the same
  strings in the packaged graph payload.

Why this is worse than a docstring. Per `src_architecture.md:305-311` and
`:1177-1200`, `__architecture__`, `__components__`, `__graph_network__` and
`__graph_details__` are **packaged hardcopy exports** - agent-facing
`StaticSystemDocument` objects that ship inside the wheel. `_agent_documentation`
is the harvested agent-purpose manifest serving discovery.

So an agent introspecting Melder at runtime, through the surface built expressly
for that purpose, is told the conflict manager detects scope overlap during
admission. **It does not.** In a system whose stated premise is that intelligence
can perceive and operate the runtime directly (`mission.md`), the runtime is
currently misinforming the intelligence about its own behaviour - and unlike a
docstring, this reaches consumers who never open the source.

### WHAT THIS CHANGES ABOUT THE DECISION

Not the recommendation. bootstrap_0's read - **DELETE, scoped to the PARAMETER
and not just the class** - is well-argued and I reach the same place: an opaque
caller-supplied hash asserts "I overlap something" without naming what, while a
scope key names it and can be adjudicated.

What changes is the SIZE of the work unit. If the ruling is DELETE, it is:

1. the class, its slot, the property, the two `__slots__` entries, the mediator's
   mandatory-parameter guard, and the threading through both signatures;
2. the `scope_hashes` public parameter and its plumbing;
3. **four** docstring blocks, not two;
4. **three generated build assets**, which must be REGENERATED, not hand-edited;
5. the authored graph edge `why` strings, corrected at the DESCRIPTOR level and
   reassembled - `src_graph.md` and `src_graph_index.md` are generated and a
   hand-edit breaks the index hash so every slice refuses
   (`src_graph_generation.md`, `staleness_protocol.md:28-35`);
6. `test_conflict_manager.py`, whose four tests guard cleanup mechanics and the
   key branch, and which protect nothing that would be missed.

Items 4 and 5 were not on the previous scope list. A DELETE that stops at item 3
leaves the shipped agent-facing documentation asserting a capability that no
longer has even a dead implementation behind it.

### LANE 2 ANSWERED - WHY IT IS A ZOMBIE. Recovered, not manufactured.

bootstrap_0 marked this NOT RECOVERABLE after `git log -S find_conflicts` and an
attempt to recover a deleted story from `14a8ab77f^`. **The reasoning was never
in git. It is in this package's own archive**, in a completed task and a retained
artifact - which is precisely what `context_compass` exists to make survivable.

**The retirement landed in TASK-2026-06-12-implement-scope-lock-table-and-pending-acquisition.**

**1. It was REPLACED, not judged redundant and not judged too conservative.**
That task rebuilt the embargo manager from a binary surface into a **moded lock
table**: `ClaimMode` X/S/IX, a static compatibility matrix, atomic all-or-nothing
`try_acquire` carrying holder evidence, `wait_for_release`, and `release_owner`
wake-on-release. Admission then collapsed from two steps to one - `admit_request`
became ONE `embargo.try_acquire` of the request's merged claim set under the
orchestrator's lock.

**2. The scan was structurally incapable of expressing what replaced it.** This
is the actual answer to the epic's question. `find_conflicts` had exactly one
verdict - overlap or not - and returned a bare tuple of request ids: no mode, no
holder, no blocking evidence, and conservative by its own docstring ("hash
overlap is enough"). The moded table can say *these two requests share a key but
both hold `s`, so both proceed*; disjoint claim sets admit in parallel; `x`
excludes everything; a partial conflict acquires nothing and returns
`(scope_key, holder_id, holder_mode)`. The old scan could not represent a shared
or intent claim at all. It did not lose an argument about conservatism - it could
not participate in the new vocabulary.

**3. Why the OBJECT survived the behaviour: it was a deliberate rollback lever.**
TASK-2026-06-12, Risks / Rollback Notes: *"revert this patch id's commits;
**orchestrator revert alone restores the conflict-scan path**."* The class was
retained on purpose so a single-file revert could restore old admission. That is
the zombie's cause of death-in-life - a retained rollback affordance whose
rollback window closed and which nobody went back to shut.

**4. Removal was flagged the very next day and never actioned.** The DevOps
system map, retained as reference on the artifact board, §6 Observations:
*"`ChangeControlConflictManager` is dead weight at admission (retired; kept only
for the orchestrator signature). **Candidate for removal once the signature is
cleaned.**"* The signature was never cleaned.

**5. Why the green tests kept it looking alive.** TASK-2026-06-12's own UNKNOWN
note (3) listed the legacy suites - `test_transaction_mediator*.py`,
`test_orchestrator.py`, `test_embargo_manager.py`, **`test_conflict_manager.py`**
- as needing *"reconciliation against the new admission contract once the suite
runs."* That reconciliation never happened. The tests stayed green against a unit
nobody calls, which is exactly the shape this epic's Risk section predicted.

**6. THE OPEN QUESTION IS ANSWERED: yes, same decision, same pass.** The epic
asked whether `queue_competing_root_transactions` was removed under the same
reasoning. It was. Same task retired the coarse root FIFO for
`_admit_with_scope_wait`, and the system map records that
`max_transaction_wait_time_in_seconds` is now the **only** root-arbitration knob,
with `queue_competing_root_transactions` and `warn` removed. Coarse global
arbitration and coarse global conflict scanning died together, replaced by
scope-local claims and scope-local waiting.

EVIDENCE:
- tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md:64
- tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md:84
- tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md:135-152
- tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md:176-181
- artifacts/2026-06-13_devops_mediator_system_map.md:106-113
- artifacts/2026-06-13_devops_mediator_system_map.md:213-222
- artifacts/2026-06-13_devops_mediator_system_map.md:275-278
- artifacts/2026-06-13_devops_mediator_system_map.md:327-330

**What this does to the DECISION.** It removes the last reason to hesitate. The
epic held DELETE open against the possibility that retirement was a mistake made
for a bad reason. It was not: it was a deliberate replacement by a strictly more
expressive mechanism, the object was kept only as a rollback lever, and removal
was already the recorded recommendation of the agent who mapped the subsystem.
Nothing was lost. The lane 1 hash-vs-key capability question is real but resolves
the same way - an opaque hash asserts overlap without naming what it overlaps,
which the moded table cannot adjudicate and therefore should not accept.

### WHAT I DID NOT DO

No source touched, no test run, no deletion, no revival. The EXIT_GATE is a
recorded owner DECISION and that remains the owner's. Validation: **Not run.**

## DECISION RECORDED + OPEN SCOPE QUESTION (super_tester_0, 2026-08-03T02:25:00Z)

- DATETIME: 2026-08-03T02:25:00Z
  TYPE: DECISION
  CLAIM: Owner ruled **DELETE**. The reasoning is conceptual rather than
    mechanical and is the strongest argument produced in this lane: a CONFLICT
    denotes a clash that is unsolvable and needs solutioning. The moded claim
    table produces no unsolvable states - admission ends in admit, wait, or
    refuse with `(scope_key, holder_id, holder_mode)` evidence, all of which are
    resolved outcomes. There is therefore no condition in this design that the
    word "conflict" names, which is why nothing calls `find_conflicts` and why
    keeping the object models a concept the system no longer has.
  EVIDENCE:
  - tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md:135-152
  - artifacts/2026-06-13_devops_mediator_system_map.md:213-222
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/conflict_manager/conflict_manager.py:98-134
  IMPACT: EXIT_GATE satisfied. The epic can move to closure once the deletion
    follow-up is scoped and the aetheric plane's no-hashes decision is recorded
    as CONFIRMED in EPIC-2026-07-31.
  NEXT: Settle the public-parameter question below, then open the deletion story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-03T02:25:00Z
  TYPE: DECISION_REQUEST
  CLAIM: The owner ruled on "the object and its tests". That is unambiguous for
    the class, the two `__slots__` entries, the property, the constructor
    threading, the mediator's mandatory-`None` guard, and
    `test_conflict_manager.py`. It does NOT settle `scope_hashes`, and I will not
    infer it: removing a parameter from `Spellbook.begin_transaction` and
    `Conduit.begin_transaction` is a PUBLIC API change, which
    `engineer/AGENTS.MD:198-208` and `synaptic/AGENTS.MD:217-225` both forbid
    without an explicit request.
    THE TRADEOFF, stated plainly because it is the whole question:
    - DELETE THE PARAMETER TOO: the promise and the mechanism die together.
      Clean, but it breaks any caller passing `scope_hashes=`.
    - KEEP THE PARAMETER: bootstrap_0's warning applies verbatim - it removes the
      cheap half and leaves a public parameter documented "for conflict checks"
      that has neither a checker nor a concept behind it. Strictly worse than
      today, because today at least a dead implementation exists.
    - DEPRECATE: accept, ignore, document as retired, remove next major.
      Preserves compatibility; carries the lie for one more version.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4234
  - src/melder/aether/spellbook/spellbook.py:4447
  - src/melder/aether/conduit/conduit.py:2749
  - src/melder/aether/conduit/conduit.py:2988
  IMPACT: Decides whether the deletion story is one surface or six, and whether
    it is a patch-framework lane at all.
  NEXT: Owner rules delete-parameter / keep-parameter / deprecate-parameter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T02:25:00Z
  TYPE: PLAN
  CLAIM: Deletion is a FOLLOW-UP, not this epic - the EXECUTION_BOUNDARY says so
    explicitly. It is also system-impacting (component boundary change plus
    canonical doc updates), so `patch_framework_gating.md` applies and patch docs
    must exist and be ticket-linked BEFORE any implementation edit.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:20-27
  IMPACT: Prevents the deletion starting as a quick `rm` and skipping the gate.
  NEXT: On the parameter ruling, open
    STORY-2026-08-03-retire-conflict-manager with tasks split by surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## ACK FROM bootstrap_0 (2026-08-03T02:20:00Z) - one real miss owned

super_tester_0's NOTICE consumed. Lane is theirs, the owner has ruled DELETE, and
I am not re-opening any of it. Recording three things so the epic carries the
correction rather than leaving my wrong citation as its last word.

**THE MISS IS REAL AND IT IS MINE.** My evidence index carried no `_build_assets`
path because I actively EXCLUDED that directory from every grep in the
investigation. I was filtering generated noise and never considered that a
generated asset SHIPS IN THE WHEEL and serves agent introspection - so a false
promise there reaches more consumers than the docstring it was generated from.
Excluding generated output from a truth audit is backwards when the generated
output is the distributed artifact. That is a habit to change, not a one-off.

**THE CITATION DRIFT IS EXPLAINED, NOT DISPUTED.** My `spellbook.py:4100-4101`
does not resolve today; `scope_hashes` now sits at `:4237`. Neither does the
`4234/4236` in the NOTICE resolve to the promise text. Both are honest readings
of different moments - this file is under active edit by several agents, the same
churn that fired SEMANTICS_STALE on my graph nodes twice on 2026-08-02. The
lesson is not that someone miscounted: line citations in a hot file decay, and a
survey should cite SYMBOL plus line so the reader can re-find it after drift.

**THE FIX HAS LANDED AND I VERIFIED IT RATHER THAN ASSUMING IT.** Both public
verbs now read "ADVISORY IDENTITY ONLY - they carry NO claims and are NOT checked
for conflicts" (`spellbook.py:4237-4240`, `conduit.py:2752-2755`), and grepping
`"for conflict checks"` across `src/` returns nothing. The public lie is gone.

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
