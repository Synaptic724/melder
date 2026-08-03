# Task: Survey the Nexus / Rift transactional surface

## Metadata
- Task ID: TASK-2026-07-31-survey-nexus-transactional-surface
- Story ID: STORY-2026-07-31-subsystem-transactional-survey
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: completed
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-08-02T19:00:00Z

## SELF-CONTAINED BY DESIGN
You do NOT need the history of the investigation that produced this task. Read
the epic's Problem section for the why, then work only from the reads below.
This task is READ-ONLY. Do not change code.

## Purpose
Establish what in Nexus / Rift actually needs transactionalizing, so the
AethericMediator plane can be wired to it later without guessing.

## Starting Facts (verified 2026-07-31; re-verify, do not trust)
Nexus / Rift currently protects concurrent structural mutation with:
RiftGate + RiftGateController (per-Rift admission, drain, entry-mode), instance RLocks, config-backed drain via projection_refresh_gate_enabled / _timeout_seconds / _poll_interval_seconds, and FrameACLConfigurationChain.rollback_to_configuration(id) which is savepoint-shaped.

## Required Reads
- `context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md`
  (Problem, Component Split, Key Design Decisions)
- src/melder/nexus/ -> nexus.py, rift/rift_gate/rift_gate.py, rift/rift_gate_controller/, acl/frame_acl_configuration_chain.py

## Questions To Answer (each with file:line evidence)
1. What STRUCTURAL MUTATION verbs does Nexus / Rift expose or perform? Name them.
2. What protects each today, and what does that protection NOT cover?
3. What SCOPE KEYS would express those mutations? Propose concrete strings using
   the namespaced flat form (e.g. `nexus:<unit>:<id>`).
4. What MODE does each need - `x` exclusive, `s` shared, or `ix` intent?
   Justify any `ix`; do not use it by default.
5. What are Nexus / Rift's "BASIC CONDITIONS" - the state it would emit to the plane
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
Not run - read-only survey. Verification performed instead: every `path:line`
citation in the findings was re-resolved against source programmatically (13 in
range; the seven load-bearing ones checked for the symbol they are cited for),
0 mismatches.

## SURVEY FINDINGS (bootstrap_0, 2026-08-02T19:00:00Z)

Read-only. No code changed. Starting Facts re-verified from source, not trusted.

READ THIS FIRST if you are surveying MR next: my crystallizer survey originally
asserted `ix` means "escalate later to exclusive" and used that to refuse `ix`
everywhere. That was WRONG - both `ClaimMode` definitions say `ix` is the
PARENT-SCOPE MARKER for hierarchical claims. Correction is filed on
TASK-2026-07-31-survey-crystallizer-transactional-surface. This survey uses the
correct meaning, and Nexus is the subsystem where `ix` genuinely earns its place.

### Q1. STRUCTURAL MUTATION VERBS

**(a) Rift lifecycle** - `create_rift` (`nexus.py:882`), `add_rift` (`:974`),
`remove_rift` (`:1110`).

**(b) ACL revision** - `insert_head_frame_acl_configuration` (`nexus.py:2261`),
`register_named_frame_acl_configuration` (`:1971`),
`register_frame_acl_profile` (`:1637`), `remove_frame_acl_profile` (`:1702`);
chain-level `insert_head_configuration`
(`frame_acl_configuration_chain.py:327`), `select_current_configuration`
(`:368`), `rollback_to_configuration` (`:385`), `trim_tail` (`:424`);
container-level `rollback_view_configuration` / `rollback_command_configuration`
/ `rollback_codegen_configuration` (`frame_acl_container.py:875`, `:905`,
`:935`).

**(c) Projection refresh fan-out** - `_refresh_rift_projection_sets_for_frames`
(`nexus.py:2491`), reached from `_on_frame_acl_changed` (`:2579`) via the
`change_callback` wired at `:280`. Also `create_frame_projection_sets`
(`:2187`) and `create_frame_projection_sets_for_rift` (`:2308`).

**(d) Gate control** - `enable_rift_gate` (`:1343`), `disable_rift_gate`
(`:1375`), `close_and_wait_rift` (`:1407`), `set_rift_gate_entry_mode` (`:1559`),
`set_all_rift_gate_entry_mode` (`:1591`); controller-level `enable_all` /
`disable_all` / `close_and_wait_until_rift_free`
(`rift_gate_controller.py:278`, `:288`, `:227`).

**(e) Frame link / nexus frames** - `authorize_frame_link_for_rift`
(`nexus.py:2686`), `create_nexus_frame_for_rift` (`:2632`),
`Rift.create_frame_link`.

**(f) Subsystem lifecycle** - `enable` (`:701`), `disable` (`:749`).

### Q2. WHAT PROTECTS EACH, AND WHAT IT MISSES

**START WITH WHAT IS ALREADY RIGHT**, because a survey that only lists defects
misleads the wiring story:

- `add_rift` (`nexus.py:998-1024`) performs id-collision, name-collision,
  target-frame-budget AND active-rift-cap checks **and** the registry insert
  under ONE `self._lock`. The cap (`_validate_active_rift_budget`, `:3138`,
  called at `:1005`) is genuinely atomic. No check-then-act there.
- `RiftGate.admit_ticket` (`rift_gate.py:227`) already closed the
  check-then-register drain race - ticket-first admission, explicitly the same
  fix class as the conduit CreationGate change of 2026-07-12. The plane must not
  re-open this by admitting before ticketing.

**NOW THE GAPS.** All five live in one method,
`_refresh_rift_projection_sets_for_frames` (`nexus.py:2491-2588`), which is the
coordinated block/drain/refresh/reopen the epic describes. Its shape:

    with self._lock:
        rifts = list(self._rifts_by_id.values())      # :2512 - snapshot, lock RELEASED
    impacted_rifts = [...]                            # computed UNLOCKED
    try:
        for rift in impacted_rifts: self.disable_rift_gate(rift.id)
        for rift in impacted_rifts: self._wait_until_rift_gate_is_idle(...)
        for rift in impacted_rifts: rift.refresh_runtime_projections(...)
    finally:
        for rift_id in disabled_rift_ids:
            try: self.enable_rift_gate(rift_id)       # :2575
            except Exception: pass                    # :2576

1. **SNAPSHOT-THEN-ACT ACROSS AN UNLOCKED WINDOW.** The Nexus lock is taken only
   to copy the rift registry (`:2512`) and released immediately. `add_rift`
   takes that same lock (`:998`). A Rift registered AFTER the snapshot but
   during the drain/refresh is not in `impacted_rifts`, receives no gate
   disable, no drain and no refresh. If it carries the changed frame it can
   serve projections built outside the coordinated window. This is the exact
   failure the fan-out exists to prevent, reintroduced at its own entry.

2. **THE BLOCK IS SEQUENTIAL, NOT ATOMIC.** Gates go down one at a time in a
   loop. Between the first and last `disable_rift_gate` there is a window where
   some impacted Rifts are blocked and others are still admitting.

3. **DRAIN TIMEOUT RAISES MID-FAN-OUT.** `_wait_until_rift_gate_is_idle`
   (`:2466`) raises `RuntimeError` at its deadline (`:2487`). Because the drain
   loop precedes the refresh loop, a timeout on Rift 3 aborts before ANY refresh
   runs - but a failure inside the refresh loop leaves earlier Rifts refreshed
   and later ones not. There is no compensation: the `finally` reopens gates and
   nothing else. Partial refresh means some Rifts answer from the new ACL
   revision and some from the old, which is precisely the cross-Rift version of
   the inconsistency `FrameProjectionSet`'s generation marker prevents WITHIN a
   Rift. There is no equivalent guard ACROSS Rifts.

4. **REOPEN SWALLOWS EVERY ERROR** (`:2575-2576`). A gate that fails to reopen
   stays disabled with no record that it did. Structurally identical to
   crystallizer's `_teardown_built`, and it fails the same way: the recovery
   path cannot report what it failed to recover.

5. **NOTIFY-BEFORE-VALIDATE, all three container rollbacks.**
   `frame_acl_container.py:882-885` (and identically `:912-915`, `:942-945`):

       rolled_back = ...rollback_to_configuration(configuration_id)
       self._notify_acl_changed()                       # fan-out runs HERE
       if not isinstance(rolled_back, FrameACLViewConfiguration):
           raise RuntimeError(...)

   The refresh fan-out - block, drain, refresh, reopen, across every impacted
   Rift - completes BEFORE the type check that can raise. The caller sees a
   failure after the world has already moved.

Elsewhere: `FrameACLConfigurationChain` holds one instance lock and
`rollback_to_configuration` (`:385`) simply delegates to
`select_current_configuration` (`:368`), which repoints `_current_configuration_id`
under that lock. It is savepoint-SHAPED (history retained, selection moved) but
it is not a transaction: it has no participants and no undo beyond selecting
again.

### Q3. SCOPE KEYS

| mutation | scope key(s) |
| --- | --- |
| ACL revision on one frame | `nexus:frame_acl:<frame_name>` |
| projection refresh, per impacted Rift | `nexus:rift:<rift_id>` |
| Rift create / add / remove | `nexus:rift:<rift_id>`, `nexus:rift_registry` |
| gate enable / disable / entry-mode, one Rift | `nexus:rift_gate:<rift_id>` |
| gate all-Rift sweep | `nexus:rift_gate:*` via `nexus:rift_registry` |
| frame link authorisation | `nexus:rift:<rift_id>`, `nexus:frame_acl:<frame_name>` |
| nexus frame create | `nexus:frame:<frame_name>` |
| ACL profile register / remove | `nexus:acl_profile:<profile_name>` |
| Rift profile register | `nexus:rift_profile:<profile_name>` |
| subsystem enable / disable | `nexus:lifecycle` |

`nexus:rift_registry` exists so the fan-out can hold membership stable while it
works - see Q4, because that is the whole point.

### Q4. MODES

| scope key | mode | justification |
| --- | --- | --- |
| `nexus:frame_acl:<frame_name>` | **ix** | The fan-out holds the frame's ACL scope as a PARENT while doing per-Rift work beneath it. Two refreshes on DIFFERENT frames must proceed in parallel; a whole-unit writer on this frame must be excluded. Textbook parent-scope marker. |
| `nexus:rift:<rift_id>` | **x** | The unit actually mutated - projections are swapped on this Rift. |
| `nexus:rift_registry` | **ix** held by the fan-out | **THIS IS THE FIX FOR GAP 1.** Holding the registry under `ix` for the whole fan-out excludes `add_rift`/`remove_rift` (which would need `x`) while leaving disjoint per-Rift work parallel. The snapshot stops being a guess. |
| `nexus:rift_registry` | **x** for add/remove | Membership mutation is a whole-unit write. |
| `nexus:rift_gate:<rift_id>` | **x** | One writer decides a gate's admission state. |
| `nexus:frame:<frame_name>` | **x** | Frame creation. |
| `nexus:acl_profile:<name>`, `nexus:rift_profile:<name>` | **x** | Registry writes; independent names stay parallel by key. |
| `nexus:lifecycle` | **x** | enable/disable reshapes everything under it. |
| read-only viewer paths | **s** | Multiple readers coexist; excluded by an `x` holder. |

**`ix` IS EARNED HERE, TWICE**, and both cases are structural rather than
stylistic. The ACL fan-out is definitionally piece-work beneath a parent: one
frame's ACL change, N per-Rift refreshes. And the registry claim is what makes
the snapshot sound. Crystallizer had no such shape, which is why that survey
proposed none - the difference is real, not an inconsistency between the two.

### Q5. BASIC CONDITIONS ON ENABLE

`Nexus.enable` (`nexus.py:701-748`) is the moment: it finalises the
configuration, sets `_enabled = True`, and emits `RecordedUnitState.enabled` to
the crystallizer. What the plane needs, from that method and the configuration
schema (`nexus_configuration.py:133-153`, defaults `:336-338`):

1. `nexus.enabled = true`, `nexus.id`.
2. `projection_refresh_gate_enabled` (default **True**),
   `projection_refresh_gate_timeout_seconds` (**30.0**),
   `projection_refresh_gate_poll_interval_seconds` (**0.1**). The plane inherits
   these deadlines; if it holds claims for the fan-out it must not use a shorter
   bound than the drain it wraps.
3. `max_active_rift_count` and `allow_rift_creation` / `allow_nested_rift_creation`
   / `allow_external_rift_registration` - they decide whether
   `nexus:rift_registry` can ever be claimed for growth.
4. `nexus_frame_mode`, `default_nexus_frame_name`, `auto_create_nexus_frames`,
   `max_nexus_frame_count` - `auto_create_nexus_frames` matters most: it means
   frame creation can happen as a SIDE EFFECT of a Rift operation, so a claim
   plan that only names the Rift will under-claim.
5. The live Rift id set and each Rift's assigned frame names - this is the
   membership the fan-out reads at `:2512`, and the plane cannot compute impact
   without it.

### Q6. PROTECTION THAT CANNOT BE EXPRESSED AS SCOPE CLAIMS

**CONFLICT 1 - parked threads are invisible to a claim table.**
`RiftGate.admit` (`rift_gate.py:195-225`) with `entry_mode == "wait"` parks the
caller on a `threading.Event` (`self._event.wait()`). That thread holds no
claim, requests no claim, and is in no registry the plane can read. It is
waiting on a gate, not on a scope. So the plane can serialise the operations
that OPEN and CLOSE gates, but it cannot see or account for the population
waiting behind one, and cannot include them in any deadlock or fairness
reasoning. Claims and gates are two different waiting mechanisms and the plane
would only own one of them. `entry_mode == "raise"` does not have this problem -
it refuses instead of parking - which suggests the modes differ in more than
politeness and the plane should know which mode each gate is in.

**CONFLICT 2 - best-effort reopen has no failure channel.** Gap 4 again, stated
as a claim-model problem: releasing a scope claim is not the same act as
reopening a gate. The plane can guarantee its own claims are released on exit;
it cannot guarantee `enable_rift_gate` succeeded, and today nothing records that
it did not (`:2576` swallows). A world can therefore end a transaction with all
claims correctly released and a Rift permanently closed.

**NOT a conflict:** everything in Gaps 1, 2, 3 and 5 is expressible. Gap 1 is
fixed by `ix` on `nexus:rift_registry`; Gaps 2 and 3 are fixed by acquiring all
`nexus:rift:<id>` claims in ONE all-or-nothing `try_acquire` instead of a
sequential loop, which is exactly what `ClaimTable` already provides; Gap 5 is
an ordering bug in the caller, not a concurrency-model limitation.

### Answers-to-criteria checklist
- [x] All six questions answered with `path:line` evidence.
- [x] Scope keys and modes concrete; `ix` used twice and justified structurally.
- [x] Inexpressible protection recorded as CONFLICT notes (two).
- [x] No code changed.
- [x] No design proposed - where a claim shape obviously fixes a gap it is named
      as a finding about expressibility, which is what Q6 asks for.

### Reads performed
`nexus/nexus.py` (targeted: lifecycle, rift registry, ACL seams, the refresh
fan-out, capacity guard), `nexus/rift/rift_gate/rift_gate.py` (whole),
`nexus/rift_gate_controller/rift_gate_controller.py` (surface),
`nexus/acl/frame_acl_configuration_chain.py` (chain verbs),
`nexus/acl/frame_acl_container.py` (rollback trio + `_notify_acl_changed`),
`nexus/frame_acl_manager.py` (callback wiring), `nexus/rift/rift.py` (surface),
`nexus/configuration/nexus_configuration.py` (schema + defaults), and the epic's
Problem / Owner Constraints.

## Notes
- (append findings here as they land, per the Ticket Microcycle)

## Context / Handoff Summary
Read-only survey of Nexus / Rift feeding the AethericMediator wiring story. Answer the
six questions with evidence; propose scope keys and modes; flag anything that
cannot be expressed as a claim.
