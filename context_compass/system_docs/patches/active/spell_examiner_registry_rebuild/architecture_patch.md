# architecture_patch

## Metadata
- Patch ID: spell_examiner_registry_rebuild
- Status: draft
- Owner: codex
- Created: 2026-04-05T13:45:00Z
- Updated: 2026-04-05T13:45:00Z

## Patch Scope and Non-Goals
- Objective:
  Rebuild `SpellExaminer` to the requested `general` / `detailed` profile
  contract with one `create_profile(...)` entrypoint, no helper creators on the
  class surface, no explicit registry lock, and one long-lived examiner owned
  by `Bind`.
- Non-goals:
  - redesigning the deeper resolution-frame / mutation pipeline
  - widening the patch beyond the direct `.profile` consumer set needed for the
    `general` / `detailed` cut

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| spell_examiner | modify | replace the middle-state `binding` / `resolution` / `ai` registry with `general` / `detailed` | bind, examiner profiles/strategies |
| bind | modify | keep one long-lived SpellExaminer, keep binding pre-fingerprint path, then swap `.profile` to `general` after Spell construction | spell_examiner |
| spell_profile_consumers | modify | normalize `.profile` reads across creation, validation, and Nexus publish | spell_examiner, bind |
| spellbook_bind_scan | modify | expose and propagate public profile choice through bind, conduit, scan, and fluent binding | bind |

## Cross-Component Invariants
- `create_profile(...)` is the only public profile-creation entrypoint on
  `SpellExaminer`.
- `SpellExaminer` default registry contains only `general` and `detailed`.
- `general` is a two-step profile object:
  phase 1 builds binding data from the raw candidate, then phase 2 completes
  resolution data after `Spell` exists.
- `detailed` is the renamed AI-facing richer profile and keeps the current
  binding + resolution fields directly instead of becoming a wrapper around
  `general`.
- `detailed` follows the same two-step lifecycle and inherits from `general`.
- `Bind` still needs a binding-profile pre-step before Spell construction for
  fingerprinting and `SpellType` selection, but now it keeps one partial
  `general` profile object alive across both phases instead of rebuilding
  combined assets.
- Direct `.profile` consumers must normalize `general` / `detailed` instead of
  assuming raw binding-profile or AI-profile storage.

## Context / Handoff Summary
- What changed:
  The patch lane now reflects the requested `general` / `detailed` rebuild
  rather than the earlier safe middle-state registry rewrite.
- What remains:
  Implement the rebuild and rewire the direct `.profile` consumers together.
