"""
Empirically probe cross-thread SpellSpace behavior.

Purpose:
    Validate what actually happens when multiple threads try to use the same
    SpellSpace, both without active-scope propagation and with the same
    SpellSpace forcibly activated in each worker context.

This file is an experiment surface, not production runtime code.
"""

import threading
from queue import Queue
from typing import Any, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _ThreadScopedProbe:
    """
    Minimal unique-per-spell-space service for cross-thread experiments.

    Contract:
        - Zero-arg constructor so the experiment isolates spellspace behavior
          rather than dependency resolution.
        - Identity equality is object identity only.
    """

    def __init__(self) -> None:
        """Construct one probe instance."""
        return None


def _reset_runtime_singletons() -> None:
    """
    Reset the singleton runtime surfaces used by the experiment.

    Contract:
        - Replaces the process-wide Aether singleton.
        - Rebinds Spellbook and Conduit class-level Aether handles.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def _fresh_runtime() -> None:
    """
    Reset runtime singletons before and after each experiment.
    """
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _build_spellspace_runtime() -> Tuple[Spellbook, Conduit, str]:
    """
    Build one dynamic conduit with a unique-per-spell-space probe spell.

    Returns:
        Tuple[Spellbook, Conduit, str]:
            The owning spellbook, the rooted conduit, and the bound spell id.
    """
    configuration = SpellbookConfiguration("spellspace-thread-experiment")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook = Spellbook(
        aetheric_frame="spellspace-thread-experiment",
        configuration=configuration,
    )
    spell_id = spellbook.bind(
        spell=_ThreadScopedProbe,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name="thread_root")
    return spellbook, conduit, spell_id


def _run_workers(
    *,
    worker_count: int,
    worker_fn: Any,
) -> list[Tuple[str, str, Optional[int]]]:
    """
    Run one worker function across a fixed number of threads and collect results.

    Returns:
        list[Tuple[str, str, Optional[int]]]:
            One tuple per worker:
            - `"ok"` or `"err"`
            - payload string (type name or error type)
            - object identity when successful
    """
    results: Queue[Tuple[str, str, Optional[int]]] = Queue()
    barrier = threading.Barrier(worker_count + 1)
    threads: list[threading.Thread] = []

    def runner() -> None:
        """Synchronize worker start and record one result tuple."""
        barrier.wait(timeout=10)
        worker_fn(results)

    for idx in range(worker_count):
        thread = threading.Thread(target=runner, name=f"spellspace-exp-{idx}")
        thread.start()
        threads.append(thread)

    barrier.wait(timeout=10)
    for thread in threads:
        thread.join(timeout=10)
        assert thread.is_alive() is False

    return [results.get_nowait() for _ in range(worker_count)]


def test_spellspace_direct_use_without_any_active_scope_reuses_across_threads() -> None:
    """
    Validate that direct SpellSpace use no longer depends on thread-local active scope.

    Contract:
        - The test creates one SpellSpace but never activates it.
        - Five worker threads try to use the same SpellSpace object directly.
        - Every worker succeeds through the SpellSpace's owned front door.
        - Because all workers share one SpellSpace id, the returned object
          identity collapses to one shared spellspace-scoped instance.
    """
    _spellbook, conduit, spell_id = _build_spellspace_runtime()
    shared_space = conduit.create_spellspace()
    try:
        def worker(results: Queue[Tuple[str, str, Optional[int]]]) -> None:
            """Attempt a direct meld from the worker without any active scope."""
            try:
                obj = shared_space.meld(spell_id=spell_id)
            except Exception as exc:
                results.put(("err", type(exc).__name__, None))
            else:
                results.put(("ok", type(obj).__name__, id(obj)))

        outcomes = _run_workers(worker_count=5, worker_fn=worker)

        assert outcomes
        assert all(kind == "ok" for kind, _payload, _obj_id in outcomes)
        object_ids = {
            obj_id for _kind, _payload, obj_id in outcomes if obj_id is not None
        }
        assert len(object_ids) == 1
    finally:
        shared_space.cleanup()
        conduit.cleanup()


def test_spellspace_active_context_is_not_required_for_spawned_threads() -> None:
    """
    Validate that spawned threads can still use the shared SpellSpace directly.

    Contract:
        - The main thread enters one active spellspace context.
        - Five worker threads are spawned while that context is active.
        - Every worker still succeeds because direct SpellSpace use no longer
          depends on inheriting the conduit's active spellspace stack.
        - The returned object identity still collapses to one shared
          spellspace-scoped instance for the shared SpellSpace id.
    """
    _spellbook, conduit, spell_id = _build_spellspace_runtime()
    try:
        with conduit.enter_spellspace() as shared_space:
            def worker(results: Queue[Tuple[str, str, Optional[int]]]) -> None:
                """Attempt a meld from a spawned worker while the active scope exists."""
                try:
                    obj = shared_space.meld(spell_id=spell_id)
                except Exception as exc:
                    results.put(("err", type(exc).__name__, None))
                else:
                    results.put(("ok", type(obj).__name__, id(obj)))

            outcomes = _run_workers(worker_count=5, worker_fn=worker)

        assert outcomes
        assert all(kind == "ok" for kind, _payload, _obj_id in outcomes)
        object_ids = {
            obj_id for _kind, _payload, obj_id in outcomes if obj_id is not None
        }
        assert len(object_ids) == 1
    finally:
        conduit.cleanup()


def test_spellspace_can_be_forced_active_in_multiple_threads() -> None:
    """
    Validate what happens if each worker forcibly activates the same SpellSpace.

    Contract:
        - Five worker threads explicitly set the conduit spellspace stack to
          the same SpellSpace object before calling meld.
        - If the runtime accepts that forced activation, all workers succeed.
        - Because the spell is unique_per_spell_space and all workers use the
          same spellspace id, the returned object identity should collapse to
          one shared instance if the scope semantics hold under concurrency.
    """
    _spellbook, conduit, spell_id = _build_spellspace_runtime()
    shared_space = conduit.create_spellspace()
    try:
        def worker(results: Queue[Tuple[str, str, Optional[int]]]) -> None:
            """Force the same SpellSpace active in the worker context, then meld."""
            conduit._spellspace_stack.set([shared_space])
            try:
                obj = shared_space.meld(spell_id=spell_id)
            except Exception as exc:
                results.put(("err", type(exc).__name__, None))
            else:
                results.put(("ok", type(obj).__name__, id(obj)))
            finally:
                conduit._spellspace_stack.set([])

        outcomes = _run_workers(worker_count=5, worker_fn=worker)

        assert outcomes
        assert all(kind == "ok" for kind, _payload, _obj_id in outcomes)
        object_ids = {
            obj_id for _kind, _payload, obj_id in outcomes if obj_id is not None
        }
        assert len(object_ids) == 1
    finally:
        shared_space.cleanup()
        conduit.cleanup()
