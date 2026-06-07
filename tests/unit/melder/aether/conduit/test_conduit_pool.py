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


def test_conduit_pool_create_object_returns_none_when_empty() -> None:
    """
    Verify the pool hands back nothing when no retained lesser is idle.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=0,
        max_idle=1,
    )

    acquired = pool.create_object()

    assert acquired is None
    assert pool.in_use_count == 0


def test_conduit_pool_create_object_returns_retained_lesser() -> None:
    """
    Verify the pool reuses one retained lesser conduit shell.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=1,
        max_idle=1,
    )
    pooled = type(
        "_PooledConduitStub",
        (),
        {"permanent_cleanup": lambda self: None},
    )()

    pool.return_lesser_conduit(pooled)
    acquired = pool.create_object()

    assert acquired is pooled
    assert pool.in_use_count == 1
    assert pool.idle_count == 0


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


def test_conduit_pool_fixed_capacity_full_path_skips_decay_clock() -> None:
    """
    Verify a full fixed-capacity pool destroys overflow without clock access.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=1,
        max_idle=1,
    )
    retained = type(
        "_RetainedConduitStub",
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
    overflow = type(
        "_OverflowConduitStub",
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

    pool.return_lesser_conduit(retained)

    def exploding_clock() -> float:
        raise AssertionError("Fixed-capacity full path should not touch the decay clock.")

    pool._time_func = exploding_clock
    pool.return_lesser_conduit(overflow)

    assert pool.idle_count == 1
    assert retained.cleanup_calls == 0
    assert overflow.cleanup_calls == 1
