# Patch (lane 2): `many` may not depend on `unique_per_spell_space`

## Metadata
- Patch ID: PATCH-2026-06-23-many-not-depend-spellspace
- Program: "scope authoritative" (lane 2 — build-time scope-ordering rule)
- Status: APPLIED (strategy logic); ENFORCEMENT still pending (see caveat)
- Owner: cowork / optimizer_0
- Risk: low (one validation strategy; detection-only, additive diagnostic)
- Sandbox validation: py_compile OK (3.10); runtime run requires 3.14t.

## Rule
A `many` HOLDER has no bounded lifetime — the caller may retain it past the
request scope. So a `many` capturing a `unique_per_spell_space` instance is a
captive dependency (the spellspace instance is cleared at scope close while the
retained `many` dangles). Therefore:
- REJECT: `many -> unique_per_spell_space`.
- ALLOW: `unique_per_spell_space -> many` (a many dependency dies with its
  scoped holder; nothing longer-lived references it).
- Unchanged: `many -> upc/lineage/cluster/unique` stays allowed (caller's
  responsibility — only the acute, explicit-`with`-boundary spellspace case is
  hard-enforced). The existing broad->narrower rejections (unique/cluster/
  lineage/upc -> spellspace) are unchanged.

## Change
src/.../system/validation/scope_ordering_strategy.py: the loop previously
blanket-skipped every `many` node (so `many -> spellspace` was never flagged). It
now, for a `many` node, emits a `scope_ordering_violation` ERROR when (and only
when) a dependency is `unique_per_spell_space`; all other `many` deps remain
exempt. Non-`many` nodes are unchanged.

## Caveat — DETECTION vs ENFORCEMENT
This strategy emits the ERROR diagnostic. Conjure-time system validation is still
ADVISORY (SpellSystemValidationSystem.validate computes is_valid but never
raises; the conduit path only records per-conduit validity). So like every other
`scope_ordering_violation` today, `many -> spellspace` is now DETECTED but not yet
a hard conjure failure. The matrix test
`test_many_holder_on_spellspace_dependency_is_legal` will NOT flip to "rejected"
until conjure honors is_valid (the separate conjure-enforcement work). When that
lands, that test inverts to expect SpellbookValidationError.

## Validation
- py_compile: OK.
- Full enforcement not observable until conjure raises on scope_ordering_violation.
- Run (3.14t) to confirm no regression in the scope suites:
  - python -m pytest tests/integration/melder/conduit -q
