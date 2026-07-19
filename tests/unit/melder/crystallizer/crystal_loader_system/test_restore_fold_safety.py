"""
Unit safety tests for RestoreEngine._fold_chain (wave 3, 2026-07-19): the
fold IS the recorded-truth compiler - later-wins per (kind, key), tombstone
sweeps, custody routing, and the honesty guard. Every row seeds a synthetic
chain and folds it directly; nothing replays.

Runs only on 3.14t (melder package root import chain).
"""
from melder.crystallizer.crystal_loader_system.restore_engine import (
    RestoreEngine,
)


def _engine(windows):
    """
    Build one engine over the supplied windows.

    Returns:
        RestoreEngine: Engine whose chain is the given window list.
    """
    return RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-{0}".format(i) for i in range(len(windows))],
        chain=windows,
    )


def test_later_window_wins_per_kind_and_key():
    """
    Purpose:
        Pin the later-wins law: the newest window's payload replaces the
        older one for the same (kind, key); distinct keys coexist.
    Contract:
        book b1 folds to version 2; book b2 (older window only) survives.
    Returns:
        None.
    Raises:
        AssertionError: If fold order or key isolation drifts.
    """
    engine = _engine([
        {"journal": [[1, "spellbook", "b1"], [2, "spellbook", "b2"]],
         "payloads": {"spellbook": {
             "b1": {"version": 1}, "b2": {"version": 7}}}},
        {"journal": [[3, "spellbook", "b1"]],
         "payloads": {"spellbook": {"b1": {"version": 2}}}},
    ])
    try:
        engine._fold_chain()
        assert engine._books["b1"] == {"version": 2}
        assert engine._books["b2"] == {"version": 7}
    finally:
        engine.cleanup()


def test_spellbook_tombstone_sweeps_book_custody_and_indexes():
    """
    Purpose:
        Pin the subtree sweep: spellbook_removed evicts the book twin,
        its custody entries (both stores), and its indexes - matching the
        live eviction rules.
    Contract:
        Only the unrelated book's material survives the fold.
    Returns:
        None.
    Raises:
        AssertionError: If any subtree member survives its tombstone.
    """
    engine = _engine([
        {"journal": [
            [1, "spellbook", "dead"], [2, "spellbook", "alive"],
            [3, "spell_crystal", "sha-dead"],
            [4, "spell_crystal", "sha-alive"],
            [5, "spell_index", "idx-dead"],
            [6, "spellbook_removed", "dead"],
        ],
         "payloads": {
             "spellbook": {"dead": {}, "alive": {}},
             "spell_crystal": {
                 "sha-dead": {"spellbook_id": "dead"},
                 "sha-alive": {"spellbook_id": "alive"},
             },
             "spell_index": {"idx-dead": {"spellbook_id": "dead"}},
             "spellbook_removed": {"dead": {"removed": True}},
         }},
    ])
    try:
        engine._fold_chain()
        assert "dead" not in engine._books
        assert "alive" in engine._books
        assert "sha-dead" not in engine._custody_active
        assert "sha-alive" in engine._custody_active
        assert "idx-dead" not in engine._indexes
    finally:
        engine.cleanup()


def test_journal_entry_without_payload_reports_honesty_shortfall():
    """
    Purpose:
        Pin the honesty guard (triage lesson): a journaled entry with no
        captured payload and no explaining removal is a capture anomaly -
        reported, never silently skipped.
    Contract:
        One shortfall row names the kind/key with the anomaly reason.
    Returns:
        None.
    Raises:
        AssertionError: If the capture gap folds silently.
    """
    engine = _engine([
        {"journal": [[1, "spellbook", "ghost"]], "payloads": {}},
    ])
    try:
        engine._fold_chain()
        payload = engine._report.describe()
        assert payload["shortfalls"] == [{
            "kind": "spellbook", "key": "ghost",
            "reason": "journal_entry_without_captured_payload",
        }]
        assert "ghost" not in engine._books
    finally:
        engine.cleanup()


def test_same_window_record_then_remove_folds_silently():
    """
    Purpose:
        Pin the BUG-163 churn lane: an identity emitted then removed
        before the seal leaves a payload-less emission entry that the
        later same-window tombstone fully explains - normal churn, no
        shortfall.
    Contract:
        Zero shortfalls; the key is absent from the folded store.
    Returns:
        None.
    Raises:
        AssertionError: If normal churn is reported as an anomaly.
    """
    engine = _engine([
        {"journal": [
            [1, "contract", "gone"], [2, "contract_removed", "gone"],
        ],
         "payloads": {"contract_removed": {"gone": {"removed": True}}}},
    ])
    try:
        engine._fold_chain()
        assert engine._report.describe()["shortfalls"] == []
        assert "gone" not in engine._contracts
    finally:
        engine.cleanup()


def test_custody_location_routes_between_stores():
    """
    Purpose:
        Pin custody routing: the capture's custody_location decides the
        folded store, and an unannotated payload defaults active (old
        cached checkpoints predate the annotation).
    Contract:
        inactive -> _custody_inactive; absent annotation -> active.
    Returns:
        None.
    Raises:
        AssertionError: If custody routing drifts.
    """
    engine = _engine([
        {"journal": [
            [1, "spell_crystal", "sha-parked"],
            [2, "spell_crystal", "sha-legacy"],
        ],
         "payloads": {"spell_crystal": {
             "sha-parked": {"custody_location": "inactive"},
             "sha-legacy": {},
         }}},
    ])
    try:
        engine._fold_chain()
        assert "sha-parked" in engine._custody_inactive
        assert "sha-parked" not in engine._custody_active
        assert "sha-legacy" in engine._custody_active
    finally:
        engine.cleanup()


def test_spell_activity_flips_custody_between_stores():
    """
    Purpose:
        Pin the activity flip: a spell_activity entry moves folded custody
        to the store its current-truth payload names.
    Contract:
        active custody + {"active": False} activity -> inactive store.
    Returns:
        None.
    Raises:
        AssertionError: If the flip loses or duplicates custody.
    """
    engine = _engine([
        {"journal": [
            [1, "spell_crystal", "sha-1"],
            [2, "spell_activity", "sha-1"],
        ],
         "payloads": {
             "spell_crystal": {"sha-1": {"custody_location": "active"}},
             "spell_activity": {"sha-1": {"active": False}},
         }},
    ])
    try:
        engine._fold_chain()
        assert "sha-1" in engine._custody_inactive
        assert "sha-1" not in engine._custody_active
    finally:
        engine.cleanup()


def test_spell_removed_evicts_both_custody_stores():
    """
    Purpose:
        Pin true removal: spell_removed clears the SHA from whichever
        custody store holds it.
    Contract:
        Both an active and a parked spell leave the fold when removed.
    Returns:
        None.
    Raises:
        AssertionError: If removed custody survives.
    """
    engine = _engine([
        {"journal": [
            [1, "spell_crystal", "sha-a"],
            [2, "spell_crystal", "sha-p"],
        ],
         "payloads": {"spell_crystal": {
             "sha-a": {}, "sha-p": {"custody_location": "inactive"},
         }}},
        {"journal": [
            [3, "spell_removed", "sha-a"], [4, "spell_removed", "sha-p"],
        ],
         "payloads": {"spell_removed": {
             "sha-a": {"removed": True}, "sha-p": {"removed": True},
         }}},
    ])
    try:
        engine._fold_chain()
        assert engine._custody_active == {}
        assert engine._custody_inactive == {}
    finally:
        engine.cleanup()


def test_contract_and_cluster_tombstones_evict_their_twins():
    """
    Purpose:
        Pin relationship eviction: contract_removed and cluster_removed
        delete their folded twins across windows.
    Contract:
        Neither identity survives; the untouched contract does.
    Returns:
        None.
    Raises:
        AssertionError: If a severed relationship survives the fold.
    """
    engine = _engine([
        {"journal": [
            [1, "contract", "ct-dead"], [2, "contract", "ct-alive"],
            [3, "cluster", "cl-dead"],
        ],
         "payloads": {
             "contract": {"ct-dead": {}, "ct-alive": {}},
             "cluster": {"cl-dead": {}},
         }},
        {"journal": [
            [4, "contract_removed", "ct-dead"],
            [5, "cluster_removed", "cl-dead"],
        ],
         "payloads": {
             "contract_removed": {"ct-dead": {"removed": True}},
             "cluster_removed": {"cl-dead": {"removed": True}},
         }},
    ])
    try:
        engine._fold_chain()
        assert "ct-dead" not in engine._contracts
        assert "ct-alive" in engine._contracts
        assert engine._clusters == {}
    finally:
        engine.cleanup()


def test_nexus_state_and_boot_slots_fold_later_wins():
    """
    Purpose:
        Pin the singleton slots: the nexus lifecycle flip keeps only the
        LAST journaled state name, and the recorder's own policy twin
        folds to the boot-time slot (never replayed mid-restore).
    Contract:
        _nexus_state_name reads the newest flip; _crystallizer_payload
        carries the policy payload; frame_removed sweeps its frame.
    Returns:
        None.
    Raises:
        AssertionError: If a singleton slot drifts from later-wins.
    """
    engine = _engine([
        {"journal": [
            [1, "nexus", "root"],
            [2, "nexus_state", "enabled"],
            [3, "crystallizer", "policy"],
            [4, "frame", "doomed"],
        ],
         "payloads": {
             "nexus": {"root": {"activated": True}},
             "nexus_state": {"enabled": {"state": "enabled"}},
             "crystallizer": {"policy": {"knob": 1}},
             "frame": {"doomed": {}},
         }},
        {"journal": [
            [5, "nexus_state", "disabled"],
            [6, "frame_removed", "doomed"],
        ],
         "payloads": {
             "nexus_state": {"disabled": {"state": "disabled"}},
             "frame_removed": {"doomed": {"removed": True}},
         }},
    ])
    try:
        engine._fold_chain()
        assert engine._nexus_state_name == "disabled"
        assert engine._crystallizer_payload == {"knob": 1}
        assert engine._nexus_payload == {"activated": True}
        assert "doomed" not in engine._frames
    finally:
        engine.cleanup()
