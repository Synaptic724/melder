import inspect
from importlib import import_module
import marshal
import shutil
from pathlib import Path
from typing import Dict, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.nexus.nexus import Nexus
from tests.mocks.spellbook.core_classes import BasicLogger, BasicService


def _reset_runtime_singletons() -> None:
    """Reset singleton runtime state for cache integration tests."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_runtime_for_cache_integration() -> None:
    """Ensure each cache integration test starts from a clean runtime."""
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _package_root() -> Path:
    """
    Return the installed melder package root for relative cache fragments.

    Contract:
        Must resolve to the SAME root the runtime anchors relative cache
        fragments against (`src/melder`). `AethericFrameConfiguration` lives at
        `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`, so
        the package root is three parents up. The old two-parent version
        resolved to `src/melder/aether`, which made `_prepare_case_cache_root`
        clean empty decoy directories while the runtime's real cache
        directories accumulated stale bundles across pytest sessions and
        poisoned every namespace-sensitive cache assertion in this module.
    """
    return Path(
        inspect.getfile(AethericFrameConfiguration)
    ).resolve().parents[2]


def _prepare_case_cache_root(label: str) -> Path:
    """Reset one package-root-local cache folder for a test case."""
    path = _package_root() / "tests/integration/melder/spellbook" / label
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _build_cache_root_fragment(cache_root_path: Path) -> Path:
    """Convert an absolute cache root into a package-relative fragment."""
    return Path(cache_root_path.relative_to(_package_root()))


def _make_spellbook(
        *,
        frame_name: str,
        cache_root_fragment: Path,
        dynamic: bool,
        caching_enabled: bool = True,
) -> Spellbook:
    """Build one Spellbook configured for cache integration runs."""
    spellbook = Spellbook(aetheric_frame=frame_name)
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.configure_aether_frame(
        system_state="dynamic" if dynamic else None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=caching_enabled,
    )
    frame_configuration = spellbook._aetheric_frame_configuration
    assert frame_configuration is not None
    frame_configuration.with_system_cache_root_path(cache_root_fragment)
    return spellbook


def _bind_simple_spells(
        spellbook: Spellbook,
        *,
        include_logger: bool = False,
) -> Dict[type, str]:
    """Bind one or two simple unique spells and return their spell ids."""
    spell_ids = {
        BasicService: spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
    }
    if include_logger:
        spell_ids[BasicLogger] = spellbook.bind(
            spell=BasicLogger,
            existence=Existence.unique,
            permissions="create",
        )
    return spell_ids


def _conjure(spellbook: Spellbook, *, conduit_name: str, dynamic: bool) -> Conduit:
    """Conjure one root conduit with the requested runtime posture."""
    return spellbook.conjure(name=conduit_name, dynamic=dynamic)


def _seed_cache(conduit: Conduit, spell_ids: Dict[type, str]) -> None:
    """Publish cache packages by melding each bound spell once."""
    for spell_id in spell_ids.values():
        conduit.meld(spell_id=spell_id)


def _get_spell(spellbook: Spellbook, spell_id: str):
    """Resolve one live spell object from the spellbook pool."""
    return spellbook._spell_id_pool[spell_id]


def _cache_bundle_path(spellbook: Spellbook, *, conduit_name: str) -> Path:
    """Return the current cache bundle path for one spellbook/conduit name."""
    return spellbook._get_or_create_caching_system(conduit_name=conduit_name).bundle_path


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_bare_conjure_stages_and_emits_all_spells(dynamic: bool) -> None:
    """
    Verify a bare non-full-hit conjure stages every constructed spell and
    emits the bundle at conjure end.

    Contract:
        Conjure is the staging boundary: dependency-only spells never receive
        their own runtime publish, so meld-time staging alone can never
        complete the bundle and the conduit cache would stay permanently
        mixed. After phases 8-11 build each artifact, conjure stages every
        missing constructed spell and writes the bundle once, so the next
        identical conjure full-hits without requiring each spell to be melded
        directly first.
    """
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_no_emit_before_publish_{'dynamic' if dynamic else 'automatic'}"
    )
    spellbook = _make_spellbook(
        frame_name="cache-runtime-before-publish",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook, include_logger=True)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        assert _cache_bundle_path(spellbook, conduit_name="root").exists() is True
        caching_system = spellbook._get_or_create_caching_system()
        for spell_id in spell_ids.values():
            assert caching_system.has_spell_payload(spell_id) is True
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_first_meld_emits_file_and_payload(dynamic: bool) -> None:
    """Verify first runtime publish creates the cache file and stores the root payload."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_first_emit_{'dynamic' if dynamic else 'automatic'}"
    )
    spellbook = _make_spellbook(
        frame_name="cache-runtime-first-emit",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        conduit.meld(spell_id=spell_ids[BasicService])
        caching_system = spellbook._get_or_create_caching_system()
        assert caching_system.bundle_path.exists() is True
        assert caching_system.has_spell_payload(spell_ids[BasicService]) is True
    finally:
        conduit.cleanup()


def _seed_then_reset_single_spell_namespace(
        *,
        cache_root_path: Path,
        frame_name: str,
        conduit_name: str,
        dynamic: bool,
) -> str:
    """Seed cache for one single-spell namespace and reset runtime state."""
    spellbook = _make_spellbook(
        frame_name=frame_name,
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name=conduit_name, dynamic=dynamic)
    try:
        _seed_cache(conduit, spell_ids)
        assert _cache_bundle_path(spellbook, conduit_name=conduit_name).exists() is True
    finally:
        conduit.cleanup()
    _reset_runtime_singletons()
    return spell_ids[BasicService]


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_second_identical_run_preloads_context(dynamic: bool) -> None:
    """Verify a second identical run loads the cached context during conjure."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_second_run_preloads_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-preload",
        conduit_name="root",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-preload",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell._creation_context is not None
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_second_identical_run_marks_resolution_ready(dynamic: bool) -> None:
    """Verify a full-hit conjure marks the spell as runtime-ready before meld."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_second_run_ready_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-ready",
        conduit_name="root",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-ready",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell.resolution_complete is True
        assert spell.resolution_required is False
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_second_identical_run_skips_phase11_artifact(dynamic: bool) -> None:
    """Verify a full-hit conjure avoids rebuilding the phase-11 artifact."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_second_run_skip_phase11_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-skip-phase11",
        conduit_name="root",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-skip-phase11",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell._compiler_artifact._spell_codegen_creation is None
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_stale_surplus_cache_still_full_hits(dynamic: bool) -> None:
    """Verify extra cached spell ids do not block full-hit reload for live ids."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_surplus_full_hit_{'dynamic' if dynamic else 'automatic'}"
    )
    first_spellbook = _make_spellbook(
        frame_name="cache-runtime-surplus",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    first_spell_ids = _bind_simple_spells(first_spellbook, include_logger=True)
    first_conduit = _conjure(first_spellbook, conduit_name="root", dynamic=dynamic)
    try:
        _seed_cache(first_conduit, first_spell_ids)
    finally:
        first_conduit.cleanup()
    _reset_runtime_singletons()

    second_spellbook = _make_spellbook(
        frame_name="cache-runtime-surplus",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    second_spell_ids = _bind_simple_spells(second_spellbook, include_logger=False)
    second_conduit = _conjure(second_spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(second_spellbook, second_spell_ids[BasicService])
        assert spell._creation_context is not None
        assert spell.resolution_required is False
    finally:
        second_conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_missing_live_spell_ids_force_rerun(dynamic: bool) -> None:
    """Verify adding new live spell ids turns the second run into a rerun path."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_missing_live_ids_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-missing-live",
        conduit_name="root",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-missing-live",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook, include_logger=True)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell._creation_context is None
        assert spell._compiler_artifact._spell_codegen_creation is not None
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_changed_conduit_name_misses_cache(dynamic: bool) -> None:
    """Verify changing conduit name changes the cache namespace and misses cache."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_changed_conduit_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-changed-conduit",
        conduit_name="alpha",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-changed-conduit",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="beta", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell._creation_context is None
        assert spell._compiler_artifact._spell_codegen_creation is not None
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_changed_frame_name_misses_cache(dynamic: bool) -> None:
    """Verify changing frame name changes the cache namespace and misses cache."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_changed_frame_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-frame-a",
        conduit_name="root",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-frame-b",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell._creation_context is None
        assert spell._compiler_artifact._spell_codegen_creation is not None
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_cache_integration_disabled_second_run_ignores_existing_cache(dynamic: bool) -> None:
    """Verify cache-disabled runs ignore already seeded cache namespaces."""
    cache_root_path = _prepare_case_cache_root(
        f"_cache_runtime_disabled_second_run_{'dynamic' if dynamic else 'automatic'}"
    )
    _seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="cache-runtime-disabled-second-run",
        conduit_name="root",
        dynamic=dynamic,
    )

    spellbook = _make_spellbook(
        frame_name="cache-runtime-disabled-second-run",
        cache_root_fragment=_build_cache_root_fragment(cache_root_path),
        dynamic=dynamic,
        caching_enabled=False,
    )
    spell_ids = _bind_simple_spells(spellbook)
    conduit = _conjure(spellbook, conduit_name="root", dynamic=dynamic)
    try:
        spell = _get_spell(spellbook, spell_ids[BasicService])
        assert spell._creation_context is None
        assert spell._compiler_artifact._spell_codegen_creation is not None
        assert spellbook._caching_system is None
    finally:
        conduit.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize(
    ("previous_release", "current_release"),
    [
        pytest.param("1.0.0", "1.0.1", id="upgrade"),
        pytest.param("1.0.1", "1.0.0", id="downgrade"),
        pytest.param("1.0.0rc1", "1.0.0", id="prerelease"),
        pytest.param("1.0.0", "1.0.0+local", id="local-version"),
    ],
)
def test_changed_melder_release_rebuilds_same_bindings_then_reuses_cache(
        monkeypatch: pytest.MonkeyPatch,
        dynamic: bool,
        previous_release: str,
        current_release: str,
) -> None:
    """
    Reject a previous release before hydration, then reuse the rebuilt bundle.

    Contract:
        Three fresh runtime lifetimes share identical binding IDs, cache format
        and cache path. The second must not publish an old cached context. The
        third must resolve correctly without running plan compilation again.
        Only the cache loader's imported release value changes; package files
        and generated assets are never edited by the test.

    Args:
        monkeypatch: Restore the simulated release and orchestration probes.
        dynamic: Exercise automatic and dynamic worlds.
        previous_release: Release recorded by the first runtime.
        current_release: Different release used by both later runtimes.

    Returns:
        None.
    """
    cache_module = import_module("melder.utilities.caching_system.caching_system")
    cache_root_path = _prepare_case_cache_root(
        f"_cache_release_{previous_release}_{current_release}_{dynamic}"
    )
    fragment = _build_cache_root_fragment(cache_root_path)
    frame_name = "cache-release-compatibility"
    monkeypatch.setattr(cache_module, "__version__", previous_release)

    original_book = _make_spellbook(
        frame_name=frame_name, cache_root_fragment=fragment, dynamic=dynamic,
    )
    original_ids = _bind_simple_spells(original_book, include_logger=True)
    original_root = _conjure(original_book, conduit_name="root", dynamic=dynamic)
    try:
        _seed_cache(original_root, original_ids)
        bundle_path = _cache_bundle_path(original_book, conduit_name="root")
        original_bundle = marshal.loads(bundle_path.read_bytes())
        assert original_bundle["melder_version"] == previous_release
    finally:
        original_root.cleanup()
    _reset_runtime_singletons()

    monkeypatch.setattr(cache_module, "__version__", current_release)

    def reject_old_cached_context(**_kwargs: object) -> None:
        """Fail if a release mismatch reaches cached-executor publication."""
        pytest.fail("A previous Melder release reached cached-context publication.")

    with monkeypatch.context() as cold_probe:
        cold_probe.setattr(
            SpellbookCreationSystem,
            "_publish_cached_creation_context_for_spell",
            staticmethod(reject_old_cached_context),
        )
        rebuilt_book = _make_spellbook(
            frame_name=frame_name, cache_root_fragment=fragment, dynamic=dynamic,
        )
        rebuilt_ids = _bind_simple_spells(rebuilt_book, include_logger=True)
        assert rebuilt_ids == original_ids
        rebuilt_root = _conjure(rebuilt_book, conduit_name="root", dynamic=dynamic)
        try:
            assert isinstance(rebuilt_root.meld(spell_id=rebuilt_ids[BasicService]), BasicService)
            assert isinstance(rebuilt_root.meld(spell_id=rebuilt_ids[BasicLogger]), BasicLogger)
            rebuilt_bundle = marshal.loads(bundle_path.read_bytes())
            assert rebuilt_bundle["version"] == original_bundle["version"]
            assert rebuilt_bundle["melder_version"] == current_release
            assert set(rebuilt_bundle["spell_payloads"]) == set(original_ids.values())
        finally:
            rebuilt_root.cleanup()
    _reset_runtime_singletons()

    def reject_unnecessary_plan_rebuild(**_kwargs: object) -> None:
        """Fail if a compatible subsequent runtime recompiles phases 8-11."""
        pytest.fail("A same-release cache hit unnecessarily rebuilt the creation plan.")

    with monkeypatch.context() as warm_probe:
        warm_probe.setattr(
            SpellbookCreationSystem,
            "_run_conduit_plan_resolution_phases",
            staticmethod(reject_unnecessary_plan_rebuild),
        )
        warm_book = _make_spellbook(
            frame_name=frame_name, cache_root_fragment=fragment, dynamic=dynamic,
        )
        warm_ids = _bind_simple_spells(warm_book, include_logger=True)
        assert warm_ids == original_ids
        warm_root = _conjure(warm_book, conduit_name="root", dynamic=dynamic)
        try:
            assert isinstance(warm_root.meld(spell_id=warm_ids[BasicService]), BasicService)
            assert isinstance(warm_root.meld(spell_id=warm_ids[BasicLogger]), BasicLogger)
            assert marshal.loads(bundle_path.read_bytes())["melder_version"] == current_release
        finally:
            warm_root.cleanup()
