

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class PersistenceCrystal(Cleanable):
    """
    One sealed checkpoint: the snapshot artifact of a profile's segment.

    Purpose:
        Capture everything that happened in one profile since its previous
        checkpoint, as fully detached plain-value payloads. A PersistenceCrystal
        maps to persistence the way a SpellCrystal maps to a spell: it is a
        manifest-style artifact that can be turned into a cached item and
        saved, and the in-memory instance can be wiped once cached because
        `from_cached_item` rehydrates it completely.

    Contract:
        - Plain data from birth: no live twin references, no locks, no
          callables. Immune to later replace-on-emit cleanup by construction.
        - Incremental at the world level (only identities journaled inside
          the capture window appear); full objects at the twin level (each
          payload is the complete final state of that unit in the window).
        - Composing a world at checkpoint K = fold the profile's checkpoint
          chain 1..K, later payloads winning per (kind, key).
        - Immutable after construction.

    Threading:
        Immutable-after-init; safe to share across threads without locking.

    Lifecycle:
        Owned by exactly one PersistenceSystem ledger entry. `cleanup()`
        (= wipe) deletes owned fields; idempotent; reload via
        `from_cached_item` when the cached form was stored.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_profile_name",
        "_checkpoint_number",
        "_created_at",
        "_description",
        "_journal_segment",
        "_captured_payloads",
        "_sequence_range",
    ]

    def __init__(
            self,
            checkpoint_id: str,
            profile_name: str,
            checkpoint_number: int,
            description: Optional[str],
            journal_segment: List[Tuple[int, str, str]],
            captured_payloads: Dict[str, Dict[str, Dict[str, object]]],
            sequence_range: Tuple[int, int],
            created_at: Optional[str] = None,
    ) -> None:
        """
        Initialize one sealed checkpoint from a captured profile segment.

        Args:
            checkpoint_id:
                ULID identity (time-ordered) minted by the persistence system.
            profile_name:
                Profile this checkpoint was cut from.
            checkpoint_number:
                Per-profile monotonic checkpoint counter (1-based).
            description:
                Optional caller note.
            journal_segment:
                The (sequence, kind, key) journal entries inside the capture
                window, in emission order.
            captured_payloads:
                Detached twin payloads by kind -> key -> payload.
            sequence_range:
                (first_sequence, last_sequence) of the capture window.
            created_at:
                ISO-8601 creation stamp; None mints now (UTC). Supplied only
                by `from_cached_item` rehydration.

        Returns:
            None.

        Raises:
            ValueError:
                If `checkpoint_id` / `profile_name` is empty or
                `checkpoint_number` < 1.
        """
        super().__init__()
        if not checkpoint_id:
            raise ValueError("PersistenceCrystal requires a non-empty checkpoint_id.")
        if not profile_name:
            raise ValueError("PersistenceCrystal requires a non-empty profile_name.")
        if checkpoint_number < 1:
            raise ValueError(
                "checkpoint_number is 1-based; got {0}.".format(checkpoint_number)
            )
        self._id: str = checkpoint_id
        self._profile_name: str = profile_name
        self._checkpoint_number: int = checkpoint_number
        self._created_at: str = (
            created_at
            if created_at is not None
            else datetime.now(timezone.utc).isoformat()
        )
        self._description: Optional[str] = description
        self._journal_segment: List[Tuple[int, str, str]] = [
            (int(sequence), str(kind), str(key))
            for sequence, kind, key in journal_segment
        ]
        self._captured_payloads: Dict[str, Dict[str, Dict[str, object]]] = {
            kind: {key: dict(payload) for key, payload in by_key.items()}
            for kind, by_key in captured_payloads.items()
        }
        self._sequence_range: Tuple[int, int] = (
            int(sequence_range[0]),
            int(sequence_range[1]),
        )

    def cleanup(self) -> None:
        """
        Wipe the in-memory snapshot and mark it cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).
            - Wiping is safe once the cached form exists elsewhere; reload
              via `from_cached_item`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._id
        del self._profile_name
        del self._checkpoint_number
        del self._created_at
        del self._description
        del self._journal_segment
        del self._captured_payloads
        del self._sequence_range

    @property
    def id(self) -> str:
        """
        Return the checkpoint's ULID identity (lexicographic = chronological).

        Returns:
            str:
                ULID checkpoint id.
        """
        self.check_cleaned()
        return self._id

    @property
    def profile_name(self) -> str:
        """
        Return the profile this checkpoint was cut from.

        Returns:
            str:
                Source profile name.
        """
        self.check_cleaned()
        return self._profile_name

    @property
    def checkpoint_number(self) -> int:
        """
        Return the per-profile checkpoint counter (1-based).

        Returns:
            int:
                Position of this checkpoint in its profile's chain.
        """
        self.check_cleaned()
        return self._checkpoint_number

    @property
    def created_at(self) -> str:
        """
        Return the ISO-8601 UTC creation stamp.

        Returns:
            str:
                Creation time.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def description(self) -> Optional[str]:
        """
        Return the caller note recorded at seal time.

        Returns:
            Optional[str]:
                Description, or None.
        """
        self.check_cleaned()
        return self._description

    @property
    def sequence_range(self) -> Tuple[int, int]:
        """
        Return the (first, last) journal-sequence window this seal captured.

        Returns:
            Tuple[int, int]:
                Capture window bounds.
        """
        self.check_cleaned()
        return self._sequence_range

    def describe(self) -> Dict[str, object]:
        """
        Return the checkpoint's detached metadata summary (ledger view).

        Returns:
            Dict[str, object]:
                Metadata + per-kind capture counts; twin_custody is
                "captured" (this seal holds real detached payloads).
        """
        self.check_cleaned()
        return {
            "checkpoint_id": self._id,
            "profile_name": self._profile_name,
            "checkpoint_number": self._checkpoint_number,
            "created_at": self._created_at,
            "description": self._description,
            "sequence_range": list(self._sequence_range),
            "journal_entry_count": len(self._journal_segment),
            "captured_counts": {
                kind: len(by_key)
                for kind, by_key in self._captured_payloads.items()
            },
            "twin_custody": "captured",
        }

    def to_cached_item(self) -> Dict[str, object]:
        """
        Return the checkpoint's complete cached-item form.

        Purpose:
            The serialization mapping (the SpellCrystal "bytecode" analogy):
            everything needed to rehydrate this crystal via
            `from_cached_item`, as one plain-value payload.

        Returns:
            Dict[str, object]:
                Full detached payload (metadata + journal segment + captured
                twin payloads).
        """
        self.check_cleaned()
        return {
            "checkpoint_id": self._id,
            "profile_name": self._profile_name,
            "checkpoint_number": self._checkpoint_number,
            "created_at": self._created_at,
            "description": self._description,
            "sequence_range": list(self._sequence_range),
            "journal_segment": [
                [sequence, kind, key]
                for sequence, kind, key in self._journal_segment
            ],
            "captured_payloads": {
                kind: {key: dict(payload) for key, payload in by_key.items()}
                for kind, by_key in self._captured_payloads.items()
            },
        }

    @classmethod
    def from_cached_item(cls, cached_item: Dict[str, object]) -> "PersistenceCrystal":
        """
        Rehydrate one PersistenceCrystal from its cached-item form.

        Args:
            cached_item:
                Payload previously produced by `to_cached_item`.

        Returns:
            PersistenceCrystal:
                Live snapshot artifact equivalent to the sealed original.

        Raises:
            KeyError:
                If required cached-item fields are missing.
            ValueError:
                If field values violate the construction contract.
        """
        journal = [
            (int(entry[0]), str(entry[1]), str(entry[2]))
            for entry in cached_item["journal_segment"]
        ]
        sequence_range = cached_item["sequence_range"]
        return cls(
            checkpoint_id=str(cached_item["checkpoint_id"]),
            profile_name=str(cached_item["profile_name"]),
            checkpoint_number=int(cached_item["checkpoint_number"]),
            description=cached_item["description"],
            journal_segment=journal,
            captured_payloads=cached_item["captured_payloads"],
            sequence_range=(int(sequence_range[0]), int(sequence_range[1])),
            created_at=str(cached_item["created_at"]),
        )
