import inspect
import types
import typing
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Tuple, Union, get_args, get_origin

if TYPE_CHECKING:
    from melder.aether.spellbook.spellbook import Spellbook

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.ispell import ISpell

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class CompilerPhase3:
    """
    Compiler phase 3 surface.

    Purpose:
        Expose the current local-frame / DAG build behavior through a
        compiler-owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-3 behavior.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def _get_required_current_spell_id(
            self,
            spell: ISpell,
    ) -> str:
        """
        Return the current bound spell version id or raise.

        Args:
            spell:
                Bound spell whose versioned identifier is required.

        Returns:
            str: Current spell version id.

        Raises:
            RuntimeError: If the spell has no bound `spell_index.current`.

        """
        current_spell_id = spell.spell_index.current
        if current_spell_id is None:
            raise RuntimeError("SpellCrafter requires a bound spell current id.")
        return current_spell_id

    def _get_required_spell_system_states(
            self,
            spell_system_states: SpellSystemStates,
    ) -> SpellSystemStates:
        """
        Return the borrowed spell-system-state registry or raise.

        Args:
            spell_system_states:
                Candidate spell-system-state surface.

        Returns:
            SpellSystemStates: Borrowed spell-system-state registry.

        Raises:
            RuntimeError: If the registry is missing at runtime.
        """
        if spell_system_states is None:
            raise RuntimeError(
                "SpellCrafter requires a live SpellSystemStates surface."
            )
        return spell_system_states

    def _iter_all_spells(
            self,
            spellbook: Spellbook,
    ) -> Generator[tuple[Any, Any], Any, None]:
        """
            Iterate all visible spells via the Spellbook's live spell_id_pool.
            
            Purpose:
                Provide a single internal iterator that Phase 3 can use for
                resolution without relying on any scanner wrapper.
            Contract:
                - Yields "(spell_index, spell)" in the insertion order of
                  "_spell_id_pool".
                - Uses the Spellbook's live "_spell_id_pool" directly; no copies
                  or snapshots are created.
            Returns:
                Iterator[Tuple[SpellIndex, ISpell]]: Live iteration stream.
        """
        for spell_instance in spellbook._spell_id_pool.values():
            yield spell_instance.spell_index, spell_instance

    def _normalize_annotation_for_matching(self, annotation: Any) -> Any:
        """
            Normalize a DI annotation for Phase 3 matching.
            
            This unwraps Optional/Union-with-None annotations and converts
            ForwardRef tokens into their string names so name-based matching
            can succeed for local forward references.
            
            Args:
                annotation:
                    The raw annotation object from Phase 1.
            
            Returns:
                Any:
                    The normalized annotation to use for matching.
        """
        if isinstance(annotation, typing.ForwardRef):
            return annotation.__forward_arg__

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin in (Union, types.UnionType) and args:
            non_none_args: List[Any] = []
            for arg in args:
                if isinstance(arg, typing.ForwardRef):
                    arg_value = arg.__forward_arg__
                else:
                    arg_value = arg
                if arg_value is type(None):
                    continue
                non_none_args.append(arg_value)

            if len(non_none_args) == 1:
                return non_none_args[0]

        return annotation

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: ISpell,
            *,
            require_class_spell: bool,
    ) -> bool:
        """
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy:
            - Optional/Union wrappers are stripped before matching.
            - String/bare-name annotation matches against `spell_name`, `frame`
              (string or type name), and the bound spell type object.
            - Non-string annotation matches against `spell.spell` and
              `spell.spellframe`.
            - `require_class_spell=True` excludes METHOD/LAMBDA spell kinds.

        Args:
            annotation:
                Canonicalized annotation to match.
            binding_name:
                Optional binding-name filter.
            spell_obj:
                Candidate spell.
            require_class_spell:
                When True, only class-like spells are allowed.

        Returns:
            bool: `True` when the candidate should be considered for this
            dependency.
        """
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__

        if isinstance(annotation, str):
            if spell_obj.spell_name == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

            frame = spell_obj.spellframe
            if isinstance(frame, str) and frame == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

            if inspect.isclass(frame) and frame.__name__ == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

        if spell_obj.spell is annotation:
            if binding_name is not None and spell_obj.binding_name != binding_name:
                return False
            return True

        frame = spell_obj.spellframe
        if frame is annotation or frame == annotation:
            if binding_name is not None and spell_obj.binding_name != binding_name:
                return False
            return True

        return False

    def _resolve_single_by_annotation(
            self,
            spell: ISpell,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        Args:
            spell:
                Consuming spell owning the dependency.
            spellbook:
                Spellbook used for candidate enumeration.
            dep:
                Dependency metadata for this constructor parameter.

        Returns:
            Dict[Any, ISpell]:
                Mapping from matched `spell_index` to spell.

        Raises:
            RuntimeError: If zero candidates are found or multiple candidates
                match the annotation constraints.
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        binding_name: Optional[str] = None

        candidates: Dict[Any, ISpell] = {}

        for index, spell_obj in self._iter_all_spells(spellbook):
            if self._matches_annotation(
                    annotation,
                    binding_name,
                    spell_obj,
                    require_class_spell=True,
            ):
                candidates[index] = spell_obj

        if not candidates:
            raise RuntimeError(
                f"SpellCrafter Phase 3: no DI candidate found for parameter "
                f"{dep.param_name!r} on spell {spell.spell_name!r} "
                f"(annotation={annotation!r})."
            )

        if len(candidates) > 1:
            names = ", ".join(
                sorted(candidate_spell.spell_name for candidate_spell in candidates.values())
            )
            raise RuntimeError(
                "SpellCrafter Phase 3: multiple DI candidates found for "
                f"parameter {dep.param_name!r} on spell {spell.spell_name!r} "
                f"(annotation={annotation!r}). "
                f"Candidates: {names}. "
                "Use a SpellMap with an explicit spellframe/binding_name or a "
                "collection type (e.g. list[FrameType]) to inject multiple "
                "implementations."
            )

        return candidates

    def _resolve_collection_by_annotation(
            self,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
            Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
            spells (classes, methods, lambdas) bound under the given frame/type.
            
            This corresponds to list[FrameType]-style DI where the user explicitly
            asked for "all implementations".
            
            Returns:
                Dict[SpellIndex, Spell]: mapping of all candidates. It is valid
                for this mapping to be empty (an empty collection will be injected).
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        binding_name: Optional[str] = None

        candidates: Dict[Any, ISpell] = {}

        for index, spell_obj in self._iter_all_spells(spellbook):
            if self._matches_annotation(
                    annotation,
                    binding_name,
                    spell_obj,
                    require_class_spell=False,
            ):
                candidates[index] = spell_obj

        return candidates

    def _socket_kind_for_dep(self, dep: SpellSymbolicDependency) -> SocketKind:
        """
            Map a symbolic dependency's DI shape into a SocketKind.
            
            NORMAL:
                Regular DI parameter (annotation, SpellMap, collection) or a
                plain constructor socket.
            SPELL_CONTRACT:
                SpellContract socket - must be satisfied by a provider.
            MUTATION_CONTRACT:
                MutationContract socket - can be rewired at meld-time.
            
            For now, we classify based solely on `dep.di_shape`. If we later
            introduce additional DI shapes, this is the central mapping point.
        """
        di_shape = dep.di_shape

        if di_shape is ParameterDIShape.SPELL_CONTRACT:
            return SocketKind.SPELL_CONTRACT
        if di_shape is ParameterDIShape.MUTATION_CONTRACT:
            return SocketKind.MUTATION_CONTRACT

        return SocketKind.NORMAL

    def _resolve_spellmap_default(
            self,
            spell: ISpell,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a SPELLMAP_DEFAULT dependency using the original SpellMap
        default attached to the parameter.

        Args:
            spell:
                Consuming spell owning the dependency.
            spellbook:
                Spellbook used for candidate enumeration.
            dep:
                Dependency metadata containing spellmap defaults.

        Returns:
            Dict[Any, ISpell]:
                Mapping with exactly one resolved spell for the default.

        Raises:
            RuntimeError: If no candidate can be resolved or multiple
                candidates satisfy the explicit default selection constraints.
        """
        spellmap = dep.spellmap_default
        if spellmap is None:
            return {}

        candidates: Dict[Any, ISpell] = {}
        explicit_spell = spellmap.spell
        frame = spellmap.spellframe
        binding_name = spellmap.binding_name

        if explicit_spell is not None:
            for index, spell_obj in self._iter_all_spells(spellbook):
                if spell_obj.spell is not explicit_spell:
                    continue

                if frame is not None:
                    spell_frame = spell_obj.spellframe
                    if not (spell_frame is frame or spell_frame == frame):
                        continue

                if binding_name is not None and spell_obj.binding_name != binding_name:
                    continue

                candidates[index] = spell_obj
        else:
            for index, spell_obj in self._iter_all_spells(spellbook):
                if spell_obj.spellframe is spellmap.spellframe or spell_obj.spellframe == spellmap.spellframe:
                    if spell_obj.binding_name == spellmap.binding_name:
                        candidates[index] = spell_obj

        if not candidates:
            raise RuntimeError(
                "SpellCrafter Phase 3: SpellMap default could not be resolved for "
                f"parameter {dep.param_name!r} on spell {spell.spell_name!r}. "
                f"SpellMap={spellmap!r}."
            )

        if len(candidates) > 1:
            names = ", ".join(
                sorted(candidate_spell.spell_name for candidate_spell in candidates.values())
            )
            raise RuntimeError(
                "SpellCrafter Phase 3: SpellMap default resolved to multiple "
                f"candidates for parameter {dep.param_name!r} on spell "
                f"{spell.spell_name!r}. Candidates: {names}. "
                "SpellMap defaults must be unambiguous."
            )

        return candidates

    def _dependency_key_for_dep(
            self,
            dep: SpellSymbolicDependency,
    ) -> Optional[Tuple[str, str]]:
        """
        Resolve the canonical dependency key for a NORMAL DI socket.

        For SpellMap defaults, this uses the SpellMap's canonical key.
        For annotation-driven shapes (single/collection), this normalizes
        the frame key from the target annotation using the default binding.

        Args:
            dep:
                Dependency metadata for which a locality key is requested.

        Returns:
            Optional[Tuple[str, str]]:
                Canonical socket key for topology metadata, or None when no key
                applies.
        """
        if dep is None:
            return None

        if dep.di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
            spellmap = dep.spellmap_default
            if spellmap is None:
                return None
            spellmap_key: Tuple[str, str] = spellmap.canonical_key
            return spellmap_key

        if dep.di_shape in (
                ParameterDIShape.SINGLE_BY_ANNOTATION,
                ParameterDIShape.COLLECTION_BY_ANNOTATION,
        ):
            if dep.target_annotation is None:
                return None
            normalized_key: Tuple[str, str] = SpellInputUtils.normalize_spell_key(
                spellframe=dep.target_annotation,
                binding_name=None,
            )
            return normalized_key

        return None

    def _build_local_topology(
            self,
            spell: ISpell,
            graph: SpellSymbolicGraph,
            socket_targets: Dict[tuple[str, int], List[str]],
    ) -> SpellLocalTopology:
        """
            Internal helper for Phase 3.
            
            Construct a: class:`SpellLocalTopology` describing this Spell's
            constructor sockets, based on:
            
                * the symbolic dependencies from: class:`SpellSymbolicGraph`, and
                * the concrete dependency spell ids resolved during Phase 3.
            
            For each: class:`SpellSymbolicDependency`:
                * Determine "socket_kind" from its: class:`ParameterDIShape`.
                * Copy "is_collection" and "is_optional" flags from the
                  symbolic graph.
                * Look up any concrete targets via "socket_targets" using
                    "(param_name, position)". Normal DI sockets may have one or
                    many targets; contract, mutation, and plain sockets will
                    typically have none at this phase.
                * Preserve contract metadata for SpellContract / MutationContract
                  sockets (canonical key, late-binding flag).
                * Create a: class:`SpellSocketDescriptor` for that parameter.
            
            The resulting: class:`SpellLocalTopology` is a per-spell, constructor-
            local view of sockets that later phases (blueprint assembly, override
            targeting, change-control) will consume. It is registered into: class:`SpellSystemStates` by Phase 3; this method does not talk to
            SpellSystemStates directly.
        """
        spell_id = self._get_required_current_spell_id(spell)
        descriptors: List[SpellSocketDescriptor] = []

        for dep in graph.dependencies:
            targets = socket_targets.get((dep.param_name, dep.position))
            if targets:
                target_spell_ids = tuple(targets)
            else:
                target_spell_ids = ()

            socket_kind = self._socket_kind_for_dep(dep)
            dependency_key = None
            if socket_kind is SocketKind.NORMAL:
                dependency_key = self._dependency_key_for_dep(dep)

            descriptor = SpellSocketDescriptor(
                spell_id=spell_id,
                param_name=dep.param_name,
                position=dep.position,
                socket_kind=socket_kind,
                is_collection=dep.is_collection,
                is_optional=dep.is_optional,
                target_spell_ids=target_spell_ids,
                dependency_key=dependency_key,
                contract_key=dep.contract_key,
                contract_late_binding=dep.contract_late_binding,
            )
            descriptors.append(descriptor)

        topology = SpellLocalTopology(
            spell_id=spell_id,
            sockets=descriptors,
        )
        return topology

    def _build_local_frame_dag(
            self,
            spell: ISpell,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            requirements: "SpellRequirements",
            graph: SpellSymbolicGraph,
            cancellation_event: Optional[CancellationEvent],
            *,
            return_dependencies: bool = False,
    ) -> Union[DirectedAcyclicWorkGraph, Tuple[DirectedAcyclicWorkGraph, List[str]]]:
        """
            Internal helper for Phase 3.
            
            Build the concrete DAG for this Spell's **local frame** and emit
            constructor topology into SpellSystemStates.
            
            Responsibilities:
                * Add a DAG node for the root Spell (current SpellIndex version).
                * For each symbolic dependency:
                      - resolve normal DI shapes via direct Spellbook map iteration,
                      - add DAG nodes for resolved dependency spells,
                      - add edges from each dependency node to the root node,
                        tagging edges with "param_name" and "socket_kind".
                * Track, per constructor socket "(param_name, position)", the
                  concrete dependency spell ids resolved in this phase.
                * Build a: class:`SpellLocalTopology` from the symbolic graph plus
                  the per-socket targets.
                * Call into: class:`SpellSystemStates`:
                      - record direct dependency spell ids, and
                      - register the local topology for this Spell.
            
            Important:
                * This helper does **not** mutate the Spell object. All artifacts
                  (DAG, topology, dependency ids) remain in these SpellCrafter and
                  SpellSystemStates.
                * If "return_dependencies" is True, it returns a tuple of
                  "(dag, dependency_spell_ids)"; otherwise it returns only the DAG.
                * SpellContract and MutationContract sockets take part in the
                  symbolic graph and topology but do not produce DAG edges or
                  concrete targets at this stage.
        """
        if requirements is None:
            raise ValueError("requirements must not be None.")
        if graph is None:
            raise ValueError("graph must not be None.")

        CompilerPhaseUtility.throw_if_cancelled(cancellation_event)

        if spell.spell_index is None:
            raise RuntimeError("SpellCrafter has no bound Spell with a SpellIndex.")

        root_id = self._get_required_current_spell_id(spell)
        dag = DirectedAcyclicWorkGraph()

        # Register the root node first.
        dag.add_node(key=root_id, payload=spell)

        # Track all dependency spell IDs for SpellSystemStates.
        dependency_spell_ids: List[str] = []

        # Track per-socket resolutions for local topology:
        # keyed by (param_name, position) -> [spell_id, ...]
        socket_targets: Dict[tuple[str, int], List[str]] = {}

        for dep in graph.dependencies:
            CompilerPhaseUtility.throw_if_cancelled(cancellation_event)

            di_shape = dep.di_shape

            # Only "normal" DI shapes produce concrete DAG edges for now.
            if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                resolved = self._resolve_single_by_annotation(spell, spellbook, dep)
            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                resolved = self._resolve_collection_by_annotation(spellbook, dep)
            elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                resolved = self._resolve_spellmap_default(spell, spellbook, dep)
            else:
                # SpellContract / MutationContract / PLAIN and any future shapes
                # are currently metadata-only at the DAG level. They still
                # participate in the local topology below.
                resolved = {}

            if not resolved:
                continue

            key = (dep.param_name, dep.position)
            targets_for_socket = socket_targets.setdefault(key, [])

            for spell_index, spell_obj in resolved.items():
                dep_spell_id = spell_index.current
                dependency_spell_ids.append(dep_spell_id)
                targets_for_socket.append(dep_spell_id)

                dag.add_node(key=dep_spell_id, payload=spell_obj)
                dag.add_dependency(
                    parent_key=dep_spell_id,
                    child_key=root_id,
                    param_name=dep.param_name,
                    socket_kind=self._socket_kind_for_dep(dep),
                )

        # Snapshot local topology for this spell's constructor.
        topology = self._build_local_topology(spell, graph, socket_targets)

        # Update spell-system state with dependency IDs and local topology.
        if spell.spell_index is not None:
            spell_system_states.update_dependencies(
                spell.spell_index,
                dependency_spell_ids,
            )
            spell_system_states.register_local_topology(
                spell.spell_index,
                topology,
            )

        if return_dependencies:
            return dag, dependency_spell_ids

        return dag

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 3 - Build the local-frame DAG and constructor topology.

        Responsibilities:
            * Consume the Phase 2 symbolic graph and resolve each socket into
              concrete dependency spell ids.
            * Build the local constructor DAG
              (:class:`DirectedAcyclicWorkGraph`) rooted at this spell, where:
                  - dependency spells are parents,
                  - this spell is the child/root node.
            * Build and register a :class:`SpellLocalTopology` describing the
              constructor sockets (normal sockets, SpellContract sockets,
              MutationContract sockets) and the resolved target spell ids.
            * Persist:
                  - the ordered local frame
                    (:class:`SpellResolutionFrame`) on this compiler artifact,
                  - direct dependency ids on the Spell via
                    :meth:`Spell._add_build_details`,
                  - local topology and direct dependencies into
                    :class:`SpellSystemStates`.

        Args:
            spell:
                Bound spell for which local resolution is being computed.
            artifact:
                Phase-2 artifact bundle carrying requirements and symbolic graph.
            spellbook:
                Spell registry used during annotation resolution.
            spell_system_states:
                Borrowed state registry for topology/dependency caching.
            cancel_event:
                Optional cooperative cancellation signal.

        Contracts:
            * Phases 1 and 2 must already have completed successfully. If
              requirements or symbolic graph are missing, this method raises
              instead of auto-running earlier phases.
            * Assumes the bound Spell is attached to a Spellbook; direct
              Spellbook map iteration is used for resolution.
            * Stores the local DAG and direct dependency list on the Spell via
              :meth:`Spell._add_build_details`, and keeps a
              :class:`SpellResolutionFrame` on this compiler artifact.
            * Does not return a value; callers rely on:
                  - `artifact._resolution_frame` for ordering, and
                  - SpellSystemStates for dependencies and topology.
        """
        artifact.check_cleaned()
        CompilerPhaseUtility.throw_if_cancelled(cancel_event)

        if artifact._requirements is None or artifact._symbolic_graph is None:
            raise RuntimeError(
                "SpellCrafter Phase 3: cannot build local frame before "
                "Phases 1-2 have completed."
            )

        required_spell_system_states = self._get_required_spell_system_states(
            spell_system_states
        )
        dag_with_dependencies = self._build_local_frame_dag(
            spell=spell,
            spellbook=spellbook,
            spell_system_states=required_spell_system_states,
            requirements=artifact._requirements,
            graph=artifact._symbolic_graph,
            cancellation_event=cancel_event,
            return_dependencies=True,
        )
        if not isinstance(dag_with_dependencies, tuple):
            raise RuntimeError(
                "SpellCrafter Phase 3 expected a DAG/dependency tuple when return_dependencies=True."
            )
        dag, dependency_spell_ids = dag_with_dependencies

        # Topological order of node ids (deps first, then root).
        ordered_node_ids = dag.collect_dependency_ids()

        artifact._resolution_frame = SpellResolutionFrame(
            spell_id=self._get_required_current_spell_id(spell),
            ordered_node_ids=ordered_node_ids,
        )

        # Persist dependency metadata on the Spell for validation and contract linking.
        unique_dependencies = list(dict.fromkeys(dependency_spell_ids))
        try:
            spell._add_build_details(
                dag=dag,
                dependencies=unique_dependencies,
            )
        except AttributeError:
            # Test stubs may not implement the build-details hook.
            pass
        SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)


