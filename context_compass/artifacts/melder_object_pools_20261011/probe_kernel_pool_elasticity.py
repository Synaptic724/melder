"""
Probe: how the kernel pools (SpellSpacePool, ConduitPool) size themselves under a burst.

Question (pools epic, owner challenge of 2026-10-12): do the kernel pools behave elastically, and
does their retained target (`target_idle`) move? Reads each pool's public `describe()` before a burst,
while 50 objects are out at once, after they all return, and after a second burst.

Run on a copy of `src` (the conjure cache writes under the package root):
    PYTHONPATH=<copy>/src PYTHONDONTWRITEBYTECODE=1 python probe_kernel_pool_elasticity.py
"""
import sys
from contextlib import ExitStack
from typing import Any

from melder import Spellbook


def report(label: str, pool: Any) -> None:
    """Write the pool's sizing fields after `label`."""
    state = pool.describe()
    sys.stdout.write(
        f"{label}: target_idle={state['target_idle']} idle={state['idle_count']} "
        f"baseline={state['baseline_idle']} max={state['max_idle']}\n"
    )


def spellspace_burst(root: Any, label: str) -> None:
    """Hold 50 nested managed spellspaces open at once, then return them all."""
    pool = root._spellspace_pool
    with ExitStack() as stack:
        held = [stack.enter_context(root.enter_spellspace()) for _ in range(50)]
        report(f"spellspace pool, {label}, 50 open", pool)
        sys.stdout.write(f"  distinct live spaces: {len({id(space) for space in held})}\n")
    report(f"spellspace pool, {label}, all returned", pool)


def lesser_burst(root: Any, label: str) -> None:
    """Hold 50 lesser conduits at once, then return them all to the root's pool."""
    pool = root._conduit_pool
    held = [root.create_lesser_conduit() for _ in range(50)]
    report(f"lesser pool, {label}, 50 live", pool)
    sys.stdout.write(f"  distinct live lessers: {len({id(lesser) for lesser in held})}\n")
    for lesser in held:
        lesser.cleanup()
    report(f"lesser pool, {label}, all returned", pool)


def main() -> int:
    """Run two bursts against each kernel pool of one root and return 0."""
    book = Spellbook()
    root = book.conjure(name="pool_probe_root")
    try:
        report("spellspace pool, fresh", root._spellspace_pool)
        spellspace_burst(root, "burst 1")
        spellspace_burst(root, "burst 2")
        report("lesser pool, fresh", root._conduit_pool)
        lesser_burst(root, "burst 1")
        lesser_burst(root, "burst 2")
    finally:
        root.permanent_cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
