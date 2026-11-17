"""
Unit tests for crystal analyses reusing what earlier analyses learned about each module (GitHub #331).

Purpose:
    Pin the owner's decision of 2026-11-17: an analysis reuses each module's resolved path, custody kind and
    import facts, the policy roots and site-package provenance from earlier analyses while the module object and
    its file are unchanged, records exactly what a fresh analysis records, and derives a module again when its
    file or its module object changes. Synthetic modules and custom strategies are never served from the cache,
    and the cache keeps no module alive.

Runs only on 3.14t (melder package root import chain).
"""
import gc
import hashlib
import importlib
import importlib.metadata
import importlib.util
import os
import pathlib
import sys
import threading
import types
import weakref
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import pytest

from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.crystal_analyzer import CrystalAnalyzer
from melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy import (
    SitePackageCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy import (
    SyntheticCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.module_answer_cache import ModuleAnswerCache
from melder.crystallizer.crystal_analysis.physical_source_cache import (
    PhysicalSourceCache,
)
from melder.crystallizer.crystal_analysis.strategies.dependency_view_strategy import (
    DependencyViewStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.export_surface_strategy import (
    ExportSurfaceStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.from_import_statement_strategy import (
    FromImportStatementStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.import_statement_strategy import (
    ImportStatementStrategy,
)
from melder.crystallizer.synthetic_module import SyntheticModule


class AnswerWorld:
    """
    Module names and sources of the reuse world, unique to this file.

    Contract:
        - `ROOT` imports the package's `core` member and `json`; `core` imports a function from `helpers`, the
          `helpers` module relatively and `os`; `helpers` imports nothing. So the world has plain imports, a member
          that is a submodule, a member that is not, a relative import and two standard-library leaves.
        - `EXTRA` is written but imported only after an edit of `helpers`.
    """

    ROOT: str = "p331_root"
    PACKAGE: str = "p331pkg"
    CORE: str = "p331pkg.core"
    HELPERS: str = "p331pkg.helpers"
    EXTRA: str = "p331_extra"
    SOURCES: Dict[str, str] = {
        "p331_root.py": "from p331pkg import core\nimport json\n\n\nclass RootSpell:\n    pass\n",
        "p331pkg/__init__.py": "",
        "p331pkg/core.py": "from p331pkg.helpers import tool\nfrom . import helpers\nimport os\nVALUE = 1\n",
        "p331pkg/helpers.py": "def tool() -> int:\n    return 1\n",
        "p331_extra.py": "EXTRA = 1\n",
    }

    @staticmethod
    def module_names() -> Tuple[str, ...]:
        """
        Return every module name the world writes.

        Returns:
            Tuple[str, ...]: Names to evict from `sys.modules` around each test.
        """
        return (AnswerWorld.ROOT, AnswerWorld.PACKAGE, AnswerWorld.CORE, AnswerWorld.HELPERS, AnswerWorld.EXTRA)


def _reset_analysis_caches() -> None:
    """
    Empty the three process-wide analysis caches, so a test starts and ends with nothing remembered.

    Returns:
        None.
    """
    ModuleAnswerCache._clear_for_tests()
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    PhysicalSourceCache._clear_for_tests()


@pytest.fixture()
def answer_world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """
    Write the reuse world, put it on `sys.path` and import it, with empty analysis caches around the test.

    Contract:
        - Every module is imported before the test, as a bound spell's modules are, so each name has one live
          module object from the first analysis on.

    Yields:
        Path: The resolved directory holding the world, used as the user source root.
    """
    for relative, source in AnswerWorld.SOURCES.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in AnswerWorld.module_names():
        sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    for module_name in (AnswerWorld.ROOT, AnswerWorld.CORE, AnswerWorld.HELPERS):
        importlib.import_module(module_name)
    _reset_analysis_caches()
    yield tmp_path.resolve()
    for module_name in AnswerWorld.module_names():
        sys.modules.pop(module_name, None)
    _reset_analysis_caches()


def _analyze(world: Path, analyzer: Optional[CrystalAnalyzer] = None) -> CrystalAnalysisResult:
    """
    Run one analysis of the world from its live root module, as a spell crystal does.

    Args:
        world: The resolved world directory, the only user root.
        analyzer: An analyzer to use instead of a default one; it is cleaned here either way.

    Returns:
        CrystalAnalysisResult: The analysis result; the caller cleans it.
    """
    worker = analyzer or CrystalAnalyzer(user_source_root_paths=(world,), site_package_root_paths=())
    root_module = sys.modules[AnswerWorld.ROOT]
    try:
        return worker.analyze_spell_root(
            root_module_name=AnswerWorld.ROOT,
            root_module_obj=root_module,
            root_module_path=CrystalAnalyzer.resolve_module_path(AnswerWorld.ROOT, root_module),
        )
    finally:
        worker.cleanup()


def _described(world: Path, analyzer: Optional[CrystalAnalyzer] = None) -> Dict[str, Any]:
    """
    Run one analysis and return its describe() payload, cleaning the result.

    Args:
        world: The resolved world directory.
        analyzer: Optional analyzer, as in `_analyze`.

    Returns:
        Dict[str, Any]: The detached payload.
    """
    result = _analyze(world, analyzer)
    try:
        return result.describe()
    finally:
        result.cleanup()


class CallCounts:
    """
    Count calls of a few functions by name while a test body runs, delegating to the real functions.

    Contract:
        - `watch(owner, attribute)` wraps `owner.attribute` through the test's monkeypatch, so pytest restores it.
        - `counts[attribute]` is how many times the wrapped function ran since `reset()`.
    """

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Start with no watched functions.

        Args:
            monkeypatch: The test's monkeypatch, which owns every replacement.
        """
        self._monkeypatch = monkeypatch
        self.counts: Counter = Counter()

    def watch(self, owner: Any, attribute: str) -> None:
        """
        Count calls of `owner.attribute` from now on.

        Args:
            owner: The class or module holding the function.
            attribute: The attribute name to wrap.

        Returns:
            None.
        """
        original: Callable[..., Any] = getattr(owner, attribute)
        counts = self.counts

        def counting(*args: Any, **kwargs: Any) -> Any:
            """Record one call, then make it for real."""
            counts[attribute] += 1
            return original(*args, **kwargs)

        self._monkeypatch.setattr(owner, attribute, counting)

    def reset(self) -> None:
        """
        Forget every count so far.

        Returns:
            None.
        """
        self.counts.clear()


def _watch_analysis_work(monkeypatch: pytest.MonkeyPatch) -> CallCounts:
    """
    Count the three kinds of work a reused analysis must not repeat: path resolution, member probes and custody.

    Args:
        monkeypatch: The test's monkeypatch.

    Returns:
        CallCounts: Counting `Path.resolve`, `importlib.util.find_spec` and the synthetic strategy's `matches`
            (the custody chain's first question).
    """
    calls = CallCounts(monkeypatch)
    calls.watch(pathlib.Path, "resolve")
    calls.watch(importlib.util, "find_spec")
    calls.watch(SyntheticCustodyStrategy, "matches")
    return calls


def test_a_second_analysis_of_an_unchanged_world_resolves_matches_and_probes_nothing(
        answer_world: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: the first analysis derives every answer; a second analysis of the unchanged world resolves no path,
    runs no custody chain and makes no member-submodule probe - every answer comes from the cache.
    """
    calls = _watch_analysis_work(monkeypatch)
    _described(answer_world)
    assert calls.counts["resolve"] > 0
    assert calls.counts["find_spec"] > 0
    assert calls.counts["matches"] > 0
    calls.reset()

    _described(answer_world)

    assert dict(calls.counts) == {}


def test_a_reused_analysis_records_what_a_fresh_analysis_records(answer_world: Path) -> None:
    """
    Contract: answers served from the cache produce the same result as a fresh analysis - targets, kinds, paths,
    edges, from-import diagnostics, fingerprints, export surfaces and load order alike.
    """
    fresh = _described(answer_world)
    reused = _described(answer_world)
    _reset_analysis_caches()
    fresh_again = _described(answer_world)

    assert reused == fresh
    assert fresh_again == fresh
    assert fresh["module_to_direct_dependencies"][AnswerWorld.CORE] == [AnswerWorld.HELPERS, AnswerWorld.PACKAGE, "os"]
    assert set(fresh["physical_module_fingerprints"]) == {
        AnswerWorld.ROOT, AnswerWorld.CORE, AnswerWorld.HELPERS,
    }


def test_editing_a_module_file_derives_that_module_again(answer_world: Path) -> None:
    """
    Contract: a file whose size and modification time change is derived again on the next analysis - its new
    import shows up - while the result still equals a fresh analysis of the edited world.
    """
    _described(answer_world)
    helpers_file = answer_world / "p331pkg" / "helpers.py"
    previous = helpers_file.stat()
    helpers_file.write_text("import p331_extra\n\n\ndef tool() -> int:\n    return 2\n", encoding="utf-8")
    os.utime(helpers_file, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000_000))

    edited = _described(answer_world)
    _reset_analysis_caches()
    fresh = _described(answer_world)

    assert edited["module_to_direct_dependencies"][AnswerWorld.HELPERS] == [AnswerWorld.EXTRA]
    assert edited == fresh


def test_a_member_submodule_created_later_is_seen_once_its_importer_changes(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract (the accepted residual of #331): a `from pkg import name` probe is kept with the importing module's
    facts, so a submodule file created later under that name is not seen while the importer and its file are
    unchanged; once the importer's file changes, the next analysis probes again and records the new submodule.
    """
    _reset_analysis_caches()
    package = tmp_path / "p331late"
    package.mkdir()
    (package / "__init__.py").write_text("def member() -> int:\n    return 1\n", encoding="utf-8")
    importer = tmp_path / "p331_late_importer.py"
    importer.write_text("from p331late import member\n", encoding="utf-8")
    module_names = ("p331late", "p331late.member", "p331_late_importer")
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in module_names:
        sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
    importer_module = importlib.import_module("p331_late_importer")

    def importer_dependencies() -> List[str]:
        """Analyze the importer once and return its recorded dependencies."""
        analyzer = CrystalAnalyzer(user_source_root_paths=(tmp_path.resolve(),), site_package_root_paths=())
        try:
            result = analyzer.analyze_spell_root(
                root_module_name="p331_late_importer",
                root_module_obj=importer_module,
                root_module_path=CrystalAnalyzer.resolve_module_path("p331_late_importer", importer_module),
            )
        finally:
            analyzer.cleanup()
        try:
            return list(result.module_to_direct_dependencies["p331_late_importer"])
        finally:
            result.cleanup()

    try:
        before = importer_dependencies()
        (package / "member.py").write_text("VALUE = 1\n", encoding="utf-8")
        importlib.invalidate_caches()
        kept = importer_dependencies()
        previous = importer.stat()
        importer.write_text("from p331late import member  # touched\n", encoding="utf-8")
        os.utime(importer, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000_000))
        after_edit = importer_dependencies()
    finally:
        for module_name in module_names:
            sys.modules.pop(module_name, None)
        _reset_analysis_caches()

    assert before == ["p331late"]
    assert kept == ["p331late"]
    assert after_edit == ["p331late.member", "p331late"]


def test_a_reimported_module_object_has_its_path_and_facts_derived_again(
        answer_world: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: path and facts answers belong to the module object they were derived from; when `sys.modules` holds
    a new object for a name, the next analysis computes that module's path and derives its facts again (reading
    its source fingerprint), and nothing else.
    """
    _described(answer_world)
    sys.modules.pop(AnswerWorld.HELPERS)
    replacement = importlib.import_module(AnswerWorld.HELPERS)
    resolved: List[str] = []
    original = CrystalAnalyzer._resolve_module_path_uncached

    def recording(module_name: str, module_obj: Optional[Any]) -> Optional[Path]:
        """Record which module had its path computed, then compute it."""
        resolved.append(module_name)
        return original(module_name, module_obj)

    monkeypatch.setattr(CrystalAnalyzer, "_resolve_module_path_uncached", staticmethod(recording))
    fingerprints = CallCounts(monkeypatch)
    fingerprints.watch(PhysicalSourceCache, "fingerprint_if_unchanged")

    described = _described(answer_world)

    assert resolved == [AnswerWorld.HELPERS]
    assert fingerprints.counts["fingerprint_if_unchanged"] == 1
    assert described["module_to_path"][AnswerWorld.HELPERS] == str(Path(replacement.__file__).resolve())


def test_synthetic_module_source_is_read_on_every_analysis(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: a synthetic module's source lives in memory and can change without a file to stat, so its custody is
    matched and its source read on every analysis - nothing about it is served from the cache.
    """
    _reset_analysis_caches()
    source_text = "import json\n"
    synthetic = SyntheticModule(
        module_name="p331_synthetic",
        spell_crystal_id="p331-crystal",
        source_text=source_text,
        source_sha256=hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        binding_signature="p331-signature",
    )
    reads = CallCounts(monkeypatch)
    reads.watch(SyntheticCustodyStrategy, "resolve_source")
    try:
        for _ in range(2):
            analyzer = CrystalAnalyzer(user_source_root_paths=(Path.cwd(),), site_package_root_paths=())
            try:
                result = analyzer.analyze_spell_root(
                    root_module_name="p331_synthetic",
                    root_module_obj=synthetic,
                    root_module_path=None,
                )
            finally:
                analyzer.cleanup()
            assert result.module_to_kind["p331_synthetic"] == "synthetic_module"
            result.cleanup()
    finally:
        _reset_analysis_caches()

    assert reads.counts["resolve_source"] == 2


def test_an_analyzer_with_its_own_fact_strategies_derives_every_module_again(
        answer_world: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: supplied fact strategies may not be source-pure, so such an analyzer re-derives every module's facts
    (here: makes its member probes again) even when a default analyzer already cached them.
    """
    _described(answer_world)
    calls = _watch_analysis_work(monkeypatch)

    custom = CrystalAnalyzer(
        user_source_root_paths=(answer_world,),
        site_package_root_paths=(),
        fact_strategies=[
            ImportStatementStrategy(),
            FromImportStatementStrategy(),
            ExportSurfaceStrategy(),
            DependencyViewStrategy(),
        ],
    )
    described = _described(answer_world, custom)

    assert calls.counts["find_spec"] > 0
    assert described["module_to_direct_dependencies"][AnswerWorld.CORE] == [
        AnswerWorld.HELPERS, AnswerWorld.PACKAGE, "os",
    ]


def test_a_cached_answer_does_not_keep_its_module_alive(tmp_path: Path) -> None:
    """
    Contract: the cache holds a module only by weak reference, so a module nothing else holds is collected even
    after its path was cached.
    """
    _reset_analysis_caches()
    module_file = tmp_path / "p331_ephemeral.py"
    module_file.write_text("VALUE = 1\n", encoding="utf-8")
    ephemeral = types.ModuleType("p331_ephemeral")
    ephemeral.__file__ = str(module_file)
    try:
        resolved = CrystalAnalyzer.resolve_module_path("p331_ephemeral", ephemeral)
        cached_paths = ModuleAnswerCache._stats_for_tests()["module_paths"]
        reference = weakref.ref(ephemeral)
        del ephemeral
        gc.collect()
        collected = reference() is None
    finally:
        _reset_analysis_caches()

    assert resolved == module_file.resolve()
    assert cached_paths == 1
    assert collected


def test_the_oldest_answers_are_evicted_beyond_the_capacity(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: each map is bounded; storing past the capacity evicts the least recently used answer, which is then
    computed again on its next use.
    """
    _reset_analysis_caches()
    monkeypatch.setattr(ModuleAnswerCache, "_MAX_ENTRIES", 2)
    modules: List[types.ModuleType] = []
    for index in range(3):
        module_file = tmp_path / "p331_bounded_{0}.py".format(index)
        module_file.write_text("VALUE = {0}\n".format(index), encoding="utf-8")
        module = types.ModuleType("p331_bounded_{0}".format(index))
        module.__file__ = str(module_file)
        modules.append(module)
    try:
        for module in modules:
            CrystalAnalyzer.resolve_module_path(module.__name__, module)
        assert ModuleAnswerCache._stats_for_tests()["module_paths"] == 2
        calls = CallCounts(monkeypatch)
        calls.watch(pathlib.Path, "resolve")
        CrystalAnalyzer.resolve_module_path(modules[2].__name__, modules[2])
        assert calls.counts["resolve"] == 0
        CrystalAnalyzer.resolve_module_path(modules[0].__name__, modules[0])
        assert calls.counts["resolve"] == 1
    finally:
        _reset_analysis_caches()


def test_site_package_provenance_reads_installed_metadata_once_until_a_site_root_changes(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: the installed-distribution map is read once per state of the site roots; a later harvest reuses it,
    returns a fresh payload each time, and a site root whose modification time changes is read again.
    """
    _reset_analysis_caches()
    site_root = tmp_path / "site-packages"
    site_root.mkdir()
    reads: Counter = Counter()

    def fake_distributions() -> Dict[str, List[str]]:
        """Count one read of the installed metadata and answer for the fake package."""
        reads["packages_distributions"] += 1
        return {"p331dist": ["p331-dist"]}

    def fake_version(distribution_name: str) -> str:
        """Answer one fixed version for any distribution."""
        return "1.0"

    monkeypatch.setattr(importlib.metadata, "packages_distributions", fake_distributions)
    monkeypatch.setattr(importlib.metadata, "version", fake_version)
    strategy = SitePackageCustodyStrategy((site_root.resolve(),))
    try:
        first = strategy.harvest_provenance(module_name="p331dist.inner", module_path=None)
        assert first is not None
        first["all_distributions"].append("mutated by the caller")
        second = strategy.harvest_provenance(module_name="p331dist", module_path=None)
        assert reads["packages_distributions"] == 1
        assert second == {
            "distribution_name": "p331-dist",
            "distribution_version": "1.0",
            "all_distributions": ["p331-dist"],
            "top_level": "p331dist",
        }
        before = site_root.stat()
        os.utime(site_root, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
        strategy.harvest_provenance(module_name="p331dist", module_path=None)
        assert reads["packages_distributions"] == 2
    finally:
        strategy.cleanup()
        _reset_analysis_caches()


def test_policy_roots_are_resolved_once_per_input_and_working_directory(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: the user, site and environment roots are resolved once for the same raw input and interpreter
    state; the default user root follows the working directory, so a new working directory is resolved again.
    """
    _reset_analysis_caches()
    first_directory = tmp_path / "first"
    second_directory = tmp_path / "second"
    first_directory.mkdir()
    second_directory.mkdir()
    first_resolved = first_directory.resolve()
    second_resolved = second_directory.resolve()
    try:
        monkeypatch.chdir(first_directory)
        user_roots = CrystalAnalyzer.resolve_user_root_paths(None)
        site_roots = CrystalAnalyzer.resolve_site_package_root_paths()
        environment_roots = CrystalAnalyzer.resolve_environment_root_paths(site_roots)
        calls = CallCounts(monkeypatch)
        calls.watch(pathlib.Path, "resolve")

        user_again = CrystalAnalyzer.resolve_user_root_paths(None)
        site_again = CrystalAnalyzer.resolve_site_package_root_paths()
        environment_again = CrystalAnalyzer.resolve_environment_root_paths(site_roots)
        resolves_while_reused = calls.counts["resolve"]

        monkeypatch.chdir(second_directory)
        user_elsewhere = CrystalAnalyzer.resolve_user_root_paths(None)
        with pytest.raises(TypeError):
            CrystalAnalyzer.resolve_user_root_paths((1,))
    finally:
        _reset_analysis_caches()

    assert user_again == user_roots == (first_resolved,)
    assert site_again == site_roots
    assert environment_again == environment_roots
    assert resolves_while_reused == 0
    assert user_elsewhere == (second_resolved,)


def test_concurrent_analyses_of_one_world_record_the_same_result(answer_world: Path) -> None:
    """
    Contract: analyses running at once on several threads (the GIL off) share the cache safely and each records
    what a fresh single analysis records.
    """
    expected = _described(answer_world)
    _reset_analysis_caches()
    barrier = threading.Barrier(8)

    def analyze_once() -> Dict[str, Any]:
        """Wait for every thread, then analyze the world once and return its payload."""
        barrier.wait()
        return _described(answer_world)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(analyze_once) for _ in range(8)]
        results = [future.result(timeout=120) for future in futures]

    assert all(result == expected for result in results)
