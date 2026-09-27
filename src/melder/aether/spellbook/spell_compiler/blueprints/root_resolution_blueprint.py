from typing import List, Optional, Sequence, ClassVar



# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry

class RootResolutionBlueprint(Cleanable):
    """
    Phase 5 rooted deep-DAG artifact for one spell.

    This blueprint is the handoff object between structural spell compilation
    and the later system/planning phases. It does not discover dependencies or
    validate policy by itself; instead, it packages the rooted DAG, stable
    execution order, and the PathRegistry that Phase 8 mints root-relative path
    ids into, for system validation, change-control/component-of wiring, and
    Phase 8-10 planning. (The Phase-5 per-path socket overlay and its targeting
    index were retired on 2026-09-26; no reader needed them.)

    Contract:
        - `root_spell_id` is the versioned identity of the root spell at
          blueprint-build time.
        - `root_lineage_id` is optional lineage metadata for DevOps/change-
          control use; graph semantics remain version-id-based.
        - The blueprint owns its DAG and its PathRegistry.
        - Consumers should treat exposed list/index data as read-only, even
          when accessors return copies.
    """
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_root_lineage_id",
        "_dag",
        "_ordered_node_ids",
        "_requires_spellspace_request",
        "_path_registry",
    ]

    def __init__(
            self,
            root_spell_id: str,
            root_lineage_id: Optional[str],
            dag: DirectedAcyclicWorkGraph,
            ordered_node_ids: Optional[Sequence[str]] = None,
            requires_spellspace_request: bool = False,
            path_registry: Optional[PathRegistry] = None,
    ) -> None:
        """
        Initialize a rooted deep-DAG blueprint.

        Args:
            root_spell_id:
                Versioned spell id for the root node this blueprint represents.
            root_lineage_id:
                Optional lineage id for DevOps/change-control consumers.
            dag:
                Owned deep DAG for the root spell's reachable dependency
                closure.
            ordered_node_ids:
                Optional precomputed topological order. Dependencies should
                appear before the root.
            requires_spellspace_request:
                Whether the rooted graph contains spellspace-scoped work.
            path_registry:
                Optional PathRegistry to own. When omitted, a fresh one is
                allocated; Phase 8 mints occurrence paths into it.

        Contract:
            - `root_spell_id` and `dag` are required.
            - Sequence inputs are copied into blueprint-owned lists.
            - The blueprint always owns a non-None `PathRegistry`.
        """
        super().__init__()

        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if dag is None:
            raise ValueError("dag must not be None.")

        self._root_spell_id: str = root_spell_id
        self._root_lineage_id: Optional[str] = root_lineage_id
        self._dag: DirectedAcyclicWorkGraph = dag

        # Execution order: dependencies first, root last.
        self._ordered_node_ids: List[str] = list(ordered_node_ids) if ordered_node_ids else []
        self._requires_spellspace_request: bool = bool(requires_spellspace_request)

        # Root-relative path ids; Phase 8 mints occurrence paths into it.
        self._path_registry: PathRegistry = (
            path_registry if path_registry is not None else PathRegistry()
        )


    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down the blueprint and its heavy children.

        Behaviour:
            * Idempotent - safe to call multiple times.
            * Cleans up the DAG and the PathRegistry.
            * Drops references to node ids.

        Contract:
            Cleanup releases only blueprint-owned artifacts. It does not mutate
            the spell/runtime payload objects stored inside the DAG.
        """
        if self._cleaned:
            return

        self._cleaned = True

        if self._dag is not None:
            self._dag.cleanup()
        self._path_registry.cleanup()

        self._ordered_node_ids.clear()

        del self._ordered_node_ids
        del self._requires_spellspace_request
        del self._path_registry
        del self._dag
        del self._root_spell_id
        del self._root_lineage_id


    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def root_spell_id(self) -> str:
        """
        Return the versioned root spell id for this blueprint.
        """
        self.check_cleaned()
        return self._root_spell_id

    @property
    def root_lineage_id(self) -> Optional[str]:
        """
        Return the optional lineage id for the root spell.

        This value is metadata for DevOps/change-control consumers; execution
        and targeting are still key off `root_spell_id`.
        """
        self.check_cleaned()
        return self._root_lineage_id

    @property
    def dag(self) -> DirectedAcyclicWorkGraph:
        """
        Return the owned deep DAG for this root.

        The DAG nodes are keyed by spell version id and represent the full
        reachable dependency closure rooted at `root_spell_id`.
        """
        self.check_cleaned()
        return self._dag

    @property
    def ordered_node_ids(self) -> List[str]:
        """
        Return the stable topological order for this rooted DAG.

        Contract:
            Returns a copy of the stored order so callers cannot mutate the
            blueprint's internal list. Dependencies appear before the root.
        """
        self.check_cleaned()
        return list(self._ordered_node_ids)

    @property
    def requires_spellspace_request(self) -> bool:
        """
        Return whether this rooted request graph contains spellspace-scoped work.
        """
        self.check_cleaned()
        return self._requires_spellspace_request

    @property
    def path_registry(self) -> PathRegistry:
        """
        Return the PathRegistry that interns root-relative parameter paths for
        this blueprint.

        Contract:
            Phase 8 mints the path id of every occurrence below the root into
            this registry; the blueprint owns it and cleans it.
        """
        self.check_cleaned()
        return self._path_registry
