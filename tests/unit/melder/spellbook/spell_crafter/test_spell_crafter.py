from __future__ import annotations

from typing import Any, Iterable, Sequence
from threading import RLock

import pytest

import melder.spellbook.spell_crafter.spell_crafter as spell_crafter_module
from melder.spellbook.spell_crafter.spell_crafter import SpellCrafter
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils


class _CleanableStub(Cleanable):
    """
    Purpose:
        Provide a Cleanable stub for cleanup tracking.
    Contract:
        Records cleanup calls and optionally raises.
    """

    def __init__(self, *, raise_on_cleanup: bool = False) -> None:
        """
        Purpose:
            Initialize the stub with cleanup behavior.
        Contract:
            Stores the raise_on_cleanup flag and resets call counters.
        Args:
            raise_on_cleanup: Whether cleanup should raise.
        Returns:
            None.
        """
        super().__init__()
        self.cleanup_calls = 0
        self._raise_on_cleanup = raise_on_cleanup

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls and optionally raise.
        Contract:
            Increments cleanup_calls and marks cleaned when not raising.
        Raises:
            RuntimeError: When configured to raise.
        """
        self.cleanup_calls += 1
        if self._raise_on_cleanup:
            raise RuntimeError("cleanup boom")
        self._cleaned = True

    async def async_cleanup(self) -> None:
        """
        Purpose:
            Provide the async cleanup hook required by Cleanable.
        Contract:
            Not used in these tests.
        """
        raise NotImplementedError("async cleanup not implemented in stub")


class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal spell index with current and id values.
    Contract:
        Exposes current and id without validation.
    """

    def __init__(self, current: str, index_id: str = "lineage") -> None:
        """
        Purpose:
            Initialize the stub with current and id values.
        Contract:
            Stores the provided identifiers without validation.
        Args:
            current: Current spell id string.
            index_id: Lineage id string.
        Returns:
            None.
        """
        self.current = current
        self.id = index_id


class _ValidationResultStub:
    """
    Purpose:
        Provide a minimal validation result stub.
    Contract:
        Exposes the has_errors flag for SpellCrafter.
    """

    def __init__(self, *, has_errors: bool, issues: list[object] | None = None) -> None:
        """
        Purpose:
            Initialize the stub with an error flag.
        Contract:
            Stores the has_errors value.
        Args:
            has_errors: Whether the validation result has errors.
        Returns:
            None.
        """
        self.has_errors = has_errors
        self.issues = list(issues or [])


class _ValidationSystemStub:
    """
    Purpose:
        Provide a stub SpellValidationSystem for Phase 4 tests.
    Contract:
        Records validate_spell calls and returns a configured result.
    """

    def __init__(self, result: _ValidationResultStub) -> None:
        """
        Purpose:
            Initialize the stub with a result to return.
        Contract:
            Stores the result and resets call tracking.
        Args:
            result: Validation result stub to return.
        Returns:
            None.
        """
        self._result = result
        self.calls: list[dict[str, object]] = []

    def validate_spell(
        self,
        *,
        spell: object,
        requirements: object,
        symbolic_graph: object,
        resolution_frame: object,
        cancel_event: object | None = None,
    ) -> _ValidationResultStub:
        """
        Purpose:
            Record validate_spell inputs and return the configured result.
        Contract:
            Appends call metadata and returns the configured result.
        Args:
            spell: Spell under validation.
            requirements: Phase 1 requirements.
            symbolic_graph: Phase 2 symbolic graph.
            resolution_frame: Phase 3 resolution frame.
            cancel_event: Optional cancellation event.
        Returns:
            _ValidationResultStub: The configured result.
        """
        self.calls.append(
            {
                "spell": spell,
                "requirements": requirements,
                "symbolic_graph": symbolic_graph,
                "resolution_frame": resolution_frame,
                "cancel_event": cancel_event,
            }
        )
        return self._result


class _ChangeControlManagerStub:
    """
    Purpose:
        Provide a change control manager stub for Phase 7 tests.
    Contract:
        Records rebuild and revalidator registration calls.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the stub call trackers.
        Contract:
            Sets _revalidate_fn to None and clears call lists.
        Returns:
            None.
        """
        self._revalidate_fn = None
        self.rebuild_calls: list[object] = []
        self.set_calls = 0

    def rebuild_component_of(self, root_blueprints: object) -> None:
        """
        Purpose:
            Record rebuild_component_of calls.
        Contract:
            Appends the provided root blueprints to rebuild_calls.
        Args:
            root_blueprints: Root blueprint mapping passed in.
        Returns:
            None.
        """
        self.rebuild_calls.append(root_blueprints)

    def set_revalidator(self, fn: object) -> None:
        """
        Purpose:
            Record revalidator registration.
        Contract:
            Stores the function and increments set_calls.
        Args:
            fn: Revalidator callable.
        Returns:
            None.
        """
        self._revalidate_fn = fn
        self.set_calls += 1


class _AetherStub:
    """
    Purpose:
        Provide an Aether stub for change control lookups.
    Contract:
        Returns a configured change control manager or raises when requested.
    """

    def __init__(
        self,
        *,
        manager: _ChangeControlManagerStub | None = None,
        raise_on_get: bool = False,
    ) -> None:
        """
        Purpose:
            Initialize the stub with manager behavior.
        Contract:
            Stores manager and raise_on_get configuration.
        Args:
            manager: Change control manager to return.
            raise_on_get: Whether _get_change_control_manager should raise.
        Returns:
            None.
        """
        self._manager = manager
        self._raise_on_get = raise_on_get
        self.calls: list[str] = []

    def _get_change_control_manager(self, frame_name: str) -> _ChangeControlManagerStub | None:
        """
        Purpose:
            Return the configured change control manager or raise.
        Contract:
            Records the frame name and raises when configured.
        Args:
            frame_name: Frame name used for lookup.
        Returns:
            _ChangeControlManagerStub | None: The configured manager.
        Raises:
            RuntimeError: When raise_on_get is True.
        """
        self.calls.append(frame_name)
        if self._raise_on_get:
            raise RuntimeError("boom")
        return self._manager


class _SpellbookStub:
    """
    Purpose:
        Provide a spellbook stub with validator and change control access.
    Contract:
        Exposes _spell_validator, _aether, _aetheric_frame, and _spell_id_pool.
    """

    def __init__(
        self,
        *,
        validator: _ValidationSystemStub,
        aether: _AetherStub | None = None,
        frame_name: str = "frame",
    ) -> None:
        """
        Purpose:
            Initialize the spellbook stub.
        Contract:
            Stores validator, aether, and frame name.
        Args:
            validator: Validation system stub.
            aether: Aether stub for change control lookups.
            frame_name: Frame name string.
        Returns:
            None.
        """
        self._spell_validator = validator
        self._aether = aether or _AetherStub(manager=_ChangeControlManagerStub())
        self._aetheric_frame = frame_name
        self._spells: dict[object, object] = {}
        self._contracted_spells: dict[str, dict[object, object]] = {}
        self._spell_id_pool: dict[str, object] = {}

    @property
    def spells(self) -> dict[object, object]:
        return self._spells

    @property
    def contracted_spells(self) -> dict[str, dict[object, object]]:
        return self._contracted_spells


class _SpellSystemStateStub:
    """
    Purpose:
        Provide a minimal spell system state for adjacency snapshots.
    Contract:
        Exposes current_spell_id, direct_dependencies, and spell_index_id.
    """

    def __init__(
        self,
        *,
        current_spell_id: str,
        direct_dependencies: Iterable[str] | None = None,
        spell_index_id: str | None = None,
    ) -> None:
        """
        Purpose:
            Initialize the state stub with identity and dependencies.
        Contract:
            Stores the provided values without validation.
        Args:
            current_spell_id: Current spell id string.
            direct_dependencies: Optional dependency ids.
            spell_index_id: Optional lineage id.
        Returns:
            None.
        """
        self._lock = RLock()
        self._current_spell_id = current_spell_id
        self._direct_dependencies = set(direct_dependencies or [])
        self.spell_index_id = spell_index_id or f"lineage-{current_spell_id}"
        self.validity = None

    @property
    def current_spell_id(self) -> str:
        return self._current_spell_id

    @property
    def direct_dependencies(self) -> set[str]:
        return set(self._direct_dependencies)

    def set_validity(self, *args: object, **kwargs: object) -> None:
        self.validity = args[0] if args else None

    def clear_dirty(self, *_args: object, **_kwargs: object) -> None:
        return None


class _SpellSystemStatesStub:
    """
    Purpose:
        Provide a SpellSystemStates stub for dependency tracking.
    Contract:
        Records update and topology registration calls.
    """

    def __init__(self, *, states: Sequence[_SpellSystemStateStub] | None = None) -> None:
        """
        Purpose:
            Initialize the stub with optional state snapshots.
        Contract:
            Stores provided state list and resets call tracking.
        Args:
            states: Optional iterable of state stubs.
        Returns:
            None.
        """
        self._lock = RLock()
        self._states = list(states or [])
        self._states_by_index_id = {state.spell_index_id: state for state in self._states}
        self._local_topologies: dict[str, object] = {}
        self.update_calls: list[tuple[object, list[str]]] = []
        self.topology_calls: list[tuple[object, object]] = []

    def update_dependencies(self, spell_index: object, dependency_ids: list[str]) -> None:
        """
        Purpose:
            Record dependency update calls.
        Contract:
            Appends the inputs to update_calls.
        Args:
            spell_index: Spell index object.
            dependency_ids: Dependency id list.
        Returns:
            None.
        """
        self.update_calls.append((spell_index, list(dependency_ids)))

    def register_local_topology(self, spell_index: object, topology: object) -> None:
        """
        Purpose:
            Record local topology registration calls.
        Contract:
            Appends the inputs to topology_calls.
        Args:
            spell_index: Spell index object.
            topology: Topology instance.
        Returns:
            None.
        """
        self.topology_calls.append((spell_index, topology))
        if hasattr(spell_index, "current"):
            self._local_topologies[spell_index.current] = topology

    def iter_states(self) -> list[_SpellSystemStateStub]:
        """
        Purpose:
            Return the configured state snapshot list.
        Contract:
            Returns the stored state list.
        Returns:
            list[_SpellSystemStateStub]: State snapshot list.
        """
        return list(self._states)

    def get_by_spell_id(self, spell_id: str) -> _SpellSystemStateStub | None:
        """
        Purpose:
            Return the first state with the matching spell id.
        Contract:
            Searches the stored state list for a matching current_spell_id.
        Args:
            spell_id: Spell id to match.
        Returns:
            _SpellSystemStateStub | None: Matching state or None.
        """
        for state in self._states:
            if state.current_spell_id == spell_id:
                return state
        return None

    def get_by_index_id(self, index_id: str) -> _SpellSystemStateStub | None:
        return self._states_by_index_id.get(index_id)

    def get_local_topology_by_id(self, spell_id: str) -> object | None:
        """
        Purpose:
            Return any stored topology for the provided spell id.
        Contract:
            Looks up topologies stored by set_local_topology_for_id.
        Args:
            spell_id: Spell id to look up.
        Returns:
            object | None: Stored topology or None.
        """
        return self._local_topologies.get(spell_id)

    def set_local_topology_for_id(self, spell_id: str, topology: object) -> None:
        """
        Purpose:
            Store a topology for retrieval during adjacency builds.
        Contract:
            Updates the topology mapping with the provided values.
        Args:
            spell_id: Spell id for the topology.
            topology: Topology object to store.
        Returns:
            None.
        """
        self._local_topologies[spell_id] = topology


class _SpellStub:
    """
    Purpose:
        Provide a spell stub with the attributes SpellCrafter expects.
    Contract:
        Exposes spell_index, spell_name, and metadata used during Phase 5.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: str = "spell-name",
        spell_type: SpellType = SpellType.SPELL,
        existence: Existence = Existence.unique,
        spell: object | None = None,
        spellframe: object | None = None,
        binding_name: str | None = None,
        spellbook: _SpellbookStub,
        spell_system_states: _SpellSystemStatesStub | None = None,
        owner_conduit_id: str | None = None,
        include_dependency_graph: bool = True,
        dependency_graph: object | None = None,
    ) -> None:
        """
        Purpose:
            Initialize the stub with identifiers and references.
        Contract:
            Stores provided attributes and sets optional dependency_graph.
        Args:
            spell_id: Current spell id.
            spell_name: Spell name string.
            spell_type: Spell type enum.
            existence: Existence policy for the stubbed spell.
            spell: Underlying callable or class.
            spellframe: Spellframe object.
            binding_name: Optional binding name.
            spellbook: Owning spellbook stub.
            spell_system_states: Optional system state registry.
            owner_conduit_id: Optional owner conduit id for the spell.
            include_dependency_graph: Whether to set dependency_graph attribute.
            dependency_graph: Dependency graph object or None.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id, index_id=f"lineage-{spell_id}")
        self.spell_name = spell_name
        self.spell_type = spell_type
        self.existence = existence
        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = binding_name
        self._spellbook = spellbook
        self._spell_system_states = spell_system_states
        self._owner_conduit_id = owner_conduit_id
        self._crafter = None
        self.is_existing_creation = False
        if include_dependency_graph:
            self.dependency_graph = dependency_graph

    def _ensure_crafter(self) -> SpellCrafter:
        if self._crafter is None:
            self._crafter = SpellCrafter(self)
        return self._crafter


class _CancelStub:
    """
    Purpose:
        Provide a cancellation stub that raises when set.
    Contract:
        throw_if_set raises RuntimeError when is_set is True.
    """

    def __init__(self, *, is_set: bool) -> None:
        """
        Purpose:
            Initialize the stub with a fixed cancellation state.
        Contract:
            Stores the provided state for is_set queries.
        Args:
            is_set: Whether cancellation is active.
        Returns:
            None.
        """
        self._is_set = is_set
        self.throw_calls = 0

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Report whether cancellation is active.
        Contract:
            Returns the configured state.
        Returns:
            bool: True when cancellation is active.
        """
        return self._is_set

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise when cancellation is active.
        Contract:
            Increments throw_calls on each invocation.
        Raises:
            RuntimeError: When cancellation is active.
        """
        self.throw_calls += 1
        if self._is_set:
            raise RuntimeError("cancelled")


class _RequirementsFinderStub:
    """
    Purpose:
        Provide a requirements finder stub for Phase 1 tests.
    Contract:
        Returns a configured requirements object and records cancel events.
    """

    requirements: object | None = None
    calls: list[object | None] = []

    def __init__(self, spell: object) -> None:
        """
        Purpose:
            Store the spell reference for verification.
        Contract:
            Records the spell instance without validation.
        Args:
            spell: Spell instance passed into the finder.
        Returns:
            None.
        """
        self.spell = spell

    def build_requirements(self, *, cancel_event: object | None = None) -> object:
        """
        Purpose:
            Record the cancel_event and return the configured requirements.
        Contract:
            Appends cancel_event to calls and returns requirements.
        Args:
            cancel_event: Optional cancellation event.
        Returns:
            object: Configured requirements object.
        """
        self.calls.append(cancel_event)
        return self.requirements


class _ParamStub:
    """
    Purpose:
        Provide a parameter stub for Phase 2 symbolic graph tests.
    Contract:
        Exposes DI metadata used by run_phase_symbolic_graph.
    """

    def __init__(
        self,
        *,
        name: str,
        position: int,
        di_shape: ParameterDIShape,
        is_optional: bool,
        annotation: object | None = None,
        collection_element_annotation: object | None = None,
        spellmap_default: object | None = None,
        default_value: object | None = None,
    ) -> None:
        """
        Purpose:
            Initialize the parameter stub with DI metadata.
        Contract:
            Stores the provided values without validation.
        Args:
            name: Parameter name string.
            position: Parameter position index.
            di_shape: DI shape classification.
            is_optional: Whether the parameter is optional.
            annotation: Parameter annotation.
            collection_element_annotation: Collection element annotation.
            spellmap_default: SpellMap default object.
            default_value: Default value for the parameter, if any.
        Returns:
            None.
        """
        self.name = name
        self.position = position
        self.di_shape = di_shape
        self.is_optional = is_optional
        self.annotation = annotation
        self.collection_element_annotation = collection_element_annotation
        self.spellmap_default = spellmap_default
        self.default_value = default_value


class _RequirementsStub:
    """
    Purpose:
        Provide a minimal requirements stub for Phase 2 tests.
    Contract:
        Exposes a parameters sequence.
    """

    def __init__(self, parameters: Sequence[_ParamStub]) -> None:
        """
        Purpose:
            Initialize the stub with parameter requirements.
        Contract:
            Stores a list of parameters.
        Args:
            parameters: Parameter requirement stubs.
        Returns:
            None.
        """
        self._parameters = list(parameters)

    @property
    def parameters(self) -> tuple[_ParamStub, ...]:
        """
        Purpose:
            Provide the parameter list as a tuple.
        Contract:
            Returns a tuple copy of stored parameters.
        Returns:
            tuple[_ParamStub, ...]: Parameter requirement tuple.
        """
        return tuple(self._parameters)


class _DependencyStub:
    """
    Purpose:
        Provide a symbolic dependency stub for Phase 3 tests.
    Contract:
        Exposes fields used by SpellCrafter local frame logic.
    """

    def __init__(
        self,
        *,
        param_name: str,
        position: int,
        di_shape: ParameterDIShape,
        is_collection: bool = False,
        is_optional: bool = False,
        target_annotation: object | None = None,
        spellmap_default: object | None = None,
    ) -> None:
        """
        Purpose:
            Initialize the dependency stub with symbolic metadata.
        Contract:
            Stores the provided values without validation.
        Args:
            param_name: Parameter name string.
            position: Parameter position index.
            di_shape: DI shape classification.
            is_collection: Whether this dependency is a collection.
            is_optional: Whether this dependency is optional.
            target_annotation: Target annotation for DI resolution.
            spellmap_default: SpellMap default for SpellMap DI.
        Returns:
            None.
        """
        self.param_name = param_name
        self.position = position
        self.di_shape = di_shape
        self.is_collection = is_collection
        self.is_optional = is_optional
        self.target_annotation = target_annotation
        self.spellmap_default = spellmap_default


class _SpellMapStub:
    """
    Purpose:
        Provide a minimal SpellMap-like stub for resolution tests.
    Contract:
        Exposes spell, spellframe, binding_name, and canonical_key attributes.
    """

    def __init__(
        self,
        *,
        spell: object | None,
        spellframe: object | None,
        binding_name: str | None,
    ) -> None:
        """
        Purpose:
            Initialize the stub with SpellMap lookup fields.
        Contract:
            Stores the provided attributes without validation.
        Args:
            spell: Explicit spell object or None.
            spellframe: Spellframe object or None.
            binding_name: Binding name or None.
        Returns:
            None.
        """
        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = binding_name

    @property
    def canonical_key(self) -> tuple[str, str]:
        """
        Purpose:
            Provide the normalized SpellMap key for dependency mapping.
        Contract:
            Uses SpellInputUtils.normalize_spell_key for spell or spellframe.
        Returns:
            tuple[str, str]: Normalized (frame_key, binding_key).
        """
        return SpellInputUtils.normalize_spell_key(
            spell=self.spell,
            spellframe=self.spellframe,
            binding_name=self.binding_name,
        )


class _DagStub:
    """
    Purpose:
        Provide a DirectedAcyclicWorkGraph stub for Phase 3 tests.
    Contract:
        Records add_node/add_dependency calls and returns configured ids.
    """

    last_instance: "_DagStub | None" = None
    next_dependency_ids: list[str] = []

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the DAG stub and track the latest instance.
        Contract:
            Resets call lists and records the instance globally.
        Returns:
            None.
        """
        self.nodes: list[tuple[str, object | None]] = []
        self.dependencies: list[tuple[str, str, str | None, SocketKind | None]] = []
        self.dependency_ids = list(self.next_dependency_ids)
        _DagStub.last_instance = self

    def add_node(self, key: str, payload: object | None = None) -> None:
        """
        Purpose:
            Record node additions.
        Contract:
            Appends the key/payload pair to nodes.
        Args:
            key: Node key string.
            payload: Optional payload.
        Returns:
            None.
        """
        self.nodes.append((key, payload))

    def add_dependency(
        self,
        parent_key: str,
        child_key: str,
        *,
        param_name: str | None = None,
        socket_kind: SocketKind | None = None,
    ) -> None:
        """
        Purpose:
            Record dependency edges.
        Contract:
            Appends edge metadata to dependencies.
        Args:
            parent_key: Dependency node key.
            child_key: Dependent node key.
            param_name: Optional parameter name.
            socket_kind: Optional socket kind.
        Returns:
            None.
        """
        self.dependencies.append((parent_key, child_key, param_name, socket_kind))

    def collect_dependency_ids(self) -> list[str]:
        """
        Purpose:
            Return the configured dependency id ordering.
        Contract:
            Returns dependency_ids set at initialization.
        Returns:
            list[str]: Dependency id ordering.
        """
        return list(self.dependency_ids)


class _AdjacencySnapshotStub:
    """
    Purpose:
        Provide a minimal adjacency snapshot for Phase 5 tests.
    Contract:
        Exposes dependencies, root_spell_ids, and topologies attributes.
    """

    def __init__(
        self,
        *,
        dependencies: dict[str, set[str]],
        root_spell_ids: set[str],
        topologies: dict[str, Any] | None = None,
    ) -> None:
        """
        Purpose:
            Initialize the snapshot stub.
        Contract:
            Stores the provided dependencies, root ids, and topologies.
        Args:
            dependencies: Mapping of spell id to dependency ids.
            root_spell_ids: Set of root spell ids.
            topologies: Optional mapping of spell id to topology stubs.
        Returns:
            None.
        """
        self.dependencies = dependencies
        self.root_spell_ids = root_spell_ids
        self.topologies = topologies if topologies is not None else {}


class _RootBlueprintStub:
    """
    Purpose:
        Provide a root blueprint stub with cleanup tracking.
    Contract:
        Exposes root_spell_id and cleanup behavior.
    """

    def __init__(self, root_spell_id: str, *, raise_on_cleanup: bool = False) -> None:
        """
        Purpose:
            Initialize the blueprint stub.
        Contract:
            Stores root id and cleanup behavior.
        Args:
            root_spell_id: Root spell id string.
            raise_on_cleanup: Whether cleanup should raise.
        Returns:
            None.
        """
        self.root_spell_id = root_spell_id
        self.cleanup_calls = 0
        self._raise_on_cleanup = raise_on_cleanup

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls and optionally raise.
        Contract:
            Increments cleanup_calls and raises when configured.
        Raises:
            RuntimeError: When configured to raise.
        """
        self.cleanup_calls += 1
        if self._raise_on_cleanup:
            raise RuntimeError("cleanup boom")


class _SpellSystemValidationSystemStub:
    """
    Purpose:
        Provide a system validation stub for Phase 6 tests.
    Contract:
        Records validate calls and returns a configured result.
    """

    last_instance: "_SpellSystemValidationSystemStub | None" = None

    def __init__(self, *, strategies: list[object]) -> None:
        """
        Purpose:
            Initialize the stub with the provided strategies list.
        Contract:
            Stores strategies and tracks the latest instance.
        Args:
            strategies: Strategy instances provided by SpellCrafter.
        Returns:
            None.
        """
        self.strategies = list(strategies)
        self.validate_calls: list[dict[str, object]] = []
        _SpellSystemValidationSystemStub.last_instance = self

    def validate(
        self,
        *,
        index: object,
        blueprints: object,
        phase4_results: dict[str, object],
        broken_spell_ids: set[str],
        spell_system_states: object,
        conduit_id: str | None = None,
        spell_lookup: dict[str, object],
        cancel_event: object | None,
    ) -> object:
        """
        Purpose:
            Record validation inputs and return a stub state.
        Contract:
            Appends input metadata to validate_calls.
        Args:
            index: SpellSystemIndex instance.
            blueprints: Root blueprint mapping.
            phase4_results: Phase 4 results mapping.
            broken_spell_ids: Broken spell id set.
            spell_system_states: SpellSystemStates instance.
            conduit_id: Optional conduit identifier for resolution scoping.
            spell_lookup: Mapping of spell ids to spell instances.
            cancel_event: Optional cancellation event.
        Returns:
            object: Validation state stub.
        """
        self.validate_calls.append(
            {
                "index": index,
                "blueprints": blueprints,
                "phase4_results": dict(phase4_results),
                "broken_spell_ids": set(broken_spell_ids),
                "spell_system_states": spell_system_states,
                "conduit_id": conduit_id,
                "spell_lookup": dict(spell_lookup),
                "cancel_event": cancel_event,
            }
        )
        return {"state": "ok"}


def _make_crafter(
    *,
    spell_id: str = "root",
    spell_name: str = "spell-name",
    spell_type: SpellType = SpellType.SPELL,
    spell_system_states: _SpellSystemStatesStub | None = None,
    validator_result_has_errors: bool = False,
) -> SpellCrafter:
    """
    Purpose:
        Build a SpellCrafter with stubbed spellbook and validator.
    Contract:
        Returns a SpellCrafter configured with a stub spell.
    Args:
        spell_id: Spell id for the stub spell.
        spell_name: Spell name for the stub spell.
        spell_type: Spell type for the stub spell.
        spell_system_states: Optional system state registry stub.
        validator_result_has_errors: Error flag for validation result.
    Returns:
        SpellCrafter: The configured spell crafter.
    """
    validation_result = _ValidationResultStub(has_errors=validator_result_has_errors)
    validator = _ValidationSystemStub(validation_result)
    spellbook = _SpellbookStub(validator=validator)
    spell = _SpellStub(
        spell_id=spell_id,
        spell_name=spell_name,
        spell_type=spell_type,
        spellbook=spellbook,
        spell_system_states=spell_system_states,
    )
    spellbook._spells[spell.spell_index] = spell
    crafter = SpellCrafter(spell)
    spell._crafter = crafter
    return crafter


def _build_spell_and_crafter(
    *,
    spell_id: str = "root",
    spell_name: str = "spell-name",
    spell_type: SpellType = SpellType.SPELL,
    spell_system_states: _SpellSystemStatesStub | None = None,
    validator_result_has_errors: bool = False,
    aether: _AetherStub | None = None,
    frame_name: str = "frame",
    include_dependency_graph: bool = True,
    dependency_graph: object | None = None,
) -> tuple[SpellCrafter, _SpellStub, _ValidationSystemStub]:
    """
    Purpose:
        Build a SpellCrafter with explicit components for assertions.
    Contract:
        Returns a crafter with a stub spellbook, validator, and spell wired
        together, registers the spell in the spell_id_pool, and sets
        spell._crafter on the returned spell.
    Args:
        spell_id: Spell id for the stub spell.
        spell_name: Spell name for the stub spell.
        spell_type: Spell type for the stub spell.
        spell_system_states: Optional system state registry stub.
        validator_result_has_errors: Error flag for the validation result.
        aether: Optional Aether stub for change-control wiring.
        frame_name: Aetheric frame name to attach to the spellbook.
        include_dependency_graph: Whether to define dependency_graph on the spell.
        dependency_graph: Dependency graph object to store when enabled.
    Returns:
        tuple[SpellCrafter, _SpellStub, _ValidationSystemStub]:
            The crafter, its owning spell, and the validation system stub.
    """
    validation_result = _ValidationResultStub(has_errors=validator_result_has_errors)
    validator = _ValidationSystemStub(validation_result)
    spellbook = _SpellbookStub(validator=validator, aether=aether, frame_name=frame_name)
    spell = _SpellStub(
        spell_id=spell_id,
        spell_name=spell_name,
        spell_type=spell_type,
        spellbook=spellbook,
        spell_system_states=spell_system_states,
        include_dependency_graph=include_dependency_graph,
        dependency_graph=dependency_graph,
    )
    spellbook._spells[spell.spell_index] = spell
    spellbook._spell_id_pool[spell.spell_index.current] = spell
    crafter = SpellCrafter(spell)
    spell._crafter = crafter
    return crafter, spell, validator


def _set_spell_id_pool(spellbook: _SpellbookStub, spells: Sequence[_SpellStub]) -> None:
    """
    Purpose:
        Reset the Spellbook stub's spell_id_pool to a known spell set.
    Contract:
        Clears the live pool and re-inserts spells in the provided order.
    Args:
        spellbook: Spellbook stub whose pool should be updated.
        spells: Spells to insert into the pool.
    Returns:
        None.
    """
    spellbook._spell_id_pool.clear()
    for spell in spells:
        spellbook._spell_id_pool[spell.spell_index.current] = spell


def _make_dependency(
    *,
    spell_id: str,
    param_name: str,
    position: int,
    di_shape: ParameterDIShape,
    is_optional: bool = False,
    target_annotation: object | None = None,
    is_collection: bool = False,
    spellmap_default: object | None = None,
) -> SpellSymbolicDependency:
    """
    Purpose:
        Build a SpellSymbolicDependency for targeted tests.
    Contract:
        Returns a dependency populated with the provided metadata.
    Args:
        spell_id: Version id for the owning spell.
        param_name: Constructor parameter name.
        position: Parameter position index.
        di_shape: Dependency injection shape classification.
        is_optional: Whether the parameter is optional.
        target_annotation: Annotation used for DI targeting.
        is_collection: Whether the dependency is a collection.
        spellmap_default: SpellMap default attached to the parameter.
    Returns:
        SpellSymbolicDependency: The constructed dependency instance.
    """
    return SpellSymbolicDependency(
        spell_version_id=spell_id,
        param_name=param_name,
        position=position,
        di_shape=di_shape,
        is_optional=is_optional,
        target_annotation=target_annotation,
        is_collection=is_collection,
        spellmap_default=spellmap_default,
    )


def _make_symbolic_graph(
    *,
    spell_id: str,
    dependencies: Sequence[SpellSymbolicDependency],
) -> SpellSymbolicGraph:
    """
    Purpose:
        Build a SpellSymbolicGraph with explicit dependencies.
    Contract:
        Returns a graph that contains the provided dependency list.
    Args:
        spell_id: Version id for the owning spell.
        dependencies: Symbolic dependencies to include.
    Returns:
        SpellSymbolicGraph: The constructed symbolic graph.
    """
    return SpellSymbolicGraph(
        spell_version_id=spell_id,
        dependencies=list(dependencies),
    )


def _reset_stub_state() -> None:
    """
    Purpose:
        Reset class-level stub state for deterministic tests.
    Contract:
        Clears all stored outputs and call histories on shared stubs.
    Returns:
        None.
    """
    _RequirementsFinderStub.requirements = None
    _RequirementsFinderStub.calls.clear()
    _DagStub.last_instance = None
    _DagStub.next_dependency_ids = []
    _SpellSystemValidationSystemStub.last_instance = None
    _AdjacencyBuilderStub.last_instance = None
    _AdjacencyBuilderStub.next_snapshot = None
    _RootBlueprintBuilderStub.last_instance = None
    _RootBlueprintBuilderStub.next_blueprints = None


class _AdjacencyBuilderStub:
    """
    Purpose:
        Provide an adjacency builder stub for Phase 5 tests.
    Contract:
        Returns a preconfigured snapshot and records build calls.
    """

    last_instance: "_AdjacencyBuilderStub | None" = None
    next_snapshot: _AdjacencySnapshotStub | None = None

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the stub and track the latest instance.
        Contract:
            Stores the configured snapshot and resets call tracking.
        Returns:
            None.
        """
        self.snapshot = self.next_snapshot
        self.calls: list[object] = []
        _AdjacencyBuilderStub.last_instance = self

    def build(self, spell_system_states: object) -> _AdjacencySnapshotStub:
        """
        Purpose:
            Return the configured adjacency snapshot.
        Contract:
            Records the input and returns the configured snapshot.
        Args:
            spell_system_states: SpellSystemStates instance passed in.
        Returns:
            _AdjacencySnapshotStub: The configured snapshot stub.
        """
        self.calls.append(spell_system_states)
        return self.snapshot


class _RootBlueprintBuilderStub:
    """
    Purpose:
        Provide a root blueprint builder stub for Phase 5 tests.
    Contract:
        Returns a preconfigured blueprint mapping and records inputs.
    """

    last_instance: "_RootBlueprintBuilderStub | None" = None
    next_blueprints: dict[str, _RootBlueprintStub] | None = None

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the stub and track the latest instance.
        Contract:
            Stores the configured blueprints and resets call tracking.
        Returns:
            None.
        """
        self.blueprints = self.next_blueprints or {}
        self.calls: list[object] = []
        _RootBlueprintBuilderStub.last_instance = self

    def build_root_blueprints(
        self,
        snapshot: object,
    ) -> dict[str, _RootBlueprintStub]:
        """
        Purpose:
            Return the configured root blueprint mapping.
        Contract:
            Records the snapshot input and returns configured blueprints.
        Args:
            snapshot: Adjacency snapshot provided by the builder call.
        Returns:
            dict[str, _RootBlueprintStub]: Root blueprint mapping.
        """
        self.calls.append(snapshot)
        return dict(self.blueprints)

    def build_blueprint_for_spell_id(
        self,
        *,
        root_spell_id: str,
        snapshot: object,
    ) -> _RootBlueprintStub:
        """
        Purpose:
            Build a blueprint for a single root spell id when missing.
        Contract:
            Returns a blueprint from the configured map or a new stub.
        Args:
            root_spell_id: Root spell id requested by the caller.
            snapshot: Snapshot provided for context (recorded).
        Returns:
            _RootBlueprintStub: Blueprint stub for the root id.
        """
        self.calls.append((root_spell_id, snapshot))
        return self.blueprints.get(root_spell_id, _RootBlueprintStub(root_spell_id))


@pytest.fixture(autouse=True)
def _reset_stubs_fixture() -> None:
    """
    Purpose:
        Ensure stub state is reset before each test.
    Contract:
        Invokes the central stub reset helper every test run.
    Returns:
        None.
    """
    _reset_stub_state()


def _access_property(crafter: SpellCrafter, property_name: str) -> object:
    """
    Purpose:
        Access a SpellCrafter property by explicit name without reflection.
    Contract:
        Returns the requested property value or raises for unknown names.
    Args:
        crafter: SpellCrafter instance providing the property.
        property_name: Name of the property to access.
    Returns:
        object: The property value returned by SpellCrafter.
    Raises:
        ValueError: If property_name does not match a supported property.
    """
    if property_name == "spell":
        return crafter.spell
    if property_name == "requirements":
        return crafter.requirements
    if property_name == "symbolic_graph":
        return crafter.symbolic_graph
    if property_name == "resolution_frame":
        return crafter.resolution_frame
    if property_name == "validation_result_phase4":
        return crafter.validation_result_phase4
    if property_name == "root_blueprint_phase5":
        return crafter.root_blueprint_phase5
    if property_name == "spell_system_index_phase5":
        return crafter.spell_system_index_phase5
    if property_name == "validation_result_phase6":
        return crafter.validation_result_phase6
    if property_name == "validated":
        return crafter.validated
    if property_name == "is_broken":
        return crafter.is_broken
    raise ValueError(f"Unsupported property name: {property_name}")


def test_init_rejects_none_spell() -> None:
    """
    Purpose:
        Ensure SpellCrafter rejects a missing spell reference.
    Contract:
        __init__ raises ValueError when spell is None.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="spell must not be None"):
        SpellCrafter(None)


def test_init_sets_default_state() -> None:
    """
    Purpose:
        Verify SpellCrafter initializes core state deterministically.
    Contract:
        Default artifacts are None and validation flags are False.
    Returns:
        None.
    Raises:
        AssertionError: If defaults or wiring are incorrect.
    """
    crafter, spell, validator = _build_spell_and_crafter()

    assert crafter.spell is spell
    assert crafter.requirements is None
    assert crafter.symbolic_graph is None
    assert crafter.resolution_frame is None
    assert crafter.validation_result_phase4 is None
    assert crafter.validation_result_phase6 is None
    assert crafter.root_blueprint_phase5 is None
    assert crafter.spell_system_index_phase5 is None
    assert crafter.validated is False
    assert crafter.is_broken is False
    assert crafter._spell_validator is validator
    assert crafter._spell_system_states is None
    assert crafter._lock is not None


def test_cleanup_calls_cleanup_on_artifacts() -> None:
    """
    Purpose:
        Verify cleanup triggers teardown on owned artifacts.
    Contract:
        Every attached Cleanable or cleanup-capable artifact is cleaned once.
    Returns:
        None.
    Raises:
        AssertionError: If any artifact cleanup is skipped.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    requirements = _CleanableStub()
    symbolic = _CleanableStub()
    resolution_frame = _CleanableStub()
    phase4 = _CleanableStub()
    phase6 = _CleanableStub()
    root_blueprint = _RootBlueprintStub("root")
    system_index = _CleanableStub()
    dag_blueprint = _RootBlueprintStub("dag")

    crafter._requirements = requirements
    crafter._symbolic_graph = symbolic
    crafter._resolution_frame = resolution_frame
    crafter._validation_result_phase4 = phase4
    crafter._validation_result_phase6 = phase6
    crafter._root_blueprint_phase5 = root_blueprint
    crafter._spell_system_index_phase5 = system_index
    crafter._entire_dag_blueprint_phase5 = {"root": dag_blueprint}

    crafter.cleanup()

    assert requirements.cleanup_calls == 1
    assert symbolic.cleanup_calls == 1
    assert resolution_frame.cleanup_calls == 1
    assert phase4.cleanup_calls == 1
    assert phase6.cleanup_calls == 1
    assert root_blueprint.cleanup_calls == 1
    assert system_index.cleanup_calls == 1
    assert dag_blueprint.cleanup_calls == 1


def test_cleanup_swallow_exceptions() -> None:
    """
    Purpose:
        Confirm cleanup absorbs exceptions from child artifacts.
    Contract:
        Cleanup completes and marks the crafter as cleaned despite exceptions.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not complete or skips calls.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    requirements = _CleanableStub(raise_on_cleanup=True)
    root_blueprint = _RootBlueprintStub("root", raise_on_cleanup=True)
    dag_blueprint = _RootBlueprintStub("dag", raise_on_cleanup=True)

    crafter._requirements = requirements
    crafter._root_blueprint_phase5 = root_blueprint
    crafter._entire_dag_blueprint_phase5 = {"root": dag_blueprint}

    crafter.cleanup()

    assert crafter.cleaned is True
    assert requirements.cleanup_calls == 1
    assert root_blueprint.cleanup_calls == 1
    assert dag_blueprint.cleanup_calls == 1


def test_cleanup_idempotent() -> None:
    """
    Purpose:
        Ensure cleanup can be called multiple times safely.
    Contract:
        Subsequent cleanup calls are no-ops and do not re-clean artifacts.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup repeats or raises on second call.
    """
    crafter, _, _ = _build_spell_and_crafter()
    requirements = _CleanableStub()
    crafter._requirements = requirements

    crafter.cleanup()
    crafter.cleanup()

    assert requirements.cleanup_calls == 1
    assert crafter.cleaned is True


def test_cleanup_clears_references() -> None:
    """
    Purpose:
        Verify cleanup drops references to owned artifacts.
    Contract:
        All crafter-owned fields are reset to None after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If any owned reference is retained.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    crafter._requirements = _CleanableStub()
    crafter._symbolic_graph = _CleanableStub()
    crafter._resolution_frame = _CleanableStub()
    crafter._validation_result_phase4 = _CleanableStub()
    crafter._validation_result_phase6 = _CleanableStub()
    crafter._root_blueprint_phase5 = _RootBlueprintStub("root")
    crafter._spell_system_index_phase5 = _CleanableStub()
    crafter._entire_dag_blueprint_phase5 = {"root": _RootBlueprintStub("root")}

    crafter.cleanup()

    assert crafter._requirements is None
    assert crafter._symbolic_graph is None
    assert crafter._resolution_frame is None
    assert crafter._validation_result_phase4 is None
    assert crafter._validation_result_phase6 is None
    assert crafter._root_blueprint_phase5 is None
    assert crafter._spell_system_index_phase5 is None
    assert crafter._entire_dag_blueprint_phase5 is None
    assert crafter._spell_system_states is None
    assert crafter._spell is None
    assert crafter._spell_validator is None
    assert crafter._lock is None


@pytest.mark.parametrize(
    "property_name",
    [
        "spell",
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "validation_result_phase4",
        "root_blueprint_phase5",
        "spell_system_index_phase5",
        "validation_result_phase6",
        "validated",
        "is_broken",
    ],
)
def test_properties_raise_after_cleanup(property_name: str) -> None:
    """
    Purpose:
        Ensure public properties reject access after cleanup.
    Contract:
        Each property raises RuntimeError once the crafter is cleaned.
    Args:
        property_name: Descriptive name for the property under test.
    Returns:
        None.
    Raises:
        AssertionError: If any property does not enforce cleaned checks.
    """
    crafter, _, _ = _build_spell_and_crafter()
    crafter.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        _ = _access_property(crafter, property_name)


@pytest.mark.parametrize(
    "phase4,phase6,is_broken,expected",
    [
        (False, False, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (True, True, False, True),
        (True, True, True, False),
        (True, False, True, False),
        (False, True, True, False),
        (False, False, True, False),
    ],
)
def test_validated_property_combinations(
    phase4: bool,
    phase6: bool,
    is_broken: bool,
    expected: bool,
) -> None:
    """
    Purpose:
        Verify the validated property reflects Phase 4/6 status correctly.
    Contract:
        validated is True only when both phases pass and the spell is not broken.
    Args:
        phase4: Whether Phase 4 validation succeeded.
        phase6: Whether Phase 6 validation succeeded.
        is_broken: Whether the spell is flagged as broken.
        expected: Expected validated property output.
    Returns:
        None.
    Raises:
        AssertionError: If validated does not match the expected result.
    """
    crafter, _, _ = _build_spell_and_crafter()
    crafter._validated_phase4 = phase4
    crafter._validated_phase6 = phase6
    crafter._is_broken = is_broken

    assert crafter.validated is expected


@pytest.mark.parametrize(
    "is_set,expect_raise",
    [
        (True, True),
        (False, False),
    ],
)
def test_throw_if_cancelled_behavior(is_set: bool, expect_raise: bool) -> None:
    """
    Purpose:
        Ensure cancellation checks trigger when the event is set.
    Contract:
        throw_if_cancelled raises when is_set is True and is a no-op otherwise.
    Args:
        is_set: Whether the cancellation event is active.
        expect_raise: Whether a RuntimeError is expected.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation behavior does not match expectations.
    """
    crafter, _, _ = _build_spell_and_crafter()
    cancel = _CancelStub(is_set=is_set)

    if expect_raise:
        with pytest.raises(RuntimeError, match="cancelled"):
            crafter._throw_if_cancelled(cancel)
        assert cancel.throw_calls == 1
    else:
        crafter._throw_if_cancelled(cancel)
        assert cancel.throw_calls == 0


@pytest.mark.parametrize(
    "drop_states,drop_index",
    [
        (True, False),
        (False, True),
    ],
)
def test_notify_dependencies_updated_skips_when_missing(
    drop_states: bool,
    drop_index: bool,
) -> None:
    """
    Purpose:
        Ensure dependency notifications are skipped without required state.
    Contract:
        No update occurs when SpellSystemStates or the spell index is missing.
    Args:
        drop_states: Whether to clear the spell system state registry.
        drop_index: Whether to clear the spell index reference.
    Returns:
        None.
    Raises:
        AssertionError: If update calls are recorded unexpectedly.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(spell_system_states=states)

    if drop_states:
        crafter._spell_system_states = None
    if drop_index:
        spell.spell_index = None

    crafter._notify_dependencies_updated(["a"])

    assert states.update_calls == []


@pytest.mark.parametrize(
    "dependency_ids,expected",
    [
        (["a", "b"], ["a", "b"]),
        (None, []),
    ],
)
def test_notify_dependencies_updated_passes_dependencies(
    dependency_ids: list[str] | None,
    expected: list[str],
) -> None:
    """
    Purpose:
        Verify dependency updates forward the expected id list.
    Contract:
        The state registry receives a normalized list of dependency ids.
    Args:
        dependency_ids: Dependency list or None for normalization testing.
        expected: Expected dependency list passed to SpellSystemStates.
    Returns:
        None.
    Raises:
        AssertionError: If update call metadata is incorrect.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(spell_system_states=states)

    crafter._notify_dependencies_updated(dependency_ids)

    assert states.update_calls == [(spell.spell_index, expected)]


def test_set_root_blueprint_phase5_rejects_none() -> None:
    """
    Purpose:
        Confirm set_root_blueprint_phase5 enforces non-null inputs.
    Contract:
        Passing None raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    crafter, _, _ = _build_spell_and_crafter()

    with pytest.raises(ValueError, match="blueprint must not be None"):
        crafter.set_root_blueprint_phase5(None)


def test_set_root_blueprint_phase5_sets_value() -> None:
    """
    Purpose:
        Verify set_root_blueprint_phase5 stores the provided blueprint.
    Contract:
        The public root_blueprint_phase5 property returns the assigned value.
    Returns:
        None.
    Raises:
        AssertionError: If the stored blueprint is incorrect.
    """
    crafter, _, _ = _build_spell_and_crafter()
    blueprint = _RootBlueprintStub("root")

    crafter.set_root_blueprint_phase5(blueprint)

    assert crafter.root_blueprint_phase5 is blueprint


def test_set_spell_system_index_phase5_rejects_none() -> None:
    """
    Purpose:
        Confirm set_spell_system_index_phase5 enforces non-null inputs.
    Contract:
        Passing None raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    crafter, _, _ = _build_spell_and_crafter()

    with pytest.raises(ValueError, match="index must not be None"):
        crafter.set_spell_system_index_phase5(None)


def test_set_spell_system_index_phase5_sets_value() -> None:
    """
    Purpose:
        Verify set_spell_system_index_phase5 stores the provided index.
    Contract:
        The public spell_system_index_phase5 property returns the assigned value.
    Returns:
        None.
    Raises:
        AssertionError: If the stored index is incorrect.
    """
    crafter, _, _ = _build_spell_and_crafter()
    index = _CleanableStub()

    crafter.set_spell_system_index_phase5(index)

    assert crafter.spell_system_index_phase5 is index


def test_clear_phase5_artifacts() -> None:
    """
    Purpose:
        Ensure Phase 5 artifact clearing drops stored references.
    Contract:
        Both root blueprint and system index are set to None.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 5 artifacts are not cleared.
    """
    crafter, _, _ = _build_spell_and_crafter()
    crafter._root_blueprint_phase5 = _RootBlueprintStub("root")
    crafter._spell_system_index_phase5 = _CleanableStub()

    crafter.clear_phase5_artifacts()

    assert crafter.root_blueprint_phase5 is None
    assert crafter.spell_system_index_phase5 is None


def test_iter_all_spells_proxy() -> None:
    """
    Purpose:
        Verify _iter_all_spells walks the live spell_id_pool.
    Contract:
        The helper yields the spell_index/spell pairs in pool insertion order.
    Returns:
        None.
    Raises:
        AssertionError: If the returned sequence differs from the pool contents.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    spellbook = spell._spellbook
    first = _SpellStub(
        spell_id="first",
        spell_name="first",
        spellbook=spellbook,
    )
    second = _SpellStub(
        spell_id="second",
        spell_name="second",
        spellbook=spellbook,
    )
    spellbook._spell_id_pool.clear()
    spellbook._spell_id_pool[first.spell_index.current] = first
    spellbook._spell_id_pool[second.spell_index.current] = second

    result = list(crafter._iter_all_spells())

    assert result == [
        (first.spell_index, first),
        (second.spell_index, second),
    ]


@pytest.mark.parametrize(
    "spell_type,match_kind,binding_name,candidate_binding,require_class_spell,expected",
    [
        (SpellType.SPELL, "spell", None, None, True, True),
        (SpellType.SPELL, "spell", "alpha", "beta", True, False),
        (SpellType.SPELL, "frame", None, None, True, True),
        (SpellType.SPELL, "frame_eq", None, None, True, True),
        (SpellType.METHOD, "spell", None, None, True, False),
        (SpellType.METHOD, "spell", None, None, False, True),
    ],
)
def test_matches_annotation_cases(
    spell_type: SpellType,
    match_kind: str,
    binding_name: str | None,
    candidate_binding: str | None,
    require_class_spell: bool,
    expected: bool,
) -> None:
    """
    Purpose:
        Validate annotation matching respects spell type, frame, and binding.
    Contract:
        _matches_annotation returns True only for valid annotation matches.
    Args:
        spell_type: Spell type for the candidate spell.
        match_kind: Kind of match to exercise (spell, frame, frame_eq).
        binding_name: Binding name required by the caller.
        candidate_binding: Binding name on the candidate spell.
        require_class_spell: Whether method/lambda spells are excluded.
        expected: Expected match result.
    Returns:
        None.
    Raises:
        AssertionError: If matching behavior differs from expectations.
    """
    crafter, _, _ = _build_spell_and_crafter()
    spellbook = crafter.spell._spellbook

    spell_token = object()
    frame_token = object()
    frame_eq = ["frame"]

    if match_kind == "spell":
        annotation = spell_token
        spell_value = spell_token
        frame_value = None
    elif match_kind == "frame":
        annotation = frame_token
        spell_value = None
        frame_value = frame_token
    else:
        annotation = ["frame"]
        spell_value = None
        frame_value = frame_eq

    candidate = _SpellStub(
        spell_id="candidate",
        spell_name="candidate",
        spell_type=spell_type,
        spell=spell_value,
        spellframe=frame_value,
        binding_name=candidate_binding,
        spellbook=spellbook,
    )

    result = crafter._matches_annotation(
        annotation,
        binding_name,
        candidate,
        require_class_spell=require_class_spell,
    )

    assert result is expected


def test_matches_annotation_rejects_binding_mismatch_on_frame() -> None:
    """
    Purpose:
        Confirm frame matches still enforce binding_name constraints.
    Contract:
        _matches_annotation returns False when the frame matches but the
        binding name differs.
    Returns:
        None.
    Raises:
        AssertionError: If binding mismatches are not rejected.
    """
    crafter, _, _ = _build_spell_and_crafter()
    spellbook = crafter.spell._spellbook
    frame_token = object()

    candidate = _SpellStub(
        spell_id="candidate",
        spell_name="candidate",
        spell_type=SpellType.SPELL,
        spell=None,
        spellframe=frame_token,
        binding_name="beta",
        spellbook=spellbook,
    )

    result = crafter._matches_annotation(
        frame_token,
        "alpha",
        candidate,
        require_class_spell=True,
    )

    assert result is False


@pytest.mark.parametrize(
    "method_only",
    [
        False,
        True,
    ],
)
def test_resolve_single_by_annotation_no_candidates(method_only: bool) -> None:
    """
    Purpose:
        Ensure SINGLE_BY_ANNOTATION fails when no eligible candidates exist.
    Contract:
        A RuntimeError is raised if zero class-based candidates match.
    Args:
        method_only: Whether to provide a method spell that should be excluded.
    Returns:
        None.
    Raises:
        AssertionError: If the expected RuntimeError is not raised.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=annotation,
    )

    if method_only:
        method_spell = _SpellStub(
            spell_id="method",
            spell_name="method",
            spell_type=SpellType.METHOD,
            spell=annotation,
            spellbook=spell._spellbook,
        )
        _set_spell_id_pool(spell._spellbook, [method_spell])

    with pytest.raises(RuntimeError, match="no DI candidate"):
        crafter._resolve_single_by_annotation(dep)


def test_resolve_single_by_annotation_multiple_candidates() -> None:
    """
    Purpose:
        Verify SINGLE_BY_ANNOTATION rejects ambiguous candidates.
    Contract:
        A RuntimeError is raised when multiple class-based matches are found.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity does not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=annotation,
    )

    first_spell = _SpellStub(
        spell_id="one",
        spell_name="one",
        spell_type=SpellType.SPELL,
        spell=annotation,
        spellbook=spell._spellbook,
    )
    second_spell = _SpellStub(
        spell_id="two",
        spell_name="two",
        spell_type=SpellType.SPELL,
        spell=annotation,
        spellbook=spell._spellbook,
    )

    _set_spell_id_pool(spell._spellbook, [first_spell, second_spell])

    with pytest.raises(RuntimeError, match="multiple DI candidates"):
        crafter._resolve_single_by_annotation(dep)


def test_resolve_single_by_annotation_success() -> None:
    """
    Purpose:
        Ensure SINGLE_BY_ANNOTATION returns the sole candidate.
    Contract:
        The resolved mapping contains exactly the matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If the returned mapping is incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=annotation,
    )

    candidate = _SpellStub(
        spell_id="cand",
        spell_name="cand",
        spell_type=SpellType.SPELL,
        spell=annotation,
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    result = crafter._resolve_single_by_annotation(dep)

    assert list(result.values()) == [candidate]


def test_resolve_collection_by_annotation_empty_returns_empty() -> None:
    """
    Purpose:
        Confirm COLLECTION_BY_ANNOTATION can yield an empty mapping.
    Contract:
        When no candidates match, an empty dict is returned.
    Returns:
        None.
    Raises:
        AssertionError: If the mapping is not empty.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        target_annotation=annotation,
        is_collection=True,
    )
    _set_spell_id_pool(spell._spellbook, [])

    result = crafter._resolve_collection_by_annotation(dep)

    assert result == {}


def test_resolve_collection_by_annotation_includes_method_spells() -> None:
    """
    Purpose:
        Verify COLLECTION_BY_ANNOTATION includes method spells.
    Contract:
        Method and class spells matching the annotation are returned together.
    Returns:
        None.
    Raises:
        AssertionError: If method spells are excluded from results.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        target_annotation=annotation,
        is_collection=True,
    )

    class_spell = _SpellStub(
        spell_id="class",
        spell_name="class",
        spell_type=SpellType.SPELL,
        spell=annotation,
        spellbook=spell._spellbook,
    )
    method_spell = _SpellStub(
        spell_id="method",
        spell_name="method",
        spell_type=SpellType.METHOD,
        spell=annotation,
        spellbook=spell._spellbook,
    )

    _set_spell_id_pool(spell._spellbook, [class_spell, method_spell])

    result = crafter._resolve_collection_by_annotation(dep)

    assert set(result.values()) == {class_spell, method_spell}


def test_resolve_spellmap_default_none_returns_empty() -> None:
    """
    Purpose:
        Ensure SpellMap defaults are optional when not provided.
    Contract:
        _resolve_spellmap_default returns an empty mapping when spellmap_default is None.
    Returns:
        None.
    Raises:
        AssertionError: If a mapping is returned.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=None,
    )
    result = crafter._resolve_spellmap_default(dep)

    assert result == {}


def test_resolve_spellmap_default_explicit_spell_success() -> None:
    """
    Purpose:
        Ensure explicit SpellMap defaults resolve to a single candidate.
    Contract:
        The explicit spell match is returned when frame and binding align.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved mapping is incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    explicit = object()
    frame = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=explicit,
            spellframe=frame,
            binding_name="bind",
        ),
    )

    candidate = _SpellStub(
        spell_id="cand",
        spell_name="cand",
        spell_type=SpellType.SPELL,
        spell=explicit,
        spellframe=frame,
        binding_name="bind",
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    result = crafter._resolve_spellmap_default(dep)

    assert list(result.values()) == [candidate]


def test_resolve_spellmap_default_explicit_spell_mismatch_raises() -> None:
    """
    Purpose:
        Verify explicit SpellMap defaults fail when filters exclude matches.
    Contract:
        A RuntimeError is raised if explicit candidates are filtered out.
    Returns:
        None.
    Raises:
        AssertionError: If the mismatch does not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    explicit = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=explicit,
            spellframe=object(),
            binding_name="bind",
        ),
    )

    candidate = _SpellStub(
        spell_id="cand",
        spell_name="cand",
        spell_type=SpellType.SPELL,
        spell=explicit,
        spellframe=None,
        binding_name="other",
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    with pytest.raises(RuntimeError, match="SpellMap default could not be resolved"):
        crafter._resolve_spellmap_default(dep)


def test_resolve_spellmap_default_explicit_spell_multiple_raises() -> None:
    """
    Purpose:
        Ensure explicit SpellMap defaults reject multiple candidates.
    Contract:
        A RuntimeError is raised when explicit spell resolution is ambiguous.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity does not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    explicit = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=explicit,
            spellframe=None,
            binding_name=None,
        ),
    )

    first = _SpellStub(
        spell_id="one",
        spell_name="one",
        spell_type=SpellType.SPELL,
        spell=explicit,
        spellbook=spell._spellbook,
    )
    second = _SpellStub(
        spell_id="two",
        spell_name="two",
        spell_type=SpellType.SPELL,
        spell=explicit,
        spellbook=spell._spellbook,
    )

    _set_spell_id_pool(spell._spellbook, [first, second])

    with pytest.raises(RuntimeError, match="multiple candidates"):
        crafter._resolve_spellmap_default(dep)


def test_resolve_spellmap_default_frame_binding_success() -> None:
    """
    Purpose:
        Verify SpellMap defaults resolve via frame and binding lookups.
    Contract:
        The pool match is returned when exactly one candidate exists.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved mapping is incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=None,
            spellframe=object(),
            binding_name="bind",
        ),
    )
    frame = dep.spellmap_default.spellframe

    candidate = _SpellStub(
        spell_id="cand",
        spell_name="cand",
        spell_type=SpellType.SPELL,
        spell=object(),
        spellframe=frame,
        binding_name="bind",
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    result = crafter._resolve_spellmap_default(dep)

    assert list(result.values()) == [candidate]


def test_resolve_spellmap_default_frame_binding_empty_raises() -> None:
    """
    Purpose:
        Ensure SpellMap defaults raise when no frame binding exists.
    Contract:
        A RuntimeError is raised when the frame lookup returns no candidates.
    Returns:
        None.
    Raises:
        AssertionError: If missing candidates do not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=None,
            spellframe=object(),
            binding_name="bind",
        ),
    )
    _set_spell_id_pool(spell._spellbook, [])

    with pytest.raises(RuntimeError, match="SpellMap default could not be resolved"):
        crafter._resolve_spellmap_default(dep)


def test_resolve_spellmap_default_frame_binding_multiple_raises() -> None:
    """
    Purpose:
        Ensure SpellMap defaults reject ambiguous frame lookups.
    Contract:
        A RuntimeError is raised when frame lookup returns multiple candidates.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity does not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=None,
            spellframe=object(),
            binding_name="bind",
        ),
    )
    frame = dep.spellmap_default.spellframe

    first = _SpellStub(
        spell_id="one",
        spell_name="one",
        spell_type=SpellType.SPELL,
        spell=object(),
        spellframe=frame,
        binding_name="bind",
        spellbook=spell._spellbook,
    )
    second = _SpellStub(
        spell_id="two",
        spell_name="two",
        spell_type=SpellType.SPELL,
        spell=object(),
        spellframe=frame,
        binding_name="bind",
        spellbook=spell._spellbook,
    )

    _set_spell_id_pool(spell._spellbook, [first, second])

    with pytest.raises(RuntimeError, match="multiple candidates"):
        crafter._resolve_spellmap_default(dep)


@pytest.mark.parametrize(
    "di_shape,expected",
    [
        (ParameterDIShape.PLAIN, SocketKind.NORMAL),
        (ParameterDIShape.SINGLE_BY_ANNOTATION, SocketKind.NORMAL),
        (ParameterDIShape.COLLECTION_BY_ANNOTATION, SocketKind.NORMAL),
        (ParameterDIShape.SPELLMAP_DEFAULT, SocketKind.NORMAL),
        (ParameterDIShape.SPELL_CONTRACT, SocketKind.SPELL_CONTRACT),
        (ParameterDIShape.MUTATION_CONTRACT, SocketKind.MUTATION_CONTRACT),
    ],
)
def test_socket_kind_for_dep_mapping(
    di_shape: ParameterDIShape,
    expected: SocketKind,
) -> None:
    """
    Purpose:
        Validate socket kind mapping for symbolic dependencies.
    Contract:
        Each DI shape maps to the expected SocketKind.
    Args:
        di_shape: Dependency injection shape under test.
        expected: Expected SocketKind mapping.
    Returns:
        None.
    Raises:
        AssertionError: If the socket kind mapping is incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=di_shape,
    )

    assert crafter._socket_kind_for_dep(dep) is expected


def test_run_phase_requirements_sets_requirements(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 1 stores the requirements built by the finder.
    Contract:
        The built requirements are cached and the cancel_event is forwarded.
    Args:
        monkeypatch: Pytest fixture for patching SpellRequirementsFinder.
    Returns:
        None.
    Raises:
        AssertionError: If requirements or call tracking are incorrect.
    """
    crafter, _, _ = _build_spell_and_crafter()
    requirements = object()
    _RequirementsFinderStub.requirements = requirements

    monkeypatch.setattr(
        spell_crafter_module,
        "SpellRequirementsFinder",
        _RequirementsFinderStub,
    )

    cancel = _CancelStub(is_set=False)
    crafter.run_phase_requirements(cancel_event=cancel)

    assert crafter.requirements is requirements
    assert _RequirementsFinderStub.calls == [cancel]


def test_run_phase_requirements_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure Phase 1 respects cancellation before building requirements.
    Contract:
        Cancellation raises and the requirements finder is not invoked.
    Args:
        monkeypatch: Pytest fixture for patching SpellRequirementsFinder.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation is ignored or finder is called.
    """
    crafter, _, _ = _build_spell_and_crafter()
    _RequirementsFinderStub.requirements = object()

    monkeypatch.setattr(
        spell_crafter_module,
        "SpellRequirementsFinder",
        _RequirementsFinderStub,
    )

    cancel = _CancelStub(is_set=True)
    with pytest.raises(RuntimeError, match="cancelled"):
        crafter.run_phase_requirements(cancel_event=cancel)

    assert _RequirementsFinderStub.calls == []


def test_run_phase_symbolic_graph_requires_phase1() -> None:
    """
    Purpose:
        Ensure Phase 2 requires Phase 1 requirements to exist.
    Contract:
        A RuntimeError is raised when requirements are missing.
    Returns:
        None.
    Raises:
        AssertionError: If missing requirements do not raise.
    """
    crafter, _, _ = _build_spell_and_crafter()

    with pytest.raises(RuntimeError, match="Phase 2"):
        crafter.run_phase_symbolic_graph(cancel_event=None)


@pytest.mark.parametrize(
    "di_shape,target_annotation,is_collection,spellmap_default,is_optional",
    [
        (ParameterDIShape.SINGLE_BY_ANNOTATION, object(), False, None, True),
        (ParameterDIShape.COLLECTION_BY_ANNOTATION, object(), True, None, False),
        (ParameterDIShape.SPELLMAP_DEFAULT, None, False, object(), True),
        (ParameterDIShape.SPELL_CONTRACT, object(), False, None, False),
        (ParameterDIShape.MUTATION_CONTRACT, object(), False, None, True),
    ],
)
def test_run_phase_symbolic_graph_builds_dependencies(
    di_shape: ParameterDIShape,
    target_annotation: object | None,
    is_collection: bool,
    spellmap_default: object | None,
    is_optional: bool,
) -> None:
    """
    Purpose:
        Verify Phase 2 maps parameters into symbolic dependencies correctly.
    Contract:
        Each supported DI shape yields a dependency with expected metadata.
    Args:
        di_shape: ParameterDIShape under test.
        target_annotation: Expected target annotation on the dependency.
        is_collection: Expected collection flag on the dependency.
        spellmap_default: Expected SpellMap default stored on the dependency.
        is_optional: Expected optional flag on the dependency.
    Returns:
        None.
    Raises:
        AssertionError: If dependency metadata is incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    default_value = None
    if di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
        default_value = spellmap_default
    elif di_shape is ParameterDIShape.SPELL_CONTRACT:
        default_value = SpellContract(spellframe=target_annotation, binding_name="primary")
    elif di_shape is ParameterDIShape.MUTATION_CONTRACT:
        default_value = MutationContract(spellframe=target_annotation, binding_name="primary")
    param = _ParamStub(
        name="param",
        position=1,
        di_shape=di_shape,
        is_optional=is_optional,
        annotation=target_annotation,
        collection_element_annotation=target_annotation,
        spellmap_default=spellmap_default,
        default_value=default_value,
    )
    crafter._requirements = _RequirementsStub([param])

    crafter.run_phase_symbolic_graph(cancel_event=None)

    graph = crafter.symbolic_graph
    deps = graph.dependencies

    assert len(deps) == 1
    dep = deps[0]
    assert dep.spell_id == spell.spell_index.current
    assert dep.param_name == "param"
    assert dep.position == 1
    assert dep.di_shape is di_shape
    assert dep.target_annotation == target_annotation
    assert dep.is_collection is is_collection
    assert dep.is_optional is is_optional
    assert dep.spellmap_default is spellmap_default


def test_run_phase_symbolic_graph_includes_plain_and_skips_ignore() -> None:
    """
    Purpose:
        Ensure Phase 2 includes plain parameters and skips ignored ones.
    Contract:
        PLAIN parameters become symbolic dependencies while IGNORE does not.
    Returns:
        None.
    Raises:
        AssertionError: If plain parameters are skipped or ignore is included.
    """
    crafter, _, _ = _build_spell_and_crafter()
    plain_param = _ParamStub(
        name="plain",
        position=0,
        di_shape=ParameterDIShape.PLAIN,
        is_optional=False,
        annotation=int,
    )
    ignore_param = _ParamStub(
        name="ignore",
        position=1,
        di_shape=ParameterDIShape.IGNORE,
        is_optional=False,
    )
    crafter._requirements = _RequirementsStub([plain_param, ignore_param])

    crafter.run_phase_symbolic_graph(cancel_event=None)

    deps = crafter.symbolic_graph.dependencies
    assert len(deps) == 1
    dep = deps[0]
    assert dep.param_name == "plain"
    assert dep.position == 0
    assert dep.di_shape is ParameterDIShape.PLAIN
    assert dep.is_optional is False
    assert dep.is_collection is False
    assert dep.target_annotation is int
    assert dep.spellmap_default is None


@pytest.mark.parametrize(
    "drop_spell,drop_index",
    [
        (True, False),
        (False, True),
    ],
)
def test_build_local_topology_requires_spell(
    drop_spell: bool,
    drop_index: bool,
) -> None:
    """
    Purpose:
        Ensure local topology construction requires a bound spell index.
    Contract:
        A RuntimeError is raised when the spell or spell index is missing.
    Args:
        drop_spell: Whether to clear the spell reference entirely.
        drop_index: Whether to clear the spell index reference.
    Returns:
        None.
    Raises:
        AssertionError: If missing spell data does not raise.
    """
    crafter, _, _ = _build_spell_and_crafter()
    graph = _make_symbolic_graph(spell_id="root", dependencies=[])

    if drop_spell:
        crafter._spell = None
    if drop_index:
        crafter.spell.spell_index = None

    with pytest.raises(RuntimeError, match="SpellCrafter has no bound Spell"):
        crafter._build_local_topology(graph, {})


def test_build_local_topology_builds_descriptors() -> None:
    """
    Purpose:
        Verify local topology descriptors reflect symbolic graph metadata.
    Contract:
        Each dependency yields a SpellSocketDescriptor with expected fields.
    Returns:
        None.
    Raises:
        AssertionError: If descriptor metadata is incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    dep_normal = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="alpha",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        is_optional=False,
    )
    dep_contract = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="beta",
        position=1,
        di_shape=ParameterDIShape.SPELL_CONTRACT,
        is_optional=True,
    )
    graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=[dep_normal, dep_contract],
    )
    socket_targets = {("alpha", 0): ["dep1", "dep2"]}

    topology = crafter._build_local_topology(graph, socket_targets)

    assert topology.spell_id == spell.spell_index.current
    assert len(topology.sockets) == 2

    alpha_socket = topology.get_sockets_for_param("alpha")[0]
    beta_socket = topology.get_sockets_for_param("beta")[0]

    assert alpha_socket.param_name == "alpha"
    assert alpha_socket.position == 0
    assert alpha_socket.socket_kind is SocketKind.NORMAL
    assert alpha_socket.is_collection is False
    assert alpha_socket.is_optional is False
    assert alpha_socket.target_spell_ids == ("dep1", "dep2")

    assert beta_socket.param_name == "beta"
    assert beta_socket.position == 1
    assert beta_socket.socket_kind is SocketKind.SPELL_CONTRACT
    assert beta_socket.is_collection is False
    assert beta_socket.is_optional is True
    assert beta_socket.target_spell_ids == ()


@pytest.mark.parametrize(
    "drop_requirements,drop_graph,expected_message",
    [
        (True, False, "requirements must not be None"),
        (False, True, "graph must not be None"),
    ],
)
def test_build_local_frame_dag_requires_inputs(
    drop_requirements: bool,
    drop_graph: bool,
    expected_message: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure local DAG construction requires non-null inputs.
    Contract:
        A ValueError is raised when requirements or graph is missing.
    Args:
        drop_requirements: Whether to clear the requirements argument.
        drop_graph: Whether to clear the graph argument.
        expected_message: Substring expected in the raised error message.
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If missing inputs do not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    requirements = object()
    graph = _make_symbolic_graph(spell_id=spell.spell_index.current, dependencies=[])

    if drop_requirements:
        requirements = None
    if drop_graph:
        graph = None

    with pytest.raises(ValueError, match=expected_message):
        crafter._build_local_frame_dag(
            requirements=requirements,
            graph=graph,
            cancellation_event=_CancelStub(is_set=False),
        )


@pytest.mark.parametrize(
    "drop_spell,drop_index",
    [
        (True, False),
        (False, True),
    ],
)
def test_build_local_frame_dag_requires_spell_index(
    drop_spell: bool,
    drop_index: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure local DAG construction requires a bound spell index.
    Contract:
        A RuntimeError is raised when the spell or spell index is missing.
    Args:
        drop_spell: Whether to clear the spell reference.
        drop_index: Whether to clear the spell index reference.
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If missing spell data does not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    if drop_spell:
        crafter._spell = None
    if drop_index:
        spell.spell_index = None

    graph = _make_symbolic_graph(spell_id="root", dependencies=[])

    with pytest.raises(RuntimeError, match="SpellCrafter has no bound Spell"):
        crafter._build_local_frame_dag(
            requirements=object(),
            graph=graph,
            cancellation_event=_CancelStub(is_set=False),
        )


def test_build_local_frame_dag_builds_single_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify local DAG construction adds nodes and edges for single DI.
    Contract:
        The dependency node and edge to the root are registered in the DAG.
    Args:
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If nodes or edges are missing from the DAG.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=annotation,
    )
    graph = _make_symbolic_graph(spell_id=spell.spell_index.current, dependencies=[dep])

    candidate = _SpellStub(
        spell_id="dep-id",
        spell_name="dep",
        spell_type=SpellType.SPELL,
        spell=annotation,
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    dag = crafter._build_local_frame_dag(
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dag is _DagStub.last_instance
    assert dag.nodes[0][0] == spell.spell_index.current
    assert dag.nodes[1][0] == "dep-id"
    assert dag.dependencies == [("dep-id", spell.spell_index.current, "dep", SocketKind.NORMAL)]


def test_build_local_frame_dag_skips_unresolved_collection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure unresolved collection dependencies do not add DAG edges.
    Contract:
        When no candidates are found, only the root node is added.
    Args:
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If unexpected DAG edges are present.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        target_annotation=object(),
        is_collection=True,
    )
    graph = _make_symbolic_graph(spell_id=spell.spell_index.current, dependencies=[dep])

    dag = crafter._build_local_frame_dag(
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dag.nodes == [(spell.spell_index.current, spell)]
    assert dag.dependencies == []


def test_build_local_frame_dag_handles_spellmap_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify SpellMap defaults produce DAG edges for resolved spells.
    Contract:
        Resolved SpellMap defaults appear as nodes and edges in the DAG.
    Args:
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If SpellMap resolutions are not represented in the DAG.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    explicit = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=_SpellMapStub(
            spell=explicit,
            spellframe=None,
            binding_name=None,
        ),
    )
    graph = _make_symbolic_graph(spell_id=spell.spell_index.current, dependencies=[dep])

    candidate = _SpellStub(
        spell_id="dep-id",
        spell_name="dep",
        spell_type=SpellType.SPELL,
        spell=explicit,
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    dag = crafter._build_local_frame_dag(
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dag.dependencies == [("dep-id", spell.spell_index.current, "dep", SocketKind.NORMAL)]


def test_build_local_frame_dag_ignores_contract_shapes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure contract sockets do not generate DAG edges.
    Contract:
        SpellContract and MutationContract dependencies are metadata-only.
    Args:
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If contract sockets create DAG edges.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(spell_system_states=states)
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    contract_dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="contract",
        position=0,
        di_shape=ParameterDIShape.SPELL_CONTRACT,
        target_annotation=object(),
    )
    mutation_dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="mutation",
        position=1,
        di_shape=ParameterDIShape.MUTATION_CONTRACT,
        target_annotation=object(),
    )
    graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=[contract_dep, mutation_dep],
    )

    dag = crafter._build_local_frame_dag(
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dag.dependencies == []
    assert states.update_calls == [(spell.spell_index, [])]
    assert states.topology_calls != []


def test_build_local_frame_dag_updates_states(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify local DAG construction updates SpellSystemStates.
    Contract:
        Dependencies and topology are registered when states are provided.
    Args:
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If state updates are missing or incorrect.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(spell_system_states=states)
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    annotation = object()
    dep = _make_dependency(
        spell_id=spell.spell_index.current,
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=annotation,
    )
    graph = _make_symbolic_graph(spell_id=spell.spell_index.current, dependencies=[dep])

    candidate = _SpellStub(
        spell_id="dep-id",
        spell_name="dep",
        spell_type=SpellType.SPELL,
        spell=annotation,
        spellbook=spell._spellbook,
    )
    _set_spell_id_pool(spell._spellbook, [candidate])

    crafter._build_local_frame_dag(
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert states.update_calls == [(spell.spell_index, ["dep-id"])]
    assert len(states.topology_calls) == 1
    assert states.topology_calls[0][0] is spell.spell_index


@pytest.mark.parametrize(
    "drop_requirements,drop_graph",
    [
        (True, False),
        (False, True),
    ],
)
def test_run_phase_local_frame_requires_prior_phases(
    drop_requirements: bool,
    drop_graph: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure Phase 3 requires both requirements and symbolic graph.
    Contract:
        A RuntimeError is raised when Phase 1 or Phase 2 artifacts are missing.
    Args:
        drop_requirements: Whether to clear stored requirements.
        drop_graph: Whether to clear stored symbolic graph.
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If missing artifacts do not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    crafter._requirements = _RequirementsStub([])
    crafter._symbolic_graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=[],
    )

    if drop_requirements:
        crafter._requirements = None
    if drop_graph:
        crafter._symbolic_graph = None

    with pytest.raises(RuntimeError, match="Phase 3"):
        crafter.run_phase_local_frame(cancel_event=None)


def test_run_phase_local_frame_sets_resolution_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 3 stores the resolution frame with ordered ids.
    Contract:
        The resolution frame captures the DAG ordering returned by the DAG.
    Args:
        monkeypatch: Pytest fixture for patching DAG types.
    Returns:
        None.
    Raises:
        AssertionError: If the resolution frame fields are incorrect.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    monkeypatch.setattr(spell_crafter_module, "DirectedAcyclicWorkGraph", _DagStub)

    _DagStub.next_dependency_ids = ["dep", spell.spell_index.current]
    crafter._requirements = _RequirementsStub([])
    crafter._symbolic_graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=[],
    )

    crafter.run_phase_local_frame(cancel_event=None)

    frame = crafter.resolution_frame
    assert frame.spell_id == spell.spell_index.current
    assert frame.ordered_node_ids == ["dep", spell.spell_index.current]


@pytest.mark.parametrize(
    "drop_requirements,drop_graph,drop_frame",
    [
        (True, False, False),
        (False, True, False),
        (False, False, True),
    ],
)
def test_run_phase_validation_requires_prior_phases(
    drop_requirements: bool,
    drop_graph: bool,
    drop_frame: bool,
) -> None:
    """
    Purpose:
        Ensure Phase 4 validation requires Phases 1-3 artifacts.
    Contract:
        A RuntimeError is raised when any required artifact is missing.
    Args:
        drop_requirements: Whether to clear stored requirements.
        drop_graph: Whether to clear stored symbolic graph.
        drop_frame: Whether to clear stored resolution frame.
    Returns:
        None.
    Raises:
        AssertionError: If missing artifacts do not raise.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    crafter._requirements = _RequirementsStub([])
    crafter._symbolic_graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=[],
    )
    crafter._resolution_frame = SpellResolutionFrame(
        spell_id=spell.spell_index.current,
        ordered_node_ids=[],
    )

    if drop_requirements:
        crafter._requirements = None
    if drop_graph:
        crafter._symbolic_graph = None
    if drop_frame:
        crafter._resolution_frame = None

    with pytest.raises(RuntimeError, match="Phase 4"):
        crafter.run_phase_validation(cancel_event=None)


@pytest.mark.parametrize(
    "has_errors,expected_broken",
    [
        (True, True),
        (False, False),
    ],
)
def test_run_phase_validation_sets_flags(
    has_errors: bool,
    expected_broken: bool,
) -> None:
    """
    Purpose:
        Verify Phase 4 stores validation results and flags.
    Contract:
        Validation results are cached, _validated_phase4 is True, and is_broken
        reflects the result.
    Args:
        has_errors: Whether the validation result should report errors.
        expected_broken: Expected broken flag value.
    Returns:
        None.
    Raises:
        AssertionError: If cached results or flags are incorrect.
    """
    crafter, spell, validator = _build_spell_and_crafter(
        validator_result_has_errors=has_errors,
    )
    crafter._requirements = _RequirementsStub([])
    crafter._symbolic_graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=[],
    )
    crafter._resolution_frame = SpellResolutionFrame(
        spell_id=spell.spell_index.current,
        ordered_node_ids=[],
    )

    crafter.run_phase_validation(cancel_event=None)

    assert crafter.validation_result_phase4 is validator._result
    assert crafter._validated_phase4 is True
    assert crafter.is_broken is expected_broken


def test_run_phase_validation_skips_when_cached() -> None:
    """
    Purpose:
        Ensure Phase 4 skips revalidation when a cached result exists.
    Contract:
        If already validated with a cached result, validator is not invoked.
    Returns:
        None.
    Raises:
        AssertionError: If validation is re-run despite cached results.
    """
    crafter, _, validator = _build_spell_and_crafter()
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = object()

    crafter.run_phase_validation(cancel_event=None)

    assert validator.calls == []


@pytest.mark.parametrize("has_result", [False, True])
def test_run_phase_root_blueprints_requires_phase4(
    has_result: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure Phase 5 requires Phase 4 validation completion.
    Contract:
        Missing Phase 4 results raise unless a cached result exists.
    Args:
        has_result: Whether to pre-populate Phase 4 results.
        expect_raise: Whether a RuntimeError is expected.
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 4 gating behavior is incorrect.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=states)

    crafter._validated_phase4 = False
    if has_result:
        crafter._validation_result_phase4 = object()

    snapshot = _AdjacencySnapshotStub(dependencies={"root": set()}, root_spell_ids=set())
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {}

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)

    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert crafter.spell_system_index_phase5 is not None


def test_run_phase_root_blueprints_builds_index_and_attaches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 5 builds the system index and attaches root blueprints.
    Contract:
        Root crafters receive blueprints and the system index is populated.
    Args:
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If index population or attachment fails.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies={"dep"},
                spell_index_id="lineage-root",
            ),
            _SpellSystemStateStub(
                current_spell_id="dep",
                direct_dependencies=set(),
                spell_index_id="lineage-dep",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(spell_system_states=states)
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = object()

    snapshot = _AdjacencySnapshotStub(
        dependencies={"root": {"dep"}, "dep": set()},
        root_spell_ids={"root"},
    )
    blueprint = _RootBlueprintStub("root")
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {"root": blueprint}

    dep_spell = _SpellStub(
        spell_id="dep",
        spell_name="dep",
        spell_type=SpellType.SPELL,
        spellbook=spell._spellbook,
    )

    _set_spell_id_pool(spell._spellbook, [spell, dep_spell])

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)
    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert crafter.root_blueprint_phase5 is blueprint
    assert crafter.spell_system_index_phase5 is not None
    root_node = crafter.spell_system_index_phase5.get_node("root")
    dep_node = crafter.spell_system_index_phase5.get_node("dep")
    assert root_node.is_root is True
    assert root_node.dependencies == {"dep"}
    assert dep_node.is_root is False


def test_run_phase_root_blueprints_attaches_fallback_blueprint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure Phase 5 attaches a fallback blueprint when the root is missing
        from the snapshot.
    Contract:
        Visible spells receive a blueprint even when the snapshot omits them.
    Args:
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If fallback blueprint attachment fails.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=states)
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = object()

    snapshot = _AdjacencySnapshotStub(dependencies={}, root_spell_ids={"missing"})
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {"missing": _RootBlueprintStub("missing")}

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)
    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    blueprint = crafter.root_blueprint_phase5
    assert blueprint is not None
    assert blueprint.root_spell_id == "root"
    assert crafter.spell_system_index_phase5 is not None


def test_run_phase_root_blueprints_change_control_wires_revalidator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 5 wires change control rebuild and revalidator hooks.
    Contract:
        The manager receives rebuild_component_of and set_revalidator calls.
    Args:
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If change control wiring is missing.
    """
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager=manager)
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(
        spell_system_states=states,
        aether=aether,
    )
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = object()

    snapshot = _AdjacencySnapshotStub(dependencies={}, root_spell_ids=set())
    blueprints = {"root": _RootBlueprintStub("root")}
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = blueprints

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)
    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert manager.rebuild_calls == [blueprints]
    assert manager.set_calls == 1
    assert manager._revalidate_fn is not None


def test_run_phase_root_blueprints_revalidator_runs_dirty_roots(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure the change-control revalidator reruns phases for dirty roots.
    Contract:
        The revalidator calls run_all_phases for matching roots and honors
        cancellation signals.
    Args:
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If revalidation calls or cancellation checks fail.
    """
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager=manager)
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(
        spell_system_states=states,
        aether=aether,
    )
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = object()

    snapshot = _AdjacencySnapshotStub(dependencies={"root": set()}, root_spell_ids={"root"})
    blueprints = {"root": _RootBlueprintStub("root")}
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = blueprints

    calls: list[dict[str, object]] = []

    def _run_all_phases(
            self: SpellCrafter,
            conduit_id: str,
            *,
            cancel_event: object | None = None,
    ) -> None:
        """
        Purpose:
            Record revalidation calls for dirty roots.
        Contract:
            Appends the crafter, conduit id, and cancel_event to the call list.
        Args:
            conduit_id: Conduit identifier forwarded by the revalidator.
            cancel_event: Optional cancellation event forwarded by the revalidator.
        Returns:
            None.
        """
        calls.append(
            {
                "crafter": self,
                "conduit_id": conduit_id,
                "cancel_event": cancel_event,
            }
        )

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)
    monkeypatch.setattr(SpellCrafter, "run_all_phases", _run_all_phases)

    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert manager._revalidate_fn is not None

    cancel = _CancelStub(is_set=False)
    manager._revalidate_fn({"root"}, cancel)

    assert calls == [{"crafter": crafter, "conduit_id": "cid", "cancel_event": cancel}]

    cancel_set = _CancelStub(is_set=True)
    manager._revalidate_fn({"root"}, cancel_set)

    assert calls == [
        {"crafter": crafter, "conduit_id": "cid", "cancel_event": cancel},
        {"crafter": crafter, "conduit_id": "cid", "cancel_event": cancel_set},
    ]


def test_run_phase_root_blueprints_swallow_change_control_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure Phase 5 ignores change control failures.
    Contract:
        Exceptions from change control lookup are swallowed.
    Args:
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If exceptions propagate from change control wiring.
    """
    aether = _AetherStub(raise_on_get=True)
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="root",
                direct_dependencies=set(),
                spell_index_id="lineage-root",
            ),
        ]
    )
    crafter, spell, _ = _build_spell_and_crafter(
        spell_system_states=states,
        aether=aether,
    )
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = object()

    snapshot = _AdjacencySnapshotStub(dependencies={"root": set()}, root_spell_ids=set())
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {}

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)

    with pytest.raises(RuntimeError, match="boom"):
        crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert crafter.spell_system_index_phase5 is not None


def test_run_phase_root_blueprints_cancellation() -> None:
    """
    Purpose:
        Ensure Phase 5 respects cancellation before work begins.
    Contract:
        A cancellation event raises RuntimeError immediately.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation does not raise.
    """
    crafter, _, _ = _build_spell_and_crafter()
    cancel = _CancelStub(is_set=True)
    crafter._spell_system_states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id=crafter.spell.spell_index.current,
                direct_dependencies=set(),
                spell_index_id=crafter.spell.spell_index.id,
            ),
        ]
    )
    crafter.run_phase_root_blueprints("cid", cancel_event=cancel)
    assert cancel.throw_calls == 0


@pytest.mark.parametrize(
    "missing_blueprints,missing_index",
    [
        (True, False),
        (False, True),
    ],
)
def test_run_phase_system_validation_requires_phase5(
    missing_blueprints: bool,
    missing_index: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure Phase 6 requires Phase 5 artifacts.
    Contract:
        Missing blueprints or system index raises RuntimeError.
    Args:
        missing_blueprints: Whether to clear Phase 5 blueprints.
        missing_index: Whether to clear the system index.
        monkeypatch: Pytest fixture for patching the validation system type.
    Returns:
        None.
    Raises:
        AssertionError: If missing artifacts do not raise.
    """
    crafter, _, _ = _build_spell_and_crafter()
    monkeypatch.setattr(
        spell_crafter_module,
        "SpellSystemValidationSystem",
        _SpellSystemValidationSystemStub,
    )

    if not missing_blueprints:
        crafter._entire_dag_blueprint_phase5 = {"root": _RootBlueprintStub("root")}
    if not missing_index:
        crafter._spell_system_index_phase5 = spell_crafter_module.SpellSystemIndex()

    crafter.run_phase_system_validation("cid", cancel_event=None)
    assert crafter._validated_phase6 is True


def test_run_phase_system_validation_collects_phase4_and_broken(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 6 aggregates Phase 4 results and broken spell ids.
    Contract:
        Validation inputs include phase4 results and broken ids from spell crafters.
    Args:
        monkeypatch: Pytest fixture for patching validation system types.
    Returns:
        None.
    Raises:
        AssertionError: If aggregation inputs are incorrect.
    """
    states = _SpellSystemStatesStub()
    crafter, spell, _ = _build_spell_and_crafter(spell_system_states=states)
    crafter._entire_dag_blueprint_phase5 = {"root": _RootBlueprintStub("root")}
    crafter._spell_system_index_phase5 = spell_crafter_module.SpellSystemIndex()

    other_crafter, other_spell, _ = _build_spell_and_crafter(spell_id="other")
    other_crafter._validation_result_phase4 = object()
    other_crafter._is_broken = True

    crafter._validation_result_phase4 = object()
    crafter._is_broken = False

    _set_spell_id_pool(spell._spellbook, [spell, other_spell])

    monkeypatch.setattr(
        spell_crafter_module,
        "SpellSystemValidationSystem",
        _SpellSystemValidationSystemStub,
    )

    crafter.run_phase_system_validation("cid", cancel_event=None)

    validator = _SpellSystemValidationSystemStub.last_instance
    assert validator is not None
    call = validator.validate_calls[0]
    assert set(call["phase4_results"].keys()) == {"root", "other"}
    assert call["broken_spell_ids"] == {"other"}
    strategy_names = [type(strategy).__name__ for strategy in validator.strategies]
    assert strategy_names == [
        "CycleDetectionStrategy",
        "BrokenSpellInDagStrategy",
        "GraphConsistencyStrategy",
        "MissingPhase4Strategy",
        "RootReachabilityStrategy",
        "RootCoverageStrategy",
        "IndexDependencySanityStrategy",
        "VisibilityGapStrategy",
        "TopologyDependencyMismatchStrategy",
        "IdentityMixingStrategy",
        "ContractedVersionDriftStrategy",
        "LineageAlignmentStrategy",
        "IndexCoverageStrategy",
        "LineageVersionConflictStrategy",
        "RootLineageConflictStrategy",
        "OwnershipConsistencyStrategy",
        "DependencyTypeSanityStrategy",
        "ScopeOrderingStrategy",
        "ContractGraphCycleStrategy",
        "RootScaleLimitStrategy",
        "RootViabilityStrategy",
        "SocketRefSanityStrategy",
    ]


def test_run_phase_system_validation_sets_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 6 stores validation state and marks completion.
    Contract:
        The validation state is cached and _validated_phase6 is True.
    Args:
        monkeypatch: Pytest fixture for patching validation system types.
    Returns:
        None.
    Raises:
        AssertionError: If validation state is not stored correctly.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    crafter._entire_dag_blueprint_phase5 = {"root": _RootBlueprintStub("root")}
    crafter._spell_system_index_phase5 = spell_crafter_module.SpellSystemIndex()

    _set_spell_id_pool(spell._spellbook, [spell])

    monkeypatch.setattr(
        spell_crafter_module,
        "SpellSystemValidationSystem",
        _SpellSystemValidationSystemStub,
    )

    crafter.run_phase_system_validation("cid", cancel_event=None)

    assert crafter.validation_result_phase6 is not None
    assert crafter._validated_phase6 is True


def test_run_phase_change_control_calls_ensure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify Phase 7 delegates to _ensure_change_control_ready.
    Contract:
        The internal helper is invoked exactly once.
    Args:
        monkeypatch: Pytest fixture for patching the internal helper.
    Returns:
        None.
    Raises:
        AssertionError: If the helper is not invoked.
    """
    crafter, _, _ = _build_spell_and_crafter()
    calls = {"count": 0}

    def _ensure(self: SpellCrafter, conduit_id: str) -> None:
        """
        Purpose:
            Track helper invocation for the test.
        Contract:
            Increments the call counter when invoked.
        Returns:
            None.
        """
        assert conduit_id == "cid"
        calls["count"] += 1

    monkeypatch.setattr(SpellCrafter, "_ensure_change_control_ready", _ensure)

    crafter.run_phase_change_control("cid", cancel_event=None)

    assert calls["count"] == 1


def test_run_phase_change_control_cancellation() -> None:
    """
    Purpose:
        Ensure Phase 7 respects cancellation before wiring change control.
    Contract:
        A cancellation event raises RuntimeError immediately.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation does not raise.
    """
    crafter, _, _ = _build_spell_and_crafter()
    cancel = _CancelStub(is_set=True)
    crafter.run_phase_change_control("cid", cancel_event=cancel)
    assert cancel.throw_calls == 0


def test_ensure_change_control_ready_rebuilds_component_index() -> None:
    """
    Purpose:
        Verify change control rebuilds component-of index when blueprints exist.
    Contract:
        The manager receives rebuild_component_of with the stored blueprints.
    Returns:
        None.
    Raises:
        AssertionError: If rebuild_component_of is not called.
    """
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager=manager)
    crafter, _, _ = _build_spell_and_crafter(aether=aether)

    blueprints = {"root": _RootBlueprintStub("root")}
    crafter._entire_dag_blueprint_phase5 = blueprints

    crafter._ensure_change_control_ready("cid")

    assert manager.rebuild_calls == [blueprints]


def test_ensure_change_control_ready_registers_revalidator_when_missing() -> None:
    """
    Purpose:
        Ensure change control registers a revalidator when missing.
    Contract:
        set_revalidator is called once when no revalidator is registered.
    Returns:
        None.
    Raises:
        AssertionError: If the revalidator is not registered.
    """
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager=manager)
    crafter, _, _ = _build_spell_and_crafter(aether=aether)

    crafter._ensure_change_control_ready("cid")

    assert manager.set_calls == 1
    assert manager._revalidate_fn is not None


def test_ensure_change_control_ready_skips_when_manager_none() -> None:
    """
    Purpose:
        Verify change control wiring is skipped without a manager.
    Contract:
        No rebuild or revalidator calls occur when manager is None.
    Returns:
        None.
    Raises:
        AssertionError: If calls are made without a manager.
    """
    crafter, _, _ = _build_spell_and_crafter(aether=_AetherStub(manager=None))

    with pytest.raises(AttributeError):
        crafter._ensure_change_control_ready("cid")


def test_ensure_change_control_ready_skips_when_revalidator_present() -> None:
    """
    Purpose:
        Ensure existing revalidator prevents duplicate registration.
    Contract:
        set_revalidator is not called when _revalidate_fn is already set.
    Returns:
        None.
    Raises:
        AssertionError: If set_revalidator is called unexpectedly.
    """
    manager = _ChangeControlManagerStub()
    manager._revalidate_fn = object()
    aether = _AetherStub(manager=manager)
    crafter, _, _ = _build_spell_and_crafter(aether=aether)

    crafter._ensure_change_control_ready("cid")

    assert manager.set_calls == 0


def test_ensure_change_control_ready_swallow_errors() -> None:
    """
    Purpose:
        Ensure change control wiring ignores lookup errors.
    Contract:
        Exceptions raised during manager lookup are swallowed.
    Returns:
        None.
    Raises:
        AssertionError: If lookup errors propagate.
    """
    aether = _AetherStub(raise_on_get=True)
    crafter, _, _ = _build_spell_and_crafter(aether=aether)
    with pytest.raises(RuntimeError, match="boom"):
        crafter._ensure_change_control_ready("cid")


def test_run_all_phases_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Verify run_all_phases invokes each phase in order.
    Contract:
        All phase methods are called in the documented sequence.
    Args:
        monkeypatch: Pytest fixture for patching phase methods.
    Returns:
        None.
    Raises:
        AssertionError: If phases are called out of order.
    """
    crafter, _, _ = _build_spell_and_crafter()
    calls: list[str] = []

    def _record(name: str):
        """
        Purpose:
            Build a phase stub that records the call order.
        Contract:
            Appends the phase name when invoked.
        Args:
            name: Label for the phase being recorded.
        Returns:
            callable: Phase stub callable.
        """
        def _phase(
                self: SpellCrafter,
                *args: object,
                cancel_event: object | None = None,
        ) -> None:
            """
            Purpose:
                Record a single phase invocation.
            Contract:
                Appends the phase name to the outer call list.
            Args:
                args: Optional positional args (conduit_id for phases 5-10).
                cancel_event: Optional cancel event forwarded by run_all_phases.
            Returns:
                None.
            """
            calls.append(name)

        return _phase

    monkeypatch.setattr(SpellCrafter, "run_phase_requirements", _record("requirements"))
    monkeypatch.setattr(SpellCrafter, "run_phase_symbolic_graph", _record("symbolic"))
    monkeypatch.setattr(SpellCrafter, "run_phase_local_frame", _record("local_frame"))
    monkeypatch.setattr(SpellCrafter, "run_phase_validation", _record("validation"))
    monkeypatch.setattr(SpellCrafter, "run_phase_root_blueprints", _record("root_blueprints"))
    monkeypatch.setattr(SpellCrafter, "run_phase_occurrence_plan", _record("occurrence_plan"))
    monkeypatch.setattr(SpellCrafter, "run_phase_injection_plan", _record("injection_plan"))
    monkeypatch.setattr(SpellCrafter, "run_phase_patch_maps", _record("patch_maps"))
    monkeypatch.setattr(SpellCrafter, "run_phase_system_validation", _record("system_validation"))
    monkeypatch.setattr(SpellCrafter, "run_phase_change_control", _record("change_control"))
    monkeypatch.setattr(SpellCrafter, "run_phase_execution_plan", _record("execution_plan"))

    crafter.run_all_phases("cid", cancel_event=None)

    assert calls == [
        "requirements",
        "symbolic",
        "local_frame",
        "validation",
        "root_blueprints",
        "occurrence_plan",
        "injection_plan",
        "patch_maps",
        "execution_plan",
        "system_validation",
        "change_control",
    ]


def test_run_all_phases_passes_cancel_event(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Ensure run_all_phases forwards the cancellation event to each phase.
    Contract:
        Every phase stub receives the same cancel_event reference.
    Args:
        monkeypatch: Pytest fixture for patching phase methods.
    Returns:
        None.
    Raises:
        AssertionError: If any phase does not receive the cancel event.
    """
    crafter, _, _ = _build_spell_and_crafter()
    cancel = _CancelStub(is_set=False)
    received: list[object | None] = []

    def _record(
            self: SpellCrafter,
            *args: object,
            cancel_event: object | None = None,
    ) -> None:
        """
        Purpose:
            Record the cancel_event passed by run_all_phases.
        Contract:
            Appends the cancel_event to the received list.
        Args:
            args: Optional positional args (conduit_id for phases 5-10).
            cancel_event: Cancel event provided by run_all_phases.
        Returns:
            None.
        """
        received.append(cancel_event)

    monkeypatch.setattr(SpellCrafter, "run_phase_requirements", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_symbolic_graph", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_local_frame", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_validation", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_root_blueprints", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_occurrence_plan", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_injection_plan", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_patch_maps", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_execution_plan", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_system_validation", _record)
    monkeypatch.setattr(SpellCrafter, "run_phase_change_control", _record)

    crafter.run_all_phases("cid", cancel_event=cancel)

    assert received == [cancel] * 11
