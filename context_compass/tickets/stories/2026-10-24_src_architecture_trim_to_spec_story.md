

# Story: src_architecture trimmed to its authoring spec, component detail moved to src_components

## Metadata
- Story ID: STORY-2026-10-24-src_architecture_trim_to_spec
- Epic: EPIC-2026-10-24-src_architecture_to_spec
- Status: in_progress
- Owner: Mark (owner; scope and acceptance)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T20:58:18Z
- Updated: 2026-10-24T21:32:10Z

## User Narrative
As an agent re-entering Melder after a compaction, I want src_architecture to hold the system as it is today -
boundaries, sequences, the rules in force and today's failure behaviour - without months of change history and
per-component mechanics, so that the baseline read is short enough to hold and still complete enough to trust.

## Value / MRP Alignment
The document is a baseline read for every engineer role and the packaged architecture hardcopy. History belongs to
git and the release notes, component mechanics to src_components; what remains must still be true and evidenced.

## Ticket Contract
- ENTRY_GATE: the board row routes here; edits wait until melder_0's F5 and melder_1's turn-in have landed their
  writes to both documents (or an order is agreed), and the preservation baseline is captured right before them.
- EXECUTION_BOUNDARY: `context_compass/system_docs/src_architecture.md`, `src_components.md` (only the sections that
  receive moved material) and both indexes; the asset rebuild. Nothing in `src/`, tests, version or release note.
- DEPENDENCIES: EPIC-2026-10-24-src_architecture_to_spec; TASK-2026-10-24-cache_file_write_failure_fails_meld;
  STORY-2026-10-24-remove_many_child_holder_ownership.
- EXIT_GATE: the Quality Gate of the src_architecture instructions passes; every baseline line is accounted for;
  the rubric is scored and recorded; both indexes and both asset builders `--check` OK; board and artifacts synced.
- FAILURE_ESCALATION: DECISION_REQUEST when a cut would remove a rule in force or an owner ruling; CONFLICT when
  another lane writes the same sections; BLOCKER when a gate cannot pass.

## Requirements (Functional)
- The 17 contract sections stay present and in order; extra sections stay where they are useful.
- Context / Handoff Summary: the recent entries stay; older entries go to git and the release notes, and the
  decisions still in force stay as a short list pointing at the sections that carry them.
- Operational Invariants and Failure Modes: history clauses about released versions and fixed-defect narratives are
  removed; component mechanics move to the matching src_components entry unless it already carries them.
- C1 Code Map: the five contract fields unchanged; notes cut to their descriptive part.
- No path into the Context Compass package anywhere in the document; no absolute paths.

## Requirements (Non-Functional)
- Moved text is carried verbatim; nothing is reworded on the way.
- Edits are made by scripts that slice the file, never by retyping file content from tool output.
- Re-read each document immediately before writing it.

## Scope Boundaries
- In scope: the two documents and their indexes; this story's artifacts; the boards; the asset rebuild.
- Out of scope: src_graph (generated), tests_architecture, tests_components, README, `docs/`, policy documents.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner set the scope (chat, 2026-10-24); the audit runs now, read-only.

## Dependencies / Related Work
- TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0): F5 writes both documents.
- STORY-2026-10-24-remove_many_child_holder_ownership (melder_1): turn-in merges its patch into both.

## Tasks (Implementation Checklist)
- [x] A1: structural checks - heading order against the contract, wrapped headings, the portability and
      absolute-path searches, C1 five-field completeness, index `--check`.
- [ ] A2: read the example architecture document and the rubric; score the current document.
- [x] A3: disposition per section and per entry - keep, cut history, move to a named src_components section, or
      remove with its account - with line estimates.
- [x] A4: for each move, slice the matching src_components section and record whether it already carries the
      material (drop the duplicate) or not (move verbatim).
- [ ] C1: NOTICEs to melder_0 and melder_1 (sent; order agreed, M1-51); record when their writes land.
- [ ] E0: preservation baseline (multiset) of both documents immediately before the first edit.
- [ ] E1: Context / Handoff Summary.
- [ ] E2: Operational Invariants and Failure Modes.
- [ ] E3: C1 Code Map notes.
- [ ] E4: Indexing, Unknowns, Glossary, Promoted Patch Decisions, System Boundary.
- [ ] E5: both indexes regenerated; `--check` OK.
- [ ] V1: preservation gate over the documents and migration targets; Quality Gate; rubric after.
- [ ] V2: asset runner and llm_support builder, each then `--check`, on Python 3.14 - last.
- [ ] Close: summary, completed/, board and artifact sync, a NOTICE of the layout rules to active agents.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- src_architecture: 17 contract sections in order; the portability and absolute-path searches return nothing; about
  1,000 lines fewer than the baseline, or the reason it is fewer recorded.
- Every baseline line is in a document or accounted for (moved target, or history left to a named git revision).
- Rubric score recorded before and after; indexes and both asset builders `--check` OK.

## Validation / Test Plan
- `index_document.py --check` on both documents; the two searches from the instructions' Validation Commands;
  preservation multiset diff; rubric; the two builders with `--check`. No test suite is affected (documents only).

## UX / API / Data Notes
- The packaged `__architecture__` and `__components__` hardcopies change with the rebuild; no API changes.

## Risks / Mitigations
- Concurrent writers -> edits after their landings; re-read before every write.
- Content loss -> preservation gate; moved text verbatim.
- Removing a rule with its history -> only history clauses go; uncertain text stays.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- The "recent" line for the handoff log: proposed as the release-note boundary (0.2.8228 onward; 0.2.8227.md
  is the last closed note, the running note starts at 0.2.8228).

## Decision Log
- 2026-10-24: owner scope (chat) - see the epic.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/src_architecture_to_spec_20261024/
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: this story's closure, after the preservation gate is accounted

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_3 (synaptic_python_developer); prose; revision 1 of this story.
- Published By: UNKNOWN before publication (local files; the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-24T21:02:36Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: A1 on the document as melder_0's F5 left it (5,700 lines, sha256 2bff3388..., written 20:54:46Z): one H1
    (the other three `# ` lines are comments inside the citation recipe's code fence); the 17 contract sections are
    present and in order, plus five extra H2s (What Melder Is, Glossary, Runtime Type Names, Extension Points,
    Promoted Patch Decisions); no wrapped heading; both indexes `--check` OK; 164 C1 entries, each with all five
    fields, all 164 paths resolving in src_graph_index; no absolute path. The spec's portability search returns
    nothing, but three lines point into this package without its trailing-slash spellings: the citation recipe's
    `pathlib.Path("system_docs")` (135), `artifacts/2026-07-09_crystallizer_philosophy_v3.md` (3273) and the
    rubric's skill path `design_engineer/policies/system_document_quality_rubric.md` (5624).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:135-135
  - context_compass/system_docs/src_architecture.md:3273-3273
  - context_compass/system_docs/src_architecture.md:5624-5624
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:134-175
  IMPACT: structure already meets the contract; the work is history, component detail and three leaks, not
    reordering. Line numbers move with every write by any lane, so edits anchor on text, never on numbers.
  NEXT: A3 - inventory Operational Invariants and Failure Modes entry by entry (range, size, versions named).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:04:44Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: A3 disposition, about 1,000 lines. "Recent" is everything after the release-note boundary (release_docs/0.2.8227.md
    ends at 0.2.8227, the running note starts at 0.2.8228), so 0.2.8228 onward stays as written. (1) Context / Handoff Summary 5045-5700: keep the dated entries
    5047-5318 (0.2.8228-0.2.8266); the 2026-10-04-and-older entries, the 2026-08 recomposition blocks and the
    carried-forward 2026-07-25 block become a short state, decisions-in-force and history pointer (about -360).
    (2) Operational Invariants entries from 2026-10-04 back (1938-2428): component mechanics (codegen emission,
    cache envelopes, store locks, hook maps, recording) shrink to the rule statement plus a pointer to the
    src_components entry that already carries them; architecture-level rules (settle-then-inherit, the four posture
    gates, scope exits, the Aether singleton, lock orders) stay (about -260). (3) Failure Modes from 0.2.8227 back:
    history clauses go, the current behaviour stays (about -60). (4) C1 Code Map: notes keep their description, lose
    their per-version change clauses (they repeat the invariants, the handoff and the release notes); the five fields
    are untouched (about -170). (5) Structure: the citation recipe duplicated in src_components' Indexing leaves this
    document for a pointer (-45); the MutationResearch interface bullet (about 110 lines) shrinks to its boundary
    facts, its verb inventory checked against src_components (-90); re-absorption and correction notes in Unknowns,
    Glossary, Runtime Type Names, Extension Points and Promoted Patch Decisions go (-50); the three leaks are fixed.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:5045-5700
  - context_compass/system_docs/src_architecture.md:1938-2428
  - context_compass/system_docs/src_architecture.md:3384-4540
  - release_docs/0.2.8227.md:1-3
  - release_docs/next_version_release.md:1-5
  IMPACT: the cut falls on released history and duplicated component mechanics; every rule in force and every
    recent entry stays. Removed lines are accounted for by src_components sections, git (HEAD 70ea25d23) and the
    release notes.
  NEXT: A4 - read the src_components slices each condensed invariant will point at; record the covered/move list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:05:56Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Write order agreed (M1-51 from melder_1, 21:04:30Z, consumed here): melder_0's 0.2.8266 lands, then
    melder_1's many-child turn-in, then this pass, rebased on both. melder_1 will NOTICE when its edits are in. Its
    src_architecture edits: the Runtime Model paragraph, the meld and transfer sequences, one new operational
    invariant and three rewritten, two failure modes, the guardrail's bind-guard count, the C1 code map, the handoff
    summary. Its src_components edits: the Creations, Meld, SpellCompiler and Ownership Transfer entries, the disposal
    pipeline, the transfer flow, the code map, the handoff summary; both indexes regenerated. melder_0's F5 document
    write already landed at 20:54:46Z.
  EVIDENCE: context_compass/tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md:1-12
  IMPACT: the edit script must anchor on text and run on the document as both lanes leave it; the preservation
    baseline is captured only after melder_1's NOTICE. Their new and rewritten entries are recent, so this pass keeps
    them as written.
  NEXT: A4 - read the src_components slices the condensed invariants will point at.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:07:48Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: A4, read in src_components (as at 12,544 lines): the mechanism of every old component-level invariant this
    pass condenses is already carried by a component entry - Spellbook Core: generation 9 release admission,
    generation 12 complete bundles, generation 15 structural snapshot, generation 19 world stamp, bind-hook ownership;
    SpellCompiler: compiler pool reads, `CodegenSignature`, the site-plan runtime, lazy `instance_results`,
    owner-store constants; Creations and SpellSpace: `ManyDisposalBucket`/`register_many`, slot guards, door-held
    roots, purge; Meld Resolution Runtime: purge discovery, pooled Meld hooks, injected dependencies; Conduit
    Runtime: named lessers, hook baselines, graduation, bind-hook facades; SpellSystemStates Registry and Conduit
    Resolution State: verdict retirement; Crystallizer: custody keys, ConduitHierarchy replay; Packaged Hardcopy:
    the document-view key map; Nexus Descriptor: published relationships and the named record lifecycle. Not
    carried: the MutationResearch boundary bullet as a whole - its verbs are spread over several entries and
    `create_diff_engine` appears nowhere - so it moves verbatim into Subcomponent: MutationResearch Root.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:436-440
  - context_compass/system_docs/src_components.md:484-499
  - context_compass/system_docs/src_components.md:4941-4946
  - context_compass/system_docs/src_components.md:5118-5136
  - context_compass/system_docs/src_components.md:3762-3770
  - context_compass/system_docs/src_components.md:3857-3862
  - context_compass/system_docs/src_components.md:4198-4222
  - context_compass/system_docs/src_components.md:3240-3262
  - context_compass/system_docs/src_components.md:7722-7732
  - context_compass/system_docs/src_components.md:7259-7347
  IMPACT: condensing those entries to their rule plus a named pointer loses no mechanism; the MR inventory is the
    one migration that adds text to src_components. Line numbers here move with melder_1's turn-in; the pointers
    name entries, not lines.
  NEXT: write the edit script with text anchors and run it on a scratch copy while melder_1's turn-in lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:32:10Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M0-218 (melder_0, 21:09:00Z, ACK of M3-1): its F5 writes to both documents, both indexes and the
    graph landed for 0.2.8266 (now `__version__`), it writes neither document again in its lane, and melder_1
    (0.2.8267) edits both next, then this pass. Consumed M2-33 (melder_2, 21:27:30Z, NOTICE): its CI lane (no src,
    no notch) changes LLM-bundle inputs - pyproject.toml's description, README.md:44, docs/requirements.lock,
    .github, tests/unit/github_workflows, a release-note bullet, tests_components.md's C1 extents and index - and
    nothing in src_architecture or src_components; it will NOTICE again when done.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1278-1278
  - context_compass/tickets/tasks/2026-10-24_ci_lane_loose_ends_task.md:1-13
  IMPACT: the write order is unchanged (after melder_1's turn-in); tests_components stays out of this story; if
    this landing is the last, its V2 rebuild also covers melder_2's inputs.
  NEXT: read the src_architecture and src_components authoring instructions (triggered: this story writes both)
    and review the trim script's dry run against them.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

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
Scope: src_architecture to its spec and about 1,000 lines lighter; component material to src_components. State:
in_progress, melder_3, audit (A1-A4) read-only. Hold: no edit to either document until melder_0's F5 and
melder_1's turn-in land. Next: A1 structural checks; NOTICEs to melder_0 and melder_1.

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
