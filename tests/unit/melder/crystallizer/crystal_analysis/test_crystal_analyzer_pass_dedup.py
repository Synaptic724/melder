"""
Unit tests for one CrystalAnalyzer pass asking each module question once (#327, fix B).

Purpose:
    Pin that one `analyze_spell_root` pass resolves each distinct module's path once and runs the custody chain
    once per distinct module, however many modules import it, and - since the owner's decision of 2026-11-17
    (#331) - that a later pass over the unchanged world reuses those answers instead of asking again. Also pin the
    environment roots the analyzer hands to user-source custody (fix A).

Runs only on 3.14t (melder package root import chain).
"""
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Optional, Tuple

import pytest

from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.crystal_analyzer import CrystalAnalyzer
from melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy import (
    SyntheticCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.module_answer_cache import ModuleAnswerCache


class FanInNames:
    """
    Module names of the fan-in world, unique to this file.

    Contract:
        - `ROOT` imports every branch and `SHARED`; every branch imports `SHARED`, so `SHARED` has four importers.
        - All are top-level modules: resolving one never imports a package, so every import edge sees the same
          module object (None, nothing is imported) for a given name.
    """

    ROOT: str = "p327_fanin_root"
    BRANCHES: Tuple[str, ...] = ("p327_fanin_a", "p327_fanin_b", "p327_fanin_c")
    SHARED: str = "p327_fanin_shared"

    @staticmethod
    def all_names() -> Tuple[str, ...]:
        """
        Return every module name the fan-in world writes.

        Returns:
            Tuple[str, ...]: Names to evict from `sys.modules` around each test.
        """
        return (FanInNames.ROOT, FanInNames.SHARED) + FanInNames.BRANCHES

    @staticmethod
    def imported_names() -> Tuple[str, ...]:
        """
        Return the names some module of the world imports (every name but the root).

        Returns:
            Tuple[str, ...]: The branches and the shared module.
        """
        return FanInNames.BRANCHES + (FanInNames.SHARED,)


@pytest.fixture()
def fan_in_world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """
    Write the fan-in world on disk and put it on `sys.path` for the test only.

    Yields:
        Path: The resolved directory holding the world, used as the user source root.
    """
    shared_import = "import {0}\n".format(FanInNames.SHARED)
    for branch in FanInNames.BRANCHES:
        (tmp_path / "{0}.py".format(branch)).write_text(shared_import, encoding="utf-8")
    (tmp_path / "{0}.py".format(FanInNames.SHARED)).write_text("VALUE = 1\n", encoding="utf-8")
    root_source = "".join("import {0}\n".format(branch) for branch in FanInNames.BRANCHES) + shared_import
    (tmp_path / "{0}.py".format(FanInNames.ROOT)).write_text(root_source, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in FanInNames.all_names():
        sys.modules.pop(module_name, None)
    ModuleAnswerCache._clear_for_tests()
    yield tmp_path.resolve()
    for module_name in FanInNames.all_names():
        sys.modules.pop(module_name, None)
    ModuleAnswerCache._clear_for_tests()


@pytest.fixture()
def resolve_counts(monkeypatch: pytest.MonkeyPatch) -> Counter:
    """
    Count `CrystalAnalyzer.resolve_module_path` calls per module name, delegating to the real resolver.

    Returns:
        Counter: Calls per module name, filled while the test runs.
    """
    counts: Counter = Counter()
    original = CrystalAnalyzer.resolve_module_path

    def counting_resolve(module_name: str, module_obj: Optional[Any]) -> Optional[Path]:
        """Record one resolution of `module_name`, then resolve it for real."""
        counts[module_name] += 1
        return original(module_name, module_obj)

    monkeypatch.setattr(CrystalAnalyzer, "resolve_module_path", staticmethod(counting_resolve))
    return counts


@pytest.fixture()
def custody_counts(monkeypatch: pytest.MonkeyPatch) -> Counter:
    """
    Count custody-chain runs per module name through the chain's first strategy, which every run consults.

    Returns:
        Counter: Synthetic-custody `matches` calls per module name, filled while the test runs.
    """
    counts: Counter = Counter()
    original = SyntheticCustodyStrategy.matches

    def counting_matches(
            self: SyntheticCustodyStrategy,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> bool:
        """Record one custody question about `module_name`, then answer it for real."""
        counts[module_name] += 1
        return original(self, module_name=module_name, module_obj=module_obj, module_path=module_path)

    monkeypatch.setattr(SyntheticCustodyStrategy, "matches", counting_matches)
    return counts


def _new_analyzer(world: Path) -> CrystalAnalyzer:
    """
    Build an analyzer whose only user root is the fan-in world.

    Args:
        world: The resolved world directory.

    Returns:
        CrystalAnalyzer: A fresh analyzer; the caller cleans it.
    """
    return CrystalAnalyzer(user_source_root_paths=(world,), site_package_root_paths=())


def _analyze(analyzer: CrystalAnalyzer, world: Path) -> CrystalAnalysisResult:
    """
    Run one pass over the fan-in world from its root module, from disk truth.

    Args:
        analyzer: The analyzer to run.
        world: The resolved world directory.

    Returns:
        CrystalAnalysisResult: The pass's result; the caller cleans it.
    """
    return analyzer.analyze_spell_root(
        root_module_name=FanInNames.ROOT,
        root_module_obj=None,
        root_module_path=world / "{0}.py".format(FanInNames.ROOT),
    )


def test_one_pass_resolves_each_imported_module_once_however_many_modules_import_it(
        fan_in_world: Path,
        resolve_counts: Counter,
) -> None:
    """
    Contract: within one pass the shared module, imported from four places, has its path resolved once, and so
    does every branch - the per-edge repetition #327 measured is gone.
    """
    analyzer = _new_analyzer(fan_in_world)
    try:
        result = _analyze(analyzer, fan_in_world)
    finally:
        analyzer.cleanup()
    try:
        assert dict(resolve_counts) == {name: 1 for name in FanInNames.imported_names()}
    finally:
        result.cleanup()


def test_one_pass_runs_the_custody_chain_once_per_module(
        fan_in_world: Path,
        custody_counts: Counter,
) -> None:
    """
    Contract: within one pass every module is classified once - the root (asked for its kind and again by the
    walk) and the shared module (asked by four importers and by its own walk step) included.
    """
    analyzer = _new_analyzer(fan_in_world)
    try:
        result = _analyze(analyzer, fan_in_world)
    finally:
        analyzer.cleanup()
    try:
        assert dict(custody_counts) == {name: 1 for name in FanInNames.all_names()}
    finally:
        result.cleanup()


def test_one_pass_still_records_every_import_edge_and_fingerprint(fan_in_world: Path) -> None:
    """
    Contract: asking once per module changes nothing in the result - every importer keeps its edge to the shared
    module in import order, every module is user source, and every module is fingerprinted.
    """
    analyzer = _new_analyzer(fan_in_world)
    try:
        result = _analyze(analyzer, fan_in_world)
    finally:
        analyzer.cleanup()
    try:
        dependencies = dict(result.module_to_direct_dependencies)
        assert dependencies[FanInNames.ROOT] == list(FanInNames.imported_names())
        for branch in FanInNames.BRANCHES:
            assert dependencies[branch] == [FanInNames.SHARED]
        assert dependencies[FanInNames.SHARED] == []
        assert set(result.module_to_kind.values()) == {"user_source"}
        assert set(result.physical_module_fingerprints) == set(FanInNames.all_names())
    finally:
        result.cleanup()


def test_a_new_analysis_of_an_unchanged_world_reuses_the_whole_world(
        fan_in_world: Path,
        resolve_counts: Counter,
        custody_counts: Counter,
) -> None:
    """
    Contract (owner decisions 2026-11-17, #331; they replace "nothing is kept between analyses"): a second analyzer
    over the unchanged world copies the first analysis's result - its modules are not imported, so their files'
    stats and `sys.path` are re-checked - and asks no module question at all: no path and no custody chain.
    """
    payloads = []
    for _ in range(2):
        analyzer = _new_analyzer(fan_in_world)
        try:
            result = _analyze(analyzer, fan_in_world)
        finally:
            analyzer.cleanup()
        payloads.append(result.describe())
        result.cleanup()
    assert resolve_counts[FanInNames.SHARED] == 1
    assert dict(custody_counts) == {name: 1 for name in FanInNames.all_names()}
    assert payloads[1] == payloads[0]


def test_a_reused_analyzer_reuses_its_earlier_answers_on_the_next_pass(
        fan_in_world: Path,
        custody_counts: Counter,
) -> None:
    """
    Contract (#331): when one analyzer runs two passes (single use is a convention), the second pass empties its
    per-pass answers as before yet classifies nothing again - the kinds come from the first pass - and records the
    same edges.
    """
    analyzer = _new_analyzer(fan_in_world)
    try:
        first = _analyze(analyzer, fan_in_world)
        second = _analyze(analyzer, fan_in_world)
    finally:
        analyzer.cleanup()
    try:
        assert custody_counts[FanInNames.SHARED] == 1
        assert dict(second.module_to_direct_dependencies) == dict(first.module_to_direct_dependencies)
    finally:
        first.cleanup()
        second.cleanup()


def test_environment_roots_are_the_site_roots_then_the_interpreter_prefixes(tmp_path: Path) -> None:
    """
    Contract (#327 fix A): the roots that are never user source are the given site roots, in order, followed by
    the running interpreter's `sys.prefix`, `sys.base_prefix` and `sys.exec_prefix`, resolved and without
    duplicates.
    """
    site_root = (tmp_path / "site").resolve()

    roots = CrystalAnalyzer.resolve_environment_root_paths((site_root, site_root))

    assert roots[0] == site_root
    for prefix in (sys.prefix, sys.base_prefix, sys.exec_prefix):
        assert Path(prefix).resolve() in roots
    assert len(roots) == len(set(roots))
