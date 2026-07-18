import pytest

from melder.mutation_research.research_set.network_versioner import (
    NetworkVersioner,
)


def test_snapshot_is_content_addressed_and_deterministic() -> None:
    """
    Verify identical payloads produce identical addresses regardless of key
    order.
    """
    versioner = NetworkVersioner()
    first = versioner.snapshot({"b": 2, "a": 1})
    second = versioner.snapshot({"a": 1, "b": 2})

    assert first == second
    assert versioner.snapshot_count == 1
    assert len(first) == 64


def test_snapshot_get_returns_detached_value_copy() -> None:
    """
    Verify reads decode fresh copies; the store never leaks.
    """
    versioner = NetworkVersioner()
    address = versioner.snapshot({"lanes": [{"name": "default"}]})
    read = versioner.get(address)
    read["lanes"].append({"name": "injected"})

    assert versioner.get(address) == {"lanes": [{"name": "default"}]}


def test_snapshot_ring_retention_drops_oldest() -> None:
    """
    Verify FIFO retention at the configured bound.
    """
    versioner = NetworkVersioner(max_snapshots=2)
    first = versioner.snapshot({"v": 1})
    second = versioner.snapshot({"v": 2})
    third = versioner.snapshot({"v": 3})

    assert versioner.snapshot_shas() == [second, third]
    assert versioner.has(first) is False
    with pytest.raises(KeyError, match="retention"):
        versioner.get(first)
    assert versioner.latest_sha == third


def test_versioner_validates_bound() -> None:
    """
    Verify the retention bound must be at least one.
    """
    with pytest.raises(ValueError, match="max_snapshots"):
        NetworkVersioner(max_snapshots=0)


def test_versioner_describe_from_payload_roundtrip() -> None:
    """
    Verify describe() and from_payload() are exact inverses.
    """
    versioner = NetworkVersioner(max_snapshots=8)
    versioner.snapshot({"v": 1})
    versioner.snapshot({"v": 2})

    rebuilt = NetworkVersioner.from_payload(versioner.describe())

    assert rebuilt.describe() == versioner.describe()
    assert rebuilt.latest_sha == versioner.latest_sha


def test_versioner_cleanup_is_idempotent_and_guards_reads() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    versioner = NetworkVersioner()
    versioner.snapshot({"v": 1})
    versioner.cleanup()
    versioner.cleanup()

    assert versioner.cleaned is True
    with pytest.raises(RuntimeError):
        versioner.snapshot({"v": 2})


def test_from_payload_refuses_false_content_addresses() -> None:
    """
    Regression (BUG-038): hydration installed `canonical_by_sha` entries
    under their CLAIMED keys without recomputing the digest, so a false
    (for example all-zero) SHA stayed addressable as if content-verified.
    Corrected behavior: every hydrated entry's digest is recomputed and a
    mismatch refuses loudly, naming claimed vs actual.
    """
    versioner = NetworkVersioner()
    address = versioner.snapshot({"lanes": [{"name": "default"}]})
    payload = versioner.describe()
    forged = "0" * 64
    payload["canonical_by_sha"] = {
        forged: payload["canonical_by_sha"][address],
    }
    payload["order"] = [forged]

    with pytest.raises(ValueError, match="content address"):
        NetworkVersioner.from_payload(payload)


def test_from_payload_still_accepts_true_content_addresses() -> None:
    """
    Guard against over-rejection: an untampered describe() payload keeps
    hydrating exactly as before.
    """
    versioner = NetworkVersioner(max_snapshots=4)
    versioner.snapshot({"v": 1})
    address = versioner.latest_sha

    rebuilt = NetworkVersioner.from_payload(versioner.describe())

    assert rebuilt.latest_sha == address
    assert rebuilt.get(address) == {"v": 1}
