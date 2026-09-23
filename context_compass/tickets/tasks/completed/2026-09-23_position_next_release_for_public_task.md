# Task: Position the next release notes for public users

## Metadata
- Task ID: TASK-2026-09-23-position-next-release-for-public
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-23T22:24:15Z
- Updated: 2026-09-23T22:30:29Z
- Completed: 2026-09-23T22:30:29Z
- Summary: Public release copy now leads with named lesser conduits and ConduitCloud discovery;
  internal handoff/test history removed while delivered feature contracts are preserved.

## Objective
Make named lesser conduits and ConduitCloud discovery prominent in the next release draft and
rewrite its internal handoff language for public library users.

## Ticket Contract
- ENTRY_GATE: Owner requests the document update and public positioning.
- EXECUTION_BOUNDARY: release_docs/next_version_release.md and this documentation closeout only.
- DEPENDENCIES: Accepted named-conduit, Bind-hook, pooled-hook, graduation and purge contracts.
- EXIT_GATE: Public features, usage and compatibility are clear; internal work history is removed.
- FAILURE_ESCALATION: Verify any changed behavioral wording against source before publication.

## Scope Boundaries
- Include name-based Cloud discovery, cleanup/reuse, promotion, Nexus and structural recording.
- Preserve the other delivered public features while removing owner instructions and test-run logs.
- No runtime changes, version bump, compiler-epic claim or publication.
- Following the owner's standing instruction, run asset builders directly after all edits and
  documentation tracking are finished. Do not create a separate asset-rebuild task or edit afterward.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Requested public copy is written, read back and syntax/whitespace checked.

## Steps / Checklist
- [x] Read current draft and public guides/examples.
- [x] Verify naming and discovery contracts and rewrite the draft.
- [x] Review public copy and finish documentation tracking before the final asset rebuild.

## Validation
Read back the revised Markdown, verify examples/signatures and check scoped whitespace. Runtime
behavior is unchanged; do not rerun broad runtime suites for copy editing.

## Applicable Anti-Patterns
- [x] No personal handoff, owner-specific directions or implementation diary in public release copy.
- [x] No asset task and no file edits after the final generation/check commands.

## Artifact Links
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Record the wording decision and final document result; keep build status in command output.

## Notes
- DATETIME: 2026-09-23T22:30:29Z
  TYPE: MEASURE
  CLAIM: Rewrote the release draft for public library users. The leading feature explains named
    lesser scopes and Cloud name/ID discovery, cleanup/reuse, promotion, Nexus and structural restore.
    Bind hooks, pool isolation, independent graduation and purge remain documented. Removed owner
    directions, internal qualification counts, private guard work and generator history.
  EVIDENCE:
  - release_docs/next_version_release.md:1-257
  - src/melder/aether/aetheric_frame/conduit_cloud.py:481-683
  - src/melder/aether/conduit/conduit.py:2223-2359
  IMPACT: All seven Python examples parse, Markdown fences balance, readback is complete and scoped
    whitespace checks pass. Corrected promotion wording to say in-place with None return. Runtime
    tests were not rerun for prose-only changes. No runtime code, source version or compiler epic changed.
  NEXT: Run package and LLM builders directly, then their checks, with no subsequent repository edits.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T22:24:57Z
  TYPE: DECISION
  CLAIM: Source confirms creation-only optional names in either mode, named normal/lesser lookup
    through the same Cloud, and discovery that does not extend scope lifetime. Lead with that public
    capability and its example. Keep lifecycle/compatibility guidance; remove internal test counts,
    owner decisions, guard-audit notes and asset-generation history throughout the release draft.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2539-2720
  - src/melder/aether/aetheric_frame/conduit_cloud.py:481-500
  - src/melder/aether/aetheric_frame/conduit_cloud.py:658-683
  - docs/intermediate/hooks.md:24-70
  IMPACT: Retain all delivered features and public behavior while making the document suitable for
    publication. Add a dedicated Bind lifecycle section, and keep tutorial changes together.
  NEXT: Rewrite and read back the release draft, then finish documentation records before asset generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T22:24:15Z
  TYPE: FACT
  CLAIM: The draft already contains naming but mixes public contracts with code-review history,
    test-selection counts and internal publication terms. Cloud discovery needs explicit positioning.
  EVIDENCE:
  - release_docs/next_version_release.md:1-115
  - docs/intermediate/scopes.md:24-62
  - docs/expert/restore.md:22-41
  IMPACT: Rewrite as a public release announcement with feature benefits, examples and compatibility.
  NEXT: Verify the named scope/discovery source contracts and write the public draft.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Public release revision is complete and checked. All documentation tracking is closed before the
direct asset rebuild. Build outcomes belong in command output; no asset task or follow-up file edit.
Compiler epic remains unclaimed.