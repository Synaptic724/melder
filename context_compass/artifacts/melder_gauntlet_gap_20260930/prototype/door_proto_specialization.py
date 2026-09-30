"""
Specialization check for the top-level door overlay (melder_0, 2026-09-30).

Purpose:
    Show how CPython's adaptive interpreter has specialized the call sites that invoke creation-context doors
    (the warm lanes of SpellSpace.meld and Conduit.meld) and the global loads inside the doors, after warm scope
    cycles, with and without the overlay.

Usage:
    python -X gil=0 door_proto_specialization.py --repo-root <tree> [--proto] [--cycles 3000]

Contract:
    - Warms the harness Melder lane (20 harness iterations plus --cycles cycles per lane on this thread), then prints
      the adaptive opnames of every CALL on the door-call lines and of the LOAD_GLOBALs in one door of each route.
"""
import argparse
import dis
import importlib
import inspect
import sys
from pathlib import Path


def _call_sites(function, needle: str) -> list:
    """
    Adaptive opnames of the CALL instructions on source lines containing `needle`.

    Args:
        function: A Python function.
        needle: Source text identifying the call line.

    Returns:
        list: (line, opname) pairs.
    """
    lines, start = inspect.getsourcelines(function)
    wanted = {start + ix for ix, text in enumerate(lines) if needle in text}
    found = []
    for instruction in dis.get_instructions(function, adaptive=True):
        if instruction.positions and instruction.positions.lineno in wanted and instruction.opname.startswith("CALL"):
            found.append((instruction.positions.lineno, instruction.opname))
    return found


def main() -> int:
    """
    Warm, then print the specialization state.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--proto", action="store_true")
    parser.add_argument("--cycles", type=int, default=3000)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    for path in (root, root / "src", Path(__file__).resolve().parent):
        sys.path.insert(0, str(path))
    if args.proto:
        import door_proto
        door_proto.install(door_proto.door_module())
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops("melder")
    ops.spawn_singletons()
    for ix in range(20):
        gauntlet._run_gauntlet_once(ops, cfg, ix)
    for lane in (ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle):
        for ix in range(args.cycles):
            lane(ix % 3)
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.conduit.spell_space.spell_space import SpellSpace
    print(f"proto={args.proto}")
    print("  SpellSpace.meld door call:", _call_sites(SpellSpace.meld, "fast_executor(meld_door"))
    print("  Conduit.meld door call:   ", _call_sites(Conduit.meld, "fast_executor(meld_door"))
    import gc
    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
    seen = set()
    for obj in gc.get_objects():
        if isinstance(obj, CreationContext):
            door = getattr(obj, "_no_overrides_instance_executor", None)
            if door is None or not hasattr(door, "__code__"):
                continue
            route = door.__code__.co_filename
            if route in seen or "_cold" in door.__code__.co_name:
                continue
            seen.add(route)
            ops_in_door = [ins.opname for ins in dis.get_instructions(door, adaptive=True)
                           if ins.opname.startswith(("LOAD_GLOBAL", "LOAD_DEREF", "COPY_FREE_VARS", "LOAD_ATTR"))]
            print(f"  door {route}: {ops_in_door}")
    ops.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
