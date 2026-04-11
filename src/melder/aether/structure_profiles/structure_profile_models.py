from typing import Any, Dict, List, Optional, Sequence, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.helpers.id_builder import IDBuilder


class StructureHint(Cleanable):
    """
    Tooling hint derived from structure profiles.

    Purpose:
        Represent a derived observation with provenance and confidence, suitable
        for UI/AI tooling while remaining separate from truth data.

    Contract:
        - `confidence` is a float in [0.0, 1.0].
        - `provenance` describes the source and method used to derive the hint.
        - cleanup() is idempotent and clears all references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "kind",
        "description",
        "confidence",
        "provenance",
        "scope",
        "_id"

    ]

    def __init__(
            self,
            *,
            kind: str,
            description: str,
            confidence: float,
            provenance: Optional[Dict[str, Any]] = None,
            scope: Optional[str] = None,
    ) -> None:
        """
        Initialize a StructureHint.

        Args:
            kind: Hint category identifier.
            description: Human-readable hint description.
            confidence: Confidence score in [0.0, 1.0].
            provenance: Optional provenance payload describing source/method.
            scope: Optional scope tag (frame/conduit/spellbook/spell).
        Contract:
            - Stores only derived metadata, never truth data.
            - Copies provenance mappings so callers cannot retain live aliases.
        Raises:
            ValueError: If `confidence` is outside `[0.0, 1.0]`.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        if confidence < 0.0 or confidence > 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        self.kind = kind
        self.description = description
        self.confidence = confidence
        self.provenance = dict(provenance) if provenance is not None else {}
        self.scope = scope

    def cleanup(self) -> None:
        """
        Idempotently clear hint fields.

        Contract:
            Safe to call more than once.
        """
        if self._cleaned:
            return
        self.kind = None
        self.description = None
        self.confidence = None
        self.provenance = None
        self.scope = None
        self._cleaned = True


class SpellStructureRecord(Cleanable):
    """
    Structure snapshot for a single spell lineage/version.

    Purpose:
        Provide a tool-friendly view of a spell's structural truth data
        (dependencies, sockets, identifiers) plus derived hints.

    Contract:
        - `dependencies` and `sockets` are truth data (no derivation).
        - `derived_hints` contains derived observations with provenance.
        - cleanup() is idempotent and clears all references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "spell_id",
        "lineage_id",
        "owner_conduit_id",
        "binding_key",
        "existence",
        "spell_type",
        "permissions",
        "dependencies",
        "sockets",
        "spellmap_defaults",
        "derived_hints",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            lineage_id: str,
            owner_conduit_id: Optional[str],
            binding_key: Optional[Tuple[str, str]],
            existence: Optional[str],
            spell_type: Optional[str],
            permissions: Optional[str],
            dependencies: Dict[str, List[str]],
            sockets: List[Dict[str, Any]],
            spellmap_defaults: Optional[List[Dict[str, Any]]] = None,
            derived_hints: Optional[Sequence[StructureHint]] = None,
    ) -> None:
        """
        Initialize a SpellStructureRecord.

        Args:
            spell_id: Current version id for the spell.
            lineage_id: Lineage id (SpellIndex.id).
            owner_conduit_id: Owning conduit id when known.
            binding_key: Tuple of (frame_key, binding_key) when known.
            existence: String representation of the Existence enum.
            spell_type: String representation of the SpellType enum.
            permissions: String representation of the Permissions enum.
            dependencies: Mapping of dependency kinds to spell ids.
            sockets: List of socket dictionaries from SpellLocalTopology.
            spellmap_defaults: Optional list of SpellMap default payloads.
            derived_hints: Optional list of derived StructureHint entries.
        Contract:
            - Copies all mutable list/dict inputs so the record becomes a
              stable snapshot.
            - Treats `dependencies` and `sockets` as truth data and
              `derived_hints` as derived observations.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self.spell_id = spell_id
        self.lineage_id = lineage_id
        self.owner_conduit_id = owner_conduit_id
        self.binding_key = binding_key
        self.existence = existence
        self.spell_type = spell_type
        self.permissions = permissions
        self.dependencies = dict(dependencies)
        self.sockets = list(sockets)
        self.spellmap_defaults = list(spellmap_defaults) if spellmap_defaults is not None else []
        self.derived_hints = list(derived_hints) if derived_hints is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear record fields and nested hints.

        Contract:
            - Best-effort cleans nested hints first.
            - Clears copied dependency/socket/default collections before
              dropping references.
        """
        if self._cleaned:
            return
        for hint in self.derived_hints:
            if isinstance(hint, Cleanable):
                try:
                    hint.cleanup()
                except Exception:
                    pass
        if isinstance(self.dependencies, dict):
            self.dependencies.clear()
        if isinstance(self.sockets, list):
            self.sockets.clear()
        if isinstance(self.spellmap_defaults, list):
            self.spellmap_defaults.clear()
        self.spell_id = None
        self.lineage_id = None
        self.owner_conduit_id = None
        self.binding_key = None
        self.existence = None
        self.spell_type = None
        self.permissions = None
        self.dependencies = None
        self.sockets = None
        self.spellmap_defaults = None
        self.derived_hints = None
        self._cleaned = True


class ConduitStructureProfile(Cleanable):
    """
    Structure snapshot for a single conduit.

    Purpose:
        Capture conduit metadata, spell inventory, and derived hints for
        tooling and diagnostics.

    Contract:
        - spell_records is a mapping of spell_id to SpellStructureRecord.
        - cleanup() is idempotent and clears all references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "conduit_id",
        "conduit_name",
        "conduit_state",
        "dynamic_environment",
        "aetheric_frame",
        "spell_records",
        "derived_hints",

    ]

    def __init__(
            self,
            *,
            conduit_id: str,
            conduit_name: str,
            conduit_state: str,
            dynamic_environment: Optional[bool],
            aetheric_frame: Optional[str],
            spell_records: Dict[str, SpellStructureRecord],
            derived_hints: Optional[Sequence[StructureHint]] = None,
    ) -> None:
        """
        Initialize a ConduitStructureProfile.

        Args:
            conduit_id: Conduit identifier.
            conduit_name: Conduit name.
            conduit_state: String representation of ConduitState.
            dynamic_environment: Whether the conduit is dynamic.
            aetheric_frame: Frame name the conduit belongs to.
            spell_records: Mapping of spell_id to SpellStructureRecord.
            derived_hints: Optional list of derived StructureHint entries.
        Contract:
            - Copies the spell-record mapping so the profile is snapshot-shaped.
            - Stores derived hints separately from truth data.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self.conduit_id = conduit_id
        self.conduit_name = conduit_name
        self.conduit_state = conduit_state
        self.dynamic_environment = dynamic_environment
        self.aetheric_frame = aetheric_frame
        self.spell_records = dict(spell_records)
        self.derived_hints = list(derived_hints) if derived_hints is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear conduit profile fields and nested records.

        Contract:
            - Best-effort cleans nested spell records and hints first.
            - Clears copied record mappings before dropping references.
        """
        if self._cleaned:
            return
        for record in self.spell_records.values():
            if isinstance(record, Cleanable):
                try:
                    record.cleanup()
                except Exception:
                    pass
        for hint in self.derived_hints:
            if isinstance(hint, Cleanable):
                try:
                    hint.cleanup()
                except Exception:
                    pass
        if isinstance(self.spell_records, dict):
            self.spell_records.clear()
        self.conduit_id = None
        self.conduit_name = None
        self.conduit_state = None
        self.dynamic_environment = None
        self.aetheric_frame = None
        self.spell_records = None
        self.derived_hints = None
        self._cleaned = True


class FrameStructureProfile(Cleanable):
    """
    Structure snapshot for an Aetheric frame.

    Purpose:
        Aggregate conduit profiles, cluster membership, and spell inventory
        for tooling and diagnostics.

    Contract:
        - `conduit_profiles` maps conduit_id to ConduitStructureProfile.
        - `spell_records` maps spell_id to SpellStructureRecord.
        - cleanup() is idempotent and clears all references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "frame_id",
        "frame_name",
        "conduit_profiles",
        "spell_records",
        "clusters",
        "max_related",
        "derived_hints",
    ]

    def __init__(
            self,
            *,
            frame_id: str,
            frame_name: str,
            conduit_profiles: Dict[str, ConduitStructureProfile],
            spell_records: Dict[str, SpellStructureRecord],
            clusters: List[Dict[str, Any]],
            max_related: Optional[int] = None,
            derived_hints: Optional[Sequence[StructureHint]] = None,
    ) -> None:
        """
        Initialize a FrameStructureProfile.

        Args:
            frame_id: Frame identifier.
            frame_name: Frame name.
            conduit_profiles: Mapping of conduit_id to ConduitStructureProfile.
            spell_records: Mapping of spell_id to SpellStructureRecord.
            clusters: Cluster summaries for the frame.
            max_related: Default limit for related-spell queries.
            derived_hints: Optional list of derived StructureHint entries.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self.frame_id = frame_id
        self.frame_name = frame_name
        self.conduit_profiles = dict(conduit_profiles)
        self.spell_records = dict(spell_records)
        self.clusters = list(clusters)
        self.max_related = max_related
        self.derived_hints = list(derived_hints) if derived_hints is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear frame profile fields and nested records.
        """
        if self._cleaned:
            return
        for conduit in self.conduit_profiles.values():
            if isinstance(conduit, Cleanable):
                try:
                    conduit.cleanup()
                except Exception:
                    pass
        for record in self.spell_records.values():
            if isinstance(record, Cleanable):
                try:
                    record.cleanup()
                except Exception:
                    pass
        for hint in self.derived_hints:
            if isinstance(hint, Cleanable):
                try:
                    hint.cleanup()
                except Exception:
                    pass
        if isinstance(self.conduit_profiles, dict):
            self.conduit_profiles.clear()
        if isinstance(self.spell_records, dict):
            self.spell_records.clear()
        if isinstance(self.clusters, list):
            self.clusters.clear()
        self.frame_id = None
        self.frame_name = None
        self.conduit_profiles = None
        self.spell_records = None
        self.clusters = None
        self.max_related = None
        self.derived_hints = None
        self._cleaned = True
