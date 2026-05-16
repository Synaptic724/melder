import importlib

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.crystallizer.spell_crystal_harness import (
    PHYSICAL_CASES,
    PHYSICAL_PACKAGE_PREFIX,
    PHYSICAL_USER_SOURCE_ROOT,
    clear_modules,
    clear_modules_by_prefix,
    install_component_synthetic_dependency,
    physical_case_id,
)


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_singletons_for_spell_crystal_integration() -> None:
    """
    Reset singleton runtime state around each integration test.

    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _create_integration_crystallizer() -> Crystallizer:
    """
    Build one activated hosted crystallizer for integration graph cases.

    Returns:
        Crystallizer: Activated hosted crystallizer.
    """
    aether = Aether()
    crystallizer = aether._crystallizer
    configuration = (
        crystallizer.create_configuration()
        .with_user_source_root_paths((PHYSICAL_USER_SOURCE_ROOT,))
        .activate()
    )
    crystallizer.activate(configuration)
    return crystallizer


def _make_configuration(frame_name: str) -> SpellbookConfiguration:
    """
    Build one small automatic Spellbook configuration for integration tests.

    Args:
        frame_name:
            Target frame name.

    Returns:
        SpellbookConfiguration: Prepared configuration object.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


@pytest.fixture(params=PHYSICAL_CASES, ids=physical_case_id)
def integration_spell_crystal_case(request):
    """
    Build one real bound spell and the resulting `SpellCrystal`.
    """
    case = request.param
    clear_modules_by_prefix(PHYSICAL_PACKAGE_PREFIX)
    synthetic_module = None
    if case.get("requires_synthetic_dependency"):
        synthetic_module = install_component_synthetic_dependency()

    root_module = importlib.import_module(case["root_module_name"])
    root_type = getattr(root_module, case["root_class_name"])
    spellbook = Spellbook(
        aetheric_frame="spell-crystal-integration-{0}".format(case["case_id"]),
        configuration=_make_configuration(
            "spell-crystal-integration-{0}".format(case["case_id"])
        ),
    )
    spell_id = spellbook.bind(
        spell=root_type,
        existence=Existence.unique,
    )
    spell = spellbook._spells_by_id[spell_id]
    crystal = _create_integration_crystallizer().create_spell_crystal(spell)
    try:
        yield case, spell_id, crystal
    finally:
        crystal.cleanup()
        spellbook.cleanup()
        if synthetic_module is not None:
            synthetic_module.cleanup()
            clear_modules(case["expected_module_targets"][-1])
        clear_modules_by_prefix(PHYSICAL_PACKAGE_PREFIX)


def test_integration_case_preserves_id(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case carries the real bound identity through.
    """
    _case, spell_id, crystal = integration_spell_crystal_case
    assert crystal.id == spell_id


def test_integration_case_root_module_name_matches_expected(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case exposes the expected root module name.
    """
    case, _spell_id, crystal = integration_spell_crystal_case
    assert crystal.root_module_name == case["root_module_name"]


def test_integration_case_root_module_kind_matches_expected(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case exposes the expected root module kind.
    """
    case, _spell_id, crystal = integration_spell_crystal_case
    assert crystal.root_module_kind == case["expected_kind_by_module"][case["root_module_name"]]


def test_integration_case_root_target_kind_is_class(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case binds and crystallizes one class target.
    """
    _case, _spell_id, crystal = integration_spell_crystal_case
    assert crystal.root_target_kind == "class"


def test_integration_case_collects_expected_module_targets(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case records the expected module target set.
    """
    case, _spell_id, crystal = integration_spell_crystal_case
    assert set(crystal.module_targets) == set(case["expected_module_targets"])


def test_integration_case_collects_expected_direct_dependencies(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case records the expected direct dependency map.
    """
    case, _spell_id, crystal = integration_spell_crystal_case
    assert {
        module_name: set(dependency_names)
        for module_name, dependency_names in crystal.module_to_direct_dependencies.items()
    } == {
        module_name: set(dependency_names)
        for module_name, dependency_names in case["expected_direct_dependencies"].items()
    }


def test_integration_case_collects_expected_kind_map(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case records the expected module-kind map.
    """
    case, _spell_id, crystal = integration_spell_crystal_case
    assert crystal.module_to_kind == case["expected_kind_by_module"]


def test_integration_case_describe_snapshot_matches_expected_maps(
        integration_spell_crystal_case,
) -> None:
    """
    Verify each integration case `describe()` snapshot mirrors the manifest.
    """
    case, spell_id, crystal = integration_spell_crystal_case
    description = crystal.describe()
    assert description["id"] == spell_id
    assert set(description["module_targets"]) == set(case["expected_module_targets"])
    assert {
        module_name: set(dependency_names)
        for module_name, dependency_names in description["module_to_direct_dependencies"].items()
    } == {
        module_name: set(dependency_names)
        for module_name, dependency_names in case["expected_direct_dependencies"].items()
    }
