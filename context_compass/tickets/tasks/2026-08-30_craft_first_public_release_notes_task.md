# Task: Craft Melder's first public release notes

## Metadata
- Task ID: TASK-2026-08-30-craft-first-public-release-notes
- Story: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T22:50:02Z
- Updated: 2026-08-30T23:21:07Z

## Objective
Create a truthful, compelling, user-facing Markdown release draft for Melder
v0.2.0, suitable for the first GitHub release and adaptable to PyPI.

## Ticket Contract
- ENTRY_GATE: Owner requested a release draft; attention routes here.
- EXECUTION_BOUNDARY: Read public README, metadata, examples, and architecture
  documentation; write one release-notes Markdown file and ContextCompass tracking.
- DEPENDENCIES: Committed version 0.2.0 and current public documentation.
- EXIT_GATE: Draft is evidence-grounded, installable/usable, concise enough for
  GitHub, and explicitly avoids unsupported performance or stability claims.
- FAILURE_ESCALATION: Mark unknown or omit any claim not supported by public docs/source.

## Scope Boundaries
- In scope: release positioning, highlights, install/quick-start, compatibility,
  documentation routes, tradeoffs, and first-release framing.
- Out of scope: tagging, commits, pushes, GitHub release creation, or PyPI publication.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The first-real-release draft is complete, reread, and
  validation-clean; owner wording acceptance remains.

## Steps / Checklist
- [x] Read README and current package/release metadata.
- [x] Read the public documentation/example routes referenced by README.
- [x] Draft and reread the v0.2.0 release notes.
- [x] Validate claims, links, formatting, and diff hygiene.
- [x] Run Ticket Microcycle during execution.
- [x] Document meaningful findings before continuing.

## Deliverables
- `RELEASE_NOTES_0.2.0.md`

## Files / Paths Impacted
- `RELEASE_NOTES_0.2.0.md`
- `context_compass/attention_board.md`
- This task.

## Validation
- Quick-start execution against repository source: pass (`QUICK_START_OK`).
- Markdown structure: pass (208 physical lines, 14 headings, eight balanced
  fence markers, one reference definition, no line over 120 characters).
- Public local link targets: present.
- Tracked-input `llm_support/_builder.py --check`: pass for all three corpora.
- Prospective include-untracked check: expected `other` staleness from this
  new root document; regenerate after staging and before commit.
- `git -c core.whitespace=cr-at-eol diff --check`: pass.

## Risks / Rollback Notes
- First-release language can overstate maturity; label alpha status and concrete tradeoffs.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation from unsupported claims.
- [ ] No closure without acceptance confirmation and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverable produced
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [x] Applicable anti-pattern checks are clear.
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for review routing

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - first public release positioning
  - user-facing capability summary
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: source-backed release claims, audience value, and exact next action.

## Notes
- DATETIME: 2026-08-30T22:50:02Z
  TYPE: PLAN
  CLAIM: Build the release narrative from public documentation and metadata,
    then verify every compatibility/capability claim before opening the draft.
  EVIDENCE:
  - `README.md`
  - `pyproject.toml`
  IMPACT: The first release will be useful marketing without unsupported hype.
  NEXT: Read the complete README and inventory existing release-note conventions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:12:18Z
  TYPE: FACT
  CLAIM: The complete README supports a two-level first-release narrative:
    a human-first dependency graph runtime in the foreground, with live
    linking, isolation, scopes, and inspection; and an explicitly optional
    expert ceiling for mediated agent rooms, persistence, governed structural
    change, and free-threaded execution.
  EVIDENCE:
  - `README.md:1-500`
  - `README.md:501-1072`
  IMPACT: The release opening should explain the usable DI/runtime core first,
    then summarize the advanced ceiling without turning the announcement into
    a catalogue or implying every reader needs agent-facing features.
  NEXT: Verify package metadata and inspect the highest-value linked public
    documentation routes before drafting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:12:50Z
  TYPE: FACT
  CLAIM: Release metadata is explicit: version 0.2.0, Python 3.14 or newer,
    zero runtime dependencies, AGPL-3.0-or-later, typed packaging, and an Alpha
    development classifier with free-threading support classified Beta.
  EVIDENCE:
  - `pyproject.toml:1-64`
  - `src/melder/__version__.py:1-12`
  IMPACT: The release must present 0.2.0 as an ambitious first public alpha,
    state Python 3.14+ and zero dependencies prominently, and avoid implying a
    stable 1.0 compatibility contract.
  NEXT: Read the architecture landing pages and inspect the runnable-example
    entry routes that the release should link.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:13:51Z
  TYPE: RISK
  CLAIM: The public architecture route is strong and intentionally layered,
    with a human core, source descent, seventeen handmade drawings, and
    runnable beginner-to-expert examples. However, both architecture landing
    pages still declare verification against 0.1.2 while the package is 0.2.0,
    and the sixty-second example still teaches class-token melding even though
    the address-law example proves the new human-name and explicit-ID forms.
  EVIDENCE:
  - `architecture_and_design/README.md:1-59`
  - `architecture_and_design/05_engineering_drawings/README.md:1-303`
  - `UX_and_AIX_experiences/01_beginner/01_hello_meld.py:1-26`
  - `UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:1-45`
  IMPACT: The release can link these public resources, but must not claim that
    every linked page is already stamped as 0.2.0-verified. Its quick start
    should use the cleaner human-name form proven by the current address law.
  NEXT: Read the public category, application-composition, and tradeoff pages,
    then lock the release outline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:15:36Z
  TYPE: DECISION
  CLAIM: Frame Melder 0.2.0 as the first real release. Lead with the complete
    bind-conjure-meld runtime and human-name resolution; group scopes, links,
    frames, self-documentation, Rift access, continuity, governed evolution,
    and free-threaded coordination as a capability ladder; retain an explicit
    Alpha and pre-1.0 compatibility notice.
  EVIDENCE:
  - Owner direction in the active conversation, 2026-08-30
  - `architecture_and_design/01_overview/what_melder_is.md:1-50`
  - `architecture_and_design/01_overview/capability_ladder.md:1-39`
  - `architecture_and_design/03_usage/compose_an_application.md:1-51`
  - `architecture_and_design/04_tradeoffs/design_tradeoffs.md:1-46`
  IMPACT: The announcement can sound like a real product launch without
    obscuring the deliberate costs or promising 1.0-level API stability.
  NEXT: Create `RELEASE_NOTES_0.2.0.md` with the approved narrative and
    reread it as a GitHub release body.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:17:00Z
  TYPE: FACT
  CLAIM: The 207-line release draft is implemented and reread. It frames 0.2.0
    as the first real release, includes a runnable human-name quick start,
    separates the complete dependency-runtime floor from the optional
    operational ceiling, states deliberate tradeoffs and Alpha posture, records
    validation evidence, and ends with public documentation and feedback routes.
  EVIDENCE: `RELEASE_NOTES_0.2.0.md:1-207`
  IMPACT: The owner now has a complete GitHub-release body rather than an
    outline; remaining work is claim, link, Markdown, and repository-impact validation.
  NEXT: Validate code snippets, local/remote links, line length, diff hygiene,
    and the release file's effect on repository assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:18:24Z
  TYPE: BLOCKER
  CLAIM: First validation pass has no whitespace error and balanced Markdown
    fences, but the quick start did not execute because the isolated command
    omitted the repository `src` import path. Four lines exceed the prose hard
    cap, and include-untracked repository-asset checking correctly reports only
    the new root document as moving the `other` corpus fingerprint.
  EVIDENCE:
  - `RELEASE_NOTES_0.2.0.md:1-207`
  - `llm_support/_builder.py --check --include-untracked`
  - `git -c core.whitespace=cr-at-eol diff --check`
  IMPACT: The draft is not yet validated as executable, and committing it will
    require an LLM other-corpus regeneration. No runtime or generated-asset
    defect is evidenced by this pass.
  NEXT: Rerun the snippet with `PYTHONPATH=src`, inspect and wrap the four long
    lines, then repeat all release checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T23:20:31Z
  TYPE: MEASURE
  CLAIM: Final release-draft validation passes. The quick start executes
    against `src`; Markdown has 208 physical lines, 14 headings, eight balanced
    fence markers, one resolved drawings reference, and no line over 120
    characters; all local link targets exist; tracked-input repository assets
    remain current; and diff hygiene exits zero.
  EVIDENCE:
  - `RELEASE_NOTES_0.2.0.md:1-208`
  - `llm_support/_builder.py --check`
  - `git -c core.whitespace=cr-at-eol diff --check`
  IMPACT: The release body is runnable, structurally clean, source-grounded,
    and ready for owner review. Prospective checking correctly reports that the
    LLM `other` corpus will become stale once this new file is tracked.
  NEXT: Move the task and attention route to review, open the release draft,
    and tell the owner to regenerate repository assets before committing it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The validated 208-line draft frames 0.2.0 as Melder's first real release,
keeps Alpha/pre-1.0 posture explicit, provides a runnable human-name quick
start, and separates the complete dependency-runtime floor from the optional
agent/operations ceiling. No commit, tag, push, GitHub release, or PyPI action
occurred. If the draft is committed, stage it first and regenerate the
`llm_support` other corpus in the same commit.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
