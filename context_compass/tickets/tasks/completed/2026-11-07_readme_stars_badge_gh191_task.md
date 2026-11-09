# Task: README stars badge in the social style (GitHub #191)

- Completed: 2026-11-07T08:03:29Z
- Summary: README.md's stars badge is the social-style badge GitHub #191 specifies, linking to the stargazers page; one line changed, no notch (no src/ change); running-note line added.

## Metadata
- Task ID: TASK-2026-11-07-readme_stars_badge_gh191
- Story: none (standalone; external record https://github.com/Synaptic724/melder/issues/191)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p3
- Created: 2026-11-07T08:02:09Z
- Updated: 2026-11-07T08:03:29Z

## Objective
GitHub issue #191 (SynapticAISystems, 2026-10-12): the README carries a GitHub Stars badge in the social style the
Context Compass README uses, targeting `Synaptic724/melder`, linking to its stargazers page. The owner's go: chat
2026-11-07, "lets go ahead and try and finish those 4 github tickets".

## Ticket Contract
- ENTRY_GATE: the owner's go above; no local ticket existed for #191.
- EXECUTION_BOUNDARY: README.md (one badge line) and its entry in release_docs/next_version_release.md. No src/
  change, so no notch.
- DEPENDENCIES: none.
- EXIT_GATE: the README diff is the one badge line; the running note names it; the issue answered and closed.
- FAILURE_ESCALATION: DECISION_REQUEST if the owner wants both star badges kept.

## Scope Boundaries
- In scope: the stars badge line of README.md; the running note's Packaging and documentation section.
- Out of scope: every other README line, the "SUPPORT US" wording and link, code, TOML and other docs.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the README diff is the one badge line (MEASURE note of this date); GitHub #191 answered and closed.
- earlier:
- from_state: ready
- to_state: in_progress
- transition_reason: the owner's go above (PLAN note of 2026-11-07T08:02:09Z).

## Steps / Checklist
- [x] Read the issue and the README's badge block.
- [x] Replace the plain stars badge with the issue's social badge.
- [x] Validate the diff; close; answer and close the issue.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.

## Deliverables
- README.md line 22 carries the issue's badge; a running-note line.

## Files / Paths Impacted
- README.md
- release_docs/next_version_release.md

## Validation
- Run 2026-11-07: `git diff --ignore-cr-at-eol -- README.md` is 1 insertion and 1 deletion, the badge line. Badge rendering on
  GitHub: Not run (it shows once the owner pushes).

## Risks / Rollback Notes
- One line; revert by restoring the previous badge text quoted in the PLAN note.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Validation status recorded
- [x] Board sync completed for closure anchor update.

## Artifact Links (Optional)
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
  - README badges
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; correct history only for factual errors.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and the README edit; created 2026-11-07.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-11-07T08:02:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: README line 22 already carries a plain stars badge, `[![GitHub stars](https://img.shields.io/github/stars/Synaptic724/melder)](https://github.com/Synaptic724/melder)`, added 2026-10-24
    (0fddab923, after the issue was filed on 2026-10-12): default style, linking to the repository root. The issue
    asks for the social style linking to the stargazers page and no second star callout. Replacing that line with
    the issue's exact badge meets the issue in one line; adding a second badge would show two star counts.
  EVIDENCE:
  - README.md:16-26
  - README.md:36-37
  IMPACT: One README line changes; the "SUPPORT US" wording and link stay as they are.
  NEXT: Replace line 22 and add the running-note line.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-11-07T08:03:29Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: README.md line 22 now reads `[![Stars](https://img.shields.io/github/stars/Synaptic724/melder?style=social)](https://github.com/Synaptic724/melder/stargazers)`;
    `git diff --ignore-cr-at-eol --stat -- README.md` against HEAD de33cff49 (branch codex_features2) reports 1 insertion,
    1 deletion. The working-tree README is CRLF on every line while HEAD stores LF (it was so before this edit; the
    edit replaced bytes and kept the CRLF), so a Linux `git diff` without --ignore-cr-at-eol shows the whole file;
    a commit from the owner's Windows checkout normalizes it. The running note's Packaging and documentation section
    names the change.
  EVIDENCE:
  - README.md:22-22
  - release_docs/next_version_release.md:51-58
  IMPACT: #191's change is in the owner's working tree; it ships with his next commit. No notch (no src/ change).
  NEXT: Answer and close GitHub #191; the asset and bundle rebuild runs once at the end of this pass.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Done 2026-11-07: the README stars badge is #191's social badge linking to stargazers; one line; running-note line
  added. Delivery: uncommitted in the owner's working tree (codex_features2 at de33cff49); README.md is CRLF in the
  working tree against LF in HEAD (pre-existing), so commit it from the Windows checkout.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
