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
