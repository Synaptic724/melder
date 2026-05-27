from typing import Any, Dict, List

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


def test_release_without_matching_acquire_raises() -> None:
    """
    Releasing without an in-use object count should raise.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=10,
        time_func=clock,
    )

    try:
        pool.release({"id": 1, "prepared_tag": None, "reset_count": 0})
    except RuntimeError:
        return
    raise AssertionError("Expected RuntimeError when release has no in-use object.")


def test_acquire_stretches_target_when_demand_exceeds_capacity() -> None:
    """
    Acquire should stretch target idle once demand exceeds prepared capacity.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        stretch_percent=50,
        max_idle=10,
        time_func=clock,
    )

    first = pool.acquire()
    second = pool.acquire()
    third = pool.acquire()

    assert first["id"] == 1
    assert second["id"] == 2
    assert third["id"] == 3
    assert pool.target_idle == 3
    assert pool.in_use_count == 3


def test_stretch_caps_at_max_idle() -> None:
    """
    Stretch should never increase target idle beyond max_idle.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        stretch_percent=100,
        max_idle=4,
        time_func=clock,
    )

    pool.acquire()
    pool.acquire()
    pool.acquire()
    pool.acquire()
    pool.acquire()

    assert pool.target_idle == 4


def test_release_destroys_excess_when_idle_already_full() -> None:
    """
    Release should destroy returned objects once idle retention is full.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=1,
        max_idle=1,
        time_func=clock,
    )
    first = pool.acquire()
    second = pool.acquire()

    pool.release(first)
    pool.release(second)

    assert pool.idle_count == 1
    assert pool.destroyed_ids == [2]


def test_no_decay_before_cooldown_elapses() -> None:
    """
    Decay should not start before settle time has elapsed.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        stretch_percent=50,
        settle_time_seconds=10.0,
        decay_percent_per_interval=25,
        decay_interval_seconds=5.0,
        max_idle=10,
        time_func=clock,
    )

    pool.acquire()
    pool.acquire()
    pool.acquire()
    assert pool.target_idle == 3

    clock.value = 9.0
    returned = {"id": 999, "prepared_tag": None, "reset_count": 0}
    pool.release(returned)

    assert pool.target_idle == 3


def test_decay_reduces_target_after_cooldown() -> None:
    """
    Decay should reduce the target idle toward baseline after cooldown.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=2,
        stretch_percent=50,
        settle_time_seconds=10.0,
        decay_percent_per_interval=25,
        decay_interval_seconds=5.0,
        max_idle=10,
        time_func=clock,
    )

    pool.acquire()
    pool.acquire()
    pool.acquire()
    assert pool.target_idle == 3

    clock.value = 16.0
    pool.release({"id": 999, "prepared_tag": None, "reset_count": 0})

    assert pool.target_idle == 2


def test_decay_applies_multiple_intervals() -> None:
    """
    Decay should apply multiple steps when several intervals have elapsed.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=10,
        stretch_percent=100,
        settle_time_seconds=10.0,
        decay_percent_per_interval=10,
        decay_interval_seconds=5.0,
        max_idle=100,
        time_func=clock,
    )

    for _ in range(11):
        pool.acquire()
    assert pool.target_idle == 20

    clock.value = 31.0
    pool.release({"id": 999, "prepared_tag": None, "reset_count": 0})

    assert pool.target_idle == 13


def test_decay_never_drops_below_baseline() -> None:
    """
    Decay should stop at baseline_idle even after long quiet periods.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        baseline_idle=3,
        stretch_percent=100,
        settle_time_seconds=1.0,
        decay_percent_per_interval=50,
        decay_interval_seconds=1.0,
        max_idle=50,
        time_func=clock,
    )

    for _ in range(4):
        pool.acquire()
    assert pool.target_idle == 6

    clock.value = 100.0
    pool.release({"id": 999, "prepared_tag": None, "reset_count": 0})

    assert pool.target_idle == 3


def test_disabled_pool_destroys_on_release() -> None:
    """
    Disabled pools should destroy returned objects instead of retaining them.
    """
    clock = _Clock()
    pool = _TestElasticPool(
        enabled=False,
        baseline_idle=2,
        max_idle=10,
        time_func=clock,
    )
    obj = pool.acquire()

    pool.release(obj)

    assert pool.idle_count == 0
    assert pool.destroyed_ids == [1]


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

    assert snapshot["enabled"] is True
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