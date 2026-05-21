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



