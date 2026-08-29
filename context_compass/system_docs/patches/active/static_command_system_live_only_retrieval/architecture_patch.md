# Architecture Patch: Static Command System Live Only Retrieval

## Objective
Keep the existing command getter names but make `StaticCommandSystem` return a
spell runtime object only when it already has a live creation.

## Non-Goals
- no capability handle design
- no broad runtime-object redesign
- no creation-on-demand path in static mode

## Changed Components
- `StaticCommandSystem`
- supporting internal conduit/creation live retrieval helper

## Invariants
- static mode never creates through the generic spell getters
- static mode returns a spell runtime object only when it is already live
- the public command API shape stays unchanged

## Interface Deltas
- existing static spell getters change from blanket denial to live-only
  retrieval

## Migration Order
1. add internal live retrieval helper over current runtime storage
2. use it from `StaticCommandSystem`
3. update focused tests

## Rollback
Rollback is code-level only for this patch. Do not partially mix blanket deny
and live-only behavior across the static spell getters.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_implement_static_command_system_live_only_retrieval_task.md`
