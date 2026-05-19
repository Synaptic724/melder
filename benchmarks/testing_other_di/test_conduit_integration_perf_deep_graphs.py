from __future__ import annotations

import time

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import (
    Depth3Root,
    Depth7Root,
    Depth9Root,
    Depth9LeafA,
    Depth9LeafB,
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


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


def _bind_classes(
    spellbook: Spellbook,
    classes: tuple[type, ...],
    *,
    existence: Existence,
) -> dict[type, str]:
    """
    Purpose:
        Bind a set of classes into the spellbook with the same Existence mode.
    Returns:
        dict[type, str]: Class -> spell_id mapping.
    """
    spell_ids: dict[type, str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


def _depth9_leaf_ids(root: Depth9Root) -> tuple[int, int]:
    """
    Purpose:
        Extract leaf object ids from a Depth9Root instance for reuse checks.
    Returns:
        tuple[int, int]: (leaf_a_id, leaf_b_id)
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
    return id(leaf_a), id(leaf_b)


def _bind_depth9_mixed_existence(
    spellbook: Spellbook,
    *,
    leaf_existence: Existence,
    other_existence: Existence,
) -> dict[type, str]:
    """
    Purpose:
        Bind the depth-9 graph with mixed Existence modes.
    Contract:
        - Depth9LeafA/Depth9LeafB use leaf_existence.
        - All other depth-9 nodes use other_existence.
    """
    spell_ids: dict[type, str] = {}
    for cls in get_depth_9_classes():
        existence = leaf_existence if cls in (Depth9LeafA, Depth9LeafB) else other_existence
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


def test_perf_conjure_scaling_depth3_5_7_9_automatic() -> None:
    """
    Purpose:
        Roughly time conjure + first meld as spell count grows (depth 3/5/7/9).
    Notes:
        - Run with: pytest -s -k test_perf_conjure_scaling_depth3_5_7_9_automatic
        - No timing thresholds asserted; prints numbers for local comparison.
    """
    cases = (
        (3, get_depth_3_classes(), Depth3Root),
        (5, get_depth_5_classes(), None),
        (7, get_depth_7_classes(), None),
        (9, get_depth_9_classes(), Depth9Root),
    )

    for depth, classes, root_cls in cases:
        # Use distinct frames so conduit cleanup in one case does not clean the
        # shared configuration used by the next case.
        spellbook = Spellbook(aetheric_frame=f"perf-scale-depth-{depth}")
        cfg = spellbook.get_configuration()
        cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

        spell_ids = _bind_classes(spellbook, classes, existence=Existence.unique)
        # Pick a root class for meld timing (Depth3/Depth9 are explicitly imported).
        if root_cls is None:
            root_cls = classes[-1]

        t0 = time.perf_counter()
        conduit = spellbook.conjure(name=f"perf-depth-{depth}")
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            _ = conduit.meld(spell=spell_ids[root_cls])
            meld_s = time.perf_counter() - t0
            print(
                f"Perf scaling depth={depth} (ms): "
                f"conjure={_ms(conjure_s):.3f}, "
                f"meld_root_cold={_ms(meld_s):.3f}"
            )
        finally:
            conduit.cleanup()


def test_perf_depth9_unique_conjure_and_meld_cold_warm() -> None:
    """
    Purpose:
        Time a depth-9 branched graph in automatic mode (unique caching).
    Notes:
        - Run with: pytest -s -k test_perf_depth9_unique_conjure_and_meld_cold_warm
    """
    spellbook = Spellbook()
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids = _bind_classes(spellbook, get_depth_9_classes(), existence=Existence.unique)
    root_id = spell_ids[Depth9Root]

    t0 = time.perf_counter()
    conduit = spellbook.conjure(name="perf-depth9-unique")
    conjure_s = time.perf_counter() - t0
    try:
        t0 = time.perf_counter()
        root1 = conduit.meld(spell=root_id)
        cold_s = time.perf_counter() - t0
        assert isinstance(root1, Depth9Root)

        t0 = time.perf_counter()
        root2 = conduit.meld(spell=root_id)
        warm_s = time.perf_counter() - t0
        assert root1 is root2

        print(
            "Perf depth9 unique (ms): "
            f"conjure={_ms(conjure_s):.3f}, "
            f"meld_root_cold={_ms(cold_s):.3f}, "
            f"meld_root_warm={_us(warm_s):.2f}us"
        )
    finally:
        conduit.cleanup()


def test_perf_depth9_many_all_nodes_avg() -> None:
    """
    Purpose:
        Time a depth-9 branched graph with Existence.many (new graph each call).
    Notes:
        - Run with: pytest -s -k test_perf_depth9_many_all_nodes_avg
    """
    spellbook = Spellbook()
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids = _bind_classes(spellbook, get_depth_9_classes(), existence=Existence.many)
    root_id = spell_ids[Depth9Root]

    conduit = spellbook.conjure(name="perf-depth9-many")
    try:
        # Warm up interpreter/method caches a bit.
        _ = conduit.meld(spell=root_id)

        iterations = 250
        t0 = time.perf_counter()
        leaf_a_id = 0
        leaf_b_id = 0
        for _i in range(iterations):
            root = conduit.meld(spell=root_id)
            assert isinstance(root, Depth9Root)
            leaf_a_id, leaf_b_id = _depth9_leaf_ids(root)
        total_s = time.perf_counter() - t0

        # Use the ids so the loop has observable work beyond allocation.
        assert leaf_a_id != 0
        assert leaf_b_id != 0

        print(
            f"Perf depth9 many (avg over {iterations}) (ms): "
            f"avg_meld_root={_ms(total_s) / iterations:.3f}"
        )
    finally:
        conduit.cleanup()


def test_perf_spellspace_depth3_unique_per_spellspace() -> None:
    """
    Purpose:
        Time spellspace behavior using a depth-3 graph scoped by spellspace.
    Notes:
        - Run with: pytest -s -k test_perf_spellspace_depth3_unique_per_spellspace
    """
    spellbook = Spellbook()
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids = _bind_classes(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique_per_spell_space,
    )
    root_id = spell_ids[Depth3Root]

    conduit = spellbook.conjure(name="perf-spellspace-depth3")
    try:
        # One spellspace: cold + warm within the same scope.
        with conduit.enter_spellspace() as space:
            t0 = time.perf_counter()
            root1 = space.meld(spell=root_id)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth3Root)

            warm_iters = 10_000
            t0 = time.perf_counter()
            for _ in range(warm_iters):
                root2 = space.meld(spell=root_id)
            warm_total_s = time.perf_counter() - t0
            assert root1 is root2

        # Multiple spellspaces: each should get its own instance.
        spaces = 200
        t0 = time.perf_counter()
        first_id = None
        last_id = None
        for i in range(spaces):
            with conduit.enter_spellspace() as space:
                root = space.meld(spell=root_id)
                if i == 0:
                    first_id = id(root)
                last_id = id(root)
        total_spaces_s = time.perf_counter() - t0

        assert first_id is not None
        assert last_id is not None
        assert first_id != last_id

        print(
            "Perf spellspace depth3 (ms/us): "
            f"meld_root_cold_in_space={_ms(cold_s):.3f}ms, "
            f"meld_root_warm_avg={_us(warm_total_s) / warm_iters:.2f}us, "
            f"per_spellspace_cold_avg={_ms(total_spaces_s) / spaces:.3f}ms"
        )
    finally:
        conduit.cleanup()


def test_perf_depth9_many_with_cached_leaves_and_cleanup() -> None:
    """
    Purpose:
        Time a depth-9 graph where only the leaf nodes are cached per conduit.
    Notes:
        - Run with: pytest -s -k test_perf_depth9_many_with_cached_leaves_and_cleanup
    """
    spellbook = Spellbook(aetheric_frame="perf-depth9-many-leaves-unique")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids = _bind_depth9_mixed_existence(
        spellbook,
        leaf_existence=Existence.unique_per_conduit,
        other_existence=Existence.many,
    )
    root_id = spell_ids[Depth9Root]

    conduit = spellbook.conjure(name="perf-depth9-many-leaves-unique")
    try:
        # Cold build + verify leaf reuse across calls.
        t0 = time.perf_counter()
        root1 = conduit.meld(spell=root_id)
        cold_s = time.perf_counter() - t0
        assert isinstance(root1, Depth9Root)
        leaf_a_1, leaf_b_1 = _depth9_leaf_ids(root1)

        root2 = conduit.meld(spell=root_id)
        assert isinstance(root2, Depth9Root)
        leaf_a_2, leaf_b_2 = _depth9_leaf_ids(root2)
        assert leaf_a_1 == leaf_a_2
        assert leaf_b_1 == leaf_b_2

        iterations = 200
        t0 = time.perf_counter()
        for _ in range(iterations):
            root = conduit.meld(spell=root_id)
            assert isinstance(root, Depth9Root)
        total_s = time.perf_counter() - t0

        t0 = time.perf_counter()
        conduit.cleanup()
        cleanup_s = time.perf_counter() - t0

        print(
            f"Perf depth9 many w/ cached leaves (iters={iterations}) (ms): "
            f"meld_root_cold={_ms(cold_s):.3f}, "
            f"avg_meld_root={_ms(total_s) / iterations:.3f}, "
            f"conduit_cleanup={_ms(cleanup_s):.3f}"
        )
    finally:
        conduit.cleanup()


def test_perf_mixed_workload_alternating_depth7_depth9_and_spellspace_cleanup() -> None:
    """
    Purpose:
        Simulate a mixed workload:
          - Alternate between two deep root types (depth-7 vs depth-9).
          - Periodically enter a spellspace to force frequent cleanup.
    Notes:
        - Run with: pytest -s -k test_perf_mixed_workload_alternating_depth7_depth9_and_spellspace_cleanup
    """
    spellbook = Spellbook(aetheric_frame="perf-mixed-workload")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    # Depth-9: mixed existence (cached leaves), depth-7: full many.
    spell_ids_9 = _bind_depth9_mixed_existence(
        spellbook,
        leaf_existence=Existence.unique_per_conduit,
        other_existence=Existence.many,
    )
    spell_ids_7 = _bind_classes(spellbook, get_depth_7_classes(), existence=Existence.many)
    # Spellspace graph: depth-3 scoped per spellspace.
    spell_ids_3 = _bind_classes(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique_per_spell_space,
    )

    root9_id = spell_ids_9[Depth9Root]
    root7_id = spell_ids_7[Depth7Root]
    root3_space_id = spell_ids_3[Depth3Root]

    conduit = spellbook.conjure(name="perf-mixed-workload")
    try:
        iterations = 200
        spellspace_every = 20
        spellspace_count = 0
        spellspace_total_s = 0.0

        t0 = time.perf_counter()
        for i in range(iterations):
            if i % 2 == 0:
                root = conduit.meld(spell=root9_id)
                assert isinstance(root, Depth9Root)
            else:
                root = conduit.meld(spell=root7_id)
                assert isinstance(root, Depth7Root)

            if (i + 1) % spellspace_every == 0:
                spellspace_count += 1
                t_space = time.perf_counter()
                with conduit.enter_spellspace() as space:
                    obj = space.meld(spell=root3_space_id)
                    assert isinstance(obj, Depth3Root)
                spellspace_total_s += time.perf_counter() - t_space

        workload_s = time.perf_counter() - t0

        t0 = time.perf_counter()
        conduit.cleanup()
        cleanup_s = time.perf_counter() - t0

        print(
            f"Perf mixed workload (iters={iterations}) (ms): "
            f"avg_step={_ms(workload_s) / iterations:.3f}, "
            f"spellspace_cycles={spellspace_count}, "
            f"avg_spellspace_cycle={_ms(spellspace_total_s) / max(spellspace_count, 1):.3f}, "
            f"conduit_cleanup={_ms(cleanup_s):.3f}"
        )
    finally:
        conduit.cleanup()


def test_perf_cycle_conjure_meld_cleanup_depth9_unique_per_conduit() -> None:
    """
    Purpose:
        Measure end-to-end lifecycle costs across multiple cycles:
          bind -> conjure -> meld -> cleanup
        using a depth-9 graph cached per conduit.
    Notes:
        - Run with: pytest -s -k test_perf_cycle_conjure_meld_cleanup_depth9_unique_per_conduit
    """
    cycles = 10
    conjure_total = 0.0
    meld_total = 0.0
    cleanup_total = 0.0

    for i in range(cycles):
        spellbook = Spellbook(aetheric_frame=f"perf-cycle-{i}")
        cfg = spellbook.get_configuration()
        cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

        spell_ids = _bind_classes(
            spellbook,
            get_depth_9_classes(),
            existence=Existence.unique_per_conduit,
        )
        root_id = spell_ids[Depth9Root]

        t0 = time.perf_counter()
        conduit = spellbook.conjure(name=f"perf-cycle-{i}")
        conjure_s = time.perf_counter() - t0
        conjure_total += conjure_s
        try:
            t0 = time.perf_counter()
            root = conduit.meld(spell=root_id)
            meld_s = time.perf_counter() - t0
            meld_total += meld_s
            assert isinstance(root, Depth9Root)

            t0 = time.perf_counter()
            conduit.cleanup()
            cleanup_s = time.perf_counter() - t0
            cleanup_total += cleanup_s
        finally:
            conduit.cleanup()

    print(
        f"Perf cycle depth9 unique_per_conduit (cycles={cycles}) (ms): "
        f"avg_conjure={_ms(conjure_total) / cycles:.3f}, "
        f"avg_meld_root={_ms(meld_total) / cycles:.3f}, "
        f"avg_cleanup={_ms(cleanup_total) / cycles:.3f}"
    )


def test_perf_spellspace_depth9_unique_per_spellspace_repeated_cleanup() -> None:
    """
    Purpose:
        Time repeated spellspace creation + root meld + spellspace cleanup for a depth-9 graph.
    Notes:
        - Run with: pytest -s -k test_perf_spellspace_depth9_unique_per_spellspace_repeated_cleanup
    """
    spellbook = Spellbook(aetheric_frame="perf-spellspace-depth9")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids = _bind_classes(
        spellbook,
        get_depth_9_classes(),
        existence=Existence.unique_per_spell_space,
    )
    root_id = spell_ids[Depth9Root]

    conduit = spellbook.conjure(name="perf-spellspace-depth9")
    try:
        spaces = 50
        t0 = time.perf_counter()
        for _ in range(spaces):
            with conduit.enter_spellspace() as space:
                root = space.meld(spell=root_id)
                assert isinstance(root, Depth9Root)
        total_s = time.perf_counter() - t0

        print(
            f"Perf spellspace depth9 (spaces={spaces}) (ms): "
            f"avg_cycle={_ms(total_s) / spaces:.3f}"
        )
    finally:
        conduit.cleanup()
