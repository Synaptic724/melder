"""Unit tests for CreationMutationNode cleanup behavior."""

from __future__ import annotations

from melder.spellbook.mutations.research.creation.node.creation_mutation_node import CreationMutationNode


def test_creation_mutation_node_cleanup_clears_payloads() -> None:
    """
    Purpose:
        Validate CreationMutationNode cleanup clears metadata and snapshot payloads.
    Contract:
        - cleanup() marks the node as cleaned.
        - cleanup() clears parent_id and payload references.
        - cleanup() is idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear node payloads.
    """
    node = CreationMutationNode(
        creation_id="creation-id",
        parent_id="parent-id",
        metadata={"message": "seed"},
        snapshot={"field": "value"},
    )

    node.cleanup()

    assert node.cleaned is True
    assert node._metadata is None
    assert node._snapshot is None
    assert node._parent_id is None

    node.cleanup()
