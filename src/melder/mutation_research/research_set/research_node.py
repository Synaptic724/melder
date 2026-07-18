import copy
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

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
            - Idempotent; del posture (no tombstones).
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

        Returns:
            Dict[str, object]:
                Detached metadata mapping.
        """
        self.check_cleaned()
        return copy.deepcopy(self._metadata)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this node.

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
