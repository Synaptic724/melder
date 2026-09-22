# Task: Refresh deferred build assets when the owner releases the hold

## Metadata
- Task ID: TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved
- Status: blocked
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-22T14:41:23Z
- Updated: 2026-09-22T20:11:00Z

## Objective
Keep the owner's packaged build-asset hold explicit after graduation source/test epic closure.
Run the existing Melder build-asset workflow only when the owner authorizes generation.

## Ticket Contract
- ENTRY_GATE: Owner releases the build-asset hold; route this ticket before running generators.
- EXECUTION_BOUNDARY: Existing build runner, affected generated assets and their validation.
- DEPENDENCIES: Completed graduation source and additional isolation tests; bind-hook source lane.
- EXIT_GATE: Requested packaged assets regenerate and validate, with source behavior unchanged.
- FAILURE_ESCALATION: Record generator/source drift and resolve in scope; do not silently patch runtime.

## Scope Boundaries
- In: packaged API/hardcopy/guard metadata produced by the existing runner once authorized.
- Out: runtime redesign, additional hook APIs, version bump, wheel, publishing or unrelated cleanup.
- ContextCompass architecture/components and graph documentation were promoted at graduation turn-in.
  The Melder build runner and src packaged assets were not regenerated.
- Bind-hook canonical documentation and tutorials are now accepted too. Include their current
  source/documentation inputs when generation is released; this extends the existing follow-up.
- Pool-hook canonical contracts are now promoted and accepted. Reconcile all accepted source,
  tutorial and release-note inputs for packaged and LLM assets when the build hold is released.

## State Transition Event
- from_state: draft
- to_state: blocked
- transition_reason: The existing owner hold on packaged generation remains in force.

## Steps / Checklist
- [ ] Receive authorization for packaged build-asset generation.
- [ ] Read current runner and reconcile graduation and bind-hook pending asset inputs.
- [ ] Run the normal build workflow and relevant generated-asset checks.
- [ ] Record outputs and retain unchanged runtime source behavior.

## Required Reading
- tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md
- tickets/tasks/completed/2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md
- tickets/tasks/completed/2026-09-21_implement_bind_lifecycle_hooks_task.md
- tickets/tasks/completed/2026-09-22_add_bind_hook_intermediate_and_expert_examples_task.md
- tickets/tasks/completed/2026-09-22_add_local_hook_setters_and_tracking_task.md
- src/melder/_build_assets/_build_asset_runner.py
- artifacts/graduation_configuration_20260922/upgrade_review.md

## Validation / Risks
Not run: generation intentionally held. Source qualification and document-index validation are
already recorded in the completed graduation task; do not mistake them for packaged asset generation.

## Applicable Anti-Patterns
- [x] No generator runs while the explicit owner hold is active.
- [x] Pending packaging work remains visible after source epic closure.
- [x] No unmeasured coverage or full-suite claims.

## Artifact Links
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Record owner authorization, generator findings and concrete validation in this ticket before continuing.

## Notes
2026-09-22 version correction: canonical package metadata and next-release draft are now 0.2.47.
The owner clarified a 0.2.43 baseline plus four epics total; the earlier 0.2.49 target double-counted
two increments and is superseded. Use the current source version when the build hold is released.

2026-09-22 bind-hook epic turn-in also leaves packaged/LLM generation here. The accepted callback
contracts were promoted into canonical maps/descriptors and original patches archived. No runtime
or package assets were changed by closure; do not reopen completed source work to rebuild metadata.

The owner requested additional hook-isolation tests and graduation epic turn-in. The source and
documentation work is complete; the separate generation hold is preserved here without running it.

## Context / Handoff Summary
Wait for owner authorization of packaged generation. Then use the existing build runner; do not
reimplement graduation or restart the separate pooled-hook reset investigation.
