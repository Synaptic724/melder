"""
Characterization tests for the Crystallizer's custody boundary (core-protection review, 2026-10-10).

Purpose:
    Pin how the analyzer decides which modules are the user's own source and which are installed
    packages, and how far it walks into each. The review left one question open on root precedence (is a
    virtual environment inside the user root meant to count as user source?); the owner answered it on
    2026-11-16 (#327): the environment wins. These tests moved to that answer on purpose.

Contract pinned here:
    - An environment nested inside a user root is never user source: its installed package classifies as
      a site package, is never fingerprinted, and is walked into only when descent is on - the same as
      when the user root excludes the environment.
    - Retained user source text follows the classification, so no installed package's text is retained.
    - User roots classify modules; they never make a module importable.
    - `CrystallizerConfiguration.with_defaults()` takes the working directory as the user root and
      turns descent off; run from a project with a `.venv` inside it, the environment stays a site
      package.

Runs only on 3.14t (melder package root import chain).
"""
import sys
from pathlib import Path
from typing import Iterator, Tuple

import pytest

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.crystal_analyzer import CrystalAnalyzer


class CustodyNames:
    """
    Module names used by the scratch project, unique to this file.

    Contract:
        - `APP` is the project's own module under `src/`; it imports `PACKAGE`.
        - `PACKAGE` is installed in the project's `.venv` site-packages and imports `DEPENDENCY` from
          the same site-packages.
        - The names are distinct from every other test module so `sys.modules` and the analyzer memo
          never see them from another test.
    """

    APP: str = "cpb_custody_app"
    PACKAGE: str = "cpb_custody_venv_pkg"
    DEPENDENCY: str = "cpb_custody_venv_dep"
    HIDDEN: str = "cpb_custody_hidden"
    HIDDEN_CONSUMER: str = "cpb_custody_hidden_consumer"

    @staticmethod
    def all_names() -> Tuple[str, ...]:
        """
        Return every module name the scratch projects create.

        Returns:
            Tuple[str, ...]: Names to evict from `sys.modules` around each test.
        """
        return (
            CustodyNames.APP,
            CustodyNames.PACKAGE,
            CustodyNames.DEPENDENCY,
            CustodyNames.HIDDEN,
            CustodyNames.HIDDEN_CONSUMER,
        )


@pytest.fixture()
def nested_venv_project(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Tuple[Path, Path, Path]]:
    """
    Build a project whose virtual environment sits inside the project directory.

    Purpose:
        Reproduce the layout of a checkout with a local `.venv` at its root, without pip: the
        installed package is two plain files under `.venv/lib/python3.14t/site-packages`.

    Contract:
        - The site-packages directory and `src/` are prepended to `sys.path` for the test only.
        - The scratch modules are evicted from `sys.modules` before and after the test.

    Yields:
        Tuple[Path, Path, Path]: Resolved project root, source root and site-packages root.
    """
    project_root = tmp_path / "project"
    source_root = project_root / "src"
    site_root = project_root / ".venv" / "lib" / "python3.14t" / "site-packages"
    package_dir = site_root / CustodyNames.PACKAGE
    package_dir.mkdir(parents=True)
    source_root.mkdir(parents=True)
    (package_dir / "__init__.py").write_text(
        "import {0}\n"
        "VALUE = {0}.VALUE\n".format(CustodyNames.DEPENDENCY),
        encoding="utf-8",
    )
    (site_root / "{0}.py".format(CustodyNames.DEPENDENCY)).write_text(
        "VALUE = 7\n",
        encoding="utf-8",
    )
    (source_root / "{0}.py".format(CustodyNames.APP)).write_text(
        "import {0}\n"
        "\n"
        "class AppService:\n"
        "    pass\n".format(CustodyNames.PACKAGE),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(site_root))
    monkeypatch.syspath_prepend(str(source_root))
    for module_name in CustodyNames.all_names():
        sys.modules.pop(module_name, None)
    yield project_root.resolve(), source_root.resolve(), site_root.resolve()
    for module_name in CustodyNames.all_names():
        sys.modules.pop(module_name, None)


def _analyze_app(
        source_root: Path,
        site_root: Path,
        user_roots: Tuple[Path, ...],
        *,
        descent: bool,
        retain: bool = False,
) -> CrystalAnalysisResult:
    """
    Analyze the project's own module the way a SpellCrystal does at bind.

    Args:
        source_root: Directory holding the app module.
        site_root: The environment's site-packages, passed as the interpreter's site root.
        user_roots: Roots that define user-source authority.
        descent: The site-package descent policy under test.
        retain: Whether user-source text is retained.

    Returns:
        CrystalAnalysisResult: The analysis; the caller cleans it.
    """
    analyzer = CrystalAnalyzer(
        user_source_root_paths=user_roots,
        site_package_root_paths=(site_root,),
        retain_user_sources=retain,
        site_package_dependency_descent=descent,
    )
    try:
        return analyzer.analyze_spell_root(
            root_module_name=CustodyNames.APP,
            root_module_obj=None,
            root_module_path=source_root / "{0}.py".format(CustodyNames.APP),
        )
    finally:
        analyzer.cleanup()


@pytest.mark.parametrize("descent", [False, True])
def test_environment_nested_in_the_user_root_classifies_as_site_packages(
        nested_venv_project: Tuple[Path, Path, Path],
        descent: bool,
) -> None:
    """
    Contract: with the project directory as the user root, the project's module is user source and
    fingerprinted, while the installed package in the project's `.venv` is a site package with no
    fingerprint - the environment wins over the user root. Descent decides whether the walk enters the
    package: off, it is a leaf and its dependency is never recorded; on, its dependency records as a
    site package, also unfingerprinted.
    """
    project_root, source_root, site_root = nested_venv_project

    result = _analyze_app(source_root, site_root, (project_root,), descent=descent)
    try:
        kinds = dict(result.module_to_kind)
        assert kinds[CustodyNames.APP] == "user_source"
        assert kinds[CustodyNames.PACKAGE] == "site_package"
        dependencies = dict(result.module_to_direct_dependencies)
        if descent:
            assert kinds[CustodyNames.DEPENDENCY] == "site_package"
            assert CustodyNames.DEPENDENCY in dependencies[CustodyNames.PACKAGE]
        else:
            assert dependencies[CustodyNames.PACKAGE] == []
            assert CustodyNames.DEPENDENCY not in kinds
        fingerprints = dict(result.physical_module_fingerprints)
        assert CustodyNames.APP in fingerprints
        assert CustodyNames.PACKAGE not in fingerprints
        assert CustodyNames.DEPENDENCY not in fingerprints
    finally:
        result.cleanup()


def test_user_root_excluding_the_environment_records_the_package_as_a_site_leaf(
        nested_venv_project: Tuple[Path, Path, Path],
) -> None:
    """
    Contract: with only `src/` as the user root and descent off (the configuration default), the
    installed package is a site-package leaf with no dependency edges, its own import is never
    walked, and no site module is fingerprinted, while the project's module still is.
    """
    _project_root, source_root, site_root = nested_venv_project

    result = _analyze_app(source_root, site_root, (source_root,), descent=False)
    try:
        kinds = dict(result.module_to_kind)
        assert kinds[CustodyNames.APP] == "user_source"
        assert kinds[CustodyNames.PACKAGE] == "site_package"
        assert dict(result.module_to_direct_dependencies)[CustodyNames.PACKAGE] == []
        assert CustodyNames.DEPENDENCY not in kinds
        fingerprints = dict(result.physical_module_fingerprints)
        assert CustodyNames.APP in fingerprints
        assert CustodyNames.PACKAGE not in fingerprints
    finally:
        result.cleanup()


def test_descent_walks_the_excluded_environment_as_site_packages_without_fingerprints(
        nested_venv_project: Tuple[Path, Path, Path],
) -> None:
    """
    Contract: with only `src/` as the user root and descent on, the walk enters the installed
    package and records its dependency, both as site packages, and neither is fingerprinted.
    """
    _project_root, source_root, site_root = nested_venv_project

    result = _analyze_app(source_root, site_root, (source_root,), descent=True)
    try:
        kinds = dict(result.module_to_kind)
        assert kinds[CustodyNames.PACKAGE] == "site_package"
        assert kinds[CustodyNames.DEPENDENCY] == "site_package"
        fingerprints = dict(result.physical_module_fingerprints)
        assert CustodyNames.PACKAGE not in fingerprints
        assert CustodyNames.DEPENDENCY not in fingerprints
    finally:
        result.cleanup()


@pytest.mark.parametrize("root_choice", ["project", "source"])
def test_retained_user_source_follows_the_root_classification(
        nested_venv_project: Tuple[Path, Path, Path],
        root_choice: str,
) -> None:
    """
    Contract: with retention on, the record keeps the text of every module classified as user
    source - the project's own module, and never the installed package, whether or not the
    environment sits inside the user root.
    """
    project_root, source_root, site_root = nested_venv_project
    user_root = project_root if root_choice == "project" else source_root

    result = _analyze_app(source_root, site_root, (user_root,), descent=False, retain=True)
    try:
        retained = result.user_module_sources
        assert "class AppService" in str(retained[CustodyNames.APP]["source_text"])
        assert CustodyNames.PACKAGE not in retained
    finally:
        result.cleanup()


def test_user_roots_classify_modules_but_never_make_them_importable(tmp_path: Path) -> None:
    """
    Contract: a module that sits inside the user root but on no `sys.path` entry is an unknown,
    unwalked leaf, and analysis leaves `sys.path` and `sys.modules` untouched - a user root grants
    ownership, never access.
    """
    user_root = tmp_path / "owned"
    user_root.mkdir()
    (user_root / "{0}.py".format(CustodyNames.HIDDEN)).write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    consumer_path = user_root / "{0}.py".format(CustodyNames.HIDDEN_CONSUMER)
    consumer_path.write_text(
        "import {0}\n".format(CustodyNames.HIDDEN),
        encoding="utf-8",
    )
    path_before = list(sys.path)
    analyzer = CrystalAnalyzer(
        user_source_root_paths=(user_root.resolve(),),
        site_package_root_paths=(),
    )
    try:
        result = analyzer.analyze_spell_root(
            root_module_name=CustodyNames.HIDDEN_CONSUMER,
            root_module_obj=None,
            root_module_path=consumer_path,
        )
    finally:
        analyzer.cleanup()
    try:
        assert list(sys.path) == path_before
        assert CustodyNames.HIDDEN not in sys.modules
        assert dict(result.module_to_kind)[CustodyNames.HIDDEN] == "unknown"
        assert dict(result.module_to_direct_dependencies)[CustodyNames.HIDDEN] == []
        assert CustodyNames.HIDDEN not in dict(result.physical_module_fingerprints)
    finally:
        result.cleanup()


def test_with_defaults_takes_the_working_directory_as_the_user_root_and_turns_descent_off(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: the default configuration's user root is the resolved working directory, with descent
    off and no text retained.
    """
    monkeypatch.chdir(tmp_path)

    configuration = CrystallizerConfiguration().with_defaults()
    try:
        assert configuration.user_source_root_paths == (tmp_path.resolve(),)
        assert configuration.site_package_dependency_descent is False
        assert configuration.retain_user_sources is False
    finally:
        configuration.cleanup()


def test_default_configuration_classifies_a_working_directory_venv_as_a_site_package(
        nested_venv_project: Tuple[Path, Path, Path],
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Contract: run from the project directory, the policy `with_defaults()` produces - working
    directory as user root, descent off - records the nested environment's package as an
    unfingerprinted site-package leaf: the case the review's root-precedence question was about,
    answered by the owner on 2026-11-16 (#327).
    """
    project_root, source_root, site_root = nested_venv_project
    monkeypatch.chdir(project_root)
    configuration = CrystallizerConfiguration().with_defaults()
    try:
        user_roots = configuration.user_source_root_paths
        descent = configuration.site_package_dependency_descent
    finally:
        configuration.cleanup()

    result = _analyze_app(source_root, site_root, user_roots, descent=descent)
    try:
        assert dict(result.module_to_kind)[CustodyNames.PACKAGE] == "site_package"
        assert dict(result.module_to_direct_dependencies)[CustodyNames.PACKAGE] == []
        assert CustodyNames.PACKAGE not in dict(result.physical_module_fingerprints)
    finally:
        result.cleanup()
