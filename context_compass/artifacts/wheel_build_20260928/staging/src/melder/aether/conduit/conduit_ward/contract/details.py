from threading import RLock



# Melder imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from typing import Set, ClassVar, Optional
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.spellbook.bind.spell_index import SpellIndex

class Detail(Cleanable):
    """
    Spell-level permission entry stored inside a Contract.

    A `Detail` records which lineage is being shared, which version was
    present when the contract was created, and what permission applies.
    It is lineage-aware (uses `SpellIndex`) and direction-aware (via
    `contract_type`). It also carries optional `sources`, which lets the ward
    distinguish details that were added for one specific root-driven dependency
    expansion from details that were granted independently.

    Attributes:
        spell_index (SpellIndex): Lineage identity for the contracted spell.
        spell_id (str): Spell id (SHA) captured at contract creation time.
        permissions (Permissions): Granted permission (read/create/block).
        contract_type (ContractTypes): Whether this entry was initiated
            or received from the owning ward's perspective.
        reason (DetailReason): Why this detail exists in the contract.
        sources (Set[str]): Root spell ids that currently justify this detail.

    Owned State:
        One `RLock`, a stable `IDBuilder` id, and the six fields above.
        `sources` is the only mutable collection.

    Contract:
        - `spell_index` is the DURABLE anchor; `spell_id` is a point-in-time
          capture. Where they disagree, the index resolves the current head and
          the captured id records what was actually agreed at grant time.
        - `sources` is justification reference-counting: the detail survives
          exactly as long as at least one root still justifies it.
        - Constructor arguments are type-checked and raise `TypeError` rather
          than coercing.

    Threading:
        One instance `RLock`. Details are mutated through the owning
        `ConduitWard`, so lock order runs ward -> contract -> detail.

    Registration:
        MELDER KERNEL - guarded. Details are authored by `ConduitWard` when a
        lineage is granted or borrowed; users read contract state through ward
        verbs rather than constructing entries.

    Subsystem Context:
        The VERSION-SNAPSHOT row of the ward contract model, paired with
        `IndexDetail`, which subscribes to a whole lineage instead. Its three
        enum fields are the vocabulary defined alongside it: `permissions`
        bounds capability, `contract_type` records whose perspective wrote the
        row, and `reason` records why it exists.

    System Context:
        `sources` is what makes dependency-linked rollback correct. One lineage
        can be pulled into a contract by several roots at once, so removal
        cannot be a plain delete - the ward discards the departing root's id and
        retires the detail only when the set empties. Without it, unlinking one
        root would revoke a lineage another root still depends on.
        This pairs directly with `DetailReason`: `dependency` rows are the ones
        carrying justifying sources, while a `manual` grant was never owned by
        any root and therefore survives root removal entirely.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Spell-level permission entry stored inside a Contract. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "spell_index",
        "spell_id",
        "permissions",
        "contract_type",
        "reason",
        "sources",
    ]

    def __init__(
            self,
            spell_index: SpellIndex,
            spell_id: str,
            permissions: Permissions,
            contract_type: ContractTypes,
            reason: DetailReason = DetailReason.other,
            sources: Set[str] | None = None,
    ) -> None:
        """
        Initialize a contract detail.

        Args:
            spell_index: Lineage identifier for the contracted spell.
            spell_id: Spell id (SHA) captured at contract creation time.
            permissions: Permission granted to this lineage.
            contract_type: Direction of the grant from the owning ward's view.
            reason: Why this detail exists.
            sources:
                Optional root spell ids that currently justify this detail.

        Raises:
            TypeError: If any argument is not the expected type.

        Contract:
            `spell_id` records the spell id visible at creation time, while
            `spell_index` remains the durable lineage anchor used for later
            current-head resolution.

        Returns:
            None.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._id: str = IDBuilder.create_id()

        if not isinstance(spell_index, SpellIndex):
            raise TypeError(
                f"spell_index must be SpellIndex, got {type(spell_index).__name__}"
            )
        if not isinstance(permissions, Permissions):
            raise TypeError(
                f"permissions must be Permissions, got {type(permissions).__name__}"
            )
        if not isinstance(contract_type, ContractTypes):
            raise TypeError(
                f"contract_type must be ContractTypes, got {type(contract_type).__name__}"
            )
        if not isinstance(reason, DetailReason):
            raise TypeError(
                f"reason must be DetailReason, got {type(reason).__name__}"
            )
        if sources is not None and not isinstance(sources, set):
            raise TypeError(
                f"sources must be a set of spell_ids when provided, got {type(sources).__name__}"
            )

        self.spell_index: SpellIndex = spell_index
        self.spell_id: str = spell_id
        self.permissions: Permissions = permissions
        self.contract_type: ContractTypes = contract_type
        self.reason: DetailReason = reason
        self.sources: Set[str] = sources if sources is not None else set()


    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Idempotently clear contract metadata and mark this detail cleaned.

        Drops references to the lineage, version, permissions, and contract
        direction so the object cannot be reused after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            del self.spell_index
            del self.spell_id
            del self.permissions
            del self.contract_type
            del self.reason
            if self.sources is not None:
                self.sources.clear()
            del self.sources
            del self._id


    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def has_spell(self, spell_id: str) -> bool:
        """
        Check whether this lineage contains a specific version SHA.

        Args:
            spell_id: SHA fingerprint to check within the index member history.

        Returns:
            bool: True if the lineage advertises the version, else False.
        """
        self.check_cleaned()
        member_ids = self.spell_index._spells_in_index
        if not member_ids:
            return False
        return spell_id in member_ids

    def add_source(self, root_spell_id: str) -> None:
        """
        Record that one root spell id currently justifies this detail.

        Contract:
            Source tagging is additive. Multiple roots may point at the same
            detail when they transitively require the same contracted lineage.

        Returns:
            None.
        """
        self.check_cleaned()
        if root_spell_id is None:
            return
        with self._lock:
            if self.sources is None:
                self.sources = set()
            self.sources.add(root_spell_id)

    def remove_source(self, root_spell_id: str) -> bool:
        """
        Remove one root spell id source from this detail.

        Returns:
            bool:
                True when the source set becomes empty and the caller should
                delete the detail entirely.
        """
        self.check_cleaned()
        if root_spell_id is None or self.sources is None:
            return False
        with self._lock:
            self.sources.discard(root_spell_id)
            return len(self.sources) == 0


class IndexDetail(Cleanable):
    """
    Index-level contract entry stored inside a Contract.

    Where a `Detail` snapshots a version, an `IndexDetail` subscribes a peer to a
    whole SpellIndex (lineage). It is identified by the index's stable id
    (`index_id`), and `selected_spell_id` tracks the lineage's CURRENT active
    member -- it is updated as the owner notches, so the contract surface never has
    to be rewritten on a version change. The receiving conduit consumes the
    selected-id deltas; the index id is the durable subscription key.

    Attributes:
        spell_index (SpellIndex): The contracted lineage (durable identity).
        selected_spell_id (str): The lineage's current active member id (mutable).
        permissions (Permissions): Granted permission (read/create/block).
        contract_type (ContractTypes): Direction of the grant from the owning
            ward's perspective.
        reason (DetailReason): Why this detail exists in the contract.
        sources (Set[str]): Root spell ids that currently justify this detail.

    Owned State:
        One `RLock`, a stable `IDBuilder` id, and the six fields above.
        `selected_spell_id` and `sources` are both mutable.

    Contract:
        - `index_id` is the durable SUBSCRIPTION KEY; `selected_spell_id` is a
          moving pointer refreshed as the owner notches.
        - A version change updates that pointer in place - the contract surface
          is never rewritten and no re-grant is required.
        - `sources` reference-counts justification exactly as `Detail` does.

    Threading:
        One instance `RLock`. Mutated through the owning `ConduitWard`, so lock
        order runs ward -> contract -> detail.

    Registration:
        MELDER KERNEL - guarded. Authored by `ConduitWard` on index-link grants;
        users read contract state through ward verbs.

    Subsystem Context:
        The SUBSCRIPTION row of the ward contract model, paired with `Detail`
        (the version snapshot). A contract holds separate maps for the two: one
        keyed by spell_id, one by index_id.

    System Context:
        This row is what decouples cross-conduit sharing from version churn.
        Because the borrower follows the INDEX rather than a captured member,
        an owner can notch a lineage - repointing its active spell - and every
        peer sees the new head without any contract being renegotiated. The
        alternative, re-granting each borrowed lineage on every notch, would
        make version movement O(peers) and would race with in-flight
        resolution.
        `SpellIndex` identity is a ULID and immutable, which is precisely what
        makes it a safe durable key while the member it targets keeps moving;
        the record mirrors that split by snapshotting index MEMBERSHIP as its
        own twin (`SpellIndexCrystal`) rather than folding it into the spell.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Index-level contract entry stored inside a Contract. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "spell_index",
        "selected_spell_id",
        "permissions",
        "contract_type",
        "reason",
        "sources",
    ]

    def __init__(
            self,
            spell_index: SpellIndex,
            selected_spell_id: str,
            permissions: Permissions,
            contract_type: ContractTypes,
            reason: DetailReason = DetailReason.other,
            sources: Optional[Set[str]] = None,
    ) -> None:
        """
        Initialize an index-level contract detail.

        Args:
            spell_index: The contracted lineage (durable identity / map key source).
            selected_spell_id: The lineage's active member id at creation time.
            permissions: Permission granted to this lineage.
            contract_type: Direction of the grant from the owning ward's view.
            reason: Why this detail exists.
            sources: Optional root spell ids that currently justify this detail.

        Raises:
            TypeError: If any argument is not the expected type.

        Returns:
            None.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._id: str = IDBuilder.create_id()

        if not isinstance(spell_index, SpellIndex):
            raise TypeError(
                f"spell_index must be SpellIndex, got {type(spell_index).__name__}"
            )
        if not isinstance(permissions, Permissions):
            raise TypeError(
                f"permissions must be Permissions, got {type(permissions).__name__}"
            )
        if not isinstance(contract_type, ContractTypes):
            raise TypeError(
                f"contract_type must be ContractTypes, got {type(contract_type).__name__}"
            )
        if not isinstance(reason, DetailReason):
            raise TypeError(
                f"reason must be DetailReason, got {type(reason).__name__}"
            )
        if sources is not None and not isinstance(sources, set):
            raise TypeError(
                f"sources must be a set of spell_ids when provided, got {type(sources).__name__}"
            )

        self.spell_index: SpellIndex = spell_index
        self.selected_spell_id: str = selected_spell_id
        self.permissions: Permissions = permissions
        self.contract_type: ContractTypes = contract_type
        self.reason: DetailReason = reason
        self.sources: Set[str] = sources if sources is not None else set()

    @property
    def index_id(self) -> str:
        """
        Stable id of the contracted index -- the key this detail is stored under.
        """
        self.check_cleaned()
        return self.spell_index.id

    def update_selected(self, spell_id: str) -> None:
        """
        Repoint the subscription to the lineage's new active member.

        Called when the owner notches the index, so the contract entry persists and
        only its current-head pointer moves.

        Args:
            spell_id: The lineage's new active member id.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.selected_spell_id = spell_id

    def cleanup(self) -> None:
        """
        Idempotently clear index-contract metadata and mark this detail cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self.spell_index
            del self.selected_spell_id
            del self.permissions
            del self.contract_type
            del self.reason
            if self.sources is not None:
                self.sources.clear()
            del self.sources
            del self._id

    def has_spell(self, spell_id: str) -> bool:
        """
        Check whether the contracted lineage contains a specific version SHA.

        Args:
            spell_id: SHA fingerprint to check within the index member set.

        Returns:
            bool: True if the lineage advertises the version, else False.
        """
        self.check_cleaned()
        member_ids = self.spell_index._spells_in_index
        if not member_ids:
            return False
        return spell_id in member_ids

    def add_source(self, root_spell_id: str) -> None:
        """
        Record that one root spell id currently justifies this index detail.

        Purpose:
            Index details live only while at least one root spell still
            references them; this adds one justification (the source-counting
            half of the `add_source`/`remove_source` pair that governs detail
            lifetime).

        Contract:
            - Serialized by the detail instance lock.
            - A None `root_spell_id` is silently ignored (no-op).
            - The backing `sources` set is created lazily on first add.
            - Idempotent per id: re-adding a present source is a set no-op.

        Args:
            root_spell_id:
                Root spell id now justifying this detail; None is ignored.

        Returns:
            None.

        Threading:
            Holds the detail lock; safe against concurrent add/remove on the
            same detail.
        """
        self.check_cleaned()
        if root_spell_id is None:
            return
        with self._lock:
            if self.sources is None:
                self.sources = set()
            self.sources.add(root_spell_id)

    def remove_source(self, root_spell_id: str) -> bool:
        """
        Remove one root spell id source from this index detail.

        Returns:
            bool: True when the source set becomes empty and the caller should
                delete the detail entirely.
        """
        self.check_cleaned()
        if root_spell_id is None or self.sources is None:
            return False
        with self._lock:
            self.sources.discard(root_spell_id)
            return len(self.sources) == 0
