import pytest

from melder.mutation_research.research_set.residence_registry import (
    ResidenceRegistry,
)


def test_claim_registers_single_residence() -> None:
    """
    Verify a fresh identity claims into exactly one lane.
    """
    registry = ResidenceRegistry()
    registry.claim("sha-a", "lane-1")

    assert registry.residence_of("sha-a") == "lane-1"
    assert registry.is_resident("sha-a") is True
    assert registry.resident_count == 1


def test_claim_collision_is_rediscovery_naming_the_holder() -> None:
    """
    Verify the single-residence invariant: a second claim anywhere raises
    and names the holding lane (identical content rebinds to the same SHA).
    """
    registry = ResidenceRegistry()
    registry.claim("sha-a", "lane-1")

    with pytest.raises(RuntimeError, match="Rediscovery.*lane-1"):
        registry.claim("sha-a", "lane-2")
    with pytest.raises(RuntimeError, match="Rediscovery.*lane-1"):
        registry.claim("sha-a", "lane-1")


def test_claim_validates_inputs() -> None:
    """
    Verify empty identities and lanes are refused.
    """
    registry = ResidenceRegistry()

    with pytest.raises(ValueError, match="spell_id"):
        registry.claim("", "lane-1")
    with pytest.raises(ValueError, match="lane_id"):
        registry.claim("sha-a", "")


def test_transfer_repoints_all_or_nothing() -> None:
    """
    Verify the join mechanic: every identity must be resident or nothing
    moves.
    """
    registry = ResidenceRegistry()
    registry.claim("sha-a", "lane-1")
    registry.claim("sha-b", "lane-1")

    with pytest.raises(KeyError, match="sha-missing"):
        registry.transfer(["sha-a", "sha-missing"], "lane-2")
    assert registry.residence_of("sha-a") == "lane-1"

    registry.transfer(["sha-a", "sha-b"], "lane-2")
    assert registry.residence_of("sha-a") == "lane-2"
    assert registry.residence_of("sha-b") == "lane-2"


def test_registry_has_no_release_verb() -> None:
    """
    Verify residence is permanent by construction (no release surface).
    """
    registry = ResidenceRegistry()

    assert not hasattr(registry, "release")
    assert not hasattr(registry, "remove")


def test_registry_describe_from_payload_roundtrip() -> None:
    """
    Verify describe() and from_payload() are exact inverses.
    """
    registry = ResidenceRegistry()
    registry.claim("sha-a", "lane-1")
    registry.claim("sha-b", "lane-2")

    rebuilt = ResidenceRegistry.from_payload(registry.describe())

    assert rebuilt.describe() == registry.describe()


def test_registry_cleanup_is_idempotent_and_guards_reads() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    registry = ResidenceRegistry()
    registry.claim("sha-a", "lane-1")
    registry.cleanup()
    registry.cleanup()

    assert registry.cleaned is True
    with pytest.raises(RuntimeError):
        registry.claim("sha-b", "lane-1")
