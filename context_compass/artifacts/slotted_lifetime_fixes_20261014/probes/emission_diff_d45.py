"""
Emission diff for 0.2.8238 (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D4/D5): the site-plan lowering of
0.2.8237 (a copy beside this probe) against the tree's, over representative plan shapes.

Expected: every `_site_plan_executor` body is byte-identical; a miss differs only by one added
`c{i}.adopt_children(...)` line, and only when it registers disposal-bearing `many` children.
Run from a tree root: PYTHONPATH=src:. python <this file>
"""
import difflib
import importlib.util
import pathlib
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellLocalTopology
from tests.unit.melder.spellbook.spell_compiler.shared_assets.test_site_plan_lowering import _socket, _spell, _step


def _load_old() -> Any:
    """Load the 0.2.8237 lowering module from the copy beside this probe."""
    path = pathlib.Path(__file__).resolve().parent / "site_plan_lowering_0_2_8237.py"
    spec = importlib.util.spec_from_file_location("site_plan_lowering_0_2_8237", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.SitePlanLowering


def _emit(lowering: Any, steps: Tuple[Any, ...], topologies: Dict[str, Any], root_key: Tuple[str, Any],
          keys: Tuple[str, ...], normal_mode: bool, door_route_key: Any) -> str:
    """Emit one plan's source with one lowering class."""
    graph = lowering.build_site_graph(
        root_spell_id=root_key[0], root_instance_key=root_key, steps=steps, topology_for=topologies.get,
    )
    source, _namespace, _masked = lowering.emit(
        steps=steps, site_graph=graph, resolution=OverrideKeyResolver.resolve(graph, keys),
        root_instance_key=root_key, root_spell_id=root_key[0], root_spell_name=root_key[0], arity=0,
        normal_mode=normal_mode, door_route_key=door_route_key,
    )
    graph.cleanup()
    return source


def _shapes() -> List[Tuple[str, Tuple[Any, ...], Dict[str, Any], Tuple[str, Any], Tuple[str, ...], bool, Any]]:
    """Return (name, steps, topologies, root key, keys, normal mode, door route key) for every probed shape."""
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    shapes = []
    # 1. many root over S(d: D disposal, n: N plain)
    d, n = _spell("d", built, disposal=("close",)), _spell("n", built)
    s, root = _spell("s", built, shared), _spell("root", built)
    steps = (_step(("d", 1), d), _step(("n", 2), n), _step(("s", None), s, ("d", (("d", 1),)), ("n", (("n", 2),))),
             _step(("root", 0), root, ("s", (("s", None),))))
    topologies = {"root": SpellLocalTopology("root", (_socket("root", "s", 0), _socket("root", "limit", 1, optional=True))),
                  "s": SpellLocalTopology("s", (_socket("s", "d", 0), _socket("s", "n", 1)))}
    shapes.append(("many-root-over-holder normal", steps, topologies, ("root", 0), (), True, None))
    shapes.append(("many-root-over-holder override(limit)", steps, topologies, ("root", 0), ("limit",), False, None))
    # 2. holder without disposal children (no adoption expected)
    n2, s2, root2 = _spell("n", built), _spell("s", built, shared), _spell("root", built)
    steps2 = (_step(("n", 1), n2), _step(("s", None), s2, ("n", (("n", 1),))), _step(("root", 0), root2, ("s", (("s", None),))))
    topologies2 = {"root": SpellLocalTopology("root", (_socket("root", "s", 0),)),
                   "s": SpellLocalTopology("s", (_socket("s", "n", 0),))}
    shapes.append(("holder-with-plain-child normal", steps2, topologies2, ("root", 0), (), True, None))
    # 3. nested: root(t: T(s: S(d: D)), d2: D2 at top level)
    d3, s3, t3 = _spell("d", built, disposal=("close",)), _spell("s", built, shared), _spell("t", built, shared)
    d4, root3 = _spell("d2", built, disposal=("close",)), _spell("root", built)
    steps3 = (_step(("d", 1), d3), _step(("s", None), s3, ("d", (("d", 1),))), _step(("t", None), t3, ("s", (("s", None),))),
              _step(("d2", 2), d4), _step(("root", 0), root3, ("t", (("t", None),)), ("d2", (("d2", 2),))))
    topologies3 = {"root": SpellLocalTopology("root", (_socket("root", "t", 0), _socket("root", "d2", 1))),
                   "t": SpellLocalTopology("t", (_socket("t", "s", 0),)),
                   "s": SpellLocalTopology("s", (_socket("s", "d", 0),))}
    shapes.append(("nested-holders + top-level disposal many normal", steps3, topologies3, ("root", 0), (), True, None))
    # 4. door-held per-conduit root with a disposal child
    d5, root5 = _spell("d", built, disposal=("close",)), _spell("root", built, shared, disposal=("close",))
    steps5 = (_step(("d", 1), d5), _step(("root", None), root5, ("d", (("d", 1),))))
    topologies5 = {"root": SpellLocalTopology("root", (_socket("root", "d", 0),))}
    shapes.append(("door-held per-conduit root normal", steps5, topologies5, ("root", None), (), True, "unique_per_conduit"))
    shapes.append(("per-conduit root without door normal", steps5, topologies5, ("root", None), (), True, None))
    # 5. a unique root holder (owner-store route) with a disposal child and a plain `extra` many; the override
    #    plan supplies `extra` (the shape of the 0.2.8235 override test)
    d6, x6 = _spell("d", built, disposal=("close",)), _spell("x", built)
    root6 = _spell("root", built, Existence.unique)
    steps6 = (_step(("d", 1), d6), _step(("x", 2), x6),
              _step(("root", None), root6, ("d", (("d", 1),)), ("extra", (("x", 2),))))
    topologies6 = {"root": SpellLocalTopology("root", (_socket("root", "d", 0), _socket("root", "extra", 1)))}
    shapes.append(("unique root holder normal", steps6, topologies6, ("root", None), (), True, None))
    shapes.append(("unique root holder override(extra)", steps6, topologies6, ("root", None), ("extra",), False, None))
    return shapes


def _functions(source: str) -> Dict[str, str]:
    """Split emitted source into its top-level functions by name."""
    functions: Dict[str, str] = {}
    for chunk in source.split("\ndef ")[0:]:
        text = chunk if chunk.startswith("def ") else "def " + chunk
        name = text[4:text.index("(")]
        functions[name] = text
    return functions


def main() -> int:
    """Diff every shape; print one verdict line per shape and the added lines; exit 1 on an unexpected change."""
    old_lowering = _load_old()
    unexpected = 0
    for name, steps, topologies, root_key, keys, normal_mode, door in _shapes():
        old = _emit(old_lowering, steps, topologies, root_key, keys, normal_mode, door)
        new = _emit(SitePlanLowering, steps, topologies, root_key, keys, normal_mode, door)
        old_functions, new_functions = _functions(old), _functions(new)
        plan = SitePlanLowering.PLAN_FUNCTION_NAME
        plan_same = old_functions[plan] == new_functions[plan]
        added: List[str] = []
        other = 0
        for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0):
            if line.startswith(("---", "+++", "@@")):
                continue
            if line.startswith("+") and "adopt_children(" in line:
                added.append(line[1:].strip())
            else:
                other += 1
        ok = plan_same and other == 0 and set(old_functions) == set(new_functions)
        unexpected += 0 if ok else 1
        print(f"{'OK ' if ok else 'BAD'} | {name} | plan body identical={plan_same} | other diff lines={other} | "
              f"added={added}")
    print(f"shapes with unexpected changes: {unexpected}")
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
