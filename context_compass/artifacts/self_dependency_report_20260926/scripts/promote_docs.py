"""Promote the self-dependency fix into src_components and src_architecture (anchored edits; repository root)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block as _replace_block


def replace_block(path: pathlib.Path, old: str, new: str) -> None:
    """Apply one anchored edit unless its replacement text is already present (re-runnable after a partial run)."""
    if new in path.read_bytes().decode("utf-8").replace("\r\n", "\n"):
        print(f"already applied in {path.name}")
        return
    _replace_block(path, old, new)

DOCS = pathlib.Path("context_compass/system_docs")
COMP = DOCS / "src_components.md"
ARCH = DOCS / "src_architecture.md"

replace_block(COMP, """- Rules: exact (code, message) repeats drop; BINDING_RESOLUTION_CYCLE hides when CIRCULAR_DEPENDENCY is shown
  for the same spell; root_not_viable and broken_spell_in_dag hide when any other error is shown. Codes in""",
"""- Rules: exact (code, message) repeats drop; BINDING_RESOLUTION_CYCLE hides when CIRCULAR_DEPENDENCY is reported
  for the same spell, and CIRCULAR_DEPENDENCY when SELF_DEPENDENCY is (the spell's result keeps both codes);
  root_not_viable and broken_spell_in_dag hide when any other error is shown. Codes in""")
replace_block(COMP, """  `src/melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.py:ParameterPolicyStrategy._looks_like_di_target`.""",
"""  `src/melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.py:ParameterPolicyStrategy._looks_like_di_target`.
- Self-referencing constructors (2026-09-26): Phase 3 records a parameter that resolves to its own spell as a
  dependency outside the frame order, so Phase 4's SELF_DEPENDENCY refuses the spell through this report instead
  of a PhaseExecutionError at conjure or a bare ValueError at a late dynamic bind. The message names the
  parameter(s) from the Phase-3 topology (`details["parameter_names"]`) and stays generic without one.
  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/validation/strategies/self_validation_strategy.py:SelfDependencyStrategy`
  and `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:CompilerPhase3._build_local_frame_dag`.""")
replace_block(COMP, """- A constructor parameter that resolves to its own class still fails in Phase 3 with PhaseExecutionError
  "DagNode cannot depend on itself" before SELF_DEPENDENCY can report it (open, 2026-09-26).""",
"""- Until 2026-09-26 a constructor parameter that resolved to its own class aborted Phase 3 with PhaseExecutionError
  "DagNode cannot depend on itself" (a bare ValueError at a late dynamic bind); SELF_DEPENDENCY now refuses it
  through the report. A spell that only consumes a cycle is still listed as "part of" it (all cycles; open).""")
replace_block(COMP, """## Context / Handoff Summary

2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type""", """## Context / Handoff Summary

2026-09-26 self-referencing constructors: a constructor taking its own class now reaches Phase 4 (Phase 3 records
the self id instead of raising) and is refused as SELF_DEPENDENCY naming the parameter; the report hides the
CIRCULAR_DEPENDENCY the same spell also carries. Promoted into the SpellCompiler and Validation Pipeline entry
("Conjure validation report" and Failure Modes). Open: a cycle's consumers read as "part of" the cycle.

2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type""")
replace_block(ARCH, """  conduit-verdict refusal printed "(none recorded)" and every message carried 64-character spell ids.""",
"""  conduit-verdict refusal printed "(none recorded)" and every message carried 64-character spell ids. A
  constructor that takes its own class is refused the same way (SELF_DEPENDENCY, naming the parameter); before,
  conjure aborted with PhaseExecutionError "DagNode cannot depend on itself".""")
replace_block(ARCH, """## Context / Handoff Summary

2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type""", """## Context / Handoff Summary

2026-09-26 self-referencing constructors: a constructor taking its own class is refused by the readable conjure
report (SELF_DEPENDENCY, naming the parameter) instead of aborting in the compiler. The component map carries the
detail.

2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type""")
print("docs promoted")
