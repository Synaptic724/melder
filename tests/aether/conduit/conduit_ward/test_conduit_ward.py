import unittest
from uuid import uuid4, UUID
from unittest.mock import patch

# SUT imports
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.interfaces import IConduit, ISpell


# -----------------------------
# Protocol-compliant fakes
# -----------------------------
class _FakeCreationContext:
    def __init__(self, cid: UUID | None = None):
        self._conduit_id: UUID = cid or uuid4()


class _FakeSpellbook:
    """
    Minimal spellbook stub used by ConduitWard internals.
    Tracks only *contracted* spells. Ownership lives on the conduit.
    """
    def __init__(self, owner_conduit: "FakeConduit"):
        self._owner = owner_conduit
        self._created_link_contracts: list[UUID] = []
        self._severed_link_contracts: list[UUID] = []
        self._added: list[tuple[str, UUID]] = []     # (spell_id, peer_conduit_id)
        self._removed: list[tuple[str, UUID]] = []   # (spell_id, peer_conduit_id)
        self._cleared_for: list[UUID] = []

        # Contracted spells keyed by peer conduit id -> set(spell_id)
        self._by_peer: dict[UUID, set[str]] = {}

    def _create_link_contract(self, peer_id: UUID) -> None:
        self._created_link_contracts.append(peer_id)
        self._by_peer.setdefault(peer_id, set())

    def _sever_link_contract(self, peer_id: UUID) -> None:
        self._severed_link_contracts.append(peer_id)
        # Severing a link implies the contract is gone; clear contracted spells from that peer.
        for sid in list(self._by_peer.get(peer_id, set())):
            self._owner._contracted_spells.pop(sid, None)
        self._by_peer.pop(peer_id, None)

    def _add_contracted_spell(self, spell: "FakeSpell", peer_conduit_id: UUID) -> None:
        # record in owner's contracted registry so find_contracted_spell() returns it
        self._owner._contracted_spells[spell.spell_id] = spell
        self._by_peer.setdefault(peer_conduit_id, set()).add(spell.spell_id)
        self._added.append((spell.spell_id, peer_conduit_id))

    def _remove_contracted_spell(self, spell_id: str, peer_conduit_id: UUID) -> None:
        self._by_peer.setdefault(peer_conduit_id, set()).discard(spell_id)
        self._owner._contracted_spells.pop(spell_id, None)
        self._removed.append((spell_id, peer_conduit_id))

    def _clear_contracted_spells_for_conduit(self, peer_conduit_id: UUID) -> None:
        # Remove all spells granted by peer_conduit_id
        for sid in list(self._by_peer.get(peer_conduit_id, set())):
            self._owner._contracted_spells.pop(sid, None)
        self._by_peer.pop(peer_conduit_id, None)
        self._cleared_for.append(peer_conduit_id)

    def _find_contracted_spell(self, spell_id: str):
        return self._owner._contracted_spells.get(spell_id)


class FakeSpell(ISpell):
    def __init__(
            self,
            spell_id: str,
            name: str = "S",
            owner_id: UUID | None = None,
            perm: Permissions = Permissions.create,
            frame: str = "F",
            bind_name: str = "__default__",
    ):
        self.spell_id = spell_id
        self.__name__ = name
        self._owner_conduit_id = owner_id
        self._permissions = perm
        self.permissions = perm  # some code reads .permissions
        self.spellframe = frame
        self.spell_name = name
        self.binding_name = bind_name


class FakeConduit(IConduit):
    def __init__(
            self,
            name: str | None = None,
            state: ConduitState = ConduitState.normal,
            cid: UUID | None = None,
    ):
        self._name = name
        self._conduit_state = state
        self._id = _FakeCreationContext(cid)
        self._conduit_ward = None  # set by tests
        self._spellbook = _FakeSpellbook(self)
        self._parent_conduit = None

        # Distinguish OWNED vs CONTRACTED spells
        self._owned_spells: dict[str, FakeSpell] = {}
        self._contracted_spells: dict[str, FakeSpell] = {}

        # Peers
        self._conduits_by_id: dict[str, "FakeConduit"] = {}

    # Ward calls:
    def get_spell_by_id(self, spell_id: str, aetheric_frame: str = "default"):
        return self._owned_spells.get(spell_id)

    def inspect_spell(self, spell: ISpell, aetheric_frame: str = "default") -> str | None:
        return getattr(spell, "spell_id", None)

    def get_conduit_by_id(self, conduit_id: str, aetheric_frame: str = "default"):
        return self._conduits_by_id.get(conduit_id)

    def find_contracted_spell(self, spell_id: str):
        # MUST return contracted only (not owned)
        return self._contracted_spells.get(spell_id)

    # helpers for tests
    def register_peer(self, other: "FakeConduit"):
        self._conduits_by_id[other._id] = other


# -----------------------------
# Lightweight in-memory Contract/Detail patches
# -----------------------------
class _PatchedDetail:
    def __init__(self, spell_id: str, permissions: Permissions):
        self.spell_id = spell_id
        self.permissions = permissions


class _PatchedContract:
    """
    Symmetric contract between two wards.
    Stores: what each ward has received from the peer.
    """
    def __init__(self, ward_a: ConduitWard, ward_b: ConduitWard):
        from threading import RLock
        self._id = uuid4()
        self._ward_a = ward_a
        self._ward_b = ward_b
        self._lock = RLock()

        # what each ward has received from the peer (spell_id -> Detail)
        self._to_a: dict[str, _PatchedDetail] = {}
        self._to_b: dict[str, _PatchedDetail] = {}

    def _get_peer(self, ward: ConduitWard) -> ConduitWard:
        return self._ward_b if ward is self._ward_a else self._ward_a

    def _get_detail_map(self, ward: ConduitWard) -> dict[str, _PatchedDetail]:
        # spells granted to this ward
        return self._to_a if ward is self._ward_a else self._to_b

    def _check_if_exists_and_permissions(self, ward: ConduitWard, spell_id: str, permissions: Permissions) -> bool:
        m = self._get_detail_map(ward)
        d = m.get(spell_id)
        return d is not None and d.permissions == permissions

    def _check_if_exists(self, ward: ConduitWard, spell_id: str) -> bool:
        return spell_id in self._get_detail_map(ward)

    def _add(self, grantee: ConduitWard, detail: _PatchedDetail):
        self._get_detail_map(grantee)[detail.spell_id] = detail

    def _remove(self, grantee: ConduitWard, spell_id: str):
        self._get_detail_map(grantee).pop(spell_id, None)

    def _clear_contract(self):
        self._to_a.clear()
        self._to_b.clear()

    def _find_spell_in_ward(self, spell_id: str):
        if spell_id in self._to_a:
            return self._ward_a
        if spell_id in self._to_b:
            return self._ward_b
        return None

    def seal(self):
        pass


# -----------------------------
# Test Suite
# -----------------------------
@patch("melder.aether.conduit.conduit_ward.conduit_ward.Contract", _PatchedContract)
@patch("melder.aether.conduit.conduit_ward.conduit_ward.Detail", _PatchedDetail)
class TestConduitWard(unittest.TestCase):
    def setUp(self):
        # Two normal dynamic conduits with wards
        self.c1 = FakeConduit(name="C1", state=ConduitState.normal)
        self.c2 = FakeConduit(name="C2", state=ConduitState.normal)

        self.c1.register_peer(self.c2)
        self.c2.register_peer(self.c1)

        self.w1 = ConduitWard(self.c1, dynamic=True, conduit_type=ConduitState.normal, policy=Policies.dynamic)
        self.w2 = ConduitWard(self.c2, dynamic=True, conduit_type=ConduitState.normal, policy=Policies.dynamic)

        self.c1._conduit_ward = self.w1
        self.c2._conduit_ward = self.w2

        # IMPORTANT:
        # Current prod adds contracted spells to the *provider's* spellbook side.
        # We therefore set ownership to the *grantee* (c2), but expect contracted
        # entries to appear under c1.find_contracted_spell(...).
        self.sp1 = FakeSpell(
            "SID1",
            name="Foo",
            owner_id=self.c2._id,  # owner == grantee (c2)
            perm=Permissions.create,
        )
        # OWNED spells live in the owner's OWNED map
        self.c2._owned_spells[self.sp1.spell_id] = self.sp1

    # ---- Linking basics ----
    def test_link_creates_contract_and_indexes(self):
        ok = self.w1._link(self.c2)
        self.assertTrue(ok)
        self.assertEqual(len(self.w1._contracts), 1)
        self.assertEqual(len(self.w2._contracts), 1)
        c2id = self.c2._id
        c1id = self.c1._id
        self.assertIn(c2id, self.w1._initiated_index)
        self.assertIn(c1id, self.w2._received_index)
        self.assertEqual(self.c2._spellbook._created_link_contracts, [c2id])

    def test_link_is_idempotent(self):
        self.assertTrue(self.w1._link(self.c2))
        self.assertTrue(self.w1._link(self.c2))
        self.assertEqual(len(self.w1._contracts), 1)
        self.assertEqual(len(self.w2._contracts), 1)

    def test_find_contract_id_and_find_contract(self):
        self.w1._link(self.c2)
        cid = self.w1._find_contract_id(self.c2)
        self.assertIsInstance(cid, UUID)
        c = self.w1._find_contract(self.c2)
        self.assertIsNotNone(c)

    def test_sever_link_removes_indexes_and_spellbook_link(self):
        self.w1._link(self.c2)
        self.assertTrue(self.w1._sever_link(self.c2))
        self.assertEqual(len(self.w1._contracts), 0)
        self.assertEqual(len(self.w2._contracts), 0)
        c2id = self.c2._id
        c1id = self.c1._id
        self.assertNotIn(c2id, self.w1._initiated_index)
        self.assertNotIn(c1id, self.w2._received_index)
        self.assertIn(c1id, self.c2._spellbook._severed_link_contracts)
        self.assertIn(c2id, self.c1._spellbook._severed_link_contracts)

    # ---- Policies ----
    def test_set_new_policy_rejects_block_whitelist_if_contracts_exist(self):
        self.w1._link(self.c2)
        with self.assertRaises(RuntimeError):
            self.w1._set_new_policy(Policies.block_all)
        with self.assertRaises(RuntimeError):
            self.w1._set_new_policy(Policies.whitelist_all)

    def test_set_new_policy_rejects_automatic_in_dynamic(self):
        with self.assertRaises(RuntimeError):
            self.w1._set_new_policy(Policies.automatic)

    # ---- Lesser conduit lineage ----
    def test_link_lesser_and_recursive_get(self):
        lesser = FakeConduit(name="L", state=ConduitState.lesser)
        self.c1.register_peer(lesser)
        lesser._conduit_ward = ConduitWard(lesser, dynamic=True, conduit_type=ConduitState.lesser, policy=Policies.lesser_conduit)

        self.w1._link_lesser_conduit(lesser)
        got = self.w1._get_lesser_conduit(lesser._id)
        self.assertIs(got, lesser)

        # allow lesser to upgrade (no children, has parent)
        lesser._conduit_ward._lesser_conduits.clear()
        lesser._conduit_ward._parent_conduit = self.c1
        lesser._conduit_ward._convert_to_normal_conduit()
        self.assertEqual(lesser._conduit_ward._conduit_type, ConduitState.normal)

    # ---- Contracting spells: add/remove/bulk ----
    def test_add_spell_rejects_when_no_link(self):
        with self.assertRaises(RuntimeError):
            self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)

    def test_add_spell_rejects_by_policy_block_all(self):
        self.w2._policy = Policies.block_all
        self.w1._link(self.c2)
        with self.assertRaises(RuntimeError):
            self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)

    def test_add_spell_rejects_permission_mismatch(self):
        sp_read = FakeSpell(
            "SID2",
            name="RO",
            owner_id=self.c2._id,  # owner == grantee (c2)
            perm=Permissions.read,
        )
        self.c2._owned_spells[sp_read.spell_id] = sp_read
        self.w1._link(self.c2)
        with self.assertRaises(RuntimeError):
            self.w1._add_spell_to_contract(spell=sp_read, conduit=self.c2, permissions="create")

    def test_add_spell_to_contract_happy_path(self):
        self.w1._link(self.c2)
        ok = self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2, permissions="create")
        self.assertTrue(ok)
        # NOTE: current prod adds to *provider* spellbook; check c1, not c2
        self.assertIsNotNone(self.c1.find_contracted_spell(self.sp1.spell_id))

    def test_add_spells_to_contract_reports_success_and_failures(self):
        self.w1._link(self.c2)
        sp2 = FakeSpell("SID2", owner_id=self.c2._id, perm=Permissions.create)
        # OWNED by c2
        self.c2._owned_spells[sp2.spell_id] = sp2
        # IMPORTANT: bulk path resolves by *self._conduit* (c1), so make c1 able to resolve IDs
        self.c1._owned_spells[self.sp1.spell_id] = self.sp1
        self.c1._owned_spells[sp2.spell_id] = sp2

        report = self.w1._add_spells_to_contract(
            spell_ids=["SID1", "SID2", "NOPE"],
            conduit=self.c2,
            permissions="create",
        )
        self.assertEqual(set(report["success"]), {"SID1", "SID2"})
        self.assertIn("NOPE", report["failed"])

    def test_remove_spell_from_contract(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        self.w1._remove_spell_from_contract(spell=self.sp1, conduit=self.c2)
        # removal should reflect on the side that had it (provider per current prod)
        self.assertIsNone(self.c1.find_contracted_spell(self.sp1.spell_id))

    def test_remove_all_spells_from_contract(self):
        self.w1._link(self.c2)
        sp2 = FakeSpell("SID2", owner_id=self.c2._id, perm=Permissions.create)
        self.c2._owned_spells[sp2.spell_id] = sp2
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        self.w1._add_spell_to_contract(spell=sp2, conduit=self.c2)

        ok = self.w1._remove_all_spells_from_contract(conduit=self.c2)
        self.assertTrue(ok)
        # both contracted spells should be gone from provider (c1) under current prod
        self.assertIsNone(self.c1.find_contracted_spell(self.sp1.spell_id))
        self.assertIsNone(self.c1.find_contracted_spell(sp2.spell_id))

    # ---- Query helpers ----
    def test_get_all_spells_in_contracts_and_by_conduit(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        # The "received" spells live as DETAILS on w2; the object resolution consults *peer* spellbook (c1)
        all_spells = self.w2._get_all_spells_in_contracts()
        self.assertIsInstance(all_spells, dict)
        self.assertEqual(len(list(all_spells.values())[0]), 1)

        peer_id = self.c1._id  # from c2's POV, the peer is c1
        by_peer = self.w2._get_spells_in_contract_by_conduit(peer_id)
        self.assertIn(("SID1", self.c1.find_contracted_spell("SID1")), by_peer["inbound"])

    def test_get_spells_in_contract_by_conduit_name(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        # From grantee POV (c2), peer name is "C1"
        by_name = self.w2._get_spells_in_contract_by_conduit_name("C1")
        self.assertIsNotNone(by_name)
        self.assertTrue(any(sid == "SID1" for sid, _ in by_name["inbound"]))

    def test_get_spell_in_contracts(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        found = self.w2._get_spell_in_contracts("SID1")  # grantee finds inbound
        self.assertIsNotNone(found)
        peer_id, spell = found
        self.assertIsInstance(peer_id, UUID)
        self.assertEqual(spell.spell_id, "SID1")

    def test_get_links_initiated_and_provider_lists(self):
        self.assertTrue(self.w1._link(self.c2))
        initiated = self.w1._get_initiated_conduits()
        provider = self.w1._get_provider_conduits()
        self.assertEqual([c._name for c in initiated], ["C2"])
        self.assertEqual(provider, [])
        self.assertEqual([c._name for c in self.w2._get_provider_conduits()], ["C1"])
        all_links = self.w1._get_links()
        self.assertEqual([c._name for c in all_links], ["C2"])

    def test_get_contracted_conduits_and_describe_contract(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        lst = self.w2._get_contracted_conduits()   # grantee’s ward has the inbound details
        self.assertEqual(len(lst), 1)
        peer_id, peer = lst[0]
        self.assertEqual(peer._name, "C1")

        desc = self.w2._describe_contract(peer_id)
        self.assertEqual(desc["peer_conduit_name"], "C1")
        self.assertEqual(desc["spell_count"], 1)
        self.assertEqual(desc["spells"][0]["spell_id"], "SID1")

    def test_validate_contracts_and_received(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        # from grantee POV, initial validation OK
        self.assertTrue(self.w2._validate_received_contracts())
        # Invalidate by removing from *provider* contracted map (matches current prod placement)
        self.c1._contracted_spells.pop("SID1", None)
        results = self.w2._validate_contracts_and_define()
        self.assertEqual(list(results.values()), [False])

    # -----------------------------
    # +20 Additional edge/negative tests
    # -----------------------------

    def test_find_contract_id_returns_none_when_no_link(self):
        self.assertIsNone(self.w1._find_contract_id(self.c2))

    def test_find_contract_by_id_returns_none_when_unknown(self):
        unknown_id = uuid4()
        self.assertIsNone(self.w1._find_contract_by_id(unknown_id))

    def test_link_to_self_raises(self):
        with self.assertRaises(RuntimeError):
            self.w1._link(self.c1)

    def test_link_to_lesser_raises(self):
        lesser = FakeConduit(name="L", state=ConduitState.lesser)
        lesser._conduit_ward = ConduitWard(lesser, dynamic=True, conduit_type=ConduitState.lesser, policy=Policies.lesser_conduit)
        with self.assertRaises(RuntimeError):
            self.w1._link(lesser)

    def test_sever_link_raises_when_no_contract(self):
        with self.assertRaises(RuntimeError):
            self.w1._sever_link(self.c2)

    def test_add_spell_duplicate_same_permissions_raises(self):
        self.w1._link(self.c2)
        self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2, permissions="create")
        with self.assertRaises(RuntimeError):
            self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2, permissions="create")

    def test_add_spell_permissions_case_insensitive(self):
        self.w1._link(self.c2)
        spx = FakeSpell("SIDX", owner_id=self.c2._id, perm=Permissions.create)
        self.c2._owned_spells[spx.spell_id] = spx
        ok = self.w1._add_spell_to_contract(spell=spx, conduit=self.c2, permissions="CrEaTe")
        self.assertTrue(ok)
        # provider holds contracted entry in current prod
        self.assertIsNotNone(self.c1.find_contracted_spell("SIDX"))

        # clean up and ensure removal works too
        self.w1._remove_spell_from_contract(spell=spx, conduit=self.c2)
        self.assertIsNone(self.c1.find_contracted_spell("SIDX"))

    def test_add_spells_bulk_all_fail(self):
        self.w1._link(self.c2)
        report = self.w1._add_spells_to_contract(spell_ids=["NOPE1", "NOPE2"], conduit=self.c2, permissions="create")
        self.assertEqual(report["success"], [])
        self.assertEqual(set(report["failed"].keys()), {"NOPE1", "NOPE2"})

    def test_remove_spell_from_contract_raises_when_missing(self):
        self.w1._link(self.c2)
        with self.assertRaises(RuntimeError):
            self.w1._remove_spell_from_contract(spell_id="MIA", conduit=self.c2)

    def test_remove_all_spells_raises_when_no_contract(self):
        with self.assertRaises(RuntimeError):
            self.w1._remove_all_spells_from_contract(conduit=self.c2)

    def test_get_spells_in_contract_by_conduit_unknown_returns_none(self):
        self.assertIsNone(self.w2._get_spells_in_contract_by_conduit(uuid4()))

    def test_get_spells_in_contract_by_conduit_name_invalid_arg_raises(self):
        with self.assertRaises(ValueError):
            self.w2._get_spells_in_contract_by_conduit_name("")

    def test_describe_contract_unknown_raises(self):
        with self.assertRaises(RuntimeError):
            self.w2._describe_contract(uuid4())

    def test_validate_received_contracts_false_when_no_contracts(self):
        self.assertFalse(self.w2._validate_received_contracts())

    def test_set_initial_policy_type_error(self):
        with self.assertRaises(TypeError):
            ConduitWard(self.c1, dynamic=True, conduit_type=ConduitState.normal, policy="not-an-enum")

    def test_set_new_policy_bad_string_raises(self):
        with self.assertRaises(ValueError):
            self.w1._set_new_policy("no_such_policy")

    def test_set_new_policy_lesser_conduit_on_normal_raises(self):
        with self.assertRaises(RuntimeError):
            self.w1._set_new_policy(Policies.lesser_conduit)

    def test_set_new_policy_whitelist_ok_when_no_contracts(self):
        self.w1._set_new_policy(Policies.whitelist_all)
        self.assertEqual(self.w1._policy, Policies.whitelist_all)

    def test_helpers_type_errors(self):
        with self.assertRaises(TypeError):
            self.w1._find_contract("not-a-conduit")  # type: ignore
        with self.assertRaises(TypeError):
            self.w1._find_contract_id("not-a-conduit")  # type: ignore

    def test_sealed_blocks_mutations_and_queries_where_applicable(self):
        self.w1._sealed = True
        with self.assertRaises(RuntimeError): self.w1._link(self.c2)
        with self.assertRaises(RuntimeError): self.w1._find_contract_id(self.c2)
        with self.assertRaises(RuntimeError): self.w1._add_spell_to_contract(spell=self.sp1, conduit=self.c2)
        with self.assertRaises(RuntimeError): self.w1._remove_spell_from_contract(spell_id="SID1", conduit=self.c2)
        with self.assertRaises(RuntimeError): self.w1._remove_all_spells_from_contract(conduit=self.c2)
        with self.assertRaises(RuntimeError): self.w1._get_all_spells_in_contracts()
        with self.assertRaises(RuntimeError): self.w1._get_spells_in_contract_by_conduit(self.c2._id)

    def test_check_helpers_resolution_errors(self):
        with self.assertRaises(RuntimeError):
            self.w1._check_spell_id_and_spell(spell_id="NOPE")
        with self.assertRaises(RuntimeError):
            self.w1._check_conduit_id_and_conduit(conduit_id=uuid4())


if __name__ == "__main__":
    unittest.main()
