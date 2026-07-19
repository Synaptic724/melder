"""Unit tests for the package version metadata contract (single-truth law)."""


def test_version_module_exposes_expected_base_version() -> None:
    """Pin the direct base version exported by the version metadata module."""
    from melder.__version__ import __version__

    assert __version__ == "0.1.0"


def test_package_version_is_the_single_truth_unmutated() -> None:
    """
    Purpose:
        Regression for the retired DEBUG_MODE lane: the package-level
        __version__ IS the metadata module's literal - no environment
        mutation, no dev suffix, one truth for runtime and build alike.
    Contract:
        melder.__version__ == melder.__version__.__version__ byte-equal.
    """
    import melder
    from melder.__version__ import __version__ as base_version

    assert melder.__version__ == base_version
def test_pep_561_marker_ships_beside_the_package() -> None:
    """
    Purpose:
        The codebase is exhaustively typed; without the py.typed marker a
        wheel throws that away (checkers see Any). Pin the marker's
        presence beside the package root.
    Contract:
        src/melder/py.typed exists next to melder.__init__.
    """
    from pathlib import Path

    import melder

    assert (Path(melder.__file__).parent / "py.typed").is_file()
