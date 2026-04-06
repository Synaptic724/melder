"""Unit tests for the package license metadata contract."""


def test_license_module_exposes_expected_license_string() -> None:
    """Pin the direct string exported by the license metadata module."""
    from melder.__license__ import __license__

    assert __license__ == "Apache 2.0"


def test_package_license_reexport_matches_module_constant() -> None:
    """Ensure the package-level __license__ surface stays aligned."""
    import melder
    from melder.__license__ import __license__

    assert melder.__license__ == __license__
