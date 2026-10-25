# Task: Cut the 0.2.8265 release note into its own file

- Completed: 2026-10-24T22:53:33Z
- Summary: `release_docs/0.2.8265.md` holds the 0.2.8265 release notes byte for byte as released (the running note at
  the tag's commit 2d6c75233); `release_docs/next_version_release.md` holds only what landed since - melder_0's cache
  section, melder_1's `many` section, their packaging bullets, melder_2's pip bullet, a bind-guard bullet and the
  rebuild line (127 lines). No source, no notch. Rebuild last, after the closure.

## Metadata
- Task ID: TASK-2026-10-24-cut_release_note_0_2_8265
- Story: none (standalone, owner-directed)
- Status: done
- Owner: Mark
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T22:43:20Z
- Updated: 2026-10-24T22:53:33Z

## Objective
The 0.2.8265 release's notes live in `release_docs/0.2.8265.md`, exactly as they were released at the 0.2.8265 tag,
and `release_docs/next_version_release.md` holds only what landed after that release (0.2.8266 and 0.2.8267), so the
running note reads as the next release. The owner, chat 2026-10-24: "can you please take the melder 0.2.8265 release
you added your stuff into and move that into another file next to it? because its got the old release stuff we
already had in there in it can you do that?"

## Ticket Contract
- ENTRY_GATE: the owner's request above; this task's board row; melder_3's rebuild for its closed lane finished
  before any write under release_docs/ (its LLM check reads them).
- EXECUTION_BOUNDARY: `release_docs/0.2.8265.md` (new) and `release_docs/next_version_release.md`; this ticket and
  the boards. No src, no notch, no system documents.
- DEPENDENCIES: the note as released (`release_docs/next_version_release.md` at commit 2d6c75233, the commit the
  0.2.8265 tag names); STORY-2026-10-24-src_architecture_trim_to_spec (closed; its rebuild pending).
- EXIT_GATE: `0.2.8265.md` byte-equal to the released note; the running note carries exactly the entries added since
  the release (every line of today's note accounted for in one of the two files); rebuild last, both checks OK.
- FAILURE_ESCALATION: CONFLICT by mailbox if another agent holds a release_docs file; DECISION_REQUEST to the owner
  if the released note is ambiguous.

## Scope Boundaries
- In scope: the two release_docs files; a cross-reference in the 0.2.8267 section that pointed at a section that
  stays with 0.2.8265.
- Out of scope: rewording released text (the cut stays as released, as `0.2.8227.md` did); a release cut of
  0.2.8267 (the owner's call).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: both files are written and checked (FACT note of the write); the rebuild runs last, after
  this closure. Routine closure of the owner's request.
- from_state (earlier): draft
- to_state (earlier): in_progress
- transition_reason: the owner's request (chat 2026-10-24), quoted in the Objective.

## Steps / Checklist
- [x] Wait for melder_3's rebuild (its ACK to M1-57).
- [x] Write `0.2.8265.md` from the released note; check it byte-equal.
- [x] Reduce `next_version_release.md` to the entries added since 0.2.8265; account for every line.
- [x] Closure, board sync; the rebuild runs last, after the closure.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- `release_docs/0.2.8265.md`
- `release_docs/next_version_release.md`, 0.2.8266-0.2.8267 only

## Files / Paths Impacted
- release_docs/0.2.8265.md
- release_docs/next_version_release.md

## Validation
- The accounting check and the byte comparison ran (FACT note); the rebuild checks run after the closure.
- Recommended commands:
  - `python src/melder/_build_assets/_build_asset_runner.py --check`
  - `python llm_support/_builder.py --check --include-untracked`

## Risks / Rollback Notes
- A line of today's note lost in the split: every line is checked into one of the two files before the write.
- Rollback: restore `next_version_release.md` from git and delete `0.2.8265.md`.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1; synaptic_python_developer; prose, evidence.
- Published By: melder_1 to the local filesystem on the owner's machine; the owner commits.
- Independent Review: none claimed.

## Notes
- DATETIME: 2026-10-24T22:43:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The release was never cut in the repository: release_docs/ holds `0.2.8227.md` and the running note, whose
    header read `# Melder 0.2.8265` at the release commit 2d6c75233 (1,429 lines, LF). Since then the running note
    gained exactly three things: melder_0's section "A cache file that cannot be saved no longer fails a meld" and
    its packaging bullet (0.2.8266), melder_2's pip bullet (no notch), and melder_1's 0.2.8267 work - its section
    in place of the released "A `many` dependency is disposed with the object that holds it", three edited
    packaging bullets (the two holder-record bullets and the bind-guard count) and a documentation bullet - plus the
    header and the rebuild line. Nothing else differs (a line diff of the two revisions).
  EVIDENCE:
  - release_docs/next_version_release.md:213-277
  - release_docs/next_version_release.md:1287-1322
  - release_docs/next_version_release.md:1474-1491
  IMPACT: The cut is the released note unchanged; the running note is those three changes alone, the three edited
    bullets turned into one new bind-guard bullet, and the 0.2.8267 section's "below" reference fixed.
  NEXT: Ask melder_3 to ACK when its rebuild is done; then write both files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:43:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M3-4 consumed (melder_3, NOTICE): its src_architecture trim is closed (5,739 -> 4,784 lines) and its rebuild
    runs after that closure. For melder_1's next edit of src_architecture: an invariant or failure mode states
    today's rule and its mechanism, with no "before 0.2.x" history or chat timings; component mechanics go to the
    src_components entry; a C1 note is a description only, what changed goes in the lane's handoff entry; one dated
    handoff entry per lane, at the top; no path into context_compass in any spelling. src_components gets the same
    pass next (its Story 2): melder_1 tells melder_3 before writing it. This task writes neither document.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md:1-12
  IMPACT: This task waits for melder_3's rebuild before writing release_docs/ (M1-57 asks for its ACK).
  NEXT: Wait for melder_3's ACK.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:45:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Both files are built in /tmp from today's note and the released blob, not yet written: `0.2.8265.md` is the
    released note byte for byte (1,429 lines, LF, "**Unreleased**" kept as `0.2.8227.md` kept it); the running note
    (127 lines) is `# Melder 0.2.8267`, melder_0's cache section, melder_1's `many` section (its "see
    `Existence.managed_spell_quantity` below" now names the existence in place, since that section stays with
    0.2.8265) and a packaging section of melder_0's, melder_2's and melder_1's bullets, one new bind-guard bullet
    (629 at 0.2.8267, `HolderDisposalEntry` left) and the rebuild line. Accounting: of today's 1,491 lines, 12 are
    in neither file, and all 12 are intended - the reworded "below" sentence (2) and melder_1's three edits of
    released packaging bullets (10), whose released text stays in the cut and whose news is in the new bullets.
  EVIDENCE:
  - release_docs/next_version_release.md:271-272
  - release_docs/next_version_release.md:1344-1346
  - release_docs/next_version_release.md:1359-1360
  - release_docs/next_version_release.md:1378-1382
  IMPACT: The write is two file replacements with nothing left to decide.
  NEXT: On melder_3's ACK, rebuild both files from the then-current note, check the accounting again and write them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:52:47Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_3's rebuild is done (its epic's MEASURE note of 22:46:43Z: the asset runner's and the LLM builder's
    --check print only OK; release_docs untouched), so the release_docs write can go ahead without its ACK. M0-221
    consumed (melder_0, NOTICE): its lane adds one untracked Windows-only test file,
    tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py (no notch, no release-note
    entry), and leaves it to this task's rebuild to take it into the LLM bundles' tests corpus with
    --include-untracked.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-24_src_architecture_to_spec_epic.md:212-229
  - context_compass/tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md:1-12
  IMPACT: This task's rebuild runs with --include-untracked and covers melder_0's new test file.
  NEXT: Rebuild both files from the current note, recheck the accounting and write them.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:53:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Both files are written, from a snapshot of the running note taken and compared just before the write:
    `release_docs/0.2.8265.md` (new, untracked) is byte-equal to the released note (96,987 bytes, 1,429 lines, LF;
    sha256 07277834260d8ce4...), and `release_docs/next_version_release.md` is the 127-line note of the PLAN note
    (git: 31 insertions, 1,395 deletions). The accounting ran again on the snapshot: the same 12 intended lines are
    in neither file, every other line of the old note is in one of the two.
  EVIDENCE:
  - release_docs/0.2.8265.md:1-1429
  - release_docs/next_version_release.md:1-127
  IMPACT: The running note reads as the next release; the 0.2.8265 notes are kept as released.
  NEXT: Record the closure.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:53:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closure. The EXIT_GATE is met but for the rebuild, which runs after this pass: the cut is byte-equal to the
    released note, the running note carries exactly the entries since the release, and every line is accounted for.
    Acceptance: routine completion of the owner's request; no independent review was requested. The board row and
    detail are removed and a closed anchor added; no artifacts were made.
  EVIDENCE:
  - release_docs/0.2.8265.md:1-3
  - release_docs/next_version_release.md:1-3
  IMPACT: The task is turned in.
  NEXT: Rebuild last (asset runner in the /tmp mirror, the LLM builder with --include-untracked, both checks) and
    record it here; NOTICE melder_0, melder_2 and melder_3; tell the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T22:56:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuild, last (22:54-22:56, Python 3.14.7 free-threaded): the asset runner, run in the /tmp mirror, changed no
    asset (it reads no release_docs file) and its --check in the repository prints three OK lines at 0.2.8267. The LLM
    builder (--include-untracked) left src unchanged and wrote tests (1,146 files: melder_0's new Windows-only test
    file joined, M0-221) and other (413: the new `release_docs/0.2.8265.md` joined); its --check prints OK for src,
    tests and other. No .git/index.lock appeared.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/rebuild_s4_assets.py:1-122
  - llm_support/_builder.py:80-100
  IMPACT: The change set is complete with every check OK.
  NEXT: None in this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: move the 0.2.8265 release's notes into `release_docs/0.2.8265.md`; keep only the later entries in the running
  note. State: done (2026-10-24T22:53:33Z), melder_1; both files written and checked.
- Next: none - rebuilt last with every check OK (MEASURE note); NOTICEs sent to melder_0, melder_2 and melder_3.

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
