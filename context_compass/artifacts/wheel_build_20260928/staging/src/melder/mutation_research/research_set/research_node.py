import copy
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, ClassVar

from melder.utilities.general_base.cleanable import Cleanable


class ResearchNode(Cleanable):
    """
    One immutable version record inside a research lane.

    Purpose:
        Formally declare that one bound version (a full object, never a diff)
        is part of research. The node is reference-based: it pins NO source
        payload, because custody lives with the crystallizer - the spell's
        binding-signature SHA256 is simultaneously the `SpellCrystal` id
        (`SpellCrystal.__init__` adopts `spell.spell_id` as its manifest id),
        so `spell_id` alone is the custody key.

    Contract:
        - Value object; immutable after construction (no setters, no lock).
        - `spell_id` is REQUIRED and is both the version identity and the
          custody-crystal reference (one field, one truth).
        - `module_source_sha256` carries the module-version SHA256 the spell was bound
          against, so recall can never resurrect a spell into the wrong
          module world.
        - `parent_spell_ids` is ancestry only; multi-parent records express
          composition performed in the codegen workshop (there is no
          merge/rebase machinery to reference).
        - `describe()` returns the detached serialization-ready payload;
          `from_payload()` is its exact inverse.

    Threading:
        Immutable-after-init; safe to share across threads without locking.

    Lifecycle:
        Owned by exactly one `ResearchLane` at a time (single-residence
        invariant); `cleanup()` deletes owned fields; idempotent.

    Registration:
        MELDER KERNEL - guarded. A version record is the record's own bookkeeping;
        users declare research through `ResearchSet` verbs rather than
        constructing nodes.

    Subsystem Context:
        The spell-grain node type of the ResearchSet package, and the sibling of
        `GroupedResearchNode` - which is a deliberately SEPARATE node type for
        compositions rather than an optional field on this one. A lane holds
        either kind, dispatching through the module-level identity helper. This
        one records "a spell version entered the world"; the other records "a
        set of spells was pinned together".

    System Context:
        The join point between research and custody. Because a spell's
        binding-signature SHA256 IS its `SpellCrystal` id, `spell_id` alone
        reaches the crystallizer's recorded material - which is why a node can
        stay purely referential and still support source, diff, and impact
        reads. Nodes are minted from the Spellbook's bind and notch confirmation
        points while the research root is active.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. One immutable version record inside a research lane. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_spell_id",
        "_module_source_sha256",
        "_parent_spell_ids",
        "_author",
        "_reason",
        "_campaign",
        "_created_at",
        "_metadata",
    ]

    def __init__(
            self,
            spell_id: str,
            *,
            module_source_sha256: Optional[str] = None,
            parent_spell_ids: Optional[List[str]] = None,
            author: Optional[str] = None,
            reason: Optional[str] = None,
            campaign: Optional[str] = None,
            created_at: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one immutable version record.

        Contract:
            - IMMUTABLE AFTER THIS RETURNS. There are no setters and no lock; the
              node's state is fixed at construction, which is what makes it safe
              to share across threads and hand out as a live read surface.
            - DEFENSIVE-COPIES ITS COLLECTIONS. `parent_spell_ids` is stored as a
              private tuple and `metadata` is `deepcopy`-ed on the way in, so a
              caller mutating the objects it passed cannot reach into the node
              afterwards.
            - `spell_id` is REQUIRED and does double duty: it is the version
              identity AND the custody-crystal reference, so an empty value is
              rejected up front.
            - EVERY parent sha is validated non-empty; a single empty entry
              raises rather than being silently dropped, because ancestry that
              silently loses a parent would corrupt the graph.
            - `created_at` is minted NOW only when omitted; a supplied stamp is
              kept verbatim, which is what lets `from_payload` round-trip the
              original creation time rather than stamping the rebuild.

        Threading:
            Construction is unsynchronized; the object is not shared until the
            owning lane publishes it, and it is immutable thereafter.

        Args:
            spell_id:
                Binding-signature SHA256 of the registered version; doubles as
                the custody `SpellCrystal` id.
            module_source_sha256:
                Optional module-version SHA256 the version was bound against.
            parent_spell_ids:
                Optional ancestry identities (detached copy is stored).
            author:
                Optional registering agent name.
            reason:
                Optional human/agent reason line.
            campaign:
                Optional research-campaign stamp.
            created_at:
                Optional ISO-8601 UTC stamp; minted now when omitted.
            metadata:
                Optional value-typed annotations (detached copy is stored).

        Raises:
            ValueError:
                If spell_id is empty or any parent sha is empty.

        Returns:
            None.
        """
        super().__init__()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        parents: List[str] = list(parent_spell_ids) if parent_spell_ids else []
        for parent_sha in parents:
            if not isinstance(parent_sha, str) or not parent_sha:
                raise ValueError("parent_spell_ids must contain non-empty strings.")
        self._spell_id: str = spell_id
        self._module_source_sha256: Optional[str] = module_source_sha256
        self._parent_spell_ids: Tuple[str, ...] = tuple(parents)
        self._author: Optional[str] = author
        self._reason: Optional[str] = reason
        self._campaign: Optional[str] = campaign
        self._created_at: str = (
            created_at
            if created_at
            else datetime.now(timezone.utc).isoformat()
        )
        self._metadata: Dict[str, object] = copy.deepcopy(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Release owned fields and mark the node cleaned.

        Contract:
            - IDEMPOTENT: a second call returns immediately on the `_cleaned`
              flag. Unlike the lane and set, there is NO lock here - the node is
              immutable and single-residence, so cleanup is only ever driven by
              its one owning lane, never concurrently.
            - DELETE-NOT-NULL: owned fields are removed with `del`, leaving no
              tombstones, so any post-cleanup access raises `AttributeError`
              through `check_cleaned()` rather than returning stale data.
            - Owns no children and no external resources, so there is no cascade
              and no ordering concern - it drops its own value fields only.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spell_id
        del self._module_source_sha256
        del self._parent_spell_ids
        del self._author
        del self._reason
        del self._campaign
        del self._created_at
        del self._metadata

    @property
    def spell_id(self) -> str:
        """
        Return the version identity (and custody-crystal id).

        Contract:
            - ONE VALUE, TWO ROLES: this is both the research identity and the
              custody `SpellCrystal` id, so it is the single key that reaches the
              crystallizer's recorded material for this version.
            - Always present and non-empty; the constructor guarantees it.

        Returns:
            str:
                Binding-signature SHA256.
        """
        self.check_cleaned()
        return self._spell_id

    @property
    def module_source_sha256(self) -> Optional[str]:
        """
        Return the module-version SHA256 this version binds against.

        Contract:
            - `None` means UNRECORDED, not "no module" - the version may still
              have a module world; its source SHA simply was not captured.
            - When present, this is what prevents recall from resurrecting the
              spell into the wrong module version.

        Returns:
            Optional[str]:
                Module-version SHA256 or None when unrecorded.
        """
        self.check_cleaned()
        return self._module_source_sha256

    @property
    def parent_spell_ids(self) -> List[str]:
        """
        Return a detached copy of the ancestry identities.

        Contract:
            - A FRESH LIST each call, built from the private tuple, so mutating
              the result cannot alter the node's ancestry.
            - Declaration order is preserved. An empty list means a ROOT version
              (no ancestry); more than one entry means a composition performed in
              the codegen workshop - there is no merge/rebase machinery, so
              multi-parent is always a deliberate composition record.

        Returns:
            List[str]:
                Parent SHA256 identities in declaration order.
        """
        self.check_cleaned()
        return list(self._parent_spell_ids)

    @property
    def author(self) -> Optional[str]:
        """
        Return the registering agent name, when recorded.

        Contract:
            - `None` means the registering verb supplied no author; it is an
              optional annotation, never inferred.

        Returns:
            Optional[str]:
                Author name or None.
        """
        self.check_cleaned()
        return self._author

    @property
    def reason(self) -> Optional[str]:
        """
        Return the recorded reason line, when one exists.

        Contract:
            - `None` means no reason was supplied at registration; free-text
              annotation only, never parsed or acted on.

        Returns:
            Optional[str]:
                Reason text or None.
        """
        self.check_cleaned()
        return self._reason

    @property
    def campaign(self) -> Optional[str]:
        """
        Return the research-campaign stamp, when recorded.

        Contract:
            - `None` means the version was declared outside any campaign, or the
              ambient campaign was clear at registration. Campaign is intent
              stamped ACROSS lanes; a node carries at most the one it was
              registered under.

        Returns:
            Optional[str]:
                Campaign stamp or None.
        """
        self.check_cleaned()
        return self._campaign

    @property
    def created_at(self) -> str:
        """
        Return the ISO-8601 UTC creation stamp.

        Contract:
            - ALWAYS present (never None): minted at construction when not
              supplied. On a rebuilt node it is the ORIGINAL recorded time, not
              the rebuild time, because `from_payload` passes the stored stamp
              straight through.

        Returns:
            str:
                Creation timestamp.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached copy of the value-typed annotations.

        Contract:
            - DEEP-COPIED on the way out, mirroring the deep copy on the way in,
              so neither the caller's original nor the returned dict can mutate
              the node's stored metadata. Nested containers are safe to modify.
            - Empty dict (never None) when no annotations were supplied.

        Returns:
            Dict[str, object]:
                Detached metadata mapping.
        """
        self.check_cleaned()
        return copy.deepcopy(self._metadata)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this node.

        Contract:
            - THE EXACT INVERSE of `from_payload()`: the eight keys it emits are
              precisely the ones `from_payload` reads, so a node round-trips
              losslessly through describe -> from_payload, including its original
              `created_at`.
            - Fully DETACHED: `parent_spell_ids` is copied to a list and
              `metadata` is deep-copied, so mutating the returned payload cannot
              reach back into the node.
            - PLAIN-VALUE THROUGHOUT (str/None/list/dict), so it crosses a JSON
              persistence boundary without custom encoding.

        Returns:
            Dict[str, object]:
                Plain-value payload (exact `from_payload()` inverse).
        """
        self.check_cleaned()
        return {
            "spell_id": self._spell_id,
            "module_source_sha256": self._module_source_sha256,
            "parent_spell_ids": list(self._parent_spell_ids),
            "author": self._author,
            "reason": self._reason,
            "campaign": self._campaign,
            "created_at": self._created_at,
            "metadata": copy.deepcopy(self._metadata),
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "ResearchNode":
        """
        Rebuild one node from a `describe()` payload.

        Contract:
            - `spell_id` IS THE ONLY HARD REQUIREMENT. A missing or empty
              `spell_id` raises `ValueError`; every other field is optional and
              defaults exactly as the constructor does when absent.
            - TOLERANT OF WRONG-TYPED OPTIONALS. A `parent_spell_ids` or
              `metadata` value that is not a list/dict is treated as absent
              rather than raising, so a partially-corrupt payload still yields a
              valid node instead of failing the whole rebuild.
            - PRESERVES the recorded `created_at`, so the rebuilt node reports
              its original creation time, not the rebuild time.
            - Runs the constructor's full validation, so an empty parent sha in
              the payload is still rejected - `from_payload` cannot smuggle in a
              node the constructor would refuse.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            ResearchNode:
                Reconstructed immutable node.

        Raises:
            ValueError:
                If required keys are missing or invalid.
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        spell_id = payload.get("spell_id")
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("payload is missing a valid 'spell_id' value.")
        parents = payload.get("parent_spell_ids")
        metadata = payload.get("metadata")
        return cls(
            spell_id,
            module_source_sha256=payload.get("module_source_sha256"),
            parent_spell_ids=list(parents) if isinstance(parents, list) else None,
            author=payload.get("author"),
            reason=payload.get("reason"),
            campaign=payload.get("campaign"),
            created_at=payload.get("created_at"),
            metadata=metadata if isinstance(metadata, dict) else None,
        )
