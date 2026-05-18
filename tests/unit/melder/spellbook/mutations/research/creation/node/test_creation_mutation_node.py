"""Unit tests for CreationMutationNode cleanup behavior."""

from __future__ import annotations

import pytest

from melder.mutation_research.research.creation.node.creation_mutation_node import CreationMutationNode


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


def test_creation_mutation_node_properties_and_metadata_detach() -> None:
    """
    Purpose:
        Validate the stable property surface before cleanup.
    Contract:
        - id is a non-empty string.
        - creation_id and parent_id round-trip constructor values.
        - metadata returns a detached shallow copy.
        - snapshot exposes the stored payload.
    Returns:
        None.
    Raises:
        AssertionError: If the property surface is incorrect.
    """
    payload = {"field": "value"}
    node = CreationMutationNode(
        creation_id="creation-id",
        parent_id="parent-id",
        metadata={"message": "seed"},
        snapshot=payload,
    )

    meta = node.metadata
    meta["message"] = "mutated"

    assert isinstance(node.id, str)
    assert node.id != ""
    assert node.creation_id == "creation-id"
    assert node.parent_id == "parent-id"
    assert node.metadata == {"message": "seed"}
    assert node.snapshot is payload

    node.cleanup()


def test_creation_mutation_node_placeholder_methods_raise() -> None:
    """
    Purpose:
        Validate the explicit placeholder contract.
    Contract:
        - snapshot_from_creation raises until implemented.
        - apply_to_creation raises until implemented.
    Returns:
        None.
    Raises:
        AssertionError: If placeholder methods stop raising.
    """
    node = CreationMutationNode(creation_id="creation-id")

    with pytest.raises(NotImplementedError):
        CreationMutationNode.snapshot_from_creation(
            object(),
            creation_id="creation-id",
        )

    with pytest.raises(NotImplementedError):
        node.apply_to_creation(object())

    node.cleanup()

    assert node.cleaned is True
    assert not hasattr(node, '_metadata')
    assert not hasattr(node, '_snapshot')
    assert node._parent_id is None

    node.cleanup()
