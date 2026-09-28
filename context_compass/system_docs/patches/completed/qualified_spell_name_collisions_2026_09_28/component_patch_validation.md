# Qualified spell-name collisions: validation component patch

## Purpose and boundary
Spell Validation Strategies emits Phase-4 structural issues for the visible local/contracted pool.

## Before and after
Before: every repeated spell_name errors even with unique addresses. After: only repeated canonical
(frame_key, bind_key) addresses error. The established helper normalizes class/string frames, fallback
spell names, case and default bindings. Explicit frames supersede spell names in address identity.

## Interface deltas
Preserve DuplicateSpellNameStrategy and DUPLICATE_SPELL_NAME for compatibility. The description,
message and contract describe address collisions. Keep existing detail fields and add lookup_key.

## State and lifecycle deltas
The pass memo stores tuple-keyed collision lists; no persistent state, locks or lifetime change.
Absent book/spell and nameless metadata retain current no-op behavior; cancellation still propagates.

## Failure modes
Different names with one normalized address MUST error. Qualified twins MUST produce no issue.
Discoverable definitions own addresses exactly like resolvable registrations; no exemption is added.

## Dependencies and ordering
Use the shared normalization helper. Keep the existing pool copy to avoid concurrent mutation during
iteration. Tests land before runtime changes. The production writer is workflows_0.

## Validation expectations
Run the strategy unit module, affected component validation modules, affected integration modules
and the added conjure/meld regression matrix. Preserve real-address bind refusal controls.

## Unknowns and open decisions
None. Contract admission and runtime lookup semantics are unchanged.
