from __future__ import annotations

from threading import Barrier, Lock, Thread
from typing import Any, Callable, Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
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
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
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


def _make_dynamic_spellbook(
    *,
    workers: int = 4,
    configuration: SpellbookConfiguration | None = None,
) -> Spellbook:
    """
    Purpose:
        Build a spellbook configured for dynamic concurrency tests.
    Contract:
        - Reuses the Aether configuration when present to avoid mismatches.
        - Applies dynamic defaults for fresh configurations.
        - Sets the phase scheduler workers for concurrency coverage when mutable.
    Args:
        workers: Scheduler worker count for the spellbook.
        configuration: Optional configuration override to reuse across spellbooks.
    Returns:
        Spellbook: Configured spellbook instance.
    """
    if configuration is None:
        configuration = Aether()._get_configuration("default")
    if configuration is None:
        configuration = SpellbookConfiguration()
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    if not configuration._frozen:
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


def _assert_basic_service(instance: Any) -> None:
    """
    Purpose:
        Validate BasicService instances for concurrency tests.
    Contract:
        - Instance must be BasicService.
    Args:
        instance: Object returned from meld.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not BasicService.
    """
    assert isinstance(instance, BasicService)


def _assert_basic_config(instance: Any) -> None:
    """
    Purpose:
        Validate BasicConfig instances for concurrency tests.
    Contract:
        - Instance must be BasicConfig.
    Args:
        instance: Object returned from meld.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not BasicConfig.
    """
    assert isinstance(instance, BasicConfig)


def _get_inbound_spell_ids(
    spells_by_conduit: dict[str, list[tuple[str, Any]]] | None,
) -> list[str]:
    """
    Purpose:
        Extract inbound spell IDs from a contract snapshot.
    Contract:
        - Returns spell IDs from inbound entries only.
        - Preserves duplicates so callers can assert idempotence.
    Args:
        spells_by_conduit: Contract snapshot keyed by inbound/outbound or None
            when no contracted spells are present.
    Returns:
        list[str]: Spell IDs found in inbound entries.
    """
    inbound_ids: list[str] = []
    if not spells_by_conduit:
        return inbound_ids
    for spell_id, _spell in spells_by_conduit.get("inbound", []):
        inbound_ids.append(spell_id)
    return inbound_ids


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


def _run_concurrent_calls(
    *,
    functions: list[Callable[[], Any]],
    timeout: float = 5.0,
) -> tuple[list[Any], list[Exception]]:
    """
    Purpose:
        Execute concurrent callables and collect results/errors.
    Contract:
        - All functions begin execution after the barrier.
        - Any raised exception is returned for assertions.
    Args:
        functions: Callables to run concurrently.
        timeout: Barrier timeout in seconds.
    Returns:
        tuple[list[Any], list[Exception]]: (results, errors).
    """
    barrier = Barrier(len(functions))
    lock = Lock()
    results: list[Any] = []
    errors: list[Exception] = []

    def worker(fn: Callable[[], Any]) -> None:
        """
        Purpose:
            Run a single callable under barrier synchronization.
        Contract:
            - Captures results and errors for the caller.
        Args:
            fn: Callable to execute.
        Returns:
            None.
        """
        try:
            barrier.wait(timeout=timeout)
            result = fn()
            with lock:
                results.append(result)
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [Thread(target=worker, args=(fn,)) for fn in functions]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return results, errors


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

        with borrowers[0].transaction("link", conduits=[borrowers[0], owner]):
            borrowers[0].add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )
        with borrowers[1].transaction("link", conduits=[borrowers[1], owner]):
            borrowers[1].add_spell_to_contract(
                spell_id=depth5_ids[Depth5Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )
        with borrowers[2].transaction("link", conduits=[borrowers[2], owner]):
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
            with borrower.transaction("link", conduits=[borrower, owner]):
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


def test_conduit_cluster_concurrent_meld_unique_per_conduit_cluster_shared_instance() -> None:
    """
    Purpose:
        Stress concurrent melds across a cluster for unique_per_conduit_cluster.
    Contract:
        - Conduits in the same cluster resolve the same instance.
        - Concurrent calls do not produce duplicate instances.
    Returns:
        None.
    Raises:
        AssertionError: If instances diverge or concurrency fails.
    """
    owner_book = _make_dynamic_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_books = [
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
    ]
    borrowers = [
        borrower_books[0].conjure(automatic=False, name="borrower-1"),
        borrower_books[1].conjure(automatic=False, name="borrower-2"),
        borrower_books[2].conjure(automatic=False, name="borrower-3"),
    ]
    try:
        for borrower in borrowers:
            owner.link(borrower)
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame)
        cloud.create_cluster("cluster-hard")
        cloud.add_conduit_to_cluster(owner, "cluster-hard")
        for borrower in borrowers:
            cloud.add_conduit_to_cluster(borrower, "cluster-hard")
        cloud.refresh_cluster_shares_for_conduit(owner)

        barrier = Barrier(4)
        lock = Lock()
        results: list[Any] = []
        errors: list[Exception] = []

        def worker(conduit: Conduit) -> None:
            """
            Purpose:
                Meld a shared spell concurrently in a cluster.
            Contract:
                - Records the resolved instance.
            Args:
                conduit: Conduit executing the meld.
            Returns:
                None.
            """
            try:
                barrier.wait(timeout=5)
                instance = conduit.meld(spell=spell_id)
                with lock:
                    results.append(instance)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [Thread(target=worker, args=(owner,))]
        threads.extend(Thread(target=worker, args=(borrower,)) for borrower in borrowers)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert errors == []
        assert len(results) == 4
        assert len({id(instance) for instance in results}) == 1
        assert isinstance(results[0], BasicService)
    finally:
        for borrower in borrowers:
            borrower.cleanup()
        owner.cleanup()


def test_conduit_concurrent_contract_additions_idempotent() -> None:
    """
    Purpose:
        Stress concurrent contract additions for the same spell.
    Contract:
        - Concurrent adds do not create duplicate contract entries.
        - Root spell remains contracted after concurrent adds.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate entries appear or adds fail.
    """
    owner_book = _make_dynamic_spellbook()
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_book = _make_dynamic_spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            barrier = Barrier(4)
            lock = Lock()
            errors: list[Exception] = []

            def worker() -> None:
                """
                Purpose:
                    Concurrently attempt to add the same spell to a contract.
                Contract:
                    - Any exception is captured for assertions.
                Returns:
                    None.
                """
                try:
                    barrier.wait(timeout=5)
                    borrower.add_spell_to_contract(
                        spell_id=depth3_ids[Depth3Root],
                        conduit=owner,
                        permissions="create",
                        link_dependencies=True,
                    )
                except Exception as exc:
                    with lock:
                        errors.append(exc)

            threads = [Thread(target=worker) for _ in range(4)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            assert errors == []
            spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner._id)
            assert spells_by_conduit is not None
            inbound_ids = _get_inbound_spell_ids(spells_by_conduit)
            assert inbound_ids.count(depth3_ids[Depth3Root]) == 1
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_lineage_concurrent_meld_unique_per_conduit_lineage_shared_instance() -> None:
    """
    Purpose:
        Stress concurrent melds across a conduit lineage.
    Contract:
        - Root and lesser conduits resolve the same instance.
        - Concurrent calls do not produce duplicate instances.
    Returns:
        None.
    Raises:
        AssertionError: If lineage sharing fails or concurrency errors occur.
    """
    spellbook = _make_dynamic_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    nested = lesser.create_lesser_conduit()
    barrier = Barrier(3)
    lock = Lock()
    results: list[Any] = []
    errors: list[Exception] = []

    def worker(target: Conduit) -> None:
        """
        Purpose:
            Meld the lineage-shared spell concurrently.
        Contract:
            - Records the resolved instance.
        Args:
            target: Conduit executing the meld.
        Returns:
            None.
        """
        try:
            barrier.wait(timeout=5)
            instance = target.meld(spell=spell_id)
            with lock:
                results.append(instance)
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [
        Thread(target=worker, args=(conduit,)),
        Thread(target=worker, args=(lesser,)),
        Thread(target=worker, args=(nested,)),
    ]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert errors == []
        assert len(results) == 3
        assert len({id(instance) for instance in results}) == 1
        assert isinstance(results[0], BasicService)
    finally:
        nested.cleanup()
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_concurrent_shared_unique_contract_reuses_owner_instance() -> None:
    """
    Purpose:
        Stress concurrent melds across linked conduits for shared unique.
    Contract:
        - Owner and borrower resolve the same instance.
        - Concurrent calls do not create duplicates.
    Returns:
        None.
    Raises:
        AssertionError: If shared-unique reuse fails.
    """
    owner_book = _make_dynamic_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_book = _make_dynamic_spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            )
        barrier = Barrier(2)
        lock = Lock()
        results: list[Any] = []
        errors: list[Exception] = []

        def worker(target: Conduit) -> None:
            """
            Purpose:
                Meld a shared unique spell concurrently.
            Contract:
                - Records the resolved instance.
            Args:
                target: Conduit executing the meld.
            Returns:
                None.
            """
            try:
                barrier.wait(timeout=5)
                instance = target.meld(spell=spell_id)
                with lock:
                    results.append(instance)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [
            Thread(target=worker, args=(owner,)),
            Thread(target=worker, args=(borrower,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert errors == []
        assert len(results) == 2
        assert len({id(instance) for instance in results}) == 1
        assert isinstance(results[0], BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_unique_per_conduit_lineage_isolated_across_lineages_concurrent() -> None:
    """
    Purpose:
        Stress concurrent melds across two independent lineages.
    Contract:
        - Each lineage reuses its own instance.
        - Lineages do not share instances across roots.
    Returns:
        None.
    Raises:
        AssertionError: If lineage isolation fails.
    """
    spellbook_a = _make_dynamic_spellbook()
    spell_id_a = spellbook_a.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )
    configuration = spellbook_a.get_configuration()
    spellbook_b = _make_dynamic_spellbook(configuration=configuration)
    spell_id_b = spellbook_b.bind(
        spell=BasicConfig,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )
    root_a = spellbook_a.conjure(name="root-a")
    root_b = spellbook_b.conjure(name="root-b")
    lesser_a = root_a.create_lesser_conduit()
    lesser_b = root_b.create_lesser_conduit()
    try:
        tasks = [
            ("root-a", root_a, spell_id_a, _assert_basic_service),
            ("lesser-a", lesser_a, spell_id_a, _assert_basic_service),
            ("root-b", root_b, spell_id_b, _assert_basic_config),
            ("lesser-b", lesser_b, spell_id_b, _assert_basic_config),
        ]
        results = _run_concurrent_melds(tasks=tasks)
        instance_a = results["root-a"]
        instance_b = results["root-b"]
        assert instance_a is results["lesser-a"]
        assert instance_b is results["lesser-b"]
        assert instance_a is not instance_b
    finally:
        lesser_a.cleanup()
        root_a.cleanup()
        lesser_b.cleanup()
        root_b.cleanup()


def test_conduit_cluster_concurrent_meld_two_clusters_isolated() -> None:
    """
    Purpose:
        Stress concurrent melds across two distinct clusters.
    Contract:
        - Conduits within a cluster share the instance.
        - Conduits across clusters do not share instances.
    Returns:
        None.
    Raises:
        AssertionError: If cluster isolation fails.
    """
    cluster_a_owner_book = _make_dynamic_spellbook()
    spell_id_a = cluster_a_owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    configuration = cluster_a_owner_book.get_configuration()
    cluster_b_owner_book = _make_dynamic_spellbook(configuration=configuration)
    spell_id_b = cluster_b_owner_book.bind(
        spell=BasicConfig,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    cluster_a_peer_book = _make_dynamic_spellbook(configuration=configuration)
    cluster_b_peer_book = _make_dynamic_spellbook(configuration=configuration)
    cluster_a_owner = cluster_a_owner_book.conjure(
        automatic=False,
        name="cluster-a-owner",
    )
    cluster_a_peer = cluster_a_peer_book.conjure(
        automatic=False,
        name="cluster-a-peer",
    )
    cluster_b_owner = cluster_b_owner_book.conjure(
        automatic=False,
        name="cluster-b-owner",
    )
    cluster_b_peer = cluster_b_peer_book.conjure(
        automatic=False,
        name="cluster-b-peer",
    )
    try:
        cluster_a_owner.link(cluster_a_peer)
        cluster_b_owner.link(cluster_b_peer)

        cloud_a = cluster_a_owner._spellbook._aether.get_conduit_cloud(cluster_a_owner._aetheric_frame)
        cloud_b = cluster_b_owner._spellbook._aether.get_conduit_cloud(cluster_b_owner._aetheric_frame)
        cloud_a.create_cluster("cluster-a")
        cloud_a.add_conduit_to_cluster(cluster_a_owner, "cluster-a")
        cloud_a.add_conduit_to_cluster(cluster_a_peer, "cluster-a")
        cloud_b.create_cluster("cluster-b")
        cloud_b.add_conduit_to_cluster(cluster_b_owner, "cluster-b")
        cloud_b.add_conduit_to_cluster(cluster_b_peer, "cluster-b")
        cloud_a.refresh_cluster_shares_for_conduit(cluster_a_owner)
        cloud_b.refresh_cluster_shares_for_conduit(cluster_b_owner)

        tasks = [
            ("cluster-a-owner", cluster_a_owner, spell_id_a, _assert_basic_service),
            ("cluster-a-peer", cluster_a_peer, spell_id_a, _assert_basic_service),
            ("cluster-b-owner", cluster_b_owner, spell_id_b, _assert_basic_config),
            ("cluster-b-peer", cluster_b_peer, spell_id_b, _assert_basic_config),
        ]
        results = _run_concurrent_melds(tasks=tasks)
        assert results["cluster-a-owner"] is results["cluster-a-peer"]
        assert results["cluster-b-owner"] is results["cluster-b-peer"]
        assert results["cluster-a-owner"] is not results["cluster-b-owner"]
    finally:
        cluster_a_peer.cleanup()
        cluster_a_owner.cleanup()
        cluster_b_peer.cleanup()
        cluster_b_owner.cleanup()


def test_conduit_concurrent_contract_additions_multiple_spells() -> None:
    """
    Purpose:
        Stress concurrent contract additions for multiple spell roots.
    Contract:
        - Each root spell is contracted once.
        - No errors occur under concurrent additions.
    Returns:
        None.
    Raises:
        AssertionError: If contract additions fail.
    """
    owner_book = _make_dynamic_spellbook()
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    depth5_ids = _bind_graph(
        owner_book,
        get_depth_5_classes(),
        existence=Existence.unique,
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_book = _make_dynamic_spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)

        def add_depth3() -> None:
            """
            Purpose:
                Contract the depth-3 root spell.
            Contract:
                - Adds the root spell to the contract.
            Returns:
                None.
            """
            borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

        def add_depth5() -> None:
            """
            Purpose:
                Contract the depth-5 root spell.
            Contract:
                - Adds the root spell to the contract.
            Returns:
                None.
            """
            borrower.add_spell_to_contract(
                spell_id=depth5_ids[Depth5Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

        with borrower.transaction("link", conduits=[borrower, owner]):
            _results, errors = _run_concurrent_calls(functions=[add_depth3, add_depth5])
        assert errors == []
        spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner._id)
        assert spells_by_conduit is not None
        inbound_ids = _get_inbound_spell_ids(spells_by_conduit)
        assert inbound_ids.count(depth3_ids[Depth3Root]) == 1
        assert inbound_ids.count(depth5_ids[Depth5Root]) == 1
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_concurrent_contract_additions_same_spell_multiple_borrowers() -> None:
    """
    Purpose:
        Stress concurrent contract additions for the same spell across borrowers.
    Contract:
        - Each borrower contracts the spell once.
        - Change-control may reject overlapping link transactions.
    Returns:
        None.
    Raises:
        AssertionError: If any borrower lacks the contract.
    """
    owner_book = _make_dynamic_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_books = [
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
    ]
    borrowers = [
        borrower_books[0].conjure(automatic=False, name="borrower-1"),
        borrower_books[1].conjure(automatic=False, name="borrower-2"),
        borrower_books[2].conjure(automatic=False, name="borrower-3"),
    ]
    try:
        for borrower in borrowers:
            owner.link(borrower)

        def add_for(borrower: Conduit) -> Callable[[], None]:
            """
            Purpose:
                Build a callable that contracts the spell for a borrower.
            Contract:
                - Adds the spell to the borrower's contract.
            Args:
                borrower: Target borrower conduit.
            Returns:
                Callable[[], None]: Contracting function.
            """
            def _add() -> None:
                """
                Purpose:
                    Contract the shared spell for a borrower.
                Contract:
                    - Adds the spell to the contract.
                Returns:
                    None.
                """
                with borrower.transaction("link", conduits=[borrower, owner]):
                    borrower.add_spell_to_contract(
                        spell_id=spell_id,
                        conduit=owner,
                        permissions="create",
                    )
            return _add

        functions = [add_for(borrower) for borrower in borrowers]
        _results, errors = _run_concurrent_calls(functions=functions)
        assert all(
            "Change-control admission denied" in str(error)
            for error in errors
        )
        for borrower in borrowers:
            spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner._id)
            assert spells_by_conduit is not None
            inbound_ids = _get_inbound_spell_ids(spells_by_conduit)
            if inbound_ids.count(spell_id) != 1:
                with borrower.transaction("link", conduits=[borrower, owner]):
                    borrower.add_spell_to_contract(
                        spell_id=spell_id,
                        conduit=owner,
                        permissions="create",
                    )
                spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner._id)
                assert spells_by_conduit is not None
                inbound_ids = _get_inbound_spell_ids(spells_by_conduit)
                assert inbound_ids.count(spell_id) == 1
    finally:
        for borrower in borrowers:
            borrower.cleanup()
        owner.cleanup()


def test_conduit_concurrent_meld_many_across_borrowers_distinct_instances() -> None:
    """
    Purpose:
        Stress concurrent melds for Existence.many across borrowers.
    Contract:
        - Each meld returns a distinct instance.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused.
    """
    owner_book = _make_dynamic_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.many,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_books = [
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
    ]
    borrowers = [
        borrower_books[0].conjure(automatic=False, name="borrower-1"),
        borrower_books[1].conjure(automatic=False, name="borrower-2"),
        borrower_books[2].conjure(automatic=False, name="borrower-3"),
    ]
    try:
        for borrower in borrowers:
            owner.link(borrower)
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.add_spell_to_contract(
                    spell_id=spell_id,
                    conduit=owner,
                    permissions="create",
                )

        def meld_owner() -> BasicService:
            """
            Purpose:
                Meld the many spell from the owner conduit.
            Contract:
                - Returns a new BasicService instance.
            Returns:
                BasicService: New instance.
            """
            instance = owner.meld(spell=spell_id)
            _assert_basic_service(instance)
            return instance

        def meld_borrower(borrower: Conduit) -> Callable[[], BasicService]:
            """
            Purpose:
                Build a callable that melds the many spell from a borrower.
            Contract:
                - Returns a new BasicService instance.
            Args:
                borrower: Borrower conduit.
            Returns:
                Callable[[], BasicService]: Meld function.
            """
            def _meld() -> BasicService:
                """
                Purpose:
                    Meld the many spell from a borrower conduit.
                Contract:
                    - Returns a new BasicService instance.
                Returns:
                    BasicService: New instance.
                """
                instance = borrower.meld(spell=spell_id)
                _assert_basic_service(instance)
                return instance
            return _meld

        functions = [meld_owner]
        functions.extend(meld_borrower(borrower) for borrower in borrowers)
        results, errors = _run_concurrent_calls(functions=functions)
        assert errors == []
        assert len({id(instance) for instance in results}) == 4
    finally:
        for borrower in borrowers:
            borrower.cleanup()
        owner.cleanup()


def test_conduit_concurrent_meld_unique_across_multiple_borrowers_shared_instance() -> None:
    """
    Purpose:
        Stress concurrent melds for shared unique across multiple borrowers.
    Contract:
        - All conduits resolve the same instance.
    Returns:
        None.
    Raises:
        AssertionError: If shared reuse fails.
    """
    owner_book = _make_dynamic_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_books = [
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
        _make_dynamic_spellbook(),
    ]
    borrowers = [
        borrower_books[0].conjure(automatic=False, name="borrower-1"),
        borrower_books[1].conjure(automatic=False, name="borrower-2"),
        borrower_books[2].conjure(automatic=False, name="borrower-3"),
    ]
    try:
        for borrower in borrowers:
            owner.link(borrower)
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.add_spell_to_contract(
                    spell_id=spell_id,
                    conduit=owner,
                    permissions="create",
                )

        def meld_owner() -> BasicService:
            """
            Purpose:
                Meld the shared unique spell from the owner conduit.
            Contract:
                - Returns the shared BasicService instance.
            Returns:
                BasicService: Shared instance.
            """
            instance = owner.meld(spell=spell_id)
            _assert_basic_service(instance)
            return instance

        def meld_borrower(borrower: Conduit) -> Callable[[], BasicService]:
            """
            Purpose:
                Build a callable that melds shared unique from a borrower.
            Contract:
                - Returns the shared BasicService instance.
            Args:
                borrower: Borrower conduit.
            Returns:
                Callable[[], BasicService]: Meld function.
            """
            def _meld() -> BasicService:
                """
                Purpose:
                    Meld the shared unique spell from a borrower.
                Contract:
                    - Returns the shared BasicService instance.
                Returns:
                    BasicService: Shared instance.
                """
                instance = borrower.meld(spell=spell_id)
                _assert_basic_service(instance)
                return instance
            return _meld

        functions = [meld_owner]
        functions.extend(meld_borrower(borrower) for borrower in borrowers)
        results, errors = _run_concurrent_calls(functions=functions)
        assert errors == []
        assert len({id(instance) for instance in results}) == 1
    finally:
        for borrower in borrowers:
            borrower.cleanup()
        owner.cleanup()


def test_conduit_concurrent_meld_mixed_spells_same_conduit() -> None:
    """
    Purpose:
        Stress concurrent melds for mixed spells in the same conduit.
    Contract:
        - Each spell reuses its own instance under contention.
        - Mixed spell instances do not collide.
    Returns:
        None.
    Raises:
        AssertionError: If reuse or isolation fails.
    """
    spellbook = _make_dynamic_spellbook()
    depth3_ids = _bind_graph(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique_per_conduit,
    )
    basic_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        def meld_basic() -> BasicService:
            """
            Purpose:
                Meld BasicService in the conduit.
            Contract:
                - Returns the shared BasicService instance.
            Returns:
                BasicService: Shared instance.
            """
            instance = conduit.meld(spell=basic_id)
            _assert_basic_service(instance)
            return instance

        def meld_depth3() -> Depth3Root:
            """
            Purpose:
                Meld Depth3Root in the conduit.
            Contract:
                - Returns the shared Depth3Root instance.
            Returns:
                Depth3Root: Shared instance.
            """
            root = conduit.meld(spell=depth3_ids[Depth3Root])
            _assert_depth3_root(root)
            return root

        functions = [meld_basic, meld_basic, meld_depth3, meld_depth3]
        results, errors = _run_concurrent_calls(functions=functions)
        assert errors == []
        basics = [result for result in results if isinstance(result, BasicService)]
        roots = [result for result in results if isinstance(result, Depth3Root)]
        assert len(basics) == 2
        assert len(roots) == 2
        assert len({id(instance) for instance in basics}) == 1
        assert len({id(instance) for instance in roots}) == 1
        assert basics[0] is not roots[0]
    finally:
        conduit.cleanup()


def test_conduit_concurrent_link_separate_pairs() -> None:
    """
    Purpose:
        Stress concurrent linking across separate conduit pairs.
    Contract:
        - Each pair links successfully without interference.
    Returns:
        None.
    Raises:
        AssertionError: If linking fails.
    """
    book_a = _make_dynamic_spellbook()
    configuration = book_a.get_configuration()
    book_b = _make_dynamic_spellbook(configuration=configuration)
    book_c = _make_dynamic_spellbook(configuration=configuration)
    book_d = _make_dynamic_spellbook(configuration=configuration)
    conduit_a = book_a.conjure(automatic=False, name="conduit-a")
    conduit_b = book_b.conjure(automatic=False, name="conduit-b")
    conduit_c = book_c.conjure(automatic=False, name="conduit-c")
    conduit_d = book_d.conjure(automatic=False, name="conduit-d")
    try:
        def link_ab() -> bool:
            """
            Purpose:
                Link conduit A to conduit B.
            Contract:
                - Returns True on successful link.
            Returns:
                bool: Link result.
            """
            return conduit_a.link(conduit_b)

        def link_cd() -> bool:
            """
            Purpose:
                Link conduit C to conduit D.
            Contract:
                - Returns True on successful link.
            Returns:
                bool: Link result.
            """
            return conduit_c.link(conduit_d)

        results, errors = _run_concurrent_calls(functions=[link_ab, link_cd])
        assert errors == []
        assert len(results) == 2
        assert all(result is True for result in results)
        contracted_a = conduit_a.get_contracted_conduits()
        contracted_c = conduit_c.get_contracted_conduits()
        assert contracted_a is not None
        assert contracted_c is not None
        assert any(conduit_id == conduit_b._id for conduit_id, _ in contracted_a)
        assert any(conduit_id == conduit_d._id for conduit_id, _ in contracted_c)
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()
        conduit_d.cleanup()
        conduit_c.cleanup()


def test_conduit_concurrent_meld_repeated_rounds_unique_per_conduit() -> None:
    """
    Purpose:
        Stress repeated rounds of concurrent melds in a single conduit.
    Contract:
        - Each round reuses the same instance.
        - No errors occur across rounds.
    Returns:
        None.
    Raises:
        AssertionError: If reuse fails across rounds.
    """
    spellbook = _make_dynamic_spellbook()
    depth3_ids = _bind_graph(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique_per_conduit,
    )
    conduit = spellbook.conjure(name="root")
    try:
        def meld_root() -> Depth3Root:
            """
            Purpose:
                Meld the depth-3 root in the conduit.
            Contract:
                - Returns the shared Depth3Root instance.
            Returns:
                Depth3Root: Shared instance.
            """
            root = conduit.meld(spell=depth3_ids[Depth3Root])
            _assert_depth3_root(root)
            return root

        shared_instance: Depth3Root | None = None
        for _round in range(3):
            results, errors = _run_concurrent_calls(
                functions=[meld_root, meld_root, meld_root, meld_root],
            )
            assert errors == []
            assert len({id(root) for root in results}) == 1
            if shared_instance is None:
                shared_instance = results[0]
            assert results[0] is shared_instance
    finally:
        conduit.cleanup()


def test_conduit_concurrent_bulk_contract_additions() -> None:
    """
    Purpose:
        Stress concurrent bulk contract additions for multiple spell IDs.
    Contract:
        - All spell IDs are contracted without duplication.
    Returns:
        None.
    Raises:
        AssertionError: If any spell ID is missing from contracts.
    """
    owner_book = _make_dynamic_spellbook()
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    depth5_ids = _bind_graph(
        owner_book,
        get_depth_5_classes(),
        existence=Existence.unique,
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower_book = _make_dynamic_spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        spell_ids_a = [depth3_ids[Depth3Root], depth5_ids[Depth5Root]]
        spell_ids_b = [depth3_ids[Depth3Root]]

        def add_batch_a() -> dict[str, bool]:
            """
            Purpose:
                Contract the first batch of spell IDs.
            Contract:
                - Adds each spell id to the contract.
            Returns:
                dict[str, bool]: Result mapping from add_spells_to_contract.
            """
            return borrower.add_spells_to_contract(
                spell_ids=spell_ids_a,
                conduit=owner,
                permissions="create",
            )

        def add_batch_b() -> dict[str, bool]:
            """
            Purpose:
                Contract the second batch of spell IDs.
            Contract:
                - Adds each spell id to the contract.
            Returns:
                dict[str, bool]: Result mapping from add_spells_to_contract.
            """
            return borrower.add_spells_to_contract(
                spell_ids=spell_ids_b,
                conduit=owner,
                permissions="create",
            )

        with borrower.transaction("link", conduits=[borrower, owner]):
            _results, errors = _run_concurrent_calls(functions=[add_batch_a, add_batch_b])
        assert errors == []
        spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner._id)
        assert spells_by_conduit is not None
        inbound_ids = _get_inbound_spell_ids(spells_by_conduit)
        assert inbound_ids.count(depth3_ids[Depth3Root]) == 1
        assert inbound_ids.count(depth5_ids[Depth5Root]) == 1
    finally:
        borrower.cleanup()
        owner.cleanup()
