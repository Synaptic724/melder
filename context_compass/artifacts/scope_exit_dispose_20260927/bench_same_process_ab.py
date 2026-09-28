"""Same-process A/B of the scope-exit change on the hot scope operations. melder_0, 2026-09-27.

Process and memory-layout noise between two interpreter runs is about +-3% on these operations, larger than the
change. This harness loads the NEW tree and compiles the OLD versions of every method on the measured paths from
the OLD tree's source into the same module namespaces, then alternates OLD and NEW implementations in ABBA blocks
inside one process, so both variants share one heap, one code layout and one warm world.

Swapped per operation:
    lesser create+cleanup: Conduit._prepare_for_pool, Conduit._cleanup_spellspaces_for_pool
    managed space enter/exit: Conduit.enter_spellspace, SpellSpace.__exit__,
                              SpellSpace.recycle_from_managed_context, SpellSpacePool.acquire_untracked,
                              SpellSpacePool.release
    warm space meld: SpellSpace.meld (the released check)
Usage: python -X gil=0 bench_same_process_ab.py <old tree> <new tree> [blocks]
"""
import ast
import statistics
import sys
import threading
import time
from pathlib import Path

assert sys.version_info >= (3, 14), sys.version
OLD, NEW = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
BLOCKS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
for p in (NEW, NEW / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
import melder.aether.conduit.conduit as conduit_module
import melder.aether.conduit.spell_space.spell_space as space_module
import melder.aether.conduit.spell_space.spell_space_pool as pool_module

assert Path(conduit_module.__file__).resolve().is_relative_to(NEW), conduit_module.__file__


def old_methods(rel_path, class_name, names, module):
    """Compile the OLD tree's version of `names` from `class_name` into `module`'s globals."""
    source = (OLD / "src" / rel_path).read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    out = {}
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            wrapper = ast.Module(body=[node], type_ignores=[])
            namespace = {}
            exec(compile(wrapper, f"<old {class_name}.{node.name}>", "exec"), module.__dict__, namespace)
            fn = namespace[node.name]
            fn.__qualname__ = f"{class_name}.{node.name}"
            out[node.name] = fn
    assert set(out) == set(names), (class_name, set(names) - set(out))
    return out


SWAPS = {
    "lesser_create_cleanup": [
        (conduit_module.Conduit, old_methods("melder/aether/conduit/conduit.py", "Conduit",
                                             ["_prepare_for_pool", "_cleanup_spellspaces_for_pool"], conduit_module)),
    ],
    "space_enter_exit": [
        (conduit_module.Conduit, old_methods("melder/aether/conduit/conduit.py", "Conduit",
                                             ["enter_spellspace"], conduit_module)),
        (space_module.SpellSpace, old_methods("melder/aether/conduit/spell_space/spell_space.py", "SpellSpace",
                                              ["__exit__", "recycle_from_managed_context"], space_module)),
        (pool_module.SpellSpacePool, old_methods("melder/aether/conduit/spell_space/spell_space_pool.py",
                                                 "SpellSpacePool", ["acquire_untracked", "release"], pool_module)),
    ],
    "space_warm_meld": [
        (space_module.SpellSpace, old_methods("melder/aether/conduit/spell_space/spell_space.py", "SpellSpace",
                                              ["meld"], space_module)),
    ],
}
NEW_IMPL = {op: [(cls, {name: cls.__dict__[name] for name in fns}) for cls, fns in swaps] for op, swaps in SWAPS.items()}


def use(op, variant):
    """Install the OLD or NEW implementations for one operation."""
    for cls, fns in (SWAPS[op] if variant == "old" else NEW_IMPL[op]):
        for name, fn in fns.items():
            setattr(cls, name, fn)


ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit = rv["conduit"]
marker_id = rv["spell_ids"][g.RequestScopeMarker]
pc = time.perf_counter_ns
results = {op: {"old": [], "new": []} for op in SWAPS}


def lesser_loop(n):
    """Lesser acquisition and soft cleanup with nothing inside."""
    create = conduit.create_lesser_conduit
    for _ in range(n):
        create().cleanup()


def space_loop(n):
    """Managed space scope with nothing inside, on one lesser."""
    lesser = conduit.create_lesser_conduit()
    enter = lesser.enter_spellspace
    for _ in range(n):
        with enter():
            pass
    lesser.cleanup()


def space_meld_loop(n):
    """Warm melds of a space-scoped object inside one managed space."""
    lesser = conduit.create_lesser_conduit()
    with lesser.enter_spellspace() as space:
        space.meld(spell_id=marker_id)
        meld = space.meld
        for _ in range(n):
            meld(spell_id=marker_id)
    lesser.cleanup()


LOOPS = {"lesser_create_cleanup": (lesser_loop, 30_000), "space_enter_exit": (space_loop, 80_000),
         "space_warm_meld": (space_meld_loop, 120_000)}


def body():
    """Warm both variants, then time ABBA blocks for every operation."""
    for op, (loop, n) in LOOPS.items():
        for variant in ("old", "new"):
            use(op, variant); loop(n // 5)
        use(op, "new")
    for block in range(BLOCKS):
        order = ("old", "new", "new", "old") if block % 2 == 0 else ("new", "old", "old", "new")
        for op, (loop, n) in LOOPS.items():
            for variant in order:
                use(op, variant)
                t0 = pc(); loop(n); results[op][variant].append((pc() - t0) / n)
            use(op, "new")


t = threading.Thread(target=body)
t.start()
t.join()
print(f"old={OLD.name} new={NEW.name} blocks={BLOCKS} gil={sys._is_gil_enabled()} ({sys.version.split()[0]})")
for op, per in results.items():
    o, n = statistics.median(per["old"]), statistics.median(per["new"])
    print(f"  {op:24s} old={o:7.1f} ns  new={n:7.1f} ns  delta={n - o:+6.1f} ns ({(n - o) / o:+.1%})"
          f"  old_range={min(per['old']):.1f}-{max(per['old']):.1f}  new_range={min(per['new']):.1f}-{max(per['new']):.1f}"
          f"  samples={len(per['old'])}")
ops.cleanup()
