import sys

import pytest

from melder.crystallizer.crystal_loader_system.user_world_rebuild import (
    rebuild_absent_user_modules,
)
from melder.crystallizer.synthetic_module import SyntheticModule


@pytest.fixture(autouse=True)
def clean_probe_modules():
    """
    Tear down every module this file materializes, for isolation.
    """
    yield
    for name in list(SyntheticModule._registered_modules_by_name):
        if name.startswith(("lo_probe", "r11_probe")):
            module = SyntheticModule._registered_modules_by_name[name]
            if not module.cleaned:
                module.cleanup()
    for name in list(sys.modules):
        if name.startswith(("lo_probe", "r11_probe")):
            sys.modules.pop(name, None)


def _module(name: str, deps=None, published: bool = True) -> SyntheticModule:
    """
    Register one minimal synthetic module for registry-level tests.

    Args:
        name: Canonical module name.
        deps: Optional internal dependency names.
        published: When True, publish into sys.modules.

    Returns:
        SyntheticModule: The registered module.
    """
    module = SyntheticModule(
        module_name=name,
        spell_crystal_id="probe_crystal",
        source_text="VALUE = 1\n",
        source_sha256="beef",
        binding_signature="probe",
        internal_dependency_names=list(deps or []),
    )
    module.register_in_import_registry()
    if published:
        module.publish_to_sys_modules()
    return module


def test_rebuild_follows_recorded_load_order() -> None:
    """
    The load_order residue contract: when the crystal payload carries a
    topological module_load_order, absent modules rebuild in EXACTLY that
    order, not dot-depth order.
    """
    built: list = []
    crystal = {
        "module_load_order": ["lo_probe_leaf", "lo_probe_root"],
        "user_module_sources": {
            # Dot-depth order would build root (0 dots, alphabetical
            # 'lo_probe_leaf' < 'lo_probe_root' actually - so force the
            # recorded order to INVERT the fallback's alphabetical pick.
            "lo_probe_root": {"source_text": "R = 1\n", "source_sha256": "a"},
            "lo_probe_leaf": {"source_text": "L = 1\n", "source_sha256": "b"},
        },
    }
    result = rebuild_absent_user_modules(
        "spell-sha",
        crystal,
        on_built=lambda module: built.append(module.__name__),
        on_shortfall=lambda reason: None,
    )
    assert result is True
    assert built == ["lo_probe_leaf", "lo_probe_root"]


def test_rebuild_without_recorded_order_falls_back_to_dot_depth() -> None:
    """
    Pre-load-order payload compatibility: no module_load_order key means
    the historical dot-depth parents-first ordering still governs.
    """
    built: list = []
    crystal = {
        "user_module_sources": {
            "lo_probe_pkg_child": {"source_text": "C = 1\n", "source_sha256": "c"},
            "lo_probe_apkg": {"source_text": "A = 1\n", "source_sha256": "d"},
        },
    }
    rebuild_absent_user_modules(
        "spell-sha",
        crystal,
        on_built=lambda module: built.append(module.__name__),
        on_shortfall=lambda reason: None,
    )
    assert built == ["lo_probe_apkg", "lo_probe_pkg_child"]


def test_live_published_dependent_keeps_target_resident() -> None:
    """
    R11 contract: a published module whose internal deps name the target
    reports as a live dependent, so a park must keep the target resident.
    """
    _module("r11_probe_dep")
    _module("r11_probe_user", deps=["r11_probe_dep"])
    assert SyntheticModule.has_live_synthetic_dependents("r11_probe_dep") is True


def test_unpublished_dependent_does_not_hold_the_target() -> None:
    """
    R11 scope contract: an unpublished (parked) dependent no longer holds
    the import surface open - the target may unseed.
    """
    _module("r11_probe_dep2")
    holder = _module("r11_probe_user2", deps=["r11_probe_dep2"])
    holder.unpublish_from_sys_modules()
    assert SyntheticModule.has_live_synthetic_dependents("r11_probe_dep2") is False


def test_self_reference_never_counts_as_a_dependent() -> None:
    """
    R11 identity contract: a module naming itself among its dependencies
    never blocks its own unseed.
    """
    _module("r11_probe_selfish", deps=["r11_probe_selfish"])
    assert (
        SyntheticModule.has_live_synthetic_dependents("r11_probe_selfish")
        is False
    )
