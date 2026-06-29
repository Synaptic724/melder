import threading

import pytest

from melder.aether.aetheric_frame.lookup_container import LookupContainer


def test_claim_then_get_returns_spell_id():
    """claim records the signature; get returns the active spell_id."""
    c = LookupContainer()
    c.claim(("frame", "bind"), "sid-1")
    assert c.get(("frame", "bind")) == "sid-1"


def test_get_missing_returns_none():
    """get returns None for an unclaimed signature."""
    c = LookupContainer()
    assert c.get(("frame", "bind")) is None


def test_contains_reflects_claim_and_release():
    """contains is True after claim, False after release."""
    c = LookupContainer()
    key = ("frame", "bind")
    assert c.contains(key) is False
    c.claim(key, "sid-1")
    assert c.contains(key) is True
    c.release(key)
    assert c.contains(key) is False


def test_claim_same_spell_id_is_idempotent():
    """Re-claiming a signature for the same spell_id does not raise."""
    c = LookupContainer()
    key = ("frame", "bind")
    c.claim(key, "sid-1")
    c.claim(key, "sid-1")
    assert c.get(key) == "sid-1"


def test_claim_different_spell_id_raises_and_keeps_original():
    """Claiming an active signature for a different spell_id raises; state is unchanged."""
    c = LookupContainer()
    key = ("frame", "bind")
    c.claim(key, "sid-1")
    with pytest.raises(RuntimeError, match="already active in this frame"):
        c.claim(key, "sid-2")
    assert c.get(key) == "sid-1"


def test_update_repoints_signature():
    """update re-points an active signature to a new spell_id (notch)."""
    c = LookupContainer()
    key = ("frame", "bind")
    c.claim(key, "sid-1")
    c.update(key, "sid-2")
    assert c.get(key) == "sid-2"


def test_update_sets_fresh_signature():
    """update sets a signature even when previously unclaimed."""
    c = LookupContainer()
    key = ("frame", "bind")
    c.update(key, "sid-1")
    assert c.get(key) == "sid-1"


def test_release_absent_is_noop():
    """Releasing an unclaimed signature is a no-op."""
    c = LookupContainer()
    c.release(("frame", "bind"))
    assert c.get(("frame", "bind")) is None


def test_release_frees_signature_for_other_spell():
    """Once released, a signature is free for a different spell_id."""
    c = LookupContainer()
    key = ("frame", "bind")
    c.claim(key, "sid-1")
    c.release(key)
    c.claim(key, "sid-2")
    assert c.get(key) == "sid-2"


def test_distinct_keys_coexist():
    """Different signatures hold independent spell_ids."""
    c = LookupContainer()
    c.claim(("f1", "b"), "sid-1")
    c.claim(("f2", "b"), "sid-2")
    assert c.get(("f1", "b")) == "sid-1"
    assert c.get(("f2", "b")) == "sid-2"


def test_cleanup_is_idempotent():
    """cleanup runs once and a second call is a safe no-op."""
    c = LookupContainer()
    c.claim(("frame", "bind"), "sid-1")
    c.cleanup()
    c.cleanup()


def test_concurrent_claims_of_distinct_keys_all_land():
    """Parallel claims on distinct signatures all succeed under the internal lock."""
    c = LookupContainer()
    keys = [("frame", "b%d" % i) for i in range(64)]

    def worker(k):
        c.claim(k, "sid-" + k[1])

    threads = [threading.Thread(target=worker, args=(k,)) for k in keys]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for k in keys:
        assert c.get(k) == "sid-" + k[1]


def test_concurrent_same_key_same_spell_id_is_safe():
    """Parallel idempotent claims on one signature neither raise nor corrupt."""
    c = LookupContainer()
    key = ("frame", "bind")
    errors = []

    def worker():
        try:
            c.claim(key, "sid-1")
        except RuntimeError as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(32)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert c.get(key) == "sid-1"
