# Component Patch: SpellRecord

## Component Purpose and Boundary In Current Architecture
Canonical Nexus record for one published spell.

## Before / After Behavior Summary
Before:
- published stable SpellIndex identity field was named `lineage_id`

After:
- published stable SpellIndex identity field is named `spell_index_id`

## Interface Deltas
- constructor argument `lineage_id` -> `spell_index_id`
- public field `lineage_id` -> `spell_index_id`

## State and Lifecycle Deltas
- no lifecycle or ownership change
- same value, same cleanup, different public name

## Failure Mode Deltas
- none; this is a contract rename, not a behavior change

## Dependency and Ordering Constraints
- descriptor-manager publish path must use the renamed constructor arg
- viewer surfaces must be swept in the same tranche to avoid mixed output

## Validation Expectations
- focused descriptor and viewer tests updated together

## Unknowns and Open Decisions
- none for this slice
