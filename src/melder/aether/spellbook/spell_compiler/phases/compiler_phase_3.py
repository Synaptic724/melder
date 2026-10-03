import inspect
import types
import typing
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Set, Tuple, Union, get_args, get_origin

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
    from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
        SpellSymbolicDependency,
    )
    from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
        SpellSymbolicGraph,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.helpers.general_helpers import SpellInputUtils



class CompilerPhase3:
    """
    Compiler phase 3 surface.

    Purpose:
        Expose the current local-frame / DAG build behavior through a
        compiler-owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-3 behavior.
        - Annotation matching is by address key (2026-10-03): a DI annotation
          names `normalize_frame_key(annotation)`, and a spell is a candidate
          when that key is its address frame key (spellframe, else its own
          name) or its type key (`spell_name`; an existing object's class
          name). No identity comparison: a spellframe is a category or a
          shape label, never a type, and a `TYPE_CHECKING`-only annotation
          (a string at runtime) resolves exactly as the class object does.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def _get_required_current_spell_id(
            self,
            spell: Spell,
    ) -> str:
        """
        Return the current bound spell version id or raise.

        Args:
            spell:
                Bound spell whose versioned identifier is required.

        Returns:
            str: Current spell version id.

        Raises:
            RuntimeError: If the spell has no bound `spell_index.selected_spell_id`.

        """
        current_spell_id = spell.spell_index.selected_spell_id
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
            Iterate all visible spells via a copy of the Spellbook's spell_id_pool.
            
            Purpose:
                Provide a single internal iterator that Phase 3 can use for
                resolution without relying on any scanner wrapper.
            Contract:
                - Yields "(spell_index, spell)" in the insertion order of
                  "_spell_id_pool".
                - Iterates a copy of "_spell_id_pool" taken in one call when the
                  iteration starts. A concurrent bind, notch, contract grant or
                  transfer changes the live dict under the Spellbook lock, which
                  this pass does not hold (meld-time reruns run outside any
                  transaction); iterating it live raised "dictionary changed size
                  during iteration".
            Returns:
                Iterator[Tuple[SpellIndex, Spell]]: Stream over the copy.
        """
        for spell_instance in spellbook._spell_id_pool.copy().values():
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

    @staticmethod
    def _annotation_key(annotation: Any) -> str:
        """
        Return the address key a DI annotation names.

        Contract:
            A `ForwardRef` keys by its name; everything else keys through
            `SpellInputUtils.normalize_frame_key` - a class or Protocol by
            `__name__`, a string by itself, anything else by `str()` -
            lowercased, the normalization every spell address already uses.

        Args:
            annotation: The normalized annotation (Optional/Union unwrapped).

        Returns:
            str: The lowercased key.
        """
        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__
        return SpellInputUtils.normalize_frame_key(annotation)

    @staticmethod
    def _spell_keys(spell_obj: Spell) -> Tuple[str, ...]:
        """
        Return the keys a spell answers to: its address frame key and its type key.

        Contract:
            The frame key is the spellframe when one was given, else the spell's
            own name - exactly what `make_spell_key_from_parts` stores at bind.
            The type key is the spell's name: a class's name, or an existing
            object's class name. Equal keys collapse to one entry, so a bare
            binding answers to one key and a framed binding to two.

        Args:
            spell_obj: The candidate spell (any object with `spell_name` and `spellframe`).

        Returns:
            Tuple[str, ...]: One or two lowercased keys.
        """
        type_key = SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        frame = spell_obj.spellframe
        if frame is None:
            return (type_key,)
        frame_key = SpellInputUtils.normalize_frame_key(frame)
        if frame_key == type_key:
            return (type_key,)
        return (frame_key, type_key)

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: Spell,
            *,
            require_class_spell: bool,
    ) -> bool:
        """
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy (by address key, 2026-10-03):
            - Optional/Union wrappers were stripped by the caller; a ForwardRef
              keys by its name.
            - The annotation's key (`_annotation_key`) must equal one of the
              spell's keys (`_spell_keys`): its address frame key or its type
              key. A class-object annotation and its string spelling therefore
              resolve identically, an existing object is matched by its class,
              and a spellframe is a category or a shape label - never compared
              by object identity.
            - `binding_name`, when given, must equal the spell's binding name.
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

        if self._annotation_key(annotation) not in self._spell_keys(spell_obj):
            return False
        if binding_name is not None and spell_obj.binding_name != binding_name:
            return False
        return True

    @staticmethod
    def _eq_safe_object(candidate: Any) -> bool:
        """
        Return True when equality on `candidate` is provably identity/str-like.

        Purpose:
            The structural snapshot's replayability rule: it marks a pool
            non-replayable when a bound object or spellframe carries a custom
            `__eq__`. Phase 3 itself no longer needs it - its index matches by
            address key, which is exact for every pool (2026-10-03).

        Contract:
            - None, str, classes with the default `type.__eq__` metaclass
              behavior, and instances whose type uses `object.__eq__` are
              safe.
            - Anything else (custom `__eq__`, custom metaclass `__eq__`)
              flags the whole pass as eq-risky and disables the index so the
              original scan semantics are preserved byte-for-byte.
        """
        if candidate is None or isinstance(candidate, str):
            return True
        if isinstance(candidate, type):
            return type(candidate).__eq__ is type.__eq__
        return type(candidate).__eq__ is object.__eq__

    def _build_candidate_index(self, spellbook: Spellbook) -> Dict[str, Any]:
        """
        Build the pass-scoped phase-3 candidate index over the live pool.

        Purpose:
            Collapse the O(dependencies x spells) annotation scans into one
            bucket lookup per dependency. Bucket keys are the spells' address
            keys (`_spell_keys`), which derive from pass-invariant inputs
            (binds are transactional and the resolution pass runs post-bind):
            spellframe and spell_name.

        Contract:
            - Entries are `(pool_position, spell_index, spell_obj)` so a bucket
              can be re-sorted into `_spell_id_pool` iteration order, keeping
              collection-injection order identical to the scan implementation.
            - Each spell is appended once per distinct key (one or two).
            - Keys are strings, so bucket membership equals scan membership for
              every pool; no equality guard is needed (2026-10-03).

        Returns:
            Dict[str, Any]: `{"by_key": {key: [entries]}}`.
        """
        by_key: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        position = 0
        for index, spell_obj in self._iter_all_spells(spellbook):
            entry = (position, index, spell_obj)
            position += 1
            for key in self._spell_keys(spell_obj):
                by_key.setdefault(key, []).append(entry)
        return {"by_key": by_key}

    def _get_candidate_index(
            self,
            spellbook: Spellbook,
            resolution_pass_cache: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Return the usable pass-scoped candidate index, building it lazily.

        Contract:
            - Returns None (scan path) only when no pass cache was supplied;
              the key index is exact for every pool (2026-10-03).
            - Benign build race under multi-worker scheduling: the build is
              idempotent over pass-invariant inputs and the last writer wins
              with an equivalent value (same contract as the phase-4
              binding-graph memo in `validation_pass_cache`).
        """
        if resolution_pass_cache is None:
            return None
        index = resolution_pass_cache.get("phase3_candidate_index")
        if index is None:
            index = self._build_candidate_index(spellbook)
            resolution_pass_cache["phase3_candidate_index"] = index
        return index

    def _indexed_annotation_candidates(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            require_class_spell: bool,
    ) -> Dict[Any, "Spell"]:
        """
        Bucket-lookup equivalent of the `_matches_annotation` scan.

        Contract:
            - Reads the one bucket of the annotation's key (`_annotation_key`);
              membership equals scan membership because both sides use the
              same keys (2026-10-03).
            - `binding_name` filtering is omitted because both annotation
              resolvers pass None today (scan applies the filter only when a
              binding name is present).
            - `require_class_spell=True` applies the same METHOD/LAMBDA
              exclusions as the scan.
        """
        bucket = candidate_index["by_key"].get(self._annotation_key(annotation))

        # Replicate the scan's dict semantics exactly: when one SpellIndex
        # matches through multiple pool entries (version lineages), the scan
        # keeps the FIRST insertion position but the LAST matching spell
        # object (dict insert-then-overwrite).
        # collected: id(index) -> [first_pos, value_pos, index, spell_obj]
        collected: Dict[int, List[Any]] = {}
        for position, index, spell_obj in (bucket or ()):
            if require_class_spell and spell_obj.spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                continue
            record = collected.get(id(index))
            if record is None:
                collected[id(index)] = [position, position, index, spell_obj]
                continue
            if position < record[0]:
                record[0] = position
            if position > record[1]:
                record[1] = position
                record[3] = spell_obj

        ordered = sorted(collected.values(), key=lambda record: record[0])
        return {record[2]: record[3] for record in ordered}

    def _resolve_single_by_annotation(
            self,
            spell: Spell,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
            candidate_index: Optional[Dict[str, Any]] = None,
    ) -> Dict[Any, Spell]:
        """
        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        Prefer matching resolvable providers. Only when none exist may a single
        non-resolvable definition be selected for an OVERRIDE_REQUIRED input.
        Matching and index grouping happen first; capability does not change them.
        When nothing matches at all, the mapping is empty: the caller records an
        UNRESOLVED_INPUT socket, which the constructing meld must supply.

        Args:
            spell:
                Consuming spell owning the dependency.
            spellbook:
                Spellbook used for candidate enumeration.
            dep:
                Dependency metadata for this constructor parameter.

        Returns:
            Dict[Any, Spell]:
                Mapping from matched `spell_index` to spell. Empty when no
                registered spell matches the annotation.

        Raises:
            RuntimeError: If multiple candidates match the annotation
                constraints (ambiguity is a configuration error, not an input).
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        binding_name: Optional[str] = None

        if candidate_index is not None:
            candidates = self._indexed_annotation_candidates(
                candidate_index,
                annotation,
                require_class_spell=True,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=True,
                ):
                    candidates[index] = spell_obj

        resolvable_candidates = {
            index: candidate for index, candidate in candidates.items() if candidate.resolvable
        }
        if resolvable_candidates:
            candidates = resolvable_candidates

        if not candidates:
            # Nothing registered provides this type. `_build_local_frame_dag`
            # records an UNRESOLVED_INPUT socket instead of failing resolution;
            # the constructing meld supplies the value or raises
            # UnresolvedInputError when this object is built.
            return {}

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
            candidate_index: Optional[Dict[str, Any]] = None,
    ) -> Dict[Any, Spell]:
        """
            Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
            spells (classes, methods, lambdas) bound under the given frame/type.
            
            This corresponds to list[FrameType]-style DI where the user explicitly
            asked for "all implementations". Non-resolvable definitions are
            excluded after the existing matching and ordering decisions.
            
            Returns:
                Dict[SpellIndex, Spell]: mapping of all candidates. It is valid
                for this mapping to be empty (an empty collection will be injected).
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        binding_name: Optional[str] = None

        if candidate_index is not None:
            candidates = self._indexed_annotation_candidates(
                candidate_index,
                annotation,
                require_class_spell=False,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=False,
                ):
                    candidates[index] = spell_obj

        return {index: candidate for index, candidate in candidates.items() if candidate.resolvable}

    def _socket_kind_for_dep(self, dep: SpellSymbolicDependency) -> SocketKind:
        """
            Map a symbolic dependency's DI shape into a SocketKind.
            
            NORMAL:
                Regular DI parameter (annotation, SpellMap, collection) or a
                plain constructor socket.
            SPELL_CONTRACT:
                SpellContract socket - must be satisfied by a provider.
            For now, we classify based solely on `dep.di_shape`. If we later
            introduce additional DI shapes, this is the central mapping point.
        """
        di_shape = dep.di_shape

        if di_shape is ParameterDIShape.SPELL_CONTRACT:
            return SocketKind.SPELL_CONTRACT

        return SocketKind.NORMAL

    def _resolve_spellmap_default(
            self,
            spell: Spell,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, Spell]:
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
            Dict[Any, Spell]:
                Mapping with exactly one resolved spell for the default.

        Raises:
            RuntimeError: If no candidate can be resolved or multiple
                candidates satisfy the explicit default selection constraints.
        """
        spellmap = dep.spellmap_default
        if spellmap is None:
            return {}

        candidates: Dict[Any, Spell] = {}
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
                spellframe=self._normalize_annotation_for_matching(dep.target_annotation),
                binding_name=None,
            )
            return normalized_key

        return None

    def _build_local_topology(
            self,
            spell: Spell,
            graph: SpellSymbolicGraph,
            socket_targets: Dict[tuple[str, int], List[str]],
            *,
            requirements: SpellRequirements,
            socket_references: Dict[tuple[str, int], List[str]],
            socket_unresolved: Optional[Set[tuple[str, int]]] = None,
    ) -> SpellLocalTopology:
        """
            Internal helper for Phase 3.
            
            Construct a: class:`SpellLocalTopology` describing this Spell's
            constructor sockets, based on:
            
                * the symbolic dependencies from: class:`SpellSymbolicGraph`, and
                * the concrete dependency spell ids resolved during Phase 3.
            
            For each: class:`SpellSymbolicDependency`:
                * Determine declaration kind, then mark selected descriptive targets
                  OVERRIDE_REQUIRED without altering Phase-1/2 declaration facts.
                * Mark single typed sockets listed in "socket_unresolved" (no
                  registered provider at all) UNRESOLVED_INPUT. They keep their
                  dependency_key so a later matching bind re-resolves this spell.
                * Copy "is_collection" and "is_optional" flags from the
                  symbolic graph.
                * Look up any concrete targets via "socket_targets" using
                    "(param_name, position)". Normal DI sockets may have one or
                    many targets; contract and plain sockets will
                    typically have none at this phase.
                * Preserve contract metadata for SpellContract sockets.
                * Preserve reference IDs separately from executable targets and
                  copy the real parameter kind from Phase-1 requirements.
                * Create a: class:`SpellSocketDescriptor` for that parameter.
            
            The resulting: class:`SpellLocalTopology` is a per-spell, constructor-
            local view of sockets that later phases (blueprint assembly, override
            targeting, change-control) will consume. It is registered into: class:`SpellSystemStates` by Phase 3; this method does not talk to
            SpellSystemStates directly.
        """
        spell_id = self._get_required_current_spell_id(spell)
        descriptors: List[SpellSocketDescriptor] = []
        parameter_kinds = {param.name: param.kind.name for param in requirements.parameters}

        for dep in graph.dependencies:
            targets = socket_targets.get((dep.param_name, dep.position))
            if targets:
                target_spell_ids = tuple(targets)
            else:
                target_spell_ids = ()

            socket_kind = self._socket_kind_for_dep(dep)
            referenced_spell_ids = tuple(socket_references.get((dep.param_name, dep.position), ()))
            if referenced_spell_ids:
                socket_kind = SocketKind.OVERRIDE_REQUIRED
            elif socket_unresolved and (dep.param_name, dep.position) in socket_unresolved:
                socket_kind = SocketKind.UNRESOLVED_INPUT
            dependency_key = None
            if spell.resolvable and socket_kind in (
                    SocketKind.NORMAL,
                    SocketKind.OVERRIDE_REQUIRED,
                    SocketKind.UNRESOLVED_INPUT,
            ):
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
                referenced_spell_ids=referenced_spell_ids,
                parameter_kind=parameter_kinds.get(dep.param_name),
            )
            descriptors.append(descriptor)

        topology = SpellLocalTopology(
            spell_id=spell_id,
            sockets=descriptors,
        )
        return topology

    def _build_local_frame_dag(
            self,
            spell: Spell,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            requirements: SpellRequirements,
            graph: SpellSymbolicGraph,
            cancellation_event: Optional[CancellationEvent],
            *,
            resolution_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[str], List[str]]:
        """
            Internal helper for Phase 3.
            
            Resolve this Spell's **local frame** into id rows and emit constructor
            topology into SpellSystemStates.
            
            Responsibilities:
                * For each symbolic dependency:
                      - resolve normal DI shapes via direct Spellbook map iteration,
                      - record each resolved dependency spell id as a direct
                        dependency of the root (this spell).
                * Track, per constructor socket "(param_name, position)", the
                  concrete dependency spell ids resolved in this phase.
                * Build a: class:`SpellLocalTopology` from the symbolic graph plus
                  the per-socket targets.
                * Call into: class:`SpellSystemStates`:
                      - record direct dependency spell ids, and
                      - register the local topology for this Spell.
                * Compute the ordered local frame: the distinct dependency ids in
                  ascending id order, then the root id last. This is the order the
                  per-spell dependency DAG used to yield (dependencies first, ties
                  broken by id, root last); the graph object is no longer built.
            
            Returns:
                Tuple[List[str], List[str]]:
                    ``(ordered_node_ids, dependency_spell_ids)`` where
                    ``ordered_node_ids`` is the local frame order described above
                    and ``dependency_spell_ids`` lists the resolved dependency ids
                    in resolution order (a spell resolved through two sockets
                    appears twice; callers de-duplicate as needed).
            
            Raises:
                ValueError:
                    If ``requirements`` or ``graph`` is None.
                RuntimeError:
                    If the spell has no bound SpellIndex / current spell id, or
                    when annotation resolution is ambiguous (see the resolvers).
            
            Important:
                * This helper does **not** mutate the Spell object. All artifacts
                  (topology, dependency ids) remain in this SpellCrafter and
                  SpellSystemStates.
                * SpellContract sockets take part in the
                  symbolic graph and topology but do not produce dependency ids or
                  concrete targets at this stage.
                * Selected non-resolvable definitions produce reference-only
                  OVERRIDE_REQUIRED inputs. Non-resolvable roots retain their own
                  declarations/topology without resolving constructor requirements.
                * A single typed dependency that no registered spell provides
                  produces an UNRESOLVED_INPUT socket (no dependency id) instead of
                  failing: the constructing meld supplies it.
                * The per-socket target rows carry everything the retired DAG held
                  (parent id, child id, parameter name; every edge was NORMAL), so
                  no edge list is kept beside them.
                * A constructor that takes its own class resolves to the spell
                  itself. That self-resolution is RECORDED - in the dependency ids,
                  the socket targets, the registry and `Spell.dependencies` - and
                  kept out of the ordered frame, so Phase 4's SELF_DEPENDENCY check
                  refuses the spell through the readable validation report instead
                  of a Phase-3 abort (owner decision 2026-09-26; the retired DAG
                  raised ValueError here).
        """
        if requirements is None:
            raise ValueError("requirements must not be None.")
        if graph is None:
            raise ValueError("graph must not be None.")

        CompilerPhaseUtility.throw_if_cancelled(cancellation_event)

        if spell.spell_index is None:
            raise RuntimeError("SpellCrafter has no bound Spell with a SpellIndex.")

        root_id = self._get_required_current_spell_id(spell)

        # Pass-scoped candidate index (None -> original scan semantics).
        # Built lazily once per resolution pass; exact for every pool (key matching).
        candidate_index = (
            self._get_candidate_index(spellbook, resolution_pass_cache)
            if spell.resolvable else None
        )

        # Track all dependency spell IDs for SpellSystemStates.
        dependency_spell_ids: List[str] = []

        # Track per-socket resolutions for local topology:
        # keyed by (param_name, position) -> [spell_id, ...]
        socket_targets: Dict[tuple[str, int], List[str]] = {}
        socket_references: Dict[tuple[str, int], List[str]] = {}
        # Single typed sockets with no registered provider: recorded, not refused.
        socket_unresolved: Set[tuple[str, int]] = set()

        for dep in graph.dependencies if spell.resolvable else ():
            CompilerPhaseUtility.throw_if_cancelled(cancellation_event)

            di_shape = dep.di_shape

            # Only "normal" DI shapes produce concrete dependency ids for now.
            if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                resolved = self._resolve_single_by_annotation(
                    spell,
                    spellbook,
                    dep,
                    candidate_index,
                )
            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                resolved = self._resolve_collection_by_annotation(
                    spellbook,
                    dep,
                    candidate_index,
                )
            elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                resolved = self._resolve_spellmap_default(spell, spellbook, dep)
            else:
                # SpellContract / PLAIN and any future shapes
                # are currently metadata-only at the dependency level. They
                # still participate in the local topology below.
                resolved = {}

            key = (dep.param_name, dep.position)
            if not resolved:
                if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                    # Nothing registered provides this typed parameter; keep it
                    # as an unresolved input instead of failing resolution.
                    socket_unresolved.add(key)
                continue

            for spell_index, spell_obj in resolved.items():
                dep_spell_id = spell_index.selected_spell_id
                if not spell_obj.resolvable:
                    if (
                            di_shape is ParameterDIShape.SPELLMAP_DEFAULT
                            and dep.spellmap_default.override is not None
                    ):
                        raise RuntimeError(
                            f"Parameter {dep.param_name!r} on spell {spell.spell_name!r} selects "
                            f"non-resolvable definition {spell_obj.spell_name!r} with an override "
                            "construction payload. Remove that payload and supply the consumer "
                            "parameter through a meld override."
                        )
                    socket_references.setdefault(key, []).append(dep_spell_id)
                    continue
                # A self-resolution (dep_spell_id == root_id) is recorded like any
                # other dependency; Phase 4 reports it as SELF_DEPENDENCY.
                dependency_spell_ids.append(dep_spell_id)
                socket_targets.setdefault(key, []).append(dep_spell_id)

        # Snapshot local topology for this spell's constructor.
        topology = self._build_local_topology(
            spell, graph, socket_targets,
            requirements=requirements,
            socket_references=socket_references,
            socket_unresolved=socket_unresolved,
        )

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

        # Local frame order: distinct dependencies ascending by id, root last -
        # the topological order of the star graph phase 3 used to materialize.
        # A recorded self-resolution is not a frame node of its own.
        ordered_node_ids: List[str] = sorted(set(dependency_spell_ids) - {root_id})
        ordered_node_ids.append(root_id)
        return ordered_node_ids, dependency_spell_ids

    def run(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            cancel_event: Optional[CancellationEvent] = None,
            resolution_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Phase 3 - Resolve the local frame and constructor topology.

        Responsibilities:
            * Consume the Phase 2 symbolic graph and resolve each socket into
              concrete dependency spell ids.
            * Compute the ordered local frame rooted at this spell (resolved
              dependencies first, ascending by id; this spell last) as id rows -
              no per-spell graph object is built (retired 2026-09-26).
            * Build and register a :class:`SpellLocalTopology` describing the
              constructor sockets (normal sockets and SpellContract sockets)
              and the resolved target spell ids.
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
            * Stores the direct dependency list on the Spell via
              :meth:`Spell._add_build_details`, and keeps a
              :class:`SpellResolutionFrame` on this compiler artifact.
            * Does not return a value; callers rely on:
                  - `artifact._resolution_frame` for ordering, and
                  - SpellSystemStates for dependencies and topology.
            * Refreshes enabled post-conjure Nexus publication after topology exists;
              no projection refresh or runtime resolution is performed here.
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
        ordered_node_ids, dependency_spell_ids = self._build_local_frame_dag(
            spell=spell,
            spellbook=spellbook,
            spell_system_states=required_spell_system_states,
            requirements=artifact._requirements,
            graph=artifact._symbolic_graph,
            cancellation_event=cancel_event,
            resolution_pass_cache=resolution_pass_cache,
        )

        # Ordered local frame (deps first, then root) computed as rows.
        artifact._resolution_frame = SpellResolutionFrame(
            spell_id=self._get_required_current_spell_id(spell),
            ordered_node_ids=ordered_node_ids,
        )

        # Persist dependency metadata on the Spell for validation and contract linking.
        unique_dependencies = list(dict.fromkeys(dependency_spell_ids))
        try:
            spell._add_build_details(
                dependencies=unique_dependencies,
            )
        except AttributeError:
            # Test stubs may not implement the build-details hook.
            pass
        if spellbook._nexus_publish_enabled:
            spellbook._publish_spell_record_to_nexus(spell)
        # Eager phase2_5 IR capture removed (write-only; see compiler_phase_2).


