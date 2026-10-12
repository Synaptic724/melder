from typing import Any, Dict, List

import pytest

from melder.utilities.general_base.abstract_elastic_pool import (
    AbstractElasticPool,
)


class _TestElasticPool(AbstractElasticPool[Dict[str, Any]]):
    """
    Concrete test pool used to validate abstract elastic pool mechanics.
    """

    __slots__ = AbstractElasticPool.__slots__ + [
        "_create_counter",
        "created_ids",
        "destroyed_ids",
        "prepared_tags",
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._create_counter: int = 0
        self.created_ids: List[int] = []
        self.destroyed_ids: List[int] = []
        self.prepared_tags: List[Any] = []

    def create_object(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        self._create_counter += 1
        obj = {
            "id": self._create_counter,
            "prepared_tag": None,
            "reset_count": 0,
        }
        self.created_ids.append(obj["id"])
        return obj

    def destroy_object(self, obj: Dict[str, Any]) -> None:
        self.destroyed_ids.append(obj["id"])

    def prepare_object(self, obj: Dict[str, Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        prepared_tag = kwargs.get("prepared_tag")
        obj["prepared_tag"] = prepared_tag
        self.prepared_tags.append(prepared_tag)
        return obj


class _Clock:
    """
    Simple mutable monotonic clock stub for elastic pool tests.
    """

    __slots__ = ["value"]

    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def test_acquire_creates_and_prepares_object() -> None:
    """
    Acquire should create a new object when the idle pool is empty.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=10,
        time_func=clock,
    )

    obj = pool.acquire(prepared_tag="first")

    assert obj["id"] == 1
    assert obj["prepared_tag"] == "first"
    assert pool.in_use_count == 1
    assert pool.idle_count == 0


def test_init_rejects_invalid_numeric_configuration() -> None:
    """
    Constructor should reject invalid pool configuration values.
    """
    clock = _Clock()
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
            _TestElasticPool(time_func=clock, **kwargs)
        except ValueError:
            continue
        raise AssertionError("Expected ValueError for invalid pool kwargs.")


def test_release_retains_object_under_target() -> None:
    """
    Release should retain an object while idle capacity remains.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=10,
        time_func=clock,
    )
    obj = pool.acquire(prepared_tag="first")

    pool.release(obj)

    assert pool.in_use_count == 0
    assert pool.idle_count == 1
    assert pool.destroyed_ids == []
    assert obj["prepared_tag"] == "first"


def test_prepare_object_runs_on_reused_object() -> None:
    """
    Reused objects should still pass through prepare_object on acquire.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=10,
        time_func=clock,
    )
    first = pool.acquire(prepared_tag="one")
    pool.release(first)

    reused = pool.acquire(prepared_tag="two")

    assert reused is first
    assert reused["prepared_tag"] == "two"
    assert pool.prepared_tags == ["one", "two"]


def test_acquire_reuses_retained_object() -> None:
    """
    Acquire should reuse a retained object before creating a new one.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=10,
        time_func=clock,
    )
    first = pool.acquire(prepared_tag="first")
    pool.release(first)

    second = pool.acquire(prepared_tag="second")

    assert second is first
    assert second["id"] == 1
    assert second["prepared_tag"] == "second"
    assert pool.created_ids == [1]


def test_release_without_matching_acquire_retains_when_capacity_allows() -> None:
    """
    Releasing without an in-use object count should not hard-fail the hot path.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=10,
        time_func=clock,
    )

    pool.release({"id": 1, "prepared_tag": None, "reset_count": 0})

    assert pool.in_use_count == 0
    assert pool.idle_count == 1
    assert pool.destroyed_ids == []


def _burst(pool: _TestElasticPool, count: int) -> List[Dict[str, Any]]:
    """
    Take `count` objects at once (every one a miss on an empty pool) and return them all.

    Returns:
        List[Dict[str, Any]]: The objects, in the order they were taken and returned.
    """
    held = [pool.acquire() for _ in range(count)]
    for obj in held:
        pool.release(obj)
    return held


def _cycle(pool: _TestElasticPool) -> None:
    """One ordinary use: take one object (a hit while any is idle) and return it."""
    pool.release(pool.acquire())


def _elastic_pool(clock: _Clock, **overrides: Any) -> _TestElasticPool:
    """Build a pool with baseline 2, max 20, settle 10 s, 20% decay per 5 s, unless overridden."""
    settings: Dict[str, Any] = {
        "baseline_idle": 2,
        "max_idle": 20,
        "settle_time_seconds": 10.0,
        "decay_percent_per_interval": 20,
        "decay_interval_seconds": 5.0,
    }
    settings.update(overrides)
    return _TestElasticPool(time_func=clock, **settings)


def test_miss_records_pressure_without_moving_the_target() -> None:
    """
    A miss builds and records pressure; the target moves only when returns overflow it.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)

    held = [pool.acquire() for _ in range(5)]

    assert [obj["id"] for obj in held] == [1, 2, 3, 4, 5]
    assert pool.target_idle == 2
    assert pool.in_use_count == 5


def test_burst_under_pressure_is_kept_whole() -> None:
    """
    Returns of a burst past the baseline raise the target to the idle count; nothing is destroyed.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)

    _burst(pool, 8)

    assert pool.target_idle == 8
    assert pool.idle_count == 8
    assert pool.destroyed_ids == []


def test_repeat_burst_reuses_every_kept_object() -> None:
    """
    A repeat of a kept burst is served entirely from idle objects.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)
    _burst(pool, 8)

    _burst(pool, 8)

    assert pool.created_ids == [1, 2, 3, 4, 5, 6, 7, 8]
    assert pool.idle_count == 8


def test_stretch_adds_headroom_percent() -> None:
    """
    stretch_percent adds headroom over the idle count the stretching return observed.
    """
    clock = _Clock()
    pool = _elastic_pool(clock, stretch_percent=50)

    _burst(pool, 6)

    assert pool.target_idle == 7
    assert pool.idle_count == 6


def test_stretch_caps_at_max_idle_and_trims_the_rest() -> None:
    """
    A burst past max_idle keeps max_idle objects and destroys the oldest surplus.
    """
    clock = _Clock()
    pool = _elastic_pool(clock, max_idle=4, decay_percent_per_interval=10)

    _burst(pool, 6)

    assert pool.target_idle == 4
    assert pool.idle_count == 4
    assert pool.destroyed_ids == [1, 2]


def test_return_without_pressure_trims_to_the_target() -> None:
    """
    Objects returned past the baseline with no recent miss are trimmed, not kept.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)

    for item_id in range(100, 105):
        pool.release({"id": item_id, "prepared_tag": None, "reset_count": 0})

    assert pool.target_idle == 2
    assert pool.idle_count == 2
    assert pool.destroyed_ids == [100, 101, 102]


def test_no_decay_inside_the_settle_window() -> None:
    """
    The target holds while the last miss is within settle_time_seconds.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)
    _burst(pool, 10)

    clock.value = 9.9
    _cycle(pool)

    assert pool.target_idle == 10
    assert pool.idle_count == 10


def test_decay_one_step_per_interval_after_settling() -> None:
    """
    Once settled, each interval lowers the target by one step of the stretched value and trims the oldest.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)
    _burst(pool, 10)

    clock.value = 10.0
    _cycle(pool)
    assert pool.target_idle == 8
    assert pool.idle_count == 8
    assert pool.destroyed_ids == [1, 2]

    clock.value = 12.0
    _cycle(pool)
    assert pool.target_idle == 8

    clock.value = 15.0
    _cycle(pool)
    assert pool.target_idle == 6
    assert pool.idle_count == 6


def test_decay_catches_up_after_a_long_quiet_period() -> None:
    """
    Steps missed while no return happened apply together; trims stay bounded per return.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)
    _burst(pool, 10)

    clock.value = 100.0
    _cycle(pool)

    assert pool.target_idle == 2
    assert pool.idle_count == 8
    _cycle(pool)
    _cycle(pool)
    _cycle(pool)
    assert pool.idle_count == 2
    assert len(pool.destroyed_ids) == 8


def test_decay_never_drops_below_baseline() -> None:
    """
    Decay stops at baseline_idle however long the pool stayed quiet.
    """
    clock = _Clock()
    pool = _elastic_pool(clock, baseline_idle=3, decay_percent_per_interval=50)
    _burst(pool, 12)

    clock.value = 10_000.0
    for _ in range(6):
        _cycle(pool)

    assert pool.target_idle == 3
    assert pool.idle_count == 3


def test_miss_inside_the_settle_window_postpones_decay() -> None:
    """
    A later miss restarts the settle period, so decay waits a full period after it.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)
    _burst(pool, 10)

    clock.value = 8.0
    _burst(pool, 11)
    assert pool.target_idle == 11

    clock.value = 17.9
    _cycle(pool)
    assert pool.target_idle == 11

    clock.value = 18.0
    _cycle(pool)
    assert pool.target_idle == 9


def test_burst_after_decay_stretches_again() -> None:
    """
    Pressure after a decay raises the target to the new burst.
    """
    clock = _Clock()
    pool = _elastic_pool(clock)
    _burst(pool, 10)
    clock.value = 100.0
    for _ in range(4):
        _cycle(pool)
    assert pool.idle_count == 2

    _burst(pool, 12)

    assert pool.target_idle == 12
    assert pool.idle_count == 12


def test_fixed_capacity_pool_evicts_without_the_clock() -> None:
    """
    max_idle == baseline_idle keeps the one-eviction return: oldest first, no clock read.
    """
    clock = _Clock()
    pool = _TestElasticPool(baseline_idle=1, max_idle=1, time_func=clock)
    first = pool.acquire()
    second = pool.acquire()

    def exploding_clock() -> float:
        raise AssertionError("A fixed-capacity return must not read the clock.")

    pool._time_func = exploding_clock
    pool.release(first)
    pool.release(second)

    assert pool.idle_count == 1
    assert pool.destroyed_ids == [1]


class _FailingDestroyPool(_TestElasticPool):
    """
    Test pool whose destroy_object raises for the ids listed in `fail_ids`.
    """

    __slots__ = ["fail_ids"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fail_ids: List[int] = []

    def destroy_object(self, obj: Dict[str, Any]) -> None:
        if obj["id"] in self.fail_ids:
            raise RuntimeError(f"destroy failed for {obj['id']}")
        super().destroy_object(obj)


def test_destroy_failure_keeps_the_rest_of_the_trim_pooled() -> None:
    """
    A destroy that raises propagates; the detached objects after it go back to the idle deque, none is lost.
    """
    clock = _Clock()
    pool = _FailingDestroyPool(
        baseline_idle=0,
        max_idle=10,
        settle_time_seconds=10.0,
        decay_percent_per_interval=100,
        decay_interval_seconds=5.0,
        time_func=clock,
    )
    _burst(pool, 5)
    assert pool.target_idle == 5
    pool.fail_ids.append(2)

    clock.value = 10.0
    obj = pool.acquire()
    with pytest.raises(RuntimeError, match="destroy failed for 2"):
        pool.release(obj)

    assert pool.destroyed_ids == [1]
    assert [item["id"] for item in pool._idle] == [3, 4, 5]


def test_describe_reports_current_pool_state() -> None:
    """
    describe should report a detached snapshot of current policy and counts.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=4,
        stretch_percent=25,
        settle_time_seconds=11.0,
        decay_percent_per_interval=5,
        decay_interval_seconds=7.0,
        max_idle=12,
        time_func=clock,
    )
    pool.acquire(prepared_tag="x")
    snapshot = pool.describe()

    assert snapshot["baseline_idle"] == 4
    assert snapshot["target_idle"] == 4
    assert snapshot["max_idle"] == 12
    assert snapshot["idle_count"] == 0
    assert snapshot["in_use_count"] == 1
    assert snapshot["stretch_percent"] == 25
    assert snapshot["settle_time_seconds"] == 11.0
    assert snapshot["decay_percent_per_interval"] == 5
    assert snapshot["decay_interval_seconds"] == 7.0


def test_cleanup_destroys_all_idle_objects() -> None:
    """
    Cleanup should destroy all retained idle objects and retire the pool.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        max_idle=10,
        time_func=clock,
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
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=10,
        time_func=clock,
    )
    obj = pool.acquire()
    pool.release(obj)

    pool.cleanup()
    pool.cleanup()

    assert pool.cleaned is True
    assert pool.destroyed_ids == [1]
