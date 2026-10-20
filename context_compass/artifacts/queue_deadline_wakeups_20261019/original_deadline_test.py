def test_queue_deadline_is_taken_once_across_wakeups() -> None:
    """Wake-ups that free nothing do not restart the wait: the waiter raises at its original deadline."""
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=0.3)
    pool.reserve()
    started = time.monotonic()
    finished: Dict[str, float] = {}

    def _wait() -> None:
        try:
            pool.reserve()
        finally:
            finished["at"] = time.monotonic()

    thread, outcome = _run_in_thread(_wait)
    while thread.is_alive() and time.monotonic() - started < 0.9:
        with pool._condition:
            pool._condition.notify_all()
        time.sleep(0.02)
    thread.join(5.0)
    assert isinstance(outcome["error"], ManagedSpellExhaustedError)
    assert finished["at"] - started < 0.75
