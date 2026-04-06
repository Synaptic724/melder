"""Unit tests for the package description metadata contract."""


def test_description_module_exposes_expected_description_string() -> None:
    """Pin the direct string exported by the description metadata module."""
    from melder.__description__ import __description__

    assert __description__ == (
        "Melder is a lightweight dependency injection system designed for "
        "high-performance modular Python systems like ThreadFactory."
    )


def test_package_description_reexport_matches_module_constant() -> None:
    """Ensure the package-level __description__ surface stays aligned."""
    import melder
    from melder.__description__ import __description__

    assert melder.__description__ == __description__
