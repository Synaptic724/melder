"""
Unit tests for distribution provenance (finishing slice 1): the
site-package harvest verb and the result channel it feeds.
"""
import pytest

from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy import (
    SitePackageCustodyStrategy,
)


def test_harvest_provenance_resolves_an_installed_distribution():
    """
    Contract:
        A module provided by a real installed distribution resolves to
        {distribution_name, distribution_version, all_distributions,
        top_level} - pytest itself is the deterministic fixture (this
        suite cannot run without it installed).
    """
    strategy = SitePackageCustodyStrategy(tuple())
    payload = strategy.harvest_provenance(
        module_name="pytest", module_path=None
    )
    assert payload is not None
    assert payload["distribution_name"] == "pytest"
    assert isinstance(payload["distribution_version"], str)
    assert "pytest" in payload["all_distributions"]
    assert payload["top_level"] == "pytest"
    strategy.cleanup()


def test_harvest_provenance_uses_the_top_level_name_for_submodules():
    """
    Contract:
        Resolution walks from the TOP-LEVEL name: a dotted submodule of
        an installed distribution resolves to the same distribution.
    """
    strategy = SitePackageCustodyStrategy(tuple())
    payload = strategy.harvest_provenance(
        module_name="pytest.somewhere.deep", module_path=None
    )
    assert payload is not None
    assert payload["distribution_name"] == "pytest"
    assert payload["top_level"] == "pytest"
    strategy.cleanup()


def test_harvest_provenance_unresolvable_is_honest_none():
    """
    Contract:
        A top-level that maps to no installed distribution (vendored
        tree, path-hacked import) returns None - never a guess, never
        an exception (provenance must not break a bind-time walk).
    """
    strategy = SitePackageCustodyStrategy(tuple())
    payload = strategy.harvest_provenance(
        module_name="zz_no_such_distribution_xyz.mod", module_path=None
    )
    assert payload is None
    strategy.cleanup()


def test_harvest_provenance_refuses_after_cleanup():
    """
    Contract:
        The verb enforces the live-object law: a cleaned strategy
        raises instead of answering from torn-down state.
    """
    strategy = SitePackageCustodyStrategy(tuple())
    strategy.cleanup()
    with pytest.raises(RuntimeError):
        strategy.harvest_provenance(module_name="pytest", module_path=None)


def test_result_channel_records_describes_and_detaches():
    """
    Contract:
        record_distribution_provenance lands the payload; the property
        and describe() both emit it under "distribution_provenance";
        emitted copies are detached (mutation never leaks back).
    """
    result = CrystalAnalysisResult()
    result.record_distribution_provenance(
        "requests",
        {"distribution_name": "requests", "distribution_version": "2.0"},
    )
    emitted = result.distribution_provenance
    assert emitted["requests"]["distribution_name"] == "requests"
    described = result.describe()
    assert described["distribution_provenance"]["requests"][
        "distribution_version"
    ] == "2.0"
    emitted["requests"]["distribution_name"] = "mutated"
    assert (
        result.distribution_provenance["requests"]["distribution_name"]
        == "requests"
    )
    result.cleanup()


# --- Walk-level contract tests: the whole chain, not unit crumbs -------

import pytest as pytest_module  # the deterministic installed-dist fixture

from pathlib import Path

from melder.crystallizer.crystal_analysis.crystal_analyzer import (
    CrystalAnalyzer,
)
from melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy import (
    BinaryUnknownCustodyStrategy,
)


def test_walk_records_provenance_and_refold_keeps_parity(tmp_path):
    """
    Contract (the whole slice-1 chain in one walk):
        A real tmp module that imports a REAL installed site-package
        module (pytest, rooted deterministically via its actual parent
        directory - no path-text luck) walks to: (a) site_package
        classification, (b) an always-on provenance row naming the
        pytest distribution and its installed version, (c) a describe()
        payload carrying the row, and (d) analyze_payload REFOLD parity
        - the MR re-analysis seam sees byte-equal provenance with no
        live modules present.
    """
    package_dir = tmp_path / "provpkg"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "rootmod.py").write_text(
        "import pytest\n\nclass Root:\n    pass\n", encoding="utf-8"
    )
    site_root = Path(pytest_module.__file__).resolve().parent.parent
    analyzer = CrystalAnalyzer(
        user_source_root_paths=(tmp_path.resolve(),),
        site_package_root_paths=(site_root,),
    )
    try:
        result = analyzer.analyze_spell_root(
            root_module_name="provpkg.rootmod",
            root_module_obj=None,
            root_module_path=package_dir / "rootmod.py",
        )
        provenance = result.distribution_provenance
        assert "pytest" in provenance, provenance
        row = provenance["pytest"]
        assert row["distribution_name"] == "pytest"
        assert row["distribution_version"] == pytest_module.__version__
        # Refold parity: a historical payload re-derives the SAME rows.
        payload = result.describe()
        refolded = analyzer.analyze_payload(payload)
        try:
            assert refolded.distribution_provenance == provenance
        finally:
            refolded.cleanup()
        result.cleanup()
    finally:
        analyzer.cleanup()


def test_binary_identity_hashes_real_bytes_and_scopes_by_extension(
        tmp_path,
):
    """
    Contract (slice 2, against real file bytes):
        A .pyd leaf yields {binary_path, binary_sha256, top_level} with
        the sha256 of the ACTUAL bytes (verified independently via
        hashlib); a .py path and a pathless module yield None (the
        honest-leaf law untouched for everything non-binary); a
        vanished file still yields its path identity with sha None
        (the path IS identity; half-answer beats silence).
    """
    import hashlib

    binary_path = tmp_path / "native_ext.pyd"
    binary_bytes = b"\x7fELFfake-native-bytes\x00\x01\x02"
    binary_path.write_bytes(binary_bytes)
    strategy = BinaryUnknownCustodyStrategy()
    payload = strategy.harvest_binary_identity(
        module_name="native_ext.sub", module_path=binary_path
    )
    assert payload is not None
    assert payload["binary_sha256"] == hashlib.sha256(
        binary_bytes
    ).hexdigest()
    assert payload["top_level"] == "native_ext"
    assert payload["binary_path"].endswith("native_ext.pyd")

    plain_py = tmp_path / "plain.py"
    plain_py.write_text("x = 1\n", encoding="utf-8")
    assert strategy.harvest_binary_identity(
        module_name="plain", module_path=plain_py
    ) is None
    assert strategy.harvest_binary_identity(
        module_name="ghost", module_path=None
    ) is None

    vanished = tmp_path / "gone.so"
    vanished.write_bytes(b"x")
    vanished.unlink()
    ghost_payload = strategy.harvest_binary_identity(
        module_name="gone", module_path=vanished
    )
    assert ghost_payload is not None
    assert ghost_payload["binary_sha256"] is None
    strategy.cleanup()
