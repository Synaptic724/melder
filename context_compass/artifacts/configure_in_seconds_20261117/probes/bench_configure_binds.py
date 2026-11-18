"""
Scratch benchmark for #331's widened landing: bind many spells with the Crystallizer and, optionally,
MutationResearch recording, timed without a profiler.

Builds a throwaway project (MODULES modules in one package under <tmp>/src, each importing IMPORTS earlier
siblings plus a few melder modules), imports it, activates the Crystallizer with defaults and that source root,
optionally activates the Aether-hosted MutationResearch root, and binds SPELLS_PER_MODULE classes per module
through the root conduit of a Nexus frame (a dynamic frame, so every bind builds a spell crystal and, with
research on, records a world entry). Reports wall time for all binds, for the first and the last hundred, the time
inside `Crystallizer.create_spell_crystal` and `MutationResearch.record_world_entry`, and call counts of
`ResearchNode.describe` and `NetworkVersioner.snapshot` (constant per entry after the landing, growing before).

Usage, from the repository root:
    python -X gil=0 <this file> MODULES SPELLS_PER_MODULE IMPORTS RESEARCH(0|1)
"""

import importlib
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, List

# context_compass/artifacts/<lane>/probes/<this file>: the repository root is four levels up.
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


class CallTimer:
    """Count and time the calls of one class attribute by wrapping it (no profiler)."""

    def __init__(self, owner: Any, attribute: str) -> None:
        self.owner = owner
        self.attribute = attribute
        self.original = owner.__dict__[attribute]
        self.calls = 0
        self.seconds = 0.0
        timer = self

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            timer.calls += 1
            started = time.perf_counter()
            try:
                return timer.original(*args, **kwargs)
            finally:
                timer.seconds += time.perf_counter() - started

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
    research_on = sys.argv[4] == "1"
    workdir = Path(tempfile.mkdtemp(prefix="configure_bench_"))
    try:
        names = build_project(workdir, modules, spells_per_module, imports)
        sys.path.insert(0, str(workdir / "src"))
        from melder.__version__ import __version__
        from melder.aether.aether import Aether
        from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
        from melder.crystallizer.configuration.crystallizer_configuration import (
            CrystallizerConfiguration,
        )
        from melder.crystallizer.crystallizer import Crystallizer
        from melder.mutation_research.mutation_research import MutationResearch
        from melder.mutation_research.research_set.network_versioner import NetworkVersioner
        from melder.mutation_research.research_set.research_node import ResearchNode
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
        if research_on:
            research = Aether().mutation_research
            research.configure(research.create_configuration().with_defaults().activate())
            research.activate(hydrate_from_record=False)
        targets = []
        for index, module in enumerate(module_objects):
            for spell in range(spells_per_module):
                targets.append(getattr(module, "Spell_{0}_{1}".format(index, spell)))
        crystal_timer = CallTimer(Crystallizer, "create_spell_crystal")
        world_entry_timer = CallTimer(MutationResearch, "record_world_entry")
        describe_counter = CallTimer(ResearchNode, "describe")
        snapshot_counter = CallTimer(NetworkVersioner, "snapshot")
        bind_seconds: List[float] = []
        started = time.perf_counter()
        for target in targets:
            bind_started = time.perf_counter()
            book.bind(spell=target, existence="unique", permissions="create")
            bind_seconds.append(time.perf_counter() - bind_started)
        total = time.perf_counter() - started
        for timer in (crystal_timer, world_entry_timer, describe_counter, snapshot_counter):
            timer.restore()
        first = bind_seconds[:100]
        last = bind_seconds[-100:]
        print(
            "melder={0} research={1} binds={2} modules={3} total={4:.2f}s per_bind={5:.2f}ms "
            "first100={6:.2f}ms/bind last100={7:.2f}ms/bind".format(
                __version__, int(research_on), len(targets), modules, total, 1000 * total / len(targets),
                1000 * sum(first) / len(first), 1000 * sum(last) / len(last),
            )
        )
        print(
            "create_spell_crystal {0} calls {1:.2f}s; record_world_entry {2} calls {3:.2f}s; "
            "ResearchNode.describe {4} calls; NetworkVersioner.snapshot {5} calls".format(
                crystal_timer.calls, crystal_timer.seconds, world_entry_timer.calls, world_entry_timer.seconds,
                describe_counter.calls, snapshot_counter.calls,
            )
        )
        reset_runtime_singletons()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
