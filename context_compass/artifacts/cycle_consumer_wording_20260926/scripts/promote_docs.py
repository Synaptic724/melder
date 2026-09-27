"""Promote the cycle-consumer wording into src_components, src_architecture and the release note (2026-09-26).

Usage: python promote_docs.py <repo_root>. Full-line anchors via patch_util; each edit is skipped when its new
text is already present, so a re-run is safe. Indexes are regenerated separately.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

ROOT = pathlib.Path(sys.argv[1])
COMP = ROOT / "context_compass/system_docs/src_components.md"
ARCH = ROOT / "context_compass/system_docs/src_architecture.md"
REL = ROOT / "release_docs/next_version_release.md"


def edit(path: pathlib.Path, old: str, new: str) -> None:
    """Replace `old` with `new` once, unless `new` is already present (each `new` contains its `old`)."""
    if new in path.read_bytes().decode("utf-8").replace("\r\n", "\n"):
        print(f"skip {path.name} (already applied)")
        return
    replace_block(path, old, new)


edit(COMP, """  with what to change. Codes, severities and `details` payloads are unchanged.
- Misfires fixed with it: ParameterPolicyStrategy treated `typing.Any` as injectable, so `*args: Any` /""",
"""  with what to change. Codes, severities and `details` payloads are unchanged.
- Cycle consumers (2026-09-26): every spell from which a cycle is reachable is refused, but only members read
  "is part of a dependency cycle". A spell outside the cycle reads "cannot be built: it needs 'Y', which is part
  of a dependency cycle: ..." (Y a member), "which depends on a dependency cycle: ..." (Y an intermediate) or
  "which depends on itself ('Y' -> 'Y')" (Y a self-loop), then the fix ("Break that cycle (...)", or
  "Fix '<loop spell>' (...)" for a self-loop) and "'X' itself is not part of that cycle." Y is the spell's direct
  dependency on the route; the DFS keeps the path before the cycle and `_cycle_message` words it. Code and
  `details["cycle"]` are unchanged.
  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py:CircularDependencyStrategy._cycle_message`.
- Misfires fixed with it: ParameterPolicyStrategy treated `typing.Any` as injectable, so `*args: Any` /""")
edit(COMP, """## Context / Handoff Summary

2026-09-26 self-referencing constructors: a constructor taking its own class now reaches Phase 4 (Phase 3 records""",
"""## Context / Handoff Summary

2026-09-26 cycle consumers: a spell that only needs a dependency cycle was told it "is part of" the cycle; it now
reads "cannot be built: it needs 'Y', which is part of (or depends on) a dependency cycle ... 'X' itself is not
part of that cycle", naming its direct dependency on the route. Members' messages, codes and details are
unchanged. Promoted into the SpellCompiler and Validation Pipeline entry ("Conjure validation report"); this
closes the open item recorded with the self-referencing constructors below.

2026-09-26 self-referencing constructors: a constructor taking its own class now reaches Phase 4 (Phase 3 records""")
edit(ARCH, """  conjure aborted with PhaseExecutionError "DagNode cannot depend on itself".""",
"""  conjure aborted with PhaseExecutionError "DagNode cannot depend on itself". A spell that only needs a cycle is
  named as its consumer ("cannot be built: it needs 'Y' ... 'X' itself is not part of that cycle"), not as a
  member.""")
edit(ARCH, """## Context / Handoff Summary

2026-09-26 self-referencing constructors: a constructor taking its own class is refused by the readable conjure""",
"""## Context / Handoff Summary

2026-09-26 cycle consumers: the conjure report tells a spell that only needs a dependency cycle which of its
dependencies leads there and that it is not part of the cycle, instead of calling it a member. The component map
carries the wording.

2026-09-26 self-referencing constructors: a constructor taking its own class is refused by the readable conjure""")
edit(REL, """  that parameter or give it a default. [SELF_DEPENDENCY]`. A default (`parent: Optional[Node] = None`)
  makes the parameter plain, and the spell conjures.""",
"""  that parameter or give it a default. [SELF_DEPENDENCY]`. A default (`parent: Optional[Node] = None`)
  makes the parameter plain, and the spell conjures.
- **A spell that only uses a cycle is told so.** Every spell that needs a cycle, directly or through other
  spells, is refused with it, but it read as a member of the cycle. `Consumer(a: CycleA)` now reads
  `Spell 'Consumer' cannot be built: it needs 'CycleA', which is part of a dependency cycle: 'CycleA' ->
  'CycleB' -> 'CycleA'. Break that cycle (remove one of those constructor dependencies or give that parameter
  a default); 'Consumer' itself is not part of that cycle.` A spell reaching the cycle through another spell
  names that spell ("which depends on a dependency cycle"), and one that needs `Node(parent: Node)` reads
  `it needs 'Node', which depends on itself ('Node' -> 'Node'). Fix 'Node' (...)`. Members read as before.""")
print("done")
