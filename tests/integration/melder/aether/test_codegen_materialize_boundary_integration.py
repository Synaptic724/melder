"""
Integration contract (D-20): `materialize_codegen` never replaces or shadows a live module, and every exit leaves
`sys.modules` and the parent package attribute as found.

Under every codegen posture the verb refuses a name already in `sys.modules`, a name under the protected core root
`melder`, a standard-library name and an installed top-level import name; a frame's `materialize_modules` rule
narrows the names further. Materialized code runs with the room's filtered builtins. These are policy checks in the
room's own process - defence in depth, not isolation.

Runs only on 3.14t (melder package root import chain).
"""
import importlib
import importlib.metadata
import sys
from typing import TYPE_CHECKING, Iterator, List, Optional, Tuple

import pytest

from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.rift.command_system.codegen_command_system import CodegenCommandSystem

_MATERIALIZED_PREFIXES: List[str] = []


@pytest.fixture(autouse=True)
def isolated_runtime() -> Iterator[None]:
    """
    Run each test against fresh runtime singletons and tear down what it materialized.

    Yields:
        None.
    """
    from melder.crystallizer.synthetic_module import SyntheticModule

    reset_runtime_singletons()
    _MATERIALIZED_PREFIXES.clear()
    yield
    for prefix in _MATERIALIZED_PREFIXES:
        names = sorted(
            (name for name in list(SyntheticModule._registered_modules_by_name)
             if name == prefix or name.startswith(prefix + ".")),
            key=len,
            reverse=True,
        )
        for name in names:
            module = SyntheticModule._registered_modules_by_name.get(name)
            if module is not None and not module.cleaned:
                module.cleanup()
        for name in [n for n in list(sys.modules) if n == prefix or n.startswith(prefix + ".")]:
            if isinstance(sys.modules.get(name), SyntheticModule):
                sys.modules.pop(name, None)
    reset_runtime_singletons()


def _codegen_room(
        profile_name: str,
        *,
        allowed_roots: Tuple[str, ...] = tuple(),
        denied_roots: Tuple[str, ...] = tuple(),
) -> Tuple["Conduit", "CodegenCommandSystem"]:
    """
    Open a codegen room on frame "ops" under one standard codegen profile, optionally with generation rules.

    Args:
        profile_name: Standard codegen profile.
        allowed_roots: Roots for a `materialize_modules` allow rule (none when empty).
        denied_roots: Roots for a `materialize_modules` deny rule (none when empty).

    Returns:
        Tuple[Conduit, CodegenCommandSystem]: The frame's root conduit and the room's command system.
    """
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    change = nexus.get_frame_acl_builder("ops").begin_codegen_change(reason="materialize_boundary")
    change.use_profile(profile_name)
    if allowed_roots:
        change.allow_materialize_module_roots(*allowed_roots)
    if denied_roots:
        change.deny_materialize_module_roots(*denied_roots)
    change.commit_change()
    rift.create_frame_link("ops")
    return conduit, rift.space.command_system


def _materialize(
        profile_name: str,
        module_name: str,
        code: str,
        **rules: Tuple[str, ...],
) -> dict:
    """
    Materialize one module in a fresh room and return the verb's payload.
    """
    _MATERIALIZED_PREFIXES.append(module_name.split(".")[0])
    conduit, command_system = _codegen_room(profile_name, **rules)
    try:
        return command_system.materialize_codegen(code, module_name=module_name, frame_name="ops")
    finally:
        conduit.cleanup()
        reset_runtime_singletons()


def _snapshot(module_name: str) -> Tuple[Optional[object], Optional[object]]:
    """
    Return the module `sys.modules` holds under the name, and the parent package's attribute for it.
    """
    parent_name, _, child = module_name.rpartition(".")
    parent = sys.modules.get(parent_name) if parent_name else None
    return sys.modules.get(module_name), (getattr(parent, child, None) if parent is not None else None)


@pytest.mark.parametrize("profile_name", ["safe", "hybrid", "full_access"])
@pytest.mark.parametrize(
    "module_name",
    ["melder.aether.spellbook.bind.bind", "csv", "json", "pytest"],
)
def test_materializing_over_a_loaded_module_is_refused_and_leaves_it_in_place(
        profile_name: str,
        module_name: str,
) -> None:
    """
    Contract (N11): a name already in `sys.modules` - a core module, a stdlib one, an installed one - is refused
    before anything is published; `sys.modules` and the parent attribute still hold the original.
    """
    importlib.import_module(module_name)
    before = _snapshot(module_name)

    payload = _materialize(profile_name, module_name, "Bind = None\n")

    assert payload["materialized"] is False
    assert "already loaded" in payload["refusal"]
    assert module_name in payload["refusal"]
    after = _snapshot(module_name)
    assert after[0] is before[0]
    assert after[1] is before[1]


@pytest.mark.parametrize("profile_name", ["safe", "hybrid", "full_access"])
def test_a_new_name_under_the_protected_core_root_is_refused(profile_name: str) -> None:
    """
    Contract (N11): `melder.injected_probe` - not loaded - is refused as a name under the protected core root.
    """
    payload = _materialize(profile_name, "melder.injected_probe", "value = 1\n")

    assert payload["materialized"] is False
    assert "protected core root 'melder'" in payload["refusal"]
    assert "melder.injected_probe" not in sys.modules
    assert not hasattr(sys.modules["melder"], "injected_probe")


def test_an_unimported_standard_library_name_is_refused() -> None:
    """
    Contract (N11): a standard-library name nobody imported yet is refused all the same.
    """
    name = next(
        n for n in sorted(sys.stdlib_module_names)
        if n.isidentifier() and not n.startswith("_") and n not in sys.modules
    )

    payload = _materialize("hybrid", name, "value = 1\n")

    assert payload["materialized"] is False
    assert "standard-library" in payload["refusal"]
    assert name not in sys.modules


def test_an_unimported_installed_import_name_is_refused() -> None:
    """
    Contract (N11): an installed distribution's top-level import name nobody imported yet is refused.
    """
    candidates = sorted(
        n for n in importlib.metadata.packages_distributions()
        if n.isidentifier() and not n.startswith("_") and n not in sys.modules
        and n not in sys.stdlib_module_names and n != "melder"
    )
    if not candidates:
        pytest.skip("every installed import name is already imported in this interpreter")

    payload = _materialize("hybrid", candidates[0], "value = 1\n")

    assert payload["materialized"] is False
    assert "installed import name" in payload["refusal"]
    assert candidates[0] not in sys.modules


@pytest.mark.parametrize("profile_name", ["safe", "hybrid"])
def test_a_new_name_with_no_namespace_rule_still_materializes(profile_name: str) -> None:
    """
    Contract (the owner's no-rule default): with no `materialize_modules` rule a new, unclaimed name materializes.
    """
    payload = _materialize(profile_name, "d20_new_tool_probe", "def answer():\n    return 42\n")

    assert payload["materialized"] is True
    assert importlib.import_module("d20_new_tool_probe").answer() == 42


def test_a_failed_materialize_leaves_no_module_and_no_parent_shell() -> None:
    """
    Contract (R6): a materialize whose exec raises leaves `sys.modules` exactly as before - the module and the
    parent shell the call created are both gone.
    """
    with pytest.raises(ValueError, match="d20 boom"):
        _materialize("hybrid", "d20_failpkg_probe.child", "value = 1\nraise ValueError('d20 boom')\n")

    assert "d20_failpkg_probe.child" not in sys.modules
    assert "d20_failpkg_probe" not in sys.modules


def test_a_declared_namespace_rule_narrows_materialize_to_its_roots() -> None:
    """
    Contract (C1.4): a frame's allow rule admits names under its roots and refuses every other new name.
    """
    inside = _materialize(
        "hybrid", "d20_gen_probe.tool", "value = 1\n", allowed_roots=("d20_gen_probe",),
    )
    outside = _materialize(
        "hybrid", "d20_other_probe", "value = 1\n", allowed_roots=("d20_gen_probe",),
    )

    assert inside["materialized"] is True
    assert outside["materialized"] is False
    assert "outside this frame's generation namespace" in outside["refusal"]
    assert "d20_other_probe" not in sys.modules


def test_a_denied_generation_root_is_refused() -> None:
    """
    Contract (C1.4): a frame's deny rule refuses names under its roots.
    """
    payload = _materialize("hybrid", "d20_secret_probe.x", "value = 1\n", denied_roots=("d20_secret_probe",))

    assert payload["materialized"] is False
    assert "denied generation root 'd20_secret_probe'" in payload["refusal"]
    assert "d20_secret_probe" not in sys.modules


def test_materialized_code_runs_with_the_rooms_filtered_builtins() -> None:
    """
    Contract (the owner's builtins decision): under hybrid the module's builtins lack `open` and its `__import__`
    is the room's root-checking wrapper; under full_access `open` is there.
    """
    _materialize("hybrid", "d20_builtins_probe", "value = 1\n")
    hybrid_builtins = sys.modules["d20_builtins_probe"].__dict__["__builtins__"]
    _materialize("full_access", "d20_builtins_full_probe", "value = 1\n")
    full_builtins = sys.modules["d20_builtins_full_probe"].__dict__["__builtins__"]

    assert isinstance(hybrid_builtins, dict)
    assert "open" not in hybrid_builtins
    with pytest.raises(ImportError, match="subprocess"):
        hybrid_builtins["__import__"]("subprocess")
    assert "open" in full_builtins
