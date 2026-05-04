import sys

import pytest

from tests.experimentation import (
    physical_to_synthetic_module_swap_semantics_testbench as swap_bench,
)
from tests.experimentation import (
    unittest_synthetic_module_edge_cases_testbench as edge_bench,
)


def _clear_names(*module_names: str) -> None:
    """
    Remove explicit module names from `sys.modules`.
    """
    for module_name in reversed(module_names):
        sys.modules.pop(module_name, None)


def _assert_names_absent(*module_names: str) -> None:
    """
    Assert explicit module names are absent from `sys.modules`.
    """
    for module_name in module_names:
        assert module_name not in sys.modules


def _assert_prefix_absent(prefix: str) -> None:
    """
    Assert one dotted-name prefix is absent from `sys.modules`.
    """
    for module_name in list(sys.modules.keys()):
        assert not (
            module_name == prefix or module_name.startswith(prefix + ".")
        )


def _run_collision_case() -> None:
    """
    Run the collision-authority experiment directly.
    """
    edge_bench._collision_authority_experiment()


def _assert_collision_cleanup() -> None:
    """
    Assert the collision-authority experiment cleaned its live modules.
    """
    _assert_names_absent(
        "synthetic_edge_collision_target",
        "synthetic_edge_duplicate_target",
    )


COMPONENT_CASES = (
    {
        "case_id": "eager_function_retention",
        "runner": swap_bench._eager_from_import_function_retention_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_eager_function"),
    },
    {
        "case_id": "module_object_retention",
        "runner": swap_bench._module_object_retention_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_module_object"),
    },
    {
        "case_id": "lazy_import_rebind",
        "runner": swap_bench._lazy_import_rebinding_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_lazy_import"),
    },
    {
        "case_id": "function_globals_retention",
        "runner": swap_bench._function_globals_retention_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_function_globals"),
    },
    {
        "case_id": "class_method_retention",
        "runner": swap_bench._class_method_retention_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_class_method"),
    },
    {
        "case_id": "importlib_reload_rebind",
        "runner": swap_bench._importlib_reload_rebind_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_reload"),
    },
    {
        "case_id": "nested_submodule_swap",
        "runner": swap_bench._nested_package_submodule_swap_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_nested"),
    },
    {
        "case_id": "existing_instance_coexistence",
        "runner": swap_bench._existing_instance_coexistence_experiment,
        "cleanup": lambda: _assert_prefix_absent("swap_case_instances"),
    },
    {
        "case_id": "collision_authority",
        "runner": _run_collision_case,
        "cleanup": _assert_collision_cleanup,
    },
    {
        "case_id": "file_backed_morph",
        "runner": edge_bench._file_backed_morph_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_edge_morph"),
    },
)


def _component_case_id(case) -> str:
    """
    Return the stable pytest id for one component case.
    """
    return case["case_id"]


@pytest.fixture(params=COMPONENT_CASES, ids=_component_case_id)
def synthetic_module_component_case(request):
    """
    Provide one component-level synthetic-module experiment case.
    """
    return request.param


def test_component_synthetic_module_case_executes_successfully(
        synthetic_module_component_case,
) -> None:
    """
    Verify each component case runs without semantic failure.
    """
    synthetic_module_component_case["runner"]()


def test_component_synthetic_module_case_is_repeatable(
        synthetic_module_component_case,
) -> None:
    """
    Verify each component case can run twice back-to-back.
    """
    synthetic_module_component_case["runner"]()
    synthetic_module_component_case["runner"]()


def test_component_synthetic_module_case_cleans_live_modules(
        synthetic_module_component_case,
) -> None:
    """
    Verify each component case leaves no stale live modules behind.
    """
    synthetic_module_component_case["runner"]()
    synthetic_module_component_case["cleanup"]()


def test_component_synthetic_module_case_leaves_meta_path_clean(
        synthetic_module_component_case,
) -> None:
    """
    Verify each component case restores `sys.meta_path`.
    """
    before = list(sys.meta_path)
    synthetic_module_component_case["runner"]()
    after = list(sys.meta_path)
    assert after == before
