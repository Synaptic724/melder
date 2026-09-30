# component_patch_spellbook_conjure

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-30T00:19:44Z

<!-- BEGIN ENTRY: "Spellbook.conjure: refuse before settling" -->
## Before
- `conjure(dynamic=True)` settles an unsettled frame dynamic (`_settle_or_inherit_conjure_mode`) and only then, in
  `_conjure_within_transaction_window`, refuses when an active Crystallizer meets binds made under a mutable
  configuration. The refused conjure leaves the frame frozen dynamic, so a later automatic conjure there inherits
  dynamic and is refused too.
  EVIDENCE: src/melder/aether/spellbook/spellbook.py:6502-6620, src/melder/aether/spellbook/spellbook.py:6877-6935.

## After
- `conjure` computes the mode settlement would produce (pure, no mutation), runs the discipline refusal against it,
  and settles only when it passes. Message, exception type and logging are unchanged. The transaction window
  re-runs the same check on the settled mode; it only fires if another Book settled the shared frame between the
  prediction and settlement. `_conjure_existing_conduit` is unchanged (its Book is new and empty).

## Validation Expectations
- After the refusal the frame posture is still unfrozen and automatic, and an automatic conjure succeeds; the
  effective-mode helper agrees with settlement for every posture/flag combination.
<!-- END ENTRY: "Spellbook.conjure: refuse before settling" -->
