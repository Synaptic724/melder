"""Promote the class binding-profile annotation fix into src_components and src_architecture (anchored edits).

Run from the repository root. Regenerate both indexes afterwards.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

DOCS = pathlib.Path("context_compass/system_docs")
COMP = DOCS / "src_components.md"
ARCH = DOCS / "src_architecture.md"
BPS = "src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py"

replace_block(COMP, f"""  falls back to `SignatureReflection.class_annotations` (FORWARDREF) on NameError.
  EVIDENCE:
  - src/melder/utilities/helpers/signature_reflection.py:52-190
  - {BPS}:106-114
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/class_inspector.py:150-175""",
f"""  falls back to `SignatureReflection.class_annotations` (FORWARDREF) on NameError.
  EVIDENCE:
  - src/melder/utilities/helpers/signature_reflection.py:52-190
  - {BPS}:105-113
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/class_inspector.py:150-175
- The class binding profile reads class-level annotations the same way (2026-09-26,
  `BindingProfileStrategy._read_class_annotations`): a name unbound at runtime keeps its key, its value the
  source text (`'Decimal'`, `'list[Decimal]'`). `Bind.sha256_profile` hashes the sorted keys, so every
  annotated field counts in the spell id, and Nexus publishes the fields. Before, one such name dropped every
  annotation to `{{}}`; affected classes got a new id once. Any other read failure, or a failing fallback,
  still gives `{{}}`, so binding never fails over annotations.
  EVIDENCE:
  - {BPS}:147-191
  - src/melder/aether/spellbook/bind/bind.py:946-956""")

replace_block(COMP, f"""- Known limits, recorded and not fixed (2026-09-26): a function spell's fingerprint hashes its `repr()`,
  which carries a memory address, so function spell ids change per process; the binding profile's class
  `annotations` fall back to `{{}}` when any name in them is unresolved.
  EVIDENCE: {BPS}:84-92""",
f"""- Both limits recorded here earlier on 2026-09-26 are fixed: function spell fingerprints hash an
  address-free repr (process-stable ids), and class binding-profile annotations keep names unbound at
  runtime. A class whose annotations cannot be read at all (not a NameError) still binds with `{{}}`.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1006-1026
  - {BPS}:147-191""")

replace_block(COMP, """## Context / Handoff Summary

2026-09-26 conjure validation report: SpellbookValidationError lists each broken spell's errors by name with""",
"""## Context / Handoff Summary

2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type
kept none of them in its binding profile, so its spell id ignored those fields and Nexus showed none. The
profile now reads them as `ClassInspector` does (unavailable names as source text); affected classes get a new
id once. Promoted into the Spell Examination Profiles entry, whose stale "known limits" line (function ids,
fixed earlier) is corrected.

2026-09-26 conjure validation report: SpellbookValidationError lists each broken spell's errors by name with""")

replace_block(ARCH, """  source text, never a ForwardRef owner or a memory address. Bind fingerprints hash that text, so a class
  annotated with a `TYPE_CHECKING`-only type keeps one spell id across processes. Every annotation in
  `src/melder` evaluates once its `TYPE_CHECKING` imports are bound, enforced by a unit guard.
  EVIDENCE: `src/melder/utilities/helpers/signature_reflection.py:SignatureReflection` and
  `tests/unit/melder/test_annotation_integrity.py`.""",
f"""  source text, never a ForwardRef owner or a memory address. Bind fingerprints hash that text, so a class
  annotated with a `TYPE_CHECKING`-only type keeps one spell id across processes. The class binding
  profile reads class-level annotations the same way, so a field typed with such a name counts in the
  fingerprint (affected classes changed id once when this landed). Every annotation in `src/melder`
  evaluates once its `TYPE_CHECKING` imports are bound, enforced by a unit guard.
  EVIDENCE: `src/melder/utilities/helpers/signature_reflection.py:SignatureReflection`,
  `{BPS}:BindingProfileStrategy._read_class_annotations`
  and `tests/unit/melder/test_annotation_integrity.py`.""")

replace_block(ARCH, """## Context / Handoff Summary

2026-09-26 conjure validation report: a refused conjure now tells the user which spells failed, why and how to""",
"""## Context / Handoff Summary

2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type
lost all of them from its binding profile, so its spell id ignored those fields. They are now kept as source
text; affected classes get a new id once. The component map carries the detail.

2026-09-26 conjure validation report: a refused conjure now tells the user which spells failed, why and how to""")
print("docs promoted")
