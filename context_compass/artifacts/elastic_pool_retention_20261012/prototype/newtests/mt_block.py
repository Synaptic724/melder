@pytest.mark.parametrize("worker_count", [4, 8])
def test_multithreaded_band_returns_keep_target_within_bounds(worker_count: int) -> None:
    """Concurrent returns into the elastic band with a decay due keep the target within bounds and trim the excess."""
    clock = _Clock(value=100.0)
    pool = _ThreadedElasticPool(
        baseline_idle=2,
        settle_time_seconds=10.0,
        decay_percent_per_interval=25,
        decay_interval_seconds=5.0,
        max_idle=10,
        time_func=clock,
    )
    pool._target_idle = 6
    pool._decay_step = 1
    pool._last_miss_at = 0.0
    pool._next_decay_at = 0.0
    for item_id in range(100, 106):
        pool._idle.append({"id": item_id})

    def worker(index: int) -> None:
        pool.release({"id": 1000 + index})

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert pool.baseline_idle <= pool.target_idle <= 6
    assert pool.idle_count == 6
    assert len(pool.destroyed_ids) == worker_count


@pytest.mark.parametrize("worker_count", [4, 8, 16])
def test_multithreaded_burst_under_pressure_is_kept_whole(worker_count: int) -> None:
    """Objects returned concurrently after a burst of misses are all kept; the target ends at the burst size."""
    clock = _Clock()
    pool = _ThreadedElasticPool(
        baseline_idle=1,
        max_idle=32,
        time_func=clock,
    )
    held = [pool.acquire() for _ in range(worker_count)]

    def worker(index: int) -> None:
        pool.release(held[index])

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert pool.target_idle == worker_count
    assert pool.idle_count == worker_count
    assert pool.destroyed_ids == []
