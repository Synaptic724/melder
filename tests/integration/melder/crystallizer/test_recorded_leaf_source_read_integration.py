"""
Characterization tests: recorded installed-package leaves stay readable (core-protection review,
2026-10-10).

Purpose:
    The Crystallizer's default descent policy stops its walk at installed packages, recording them
    as leaves. That is an analysis-depth policy, not a read barrier: MutationResearch.source_view
    and a codegen room's research_source read a recorded leaf's text from the live disk, without a
    frame ACL check and under the most restrictive codegen profile. These tests pin that, together
    with the two limits of the read: only modules the spell's recorded world carries can be read,
    and an installed leaf carries no fingerprint, so an on-disk edit after recording reads back with
    no drift verdict. They describe today's behaviour for the owner's decisions on the review's
    read and protection questions; they do not claim it is the intended policy.

Runs only on 3.14t (melder package root import chain).
"""
import importlib
import sys
from pathlib import Path
from typing import Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from melder.nexus.rift.rift import Rift
from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)


class LeafNames:
    """
    Module names of the scratch project, unique to this file.

    Contract:
        - `APP` lives under the project's `src/` and imports `DIST`.
        - `DIST` is an installed package under a `site-packages` directory; it imports `INTERIOR`.
    """

    APP: str = "cpb_leaf_app"
    DIST: str = "cpb_leaf_dist"
    INTERIOR: str = "cpb_leaf_dist.interior"


@pytest.fixture(autouse=True)
def clean_world(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """
    Isolate each test behind fresh runtime singletons and a per-test crystallizer cache.

    Yields:
        None.
    """
    monkeypatch.setattr(
        CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: tmp_path / "__crystallizer_cache__"),
    )
    reset_runtime_singletons()
    try:
        yield
    finally:
        reset_runtime_singletons()


@pytest.fixture()
def leaf_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Tuple[Path, Path]]:
    """
    Build a project module that imports an installed package with an interior module.

    Contract:
        - `src/` and the `site-packages` directory are on `sys.path` for the test only.
        - The scratch modules are evicted from `sys.modules` before and after the test.

    Yields:
        Tuple[Path, Path]: Resolved source root and site-packages root.
    """
    source_root = tmp_path / "leafproject" / "src"
    site_root = tmp_path / "leafproject" / "env" / "lib" / "site-packages"
    dist_dir = site_root / LeafNames.DIST
    dist_dir.mkdir(parents=True)
    source_root.mkdir(parents=True)
    (dist_dir / "__init__.py").write_text(
        "from {0} import interior\n"
        "INSTALLED_MARKER = 'installed leaf text'\n".format(LeafNames.DIST),
        encoding="utf-8",
    )
    (dist_dir / "interior.py").write_text("DEEP = True\n", encoding="utf-8")
    (source_root / "{0}.py".format(LeafNames.APP)).write_text(
        "import {0}\n"
        "\n"
        "class LeafReaderService:\n"
        "    pass\n".format(LeafNames.DIST),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(site_root))
    monkeypatch.syspath_prepend(str(source_root))
    for module_name in (LeafNames.APP, LeafNames.DIST, LeafNames.INTERIOR):
        sys.modules.pop(module_name, None)
    yield source_root.resolve(), site_root.resolve()
    for module_name in (LeafNames.APP, LeafNames.DIST, LeafNames.INTERIOR):
        sys.modules.pop(module_name, None)


def _recorded_world(source_root: Path) -> Tuple[Nexus, Rift, Conduit, str]:
    """
    Record one bound spell whose module imports the installed package.

    Purpose:
        Activate recording with `src/` as the only user root and the default descent policy (off),
        open a codegen room whose frame uses the `safe` codegen profile, activate MutationResearch
        and bind the project's class.

    Args:
        source_root: The project's `src/` directory.

    Returns:
        Tuple[Nexus, Rift, Conduit, str]: The live Nexus, the codegen Rift, the frame's root
            conduit and the bound spell id.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.with_user_source_root_paths((source_root,))
    configuration.activate()
    Crystallizer().activate(configuration)
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    research = Aether().mutation_research
    research.configure(research.create_configuration().with_defaults().activate())
    research.activate(hydrate_from_record=False)
    codegen_change = nexus.get_frame_acl_builder("ops").begin_codegen_change(
        reason="recorded_leaf_source_read",
    )
    codegen_change.use_profile("safe")
    codegen_change.commit_change()
    rift.create_frame_link("ops")
    app_module = importlib.import_module(LeafNames.APP)
    spell_id = conduit.bind(spell=app_module.LeafReaderService, existence="unique")
    return nexus, rift, conduit, spell_id


def test_descent_off_leaf_is_recorded_unwalked_and_read_from_the_live_disk(
        leaf_project: Tuple[Path, Path],
) -> None:
    """
    Contract: with descent off the installed package is recorded as a site-package leaf and its
    interior is not; source_view still returns the leaf's file text from the live disk (no drift
    verdict, since leaves are not fingerprinted); the unwalked interior answers unknown_module
    instead of being read; and a codegen room under the `safe` profile reads the same text through
    research_source.
    """
    source_root, site_root = leaf_project
    _nexus, rift, conduit, spell_id = _recorded_world(source_root)
    try:
        crystal = Crystallizer().get_spell_crystal(spell_id)
        assert LeafNames.DIST in crystal.site_package_targets
        assert LeafNames.INTERIOR not in crystal.module_targets
        leaf_text = (site_root / LeafNames.DIST / "__init__.py").read_text(encoding="utf-8")

        view = Aether().mutation_research.source_view(spell_id, module_name=LeafNames.DIST)
        row = view["modules"][LeafNames.DIST]
        assert row["origin"] == "live_disk"
        assert row["source"] == leaf_text
        assert row["drifted"] is None

        interior = Aether().mutation_research.source_view(
            spell_id,
            module_name=LeafNames.INTERIOR,
        )
        assert interior["unknown_module"] is True
        assert interior["modules"] == {}

        room_view = rift.space.command_system.research_source(
            spell_id,
            module_name=LeafNames.DIST,
        )
        assert room_view["modules"][LeafNames.DIST]["source"] == leaf_text
    finally:
        conduit.cleanup()


def test_an_installed_leaf_edited_after_recording_reads_back_without_a_drift_verdict(
        leaf_project: Tuple[Path, Path],
) -> None:
    """
    Contract: a recorded installed leaf carries no fingerprint, so after its file is edited on disk
    source_view returns the edited text with `drifted` None - while the project's own module, which
    is fingerprinted, reports the same kind of edit as drift.
    """
    source_root, site_root = leaf_project
    _nexus, _rift, conduit, spell_id = _recorded_world(source_root)
    try:
        leaf_path = site_root / LeafNames.DIST / "__init__.py"
        app_path = source_root / "{0}.py".format(LeafNames.APP)
        leaf_path.write_text(
            leaf_path.read_text(encoding="utf-8") + "EDITED_AFTER_RECORDING = True\n",
            encoding="utf-8",
        )
        app_path.write_text(
            app_path.read_text(encoding="utf-8") + "EDITED_AFTER_RECORDING = True\n",
            encoding="utf-8",
        )

        research = Aether().mutation_research
        leaf_row = research.source_view(spell_id, module_name=LeafNames.DIST)["modules"][LeafNames.DIST]
        app_row = research.source_view(spell_id, module_name=LeafNames.APP)["modules"][LeafNames.APP]

        assert "EDITED_AFTER_RECORDING" in str(leaf_row["source"])
        assert leaf_row["drifted"] is None
        assert app_row["origin"] == "live_disk"
        assert app_row["drifted"] is True
    finally:
        conduit.cleanup()
