# Task: Dishka adapter scope placement, untimed scope-semantics parity phase, and the threads sweep

## Metadata
- Task ID: TASK-2026-09-27-dishka-scope-placement-and-parity-phase
- Story: none (owner-directed benchmark work; follows the fairness review)
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T11:41:00Z
- Updated: 2026-09-27T11:54:31Z

## Objective
Owner directive 2026-09-27 (relaying a GPT idea after Astra's audit): keep the dishka mapping for singletons,
bootstrap objects, sessions, request roots/markers and request transients; test moving `Layer1Scope`-`Layer4Scope`
from `Scope.APP, cache=False` to `Scope.SESSION, cache=False`; add untimed correctness assertions (transient
layers not cached, session objects cached, request objects request-local, app singletons shared, dependency
identities correct); rerun the persistent benchmark at 1, 2, 4, 8 and 10 threads against the original mapping;
if material, document both and use the most idiomatic dishka representation for the final comparison.

## Ticket Contract
- ENTRY_GATE: owner directive; the fairness review (TASK-2026-09-27-persistent-gauntlet-fairness-review).
- EXECUTION_BOUNDARY: `benchmarks/testing_other_di/test_real_world_gauntlet.py` (dishka layer-scope switch,
  per-adapter scope probes, the shared verifier), `benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py`
  (untimed parity phase before the timed threads, environment/version line, a parity test); no src edits.
- DEPENDENCIES: dishka 1.10.1, dependency-injector 4.49.1 (VM venv for the rehearsal).
- EXIT_GATE: parity phase green for all three libraries in the VM; both mappings run; edits on the device tree
  byte-identical; the owner runs the 1/2/4/8/10 sweep on his box (the VM has 2 cores).
- FAILURE_ESCALATION: DECISION_REQUEST if the parity phase finds a semantic difference between libraries.

## Scope Boundaries
- In scope: the switch, the probes, the verifier, the config line, the parity test, the rehearsal.
- Extended by the owner ("fix everything we need to fix"): the objects/s label, the cleanup labels, the deadline
  ordering + work validation, the minimal-instrumentation mode, the variant identity checks, the GC/FastAPI wording,
  the cold-import flag - all landed in this task.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directive (2026-09-27T11:41:00Z); worktree first, then the device tree.
- from_state: in_progress
- to_state: review
- transition_reason: Switch, probes, verifier and environment line landed byte-identically after a green VM rehearsal
  (2026-09-27T11:44:54Z); the owner's sweep remains.

## Steps / Checklist
- [x] D1: `GAUNTLET_DISHKA_LAYER_SCOPE=app|session` switch in the dishka builder (default app = original).
- [x] D2: `probe_scopes()` per adapter + shared `verify_scope_semantics()`; untimed call before the timed threads;
  `test_scope_semantics_parity[lib]`.
- [x] D3: config line gains cores, interpreter, GIL state at setup, library versions, the dishka mapping.
- [x] D4: VM rehearsal (parity green x3; both mappings at threads 1-2); device tree; cmp.
- [x] D6 (owner: "fix everything"): objects/s_request_active_min uses inner objects (57/23/18); DI cleanup fields
  labelled "not separately measured" (`_RuntimeOps.cleanup_timed`); deadlines published after the readiness
  barrier with bounded waits/joins and validation (cycles > 0 per worker, window >= 90% of the duration);
  `PERSISTENT_GAUNTLET_INSTRUMENTATION=full|minimal`; `root1 is root2` in every variant-2 callback; cold-import
  flag on the setup time; GC and FastAPI wording rewritten as hypothesis/description; a notes line on what the
  numbers are.
- [ ] D5: owner sweep (1/2/4/8/10 x both mappings); decision on the final mapping.

## Deliverables
- Switchable dishka mapping, parity phase, environment line; the sweep commands for the owner.

## Files / Paths Impacted
- benchmarks/testing_other_di/test_real_world_gauntlet.py
- benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py

## Validation
- D6: VM full+minimal modes x 3 libraries green (3 s runs); device tree lane-parity + scope-parity 8 passed.
- VM (3.14.7t, `-X gil=0`): `test_scope_semantics_parity` 54 assertions x 3 libraries green; both dishka mappings run
  the persistent harness (threads=2, 5 s); full persistent parametrization 9 passed (3 s runs); on the device tree:
  `test_gauntlet_melder_lane_parity.py` + `test_scope_semantics_parity` 8 passed.
- Owner sweep: Not run.

## Risks / Rollback Notes
- Benchmark-only edits; rollback by reverting the two files.

## Applicable Anti-Patterns
- [x] No timed-path change hidden inside the correctness phase (the phase runs once, before the threads).

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: dishka root lock; scope semantics parity; threads sweep.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T11:41:00Z
  TYPE: MEASURE
  CLAIM: Before any edit (VM, 2 cores, 3.14.7t, `-X gil=0`, fastapi_steady, 6 s): dishka's root container takes
    its lock on EVERY parent-scope dependency read, cached singletons included (`Container._get` wraps
    `_get_unlocked` in `with lock`; child containers are built with `lock_factory=None` and route parent keys
    through the parent's `_get`). Unmodified adapter: ~2 root-lock acquisitions per cycle; at 2 threads the
    lock wait is 5.5 s of 11.1 s worker time (50%), and the whole cycle increase (10.9 -> 23.6 us) sits in the
    outer phase. Layers moved to `Scope.SESSION, cache=False`: ~7 acquisitions per cycle (each cached
    singleton read plus BootstrapAObject now goes through the lock separately), lock wait 4.7 s of 11.1 s
    (43%), cycle 13.4 -> 24.0 us. So the contention is dishka's design (root lock per parent access), not the
    adapter's placement of the layers; the placement only trades hold length for acquisition count. Also:
    importing dependency_injector.providers 4.49.1 re-enables the GIL ("has not declared that it can run
    safely without the GIL"); the owner's `-X gil=0` keeps it off "at your own risk".
  EVIDENCE:
  - (VM venv) dishka/container.py:149-215
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:784-806
  - (probes: VM home work/bench/fair/dishka_lock_count.py; output recorded here)
  IMPACT: The sweep decides materiality on the owner's cores; the parity phase decides equivalence.
  NEXT: D1-D3 in the worktree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T11:44:54Z
  TYPE: FACT
  CLAIM: D1-D4 landed on the device tree (cmp byte-identical to the rehearsed worktree). Base module:
    `GAUNTLET_DISHKA_LAYER_SCOPE=app|session` (default app = original) decides where Layer1-4Scope live
    (`cache=False` either way; bootstrap objects stay APP for the root fan-out); every adapter gains an untimed
    `probe_scopes()` (two outer scopes, two requests inside the first, the extra transient group, the app
    singleton from the root); the shared `verify_scope_semantics(ops)` runs 54 assertions - sessions cached
    per outer scope and distinct across scopes, the Layer chain and BootstrapAObject fresh per session, roots
    and markers request-local (distinct across two requests of one session), app singletons one object through
    the root, the sessions and the layer branches, five distinct groups and fifty distinct leaves per root,
    the extra group outside the root and sharing no leaf, every group/root/marker referencing its session.
    Persistent harness: the phase runs once per library before the timed threads (never inside a timed path);
    a `test_scope_semantics_parity[lib]` test; the config line adds the GIL state at setup; a new environment
    line prints interpreter, free-threading build, cpu_count, platform, the three library versions and the
    dishka mapping. All three libraries pass the 54 assertions under both mappings.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py (search `verify_scope_semantics`, `probe_scopes`)
  - benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py (search `_environment_line`)
  IMPACT: Astra's items 2 (unverified equivalence) and 7 (versions/environment unrecorded) are closed by the
    harness itself; item 1 (dishka lock) is measured and switchable; the sweep decides materiality.
  NEXT: D5 - owner runs 1/2/4/8/10 threads for both mappings (commands in the report).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T11:54:31Z
  TYPE: FACT
  CLAIM: D6 landed on the device tree (cmp byte-identical; lane-parity + scope-parity 8 passed there; VM: both
    instrumentation modes run for all three libraries; a 0.3 s window with 10 threads and no warmup now records
    27,933 cycles instead of risking zero). Reporting changes: `objects/s_request_active_min` divides the objects
    built inside the request phase (57/23/18 per cycle) by request_total; dependency-injector's cleanup rows
    print "not separately measured: the adapter has no scope teardown" instead of 0.000ms; the config line gains
    `instrumentation=` and `(cold imports: yes/no)`; a persistent notes line states that worker_active is
    elapsed-in-cycles, objects_min are declared minimums, latencies are saturated-loop completion times.
    Harness changes: measure/end deadlines are computed after every worker passed the readiness barrier and
    published to the workers before the start event; `ready.wait`/`join` are bounded (60 s/120 s) and stuck
    workers raise; the run raises when any worker recorded no cycle or the window is short. Minimal mode records
    cycles, elapsed and lane counts only (about 1 us per cycle less harness work). Every variant-2 callback now
    asserts `root1 is root2`. Docstrings: fastapi_steady described as the thread pattern of a FastAPI-like
    service with no HTTP/I/O; GC drift framed as the hypothesis the bucket mode confirms or rejects.
  EVIDENCE:
  - benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py (search `_STARTUP_TIMEOUT_S`, `add_cycle_minimal`, `inner objects only`)
  - benchmarks/testing_other_di/test_real_world_gauntlet.py (search `_REQUEST_INNER_OBJECTS_PER_ROOT`, `cleanup_timed`)
  IMPACT: Astra's items 3, 4, 5, 6 and 8 are closed in the harness; 1 is switchable and measured; 2 and 7 were
    closed at D2/D3. Open by design: fresh-process repetitions (documented, not automated).
  NEXT: D5 - the owner's sweep; then close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-27T11:41:00Z: IN_PROGRESS. Lock mechanics measured (note above); implementing the switch, probes and
parity phase.
STATE 2026-09-27T11:44:54Z: REVIEW. D1-D4 on the device tree; waiting on the owner's threads sweep (D5) to pick the
final mapping.
STATE 2026-09-27T11:54:31Z: REVIEW. D6 (all audit fixes) on the device tree; only the owner's sweep (D5) and the
mapping decision remain.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
