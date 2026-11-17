"""
Scratch benchmark: bind many spells with the Crystallizer active and a user source root.

Builds a throwaway project (MODULES modules in one package under <tmp>/src, each importing
IMPORTS earlier siblings plus a few melder modules), imports it, activates the Crystallizer
with defaults and that source root, and binds SPELLS_PER_MODULE classes per module through
the root conduit of a Nexus frame (a dynamic frame, so every bind builds a spell crystal).
Reports the total bind time, realpath and find_spec call counts, and optionally a cProfile of
the first PROFILE_BINDS binds. Windows only (it counts ntpath.realpath).

Usage, from the repository root:
    python -X gil=0 <this file> MODULES SPELLS_PER_MODULE IMPORTS PROFILE_BINDS
"""

import cProfile
import importlib
import importlib.util
import io
import ntpath
import pstats
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

# context_compass/artifacts/<lane>/probes/<this file>: the repository root is four levels up.
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


class CallCounter:
    """Count calls of one function by wrapping it."""

    def __init__(self, owner: Any, attribute: str) -> None:
        self.owner = owner
        self.attribute = attribute
        self.original = getattr(owner, attribute)
        self.calls = 0
        self.seconds = 0.0
        counter = self

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            counter.calls += 1
            started = time.perf_counter()
            try:
                return counter.original(*args, **kwargs)
            finally:
                counter.seconds += time.perf_counter() - started

        setattr(owner, attribute, wrapped)

    def restore(self) -> None:
        setattr(self.owner, self.attribute, self.original)


def build_project(root: Path, modules: int, spells_per_module: int, imports: int) -> List[str]:
    """Write the package and return its module names in creation order."""
    package = root / "src" / "benchapp"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    rng = random.Random(7)
    names: List[str] = []
    melder_imports = (
        "from melder.aether.conduit.meld.contracts.spell_map import SpellMap\n"
        "from melder.aether.spellbook.existence.existence import Existence\n"
        "import melder.aether.aether\n"
        "import json\nimport os\nfrom typing import Optional, List\n"
    )
    for index in range(modules):
        lines = [melder_imports]
        if index:
            for target in sorted(set(rng.randrange(0, index) for _ in range(imports))):
                lines.append(
                    "from benchapp.mod_{0} import Spell_{0}_0, Spell_{0}_1\n".format(target)
                    if spells_per_module > 1
                    else "from benchapp.mod_{0} import Spell_{0}_0\n".format(target)
                )
        for spell in range(spells_per_module):
            lines.append(
                "\n\nclass Spell_{0}_{1}:\n    def __init__(self) -> None:\n"
                "        self.value = {1}\n".format(index, spell)
            )
        (package / "mod_{0}.py".format(index)).write_text("".join(lines), encoding="utf-8")
        names.append("benchapp.mod_{0}".format(index))
    return names


def main() -> None:
    modules = int(sys.argv[1])
    spells_per_module = int(sys.argv[2])
    imports = int(sys.argv[3])
    profile_binds = int(sys.argv[4])
    workdir = Path(tempfile.mkdtemp(prefix="crystal_bench_"))
    try:
        names = build_project(workdir, modules, spells_per_module, imports)
        sys.path.insert(0, str(workdir / "src"))
        from melder.aether.aether import Aether
        from melder.aether.spellbook.spellbook import Spellbook
        from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
        from melder.crystallizer.configuration.crystallizer_configuration import (
            CrystallizerConfiguration,
        )
        from melder.crystallizer.crystallizer import Crystallizer
        from tests._codegen_system_support import (
            create_codegen_rift,
            create_enabled_nexus,
            reset_runtime_singletons,
        )

        CrystallizerCache.resolve_cache_root_path = staticmethod(
            lambda: workdir / "__crystallizer_cache__"
        )
        reset_runtime_singletons()
        module_objects = [importlib.import_module(name) for name in names]
        configuration = CrystallizerConfiguration().with_defaults()
        configuration.with_user_source_root_paths((workdir / "src",))
        configuration.activate()
        Crystallizer().activate(configuration)
        nexus = create_enabled_nexus()
        rift = create_codegen_rift(nexus)
        book = rift.create_nexus_frame(frame_name="bench")
        targets = []
        for index, module in enumerate(module_objects):
            for spell in range(spells_per_module):
                targets.append(getattr(module, "Spell_{0}_{1}".format(index, spell)))
        realpath = CallCounter(ntpath, "realpath")
        find_spec = CallCounter(importlib.util, "find_spec")
        profiler = cProfile.Profile()
        timings: Dict[str, float] = {}
        started = time.perf_counter()
        for position, target in enumerate(targets):
            if position < profile_binds:
                profiler.enable()
            book.bind(spell=target, existence="unique", permissions="create")
            if position < profile_binds:
                profiler.disable()
            if position + 1 == min(50, len(targets)):
                timings["first_50"] = time.perf_counter() - started
        timings["all"] = time.perf_counter() - started
        realpath.restore()
        find_spec.restore()
        print(
            "binds={0} modules={1} total={2:.2f}s per_bind={3:.1f}ms first50={4:.2f}s".format(
                len(targets), modules, timings["all"], 1000 * timings["all"] / len(targets),
                timings["first_50"],
            )
        )
        print(
            "realpath calls={0} ({1:.2f}s)  find_spec calls={2} ({3:.2f}s)".format(
                realpath.calls, realpath.seconds, find_spec.calls, find_spec.seconds
            )
        )
        if profile_binds:
            buffer = io.StringIO()
            stats = pstats.Stats(profiler, stream=buffer)
            stats.sort_stats("tottime").print_stats(22)
            print(buffer.getvalue()[-6000:])
        reset_runtime_singletons()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
