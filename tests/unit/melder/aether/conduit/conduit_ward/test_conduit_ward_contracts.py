from __future__ import annotations

import threading
from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock, patch

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell import Spell
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.aether.conduit.conduit import Conduit


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
        binding_name: str | None = None,
        dependencies: list[str] | None = None,
    ) -> None:
        """
        Purpose:
            Create a spell with lineage, ownership metadata, and a binding name.
        Contract:
            - Initializes SpellIndex lineage with the provided spell_id.
            - Records owner conduit metadata for ownership checks.
            - Uses the provided binding_name or defaults to "default".
        Args:
            spell_id: Versioned spell id for lineage tracking.
            owner_id: Owning conduit id for ownership checks.
            permissions: Permissions assigned to the spell.
            spell_name: Friendly spell name for diagnostics.
            binding_name: Binding name for lookup key generation.
            dependencies: Optional dependency spell ids.
        Returns:
            None.
        """
        self._cleaned = False
        self._lock = threading.RLock()
        self._id = f"spell-{spell_id}"
        self.spell_id = spell_id
        self.spell_index = SpellIndex(spell_id)
        self._active = True
        self.permissions = permissions
        self._permissions = permissions
        self.spellframe = "frame"
        self.binding_name = "default" if binding_name is None else binding_name
        self.spell_name = spell_name
        self.__name__ = spell_name
        self._owner_conduit_id = owner_id
        self._owner_conduit_name = None
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



class FakeSpellbook:
    """Minimal spellbook that tracks contracted and local spells."""

    def __init__(self) -> None:
        """Initialize storage and call tracking for contract operations."""
        self._lock = threading.RLock()
        self._spells: dict[SpellIndex, FakeSpell] = {}
        self._contracted_spells: dict[str, dict[SpellIndex, FakeSpell]] = {}
        self._lookup_spells: dict[tuple[str, str], SpellIndex] = {}
        self._lookup_contracted_spells: dict[str, dict[tuple[str, str], SpellIndex]] = {}
        self._contracted_spell_ids: dict[str, set[str]] = {}
        self._create_link_calls: list[str] = []
        self._add_contracted_calls: list[tuple[str, str]] = []
        self._remove_contracted_calls: list[tuple[str, str]] = []
        self._clear_contracted_calls: list[str] = []
        self._sever_link_calls: list[str] = []

    def add_local_spell(self, spell: FakeSpell) -> None:
        """Register a locally owned spell for lineage checks."""
        self._spells[spell.spell_index] = spell
        lookup_key = self._make_spell_key(
            spell.spellframe,
            spell.spell_name,
            spell.binding_name,
        )
        self._lookup_spells[lookup_key] = spell.spell_index

    def _make_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> tuple[str, str]:
        """
        Create a normalized lookup key for spells in this fake spellbook.

        Args:
            spellframe: Spellframe identifier to normalize.
            spell_name: Spell name used for frame fallback.
            binding_name: Binding name to normalize.

        Returns:
            tuple[str, str]: Normalized (frame_key, binding_key) pair.
        """
        frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
        )
        return frame_key, bind_key

    def _assert_lookup_key_available(
        self,
        *,
        lookup_key: tuple[str, str],
        spell_index: SpellIndex,
        context: str,
        check_local: bool = True,
        check_contracted: bool = True,
    ) -> None:
        """
        Validate lookup key uniqueness for local/contracted spell maps.

        Args:
            lookup_key: Normalized (frame_key, binding_key) tuple.
            spell_index: SpellIndex associated with the incoming spell.
            context: Caller context for error reporting.
            check_local: When True, enforce uniqueness against local entries.
            check_contracted: When True, enforce uniqueness against contracted entries.

        Raises:
            RuntimeError: If the lookup key collides with another spell.
        """
        if check_local:
            existing_local = self._lookup_spells.get(lookup_key)
            if existing_local is not None and existing_local is not spell_index:
                frame_key, bind_key = lookup_key
                raise RuntimeError(
                    "Spell binding key collision detected in local registry. "
                    f"frame_key='{frame_key}', binding_name='{bind_key}'. "
                    "Use a distinct spellframe or binding_name to disambiguate."
                )

        if check_contracted:
            for conduit_id, lookup_map in self._lookup_contracted_spells.items():
                existing_contracted = lookup_map.get(lookup_key)
                if existing_contracted is None or existing_contracted is spell_index:
                    continue
                frame_key, bind_key = lookup_key
                raise RuntimeError(
                    "Spell binding key collision detected in contracted registry. "
                    f"frame_key='{frame_key}', binding_name='{bind_key}', "
                    f"conduit_id='{conduit_id}'. Use a distinct spellframe or binding_name "
                    "to disambiguate."
                )

    def _create_link_contract(self, conduit_id: str) -> None:
        """Create contracted spell buckets for a peer conduit."""
        self._create_link_calls.append(conduit_id)
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells
        c_exists = conduit_id in self._contracted_spell_ids
        if not (a_exists == b_exists == c_exists):
            raise RuntimeError("Inconsistent link contract state.")
        if not a_exists:
            self._contracted_spells[conduit_id] = {}
            self._lookup_contracted_spells[conduit_id] = {}
            self._contracted_spell_ids[conduit_id] = set()

    def _add_contracted_spell(self, spell: FakeSpell, conduit_id: str) -> None:
        """Record a contracted spell under a peer conduit id."""
        self._add_contracted_calls.append((conduit_id, spell.spell_id))
        if conduit_id not in self._contracted_spells:
            self._create_link_contract(conduit_id)
        spell_map = self._contracted_spells[conduit_id]
        lookup_map = self._lookup_contracted_spells[conduit_id]
        versions_set = self._contracted_spell_ids[conduit_id]
        spell_map[spell.spell_index] = spell
        lookup_key = self._make_spell_key(
            spell.spellframe,
            spell.spell_name,
            spell.binding_name,
        )
        lookup_map[lookup_key] = spell.spell_index
        versions = spell.spell_index._spells_in_index
        if versions:
            for version_id in versions:
                versions_set.add(version_id)

    def _find_contracted_spell(self, spell_index: SpellIndex | str) -> FakeSpell:
        """Locate a contracted spell by SpellIndex or version id across all peers."""
        for spell_map in self._contracted_spells.values():
            if isinstance(spell_index, SpellIndex):
                if spell_index in spell_map:
                    return spell_map[spell_index]
            else:
                for idx, spell in spell_map.items():
                    versions = idx._spells_in_index
                    if versions and spell_index in versions:
                        return spell
        raise RuntimeError("Contracted spell not found.")

    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> FakeSpell | None:
        """Locate a contracted spell by version id within a peer conduit."""
        spell_map = self._contracted_spells.get(conduit_id)
        if spell_map is None:
            return None
        for spell_index, spell in spell_map.items():
            versions = spell_index._spells_in_index
            if versions and spell_id in versions:
                return spell
        return None

    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """Remove a contracted spell by version id for a peer conduit."""
        self._remove_contracted_calls.append((conduit_id, spell_id))
        spell_map = self._contracted_spells.get(conduit_id)
        lookup_map = self._lookup_contracted_spells.get(conduit_id)
        versions_set = self._contracted_spell_ids.get(conduit_id)
        if spell_map is None or lookup_map is None or versions_set is None:
            raise RuntimeError("No contracted spell maps found.")
        spell_index = None
        spell = None
        for idx, candidate in spell_map.items():
            versions = idx._spells_in_index
            if versions and spell_id in versions:
                spell_index = idx
                spell = candidate
                break
        if spell_index is None or spell is None:
            raise RuntimeError("Spell version not found.")
        spell_map.pop(spell_index, None)
        lookup_key = self._make_spell_key(
            spell.spellframe,
            spell.spell_name,
            spell.binding_name,
        )
        lookup_map.pop(lookup_key, None)
        versions = spell_index._spells_in_index
        if versions:
            for version_id in versions:
                versions_set.discard(version_id)

    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """Clear contracted spells for a peer while keeping buckets."""
        self._clear_contracted_calls.append(conduit_id)
        if (
            conduit_id not in self._contracted_spells
            or conduit_id not in self._lookup_contracted_spells
            or conduit_id not in self._contracted_spell_ids
        ):
            raise RuntimeError("No contracted spell maps found.")
        self._contracted_spells[conduit_id].clear()
        self._lookup_contracted_spells[conduit_id].clear()
        self._contracted_spell_ids[conduit_id].clear()

    def _sever_link_contract(self, conduit_id: str) -> None:
        """Remove contracted spell buckets and all contained spells."""
        self._sever_link_calls.append(conduit_id)
        self._clear_contracted_spells_for_conduit(conduit_id)
        self._contracted_spells.pop(conduit_id, None)
        self._lookup_contracted_spells.pop(conduit_id, None)
        self._contracted_spell_ids.pop(conduit_id, None)


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
        # Real conduits pull a non-owning crystallizer at init; the ward's
        # contract-record seams read `.activated` through it. "Present but
        # not recording" makes every record seam skip.
        self._crystallizer = SimpleNamespace(cleaned=False, activated=False)
        self._name = name
        self.__debugger_mode__ = False
        self.__dynamic_environment__ = dynamic
        self._aetheric_frame_name = "default"
        self._configuration = None
        self._logger = FakeLogger()
        self._spellbook = FakeSpellbook()
        self._devops_information_registry = DevopsInformationRegistry("default")
        self._ward_frame = SimpleNamespace(
            _conduit_cloud=SimpleNamespace(
                get_conduit_by_id=lambda conduit_id: self._known_conduits.get(
                    conduit_id
                )
            ),
            devops_information_registry=self._devops_information_registry,
        )
        self._conduit_state = ConduitState.normal
        self._creations = None
        self._meld = None
        self._cleaned = False
        self._known_conduits: dict[str, "FakeConduit"] = {}
        self._spell_by_id: dict[str, FakeSpell] = {}
        self._spell_owners: dict[str, "FakeConduit"] = {}
        self._transaction_identity = DevopsIdentity(
            owner_kind="conduit",
            owner_id=self._id,
            aetheric_frame_name=self._aetheric_frame_name,
            metadata={},
            available_transactions=("link", "transfer_ownership"),
        )
        self._transaction_identity.attach_registry(
            self._devops_information_registry,
            object_ref=self,
        )
        self._conduit_ward = ConduitWard(
            self,
            dynamic,
            self._conduit_state,
            policy,
            self._ward_frame,
        )

    def _emit_conduit_twin(self) -> None:
        """
        No-op record emitter for the ward's link/sever seams.

        Real conduits re-emit their twin when link topology changes; these
        tests run without a recording crystallizer, so the seam call is
        absorbed silently (matching the real helper, which gates itself
        off in a never-activated world).
        """
        return None

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
        try:
            self._conduit_ward.cleanup()
        except Exception:
            pass
        try:
            self._transaction_identity.cleanup()
        except Exception:
            pass
        try:
            self._devops_information_registry.cleanup()
        except Exception:
            pass
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

    def register_spell_owner(self, spell_id: str, owner: "FakeConduit") -> None:
        """Register the owning conduit for a spell id."""
        self._spell_owners[spell_id] = owner

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
    binding_name: str | None = None,
    dependencies: list[str] | None = None,
) -> FakeSpell:
    """
    Purpose:
        Create and register a spell owned by the given conduit.
    Contract:
        - Creates a FakeSpell with a unique binding_name when one is not provided.
        - Registers the spell on the conduit and its fake spellbook.
    Args:
        conduit: Conduit that will own the spell.
        spell_id: Versioned spell id for lineage tracking.
        permissions: Permissions assigned to the spell.
        spell_name: Friendly spell name for diagnostics.
        binding_name: Optional binding name override.
        dependencies: Optional dependency spell ids.
    Returns:
        FakeSpell: The registered spell instance.
    """
    resolved_binding = f"binding-{spell_id}" if binding_name is None else binding_name
    spell = FakeSpell(
        spell_id,
        conduit._id,
        permissions=permissions,
        spell_name=spell_name,
        binding_name=resolved_binding,
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


def test_add_spell_to_contract_rolls_back_detail_when_spellbook_add_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spellbook add failures do not leave a partial contract detail behind."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-add-fail", permissions=Permissions.create)
    borrower._spellbook._add_contracted_spell = MagicMock(side_effect=RuntimeError("add boom"))

    with pytest.raises(RuntimeError, match="add boom"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="create",
        )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract is not None
    assert contract._get_detail_map(owner._conduit_ward) == {}
    assert owner._id in borrower._spellbook._contracted_spells
    assert borrower._spellbook._contracted_spells[owner._id] == {}


def test_add_spell_to_contract_logs_when_spellbook_add_rollback_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spellbook-add rollback failures are logged while the original add error still propagates."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-add-rollback-log", permissions=Permissions.create)
    borrower._spellbook._add_contracted_spell = MagicMock(side_effect=RuntimeError("add boom"))
    contract = borrower._conduit_ward._find_contract(owner)

    with patch.object(Contract, "_remove_source", side_effect=RuntimeError("rollback boom")):
        with pytest.raises(RuntimeError, match="add boom"):
            borrower._conduit_ward._add_spell_to_contract(
                spell=spell,
                spell_id=spell.spell_id,
                conduit=owner,
                permissions="create",
            )

    assert any(
        level == "error" and "rollback failed after spellbook add error" in message
        for level, message in borrower._logger.messages
    )


def test_add_spell_to_contract_rolls_back_root_when_dependency_linking_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependency-link failures remove the just-added root contract detail instead of leaving partial state."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-dep-fail", permissions=Permissions.create)

    with pytest.raises(RuntimeError, match="dep boom"):
        with patch.object(
            ConduitWard,
            "_link_spell_dependencies",
            side_effect=RuntimeError("dep boom"),
        ):
            borrower._conduit_ward._add_spell_to_contract(
                spell=spell,
                spell_id=spell.spell_id,
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract is None
    assert owner._id not in borrower._spellbook._contracted_spells


def test_add_spell_to_contract_logs_when_dependency_link_rollback_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependency-link rollback failures are logged while the original dependency error still propagates."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-dep-rollback-log", permissions=Permissions.create)

    with patch.object(
        ConduitWard,
        "_link_spell_dependencies",
        side_effect=RuntimeError("dep boom"),
    ), patch.object(
        ConduitWard,
        "_remove_root_from_contracts",
        side_effect=RuntimeError("rollback boom"),
    ):
        with pytest.raises(RuntimeError, match="dep boom"):
            borrower._conduit_ward._add_spell_to_contract(
                spell=spell,
                spell_id=spell.spell_id,
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

    assert any(
        level == "error" and "rollback failed after dependency link error" in message
        for level, message in borrower._logger.messages
    )


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
            permissions="block",
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


def test_remove_spell_from_contract_restores_detail_when_spellbook_remove_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spellbook remove failures restore the deleted detail instead of leaving divergence."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-remove-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._remove_contracted_spell = MagicMock(side_effect=RuntimeError("remove boom"))

    with pytest.raises(RuntimeError, match="remove boom"):
        borrower._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
        )

    contract = borrower._conduit_ward._find_contract(owner)
    assert spell.spell_id in contract._get_detail_map(owner._conduit_ward)
    assert spell.spell_index in borrower._spellbook._contracted_spells[owner._id]


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


def test_remove_all_spells_from_contract_preserves_details_when_spellbook_clear_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spellbook clear failures do not clear contract details first."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-clear-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._clear_contracted_spells_for_conduit = MagicMock(side_effect=RuntimeError("clear boom"))

    with pytest.raises(RuntimeError, match="clear boom"):
        borrower._conduit_ward._remove_all_spells_from_contract(conduit=owner)

    contract = borrower._conduit_ward._find_contract(owner)
    assert spell.spell_id in contract._get_detail_map(owner._conduit_ward)
    assert spell.spell_index in borrower._spellbook._contracted_spells[owner._id]


def test_remove_spell_from_contract_swallows_invalidate_contract_consumers_error(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify invalidate-consumer failures are swallowed after successful spell removal."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-invalidate-remove", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    with patch.object(
        ConduitWard,
        "_invalidate_contract_consumers",
        side_effect=RuntimeError("invalidate boom"),
    ):
        result = borrower._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
        )

    assert result is True
    assert borrower._conduit_ward._find_contract(owner) is None


def test_remove_spell_from_contract_raises_when_contract_cleanup_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removal logs and re-raises when final contract cleanup fails after the spell is removed."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-cleanup-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    with patch.object(
        ConduitWard,
        "_remove_contract",
        side_effect=RuntimeError("cleanup boom"),
    ):
        with pytest.raises(RuntimeError, match="cleanup boom"):
            borrower._conduit_ward._remove_spell_from_contract(
                spell=spell,
                spell_id=spell.spell_id,
                conduit=owner,
            )

    assert borrower._spellbook._remove_contracted_calls == [(owner._id, spell.spell_id)]
    assert any(
        level == "error" and "contract cleanup failed" in message
        for level, message in borrower._logger.messages
    )


def test_remove_spell_from_contract_succeeds_when_contract_key_lookup_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removal still succeeds when contracted-spell lookup for invalidation metadata fails."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-key-lookup-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell_by_id = MagicMock(side_effect=RuntimeError("lookup boom"))
    with patch.object(ConduitWard, "_invalidate_contract_consumers") as mock_invalidate:
        result = borrower._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
        )

    assert result is True
    mock_invalidate.assert_called_once_with(None)


def test_remove_spell_from_contract_logs_when_restore_rollback_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify remove_spell logs rollback failures when detail restoration itself fails."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-remove-rollback-log", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    with patch.object(
        borrower._spellbook,
        "_remove_contracted_spell",
        side_effect=RuntimeError("remove boom"),
    ), patch.object(
        ConduitWard,
        "_restore_detail_snapshot",
        side_effect=RuntimeError("restore boom"),
    ):
        with pytest.raises(RuntimeError, match="remove boom"):
            borrower._conduit_ward._remove_spell_from_contract(
                spell=spell,
                spell_id=spell.spell_id,
                conduit=owner,
            )

    assert any(
        level == "error" and "rollback failed after spellbook remove error" in message
        for level, message in borrower._logger.messages
    )


def test_remove_spell_from_contract_succeeds_when_contract_key_lookup_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removal still succeeds when contracted-spell lookup for invalidation metadata fails."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-key-lookup-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell_by_id = MagicMock(side_effect=RuntimeError("lookup boom"))
    with patch.object(ConduitWard, "_invalidate_contract_consumers") as mock_invalidate:
        result = borrower._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
        )

    assert result is True
    mock_invalidate.assert_called_once_with(None)


def test_remove_all_spells_from_contract_swallows_invalidate_contract_consumers_error(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify invalidate-consumer failures are swallowed after successful bulk contract clearing."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-invalidate-clear", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    with patch.object(
        ConduitWard,
        "_invalidate_contract_consumers",
        side_effect=RuntimeError("invalidate boom"),
    ):
        result = borrower._conduit_ward._remove_all_spells_from_contract(conduit=owner)

    contract = borrower._conduit_ward._find_contract(owner)
    assert result is True
    assert contract._get_detail_map(owner._conduit_ward) == {}


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


def test_sever_link_raises_when_missing_contract(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify severing without a contract raises. The ward should reject the operation."""
    owner, borrower = conduit_pair

    with pytest.raises(RuntimeError, match="No contract found"):
        borrower._conduit_ward._sever_link(owner)


def test_remove_contract_noop_when_missing(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify removing a missing contract is a no-op. The method should return False."""
    owner, borrower = conduit_pair

    result = borrower._conduit_ward._remove_contract(owner)

    assert result is False
    assert borrower._spellbook._sever_link_calls == []
    assert owner._spellbook._sever_link_calls == []


def test_get_contracted_conduits_returns_none_when_empty(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify no contracts return None. Empty wards should not return an empty list."""
    _, borrower = conduit_pair

    assert borrower._conduit_ward._get_contracted_conduits() is None


def test_get_contracted_conduits_returns_peer_after_link(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify linked peer conduits are listed. Returned tuples should include the peer id and object."""
    owner, borrower = conduit_pair
    _link_contract(borrower, owner)

    result = borrower._conduit_ward._get_contracted_conduits()

    assert result is not None
    assert len(result) == 1
    peer_id, peer = result[0]
    assert peer_id == owner._id
    assert peer is owner


def test_get_spells_in_contract_by_conduit_returns_none_when_missing(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify missing contracts return None. The lookup should not raise."""
    owner, borrower = conduit_pair

    assert borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id) is None


def test_get_spells_in_contract_by_conduit_name_validates_name(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify empty conduit names raise ValueError. A non-empty string is required."""
    _, borrower = conduit_pair

    with pytest.raises(ValueError, match="non-empty"):
        borrower._conduit_ward._get_spells_in_contract_by_conduit_name("")


def test_get_spells_in_contract_by_conduit_name_returns_none_for_unknown(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify unknown conduit names return None. The search should not match unrelated names."""
    _, borrower = linked_pair

    assert borrower._conduit_ward._get_spells_in_contract_by_conduit_name("Missing") is None


def test_add_spells_to_contract_reports_success_and_failure(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify bulk add reports per-spell status. Missing spell ids should be recorded as failures."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-19", permissions=Permissions.create)

    report = borrower._conduit_ward._add_spells_to_contract(
        spell_ids=[spell.spell_id, "missing-spell"],
        conduit=owner,
        permissions="create",
    )

    assert report["success"] == [spell.spell_id]
    assert "missing-spell" in report["failed"]
    assert spell.spell_index in borrower._spellbook._contracted_spells[owner._id]


def test_remove_spells_from_contract_reports_success_and_failure(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify bulk removal reports failures without aborting. Remaining details should persist."""
    owner, borrower = linked_pair
    spell_a = _register_spell(owner, "spell-20", permissions=Permissions.create)
    spell_b = _register_spell(owner, "spell-21", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_a,
        spell_id=spell_a.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_b,
        spell_id=spell_b.spell_id,
        conduit=owner,
        permissions="create",
    )

    report = borrower._conduit_ward._remove_spells_from_contract(
        spell_ids=[spell_a.spell_id, "missing-spell"],
        conduit=owner,
    )

    assert report["success"] == [spell_a.spell_id]
    assert "missing-spell" in report["failed"]
    contract = borrower._conduit_ward._find_contract(owner)
    assert contract._get_detail_map(owner._conduit_ward).get(spell_b.spell_id) is not None


def test_remove_root_from_contracts_severs_when_empty(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing a root deletes the detail and severs empty contracts. Spellbook removal should occur."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-22", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-x",
    )
    contract = borrower._conduit_ward._find_contract(owner)

    report = borrower._conduit_ward._remove_root_from_contracts(
        root_spell_id="root-x",
        conduit=owner,
    )

    assert report["success"] == [contract._id]
    assert borrower._conduit_ward._contracts == {}
    assert owner._conduit_ward._contracts == {}
    assert borrower._spellbook._remove_contracted_calls == [(owner._id, spell.spell_id)]
    assert borrower._spellbook._sever_link_calls == [owner._id]
    assert owner._spellbook._sever_link_calls == [borrower._id]


def test_remove_root_from_contracts_preserves_detail_with_multiple_sources(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing one root keeps the detail when other sources remain. The contract should stay active."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-23", permissions=Permissions.create)

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

    report = borrower._conduit_ward._remove_root_from_contracts(
        root_spell_id="root-a",
        conduit=owner,
    )

    detail = contract._get_detail_map(owner._conduit_ward)[spell.spell_id]
    assert report["success"] == []
    assert detail.sources == {"root-b"}
    assert borrower._spellbook._remove_contracted_calls == []


def test_remove_root_from_contracts_restores_detail_when_spellbook_remove_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify root removal failures restore the deleted detail instead of leaving partial mutation."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-root-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-fail",
    )
    contract = borrower._conduit_ward._find_contract(owner)
    borrower._spellbook._remove_contracted_spell = MagicMock(side_effect=RuntimeError("remove boom"))

    report = borrower._conduit_ward._remove_root_from_contracts(
        root_spell_id="root-fail",
        conduit=owner,
    )

    detail = contract._get_detail_map(owner._conduit_ward)[spell.spell_id]
    assert report["success"] == []
    assert contract._id in report["failed"]
    assert detail.sources == {"root-fail"}
    assert spell.spell_index in borrower._spellbook._contracted_spells[owner._id]


def test_remove_root_from_contracts_logs_when_restore_rollback_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify remove_root logs rollback failures when detail restoration itself fails."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-root-restore-log", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-restore-log",
    )
    with patch.object(
        borrower._spellbook,
        "_remove_contracted_spell",
        side_effect=RuntimeError("remove boom"),
    ), patch.object(
        ConduitWard,
        "_restore_detail_snapshot",
        side_effect=RuntimeError("restore boom"),
    ):
        report = borrower._conduit_ward._remove_root_from_contracts(
            root_spell_id="root-restore-log",
            conduit=owner,
        )

    assert report["success"] == []
    assert any(
        level == "error" and "rollback failed for" in message
        for level, message in borrower._logger.messages
    )



def test_link_spell_dependencies_creates_contract_and_details(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependency linking creates contracts and Detail entries. Each detail should be tagged as dependency."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-1", permissions=Permissions.create)
    root_spell = _register_spell(borrower, "root-1", permissions=Permissions.create, dependencies=["dep-1"])
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail = contract._get_detail_map(owner._conduit_ward)[dep_spell.spell_id]

    assert detail.reason == DetailReason.dependency
    assert detail.contract_type == ContractTypes.received
    assert detail.sources == {root_spell.spell_id}
    assert dep_spell.spell_index in borrower._spellbook._contracted_spells[owner._id]
    assert borrower._spellbook._add_contracted_calls == [(owner._id, dep_spell.spell_id)]


def test_link_spell_dependencies_downgrades_permissions_to_read(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependencies downgrade to read when needed. Requested create should not elevate read-only spells."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-2", permissions=Permissions.read)
    root_spell = _register_spell(borrower, "root-2", permissions=Permissions.create, dependencies=["dep-2"])
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail = contract._get_detail_map(owner._conduit_ward)[dep_spell.spell_id]

    assert detail.permissions == Permissions.read


def test_link_spell_dependencies_skips_local_versions(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify local dependencies are skipped. No contract should be created for local versions."""
    owner, borrower = conduit_pair
    local_dep = _register_spell(borrower, "dep-local", permissions=Permissions.create)
    root_spell = _register_spell(borrower, "root-3", permissions=Permissions.create, dependencies=[local_dep.spell_id])
    borrower.register_spell_owner(local_dep.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    assert borrower._conduit_ward._contracts == {}
    assert borrower._spellbook._add_contracted_calls == []


def test_preflight_contract_dependency_collisions_skips_duplicate_dependency_ids() -> None:
    """Verify preflight treats duplicate dependency ids as one visited lineage."""
    owner, borrower = _build_conduit_pair()
    dep_spell = _register_spell(owner, "dep-dup-id", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-dup-id",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id, dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)
    borrower._spellbook._assert_lookup_key_available = MagicMock()

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    assert borrower._spellbook._assert_lookup_key_available.call_count == 2


def test_preflight_contract_dependency_collisions_skips_local_versions() -> None:
    """Verify preflight skips dependency ids already present locally."""
    owner, borrower = _build_conduit_pair()
    local_dep = _register_spell(borrower, "dep-local-preflight", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-local-preflight",
        permissions=Permissions.create,
        dependencies=[local_dep.spell_id],
    )
    borrower.register_spell_owner(local_dep.spell_id, owner)
    borrower.get_conduit_by_spell_id = MagicMock(side_effect=RuntimeError("should not resolve owner"))

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_skips_owner_self_when_not_local() -> None:
    """Verify preflight skips dependency ids whose reported owner is the borrower itself."""
    _, borrower = _build_conduit_pair()
    root_spell = _register_spell(
        borrower,
        "root-self-preflight",
        permissions=Permissions.create,
        dependencies=["dep-self-preflight"],
    )
    borrower.register_spell_owner("dep-self-preflight", borrower)
    borrower.get_spell_by_id = MagicMock(side_effect=RuntimeError("should not resolve spell"))

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_downgrades_requested_read() -> None:
    """Verify preflight downgrades dependency permissions to read when the request is read-scoped."""
    owner, borrower = _build_conduit_pair()
    dep_spell = _register_spell(owner, "dep-preflight-read", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-preflight-read",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    with patch.object(ConduitWard, "_check_spell_if_eligible") as mock_eligible:
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.read,
        )

    assert mock_eligible.call_args.args[2] == Permissions.read


def test_preflight_contract_dependency_collisions_rejects_duplicate_contract_keys_in_batch() -> None:
    """Verify preflight raises when two dependency spells in the same batch share one contract key."""
    owner, borrower = _build_conduit_pair()
    dep_one = _register_spell(
        owner,
        "dep-dup-one",
        permissions=Permissions.create,
        binding_name="dup-binding",
    )
    dep_two = _register_spell(
        owner,
        "dep-dup-two",
        permissions=Permissions.create,
        binding_name="dup-binding",
    )
    root_spell = _register_spell(
        borrower,
        "root-dup-batch",
        permissions=Permissions.create,
        dependencies=[dep_one.spell_id, dep_two.spell_id],
    )
    borrower.register_spell_owner(dep_one.spell_id, owner)
    borrower.register_spell_owner(dep_two.spell_id, owner)

    with pytest.raises(RuntimeError, match="binding key collision"):
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.create,
        )


def test_link_spell_dependencies_skips_owner_self_when_dependency_not_local(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependency walking skips non-local dependencies whose reported owner is the borrower itself."""
    _, borrower = conduit_pair
    root_spell = _register_spell(
        borrower,
        "root-self-owner",
        permissions=Permissions.create,
        dependencies=["dep-self-owner"],
    )
    borrower.register_spell_owner("dep-self-owner", borrower)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    assert borrower._conduit_ward._contracts == {}
    assert borrower._spellbook._add_contracted_calls == []


def test_link_spell_dependencies_skips_duplicate_dependency_ids(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify duplicate dependency ids are visited only once during dependency linking."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-dup-link", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-dup-link",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id, dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail_map = contract._get_detail_map(owner._conduit_ward)

    assert list(detail_map.keys()) == [dep_spell.spell_id]
    assert borrower._spellbook._add_contracted_calls == [(owner._id, dep_spell.spell_id)]


def test_link_spell_dependencies_adds_transitive_dependencies(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify transitive dependencies are contracted. Both direct and indirect dependencies should be linked."""
    owner, borrower = conduit_pair
    dep_two = _register_spell(owner, "dep-3", permissions=Permissions.create)
    dep_one = _register_spell(owner, "dep-4", permissions=Permissions.create, dependencies=[dep_two.spell_id])
    root_spell = _register_spell(borrower, "root-4", permissions=Permissions.create, dependencies=[dep_one.spell_id])
    borrower.register_spell_owner(dep_one.spell_id, owner)
    borrower.register_spell_owner(dep_two.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail_map = contract._get_detail_map(owner._conduit_ward)

    assert dep_one.spell_id in detail_map
    assert dep_two.spell_id in detail_map
    assert len(borrower._spellbook._add_contracted_calls) == 2
    assert set(borrower._spellbook._add_contracted_calls) == {
        (owner._id, dep_one.spell_id),
        (owner._id, dep_two.spell_id),
    }


def test_link_spell_dependencies_downgrades_permissions_when_requested_read(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify read requests downgrade create-capable dependencies to read contracts."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-read-request", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-read-request",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.read,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail = contract._get_detail_map(owner._conduit_ward)[dep_spell.spell_id]

    assert detail.permissions == Permissions.read


def test_link_spell_dependencies_handles_dependency_without_dependencies_attr(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependency walking tolerates dependency spells that omit a dependencies attribute."""
    owner, borrower = conduit_pair
    dep_spell = SimpleNamespace(
        spell_id="dep-no-child-attr",
        spell_index=SpellIndex("dep-no-child-attr"),
        permissions=Permissions.create,
        spellframe="frame",
        binding_name="binding-dep-no-child-attr",
        spell_name="DepNoChildAttr",
        __name__="DepNoChildAttr",
        _owner_conduit_id=owner._id,
    )
    owner._spell_by_id[dep_spell.spell_id] = dep_spell
    owner._spellbook._spells[dep_spell.spell_index] = dep_spell
    root_spell = _register_spell(
        borrower,
        "root-no-child-attr",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    assert dep_spell.spell_id in contract._get_detail_map(owner._conduit_ward)


def test_link_spell_dependencies_raises_when_contract_cannot_be_established(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify dependency linking raises when the owner contract still does not exist after link attempt."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-missing-contract", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-missing-contract",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    with patch.object(ConduitWard, "_find_contract", return_value=None), patch.object(
        ConduitWard,
        "_link",
        return_value=True,
    ):
        with pytest.raises(RuntimeError, match="Failed to create contract"):
            borrower._conduit_ward._link_spell_dependencies(
                root_spell=root_spell,
                root_spell_id=root_spell.spell_id,
                requested_permissions=Permissions.create,
            )


def test_add_spell_to_contract_preflight_rejects_dependency_collision() -> None:
    """Verify dependency collisions fail fast before contract mutation when linking dependencies."""
    owner, borrower = _build_conduit_pair()
    owner_two = FakeConduit("owner-2", name="OwnerTwo", policy=Policies.default, dynamic=True)
    borrower.register_conduit(owner_two)
    owner_two.register_conduit(borrower)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._create_new_contract(owner_two)

    collision_spell = _register_spell(
        owner_two,
        "spell-collision",
        permissions=Permissions.create,
        binding_name="shared",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=collision_spell,
        spell_id=collision_spell.spell_id,
        conduit=owner_two,
        permissions="create",
    )

    dep_spell = _register_spell(
        owner,
        "dep-collision",
        permissions=Permissions.create,
        binding_name="shared",
    )
    root_spell = _register_spell(
        owner,
        "root-collision",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    with pytest.raises(RuntimeError, match="binding key collision"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=root_spell,
            spell_id=root_spell.spell_id,
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract._get_detail_map(owner._conduit_ward) == {}


def test_preflight_contract_dependency_collisions_rejects_duplicate_contract_keys_in_batch() -> None:
    """Verify preflight raises when two dependency spells in the same batch share one contract key."""
    owner, borrower = _build_conduit_pair()
    dep_one = _register_spell(
        owner,
        "dep-dup-one",
        permissions=Permissions.create,
        binding_name="dup-binding",
    )
    dep_two = _register_spell(
        owner,
        "dep-dup-two",
        permissions=Permissions.create,
        binding_name="dup-binding",
    )
    root_spell = _register_spell(
        borrower,
        "root-dup-batch",
        permissions=Permissions.create,
        dependencies=[dep_one.spell_id, dep_two.spell_id],
    )
    borrower.register_spell_owner(dep_one.spell_id, owner)
    borrower.register_spell_owner(dep_two.spell_id, owner)

    with pytest.raises(RuntimeError, match="binding key collision"):
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.create,
        )


def test_add_spell_to_contract_preflight_rejects_root_collision() -> None:
    """Verify root spell collisions fail fast before contract mutation with link_dependencies."""
    owner, borrower = _build_conduit_pair()
    owner_two = FakeConduit("owner-2", name="OwnerTwo", policy=Policies.default, dynamic=True)
    borrower.register_conduit(owner_two)
    owner_two.register_conduit(borrower)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._create_new_contract(owner_two)

    collision_spell = _register_spell(
        owner_two,
        "spell-root-collision",
        permissions=Permissions.create,
        binding_name="shared-root",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=collision_spell,
        spell_id=collision_spell.spell_id,
        conduit=owner_two,
        permissions="create",
    )

    root_spell = _register_spell(
        owner,
        "spell-root",
        permissions=Permissions.create,
        binding_name="shared-root",
    )

    with pytest.raises(RuntimeError, match="binding key collision"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=root_spell,
            spell_id=root_spell.spell_id,
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract._get_detail_map(owner._conduit_ward) == {}


def test_add_spell_to_contract_preflight_allows_local_collision() -> None:
    """Verify local binding collisions are allowed when contracting dependencies."""
    owner, borrower = _build_conduit_pair()
    borrower._conduit_ward._create_new_contract(owner)

    _register_spell(
        borrower,
        "spell-local",
        permissions=Permissions.create,
        binding_name="shared-local",
    )
    root_spell = _register_spell(
        owner,
        "spell-root-local",
        permissions=Permissions.create,
        binding_name="shared-local",
    )

    borrower._conduit_ward._add_spell_to_contract(
        spell=root_spell,
        spell_id=root_spell.spell_id,
        conduit=owner,
        permissions="create",
        link_dependencies=True,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract._get_detail_map(owner._conduit_ward).get(root_spell.spell_id) is not None


def test_add_spell_to_contract_preflight_raises_on_missing_dependency_owner() -> None:
    """Verify missing dependency owners fail fast before contract mutation."""
    owner, borrower = _build_conduit_pair()
    borrower._conduit_ward._create_new_contract(owner)

    root_spell = _register_spell(
        owner,
        "spell-root-missing-owner",
        permissions=Permissions.create,
        dependencies=["dep-missing-owner"],
    )

    with pytest.raises(RuntimeError, match="owner not found"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=root_spell,
            spell_id=root_spell.spell_id,
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract._get_detail_map(owner._conduit_ward) == {}


def test_add_spell_to_contract_preflight_raises_on_missing_dependency_spell() -> None:
    """Verify missing dependency spells fail fast before contract mutation."""
    owner, borrower = _build_conduit_pair()
    borrower._conduit_ward._create_new_contract(owner)

    dep_id = "dep-missing-spell"
    borrower.register_spell_owner(dep_id, owner)
    root_spell = _register_spell(
        owner,
        "spell-root-missing-spell",
        permissions=Permissions.create,
        dependencies=[dep_id],
    )

    with pytest.raises(RuntimeError, match="not found in owner conduit"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=root_spell,
            spell_id=root_spell.spell_id,
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract._get_detail_map(owner._conduit_ward) == {}


def test_add_spell_to_contract_preflight_rejects_mixed_owner_dependency_collision() -> None:
    """Verify mixed-owner dependency collisions fail fast without partial mutation."""
    owner, borrower = _build_conduit_pair()
    owner_two = FakeConduit("owner-2", name="OwnerTwo", policy=Policies.default, dynamic=True)
    borrower.register_conduit(owner_two)
    owner_two.register_conduit(borrower)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._create_new_contract(owner_two)

    collision_spell = _register_spell(
        owner_two,
        "spell-collision-owner-two",
        permissions=Permissions.create,
        binding_name="shared-mixed",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=collision_spell,
        spell_id=collision_spell.spell_id,
        conduit=owner_two,
        permissions="create",
    )

    dep_ok = _register_spell(owner, "dep-ok", permissions=Permissions.create)
    dep_collision = _register_spell(
        owner_two,
        "dep-collision",
        permissions=Permissions.create,
        binding_name="shared-mixed",
    )
    borrower.register_spell_owner(dep_ok.spell_id, owner)
    borrower.register_spell_owner(dep_collision.spell_id, owner_two)
    root_spell = _register_spell(
        owner,
        "spell-root-mixed",
        permissions=Permissions.create,
        dependencies=[dep_ok.spell_id, dep_collision.spell_id],
    )

    with pytest.raises(RuntimeError, match="binding key collision"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=root_spell,
            spell_id=root_spell.spell_id,
            conduit=owner,
            permissions="create",
            link_dependencies=True,
        )

    contract_owner = borrower._conduit_ward._find_contract(owner)
    contract_owner_two = borrower._conduit_ward._find_contract(owner_two)
    assert contract_owner._get_detail_map(owner._conduit_ward) == {}
    detail_map_two = contract_owner_two._get_detail_map(owner_two._conduit_ward)
    assert detail_map_two.get(dep_collision.spell_id) is None
    assert detail_map_two.get(collision_spell.spell_id) is not None


def test_link_returns_true_when_contract_already_exists(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify _link returns True without duplicating an existing contract. Spellbook buckets should not duplicate."""
    owner, borrower = conduit_pair
    borrower._conduit_ward._create_new_contract(owner)
    contract_ids = set(borrower._conduit_ward._contracts.keys())
    create_calls = list(borrower._spellbook._create_link_calls)

    result = borrower._conduit_ward._link(owner)

    assert result is True
    assert set(borrower._conduit_ward._contracts.keys()) == contract_ids
    assert borrower._spellbook._create_link_calls == create_calls


def test_link_raises_when_dynamic_disabled() -> None:
    """Verify _link rejects non-dynamic environments. A RuntimeError should be raised."""
    owner, borrower = _build_conduit_pair(dynamic=False)

    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        borrower._conduit_ward._link(owner)


def test_add_spell_to_contract_raises_when_no_contract(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify add_spell_to_contract requires an existing contract. Missing contracts should raise."""
    owner, borrower = conduit_pair
    spell = _register_spell(owner, "spell-24", permissions=Permissions.create)

    with pytest.raises(RuntimeError, match="No contract found"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="create",
        )


def test_add_spell_to_contract_raises_on_mismatched_spell_id(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify mismatched spell_id and spell identity raises. The contract should not be modified."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-25", permissions=Permissions.create)
    mismatched_id = "mismatched-id"

    with pytest.raises(RuntimeError, match="does not match inspected"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=mismatched_id,
            conduit=owner,
            permissions="create",
        )


def test_remove_spell_from_contract_leaves_contract_when_other_details_exist(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing one spell keeps the contract if other details exist. Spellbook removal should occur once."""
    owner, borrower = linked_pair
    spell_a = _register_spell(owner, "spell-26", permissions=Permissions.create)
    spell_b = _register_spell(owner, "spell-27", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_a,
        spell_id=spell_a.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_b,
        spell_id=spell_b.spell_id,
        conduit=owner,
        permissions="create",
    )

    borrower._conduit_ward._remove_spell_from_contract(
        spell=spell_a,
        spell_id=spell_a.spell_id,
        conduit=owner,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    assert contract is not None
    assert spell_b.spell_id in contract._get_detail_map(owner._conduit_ward)
    assert borrower._spellbook._remove_contracted_calls == [(owner._id, spell_a.spell_id)]
    assert borrower._spellbook._sever_link_calls == []


def test_remove_all_spells_from_contract_raises_when_missing(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing all spells without a contract raises. The caller must link first."""
    owner, borrower = conduit_pair

    with pytest.raises(RuntimeError, match="No contract found"):
        borrower._conduit_ward._remove_all_spells_from_contract(conduit=owner)


def test_get_all_spells_in_contracts_raises_when_validation_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify validation failures raise when requested. Invalid contracts should stop retrieval."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-28", permissions=Permissions.create)

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            spell,
            Permissions.create,
            ContractTypes.received,
            reason=DetailReason.manual,
        )
        contract._add(owner._conduit_ward, detail)

    with pytest.raises(RuntimeError, match="invalid"):
        borrower._conduit_ward._get_all_spells_in_contracts(validate=True)


def test_get_all_spells_in_contracts_returns_none_when_validate_false(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify invalid entries are skipped when validate=False. The result should be None for empty data."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-29", permissions=Permissions.create)

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            spell,
            Permissions.create,
            ContractTypes.received,
            reason=DetailReason.manual,
        )
        contract._add(owner._conduit_ward, detail)

    result = borrower._conduit_ward._get_all_spells_in_contracts(validate=False)

    assert result is None


def test_get_all_spells_in_contracts_raises_when_contracted_lookup_fails_with_validate_true(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify contracted lookup errors are wrapped when validate=True and contract validation passes."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-lookup-boom", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell = MagicMock(side_effect=RuntimeError("lookup boom"))
    contract = borrower._conduit_ward._find_contract(owner)

    with patch.object(
        ConduitWard,
        "_validate_contracts_and_define",
        return_value={contract._id: True},
    ):
        with pytest.raises(RuntimeError, match="Failed to inspect contract"):
            borrower._conduit_ward._get_all_spells_in_contracts(validate=True)


def test_get_all_spells_in_contracts_skips_lookup_failure_when_validate_false(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify contracted lookup errors are skipped when validate=False."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-lookup-skip", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell = MagicMock(side_effect=RuntimeError("lookup boom"))

    result = borrower._conduit_ward._get_all_spells_in_contracts(validate=False)

    assert result is None


def test_get_spell_in_contracts_returns_none_when_missing(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify missing spell ids return None. No contract matches should be found."""
    _, borrower = linked_pair

    assert borrower._conduit_ward._get_spell_in_contracts("missing-spell") is None


def test_get_spell_in_contracts_returns_none_on_contracted_lookup_error(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify contracted lookup errors return None instead of propagating."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-lookup-error", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell = MagicMock(side_effect=RuntimeError("lookup boom"))

    assert borrower._conduit_ward._get_spell_in_contracts(spell.spell_id) is None


def test_get_spell_in_contracts_returns_none_when_contracts_exist_but_no_detail_matches(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spell lookup returns None when contracts exist but no detail lineage matches the requested spell id."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-present-other", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    assert borrower._conduit_ward._get_spell_in_contracts("spell-missing") is None


def test_get_spells_in_contract_by_conduit_skips_outbound_resolution_exception(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify outbound spell resolution exceptions are skipped instead of propagating."""
    owner, borrower = linked_pair
    inbound_spell = _register_spell(owner, "spell-outbound-skip", permissions=Permissions.create)
    outbound_spell = _register_spell(borrower, "spell-outbound-local", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=inbound_spell,
        spell_id=inbound_spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            outbound_spell,
            Permissions.create,
            ContractTypes.initiated,
            reason=DetailReason.manual,
        )
        contract._add(borrower._conduit_ward, detail)

    borrower.get_spell_by_id = MagicMock(side_effect=RuntimeError("lookup boom"))

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id)

    inbound = {sid: found for sid, found in result["inbound"]}
    assert inbound[inbound_spell.spell_id] is inbound_spell
    assert result["outbound"] == []


def test_describe_contract_raises_when_missing(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify describe_contract raises without an existing contract. Missing ids should error."""
    owner, borrower = conduit_pair

    with pytest.raises(RuntimeError, match="No contract found"):
        borrower._conduit_ward._describe_contract(owner._id)


def test_validate_received_contracts_returns_true_when_valid(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify validate_received_contracts returns True for valid contracts. Borrowed spells should validate."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-30", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    assert borrower._conduit_ward._validate_received_contracts() is True


def test_validate_contracts_and_define_falls_back_to_find_by_id(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify validation falls back to contracted lookup by spell_id when lookup by SpellIndex fails."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-fallback", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell = MagicMock(side_effect=RuntimeError("index boom"))
    borrower._spellbook._find_contracted_spell_by_id = MagicMock(return_value=spell)

    results = borrower._conduit_ward._validate_contracts_and_define()
    contract = borrower._conduit_ward._find_contract(owner)

    assert results[contract._id] is True


def test_validate_contracts_and_define_returns_false_when_fallback_lookup_by_id_fails(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify validation returns False when both contracted lookup strategies fail."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-fallback-miss", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._spellbook._find_contracted_spell = MagicMock(side_effect=RuntimeError("index boom"))
    borrower._spellbook._find_contracted_spell_by_id = MagicMock(side_effect=RuntimeError("id boom"))

    results = borrower._conduit_ward._validate_contracts_and_define()
    contract = borrower._conduit_ward._find_contract(owner)

    assert results[contract._id] is False


def test_preflight_contract_dependency_collisions_rejects_missing_root_spell() -> None:
    """Verify preflight rejects a missing root spell immediately."""
    owner, borrower = _build_conduit_pair()

    with pytest.raises(ValueError, match="root_spell must not be None"):
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=None,
            root_spell_id="root-missing",
            requested_permissions=Permissions.create,
        )


def test_preflight_contract_dependency_collisions_rejects_missing_root_spell_id() -> None:
    """Verify preflight rejects a missing root spell id immediately."""
    _, borrower = _build_conduit_pair()
    root_spell = _register_spell(borrower, "root-preflight", permissions=Permissions.create)

    with pytest.raises(ValueError, match="root_spell_id must not be None"):
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=root_spell,
            root_spell_id=None,
            requested_permissions=Permissions.create,
        )


def test_preflight_contract_dependency_collisions_handles_root_without_dependencies_attr() -> None:
    """Verify preflight treats a missing dependencies attribute as no dependencies."""
    _, borrower = _build_conduit_pair()
    root_spell = SimpleNamespace(
        spell_id="root-preflight-no-deps",
        spell_index=SpellIndex("root-preflight-no-deps"),
        permissions=Permissions.create,
        spellframe="frame",
        binding_name="binding-root-preflight-no-deps",
        spell_name="RootPreflightNoDeps",
        __name__="RootPreflightNoDeps",
    )

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_handles_child_without_dependencies_attr() -> None:
    """Verify preflight tolerates dependency spells that omit a dependencies attribute."""
    owner, borrower = _build_conduit_pair()
    dep_spell = SimpleNamespace(
        spell_id="dep-preflight-no-child-attr",
        spell_index=SpellIndex("dep-preflight-no-child-attr"),
        permissions=Permissions.create,
        spellframe="frame",
        binding_name="binding-dep-preflight-no-child-attr",
        spell_name="DepPreflightNoChildAttr",
        __name__="DepPreflightNoChildAttr",
        _owner_conduit_id=owner._id,
    )
    owner._spell_by_id[dep_spell.spell_id] = dep_spell
    owner._spellbook._spells[dep_spell.spell_index] = dep_spell
    root_spell = _register_spell(
        borrower,
        "root-preflight-child-no-deps",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_walks_child_dependencies() -> None:
    """Verify preflight walks child dependency ids when a dependency exposes nested dependencies."""
    owner, borrower = _build_conduit_pair()
    dep_child = _register_spell(owner, "dep-preflight-child", permissions=Permissions.create)
    dep_parent = _register_spell(
        owner,
        "dep-preflight-parent",
        permissions=Permissions.create,
        dependencies=[dep_child.spell_id],
    )
    root_spell = _register_spell(
        borrower,
        "root-preflight-nested",
        permissions=Permissions.create,
        dependencies=[dep_parent.spell_id],
    )
    borrower.register_spell_owner(dep_parent.spell_id, owner)
    borrower.register_spell_owner(dep_child.spell_id, owner)
    borrower._spellbook._assert_lookup_key_available = MagicMock()

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    assert borrower._spellbook._assert_lookup_key_available.call_count == 3


def test_preflight_contract_dependency_collisions_noops_without_spellbook() -> None:
    """Verify preflight returns without error when the conduit has no spellbook."""
    _, borrower = _build_conduit_pair()
    root_spell = _register_spell(borrower, "root-no-spellbook", permissions=Permissions.create)
    borrower._spellbook = None

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_skips_duplicate_dependency_ids() -> None:
    """Verify preflight treats duplicate dependency ids as one visited lineage."""
    owner, borrower = _build_conduit_pair()
    dep_spell = _register_spell(owner, "dep-dup-id", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-dup-id",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id, dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)
    borrower._spellbook._assert_lookup_key_available = MagicMock()

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )

    assert borrower._spellbook._assert_lookup_key_available.call_count == 2


def test_preflight_contract_dependency_collisions_skips_local_versions() -> None:
    """Verify preflight skips dependency ids already present locally."""
    owner, borrower = _build_conduit_pair()
    local_dep = _register_spell(borrower, "dep-local-preflight", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-local-preflight",
        permissions=Permissions.create,
        dependencies=[local_dep.spell_id],
    )
    borrower.register_spell_owner(local_dep.spell_id, owner)
    borrower.get_conduit_by_spell_id = MagicMock(side_effect=RuntimeError("should not resolve owner"))

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_skips_owner_self_when_not_local() -> None:
    """Verify preflight skips dependency ids whose reported owner is the borrower itself."""
    _, borrower = _build_conduit_pair()
    root_spell = _register_spell(
        borrower,
        "root-self-preflight",
        permissions=Permissions.create,
        dependencies=["dep-self-preflight"],
    )
    borrower.register_spell_owner("dep-self-preflight", borrower)
    borrower.get_spell_by_id = MagicMock(side_effect=RuntimeError("should not resolve spell"))

    borrower._conduit_ward._preflight_contract_dependency_collisions(
        root_spell=root_spell,
        root_spell_id=root_spell.spell_id,
        requested_permissions=Permissions.create,
    )


def test_preflight_contract_dependency_collisions_downgrades_requested_read() -> None:
    """Verify preflight downgrades dependency permissions to read when the request is read-scoped."""
    owner, borrower = _build_conduit_pair()
    dep_spell = _register_spell(owner, "dep-preflight-read", permissions=Permissions.create)
    root_spell = _register_spell(
        borrower,
        "root-preflight-read",
        permissions=Permissions.create,
        dependencies=[dep_spell.spell_id],
    )
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    with patch.object(ConduitWard, "_check_spell_if_eligible") as mock_eligible:
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.read,
        )

    assert mock_eligible.call_args.args[2] == Permissions.read


def test_preflight_contract_dependency_collisions_rejects_duplicate_contract_keys_in_batch() -> None:
    """Verify preflight raises when two dependency spells in the same batch share one contract key."""
    owner, borrower = _build_conduit_pair()
    dep_one = _register_spell(
        owner,
        "dep-dup-one",
        permissions=Permissions.create,
        binding_name="dup-binding",
    )
    dep_two = _register_spell(
        owner,
        "dep-dup-two",
        permissions=Permissions.create,
        binding_name="dup-binding",
    )
    root_spell = _register_spell(
        borrower,
        "root-dup-batch",
        permissions=Permissions.create,
        dependencies=[dep_one.spell_id, dep_two.spell_id],
    )
    borrower.register_spell_owner(dep_one.spell_id, owner)
    borrower.register_spell_owner(dep_two.spell_id, owner)

    with pytest.raises(RuntimeError, match="binding key collision"):
        borrower._conduit_ward._preflight_contract_dependency_collisions(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.create,
        )


def test_get_spells_in_contract_by_conduit_name_returns_match(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify conduit name lookup returns inbound spells. The peer name should map to its contract."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-31", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit_name(owner._name)

    inbound = {sid: found for sid, found in result["inbound"]}
    assert inbound[spell.spell_id] is spell
    assert result["outbound"] == []


def test_get_contracted_conduits_returns_multiple_peers() -> None:
    """Verify multiple peers are listed. The ward should expose all linked conduits."""
    owner, borrower = _build_conduit_pair()
    owner_two = FakeConduit("owner-2", name="OwnerTwo", policy=Policies.default, dynamic=True)
    borrower.register_conduit(owner_two)
    owner_two.register_conduit(borrower)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._create_new_contract(owner_two)

    result = borrower._conduit_ward._get_contracted_conduits()

    ids = {conduit_id for conduit_id, _ in result}
    assert ids == {owner._id, owner_two._id}


def test_remove_root_from_contracts_across_all_contracts() -> None:
    """Verify removing a root across all contracts severs each empty contract. All peers should be cleaned."""
    owner, borrower = _build_conduit_pair()
    owner_two = FakeConduit("owner-3", name="OwnerThree", policy=Policies.default, dynamic=True)
    borrower.register_conduit(owner_two)
    owner_two.register_conduit(borrower)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._create_new_contract(owner_two)

    spell_one = _register_spell(owner, "spell-32", permissions=Permissions.create)
    spell_two = _register_spell(owner_two, "spell-33", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_one,
        spell_id=spell_one.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-shared",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_two,
        spell_id=spell_two.spell_id,
        conduit=owner_two,
        permissions="create",
        root_spell_id="root-shared",
    )

    contract_ids = {contract._id for contract in borrower._conduit_ward._contracts.values()}

    report = borrower._conduit_ward._remove_root_from_contracts(root_spell_id="root-shared")

    assert set(report["success"]) == contract_ids
    assert borrower._conduit_ward._contracts == {}
    assert set(borrower._spellbook._remove_contracted_calls) == {
        (owner._id, spell_one.spell_id),
        (owner_two._id, spell_two.spell_id),
    }


def test_remove_root_from_contracts_skips_none_peer_on_empty_contract(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify remove_root skips a None peer when an emptied contract cannot be severed by peer reference."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-root-none-peer", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-none-peer",
    )
    contract = borrower._conduit_ward._find_contract(owner)
    owner._conduit_ward._conduit = None

    report = borrower._conduit_ward._remove_root_from_contracts(
        root_spell_id="root-none-peer",
    )

    assert report["success"] == [contract._id]



def test_link_spell_dependencies_raises_when_owner_missing(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify missing owner conduits raise. Dependencies must have a known owner."""
    _, borrower = conduit_pair
    root_spell = _register_spell(borrower, "root-5", permissions=Permissions.create, dependencies=["missing-dep"])

    with pytest.raises(RuntimeError, match="owner not found"):
        borrower._conduit_ward._link_spell_dependencies(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.create,
        )


def test_link_spell_dependencies_raises_when_dependency_missing(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify missing dependency spells raise. Owners must actually contain the dependency spell."""
    owner, borrower = conduit_pair
    borrower.register_spell_owner("missing-dep", owner)
    root_spell = _register_spell(borrower, "root-6", permissions=Permissions.create, dependencies=["missing-dep"])

    with pytest.raises(RuntimeError, match="not found in owner conduit"):
        borrower._conduit_ward._link_spell_dependencies(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.create,
        )


def test_link_spell_dependencies_merges_sources_without_duplicate_contracts(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify multiple roots merge sources without extra contracted spell inserts."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-5", permissions=Permissions.create)
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    root_one = _register_spell(borrower, "root-7", permissions=Permissions.create, dependencies=[dep_spell.spell_id])
    root_two = _register_spell(borrower, "root-8", permissions=Permissions.create, dependencies=[dep_spell.spell_id])

    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_one,
        root_spell_id=root_one.spell_id,
        requested_permissions=Permissions.create,
    )
    borrower._conduit_ward._link_spell_dependencies(
        root_spell=root_two,
        root_spell_id=root_two.spell_id,
        requested_permissions=Permissions.create,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail = contract._get_detail_map(owner._conduit_ward)[dep_spell.spell_id]

    assert detail.sources == {root_one.spell_id, root_two.spell_id}
    assert borrower._spellbook._add_contracted_calls == [(owner._id, dep_spell.spell_id)]


def test_link_spell_dependencies_raises_when_policy_block_all() -> None:
    """Verify block_all policy rejects dependency contracts. The ward should raise before contracting."""
    owner, borrower = _build_conduit_pair(owner_policy=Policies.block_all)
    dep_spell = _register_spell(owner, "dep-6", permissions=Permissions.create)
    root_spell = _register_spell(borrower, "root-9", permissions=Permissions.create, dependencies=[dep_spell.spell_id])
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    with pytest.raises(RuntimeError, match="block_all"):
        borrower._conduit_ward._link_spell_dependencies(
            root_spell=root_spell,
            root_spell_id=root_spell.spell_id,
            requested_permissions=Permissions.create,
        )


def test_find_contract_by_id_returns_contract(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify contract lookups by peer id return the shared contract. The returned object should match the peer link."""
    owner, borrower = conduit_pair
    borrower._conduit_ward._create_new_contract(owner)

    contract = borrower._conduit_ward._find_contract_by_id(owner._id)

    assert contract is borrower._conduit_ward._find_contract(owner)
    assert contract is owner._conduit_ward._find_contract(borrower)


def test_find_contract_by_id_returns_none_when_missing(conduit_pair: tuple[FakeConduit, FakeConduit]) -> None:
    """Verify missing contract lookups return None. The ward should not raise for absent peers."""
    owner, borrower = conduit_pair

    assert borrower._conduit_ward._find_contract_by_id(owner._id) is None


def test_remove_spell_from_contract_raises_when_contract_missing(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing a spell without a contract raises. The ward should reject removal for unknown peers."""
    owner, borrower = conduit_pair
    spell = _register_spell(owner, "spell-34", permissions=Permissions.create)

    with pytest.raises(RuntimeError, match="No contract found"):
        borrower._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
        )


def test_remove_root_from_contracts_raises_on_non_string_root(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify root removal requires a string id. Non-string roots should raise TypeError."""
    _, borrower = linked_pair

    with pytest.raises(TypeError, match="root_spell_id must be a string"):
        borrower._conduit_ward._remove_root_from_contracts(root_spell_id=123)


def test_remove_root_from_contracts_no_matching_sources(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify removing a non-existent root leaves details intact. The contract should remain unchanged."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-35", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-a",
    )
    contract = borrower._conduit_ward._find_contract(owner)

    report = borrower._conduit_ward._remove_root_from_contracts(
        root_spell_id="root-b",
        conduit=owner,
    )

    assert report["success"] == []
    assert spell.spell_id in contract._get_detail_map(owner._conduit_ward)
    assert borrower._spellbook._remove_contracted_calls == []


def test_remove_root_from_contracts_logs_contract_sever_failure(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify root removal logs and continues when empty-contract severing fails."""
    owner, borrower = linked_pair
    spell = _register_spell(owner, "spell-root-sever-fail", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell,
        spell_id=spell.spell_id,
        conduit=owner,
        permissions="create",
        root_spell_id="root-sever-fail",
    )
    contract = borrower._conduit_ward._find_contract(owner)

    with patch.object(
        ConduitWard,
        "_remove_contract",
        side_effect=RuntimeError("sever boom"),
    ):
        report = borrower._conduit_ward._remove_root_from_contracts(
            root_spell_id="root-sever-fail",
            conduit=owner,
        )

    assert report["success"] == [contract._id]
    assert any(
        level == "error" and "contract sever failed" in message
        for level, message in borrower._logger.messages
    )


def test_add_spell_to_contract_rejects_block_all_policy() -> None:
    """Verify owner policy block_all rejects contracting. The eligibility check should raise."""
    owner, borrower = _build_conduit_pair(owner_policy=Policies.block_all)
    borrower._conduit_ward._create_new_contract(owner)
    spell = _register_spell(owner, "spell-36", permissions=Permissions.create)

    with pytest.raises(RuntimeError, match="block_all"):
        borrower._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell.spell_id,
            conduit=owner,
            permissions="create",
        )


def test_add_spell_to_contract_links_dependencies_when_flag_true(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify link_dependencies contracts dependency lineages. Both root and dependency details should be created."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-7", permissions=Permissions.create)
    root_spell = _register_spell(owner, "spell-37", permissions=Permissions.create, dependencies=[dep_spell.spell_id])
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._add_spell_to_contract(
        spell=root_spell,
        spell_id=root_spell.spell_id,
        conduit=owner,
        permissions="create",
        link_dependencies=True,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail_map = contract._get_detail_map(owner._conduit_ward)

    assert root_spell.spell_id in detail_map
    assert dep_spell.spell_id in detail_map
    assert detail_map[dep_spell.spell_id].reason == DetailReason.dependency
    assert detail_map[dep_spell.spell_id].sources == {root_spell.spell_id}
    assert set(borrower._spellbook._add_contracted_calls) == {
        (owner._id, root_spell.spell_id),
        (owner._id, dep_spell.spell_id),
    }


def test_add_spells_to_contract_with_link_dependencies_links_each(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify bulk add links dependencies per root. Contracted spells should include roots and dependencies."""
    owner, borrower = conduit_pair
    dep_spell = _register_spell(owner, "dep-8", permissions=Permissions.create)
    root_one = _register_spell(owner, "spell-38", permissions=Permissions.create, dependencies=[dep_spell.spell_id])
    root_two = _register_spell(owner, "spell-39", permissions=Permissions.create)
    borrower.register_spell_owner(dep_spell.spell_id, owner)

    borrower._conduit_ward._create_new_contract(owner)
    report = borrower._conduit_ward._add_spells_to_contract(
        spell_ids=[root_one.spell_id, root_two.spell_id],
        conduit=owner,
        permissions="create",
        link_dependencies=True,
    )

    contract = borrower._conduit_ward._find_contract(owner)
    detail_map = contract._get_detail_map(owner._conduit_ward)

    assert report["success"] == [root_one.spell_id, root_two.spell_id]
    assert dep_spell.spell_id in detail_map
    assert set(borrower._spellbook._add_contracted_calls) == {
        (owner._id, root_one.spell_id),
        (owner._id, root_two.spell_id),
        (owner._id, dep_spell.spell_id),
    }


def test_get_spells_in_contract_by_conduit_returns_empty_when_no_spells_in_contract(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify empty contracts return empty spell listings. No inbound or outbound spells should be reported."""
    owner, borrower = conduit_pair
    borrower._conduit_ward._create_new_contract(owner)

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id)

    assert result == {"inbound": [], "outbound": []}


def test_get_spells_in_contract_by_conduit_skips_missing_outbound_spell(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify outbound spells without resolution are skipped. Inbound spells should still be returned."""
    owner, borrower = linked_pair
    inbound_spell = _register_spell(owner, "spell-40", permissions=Permissions.create)
    orphan_spell = FakeSpell("spell-41", owner_id=borrower._id, permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=inbound_spell,
        spell_id=inbound_spell.spell_id,
        conduit=owner,
        permissions="create",
    )

    contract = borrower._conduit_ward._find_contract(owner)
    with contract._lock:
        detail = borrower._conduit_ward._create_detail(
            orphan_spell,
            Permissions.create,
            ContractTypes.initiated,
            reason=DetailReason.manual,
        )
        contract._add(borrower._conduit_ward, detail)

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id)

    inbound = {sid: found for sid, found in result["inbound"]}
    assert inbound[inbound_spell.spell_id] is inbound_spell
    assert result["outbound"] == []


def test_get_all_spells_in_contracts_includes_multiple_peers() -> None:
    """Verify aggregate inspection includes each peer conduit. The map should include spell entries per peer id."""
    owner, borrower = _build_conduit_pair()
    owner_two = FakeConduit("owner-4", name="OwnerFour", policy=Policies.default, dynamic=True)
    borrower.register_conduit(owner_two)
    owner_two.register_conduit(borrower)

    borrower._conduit_ward._create_new_contract(owner)
    borrower._conduit_ward._create_new_contract(owner_two)

    spell_one = _register_spell(owner, "spell-42", permissions=Permissions.create)
    spell_two = _register_spell(owner_two, "spell-43", permissions=Permissions.create)

    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_one,
        spell_id=spell_one.spell_id,
        conduit=owner,
        permissions="create",
    )
    borrower._conduit_ward._add_spell_to_contract(
        spell=spell_two,
        spell_id=spell_two.spell_id,
        conduit=owner_two,
        permissions="create",
    )

    result = borrower._conduit_ward._get_all_spells_in_contracts()

    assert set(result.keys()) == {owner._id, owner_two._id}
    assert result[owner._id][0][1] is spell_one
    assert result[owner_two._id][0][1] is spell_two


def test_get_all_spells_in_contracts_returns_none_for_empty_linked_contracts() -> None:
    """Verify linked contracts with no details are skipped and yield None when no spells are available."""
    owner, borrower = _build_conduit_pair()
    borrower._conduit_ward._create_new_contract(owner)

    result = borrower._conduit_ward._get_all_spells_in_contracts(validate=False)

    assert result is None


def test_get_spell_in_contracts_returns_none_when_no_contracts(
    conduit_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify spell lookups return None when no contracts exist. The ward should not raise."""
    _, borrower = conduit_pair

    assert borrower._conduit_ward._get_spell_in_contracts("spell-44") is None

