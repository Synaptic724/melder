"""Unit tests for the package version metadata contract."""


def test_version_module_exposes_expected_base_version() -> None:
    """Pin the direct base version exported by the version metadata module."""
    from melder.__version__ import __version__

    assert __version__ == "0.1.0"


def test_package_version_reexport_appends_dev_suffix() -> None:
    """Ensure the package-level __version__ remains derived from the base version."""
    import melder
    from melder.__version__ import __version__ as base_version

    assert melder.__version__ == base_version + "-dev"
