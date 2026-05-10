"""Unit tests for ResearchCreation cleanup behavior."""

from __future__ import annotations

import pytest

from melder.mutation_research.research.creation.creation_research import ResearchCreation


class _WeakRefTarget:
    """
    Purpose:
        Provide a weakref-friendly target for ResearchCreation.attach_creation.
    Contract:
        - Instances support weak references.
        - No behavior beyond identity is required.
    """


def test_research_creation_cleanup_cleans_nodes_and_refs() -> None:
    """
    Purpose:
        Validate ResearchCreation cleanup clears mutation nodes and weak references.
    Contract:
        - cleanup() marks the research line as cleaned.
        - cleanup() cleans committed nodes.
        - cleanup() nulls node registries, head id, metadata, and weak refs.
        - cleanup() is idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear owned state.
    """
    research = ResearchCreation(creation_id="creation-id", name="creation-line")
    research.attach_creation(_WeakRefTarget())
    node = research.begin_mutation(message="seed")
    research.commit_mutation(node)

    research.cleanup()

    assert research.cleaned is True
    assert node.cleaned is True
    assert research._creation_ref is None
    assert research._nodes is None
    assert research._node_ids is None
    assert research._metadata is None
    assert research._head_id is None

    research.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        research.begin_mutation()


def test_research_creation_properties_and_metadata_detach() -> None:
    """
    Purpose:
        Validate the stable property surface before cleanup.
    Contract:
        - id is a non-empty string.
        - creation_id, name, and head_id reflect constructor state.
        - metadata returns a detached shallow copy.
    Returns:
        None.
    Raises:
        AssertionError: If the property surface is incorrect.
    """
    research = ResearchCreation(
        creation_id="creation-id",
        name="creation-line",
    )
    try:
        meta = research.metadata
        meta["x"] = 1

        assert isinstance(research.id, str)
        assert research.id != ""
        assert research.creation_id == "creation-id"
        assert research.name == "creation-line"
        assert research.head_id is None
        assert research.metadata == {}
    finally:
        research.cleanup()


def test_research_creation_attach_get_begin_commit_checkout_and_list_nodes() -> None:
    """
    Purpose:
        Validate the live reference and mutation-node orchestration.
    Contract:
        - attach_creation rejects None and stores a weak live reference.
        - begin_mutation uses current head when no parent is supplied.
        - commit_mutation inserts new nodes and advances head.
        - checkout and get_node resolve committed nodes by id.
        - list_nodes preserves commit order.
    Returns:
        None.
    Raises:
        AssertionError: If line orchestration is incorrect.
    """
    creation = _WeakRefTarget()
    research = ResearchCreation(creation_id="creation-id", name="creation-line")
    try:
        with pytest.raises(ValueError, match="creation cannot be None"):
            research.attach_creation(None)

        research.attach_creation(creation)
        assert research.get_creation() is creation

        first = research.begin_mutation(message="first", tags=["a"])
        assert first.parent_id is None
        assert first.metadata == {"message": "first", "tags": ["a"]}

        research.commit_mutation(first)
        assert research.head_id == first.id
        assert research.get_head() is first
        assert research.get_node(first.id) is first

        second = research.begin_mutation(message="second")
        assert second.parent_id == first.id
        research.commit_mutation(second)
        assert research.checkout(first.id) is first
        assert research.head_id == first.id
        assert research.list_nodes() == [first, second]

        with pytest.raises(ValueError, match="node_id cannot be empty"):
            research.get_node("")
        with pytest.raises(KeyError, match="Unknown creation node id"):
            research.get_node("missing")
        with pytest.raises(ValueError, match="node cannot be None"):
            research.commit_mutation(None)  # type: ignore[arg-type]
    finally:
        research.cleanup()
