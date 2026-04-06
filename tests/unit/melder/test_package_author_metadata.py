"""Unit tests for the package author metadata contract."""


def test_author_module_exposes_creator_and_github_constants() -> None:
    """Pin the direct constants exported by the author metadata module."""
    from melder.__author__ import CREATOR
    from melder.__author__ import GITHUB

    assert CREATOR == "Mark Geleta"
    assert GITHUB == "https://github.com/Synaptic724/"


def test_package_author_reexport_matches_creator_constant() -> None:
    """Ensure the package-level __author__ surface stays aligned to CREATOR."""
    import melder
    from melder.__author__ import CREATOR

    assert melder.__author__ == CREATOR
