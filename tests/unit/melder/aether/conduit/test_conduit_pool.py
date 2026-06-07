from melder.aether.conduit.conduit_pool import ConduitPool


class _RootConduitStub:
    """Minimal root-conduit stub for ConduitPool unit tests."""

    def __init__(self, conduit_id: str) -> None:
        """Initialize the stub with one stable conduit id."""
        self._id = conduit_id


def test_conduit_pool_exposes_root_conduit_and_id() -> None:
    """
    The pool should expose the owning root conduit and its stable id.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=40,
        max_idle=40,
    )

    assert pool.root_conduit is root
    assert pool.root_conduit_id == "root-1"


def test_conduit_pool_describe_reports_burst_holder_state() -> None:
    """
    The lesser pool should report the coarse burst-holder state.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=40,
        max_idle=40,
    )

    snapshot = pool.describe()

    assert snapshot["baseline_idle"] == 40
    assert snapshot["target_idle"] == 40
    assert snapshot["max_idle"] == 40
    assert snapshot["burst_factor"] == 4


def test_conduit_pool_create_object_returns_none_on_miss() -> None:
    """
    Holder-only lesser acquire should return None on a miss.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=40,
        max_idle=40,
    )

    acquired = pool.create_object()

    assert acquired is None
    assert pool.in_use_count == 1
    assert pool.idle_count == 0


def test_conduit_pool_create_object_reuses_retained_lesser() -> None:
    """
    Holder-only lesser acquire should reuse one retained shell when available.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=40,
        max_idle=40,
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
    destroy_object should route through the conduit hard-destroy lane.
    """
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=40,
        max_idle=40,
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
