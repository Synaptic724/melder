from typing import Dict, List, Optional, Set, Tuple

from melder.utilities.general_base.cleanable import Cleanable

OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]


class SpellOccurrenceInstanceAnalysis(Cleanable):
    """
    Processor-owned occurrence instance/sharedness artifact.

    Purpose:
        Hold the instance-key, sharedness, and canonical-occurrence decisions
        derived from analyzer-owned occurrence graph data.
    """

    __slots__ = Cleanable.__slots__ + [
        "instance_keys_by_spell_id",
        "canonical_occurrences_by_spell_id",
        "root_instance_key",
        "shared_spell_ids",
        "unique_spell_count",
        "shared_spell_count",
        "instance_count",
    ]

    def __init__(
            self,
            *,
            instance_keys_by_spell_id: Dict[str, List[InstanceKey]],
            canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey],
            root_instance_key: InstanceKey,
            shared_spell_ids: Set[str],
    ) -> None:
        """
        Build one occurrence-instance artifact.

        Contract:
            Stores the four inputs by reference and derives three counts:
            `unique_spell_count` (distinct spells), `shared_spell_count`
            (shared spells), and `instance_count` (total instance keys).

        Args:
            instance_keys_by_spell_id:
                Per-spell list of instance keys (spell_name, occurrence-or-None).
            canonical_occurrences_by_spell_id:
                Chosen canonical occurrence key per spell.
            root_instance_key:
                Instance key of the root spell.
            shared_spell_ids:
                Ids of spells shared across more than one instance.

        Returns:
            None.
        """
        super().__init__()
        self.instance_keys_by_spell_id = instance_keys_by_spell_id
        self.canonical_occurrences_by_spell_id = canonical_occurrences_by_spell_id
        self.root_instance_key = root_instance_key
        self.shared_spell_ids = shared_spell_ids
        self.unique_spell_count = len(instance_keys_by_spell_id)
        self.shared_spell_count = len(shared_spell_ids)
        self.instance_count = sum(
            len(instance_keys)
            for instance_keys in instance_keys_by_spell_id.values()
        )

    def cleanup(self) -> None:
        """
        Deterministically release owned instance-analysis data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.instance_keys_by_spell_id.clear()
        self.canonical_occurrences_by_spell_id.clear()
        self.shared_spell_ids.clear()
        del self.instance_keys_by_spell_id
        del self.canonical_occurrences_by_spell_id
        del self.root_instance_key
        del self.shared_spell_ids
        del self.unique_spell_count
        del self.shared_spell_count
        del self.instance_count
