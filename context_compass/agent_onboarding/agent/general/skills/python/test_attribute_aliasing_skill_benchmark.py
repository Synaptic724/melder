"""
Skill-owned entrypoint for attribute-aliasing performance benchmarks.

Purpose:
    Expose a stable benchmark command in the skills folder so agents can run
    and challenge hot-path aliasing rules with measured data.

Contract:
    - Reuses benchmark logic from the primary benchmark suite.
    - Prints benchmark tables when executed with ``-s``.
    - Contains no additional benchmark semantics.
"""

from benchmarks.testing_other_di.test_local_alias_vs_direct_attr_perf import (
    test_local_alias_vs_direct_attribute_access_perf as _bench_self_flat,
)
from benchmarks.testing_other_di.test_local_alias_vs_direct_attr_perf import (
    test_local_alias_vs_direct_parameter_attr_access_perf as _bench_param_flat,
)
from benchmarks.testing_other_di.test_local_alias_vs_direct_attr_perf import (
    test_local_alias_vs_direct_parameter_chained_attr_access_perf as _bench_param_chain,
)
from benchmarks.testing_other_di.test_local_alias_vs_direct_attr_perf import (
    test_local_alias_vs_direct_self_chained_attr_access_perf as _bench_self_chain,
)


def test_skill_benchmark_self_flat_alias_vs_direct() -> None:
    """
    Run flat self-attribute alias-vs-direct benchmark.
    """
    _bench_self_flat()


def test_skill_benchmark_param_flat_alias_vs_direct() -> None:
    """
    Run flat parameter-attribute alias-vs-direct benchmark.
    """
    _bench_param_flat()


def test_skill_benchmark_self_chain_alias_vs_direct() -> None:
    """
    Run chained self-attribute alias-vs-direct benchmark.
    """
    _bench_self_chain()


def test_skill_benchmark_param_chain_alias_vs_direct() -> None:
    """
    Run chained parameter-attribute alias-vs-direct benchmark.
    """
    _bench_param_chain()
