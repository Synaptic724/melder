"""
Unit tests for CrystalAnalyzer: end-to-end walks over real temp module
trees, retained-payload re-analysis (the MR seam), physical fingerprint
drift detection, and payload validation honesty.

Runs only on 3.14t (melder package root import chain).
"""
import sys

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
