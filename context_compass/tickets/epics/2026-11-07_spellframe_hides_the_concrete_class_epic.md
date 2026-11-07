

# Epic: spellframe_hides_the_concrete_class - a spell bound under a spellframe is reached through that frame, never by its class

## Metadata
- Epic ID: EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T10:22:44Z
- Target Window: 2026-Q4
- Related Program/Initiative: EPIC-2026-10-25-dependency_watchers_listen_for_names (its key split, found by S1)

## Problem / Opportunity
Melder answers "can a spell bound under a spellframe be resolved by its concrete class?" two ways on 0.2.8277
(measured, the GIL off and on): the class meld door says no - `meld(English)` raises KeyError when English is bound
under the Protocol `Greeter` - while constructor injection says yes - `greeter: English` resolves the framed English,
because Phase 3 matches a class annotation by the spell's type key whatever its frame. The accepting path is where
S1 found the key split: a consumer compiled before its provider waits under the annotated class name, but the
provider's bind, notch or contract grant announces its frame, so the consumer never wakes (14 strict xfails in
tests/component). Interface-style resolution itself works: by the frame, by a Protocol annotation, by a SpellMap,
with AMBIGUOUS_PROVIDER for two implementations (the owner's 2026-10-04 ruling).

The owner chose, chat 2026-11-07, the Autofac-strict model ("I prefer 2nd option"): framing hides the concrete class,
as Autofac's `.As<IGreeter>()` without `.AsSelf()` does. He also asked for a check: "I also want to add a phase 4 or
phase 6 check to see if multiple spells are bound with a spellframe without a binding_name and that should help the
user situation, make an epic for this and lets tackle it the right way".

## MRP Alignment (Most Reasonable Product)
One rule for every door: a spellframe is the spell's interface. Bound under a frame, a spell is reached through the
frame - a Protocol or name annotation of the frame, a label list, a SpellMap, the frame address; bound bare, it is
reached by its class. With one rule every annotation's match key is its provider's address frame, so a waiting
consumer's watch key and a change's announced key agree by construction and the S1 key split cannot occur in any
shape. Fixing the wake-up instead (option A) would keep two answers to one question.

## Ticket Contract
- ENTRY_GATE: the owner's decision (chat 2026-11-07); a board row routes here; T1 (the inventory) goes first.
- EXECUTION_BOUNDARY: Phase 3's class and name matching and its candidate index; the S1 regression file and every
  test, doc and example the change breaks; the owner's Phase 4 check and the duplicate-address paths (T3).
  Excluded: the meld doors (they already refuse a framed class), the other S1 misses (they stay on the
  dependency-watchers epic).
- DEPENDENCIES: STORY-2026-10-25-map_dependency_watchers_and_announcers (matrix, regressions, option analysis); the
  0.2.8222 kind-matching rules; special_instructions/agent_contribution_guide.md (notch, release note, rebuild).
- EXIT_GATE: T1-T3 done; the release note's Breaking entry; the regressions assert this contract and pass in both GIL
  modes; the S1 matrix re-run shows no key-split MISS; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for each edge case T1 finds (an existing object bound under a frame; a string
  annotation that names both a class and a category; Protocol definitions); CONFLICT if another lane holds
  compiler_phase_3.py.

## Goals (Outcomes)
- A class annotation (`greeter: English`), a string naming a class and `list[English]` select only spells bound bare;
  a framed spell is reached through its frame, as the class meld door already requires.
- A consumer waiting on a provider wakes when a provider it matches arrives, returns or is granted, in every shape.
- A Phase 4 error refuses a consumer annotated with a class bound only under a spellframe and names the frame to ask
  by; two spells at one address - one spellframe with no binding_name, one name with neither - stay refused on every
  path (the owner's rule, 2026-11-07; T3).

## Non-Goals (Explicit Exclusions)
- Changing the meld doors' lookups (they already behave this way).
- S1's other misses: a transfer marking the source Book, departures (D1, G4), a resolved socket not watched (E1),
  the Phase 4 binding-key cycle heuristic (P1a). They stay on EPIC-2026-10-25-dependency_watchers_listen_for_names.
- cleanup_spell's after-effects (the owner: not a defect, chat 2026-11-07).

## Scope Boundaries
- In scope: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py (`_spell_keys_for`,
  `_build_candidate_index`, `_index_buckets_for`) and whatever else T1 finds matching by type key; the tests, system
  docs and examples that rely on it; the creation-cache generation if replayed rows would keep old matches.
- Out of scope: Bind, addresses, SpellMap and SpellContract resolution, Protocol/contract and label matching.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: filed and started on the owner's word (chat 2026-11-07); T1 first.

## Success Metrics
- The S1 matrix re-run: no MISS in the key-split cells; class cells read unresolved in LIVE and FRESH alike.
- Every test, doc and example that resolved a framed spell by class is converted or removed, none left silent.

## Requirements (Functional + Non-Functional)
- Functional: type matching (single sockets, collections, a name annotation's type part) admits only spells with no
  spellframe; contract, definition and label matching unchanged; a refused class match compiles an UNRESOLVED_INPUT
  socket like any missing provider.
- Non-functional: no warm-meld cost, no new lock, both GIL modes; a creation-cache generation bump when T1 shows
  replayed phase 3-4 rows would carry the old matches.

## Constraints / Assumptions
- Breaking change: a consumer that resolves a framed spell by class today stops resolving. The release note leads
  with **Breaking change:** and the upgrade path: annotate the frame's Protocol, use a SpellMap, or bind the class bare.
- UNKNOWN until T1: how many tests, docs and examples rely on class matching of framed spells.

## Dependencies / External References
- tickets/stories/2026-10-25_map_dependency_watchers_and_announcers_story.md
- tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md
- tests/component/melder/aether/conduit/test_conduit_component_waiting_consumer_wakes_for_its_provider.py
- GitHub: the epic issue on Synaptic724/melder (URL in Notes)

## Milestones (Track Progress)
- [ ] Milestone 1: the inventory and the edge-case decisions (T1).
- [ ] Milestone 2: the strict model landed with tests, docs, release note, notch and rebuild (T2).
- [ ] Milestone 3: the Phase 4 check and the duplicate-address tests landed (T3).

## Stories (Required to Complete)
- [ ] none - tasks sit directly under the epic, on the owner's "make an epic ... build your tasks around it".

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-11-07-inventory_class_resolution_of_framed_spells (read-only in src)
- [ ] Task: TASK-2026-11-07-class_annotation_selects_only_bare_spells
- [ ] Task: TASK-2026-11-07-spellframe_ambiguity_validation_check
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `greeter: English`, `greeter: "English"` and `list[English]` never resolve an English bound under a frame; a bare
  English resolves as before; Protocol, label and SpellMap consumers are unchanged.
- The waiting-consumer regressions assert this contract and pass, the GIL off and on.
- The Phase 4 check refuses a consumer of a class bound only under a spellframe through the readable validation
  report, naming the frame; regression tests pin both duplicate-address shapes on every path.
- Release note entry, notch and rebuild per the contribution guide; the owner accepts.

## Risks / Mitigations
- Users resolving framed spells by class break: the Breaking entry names the upgrade path, and T3 can make the
  refusal name the frame to ask by.
- Cached plans replaying old matches: T1 checks the structural snapshot and creation-cache rows; T2 bumps the
  generation if they do.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- The S1 regression file rewritten to this contract; the S1 matrix probe and the interface check re-run; the full
  suite run and reported truthfully, the GIL off and on.

## Rollout / Adoption Plan
- One release-note section (Breaking), one notch per landed source change, the rebuild last.

## Open Questions
- RESOLVED 2026-11-07 (T3): the check's rule - see the Decision Log and T3's Notes (the candidates are in T3's
  DECISION_REQUEST note).
- UNKNOWN (T1): the edge cases in FAILURE_ESCALATION.

## Decision Log
- 2026-11-07T10:03:26Z: the owner chose the Autofac-strict model (option B) over fixing the wake-up (option A) and
  asked for a Phase 4/6 check (chat 2026-11-07).
- 2026-11-07T10:22:44Z: the owner set T3's rule (chat 2026-11-07, "lets do 3"): a Phase 4 error for a consumer
  annotated with a class bound only under a spellframe, naming the frame; and two spells at one address - one
  spellframe with no binding_name, one name with neither - refused on every path, a check added where one is not.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/dependency_watchers_20261107/probes/interface_resolution_check.py
  - artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt
  - artifacts/dependency_watchers_20261107/probes/binding_name_and_spellmap_check.py
  - artifacts/dependency_watchers_20261107/runs/binding_name_and_spellmap_check_0_2_8277.txt
  - artifacts/dependency_watchers_20261107/probes/meld_door_check.py
  - artifacts/dependency_watchers_20261107/runs/meld_door_check_0_2_8277.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: T2 re-runs them as its before/after evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which doors resolve a framed spell by class, and the Phase 4/6 check's rule
- IF_UNKNOWN: ask user before implementation

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence; filed 2026-11-07T10:03:26Z.
- Published By: GitHub Synaptic724/melder issue #208 (gh CLI, 2026-11-07T10:07:37Z); this file is the local record
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T10:03:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Filed on the owner's word (chat 2026-11-07): the Autofac-strict model ("I prefer 2nd option") and a Phase 4
    or 6 check. Measured basis on 0.2.8277, both GIL modes: with English under `Greeter`, `meld(spellframe=Greeter)`
    and `greeter: Greeter` give English and a binding name keys the frame meld; two named implementations make
    `greeter: Greeter` AMBIGUOUS_PROVIDER; a second spell under `Greeter` with no binding name is refused at bind;
    `meld(English)` raises KeyError while `greeter: English` resolves the framed English - the two answers this epic
    makes one. binding_name alone never hides a class, and a SpellMap consumer refuses at conjure rather than wait.
    Phase 3's type matching ignores the frame, which is the line to change.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt:1-51
  - context_compass/artifacts/dependency_watchers_20261107/runs/binding_name_and_spellmap_check_0_2_8277.txt:1-19
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-519
  IMPACT: The key split goes away by construction; the change is breaking for class consumers of framed spells.
  NEXT: T1 - the inventory of every path, test, doc and example that resolves a framed spell by class.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T10:07:37Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Mirrored on GitHub on the owner's word ("make an epic for this"): https://github.com/Synaptic724/melder/issues/208,
    created by `gh issue create` from the Synaptic724/melder checkout - summary, the measured two-answers table, the
    stuck-consumer link to the regression file, the three tasks as a checklist and the breaking change with its
    upgrade path. The board routes the new row to T1.
  EVIDENCE:
  - context_compass/attention_board.md:110-111
  IMPACT: The investigation is visible where the owner tracks melder work; the local epic stays the working record.
  NEXT: T1, read-only; the owner's answer on T3's rule.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-11-07T10:22:44Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: T3's scope is set by the owner (chat 2026-11-07): part (a), candidate 3 as a Phase 4 error naming the frame,
    lands after T2; part (b), the two duplicate-address shapes held refused on every path, is independent of T2.
    Tranche order stays T1 -> T2 -> T3 (stated to the owner before he re-certified melder_0). GitHub #208's task
    list still says "rule to be confirmed"; it is not edited without the owner's word.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-11-07_spellframe_ambiguity_validation_check_task.md:16-35
  IMPACT: Every open question of the epic is answered except T1's edge cases.
  NEXT: T1 - read Phase 3's type-key matchers in full.
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
- Scope: make class-based injection agree with the class meld door - a framed spell is reached through its frame -
  and add the owner's Phase 4/6 check. Decided by the owner, chat 2026-11-07.
- State: in_progress, melder_0. Basis measured (Notes). The S1 regression file holds 14 strict xfails written for the
  other option; T2 rewrites them to this contract.
- T3's rule is set (Decision Log, 2026-11-07T10:22:44Z).
- Next: (1) T1 inventory, read-only, in progress; (2) T2; (3) T3, part (b) possibly alongside T2.

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
