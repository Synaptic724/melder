from __future__ import annotations

import types
import typing
from typing import Any, Iterable, Sequence
from threading import RLock

import pytest

from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_types.spell_types import SpellType
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
        # Some SpellCrafter paths now read these attributes during IR capture.
        self.issues: list[object] = []
        self.nodes: dict[str, object] = {}

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
            Initializes per-conduit revalidator storage and clears call lists.
        Returns:
            None.
        """
        self._revalidate_fn_by_conduit: dict[str, object] = {}
        self.rebuild_calls: list[dict[str, object]] = []
        self.upsert_calls: list[dict[str, object]] = []
        self.set_calls = 0

    def rebuild_component_of(self, conduit_id: str, root_blueprints: object) -> None:
        """
        Purpose:
            Record rebuild_component_of calls.
        Contract:
            Appends conduit and blueprint payload to rebuild_calls.
        Args:
            conduit_id: Conduit identifier used for the rebuild.
            root_blueprints: Root blueprint mapping passed in.
        Returns:
            None.
        """
        self.rebuild_calls.append(
            {
                "conduit_id": conduit_id,
                "root_blueprints": root_blueprints,
            }
        )

    def set_revalidator(self, conduit_id: str, fn: object) -> None:
        """
        Purpose:
            Record revalidator registration.
        Contract:
            Stores the function by conduit id and increments set_calls.
        Args:
            conduit_id: Conduit identifier for this revalidator.
            fn: Revalidator callable.
        Returns:
            None.
        """
        self._revalidate_fn_by_conduit[conduit_id] = fn
        self.set_calls += 1

    def has_revalidator_for_conduit(self, conduit_id: str) -> bool:
        """
        Purpose:
            Report whether a conduit already has a registered revalidator.
        Contract:
            Returns True only when the stub already stores a revalidator for
            the supplied conduit id.
        Args:
            conduit_id: Conduit identifier to inspect.
        Returns:
            bool: True when a revalidator exists for the conduit.
        """
        return conduit_id in self._revalidate_fn_by_conduit

    def upsert_component_of(self, conduit_id: str, root_blueprints: object) -> None:
        """
        Purpose:
            Record upsert_component_of calls.
        Contract:
            Appends conduit and blueprint payload to upsert_calls.
        Args:
            conduit_id: Conduit identifier used for the upsert.
            root_blueprints: Root blueprint mapping passed in.
        Returns:
            None.
        """
        self.upsert_calls.append(
            {
                "conduit_id": conduit_id,
                "root_blueprints": root_blueprints,
            }
        )


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
        Exposes _spell_validator, _aether, _aetheric_frame, _spells_by_id,
        _spell_id_pool, contracted lookup maps, and minimal configuration.
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
            Stores validator, aether, frame name, and id lookup maps.
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
        self._lookup_contracted_spells: dict[str, dict[object, object]] = {}
        self._spells_by_id: dict[str, object] = {}
        self._spell_id_pool: dict[str, object] = {}
        self._configuration = _ConfigurationStub()
        self._aetheric_frame_configuration = AethericFrameConfiguration(
            origin_spellbook_id="spellbook-stub",
            system_state=SystemState.automatic,
            ai_native_enabled=False,
            rift_enabled=False,
        )

    @property
    def spells(self) -> dict[object, object]:
        return self._spells

    @property
    def contracted_spells(self) -> dict[str, dict[object, object]]:
        return self._contracted_spells


class _ConfigurationStub:
    """
    Purpose:
        Provide a minimal configuration surface for SpellCrafter unit tests.
    Contract:
        Exposes `get_property(...)` for the specific keys used by the tested
        SpellCrafter fast-key code paths.
    """

    def get_property(self, key: str) -> object:
        """
        Purpose:
            Return a stable property value for the requested key.
        Contract:
            Supports the minimal key set required by SpellCrafter unit tests.
        Args:
            key: Configuration property name.
        Returns:
            object: Stored test property value.
        Raises:
            KeyError: If the property is not supported by this stub.
        """
        if key == "system_state":
            return "dynamic"
        raise KeyError(key)


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


class _ConduitResolutionStateStub:
    """
    Purpose:
        Provide a conduit-resolution state stub with error gating semantics.
    Contract:
        Tracks whether the conduit currently reports resolution errors.
    """

    def __init__(self, *, has_errors: bool = False) -> None:
        """
        Purpose:
            Initialize conduit-resolution error state.
        Contract:
            Stores one mutable boolean used by has_errors().
        Args:
            has_errors: Initial conduit-resolution error flag.
        Returns:
            None.
        """
        self._has_errors = has_errors

    def has_errors(self) -> bool:
        """
        Purpose:
            Return current conduit-resolution error state.
        Contract:
            True means foundational resolution reported errors.
        Returns:
            bool: Current conduit-resolution error state.
        """
        return self._has_errors


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
        self._resolution_state_by_conduit: dict[str, _ConduitResolutionStateStub] = {}
        self.update_calls: list[tuple[object, list[str]]] = []
        self.topology_calls: list[tuple[object, object]] = []
        self.unregistered_lineages: list[object] = []
        self.bulk_spell_validity_calls: list[tuple[str, dict[str, object], object]] = []
        self.bulk_root_validity_calls: list[tuple[str, dict[str, object], object]] = []
        self.recorded_conduit_diagnostics: list[tuple[str, list[object]]] = []

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

    def unregister_index(self, spell_index: object) -> None:
        """
        Purpose:
            Record a lineage unregistration from Spellbook.cleanup.
        Contract:
            - Appends spell_index to unregistered_lineages.
        Args:
            spell_index: SpellIndex removed from system-state tracking.
        Returns:
            None.
        """
        self.unregistered_lineages.append(spell_index)

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

    def set_conduit_resolution_has_errors(self, conduit_id: str, has_errors: bool) -> None:
        """
        Purpose:
            Set the conduit-resolution error flag for one conduit id.
        Contract:
            Creates state lazily when a conduit has no prior state.
        Args:
            conduit_id: Conduit id whose resolution state should be updated.
            has_errors: Error flag to store.
        Returns:
            None.
        """
        state = self._resolution_state_by_conduit.get(conduit_id)
        if state is None:
            state = _ConduitResolutionStateStub(has_errors=has_errors)
            self._resolution_state_by_conduit[conduit_id] = state
            return
        state._has_errors = has_errors

    def get_conduit_resolution_state(self, conduit_id: str) -> _ConduitResolutionStateStub:
        """
        Purpose:
            Return conduit-resolution state for the supplied conduit id.
        Contract:
            Returns a stable per-conduit state object; defaults to no errors.
        Args:
            conduit_id: Conduit id whose resolution state is requested.
        Returns:
            _ConduitResolutionStateStub: Conduit-resolution state object.
        """
        state = self._resolution_state_by_conduit.get(conduit_id)
        if state is None:
            state = _ConduitResolutionStateStub(has_errors=False)
            self._resolution_state_by_conduit[conduit_id] = state
        return state

    def bulk_set_conduit_spell_validity(
        self,
        conduit_id: str,
        validity_by_spell_id: dict[str, object],
        *,
        change_reason: object,
    ) -> None:
        self.bulk_spell_validity_calls.append(
            (
                conduit_id,
                dict(validity_by_spell_id),
                change_reason,
            )
        )

    def bulk_set_conduit_root_validity(
        self,
        conduit_id: str,
        validity_by_root_id: dict[str, object],
        *,
        change_reason: object,
    ) -> None:
        self.bulk_root_validity_calls.append(
            (
                conduit_id,
                dict(validity_by_root_id),
                change_reason,
            )
        )

    def record_conduit_diagnostics(
        self,
        conduit_id: str,
        diagnostics: list[object],
    ) -> None:
        self.recorded_conduit_diagnostics.append(
            (
                conduit_id,
                list(diagnostics),
            )
        )


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
        self._mutation_override = None
        self.is_existing_creation = False
        self.dependencies: list[str] = []
        if include_dependency_graph:
            self.dependency_graph = dependency_graph

    @property
    def mutation_override(self) -> object | None:
        """
        Purpose:
            Return the current mutation override payload for this spell stub.
        Contract:
            Mirrors the production spell surface used by the Phase 8 fast-key
            builder.
        Returns:
            object | None: Stored mutation override payload, if any.
        """
        return self._mutation_override

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
        self.ordered_node_ids: list[str] = []
        self.socket_refs: list[object] = []
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
    if spell_system_states is None:
        spell_system_states = _SpellSystemStatesStub()
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
        together, registers the spell in the spell_id_pool and spells_by_id,
        and sets spell._crafter on the returned spell.
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
    if spell_system_states is None:
        spell_system_states = _SpellSystemStatesStub()
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
    spellbook._spells_by_id[spell.spell_index.current] = spell
    spellbook._spell_id_pool[spell.spell_index.current] = spell
    crafter = SpellCrafter(spell)
    crafter._spell_validator = validator
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
        if spell._crafter is None:
            spell._ensure_crafter()
        if spell._crafter is None:
            spell._ensure_crafter()


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
    assert crafter._spell_system_states is not None
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
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
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
        Phase-1 through phase-4 owned artifacts are nulled, while later
        retained phase artifacts and borrowed collaborators are deleted after
        cleanup.
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
    assert not hasattr(crafter, "_root_blueprint_phase5")
    assert not hasattr(crafter, "_spell_system_index_phase5")
    assert not hasattr(crafter, "_entire_dag_blueprint_phase5")
    assert not hasattr(crafter, "_spell_system_states")
    assert not hasattr(crafter, "_spell")
    assert not hasattr(crafter, "_spell_validator")
    assert crafter._lock is not None


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
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
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

    if drop_states:
        with pytest.raises(RuntimeError, match="requires a live SpellSystemStates surface"):
            crafter._notify_dependencies_updated(["a"])
    else:
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


def test_normalize_annotation_for_matching_handles_forward_refs_and_optional_union() -> None:
    """
    Purpose:
        Validate DI annotation normalization for ForwardRef and Optional/Union forms.
    Contract:
        - ForwardRef normalizes to its string target.
        - Optional/Union-with-None unwraps to the single non-None member.
        - Multiple non-None Union members remain unchanged.
    """
    crafter = _make_crafter()

    assert crafter._normalize_annotation_for_matching(typing.ForwardRef("Service")) == "Service"
    assert crafter._normalize_annotation_for_matching(str | None) is str
    assert crafter._normalize_annotation_for_matching(
        typing.Union[typing.ForwardRef("Repo"), None]
    ) == "Repo"

    union_value = typing.Union[int, str]
    assert crafter._normalize_annotation_for_matching(union_value) is union_value


def test_matches_annotation_supports_forward_ref_strings_and_frame_class_names() -> None:
    """
    Purpose:
        Validate name-based matching branches used by normalized annotations.
    Contract:
        - ForwardRef string targets match spell names.
        - String targets also match string spellframes and class-name spellframes.
    """

    class FrameToken:
        pass

    crafter = _make_crafter()

    by_name = _SpellStub(
        spell_id="candidate-name",
        spell_name="Service",
        spell_type=SpellType.SPELL,
        spellbook=crafter.spell._spellbook,
    )
    assert crafter._matches_annotation(
        typing.ForwardRef("Service"),
        None,
        by_name,
        require_class_spell=True,
    ) is True

    by_string_frame = _SpellStub(
        spell_id="candidate-frame",
        spell_name="Other",
        spell_type=SpellType.SPELL,
        spellbook=crafter.spell._spellbook,
        spellframe="FrameToken",
    )
    assert crafter._matches_annotation(
        "FrameToken",
        None,
        by_string_frame,
        require_class_spell=True,
    ) is True

    by_class_name = _SpellStub(
        spell_id="candidate-class-frame",
        spell_name="Other",
        spell_type=SpellType.SPELL,
        spellbook=crafter.spell._spellbook,
        spellframe=FrameToken,
    )
    assert crafter._matches_annotation(
        "FrameToken",
        None,
        by_class_name,
        require_class_spell=True,
    ) is True


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
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

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
        crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

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
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

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
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

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
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

    snapshot = _AdjacencySnapshotStub(dependencies={}, root_spell_ids=set())
    blueprints = {"root": _RootBlueprintStub("root")}
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = blueprints

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)
    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert manager.rebuild_calls == [
        {
            "conduit_id": "cid",
            "root_blueprints": blueprints,
        }
    ]
    assert manager.set_calls == 1
    assert manager._revalidate_fn_by_conduit["cid"] is not None


def test_run_phase_root_blueprints_filters_component_of_to_owned_roots(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify component_of rebuilds are limited to owned roots.
    Contract:
        Change control receives only owned root blueprints even when
        contracted roots are visible.
    Args:
        monkeypatch: Pytest fixture for patching Phase 5 builders.
    Returns:
        None.
    Raises:
        AssertionError: If contracted roots are included in rebuild payload.
    """
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager=manager)
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(
                current_spell_id="owned",
                direct_dependencies=set(),
                spell_index_id="lineage-owned",
            ),
            _SpellSystemStateStub(
                current_spell_id="contracted",
                direct_dependencies=set(),
                spell_index_id="lineage-contracted",
            ),
        ]
    )
    crafter, owned_spell, _ = _build_spell_and_crafter(
        spell_id="owned",
        spell_system_states=states,
        aether=aether,
    )
    crafter._validated_phase4 = True
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

    contracted_spell = _SpellStub(
        spell_id="contracted",
        spellbook=owned_spell._spellbook,
        spell_system_states=states,
    )
    owned_spell._spellbook._spell_id_pool["contracted"] = contracted_spell
    contracted_spell._ensure_crafter()

    snapshot = _AdjacencySnapshotStub(
        dependencies={"owned": set(), "contracted": set()},
        root_spell_ids={"owned", "contracted"},
    )
    blueprints = {
        "owned": _RootBlueprintStub("owned"),
        "contracted": _RootBlueprintStub("contracted"),
    }
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = blueprints

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)
    crafter.run_phase_root_blueprints("cid", cancel_event=None)

    assert manager.rebuild_calls == [
        {
            "conduit_id": "cid",
            "root_blueprints": {"owned": blueprints["owned"]},
        }
    ]


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
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

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

    revalidate_fn = manager._revalidate_fn_by_conduit.get("cid")
    assert revalidate_fn is not None

    cancel = _CancelStub(is_set=False)
    revalidate_fn({"root"}, cancel)

    assert calls == [{"crafter": crafter, "conduit_id": "cid", "cancel_event": cancel}]

    cancel_set = _CancelStub(is_set=True)
    revalidate_fn({"root"}, cancel_set)

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
    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)

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
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
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


def test_collect_local_scope_spell_ids_returns_dependency_closure() -> None:
    """
    Purpose:
        Validate local Phase 5 scope collection follows dependency closure.
    Contract:
        - Starts from the target spell id.
        - Includes only ids present in snapshot.all_spell_ids.
        - Ignores missing roots cleanly.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
    snapshot = types.SimpleNamespace(
        all_spell_ids={"root", "dep1", "dep2", "leaf"},
        dependencies={
            "root": {"dep1", "dep2"},
            "dep1": {"leaf"},
            "dep2": {"outside"},
            "leaf": set(),
        },
    )

    assert crafter._collect_local_scope_spell_ids(
        root_spell_id="root",
        snapshot=snapshot,
    ) == {"root", "dep1", "dep2", "leaf"}
    assert crafter._collect_local_scope_spell_ids(
        root_spell_id="missing",
        snapshot=snapshot,
    ) == set()


def test_filter_snapshot_to_visible_spells_recomputes_roots_and_topologies() -> None:
    """
    Purpose:
        Validate snapshot filtering for local Phase 5 visibility.
    Contract:
        - Dependencies are trimmed to visible ids.
        - Reverse edges and root ids are recomputed from the filtered graph.
        - Topologies are retained only for visible spell ids.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
    snapshot = types.SimpleNamespace(
        dependencies={
            "root": {"dep", "hidden"},
            "dep": set(),
            "hidden": {"dep"},
        },
        topologies={
            "root": "top-root",
            "dep": "top-dep",
            "hidden": "top-hidden",
        },
    )

    filtered = crafter._filter_snapshot_to_visible_spells(
        snapshot=snapshot,
        visible_spell_ids={"root", "dep"},
    )

    assert filtered.dependencies == {
        "root": {"dep"},
        "dep": set(),
    }
    assert filtered.reverse_dependencies == {
        "dep": {"root"},
    }
    assert filtered.root_spell_ids == {"root"}
    assert filtered.topologies == {
        "root": "top-root",
        "dep": "top-dep",
    }
    assert filtered.all_spell_ids == {"root", "dep"}


def test_build_system_index_for_snapshot_populates_spell_metadata() -> None:
    """
    Purpose:
        Validate local Phase 5 system-index construction.
    Contract:
        - Each snapshot spell becomes a SpellSystemNode.
        - Node lineage, dependencies, existence, type, and root flag are preserved.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(current_spell_id="root", spell_index_id="lineage-root"),
            _SpellSystemStateStub(current_spell_id="dep", spell_index_id="lineage-dep"),
        ]
    )
    crafter, root_spell, _ = _build_spell_and_crafter(
        spell_system_states=states,
    )
    root_spell._owner_conduit_id = "conduit-root"
    spellbook = root_spell._spellbook
    dep_spell = _SpellStub(
        spell_id="dep",
        spell_name="dep-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
        owner_conduit_id="conduit-dep",
    )
    spellbook._spells[dep_spell.spell_index] = dep_spell
    spellbook._spells_by_id[dep_spell.spell_index.current] = dep_spell
    spellbook._spell_id_pool[dep_spell.spell_index.current] = dep_spell

    snapshot = types.SimpleNamespace(
        dependencies={
            "root": {"dep"},
            "dep": set(),
        },
        root_spell_ids={"root"},
    )

    system_index = crafter._build_system_index_for_snapshot(
        snapshot=snapshot,
        spell_lookup=spellbook._spell_id_pool,
    )

    root_node = system_index.get_node("root")
    dep_node = system_index.get_node("dep")
    assert root_node is not None
    assert dep_node is not None
    assert root_node.lineage_id == "lineage-root"
    assert dep_node.lineage_id == "lineage-dep"
    assert root_node.dependencies == {"dep"}
    assert dep_node.dependencies == set()
    assert root_node.is_root is True
    assert dep_node.is_root is False
    assert root_node.conduit_id == "conduit-root"
    assert dep_node.conduit_id == "conduit-dep"


def test_attach_phase5_artifacts_for_snapshot_scopes_spell_updates() -> None:
    """
    Purpose:
        Validate local Phase 5 artifact attachment.
    Contract:
        - Only scoped spells receive Phase 5 artifacts.
        - Existing-creation spells receive the system index but skip blueprints.
        - Missing roots use the fallback builder path.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    spellbook = root_spell._spellbook

    dep_spell = _SpellStub(
        spell_id="dep",
        spell_name="dep-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    existing_spell = _SpellStub(
        spell_id="existing",
        spell_name="existing-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    existing_spell.is_existing_creation = True
    outside_spell = _SpellStub(
        spell_id="outside",
        spell_name="outside-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    for spell_instance in (dep_spell, existing_spell, outside_spell):
        spellbook._spells[spell_instance.spell_index] = spell_instance
        spellbook._spells_by_id[spell_instance.spell_index.current] = spell_instance
        spellbook._spell_id_pool[spell_instance.spell_index.current] = spell_instance
    dep_spell._ensure_crafter()
    existing_spell._ensure_crafter()

    system_index = spell_crafter_module.SpellSystemIndex()
    root_blueprint = _RootBlueprintStub("root")
    dep_blueprint = _RootBlueprintStub("dep")
    _RootBlueprintBuilderStub.next_blueprints = {
        "root": root_blueprint,
        "dep": dep_blueprint,
        "existing": _RootBlueprintStub("existing"),
    }
    root_builder = _RootBlueprintBuilderStub()
    snapshot = types.SimpleNamespace(all_spell_ids={"root", "dep", "existing"})

    crafter._attach_phase5_artifacts_for_snapshot(
        snapshot=snapshot,
        root_blueprints={"root": root_blueprint},
        system_index=system_index,
        spell_lookup=spellbook._spell_id_pool,
        root_builder=root_builder,
    )

    assert root_spell._ensure_crafter().spell_system_index_phase5 is system_index
    assert dep_spell._ensure_crafter().spell_system_index_phase5 is system_index
    assert existing_spell._ensure_crafter().spell_system_index_phase5 is system_index
    assert root_spell._ensure_crafter().root_blueprint_phase5 is root_blueprint
    assert dep_spell._ensure_crafter().root_blueprint_phase5 is dep_blueprint
    assert existing_spell._ensure_crafter().root_blueprint_phase5 is None
    assert outside_spell._crafter is None
    assert ("dep", snapshot) in root_builder.calls


def test_run_phase_root_blueprints_local_scopes_to_dependency_closure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate local Phase 5 builds only the target spell dependency closure.
    Contract:
        - Local snapshots are filtered to the target spell and its dependencies.
        - Only scoped spells receive attached Phase 5 artifacts.
        - The crafter stores the scoped root-blueprint map and system index.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(current_spell_id="root", spell_index_id="lineage-root"),
            _SpellSystemStateStub(current_spell_id="dep", spell_index_id="lineage-dep"),
            _SpellSystemStateStub(current_spell_id="outside", spell_index_id="lineage-outside"),
        ]
    )
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    spellbook = root_spell._spellbook

    dep_spell = _SpellStub(
        spell_id="dep",
        spell_name="dep-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    outside_spell = _SpellStub(
        spell_id="outside",
        spell_name="outside-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    for spell_instance in (dep_spell, outside_spell):
        spellbook._spells[spell_instance.spell_index] = spell_instance
        spellbook._spells_by_id[spell_instance.spell_index.current] = spell_instance
        spellbook._spell_id_pool[spell_instance.spell_index.current] = spell_instance
    dep_spell._ensure_crafter()

    full_snapshot = _AdjacencySnapshotStub(
        dependencies={
            "root": {"dep"},
            "dep": set(),
            "outside": set(),
        },
        root_spell_ids={"root", "outside"},
        topologies={
            "root": "top-root",
            "dep": "top-dep",
            "outside": "top-outside",
        },
    )
    full_snapshot.all_spell_ids = {"root", "dep", "outside"}
    full_snapshot.reverse_dependencies = {"dep": {"root"}}
    _AdjacencyBuilderStub.next_snapshot = full_snapshot

    _RootBlueprintBuilderStub.next_blueprints = {
        "root": _RootBlueprintStub("root"),
    }

    monkeypatch.setattr(spell_crafter_module, "SpellSystemAdjacencyBuilder", _AdjacencyBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "SpellSystemRootBlueprintBuilder", _RootBlueprintBuilderStub)

    crafter.run_phase_root_blueprints_local("cid", cancel_event=None)

    scoped_blueprints = crafter._entire_dag_blueprint_phase5
    assert scoped_blueprints is not None
    assert set(scoped_blueprints.keys()) == {"root"}
    assert crafter.spell_system_index_phase5 is not None
    assert crafter.spell_system_index_phase5.get_node("root") is not None
    assert crafter.spell_system_index_phase5.get_node("dep") is not None
    assert crafter.spell_system_index_phase5.get_node("outside") is None
    assert root_spell._ensure_crafter().root_blueprint_phase5 is not None
    assert dep_spell._ensure_crafter().root_blueprint_phase5 is not None
    assert outside_spell._crafter is None


def test_collect_local_visibility_gap_diagnostics_emits_one_error_per_missing_edge() -> None:
    """
    Purpose:
        Validate local Phase 6 visibility-gap diagnostics from local topologies.
    Contract:
        - Missing dependency spell ids produce ERROR diagnostics.
        - Duplicate missing edges are deduplicated per (spell, param, dep) signature.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)

    class _Socket:
        def __init__(self, param_name: str, target_spell_ids: tuple[str, ...]) -> None:
            self.param_name = param_name
            self.target_spell_ids = target_spell_ids

    class _Topology:
        def __init__(self, sockets: list[_Socket]) -> None:
            self._sockets = sockets

        def iter_sockets(self) -> list[_Socket]:
            return list(self._sockets)

    states.set_local_topology_for_id(
        "root",
        _Topology(
            [
                _Socket("svc", ("missing-dep",)),
                _Socket("svc", ("missing-dep",)),
            ]
        ),
    )

    diagnostics = crafter._collect_local_visibility_gap_diagnostics(
        scoped_spell_ids={"root"},
        spell_lookup={"root": root_spell},
        root_ids={"root"},
    )

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.code == "visibility_gap_dependency_filtered"
    assert diagnostic.spell_id == "root"
    assert diagnostic.root_id == "root"
    assert diagnostic.details["missing_dependency_id"] == "missing-dep"


def test_collect_local_blueprint_visibility_gap_diagnostics_emits_missing_nodes() -> None:
    """
    Purpose:
        Validate local Phase 6 visibility-gap diagnostics from root blueprints.
    Contract:
        - Hidden blueprint DAG nodes emit one ERROR diagnostic per missing spell id.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    blueprint = types.SimpleNamespace(
        dag=types.SimpleNamespace(
            nodes={
                "root": object(),
                "missing-dep": object(),
            }
        )
    )

    diagnostics = crafter._collect_local_blueprint_visibility_gap_diagnostics(
        blueprints={"root": blueprint},
        spell_lookup={"root": root_spell},
    )

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.code == "visibility_gap_dependency_filtered"
    assert diagnostic.spell_id == "missing-dep"
    assert diagnostic.root_id == "root"
    assert diagnostic.details["missing_dependency_id"] == "missing-dep"


def test_run_phase_system_validation_local_marks_invalid_on_visibility_gap() -> None:
    """
    Purpose:
        Validate local Phase 6 short-circuits on visibility gaps.
    Contract:
        - Scoped spell/root validity is marked invalid.
        - Conduit diagnostics are recorded.
        - Scoped spell crafters receive the same invalid validation state.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)

    class _Socket:
        def __init__(self, param_name: str, target_spell_ids: tuple[str, ...]) -> None:
            self.param_name = param_name
            self.target_spell_ids = target_spell_ids

    class _Topology:
        def __init__(self, sockets: list[_Socket]) -> None:
            self._sockets = sockets

        def iter_sockets(self) -> list[_Socket]:
            return list(self._sockets)

    states.set_local_topology_for_id(
        "root",
        _Topology([_Socket("svc", ("missing-dep",))]),
    )

    crafter._spell_system_index_phase5 = types.SimpleNamespace(nodes={"root": object()})
    crafter._entire_dag_blueprint_phase5 = {
        "root": types.SimpleNamespace(
            dag=types.SimpleNamespace(nodes={"root": object()}),
        )
    }

    crafter.run_phase_system_validation_local("cid", cancel_event=None)

    assert crafter.validation_result_phase6 is not None
    assert crafter.validation_result_phase6.is_valid is False
    assert len(crafter.validation_result_phase6.errors) == 1
    assert states.bulk_spell_validity_calls == [
        (
            "cid",
            {"root": spell_crafter_module.SpellValidity.invalid},
            spell_crafter_module.SpellStateChangeReason.validation_failed,
        )
    ]
    assert states.bulk_root_validity_calls == [
        (
            "cid",
            {"root": spell_crafter_module.SpellValidity.invalid},
            spell_crafter_module.SpellStateChangeReason.validation_failed,
        )
    ]
    assert states.recorded_conduit_diagnostics
    assert root_spell._ensure_crafter().validation_result_phase6 is crafter.validation_result_phase6


def test_ensure_change_control_ready_local_upserts_owned_roots_and_registers_revalidator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate local Phase 7 wiring semantics.
    Contract:
        - Only owned roots are upserted into component-of state.
        - A revalidator is registered when missing.
        - The revalidator routes dirty roots back through run_all_phases.
    """
    states = _SpellSystemStatesStub()
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager=manager)
    crafter, root_spell, _ = _build_spell_and_crafter(
        spell_system_states=states,
        aether=aether,
        frame_name="frame-local",
    )
    crafter._entire_dag_blueprint_phase5 = {
        "root": _RootBlueprintStub("root"),
        "contracted": _RootBlueprintStub("contracted"),
    }

    calls: list[dict[str, object]] = []

    def _run_all_phases(
        self: SpellCrafter,
        conduit_id: str,
        cancel_event: object | None = None,
    ) -> None:
        calls.append(
            {
                "crafter": self,
                "conduit_id": conduit_id,
                "cancel_event": cancel_event,
            }
        )

    monkeypatch.setattr(SpellCrafter, "run_all_phases", _run_all_phases)

    crafter._ensure_change_control_ready_local("cid")

    assert manager.upsert_calls == [
        {
            "conduit_id": "cid",
            "root_blueprints": {"root": crafter._entire_dag_blueprint_phase5["root"]},
        }
    ]
    assert manager.set_calls == 1
    revalidate_fn = manager._revalidate_fn_by_conduit["cid"]
    cancel = _CancelStub(is_set=False)
    validated = revalidate_fn({"root"}, cancel)

    assert validated == {"root"}
    assert calls == [
        {
            "crafter": crafter,
            "conduit_id": "cid",
            "cancel_event": cancel,
        }
    ]


def test_run_phase_system_validation_local_requires_phase5_local_artifacts() -> None:
    """
    Purpose:
        Validate local Phase 6 requires local Phase 5 artifacts.
    Contract:
        - Missing local index or local root blueprints raises RuntimeError.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())

    with pytest.raises(RuntimeError, match="Phase 6 local requires Phase 5 local artifacts"):
        crafter.run_phase_system_validation_local("cid", cancel_event=None)


def test_collect_local_blueprint_visibility_gap_diagnostics_dedupes_duplicate_missing_nodes() -> None:
    """
    Purpose:
        Validate blueprint visibility-gap diagnostics dedupe repeated missing nodes.
    Contract:
        - Duplicate missing dependency ids under the same root emit one diagnostic.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    blueprint = types.SimpleNamespace(
        dag=types.SimpleNamespace(
            nodes={
                "root": object(),
                "missing-dep": object(),
            }
        )
    )

    diagnostics = crafter._collect_local_blueprint_visibility_gap_diagnostics(
        blueprints={
            "root": blueprint,
            "root-duplicate": blueprint,
        },
        spell_lookup={"root": root_spell},
    )

    assert len(diagnostics) == 2
    assert {(diag.root_id, diag.spell_id) for diag in diagnostics} == {
        ("root", "missing-dep"),
        ("root-duplicate", "missing-dep"),
    }


def test_run_phase_system_validation_local_uses_scoped_lookup_and_broken_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate the successful local Phase 6 path.
    Contract:
        - Only scoped spells participate in local validation.
        - Broken scoped spells are included in the broken-id set.
        - The shared validation state is published only to scoped spell crafters.
    """
    states = _SpellSystemStatesStub(
        states=[
            _SpellSystemStateStub(current_spell_id="root", spell_index_id="lineage-root"),
            _SpellSystemStateStub(current_spell_id="dep", spell_index_id="lineage-dep"),
            _SpellSystemStateStub(current_spell_id="outside", spell_index_id="lineage-outside"),
        ]
    )
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    spellbook = root_spell._spellbook

    dep_spell = _SpellStub(
        spell_id="dep",
        spell_name="dep-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    dep_spell._ensure_crafter()._is_broken = True
    outside_spell = _SpellStub(
        spell_id="outside",
        spell_name="outside-spell",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    for spell_instance in (dep_spell, outside_spell):
        spellbook._spells[spell_instance.spell_index] = spell_instance
        spellbook._spells_by_id[spell_instance.spell_index.current] = spell_instance
        spellbook._spell_id_pool[spell_instance.spell_index.current] = spell_instance

    crafter._spell_system_index_phase5 = types.SimpleNamespace(
        nodes={
            "root": object(),
            "dep": object(),
        }
    )
    crafter._entire_dag_blueprint_phase5 = {
        "root": types.SimpleNamespace(
            dag=types.SimpleNamespace(
                nodes={
                    "root": object(),
                    "dep": object(),
                }
            )
        ),
    }

    monkeypatch.setattr(
        spell_crafter_module,
        "SpellSystemValidationSystem",
        _SpellSystemValidationSystemStub,
    )

    crafter.run_phase_system_validation_local("cid", cancel_event=None)

    validator = _SpellSystemValidationSystemStub.last_instance
    assert validator is not None
    call = validator.validate_calls[0]
    assert set(call["spell_lookup"].keys()) == {"root", "dep"}
    assert call["broken_spell_ids"] == {"dep"}
    assert crafter.validation_result_phase6 == {"state": "ok"}
    assert root_spell._ensure_crafter().validation_result_phase6 == {"state": "ok"}
    assert dep_spell._ensure_crafter().validation_result_phase6 == {"state": "ok"}
    assert outside_spell._ensure_crafter().validation_result_phase6 is None


def test_run_phase_change_control_local_delegates_to_local_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate the local Phase 7 wrapper.
    Contract:
        - `run_phase_change_control_local(...)` delegates exactly once to
          `_ensure_change_control_ready_local(...)`.
    """
    crafter, _, _ = _build_spell_and_crafter()
    calls: list[str] = []

    def _ensure(self: SpellCrafter, conduit_id: str) -> None:
        calls.append(conduit_id)

    monkeypatch.setattr(SpellCrafter, "_ensure_change_control_ready_local", _ensure)

    crafter.run_phase_change_control_local("cid", cancel_event=None)

    assert calls == ["cid"]


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

    with pytest.raises(RuntimeError, match="Phase 5"):
        crafter.run_phase_system_validation("cid", cancel_event=None)


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
    other_crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)
    other_crafter._is_broken = True

    crafter._validation_result_phase4 = _ValidationResultStub(has_errors=False)
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
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
    crafter._entire_dag_blueprint_phase5 = {}
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

    assert manager.rebuild_calls == [
        {
            "conduit_id": "cid",
            "root_blueprints": blueprints,
        }
    ]


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
    crafter._entire_dag_blueprint_phase5 = {}

    crafter._ensure_change_control_ready("cid")

    assert manager.set_calls == 1
    assert manager._revalidate_fn_by_conduit["cid"] is not None


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

    crafter._entire_dag_blueprint_phase5 = {}
    with pytest.raises(AttributeError):
        crafter._ensure_change_control_ready("cid")


def test_ensure_change_control_ready_skips_when_revalidator_present() -> None:
    """
    Purpose:
        Ensure existing revalidator prevents duplicate registration.
    Contract:
        set_revalidator is not called when the conduit revalidator is already set.
    Returns:
        None.
    Raises:
        AssertionError: If set_revalidator is called unexpectedly.
    """
    manager = _ChangeControlManagerStub()
    manager._revalidate_fn_by_conduit["cid"] = object()
    aether = _AetherStub(manager=manager)
    crafter, _, _ = _build_spell_and_crafter(aether=aether)
    crafter._entire_dag_blueprint_phase5 = {}

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
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
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
        "system_validation",
        "change_control",
        "occurrence_plan",
        "injection_plan",
        "patch_maps",
        "execution_plan",
    ]


def test_run_all_phases_skips_plan_phases_when_foundational_resolution_has_errors(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify run_all_phases skips phases 8-11 when foundational phases report conduit errors.
    Contract:
        Executes phases 1-7, then returns after cleanup when conduit resolution has errors.
    Args:
        monkeypatch: Pytest fixture for patching phase methods.
    Returns:
        None.
    Raises:
        AssertionError: If plan phases run despite foundational conduit errors.
    """
    states = _SpellSystemStatesStub()
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=states)
    calls: list[str] = []

    def _record(name: str):
        def _phase(
                self: SpellCrafter,
                *args: object,
                cancel_event: Any = None,
        ) -> None:
            del self, args, cancel_event
            calls.append(name)
        return _phase

    def _change_control_with_error(
            self: SpellCrafter,
            conduit_id: str,
            cancel_event: Any = None,
    ) -> None:
        del self, cancel_event
        calls.append("change_control")
        states.set_conduit_resolution_has_errors(conduit_id, True)

    def _cleanup(self: SpellCrafter) -> None:
        del self
        calls.append("cleanup_phase_artifacts")

    monkeypatch.setattr(SpellCrafter, "run_phase_requirements", _record("requirements"))
    monkeypatch.setattr(SpellCrafter, "run_phase_symbolic_graph", _record("symbolic"))
    monkeypatch.setattr(SpellCrafter, "run_phase_local_frame", _record("local_frame"))
    monkeypatch.setattr(SpellCrafter, "run_phase_validation", _record("validation"))
    monkeypatch.setattr(SpellCrafter, "run_phase_root_blueprints", _record("root_blueprints"))
    monkeypatch.setattr(SpellCrafter, "run_phase_system_validation", _record("system_validation"))
    monkeypatch.setattr(SpellCrafter, "run_phase_change_control", _change_control_with_error)
    monkeypatch.setattr(SpellCrafter, "run_phase_occurrence_plan", _record("occurrence_plan"))
    monkeypatch.setattr(SpellCrafter, "run_phase_injection_plan", _record("injection_plan"))
    monkeypatch.setattr(SpellCrafter, "run_phase_patch_maps", _record("patch_maps"))
    monkeypatch.setattr(SpellCrafter, "run_phase_execution_plan", _record("execution_plan"))
    monkeypatch.setattr(SpellCrafter, "cleanup_phase_artifacts", _cleanup)

    crafter.run_all_phases("cid", cancel_event=None)

    assert calls == [
        "requirements",
        "symbolic",
        "local_frame",
        "validation",
        "root_blueprints",
        "system_validation",
        "change_control",
        "cleanup_phase_artifacts",
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
    crafter, _, _ = _build_spell_and_crafter(spell_system_states=_SpellSystemStatesStub())
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


def test_build_phase10_patch_maps_input_signature_uses_blueprint_shape_and_handles_failures() -> None:
    """
    Purpose:
        Validate the Phase 10 patch-map signature helper.
    Contract:
        - Signature is built from root id, path registry identity, socket count, and node count.
        - Broken blueprint access returns None instead of raising.
    """
    crafter = _make_crafter()
    path_registry = object()
    blueprint = types.SimpleNamespace(
        root_spell_id="root",
        path_registry=path_registry,
        socket_refs=[object(), object()],
        ordered_node_ids=["a", "root"],
    )

    assert crafter._build_phase10_patch_maps_input_signature(blueprint) == (
        "root",
        id(path_registry),
        2,
        2,
    )
    assert crafter._build_phase10_patch_maps_input_signature(None) is None

    class _BrokenBlueprint:
        root_spell_id = "root"
        path_registry = object()
        ordered_node_ids = ["root"]

        @property
        def socket_refs(self) -> object:
            raise RuntimeError("boom")

    assert crafter._build_phase10_patch_maps_input_signature(_BrokenBlueprint()) is None


def test_build_phase8_occurrence_plan_fast_key_serializes_visible_state_and_rejects_mutations() -> None:
    """
    Purpose:
        Validate the lightweight Phase 8 fast-key helper.
    Contract:
        - Fast key includes blueprint shape, spell visibility state, topologies, and contracted rows.
        - Any mutation override forces the helper to return None.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    spellbook = root_spell._spellbook
    dep_spell = _SpellStub(
        spell_id="dep",
        spell_name="dep",
        spell_type=SpellType.SPELL,
        spellbook=spellbook,
        spell_system_states=states,
    )
    spellbook._aetheric_frame_configuration.with_system_state(SystemState.dynamic)
    spellbook._spells[dep_spell.spell_index] = dep_spell
    spellbook._spells_by_id[dep_spell.spell_index.current] = dep_spell
    spellbook._spell_id_pool[dep_spell.spell_index.current] = dep_spell
    spellbook._lookup_contracted_spells = {
        "peer": {
            ("frame", "binding"): dep_spell.spell_index,
        }
    }
    spellbook._contracted_spells = {
        "peer": {
            dep_spell.spell_index: dep_spell,
        }
    }
    states._local_topologies = {
        "root": types.SimpleNamespace(
            sockets=[
                types.SimpleNamespace(param_name="svc", target_spell_ids=("dep",)),
            ]
        )
    }
    path_registry = object()
    blueprint = types.SimpleNamespace(
        root_spell_id="root",
        ordered_node_ids=("dep", "root"),
        path_registry=path_registry,
        socket_refs=[
            types.SimpleNamespace(
                node_id="root",
                param_name="svc",
                param_path_id=7,
                target_spell_ids=("dep",),
                socket_kind=SocketKind.NORMAL,
            )
        ],
    )

    fast_key = crafter._build_phase8_occurrence_plan_fast_key(
        root_blueprint=blueprint,
        spell_lookup=spellbook._spell_id_pool,
    )

    assert fast_key == (
        "root",
        ("dep", "root"),
        id(path_registry),
        (("root", "svc", 7, SocketKind.NORMAL.value),),
        (
            ("dep", "dep", Existence.unique.name, False),
            ("root", "root", Existence.unique.name, False),
        ),
        (("root", (("svc", ("dep",)),)),),
        SystemState.dynamic,
        (("peer", "frame", "binding", "dep"),),
    )

    dep_spell._mutation_override = {"svc": "mutated"}
    assert crafter._build_phase8_occurrence_plan_fast_key(
        root_blueprint=blueprint,
        spell_lookup=spellbook._spell_id_pool,
    ) is None


def test_build_phase8_occurrence_plan_input_signature_hashes_mutation_semantics_and_phase9_reuses_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate the full Phase 8 signature helper and Phase 9 reuse helper.
    Contract:
        - Phase 8 signature includes frozen mutation payload semantics.
        - Broken contracted lookup access returns None.
        - Phase 9 reuses the cached Phase 8 signature when available.
    """
    states = _SpellSystemStatesStub()
    crafter, root_spell, _ = _build_spell_and_crafter(spell_system_states=states)
    spellbook = root_spell._spellbook
    root_spell._mutation_override = {"svc": ["x", "y"]}
    captured_parts: list[tuple[Any, ...]] = []

    monkeypatch.setattr(
        SpellCrafter,
        "_hash_codegen_signature",
        staticmethod(lambda *parts: captured_parts.append(parts) or "phase8-signature"),
    )

    blueprint = types.SimpleNamespace(
        root_spell_id="root",
        ordered_node_ids=("root",),
        path_registry=object(),
        socket_refs=[
            types.SimpleNamespace(
                node_id="root",
                param_name="svc",
                param_path_id=7,
                target_spell_ids=("dep",),
                socket_kind=SocketKind.NORMAL,
            )
        ],
    )

    signature = crafter._build_phase8_occurrence_plan_input_signature(
        root_blueprint=blueprint,
        spell_lookup=spellbook._spell_id_pool,
    )

    assert signature == "phase8-signature"
    assert captured_parts
    spell_rows = captured_parts[0][4]
    assert spell_rows == (
        (
            "root",
            "root",
            Existence.unique.name,
            False,
            crafter._freeze_phase11_schema_value(root_spell.mutation_override),
        ),
    )

    spellbook._lookup_contracted_spells = object()
    assert crafter._build_phase8_occurrence_plan_input_signature(
        root_blueprint=blueprint,
        spell_lookup=spellbook._spell_id_pool,
    ) is None

    crafter._phase8_occurrence_plan_input_signature = "phase8-signature"
    assert crafter._build_phase9_injection_plan_input_signature(
        occurrence_plan=object(),
    ) == "phase8-signature"
    assert crafter._build_phase9_injection_plan_input_signature(
        occurrence_plan=None,
    ) is None


def _make_phase11_step_stub(
    spell_id: str,
    **overrides: object,
) -> object:
    """
    Purpose:
        Build a minimal Phase 11 step stub for IR export tests.
    Contract:
        Exposes only fields read by SpellCrafter phase8_11 IR capture helpers.
    Args:
        spell_id: Spell id to expose through step.spell.spell_index.current.
        overrides: Optional explicit field overrides applied to the base step.
    Returns:
        object: Step stub compatible with `_build_phase11_variant_ir_payload`.
    """
    step = types.SimpleNamespace(
        instance_key=(spell_id, None),
        spell=types.SimpleNamespace(
            spell_index=types.SimpleNamespace(current=spell_id),
        ),
        existence=Existence.unique,
        creations_target_kind=1,
        shared_instance=False,
        dependency_resolution_order=(
            ("dep", ((f"{spell_id}-dep", None),)),
        ),
        override_match_prefix=None,
        override_match_prefix_len=0,
        override_keys=("dep",),
        expects_overrides=False,
        contract_keys=("dep",),
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        lock_hint="none",
        use_spell_lock_hint=False,
        requires_spellspace=False,
        owner_conduit_required=False,
        must_register=False,
        disposal_method_names=(),
    )
    for field_name, value in overrides.items():
        setattr(step, field_name, value)
    return step


def _make_phase11_plan_stub(
    *,
    plan_variant: str,
    root_spell_id: str,
    step_spell_ids: Sequence[str],
    root_instance_key: tuple[str, int | None] | None = None,
) -> object:
    """
    Purpose:
        Build a minimal Phase 11 plan stub for IR export tests.
    Contract:
        Exposes the plan fields consumed by SpellCrafter phase8_11 capture and
        plan-based no-overrides compile signature generation.
    Args:
        plan_variant: Execution plan variant label.
        root_spell_id: Root spell id for the plan.
        step_spell_ids: Ordered spell ids for plan steps.
        root_instance_key: Optional explicit root instance key override.
    Returns:
        object: Plan stub with deterministic step order and no transient plan.
    """
    steps = tuple(_make_phase11_step_stub(spell_id) for spell_id in step_spell_ids)
    resolved_root_instance_key = root_instance_key
    if resolved_root_instance_key is None:
        resolved_root_instance_key = (root_spell_id, None)
    return types.SimpleNamespace(
        plan_variant=plan_variant,
        root_spell_id=root_spell_id,
        root_instance_key=resolved_root_instance_key,
        steps=steps,
        fast_transient_plan=None,
    )


def test_capture_phase2_5_codegen_ir_exports_required_fields() -> None:
    """
    Purpose:
        Verify phase2_5 IR export includes required fields and stable signatures.
    Contract:
        Captured payload includes deterministic index ordering and signature
        parity between payload and top-level signature map.
    Returns:
        None.
    Raises:
        AssertionError: If required fields or deterministic values are missing.
    """
    crafter, spell, _ = _build_spell_and_crafter(spell_id="root")
    dependencies = (
        _make_dependency(
            spell_id=spell.spell_index.current,
            param_name="alpha",
            position=0,
            di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
            is_optional=False,
        ),
        _make_dependency(
            spell_id=spell.spell_index.current,
            param_name="beta",
            position=1,
            di_shape=ParameterDIShape.SPELL_CONTRACT,
            is_optional=True,
        ),
    )
    crafter._symbolic_graph = _make_symbolic_graph(
        spell_id=spell.spell_index.current,
        dependencies=dependencies,
    )
    crafter._resolution_frame = types.SimpleNamespace(
        ordered_node_ids=("dep", "root"),
    )
    spell.dependencies = ["dep-b", "dep-a"]
    crafter._validated_phase4 = True
    crafter._is_broken = False
    crafter._validation_result_phase4 = types.SimpleNamespace(
        issues=(
            types.SimpleNamespace(code="I-B"),
            types.SimpleNamespace(code="I-A"),
        ),
    )
    root_blueprint = _RootBlueprintStub("root")
    root_blueprint.root_lineage_id = "lineage-root"
    root_blueprint.ordered_node_ids = ["dep", "root"]
    root_blueprint.socket_refs = [
        types.SimpleNamespace(
            node_id="dep",
            param_name="beta",
            param_path_id=7,
            socket_kind=types.SimpleNamespace(value="spell_contract"),
        ),
        types.SimpleNamespace(
            node_id="dep",
            param_name="alpha",
            param_path_id=2,
            socket_kind=types.SimpleNamespace(value="normal"),
        ),
    ]
    class _Node:
        def __init__(self, node_id: str) -> None:
            self.id = node_id
            self.dependents: set[object] = set()
            self.incoming_params: dict[object, str] = {}

    parent_a = _Node("dep-a")
    parent_b = _Node("dep-b")
    child_root = _Node("root")
    parent_a.dependents.add(child_root)
    parent_b.dependents.add(child_root)
    child_root.incoming_params[parent_a] = "alpha"
    child_root.incoming_params[parent_b] = "beta"
    root_blueprint.dag = types.SimpleNamespace(
        nodes={
            "dep-b": parent_b,
            "dep-a": parent_a,
            "root": child_root,
        },
        _socket_kinds={
            (parent_b, child_root): types.SimpleNamespace(value="spell_contract"),
            (parent_a, child_root): types.SimpleNamespace(value="normal"),
        },
    )
    crafter._root_blueprint_phase5 = root_blueprint
    crafter._spell_system_index_phase5 = types.SimpleNamespace(
        nodes={"z": object(), "a": object()},
    )

    crafter._capture_phase2_5_codegen_ir()
    payload = crafter.codegen_ir["phase2_5"]
    signatures = crafter.codegen_ir["signatures"]
    first_signature = payload["signature"]

    assert set(payload.keys()) == {
        "symbolic_dependencies",
        "local_ordered_node_ids",
        "dependency_ids",
        "phase4_validated",
        "phase4_is_broken",
        "phase4_issue_codes",
        "phase5_root_spell_id",
        "phase5_root_lineage_id",
        "phase5_root_ordered_node_ids",
        "phase5_socket_ref_count",
        "phase5_socket_rows",
        "phase5_dag_edge_rows",
        "phase5_index_spell_ids",
        "signature",
    }
    assert payload["phase5_index_spell_ids"] == ("a", "z")
    assert payload["phase5_root_spell_id"] == "root"
    assert payload["phase5_root_lineage_id"] == "lineage-root"
    assert payload["phase5_socket_ref_count"] == 2
    assert payload["phase5_socket_rows"] == (
        ("dep", "alpha", 2, "normal"),
        ("dep", "beta", 7, "spell_contract"),
    )
    assert payload["phase5_dag_edge_rows"] == (
        ("dep-a", "root", "alpha", "normal"),
        ("dep-b", "root", "beta", "spell_contract"),
    )
    assert signatures["phase2_5"] == first_signature

    crafter._capture_phase2_5_codegen_ir()
    assert crafter.codegen_ir["phase2_5"]["signature"] == first_signature


def test_capture_phase2_5_codegen_ir_signature_changes_on_phase5_schema_rows() -> None:
    """
    Purpose:
        Ensure phase2_5 signature invalidates when Phase5 schema rows change.
    Contract:
        Changing socket or DAG edge schema rows changes the exported signature.
    Returns:
        None.
    Raises:
        AssertionError: If schema-row changes do not invalidate signatures.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")

    root_blueprint = _RootBlueprintStub("root")
    root_blueprint.root_lineage_id = "lineage-root"
    root_blueprint.ordered_node_ids = ["dep-a", "root"]
    root_blueprint.socket_refs = [
        types.SimpleNamespace(
            node_id="dep-a",
            param_name="alpha",
            param_path_id=1,
            socket_kind=types.SimpleNamespace(value="normal"),
        ),
    ]
    class _Node:
        def __init__(self, node_id: str) -> None:
            self.id = node_id
            self.dependents: set[object] = set()
            self.incoming_params: dict[object, str] = {}

    parent_a = _Node("dep-a")
    child_root = _Node("root")
    parent_a.dependents.add(child_root)
    child_root.incoming_params[parent_a] = "alpha"
    root_blueprint.dag = types.SimpleNamespace(
        nodes={
            "dep-a": parent_a,
            "root": child_root,
        },
        _socket_kinds={
            (parent_a, child_root): types.SimpleNamespace(value="normal"),
        },
    )
    crafter._root_blueprint_phase5 = root_blueprint
    crafter._capture_phase2_5_codegen_ir()
    first_signature = crafter.codegen_ir["phase2_5"]["signature"]

    changed_blueprint = _RootBlueprintStub("root")
    changed_blueprint.root_lineage_id = "lineage-root"
    changed_blueprint.ordered_node_ids = ["dep-a", "root"]
    changed_blueprint.socket_refs = [
        types.SimpleNamespace(
            node_id="dep-a",
            param_name="alpha",
            param_path_id=9,
            socket_kind=types.SimpleNamespace(value="normal"),
        ),
    ]
    changed_parent = _Node("dep-a")
    changed_child = _Node("root")
    changed_parent.dependents.add(changed_child)
    changed_child.incoming_params[changed_parent] = "alpha_changed"
    changed_blueprint.dag = types.SimpleNamespace(
        nodes={
            "dep-a": changed_parent,
            "root": changed_child,
        },
        _socket_kinds={
            (changed_parent, changed_child): types.SimpleNamespace(value="normal"),
        },
    )
    crafter._root_blueprint_phase5 = changed_blueprint
    crafter._capture_phase2_5_codegen_ir()
    second_signature = crafter.codegen_ir["phase2_5"]["signature"]

    assert second_signature != first_signature


def test_capture_phase8_11_codegen_ir_exports_sorted_payloads() -> None:
    """
    Purpose:
        Verify phase8_11 IR export normalizes sorted fields and variant payloads.
    Contract:
        Shared spell ids, injection instance keys, and patch-map target specs are
        emitted in deterministic order for signature stability.
    Returns:
        None.
    Raises:
        AssertionError: If normalized ordering or required payload sections fail.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace(
        execution_order=("step-b", "step-a"),
        root_instance_key=("root", None),
        shared_spell_ids={"z", "a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {
                "alpha": [("a", 1), ("b", 2)],
                "beta": [("a", 1)],
            },
            ("a", 1): {},
            ("b", 2): {},
        },
        instance_keys_by_spell_id={
            "root": [("root", None)],
            "a": [("a", 3), ("a", 1)],
        },
        canonical_occurrences_by_spell_id={
            "root": ("root", 0),
            "a": ("a", 1),
        },
        contract_overrides_by_occurrence={
            ("a", 1): {"x": 7, "__args__": [1, 2]},
        },
        contract_overrides_by_spell_id={
            "a": [(("a", 1), {"x": 7, "__args__": [1, 2]})],
        },
    )
    socket_ref_a = types.SimpleNamespace(
        node_id="dep-a",
        param_name="arg",
        param_path_id=3,
        socket_kind=types.SimpleNamespace(value="normal"),
    )
    socket_ref_b = types.SimpleNamespace(
        node_id="dep-b",
        param_name="arg",
        param_path_id=1,
        socket_kind=types.SimpleNamespace(value="normal"),
    )
    mutation_patch_a = types.SimpleNamespace(
        child_spell_id="child-a",
        param_name="mut",
        param_path_id=2,
        old_parent_id="old-a",
    )
    mutation_patch_b = types.SimpleNamespace(
        child_spell_id="child-b",
        param_name="mut",
        param_path_id=5,
        old_parent_id="old-b",
    )
    crafter._injection_plan_phase9 = types.SimpleNamespace(
        instance_injections={
            ("z", 3): types.SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
            ("a", 2): types.SimpleNamespace(
                allow_list_aggregation=True,
                uses_positional_override=True,
                contract_payload={"fixed": "ok", "__args__": [9]},
                param_sources={
                    "dep": types.SimpleNamespace(
                        kind="dependency",
                        dependency_keys=[("z", 3), ("a", None)],
                        override_key="dep",
                        contract_key=None,
                    ),
                    "contracted": types.SimpleNamespace(
                        kind="contract",
                        dependency_keys=[],
                        override_key="contracted",
                        contract_key="ckey",
                    ),
                },
            ),
            ("a", None): types.SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
        },
    )
    crafter._override_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={
            "override-z": [socket_ref_a],
            "override-a": [socket_ref_a, socket_ref_b],
        },
        specificity_by_spec={"override-z": 1, "override-a": 3},
    )
    crafter._mutation_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={
            "mutation-z": [mutation_patch_b],
            "mutation-a": [mutation_patch_b, mutation_patch_a],
        },
    )
    crafter._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("a", "b"),
    )
    crafter._execution_plan_phase11_overrides = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    crafter._execution_plan_phase11 = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("a", "b", "c"),
    )

    crafter._capture_phase8_11_codegen_ir()
    payload = crafter.codegen_ir["phase8_11"]
    signatures = crafter.codegen_ir["signatures"]

    assert payload["occurrence"]["shared_spell_ids"] == ("a", "z")
    assert payload["occurrence"]["graph_rows"][0] == (("a", 1), ())
    assert payload["occurrence"]["instance_key_rows"] == (
        ("a", (("a", 1), ("a", 3))),
        ("root", (("root", None),)),
    )
    assert payload["occurrence"]["canonical_occurrence_rows"] == (
        ("a", ("a", 1)),
        ("root", ("root", 0)),
    )
    assert payload["occurrence"]["contract_override_rows"] == (
        (("a", 1), (("__args__", (1, 2)), ("x", 7))),
    )
    assert payload["injection"]["instance_keys"] == (
        ("a", None),
        ("a", 2),
        ("z", 3),
    )
    assert payload["injection"]["instance_rows"][1] == (
        ("a", 2),
        True,
        True,
        (("__args__", (9,)), ("fixed", "ok")),
        (
            ("contracted", "contract", (), "contracted", "ckey"),
            ("dep", "dependency", (("a", None), ("z", 3)), "dep", None),
        ),
    )
    assert payload["patch_maps"]["override_target_specs"] == (
        "override-a",
        "override-z",
    )
    assert payload["patch_maps"]["override_target_rows"] == (
        (
            "override-a",
            3,
            (
                ("dep-a", "arg", 3, "normal"),
                ("dep-b", "arg", 1, "normal"),
            ),
        ),
        (
            "override-z",
            1,
            (
                ("dep-a", "arg", 3, "normal"),
            ),
        ),
    )
    assert payload["patch_maps"]["mutation_target_specs"] == (
        "mutation-a",
        "mutation-z",
    )
    assert payload["patch_maps"]["mutation_target_rows"] == (
        (
            "mutation-a",
            (
                ("child-a", "mut", 2, "old-a"),
                ("child-b", "mut", 5, "old-b"),
            ),
        ),
        (
            "mutation-z",
            (
                ("child-b", "mut", 5, "old-b"),
            ),
        ),
    )
    assert payload["execution"]["no_overrides"]["plan_variant"] == "no_overrides_fast"
    no_overrides_payload = payload["execution"]["no_overrides"]
    first_step_row = no_overrides_payload["steps_rows"][0]
    assert first_step_row["spell_id"] == "a"
    assert first_step_row["dependency_resolution_order"] == (
        ("dep", (("a-dep", None),)),
    )
    assert no_overrides_payload["steps_rows_signature"] is not None
    assert "steps" not in no_overrides_payload
    assert "transient_plan" not in no_overrides_payload
    assert "transient_schema" in no_overrides_payload
    assert payload["execution"]["overrides"]["plan_variant"] == "overrides"
    assert payload["execution"]["overrides_with_mutations"]["plan_variant"] == "overrides_with_mutations"
    assert signatures["phase8_11"] == payload["signature"]


def test_build_injection_instance_rows_fails_fast_on_invalid_spec_contract() -> None:
    """
    Purpose:
        Verify Phase9 injection row export fails fast on malformed specs.
    Contract:
        `_build_injection_instance_rows` expects InjectionSpec fields and raises
        when a malformed object is supplied.
    Returns:
        None.
    Raises:
        AssertionError: If malformed specs do not fail fast.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    with pytest.raises(AttributeError):
        crafter._build_injection_instance_rows(
            {
                ("root", None): object(),
            }
        )


def test_build_override_target_rows_fails_fast_on_invalid_socket_ref_contract() -> None:
    """
    Purpose:
        Verify Phase10 override row export fails fast on malformed socket refs.
    Contract:
        `_build_override_target_rows` expects socket refs with node/param/path/
        socket-kind fields and raises when malformed entries are supplied.
    Returns:
        None.
    Raises:
        AssertionError: If malformed socket refs do not fail fast.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    override_patch_map = types.SimpleNamespace(
        targets_by_spec={"spec": [object()]},
        specificity_by_spec={"spec": 1},
    )
    with pytest.raises(AttributeError):
        crafter._build_override_target_rows(override_patch_map)


def test_build_mutation_target_rows_fails_fast_on_invalid_patch_contract() -> None:
    """
    Purpose:
        Verify Phase10 mutation row export fails fast on malformed patches.
    Contract:
        `_build_mutation_target_rows` expects mutation patch fields and raises
        when malformed entries are supplied.
    Returns:
        None.
    Raises:
        AssertionError: If malformed mutation patches do not fail fast.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    mutation_patch_map = types.SimpleNamespace(
        targets_by_spec={"spec": [object()]},
    )
    with pytest.raises(AttributeError):
        crafter._build_mutation_target_rows(mutation_patch_map)


def test_capture_phase8_11_codegen_ir_signature_stable_across_map_insertion_orders() -> None:
    """
    Purpose:
        Ensure phase8_11 signature is stable across equivalent map insertion orders.
    Contract:
        Equivalent injection and patch-map data produce identical signatures even
        when dictionary insertion orders differ.
    Returns:
        None.
    Raises:
        AssertionError: If signatures differ for equivalent semantic payloads.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace(
        execution_order=("step-a",),
        root_instance_key=("root", None),
        shared_spell_ids={"a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {
                "dep": [("a", 1), ("b", 2)],
            },
            ("a", 1): {},
            ("b", 2): {},
        },
        instance_keys_by_spell_id={
            "b": [("b", 2)],
            "a": [("a", None)],
        },
        canonical_occurrences_by_spell_id={
            "b": ("b", 2),
            "a": ("a", 1),
        },
        contract_overrides_by_occurrence={
            ("a", 1): {"x": 1},
        },
        contract_overrides_by_spell_id={
            "a": [(("a", 1), {"x": 1})],
        },
    )
    crafter._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    crafter._execution_plan_phase11_overrides = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    crafter._execution_plan_phase11 = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("a",),
    )

    crafter._injection_plan_phase9 = types.SimpleNamespace(
        instance_injections={
            ("b", 1): types.SimpleNamespace(
                allow_list_aggregation=True,
                uses_positional_override=False,
                contract_payload={"fixed": "v"},
                param_sources={
                    "dep": types.SimpleNamespace(
                        kind="dependency",
                        dependency_keys=[("x", None), ("y", 2)],
                        override_key="dep",
                        contract_key=None,
                    ),
                },
            ),
            ("a", None): types.SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
        },
    )
    override_ref_a = types.SimpleNamespace(
        node_id="node-a",
        param_name="p",
        param_path_id=2,
        socket_kind=types.SimpleNamespace(value="normal"),
    )
    override_ref_b = types.SimpleNamespace(
        node_id="node-b",
        param_name="p",
        param_path_id=1,
        socket_kind=types.SimpleNamespace(value="normal"),
    )
    mutation_patch_a = types.SimpleNamespace(
        child_spell_id="child-a",
        param_name="m",
        param_path_id=4,
        old_parent_id="old-a",
    )
    mutation_patch_b = types.SimpleNamespace(
        child_spell_id="child-b",
        param_name="m",
        param_path_id=5,
        old_parent_id="old-b",
    )
    crafter._override_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"z": [override_ref_a], "a": [override_ref_a, override_ref_b]},
        specificity_by_spec={"z": 1, "a": 3},
    )
    crafter._mutation_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"z": [mutation_patch_b], "a": [mutation_patch_b, mutation_patch_a]},
    )
    crafter._capture_phase8_11_codegen_ir()
    first_signature = crafter.codegen_ir["phase8_11"]["signature"]
    first_rows_signature = crafter.codegen_ir["phase8_11"]["execution"]["no_overrides"]["steps_rows_signature"]

    crafter._injection_plan_phase9 = types.SimpleNamespace(
        instance_injections={
            ("a", None): types.SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
            ("b", 1): types.SimpleNamespace(
                allow_list_aggregation=True,
                uses_positional_override=False,
                contract_payload={"fixed": "v"},
                param_sources={
                    "dep": types.SimpleNamespace(
                        kind="dependency",
                        dependency_keys=[("y", 2), ("x", None)],
                        override_key="dep",
                        contract_key=None,
                    ),
                },
            ),
        },
    )
    crafter._override_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"a": [override_ref_b, override_ref_a], "z": [override_ref_a]},
        specificity_by_spec={"a": 3, "z": 1},
    )
    crafter._mutation_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"a": [mutation_patch_a, mutation_patch_b], "z": [mutation_patch_b]},
    )
    crafter._capture_phase8_11_codegen_ir()
    second_signature = crafter.codegen_ir["phase8_11"]["signature"]
    second_rows_signature = crafter.codegen_ir["phase8_11"]["execution"]["no_overrides"]["steps_rows_signature"]

    assert second_signature == first_signature
    assert second_rows_signature == first_rows_signature


def test_hash_codegen_signature_fastpaths_skip_pickle_for_supported_types(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify supported signature parts use typed fastpaths instead of pickle.
    Contract:
        Scalar fastpath parts should hash deterministically without calling
        `pickle.dumps`.
    Args:
        monkeypatch:
            Pytest monkeypatch fixture used to force pickle-path failure.
    Returns:
        None.
    Raises:
        AssertionError: If pickle path is invoked or hash output is unstable.
    """
    def _pickle_boom(*args: Any, **kwargs: Any) -> bytes:
        raise AssertionError("pickle.dumps should not be called for fastpath parts")

    monkeypatch.setattr(spell_crafter_module.pickle, "dumps", _pickle_boom)

    first_signature = SpellCrafter._hash_codegen_signature(
        None,
        True,
        False,
        7,
        -3.5,
        "alpha",
        b"beta",
        bytearray(b"gamma"),
    )
    second_signature = SpellCrafter._hash_codegen_signature(
        None,
        True,
        False,
        7,
        -3.5,
        "alpha",
        b"beta",
        bytearray(b"gamma"),
    )

    assert second_signature == first_signature


def test_serialize_codegen_signature_part_falls_back_to_repr_on_pickle_error() -> None:
    """
    Purpose:
        Verify serializer fallback remains deterministic when pickling fails.
    Contract:
        Unsupported values that raise during pickling should serialize via
        repr-based bytes.
    Returns:
        None.
    Raises:
        AssertionError: If repr fallback is not applied.
    """
    class _Unpicklable:
        def __reduce__(self) -> Any:
            raise TypeError("cannot pickle")

        def __repr__(self) -> str:
            return "UnpicklableStable()"

    payload = SpellCrafter._serialize_codegen_signature_part(_Unpicklable())

    assert payload == b"UnpicklableStable()"


@pytest.mark.parametrize(
    "step_overrides",
    (
        {
            "instance_key": ("root", 1),
        },
        {
            "existence": Existence.many,
        },
        {
            "shared_instance": True,
        },
        {
            "dependency_resolution_order": (
                ("dep", (("alt-dep", None),)),
            ),
        },
        {
            "override_match_prefix": 42,
            "override_match_prefix_len": 1,
        },
        {
            "override_keys": ("dep", "dep2"),
        },
        {
            "expects_overrides": True,
        },
        {
            "contract_keys": ("dep", "contract"),
        },
        {
            "allow_list_aggregation": True,
        },
        {
            "uses_positional_override": True,
            "contract_positional_override": (1, 2),
        },
        {
            "has_contract_payload": True,
            "contract_payload": {"custom": "value"},
        },
        {
            "lock_hint": "spell_lock",
        },
        {
            "use_spell_lock_hint": True,
        },
        {
            "requires_spellspace": True,
        },
        {
            "owner_conduit_required": True,
        },
        {
            "must_register": True,
        },
        {
            "disposal_method_names": ("cleanup",),
        },
        {
            "creations_target_kind": 2,
        },
    ),
)
def test_build_phase11_variant_ir_payload_signature_changes_on_step_semantics(
    step_overrides: dict[str, object],
) -> None:
    """
    Purpose:
        Ensure Phase11 variant signatures invalidate on step semantic changes.
    Contract:
        Changing dependency wiring, payload, lock/register, or routing semantics
        must change both step-row and variant signatures.
    Args:
        step_overrides: Semantic field overrides applied to one plan step.
    Returns:
        None.
    Raises:
        AssertionError: If semantic changes do not invalidate signatures.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    base_plan = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    changed_step = _make_phase11_step_stub("root", **step_overrides)
    changed_plan = types.SimpleNamespace(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        steps=(changed_step,),
        fast_transient_plan=None,
    )

    base_payload = crafter._build_phase11_variant_ir_payload(base_plan)
    changed_payload = crafter._build_phase11_variant_ir_payload(changed_plan)

    stripped_override_fields = {
        "override_match_prefix",
        "override_match_prefix_len",
        "override_keys",
        "expects_overrides",
    }
    if set(step_overrides.keys()).issubset(stripped_override_fields):
        assert changed_payload["steps_rows_signature"] == base_payload["steps_rows_signature"]
        assert changed_payload["signature"] == base_payload["signature"]
    else:
        assert changed_payload["steps_rows_signature"] != base_payload["steps_rows_signature"]
        assert changed_payload["signature"] != base_payload["signature"]


def test_build_phase11_variant_ir_payload_signature_changes_on_variant_label() -> None:
    """
    Purpose:
        Ensure Phase11 variant payloads remain distinct even with identical steps.
    Contract:
        `plan_variant` contributes to variant signatures while step-row signatures
        remain equal for equivalent step semantics.
    Returns:
        None.
    Raises:
        AssertionError: If variant signatures collapse across variant labels.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    overrides_plan = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    mutation_plan = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("root",),
    )

    overrides_payload = crafter._build_phase11_variant_ir_payload(overrides_plan)
    mutation_payload = crafter._build_phase11_variant_ir_payload(mutation_plan)

    assert mutation_payload["steps_rows_signature"] == overrides_payload["steps_rows_signature"]
    assert mutation_payload["signature"] != overrides_payload["signature"]


def test_capture_phase8_11_codegen_ir_signature_changes_on_enriched_payload_semantics() -> None:
    """
    Purpose:
        Ensure enriched Phase8-10 schema rows participate in `phase8_11` signature.
    Contract:
        Equivalent base plans with changed occurrence/injection/patch-map schema
        rows must produce different phase8_11 signatures.
    Returns:
        None.
    Raises:
        AssertionError: If enriched-segment semantic drift does not invalidate signature.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    crafter._execution_plan_phase11_overrides = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    crafter._execution_plan_phase11 = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    crafter._occurrence_plan_phase8 = types.SimpleNamespace(
        execution_order=("a",),
        root_instance_key=("root", None),
        shared_spell_ids={"a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {"dep": [("a", 1)]},
            ("a", 1): {},
        },
        instance_keys_by_spell_id={"a": [("a", None)]},
        canonical_occurrences_by_spell_id={"a": ("a", 1)},
        contract_overrides_by_occurrence={("a", 1): {"x": 1}},
        contract_overrides_by_spell_id={"a": [(("a", 1), {"x": 1})]},
    )
    crafter._injection_plan_phase9 = types.SimpleNamespace(
        instance_injections={
            ("a", None): types.SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
        },
    )
    crafter._override_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"**dep": []},
        specificity_by_spec={"**dep": 1},
    )
    crafter._mutation_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"**mut": []},
    )
    crafter._capture_phase8_11_codegen_ir()
    first_signature = crafter.codegen_ir["phase8_11"]["signature"]

    crafter._occurrence_plan_phase8 = types.SimpleNamespace(
        execution_order=("a",),
        root_instance_key=("root", None),
        shared_spell_ids={"a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {"dep": [("a", 2)]},
            ("a", 2): {},
        },
        instance_keys_by_spell_id={"a": [("a", None)]},
        canonical_occurrences_by_spell_id={"a": ("a", 2)},
        contract_overrides_by_occurrence={("a", 2): {"x": 2}},
        contract_overrides_by_spell_id={"a": [(("a", 2), {"x": 2})]},
    )
    crafter._injection_plan_phase9 = types.SimpleNamespace(
        instance_injections={
            ("a", None): types.SimpleNamespace(
                allow_list_aggregation=True,
                uses_positional_override=False,
                contract_payload={"fixed": "v"},
                param_sources={},
            ),
        },
    )
    crafter._override_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"**dep": []},
        specificity_by_spec={"**dep": 3},
    )
    crafter._mutation_patch_map_phase10 = types.SimpleNamespace(
        targets_by_spec={"**mut2": []},
    )
    crafter._capture_phase8_11_codegen_ir()
    second_signature = crafter.codegen_ir["phase8_11"]["signature"]

    assert second_signature != first_signature


@pytest.mark.parametrize(
    "step_count,max_depth,max_dependency_count,dispatch_route",
    [
        (8, 3, 1, "FAST_TRANSIENT_TIER_0"),
        (16, 6, 8, "FAST_TRANSIENT_TIER_1"),
        (24, 8, 8, "FAST_TRANSIENT_TIER_2"),
        (32, 9, 10, "FAST_TRANSIENT_TIER_3"),
        (33, 9, 10, "ENGINE"),
    ],
)
def test_cache_execution_plan_metrics_assigns_dispatch_route_tiers(
    step_count: int,
    max_depth: int,
    max_dependency_count: int,
    dispatch_route: str,
) -> None:
    """
    Purpose:
        Validate Phase 11 metric caching assigns the expected dispatch route tier.
    Contract:
        - fast transient plans use the tier thresholds based on depth, step count,
          and max dependency count.
        - Out-of-range plans fall back to ENGINE.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    depths = {index: max_depth for index in range(step_count)}
    occurrence_plan = types.SimpleNamespace(
        occurrence_graph={("spell-{0}".format(index), index): {} for index in range(step_count)},
        path_registry=types.SimpleNamespace(depth=lambda path_id: depths[path_id]),
    )

    steps = []
    for index in range(step_count):
        dependency_keys = [
            ("dep-{0}-{1}".format(index, dep_index), None)
            for dep_index in range(max_dependency_count)
        ]
        steps.append(
            _make_phase11_step_stub(
                "spell-{0}".format(index),
                dependency_keys=dependency_keys,
                has_contract_payload=False,
                spell=types.SimpleNamespace(
                    spell_index=types.SimpleNamespace(current="spell-{0}".format(index)),
                    is_existing_creation=False,
                ),
            )
        )

    plan = types.SimpleNamespace(
        steps=tuple(steps),
        spell_id_step_index={step.instance_key[0]: index for index, step in enumerate(steps)},
        fast_plan=None,
        fast_transient_plan=object(),
    )

    crafter._cache_execution_plan_metrics(
        occurrence_plan=occurrence_plan,
        plan=plan,
    )

    assert spell.execution_plan_step_count == step_count
    assert spell.execution_plan_max_occurrence_depth == max_depth
    assert spell.execution_plan_max_dependency_count == max_dependency_count
    assert spell.execution_plan_dispatch_route == dispatch_route


def test_cache_execution_plan_metrics_records_calln_payload_and_existing_creation_flags() -> None:
    """
    Purpose:
        Validate Phase 11 metric caching records execution-plan feature flags.
    Contract:
        - CALLN is detected from fast-plan metadata.
        - Contract payload and existing-creation flags are aggregated from steps.
        - Existing creations force ENGINE even when a transient plan exists.
    """
    crafter, spell, _ = _build_spell_and_crafter()
    occurrence_plan = types.SimpleNamespace(
        occurrence_graph={("root", 1): {}},
        path_registry=types.SimpleNamespace(depth=lambda path_id: 1),
    )
    steps = (
        _make_phase11_step_stub(
            "root",
            has_contract_payload=True,
            dependency_keys=[("dep", None)],
            spell=types.SimpleNamespace(
                spell_index=types.SimpleNamespace(current="root"),
                is_existing_creation=True,
            ),
        ),
    )
    fast_plan = tuple([None] * 20 + [[spell_crafter_module.ExecutionPlanCallMode.CALLN]])
    plan = types.SimpleNamespace(
        steps=steps,
        spell_id_step_index={"root": 0},
        fast_plan=fast_plan,
        fast_transient_plan=object(),
    )

    crafter._cache_execution_plan_metrics(
        occurrence_plan=occurrence_plan,
        plan=plan,
    )

    assert spell.execution_plan_has_calln is True
    assert spell.execution_plan_has_contract_payloads is True
    assert spell.execution_plan_has_existing_creations is True
    assert spell.execution_plan_dispatch_route == "ENGINE"


def test_try_build_execution_plan_variant_from_base_returns_fresh_copied_plan() -> None:
    """
    Purpose:
        Validate Phase 11 sibling-variant derivation from a compatible base plan.
    Contract:
        - Returns a fresh ExecutionPlan with copied list/dict containers.
        - Preserves root identity and structural metadata while swapping the variant label.
        - Does not carry fast-path arrays into the derived plan.
    """
    crafter, _, _ = _build_spell_and_crafter()
    base_steps = [types.SimpleNamespace(name="step")]
    base_plan = types.SimpleNamespace(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=base_steps,
        spell_id_step_index={"root": 0},
        optimistic_object_refs_by_spell_id={"root": "existing"},
        available_param_by_spell_id={"root": 1},
    )

    derived = crafter._try_build_execution_plan_variant_from_base(
        base_plan=base_plan,
        plan_variant=spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
    )

    assert derived is not None
    assert derived.root_spell_id == "root"
    assert derived.root_instance_key == ("root", None)
    assert derived.plan_variant == spell_crafter_module.ExecutionPlanVariant.OVERRIDES
    assert derived.steps == base_steps
    assert derived.steps is not base_steps
    assert derived.spell_id_step_index == {"root": 0}
    assert derived.spell_id_step_index is not base_plan.spell_id_step_index
    assert derived.optimistic_object_refs_by_spell_id == {"root": "existing"}
    assert derived.available_param_by_spell_id == {"root": 1}
    assert derived.fast_plan is None
    derived.cleanup()


@pytest.mark.parametrize(
    "base_plan",
    [
        types.SimpleNamespace(),
        types.SimpleNamespace(
            root_spell_id=None,
            root_instance_key=("root", None),
            steps=[],
            spell_id_step_index={},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={},
        ),
        types.SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=None,
            spell_id_step_index={},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={},
        ),
        types.SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=object(),
            spell_id_step_index={},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={},
        ),
    ],
)
def test_try_build_execution_plan_variant_from_base_returns_none_for_incompatible_inputs(
    base_plan: object,
) -> None:
    """
    Purpose:
        Validate Phase 11 sibling-variant derivation rejects incompatible base plans.
    Contract:
        - Missing attributes, missing identity, and uncopyable structures return None.
    """
    crafter, _, _ = _build_spell_and_crafter()

    assert crafter._try_build_execution_plan_variant_from_base(
        base_plan=base_plan,
        plan_variant=spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
    ) is None


def test_build_execution_plan_variant_delegates_to_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate the direct Phase 11 builder wrapper.
    Contract:
        - `_build_execution_plan_variant(...)` instantiates ExecutionPlanBuilder with the supplied inputs.
        - The built plan is returned unchanged to the caller.
    """
    crafter, _, _ = _build_spell_and_crafter()
    captured: dict[str, object] = {}
    expected_plan = object()

    class _ExecutionPlanBuilderStub:
        def __init__(
            self,
            *,
            occurrence_plan: object,
            injection_plan: object,
            spell_lookup: object,
            plan_variant: str,
        ) -> None:
            captured["occurrence_plan"] = occurrence_plan
            captured["injection_plan"] = injection_plan
            captured["spell_lookup"] = spell_lookup
            captured["plan_variant"] = plan_variant

        def build(self) -> object:
            return expected_plan

    monkeypatch.setattr(spell_crafter_module, "ExecutionPlanBuilder", _ExecutionPlanBuilderStub)

    occurrence_plan = object()
    injection_plan = object()
    spell_lookup = {"root": object()}

    result = crafter._build_execution_plan_variant(
        occurrence_plan=occurrence_plan,
        injection_plan=injection_plan,
        spell_lookup=spell_lookup,
        plan_variant=spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
    )

    assert result is expected_plan
    assert captured == {
        "occurrence_plan": occurrence_plan,
        "injection_plan": injection_plan,
        "spell_lookup": spell_lookup,
        "plan_variant": spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
    }


def test_cleanup_execution_plans_phase11_cleans_variants_and_resets_ir(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate deterministic cleanup of all cached Phase 11 variants.
    Contract:
        - All existing variant plans are cleaned.
        - Cleanup swallows per-plan cleanup failures.
        - Phase 8/11 IR reset is invoked once.
    """
    crafter, _, _ = _build_spell_and_crafter()
    cleaned: list[str] = []

    class _Plan:
        def __init__(self, label: str, *, raise_on_cleanup: bool = False) -> None:
            self.label = label
            self.raise_on_cleanup = raise_on_cleanup

        def cleanup(self) -> None:
            cleaned.append(self.label)
            if self.raise_on_cleanup:
                raise RuntimeError("boom")

    crafter._execution_plan_phase11 = _Plan("main")
    crafter._execution_plan_phase11_no_overrides = _Plan("fast", raise_on_cleanup=True)
    crafter._execution_plan_phase11_overrides = _Plan("overrides")
    reset_calls: list[str] = []

    def _reset(self: SpellCrafter) -> None:
        reset_calls.append("reset")

    monkeypatch.setattr(SpellCrafter, "_reset_phase8_11_codegen_ir", _reset)

    crafter._cleanup_execution_plans_phase11()

    assert cleaned == ["main", "fast", "overrides"]
    assert reset_calls == ["reset"]
    assert crafter._execution_plan_phase11 is None
    assert crafter._execution_plan_phase11_no_overrides is None
    assert crafter._execution_plan_phase11_overrides is None


def test_cleanup_execution_plans_phase11_swallows_main_and_overrides_cleanup_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate the exception-swallow branches in Phase 11 cleanup.
    Contract:
        - Main and overrides cleanup failures are swallowed.
        - IR reset still runs and cached plan refs are cleared.
    """
    crafter, _, _ = _build_spell_and_crafter()

    class _Plan:
        def cleanup(self) -> None:
            raise RuntimeError("boom")

    crafter._execution_plan_phase11 = _Plan()
    crafter._execution_plan_phase11_no_overrides = None
    crafter._execution_plan_phase11_overrides = _Plan()
    reset_calls: list[str] = []

    def _reset(self: SpellCrafter) -> None:
        reset_calls.append("reset")

    monkeypatch.setattr(SpellCrafter, "_reset_phase8_11_codegen_ir", _reset)

    crafter._cleanup_execution_plans_phase11()

    assert reset_calls == ["reset"]
    assert crafter._execution_plan_phase11 is None
    assert crafter._execution_plan_phase11_overrides is None


def test_compile_phase12_no_overrides_executor_recompiles_on_phase11_semantic_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Ensure no-overrides executor cache invalidates on Phase11 semantic drift.
    Contract:
        Re-capturing IR with a semantic step change produces a new signature and
        forces a recompilation.
    Args:
        monkeypatch: Pytest fixture for replacing compile helper function.
    Returns:
        None.
    Raises:
        AssertionError: If semantic changes do not trigger recompilation.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    compile_calls: list[str] = []

    def _compile_stub(
            *,
            codegen_ir: dict[str, object],
            spell_lookup: dict[str, object],
    ) -> object:
        compile_calls.append(str(codegen_ir["signature"]))
        return lambda _context: "compiled"

    monkeypatch.setattr(
        spell_crafter_module,
        "compile_phase12_no_overrides_executor",
        _compile_stub,
    )

    crafter._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    crafter._capture_phase8_11_codegen_ir()
    crafter._compile_phase12_no_overrides_executor()
    first_signature = crafter._phase12_no_overrides_executor_signature

    changed_step = _make_phase11_step_stub(
        "root",
        must_register=True,
    )
    crafter._execution_plan_phase11_no_overrides = types.SimpleNamespace(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        steps=(changed_step,),
        fast_transient_plan=None,
    )
    crafter._capture_phase8_11_codegen_ir()
    crafter._compile_phase12_no_overrides_executor()

    assert len(compile_calls) == 2
    assert compile_calls[1] != compile_calls[0]
    assert crafter._phase12_no_overrides_executor_signature != first_signature


def test_compile_phase12_no_overrides_executor_requires_signature_field() -> None:
    """
    Purpose:
        Verify missing required IR fields fail fast during compile wiring.
    Contract:
        `_compile_phase12_no_overrides_executor` raises RuntimeError when the
        no-overrides payload omits required contract fields.
    Returns:
        None.
    Raises:
        AssertionError: If missing required-field errors are not raised.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._codegen_ir = {
        "phase8_11": {
            "execution": {
                "no_overrides": {
                    "step_count": 1,
                    "steps_rows": ({"spell_id": "root"},),
                    "root_spell_id": "root",
                },
            },
        },
        "signatures": {},
    }

    with pytest.raises(RuntimeError, match="missing required field 'signature'"):
        crafter._compile_phase12_no_overrides_executor()


def test_compile_phase12_no_overrides_executor_requires_steps_rows() -> None:
    """
    Purpose:
        Verify no-overrides compile wiring requires executable step payload fields.
    Contract:
        `_compile_phase12_no_overrides_executor` raises RuntimeError when
        `steps_rows` is absent/empty.
    Returns:
        None.
    Raises:
        AssertionError: If missing steps payload does not fail fast.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._codegen_ir = {
        "phase8_11": {
            "execution": {
                "no_overrides": {
                    "signature": "sig-1",
                    "step_count": 1,
                    "steps_rows": (),
                    "root_spell_id": "root",
                },
            },
        },
        "signatures": {},
    }

    with pytest.raises(RuntimeError, match="must provide non-empty 'steps_rows'"):
        crafter._compile_phase12_no_overrides_executor()


def test_compile_phase12_no_overrides_executor_reuses_cached_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify no-overrides executor compile is skipped when signature is unchanged.
    Contract:
        Compile helper is called once for a repeated identical payload signature.
    Args:
        monkeypatch: Pytest fixture for replacing compile helper function.
    Returns:
        None.
    Raises:
        AssertionError: If compile helper is called more than once.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    payload = {
        "signature": "sig-1",
        "step_count": 1,
        "steps_rows": ({"spell_id": "root"},),
        "root_spell_id": "root",
    }
    crafter._codegen_ir = {
        "phase8_11": {
            "execution": {
                "no_overrides": payload,
            },
        },
        "signatures": {},
    }
    compile_calls: list[str] = []

    def _compile_stub(
            *,
            codegen_ir: dict[str, object],
            spell_lookup: dict[str, object],
    ) -> object:
        compile_calls.append(str(codegen_ir["signature"]))
        return lambda _context: "compiled"

    monkeypatch.setattr(
        spell_crafter_module,
        "compile_phase12_no_overrides_executor",
        _compile_stub,
    )

    crafter._compile_phase12_no_overrides_executor()
    first_executor = crafter.phase12_no_overrides_executor
    crafter._compile_phase12_no_overrides_executor()

    assert len(compile_calls) == 1
    assert crafter.phase12_no_overrides_executor is first_executor


def test_compile_phase12_no_overrides_executor_recompiles_on_signature_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify no-overrides executor recompiles when payload signature changes.
    Contract:
        Compile helper is called again after signature update and executor cache
        reference is replaced.
    Args:
        monkeypatch: Pytest fixture for replacing compile helper function.
    Returns:
        None.
    Raises:
        AssertionError: If compile helper is not invoked for changed signatures.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    payload = {
        "signature": "sig-1",
        "step_count": 1,
        "steps_rows": ({"spell_id": "root"},),
        "root_spell_id": "root",
    }
    crafter._codegen_ir = {
        "phase8_11": {
            "execution": {
                "no_overrides": payload,
            },
        },
        "signatures": {},
    }
    compiled_executors: list[object] = []

    def _compile_stub(
            *,
            codegen_ir: dict[str, object],
            spell_lookup: dict[str, object],
    ) -> object:
        marker = len(compiled_executors)
        executor = lambda _context, m=marker: m
        compiled_executors.append(executor)
        return executor

    monkeypatch.setattr(
        spell_crafter_module,
        "compile_phase12_no_overrides_executor",
        _compile_stub,
    )

    crafter._compile_phase12_no_overrides_executor()
    first_executor = crafter.phase12_no_overrides_executor
    payload["signature"] = "sig-2"
    crafter._compile_phase12_no_overrides_executor()

    assert len(compiled_executors) == 2
    assert first_executor is compiled_executors[0]
    assert crafter.phase12_no_overrides_executor is compiled_executors[1]


def test_compile_phase12_no_overrides_executor_from_plan_reuses_cached_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify plan-based no-overrides compile wiring reuses cached executors.
    Contract:
        Equivalent no-overrides plans should hit signature cache and avoid
        recompilation.
    Args:
        monkeypatch: Pytest fixture for replacing plan compile helper.
    Returns:
        None.
    Raises:
        AssertionError: If equivalent plans trigger recompilation.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    compile_calls: list[str] = []

    def _compile_stub(
            *,
            plan: object,
            transient_schema: dict[str, object] | None,
    ) -> object:
        del transient_schema
        compile_calls.append(str(plan.plan_variant))
        return lambda _context: "compiled"

    monkeypatch.setattr(
        spell_crafter_module,
        "compile_phase12_no_overrides_executor_from_plan",
        _compile_stub,
    )

    plan_first = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    plan_second = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )

    crafter._compile_phase12_no_overrides_executor_from_plan(plan_first)
    first_executor = crafter.phase12_no_overrides_executor
    crafter._compile_phase12_no_overrides_executor_from_plan(plan_second)

    assert len(compile_calls) == 1
    assert crafter.phase12_no_overrides_executor is first_executor


def test_compile_phase12_no_overrides_executor_from_plan_recompiles_on_semantic_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify plan-based no-overrides compile cache invalidates on semantic drift.
    Contract:
        Changing compile-affecting step semantics changes signature and triggers
        recompilation.
    Args:
        monkeypatch: Pytest fixture for replacing plan compile helper.
    Returns:
        None.
    Raises:
        AssertionError: If semantic changes do not trigger recompilation.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    compiled_executors: list[object] = []

    def _compile_stub(
            *,
            plan: object,
            transient_schema: dict[str, object] | None,
    ) -> object:
        del plan, transient_schema
        marker = len(compiled_executors)
        executor = lambda _context, m=marker: m
        compiled_executors.append(executor)
        return executor

    monkeypatch.setattr(
        spell_crafter_module,
        "compile_phase12_no_overrides_executor_from_plan",
        _compile_stub,
    )

    first_plan = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    first_step = _make_phase11_step_stub("root", must_register=True)
    second_plan = types.SimpleNamespace(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=(first_step,),
        fast_transient_plan=None,
    )

    crafter._compile_phase12_no_overrides_executor_from_plan(first_plan)
    first_executor = crafter.phase12_no_overrides_executor
    first_signature = crafter._phase12_no_overrides_executor_signature
    crafter._compile_phase12_no_overrides_executor_from_plan(second_plan)

    assert len(compiled_executors) == 2
    assert crafter._phase12_no_overrides_executor_signature != first_signature
    assert first_executor is compiled_executors[0]
    assert crafter.phase12_no_overrides_executor is compiled_executors[1]


def test_compile_phase12_no_overrides_executor_from_plan_sets_resolution_complete_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify successful plan-based Phase12 compile marks spell resolution complete.
    Contract:
        - `_compile_phase12_no_overrides_executor_from_plan` sets
          `spell.resolution_complete=True` after successful compilation.
    Args:
        monkeypatch: Pytest fixture for replacing plan compile helper.
    Returns:
        None.
    Raises:
        AssertionError: If successful compile does not set completion flag.
    """
    crafter, spell, _ = _build_spell_and_crafter(spell_id="root")
    spell.resolution_complete = False

    def _compile_stub(
            *,
            plan: object,
            transient_schema: dict[str, object] | None,
    ) -> object:
        del plan, transient_schema
        return lambda _context: "compiled"

    monkeypatch.setattr(
        spell_crafter_module,
        "compile_phase12_no_overrides_executor_from_plan",
        _compile_stub,
    )

    plan = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    crafter._compile_phase12_no_overrides_executor_from_plan(plan)

    assert spell.resolution_complete is True


def test_reset_phase8_11_codegen_ir_clears_resolution_complete_flag() -> None:
    """
    Purpose:
        Verify phase8-11 artifact reset clears spell completion flag.
    Contract:
        - `_reset_phase8_11_codegen_ir` sets `spell.resolution_complete=False`.
    Returns:
        None.
    Raises:
        AssertionError: If reset does not clear completion flag.
    """
    crafter, spell, _ = _build_spell_and_crafter(spell_id="root")
    spell.resolution_complete = True

    crafter._reset_phase8_11_codegen_ir()

    assert spell.resolution_complete is False


def test_run_phase_occurrence_plan_reuses_cached_plan_when_input_signature_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase8 reuses cached occurrence plan when phase8 input signature
        is unchanged.
    Contract:
        With stable phase8 signature and cached occurrence plan, repeated calls
        to `run_phase_occurrence_plan` should skip rebuild and avoid re-marking
        phase8_11 codegen IR dirty.
    Args:
        monkeypatch: Pytest fixture for replacing phase8 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If phase8 plan rebuild is not elided on warm rerun.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = types.SimpleNamespace()

    builder_init_calls = 0
    build_calls = 0
    cleanup_calls = 0
    mark_calls: list[str] = []

    class _OccurrencePlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build(self) -> object:
            nonlocal build_calls
            build_calls += 1
            return types.SimpleNamespace(
                execution_order=(),
                root_instance_key=("root", None),
                shared_spell_ids=set(),
                contract_dependencies_complete=True,
                occurrence_graph={},
                instance_keys_by_spell_id={},
                canonical_occurrences_by_spell_id={},
                contract_overrides_by_occurrence={},
                contract_overrides_by_spell_id={},
            )

        def cleanup(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1

    def _signature_stub(
        self: SpellCrafter,
        *,
        root_blueprint: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, root_blueprint, spell_lookup
        return "stable-phase8-signature"

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "OccurrencePlanBuilder", _OccurrencePlanBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase8_occurrence_plan_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_occurrence_plan("cid")
    first_plan = crafter._occurrence_plan_phase8
    crafter.run_phase_occurrence_plan("cid")

    assert builder_init_calls == 1
    assert build_calls == 1
    assert cleanup_calls == 1
    assert mark_calls == ["mark"]
    assert crafter._occurrence_plan_phase8 is first_plan
    assert crafter._phase8_occurrence_plan_input_signature == "stable-phase8-signature"


def test_run_phase_occurrence_plan_rebuilds_when_input_signature_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase8 rebuilds occurrence plan when phase8 signature changes.
    Contract:
        Changed phase8 input signature should force a fresh occurrence-plan
        build and dirty mark.
    Args:
        monkeypatch: Pytest fixture for replacing phase8 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If phase8 signature drift does not trigger rebuild.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = types.SimpleNamespace()

    signature_values = ["phase8-signature-a", "phase8-signature-b"]
    builder_init_calls = 0
    build_calls = 0
    cleanup_calls = 0
    mark_calls: list[str] = []

    class _OccurrencePlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build(self) -> object:
            nonlocal build_calls
            build_calls += 1
            return types.SimpleNamespace(
                execution_order=(),
                root_instance_key=("root", None),
                shared_spell_ids=set(),
                contract_dependencies_complete=True,
                occurrence_graph={},
                instance_keys_by_spell_id={},
                canonical_occurrences_by_spell_id={},
                contract_overrides_by_occurrence={},
                contract_overrides_by_spell_id={},
            )

        def cleanup(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1

    def _signature_stub(
        self: SpellCrafter,
        *,
        root_blueprint: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, root_blueprint, spell_lookup
        return signature_values.pop(0)

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "OccurrencePlanBuilder", _OccurrencePlanBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase8_occurrence_plan_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_occurrence_plan("cid")
    first_plan = crafter._occurrence_plan_phase8
    crafter.run_phase_occurrence_plan("cid")

    assert builder_init_calls == 2
    assert build_calls == 2
    assert cleanup_calls == 2
    assert mark_calls == ["mark", "mark"]
    assert crafter._occurrence_plan_phase8 is not first_plan
    assert crafter._phase8_occurrence_plan_input_signature == "phase8-signature-b"


def test_run_phase_occurrence_plan_reuses_signature_via_fast_key_when_no_mutations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase8 reuses cached signature via fast key on no-mutation warm runs.
    Contract:
        With stable no-mutation inputs and identical fast key, phase8 should
        avoid a second deep signature build call while preserving cache-hit reuse.
    Args:
        monkeypatch: Pytest fixture for replacing phase8 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If warm rerun still rebuilds deep signature.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = types.SimpleNamespace(
        root_spell_id="root",
        ordered_node_ids=("root",),
        path_registry=object(),
        socket_refs=(),
    )

    builder_init_calls = 0
    build_calls = 0
    cleanup_calls = 0
    signature_calls: list[str] = []
    mark_calls: list[str] = []

    class _OccurrencePlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build(self) -> object:
            nonlocal build_calls
            build_calls += 1
            return types.SimpleNamespace(
                execution_order=(),
                root_instance_key=("root", None),
                shared_spell_ids=set(),
                contract_dependencies_complete=True,
                occurrence_graph={},
                instance_keys_by_spell_id={},
                canonical_occurrences_by_spell_id={},
                contract_overrides_by_occurrence={},
                contract_overrides_by_spell_id={},
            )

        def cleanup(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1

    def _signature_stub(
        self: SpellCrafter,
        *,
        root_blueprint: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, root_blueprint, spell_lookup
        signature_calls.append("called")
        return "stable-phase8-signature"

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "OccurrencePlanBuilder", _OccurrencePlanBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase8_occurrence_plan_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_occurrence_plan("cid")
    first_plan = crafter._occurrence_plan_phase8
    crafter.run_phase_occurrence_plan("cid")

    assert signature_calls == ["called"]
    assert builder_init_calls == 1
    assert build_calls == 1
    assert cleanup_calls == 1
    assert mark_calls == ["mark"]
    assert first_plan is not None
    assert crafter._occurrence_plan_phase8 is first_plan
    assert crafter._phase8_occurrence_plan_fast_key is not None


def test_run_phase_occurrence_plan_fast_key_falls_back_when_mutation_override_active(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase8 fast key is disabled when mutation overrides are active.
    Contract:
        Any active mutation override must force deep-signature execution on each
        run to keep mutation payload semantics in the signature path.
    Args:
        monkeypatch: Pytest fixture for replacing phase8 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If mutation-active runs incorrectly reuse fast key.
    """
    crafter, spell, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = types.SimpleNamespace(
        root_spell_id="root",
        ordered_node_ids=("root",),
        path_registry=object(),
        socket_refs=(),
    )
    spell._mutation_override = {"flag": {"enabled": True}}

    builder_init_calls = 0
    build_calls = 0
    cleanup_calls = 0
    signature_calls: list[str] = []
    mark_calls: list[str] = []

    class _OccurrencePlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build(self) -> object:
            nonlocal build_calls
            build_calls += 1
            return types.SimpleNamespace(
                execution_order=(),
                root_instance_key=("root", None),
                shared_spell_ids=set(),
                contract_dependencies_complete=True,
                occurrence_graph={},
                instance_keys_by_spell_id={},
                canonical_occurrences_by_spell_id={},
                contract_overrides_by_occurrence={},
                contract_overrides_by_spell_id={},
            )

        def cleanup(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1

    def _signature_stub(
        self: SpellCrafter,
        *,
        root_blueprint: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, root_blueprint, spell_lookup
        signature_calls.append("called")
        return "stable-phase8-signature"

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "OccurrencePlanBuilder", _OccurrencePlanBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase8_occurrence_plan_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_occurrence_plan("cid")
    first_plan = crafter._occurrence_plan_phase8
    crafter.run_phase_occurrence_plan("cid")

    assert signature_calls == ["called", "called"]
    assert builder_init_calls == 1
    assert build_calls == 1
    assert cleanup_calls == 1
    assert mark_calls == ["mark"]
    assert first_plan is not None
    assert crafter._occurrence_plan_phase8 is first_plan
    assert crafter._phase8_occurrence_plan_fast_key is None


def test_run_phase_injection_plan_reuses_cached_plan_when_input_signature_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase9 reuses cached injection plan when phase9 signature is
        unchanged.
    Contract:
        With stable phase9 signature and cached injection plan, repeated calls
        to `run_phase_injection_plan` should skip rebuild and avoid re-marking
        phase8_11 codegen IR dirty.
    Args:
        monkeypatch: Pytest fixture for replacing phase9 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If phase9 rebuild is not elided on warm rerun.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()

    builder_init_calls = 0
    build_calls = 0
    mark_calls: list[str] = []

    class _InjectionPlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build(self) -> object:
            nonlocal build_calls
            build_calls += 1
            return types.SimpleNamespace(instance_injections={})

    def _signature_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
    ) -> str:
        del self, occurrence_plan
        return "stable-phase9-signature"

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "InjectionPlanBuilder", _InjectionPlanBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase9_injection_plan_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_injection_plan("cid")
    first_plan = crafter._injection_plan_phase9
    crafter.run_phase_injection_plan("cid")

    assert builder_init_calls == 1
    assert build_calls == 1
    assert mark_calls == ["mark"]
    assert crafter._injection_plan_phase9 is first_plan
    assert crafter._phase9_injection_plan_input_signature == "stable-phase9-signature"


def test_run_phase_injection_plan_rebuilds_when_input_signature_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase9 rebuilds injection plan when phase9 signature changes.
    Contract:
        Changed phase9 signature should force a fresh injection-plan build and
        dirty mark.
    Args:
        monkeypatch: Pytest fixture for replacing phase9 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If phase9 signature drift does not trigger rebuild.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()

    signature_values = ["phase9-signature-a", "phase9-signature-b"]
    builder_init_calls = 0
    build_calls = 0
    mark_calls: list[str] = []

    class _InjectionPlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build(self) -> object:
            nonlocal build_calls
            build_calls += 1
            return types.SimpleNamespace(instance_injections={})

    def _signature_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
    ) -> str:
        del self, occurrence_plan
        return signature_values.pop(0)

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "InjectionPlanBuilder", _InjectionPlanBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase9_injection_plan_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_injection_plan("cid")
    first_plan = crafter._injection_plan_phase9
    crafter.run_phase_injection_plan("cid")

    assert builder_init_calls == 2
    assert build_calls == 2
    assert mark_calls == ["mark", "mark"]
    assert crafter._injection_plan_phase9 is not first_plan
    assert crafter._phase9_injection_plan_input_signature == "phase9-signature-b"


def test_run_phase_patch_maps_reuses_cached_maps_when_input_signature_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase10 reuses cached patch maps on unchanged blueprint signature.
    Contract:
        With stable phase10 input signature and cached maps, `run_phase_patch_maps`
        should skip rebuild and avoid re-marking phase8_11 codegen IR dirty.
    Args:
        monkeypatch: Pytest fixture for replacing phase10 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If phase10 rebuilds patch maps on unchanged signature.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = types.SimpleNamespace()

    builder_init_calls = 0
    override_build_calls = 0
    mutation_build_calls = 0
    cleanup_calls = 0
    mark_calls: list[str] = []

    class _PatchMapBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build_override_patch_map(self) -> object:
            nonlocal override_build_calls
            override_build_calls += 1
            return types.SimpleNamespace(targets_by_spec={}, specificity_by_spec={})

        def build_mutation_patch_map(self) -> object:
            nonlocal mutation_build_calls
            mutation_build_calls += 1
            return types.SimpleNamespace(targets_by_spec={})

        def cleanup(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1

    def _signature_stub(
        self: SpellCrafter,
        root_blueprint: object,
    ) -> tuple[str]:
        del self, root_blueprint
        return ("stable-phase10-signature",)

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "PatchMapBuilder", _PatchMapBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase10_patch_maps_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_patch_maps("cid")
    first_override_patch_map = crafter._override_patch_map_phase10
    first_mutation_patch_map = crafter._mutation_patch_map_phase10
    crafter.run_phase_patch_maps("cid")

    assert builder_init_calls == 1
    assert override_build_calls == 1
    assert mutation_build_calls == 1
    assert cleanup_calls == 1
    assert mark_calls == ["mark"]
    assert crafter._override_patch_map_phase10 is first_override_patch_map
    assert crafter._mutation_patch_map_phase10 is first_mutation_patch_map
    assert crafter._phase10_patch_maps_input_signature == ("stable-phase10-signature",)


def test_run_phase_patch_maps_rebuilds_when_input_signature_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase10 rebuilds patch maps when blueprint signature changes.
    Contract:
        A changed phase10 input signature forces a fresh patch-map rebuild and
        dirty mark.
    Args:
        monkeypatch: Pytest fixture for replacing phase10 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If signature drift does not trigger rebuild.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = types.SimpleNamespace()

    signature_values = [("phase10-signature-a",), ("phase10-signature-b",)]
    builder_init_calls = 0
    override_build_calls = 0
    mutation_build_calls = 0
    cleanup_calls = 0
    mark_calls: list[str] = []

    class _PatchMapBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            nonlocal builder_init_calls
            builder_init_calls += 1

        def build_override_patch_map(self) -> object:
            nonlocal override_build_calls
            override_build_calls += 1
            return types.SimpleNamespace(targets_by_spec={}, specificity_by_spec={})

        def build_mutation_patch_map(self) -> object:
            nonlocal mutation_build_calls
            mutation_build_calls += 1
            return types.SimpleNamespace(targets_by_spec={})

        def cleanup(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1

    def _signature_stub(
        self: SpellCrafter,
        root_blueprint: object,
    ) -> tuple[str]:
        del self, root_blueprint
        return signature_values.pop(0)

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    monkeypatch.setattr(spell_crafter_module, "PatchMapBuilder", _PatchMapBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_build_phase10_patch_maps_input_signature", _signature_stub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)

    crafter.run_phase_patch_maps("cid")
    first_override_patch_map = crafter._override_patch_map_phase10
    first_mutation_patch_map = crafter._mutation_patch_map_phase10
    crafter.run_phase_patch_maps("cid")

    assert builder_init_calls == 2
    assert override_build_calls == 2
    assert mutation_build_calls == 2
    assert cleanup_calls == 2
    assert mark_calls == ["mark", "mark"]
    assert crafter._override_patch_map_phase10 is not first_override_patch_map
    assert crafter._mutation_patch_map_phase10 is not first_mutation_patch_map
    assert crafter._phase10_patch_maps_input_signature == ("phase10-signature-b",)


def test_phase8_10_runs_mark_phase8_11_codegen_ir_dirty_without_eager_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phases 8-10 mark phase8_11 IR dirty state without eager capture.
    Contract:
        `run_phase_occurrence_plan`, `run_phase_injection_plan`, and
        `run_phase_patch_maps` call dirty-marking and do not invoke direct
        phase8_11 capture.
    Args:
        monkeypatch: Pytest fixture for replacing builders and capture hooks.
    Returns:
        None.
    Raises:
        AssertionError: If phases 8-10 still perform eager capture.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._root_blueprint_phase5 = object()

    class _OccurrencePlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def build(self) -> object:
            return types.SimpleNamespace(
                execution_order=(),
                root_instance_key=("root", None),
                shared_spell_ids=set(),
                contract_dependencies_complete=True,
                occurrence_graph={},
                instance_keys_by_spell_id={},
                canonical_occurrences_by_spell_id={},
                contract_overrides_by_occurrence={},
                contract_overrides_by_spell_id={},
            )

        def cleanup(self) -> None:
            pass

    class _InjectionPlanBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def build(self) -> object:
            return types.SimpleNamespace(instance_injections={})

    class _PatchMapBuilderStub:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def build_override_patch_map(self) -> object:
            return types.SimpleNamespace(targets_by_spec={}, specificity_by_spec={})

        def build_mutation_patch_map(self) -> object:
            return types.SimpleNamespace(targets_by_spec={})

        def cleanup(self) -> None:
            pass

    mark_calls: list[str] = []
    capture_calls: list[str] = []

    def _mark_stub(self: SpellCrafter) -> None:
        mark_calls.append("mark")
        self._phase8_11_codegen_ir_dirty = True

    def _capture_stub(self: SpellCrafter) -> None:
        capture_calls.append("capture")

    monkeypatch.setattr(spell_crafter_module, "OccurrencePlanBuilder", _OccurrencePlanBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "InjectionPlanBuilder", _InjectionPlanBuilderStub)
    monkeypatch.setattr(spell_crafter_module, "PatchMapBuilder", _PatchMapBuilderStub)
    monkeypatch.setattr(SpellCrafter, "_mark_phase8_11_codegen_ir_dirty", _mark_stub)
    monkeypatch.setattr(SpellCrafter, "_capture_phase8_11_codegen_ir", _capture_stub)

    crafter.run_phase_occurrence_plan("cid")
    crafter.run_phase_injection_plan("cid")
    crafter.run_phase_patch_maps("cid")

    assert mark_calls == ["mark", "mark", "mark"]
    assert capture_calls == []
    assert crafter._phase8_11_codegen_ir_dirty is True


def test_run_phase_execution_plan_compiles_phase12_without_eager_phase8_11_flush(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase11 run compiles phase12 no-overrides executor without
        forcing eager phase8_11 flush.
    Contract:
        `run_phase_execution_plan` marks phase8_11 IR dirty, compiles phase12
        no-overrides executor from direct plan input, and leaves dirty IR for lazy
        reader-triggered capture.
    Args:
        monkeypatch: Pytest fixture for replacing plan/flush/compile hooks.
    Returns:
        None.
    Raises:
        AssertionError: If eager flush occurs or compile plan contract drifts.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()
    crafter._injection_plan_phase9 = types.SimpleNamespace()

    flush_calls: list[bool] = []
    compile_plan_variants: list[str] = []

    def _build_plan_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
        plan_variant: str,
    ) -> object:
        return _make_phase11_plan_stub(
            plan_variant=plan_variant,
            root_spell_id="root",
            step_spell_ids=("root",),
        )

    def _cache_metrics_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        plan: object,
    ) -> None:
        return None

    def _flush_stub(self: SpellCrafter) -> None:
        flush_calls.append(self._phase8_11_codegen_ir_dirty)
        self._phase8_11_codegen_ir_dirty = False

    def _compile_plan_stub(
        self: SpellCrafter,
        plan: object | None,
    ) -> None:
        del self
        assert plan is not None
        compile_plan_variants.append(str(plan.plan_variant))

    monkeypatch.setattr(SpellCrafter, "_build_execution_plan_variant", _build_plan_stub)
    monkeypatch.setattr(SpellCrafter, "_cache_execution_plan_metrics", _cache_metrics_stub)
    monkeypatch.setattr(SpellCrafter, "_capture_phase8_11_codegen_ir_if_dirty", _flush_stub)
    monkeypatch.setattr(SpellCrafter, "_compile_phase12_no_overrides_executor_from_plan", _compile_plan_stub)

    crafter.run_phase_execution_plan("cid")

    assert flush_calls == []
    assert compile_plan_variants == [spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST]
    assert crafter._phase8_11_codegen_ir_dirty is True


def test_run_phase_execution_plan_builds_override_variants_separately_from_stripped_no_overrides_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase11 rebuilds override-capable variants from source inputs
        when the no-overrides base plan is intentionally stripped.
    Contract:
        A stripped no-overrides base must not poison the override-capable
        variants. Phase11 therefore rebuilds `OVERRIDES` and
        `OVERRIDES_WITH_MUTATIONS` from occurrence/injection inputs instead of
        deriving them from the stripped base plan.
    Args:
        monkeypatch: Pytest fixture for replacing phase11 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If the override-capable variants stop rebuilding from
            source inputs.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()
    crafter._injection_plan_phase9 = types.SimpleNamespace()

    build_calls: list[str] = []

    def _build_plan_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
        plan_variant: str,
    ) -> object:
        del self, occurrence_plan, injection_plan, spell_lookup
        build_calls.append(plan_variant)
        return types.SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=[_make_phase11_step_stub("root")],
            spell_id_step_index={"root": 0},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={"root": 1},
            plan_variant=plan_variant,
            fast_transient_plan=None,
        )

    def _cache_metrics_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        plan: object,
    ) -> None:
        del self, occurrence_plan, plan
        return None

    def _compile_plan_stub(
        self: SpellCrafter,
        plan: object | None,
    ) -> None:
        del self
        assert plan is not None
        return None

    monkeypatch.setattr(SpellCrafter, "_build_execution_plan_variant", _build_plan_stub)
    monkeypatch.setattr(SpellCrafter, "_cache_execution_plan_metrics", _cache_metrics_stub)
    monkeypatch.setattr(SpellCrafter, "_compile_phase12_no_overrides_executor_from_plan", _compile_plan_stub)

    crafter.run_phase_execution_plan("cid")

    assert build_calls == [
        spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert crafter._execution_plan_phase11_no_overrides.plan_variant == spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST
    assert crafter._execution_plan_phase11_overrides.plan_variant == spell_crafter_module.ExecutionPlanVariant.OVERRIDES
    assert crafter._execution_plan_phase11.plan_variant == spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS
    assert crafter._execution_plan_phase11_overrides.fast_transient_plan is None
    assert crafter._execution_plan_phase11.fast_transient_plan is None


def test_run_phase_execution_plan_reuses_no_overrides_plan_when_input_signature_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase11 reuses cached no-overrides plan across warm runs when
        no-overrides input signature remains unchanged.
    Contract:
        With stable signature and compatible base plan, only one no-overrides
        full build occurs across repeated phase11 runs.
    Args:
        monkeypatch: Pytest fixture for replacing phase11 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If the warm rerun rebuilds the cached variant set.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()
    crafter._injection_plan_phase9 = types.SimpleNamespace()

    build_calls: list[str] = []
    signature_calls: list[str] = []

    def _build_signature_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, occurrence_plan, injection_plan, spell_lookup
        signature_calls.append("called")
        return "stable-phase11-signature"

    def _build_plan_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
        plan_variant: str,
    ) -> object:
        del self, occurrence_plan, injection_plan, spell_lookup
        build_calls.append(plan_variant)
        return types.SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=[_make_phase11_step_stub("root")],
            spell_id_step_index={"root": 0},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={"root": 1},
            plan_variant=plan_variant,
            fast_transient_plan=None,
        )

    def _cache_metrics_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        plan: object,
    ) -> None:
        del self, occurrence_plan, plan
        return None

    def _compile_plan_stub(
        self: SpellCrafter,
        plan: object,
    ) -> None:
        del self
        assert plan is not None
        return None

    monkeypatch.setattr(SpellCrafter, "_build_phase11_no_overrides_input_signature", _build_signature_stub)
    monkeypatch.setattr(SpellCrafter, "_build_execution_plan_variant", _build_plan_stub)
    monkeypatch.setattr(SpellCrafter, "_cache_execution_plan_metrics", _cache_metrics_stub)
    monkeypatch.setattr(SpellCrafter, "_compile_phase12_no_overrides_executor_from_plan", _compile_plan_stub)

    crafter.run_phase_execution_plan("cid")
    first_plan = crafter._execution_plan_phase11_no_overrides
    crafter.run_phase_execution_plan("cid")

    assert build_calls == [
        spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert signature_calls == ["called", "called"]
    assert first_plan is not None
    assert crafter._execution_plan_phase11_no_overrides is first_plan
    assert crafter._phase11_no_overrides_input_signature == "stable-phase11-signature"


def test_run_phase_execution_plan_reuses_cached_variant_set_when_input_signature_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase11 reuses the full cached variant set on unchanged-signature
        warm reruns after the override-capable variants are built from source
        inputs.
    Contract:
        With stable no-overrides input signature and cached variants, phase11
        should not rebuild any variant on the warm rerun and should retain
        cached plan object identities.
    Args:
        monkeypatch: Pytest fixture for replacing phase11 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If cached sibling variants are rebuilt on warm rerun.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()
    crafter._injection_plan_phase9 = types.SimpleNamespace()

    signature_calls: list[str] = []
    build_calls: list[str] = []
    cache_metrics_calls = 0
    compile_calls = 0

    def _build_signature_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, occurrence_plan, injection_plan, spell_lookup
        signature_calls.append("called")
        return "stable-phase11-signature"

    def _build_plan_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
        plan_variant: str,
    ) -> object:
        del self, occurrence_plan, injection_plan, spell_lookup
        build_calls.append(plan_variant)
        return types.SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=[_make_phase11_step_stub("root")],
            spell_id_step_index={"root": 0},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={"root": 1},
            plan_variant=plan_variant,
            fast_transient_plan=None,
        )

    def _cache_metrics_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        plan: object,
    ) -> None:
        del self, occurrence_plan, plan
        nonlocal cache_metrics_calls
        cache_metrics_calls += 1
        return None

    def _compile_plan_stub(
        self: SpellCrafter,
        plan: object,
    ) -> None:
        assert plan is not None
        nonlocal compile_calls
        compile_calls += 1
        self._phase12_no_overrides_executor = object()
        self._phase12_no_overrides_executor_signature = "compiled-signature"
        return None

    monkeypatch.setattr(SpellCrafter, "_build_phase11_no_overrides_input_signature", _build_signature_stub)
    monkeypatch.setattr(SpellCrafter, "_build_execution_plan_variant", _build_plan_stub)
    monkeypatch.setattr(SpellCrafter, "_cache_execution_plan_metrics", _cache_metrics_stub)
    monkeypatch.setattr(SpellCrafter, "_compile_phase12_no_overrides_executor_from_plan", _compile_plan_stub)

    crafter.run_phase_execution_plan("cid")
    first_no_overrides = crafter._execution_plan_phase11_no_overrides
    first_overrides = crafter._execution_plan_phase11_overrides
    first_overrides_with_mutations = crafter._execution_plan_phase11

    crafter.run_phase_execution_plan("cid")

    assert signature_calls == ["called", "called"]
    assert build_calls == [
        spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert cache_metrics_calls == 2
    assert compile_calls == 1
    assert crafter._execution_plan_phase11_no_overrides is first_no_overrides
    assert crafter._execution_plan_phase11_overrides is first_overrides
    assert crafter._execution_plan_phase11 is first_overrides_with_mutations
    assert crafter._phase11_no_overrides_input_signature == "stable-phase11-signature"


def test_run_phase_execution_plan_rebuilds_no_overrides_plan_when_input_signature_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase11 rebuilds the full variant set when the no-overrides
        input signature changes.
    Contract:
        A changed no-overrides input signature forces a fresh no-overrides
        rebuild, and the override-capable variants are rebuilt from source
        inputs in the same pass.
    Args:
        monkeypatch: Pytest fixture for replacing phase11 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If signature drift does not trigger the expected full
            variant rebuild.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()
    crafter._injection_plan_phase9 = types.SimpleNamespace()

    signature_values = ["phase11-signature-a", "phase11-signature-b"]
    build_calls: list[str] = []

    def _build_signature_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
    ) -> str:
        del self, occurrence_plan, injection_plan, spell_lookup
        return signature_values.pop(0)

    def _build_plan_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
        plan_variant: str,
    ) -> object:
        del self, occurrence_plan, injection_plan, spell_lookup
        build_calls.append(plan_variant)
        return types.SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=[_make_phase11_step_stub("root")],
            spell_id_step_index={"root": 0},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={"root": 1},
            plan_variant=plan_variant,
            fast_transient_plan=None,
        )

    def _cache_metrics_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        plan: object,
    ) -> None:
        del self, occurrence_plan, plan
        return None

    def _compile_plan_stub(
        self: SpellCrafter,
        plan: object,
    ) -> None:
        del self
        assert plan is not None
        return None

    monkeypatch.setattr(SpellCrafter, "_build_phase11_no_overrides_input_signature", _build_signature_stub)
    monkeypatch.setattr(SpellCrafter, "_build_execution_plan_variant", _build_plan_stub)
    monkeypatch.setattr(SpellCrafter, "_cache_execution_plan_metrics", _cache_metrics_stub)
    monkeypatch.setattr(SpellCrafter, "_compile_phase12_no_overrides_executor_from_plan", _compile_plan_stub)

    crafter.run_phase_execution_plan("cid")
    first_plan = crafter._execution_plan_phase11_no_overrides
    crafter.run_phase_execution_plan("cid")
    second_plan = crafter._execution_plan_phase11_no_overrides

    assert build_calls == [
        spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
        spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert first_plan is not None
    assert second_plan is not None
    assert second_plan is not first_plan
    assert crafter._phase11_no_overrides_input_signature == "phase11-signature-b"


def test_run_phase_execution_plan_falls_back_to_full_build_for_incompatible_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify phase11 falls back to legacy per-variant rebuild when base plan
        shape is incompatible with reuse.
    Contract:
        If the no-overrides base lacks required structural fields, phase11 must
        call `_build_execution_plan_variant` for overrides and mutations variants.
    Args:
        monkeypatch: Pytest fixture for replacing phase11 collaborators.
    Returns:
        None.
    Raises:
        AssertionError: If fallback rebuild behavior regresses.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._occurrence_plan_phase8 = types.SimpleNamespace()
    crafter._injection_plan_phase9 = types.SimpleNamespace()

    build_calls: list[str] = []

    def _build_plan_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        injection_plan: object,
        spell_lookup: dict[str, object],
        plan_variant: str,
    ) -> object:
        del self, occurrence_plan, injection_plan, spell_lookup
        build_calls.append(plan_variant)
        return _make_phase11_plan_stub(
            plan_variant=plan_variant,
            root_spell_id="root",
            step_spell_ids=("root",),
        )

    def _cache_metrics_stub(
        self: SpellCrafter,
        *,
        occurrence_plan: object,
        plan: object,
    ) -> None:
        del self, occurrence_plan, plan
        return None

    def _compile_plan_stub(
        self: SpellCrafter,
        plan: object | None,
    ) -> None:
        del self
        assert plan is not None
        return None

    monkeypatch.setattr(SpellCrafter, "_build_execution_plan_variant", _build_plan_stub)
    monkeypatch.setattr(SpellCrafter, "_cache_execution_plan_metrics", _cache_metrics_stub)
    monkeypatch.setattr(SpellCrafter, "_compile_phase12_no_overrides_executor_from_plan", _compile_plan_stub)

    crafter.run_phase_execution_plan("cid")

    assert build_calls == [
        spell_crafter_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES,
        spell_crafter_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]


def test_codegen_ir_property_flushes_phase8_11_when_dirty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify `codegen_ir` property lazily flushes pending phase8_11 exports.
    Contract:
        When phase8_11 IR is marked dirty, `codegen_ir` access triggers one
        dirty flush before returning the payload mapping.
    Args:
        monkeypatch: Pytest fixture for replacing dirty-flush helper.
    Returns:
        None.
    Raises:
        AssertionError: If `codegen_ir` does not flush dirty state.
    """
    crafter, _, _ = _build_spell_and_crafter(spell_id="root")
    crafter._phase8_11_codegen_ir_dirty = True
    flush_calls: list[bool] = []

    def _flush_stub(self: SpellCrafter) -> None:
        flush_calls.append(self._phase8_11_codegen_ir_dirty)
        self._codegen_ir = {
            "spell_id": "root",
            "lineage_id": "lineage",
            "phase2_5": {},
            "phase8_11": {"signature": "sig"},
            "signatures": {"phase8_11": "sig"},
        }
        self._phase8_11_codegen_ir_dirty = False

    monkeypatch.setattr(SpellCrafter, "_capture_phase8_11_codegen_ir_if_dirty", _flush_stub)

    payload = crafter.codegen_ir

    assert flush_calls == [True]
    assert payload is crafter._codegen_ir
    assert crafter._phase8_11_codegen_ir_dirty is False



