# Component patch: Binding Pipeline (Bind and Spell)

## Purpose and boundary
Bind examines and fingerprints a target before constructing Spell. Spell owns the resulting
binding metadata; this patch does not change resolution or instance lifecycle.

## Before / after
- Before: class-profile matches become a frozenset, which is hashed and frozen again by Spell.
- After: Bind builds one ordered list from both groups, hashes it, and passes it directly to Spell.
- The constructor's omitted metadata produces a fresh empty list per Spell, never a shared default.

## Interface deltas
Internal Bind methods accept configured names, per-spell names, and a False-default priority bool.
Spell accepts an optional resolved list and computes has_disposal_methods once from the result.
The inspector continues hashing resolved names; document that callers provide the resolved sequence.

## State and lifecycle
Spell retains the list by reference. Cleanup deletes that reference without clearing the list,
so creation entries may still retain it. No setter, invalidation, or re-identification API is added.

## Failure modes
Preserve class-profile-only matching, missing-name omission, and existing binding refusal rules.
No set/tuple compatibility wrapper or broader factory/instance matching is added.

## Dependencies and ordering
False walks spell names then book names. True walks book names then spell names. Within either
group, supplied order wins. Keep only names in the existing profile and not already in the result.
Hash that exact result before Spell construction; do not remove disposal from the SHA input.

## Validation
Test order versus class definition/alphabetical order, overlaps, absent methods, empty groups,
constructor reference ownership, default-list independence, inspector parity, and hash-seed stability.

## Open decisions
None. Post-creation mutation and consumer metadata-copy removal remain outside this slice.
