"""Write S6 part A's unit tests (red first): the bind fingerprint, the pool's rebind, the store's rebind ordering.

Run from the repository root:  python3 context_compass/artifacts/correctness_defects_20261017/scripts/s6_part_a_unit_tests.py [--dry-run]
Each replacement must match exactly once; appended blocks go at the end of their file.
"""
import pathlib
import sys

DRY = "--dry-run" in sys.argv
writes = {}


def load(path):
    p = pathlib.Path(path)
    if p not in writes:
        writes[p] = p.read_text(encoding="utf-8")
    return p


def sub(path, old, new):
    p = load(path)
    assert writes[p].count(old) == 1, (path, old[:90], writes[p].count(old))
    writes[p] = writes[p].replace(old, new, 1)


def append(path, block):
    p = load(path)
    writes[p] = writes[p].rstrip("\n") + "\n" + block


BIND = "tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py"
POOL = "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py"
POOL_MT = "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py"
STORE = "tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py"

sub(BIND,
    "to the Spell, and adds one fingerprint part for managed bindings only. Every other binding keeps its spell id\n"
    "byte for byte: the literal ids below were computed on 0.2.8241, before the options existed\n"
    "(context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_golden_ids_pre.txt).\n",
    "to the Spell, and never hashes them: they are settings of the one spell, not part of its spell_id (owner ruling,\n"
    "2026-10-17: \"the bind call itself shouldn't impact the actual SHA256\"; 0.2.8242-0.2.8253 appended a `managed:`\n"
    "part, STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool removed it). Every other binding keeps\n"
    "its spell id byte for byte: the literal ids below were computed on 0.2.8241, before the options existed\n"
    "(context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_golden_ids_pre.txt).\n")

sub(BIND,
    '''def test_the_managed_part_is_appended_after_the_existence_in_its_documented_form() -> None:
    """`managed:<mode>:<limit>:<timeout>:<names>` closes the hash input of a managed binding."""
    assert _managed_key("") == GOLDEN_MANAGED_WITHOUT_PART
    assert Bind.sha256_profile(
        golden_class_profile(), spell_name="Pooled", existence=Existence.managed_spell_quantity,
        managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=256,
    ) == _managed_key("managed:elastic:256::")
    assert Bind.sha256_profile(
        golden_class_profile(), spell_name="Pooled", existence=Existence.managed_spell_quantity,
        managed_spell_mode=ManagedSpellMode.queue, managed_spell_limit=3, managed_spell_timeout_seconds=0.5,
        managed_spell_reset_methods=("clear", "reset"),
    ) == _managed_key("managed:queue:3:0.5:clear,reset")


def test_without_a_mode_no_managed_part_is_hashed() -> None:
    """The part needs a mode: limit, timeout and names alone leave the id as it was."""
    assert Bind.sha256_profile(
        golden_class_profile(), spell_name="Pooled", existence=Existence.managed_spell_quantity,
        managed_spell_limit=9, managed_spell_timeout_seconds=1.0, managed_spell_reset_methods=("reset",),
    ) == GOLDEN_MANAGED_WITHOUT_PART


def test_each_managed_option_changes_the_spell_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mode, limit, timeout and reset names (and their order) each move the id; the default differs from 0.2.8241."""
''',
    '''def test_a_managed_binding_hashes_the_inputs_every_binding_hashes() -> None:
    """No settings part: a managed id is the documented key of its profile, name and existence (0.2.8254)."""
    assert Bind.sha256_profile(
        golden_class_profile(), spell_name="Pooled", existence=Existence.managed_spell_quantity,
    ) == _managed_key("") == GOLDEN_MANAGED_WITHOUT_PART


def test_managed_settings_do_not_change_the_spell_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mode, limit, timeout and reset names (in any order) give one spell_id: the managed id with no settings."""
''')
sub(BIND,
    '''    ids = [bind_with(monkeypatch, Existence.managed_spell_quantity, **variant).kwargs["spell_id"] for variant in variants]
    assert len(set(ids)) == len(ids)
    assert GOLDEN_MANAGED_WITHOUT_PART not in ids
''',
    '''    ids = {bind_with(monkeypatch, Existence.managed_spell_quantity, **variant).kwargs["spell_id"] for variant in variants}
    assert ids == {
        Bind.sha256_profile(golden_class_profile(), spell_name="PooledTarget", existence=Existence.managed_spell_quantity)
    }
''')
sub(BIND,
    '''def test_spell_id_inspector_matches_the_bind_fingerprint_for_a_managed_class() -> None:
    """The read-only inspector normalizes the options exactly as bind does."""
    profile = SpellGeneralProfile.create_from_target(PooledTarget)
    try:
        expected = Bind.sha256_profile(
            profile.binding_profile, spell_name="PooledTarget", existence=Existence.managed_spell_quantity,
            managed_spell_mode=ManagedSpellMode.queue, managed_spell_limit=2, managed_spell_timeout_seconds=1.5,
            managed_spell_reset_methods=("reset",),
        )
    finally:
        profile.cleanup()
    assert Bind.spell_id_inspector(
        PooledTarget, spell_name="PooledTarget", existence=Existence.managed_spell_quantity,
        managed_spell_mode="queue", managed_spell_limit=2, managed_spell_timeout_seconds=1.5,
        managed_spell_reset_methods=["reset"],
    ) == expected
''',
    '''def test_spell_id_inspector_matches_the_bind_fingerprint_for_a_managed_class() -> None:
    """The read-only inspector checks the settings as bind does and, like bind, does not hash them."""
    profile = SpellGeneralProfile.create_from_target(PooledTarget)
    try:
        expected = Bind.sha256_profile(
            profile.binding_profile, spell_name="PooledTarget", existence=Existence.managed_spell_quantity,
        )
    finally:
        profile.cleanup()
    for settings in (
            {},
            {
                "managed_spell_mode": "queue", "managed_spell_limit": 2, "managed_spell_timeout_seconds": 1.5,
                "managed_spell_reset_methods": ["reset"],
            },
    ):
        assert Bind.spell_id_inspector(
            PooledTarget, spell_name="PooledTarget", existence=Existence.managed_spell_quantity, **settings,
        ) == expected
''')

append(POOL, '''

# --- a rebind with other settings (STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool) -----------

def test_a_rebind_with_equal_settings_keeps_the_retention_state() -> None:
    """Equal settings re-point the Spell and keep the stretched target, the count and every idle object."""
    pool = _pool()
    log: List[str] = []
    objects = [_lease(pool, lambda label=f"o{n}": _Pooled(label, log)) for n in range(30)]
    for obj in objects:
        pool.put_back(obj)
    stretched = pool.target_idle
    assert stretched > pool.baseline_idle
    rebound = _SpellStub()
    pool._rebind_spell(rebound)
    assert pool.spell is rebound
    assert (pool.target_idle, pool.count, pool.idle_count, log) == (stretched, 30, 30, [])


def test_a_rebind_with_a_higher_limit_lets_the_pool_build_again() -> None:
    """limited_quantity 1 -> 2: the object out stays counted and one more can be built."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=1)
    log: List[str] = []
    first = _lease(pool, lambda: _Pooled("a", log))
    with pytest.raises(ManagedSpellExhaustedError):
        pool.reserve()
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.limited_quantity, limit=2))
    assert (pool.limit, pool.count, pool.baseline_idle, pool.max_idle) == (2, 1, 2, 2)
    second = _lease(pool, lambda: _Pooled("b", log))
    assert second is not first
    assert pool.count == 2
    pool.put_back(first)
    pool.put_back(second)
    assert (pool.count, pool.idle_count, log) == (2, 2, [])


def test_a_rebind_to_a_smaller_limit_keeps_every_object_alive_and_counted() -> None:
    """limited_quantity 3 -> 1: nothing is destroyed at the rebind; releases above the new capacity evict."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=3)
    log: List[str] = []
    objects = [_lease(pool, lambda label=f"o{n}": _Pooled(label, log)) for n in range(3)]
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.limited_quantity, limit=1))
    assert (pool.limit, pool.count, log) == (1, 3, [])
    with pytest.raises(ManagedSpellExhaustedError):
        pool.reserve()
    for obj in objects:
        pool.put_back(obj)
    assert (pool.count, pool.idle_count) == (1, 1)
    assert log == ["close:o0", "close:o1"]


def test_a_rebind_from_elastic_to_limited_quantity_fixes_the_band_at_the_limit() -> None:
    """elastic (limit 256) -> limited_quantity 4: baseline, ceiling and target all become 4."""
    pool = _pool()
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.limited_quantity, limit=4))
    assert (pool.mode, pool.limit, pool.baseline_idle, pool.max_idle, pool.target_idle) == (
        ManagedSpellMode.limited_quantity, 4, 4, 4, 4,
    )


def test_a_rebind_to_elastic_sizes_the_band_like_a_new_elastic_pool() -> None:
    """limited_quantity 2 -> elastic limit 100: the band a fresh elastic pool of limit 100 gets."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=2)
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.elastic, limit=100))
    fresh = _pool(limit=100)
    assert (pool.baseline_idle, pool.max_idle, pool.target_idle) == (
        fresh.baseline_idle, fresh.max_idle, fresh.target_idle,
    ) == (20, 100, 20)


def test_a_rebind_that_raises_a_queue_limit_wakes_a_waiter_into_the_new_place() -> None:
    """A queue lease waiting at limit 1 gets a place when a rebind raises the limit to 2."""
    pool = _pool(mode=ManagedSpellMode.queue, limit=1, timeout=5.0)
    log: List[str] = []
    _lease(pool, lambda: _Pooled("a", log))
    thread, outcome = _run_in_thread(pool.reserve)
    _wait_for_waiter(pool)
    assert thread.is_alive()
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.queue, limit=2, timeout=5.0))
    thread.join(timeout=2.0)
    assert not thread.is_alive()
    assert outcome == {"result": None}
    assert pool.count == 2


def test_a_rebind_to_queue_makes_a_lease_at_the_limit_wait_for_a_release() -> None:
    """limited_quantity -> queue: at the limit a lease waits for the next release instead of refusing."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=1)
    log: List[str] = []
    first = _lease(pool, lambda: _Pooled("a", log))
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.queue, limit=1, timeout=5.0))
    thread, outcome = _run_in_thread(pool.reserve)
    _wait_for_waiter(pool)
    assert thread.is_alive()
    pool.put_back(first)
    thread.join(timeout=2.0)
    assert not thread.is_alive()
    assert outcome == {"result": first}


def test_a_rebind_changes_the_reset_names_a_release_runs() -> None:
    """A release after the rebind runs the new reset names."""
    pool = _pool(resets=("reset",))
    log: List[str] = []
    obj = _lease(pool, lambda: _Pooled("a", log))
    pool._rebind_spell(_SpellStub(resets=("flush",)))
    pool.put_back(obj)
    assert (pool.reset_method_names, log) == (("flush",), ["flush:a"])


def test_describe_reports_the_settings_a_rebind_gave() -> None:
    """The snapshot shows the current Spell's settings."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=1)
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.queue, limit=3, timeout=2.0, resets=("reset",)))
    snapshot = pool.describe()
    assert (snapshot["mode"], snapshot["limit"], snapshot["timeout_seconds"], snapshot["reset_method_names"]) == (
        "queue", 3, 2.0, ["reset"],
    )


def test_a_rebind_of_a_torn_down_pool_changes_nothing() -> None:
    """A pool torn down meanwhile keeps its tombstone settings and stays retired."""
    pool = _pool(mode=ManagedSpellMode.limited_quantity, limit=1)
    pool.cleanup()
    pool._rebind_spell(_SpellStub(mode=ManagedSpellMode.limited_quantity, limit=5))
    assert pool.limit == 1
    assert pool._spell_unless_cleaned() is None
''')

append(POOL_MT, '''

class _CountedWorker:
    """A pooled object counting its builds and its disposals under one class lock."""

    lock = threading.Lock()
    built = 0
    closed = 0

    def __init__(self) -> None:
        """Count one build."""
        with _CountedWorker.lock:
            _CountedWorker.built += 1

    def reset(self) -> None:
        """Nothing to clear."""

    def close(self) -> None:
        """Count one disposal."""
        with _CountedWorker.lock:
            _CountedWorker.closed += 1


def test_rebinds_racing_leases_and_releases_keep_the_count_equal_to_the_objects_alive() -> None:
    """
    A thread that keeps changing the limit (3 <-> 5) under eight leasing threads never breaks the count
    (STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): once everything is back it equals the
    objects built and not destroyed, every one of them idle, and never more than the larger limit.
    """
    _CountedWorker.built = 0
    _CountedWorker.closed = 0
    pool = ManagedSpellQuantity(spell=_SpellStub(ManagedSpellMode.limited_quantity, 3), owner_conduit_id="root")
    start = threading.Barrier(9)
    errors: List[BaseException] = []
    errors_lock = threading.Lock()

    def _leaser() -> None:
        start.wait()
        try:
            for _ in range(300):
                try:
                    obj = pool._idle.pop()
                except IndexError:
                    try:
                        served = pool.reserve()
                    except ManagedSpellExhaustedError:
                        continue
                    obj = _CountedWorker() if served is None else served
                pool.put_back(obj)
        except BaseException as error:
            with errors_lock:
                errors.append(error)

    def _rebinder() -> None:
        start.wait()
        try:
            for n in range(200):
                pool._rebind_spell(_SpellStub(ManagedSpellMode.limited_quantity, 5 if n % 2 == 0 else 3))
        except BaseException as error:
            with errors_lock:
                errors.append(error)

    threads = [threading.Thread(target=_leaser, daemon=True) for _ in range(8)]
    threads.append(threading.Thread(target=_rebinder, daemon=True))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(60.0)
        assert not thread.is_alive(), "a worker hung"
    assert errors == []
    assert pool.count == _CountedWorker.built - _CountedWorker.closed
    assert pool.count == pool.idle_count
    assert pool.count <= 5
''')

sub(STORE, "from collections.abc import Iterator\n", "import threading\nfrom collections.abc import Iterator\n")
append(STORE, '''

def test_ensure_with_new_settings_keeps_the_pool_and_takes_the_settings(store: ConduitCreations) -> None:
    """A rebind under the same spell_id with other settings meets the pool, which takes them (0.2.8254)."""
    first = store.ensure_managed_quantity(_SpellStub(mode=ManagedSpellMode.limited_quantity, limit=1))
    rebound = _SpellStub(mode=ManagedSpellMode.limited_quantity, limit=2)
    second = store.ensure_managed_quantity(rebound)
    assert second is first
    assert (second.limit, second.spell) == (2, rebound)
    assert [entry["spell_id"] for entry in ReleaseManagedSpell().describe(_Probe)] == ["managed-sid"]


def test_ensure_rebinds_an_existing_pool_after_releasing_the_store_lock(
        store: ConduitCreations,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The rebind takes the pool's lock, so it runs with the store lock free: the store lock stays a leaf."""
    store.ensure_managed_quantity(_SpellStub())
    store_lock_free: List[bool] = []
    original = ManagedSpellQuantity._rebind_spell

    def _spy(pool: ManagedSpellQuantity, spell: Any) -> None:
        probe: List[bool] = []

        def _try_store_lock() -> None:
            acquired = store._lock.acquire(timeout=1.0)
            probe.append(acquired)
            if acquired:
                store._lock.release()

        prober = threading.Thread(target=_try_store_lock)
        prober.start()
        prober.join()
        store_lock_free.append(probe[0])
        original(pool, spell)

    monkeypatch.setattr(ManagedSpellQuantity, "_rebind_spell", _spy, raising=True)
    store.ensure_managed_quantity(_SpellStub())
    assert store_lock_free == [True]
''')

for p, text in writes.items():
    if not DRY:
        p.write_text(text, encoding="utf-8")
    print(("checked " if DRY else "wrote ") + str(p))
