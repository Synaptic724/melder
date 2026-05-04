import sys

import pytest

from tests.experimentation import (
    importlib_synthetic_circular_dependency_testbench as importlib_cycle_bench,
)
from tests.experimentation import (
    melder_bind_dropped_synthetic_dependency_testbench as bind_drop_bench,
)
from tests.experimentation import (
    synthetic_module_import_testbench as import_bench,
)
from tests.experimentation import (
    unittest_synthetic_module_edge_cases_testbench as edge_bench,
)
from tests.experimentation import (
    unittest_synthetic_module_testbench as unittest_bench,
)


def _assert_prefix_absent(prefix: str) -> None:
    """
    Assert one dotted-name prefix is absent from `sys.modules`.
    """
    for module_name in list(sys.modules.keys()):
        assert not (
            module_name == prefix or module_name.startswith(prefix + ".")
        )


INTEGRATION_CASES = (
    {
        "case_id": "manual_materialization_graph",
        "runner": import_bench._run_manual_materialization_bench,
        "cleanup": lambda: _assert_prefix_absent("synthetic_pkg"),
    },
    {
        "case_id": "importlib_loader_graph",
        "runner": import_bench._run_importlib_loader_bench,
        "cleanup": lambda: _assert_prefix_absent("synthetic_pkg"),
    },
    {
        "case_id": "unittest_direct_module",
        "runner": unittest_bench._direct_module_object_experiment,
        "cleanup": lambda: (
            _assert_prefix_absent("synthetic_ut_helper"),
            _assert_prefix_absent("synthetic_ut_case"),
        ),
    },
    {
        "case_id": "unittest_import_by_name",
        "runner": unittest_bench._import_by_name_graph_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_ut_pkg"),
    },
    {
        "case_id": "unittest_patch_sibling",
        "runner": unittest_bench._mock_patch_sibling_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_ut_patch_pkg"),
    },
    {
        "case_id": "unittest_relative_imports",
        "runner": unittest_bench._relative_imports_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_ut_rel"),
    },
    {
        "case_id": "unittest_lifecycle_hooks",
        "runner": unittest_bench._lifecycle_hooks_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_ut_lifecycle"),
    },
    {
        "case_id": "edge_circular_imports",
        "runner": edge_bench._circular_import_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_edge_circular"),
    },
    {
        "case_id": "dropped_dependency_eager",
        "runner": bind_drop_bench._eager_dependency_capture_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_bind_case_eager"),
    },
    {
        "case_id": "dropped_dependency_lazy",
        "runner": bind_drop_bench._lazy_dependency_import_experiment,
        "cleanup": lambda: _assert_prefix_absent("synthetic_bind_case_lazy"),
    },
)


def _integration_case_id(case) -> str:
    """
    Return the stable pytest id for one integration case.
    """
    return case["case_id"]


@pytest.fixture(params=INTEGRATION_CASES, ids=_integration_case_id)
def synthetic_module_integration_case(request):
    """
    Provide one integration-level synthetic-module experiment case.
    """
    return request.param


def test_integration_synthetic_module_case_executes_successfully(
        synthetic_module_integration_case,
) -> None:
    """
    Verify each integration case runs without semantic failure.
    """
    synthetic_module_integration_case["runner"]()


def test_integration_synthetic_module_case_is_repeatable(
        synthetic_module_integration_case,
) -> None:
    """
    Verify each integration case can run twice back-to-back.
    """
    synthetic_module_integration_case["runner"]()
    synthetic_module_integration_case["runner"]()


def test_integration_synthetic_module_case_cleans_live_modules(
        synthetic_module_integration_case,
) -> None:
    """
    Verify each integration case leaves no stale live modules behind.
    """
    synthetic_module_integration_case["runner"]()
    synthetic_module_integration_case["cleanup"]()


def test_integration_synthetic_module_case_leaves_meta_path_clean(
        synthetic_module_integration_case,
) -> None:
    """
    Verify each integration case restores `sys.meta_path`.
    """
    before = list(sys.meta_path)
    synthetic_module_integration_case["runner"]()
    after = list(sys.meta_path)
    assert after == before
