from typing import Any

import pytest

from melder.aether.conduit.conduit_pool import ConduitPool


class _RootConduitStub:
    """Minimal root-conduit stub for ConduitPool unit tests."""

    def __init__(self, conduit_id: str) -> None:
        """Initialize the stub with one stable conduit id."""
        self._id = conduit_id


def test_conduit_pool_exposes_root_conduit_and_id() -> None:
    """
    Verify the pool stores and exposes its owning root conduit surface.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=0,
        max_idle=1,
    )

    assert pool.root_conduit is root
    assert pool.root_conduit_id == "root-1"


def test_conduit_pool_inherits_base_policy_surface() -> None:
    """
    Verify the scaffold still exposes the inherited elastic pool policy state.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=2,
        max_idle=4,
        stretch_percent=50,
        settle_time_seconds=10.0,
        decay_percent_per_interval=25,
        decay_interval_seconds=5.0,
    )

    snapshot = pool.describe()

    assert snapshot["baseline_idle"] == 2
    assert snapshot["max_idle"] == 4
    assert snapshot["stretch_percent"] == 50
    assert snapshot["settle_time_seconds"] == 10.0
    assert snapshot["decay_percent_per_interval"] == 25
    assert snapshot["decay_interval_seconds"] == 5.0


def test_conduit_pool_create_object_is_explicit_placeholder() -> None:
    """
    Verify create_object remains an explicit placeholder until later wiring.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=0,
        max_idle=1,
    )

    with pytest.raises(NotImplementedError, match="not wired yet"):
        pool.create_object()


def test_conduit_pool_destroy_object_calls_permanent_cleanup() -> None:
    """
    Verify destroy_object uses the conduit hard-destroy lane.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=0,
        max_idle=1,
    )
    pooled = type(
        "_PooledConduitStub",
        (),
        {
            "__init__": lambda self: setattr(self, "cleanup_calls", 0),
            "permanent_cleanup": lambda self: setattr(
                self,
                "cleanup_calls",
                self.cleanup_calls + 1,
            ),
        },
    )()

    pool.destroy_object(pooled)

    assert pooled.cleanup_calls == 1
