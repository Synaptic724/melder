from typing import Dict, Iterable, Mapping, Optional

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.existence.existence import Existence
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class SpellSystemIndex(Cleanable):
    """
    Internal

    Version-id keyed system index for a frame (Phase 5+).

    This is the system-level mirror of the deep DAG structure described by
    RootResolutionBlueprints. It is intentionally small:

        * nodes: spell_id (version) -> SpellSystemNode

    Phase 5 builds this while assembling deep DAGs.
    Phase 6 consumes it for system-level validation.
    Phase 7 uses it for change-control / impact analysis.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_nodes"]

    def __init__(self) -> None:
        """
        Initialize an empty frame-level spell system index.

        Contract:
            Starts with no registered system nodes and owns the node mapping for
            the life of the index.
        """
        super().__init__()
        self._nodes: Dict[str, SpellSystemNode] = {}


    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down the index and its nodes.
        """
        if self._cleaned:
            return

        self._cleaned = True
        for node in self._nodes.values():
            node.cleanup()
        self._nodes.clear()

        del self._nodes


    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def nodes(self) -> Mapping[str, SpellSystemNode]:
        """
        Read-only mapping view: spell_id -> SpellSystemNode.
        """
        self.check_cleaned()
        return self._nodes

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    def get_node(self, spell_id: str) -> Optional[SpellSystemNode]:
        """
        Retrieve an existing node by version id, if present.
        """
        self.check_cleaned()
        if spell_id is None:
            raise ValueError("spell_id must not be None.")
        return self._nodes.get(spell_id)

    def upsert_node(self, node: SpellSystemNode) -> SpellSystemNode:
        """
        Register or replace a SpellSystemNode instance.

        Returns:
            The node that ended up in the index (same instance as input).
        """
        self.check_cleaned()
        if node is None:
            raise ValueError("node must not be None.")
        spell_id = node.spell_id
        self._nodes[spell_id] = node
        return node

    def ensure_node(
            self,
            spell_id: str,
            lineage_id: str,
            *,
            dependencies: Optional[Iterable[str]] = None,
            existence: Optional[Existence] = None,
            spell_type: Optional[SpellType] = None,
            conduit_id: Optional[str] = None,
            ward_id: Optional[str] = None,
            is_root: bool = False,
    ) -> SpellSystemNode:
        """
        Convenience helper used by Phase 5:

        - If a node for `spell_id` already exists:
              * dependencies are unioned in.
              * metadata fields are updated when non-None.
        - Otherwise a new node is created and registered.
        """
        self.check_cleaned()

        if spell_id is None:
            raise ValueError("spell_id must not be None.")
        if lineage_id is None:
            raise ValueError("lineage_id must not be None.")

        existing = self._nodes.get(spell_id)
        if existing is not None:
            if dependencies:
                existing.add_dependencies(dependencies)
            if existence is not None:
                existing.existence = existence
            if spell_type is not None:
                existing.spell_type = spell_type
            if conduit_id is not None:
                existing.conduit_id = conduit_id
            if ward_id is not None:
                existing.ward_id = ward_id
            if is_root:
                existing.is_root = True
            return existing

        node = SpellSystemNode(
            spell_id=spell_id,
            lineage_id=lineage_id,
            dependencies=dependencies,
            existence=existence,
            spell_type=spell_type,
            conduit_id=conduit_id,
            ward_id=ward_id,
            is_root=is_root,
        )
        self._nodes[spell_id] = node
        return node

    def iter_nodes(self) -> Iterable[SpellSystemNode]:
        """
        Snapshot of all nodes. The list is detached from internal storage.
        """
        self.check_cleaned()
        return list(self._nodes.values())
