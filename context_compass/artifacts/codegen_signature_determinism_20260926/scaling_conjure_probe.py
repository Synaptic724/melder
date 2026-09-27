"""
Owner-run scaling probe for measurement M7 (tranche T1, task 3: phase-8 pool digest).

Purpose:
    Show whether the conjure cold path carries a term that grows with the SQUARE of the spell
    count. Before task 3, phase 8 hashed the pool-wide signature rows once per root (N roots x
    N-sized rows); after it, the rows are hashed once per pass and each root pays only for its
    own blueprint. On the 29-spell gauntlet book that difference can sit inside run noise, so
    this probe conjures synthetic books of N = 29, 100 and 300 classes with a FIXED per-root
    blueprint size and reports the median conjure wall time per N.

Method:
    - `forest` shape (default): N/3 independent triples C_i -> B_i -> A_i. Every root's own
      blueprint is constant-sized, so any growth faster than linear in N is pool-sized work
      done per root (the term task 3 removes). `chain` shape: class i depends on i-1 and i-2;
      every root's blueprint grows with i, so the total is quadratic by construction - use it
      only as a control.
    - Classes are generated once per size from source text (`exec` on generated code, as the
      repository allows for codegen) with real annotations so DI resolves them by type.
    - Caching disabled, workers per spellbook from SCALE_WORKERS (default 1), fresh Aether
      per repeat; each repeat binds, conjures, cleans up. The first repeat is a warm-up and
      is discarded.

Run (native free-threaded interpreter, from the repository root), BEFORE (commit 6fc9af345)
and AFTER (the task-3 working tree), same machine, same session:
    python context_compass/artifacts/codegen_signature_determinism_20260926/scaling_conjure_probe.py

Env knobs:
    SCALE_SIZES    comma list of spell counts (default "29,100,300"; forest rounds down to x3)
    SCALE_REPEATS  timed repeats per size after one warm-up (default 5)
    SCALE_SHAPE    forest | chain (default forest)
    SCALE_WORKERS  phase_scheduler_workers_per_spellbook (default 1)

Reading the table:
    - "per_spell_us" is median conjure time divided by N. Flat per-spell cost across N means
      the cold path is linear; a per-spell cost that grows with N is the quadratic term.
    - Compare BEFORE and AFTER per N; a delta inside the BEFORE spread ("noise") is reported as
      no measurable change (measurement_plan.md, Reporting).
"""

import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _ensure_local_paths() -> None:
    """Make `src/` importable when the probe runs from a repository checkout."""
    project_root = Path(__file__).resolve().parents[3]
    src_dir = project_root / "src"
    src_as_str = str(src_dir)
    if src_as_str not in sys.path:
        sys.path.insert(0, src_as_str)


_ensure_local_paths()


class ScaleProbe:
    """
    Synthetic-book builder and timing loop for the scaling probe.

    Contract:
        - Slot-only static surface; owns no state.
        - Generated classes live in this module's namespace under unique names per size so
          two sizes never share a class object.
    """

    __slots__ = ()

    @staticmethod
    def build_classes(size: int, shape: str) -> List[type]:
        """
        Generate `size` classes with the requested dependency shape.

        Args:
            size:
                Number of classes (forest rounds down to a multiple of three).
            shape:
                `forest` or `chain`.

        Returns:
            List[type]: The classes in bind order (dependencies first).

        Raises:
            ValueError: On an unknown shape.
        """
        if shape == "forest":
            triples = max(1, size // 3)
            specs: List[Tuple[str, List[str]]] = []
            for index in range(triples):
                specs.append(("Leaf{0}".format(index), []))
                specs.append(("Mid{0}".format(index), ["Leaf{0}".format(index)]))
                specs.append(("Root{0}".format(index), ["Mid{0}".format(index)]))
        elif shape == "chain":
            specs = []
            for index in range(size):
                deps = ["Node{0}".format(j) for j in range(max(0, index - 2), index)]
                specs.append(("Node{0}".format(index), deps))
        else:
            raise ValueError("SCALE_SHAPE must be 'forest' or 'chain', got {0!r}".format(shape))
        namespace: Dict[str, Any] = {}
        lines: List[str] = []
        for name, deps in specs:
            params = ", ".join("dep{0}: {1}".format(i, dep) for i, dep in enumerate(deps))
            signature = "self, {0}".format(params) if params else "self"
            body = "".join(
                "        self.dep{0} = dep{0}\n".format(i) for i in range(len(deps))
            ) or "        pass\n"
            lines.append(
                "class {0}:\n"
                "    def __init__({1}) -> None:\n{2}".format(name, signature, body)
            )
        exec("\n".join(lines), namespace)
        classes: List[type] = []
        for name, _deps in specs:
            cls = namespace[name]
            cls.__module__ = __name__
            cls.__qualname__ = "{0}_{1}_{2}".format(shape, size, name)
            classes.append(cls)
        return classes

    @staticmethod
    def reset_runtime() -> None:
        """Start from a fresh Aether singleton (same seam the breakdown harness uses)."""
        from melder.aether.aether import Aether
        from melder.aether.conduit.conduit import Conduit
        from melder.aether.spellbook.spellbook import Spellbook
        from melder.nexus.nexus import Nexus

        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    @staticmethod
    def time_one_conjure(classes: List[type], workers: int) -> float:
        """
        Bind every class and time one conjure with caching disabled.

        Returns:
            float: Conjure wall time in seconds (bind time excluded).
        """
        from melder.aether.spellbook.existence.existence import Existence
        from melder.aether.spellbook.spellbook import Spellbook

        ScaleProbe.reset_runtime()
        spellbook = Spellbook(aetheric_frame="scale-probe")
        spellbook.get_configuration().set_property(
            "phase_scheduler_workers_per_spellbook", workers,
        )
        spellbook.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
        for cls in classes:
            spellbook.bind(spell=cls, existence=Existence.unique, permissions="create")
        started = time.perf_counter()
        conduit = spellbook.conjure(name="scale-probe", dynamic=False)
        elapsed = time.perf_counter() - started
        conduit.permanent_cleanup()
        spellbook.cleanup()
        return elapsed


def main() -> None:
    """Run the sweep and print one row per size."""
    sizes = [int(token) for token in os.environ.get("SCALE_SIZES", "29,100,300").split(",")]
    repeats = max(1, int(os.environ.get("SCALE_REPEATS", "5")))
    shape = os.environ.get("SCALE_SHAPE", "forest")
    workers = max(1, int(os.environ.get("SCALE_WORKERS", "1")))
    print(
        "scaling probe: shape={0} workers={1} repeats={2} python={3}".format(
            shape, workers, repeats, sys.version.split()[0],
        )
    )
    print("{0:>6} {1:>8} {2:>12} {3:>12} {4:>12} {5:>12}".format(
        "N", "bound", "median_ms", "min_ms", "max_ms", "per_spell_us",
    ))
    for size in sizes:
        classes = ScaleProbe.build_classes(size, shape)
        ScaleProbe.time_one_conjure(classes, workers)
        samples = [ScaleProbe.time_one_conjure(classes, workers) for _ in range(repeats)]
        median = statistics.median(samples)
        print("{0:>6} {1:>8} {2:>12.3f} {3:>12.3f} {4:>12.3f} {5:>12.1f}".format(
            size, len(classes), median * 1e3, min(samples) * 1e3, max(samples) * 1e3,
            median * 1e6 / len(classes),
        ))


if __name__ == "__main__":
    main()
