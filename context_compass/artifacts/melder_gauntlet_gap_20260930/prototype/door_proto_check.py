"""
Check the top-level door overlay on the shared gauntlet's Melder lane (melder_0, 2026-09-30).

Usage:
    python -X gil=0 door_proto_check.py --repo-root <tree> [--proto]

Contract:
    - Builds the harness Melder lane (with the overlay installed first when --proto), runs 20 harness iterations,
      then prints how many creation-context doors are nested, carry cells, or are deferred.
"""
import argparse
import importlib
import sys
from pathlib import Path


def main() -> int:
    """
    Build, warm, and describe the doors.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--proto", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    for path in (root, root / "src", Path(__file__).resolve().parent):
        sys.path.insert(0, str(path))
    import door_proto
    if args.proto:
        door_proto.install(door_proto.door_module())
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops("melder")
    ops.spawn_singletons()
    for ix in range(20):
        gauntlet._run_gauntlet_once(ops, cfg, ix)
    import gc
    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
    executors = []
    for obj in gc.get_objects():
        if isinstance(obj, CreationContext):
            for slot in ("_no_overrides_instance_executor", "_overrides_executor"):
                try:
                    value = getattr(obj, slot)
                except AttributeError:
                    continue
                if value is not None and hasattr(value, "__code__"):
                    executors.append(value)
    print(f"proto={args.proto} doors: {door_proto.describe_doors(executors)}")
    sample = next((fn for fn in executors if fn.__code__.co_name.startswith("_creation_context")), None)
    if sample is not None:
        print(f"sample: {sample.__code__.co_qualname} file={sample.__code__.co_filename} cells={sample.__code__.co_freevars}")
    ops.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
