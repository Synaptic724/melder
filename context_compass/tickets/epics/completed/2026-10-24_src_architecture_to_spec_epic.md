

# Epic: src_architecture to its authoring spec, about 1,000 lines lighter

- Completed: 2026-10-25T01:34:36Z
- Summary: src_architecture is at its authoring spec and 955 lines lighter (5,739 -> 4,784; rubric 69 -> 81, B), its
  component mechanics and the MutationResearch inventory moved to src_components (Story 1); src_components is at its
  own spec and 768 lines lighter (12,642 -> 11,874; rubric 66.5 -> 84.5, B) (Story 2). Both indexes and both asset
  rebuilds `--check` OK at v0.2.8267; no source, no notch, no release-note entry; tests Not run.

## Metadata
- Epic ID: EPIC-2026-10-24-src_architecture_to_spec
- Status: done
- Owner: Mark (owner; scope and acceptance)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T20:58:00Z
- Updated: 2026-10-25T01:34:36Z
- Target Window: 2026-10; edits apply after the two lanes now writing the same documents land (Dependencies)
- Related Program/Initiative: system documents kept to their authoring instructions

## Problem / Opportunity
`context_compass/system_docs/src_architecture.md` is 5,645 lines (415,505 bytes). Its authoring instructions ask
for a re-entry-safe C4 document built on a 17-section contract and reject component-level deep dives in it. Most of
its length is history and component detail rather than architecture:
- `## Context / Handoff Summary` is 646 lines, a dated change log back to 2026-07-25; the Handoff Rule asks for a
  concise summary of what changed, what remains unknown and where the next reader should start.
- `## Operational Invariants` (1,350 lines) and `## Failure Modes and Error Paths` (629 lines) carry
  release-by-release history, chat quotes, ticket ids and timings inside their entries.
- `## C1 Code Map (Core Only)` (1,153 lines) carries per-version change notes beside its five contract fields.

The owner asked (chat, 2026-10-24): bring it to spec, clean out old change-log detail and keep the recent entries,
remove what the src_architecture instructions do not call for, aim at about 1,000 lines fewer if that is right, and
move component material to src_components where it belongs. His first message of the session also asked that
src_components be brought to its own spec where it is not.
EVIDENCE:
- context_compass/system_docs/src_architecture_index.md:26-91
- context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:114-133
- context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:350-366

## MRP Alignment (Most Reasonable Product)
The document is read whole at every engineer onboarding and ships in the wheel as the packaged architecture
hardcopy. Every line of history is paid for by every reader on every re-entry, while the history itself already
lives in git and the release notes. The core to get right is the C4 content: boundaries, sequences, the rules in
force and the failure behaviour of today, each still evidenced. Component mechanics belong one level down in
src_components, where the reading hierarchy sends a reader who needs them.

## Ticket Contract
- ENTRY_GATE: an attention_board row routes to the active story; the Content Preservation baseline is captured
  immediately before the first edit; melder_0 (F5) and melder_1 (many-child turn-in) have landed their writes to
  both documents, or an order has been agreed with them through the mailbox.
- EXECUTION_BOUNDARY: `context_compass/system_docs/src_architecture.md`, `src_components.md` and their indexes, and
  the asset rebuilds a system_docs change requires. No change to `src/`, tests, `__version__` or the release note
  (a context_compass-only change takes no notch). No change to the authoring instructions or other policy.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0; its F5 writes both documents);
  STORY-2026-10-24-remove_many_child_holder_ownership (melder_1; its turn-in merges a patch into both).
- EXIT_GATE: Story 1 accepted with the Quality Gate passed, the preservation gate accounted, the rubric scored, both
  indexes and both asset rebuilds `--check` OK; Story 2 accepted or deferred by the owner; board and artifact sync.
- FAILURE_ESCALATION: DECISION_REQUEST when a cut would remove a rule in force or an owner ruling; CONFLICT when
  another lane writes the same sections; BLOCKER when a gate cannot pass.

## Goals (Outcomes)
- src_architecture passes its Quality Gate, the portability rule included.
- About 1,000 lines fewer, from history removed and component mechanics moved, with no rule in force lost.
- Material that moves lands in src_components to its entry contract, and is not duplicated there.
- The recent change-log entries stay; older ones are left to git and the release notes.

## Non-Goals (Explicit Exclusions)
- No change to Melder source, tests, version or release note.
- No new behaviour claims: condensing removes history and duplication, it does not restate what a rule says.
- No change to the authoring instructions or any other policy document.
- No edit of src_graph (generated).

## Scope Boundaries
- In scope: src_architecture and src_components with their indexes; this epic's tickets; the boards; the rebuild.
- Out of scope: tests_architecture and tests_components (pending set of another lane), README, `docs/`.

## State Transition Event
- from_state: in_progress (validation)
- to_state: done
- transition_reason: the EXIT_GATE is met: Story 1 accepted (the owner's reply to its report, chat 2026-10-24: "ok
  cool good job") and Story 2 closed under the same scope (2026-10-25T01:12:33Z); both indexes and both asset
  rebuilds `--check` OK (the MEASURE of 2026-10-25T01:30:45Z); board and artifact state synced. Routine closure
  under the owner's scope of 2026-10-24; he may reopen it.
- from_state (earlier): draft
- to_state (earlier): in_progress
- transition_reason (earlier): melder_3 certified by the owner, who set the scope in chat on 2026-10-24; the audit
  runs read-only while the two other lanes finish their writes to the same documents.

## Success Metrics
- src_architecture line count: about 1,000 lower, or the reason it is not recorded.
- Zero unaccounted lines in the Content Preservation Gate.
- The portability and absolute-path checks return nothing.
- Rubric score (src_architecture profile) recorded before and after.

## Requirements (Functional + Non-Functional)
- Baseline multiset of non-blank lines captured immediately before the first edit.
- Every removed line accounted for: kept, moved to a named src_components section, or history left to git (named
  revision) and the release notes.
- Each document's index regenerated in the same pass as its edit; `--check` OK.
- The asset runner and the llm_support builder, then both `--check`, on Python 3.14, as the last step.

## Constraints / Assumptions
- Shared files: re-read before each write; never overwrite another agent's change.
- Device VM: read-only git with `GIT_OPTIONAL_LOCKS=0`; load Python 3.14 per command; `TMPDIR` under /tmp.
- Approval loop (synaptic overlay): the owner's 2026-10-24 instruction confirms this scope; anything beyond it
  goes back to him first.

## Dependencies / External References
- TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0)
- STORY-2026-10-24-remove_many_child_holder_ownership (melder_1)

## Milestones (Track Progress)
- [x] Milestone 1: audit - section and entry dispositions recorded in Story 1 Notes.
- [x] Milestone 2: apply - the other lanes' writes landed, edits applied, gates pass.
- [x] Milestone 3: rebuild - both builders `--check` OK; Story 1 closed.
- [x] Milestone 4: src_components - Story 2 done or deferred by the owner (done; closed 2026-10-25T01:12:33Z).

## Stories (Required to Complete)
- [x] Story: STORY-2026-10-24-src_architecture_trim_to_spec - audit, trim, migrate, re-index, gates, rebuild
  (closed 2026-10-24T22:37:34Z, tickets/stories/completed/).
- [x] Story: STORY-2026-10-24-src_components_to_spec - audit, clean to spec, re-index, gates, rebuild (opened on
  the owner's go, 2026-10-24 16:15 MDT; closed 2026-10-25T01:12:33Z, tickets/stories/completed/).

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Agree the write order with melder_0 and melder_1 through the mailbox.
- [x] Task: Complete story STORY-2026-10-24-src_architecture_trim_to_spec.
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks (this epic and both stories: 29
  notes, the MEASURE of 2026-10-25T01:30:45Z).

## Acceptance Criteria (Epic Done)
- Story 1 accepted: 17 contract sections in order, portability clean, about 1,000 lines lighter or the reason
  recorded, preservation gate accounted, rubric recorded, indexes and rebuilds `--check` OK.
- Story 2 accepted, or deferred by the owner.

## Risks / Mitigations
- Concurrent writers to the same documents -> apply after they land; NOTICEs; re-read before every write.
- Silent content loss -> preservation gate before and after; moved text carried verbatim.
- A rule in force removed with its history -> remove history clauses only; uncertain text stays; owner rulings are
  kept or raised as DECISION_REQUEST.
- Stale ranges -> indexes regenerated in the same pass and checked.
- Stale packaged hardcopy -> asset rebuild last.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence (each transition cites the stories' closures).
- [x] No closure while required stories are incomplete or unaccepted (both stories done and accepted).
- [x] No program claims without source evidence from story/task notes (the Notes cite the stories, the output).

## Validation / Test Approach
- `index_document.py --check` on both documents; the two portability searches; heading-order check against the
  contract; preservation multiset diff over the document and its migration targets; rubric score; the asset runner
  and llm_support builder with `--check`.

## Rollout / Adoption Plan
- A mailbox NOTICE to the active agents naming where new invariants, failure modes and handoff lines go after the
  trim, so later lanes do not regrow the history.

## Open Questions
- Where "recent" starts in the handoff log: proposed as the release-note boundary (release_docs/0.2.8227.md ends
  at 0.2.8227; the running note starts at 0.2.8228); the owner may move the line. RESOLVED 2026-10-25: both
  documents keep the change log from 0.2.8228 on behind an OLDER HISTORY pointer (Decision Log).

## Decision Log
- 2026-10-24: owner scope (chat): trim to spec, keep the recent change log, about 1,000 lines, move component
  material to src_components.
- 2026-10-24: owner (chat): the next session on this lane onboards as design_engineer.
- 2026-10-24: owner (chat, 16:15 MDT): "go ahead and check out src_components next please" - Story 2 opened
  while Story 1 waits for melder_1's turn-in; Story 2's edits follow Story 1's apply and rebuild.
- 2026-10-25: the change-log boundary is the release-note boundary, 0.2.8228 on, in both documents
  (src_architecture.md:4767-4772, src_components.md:11869-11874); the owner accepted Story 1 on it ("ok cool good
  job", chat 2026-10-24) and can still move it.
- 2026-10-25: closed as routine work under the owner's scope of 2026-10-24 (State Transition Event).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/src_architecture_to_spec_20261024/ (Story 1; deleted at its closure, 2026-10-24T22:37:34Z)
  - artifacts/src_components_to_spec_20261024/ (Story 2; deleted at its closure, 2026-10-25T01:12:33Z)
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: each story's closure, after its preservation gate is accounted
- DISPOSITION RECORDED (2026-10-25): both folders deleted at their stories' closures - the accounting is in each
  story's Notes and the old document text in git (3bedd65bb, 9f240166f); artifact_board.md lists both as cleared.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_3 (synaptic_python_developer); prose; revision 1 of this epic.
- Published By: UNKNOWN before publication (local files; the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-24T20:58:00Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: One active story does the work: audit and dispositions first, read-only, then the edits once melder_0's
    F5 and melder_1's turn-in have landed their writes to both documents, then gates and the rebuild. The
    src_components conformance pass is a second story, created when the first closes.
  EVIDENCE:
  - context_compass/attention_board.md:110-111
  - context_compass/tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md:79-80
  IMPACT: editing now would collide with two lanes writing the same sections; the audit does not need to wait.
  NEXT: send melder_0 and melder_1 a NOTICE asking them to report when their writes to both documents land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T21:46:21Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Story 1 is audited and scripted: its dry run takes src_architecture from 5,700 to 4,749 lines with every
    removed line accounted for (git 3bedd65bb, or moved to src_components), and it waits only for melder_1's turn-in
    (write order M1-51; melder_0's writes done, M0-218). Story 2 (src_components to its own spec) starts from three
    items found on the way - its citation recipe's `system_docs` leak, its stale `Conduit.link` citation and the
    MutationResearch inventory to fold - plus its own rubric pass.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-24_src_architecture_trim_to_spec_story.md:1-12
  - context_compass/artifacts/src_architecture_to_spec_20261024/trim_src_architecture.py:1-771
  IMPACT: tranche order unchanged - Story 1 apply, gates and rebuild, then Story 2.
  NEXT: apply Story 1 on melder_1's NOTICE.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:46:43Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Story 1 closed (22:37:34Z) after melder_1's turn-in NOTICE (M1-54): src_architecture 5,739 -> 4,784 lines
    (-955) with the 17 contract sections in order and no path into the tooling, src_components 12,552 -> 12,642
    (+90, the MutationResearch inventory and a handoff entry); preservation accounted (1,117 removed lines in git
    3bedd65bb, 20 named melder_1 lines); rubric 69 -> 81 (B); its artifact folder deleted, the boards synced, the
    layout NOTICE sent (M3-3 to M3-5). V2, last, on Python 3.14.8: the asset runner wrote the three asset
    manifests at v0.2.8267 and its `--check` prints only OK (agent documentation, bind guard 629 entries, system
    documents); `llm_support/_builder.py` reports src, tests and other UNCHANGED (context_compass is outside its
    corpora) and its `--check` prints only OK.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md:1-12
  - context_compass/system_docs/src_architecture_index.md:9-19
  - llm_support/_builder.py:63-100
  IMPACT: milestones 2 and 3 are done; the epic's remaining work is Story 2 alone, whose entry gate (Story 1
    applied and rebuilt) is now met.
  NEXT: Story 2 B2 - read the example components document and score src_components entry by entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T01:14:56Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Story 2 closed (2026-10-25T01:12:33Z): src_components 12,642 -> 11,874 lines (-768) with the 12 contract
    sections in order, every C3 entry with its 12 fields in contract order and no path into the tooling; history out
    of the entries and the change log kept from 0.2.8228 on; stale claims corrected against source; the
    MutationResearch inventory folded; core = the C3 Key Files union (238), every range remeasured; Information
    Sources lists the 286 cited files. Preservation accounted (1,823 removed lines, 1,821 in git 9f240166f, 2 of
    Story 1's framing lines); rubric 66.5 -> 84.5 (B); index `--check` OK. Its artifact folder is deleted, the
    boards are synced and the layout NOTICE is sent (M3-6 to M3-8); this epic now holds the board row for V2.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_src_components_to_spec_story.md:1-12
  - context_compass/system_docs/src_components_index.md:9-19
  IMPACT: both stories are done; what is left is V2 (last) and this epic's closure.
  NEXT: V2 on Python 3.14.8 - the asset runner and the llm_support builder, each then `--check`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T01:30:45Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: V2 on Python 3.14.8 from the repository root (TMPDIR=/tmp, PYTHONDONTWRITEBYTECODE=1,
    GIT_OPTIONAL_LOCKS=0): `_build_asset_runner.py` wrote the three asset manifests at v0.2.8267 (agent
    documentation 469 entries, bind guard 629, system documents 4) and its `--check` prints only OK lines; the
    system-documents manifest records __architecture__ at 4,784 lines (sha 98e905a1) and __components__ at 11,874
    (sha 6381710a), the two documents as they are on disk. `llm_support/_builder.py --include-untracked` reports
    src, tests and other UNCHANGED - its corpora leave out context_compass/ and the generated `_build_assets`
    manifests and payloads - and its `--check --include-untracked` prints only OK lines. No git lock file was left.
    The microcycle check over this epic and its two stories: 29 notes, every field present and in order, types
    valid, scores 7 or more, 123 ranged evidence lines, no line over 120 characters. Tests: Not run (no source
    changed).
  EVIDENCE:
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:33-57
  - llm_support/_builder.py:63-100
  IMPACT: the exit gate's last item holds - both indexes and both rebuilds `--check` OK - so the epic can close.
  NEXT: close the epic (summary, status, transition, checklists, move to completed/, board sync), then re-run both
    `--check`s to show the closure left the assets current.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T01:34:09Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Findings for the owner, outside this epic's boundary, re-verified against source at closure. (1) Three
    creations.py docstrings still say a spell id hashes its resolved disposal names - the `ManyDisposalBucket`
    contract, `add_many_creations` and `register_many` - which is untrue since 0.2.8257 (the spell_id is the
    object's code; disposal names are a binding-manifest field), so whether one `many` key can carry two
    declarations (a rebind under other disposal names while the old bucket lives) is open; src_components records it
    as an UNKNOWN. (2) `ResearchLane.clear_anchor` is public by name and reachable through `ResearchSet.get_lane`,
    and it detaches a lane's ancestry without a journal entry, while `ResearchSet.detach` journals the same change.
    (3) The heading check `rg -n '^#{1,6} .*[([][^)\]]*$'` in all four authoring instructions does not parse in
    ripgrep 13.0.0 ("unclosed character class"); with `[(\[]` for `[([]` it parses, finds unclosed headings in a
    sample and returns nothing on either document. (4) release_docs/0.2.8227.md differs from HEAD only by CRLF line
    endings, like the other working-tree files, and needs nothing.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:23-30
  - src/melder/aether/conduit/creations/creations.py:727-760
  - src/melder/aether/conduit/creations/creations.py:791-820
  - src/melder/mutation_research/research_set/research_lane.py:775-809
  - src/melder/mutation_research/research_set/research_set.py:617-652
  - src/melder/mutation_research/research_set/research_set.py:1902-1962
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:379-379
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:321-321
  IMPACT: none blocks this epic; each is the owner's to schedule, since source and policy documents are outside its
    boundary.
  NEXT: close the epic and report the four to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (melder_3's chat report to the owner at this closure, 2026-10-25)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded (State
  Transition Event; tests Not run - no source changed; no review requested)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
Done (melder_3, closed 2026-10-25T01:34:36Z). src_architecture is at its authoring spec, 5,739 -> 4,784 lines,
rubric 69 -> 81 (B); src_components is at its own spec, 12,642 -> 11,874 lines, rubric 66.5 -> 84.5 (B); both
indexes and both asset rebuilds `--check` OK at v0.2.8267. No source, notch or release-note entry. Left for the
owner, outside this epic's boundary (the FACT note of 2026-10-25T01:34:09Z): the three creations.py docstrings that
still say a spell id hashes its disposal names, with the `many` bucket UNKNOWN in src_components;
`ResearchLane.clear_anchor`, public through `ResearchSet.get_lane`, which writes no journal entry; the authoring
instructions' heading pattern, which ripgrep does not parse. Owner direction: the next session on this lane onboards
as design_engineer. Next: none.

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
