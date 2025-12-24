"""Unit tests for ResearchCreation cleanup behavior."""

from __future__ import annotations

import pytest

from melder.spellbook.mutations.research.creation.creation_research import ResearchCreation


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
