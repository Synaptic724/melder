import inspect
import types
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.bind.spell_index import SpellIndex
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
from melder.aether.spellbook.spell_compiler.validation.hidden_provider_report import HiddenProviderReport
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
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
        - Annotation matching is by annotation kind (2026-10-04; it superseded
          the 2026-10-03 address-key rule, which compared an annotation with a
          spell's address frame key as well as its type key): a DI annotation
          names `normalize_frame_key(annotation)`, and the table in
          `_spell_keys_for` decides which spell keys that key is compared
          against - a class with type keys, a Protocol with the contracts bind
          recorded, a name with type and contract keys on a single socket and
          with address labels on a collection. No identity comparison: a
          `TYPE_CHECKING`-only annotation (a string at runtime) resolves
          exactly as the class object does.
        - A class lookup reaches only a spell bound bare - no spellframe and
          the default binding (`_answers_class_lookup`; 2026-11-07, the owner's
          rulings E1-E3: Autofac's rule that a declared service hides the
          component's own type). That holds for a class annotation, a single
          string annotation's type part, `list[Class]` and `SpellMap(spell=X)`
          without a spellframe, existing objects alike, so injection and the
          class meld door give one answer. A spell bound under a spellframe is
          reached through the frame - Melder's interface dict, keyed by
          binding name - and a bare spell bound under a binding name through
          that name.
        - A class lookup that finds nothing records the spells of that class it
          does not reach - bound under a spellframe or a binding name - as the
          socket's hidden candidates (`_hidden_class_candidates`, the
          `by_hidden_type` bucket; 2026-11-07, patch hidden_provider_2026_11_07):
          Phase 4 refuses a single or SpellMap socket that carries them with
          HIDDEN_PROVIDER, and Phase 6 names them for an empty required
          `list[Class]`. Recording them changes nothing that resolves.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def _get_required_current_spell_id(
            self,
            spell: Spell,
    ) -> str:
        """
        Return the current bound spell_id or raise.

        Args:
            spell:
                Bound spell whose versioned identifier is required.

        Returns:
            str: Current spell_id.

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

    # Annotation kinds. Class-level constants (no module globals): the vocabulary
    # `_annotation_kind` returns and the matching table below is keyed on.
    _KIND_TYPE: ClassVar[str] = "type"
    _KIND_CONTRACT: ClassVar[str] = "contract"
    _KIND_NAME: ClassVar[str] = "name"

    @staticmethod
    def _annotation_key(annotation: Any) -> str:
        """
        Return the lowercased key a DI annotation names.

        Contract:
            A `ForwardRef` keys by its name; everything else keys through
            `SpellInputUtils.normalize_frame_key` - a class or Protocol by
            `__name__`, a string by itself, anything else by `str()` -
            lowercased, the normalization every spell address already uses.
            The key says WHAT NAME was written; `_annotation_kind` says what
            kind of thing it names, and the two together select the spell keys
            it is compared against.

        Args:
            annotation: The normalized annotation (Optional/Union unwrapped).

        Returns:
            str: The lowercased key.
        """
        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__
        return SpellInputUtils.normalize_frame_key(annotation)

    @classmethod
    def _annotation_kind(cls, annotation: Any) -> str:
        """
        Classify a normalized annotation as a contract, a type or a bare name.

        Contract (owner ruling 2026-10-03: a spellframe is a label; a Protocol
        frame is a label and a contract; an annotation names a type or a
        contract, never a category):
            - A Protocol class (`SpellInputUtils.is_protocol_type`) is
              `_KIND_CONTRACT`: the parameter asks for whatever bind checked
              against that Protocol.
            - Any other class is `_KIND_TYPE`: the parameter asks for instances
              of that class; an existing object counts through its class.
            - A string, a `ForwardRef` (a `TYPE_CHECKING`-only import leaves one
              at runtime) or anything else is `_KIND_NAME`: the kind cannot be
              told from the value, so the name is compared against every kind
              a name may stand for in that position - a type or a contract for
              a single socket, a label for a collection.

        Args:
            annotation: The normalized annotation (Optional/Union unwrapped).

        Returns:
            str: One of `_KIND_CONTRACT`, `_KIND_TYPE`, `_KIND_NAME`.
        """
        if inspect.isclass(annotation):
            if SpellInputUtils.is_protocol_type(annotation):
                return cls._KIND_CONTRACT
            return cls._KIND_TYPE
        return cls._KIND_NAME

    @staticmethod
    def _spell_type_key(spell_obj: Spell) -> str:
        """
        Return the spell's type key: its lowercased name.

        Contract:
            `spell_name` is a class's name, or for an existing object the name
            of its class (Bind records `type(obj).__name__`), so the type key is
            what a class annotation of that type keys to. Methods and lambdas
            carry their function name here; `require_class_spell` keeps them
            out of single resolution before this key is read.

        Args:
            spell_obj: The candidate spell.

        Returns:
            str: The lowercased type key.
        """
        return SpellInputUtils.normalize_frame_key(spell_obj.spell_name)

    @staticmethod
    def _answers_class_lookup(spell_obj: Spell) -> bool:
        """
        Return True when `spell_obj` answers a class lookup: bound bare, with no spellframe and the default binding.

        Contract (2026-11-07, the owner's rulings E1-E3; Autofac's rule that a
        declared service hides the component's own type):
            - A spellframe is the spell's interface - Melder's interface dict,
              keyed by binding name - so a spell bound under one (a string
              category or a Protocol) is reached through the frame (a Protocol
              annotation, `list[Protocol]`, `list["label"]`,
              `SpellMap(spellframe=..., binding_name=...)`,
              `meld(spellframe=..., binding_name=...)`), never by its class.
            - A binding name is a declared name, so a bare spell bound under one
              is reached by that name (`SpellMap(Class, binding_name=...)`,
              `meld(Class, binding_name=...)`), never by its class alone.
            - An existing object follows the same rule: its class is what a
              class lookup names.
            - The class meld door resolves a class only at its bare,
              default-binding address, so this keeps injection and the door one
              rule; and a class annotation's dependency key (its name, default
              binding) is then the address of every spell it can match.
            - Reads only bind-time fields (spellframe, binding name), which are
              pass-invariant; takes no lock.

        Args:
            spell_obj: The candidate spell.

        Returns:
            bool: True when the spell has no spellframe and its binding name
            normalizes to the default binding.
        """
        if spell_obj.spellframe is not None:
            return False
        return (
            SpellInputUtils.normalize_binding_name(spell_obj.binding_name)
            == SpellInputUtils.DEFAULT_BINDING_NAME
        )

    @staticmethod
    def _hidden_type_key(spell_obj: Spell) -> Optional[str]:
        """
        Return the type key a class lookup would compare for a spell it cannot reach, else None.

        Purpose:
            The one predicate of a hidden candidate (2026-11-07, patch
            hidden_provider_2026_11_07): a spell bound under a spellframe or a
            binding name carries its class's type key, but no class lookup
            reaches it (`_answers_class_lookup`). Phase 3's scan and its
            `by_hidden_type` bucket, `UnresolvedInputError`'s failure path and
            the change-control announcers (a framed spell's bind, notch or
            contract grant also announces this key) all read this method, so
            they agree on which spells are hidden.

        Contract:
            - None for a spell that answers a class lookup (bound bare, the
              default binding): it is reached, not hidden.
            - None for a spell whose bound object is itself a Protocol - a
              Protocol's own definition never counts as a hidden candidate (the
              owner's D5): a name naming the Protocol reaches it through its
              definition key whatever its binding.
            - Otherwise the spell's type key (`_spell_type_key`, its lowercased
              name), the key a class annotation of its class names.
            - Reads bind-time fields only (spellframe, binding name, spell
              name, the bound object); takes no lock.

        Args:
            spell_obj: The spell to classify.

        Returns:
            Optional[str]: The lowercased type key, or None.
        """
        if CompilerPhase3._answers_class_lookup(spell_obj):
            return None
        if CompilerPhase3._spell_definition_key(spell_obj) is not None:
            return None
        return CompilerPhase3._spell_type_key(spell_obj)

    @staticmethod
    def _spell_label_key(spell_obj: Spell) -> str:
        """
        Return the spell's address label: the frame key of its address.

        Contract:
            The spellframe's lowercased name (a string category as itself, a
            Protocol by `__name__`) when one was given, else the spell's own
            name - exactly the frame key `make_spell_key_from_parts` stores at
            bind. This is what a collection annotation written as a name
            gathers: the members of that label.

        Args:
            spell_obj: The candidate spell.

        Returns:
            str: The lowercased label key.
        """
        frame = spell_obj.spellframe
        if frame is None:
            return SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        return SpellInputUtils.normalize_frame_key(frame)

    @staticmethod
    def _spell_contract_keys(spell_obj: Spell) -> Tuple[str, ...]:
        """
        Return the lowercased names of the Protocols the spell was checked against.

        Contract:
            Read from `Spell.implemented_protocols`, which Bind fills with the
            Protocol spellframe when the frame kind is `contract` (one entry
            today; the field is the seam a later `implements=` would extend).
            Empty for a bare binding and for a string category, so a category
            can never be reached through a contract comparison.

        Args:
            spell_obj: The candidate spell.

        Returns:
            Tuple[str, ...]: Zero or more lowercased contract keys.
        """
        return tuple(
            SpellInputUtils.normalize_frame_key(protocol)
            for protocol in spell_obj.implemented_protocols
        )

    @staticmethod
    def _spell_definition_key(spell_obj: Spell) -> Optional[str]:
        """
        Return the type key of a spell that IS a Protocol - a descriptive definition - else None.

        Contract:
            A Protocol can be bound only with `resolvable=False` (Bind refuses it
            as a concrete spell); such a binding describes the contract itself so a
            consumer annotated with the Protocol compiles an OVERRIDE_REQUIRED socket
            the caller supplies. A Protocol annotation therefore also matches the
            Protocol's own definition by name, and the resolvers' resolvable
            preference picks a real implementer whenever one is recorded.

        Args:
            spell_obj: The candidate spell.

        Returns:
            Optional[str]: The lowercased type key when the bound object is a Protocol class.
        """
        if SpellInputUtils.is_protocol_type(spell_obj.spell):
            return SpellInputUtils.normalize_frame_key(spell_obj.spell_name)
        return None

    def _spell_keys_for(
            self,
            annotation_kind: str,
            spell_obj: Spell,
            *,
            collection: bool,
    ) -> Tuple[str, ...]:
        """
        Return the spell keys an annotation of `annotation_kind` is compared against.

        The matching table (single socket | collection):
            - type:     type key*                     | type key*
            - contract: contract keys + definition    | contract keys + definition
            - name:     type key* + contract keys     | label key
                        + definition
        "definition" is the type key of a spell that is itself a Protocol (bound
        `resolvable=False` as the contract's description). * The type key is
        offered only by a spell that answers a class lookup
        (`_answers_class_lookup`: no spellframe, the default binding;
        2026-11-07): a spell bound under a spellframe or a binding name offers
        no type key, so a class annotation, `list[Class]` and a single string
        annotation's type part never reach it, while its contract keys and its
        label stay reachable. A Protocol definition keeps its definition key on
        a single name socket whatever its binding: a string naming the Protocol
        is a contract lookup and finds the definition exactly as the Protocol
        object does (for a bare definition the definition key is its type key).
        A category label is reachable only through a collection written as a
        name (`list["storage"]`), never through a single socket, and a class
        annotation never reads a frame of any kind.

        Args:
            annotation_kind: One of the `_KIND_*` constants.
            spell_obj: The candidate spell.
            collection: True when resolving a COLLECTION_BY_ANNOTATION socket.

        Returns:
            Tuple[str, ...]: The keys to compare the annotation key against;
            empty when the spell cannot answer an annotation of this kind.
        """
        if annotation_kind == self._KIND_TYPE:
            if self._answers_class_lookup(spell_obj):
                return (self._spell_type_key(spell_obj),)
            return ()
        if annotation_kind == self._KIND_CONTRACT:
            definition_key = self._spell_definition_key(spell_obj)
            if definition_key is None:
                return self._spell_contract_keys(spell_obj)
            return self._spell_contract_keys(spell_obj) + (definition_key,)
        if collection:
            return (self._spell_label_key(spell_obj),)
        if self._answers_class_lookup(spell_obj):
            return (self._spell_type_key(spell_obj),) + self._spell_contract_keys(spell_obj)
        definition_key = self._spell_definition_key(spell_obj)
        if definition_key is None:
            return self._spell_contract_keys(spell_obj)
        # A name may stand for a contract: a Protocol's own definition answers it
        # whatever its binding, as `by_definition` answers the Protocol object.
        return self._spell_contract_keys(spell_obj) + (definition_key,)

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: Spell,
            *,
            require_class_spell: bool,
            collection: bool = False,
    ) -> bool:
        """
        Return True if `spell_obj` is a candidate for the given annotation.

        Matching strategy (by annotation kind, 2026-10-04):
            - Optional/Union wrappers were stripped by the caller; a ForwardRef
              keys by its name.
            - The annotation's key (`_annotation_key`) must equal one of the
              spell keys its kind selects (`_spell_keys_for`): a class
              annotation compares with the spell's type key; a Protocol
              annotation with the Protocols bind recorded on the spell; a string
              with the type or contract keys on a single socket and with the
              address label on a collection. Only a spell bound bare - no
              spellframe, the default binding - offers its type key
              (`_answers_class_lookup`, 2026-11-07). A spell under a string
              category is therefore reached, in a collection, by the category's
              name and never by its class - and never does the category's name
              make it a provider of a class spelled the same way; a spell under
              a Protocol is reached by the Protocol; a bare spell under a
              binding name by that name (SpellMap or meld), not here.
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
            collection:
                True for a COLLECTION_BY_ANNOTATION socket (a name gathers a label).

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

        kind = self._annotation_kind(annotation)
        if self._annotation_key(annotation) not in self._spell_keys_for(kind, spell_obj, collection=collection):
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
            key, which is exact for every pool (2026-10-03).

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
            bucket lookup per dependency. Three bucket maps, one per spell key
            kind - type, label, contract - so a lookup reads exactly the
            buckets the annotation's kind selects (`_spell_keys_for`); plus the
            definition bucket and, since 2026-11-07, the `by_hidden_type`
            bucket a class-lookup miss reads to name its hidden candidates
            (`_hidden_class_candidates`; resolution never reads it). Keys
            derive from pass-invariant inputs (binds are transactional and the
            resolution pass runs post-bind): spellframe, its kind and spell_name.

        Contract:
            - Entries are `(pool_position, spell_index, spell_obj)` so a bucket
              can be re-sorted into `_spell_id_pool` iteration order, keeping
              collection-injection order identical to the scan implementation.
            - Each spell that answers a class lookup (`_answers_class_lookup`:
              no spellframe, the default binding; 2026-11-07) is appended once
              to `by_type`; a spell bound under a spellframe or a binding name
              is not, exactly as `_spell_keys_for` offers it no type key.
              Every spell is appended once to `by_label` (the same key as its
              `by_type` key for a bare binding), once per recorded contract to
              `by_contract`, and - when the bound object is itself a Protocol -
              once to `by_definition` under its type key.
            - Each spell whose `_hidden_type_key` is not None (bound under a
              spellframe or a binding name, not a Protocol definition) is
              appended once to `by_hidden_type` under that key - the scan
              path's predicate, so both paths name the same hidden candidates.
            - Keys are strings and both paths apply the same predicate, so
              bucket membership equals scan membership for every pool; no
              equality guard is needed.

        Returns:
            Dict[str, Any]: `{"by_type": {...}, "by_label": {...}, "by_contract": {...},
            "by_definition": {...}, "by_hidden_type": {...}}`, each mapping a key to its list of entries.
        """
        by_type: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_label: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_contract: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_definition: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        by_hidden_type: Dict[str, List[Tuple[int, Any, Spell]]] = {}
        position = 0
        for index, spell_obj in self._iter_all_spells(spellbook):
            entry = (position, index, spell_obj)
            position += 1
            if self._answers_class_lookup(spell_obj):
                by_type.setdefault(self._spell_type_key(spell_obj), []).append(entry)
            by_label.setdefault(self._spell_label_key(spell_obj), []).append(entry)
            for key in self._spell_contract_keys(spell_obj):
                by_contract.setdefault(key, []).append(entry)
            definition_key = self._spell_definition_key(spell_obj)
            if definition_key is not None:
                by_definition.setdefault(definition_key, []).append(entry)
            hidden_key = self._hidden_type_key(spell_obj)
            if hidden_key is not None:
                by_hidden_type.setdefault(hidden_key, []).append(entry)
        return {
            "by_type": by_type,
            "by_label": by_label,
            "by_contract": by_contract,
            "by_definition": by_definition,
            "by_hidden_type": by_hidden_type,
        }

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

    def _index_buckets_for(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            collection: bool,
    ) -> Tuple[Optional[List[Tuple[int, Any, Spell]]], ...]:
        """
        Select the index bucket(s) an annotation reads, by the same table as `_spell_keys_for`.

        Args:
            candidate_index: The three-map index from `_build_candidate_index`.
            annotation: The normalized annotation.
            collection: True for a COLLECTION_BY_ANNOTATION socket.

        Returns:
            Tuple[Optional[List[...]], ...]: One bucket for a type or a
            collection-name lookup; the contract and definition buckets for a
            Protocol; the type, contract and definition buckets for a
            single-socket name. A missing bucket is None. `by_type` holds only
            spells that answer a class lookup (`_build_candidate_index`), so a
            type lookup and a single name's type part never see a spell bound
            under a spellframe or a binding name (2026-11-07); the definition
            bucket keeps a Protocol definition reachable by a name whatever its
            binding, as `_spell_keys_for` does on the scan path (a bare
            definition sits in both buckets under one key and is seen once).
        """
        key = self._annotation_key(annotation)
        kind = self._annotation_kind(annotation)
        if kind == self._KIND_TYPE:
            return (candidate_index["by_type"].get(key),)
        if kind == self._KIND_CONTRACT:
            return (candidate_index["by_contract"].get(key), candidate_index["by_definition"].get(key))
        if collection:
            return (candidate_index["by_label"].get(key),)
        return (
            candidate_index["by_type"].get(key),
            candidate_index["by_contract"].get(key),
            candidate_index["by_definition"].get(key),
        )

    def _indexed_annotation_candidates(
            self,
            candidate_index: Dict[str, Any],
            annotation: Any,
            *,
            require_class_spell: bool,
            collection: bool = False,
    ) -> Dict[Any, "Spell"]:
        """
        Bucket-lookup equivalent of the `_matches_annotation` scan.

        Contract:
            - Reads the bucket(s) `_index_buckets_for` selects for the
              annotation's kind and socket shape; membership equals scan
              membership because both sides use the same keys, the same table
              (2026-10-04) and the same class-lookup predicate (2026-11-07). An
              entry present in two buckets (a name that is both a type key and
              a contract key of one spell) is seen once.
            - `binding_name` filtering is omitted because both annotation
              resolvers pass None today (scan applies the filter only when a
              binding name is present).
            - `require_class_spell=True` applies the same METHOD/LAMBDA
              exclusions as the scan.
        """
        buckets = self._index_buckets_for(candidate_index, annotation, collection=collection)

        # Replicate the scan's dict semantics exactly: when one SpellIndex
        # matches through multiple pool entries (several of its versions), the scan
        # keeps the FIRST insertion position but the LAST matching spell
        # object (dict insert-then-overwrite).
        # collected: id(index) -> [first_pos, value_pos, index, spell_obj]
        collected: Dict[int, List[Any]] = {}
        for bucket in buckets:
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

        A class annotation selects spells of that class bound bare - no
        spellframe, the default binding (2026-11-07, `_answers_class_lookup`) -
        a Protocol annotation the spells bind recorded under it, a string either
        by name - never the members of a string category (2026-10-04,
        `_spell_keys_for`).
        Prefer matching resolvable providers. Only when none exist may a single
        non-resolvable definition be selected for an OVERRIDE_REQUIRED input.
        Matching and index grouping happen first; capability does not change them.
        When nothing matches at all, the mapping is empty: the caller records an
        UNRESOLVED_INPUT socket, which the constructing meld must supply. When
        the class is registered, but only under a spellframe or a binding name
        (which a class lookup does not reach), the caller also records those
        spells as the socket's hidden candidates and Phase 4 refuses the spell
        with HIDDEN_PROVIDER, naming where the class is bound (2026-11-07,
        `_hidden_class_candidates`). When
        several match, every candidate is returned (2026-10-04): the caller
        records an AMBIGUOUS_INPUT socket and Phase 4 refuses the spell with
        AMBIGUOUS_PROVIDER, naming the candidates and their addresses - the
        former RuntimeError never reached the readable report.

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
                registered spell matches the annotation; more than one entry
                when the annotation is ambiguous (a configuration error the
                caller records for Phase 4, never an input the meld could pick).
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
            # No spell answers this lookup. `_build_local_frame_dag` records an
            # UNRESOLVED_INPUT socket instead of failing resolution; the
            # constructing meld supplies the value or raises UnresolvedInputError
            # when this object is built - unless the class is bound only under a
            # spellframe or a binding name, which `_build_local_frame_dag` also
            # records (hidden candidates) and Phase 4 refuses (HIDDEN_PROVIDER).
            return {}

        # Several providers: returned as they are. `_build_local_frame_dag`
        # records the socket as AMBIGUOUS_INPUT and Phase 4's
        # AmbiguousProviderStrategy refuses the spell through the readable
        # report (owner decision 2026-10-04; this used to raise RuntimeError).
        return candidates

    def _resolve_collection_by_annotation(
            self,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
            candidate_index: Optional[Dict[str, Any]] = None,
    ) -> Dict[Any, Spell]:
        """
            Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
            spells (classes, methods, lambdas) in the group the annotation names.
            
            This corresponds to list[...]-style DI where the user explicitly
            asked for "all of them": `list[Proto]` gathers the spells recorded
            under that Protocol, `list["label"]` the members of that category
            (or the bare spells named so), `list[Cls]` the spells of that class
            bound bare - no spellframe, the default binding (2026-10-04 and
            2026-11-07, `_spell_keys_for`). Non-resolvable definitions are
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
                collection=True,
            )
        else:
            candidates = {}
            for index, spell_obj in self._iter_all_spells(spellbook):
                if self._matches_annotation(
                        annotation,
                        binding_name,
                        spell_obj,
                        require_class_spell=False,
                        collection=True,
                ):
                    candidates[index] = spell_obj

        return {index: candidate for index, candidate in candidates.items() if candidate.resolvable}

    def _hidden_class_candidates(
            self,
            spellbook: Spellbook,
            annotation: Any,
            *,
            candidate_index: Optional[Dict[str, Any]],
            collection: bool,
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        """
        Return the spells a class lookup that found nothing does not reach: the class bound under a spellframe or a binding name.

        Purpose:
            A class lookup reaches only a spell bound bare (2026-11-07). When
            one finds nothing, the spells of that class bound elsewhere are what
            the user most likely meant; Phase 3 records them on the socket
            (patch hidden_provider_2026_11_07) so Phase 4 can refuse the spell
            with HIDDEN_PROVIDER, naming each address and the lookup that
            reaches it, and Phase 6 can name them for an empty `list[Class]`.
            Called only after resolution came back empty: nothing here changes
            what resolves.

        Contract:
            - Empty for a Protocol annotation (a contract lookup, not a class
              lookup) and for a name annotation on a collection (a label
              lookup).
            - Otherwise the spells whose `_hidden_type_key` equals the
              annotation's key: from the `by_hidden_type` bucket on the index
              path, from a scan of `_iter_all_spells` on the scan path - one
              predicate, so both paths return the same candidates.
            - Single socket (`collection=False`): method and lambda spells are
              dropped, as the resolver drops them; non-resolvable framed
              definitions count (the owner's D5). Collection: only resolvable
              spells count, as the resolver gathers only those.
            - Read-only; takes no lock.

        Args:
            spellbook: The spellbook whose pool the scan path reads.
            annotation: The normalized annotation (`_normalize_annotation_for_matching`).
            candidate_index: The pass-scoped index, or None on the scan path.
            collection: True for a COLLECTION_BY_ANNOTATION socket.

        Returns:
            Tuple[Tuple[str, ...], Tuple[str, ...]]: The sorted hidden spell
            ids (one per SpellIndex, its selected id) and the sorted distinct
            address frame keys of those spells; both empty when none.
        """
        kind = self._annotation_kind(annotation)
        if kind == self._KIND_CONTRACT or (kind == self._KIND_NAME and collection):
            return (), ()
        key = self._annotation_key(annotation)
        if candidate_index is not None:
            pairs = [(index, spell_obj) for _, index, spell_obj in candidate_index["by_hidden_type"].get(key, ())]
        else:
            pairs = [
                (index, spell_obj) for index, spell_obj in self._iter_all_spells(spellbook)
                if self._hidden_type_key(spell_obj) == key
            ]
        kept: List[Tuple[SpellIndex, Spell]] = []
        for index, spell_obj in pairs:
            if collection:
                if not spell_obj.resolvable:
                    continue
            elif spell_obj.spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                continue
            kept.append((index, spell_obj))
        return self._hidden_ids_and_frames(kept)

    def _hidden_ids_and_frames(
            self,
            registrations: List[Tuple[SpellIndex, Spell]],
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        """
        Turn hidden registrations into the two descriptor tuples.

        Contract:
            - Ids: one per SpellIndex - its `selected_spell_id`, the version a
              lookup by address would answer - sorted, as AMBIGUOUS_INPUT
              records its candidates.
            - Frame keys: the distinct address frame keys of the registrations
              (`_spell_label_key`: the spellframe's key, or the spell's own name
              when bare - exactly what bind stores), sorted.

        Args:
            registrations: `(spell_index, spell)` pairs of hidden spells.

        Returns:
            Tuple[Tuple[str, ...], Tuple[str, ...]]: `(hidden_spell_ids, hidden_frame_keys)`.
        """
        ids = {index.selected_spell_id for index, _ in registrations}
        frame_keys = {self._spell_label_key(spell_obj) for _, spell_obj in registrations}
        return tuple(sorted(ids)), tuple(sorted(frame_keys))

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

    @staticmethod
    def _spellmap_frame_matches(spell_frame: Any, frame: Any) -> bool:
        """
        Return True when a spell's spellframe is the frame a SpellMap names.

        Contract:
            - Two string categories match by their normalized frame keys, the
              case-insensitive rule bind registers addresses with and meld looks
              them up by: "Agents" names the category bound as "agents"
              (2026-10-04, 0.2.8226; before, the two strings had to be equal).
            - Any other pair matches by identity or equality only, as before: a
              class or Protocol frame is that object, never a same-named string.

        Args:
            spell_frame:
                The candidate spell's recorded spellframe (None when bound bare).
            frame:
                The SpellMap's `spellframe`.

        Returns:
            bool: Whether the candidate sits under the SpellMap's frame.
        """
        if isinstance(spell_frame, str) and isinstance(frame, str):
            return SpellInputUtils.normalize_frame_key(spell_frame) == SpellInputUtils.normalize_frame_key(frame)
        return spell_frame is frame or spell_frame == frame

    def _resolve_spellmap_default(
            self,
            spell: Spell,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
            *,
            hidden_out: Optional[List[Tuple[SpellIndex, Spell]]] = None,
    ) -> Dict[Any, Spell]:
        """
        Resolve a SPELLMAP_DEFAULT dependency using the original SpellMap
        default attached to the parameter.

        Matching (2026-10-04, 0.2.8226):
            A SpellMap keeps the binding name as written, as Bind keeps a
            spell's, so names are compared by their normalized keys - the
            case-insensitive rule bind registers addresses with and meld looks
            them up by - and string spellframes the same way
            (`_spellmap_frame_matches`). `None` and "" both name the default
            binding. Before, the descriptor stored the lowercased name and this
            method compared it with the spell's raw one, so a binding name with
            a capital letter never resolved.

        Class lookup (2026-11-07, the owner's rulings E2-E3):
            `SpellMap(spell=X)` with no spellframe is a class lookup and follows
            `_answers_class_lookup`: it reaches only an X bound with no
            spellframe - with no binding_name given, only X under the default
            binding; with `binding_name=b`, only X bound bare under `b` (the
            named class lookup). Before, it reached X under any spellframe or
            binding name. `SpellMap(spell=X, spellframe=F, ...)` and the
            frame-addressed `SpellMap(spellframe=F, binding_name=b)` are
            unchanged: the frame is named, so the interface dict is read.

        Hidden provider (2026-11-07, patch hidden_provider_2026_11_07):
            When `SpellMap(spell=X)` without a spellframe finds nothing while X
            is registered at addresses that class lookup does not reach (under
            a spellframe, or bare under another binding name), the miss is the
            HIDDEN_PROVIDER shape. With `hidden_out` (Phase 3's own call) every
            such registration is appended to it and the mapping is empty: the
            caller records an UNRESOLVED_INPUT socket with those hidden
            candidates and Phase 4 refuses the spell through the readable
            report. Without `hidden_out` (a direct caller) the RuntimeError
            below is raised with one sentence appended naming where X is bound
            (`HiddenProviderReport.spellmap_runtime_suffix`). A miss with X
            registered nowhere, a frame-named miss and several candidates raise
            exactly as before.

        Args:
            spell:
                Consuming spell owning the dependency.
            spellbook:
                Spellbook used for candidate enumeration.
            dep:
                Dependency metadata containing spellmap defaults.
            hidden_out:
                Optional list that receives the `(spell_index, spell)`
                registrations of X when the HIDDEN_PROVIDER shape misses; None
                keeps the raising behaviour for direct callers.

        Returns:
            Dict[Any, Spell]:
                Mapping with exactly one resolved spell for the default; empty
                only when `hidden_out` received the hidden registrations.

        Raises:
            RuntimeError: If no candidate can be resolved (outside the recorded
                HIDDEN_PROVIDER shape) or multiple candidates satisfy the
                explicit default selection constraints.
        """
        spellmap = dep.spellmap_default
        if spellmap is None:
            return {}

        candidates: Dict[Any, Spell] = {}
        # Every registration of the explicit spell, reached or not: on a miss of
        # the class-lookup form these are its hidden candidates (2026-11-07).
        registrations: List[Tuple[SpellIndex, Spell]] = []
        explicit_spell = spellmap.spell
        frame = spellmap.spellframe
        binding_name = spellmap.binding_name
        # The key every candidate's binding name is compared with: bind and meld
        # address spells by this normalized form, never by the raw text.
        binding_key = SpellInputUtils.normalize_binding_name(binding_name)

        if explicit_spell is not None:
            for index, spell_obj in self._iter_all_spells(spellbook):
                if spell_obj.spell is not explicit_spell:
                    continue
                registrations.append((index, spell_obj))

                if frame is not None:
                    if not self._spellmap_frame_matches(spell_obj.spellframe, frame):
                        continue
                elif spell_obj.spellframe is not None:
                    # No spellframe named: a class lookup, which never reaches a
                    # spell bound under a spellframe (2026-11-07).
                    continue

                spell_binding_key = SpellInputUtils.normalize_binding_name(spell_obj.binding_name)
                if binding_name is not None:
                    if spell_binding_key != binding_key:
                        continue
                elif frame is None and spell_binding_key != SpellInputUtils.DEFAULT_BINDING_NAME:
                    # Neither spellframe nor binding_name named: the plain class
                    # lookup reaches only the default binding (2026-11-07); a
                    # named one is reached with `SpellMap(X, binding_name=...)`.
                    continue

                candidates[index] = spell_obj
        else:
            for index, spell_obj in self._iter_all_spells(spellbook):
                if (self._spellmap_frame_matches(spell_obj.spellframe, frame)
                        and SpellInputUtils.normalize_binding_name(spell_obj.binding_name) == binding_key):
                    candidates[index] = spell_obj

        if not candidates:
            message = (
                "SpellCrafter Phase 3: SpellMap default could not be resolved for "
                f"parameter {dep.param_name!r} on spell {spell.spell_name!r}. "
                f"SpellMap={spellmap!r}."
            )
            if frame is None and registrations:
                # The class-lookup form missed an X registered elsewhere: the
                # HIDDEN_PROVIDER shape (2026-11-07). Phase 3 records it for the
                # readable report; a direct caller gets where X is bound.
                if hidden_out is not None:
                    hidden_out.extend(registrations)
                    return {}
                message += " " + self._spellmap_hidden_sentence(explicit_spell, registrations)
            raise RuntimeError(message)

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

    @staticmethod
    def _spellmap_hidden_sentence(
            explicit_spell: object,
            registrations: List[Tuple[SpellIndex, Spell]],
    ) -> str:
        """
        Render the sentence a direct `_resolve_spellmap_default` caller's RuntimeError gains for the HIDDEN_PROVIDER shape.

        Contract:
            - One candidate per SpellIndex (its selected id, the last pooled
              version kept, as the resolvers keep it), rendered by
              `HiddenProviderReport` with SpellMap lookups: "X is bound only
              where this class lookup does not reach: <entries>."
            - Pure; reads bind-time fields only.

        Args:
            explicit_spell: The SpellMap's `spell` (X).
            registrations: Every `(spell_index, spell)` registration of X in the pool.

        Returns:
            str: The sentence.
        """
        by_id = {index.selected_spell_id: spell_obj for index, spell_obj in registrations}
        described = [HiddenProviderReport.describe(spell_id, spell_obj) for spell_id, spell_obj in by_id.items()]
        return HiddenProviderReport.spellmap_runtime_suffix(
            class_name=HiddenProviderReport.spell_display_name(explicit_spell),
            candidates=described,
        )

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

        di_shape = dep.di_shape
        if (
                di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
                or di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
        ):
            if dep.target_annotation is None:
                return None
            normalized_key: Tuple[str, str] = SpellInputUtils.normalize_spell_key(
                spellframe=self._normalize_annotation_for_matching(dep.target_annotation),
                binding_name=None,
            )
            return normalized_key

        return None

    def _record_unresolved_miss(
            self,
            spellbook: Spellbook,
            dep: SpellSymbolicDependency,
            candidate_index: Optional[Dict[str, Any]],
            spellmap_hidden: List[Tuple[SpellIndex, Spell]],
            *,
            socket_unresolved: Set[tuple[str, int]],
            socket_hidden: Dict[tuple[str, int], Tuple[Tuple[str, ...], Tuple[str, ...]]],
    ) -> None:
        """
        Record what a socket whose lookup found nothing becomes, and its hidden candidates.

        Purpose:
            The miss branch of `_build_local_frame_dag` (2026-11-07, patch
            hidden_provider_2026_11_07): a single typed socket stays an
            UNRESOLVED_INPUT as before, and a class lookup that missed a class
            bound only under a spellframe or a binding name also records those
            spells, so Phase 4 (single, SpellMap) or Phase 6 (an empty required
            collection) can name where the class is bound.

        Contract:
            - SINGLE_BY_ANNOTATION: always added to `socket_unresolved`; its
              hidden ids and frame keys are recorded when there are any.
              `Optional[Class]` without a default takes this path (still a
              required input).
            - COLLECTION_BY_ANNOTATION: nothing for an optional collection (it
              may legitimately wire nothing); a required one records its hidden
              ids only (no frame keys: the socket stays NORMAL and the consumer
              is not refused, so no watch is needed).
            - SPELLMAP_DEFAULT: reached empty only when
              `_resolve_spellmap_default` recorded `spellmap_hidden` instead of
              raising; the socket becomes UNRESOLVED_INPUT with the hidden ids
              and frame keys of those registrations.
            - Any other shape: nothing (metadata-only sockets).
            - Mutates only the two collections passed in; reads the pool or the
              pass-scoped index; takes no lock.

        Args:
            spellbook: The spellbook whose pool the scan path reads.
            dep: The dependency that resolved to nothing.
            candidate_index: The pass-scoped index, or None on the scan path.
            spellmap_hidden: The registrations `_resolve_spellmap_default` recorded (empty otherwise).
            socket_unresolved: Sockets to mark UNRESOLVED_INPUT; updated in place.
            socket_hidden: Hidden ids and frame keys per socket; updated in place.

        Returns:
            None.
        """
        key = (dep.param_name, dep.position)
        di_shape = dep.di_shape
        if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
            socket_unresolved.add(key)
            hidden = self._hidden_class_candidates(
                spellbook,
                self._normalize_annotation_for_matching(dep.target_annotation),
                candidate_index=candidate_index,
                collection=False,
            )
        elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
            if dep.is_optional:
                return
            hidden_ids, _ = self._hidden_class_candidates(
                spellbook,
                self._normalize_annotation_for_matching(dep.target_annotation),
                candidate_index=candidate_index,
                collection=True,
            )
            hidden = (hidden_ids, ())
        elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT and spellmap_hidden:
            socket_unresolved.add(key)
            hidden = self._hidden_ids_and_frames(spellmap_hidden)
        else:
            return
        if hidden[0]:
            socket_hidden[key] = hidden

    def _build_local_topology(
            self,
            spell: Spell,
            graph: SpellSymbolicGraph,
            socket_targets: Dict[tuple[str, int], List[str]],
            *,
            requirements: SpellRequirements,
            socket_references: Dict[tuple[str, int], List[str]],
            socket_unresolved: Optional[Set[tuple[str, int]]] = None,
            socket_ambiguous: Optional[Dict[tuple[str, int], List[str]]] = None,
            socket_hidden: Optional[Dict[tuple[str, int], Tuple[Tuple[str, ...], Tuple[str, ...]]]] = None,
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
                * Mark single typed sockets listed in "socket_ambiguous" (two or
                  more resolvable providers) AMBIGUOUS_INPUT, with the candidate
                  ids as descriptive `referenced_spell_ids` and no target; they
                  keep their dependency_key for the same re-gating (2026-10-04).
                * Copy "socket_hidden" (2026-11-07) onto its sockets as
                  `hidden_spell_ids` and `hidden_frame_keys`: an UNRESOLVED_INPUT
                  single or SpellMap socket whose class is bound only where a
                  class lookup does not reach (Phase 4 refuses it with
                  HIDDEN_PROVIDER) or an empty required class collection (Phase
                  6 names them). Every other socket keeps both empty.
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
            elif socket_ambiguous and (dep.param_name, dep.position) in socket_ambiguous:
                socket_kind = SocketKind.AMBIGUOUS_INPUT
                referenced_spell_ids = tuple(socket_ambiguous[(dep.param_name, dep.position)])
            dependency_key = None
            if spell.resolvable and socket_kind in (
                    SocketKind.NORMAL,
                    SocketKind.OVERRIDE_REQUIRED,
                    SocketKind.UNRESOLVED_INPUT,
                    SocketKind.AMBIGUOUS_INPUT,
            ):
                dependency_key = self._dependency_key_for_dep(dep)
            hidden_spell_ids: Tuple[str, ...] = ()
            hidden_frame_keys: Tuple[str, ...] = ()
            if socket_hidden and (dep.param_name, dep.position) in socket_hidden:
                hidden_spell_ids, hidden_frame_keys = socket_hidden[(dep.param_name, dep.position)]

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
                hidden_spell_ids=hidden_spell_ids,
                hidden_frame_keys=hidden_frame_keys,
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
                    If the spell has no bound SpellIndex / current spell id.
            
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
                * A class lookup that misses a class bound only under a
                  spellframe or a binding name records those spells as the
                  socket's hidden candidates (2026-11-07,
                  `_record_unresolved_miss`): a single socket and a
                  `SpellMap(spell=X)` without a spellframe become an
                  UNRESOLVED_INPUT socket that Phase 4 refuses with
                  HIDDEN_PROVIDER; an empty required `list[Class]` keeps its
                  NORMAL socket, which Phase 6 reports naming them.
                * A single typed dependency that several resolvable spells provide
                  produces an AMBIGUOUS_INPUT socket (no dependency id; the
                  candidates as references) instead of a RuntimeError, so Phase
                  4's AMBIGUOUS_PROVIDER refuses the spell through the readable
                  validation report (owner decision 2026-10-04).
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
        # Single typed sockets with several resolvable providers: recorded for
        # Phase 4 with their candidate ids, never resolved.
        socket_ambiguous: Dict[tuple[str, int], List[str]] = {}
        # Class-lookup misses whose class is bound only where the lookup does
        # not reach: (hidden ids, hidden frame keys) per socket (2026-11-07).
        socket_hidden: Dict[tuple[str, int], Tuple[Tuple[str, ...], Tuple[str, ...]]] = {}

        for dep in graph.dependencies if spell.resolvable else ():
            CompilerPhaseUtility.throw_if_cancelled(cancellation_event)

            di_shape = dep.di_shape
            # The registrations a `SpellMap(spell=X)` class lookup missed (filled
            # only when `_resolve_spellmap_default` records instead of raising).
            spellmap_hidden: List[Tuple[SpellIndex, Spell]] = []

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
                resolved = self._resolve_spellmap_default(spell, spellbook, dep, hidden_out=spellmap_hidden)
            else:
                # SpellContract / PLAIN and any future shapes
                # are currently metadata-only at the dependency level. They
                # still participate in the local topology below.
                resolved = {}

            key = (dep.param_name, dep.position)
            if not resolved:
                # Nothing answers this lookup: keep a single socket as an
                # unresolved input instead of failing resolution, and record the
                # class's hidden candidates where a class lookup missed them.
                self._record_unresolved_miss(
                    spellbook,
                    dep,
                    candidate_index,
                    spellmap_hidden,
                    socket_unresolved=socket_unresolved,
                    socket_hidden=socket_hidden,
                )
                continue
            if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION and len(resolved) > 1:
                # Several providers: record the candidates for Phase 4's
                # AMBIGUOUS_PROVIDER report; no dependency id, no edge.
                socket_ambiguous[key] = sorted(
                    spell_index.selected_spell_id for spell_index in resolved
                )
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
            socket_ambiguous=socket_ambiguous,
            socket_hidden=socket_hidden,
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


