# Story: release_routes_parked_version_objects_to_active_pool - a release after a notch strands a version's pool

## Metadata
- Story ID: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-17T21:07:53Z
- Updated: 2026-10-17T21:07:53Z

## User Narrative
As an agent iterating on a managed class through versions of one index - the same class bound again with other
managed options, then notched in - I want an object I leased before the notch to go back to the pool of the
version that leased it when I release it, so that each version's pool keeps a true count and the old version
leases again after a notch back.

## Value / MRP Alignment
A pool's count is structure Melder keeps (owner ruling: structure is the contract). Today a release can leave the
count of a limited_quantity or queue pool naming an object out that the pool will never get back, so that version
refuses every lease after a notch back while nothing is out - state an agent cannot get past without knowing where
the object went.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent; an
  active board row; a component patch for `ReleaseManagedSpell`'s resolver.
- EXECUTION_BOUNDARY: `ReleaseManagedSpell._resolve_pool` (with `release`, `managed` and `release_all`, which share
  it) and, only if the answer needs one, a record on `ManagedSpellQuantity`; regression tests; the system documents
  (the Managed Spell Pools component, the ReleaseManagedSpell invariant and its failure mode) with their indexes and
  the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links); the managed epic's
  rulings (owner, 2026-10-14: notch and cleanup_spell destroy nothing; identity is not tracked).
- EXIT_GATE: probe Q2 no longer leaves A's object in B's pool silently (it returns to A, or the release refuses and
  names `spell_id=`, per the answer), and A leases after the notch back; Q1, Q3, Q4, Q5 and Q6 unchanged; regression
  tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT if the fix needs a file another lane holds.

## Requirements (Functional)
- An object released with no filter, of a class whose live pools belong to two or more versions of one index, never
  lands silently in the pool of a version that did not lease it: it goes back to the version that leased it, or
  the release raises ValueError naming each version's spell_id and the keyword that picks one (the owner's choice).
- A one-pool release keeps its fast path; releases with `spell_id=` or `conduit=`, pools of different indexes or
  roots, and leases from `Conduit.managed_spell_meld` (which carry their pool) keep today's rules.

## Requirements (Non-Functional)
- The warm release (one pool, no filter) keeps its cost: one dict get and the pool's put-back, no lock.
- No identity tracking unless the owner chooses it (his 2026-10-14 ruling: "we don't care about identity").

## Scope Boundaries
- In scope: the cold resolver's choice among pools of one class that belong to versions of one index.
- Out of scope: pools of a disposed version (kept by the 2026-10-14 ruling); releases that name their pool; elastic
  pools' retention.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes); one open question
  for the owner, because the preference that causes it is an accepted design.

## Dependencies / Related Work
- The managed epic (EPIC-2026-10-14-managed_spell_quantity, completed): its lifecycle table chose "resolver prefers
  the active version" for notch and cleanup_spell.

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on the open question.
- [ ] Task: patch docs for the resolver; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With A (limited_quantity, limit 1) and B (the same class, limit 2) on one index, an object leased from A, a notch
  to B and a release with no filter: A's count and B's idle count stay true, and after a notch back A leases.
- The cases the probe uses as controls (one version; a release naming its version; a disposed version; a rebind
  under the same spell_id; versions that are two classes) behave as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g.
  `test_release_after_a_notch_does_not_strand_the_parked_versions_limited_pool`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- Visible today: after a notch back, `managed_spell_meld` or `meld` of the old version raises
  ManagedSpellExhaustedError "Managed spell '<name>' (limited_quantity, limit <N>) has all <N> objects out." while
  `ReleaseManagedSpell().describe(cls)` shows the object idle in the other version's pool. A refusing resolver would
  be a **Breaking change:** for code that releases such objects with no filter.

## Risks / Mitigations
- Routing to the leasing version needs to know which version leased an object, which the ruling declined to track;
  refusing the ambiguous release needs none and matches how two roots or two binding names are handled today.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- When two versions of one index share a class, should a release with no filter (a) raise ValueError naming each
  version's spell_id, as two roots or two binding names do today (recommended: no identity record, no silent
  count drift), (b) keep preferring the active version and document the drift with its remedy (`spell_id=`), or
  (c) record which version leased each object (the identity tracking ruled out on 2026-10-14)?

## Decision Log
- 2026-10-17T21:07:53Z: filed under EPIC-2026-10-17-correctness_defects from sweep A6 (Notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py (cases Q1-Q6)
  - artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which pool a released managed object goes back to when versions of one index share a class
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:07:53Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T21:07:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `ReleaseManagedSpell.release` takes its fast path only for
    a class with one pool; otherwise `_resolve_pool` keeps the pools matching the filters and, when several remain,
    the one whose version its index selects (`_is_selected_version`). Two versions of one index that bind the same
    class have one pool each, so after a notch every unfiltered release of the class goes to the new active version.
    `put_back` pools any object without counting it, and the count of the pool that leased it - raised by its own
    `reserve()` - never comes down. Probe Q2 (A limited_quantity limit 1, B the same class limit 2): Worker #2
    leased from A, B staged and notched in, `release(obj)`: B count 0 idle 1, A count 1 idle 0; B serves #2 next;
    after a notch back A raises ManagedSpellExhaustedError "has all 1 objects out" with nothing out. Q3 (the same
    with `spell_id=A`) stays right; Q6 (versions that are two classes) routes by class. Identical with the GIL off
    and on (ids masked).
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:357-399
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/release_managed_spell.py:625-645
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:474-545
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:548-606
  - context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md:401-412
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py:1-205
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt:1-64
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt:1-64
  IMPACT: A limited_quantity or queue version can refuse every lease after a notch back while nothing is out.
  NEXT: The owner's answer on the open question, then patch docs for the resolver.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: a release with no filter among versions of one index that share a class (Requirements). Defect proven on
  0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner. The fix sits in release_managed_spell.py, which no other lane holds.
- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

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
