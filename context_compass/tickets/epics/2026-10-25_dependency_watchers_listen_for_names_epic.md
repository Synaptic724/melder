

# Epic: dependency_watchers_listen_for_names - a consumer waiting on a provider re-resolves when one arrives

## Metadata
- Epic ID: EPIC-2026-10-25-dependency_watchers_listen_for_names
- Status: ready
- Owner: Mark (owner)
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-25T02:26:33Z
- Updated: 2026-10-25T02:26:33Z
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness - structure that is wrong or stuck (the owner, 2026-10-14)

## Problem / Opportunity
The owner asked (chat 2026-10-25): "Make an epic to understand why the bug appears with the both models thing, we
can understand it better thats more structural in the backend I think ... make an epic for that one bug please".

The bug, measured on 0.2.8267 with public calls, the GIL off and on (the S2 story's FACT note of
2026-10-25T02:01:57Z; EPIC-2026-10-17-correctness_defects, FACT note of 2026-10-25T02:02:53Z): a consumer injected
by a class annotation that compiled without its provider - after a notch away from it, or before it was bound - is
never re-resolved when the provider comes back under a spellframe (a notch back, or a later bind under a Protocol).
Every meld of it raises UnresolvedInputError until the consumer is disposed and bound again. A provider bound bare
is unaffected.

What is known. Phase 3 records the parameter as an UNRESOLVED_INPUT socket with no dependency edge, keyed by the
annotation's name (('english', '__default__')); SpellSystemStates watches it under that key's frame, 'english'; bind
and notch stage the incoming spell's address, and the commit's dirty marker marks only the watchers of those frame
keys. The annotation names a type and the change names an address; the two agree only for a class bound bare, whose
address frame is its own name. That holds in today's address model and under option (A) alike - the "both models"
of the owner's message - because neither changes how a watcher is keyed or what a change announces.

What is not known. Whether the same split reaches the other watchers and announcers. Watchers: UNRESOLVED_INPUT,
AMBIGUOUS_INPUT, OVERRIDE_REQUIRED and NORMAL collection sockets are all keyed by `dependency_key[0]`, while Phase 3
matches by kind - a type key, contract keys, a definition key or a label key. Announcers: bind, bind_inactive,
notch, the index moves, cleanup_spell, contracts and transfers. The 0.2.8222 kind-matching task left "the watcher
and Phase 4 cycle heuristic's name keying" out of scope for a follow-up ticket that was never filed.

## MRP Alignment (Most Reasonable Product)
Agents iterate on providers in place - they bind, notch, retire and rebind them while consumers stay. A consumer
waiting on a provider must find it when it arrives however it was bound, or the structure is stuck and the only
way past is to dispose and rebind the consumer. The watcher key is the one place that decides it, so spelling it
right once, for every socket kind, is the durable fix rather than a patch per event.

## Ticket Contract
- ENTRY_GATE: the owner's ask (chat 2026-10-25); a board row routes here; the first story is defined below.
- EXECUTION_BOUNDARY: investigation first, read-only in src - STORY-2026-10-25-map_dependency_watchers_and_announcers:
  every watcher kind, every key spelling Phase 3 matches by and every announcer with the key it stages, measured
  as a matrix. Then one fix story per confirmed miss, filed here on the owner's word, each with its own patch
  docs, tests, notch and rebuild.
- DEPENDENCIES: the reproducer (Artifact Links); S2 of EPIC-2026-10-17-correctness_defects (option (A) changes no
  watcher or announcer); STORY-2026-10-25-probe_and_purge_reach_every_version (no shared code).
- EXIT_GATE: S1's matrix and root cause on its story; every confirmed miss fixed by its story or explicitly left by
  the owner; board and artifact sync.
- FAILURE_ESCALATION: DECISION_REQUEST for the fix design (key the watchers by every spelling a match may use,
  announce every key a change makes visible, or both); CONFLICT if another lane holds spell_system_states.py,
  compiler_phase_3.py or change_control_manager.py.

## Goals (Outcomes)
- Know why the stuck consumer happens, from source read whole, for every socket kind and change event.
- A consumer waiting on a provider re-resolves whenever a matching provider arrives, returns or leaves, however it
  is bound (bare, under a string category, under a Protocol), after a bind, a notch, an index move or a contract.

## Non-Goals (Explicit Exclusions)
- The address model: S2 of the correctness epic, option (A).
- The meld doors' naming rules: meld(spell=Cls) and meld('Name') as address lookups by name, and
  SpellMap(spell=Cls) by class identity (gaps 2 and 3 of the S2 story's FACT note of 2026-10-25T02:01:57Z).
- purge and has_live_creation (STORY-2026-10-25-probe_and_purge_reach_every_version).

## Scope Boundaries
- In scope: Phase 3's socket keys and match keys (`_dependency_key_for_dep`, `_spell_keys_for`), the watcher index
  (`_extract_collection_frame_keys`, `_update_collection_index`, `mark_collection_dependents_dirty`), the commit's
  dirty marker (`_default_dirty_marker`), each announcer's staged keys, and Phase 4's cycle heuristic's name keying.
- Out of scope: meld-door discovery, the creation stores, the notch's signature handling.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the owner asked for this epic (chat 2026-10-25); the bug reproduces on 0.2.8267 and the first
  story is defined.

## Success Metrics
- S1's matrix covers every cell of socket kind x annotation kind x provider binding shape x change event, each
  measured the GIL off and on.
- Once the fix stories land, no cell where a matching provider arrives or returns and the consumer stays refused.

## Requirements (Functional + Non-Functional)
- Functional: a socket waiting on a provider is marked by every change that makes a matching provider visible or
  takes one away, whatever the provider's address.
- Non-functional: no new lock or lock-order edge in the watcher index; no cost on warm melds; the GIL off and on.

## Constraints / Assumptions
- UNKNOWN until S1: whether the AMBIGUOUS_INPUT, OVERRIDE_REQUIRED and collection watchers share the split.

## Dependencies / External References
- tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md (0.2.8222 and its out-of-scope list)
- tickets/stories/completed/2026-09-26_unresolved_input_sockets_story.md (the UNRESOLVED_INPUT watcher)

## Milestones (Track Progress)
- [ ] Milestone 1: S1's matrix and root cause recorded and the owner told.
- [ ] Milestone 2: the fix stories filed on the owner's word and landed.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-10-25-map_dependency_watchers_and_announcers - every watcher and announcer
  measured as a matrix and the root cause read in full (investigation, read-only in src).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-10-25-map_dependency_watchers_and_announcers
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The reproducer's consumer recovers on a notch back and on a later bind under a spellframe, the GIL off and on.
- Every other miss in S1's matrix is fixed or explicitly left by the owner.

## Risks / Mitigations
- A broader watcher key marks more consumers per change (a revalidation cost): S1 counts the marks per change
  before any fix is designed.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- S1: a matrix probe on 0.2.8267, the GIL off and on. Each fix story: symptom-named regression tests that fail
  before the fix and pass after it, the GIL off and on.

## Rollout / Adoption Plan
- The fix stories land one at a time, each with its notch, release-note entry and rebuild.

## Open Questions
- UNKNOWN: which other socket kinds and change events miss (S1).

## Decision Log
- 2026-10-25T02:26:33Z: filed on the owner's ask (chat 2026-10-25), from the side finding of S2's meld-identity map.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/diag_class_annotated_consumer_after_notch_back.py (the reproducer)
  - artifacts/correctness_defects_20261017/runs/diag_class_annotated_consumer_after_notch_back_0_2_8267.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the fix story re-runs the reproducer and keeps it as its regression evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - dependency watcher keys against the keys a change announces
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence; filed 2026-10-25T02:26:33Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-25T02:26:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Filed on the owner's ask (chat 2026-10-25): "Make an epic to understand why the bug appears with the both
    models thing ... make an epic for that one bug please". It replaces the side-finding story the correctness
    epic's FACT note of 2026-10-25T02:02:53Z waited on. Investigation first: the first story maps every watcher
    and announcer and reads the root cause in full, read-only in src; fix stories follow on the owner's word.
    melder_1 runs it after STORY-2026-10-25-probe_and_purge_reach_every_version lands (one lane at a time), or
    sooner on his word.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:639-672
  - context_compass/artifacts/correctness_defects_20261017/runs/diag_class_annotated_consumer_after_notch_back_0_2_8267.txt:3-53
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1889-1929
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:841-877
  IMPACT: The bug has its own lane and the investigation is scoped before any fix is designed.
  NEXT: Start S1 when the probe-and-purge story lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: why a consumer waiting on a provider misses the provider's arrival when it is bound under a spellframe, for
  every watcher and announcer; then the fixes. Filed 2026-10-25T02:26:33Z on the owner's ask.
- State: ready, melder_1. Known: the UNRESOLVED_INPUT case (Problem); unknown: the other watchers (S1).
- Next: (1) S1 after the probe-and-purge story lands; (2) its matrix and a DECISION_REQUEST for the owner; (3) the
  fix stories on his word.

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
