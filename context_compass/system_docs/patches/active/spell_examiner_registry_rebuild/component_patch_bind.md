# component_patch_bind

## Component purpose and boundary in current architecture
`Bind` is the main live consumer of `SpellExaminer` in runtime code.

## Before/after behavior summary
- Before:
  `Bind` owns one long-lived `SpellExaminer`, but still fingerprints from
  `create_profile(..., "binding")`, and `spell_id_inspector(...)` still
  constructs a one-off examiner.
- After:
  `Bind` keeps one long-lived SpellExaminer, creates one partial `general`
  profile from the raw candidate, fingerprints/type-checks through its
  `binding_profile`, constructs the `Spell`, then completes that same general
  profile in place and assigns it to `.profile`. The one-off
  `spell_id_inspector(...)` examiner construction is removed.

## Validation expectations
- one examiner instance per Bind
- bind carries one partial `SpellGeneralProfile` across both phases and assigns
  it onto `.profile` after completion
- no ad hoc `SpellExaminer()` call remains in `spell_id_inspector(...)`
