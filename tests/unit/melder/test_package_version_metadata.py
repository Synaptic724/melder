"""Unit tests for the package version metadata contract (single-truth law)."""


def test_version_is_well_formed() -> None:
    """
    Purpose:
        This replaces a hardcoded `== "0.1.0"` pin. That assertion failed for a
        DELIBERATE release bump, which is precisely the shape the repo's own
        testing rule rejects: a test must fail for a real regression and NOT for
        a harmless change. Pinning a literal guarantees a red suite on every
        release forever, which trains people to edit the test rather than read
        it.
    Contract:
        The version is a non-empty dotted release string.
    """
    import re

    from melder.__version__ import __version__

    assert re.fullmatch(r"\d+\.\d+\.\d+(?:[.\-+].+)?", __version__), __version__


def test_generated_build_assets_are_stamped_for_the_live_version() -> None:
    """
    Purpose:
        THE contract the old literal pin was reaching for. Melder ships
        generated build assets whose `BUILT_FOR_VERSION` must track
        `__version__`, and one of them - the internal-bind manifest - IS the
        enforced registration policy read by `bind.py` at import. A version bump
        that leaves an asset stamped for the previous release means the shipped
        wheel enforces a stale class list, silently.

        This is not hypothetical: the manifest was found stamped 0.1.0 while the
        package read 0.1.1.
    Contract:
        Every generated asset's `BUILT_FOR_VERSION` equals `melder.__version__`.
        If this fails, regenerate:
            python src/melder/_build_assets/_build_asset_runner.py
    """
    import re
    from pathlib import Path

    import melder
    from melder.__version__ import __version__

    assets_root = Path(melder.__file__).parent / "_build_assets"
    stamped = {}
    for generated in sorted(assets_root.glob("*/*.py")):
        if generated.name == "_builder.py":
            continue
        match = re.search(
            r'^BUILT_FOR_VERSION:\s*str\s*=\s*"([^"]+)"',
            generated.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if match:
            stamped[generated.parent.name] = match.group(1)

    assert stamped, "no generated build assets carried a BUILT_FOR_VERSION stamp"
    drifted = {name: v for name, v in stamped.items() if v != __version__}
    assert not drifted, f"assets stamped for the wrong version: {drifted} (package is {__version__})"


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
