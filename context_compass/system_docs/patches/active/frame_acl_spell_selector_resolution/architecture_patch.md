# Architecture Patch: Frame ACL Spell Selector Resolution

## Objective
Add descriptor-backed spell selector validation and compile resolved spell
targets to `spell_index_id` while preserving the current viewer path that still
uses spell record keys.

## Non-Goals
- no new top-level ACL family
- no viewer redesign
- no command runtime enforcement changes

## Changed Components
- `FrameACLValidator`
- `FrameACLCompiler`
- `CompiledFrameACLAccessSurface`

## Invariants
- authored spell selector rules validate against descriptor truth
- compiled surfaces preserve current record-key visibility for viewer consumers
- compiled surfaces also expose resolved `spell_index_id` targets for later
  command/codegen/runtime consumers

## Interface Deltas
- spell precision rule conditions gain selector-aware meaning
- compiled ACL surfaces gain spell-index outputs
- validator descriptor pass validates selector existence/ambiguity

## Migration Order
1. add selector validation helpers
2. add compiled spell-index outputs
3. update tests
4. keep record-key outputs until downstream viewer migration is complete

## Rollback
Rollback is code-level only for this patch. Do not remove record-key outputs
until spell-index consumer migration is complete.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md`
