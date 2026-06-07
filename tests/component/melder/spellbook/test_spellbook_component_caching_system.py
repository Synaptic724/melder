import inspect
from pathlib import Path
import shutil
from types import CodeType

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.caching_system.caching_system import CachingSystem
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spellbook_caching() -> None:
    """
    Reset singleton runtime state for Spellbook cache component tests.

    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _package_root() -> Path:
    """
    Return the installed melder package root used by AetherConfiguration.

    Returns:
        Path:
            Absolute melder package root.
    """
    return Path(inspect.getfile(AetherConfiguration)).resolve().parent.parent


def _prepare_cache_root(path: Path) -> Path:
    """
    Reset one repo-local cache root for the component test.

    Args:
        path:
            Target test directory.

    Returns:
        Path:
            Prepared directory path.
    """
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _build_cache_root_fragment(cache_root_path: Path) -> Path:
    """
    Convert an absolute test cache root into a package-relative fragment.

    Args:
        cache_root_path:
            Absolute cache root path for the test.

    Returns:
        Path:
            Path fragment relative to the melder package root.
    """
    return Path(cache_root_path.relative_to(_package_root()))


def _activate_aether_cache_configuration(
        *,
        cache_root_fragment: Path,
        enabled: bool,
) -> AetherConfiguration:
    """
    Activate one root Aether cache configuration for the component tests.

    Args:
        cache_root_fragment:
            Relative cache-root fragment anchored under the melder package root.
        enabled:
            Desired cache-enabled state.

    Returns:
        AetherConfiguration:
            Activated root configuration installed on Aether.
    """
    aether = Aether()
    configuration = (
        aether.create_configuration()
        .with_defaults()
        .with_system_caching_enabled(enabled)
        .with_system_cache_root_path(cache_root_fragment)
        .activate()
    )
    aether.activate(configuration)
    return configuration


def _make_spellbook(*, frame_name: str = "default") -> Spellbook:
    """
    Build one Spellbook configured for the cache component tests.

    Args:
        frame_name:
            Target Aether frame name.

    Returns:
        Spellbook:
            Fresh Spellbook instance.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _conjure_root(spellbook: Spellbook, *, name: str = "root") -> None:
    """
    Conjure one root conduit for the supplied Spellbook.

    Args:
        spellbook:
            Spellbook to conjure.
        name:
            Root conduit name.

    Returns:
        None.
    """
    spellbook.conjure(name=name)


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Resolve a local Spell instance by its versioned spell id.

    Args:
        spellbook:
            Spellbook holding locally bound spells.
        spell_id:
            Versioned spell id to locate.

    Returns:
        object | None:
            Resolved spell instance when found, otherwise None.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_component_spellbook_cache_gate_returns_true_when_enabled() -> None:
    """
    Verify the Spellbook cache gate reflects the enabled root config.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_gate_enabled"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()

    assert spellbook._system_caching_enabled_in_aether() is True
    assert spellbook._caching_enabled is True


def test_component_spell_defaults_caching_enabled_before_conjure() -> None:
    """
    Verify newly bound spells start with caching enabled before ownership stamp.

    Returns:
        None.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence="unique",
        permissions="create",
    )
    spell = _get_spell_by_version_id(spellbook, spell_id)

    assert spell is not None
    assert spell._caching_enabled is True


def test_component_spellbook_cache_gate_returns_false_when_disabled() -> None:
    """
    Verify the Spellbook cache gate reflects the disabled root config.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_gate_disabled"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=False,
    )
    spellbook = _make_spellbook()

    assert spellbook._system_caching_enabled_in_aether() is False
    assert spellbook._caching_enabled is False


def test_component_spell_stamps_caching_enabled_from_root_posture() -> None:
    """
    Verify ownership stamping copies the enabled cache posture onto spells.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_spell_enabled"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence="unique",
        permissions="create",
    )

    _conjure_root(spellbook, name="root")
    spell = _get_spell_by_version_id(spellbook, spell_id)

    assert spell is not None
    assert spell._caching_enabled is True


def test_component_spell_stamps_caching_disabled_from_root_posture() -> None:
    """
    Verify ownership stamping copies the disabled cache posture onto spells.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_spell_disabled"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=False,
    )
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence="unique",
        permissions="create",
    )

    _conjure_root(spellbook, name="root")
    spell = _get_spell_by_version_id(spellbook, spell_id)

    assert spell is not None
    assert spell._caching_enabled is False


def test_component_spellbook_does_not_build_caching_system_until_first_request() -> None:
    """
    Verify the utility remains lazy even after conjure.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_lazy_build"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="root")

    assert spellbook._caching_system is None


def test_component_spellbook_lazily_builds_caching_system_when_enabled() -> None:
    """
    Verify Spellbook lazily builds one cache utility after conjure.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_enabled_root"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="root")

    caching_system = spellbook._get_or_create_caching_system()

    assert isinstance(caching_system, CachingSystem)
    assert caching_system.bundle_path == (
        cache_root_path / "default" / "root" / "bundle.json"
    )


def test_component_spellbook_uses_custom_conduit_name_in_cache_path() -> None:
    """
    Verify custom conduit names drive the cache file location.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_custom_name"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="alpha")

    caching_system = spellbook._get_or_create_caching_system()

    assert caching_system.bundle_path == (
        cache_root_path / "default" / "alpha" / "bundle.json"
    )


def test_component_spellbook_uses_frame_name_in_cache_path() -> None:
    """
    Verify the Spellbook frame name participates in the cache path.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_frame_name"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook(frame_name="ops")
    _conjure_root(spellbook, name="root")

    caching_system = spellbook._get_or_create_caching_system()

    assert caching_system.bundle_path == (
        cache_root_path / "ops" / "root" / "bundle.json"
    )


def test_component_spellbook_returns_same_caching_system_instance_on_repeat_calls() -> None:
    """
    Verify the lazy cache utility is reused after first construction.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_same_instance"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="root")

    first = spellbook._get_or_create_caching_system()
    second = spellbook._get_or_create_caching_system()

    assert first is second


def test_component_spellbook_stores_caching_system_after_creation() -> None:
    """
    Verify the Spellbook stores the created utility on its field.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_stored_field"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="root")

    caching_system = spellbook._get_or_create_caching_system()

    assert spellbook._caching_system is caching_system


def test_component_spellbook_cleanup_cleans_created_caching_system() -> None:
    """
    Verify Spellbook cleanup tears down the owned cache utility.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_cleanup"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="root")
    caching_system = spellbook._get_or_create_caching_system()

    spellbook.cleanup()

    assert caching_system.cleaned is True


def test_component_spellbook_bundle_path_uses_relative_config_fragment() -> None:
    """
    Verify the configured relative cache-root fragment is honored.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_relative_fragment"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    configuration = _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    _conjure_root(spellbook, name="root")
    caching_system = spellbook._get_or_create_caching_system()

    assert configuration.system_cache_root_path == cache_root_fragment
    assert caching_system.bundle_path.parent.parent == cache_root_path / "default"


def test_component_spell_emit_cache_writes_payload_into_spellbook_cache() -> None:
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_emit_spell"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence="unique",
        permissions="create",
    )
    _conjure_root(spellbook, name="root")
    spell = _get_spell_by_version_id(spellbook, spell_id)

    assert spell is not None
    spell._get_or_build_creation_context()

    caching_system = spellbook._get_or_create_caching_system()
    assert caching_system.has_spell_payload(spell_id) is True
    spell_payload = caching_system.get_spell_payload(spell_id)
    assert spell_payload is not None
    assert isinstance(spell_payload, tuple)
    assert len(spell_payload) == 2
    assert isinstance(spell_payload[0], CodeType)
    assert isinstance(spell_payload[1], CodeType)
    assert spell.emit_cache() is False


def test_component_spell_emit_cache_skips_existing_spell_id_payload() -> None:
    cache_root_path = _prepare_cache_root(
        _package_root() / "tests/component/melder/spellbook/_cache_emit_spell_skip_existing"
    )
    cache_root_fragment = _build_cache_root_fragment(cache_root_path)
    _activate_aether_cache_configuration(
        cache_root_fragment=cache_root_fragment,
        enabled=True,
    )
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence="unique",
        permissions="create",
    )
    _conjure_root(spellbook, name="root")
    spell = _get_spell_by_version_id(spellbook, spell_id)

    assert spell is not None
    spell._get_or_build_creation_context()
    assert spell.emit_cache() is False
