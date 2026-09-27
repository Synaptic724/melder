"""Promote the conjure-report lane into src_components and src_architecture (2026-09-26).

Usage: python promote_docs.py <context_compass root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block as _replace_block

cc = pathlib.Path(sys.argv[1])


def replace_block(path: pathlib.Path, old: str, new: str) -> None:
    """Idempotent wrapper: skip when the new block is already in the document."""
    if new in path.read_text(encoding="utf-8").replace("\r\n", "\n"):
        print(f"already applied in {path.name}")
        return
    _replace_block(path, old, new)
comp = cc / "system_docs/src_components.md"
arch = cc / "system_docs/src_architecture.md"

replace_block(comp, """### Component: SpellCompiler and Validation Pipeline
Purpose:
- Compile per-spell artifacts and validate correctness before resolution.
""", """### Component: SpellCompiler and Validation Pipeline
Purpose:
- Compile per-spell artifacts and validate correctness before resolution.

Conjure validation report (2026-09-26):
- `SpellbookValidationError(broken_spells, *, system_diagnostics=None)` renders once, at construction. First
  line "Spellbook validation failed. Broken spells: A, B." (names only; the two substrings of earlier releases
  are kept for matchers). Then one block per spell with errors, "Name (frame 'x'):", each error as
  "  - <message> [CODE]"; errors that belong to no supplied spell under "Whole-graph errors:". Warnings,
  strategy sources, details payloads and spell ids are never printed; a footer counts Phase-4 warnings and
  points at `conjure(validation_warnings=True)`.
- Rules: exact (code, message) repeats drop; BINDING_RESOLUTION_CYCLE hides when CIRCULAR_DEPENDENCY is shown
  for the same spell; root_not_viable and broken_spell_in_dag hide when any other error is shown. Codes in
  `INTERNAL_CODES` (index, blueprint, socket-reference, bind-metadata and Phase-1-consistency checks) render as
  "  - [internal] ..." with one footer asking to report them. With diagnostics handed in, spells without an
  error are not listed; without them (meld paths) such a spell is named with "No validation error was recorded".
- The conjure gate (`_enforce_conduit_resolution_valid`) and the local-rerun gate in
  `run_resolution_phases_for_target_spell` hand the conduit resolution diagnostics over. Both run after
  `cleanup_phase_artifacts_after_resolution` has cleaned the spells' Phase 4/6 results, so before this change
  a conduit-verdict failure (scope ordering, visibility, cycles) printed "(none recorded)"; the gate's
  fallback of naming every scoped spell is kept for `broken_spells` but no longer floods the text.
- Messages: `SpellInputUtils.describe_spell_id` names spells ("'Holder'", or "spell id <12 chars>" when the
  lookup cannot name it). CIRCULAR_DEPENDENCY names the closed path once (the start used to repeat),
  scope_ordering_violation, cycle_detected (members or dependents, capped at ten names), visibility gaps (four
  producers), collection_socket_no_providers and broken_spell_in_dag use names; each user-fixable error ends
  with what to change. Codes, severities and `details` payloads are unchanged.
- Misfires fixed with it: ParameterPolicyStrategy treated `typing.Any` as injectable, so `*args: Any` /
  `**kwargs: Any` broke the spell (VARIADIC_DI_UNSUPPORTED); it now matches Phase 1. LIST_ELEMENT_NOT_DI_TARGET
  fires only when a user class sits inside the element (`list[Optional[Plugin]]`), never for `list[str]` or
  `list[Any]`; the REQUIRED_HOLE list-only hint appears only when a set/frozenset/dict/tuple holds a user class.
- EVIDENCE: `src/melder/utilities/custom_exceptions/spellbook_validation_error.py:SpellbookValidationError`,
  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._enforce_conduit_resolution_valid`,
  `src/melder/utilities/helpers/general_helpers.py:SpellInputUtils.describe_spell_id`,
  `src/melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.py:ParameterPolicyStrategy._looks_like_di_target`.
""")
replace_block(comp, """  and treats `typing.Any` as not injectable; it no longer emits UNSUPPORTED_COLLECTION_SHAPE. A default-less
  container parameter is a REQUIRED_HOLE whose message adds that Melder injects collections only as `list[T]`.
  Such spells conjure; the value is supplied through meld overrides.""", """  and treats `typing.Any` as not injectable; it no longer emits UNSUPPORTED_COLLECTION_SHAPE. A default-less
  container parameter is a REQUIRED_HOLE whose message adds that Melder injects collections only as `list[T]`.
  Such spells conjure; the value is supplied through meld overrides.
- NARROWED 2026-09-26 (conjure validation report): the list-only hint and LIST_ELEMENT_NOT_DI_TARGET now
  appear only when a user class sits inside the annotation; plain data (`dict[str, Any]`, `list[str]`) gets
  neither.""")
replace_block(comp, """- Until 2026-09-26 a set/frozenset/dict/tuple parameter of user classes or `typing.Any` broke its spell at
  Phase 4 (UNSUPPORTED_COLLECTION_SHAPE error, conjure refused) although Phase 1 never injects it; it is now a
  REQUIRED_HOLE caller input.""", """- Until 2026-09-26 a set/frozenset/dict/tuple parameter of user classes or `typing.Any` broke its spell at
  Phase 4 (UNSUPPORTED_COLLECTION_SHAPE error, conjure refused) although Phase 1 never injects it; it is now a
  REQUIRED_HOLE caller input.
- Until 2026-09-26 `*args: Any` / `**kwargs: Any` broke a spell (VARIADIC_DI_UNSUPPORTED), and a conduit-verdict
  refusal at conjure (scope ordering, visibility, cycles) carried no reason in its message. Both are fixed; the
  report layout is under "Conjure validation report".
- A constructor parameter that resolves to its own class still fails in Phase 3 with PhaseExecutionError
  "DagNode cannot depend on itself" before SELF_DEPENDENCY can report it (open, 2026-09-26).""")
replace_block(comp, """- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`
- `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`


#### Architecture narrative (folded in from `src_architecture.md`, 2026-08-01)""", """- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`
- `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`
- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`


#### Architecture narrative (folded in from `src_architecture.md`, 2026-08-01)""")
replace_block(comp, """- Strategies judge what Phase 1 decided and never break a spell over a parameter Phase 1 made a caller input
  (2026-09-26: container parameters are REQUIRED_HOLE warnings, not shape errors).""", """- Strategies judge what Phase 1 decided and never break a spell over a parameter Phase 1 made a caller input
  (2026-09-26: container parameters are REQUIRED_HOLE warnings, not shape errors).
- User-fixable messages name spells (never bare ids) and end with what to change; internal consistency codes
  are listed in `SpellbookValidationError.INTERNAL_CODES` (2026-09-26).""")
replace_block(comp, """## Context / Handoff Summary

2026-09-26 shared context rebuild windows: the September 5 freeze/drain design is finished and wired, adapted""", """## Context / Handoff Summary

2026-09-26 conjure validation report: SpellbookValidationError lists each broken spell's errors by name with
a fix, adds the conduit verdict's reasons (they were lost to artifact cleanup before the gate), counts
warnings instead of printing them and marks Melder's own consistency codes as internal. Two misfires went with
it (`*args: Any`, and list/container notices on plain data). Promoted into the SpellCompiler and Validation
Pipeline entry ("Conjure validation report"). Open: a constructor taking its own class still fails in Phase 3
with a bare "DagNode cannot depend on itself".

2026-09-26 shared context rebuild windows: the September 5 freeze/drain design is finished and wired, adapted""")

replace_block(arch, """  Phase 1 decided and never breaks a spell over a caller input: such parameters are REQUIRED_HOLE warnings
  (the message names list-only collection injection) and the caller supplies them through meld overrides.""", """  Phase 1 decided and never breaks a spell over a caller input: such parameters are REQUIRED_HOLE warnings
  (for containers of user classes the message names list-only collection injection) and the caller supplies
  them through meld overrides.""")
replace_block(arch, """- Conjure raises SpellbookValidationError when broken spells exist.""", """- Conjure raises SpellbookValidationError when broken spells exist. Since 2026-09-26 the message names each
  broken spell and lists only its errors, each with what to change; the conduit verdict's reasons (scope
  ordering, visibility, cycles) are included, errors that belong to no spell appear as whole-graph errors,
  warnings are only counted, and Melder's own consistency codes are marked [internal] to report. Before, a
  conduit-verdict refusal printed "(none recorded)" and every message carried 64-character spell ids.
  EVIDENCE: `src/melder/utilities/custom_exceptions/spellbook_validation_error.py:SpellbookValidationError` and
  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._enforce_conduit_resolution_valid`.""")
replace_block(arch, """## Context / Handoff Summary

2026-09-26 shared context rebuild windows (the September 5 design, finished): concurrent first melds of a""", """## Context / Handoff Summary

2026-09-26 conjure validation report: a refused conjure now tells the user which spells failed, why and how to
fix it, by name; reasons from the conduit verdict are no longer dropped, warnings are counted rather than
listed, and Melder-internal consistency codes are flagged as bugs to report. `*args: Any` / `**kwargs: Any`
no longer break a spell. The component map carries the layout rules.

2026-09-26 shared context rebuild windows (the September 5 design, finished): concurrent first melds of a""")
print("promoted")
