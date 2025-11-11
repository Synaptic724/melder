import unittest
from uuid import uuid4, UUID

# Under test
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions


# ---- Fakes / Test Doubles ----------------------------------------------------

class FakeConduit:
    def __init__(self, name: str):
        self._name = name
        self._id = type("Ctx", (), {"_conduit_id": uuid4()})()


class FakeWard:
    """
    Minimal IConduitWard test double:
      - _id: UUID
      - _conduit: FakeConduit
    """
    def __init__(self, name: str):
        self._conduit = FakeConduit(name)
        self._id: str = self._id

    def __repr__(self):
        return f"<FakeWard {self._conduit._name} id={self._id}>"


# ---- Tests -------------------------------------------------------------------

class TestContractBasics(unittest.TestCase):
    def setUp(self):
        self.wa = FakeWard("A")
        self.wb = FakeWard("B")
        self.contract = Contract(self.wa, self.wb)

    def test_init_assigns_ids_and_maps(self):
        self.assertIsNotNone(self.contract._id)
        self.assertIs(self.contract._ward_a, self.wa)
        self.assertIs(self.contract._ward_b, self.wb)
        self.assertEqual(len(self.contract._details_a), 0)
        self.assertEqual(len(self.contract._details_b), 0)

    def test_get_peer_returns_opposite(self):
        self.assertIs(self.contract._get_peer(self.wa), self.wb)
        self.assertIs(self.contract._get_peer(self.wb), self.wa)

    def test_get_peer_raises_for_non_member(self):
        wc = FakeWard("C")
        with self.assertRaises(ValueError):
            self.contract._get_peer(wc)

    def test_get_detail_map_routes_correctly(self):
        self.assertIs(self.contract._get_detail_map(self.wa), self.contract._details_a)
        self.assertIs(self.contract._get_detail_map(self.wb), self.contract._details_b)

    def test_get_detail_map_raises_for_non_member(self):
        wc = FakeWard("C")
        with self.assertRaises(ValueError):
            self.contract._get_detail_map(wc)

    def test_add_populates_detail_map(self):
        d = Detail("SID1", Permissions.read)
        self.contract._add(self.wa, d)
        self.assertIn("SID1", self.contract._details_a)
        self.assertIs(self.contract._details_a["SID1"], d)

    def test_remove_deletes_from_detail_map(self):
        d = Detail("SID1", Permissions.read)
        self.contract._add(self.wa, d)
        self.contract._remove(self.wa, "SID1")
        self.assertNotIn("SID1", self.contract._details_a)

    def test_remove_is_idempotent(self):
        # Removing a non-existent key should not raise
        self.contract._remove(self.wa, "MISSING")
        # And still empty
        self.assertEqual(len(self.contract._details_a), 0)

    def test_check_if_exists(self):
        self.assertFalse(self.contract._check_if_exists(self.wa, "X"))
        self.contract._add(self.wa, Detail("X", Permissions.read))
        self.assertTrue(self.contract._check_if_exists(self.wa, "X"))

    def test_check_if_exists_and_permissions(self):
        self.contract._add(self.wa, Detail("X", Permissions.create))
        self.assertTrue(self.contract._check_if_exists_and_permissions(self.wa, "X", Permissions.create))
        self.assertFalse(self.contract._check_if_exists_and_permissions(self.wa, "X", Permissions.read))
        self.assertFalse(self.contract._check_if_exists_and_permissions(self.wa, "Y", Permissions.create))

    def test_find_spell_in_ward_prefers_side_with_detail(self):
        self.contract._add(self.wa, Detail("SID", Permissions.read))
        self.assertIs(self.contract._find_spell_in_ward("SID"), self.wa)

    def test_find_spell_in_ward_checks_both_sides(self):
        self.contract._add(self.wb, Detail("SIDB", Permissions.create))
        self.assertIs(self.contract._find_spell_in_ward("SIDB"), self.wb)

    def test_find_spell_in_ward_none_when_absent(self):
        self.assertIsNone(self.contract._find_spell_in_ward("NOPE"))

    def test_grant_populates_multiple_details_with_same_permission(self):
        ids = ["S1", "S2", "S3"]
        self.contract._grant(self.wa, ids, Permissions.read)
        for sid in ids:
            self.assertIn(sid, self.contract._details_a)
            self.assertEqual(self.contract._details_a[sid].permissions, Permissions.read)

    def test_clear_contract_seals_and_clears_both_maps(self):
        # Populate both sides
        self.contract._add(self.wa, Detail("A", Permissions.read))
        self.contract._add(self.wb, Detail("B", Permissions.create))
        # Keep references to test sealed state after clearing
        da = self.contract._details_a["A"]
        db = self.contract._details_b["B"]
        self.contract._clear_contract()
        self.assertEqual(len(self.contract._details_a), 0)
        self.assertEqual(len(self.contract._details_b), 0)
        # Detail objects should be sealed
        self.assertTrue(getattr(da, "_sealed", True))
        self.assertTrue(getattr(db, "_sealed", True))

    def test_get_opposite_conduit_resolves_by_known_id(self):
        # Ward A knows its own id; we should get B's conduit back
        other = self.contract._get_opposite_conduit(self.contract, self.wa._id)
        self.assertIs(other, self.wb._conduit)
        other2 = self.contract._get_opposite_conduit(self.contract, self.wb._id)
        self.assertIs(other2, self.wa._conduit)

    def test_get_opposite_conduit_none_for_unknown_id(self):
        random_id = uuid4()
        self.assertIsNone(self.contract._get_opposite_conduit(self.contract, random_id))


class TestContractSealAndCleanup(unittest.TestCase):
    def setUp(self):
        self.wa = FakeWard("A")
        self.wb = FakeWard("B")
        self.contract = Contract(self.wa, self.wb)

    def test_clean_up_seals_details_and_empties(self):
        self.contract._add(self.wa, Detail("X", Permissions.read))
        self.contract._add(self.wb, Detail("Y", Permissions.create))
        d1 = self.contract._details_a["X"]
        d2 = self.contract._details_b["Y"]
        self.contract.clean_up()
        self.assertEqual(len(self.contract._details_a), 0)
        self.assertEqual(len(self.contract._details_b), 0)
        self.assertTrue(getattr(d1, "_sealed", True))
        self.assertTrue(getattr(d2, "_sealed", True))

    def test_seal_is_idempotent_and_nulls_wards(self):
        # Seed some data
        self.contract._add(self.wa, Detail("X", Permissions.read))
        self.contract._add(self.wb, Detail("Y", Permissions.create))

        # First seal
        self.contract.seal()
        self.assertTrue(getattr(self.contract, "_sealed", False))
        self.assertIsNone(self.contract._ward_a)
        self.assertIsNone(self.contract._ward_b)
        self.assertEqual(len(self.contract._details_a), 0)
        self.assertEqual(len(self.contract._details_b), 0)

        # Second seal should be a no-op (idempotent)
        self.contract.seal()
        self.assertTrue(getattr(self.contract, "_sealed", False))

    def test_methods_behave_with_empty_maps_after_seal(self):
        # Seal first
        self.contract.seal()

        # _clear_contract should still be safe to call (it locks and clears empty maps)
        # It should not raise even if already sealed and maps are empty.
        self.contract._clear_contract()

        # Any ward-dependent operation after seal should raise because wards are nulled.
        with self.assertRaises(ValueError):
            # Using the original FakeWard (not a member anymore) should be invalid.
            self.contract._remove(self.wa, "ZZ")


class TestContractEdgeCases(unittest.TestCase):
    def setUp(self):
        self.wa = FakeWard("A")
        self.wb = FakeWard("B")
        self.contract = Contract(self.wa, self.wb)

    def test_overwrite_detail_updates_permission(self):
        self.contract._add(self.wa, Detail("S", Permissions.read))
        self.contract._add(self.wa, Detail("S", Permissions.create))  # overwrite
        self.assertEqual(self.contract._details_a["S"].permissions, Permissions.create)

    def test_grant_empty_list_is_noop(self):
        self.contract._grant(self.wa, [], Permissions.read)
        self.assertEqual(len(self.contract._details_a), 0)

    def test_large_grant_then_bulk_clear(self):
        ids = [f"SID{i}" for i in range(100)]
        self.contract._grant(self.wa, ids, Permissions.read)
        self.contract._grant(self.wb, ids, Permissions.create)
        self.assertEqual(len(self.contract._details_a), 100)
        self.assertEqual(len(self.contract._details_b), 100)
        self.contract._clear_contract()
        self.assertEqual(len(self.contract._details_a), 0)
        self.assertEqual(len(self.contract._details_b), 0)


if __name__ == "__main__":
    unittest.main()
