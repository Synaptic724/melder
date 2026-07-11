import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.spell_crystal import SpellCrystal


class _DummySpell:
    """
    Minimal spell double for crystallizer root tests.
    """

    def __init__(self, spell_id: str, spell) -> None:
        self.spell_id = spell_id
        self.spell = spell
        # Bind-signature fields consumed by SpellCrystal.__init__ (test doubles).
        self.spell_name = spell_id
        self.binding_name = None
        self.spellframe = None
        self.existence = SimpleNamespace(name="present")
        self.permissions = SimpleNamespace(name="default")
        # Capture-gap fields (restore_engine_2026_07_07): SpellCrystal also
        # reads the disposal contract and the attached profile object
        # (SimpleNamespace type-name classifies as the "general" fallback).
        self.disposal_method_names = []
        self.profile = SimpleNamespace()


@pytest.fixture(autouse=True)
def reset_crystallizer_singleton() -> None:
    """
    Reset the hosted runtime singletons around each unit test.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


def _create_hosted_crystallizer() -> Crystallizer:
    """
    Build the hosted crystallizer singleton through `Aether`.

    Returns:
        Crystallizer: Hosted singleton root.
    """
    aether = Aether()
    assert aether._crystallizer is not None
    return aether._crystallizer


def test_crystallizer_rejects_first_init_without_aether() -> None:
    """
    Verify the first crystallizer bootstrap must come through `Aether`.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="Aether must be provided"):
        Crystallizer()


def test_crystallizer_is_hosted_by_aether() -> None:
    """
    Verify `Aether` boots the hosted crystallizer root disabled by default.

    Returns:
        None.
    """
    aether = Aether()
    crystallizer = Crystallizer()

    assert aether._crystallizer is crystallizer
    assert crystallizer.is_configured is False
    assert crystallizer.is_activated is False


def test_crystallizer_behaves_as_singleton() -> None:
    """
    Verify repeated construction returns the same root object.

    Returns:
        None.
    """
    first = _create_hosted_crystallizer()
    second = Crystallizer()

    assert first is second


def test_crystallizer_activate_requires_activated_configuration() -> None:
    """
    Verify root activation rejects a non-activated configuration.

    Returns:
        None.
    """
    crystallizer = _create_hosted_crystallizer()
    configuration = crystallizer.create_configuration().with_defaults().finalize()

    crystallizer.configure(configuration)

    with pytest.raises(RuntimeError):
        crystallizer.activate()


def test_crystallizer_activate_marks_root_active() -> None:
    """
    Verify crystallizer activates once the config is activated.

    Returns:
        None.
    """
    crystallizer = _create_hosted_crystallizer()
    configuration = crystallizer.create_configuration().with_defaults().activate()

    crystallizer.activate(configuration)

    assert crystallizer.configured is True
    assert crystallizer.activated is True
    assert crystallizer.configuration is configuration


def test_crystallizer_create_spell_crystal_uses_configured_user_source_roots() -> None:
    """
    Verify crystal construction consumes root-owned source-root policy.

    Returns:
        None.
    """
    user_source_root = Path(__file__).resolve().parents[3] / "mocks" / "crystallizer"
    crystallizer = _create_hosted_crystallizer()
    configuration = (
        crystallizer.create_configuration()
        .with_user_source_root_paths((user_source_root,))
        .activate()
    )
    crystallizer.activate(configuration)

    root_module = importlib.import_module(
        "tests.mocks.crystallizer.spell_crystal_demo_pkg.root"
    )
    crystal = None
    try:
        crystal = crystallizer.create_spell_crystal(
            _DummySpell("spell-config-1", root_module.RootService)
        )
        assert isinstance(crystal, SpellCrystal)
        assert crystal.root_module_kind == "user_source"
        assert str(user_source_root.resolve()) in crystal.user_source_root_paths
    finally:
        if crystal is not None:
            crystal.cleanup()


def test_crystallizer_cleanup_resets_singleton_state() -> None:
    """
    Verify cleanup resets singleton bookkeeping without detaching the hosted root.

    Returns:
        None.
    """
    aether = Aether()
    crystallizer = aether._crystallizer
    configuration = crystallizer.create_configuration().with_defaults().activate()
    crystallizer.activate(configuration)

    crystallizer.cleanup()

    assert aether._crystallizer is crystallizer
    assert crystallizer.cleaned is True
    assert Crystallizer._instance is None
    assert Crystallizer._initialized is False
