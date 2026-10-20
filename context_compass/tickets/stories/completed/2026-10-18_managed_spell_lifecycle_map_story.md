

# Story: Read the managed pool surface whole and record its lifecycle map

## Metadata
- Story ID: STORY-2026-10-18-managed_spell_lifecycle_map
- Epic: EPIC-2026-10-18-managed_spell_examples_and_docs
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T21:14:51Z
- Updated: 2026-10-18T21:33:11Z
- Completed: 2026-10-18T21:33:11Z
- Summary: The managed-pool lifecycle is mapped from source and proven by a 19-case probe (81 rows, 0 failed,
  GIL off and on): bind options and refusals, pool composition, the three modes on a miss, leases, release,
  resets, inspection, teardown, settings rebind and transfer. Two findings: stale failure-mode text in two
  system documents (melder_0 told, M2-15) and root-held consumers that release at disposal (owner question).

## User Narrative
As the author of the managed-pool examples and Sphinx page, I want an evidence-backed map of what a managed spell
does at each step of its life, so that every example and every sentence on the page is verified in source.

## Value / MRP Alignment
The UX law (`UX_and_AIX_experiences/AGENTS.md`): examples may only assert behaviour verified in source or proven
by a probe. This story is that verification, done once and recorded where S2 and S3 read it.

## Ticket Contract
- ENTRY_GATE: the attention_board.md row `managed_spell_lifecycle_map` routes here.
- EXECUTION_BOUNDARY: read-only on `src/`, `tests/` and `docs/`; probes run on a VM copy under /tmp; writes to
  this story, the epic, the boards and `artifacts/managed_spell_examples_20261018/`.
- DEPENDENCIES: src_components.md "Component: Managed Spell Pools" (3860-3973) and "Flow: Managed Lease ->
  Release" (8256-8271), the graph slices of the managed files, then the code read whole.
- EXIT_GATE: Notes hold the lifecycle map - bind (options, refusals), conjure (pool composed), lease paths,
  release and lease, reset, refusals, inspection, disposal, transfer and rebind - each with evidence ranges over
  the logic, unknowns explicit, and the public names an example may use (md.* only).
- FAILURE_ESCALATION: code contradicting the system documents - CONFLICT note and ask the owner; a behaviour the
  code leaves unclear - probe it; still unclear - ask the owner.

## Requirements (Functional)
- Each lifecycle step names the public call, its contract and its failure modes, with `path:start-end` evidence.
- The map says which names `melder` exports at its root, so the examples need no submodule import.

## Requirements (Non-Functional)
- Evidence covers the logic described, never a one-line search hit.

## Scope Boundaries
- In scope: the managed-pool sources, their callers on the lease and release paths, existing tests as usage
  evidence.
- Out of scope: changing any of it; defects found are filed.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: exit gate met - every lifecycle step is mapped in Notes with source and probe evidence;
  routine closure by the assigned agent (no reserved owner decision; the RISK goes to the owner walkthrough).

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity (completed) and its release-note section.

## Tasks (Implementation Checklist)
- [x] Slice the component map and the lease/release flow; verify the index first.
- [x] Read managed_spell_quantity.py, release_managed_spell.py, managed_spell_lease.py, managed_spell_mode.py,
      managed_spell_exhausted_error.py whole; the managed parts of existence.py, bind.py, conduit.py,
      creations.py and spellbinder.py.
- [x] Probe anything the code leaves unclear (VM copy).
- [x] Record the lifecycle map in Notes.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Every lifecycle step in the exit gate is mapped with evidence, or marked UNKNOWN with its investigation target.

## Validation / Test Plan
- Probe runs on 3.14t where a reading needs confirmation; outputs saved under the lane's artifact folder.

## UX / API / Data Notes
- Only `md.*` names count as example surface.

## Risks / Mitigations
- melder_0's landing changes spell_id rules (0.2.8257): the map notes what the tree under test does.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No behaviour claim cited to a document or a search hit instead of the code.

## Open Questions
- None yet.

## Decision Log
- None yet.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_spell_examples_20261018/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_2; synaptic_python_developer; prose; this story; 2026-10-18T21:14:51Z
- Published By: UNKNOWN (local backend; no hosting service)
- Independent Review: none requested yet

## Notes
- DATETIME: 2026-10-18T21:14:51Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Descend the hierarchy for the managed pools: the component slice and the lease/release flow, the graph
    slices of the managed files, then the sources whole; record one map, step by step, with evidence over each
    step's logic.
  EVIDENCE: context_compass/system_docs/src_components_index.md:53-53
  IMPACT: S2's examples and S3's page assert only what this map evidences.
  NEXT: Verify src_components_index.md's staleness proof, then slice 3860-3973 and 8256-8271.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T21:31:24Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Read path and probe environment. Sliced src_components "Component: Managed Spell Pools" (3860-3973) and
    "Flow: Managed Lease -> Release" (8256-8271) after verifying the index (line_count 12250, sha256 380279a1...),
    and the graph slices of the three managed modules after verifying src_graph_index (OK; source_sha256 of all
    three equal the files on disk). Read whole: managed_spell_quantity.py, release_managed_spell.py,
    managed_spell_lease.py, managed_spell_mode.py, managed_spell_exhausted_error.py; read the managed parts of
    bind.py, spellbinder.py, conduit.py, creations.py, meld.py, conduit_meld.py, spellspace_meld.py, existence.py
    and scope_ordering_strategy.py. The device VM has CPython 3.10/3.11 only and no route to GitHub or PyPI, so
    the probe runs on CPython 3.14.6t in the cloud workspace over a mirror of src/ and UX_and_AIX_experiences/
    staged as build/melder_2_mirror/s12_mirror.tar.gz (build/ is gitignored; sha256 32ffd3d0..., tree at 0.2.8256
    with melder_0's S1/S2 src in place). Probe: 19 cases, 81 rows, 0 failed, identical with the GIL off and on.
  EVIDENCE:
  - artifacts/managed_spell_examples_20261018/probes/probe_managed_lifecycle.py:1-756
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:1-83
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil1.txt:1-83
  IMPACT: Every row below is a public-surface behaviour an example may assert (UX law).
  NEXT: Record the lifecycle map step by step.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T21:31:24Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Lifecycle map, steps 1-3 (bind, compose, lease).
    (1) BIND: `existence=Existence.managed_spell_quantity` (or its name) plus four keyword options on
    `Spellbook.bind` / `bind_inactive` / the Conduit facades, `SpellBinder.as_managed_spell_quantity(mode, *,
    limit, timeout_seconds, reset_methods)` and `scan_bind`. Mode defaults to elastic (member or name); elastic's
    limit defaults to 256 and means the most IDLE objects kept; limited_quantity and queue require a limit = the
    most objects ALIVE (idle plus out); queue alone takes (and requires) `managed_spell_timeout_seconds`; reset
    names are a list/tuple of callable attributes of the class. Classes only. Every malformed binding is refused
    at bind with a message naming the remedy (P10: nine refusals). A managed spell may depend on unique, managed
    and many spells; on a shorter scope (unique_per_conduit) conjure refuses it with scope_ordering_violation
    (P15). (2) COMPOSE: the owner stamp (conjure, a post-conjure bind, a transfer) composes one pool per (root
    store, version) and registers it with the process singleton `ReleaseManagedSpell()`: right after conjure,
    describe(cls) answers one pool, count 0 (P01). (3) LEASE: `conduit.meld(...)`, every injection into a
    constructor (each injection its own lease, P07), `conduit.managed_spell_meld(...)` (a ManagedSpellLease, P06)
    and `SpellSpace.meld` (leases from the root pool, P14) take the NEWEST idle object (LIFO, P01); an empty pool
    builds under elastic (never refuses; P02 built a third past limit 2), builds below the limit under
    limited_quantity and otherwise raises `ManagedSpellExhaustedError` (a MeldExecutionError: mode, limit,
    timeout_seconds None; nothing built, P03), and under queue waits for a release - which hands the waiter the
    released object (P04) - or raises it at the timeout, taken once at the call (P04: >= 0.3 s, timeout_seconds
    0.3). An override of the managed spell's own parameters builds a fresh object the pool never counted (P16).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:984-1250
  - src/melder/aether/spellbook/spellbinder.py:550-602
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-90
  - src/melder/aether/conduit/creations/creations.py:1118-1183
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:437-551
  - src/melder/aether/conduit/conduit.py:5095-5207
  - src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py:107-174
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:2-42
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:51-59
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:69-74
  IMPACT: Steps 1-3 are the first half of every example; the modes differ only on a miss.
  NEXT: Record steps 4-7.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T21:31:24Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Lifecycle map, steps 4-7 (release, reset, inspect, end).
    (4) RELEASE: `ReleaseManagedSpell().release(obj)` routes by `type(obj)` (one dict get) to the class's one
    pool; with several pools `spell_id=` or `conduit=` (a root or one of its lessers) picks one, a non-str
    spell_id is TypeError, an unmatched filter or a non-managed class ValueError (P09). `managed(obj)` returns a
    ManagedSpellLease; a lease releases once (`release()` twice is one release; `object` raises RuntimeError after
    it; its `with` releases on exit even when the block raised and never suppresses, P06); `release_all` attempts
    every object, then raises one ExceptionGroup (P03). A release is trusted: identity is not tracked. An elastic
    pool with limit <= 20 is fixed-capacity: a release that leaves more idle objects than the limit destroys the
    oldest idle one, disposal methods included (P02: closed=[True, False, False]). (5) RESET: the reset names run
    in order on every release, outside every lock (P05: ['clear', 'rewind']); the next lease gets the reset object;
    a raising reset destroys the object (disposal runs, count down) and its error propagates (P05). (6) INSPECT:
    `ReleaseManagedSpell().describe(cls)` - one dict per pool: mode, limit, timeout_seconds, reset and disposal
    names, count (alive), idle_count, out_count, holding_conduit_id, active_version, retention keys (P01 keys);
    `conduit.has_live_creation("Name")` is True while the pool's count > 0 (P01). (7) END: root teardown cleans the
    pools first - idle objects disposed, objects that are out left open and their holder's - and unregisters them
    (P01, P08); afterwards `release(obj)` raises the not-managed ValueError and a lease made before raises
    RuntimeError "The pool of managed spell '<name>' was torn down with its root conduit; the object is yours to
    dispose." (P19). `conduit.purge(...)` of a managed spell returns 0 and `SpellSpace.purge` refuses it (P01, P14).
    Dynamic posture: `cleanup_spell` then `bind` with other settings keeps the spell_id and the pool, whose count
    keeps the objects out (P12); `transfer_spell_ownership` moves the pool with its idle objects to the target
    root, and releases still route by class (P13).
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:357-513
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/managed_spell_lease.py:79-161
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:553-611
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:795-914
  - src/melder/aether/conduit/creations/creations.py:326-399
  - src/melder/aether/conduit/meld/meld.py:784-821
  - src/melder/aether/conduit/meld/conduit_meld.py:211-280
  - src/melder/aether/conduit/meld/spellspace_meld.py:174-239
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:2-12
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:43-50
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:61-71
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:80-82
  IMPACT: Steps 4-7 are the second half of every example and the Sphinx page's contract.
  NEXT: Record the two findings (stale failure-mode text; root-held consumers at teardown).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T21:31:24Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Stale system-document text (the code is right): src_architecture's Failure Modes say a
    `ReleaseManagedSpell().release(obj)` after the pool's root was torn down raises RuntimeError "...torn down
    with its root conduit...", and src_components' Managed Spell Pools failure modes say the same of "a release".
    Root teardown unregisters the pool before cleaning it, so a release through the registry raises the
    not-managed ValueError; only a lease (which holds its pool) or a release racing the teardown reaches the torn-
    down pool and raises the RuntimeError (P08, P19). The release note states it correctly.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:2529-2531
  - context_compass/system_docs/src_components.md:3951-3952
  - release_docs/next_version_release.md:522-525
  - src/melder/aether/conduit/creations/creations.py:326-399
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:45-45
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:80-81
  IMPACT: The examples and the Sphinx page teach the code's behaviour; the two system documents need a one-line
    correction. melder_0 is landing src_architecture and src_components now, so this lane does not edit them.
  NEXT: Tell melder_0 (mailbox NOTICE) and raise it in the owner walkthrough.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T21:31:24Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: RISK
  CLAIM: A consumer melded on the ROOT that gives its managed dependency back in its own disposal method makes
    root teardown raise ExceptionGroup "Conduit torn down with disposal failures.": the root store cleans its
    pools before its disposable registry (so pooled objects die before the uniques they hold), so the consumer's
    release meets an unregistered class. Teardown still completes and the leased object stays open (P17). The same
    consumer melded in a request scope (a lesser conduit) gives its lease back cleanly at the scope's exit,
    because the root's pool outlives the scope (P07). By the runtime model this is the holder's pending work, not
    a structural defect.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:326-399
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:39-42
  - artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:75-77
  IMPACT: The examples teach the request-scope pattern and state the root-teardown order; the owner decides
    whether root-held consumers deserve a different teardown order.
  NEXT: Ask the owner in the walkthrough; no src change in this lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T21:31:24Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: S2's example set, in 02_intermediate after lesson 41 (beginner's tier law allows only unique, many and
    unique_per_conduit; nothing here needs Nexus, MutationResearch or the crystallizer): 42 elastic pool (lease,
    release, LIFO reuse, describe, trim of a small limit); 43 limited_quantity (the refusal and its fields, release
    then lease again, release_all); 44 queue (hand-off to a waiting lease, the timeout refusal); 45 resets and
    leases (reset order, a raising reset, managed_spell_meld, ReleaseManagedSpell().managed, a raising block); 46
    injection and request scopes (each injection its own lease; handlers give it back at the scope's exit;
    teardown disposes idle objects only; release after teardown); 47 settings and transfer in a dynamic world
    (cleanup_spell + bind keeps the pool; transfer carries it). Contract probes go in a new
    pytest_examples/test_managed_spell_probes.py; the intermediate runner already globs every lesson.
  EVIDENCE:
  - UX_and_AIX_experiences/AGENTS.md:1-44
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_examples.py:13-36
  IMPACT: S1's exit gate is met; S2 starts from this list.
  NEXT: Close S1 and route the board to S2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T21:33:11Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1 closed: exit gate met (lifecycle map steps 1-7, two findings, S2's example list). Routine closure by
    the assigned agent; ACCEPTANCE: delegated-routine, VALIDATION: probe 81/81 rows GIL off and on, CHILDREN: none,
    ROUTING: board row replaced by S2's.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil0.txt:1-83
  - context_compass/artifacts/managed_spell_examples_20261018/runs/probe_managed_lifecycle_gil1.txt:1-83
  IMPACT: S2 starts from evidenced behaviour only.
  NEXT: S2 - read two neighbouring lessons for style, then write lesson 42.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user (rides with S2's walkthrough)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
State: done (closed by melder_2). The lifecycle map is in Notes (steps 1-7) with evidence; the probe and its runs
are under artifacts/managed_spell_examples_20261018/. Open findings: the stale failure-mode text in
src_architecture/src_components (melder_0 told, M2-15) and the root-held consumer RISK (owner walkthrough).
Next: STORY-2026-10-18-managed_spell_ux_examples writes the examples from the DECISION note's list.
Update this view in place. Preserve historical Notes/comments and link unchanged context/full evidence.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
