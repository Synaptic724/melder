from typing import Any, Dict, List

from melder.utilities.general_base.abstract_elastic_pool import (
    AbstractElasticPool,
)


class _TestElasticPool(AbstractElasticPool[Dict[str, Any]]):
    """
    Concrete pool used to validate the coarse burst-holder model.
    """

    __slots__ = AbstractElasticPool.__slots__ + [
        "_create_counter",
        "created_ids",
        "destroyed_ids",
        "prepared_tags",
    ]

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize one concrete test pool with simple integer-tagged shells.
        """
        super().__init__(**kwargs)
        self._create_counter: int = 0
        self.created_ids: List[int] = []
        self.destroyed_ids: List[int] = []
        self.prepared_tags: List[Any] = []

    def create_object(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create one new dictionary-backed shell for the test pool.
        """
        self._create_counter += 1
        obj = {
            "id": self._create_counter,
            "prepared_tag": None,
        }
        self.created_ids.append(obj["id"])
        return obj

    def destroy_object(self, obj: Dict[str, Any]) -> None:
        """
        Record destruction of one test shell.
        """
        self.destroyed_ids.append(obj["id"])

    def prepare_object(
            self,
            obj: Dict[str, Any],
            *args: Any,
            **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Tag one reused shell so tests can prove prepare still ran.
        """
        prepared_tag = kwargs.get("prepared_tag")
        obj["prepared_tag"] = prepared_tag
        self.prepared_tags.append(prepared_tag)
        return obj


def test_acquire_creates_and_prepares_object() -> None:
    """
    Acquire should create and prepare one object on an empty pool.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )

    obj = pool.acquire(prepared_tag="first")

    assert obj["id"] == 1
    assert obj["prepared_tag"] == "first"
    assert pool.in_use_count == 1
    assert pool.idle_count == 0


def test_init_rejects_invalid_numeric_configuration() -> None:
    """
    Constructor should still reject invalid baseline/max combinations.
    """
    invalid_cases = [
        {"baseline_idle": -1},
        {"stretch_percent": -1},
        {"settle_time_seconds": -1.0},
        {"decay_percent_per_interval": -1},
        {"decay_interval_seconds": 0.0},
        {"baseline_idle": 3, "max_idle": 2},
    ]

    for kwargs in invalid_cases:
        try:
            _TestElasticPool(**kwargs)
        except ValueError:
            continue
        raise AssertionError("Expected ValueError for invalid pool kwargs.")


def test_release_retains_object_under_cap() -> None:
    """
    Release should retain a returned shell while idle count remains below cap.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )
    obj = pool.acquire(prepared_tag="first")

    pool.release(obj)

    assert pool.in_use_count == 0
    assert pool.idle_count == 1
    assert pool.destroyed_ids == []


def test_prepare_object_runs_on_reused_object() -> None:
    """
    Reused idle shells should still pass through prepare_object.
    """
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=1,
    )
    first = pool.acquire(prepared_tag="one")
    pool.release(first)

    reused = pool.acquire(prepared_tag="two")

    assert reused is first
    assert reused["prepared_tag"] == "two"
    assert pool.prepared_tags == ["one", "two"]


def test_acquire_reuses_retained_object_before_creating() -> None:
    """
    Acquire should reuse one retained idle shell before allocating another.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )
    first = pool.acquire(prepared_tag="first")
    pool.release(first)

    second = pool.acquire(prepared_tag="second")

    assert second is first
    assert second["id"] == 1
    assert pool.created_ids == [1]


def test_release_without_matching_borrow_is_tolerated() -> None:
    """
    Release should not raise when strict in-use accounting is already at zero.
    """
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=1,
    )

    pool.release({"id": 1, "prepared_tag": None})

    assert pool.idle_count == 1
    assert pool.in_use_count == 0


def test_breach_expands_cap_by_burst_factor() -> None:
    """
    A miss at the current cap should expand the retained ceiling coarsely.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )

    pool.acquire()
    pool.acquire()
    pool.acquire()

    assert pool.target_idle == 8
    assert pool.max_idle == 8
    assert pool.in_use_count == 3
    assert pool.idle_count == 0


def test_reusing_idle_shell_does_not_expand_cap() -> None:
    """
    Reusing an idle shell should not trigger burst expansion.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )
    first = pool.acquire()
    second = pool.acquire()
    pool.release(first)

    reused = pool.acquire()

    assert reused is first
    assert pool.target_idle == 2
    assert pool.in_use_count == 2


def test_release_steps_cap_down_when_borrow_pressure_falls() -> None:
    """
    Release should shrink one floor step after borrowed pressure crosses the
    active shrink mark.
    """
    pool = _TestElasticPool(
        baseline_idle=20,
        max_idle=20,
    )

    borrowed = [pool.acquire() for _ in range(21)]

    assert pool.target_idle == 80
    assert pool.in_use_count == 21

    for index in range(2, 21):
        pool.release(borrowed[index])

    assert pool.in_use_count == 2
    assert pool.target_idle == 40


def test_release_trims_idle_shells_above_new_cap() -> None:
    """
    Shrink should destroy idle shells that no longer fit under the reduced cap.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )

    borrowed = [pool.acquire() for _ in range(3)]
    assert pool.target_idle == 8

    for obj in borrowed:
        pool.release(obj)

    assert pool.target_idle == 2
    assert pool.idle_count == 2
    assert pool.destroyed_ids == [3]


def test_disabled_pool_destroys_on_release() -> None:
    """
    Disabled pools should destroy returned objects instead of retaining them.
    """
    pool = _TestElasticPool(
        enabled=False,
        baseline_idle=2,
        max_idle=2,
    )
    obj = pool.acquire()

    pool.release(obj)

    assert pool.idle_count == 0
    assert pool.destroyed_ids == [1]


def test_describe_reports_current_burst_pool_state() -> None:
    """
    describe should report the current burst-pool state.
    """
    pool = _TestElasticPool(
        baseline_idle=4,
        max_idle=4,
    )
    pool.acquire(prepared_tag="x")
    snapshot = pool.describe()

    assert snapshot["enabled"] is True
    assert snapshot["baseline_idle"] == 4
    assert snapshot["target_idle"] == 4
    assert snapshot["max_idle"] == 4
    assert snapshot["idle_count"] == 0
    assert snapshot["in_use_count"] == 1
    assert snapshot["burst_factor"] == 4
    assert snapshot["shrink_mark"] == 0


def test_cleanup_destroys_all_idle_objects() -> None:
    """
    Cleanup should destroy all retained idle objects and retire the pool.
    """
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=2,
    )
    first = pool.acquire()
    second = pool.acquire()
    pool.release(first)
    pool.release(second)

    pool.cleanup()

    assert pool.cleaned is True
    assert pool.destroyed_ids == [1, 2]


def test_cleanup_is_idempotent() -> None:
    """
    Cleanup should be safe to call repeatedly.
    """
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=1,
    )
    obj = pool.acquire()
    pool.release(obj)

    pool.cleanup()
    pool.cleanup()

    assert pool.cleaned is True
    assert pool.destroyed_ids == [1]
