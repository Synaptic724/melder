import pytest

from melder.mutation_research.research_set.research_node import ResearchNode


def test_node_requires_spell_sha() -> None:
    """
    Verify the custody-key field is mandatory.
    """
    with pytest.raises(ValueError, match="spell_sha"):
        ResearchNode("")


def test_node_carries_reference_fields_only() -> None:
    """
    Verify the node is reference-based: identity, module world, ancestry -
    never source payloads.
    """
    node = ResearchNode(
        "sha-a",
        module_sha="mod-1",
        parent_shas=["sha-p1", "sha-p2"],
        author="mutation_0",
        reason="composed in workshop",
        campaign="campaign-x",
        metadata={"note": "multi-parent composition"},
    )

    assert node.spell_sha == "sha-a"
    assert node.module_sha == "mod-1"
    assert node.parent_shas == ["sha-p1", "sha-p2"]
    assert node.author == "mutation_0"
    assert node.campaign == "campaign-x"
    payload = node.describe()
    assert "source" not in payload and "payload" not in payload


def test_node_rejects_empty_parent_shas() -> None:
    """
    Verify ancestry entries must be real identities.
    """
    with pytest.raises(ValueError, match="parent_shas"):
        ResearchNode("sha-a", parent_shas=["sha-p1", ""])


def test_node_parent_list_is_detached_and_immutable() -> None:
    """
    Verify parent reads never expose mutable internal state.
    """
    parents = ["sha-p1"]
    node = ResearchNode("sha-a", parent_shas=parents)
    parents.append("sha-p2")
    read = node.parent_shas
    read.append("sha-p3")

    assert node.parent_shas == ["sha-p1"]


def test_node_describe_from_payload_roundtrip() -> None:
    """
    Verify describe() and from_payload() are exact inverses.
    """
    node = ResearchNode(
        "sha-a",
        module_sha="mod-1",
        parent_shas=["sha-p1"],
        author="agent",
        metadata={"k": "v"},
    )

    rebuilt = ResearchNode.from_payload(node.describe())

    assert rebuilt.describe() == node.describe()


def test_node_cleanup_is_idempotent_and_guards_reads() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    node = ResearchNode("sha-a")
    node.cleanup()
    node.cleanup()

    assert node.cleaned is True
    with pytest.raises(RuntimeError):
        _ = node.spell_sha
