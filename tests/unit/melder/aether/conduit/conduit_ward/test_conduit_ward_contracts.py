import threading

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.interfaces.interfaces import IConduit, ISpell


class ProtocolStub:
    """Callable placeholder that fails fast if a missing protocol member is used."""

    def __init__(self, name: str) -> None:
        """Store the protocol member name for error reporting."""
        self._name = name

    def __call__(self, *args, **kwargs):
        """Raise an assertion to highlight unexpected protocol usage in tests."""
        raise AssertionError(f"Unexpected protocol call: {self._name}")


def _attach_protocol_stubs(target_cls: type, protocol_cls: type) -> None:
    """Attach placeholder attributes required for runtime Protocol checks."""
    for name in protocol_cls.__protocol_attrs__:
        if name in target_cls.__dict__:
            continue
        setattr(target_cls, name, ProtocolStub(name))


class FakeLogger:
    """Minimal logger that accepts ConduitWard logging calls."""

    def __init__(self) -> None:
        """Initialize storage for debug/info/error messages."""
        self.messages: list[tuple[str, str]] = []

    def debug(self, message: str, method_name: str | None = None, **kwargs) -> None:
        """Record a debug message for optional inspection."""
        self.messages.append(("debug", message))

    def info(self, message: str, method_name: str | None = None, **kwargs) -> None:
        """Record an info message for optional inspection."""
        self.messages.append(("info", message))

    def error(self, message: str, method_name: str | None = None, **kwargs) -> None:
        """Record an error message for optional inspection."""
        self.messages.append(("error", message))


class FakeSpell:
    """Lightweight spell representation with lineage and permissions."""

    def __init__(
        self,
        spell_id: str,
        owner_id: str,
        *,
        permissions: Permissions = Permissions.create,
        spell_name: str = "FakeSpell",
        dependencies: list[str] | None = None,
    ) -> None:
        """Create a spell with a SpellIndex lineage and ownership metadata."""
        self._cleaned = False
        self._lock = threading.RLock()
        self._id = f"spell-{spell_id}"
        self.spell_id = spell_id
        self.spell_index = SpellIndex(spell_id)
        self.permissions = permissions
        self._permissions = permissions
        self.spellframe = "frame"
        self.binding_name = "default"
        self.spell_name = spell_name
        self.__name__ = spell_name
        self._owner_conduit_id = owner_id
        self._owner_conduit_name = None
        self.owned_spell = True
        self.dependencies = dependencies or []
        self.dependency_graph = None
        self._spellbook = None
        self.aetheric_frame = "default"

    @property
    def cleaned(self) -> bool:
        """Return True if cleanup has been invoked."""
        return self._cleaned

    @property
    def is_cleaned(self) -> bool:
        """Alias for cleaned used by Protocol checks."""
        return self._cleaned

    def check_cleaned(self) -> None:
        """Raise if this spell has been cleaned."""
        if self._cleaned:
            raise RuntimeError("Spell is cleaned.")

    def cleanup(self) -> None:
        """Mark the spell as cleaned for test teardown."""
        self._cleaned = True

    async def async_cleanup(self) -> None:
        """Async cleanup wrapper used by the Cleanable protocol."""
        self.cleanup()

    def add_version(self, version_id: str) -> None:
        """Advance the lineage to a new version for tests."""
        self.spell_index.update(version_id)
        self.spell_id = version_id


_attach_protocol_stubs(FakeSpell, ISpell)


class FakeSpellbook:
    """Minimal spellbook that tracks contracted and local spells."""

    def __init__(self) -> None:
        """Initialize storage and call tracking for contract operations."""
        self._lock = threading.RLock()
        self._spells: dict[SpellIndex, FakeSpell] = {}
        self._contracted_spells: dict[str, dict[SpellIndex, FakeSpell]] = {}
        self._lookup_contracted_spells: dict[str, dict[tuple[str, str, str], SpellIndex]] = {}
        self._contracted_versions: dict[str, set[str]] = {}
        self._create_link_calls: list[str] = []
        self._add_contracted_calls: list[tuple[str, str]] = []
        self._remove_contracted_calls: list[tuple[str, str]] = []
        self._clear_contracted_calls: list[str] = []
        self._sever_link_calls: list[str] = []

    def add_local_spell(self, spell: FakeSpell) -> None:
        """Register a locally owned spell for lineage checks."""
        self._spells[spell.spell_index] = spell

    def _create_link_contract(self, conduit_id: str) -> None:
        """Create contracted spell buckets for a peer conduit."""
        self._create_link_calls.append(conduit_id)
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells
        c_exists = conduit_id in self._contracted_versions
        if not (a_exists == b_exists == c_exists):
            raise RuntimeError("Inconsistent link contract state.")
        if not a_exists:
            self._contracted_spells[conduit_id] = {}
            self._lookup_contracted_spells[conduit_id] = {}
            self._contracted_versions[conduit_id] = set()

    def _add_contracted_spell(self, spell: FakeSpell, conduit_id: str) -> None:
        """Record a contracted spell under a peer conduit id."""
        self._add_contracted_calls.append((conduit_id, spell.spell_id))
        if conduit_id not in self._contracted_spells:
            self._create_link_contract(conduit_id)
        spell_map = self._contracted_spells[conduit_id]
        lookup_map = self._lookup_contracted_spells[conduit_id]
        versions_set = self._contracted_versions[conduit_id]
        spell_map[spell.spell_index] = spell
        lookup_map[(spell.spellframe, spell.spell_name, spell.binding_name)] = spell.spell_index
        versions = spell.spell_index._versions
        if versions:
            for version_id in versions:
                versions_set.add(version_id)

    def _find_contracted_spell(self, spell_index: SpellIndex) -> FakeSpell:
        """Locate a contracted spell by SpellIndex across all peers."""
        for spell_map in self._contracted_spells.values():
            if spell_index in spell_map:
                return spell_map[spell_index]
        raise RuntimeError("Contracted spell not found.")

    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> FakeSpell | None:
        """Locate a contracted spell by version id within a peer conduit."""
        spell_map = self._contracted_spells.get(conduit_id)
        if spell_map is None:
            return None
        for spell_index, spell in spell_map.items():
            versions = spell_index._versions
            if versions and spell_id in versions:
                return spell
        return None

    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """Remove a contracted spell by version id for a peer conduit."""
        self._remove_contracted_calls.append((conduit_id, spell_id))
        spell_map = self._contracted_spells.get(conduit_id)
        lookup_map = self._lookup_contracted_spells.get(conduit_id)
        versions_set = self._contracted_versions.get(conduit_id)
        if spell_map is None or lookup_map is None or versions_set is None:
            raise RuntimeError("No contracted spell maps found.")
        spell_index = None
        spell = None
        for idx, candidate in spell_map.items():
            versions = idx._versions
            if versions and spell_id in versions:
                spell_index = idx
                spell = candidate
                break
        if spell_index is None or spell is None:
            raise RuntimeError("Spell version not found.")
        spell_map.pop(spell_index, None)
        lookup_map.pop((spell.spellframe, spell.spell_name, spell.binding_name), None)
        versions = spell_index._versions
        if versions:
            for version_id in versions:
                versions_set.discard(version_id)

    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """Clear contracted spells for a peer while keeping buckets."""
        self._clear_contracted_calls.append(conduit_id)
        if (
            conduit_id not in self._contracted_spells
            or conduit_id not in self._lookup_contracted_spells
            or conduit_id not in self._contracted_versions
        ):
            raise RuntimeError("No contracted spell maps found.")
        self._contracted_spells[conduit_id].clear()
        self._lookup_contracted_spells[conduit_id].clear()
        self._contracted_versions[conduit_id].clear()

    def _sever_link_contract(self, conduit_id: str) -> None:
        """Remove contracted spell buckets and all contained spells."""
        self._sever_link_calls.append(conduit_id)
        self._clear_contracted_spells_for_conduit(conduit_id)
        self._contracted_spells.pop(conduit_id, None)
        self._lookup_contracted_spells.pop(conduit_id, None)
        self._contracted_versions.pop(conduit_id, None)


class FakeConduit:
    """Minimal Conduit implementation used for ConduitWard contract tests."""

    def __init__(
        self,
        conduit_id: str,
        *,
        name: str | None = None,
        policy: Policies = Policies.default,
        dynamic: bool = True,
    ) -> None:
        """Create a conduit with a ward and a fake spellbook."""
        self._lock = threading.RLock()
        self._id = conduit_id
        self._name = name
        self.__debugger_mode__ = False
        self.__dynamic_environment__ = dynamic
        self._aetheric_frame = "default"
        self._configuration = None
        self._logger = FakeLogger()
        self._spellbook = FakeSpellbook()
        self._conduit_state = ConduitState.normal
        self._creations = None
        self._meld = None
        self._cleaned = False
        self._known_conduits: dict[str, "FakeConduit"] = {}
        self._spell_by_id: dict[str, FakeSpell] = {}
        self._spell_owners: dict[str, "FakeConduit"] = {}
        self._conduit_ward = ConduitWard(self, dynamic, self._conduit_state, policy)

    @property
    def cleaned(self) -> bool:
        """Return True if this conduit has been cleaned."""
        return self._cleaned

    @property
    def is_cleaned(self) -> bool:
        """Alias for cleaned used by Protocol checks."""
        return self._cleaned

    def check_cleaned(self) -> None:
        """Raise if the conduit has been cleaned."""
        if self._cleaned:
            raise RuntimeError("Conduit is cleaned.")

    def cleanup(self) -> None:
        """Mark the conduit as cleaned for test teardown."""
        self._cleaned = True

    async def async_cleanup(self) -> None:
        """Async cleanup wrapper used by the Cleanable protocol."""
        self.cleanup()

    def __enter__(self) -> "FakeConduit":
        """Enter a context manager for the conduit."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the conduit context manager."""
        return None

    def __repr__(self) -> str:
        """Return a readable identifier for debug output."""
        return f"<FakeConduit id={self._id}>"

    @property
    def id(self) -> str:
        """Expose the conduit id as a property."""
        return self._id

    @property
    def name(self) -> str | None:
        """Expose the conduit name as a property."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Set the conduit name once for tests."""
        if self._name is not None:
            raise RuntimeError("Conduit name already set.")
        self._name = name

    def register_conduit(self, conduit: "FakeConduit") -> None:
        """Register a peer conduit for lookup helpers."""
        self._known_conduits[conduit._id] = conduit

    def register_spell(self, spell: FakeSpell) -> None:
        """Register a locally owned spell for lookup and ownership checks."""
        spell._owner_conduit_id = self._id
        self._spell_by_id[spell.spell_id] = spell
        self._spellbook.add_local_spell(spell)
        self._spell_owners[spell.spell_id] = self

    def get_conduit_by_id(self, conduit_id: str, aetheric_frame: str = "default") -> "FakeConduit" | None:
        """Return a known conduit by id if registered."""
        return self._known_conduits.get(conduit_id)

    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame: str = "default") -> "FakeConduit" | None:
        """Return the known owner conduit for a spell id."""
        return self._spell_owners.get(spell_id)

    def get_spell_by_id(self, spell_id: str, aetheric_frame: str = "default") -> FakeSpell | None:
        """Resolve a spell id from local or known conduits."""
        if spell_id in self._spell_by_id:
            return self._spell_by_id[spell_id]
        for conduit in self._known_conduits.values():
            if spell_id in conduit._spell_by_id:
                return conduit._spell_by_id[spell_id]
        return None

    def inspect_spell(self, spell: FakeSpell, aetheric_frame: str = "default") -> str | None:
        """Return the spell id for a spell instance."""
        if spell is None:
            return None
        return spell.spell_id

    def find_contracted_spell(self, spell_id: str) -> FakeSpell | None:
        """Find a contracted spell by version id across all peers."""
        for conduit_id in self._spellbook._contracted_spells.keys():
            spell = self._spellbook._find_contracted_spell_by_id(spell_id, conduit_id)
            if spell is not None:
                return spell
        return None


_attach_protocol_stubs(FakeConduit, IConduit)


def _build_conduit_pair(
    *,
    owner_policy: Policies = Policies.default,
    borrower_policy: Policies = Policies.default,
    dynamic: bool = True,
) -> tuple[FakeConduit, FakeConduit]:
    """Create two conduits and register them for lookup helpers."""
    owner = FakeConduit("owner", name="Owner", policy=owner_policy, dynamic=dynamic)
    borrower = FakeConduit("borrower", name="Borrower", policy=borrower_policy, dynamic=dynamic)
    owner.register_conduit(borrower)
    borrower.register_conduit(owner)
    return owner, borrower


def _link_contract(initiator: FakeConduit, target: FakeConduit):
    """Create a contract from initiator to target and return the contract."""
    initiator._conduit_ward._create_new_contract(target)
    return initiator._conduit_ward._find_contract(target)


def _register_spell(
    conduit: FakeConduit,
    spell_id: str,
    *,
    permissions: Permissions = Permissions.create,
    spell_name: str = "Spell",
    dependencies: list[str] | None = None,
) -> FakeSpell:
    """Create and register a spell owned by the given conduit."""
    spell = FakeSpell(
        spell_id,
        conduit._id,
        permissions=permissions,
        spell_name=spell_name,
        dependencies=dependencies,
    )
    conduit.register_spell(spell)
    return spell


@pytest.fixture
def conduit_pair() -> tuple[FakeConduit, FakeConduit]:
    """Provide two conduits with default policy and dynamic mode."""
    return _build_conduit_pair()


@pytest.fixture
def linked_pair(conduit_pair: tuple[FakeConduit, FakeConduit]) -> tuple[FakeConduit, FakeConduit]:
    """Provide two conduits with an active contract."""
    owner, borrower = conduit_pair
    _link_contract(borrower, owner)
    return owner, borrower


def test_create_new_contract_wires_indices_and_spellbooks(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify contract creation wires indices and spellbook buckets. The contract should be shared by both wards."""
    owner, borrower = conduit_pair
    result = borrower._conduit_ward._create_new_contract(owner)

    assert result is True
    assert len(borrower._conduit_ward._contracts) == 1

    contract_id = next(iter(borrower._conduit_ward._contracts))
    assert contract_id in owner._conduit_ward._contracts
    assert borrower._conduit_ward._initiated_index[owner._id] == contract_id
    assert owner._conduit_ward._received_index[borrower._id] == contract_id
    assert borrower._spellbook._contracted_spells[owner._id] == {}
    assert owner._spellbook._contracted_spells[borrower._id] == {}
    assert borrower._spellbook._create_link_calls == [owner._id]
    assert owner._spellbook._create_link_calls == [borrower._id]


def test_create_new_contract_is_idempotent(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify contract creation does not duplicate existing links. A second call should not mutate counts."""
    owner, borrower = conduit_pair
    borrower._conduit_ward._create_new_contract(owner)
    contract_ids = set(borrower._conduit_ward._contracts.keys())

    borrower._conduit_ward._create_new_contract(owner)

    assert set(borrower._conduit_ward._contracts.keys()) == contract_ids
    assert borrower._spellbook._create_link_calls == [owner._id]
    assert owner._spellbook._create_link_calls == [borrower._id]


def test_link_blocks_outbound_when_inbound_only() -> None:
    """Verify inbound_only policy blocks outbound link attempts. The ward should raise a policy error."""
    owner, borrower = _build_conduit_pair(
        owner_policy=Policies.default,
        borrower_policy=Policies.inbound_only,
    )

    with pytest.raises(RuntimeError, match="inbound_only"):
        borrower._conduit_ward._link(owner)


def test_link_rejects_target_outbound_only_policy() -> None:
    """Verify outbound_only policy blocks inbound link requests. The target should reject linking."""
    owner, borrower = _build_conduit_pair(
        owner_policy=Policies.outbound_only,
        borrower_policy=Policies.default,
    )

    with pytest.raises(RuntimeError, match="outbound_only"):
        borrower._conduit_ward._link(owner)


def test_add_spell_to_contract_adds_detail_and_contracted_spell(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify adding a spell creates a Detail and contracted spell entry. Sources and permissions should match."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-1", permissions=Permissions.create, spell_name="OwnerSpell")

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        reason=DetailReason.manual,
        root_spell_id="root-1",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail_map = contract._get_detail_map(owner._conduit_ward)
    detail = detail_map[spell.spell_id]

    assert detail.permissions == Permissions.create
    assert detail.contract_type == ContractTypes.received
    assert detail.reason == DetailReason.manual
    assert detail.sources == {"root-1"}
    assert spell.spell_index in borrower._spellbook._contracted_spells[owner._id]
    assert borrower._spellbook._add_contracted_calls == [(owner._id, spell.spell_id)]


def test_add_spell_to_contract_merges_sources_without_duplicate_spellbook_update(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify repeated adds merge sources and avoid duplicate spellbook updates. The detail should stay singular."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-2", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-a",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-b",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail = contract._get_detail_map(owner._conduit_ward)[spell.spell_id]

    assert detail.sources == {"root-a", "root-b"}
    assert borrower._spellbook._add_contracted_calls == [(owner._id, spell.spell_id)]
    assert len(borrower._spellbook._contracted_spells[owner._id]) == 1


def test_add_spell_to_contract_rejects_different_permissions(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify adding with different permissions fails. The ward should refuse to change permissions in place."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-3", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="read",
    )

    with pytest.raises(RuntimeError, match="different permissions"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="create",
        )


def test_add_spell_to_contract_rejects_not_owner(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify a spell owned by another conduit is rejected. Ownership must match the target conduit."""
    owner, borrower = linked_pair
    spell = FakeSpell("spell-4", owner_id="other-owner", permissions=Permissions.create)

    with pytest.raises(RuntimeError, match="not owned"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="create",
        )


def test_add_spell_to_contract_rejects_permission_escalation(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify requested permissions cannot exceed the spell's own permissions. Escalation should raise."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-5", permissions=Permissions.read)

    with pytest.raises(RuntimeError, match="create permissions"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="create",
        )


def test_add_spell_to_contract_rejects_blocked_spell_without_whitelist(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify blocked spells require whitelist policy. Non-whitelist peers should be rejected."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-6", permissions=Permissions.block)

    with pytest.raises(RuntimeError, match="block permissions"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="read",
        )


def test_remove_spell_from_contract_removes_detail_and_severs_contract_when_empty(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing the last detail severs the contract. Spellbook buckets should be removed for both sides."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-7", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    result = borrower._conduit_ward._remove_spell_from_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
    )

    assert result is True
    assert borrower._conduit_ward._contracts == {}
    assert owner._conduit_ward._contracts == {}
    assert owner._id not in borrower._spellbook._contracted_spells
    assert borrower._id not in owner._spellbook._contracted_spells
    assert borrower._spellbook._sever_link_calls == [owner._id]
    assert owner._spellbook._sever_link_calls == [borrower._id]


def test_remove_spell_from_contract_only_removes_source(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing a single root source preserves the detail. The contracted spell should remain."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-8", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-a",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-b",
    )

    borrower._conduit_ward._remove_spell_from_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        root_spell_id="root-a",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail = contract._get_detail_map(owner._conduit_ward)[spell.spell_id]

    assert detail.sources == {"root-b"}
    assert owner._id in borrower._spellbook._contracted_spells
    assert borrower._spellbook._remove_contracted_calls == []


def test_remove_spell_from_contract_raises_when_missing_spell(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing a missing spell raises a contract error. The ward should not silently succeed."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-9", permissions=Permissions.create)

    with pytest.raises(RuntimeError, match="does not exist"):
        borrower._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
        )


def test_remove_all_spells_from_contract_clears_details_and_contracted_spells(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify bulk removal clears both detail maps and contracted spells. The contract itself should remain."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-10", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    result = borrower._conduit_ward._remove_all_spells_from_contract(conduit=owner)

    contract = borrower._conduit_ward._find_contract(owner)
    assert result is True
    assert contract._get_detail_map(owner._conduit_ward) == {}
    assert contract._get_detail_map(borrower._conduit_ward) == {}
    assert borrower._spellbook._contracted_spells[owner._id] == {}
    assert owner._spellbook._contracted_spells[borrower._id] == {}


def test_get_spells_in_contract_by_conduit_reports_inbound_and_outbound(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify inbound and outbound spell lists are reported correctly. Each direction should resolve to real spells."""
    owner, borrower = linked_pair
    owner_spell = _register_spell(owner, "spell-11", permissions=Permissions.create)
    borrower_spell = _register_spell(borrower, "spell-12", permissions=Permissions.read)

    borrower._conduit_ward._add_spell_to_contract(
        spell=owner_spell,
        spell_id=owner_spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            borrower_spell,
            Permissions.read,
            ContractTypes.initiated,
            reason=DetailReason.manual,
        )
        contract._add(borrower._conduit_ward, detail)

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id)

    inbound_map = {sid: spell for sid, spell in result["inbound"]}
    outbound_map = {sid: spell for sid, spell in result["outbound"]}

    assert inbound_map[owner_spell.spell_id] is owner_spell
    assert outbound_map[borrower_spell.spell_id] is borrower_spell


def test_get_all_spells_in_contracts_returns_current_versions(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify contracted spell inspection returns current versions. The mapping should include the peer id."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-13", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    result = borrower._conduit_ward._get_all_spells_in_contracts()

    assert owner._id in result
    assert result[owner._id][0][0] == spell.spell_id
    assert result[owner._id][0][1] is spell


def test_get_spell_in_contracts_matches_lineage_versions(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spell lookup honors lineage history. A previous version id should resolve to the current spell."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-14", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    spell.add_version("spell-14b")

    result = borrower._conduit_ward._get_spell_in_contracts("spell-14")

    assert result[0] == owner._id
    assert result[1] is spell
    assert result[1].spell_id == "spell-14b"


def test_describe_contract_reports_peer_and_permissions(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify contract descriptions include peer name and spell permissions. The spell list should be accurate."""
    owner, borrower = linked_pair
    borrower_spell = _register_spell(borrower, "spell-15", permissions=Permissions.read)

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            borrower_spell,
            Permissions.read,
            ContractTypes.initiated,
            reason=DetailReason.manual,
        )
        contract._add(borrower._conduit_ward, detail)

    result = borrower._conduit_ward._describe_contract(owner._id)

    assert result["contract_id"] == contract._id
    assert result["peer_conduit_name"] == owner._name
    assert result["spell_count"] == 1
    assert result["spells"][0]["spell_id"] == borrower_spell.spell_id
    assert result["spells"][0]["permissions"] == Permissions.read.name


def test_validate_contracts_and_define_returns_true_for_consistent_contracts(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify contract validation succeeds when both sides have contracted spells. Each ward should validate True."""
    owner, borrower = linked_pair
    owner_spell = _register_spell(owner, "spell-16", permissions=Permissions.create)
    borrower_spell = _register_spell(borrower, "spell-17", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=owner_spell,
        spell_id=owner_spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    owner._conduit_ward._add_spell_to_contract(
        spell=borrower_spell,
        spell_id=borrower_spell.spell_id,
        conduit=borrower,
        permissions="create",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    results = borrower._conduit_ward._validate_contracts_and_define()

    assert results[contract._id] is True


def test_validate_received_contracts_returns_false_when_missing_contracted_spell(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify validation fails when a detail exists without a contracted spell. The aggregated result should be False."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-18", permissions=Permissions.create)

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            spell,
            Permissions.create,
            ContractTypes.received,
            reason=DetailReason.manual,
        )
        contract._add(owner._conduit_ward, detail)

    result = borrower._conduit_ward._validate_received_contracts()

    assert result is False
