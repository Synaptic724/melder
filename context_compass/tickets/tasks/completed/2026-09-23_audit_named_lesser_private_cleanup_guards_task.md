# Task: Keep named-feature cleanup guards at public entry points

## Metadata
- Task ID: TASK-2026-09-23-audit-named-lesser-private-cleanup-guards
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery (completed follow-up)
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-23T12:15:54Z
- Updated: 2026-09-23T12:47:44Z
- Completed: 2026-09-23T12:47:44Z
- Summary: Removed all generic cleanup guards from 33 scoped private methods; public admission
  remains protected. Two public regressions added; 206 affected tests passed. Owner accepted turn-in.

## Objective
Audit private methods touched by the named-lesser work and remove check_cleaned calls, retaining
cleanup admission at public entry points and preserving required lifecycle ordering.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested the audit/correction and confirmed go ahead.
- EXECUTION_BOUNDARY: Touched methods in named-feature source owners; their public callers,
  accurate docstrings and focused public-lifecycle validation. No unrelated private-method sweep.
- DEPENDENCIES: Completed named-lesser implementation/finish tasks and current source.
- EXIT_GATE: No check_cleaned calls in scoped changed private methods; public cleanup refusal and
  named lifecycle behavior remain tested; changes are documented without generated build assets.
- FAILURE_ESCALATION: Read actual caller/lock contracts before moving a required admission check.

## Scope
- Include direct calls on self and passed owned runtime objects. Python public protocol dunders
  are not private helpers. Record the exact audited method set and source lines.
- Keep existing name/state/ownership validation and necessary lock ordering. Do not replace a
  removed generic guard with a redundant defensive wrapper.
- Public methods retain cleaned-state checks. Package version stays 0.2.50; build hold persists.

## Steps
- [x] Identify the touched private methods and their cleanup-guard calls.
- [x] Read affected implementations/public callers and record the correction boundary.
- [x] Remove private guards and align affected docstrings/public admission.
- [x] Verify the audit mechanically and run relevant public-lifecycle tests.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted completed work and requested turn-in before the asset rebuild.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/named_lesser_private_guards_20260923/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-23T12:47:44Z
  TYPE: DECISION
  CLAIM: Owner accepted the completed correction and requested turn-in/cleanup. Retain the audit
    and 206-test receipt as reference; move this task to completed and synchronize both boards.
  EVIDENCE:
  - Owner's current turn-in instruction.
  - artifacts/named_lesser_private_guards_20260923/validation.md:1-23
  IMPACT: Source follow-up is complete. Packaged generation is authorized in its existing separate task.
  NEXT: Continue with the deferred packaged-asset refresh task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T12:20:00Z
  TYPE: FACT
  CLAIM: The scoped before/current audit identifies 33 changed private methods; eight contain
    twelve check_cleaned calls. Four are Cloud name helpers, two are Conduit helpers, one is the
    private Book conjure route and one is Nexus conduit publication. Source/callers are read.
  EVIDENCE:
  - artifacts/named_lesser_private_guards_20260923/before.json
  - src/melder/aether/aetheric_frame/conduit_cloud.py:242-335
  - src/melder/aether/conduit/conduit.py:2223-2401
  - src/melder/aether/conduit/conduit.py:2721-2792
  - src/melder/aether/spellbook/spellbook.py:6635-6863
  - src/melder/nexus/frame_descriptor_manager.py:342-427
  IMPACT: Remove generic private guards. Promotion's two lock-window checks move to its public
    entry point. Named attachment retains its required cleaned/pooled state rejection in one
    existing admission condition under the child lock, rather than calling a generic guard.
    Book setup is private over a fresh Book and the public caller's quiesced runtime. No change
    to ownership, locks, publication schema or pool/meld hot paths; no architecture redesign.
  NEXT: Apply the eight-method cleanup and verify public cleanup/refusal plus lifecycle regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T12:15:54Z
  TYPE: DECISION
  CLAIM: Owner's current style correction is explicit: check_cleaned belongs on public-facing
    methods, not private methods updated by this feature. Audit all three implementation stages
    and the final public-conjure repair, then make the bounded corrections.
  EVIDENCE:
  - Owner's audit request and go-ahead in this conversation.
  - tickets/tasks/completed/2026-09-23_finish_named_lesser_epic_task.md
  IMPACT: New follow-up does not reopen unrelated epics or authorize packaged generation.
  NEXT: Map scoped changed functions to their guard calls, then read their complete bodies/callers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Private guard cleanup is implemented. Audit: 33 changed private methods, zero check_cleaned calls
remaining (12 calls removed from eight methods). Two required promotion checks now sit in the public
upgrade method's lock windows. Named attachment keeps its existing lifecycle-state admission, including
callback-driven hard cleanup. Public guards are preserved. Affected selection: 206 passed.
Scoped source-document metadata synchronization is complete. Receipt:
artifacts/named_lesser_private_guards_20260923/validation.md. No packaged assets or version changes;
no test process remains running. Owner accepted this follow-up; retained evidence is linked above.
Packaged generation continues in the separately authorized asset-refresh task.
