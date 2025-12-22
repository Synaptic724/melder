from __future__ import annotations

from threading import Barrier, Lock, Thread
from typing import Any, Callable, Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import (
    Depth3Root,
    Depth5Root,
    Depth7Root,
    Depth9Root,
    get_depth_3_classes,
    get_depth_5_classes,
    get_depth_7_classes,
    get_depth_9_classes,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_dynamic_spellbook(*, workers: int = 4) -> Spellbook:
    """
    Purpose:
        Build a spellbook configured for dynamic concurrency tests.
    Contract:
        - Applies dynamic defaults and sets the phase scheduler workers.
    Args:
        workers: Scheduler worker count for the spellbook.
    Returns:
        Spellbook: Configured spellbook instance.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return Spellbook(configuration=configuration)


def _bind_graph(
    spellbook: Spellbook,
    classes: Iterable[type],
    *,
    existence: Existence,
) -> dict[type, str]:
    """
    Purpose:
        Bind a dependency graph into the spellbook for integration tests.
    Contract:
        - Each class is bound with the requested Existence.
        - Returns a mapping of class -> spell_id.
    Args:
        spellbook: Target spellbook for bindings.
        classes: Classes to bind in dependency order.
        existence: Existence mode to apply to each binding.
    Returns:
        dict[type, str]: Mapping of class to spell_id.
    """
    spell_ids: dict[type, str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


def _assert_depth3_root(root: Depth3Root) -> None:
    """
    Purpose:
        Validate Depth3Root dependency wiring for concurrency tests.
    Contract:
        - Leaf dependencies are reused across branches.
        - Leaf markers are stable.
    Args:
        root: Depth3Root instance to validate.
    Returns:
        None.
    Raises:
        AssertionError: If dependency wiring is incorrect.
    """
    assert root.left.left is root.right.left
    assert root.left.right is root.right.right
    assert root.left.left.marker == "L3A"
    assert root.left.right.marker == "L3B"


def _assert_depth5_root(root: Depth5Root) -> None:
    """
    Purpose:
        Validate Depth5Root dependency wiring for concurrency tests.
    Contract:
        - Leaf dependencies are reused across branches.
        - Leaf markers are stable.
    Args:
        root: Depth5Root instance to validate.
    Returns:
        None.
    Raises:
        AssertionError: If dependency wiring is incorrect.
    """
    leaf_a = root.left.left.left.left
    leaf_b = root.left.left.left.right
    assert leaf_a.marker == "L5A"
    assert leaf_b.marker == "L5B"
    assert leaf_a is root.right.left.left.left
    assert leaf_b is root.right.left.left.right


def _assert_depth7_root(root: Depth7Root) -> None:
    """
    Purpose:
        Validate Depth7Root dependency wiring for concurrency tests.
    Contract:
        - Leaf dependencies are reused across branches.
        - Leaf markers are stable.
    Args:
        root: Depth7Root instance to validate.
    Returns:
        None.
    Raises:
        AssertionError: If dependency wiring is incorrect.
    """
    leaf_a = root.left.left.left.left.left.left
    leaf_b = root.left.left.left.left.left.right
    assert leaf_a.marker == "L7A"
    assert leaf_b.marker == "L7B"
    assert leaf_a is root.right.left.left.left.left.left
    assert leaf_b is root.right.left.left.left.left.right


def _assert_depth9_root(root: Depth9Root) -> None:
    """
    Purpose:
        Validate Depth9Root dependency wiring for concurrency tests.
    Contract:
        - Leaf dependencies are reused across branches.
        - Leaf markers are stable.
    Args:
        root: Depth9Root instance to validate.
    Returns:
        None.
    Raises:
        AssertionError: If dependency wiring is incorrect.
    """
    layer2 = root.left
    layer3 = layer2.left
    layer4 = layer3.left
    layer5 = layer4.left
    layer6 = layer5.left
    layer7 = layer6.left
    layer8 = layer7.left
    leaf_a = layer8.left
    leaf_b = layer8.right
    assert leaf_a.marker == "L9A"
    assert leaf_b.marker == "L9B"
    assert leaf_a is root.right.left.left.left.left.left.left.left
    assert leaf_b is root.right.left.left.left.left.left.left.right


def _run_concurrent_melds(
    *,
    tasks: list[tuple[str, Conduit, str, Callable[[Any], None]]],
) -> dict[str, Any]:
    """
    Purpose:
        Execute concurrent melds and capture results for assertions.
    Contract:
        - All tasks run concurrently via a barrier.
        - Any raised exception is surfaced to the caller.
    Args:
        tasks: List of (key, conduit, spell_id, validator) tuples.
    Returns:
        dict[str, Any]: Mapping of key to melded root instance.
    Raises:
        AssertionError: If any worker reports an exception.
    """
    barrier = Barrier(len(tasks))
    lock = Lock()
    results: dict[str, Any] = {}
    errors: list[Exception] = []
    threads: list[Thread] = []

    def worker(
        key: str,
        conduit: Conduit,
        spell_id: str,
        validator: Callable[[Any], None],
    ) -> None:
        """
        Purpose:
            Run a single meld task in a worker thread.
        Contract:
            - Synchronizes via the barrier before melding.
            - Captures exceptions for the caller to assert.
        Args:
            key: Result mapping key.
            conduit: Conduit executing the meld.
            spell_id: Spell id to resolve.
            validator: Root validation function.
        Returns:
            None.
        """
        try:
            barrier.wait(timeout=5)
            root = conduit.meld(spell=spell_id)
            validator(root)
            with lock:
                results[key] = root
        except Exception as exc:
            with lock:
                errors.append(exc)

    for key, conduit, spell_id, validator in tasks:
        threads.append(
            Thread(
                target=worker,
                args=(key, conduit, spell_id, validator),
            )
        )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    return results


def test_conduit_linked_concurrent_meld_across_four_conduits() -> None:
    """
    Purpose:
        Stress concurrent melds across four linked conduits with distinct graphs.
    Contract:
        - Borrowers can contract root spells with dependencies from the owner.
        - Four conduits can meld concurrently without errors.
        - Each root graph resolves and reuses per-conduit dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If melds fail or dependency graphs are invalid.
    """
    owner_book = _make_dynamic_spellbook()
    borrower_books = [
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
    ]
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique_per_conduit,
    )
    depth5_ids = _bind_graph(
        owner_book,
        get_depth_5_classes(),
        existence=Existence.unique_per_conduit,
    )
    depth7_ids = _bind_graph(
        owner_book,
        get_depth_7_classes(),
        existence=Existence.unique_per_conduit,
    )
    depth9_ids = _bind_graph(
        owner_book,
        get_depth_9_classes(),
        existence=Existence.unique_per_conduit,
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrowers = [
        borrower_books[0].conjure(automatic=False, name="borrower-1"),
        borrower_books[1].conjure(automatic=False, name="borrower-2"),
        borrower_books[2].conjure(automatic=False, name="borrower-3"),
    ]

    try:
        for borrower in borrowers:
            owner.link(borrower)

        borrowers[0].add_spell_to_contract(
            spell_id=depth3_ids[Depth3Root],
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )
        borrowers[1].add_spell_to_contract(
            spell_id=depth5_ids[Depth5Root],
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )
        borrowers[2].add_spell_to_contract(
            spell_id=depth7_ids[Depth7Root],
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )

        tasks = [
            ("owner", owner, depth9_ids[Depth9Root], _assert_depth9_root),
            ("borrower-1", borrowers[0], depth3_ids[Depth3Root], _assert_depth3_root),
            ("borrower-2", borrowers[1], depth5_ids[Depth5Root], _assert_depth5_root),
            ("borrower-3", borrowers[2], depth7_ids[Depth7Root], _assert_depth7_root),
        ]
        results = _run_concurrent_melds(tasks=tasks)
        assert len(results) == 4
    finally:
        for borrower in borrowers:
            borrower.cleanup()
        owner.cleanup()


def test_conduit_concurrent_meld_same_conduit_reuses_unique_per_conduit() -> None:
    """
    Purpose:
        Stress concurrent melds in a single conduit for unique_per_conduit.
    Contract:
        - Concurrent melds return the same root instance.
        - The resolved graph is valid for the root type.
    Returns:
        None.
    Raises:
        AssertionError: If melds fail or reuse is violated.
    """
    spellbook = _make_dynamic_spellbook()
    depth3_ids = _bind_graph(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique_per_conduit,
    )
    conduit = spellbook.conjure(name="root")
    barrier = Barrier(4)
    lock = Lock()
    results: list[Depth3Root] = []
    errors: list[Exception] = []

    def worker() -> None:
        """
        Purpose:
            Concurrently meld the same root from one conduit.
        Contract:
            - Captures meld results for reuse assertions.
        Returns:
            None.
        """
        try:
            barrier.wait(timeout=5)
            root = conduit.meld(spell=depth3_ids[Depth3Root])
            _assert_depth3_root(root)
            with lock:
                results.append(root)
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [Thread(target=worker) for _ in range(4)]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert errors == []
        assert len(results) == 4
        assert len({id(root) for root in results}) == 1
    finally:
        conduit.cleanup()


def test_conduit_concurrent_meld_across_linked_conduits_isolated_per_conduit() -> None:
    """
    Purpose:
        Stress concurrent melds across linked conduits for unique_per_conduit.
    Contract:
        - Linked borrowers can meld contracted roots concurrently.
        - Each conduit resolves its own instance for unique_per_conduit.
    Returns:
        None.
    Raises:
        AssertionError: If melds fail or instances leak across conduits.
    """
    owner_book = _make_dynamic_spellbook()
    borrower_books = [
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
    ]
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique_per_conduit,
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrowers = [
        borrower_books[0].conjure(automatic=False, name="borrower-1"),
        borrower_books[1].conjure(automatic=False, name="borrower-2"),
        borrower_books[2].conjure(automatic=False, name="borrower-3"),
    ]
    try:
        for borrower in borrowers:
            owner.link(borrower)
            borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )
        tasks = [
            ("owner", owner, depth3_ids[Depth3Root], _assert_depth3_root),
            ("borrower-1", borrowers[0], depth3_ids[Depth3Root], _assert_depth3_root),
            ("borrower-2", borrowers[1], depth3_ids[Depth3Root], _assert_depth3_root),
            ("borrower-3", borrowers[2], depth3_ids[Depth3Root], _assert_depth3_root),
        ]
        results = _run_concurrent_melds(tasks=tasks)
        instances = {id(instance) for instance in results.values()}
        assert len(instances) == 4
    finally:
        for borrower in borrowers:
            borrower.cleanup()
        owner.cleanup()
