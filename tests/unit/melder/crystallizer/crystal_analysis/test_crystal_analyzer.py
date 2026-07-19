"""
Unit tests for CrystalAnalyzer: end-to-end walks over real temp module
trees, retained-payload re-analysis (the MR seam), physical fingerprint
drift detection, and payload validation honesty.

Runs only on 3.14t (melder package root import chain).
"""
import importlib
import sys
from pathlib import Path

import pytest

from melder.crystallizer.crystal_analysis.crystal_analyzer import (
    CrystalAnalyzer,
)


def _build_package(tmp_path, package_name):
    """
    Write one small importable package: root module depends on helper.
    """
    package_dir = tmp_path / package_name
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "helper.py").write_text(
        "__all__ = [\"Helper\"]\n"
        "class Helper:\n"
        "    pass\n",
        encoding="utf-8",
    )
    (package_dir / "rootmod.py").write_text(
        "from {0} import helper\n"
        "class Root:\n"
        "    pass\n".format(package_name),
        encoding="utf-8",
    )
    return package_dir


def _analyze(tmp_path, package_name):
    """
    Analyze the package's root module from disk truth (no live objects).
    """
    analyzer = CrystalAnalyzer(
        user_source_root_paths=(tmp_path.resolve(),),
        site_package_root_paths=(),
    )
    try:
        return analyzer.analyze_spell_root(
            root_module_name="{0}.rootmod".format(package_name),
            root_module_obj=None,
            root_module_path=tmp_path / package_name / "rootmod.py",
        )
    finally:
        analyzer.cleanup()


def test_analyze_spell_root_walks_and_classifies_a_real_module_tree(
        tmp_path, monkeypatch,
):
    """
    Contract: the walk discovers the helper dependency through the
    from-import, classifies the tree as user_source under the configured
    root, and records dependency edges for the root module.
    """
    package_name = "t7walkpkg"
    _build_package(tmp_path, package_name)
    monkeypatch.syspath_prepend(str(tmp_path))
    for module_name in list(sys.modules):
        assert not module_name.startswith(package_name)

    result = _analyze(tmp_path, package_name)
    try:
        root_name = "{0}.rootmod".format(package_name)
        helper_name = "{0}.helper".format(package_name)
        assert root_name in result.module_targets
        assert helper_name in result.module_targets
        assert result.module_to_kind[root_name] == "user_source"
        assert result.module_to_kind[helper_name] == "user_source"
        assert helper_name in result.module_to_direct_dependencies[root_name]
        assert result.root_module_kind == "user_source"
    finally:
        result.cleanup()


def test_analyzer_records_fingerprints_exports_and_load_order(
        tmp_path, monkeypatch,
):
    """
    Contract: the S1 capabilities ride every analysis - user_source
    fingerprints for walked modules, static export surfaces, and a
    topological load order placing the helper before the root.
    """
    package_name = "t7factpkg"
    _build_package(tmp_path, package_name)
    monkeypatch.syspath_prepend(str(tmp_path))

    result = _analyze(tmp_path, package_name)
    try:
        root_name = "{0}.rootmod".format(package_name)
        helper_name = "{0}.helper".format(package_name)
        fingerprints = result.physical_module_fingerprints
        assert root_name in fingerprints
        assert helper_name in fingerprints
        assert len(fingerprints[root_name]) == 64

        helper_surface = result.export_surfaces[helper_name]
        assert helper_surface["all_declared"] == ["Helper"]
        root_surface = result.export_surfaces[root_name]
        assert "Root" in root_surface["public_names"]

        load_order = result.module_load_order
        assert load_order.index(helper_name) < load_order.index(root_name)
    finally:
        result.cleanup()


def test_analyze_payload_rebuilds_a_result_without_a_live_spell(
        tmp_path, monkeypatch,
):
    """
    Contract (the MR seam): a retained payload rebuilds into a queryable
    result - recorded truths copy through verbatim and the load order is
    RECOMPUTED from the recorded edges, with no live objects involved.
    """
    package_name = "t7payloadpkg"
    _build_package(tmp_path, package_name)
    monkeypatch.syspath_prepend(str(tmp_path))

    original = _analyze(tmp_path, package_name)
    try:
        retained_payload = original.describe()
    finally:
        original.cleanup()

    analyzer = CrystalAnalyzer(
        user_source_root_paths=(tmp_path.resolve(),),
        site_package_root_paths=(),
    )
    try:
        rebuilt = analyzer.analyze_payload(retained_payload)
    finally:
        analyzer.cleanup()
    try:
        assert rebuilt.module_targets == retained_payload["module_targets"]
        assert rebuilt.module_to_kind == retained_payload["module_to_kind"]
        assert (
            rebuilt.physical_module_fingerprints
            == retained_payload["physical_module_fingerprints"]
        )
        assert rebuilt.export_surfaces == retained_payload["export_surfaces"]
        assert (
            rebuilt.module_load_order
            == retained_payload["module_load_order"]
        )
    finally:
        rebuilt.cleanup()


def test_analyze_payload_refuses_malformed_payloads_with_guidance():
    """
    Contract: payloads missing the minimum manifest keys refuse with a
    teach-grade ValueError naming the missing key.
    """
    analyzer = CrystalAnalyzer(
        user_source_root_paths=(),
        site_package_root_paths=(),
    )
    try:
        try:
            analyzer.analyze_payload({"module_targets": []})
            raised = False
        except ValueError as exc:
            raised = True
            assert "module_to_direct_dependencies" in str(exc)
        assert raised
    finally:
        analyzer.cleanup()


def test_physical_fingerprint_detects_on_disk_drift_between_analyses(
        tmp_path, monkeypatch,
):
    """
    Regression (drift symptom): the same module analyzed before and after
    an on-disk edit yields DIFFERENT SHA256 fingerprints - the silent-
    drift blind spot the pre-decomposition analyzer had is closed.
    """
    package_name = "t7driftpkg"
    package_dir = _build_package(tmp_path, package_name)
    monkeypatch.syspath_prepend(str(tmp_path))
    helper_name = "{0}.helper".format(package_name)

    before = _analyze(tmp_path, package_name)
    try:
        fingerprint_before = before.physical_module_fingerprints[helper_name]
    finally:
        before.cleanup()

    (package_dir / "helper.py").write_text(
        "__all__ = [\"Helper\"]\n"
        "class Helper:\n"
        "    changed = True\n",
        encoding="utf-8",
    )

    after = _analyze(tmp_path, package_name)
    try:
        fingerprint_after = after.physical_module_fingerprints[helper_name]
    finally:
        after.cleanup()

    assert fingerprint_before != fingerprint_after


def test_unresolvable_imports_stay_honest_unknown_leaves(tmp_path):
    """
    Contract: an import that resolves nowhere classifies as an unknown
    leaf - recorded in the manifest, never walked, never guessed.
    """
    module_file = tmp_path / "loner.py"
    module_file.write_text(
        "import definitely_not_a_real_module_xyz\n",
        encoding="utf-8",
    )
    analyzer = CrystalAnalyzer(
        user_source_root_paths=(tmp_path.resolve(),),
        site_package_root_paths=(),
    )
    try:
        result = analyzer.analyze_spell_root(
            root_module_name="loner",
            root_module_obj=None,
            root_module_path=module_file,
        )
    finally:
        analyzer.cleanup()
    try:
        assert "definitely_not_a_real_module_xyz" in result.unknown_targets
        # Honest leaf: recorded with NO dependency edges of its own.
        assert result.module_to_direct_dependencies[
            "definitely_not_a_real_module_xyz"
        ] == []
        assert result.module_to_kind[
            "definitely_not_a_real_module_xyz"
        ] == "unknown"
    finally:
        result.cleanup()


def _assert_memo_value_only(value: object) -> None:
    """
    Assert recursively that a memoized value cannot retain runtime objects.

    Args:
        value:
            Cache key or fact payload being inspected.

    Returns:
        None.

    Raises:
        AssertionError:
            If the value is not None, an integer, a string, or a tuple made
            exclusively from those value types.
    """
    if value is None or isinstance(value, (int, str)):
        return
    assert isinstance(value, tuple)
    for item in value:
        _assert_memo_value_only(item)


def test_memoized_facts_survive_analyzer_cleanup_and_preserve_payload_order(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Regression: repeated analyses reuse syntax facts after the first analyzer
    is cleaned while producing an identical, independently owned payload.
    """
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    package_name = "t7memoorderpkg"
    package_dir = _build_package(tmp_path, package_name)
    root_name = "{0}.rootmod".format(package_name)
    missing_a = "t7memo_missing_a"
    missing_b = "t7memo_missing_b"
    (package_dir / "rootmod.py").write_text(
        "import {0}\n"
        "from {1} import helper\n"
        "def delayed():\n"
        "    import {2}\n"
        "class Root:\n"
        "    pass\n".format(missing_a, package_name, missing_b),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    try:
        first = _analyze(tmp_path, package_name)
        try:
            first_payload = first.describe()
            assert first.module_to_direct_dependencies[root_name] == [
                missing_a,
                "{0}.helper".format(package_name),
                package_name,
                missing_b,
            ]
        finally:
            first.cleanup()
        cold_stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()
        assert cold_stats["misses"] > 0
        assert cold_stats["hits"] == 0

        second = _analyze(tmp_path, package_name)
        try:
            assert second.describe() == first_payload
        finally:
            second.cleanup()
        warm_stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()
        assert warm_stats["misses"] == cold_stats["misses"]
        assert warm_stats["hits"] == cold_stats["misses"]
    finally:
        CrystalAnalyzer._clear_memoized_module_facts_for_tests()


def test_source_edit_invalidates_only_changed_memoized_module_facts(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Regression: changing one dependency source misses that entry while
    unchanged modules continue to reuse their memoized syntax facts.
    """
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    package_name = "t7memodriftpkg"
    package_dir = _build_package(tmp_path, package_name)
    helper_name = "{0}.helper".format(package_name)
    monkeypatch.syspath_prepend(str(tmp_path))

    try:
        before = _analyze(tmp_path, package_name)
        try:
            assert "Helper" in before.export_surfaces[helper_name]["public_names"]
        finally:
            before.cleanup()
        cold_stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()

        (package_dir / "helper.py").write_text(
            "__all__ = [\"Changed\"]\n"
            "class Changed:\n"
            "    pass\n",
            encoding="utf-8",
        )
        after = _analyze(tmp_path, package_name)
        try:
            assert "Changed" in after.export_surfaces[helper_name]["public_names"]
            assert "Helper" not in after.export_surfaces[helper_name]["public_names"]
        finally:
            after.cleanup()

        drift_stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()
        assert drift_stats["misses"] == cold_stats["misses"] + 1
        assert drift_stats["hits"] >= 1
    finally:
        CrystalAnalyzer._clear_memoized_module_facts_for_tests()


def test_from_import_submodule_probe_remains_live_on_memo_hit(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Regression: a cached from-import descriptor reruns find_spec, allowing a
    newly created submodule to enter the current dependency graph.
    """
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    package_name = "t7memoprobepkg"
    package_dir = tmp_path / package_name
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "rootmod.py").write_text(
        "from {0} import maybe_child\n".format(package_name),
        encoding="utf-8",
    )
    root_name = "{0}.rootmod".format(package_name)
    child_name = "{0}.maybe_child".format(package_name)
    monkeypatch.syspath_prepend(str(tmp_path))

    try:
        before = _analyze(tmp_path, package_name)
        try:
            assert child_name not in before.module_to_direct_dependencies[root_name]
        finally:
            before.cleanup()
        cold_stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()

        (package_dir / "maybe_child.py").write_text(
            "VALUE = 1\n",
            encoding="utf-8",
        )
        importlib.invalidate_caches()

        after = _analyze(tmp_path, package_name)
        try:
            assert child_name in after.module_to_direct_dependencies[root_name]
        finally:
            after.cleanup()
        warm_stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()
        assert warm_stats["hits"] > cold_stats["hits"]
    finally:
        CrystalAnalyzer._clear_memoized_module_facts_for_tests()


def test_memoized_facts_contain_values_only(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: cache entries contain no modules, AST nodes, source text,
    functions, classes, paths, crystals, results, or other runtime objects.
    """
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    package_name = "t7memovaluepkg"
    _build_package(tmp_path, package_name)
    monkeypatch.syspath_prepend(str(tmp_path))

    try:
        result = _analyze(tmp_path, package_name)
        result.cleanup()
        with CrystalAnalyzer._memoized_module_fact_lock:
            cached_items = tuple(
                CrystalAnalyzer._memoized_module_facts.items()
            )
        assert cached_items
        for key, facts in cached_items:
            _assert_memo_value_only(key)
            _assert_memo_value_only(facts)
    finally:
        CrystalAnalyzer._clear_memoized_module_facts_for_tests()


def test_custom_fact_strategies_bypass_default_syntax_memo(
        tmp_path: Path,
) -> None:
    """
    Contract: explicitly supplied fact strategies keep their historical live
    AST path and never publish assumptions into the default-strategy memo.
    """
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    module_file = tmp_path / "custom_fact_module.py"
    module_file.write_text("VALUE = 1\n", encoding="utf-8")
    analyzer = CrystalAnalyzer(
        user_source_root_paths=(tmp_path.resolve(),),
        site_package_root_paths=(),
        fact_strategies=(),
    )
    try:
        result = analyzer.analyze_spell_root(
            root_module_name="custom_fact_module",
            root_module_obj=None,
            root_module_path=module_file,
        )
    finally:
        analyzer.cleanup()
    result.cleanup()

    stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()
    assert stats == {
        "size": 0,
        "capacity": CrystalAnalyzer._MAX_MEMOIZED_MODULE_FACTS,
        "hits": 0,
        "misses": 0,
    }


def test_memoized_fact_cache_evicts_least_recently_used_values(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: the shared memo remains bounded and evicts value entries without
    interacting with analyzed modules or their results.
    """
    monkeypatch.setattr(CrystalAnalyzer, "_MAX_MEMOIZED_MODULE_FACTS", 2)
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    try:
        for index in range(3):
            module_name = "bounded_memo_{0}".format(index)
            module_file = tmp_path / "{0}.py".format(module_name)
            module_file.write_text(
                "VALUE_{0} = {0}\n".format(index),
                encoding="utf-8",
            )
            analyzer = CrystalAnalyzer(
                user_source_root_paths=(tmp_path.resolve(),),
                site_package_root_paths=(),
            )
            try:
                result = analyzer.analyze_spell_root(
                    root_module_name=module_name,
                    root_module_obj=None,
                    root_module_path=module_file,
                )
            finally:
                analyzer.cleanup()
            result.cleanup()

        stats = CrystalAnalyzer._memoized_module_fact_stats_for_tests()
        assert stats["size"] == 2
        assert stats["capacity"] == 2
        assert stats["misses"] == 3
    finally:
        CrystalAnalyzer._clear_memoized_module_facts_for_tests()
def test_second_analysis_of_an_unchanged_tree_reads_zero_files(
        tmp_path, monkeypatch,
):
    """
    Purpose:
        The IO-economy law (2026-07-19): the first analysis pays the
        reads; a second analysis of the SAME unchanged tree serves every
        module from the stat guard + syntax memo with ZERO file reads.
    Contract:
        Fingerprint maps are identical across the two passes (parity),
        and the second pass performs no read_text calls.
    """
    from melder.crystallizer.crystal_analysis.physical_source_cache import (
        PhysicalSourceCache,
    )
    from melder.crystallizer.crystal_analysis.crystal_analyzer import (
        CrystalAnalyzer,
    )

    PhysicalSourceCache._clear_for_tests()
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()
    _build_package(tmp_path, "iopkg")
    monkeypatch.syspath_prepend(str(tmp_path))
    first = _analyze(tmp_path, "iopkg")
    first_prints = dict(first.physical_module_fingerprints)
    assert "iopkg.helper" in first_prints

    read_calls = []
    original_read_text = Path.read_text

    def _counting_read_text(self, *args, **kwargs):
        read_calls.append(str(self))
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _counting_read_text)
    second = _analyze(tmp_path, "iopkg")
    source_reads = [
        entry for entry in read_calls if entry.endswith(".py")
    ]
    assert source_reads == []
    assert dict(second.physical_module_fingerprints) == first_prints
    first.cleanup()
    second.cleanup()
    PhysicalSourceCache._clear_for_tests()
    CrystalAnalyzer._clear_memoized_module_facts_for_tests()


def test_changed_file_between_analyses_re_fingerprints(
        tmp_path, monkeypatch,
):
    """
    Purpose:
        The cache must never mask a real edit: changing one module
        between analyses re-reads it and records the NEW fingerprint.
    Contract:
        The changed module's fingerprint differs; untouched modules keep
        their first-pass values.
    """
    from melder.crystallizer.crystal_analysis.physical_source_cache import (
        PhysicalSourceCache,
    )

    PhysicalSourceCache._clear_for_tests()
    package_dir = _build_package(tmp_path, "driftpkg")
    monkeypatch.syspath_prepend(str(tmp_path))
    first = _analyze(tmp_path, "driftpkg")
    first_prints = dict(first.physical_module_fingerprints)
    assert "driftpkg.helper" in first_prints
    (package_dir / "helper.py").write_text(
        "__all__ = [\"Helper\"]\n"
        "class Helper:\n"
        "    CHANGED = True\n",
        encoding="utf-8",
    )
    second = _analyze(tmp_path, "driftpkg")
    second_prints = dict(second.physical_module_fingerprints)
    helper_name = "driftpkg.helper"
    root_name = "driftpkg.rootmod"
    assert second_prints[helper_name] != first_prints[helper_name]
    assert second_prints[root_name] == first_prints[root_name]
    first.cleanup()
    second.cleanup()
    PhysicalSourceCache._clear_for_tests()


def _build_site_world(tmp_path):
    """
    Build one user root module importing one fake installed package whose
    interior imports a deeper module (the descent probe shape).
    """
    site_root = tmp_path / "siteroot"
    site_pkg = site_root / "fakedist"
    site_pkg.mkdir(parents=True)
    (site_pkg / "__init__.py").write_text(
        "from fakedist import interior\n", encoding="utf-8"
    )
    (site_pkg / "interior.py").write_text(
        "DEEP = True\n", encoding="utf-8"
    )
    user_root = tmp_path / "userroot"
    user_root.mkdir()
    (user_root / "consumer.py").write_text(
        "import fakedist\n"
        "class Consumer:\n"
        "    pass\n",
        encoding="utf-8",
    )
    return user_root, site_root


def _analyze_site_world(user_root, site_root, descend):
    """
    Analyze the consumer root with an explicit descent posture.
    """
    from melder.crystallizer.crystal_analysis.crystal_analyzer import (
        CrystalAnalyzer,
    )

    analyzer = CrystalAnalyzer(
        user_source_root_paths=(user_root.resolve(),),
        site_package_root_paths=(site_root.resolve(),),
        site_package_dependency_descent=descend,
    )
    try:
        return analyzer.analyze_spell_root(
            root_module_name="consumer",
            root_module_obj=None,
            root_module_path=user_root / "consumer.py",
        )
    finally:
        analyzer.cleanup()


def test_descent_off_records_site_packages_as_leaves(
        tmp_path, monkeypatch,
):
    """
    Purpose:
        The descent policy (config default False): installed third-party
        modules record as leaves - present in the module inventory, no
        interior dependencies walked, no fingerprint claim.
    Contract:
        fakedist records with empty deps; fakedist.interior never enters
        the inventory; no site module is fingerprinted.
    """
    import sys

    user_root, site_root = _build_site_world(tmp_path)
    monkeypatch.syspath_prepend(str(site_root))
    sys.modules.pop("fakedist", None)
    sys.modules.pop("fakedist.interior", None)
    result = _analyze_site_world(user_root, site_root, descend=False)
    kinds = dict(result.module_to_kind)
    assert kinds.get("fakedist") == "site_package"
    deps = dict(result.module_to_direct_dependencies)
    assert deps.get("fakedist") == []
    assert "fakedist.interior" not in kinds
    prints = dict(result.physical_module_fingerprints)
    assert "fakedist" not in prints
    assert "consumer" in prints
    result.cleanup()


def test_descent_on_walks_the_site_package_interior(
        tmp_path, monkeypatch,
):
    """
    Purpose:
        The reversibility guarantee: descent True restores the interior
        walk wholesale (raw-analyzer default stays byte-compatible).
    Contract:
        fakedist records real deps and fakedist.interior joins the
        inventory - still without fingerprint claims (S1 law).
    """
    import sys

    user_root, site_root = _build_site_world(tmp_path)
    monkeypatch.syspath_prepend(str(site_root))
    sys.modules.pop("fakedist", None)
    sys.modules.pop("fakedist.interior", None)
    result = _analyze_site_world(user_root, site_root, descend=True)
    kinds = dict(result.module_to_kind)
    assert kinds.get("fakedist") == "site_package"
    assert kinds.get("fakedist.interior") == "site_package"
    prints = dict(result.physical_module_fingerprints)
    assert "fakedist" not in prints and "fakedist.interior" not in prints
    result.cleanup()
