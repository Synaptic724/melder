# Command Surface Name Alignment Architecture Patch

## Objective
Align drifted command-surface method names to the real lower Melder API where
the command layer is directly wrapping those runtime seams.

## Non-Goals
- No deeper semantic redesign of filtered/query helpers.
- No command-level meld helper implementation in this patch.
- No unrelated command-surface expansion.

## Changed Components
- `CommandSystem`
- `StaticCommandSystem`
- `interfaces.py` (`ICommandSystem`)

## Boundary Contract
- direct command wrappers should use the same names as the lower Melder API
  where practical
- this patch aligns:
  - `link_conduits(...)` -> `link(...)`
  - `get_spell_object_by_source_id(...)` -> `get_spell_by_source_id(...)`
  - `get_spell_object_by_index_id(...)` -> `get_spell_by_index_id(...)`
  - `get_spell_object_by_id(...)` -> `get_spell_by_id(...)`
- room-mediated helpers that do not have direct lower-runtime equivalents are
  out of scope here

## Migration Order
1. rename the command/base/static methods
2. update `ICommandSystem`
3. update focused unit and `rift/` integration callsites
4. validate unit + integration rings
