

# Task: dependabot_ci_requirements - clear the open Dependabot alerts on the CI requirement pins

## Metadata
- Task ID: TASK-2026-11-07-dependabot_ci_requirements
- Story: none - a standalone task on the owner's word
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-11-07T15:31:12Z
- Updated: 2026-11-07T15:31:12Z

## Objective
The owner asked (chat 2026-11-07): "fix the github issue with the requirements.txt go look up dependabot stuff" -
"the dependabot stuff is all the requirements.txt for the CICD stuff". Bump every pin an open alert names to its
first patched version (or later), through each file's own tooling, so the alerts close once the owner pushes.

## Ticket Contract
- ENTRY_GATE: the owner's request (chat 2026-11-07); the open alert list (Notes); .github/ci_cd/README.md read before
  any edit under .github/ (special_instructions/ci_cd_guide.md); a board row routes here.
- EXECUTION_BOUNDARY: .github/provenance/requirements.txt (and its source/lock inputs, if it is generated), the root
  requirements.txt and uv.lock (setuptools), .github/ci_cd/ docs when they name the pinned versions.
- DEPENDENCIES: special_instructions/ci_cd_guide.md; the completed PyPI provenance epic (its workflow uses these pins).
- EXIT_GATE: every named package at or above its first patched version, hashes regenerated where the file carries
  them; `python -m pytest tests/unit/github_workflows` passes; hosted CI runs reported "Not run" until the owner sees
  them; the rebuild and both `--check` runs print only OK.
- FAILURE_ESCALATION: DECISION_REQUEST when a patched version needs a newer Python or breaks another pin, or an alert
  has no patched version left vulnerable after the bump.

## Scope Boundaries
- In scope: the 26 open alerts (24 in .github/provenance/requirements.txt, 2 setuptools in requirements.txt and uv.lock).
- Out of scope: Melder's runtime dependencies (it has none), CI workflow behaviour, dismissing alerts on GitHub,
  commit and push (the owner's).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's request (chat 2026-11-07) and the alert list (Notes).

## Steps / Checklist
- [x] List the open Dependabot alerts (Notes).
- [ ] Read .github/ci_cd/README.md and how each file is produced; bump the pins through that tooling.
- [ ] Validate: tests/unit/github_workflows; each named package's resolved version against its advisory range.
- [ ] Rebuild and both `--check` runs last (shared with the license task's change set).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Bumped pins (with hashes where used); the alert-to-version table in Notes.

## Files / Paths Impacted
- .github/provenance/requirements.txt (and its inputs, if generated)
- requirements.txt, uv.lock
- .github/ci_cd/ (only if it names the versions)

## Validation
- Not run.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -m pytest tests/unit/github_workflows -q`

## Risks / Rollback Notes
- A bumped tool can change provenance/publish behaviour in hosted CI, which only the owner's runs show; rollback is
  reverting the pins.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

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
  - which pins each alert names and how each requirements file is produced
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-11-07T15:31:12Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T15:31:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: 26 open Dependabot alerts on Synaptic724/melder (`gh api repos/Synaptic724/melder/dependabot/alerts`,
    state=open), read 2026-11-07. .github/provenance/requirements.txt: PyJWT x17 (#2-#12, #16-#19; first patched
    2.14.0 or 2.15.0; #17 lists no patched version but its range ends at 2.13.0), urllib3 x3 (#13-#15; 2.8.0),
    pyasn1 x4 (#23-#26; 0.6.5), dnspython (#22; 2.9.0), cryptography (#1; 50.0.0). requirements.txt and uv.lock:
    setuptools (#20, #21; low; 84.1.0). Targets: PyJWT >= 2.15.0, urllib3 >= 2.8.0, pyasn1 >= 0.6.5, dnspython >=
    2.9.0, cryptography >= 50.0.0, setuptools >= 84.1.0.
  EVIDENCE:
  - .github/provenance/requirements.txt:1-1
  - requirements.txt:1-1
  IMPACT: The bump set is known; how each file is produced decides how it is bumped.
  NEXT: Read .github/ci_cd/README.md and the provenance file's header, then bump through its tooling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: clear the 26 open alerts by bumping the CI requirement pins (the owner: "all the requirements.txt for the
  CICD stuff"). State: in_progress, melder_0.
- Next: (1) read the CI guide and how the files are produced; (2) bump and regenerate; (3) validate, then the shared
  rebuild; the alerts close when the owner pushes.

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
