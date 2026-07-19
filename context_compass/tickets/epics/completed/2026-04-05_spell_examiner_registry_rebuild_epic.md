# Epic: Spell Examiner Registry Rebuild
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the SpellExaminer registry rebuild epic and archived the bounded rebuild lane.


## Metadata
- Epic ID: EPIC-2026-04-05-spell-examiner-registry-rebuild
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T13:45:00Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Rebuild `SpellExaminer` into a registry-driven long-lived profile factory with
one primary entrypoint, then rewire `Bind` and the live consumers/tests to the
new contract without keeping backward-compat surface.

## Problem / Opportunity
The current `SpellExaminer` has strategy objects but the live runtime only
really consumes the bind-time path. The richer `resolution` and `ai` strategy
surfaces exist, but they are not wired into one coherent active profile
creation contract. The current API also spreads behavior across:
- multiple helper methods
- `SpellExaminationKind`
- ad hoc `SpellExaminer()` instantiation in bind paths

That makes later profile-mode work harder than it needs to be.

## Goals
- Replace the current hardcoded facade with a registry-driven profile factory.
- Remove `SpellExaminationKind`.
- Add one primary `create_profile(...)` entrypoint.
- Keep the current profile families (`binding`, `resolution`, `ai`) intact.
- Make `Bind` own one long-lived `SpellExaminer` instead of creating it ad hoc.
- Rewire live runtime/test consumers to the new contract.

## Non-Goals
- Changing the default active profile mode beyond the current safe baseline.
- Reworking descriptor acceptance of richer profile data in this same slice.
- Reworking `Spell.profile` / `Spell.resolution_profile` storage semantics yet.

## Scope
- `src/melder/spellbook/spell_crafter/spell_examiner/`
- `src/melder/spellbook/bind/bind.py`
- directly affected runtime/tests/docs only

## Risks
- Tests and smaller helper consumers may still depend on the removed enum or helper methods.
- Overeager profile-semantics changes could widen this beyond the safe rebuild slice.

## Linked Story
- STORY-2026-04-05-spell-examiner-registry-rebuild

## Context / Handoff Summary
This epic exists to replace the current half-live SpellExaminer facade with
one registry-driven profile factory before more profile/ACL work builds on top
of it.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

