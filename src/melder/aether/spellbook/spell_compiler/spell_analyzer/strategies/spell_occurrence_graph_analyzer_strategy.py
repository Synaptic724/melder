import inspect
from annotationlib import Format
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_existence_occurrence_analysis import (
    SpellExistenceOccurrence,
    SpellExistenceOccurrenceAnalysis,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_occurrence_graph_analysis import (
    SpellOccurrenceGraphAnalysis,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


OccurrenceKey = Tuple[str, int]


class SpellOccurrenceGraphAnalyzerStrategy(SpellAnalyzerStrategy):
    """
    Build the occurrence-graph analysis artifact for one spell.

    Purpose:
        Own the graph-expansion stage of the occurrence analyzer directly.
        This strategy is the occurrence lane's structural foundation: it turns
        rooted blueprint truth plus live topology context into one explicit
        path-aware occurrence graph that later strategies can trust as already-
        expanded input.

    Contract:
        - Consumes `Spell`, the existing `SpellCompilerArtifact`, the owning
          Spellbook spell pool, Phase 5 rooted blueprint truth, and current
          spell-system topology state.
        - Publishes only:
          - `_occurrence_graph_analysis`
          - `_occurrence_analysis_fast_key`
          - `_occurrence_analysis_input_signature`
        - Owns:
          - shared-occurrence collapse decisions
          - occurrence graph expansion
          - ordered-node graph completion
          - topology and DAG fallback dependency expansion
          - SpellContract dependency edge insertion
          - mutation-override dependency rewrites
          - cheap graph-side metrics
        - Does not compute execution order, instance/sharedness, or contract
          payload analysis artifacts. Later strategies own those outputs.
        - Existing-creation roots no-op. Existing providers remain leaf
          occurrences in consumer graphs, with no constructor-contract scan.

    Threading:
        - Runs inside compiler-thread orchestration only.
        - Assumes upstream compiler coordination serializes artifact mutation
          for one spell during this analysis pass.

    Registration:
        MELDER KERNEL. A built-in analyzer strategy; registered, never bound.

    Subsystem Context:
        The occurrence lane's structural foundation in `spell_analyzer/strategies`:
        registered into `SpellAnalyzerStrategyBuilder` and invoked by
        `SpellAnalyzer.analyze_occurrence`.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline. It expands the graph
        but computes no execution order, instance/sharedness, or contract-payload
        analysis - later strategies own those.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-8 occurrence-graph builder strategy: turns Phase-5 rooted
        blueprint + live topology into a path-aware occurrence graph, publishing
        _occurrence_graph_analysis (+ fast_key + input_signature) onto SpellCompilerArtifact.
        Existing-creation roots no-op; existing dependencies remain leaf occurrences.
    """


    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable registry id for this occurrence strategy.
        """
        return "spell_occurrence_graph_analyzer"

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            analysis_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Build and publish the occurrence-graph analysis artifact.

        Purpose:
            Materialize one compiler-owned graph analysis object for the
            current spell so later occurrence strategies do not have to reopen
            blueprint traversal, dependency expansion, or collapse rules.

        Contract:
            - Validates that the artifact is live before any work begins.
            - Computes the graph-side fast key and input signature directly in
              this strategy instead of reaching back into old Phase 8 helper
              methods. The pool-wide rows (spell walk, topology, contracted
              routing, system state) are hashed ONCE per pass into a memoized
              digest (`_get_pool_digest`); each root keys and signs only its own
              blueprint rows plus that digest, so per-root key work is
              proportional to the root's blueprint, not to the spell pool.
            - Reads the retained analysis slot FIRST and compares key and
              signature only when an analysis is retained: phase 5's attach
              nulls the slot on every conjure pass, so the cold path never
              attempts a comparison that cannot succeed.
            - Replaces the prior graph artifact atomically and best-effort
              cleans the superseded analysis object.
            - Leaves order, instance, and contract artifacts untouched.

        Returns:
            None.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return

        spellbook = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceGraphAnalyzerStrategy requires a live owning Spellbook."
            )
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceGraphAnalyzerStrategy requires Phase 5 root blueprint truth."
            )
        # Pass-scoped reuse: the spell walk and the graph-shape rows are
        # identical for every spell analyzed in one pass (only the root-
        # specific blueprint rows differ), so both are memoized in the
        # shared `analysis_pass_cache` dict when one is supplied. The dict
        # dies with the pass units, so no invalidation protocol exists --
        # the same lifetime contract as the phase-3/phase-4 pass caches.
        shared_spell_walk = self._get_shared_spell_walk(
            spell_lookup=spellbook._spell_id_pool,
            analysis_pass_cache=analysis_pass_cache,
        )
        spell_rows = None if shared_spell_walk is None else shared_spell_walk[0]

        graph_shape = self._build_graph_shape_rows(
            spellbook=spellbook,
            spell_system_states=spell._spell_system_states,
            analysis_pass_cache=analysis_pass_cache,
        )
        # The pool-wide rows are identical for every root analyzed in one
        # pass, so they are hashed once into a pass-memoized digest; the root
        # then contributes only its own blueprint rows, built once and shared
        # by the fast key and the input signature (owner-approved C-A,
        # 2026-09-26).
        pool_digest = self._get_pool_digest(
            spell_rows=spell_rows,
            graph_shape=graph_shape,
            analysis_pass_cache=analysis_pass_cache,
        )
        root_rows = None
        if pool_digest is not None:
            root_rows = self._build_root_blueprint_rows(root_blueprint)
        fast_key = self._build_occurrence_graph_fast_key(
            root_blueprint=root_blueprint,
            root_rows=root_rows,
            pool_digest=pool_digest,
        )
        input_signature = self._build_occurrence_graph_input_signature(
            root_blueprint=root_blueprint,
            root_rows=root_rows,
            pool_digest=pool_digest,
        )
        # Analysis slot first: phase 5's attach nulls it on every conjure
        # pass, so the key comparison is only worth making when an analysis
        # is actually retained (warm JIT reuse and local reruns).
        if (
                artifact._occurrence_graph_analysis is not None
                and fast_key is not None
                and input_signature is not None
                and artifact._occurrence_analysis_fast_key == fast_key
                and artifact._occurrence_analysis_input_signature == input_signature
        ):
            return

        collapse_shared_occurrences = True
        occurrence_graph = self._build_occurrence_graph(
            dag=root_blueprint.dag,
            root_spell_id=root_blueprint.root_spell_id,
            collapse_shared_occurrences=collapse_shared_occurrences,
            spell_lookup=spellbook._spell_id_pool,
            spell_system_states=spell._spell_system_states,
            path_registry=root_blueprint.path_registry,
            spellbook=spellbook,
            root_blueprint=root_blueprint,
        )
        self._extend_occurrence_graph_with_ordered_nodes(
            occurrence_graph=occurrence_graph,
            ordered_node_ids=root_blueprint.ordered_node_ids,
            dag=root_blueprint.dag,
            collapse_shared_occurrences=collapse_shared_occurrences,
            spell_lookup=spellbook._spell_id_pool,
            spell_system_states=spell._spell_system_states,
            path_registry=root_blueprint.path_registry,
            spellbook=spellbook,
            root_blueprint=root_blueprint,
        )
        # Family selection must see the ROOT-VISIBLE spell set, not the whole
        # spellbook pool (owner finding 2026-07-12): filter the shared pool
        # walk down to the spell ids that actually appear in this root's
        # fully built occurrence graph before building the existence analysis.
        existence_occurrence_analysis = None
        if shared_spell_walk is not None:
            visible_spell_ids = {
                occurrence[0] for occurrence in occurrence_graph
            }
            existence_occurrence_analysis = self._build_existence_occurrence_analysis(
                root_spell_id=root_blueprint.root_spell_id,
                shared_spell_walk=shared_spell_walk,
                visible_spell_ids=visible_spell_ids,
            )
        graph_analysis = SpellOccurrenceGraphAnalysis(
            root_spell_id=root_blueprint.root_spell_id,
            occurrence_graph=occurrence_graph,
            path_registry=root_blueprint.path_registry,
            occurrence_count=len(occurrence_graph),
            edge_count=self._count_occurrence_edges(occurrence_graph),
            topology_dependency_count=self._count_topology_dependencies(
                spell_system_states=spell._spell_system_states,
                occurrence_graph=occurrence_graph,
            ),
            dag_fallback_dependency_count=self._count_dag_fallback_dependencies(
                spell_system_states=spell._spell_system_states,
                occurrence_graph=occurrence_graph,
            ),
            shared_collapse_enabled=collapse_shared_occurrences,
            existence_occurrence_analysis=existence_occurrence_analysis,
        )

        previous_graph = artifact._occurrence_graph_analysis
        artifact._occurrence_graph_analysis = graph_analysis
        artifact._occurrence_analysis_fast_key = fast_key
        artifact._occurrence_analysis_input_signature = input_signature
        self._cleanup_previous(previous_graph, graph_analysis)

    @staticmethod
    def _freeze_schema_value(value: Any) -> Any:
        """
        Normalize arbitrary values into deterministic schema-safe forms.

        Contract:
            - Preserves primitive scalar values.
            - Recursively normalizes composite values through the shared
              compiler execution helper.
            - Returns hashable deterministic rows suitable for signature input.
        """
        return SharedCompilerExecutions.freeze_phase11_schema_value(value)

    def _build_occurrence_graph_fast_key(
            self,
            *,
            root_blueprint: "RootResolutionBlueprint",
            root_rows: Optional[Tuple[Tuple[Any, ...], int]],
            pool_digest: Optional[str],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build a lightweight deterministic key for graph-analysis reuse.

        Contract:
            - Returns `None` when any input is unavailable (forces the rebuild
              path).
            - Key shape: `(root_spell_id, ordered_node_ids, id(path_registry),
              pool_digest)`. The root-specific rows are built once by the
              caller (`_build_root_blueprint_rows`) and the pool-wide rows are
              represented by their pass digest, so the key holds no pool-sized
              tuple. The pool digest covers every spell's topology sockets, so
              no per-root socket rows are needed (the Phase-5 socket overlay
              that produced them was retired on 2026-09-26).
            - `id(path_registry)` stays the deliberate process-local part: it
              scopes reuse to one blueprint object.
        """
        if root_blueprint is None or root_rows is None or pool_digest is None:
            return None
        ordered_node_ids, path_registry_identity = root_rows
        return (
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            pool_digest,
        )

    def _build_occurrence_graph_input_signature(
            self,
            *,
            root_blueprint: "RootResolutionBlueprint",
            root_rows: Optional[Tuple[Tuple[Any, ...], int]],
            pool_digest: Optional[str],
    ) -> Optional[str]:
        """
        Build a deterministic graph-analysis input signature.

        Purpose:
            Detect semantic drift in graph-shape inputs so repeated warm runs
            can safely skip redundant graph rebuilding when the upstream
            blueprint, spell set, topology, and contract-routing inputs are
            unchanged.

        Contract:
            - Returns `None` when any input is unavailable, forcing a rebuild.
            - Hashes exactly the four parts the fast key tracks, in the same
              order; the pool-wide rows enter through `pool_digest`, so the
              per-root hash covers only the root's own rows plus one 64-char
              digest (hash of a hash of the same inputs the old layout hashed
              flat).
            - Artifact-local only: the value is reset with the artifact and is
              never persisted, so its byte layout carries no cache-generation
              consequence.
        """
        if root_blueprint is None or root_rows is None or pool_digest is None:
            return None
        ordered_node_ids, path_registry_identity = root_rows
        return SharedCompilerExecutions.hash_codegen_signature(
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            pool_digest,
        )

    def _get_pool_digest(
            self,
            *,
            spell_rows: Optional[Tuple[Any, ...]],
            graph_shape: Optional[Tuple[Any, ...]],
            analysis_pass_cache: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Return the pass-invariant digest of the pool-wide signature rows.

        Purpose:
            The spell walk rows, topology rows, contracted routing rows and the
            system state are identical for every root analyzed in one pass;
            hashing them per root made the phase-8 key path O(spells^2). With
            a pass cache they are hashed once per pass.

        Contract:
            - Returns `None` when `spell_rows` or `graph_shape` is unavailable
              (callers treat that as "force the rebuild path"); a `None` input
              never consults or populates the memo.
            - Digest = `hash_codegen_signature(spell_rows, topology_rows,
              system_state, contracted_rows)` - the same rows in the same order
              the old flat signature carried after the root parts.
            - Memoized in `analysis_pass_cache["phase8_pool_digest"]`, which
              dies with the pass units exactly like `phase8_spell_walk` and
              `phase8_graph_shape_rows`; concurrent unit workers may race to
              build it, which is benign (identical values, last write wins).
            - Without a pass cache the digest is computed per root (the cost
              the old layout paid on every root).
        """
        if spell_rows is None or graph_shape is None:
            return None
        if analysis_pass_cache is not None:
            shared_digest = analysis_pass_cache.get("phase8_pool_digest")
            if shared_digest is not None:
                return shared_digest
        topology_rows, contracted_rows, system_state = graph_shape
        pool_digest = SharedCompilerExecutions.hash_codegen_signature(
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )
        if analysis_pass_cache is not None:
            analysis_pass_cache["phase8_pool_digest"] = pool_digest
        return pool_digest

    @staticmethod
    def _build_root_blueprint_rows(
            root_blueprint: "RootResolutionBlueprint",
    ) -> Optional[Tuple[Tuple[Any, ...], int]]:
        """
        Build the root-specific blueprint rows shared by fast key + signature.

        Contract:
            - Cost is proportional to the root's own blueprint, never to the
              full spell pool.
            - Built ONCE per root by `analyze` and handed to both key builders
              as `root_rows`.
            - Returns `None` on any extraction failure (callers treat that as
              "force the rebuild path").
        """
        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
        except Exception:
            return None
        return ordered_node_ids, path_registry_identity

    def _build_graph_shape_rows(
            self,
            *,
            spellbook: "Spellbook",
            spell_system_states: Optional["SpellSystemStates"],
            analysis_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build (or reuse) the pass-invariant graph-wide signature rows.

        Purpose:
            Topology rows and contracted provider routing rows are identical
            for every spell analyzed in one pass; building them per spell made
            phase 8 O(spells^2). With a pass cache they are built once, and
            `_get_pool_digest` hashes them once more into the pass-memoized
            `phase8_pool_digest` slot so no root hashes them again.

        Contract:
            - Returns `(topology_rows, contracted_rows, system_state)` or
              `None` on failure (callers force the rebuild path).
            - Topology rows include resolved socket policy and descriptive references,
              so required-input changes cannot reuse a stale occurrence/model signature.
            - Failures are never cached; every spell retries the build.
            - The cached tuple is immutable; concurrent unit workers may race
              to build it, which is benign (identical values, last write
              wins).
        """
        if analysis_pass_cache is not None:
            shared = analysis_pass_cache.get("phase8_graph_shape_rows")
            if shared is not None:
                return shared

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if spell_system_states is not None:
            local_topologies = spell_system_states._local_topologies
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                            socket.socket_kind.value,
                            socket.position,
                            socket.parameter_kind,
                            socket.is_collection,
                            socket.is_optional,
                            socket.referenced_spell_ids,
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            frame_configuration = spellbook._aetheric_frame_configuration
            if frame_configuration is None:
                return None
            system_state = frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.selected_spell_id
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        shared = (topology_rows, contracted_rows, system_state)
        if analysis_pass_cache is not None:
            analysis_pass_cache["phase8_graph_shape_rows"] = shared
        return shared

    def _get_shared_spell_walk(
            self,
            *,
            spell_lookup: Dict[str, "Spell"],
            analysis_pass_cache: Optional[Dict[str, Any]],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Return the pass-shared full-pool spell walk bundle, memoized per pass.

        Contract:
            - Returns the immutable six-slot bundle produced by
              `_build_spell_walk_rows` (spell rows, occurrence rows, existence
              counts, disposal-enabled count, existence/disposal counts, and
              existence by spell id), reusing the `phase8_spell_walk`
              pass-cache slot when a cache is supplied.
            - Returns `None` when no lookup is supplied or the walk fails.
            - The bundle is POOL-scoped by design (one walk per pass); callers
              needing root-scoped truth must filter it through
              `_build_existence_occurrence_analysis`.
        """
        if spell_lookup is None:
            return None
        shared = None
        if analysis_pass_cache is not None:
            shared = analysis_pass_cache.get("phase8_spell_walk")
        if shared is None:
            shared = self._build_spell_walk_rows(spell_lookup=spell_lookup)
            if shared is None:
                return None
            if analysis_pass_cache is not None:
                analysis_pass_cache["phase8_spell_walk"] = shared
        return shared

    @staticmethod
    def _build_existence_occurrence_analysis(
            *,
            root_spell_id: str,
            shared_spell_walk: Tuple[Any, ...],
            visible_spell_ids: Set[str],
    ) -> Optional[SpellExistenceOccurrenceAnalysis]:
        """
        Build the ROOT-VISIBLE existence-occurrence analysis for one root.

        Purpose:
            Phase-10 family discovery reasons about the root's visible spell
            set. The shared pass walk is pool-scoped for performance, so this
            builder filters its rows down to the spell ids present in the
            root's occurrence graph and recomputes every aggregate from the
            filtered rows (owner finding 2026-07-12: pool-scoped counts were
            contaminating solo/many_only family selection with unrelated
            spellbook members, so the same root could select different
            compiler families depending on unrelated pool composition).

        Contract:
            - `visible_spell_ids` must come from the fully built (and
              ordered-node-extended) occurrence graph for this root.
            - `total_spell_count`, rows, and every aggregate reflect ONLY the
              visible rows; `root_existence` resolution is unchanged.
            - Returns `None` when the root id is missing.

        Returns:
            Optional[SpellExistenceOccurrenceAnalysis]:
                The root-scoped analysis, or `None` without a root id.
        """
        if not root_spell_id:
            return None
        (
            _spell_rows,
            occurrence_rows,
            _existence_counts,
            _disposal_enabled_spell_count,
            _existence_disposal_counts,
            existence_by_spell_id,
        ) = shared_spell_walk

        visible_rows = tuple(
            row for row in occurrence_rows if row.spell_id in visible_spell_ids
        )
        existence_counts_by_name: Dict[Existence, int] = {}
        existence_disposal_counts_by_name: Dict[Tuple[Existence, bool], int] = {}
        disposal_enabled_spell_count = 0
        for row in visible_rows:
            existence_counts_by_name[row.existence] = (
                existence_counts_by_name.get(row.existence, 0) + 1
            )
            disposal_key = (row.existence, row.has_disposal_methods)
            existence_disposal_counts_by_name[disposal_key] = (
                existence_disposal_counts_by_name.get(disposal_key, 0) + 1
            )
            if row.has_disposal_methods:
                disposal_enabled_spell_count += 1

        return SpellExistenceOccurrenceAnalysis(
            root_existence=existence_by_spell_id.get(root_spell_id),
            total_spell_count=len(visible_rows),
            spell_existence_rows=visible_rows,
            existence_counts=tuple(existence_counts_by_name.items()),
            disposal_enabled_spell_count=disposal_enabled_spell_count,
            existence_disposal_counts=tuple(
                existence_disposal_counts_by_name.items()
            ),
        )

    @staticmethod
    def _build_spell_walk_rows(
            *,
            spell_lookup: Dict[str, "Spell"],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Walk the full spell pool once and freeze every root-independent row.

        Contract:
            - Returns an immutable bundle (tuples + one read-only dict) safe
              to share across all per-spell analyses in one pass; concurrent
              builders may race benignly (identical values, last write wins).
            - Returns `None` on any walk failure.
        """
        try:
            spell_rows_list: List[Tuple[Any, ...]] = []
            occurrence_rows_list: List[SpellExistenceOccurrence] = []
            existence_counts_by_name: Dict[Existence, int] = {}
            existence_disposal_counts_by_name: Dict[Tuple[Existence, bool], int] = {}
            existence_by_spell_id: Dict[str, Existence] = {}
            disposal_enabled_spell_count = 0

            for spell_id, candidate_spell in sorted(spell_lookup.items()):
                current_spell_id = candidate_spell.spell_index.selected_spell_id
                existence = candidate_spell.existence
                has_disposal_methods = bool(candidate_spell.has_disposal_methods)
                spell_rows_list.append(
                    (
                        spell_id,
                        current_spell_id,
                        existence.name,
                        bool(candidate_spell.is_existing_creation),
                    )
                )
                occurrence_rows_list.append(
                    SpellExistenceOccurrence(
                        spell_id=spell_id,
                        existence=existence,
                        has_disposal_methods=has_disposal_methods,
                    )
                )
                existence_by_spell_id[spell_id] = existence
                current_count = existence_counts_by_name.get(existence, 0)
                existence_counts_by_name[existence] = current_count + 1
                current_pair_count = existence_disposal_counts_by_name.get(
                    (existence, has_disposal_methods),
                    0,
                )
                existence_disposal_counts_by_name[
                    (existence, has_disposal_methods)
                ] = current_pair_count + 1
                if has_disposal_methods:
                    disposal_enabled_spell_count += 1
        except Exception:
            return None

        existence_counts = tuple(
            sorted(
                existence_counts_by_name.items(),
                key=lambda item: item[0].name,
            )
        )
        existence_disposal_counts = tuple(
            sorted(
                existence_disposal_counts_by_name.items(),
                key=lambda item: (
                    item[0][0].name,
                    int(item[0][1]),
                ),
            )
        )
        return (
            tuple(spell_rows_list),
            tuple(occurrence_rows_list),
            existence_counts,
            disposal_enabled_spell_count,
            existence_disposal_counts,
            existence_by_spell_id,
        )

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceGraphAnalysis],
            current: SpellOccurrenceGraphAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-graph analysis artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @staticmethod
    def _is_shared_existence(existence: Existence) -> bool:
        """
        Determine whether an existence policy yields a shared instance.
        """
        return existence is not Existence.many

    @staticmethod
    def _occurrence_sort_key(
            occurrence: OccurrenceKey,
    ) -> Tuple[str, int]:
        """
        Build a deterministic ordering key for occurrence tuples.
        """
        path_id = occurrence[1]
        if path_id is None:
            return occurrence[0], -1
        return occurrence[0], path_id

    @staticmethod
    def _iter_dependency_occurrences_for_enqueue(
            dependencies: Dict[str, List[OccurrenceKey]],
    ) -> Iterable[OccurrenceKey]:
        """
        Iterate dependency occurrences in deterministic queue order.
        """
        for param_name in sorted(dependencies.keys()):
            child_occurrences = sorted(
                dependencies[param_name],
                key=SpellOccurrenceGraphAnalyzerStrategy._occurrence_sort_key,
            )
            for child_occurrence in child_occurrences:
                yield child_occurrence

    def _should_collapse_shared_occurrences(
            self,
            *,
            spell_lookup: Dict[str, "Spell"],
    ) -> bool:
        """
        Determine whether shared occurrences can be collapsed during expansion.
        """
        _ = spell_lookup
        return True

    def _build_occurrence_graph(
            self,
            *,
            dag: Any,
            root_spell_id: str,
            collapse_shared_occurrences: bool,
            spell_lookup: Dict[str, "Spell"],
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
            spellbook: "Spellbook",
            root_blueprint: "RootResolutionBlueprint",
    ) -> Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]:
        """
        Build a path-aware occurrence graph rooted at the entrypoint spell.

        Contract:
            - Includes the root occurrence even when it has no dependencies.
            - Expands dependencies from topology first, then DAG fallback,
              then contract and mutation overlays.
            - Applies shared-occurrence collapse only when the spell set is
              mutation-clean for the current run.
            - Returns one analyzer-owned occurrence graph mapping that later
              strategies must treat as read-only.
        """
        root_path_id = path_registry.root_path_id
        root_occurrence = (root_spell_id, root_path_id)
        occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]] = {}
        queue = deque([root_occurrence])
        seen: Set[OccurrenceKey] = set()
        queued: Set[OccurrenceKey] = {root_occurrence}
        shared_seen: Set[str] = set()

        while queue:
            occurrence = queue.popleft()
            queued.discard(occurrence)
            if occurrence in seen:
                continue

            spell_id = occurrence[0]
            if collapse_shared_occurrences:
                spell = spell_lookup.get(spell_id)
                if spell is not None and self._is_shared_existence(spell.existence):
                    if spell_id in shared_seen:
                        seen.add(occurrence)
                        continue
                    shared_seen.add(spell_id)
            seen.add(occurrence)

            dependencies = self._collect_occurrence_dependencies(
                occurrence=occurrence,
                dag=dag,
                spell_lookup=spell_lookup,
                spell_system_states=spell_system_states,
                path_registry=path_registry,
                spellbook=spellbook,
                root_blueprint=root_blueprint,
            )
            occurrence_graph[occurrence] = dependencies

            for child_occurrence in self._iter_dependency_occurrences_for_enqueue(
                    dependencies,
            ):
                if child_occurrence not in seen and child_occurrence not in queued:
                    queued.add(child_occurrence)
                    queue.append(child_occurrence)

        return occurrence_graph

    def _extend_occurrence_graph_with_ordered_nodes(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            ordered_node_ids: Sequence[str],
            dag: Any,
            collapse_shared_occurrences: bool,
            spell_lookup: Dict[str, "Spell"],
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
            spellbook: "Spellbook",
            root_blueprint: "RootResolutionBlueprint",
    ) -> None:
        """
        Ensure ordered nodes outside the root path still get occurrences.
        """
        existing_occurrences = set(occurrence_graph.keys())
        present_spell_ids = {
            spell_id
            for spell_id, _ in existing_occurrences
        }
        root_path_id = path_registry.root_path_id
        shared_seen: Set[str] = set()
        if collapse_shared_occurrences:
            for spell_id in present_spell_ids:
                spell = spell_lookup.get(spell_id)
                if spell is not None and self._is_shared_existence(spell.existence):
                    shared_seen.add(spell_id)

        for node_id in ordered_node_ids:
            if node_id in present_spell_ids:
                continue

            queue = deque([(node_id, root_path_id)])
            queued: Set[OccurrenceKey] = {(node_id, root_path_id)}
            while queue:
                occurrence = queue.popleft()
                queued.discard(occurrence)
                if occurrence in existing_occurrences:
                    continue

                spell_id = occurrence[0]
                if collapse_shared_occurrences:
                    spell = spell_lookup.get(spell_id)
                    if spell is not None and self._is_shared_existence(spell.existence):
                        if spell_id in shared_seen:
                            existing_occurrences.add(occurrence)
                            continue
                        shared_seen.add(spell_id)
                existing_occurrences.add(occurrence)
                present_spell_ids.add(spell_id)

                dependencies = self._collect_occurrence_dependencies(
                    occurrence=occurrence,
                    dag=dag,
                    spell_lookup=spell_lookup,
                    spell_system_states=spell_system_states,
                    path_registry=path_registry,
                    spellbook=spellbook,
                    root_blueprint=root_blueprint,
                )
                occurrence_graph[occurrence] = dependencies

                for child_occurrence in self._iter_dependency_occurrences_for_enqueue(
                        dependencies,
                ):
                    if (
                            child_occurrence not in existing_occurrences
                            and child_occurrence not in queued
                    ):
                        queued.add(child_occurrence)
                        queue.append(child_occurrence)

    def _collect_occurrence_dependencies(
            self,
            *,
            occurrence: OccurrenceKey,
            dag: Any,
            spell_lookup: Dict[str, "Spell"],
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
            spellbook: "Spellbook",
            root_blueprint: "RootResolutionBlueprint",
    ) -> Dict[str, List[OccurrenceKey]]:
        """
        Collect dependency occurrences for a single spell occurrence.
        """
        dependencies: Dict[str, List[OccurrenceKey]] = {}

        used_topology = self._append_topology_dependencies(
            dependencies=dependencies,
            spell_id=occurrence[0],
            path_id=occurrence[1],
            spell_system_states=spell_system_states,
            path_registry=path_registry,
        )
        if not used_topology:
            self._append_dag_dependencies(
                dependencies=dependencies,
                spell_id=occurrence[0],
                path_id=occurrence[1],
                dag=dag,
                path_registry=path_registry,
            )
        self._apply_spell_contract_dependencies(
            dependencies=dependencies,
            occurrence=occurrence,
            spell_lookup=spell_lookup,
            spellbook=spellbook,
            path_registry=path_registry,
        )
        return dependencies

    @staticmethod
    def _append_topology_dependencies(
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path_id: int,
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
    ) -> bool:
        """
        Append dependencies discovered from SpellSystemStates local topology.

        Contract:
            - Each target of a socket becomes one child occurrence
              `(target_id, child_path_id)` under the socket's parameter name.
            - A collection socket gives every member its own child path
              (`extend_path(..., member=target_id)`), so dependencies below
              different members are separate occurrences and each member gets its
              own `Existence.many` objects. Phase 5 mints the same ids.
            - Returns False when the spell has no local topology (the caller then
              falls back to DAG metadata).
        """
        topology = spell_system_states._local_topologies.get(spell_id)
        if topology is None:
            return False

        for socket in topology.sockets:
            if not socket.target_spell_ids:
                if socket.is_collection and not socket.is_optional:
                    # Zero-provider REQUIRED collection socket: publish the
                    # param with an empty dependency list so phases 9-11 see
                    # the socket and inject [] at construction (owner policy:
                    # an empty collection spawns with an empty list rather
                    # than failing conjure). Optional empty collections stay
                    # unpublished so the constructor default applies.
                    dependencies.setdefault(socket.param_name, [])
                continue
            for target_id in socket.target_spell_ids:
                if socket.is_collection:
                    child_path_id = path_registry.extend_path(
                        path_id,
                        socket.param_name,
                        member=target_id,
                    )
                else:
                    child_path_id = path_registry.extend_path(path_id, socket.param_name)
                dependencies.setdefault(socket.param_name, []).append(
                    (target_id, child_path_id)
                )
        return True

    @staticmethod
    def _append_dag_dependencies(
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path_id: int,
            dag: Any,
            path_registry: Any,
    ) -> None:
        """
        Append dependencies discovered from the DAG metadata.

        Contract:
            - Used only when the spell has no local topology, so collection-ness
              is not known: a parameter fed by two or more nodes is treated as a
              collection and each node gets its own member path, matching the
              topology rule.
        """
        if dag is None:
            return
        node = dag.get_node(spell_id)
        if node is None:
            return
        parent_entries: List[Tuple[str, str, Any]] = []
        for parent_node in node.dependencies:
            incoming_name = node.incoming_params.get(parent_node)
            if incoming_name is None:
                continue
            parent_entries.append((incoming_name, parent_node.id, parent_node))
        entry_counts: Dict[str, int] = {}
        for param_name, _, _ in parent_entries:
            entry_counts[param_name] = entry_counts.get(param_name, 0) + 1
        for param_name, parent_id, parent_node in sorted(parent_entries):
            if entry_counts[param_name] > 1:
                child_path_id = path_registry.extend_path(
                    path_id,
                    param_name,
                    member=parent_id,
                )
            else:
                child_path_id = path_registry.extend_path(path_id, param_name)
            child_occurrence = (parent_node.id, child_path_id)

            dependencies.setdefault(param_name, []).append(child_occurrence)

    def _apply_spell_contract_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            occurrence: OccurrenceKey,
            spell_lookup: Dict[str, "Spell"],
            spellbook: "Spellbook",
            path_registry: Any,
    ) -> None:
        """
        Add dependency occurrences for SpellContract sockets.
        """
        spell = spell_lookup[occurrence[0]]
        allow_missing = self._allow_missing_contract_providers(spellbook)

        for param_name, contract in self._iter_spell_contract_defaults(spell):
            target_spell_id = self._resolve_spell_contract_spell_id(
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
                spellbook=spellbook,
                allow_missing=allow_missing,
            )
            if target_spell_id is None:
                continue
            child_path_id = path_registry.extend_path(occurrence[1], param_name)
            dependencies.setdefault(param_name, []).append(
                (target_spell_id, child_path_id)
            )

    @staticmethod
    def _iter_spell_contract_defaults(
            spell: "Spell",
    ) -> Iterable[Tuple[str, SpellContract]]:
        """
        Yield SpellContract defaults discovered in the spell's callable surface.

        Existing creations are already supplied values and have no constructor
        contracts to discover. Returning no contracts leaves the consumer's
        incoming dependency edge intact; class/factory discovery is unchanged.

        When the Phase-1 requirements have been released (they are after conjure),
        the callable signature is read in FORWARDREF format: only defaults are
        inspected, and a VALUE-format read raises NameError when an annotation
        names a TYPE_CHECKING-only type (Python 3.14 lazy annotations).
        """
        contracts: List[Tuple[str, SpellContract]] = []
        if spell.is_existing_creation:
            return contracts

        requirements = spell._compiler_artifact._requirements
        if requirements is not None:
            for param in requirements.parameters:
                if param.di_shape is ParameterDIShape.SPELL_CONTRACT:
                    if isinstance(param.default_value, SpellContract):
                        contracts.append((param.name, param.default_value))
            return contracts

        signature = inspect.signature(spell.spell, annotation_format=Format.FORWARDREF)
        for param_name, parameter in signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if parameter.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if parameter.default is inspect.Parameter.empty:
                continue
            default_value = parameter.default
            if isinstance(default_value, SpellContract):
                contracts.append((param_name, default_value))

        return contracts

    def _resolve_spell_contract_spell_id(
            self,
            *,
            contract: SpellContract,
            consumer_spell: "Spell",
            param_name: str,
            spellbook: "Spellbook",
            allow_missing: bool = False,
    ) -> Optional[str]:
        """
        Resolve a SpellContract to a concrete resolvable provider spell id.

        Contract:
            Preserve explicit cardinality and dynamic missing-provider behavior.
            A selected non-resolvable definition is incompatible, not missing.
        """
        consumer_spell_id = consumer_spell.spell_index.selected_spell_id
        if consumer_spell_id is None:
            consumer_spell_id = consumer_spell.spell_id

        contracted_candidates = self._collect_contracted_contract_candidates(
            contract_key=contract.canonical_key,
            spellbook=spellbook,
        )
        if len(contracted_candidates) > 1:
            raise MeldExecutionError(
                spell_id=consumer_spell_id,
                spell_name=consumer_spell.spell_name,
                node_id=consumer_spell_id,
                param_name=param_name,
                message=(
                    "SpellContract resolved to multiple contracted spells. "
                    "Use distinct bindings or remove the ambiguous contracts."
                ),
            )
        if len(contracted_candidates) == 1:
            if not contracted_candidates[0].resolvable:
                raise MeldExecutionError(
                    spell_id=consumer_spell_id,
                    spell_name=consumer_spell.spell_name,
                    node_id=consumer_spell_id,
                    param_name=param_name,
                    message=(
                        "SpellContract selected non-resolvable provider "
                        f"{contracted_candidates[0].spell_id!r}. Select a resolvable provider "
                        "or supply the consumer input through an override-required dependency."
                    ),
                )
            return contracted_candidates[0].spell_index.selected_spell_id

        if allow_missing:
            return None
        raise MeldExecutionError(
            spell_id=consumer_spell_id,
            spell_name=consumer_spell.spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message=(
                "SpellContract could not be resolved. "
                "No contracted spell matched the contract."
            ),
        )

    @staticmethod
    def _collect_contracted_contract_candidates(
            *,
            contract_key: Tuple[str, str],
            spellbook: "Spellbook",
    ) -> List["Spell"]:
        """
        Collect contracted spell candidates that satisfy the contract key.
        """
        contracted_candidates: List["Spell"] = []
        for conduit_id in sorted(spellbook._lookup_contracted_spells.keys()):
            lookup_map = spellbook._lookup_contracted_spells[conduit_id]
            spell_index = lookup_map.get(contract_key)
            if spell_index is None:
                continue
            contracted_map = spellbook._contracted_spells.get(conduit_id)
            if contracted_map is None:
                continue
            spell_obj = contracted_map.get(spell_index)
            if spell_obj is None:
                continue
            contracted_candidates.append(spell_obj)

        contracted_candidates.sort(
            key=lambda spell: spell.spell_index.selected_spell_id or spell.spell_id
        )
        return contracted_candidates

    @staticmethod
    def _allow_missing_contract_providers(
            spellbook: "Spellbook",
    ) -> bool:
        """
        Determine whether graph build may tolerate missing SpellContract providers.
        """
        frame_configuration = spellbook._aetheric_frame_configuration
        if frame_configuration is None:
            raise RuntimeError("Root spellbook has no frame configuration.")
        state_enum = EnumHelpers.convert_enum_and_check(
            frame_configuration.system_state,
            SystemState,
        )
        return state_enum is SystemState.dynamic

    @staticmethod
    def _count_occurrence_edges(
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count the total number of dependency edges in the occurrence graph.
        """
        edge_count = 0
        for dependency_map in occurrence_graph.values():
            for dependency_occurrences in dependency_map.values():
                edge_count += len(dependency_occurrences)
        return edge_count

    @staticmethod
    def _count_topology_dependencies(
            *,
            spell_system_states: "SpellSystemStates",
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count edges whose spell ids have topology entries.
        """
        topology_dependency_count = 0
        for occurrence, dependency_map in occurrence_graph.items():
            if spell_system_states._local_topologies.get(occurrence[0]) is None:
                continue
            for dependency_occurrences in dependency_map.values():
                topology_dependency_count += len(dependency_occurrences)
        return topology_dependency_count

    @staticmethod
    def _count_dag_fallback_dependencies(
            *,
            spell_system_states: "SpellSystemStates",
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count edges whose spell ids had to fall back to DAG metadata.
        """
        fallback_count = 0
        for occurrence, dependency_map in occurrence_graph.items():
            if spell_system_states._local_topologies.get(occurrence[0]) is not None:
                continue
            for dependency_occurrences in dependency_map.values():
                fallback_count += len(dependency_occurrences)
        return fallback_count


