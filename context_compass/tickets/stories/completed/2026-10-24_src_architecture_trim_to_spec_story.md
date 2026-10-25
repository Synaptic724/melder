

# Story: src_architecture trimmed to its authoring spec, component detail moved to src_components

- Completed: 2026-10-24T22:37:34Z
- Summary: src_architecture is at its authoring spec: 5,739 -> 4,784 lines (-955), the 17 contract sections in
  order, no path into the documentation tooling, the change log kept from 0.2.8228 on, the older component mechanics
  left to the src_components entries named at the end of Operational Invariants, and the MutationResearch boundary
  inventory moved to src_components (+90). Preservation accounted (1,117 removed lines in git 3bedd65bb, 20 named
  melder_1 lines); rubric 69 -> 81 (B); both indexes `--check` OK. No source, no notch, no release-note entry; the
  rebuild runs last, after this closure, and its result is recorded in the epic.

## Metadata
- Story ID: STORY-2026-10-24-src_architecture_trim_to_spec
- Epic: EPIC-2026-10-24-src_architecture_to_spec
- Status: done
- Owner: Mark (owner; scope and acceptance)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T20:58:18Z
- Updated: 2026-10-24T22:37:34Z

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
- from_state: in_progress (implementation)
- to_state: done
- transition_reason: the EXIT_GATE is met but for its last item, the rebuild, which the turn-in order runs after
  this closure: the Quality Gate passed, every baseline line accounted, the rubric recorded (81, B), both indexes
  `--check` OK (Notes of 2026-10-24T22:31:35Z and the V1 MEASURE after it). Routine closure under the owner's
  scope of 2026-10-24.
- from_state (earlier): draft
- to_state (earlier): in_progress
- transition_reason: the owner set the scope (chat, 2026-10-24); the audit runs now, read-only.

## Dependencies / Related Work
- TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0): F5 writes both documents.
- STORY-2026-10-24-remove_many_child_holder_ownership (melder_1): turn-in merges its patch into both.

## Tasks (Implementation Checklist)
- [x] A1: structural checks - heading order against the contract, wrapped headings, the portability and
      absolute-path searches, C1 five-field completeness, index `--check`.
- [x] A2: read the example architecture document and the rubric; score the current document.
- [x] A3: disposition per section and per entry - keep, cut history, move to a named src_components section, or
      remove with its account - with line estimates.
- [x] A4: for each move, slice the matching src_components section and record whether it already carries the
      material (drop the duplicate) or not (move verbatim).
- [x] C1: NOTICEs to melder_0 and melder_1 (sent; order agreed, M1-51); record when their writes land.
- [x] E0: preservation baseline (multiset) of both documents immediately before the first edit.
- [x] E1: Context / Handoff Summary.
- [x] E2: Operational Invariants and Failure Modes.
- [x] E3: C1 Code Map notes.
- [x] E4: Indexing, Unknowns, Glossary, Promoted Patch Decisions, System Boundary.
- [x] E5: both indexes regenerated; `--check` OK.
- [x] V1: preservation gate over the documents and migration targets; Quality Gate; rubric after.
- [ ] V2: asset runner and llm_support builder, each then `--check`, on Python 3.14 - last (runs after this
      closure; its result is recorded in the epic's Notes).
- [x] Close: summary, completed/, board and artifact sync, a NOTICE of the layout rules to active agents.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

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
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

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
- APPLIED (2026-10-24T22:37:34Z): the folder is deleted at this closure; the edit script's v1 is in git
  3bedd65bb, and the accounting it produced is recorded in this story's Notes.

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
  CLAIM: A3 disposition, about 1,000 lines. "Recent" is everything after the release-note boundary
    (release_docs/0.2.8227.md ends at 0.2.8227, the running note starts at 0.2.8228), so 0.2.8228 onward stays as
    written. (1) Context / Handoff Summary 5045-5700: keep the dated entries
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

- DATETIME: 2026-10-24T21:46:00Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The edit is one script, `artifacts/src_architecture_to_spec_20261024/trim_src_architecture.py` (v2.1): 78
    text-anchored operations on src_architecture and 3 on src_components, each asserting exactly one match; any miss
    stops the run with nothing written. It carries the A3/A4 plan (handoff, invariants, failure modes, C1 notes,
    re-absorption and correction notes, the three leaks, the MutationResearch move) plus: a C1 note keeps its first
    clause when the rest names a version (the bind-guard manifest note is left for melder_1's count; the
    MutationResearch root note and the eight research_set notes are rewritten from their class declarations); the
    C1 intro moves under its heading; every C1 range is remeasured from disk with `verified_at` set to the run; the
    `Conduit.link` type-check citation is computed from source; src_components gets the inventory, a handoff entry
    and its Updated date. Dry run on the documents as melder_0 left them: src_architecture 5,700 -> 4,749 lines
    (-951), src_components 12,544 -> 12,634 (+90); 1,143 normalized lines removed, every one present in git
    3bedd65bb (owner commit, 21:06:20Z, holding both documents as they stand), 0 unaccounted; no added line over
    the cap; the 17 contract sections in order; the portability and absolute-path checks clean.
  EVIDENCE:
  - context_compass/artifacts/src_architecture_to_spec_20261024/trim_src_architecture.py:1-771
  - context_compass/artifacts/src_architecture_to_spec_20261024/dryrun/operations_report.md:1-1817
  - context_compass/artifacts/src_architecture_to_spec_20261024/dryrun/preservation_unaccounted.txt:1-1
  IMPACT: the edit applies in one pass once melder_1 lands; the preservation gate is mechanical - removed lines
    against 3bedd65bb, moved lines against src_components - so E0-E4 become one run.
  NEXT: on melder_1's turn-in NOTICE, capture E0, rerun the dry run on the documents as melder_1 leaves them, read
    the operations report for any of its new lines the trim touches, then apply.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:46:00Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Review findings. (1) Five C1 entries are stale against disk: creations.py (1,880 cited, 1,680 on disk),
    site_plan_lowering.py, conduit.py and transfer_of_ownership.py (melder_1's uncommitted source) and
    bind_guard_manifest.py (652 cited, 651); the remeasure fixes them after melder_1 lands. (2) Runtime Type Names
    cites `Conduit.link`'s type check as conduit.py:5599-5601, two lines high: the check and the raise are
    5601-5603. src_components carries the same stale citation and the same citation recipe with its
    `pathlib.Path("system_docs")` leak - both left to Story 2. (3) The moved MutationResearch inventory overlaps
    the Root subcomponent's own Contract/Interface list; Story 2 folds the two.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1155-1156
  - src/melder/aether/conduit/conduit.py:5601-5603
  - context_compass/system_docs/src_architecture.md:4375-4380
  - context_compass/system_docs/src_components.md:3386-3386
  - context_compass/system_docs/src_components.md:7259-7347
  IMPACT: Story 1 stays inside src_architecture plus the sections that receive material; Story 2 inherits three
    concrete items instead of a re-audit.
  NEXT: record the A2 rubric baseline.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:46:00Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: A2, rubric (src_architecture profile) on the document as it stands (5,700 lines, sha256 2bff3388...):
    Fidelity 3 - claims carry citations that open to the code, but they drift (the type check above) and the
    document logs its own remaps; Contract completeness 4 - all 17 sections populated, the Handoff Summary a 656-line
    change log, not the concise summary its Handoff Rule asks for; Depth 5; Addressability 3 - one H1, unique
    unwrapped names, but `## Data Flows and Sequences` and `## Diagrams` are pure containers (both are contract
    sections, so the containers stay); Join integrity 3 - 164 of 164 C1 paths resolve in the graph index, but 76
    entries carry ranges verified 2026-08-0x and 5 are stale; Mirror agreement 3 - tests_architecture has the same
    17 sections in order and a current index, terminology not reviewed. Total 69/100, band C: usable, refresh
    before high-risk work - this story is that refresh. The example architecture document was read for shape.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1155-1156
  - context_compass/system_docs/src_architecture.md:5045-5700
  - context_compass/system_docs/src_architecture.md:795-795
  - context_compass/system_docs/src_architecture.md:4541-4541
  - context_compass/system_docs/tests_architecture.md:3-921
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:49-54
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:118-122
  IMPACT: the after-score is taken from the file on disk after the index rebuild, never from the draft; the apply
    pass remeasures every range (Join integrity 3 -> 5 expected) and fixes the drifted citation.
  NEXT: register the artifact; then wait for melder_1's turn-in NOTICE.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:05:15Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M1-53 (melder_1, 21:51:02Z, NOTICE): its 0.2.8267 edits to both documents are in (written
    21:49:23Z, indexes regenerated) - in src_architecture a new first Operational Invariant ("A `many` belongs to
    the scope that built it"), Meld Resolution step 4, the transfer sequence, the Runtime Model's defect paragraph,
    the transfer-default invariant, "Holder records" and "Holder-owned many children" marked REMOVED, two Breaking
    failure modes first, the guardrail count (629), five code-map entries, conduit.py citations past line 4273 +2, a
    handoff entry; in src_components the Creations, Meld, SpellCompiler, Registration Refusal, Ownership Transfer
    and Disposal Pipeline entries, the transfer flow, five extents, a handoff entry. It asks this pass to rebase
    now and apply after its turn-in NOTICE, because its rebuild runs last in its lane. Consumed M2-35 (melder_2,
    22:00:15Z, NOTICE): its CI task is closed with nothing in either document; a closing rebuild after melder_1
    covers its files.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md:377-407
  - context_compass/tickets/tasks/completed/2026-10-24_ci_lane_loose_ends_task.md:1-13
  - src/melder/__version__.py:12-12
  IMPACT: the write order holds - rebase the dry run on the 5,739/12,552-line documents now, apply only after
    melder_1's turn-in NOTICE; this landing will then be the last, so V2 (both builders, then --check) is this
    story's, covering melder_2's inputs too.
  NEXT: rerun the dry run on the current documents and read what it does to melder_1's new lines.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:05:58Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebased dry run on the documents as melder_1's 0.2.8267 edits left them (5,739 and 12,552 lines): all 81
    operations still anchor once; src_architecture 5,739 -> 4,784 (-955), src_components +90; melder_1's new first
    invariant, its two REMOVED markers, its Breaking failure modes and its handoff entry are kept as written (they
    are after the release-note boundary). Of 1,137 removed lines, 1,117 are in git 3bedd65bb; the other 20 are
    melder_1's own: the per-version clauses of its five 0.2.8267 C1 notes (the change is recorded in its 0.2.8267
    handoff entry and the release note), its five `verified_at` stamps (replaced by this run's remeasure) and its
    remapped conduit.py citation line (rewritten from source as 5601-5603).
  EVIDENCE:
  - context_compass/artifacts/src_architecture_to_spec_20261024/dryrun_rebase_0_2_8267/preservation_unaccounted.txt:1-20
  - context_compass/artifacts/src_architecture_to_spec_20261024/dryrun_rebase_0_2_8267/operations_report.md:1-1801
  - context_compass/tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md:377-407
  IMPACT: the apply run is a rerun of this one on whatever melder_1's turn-in leaves; every removed line has a
    named home (3bedd65bb, src_components, the 0.2.8267 handoff entry, or the remeasure).
  NEXT: wait for melder_1's turn-in NOTICE; then E0 baseline copies, the apply run, both indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:29:44Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M1-54 (melder_1, 22:16:36Z, NOTICE): STORY-2026-10-24-remove_many_child_holder_ownership is
    turned in - notched 0.2.8267 and rebuilt last, both builders' `--check` print only OK; src_architecture and
    src_components are as M1-53 described, with no edit since (both written 21:49:23Z; both indexes `--check` OK
    at 22:29:44Z over 5,739 and 12,552 lines); its tests documents, graph and release note changed too. The
    shared documents are this pass's to apply; it lands no source, so it takes no notch. C1 is done: both lanes'
    writes have landed (melder_0 M0-218, melder_1 M1-54).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md:1-14
  - context_compass/system_docs/src_architecture_index.md:9-19
  - src/melder/__version__.py:12-12
  IMPACT: the entry gate is met. E0 is captured now, and this landing is the last, so V2 also covers melder_1's
    and melder_2's builder inputs.
  NEXT: E0 - copy both documents to the artifact's e0_baseline/ and capture their multisets; then the final dry run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:31:35Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: E0 taken at 22:30:47Z, before any edit: both documents copied to the artifact's e0_baseline/ (sha256
    36116e30... and 490d1262..., the two indexes' content hashes) with their normalized line multisets (5,051 and
    9,867 distinct lines). The final dry run on them (dryrun_final/) anchors all 81 operations once: src_architecture
    5,739 -> 4,784 (-955), src_components 12,552 -> 12,642 (+90); of 1,137 removed lines 1,117 are in git 3bedd65bb
    and the other 20 are the same melder_1 lines the rebased run listed (its five 0.2.8267 C1-note clauses, its five
    `verified_at` stamps, its remapped conduit.py citation line); no added line over 118 characters; no problem
    reported. Both results equal the rebased run's except the remeasure stamps and the Updated dates.
  EVIDENCE:
  - context_compass/artifacts/src_architecture_to_spec_20261024/e0_baseline/src_architecture.e0.multiset.txt:1-5051
  - context_compass/artifacts/src_architecture_to_spec_20261024/e0_baseline/src_components.e0.multiset.txt:1-9867
  - context_compass/artifacts/src_architecture_to_spec_20261024/dryrun_final/preservation_unaccounted.txt:1-20
  - context_compass/artifacts/src_architecture_to_spec_20261024/dryrun_final/operations_report.md:1-1801
  IMPACT: the apply run is this run with --apply, so the preservation accounting is already known; V1 repeats it
    over the files on disk.
  NEXT: run the script with --apply, then regenerate both indexes and run --check on each.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:35:13Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Applied at 22:31:53Z (APPLIED, exit 0, 78 + 3 operations): src_architecture 5,739 -> 4,784 lines (-955),
    src_components 12,552 -> 12,642 (+90); both indexes regenerated, `--check` OK (61 and 156 sections). V1 on the
    files on disk. Preservation: 1,137 normalized lines removed over both documents, 1,117 in git 3bedd65bb, the
    other 20 exactly the dry run's named melder_1 lines (its 0.2.8267 handoff entry and the release note carry the
    note clauses, the remeasure replaced the stamps, the conduit.py citation is rewritten from source as
    5601-5603). Quality Gate: one H1; the 17 contract sections in order, the five extra H2s kept; no
    unclosed-bracket heading; Unknowns kept with their targets; 164 C1 entries, all five fields, remeasured this
    run, 0 stale, 164 of 164 in src_graph_index; 0 numeric citations out of bounds; the spec's two searches return
    nothing on either document and the broader spellings (system_docs, artifacts/, design_engineer/) nothing on
    src_architecture (src_components' three are Story 2's); no absolute path; no line over 120 characters added.
    Citations opened land on their symbols: spellbook.py:4107 `_apply_notch`, conduit.py:5652 `notch_spell`,
    bind.py:723 `assert_allowed`. Rubric after, from disk (src_architecture profile): Fidelity 4 (citations in
    bounds, most not reopened this pass, e.g. :523); Contract completeness 4 (the handoff still carries the
    0.2.8228-0.2.8267 change log, :4471-4784, kept on the owner's word); Depth 5; Addressability 3 (`## Data Flows
    and Sequences` :663 and `## Diagrams` :3969 are containers, both contract sections); Join integrity 5; Mirror
    agreement 3 (tests_architecture: the 17 sections in order, index current, terminology not reviewed). Total
    81/100, band B (was 69, C).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1-4784
  - context_compass/system_docs/src_architecture_index.md:9-19
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/system_docs/tests_architecture.md:3-921
  - context_compass/artifacts/src_architecture_to_spec_20261024/apply_run/preservation_unaccounted.txt:1-20
  IMPACT: the exit gate's document checks pass; what remains is the closure and the V2 rebuild, which runs last.
  NEXT: close the story (summary, completed/, board and artifact sync, the layout NOTICE), then V2 on Python 3.14.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (melder_3's chat report to the owner, 2026-10-24, after the rebuild)
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
Done (melder_3, 2026-10-24). src_architecture is at its authoring spec and 955 lines lighter (4,784); the component
mechanics it recorded before 0.2.8228 are in src_components only, and its change log keeps 0.2.8228 on. The
MutationResearch boundary inventory now sits in src_components' Subcomponent: MutationResearch Root (ResearchSet
Registry), overlapping the entry's own list until Story 2 folds the two. Remaining in the epic: the V2 rebuild
(next, last), then Story 2 (src_components to its own spec).

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
