"""
Unit contract tests for RestoreEngine._build_plan_levels (S4 plan graph,
parallel_restore_ulid_identity): the folded world compiles into dependency
LEVELS over the real DirectedAcyclicWorkGraph, with the recorded partial
order preserved as parent-before-child level placement.

These lock the REOPEN regression (2026-07-19): the plan compiler called
DirectedAcyclicWorkGraph.add_dependency with a phantom `depends_on=` kwarg
that never existed on the real signature - every parallel restore died at
"plan_graph" before building anything. The fix draws parent-first edges;
this suite drives the compiler over seeded folded stores and asserts the
resulting level structure so the phantom kwarg can never return silently.

The engine is constructed over a bare one-window chain and its folded
stores are seeded directly - _build_plan_levels reads ONLY those instance
dicts, so this exercises the compiler in isolation without a live world.

Runs only on 3.14t (melder package root import chain).
"""
from melder.crystallizer.crystal_loader_system.restore_engine import (
    RestoreEngine,
)


def _bare_engine() -> RestoreEngine:
    """
    Build a single-use engine over one empty window.

    Returns:
        RestoreEngine: An engine whose folded stores start empty and are
        seeded per test before calling _build_plan_levels().
    """
    return RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-plan"],
        chain=[{"journal": [], "payloads": {}}],
    )


def test_full_world_compiles_to_the_expected_dependency_levels():
    """
    Purpose:
        Headline regression: a frame + two books + one link + one cluster
        + one contract + nexus compile to the exact canon level order.
        (The old depends_on kwarg raised TypeError here before any level
        could be produced.)
    Contract:
        - Level 0: dependency-free roots (frame, nexus) in ascending id.
        - Level 1: both books (each depends on the frame).
        - Level 2: cluster + link (each depends on the member/endpoint
          books), ascending id.
        - Level 3: contract (depends on its link node).
    Returns:
        None.
    Raises:
        AssertionError: If the recorded partial order is not preserved.
    """
    engine = _bare_engine()
    try:
        engine._nexus_payload = {"activated": True}
        engine._frames = {"default": {}}
        engine._books = {
            "bookA": {"frame_name": "default"},
            "bookB": {"frame_name": "default"},
        }
        engine._conduits = {
            "condA": {"spellbook_id": "bookA", "link_targets": ["condB"]},
            "condB": {"spellbook_id": "bookB", "link_targets": []},
        }
        engine._clusters = {"clu1": {"member_conduit_ids": ["condA", "condB"]}}
        engine._contracts = {
            "ctrX": {"conduit_a_id": "condA", "conduit_b_id": "condB"},
        }
        levels = engine._build_plan_levels()
        assert levels == [
            [("frame", "default"), ("nexus", None)],
            [("book", "bookA"), ("book", "bookB")],
            [("cluster", "clu1"), ("link", ("condA", "condB"))],
            [("contract", "ctrX")],
        ]
    finally:
        engine.cleanup()


def test_frame_precedes_its_books():
    """
    Purpose:
        Verify the frame -> book edge direction (frames own the dynamic
        gate books read, so frames must land first).
    Contract:
        The frame node's level index is strictly below both of its books'.
    Returns:
        None.
    Raises:
        AssertionError: If a book is placed at or before its frame.
    """
    engine = _bare_engine()
    try:
        engine._frames = {"main": {}}
        engine._books = {
            "b1": {"frame_name": "main"},
            "b2": {"frame_name": "main"},
        }
        levels = engine._build_plan_levels()
        index = {
            payload: i for i, level in enumerate(levels) for payload in level
        }
        assert index[("frame", "main")] < index[("book", "b1")]
        assert index[("frame", "main")] < index[("book", "b2")]
    finally:
        engine.cleanup()


def test_link_lands_after_both_endpoint_books():
    """
    Purpose:
        Verify a link edge depends on BOTH endpoint books (a link cannot
        replay before either conduit's book is built).
    Contract:
        The link node's level index is strictly above each endpoint book's.
    Returns:
        None.
    Raises:
        AssertionError: If the link is placed before either endpoint book.
    """
    engine = _bare_engine()
    try:
        engine._frames = {"f": {}}
        engine._books = {
            "ba": {"frame_name": "f"},
            "bb": {"frame_name": "f"},
        }
        engine._conduits = {
            "ca": {"spellbook_id": "ba", "link_targets": ["cb"]},
            "cb": {"spellbook_id": "bb", "link_targets": []},
        }
        levels = engine._build_plan_levels()
        index = {
            payload: i for i, level in enumerate(levels) for payload in level
        }
        link = ("link", ("ca", "cb"))
        assert index[link] > index[("book", "ba")]
        assert index[link] > index[("book", "bb")]
    finally:
        engine.cleanup()


def test_contract_lands_after_its_link_node():
    """
    Purpose:
        Verify a contract with a matching recorded link edge depends on
        that link node (details re-grant only after the edge exists).
    Contract:
        The contract node's level index is strictly above the link node's.
    Returns:
        None.
    Raises:
        AssertionError: If the contract is placed at or before its link.
    """
    engine = _bare_engine()
    try:
        engine._frames = {"f": {}}
        engine._books = {
            "ba": {"frame_name": "f"},
            "bb": {"frame_name": "f"},
        }
        engine._conduits = {
            "ca": {"spellbook_id": "ba", "link_targets": ["cb"]},
            "cb": {"spellbook_id": "bb", "link_targets": []},
        }
        engine._contracts = {
            "ct": {"conduit_a_id": "ca", "conduit_b_id": "cb"},
        }
        levels = engine._build_plan_levels()
        index = {
            payload: i for i, level in enumerate(levels) for payload in level
        }
        assert index[("contract", "ct")] > index[("link", ("ca", "cb"))]
    finally:
        engine.cleanup()


def test_cluster_lands_after_its_member_books():
    """
    Purpose:
        Verify a cluster depends on every member conduit's book.
    Contract:
        The cluster node's level index is strictly above each member
        book's index.
    Returns:
        None.
    Raises:
        AssertionError: If the cluster is placed before a member book.
    """
    engine = _bare_engine()
    try:
        engine._frames = {"f": {}}
        engine._books = {
            "ba": {"frame_name": "f"},
            "bb": {"frame_name": "f"},
        }
        engine._conduits = {
            "ca": {"spellbook_id": "ba", "link_targets": []},
            "cb": {"spellbook_id": "bb", "link_targets": []},
        }
        engine._clusters = {"cl": {"member_conduit_ids": ["ca", "cb"]}}
        levels = engine._build_plan_levels()
        index = {
            payload: i for i, level in enumerate(levels) for payload in level
        }
        assert index[("cluster", "cl")] > index[("book", "ba")]
        assert index[("cluster", "cl")] > index[("book", "bb")]
    finally:
        engine.cleanup()


def test_unrecorded_frame_dependency_is_not_drawn():
    """
    Purpose:
        Verify a book whose frame is not recorded draws no frame edge -
        absence is handled by the unit's own honesty lanes, not by a
        dangling graph edge (parity with the sequential driver).
    Contract:
        A book referencing an absent frame is dependency-free and lands in
        level 0.
    Returns:
        None.
    Raises:
        AssertionError: If an edge to an unrecorded frame is drawn.
    """
    engine = _bare_engine()
    try:
        engine._frames = {}
        engine._books = {"orphan": {"frame_name": "ghost"}}
        levels = engine._build_plan_levels()
        assert levels == [[("book", "orphan")]]
    finally:
        engine.cleanup()


def test_nexus_root_is_edgeless_and_lands_in_level_zero():
    """
    Purpose:
        Verify the nexus root is a dependency leaf today (edgeless), so it
        sits in level 0 - placement becomes graph-derived automatically
        the moment the record carries nexus-native edges.
    Contract:
        With only a nexus payload, the single level holds exactly the
        nexus node.
    Returns:
        None.
    Raises:
        AssertionError: If nexus placement gains a phantom edge.
    """
    engine = _bare_engine()
    try:
        engine._nexus_payload = {"activated": True}
        levels = engine._build_plan_levels()
        assert levels == [[("nexus", None)]]
    finally:
        engine.cleanup()


def test_empty_world_compiles_to_no_levels():
    """
    Purpose:
        Verify an empty folded world yields an empty level list (parity
        with the sequential driver on empty worlds).
    Contract:
        No frames/books/links/clusters/contracts/nexus -> [].
    Returns:
        None.
    Raises:
        AssertionError: If an empty world produces phantom levels.
    """
    engine = _bare_engine()
    try:
        assert engine._build_plan_levels() == []
    finally:
        engine.cleanup()


def test_plan_levels_are_deterministic_across_calls():
    """
    Purpose:
        Verify the compiler is side-effect free and repeatable (the folded
        stores are read, never mutated).
    Contract:
        Two consecutive _build_plan_levels() calls return equal levels.
    Returns:
        None.
    Raises:
        AssertionError: If repeat compilation diverges.
    """
    engine = _bare_engine()
    try:
        engine._frames = {"f": {}}
        engine._books = {
            "ba": {"frame_name": "f"},
            "bb": {"frame_name": "f"},
        }
        engine._conduits = {
            "ca": {"spellbook_id": "ba", "link_targets": ["cb"]},
            "cb": {"spellbook_id": "bb", "link_targets": []},
        }
        first = engine._build_plan_levels()
        second = engine._build_plan_levels()
        assert first == second
    finally:
        engine.cleanup()


def test_flattened_levels_honor_every_recorded_edge():
    """
    Purpose:
        Verify flattening the levels yields a valid topological order:
        every dependency appears in an earlier level than its dependent.
    Contract:
        For frame->book, book->link, book->cluster, and link->contract
        edges, each parent's level index is strictly below its child's.
    Returns:
        None.
    Raises:
        AssertionError: If any recorded edge is violated by the flatten.
    """
    engine = _bare_engine()
    try:
        engine._frames = {"f": {}}
        engine._books = {
            "ba": {"frame_name": "f"},
            "bb": {"frame_name": "f"},
        }
        engine._conduits = {
            "ca": {"spellbook_id": "ba", "link_targets": ["cb"]},
            "cb": {"spellbook_id": "bb", "link_targets": []},
        }
        engine._clusters = {"cl": {"member_conduit_ids": ["ca", "cb"]}}
        engine._contracts = {
            "ct": {"conduit_a_id": "ca", "conduit_b_id": "cb"},
        }
        levels = engine._build_plan_levels()
        index = {
            payload: i for i, level in enumerate(levels) for payload in level
        }
        link = ("link", ("ca", "cb"))
        assert index[("frame", "f")] < index[("book", "ba")]
        assert index[("frame", "f")] < index[("book", "bb")]
        assert index[("book", "ba")] < index[link]
        assert index[("book", "bb")] < index[link]
        assert index[("book", "ba")] < index[("cluster", "cl")]
        assert index[link] < index[("contract", "ct")]
    finally:
        engine.cleanup()
