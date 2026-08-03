# Task: Survey the MutationResearch transactional surface

## Metadata
- Task ID: TASK-2026-07-31-survey-mr-transactional-surface
- Story ID: STORY-2026-07-31-subsystem-transactional-survey
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: completed
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-08-02T19:35:00Z

## SELF-CONTAINED BY DESIGN
You do NOT need the history of the investigation that produced this task. Read
the epic's Problem section for the why, then work only from the reads below.
This task is READ-ONLY. Do not change code.

## Purpose
Establish what in MutationResearch actually needs transactionalizing, so the
AethericMediator plane can be wired to it later without guessing.

## Starting Facts (verified 2026-07-31; re-verify, do not trust)
MutationResearch currently protects concurrent structural mutation with:
one-way lock order (spellbook -> emission -> root -> set -> child/crystallizer), a dedicated _emission_lock added for BUG-031, single-residence law (BUG-048), and hand-written failure compensation (_rollback_claim; mid-loop join refusal restores all detached nodes in original order). Proven under an 8-thread stress run: 960 identities, 61 lanes, gapless journal.

## Required Reads
- `context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md`
  (Problem, Component Split, Key Design Decisions)
- src/melder/mutation_research/ -> research_set.py, residence_registry.py, mutation_research.py

## Questions To Answer (each with file:line evidence)
1. What STRUCTURAL MUTATION verbs does MutationResearch expose or perform? Name them.
2. What protects each today, and what does that protection NOT cover?
3. What SCOPE KEYS would express those mutations? Propose concrete strings using
   the namespaced flat form (e.g. `mr:<unit>:<id>`).
4. What MODE does each need - `x` exclusive, `s` shared, or `ix` intent?
   Justify any `ix`; do not use it by default.
5. What are MutationResearch's "BASIC CONDITIONS" - the state it would emit to the plane
   when it becomes enabled and active? (Owner constraint 6.)
6. Is there any protection here that CANNOT be expressed as scope claims? That is
   a first-class finding, not a failure - record it loudly.

## Acceptance Criteria
- All six questions answered with `path:start-end` evidence.
- Proposed scope keys and modes are concrete, not descriptive.
- Any inexpressible protection is recorded as a CONFLICT note.
- No code changed.

## Applicable Anti-Patterns
- [x] No proposing a design; this is a survey.
- [x] No promoting a doc claim to FACT without opening the source.
- [x] No code changes under a read-only task.

## Validation / Test Approach
Not run - read-only survey. Verification performed instead: 13 load-bearing
`path:line` citations re-resolved against source programmatically, 0 mismatches.

## SURVEY FINDINGS (bootstrap_0, 2026-08-02T19:35:00Z)

Read-only. No code changed. Third and last of the three subsystem surveys.
Starting Facts re-verified from source rather than trusted; all of them hold.

### Q1. STRUCTURAL MUTATION VERBS

**Root (`mutation_research.py`)** - lifecycle `configure` (`:551`), `activate`
(`:587`), `deactivate` (`:731`); set creation `create_research_set` (`:804`);
hydration `load_recorded_composition` (`:905`); campaign/ancestry state
`set_active_campaign` (`:1007`), `clear_active_campaign` (`:1040`),
`stage_ancestry` (`:1102`), `clear_staged_ancestry` (`:1149`); pass-through
recording `record_world_entry` (`:1178`), `record_promotion` (`:1254`); group
`register_group` (`:3328`), `recompose_group` (`:3393`); synthesis
`synthesize_candidate` (`:2911`).

**Set (`research_set/research_set.py`)** - `create_lane` (`:974`),
`register_spell` (`:1090`), `register_group` (`:1226`), `recompose_group`
(`:1378`), `record_world_entry` (`:1610`), `record_promotion` (`:1748`),
`attach` (`:1813`), `detach` (`:1902`), `join` (`:1963`), `archive` (`:2166`),
`snapshot_network` (`:2224`), `restore_network` (`:2323`),
`set_lane_type_enforcement` (`:440`).

**Residence (`research_set/residence_registry.py`)** - `claim` (`:123`),
`transfer` (`:178`), `_rollback_claim` (`:232`).

### Q2. WHAT PROTECTS EACH, AND WHAT IT MISSES

**MR IS THE BEST-PROTECTED OF THE THREE SUBSYSTEMS SURVEYED, and the survey
should say so plainly.** Crystallizer had an unclaimed graft lane; Nexus had a
snapshot race at the entry of its own fan-out. MR has neither. What it has
instead is a stated, honoured lock order and one genuinely atomic primitive.

**The lock order is documented and one-way:** emission -> root -> set ->
crystallizer (`mutation_research.py:67-69`, restated `:87-94`), with
set -> child beneath it (`research_set.py:66`). The reason is recorded rather
than assumed: set constructors fire `on_mutation` while the ROOT lock is held,
so any path that can emit while holding the root must take the emission lock
FIRST (`:809-812`). That is the BUG-031 fix and it is a real ordering law, not a
comment.

**`ResidenceRegistry.transfer` (`:178-231`) is already a claim table in
miniature.** Its contract is TWO-PHASE ALL-OR-NOTHING: every identity is checked
for residence first, and only if all are resident are any repointed; one
non-resident identity raises `KeyError` with NOTHING moved. The full
check-then-repoint runs under one lock, so no reader observes a half-transferred
set. This is exactly the semantics `ClaimTable.try_acquire` provides, arrived at
independently - which is the epic's whole thesis in one method.

**GAPS:**

1. **COMPENSATION IS HAND-PLACED AT ONE SEAM, NOT SYSTEMATIC.**
   `register_spell` (`research_set.py:1205-1220`) reads:

       self._residence.claim(spell_id, target.lane_id)
       try:
           target._add_node(node)
       except Exception:
           self._residence._rollback_claim(spell_id, target.lane_id)
           raise
       self._journal.record(...)
       self._snapshot_locked()

   The rollback covers exactly the claim/add seam, and the in-line comment says
   why: "lanes are handed out live, so a direct terminal-state call can race
   between the claim and the add under real threads - a refused add must not
   strand the claim (partition corruption)." That is a bug someone found and
   patched precisely. But NOTHING downstream is compensated: if
   `self._journal.record(...)` raises after `_add_node` succeeded, the node is in
   the lane and the residence claim is held with no journal entry, and
   `_snapshot_locked()` never runs. The window is narrow and the operations are
   local, but the pattern is "compensate where a bug was observed" rather than
   "every step has an inverse". A plane that unwinds by policy would cover the
   whole verb rather than one seam of it.

2. **THE COMPOSITION SNAPSHOT CAN TEAR ACROSS SETS.**
   `_emit_research_composition` (`mutation_research.py:~3899-3918`) holds
   `_emission_lock` for build-and-publish together, which is what makes emission
   ordered - a paused emitter cannot publish a stale composition over a newer
   one, exactly as documented. But the payload comes from
   `describe_research_composition` (`:873-903`), which takes the ROOT lock and
   then calls `research_set.describe_composition()` per set, each of which takes
   its own set lock. The emission lock orders EMITTERS; it does not freeze the
   sets. So the published composition is internally consistent per set and may
   still mix set A at one version with set B at a later one. Whether that matters
   depends on whether any consumer reasons across sets - the MR restore
   preflight (`MutationResearchCompositionStrategy`) checks organization against
   residence WITHIN the payload, so a torn payload could produce a drift warning
   that describes no real drift.

3. **`deactivate` (`:731`) does not quiesce.** It flips the activated flag;
   in-flight set verbs are not drained and emissions already past the
   `if not self._activated: return` guard proceed. Same class as Nexus's gate
   population problem, milder because the guard is checked twice (once outside
   and once inside the emission lock).

### Q3. SCOPE KEYS

| mutation | scope key(s) |
| --- | --- |
| set creation / removal | `mr:set:<set_name>`, `mr:set_registry` |
| lane creation | `mr:set:<set_name>`, `mr:lane:<lane_id>` |
| register_spell / register_group | `mr:set:<set_name>`, `mr:lane:<lane_id>`, `mr:identity:<spell_id>` |
| attach / detach | `mr:set:<set_name>`, `mr:lane:<lane_id>` |
| join (residence transfer) | `mr:set:<set_name>`, `mr:lane:<source_lane_id>`, `mr:lane:<target_lane_id>` |
| recompose_group | `mr:set:<set_name>`, `mr:group:<group_id>` |
| archive lane | `mr:lane:<lane_id>` |
| snapshot / restore network | `mr:set:<set_name>` |
| composition emission | `mr:composition` |
| hydration (`load_recorded_composition`) | `mr:set_registry`, `mr:composition` |
| campaign / staged ancestry | `mr:campaign`, `mr:ancestry` |
| lifecycle | `mr:lifecycle` |

### Q4. MODES

| scope key | mode | justification |
| --- | --- | --- |
| `mr:set:<set_name>` | **ix** | A set is the PARENT of its lanes. Registering a spell is piece-work beneath the set; two registrations into DIFFERENT lanes of the same set have no reason to serialise. Parent-scope marker, same shape as Nexus's ACL fan-out. |
| `mr:lane:<lane_id>` | **x** | The unit actually mutated - nodes are added, tips move, residence repoints. |
| `mr:identity:<spell_id>` | **x** | The single-residence law (BUG-048, `research_lane.py:146`) says one lane owns an identity at a time. That law IS an exclusive claim on the identity, stated in domain terms. |
| `mr:set_registry` | **x** for create/remove, **ix** while hydrating | Hydration swaps the whole registry; set creation is a whole-unit write. |
| `mr:group:<group_id>` | **x** | Recomposition rewrites the group. |
| `mr:composition` | **x** | The replace-on-emit publication - by definition one writer, which is what `_emission_lock` already enforces. |
| `mr:campaign`, `mr:ancestry` | **x** | Root-held mutable state, small and singular. |
| `mr:lifecycle` | **x** | activate/deactivate reshapes everything beneath. |
| read/view verbs (`residency_view`, `history`, `walk`, the `*_view` family) | **s** | Many readers coexist and are excluded by any `x` holder. |

**`ix` IS EARNED at `mr:set:<set_name>`** for the same structural reason it was
earned in Nexus: real parent/child work where disjoint children must stay
parallel. Note the difference from crystallizer, which earned none - the three
subsystems are not inconsistent, they are shaped differently, and a survey that
forced one answer across all three would be wrong about at least two of them.

### Q5. BASIC CONDITIONS ON ENABLE

`activate` (`mutation_research.py:587-730`) is the moment, and its ORDER is
itself a basic condition worth emitting, because it encodes BUG-035: hydration
runs BEFORE the activation flip, so live research recorded through the
documented seam can never race the registry swap and be clobbered. What the
plane should receive:

1. `mr.activated = true`, `mr.id`.
2. `unrestricted_module_mutations` (default **False**) and
   `lane_type_enforcement` (default **False**) -
   `mutation_configuration.py:598-599`. `lane_type_enforcement` is propagated to
   every set at activation (`_propagate_lane_type_enforcement`), so the plane
   sees one policy governing many claim targets.
3. The set-name registry and, per set, its lane ids - this is the parent/child
   map every `ix`/`x` pair above is built on. Without it the plane cannot tell
   which lane belongs to which set.
4. The residence partition size (`resident_count`) - the invariant that must not
   change across a `join`, since `transfer` repoints without changing the count.
5. `hydrate_from_record` posture and whether hydration ran, because a hydrating
   root holds `mr:set_registry` in a way a steady-state root does not.
6. The lock-order law itself, as a declared constraint: emission -> root -> set
   -> crystallizer. If the plane ever acquires claims on MR's behalf it must not
   invert it.

### Q6. PROTECTION THAT CANNOT BE EXPRESSED AS SCOPE CLAIMS

**CONFLICT 1 - LOCK ORDER IS NOT A CLAIM ORDER, AND CLAIMS DO NOT ENFORCE IT.**
This is the important one and it is specific to MR. The subsystem's central
safety property is a declared ONE-WAY LOCK ORDER
(`mutation_research.py:67-69`, `:87-94`, `research_set.py:66`): emission ->
root -> set -> crystallizer. A scope-claim plane grants SETS of scopes
atomically; it says nothing about the order in which a holder subsequently takes
real mutexes inside its own code. A transaction could hold every correct claim
and still invert emission/root and deadlock, because the deadlock lives below the
claim layer. Claims prevent two holders touching the same scope; they do not
prevent one holder acquiring its own locks in the wrong sequence. If MR is wired
to the plane, the lock order remains a hand-maintained invariant, and the plane
will give a false sense that concurrency is now "handled".

**CONFLICT 2 - THE EMISSION LOCK GUARDS AN ORDERING, NOT A SCOPE.**
`_emission_lock` exists so a paused emitter cannot publish a stale composition
over a newer one - a LAST-WRITER-WINS ordering guarantee across time. A claim on
`mr:composition` gives mutual exclusion during a transaction, which is a
different property: it stops two emitters overlapping, but it does not stop a
slow emitter that acquired, built a payload, released, and then published late.
Expressing the emission as a claim would require the publish to happen INSIDE the
claim - which is exactly what the emission lock already does, and is therefore a
case where the plane should defer to the existing mechanism rather than replace
it.

**NOT a conflict:** Gaps 1 and 2 from Q2 are both expressible. Hand-placed
compensation is precisely what `OutcomePolicy.UNWIND` and registered rollback
actions generalise. The torn composition snapshot is fixed by holding
`mr:set:*` (or the `ix` parent plus each child) across the describe walk, which
is an ordinary all-or-nothing acquisition.

### CROSS-SUBSYSTEM NOTE (all three surveys now complete)

The epic's thesis was that three subsystems solved one problem three ways. That
holds, and the three answers are now legible side by side:

- **Crystallizer** answered with a GLOBAL EXCLUSIVE GATE (one load at a time,
  process-wide) plus best-effort teardown. Coarse, simple, and it leaves the
  graft lane unclaimed entirely.
- **Nexus** answered with PER-UNIT GATES plus a hand-rolled
  block/drain/refresh/reopen choreography. Finer-grained, and it reintroduced a
  snapshot race at its own entry.
- **MR** answered with a DECLARED LOCK ORDER plus one genuinely atomic
  two-phase primitive (`transfer`) and hand-placed compensation. The most
  disciplined of the three, and the only one whose central invariant the plane
  CANNOT absorb.

That last point is the finding worth carrying into the wiring story: the plane
subsumes crystallizer's gate and Nexus's choreography, but it does NOT subsume
MR's lock order. Wiring MR is therefore not a migration, it is an addition on
top of an invariant that stays hand-maintained.

### Answers-to-criteria checklist
- [x] All six questions answered with `path:line` evidence.
- [x] Scope keys and modes concrete; `ix` used once and justified structurally.
- [x] Inexpressible protection recorded as CONFLICT notes (two).
- [x] No code changed.
- [x] No design proposed.

### Reads performed
`mutation_research.py` (class contract, lock-order law, activate, emission,
describe_research_composition, public surface), `research_set/research_set.py`
(threading contract, register_spell compensation, join contract, public
surface), `research_set/residence_registry.py` (claim, transfer, rollback),
`research_set/research_lane.py` (single-residence law),
`mutation_configuration.py` (schema + defaults), and the epic's Problem /
Owner Constraints.

## Notes
- (append findings here as they land, per the Ticket Microcycle)

## Context / Handoff Summary
Read-only survey of MutationResearch feeding the AethericMediator wiring story. Answer the
six questions with evidence; propose scope keys and modes; flag anything that
cannot be expressed as a claim.
