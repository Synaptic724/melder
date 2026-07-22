from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
        SpellInjectionInstanceSpec,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis import (
        SpellRuntimeRecord,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )


OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]


class ManyOnlyCodegenPlanVariant:
    """
    Many-only lane variant labels.

    Purpose:
        Tell the many-only builder whether it is compiling the no-overrides or
        overrides lane without reusing generalized variant names.
    """

    __slots__ = ()
    NO_OVERRIDES: str = "no_overrides"
    OVERRIDES: str = "overrides"


class ManyOnlyCodegenPlanCallMode:
    """
    Many-only fixed-arity call labels.

    Purpose:
        Describe the emitted call shape for each many-only step using
        many-only-local names instead of generalized call-mode names.
    """

    __slots__ = ()
    CALL0: int = 0
    CALL1: int = 1
    CALL2: int = 2
    CALL3: int = 3
    CALL4: int = 4
    CALL5: int = 5
    CALL6: int = 6
    CALL7: int = 7
    CALL8: int = 8
    CALLN: int = 9


class ManyOnlyCodegenPlanStep:
    """
    One many-only execution step.

    Purpose:
        Carry the spell-static step information used by both many-only runtime
        emitters without reusing the generalized step object.
    """

    __slots__ = [
        "_instance_key",
        "_occurrence",
        "_spell",
        "_shared_instance",
        "_dependency_resolution_order",
        "_collection_param_names",
        "_uses_positional_override",
        "_contract_positional_override",
        "_has_contract_payload",
        "_contract_payload",
        "_override_match_prefix",
        "_override_match_prefix_len",
    ]

    def __init__(
            self,
            *,
            instance_key: InstanceKey,
            occurrence: OccurrenceKey,
            spell: Any,
            shared_instance: bool,
            dependency_resolution_order: List[Tuple[str, List[InstanceKey]]],
            collection_param_names: frozenset[str],
            uses_positional_override: bool,
            contract_positional_override: Optional[Any],
            has_contract_payload: bool,
            contract_payload: Optional[Dict[str, Any]],
            override_match_prefix: Optional[int],
            override_match_prefix_len: int,
    ) -> None:
        """
        Initialize one many-only execution step.
        """
        if collection_param_names is None:
            raise ValueError("collection_param_names must not be None.")
        self._instance_key = instance_key
        self._occurrence = occurrence
        self._spell = spell
        self._shared_instance = shared_instance
        self._dependency_resolution_order = dependency_resolution_order
        self._collection_param_names = collection_param_names
        self._uses_positional_override = uses_positional_override
        self._contract_positional_override = contract_positional_override
        self._has_contract_payload = has_contract_payload
        self._contract_payload = contract_payload
        self._override_match_prefix = override_match_prefix
        self._override_match_prefix_len = override_match_prefix_len

    @property
    def instance_key(self) -> InstanceKey:
        """Return the step instance key."""
        return self._instance_key

    @property
    def occurrence(self) -> OccurrenceKey:
        """Return the backing occurrence key."""
        return self._occurrence

    @property
    def spell(self) -> Any:
        """Return the runtime spell object."""
        return self._spell

    @property
    def shared_instance(self) -> bool:
        """Return whether this step is shared in the instance layer."""
        return self._shared_instance

    @property
    def creations_target_kind(self) -> int:
        """
        Return the fixed many-only creations target kind.

        Contract:
            Many-only runtime steps always use caller-owned creations.
        """
        return 1

    @property
    def dependency_resolution_order(self) -> List[Tuple[str, List[InstanceKey]]]:
        """Return ordered parameter-to-dependency bindings."""
        return self._dependency_resolution_order

    @property
    def collection_param_names(self) -> frozenset[str]:
        """
        Return the constructor parameter names that are collection DI sockets.

        Contract:
            - Carries phase-3 socket truth (list[Frame] shapes) into codegen so
              emitters wrap these parameters in a list REGARDLESS of how many
              dependency keys resolved. Never derive collection-ness from
              dependency count.
        """
        return self._collection_param_names

    @property
    def uses_positional_override(self) -> bool:
        """Return whether this step uses positional override payloads."""
        return self._uses_positional_override

    @property
    def contract_positional_override(self) -> Optional[Any]:
        """Return the plan-time positional override payload."""
        return self._contract_positional_override

    @property
    def has_contract_payload(self) -> bool:
        """Return whether this step carries plan-time contract kwargs."""
        return self._has_contract_payload

    @property
    def contract_payload(self) -> Optional[Dict[str, Any]]:
        """Return the plan-time contract kwargs payload."""
        return self._contract_payload

    @property
    def override_match_prefix(self) -> Optional[int]:
        """Return the override-target path prefix for this step."""
        return self._override_match_prefix

    @property
    def override_match_prefix_len(self) -> int:
        """Return the depth of the override-target path prefix."""
        return self._override_match_prefix_len


class ManyOnlyNoOverridesPlan(Cleanable):
    """
    Planner-owned many-only no-overrides payload.

    Purpose:
        Hold the many-only no-overrides execution contract directly, without
        reusing generalized fast/transient payload names.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lane_id",
        "_root_spell_id",
        "_root_instance_key",
        "_steps",
        "_root_step_index",
        "_step_call_targets",
        "_step_call_modes",
        "_step_dep1",
        "_step_dep2a",
        "_step_dep2b",
        "_step_dep3a",
        "_step_dep3b",
        "_step_dep3c",
        "_step_dep4a",
        "_step_dep4b",
        "_step_dep4c",
        "_step_dep4d",
        "_step_dep5a",
        "_step_dep5b",
        "_step_dep5c",
        "_step_dep5d",
        "_step_dep5e",
        "_step_dep6a",
        "_step_dep6b",
        "_step_dep6c",
        "_step_dep6d",
        "_step_dep6e",
        "_step_dep6f",
        "_step_dep7a",
        "_step_dep7b",
        "_step_dep7c",
        "_step_dep7d",
        "_step_dep7e",
        "_step_dep7f",
        "_step_dep7g",
        "_step_dep8a",
        "_step_dep8b",
        "_step_dep8c",
        "_step_dep8d",
        "_step_dep8e",
        "_step_dep8f",
        "_step_dep8g",
        "_step_dep8h",
        "_step_spell_ids",
        "_step_has_disposal_methods",
        "_step_disposal_methods",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            lane_id: str,
            root_spell_id: str,
            root_instance_key: InstanceKey,
            steps: List[ManyOnlyCodegenPlanStep],
            root_step_index: int,
            step_call_targets: List[Any],
            step_call_modes: List[int],
            step_dep1: List[int],
            step_dep2a: List[int],
            step_dep2b: List[int],
            step_dep3a: List[int],
            step_dep3b: List[int],
            step_dep3c: List[int],
            step_dep4a: List[int],
            step_dep4b: List[int],
            step_dep4c: List[int],
            step_dep4d: List[int],
            step_dep5a: List[int],
            step_dep5b: List[int],
            step_dep5c: List[int],
            step_dep5d: List[int],
            step_dep5e: List[int],
            step_dep6a: List[int],
            step_dep6b: List[int],
            step_dep6c: List[int],
            step_dep6d: List[int],
            step_dep6e: List[int],
            step_dep6f: List[int],
            step_dep7a: List[int],
            step_dep7b: List[int],
            step_dep7c: List[int],
            step_dep7d: List[int],
            step_dep7e: List[int],
            step_dep7f: List[int],
            step_dep7g: List[int],
            step_dep8a: List[int],
            step_dep8b: List[int],
            step_dep8c: List[int],
            step_dep8d: List[int],
            step_dep8e: List[int],
            step_dep8f: List[int],
            step_dep8g: List[int],
            step_dep8h: List[int],
            step_spell_ids: List[str],
            step_has_disposal_methods: List[bool],
            step_disposal_methods: List[Tuple[str, ...]],
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize one many-only no-overrides plan.
        """
        super().__init__()
        self._lane_id = lane_id
        self._root_spell_id = root_spell_id
        self._root_instance_key = root_instance_key
        self._steps = steps
        self._root_step_index = root_step_index
        self._step_call_targets = step_call_targets
        self._step_call_modes = step_call_modes
        self._step_dep1 = step_dep1
        self._step_dep2a = step_dep2a
        self._step_dep2b = step_dep2b
        self._step_dep3a = step_dep3a
        self._step_dep3b = step_dep3b
        self._step_dep3c = step_dep3c
        self._step_dep4a = step_dep4a
        self._step_dep4b = step_dep4b
        self._step_dep4c = step_dep4c
        self._step_dep4d = step_dep4d
        self._step_dep5a = step_dep5a
        self._step_dep5b = step_dep5b
        self._step_dep5c = step_dep5c
        self._step_dep5d = step_dep5d
        self._step_dep5e = step_dep5e
        self._step_dep6a = step_dep6a
        self._step_dep6b = step_dep6b
        self._step_dep6c = step_dep6c
        self._step_dep6d = step_dep6d
        self._step_dep6e = step_dep6e
        self._step_dep6f = step_dep6f
        self._step_dep7a = step_dep7a
        self._step_dep7b = step_dep7b
        self._step_dep7c = step_dep7c
        self._step_dep7d = step_dep7d
        self._step_dep7e = step_dep7e
        self._step_dep7f = step_dep7f
        self._step_dep7g = step_dep7g
        self._step_dep8a = step_dep8a
        self._step_dep8b = step_dep8b
        self._step_dep8c = step_dep8c
        self._step_dep8d = step_dep8d
        self._step_dep8e = step_dep8e
        self._step_dep8f = step_dep8f
        self._step_dep8g = step_dep8g
        self._step_dep8h = step_dep8h
        self._step_spell_ids = step_spell_ids
        self._step_has_disposal_methods = step_has_disposal_methods
        self._step_disposal_methods = step_disposal_methods
        self._metadata = {} if metadata is None else metadata

    def cleanup(self) -> None:
        """
        Deterministically release the many-only no-overrides plan.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._steps.clear()
        self._step_call_targets.clear()
        self._step_call_modes.clear()
        self._step_dep1.clear()
        self._step_dep2a.clear()
        self._step_dep2b.clear()
        self._step_dep3a.clear()
        self._step_dep3b.clear()
        self._step_dep3c.clear()
        self._step_dep4a.clear()
        self._step_dep4b.clear()
        self._step_dep4c.clear()
        self._step_dep4d.clear()
        self._step_dep5a.clear()
        self._step_dep5b.clear()
        self._step_dep5c.clear()
        self._step_dep5d.clear()
        self._step_dep5e.clear()
        self._step_dep6a.clear()
        self._step_dep6b.clear()
        self._step_dep6c.clear()
        self._step_dep6d.clear()
        self._step_dep6e.clear()
        self._step_dep6f.clear()
        self._step_dep7a.clear()
        self._step_dep7b.clear()
        self._step_dep7c.clear()
        self._step_dep7d.clear()
        self._step_dep7e.clear()
        self._step_dep7f.clear()
        self._step_dep7g.clear()
        self._step_dep8a.clear()
        self._step_dep8b.clear()
        self._step_dep8c.clear()
        self._step_dep8d.clear()
        self._step_dep8e.clear()
        self._step_dep8f.clear()
        self._step_dep8g.clear()
        self._step_dep8h.clear()
        self._step_spell_ids.clear()
        self._step_has_disposal_methods.clear()
        self._step_disposal_methods.clear()
        self._metadata.clear()

        del self._lane_id
        del self._root_spell_id
        del self._root_instance_key
        del self._steps
        del self._root_step_index
        del self._step_call_targets
        del self._step_call_modes
        del self._step_dep1
        del self._step_dep2a
        del self._step_dep2b
        del self._step_dep3a
        del self._step_dep3b
        del self._step_dep3c
        del self._step_dep4a
        del self._step_dep4b
        del self._step_dep4c
        del self._step_dep4d
        del self._step_dep5a
        del self._step_dep5b
        del self._step_dep5c
        del self._step_dep5d
        del self._step_dep5e
        del self._step_dep6a
        del self._step_dep6b
        del self._step_dep6c
        del self._step_dep6d
        del self._step_dep6e
        del self._step_dep6f
        del self._step_dep7a
        del self._step_dep7b
        del self._step_dep7c
        del self._step_dep7d
        del self._step_dep7e
        del self._step_dep7f
        del self._step_dep7g
        del self._step_dep8a
        del self._step_dep8b
        del self._step_dep8c
        del self._step_dep8d
        del self._step_dep8e
        del self._step_dep8f
        del self._step_dep8g
        del self._step_dep8h
        del self._step_spell_ids
        del self._step_has_disposal_methods
        del self._step_disposal_methods
        del self._metadata

    @property
    def lane_id(self) -> str:
        """Return the lane identifier."""
        return self._lane_id

    @property
    def root_spell_id(self) -> str:
        """Return the root spell id."""
        return self._root_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        """Return the root instance key."""
        return self._root_instance_key

    @property
    def steps(self) -> List[ManyOnlyCodegenPlanStep]:
        """Return the ordered many-only steps."""
        return self._steps

    @property
    def root_step_index(self) -> int:
        """Return the root step index."""
        return self._root_step_index

    @property
    def step_call_targets(self) -> Tuple[Any, ...]:
        """Return ordered step call targets."""
        return tuple(self._step_call_targets)

    @property
    def step_call_modes(self) -> Tuple[int, ...]:
        """Return ordered step call modes."""
        return tuple(self._step_call_modes)

    @property
    def step_dep1(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 1 references (detached)."""
        return tuple(self._step_dep1)

    @property
    def step_dep2a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 2a references (detached)."""
        return tuple(self._step_dep2a)

    @property
    def step_dep2b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 2b references (detached)."""
        return tuple(self._step_dep2b)

    @property
    def step_dep3a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 3a references (detached)."""
        return tuple(self._step_dep3a)

    @property
    def step_dep3b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 3b references (detached)."""
        return tuple(self._step_dep3b)

    @property
    def step_dep3c(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 3c references (detached)."""
        return tuple(self._step_dep3c)

    @property
    def step_dep4a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 4a references (detached)."""
        return tuple(self._step_dep4a)

    @property
    def step_dep4b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 4b references (detached)."""
        return tuple(self._step_dep4b)

    @property
    def step_dep4c(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 4c references (detached)."""
        return tuple(self._step_dep4c)

    @property
    def step_dep4d(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 4d references (detached)."""
        return tuple(self._step_dep4d)

    @property
    def step_dep5a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 5a references (detached)."""
        return tuple(self._step_dep5a)

    @property
    def step_dep5b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 5b references (detached)."""
        return tuple(self._step_dep5b)

    @property
    def step_dep5c(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 5c references (detached)."""
        return tuple(self._step_dep5c)

    @property
    def step_dep5d(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 5d references (detached)."""
        return tuple(self._step_dep5d)

    @property
    def step_dep5e(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 5e references (detached)."""
        return tuple(self._step_dep5e)

    @property
    def step_dep6a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 6a references (detached)."""
        return tuple(self._step_dep6a)

    @property
    def step_dep6b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 6b references (detached)."""
        return tuple(self._step_dep6b)

    @property
    def step_dep6c(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 6c references (detached)."""
        return tuple(self._step_dep6c)

    @property
    def step_dep6d(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 6d references (detached)."""
        return tuple(self._step_dep6d)

    @property
    def step_dep6e(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 6e references (detached)."""
        return tuple(self._step_dep6e)

    @property
    def step_dep6f(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 6f references (detached)."""
        return tuple(self._step_dep6f)

    @property
    def step_dep7a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7a references (detached)."""
        return tuple(self._step_dep7a)

    @property
    def step_dep7b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7b references (detached)."""
        return tuple(self._step_dep7b)

    @property
    def step_dep7c(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7c references (detached)."""
        return tuple(self._step_dep7c)

    @property
    def step_dep7d(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7d references (detached)."""
        return tuple(self._step_dep7d)

    @property
    def step_dep7e(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7e references (detached)."""
        return tuple(self._step_dep7e)

    @property
    def step_dep7f(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7f references (detached)."""
        return tuple(self._step_dep7f)

    @property
    def step_dep7g(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 7g references (detached)."""
        return tuple(self._step_dep7g)

    @property
    def step_dep8a(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8a references (detached)."""
        return tuple(self._step_dep8a)

    @property
    def step_dep8b(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8b references (detached)."""
        return tuple(self._step_dep8b)

    @property
    def step_dep8c(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8c references (detached)."""
        return tuple(self._step_dep8c)

    @property
    def step_dep8d(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8d references (detached)."""
        return tuple(self._step_dep8d)

    @property
    def step_dep8e(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8e references (detached)."""
        return tuple(self._step_dep8e)

    @property
    def step_dep8f(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8f references (detached)."""
        return tuple(self._step_dep8f)

    @property
    def step_dep8g(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8g references (detached)."""
        return tuple(self._step_dep8g)

    @property
    def step_dep8h(self) -> Tuple[int, ...]:
        """Return the ordered dependency-slot 8h references (detached)."""
        return tuple(self._step_dep8h)

    @property
    def step_spell_ids(self) -> Tuple[str, ...]:
        """Return ordered step spell ids."""
        return tuple(self._step_spell_ids)

    @property
    def step_has_disposal_methods(self) -> Tuple[bool, ...]:
        """Return ordered step disposal flags."""
        return tuple(self._step_has_disposal_methods)

    @property
    def step_disposal_methods(self) -> Tuple[Tuple[str, ...], ...]:
        """Return ordered step disposal method rows."""
        return tuple(self._step_disposal_methods)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return mutable metadata."""
        return self._metadata

    @property
    def has_any_disposal_methods(self) -> bool:
        """Return whether any step declares disposal methods."""
        return any(self._step_has_disposal_methods)


class ManyOnlyOverridesPlan(Cleanable):
    """
    Planner-owned many-only overrides payload.

    Purpose:
        Hold the many-only overrides lane without reusing generalized plan
        objects.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lane_id",
        "_root_spell_id",
        "_root_instance_key",
        "_steps",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            lane_id: str,
            root_spell_id: str,
            root_instance_key: InstanceKey,
            steps: List[ManyOnlyCodegenPlanStep],
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize one many-only overrides plan.
        """
        super().__init__()
        self._lane_id = lane_id
        self._root_spell_id = root_spell_id
        self._root_instance_key = root_instance_key
        self._steps = steps
        self._metadata = {} if metadata is None else metadata

    def cleanup(self) -> None:
        """
        Deterministically release the many-only overrides plan.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._steps.clear()
        self._metadata.clear()
        del self._lane_id
        del self._root_spell_id
        del self._root_instance_key
        del self._steps
        del self._metadata

    @property
    def lane_id(self) -> str:
        """Return the many-only overrides lane id."""
        return self._lane_id

    @property
    def root_spell_id(self) -> str:
        """Return the root spell id for this overrides lane."""
        return self._root_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        """Return the root instance key for this overrides lane."""
        return self._root_instance_key

    @property
    def steps(self) -> List[ManyOnlyCodegenPlanStep]:
        """Return the live ordered many-only step list (not copied)."""
        return self._steps

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return the live mutable metadata mapping (not copied)."""
        return self._metadata


class ManyOnlyCodegenPlanBuilder:
    """
    Standalone many-only lane-plan builder.

    Purpose:
        Build the many-only planner payload directly from `SpellCodegenModel`
        without inheriting generalized planner machinery.
    """

    __slots__ = [
        "_state",
        "_plan_variant",
    ]

    def __init__(
            self,
            *,
            state: "SpellCodegenModel",
            plan_variant: str,
    ) -> None:
        """
        Initialize one many-only builder.
        """
        self._state = state
        self._plan_variant = plan_variant

    def build(self) -> Any:
        """
        Build one many-only lane plan.
        """
        self._assert_many_only_preconditions()
        if self._plan_variant == ManyOnlyCodegenPlanVariant.NO_OVERRIDES:
            return self._build_no_overrides_plan()
        if self._plan_variant == ManyOnlyCodegenPlanVariant.OVERRIDES:
            return self._build_overrides_plan()
        raise ValueError(
            f"Unknown many-only plan variant '{self._plan_variant}'."
        )

    def _assert_many_only_preconditions(self) -> None:
        """
        Enforce many-only discovery preconditions on the model.
        """
        existence_occurrence_shape = self._state.existence_occurrence_shape
        if existence_occurrence_shape is None:
            raise ValueError(
                "Many-only lane build requires existence_occurrence_shape."
            )
        total_spell_count = existence_occurrence_shape.total_spell_count
        if total_spell_count <= 1:
            raise ValueError(
                "Many-only lane build requires more than one visible spell."
            )
        many_count = 0
        for existence, count in existence_occurrence_shape.existence_counts:
            if existence is Existence.many:
                many_count = count
                break
        if many_count != total_spell_count:
            raise ValueError(
                "Many-only lane build requires every visible spell to be Existence.many."
            )

    def _build_ordered_steps(self) -> Tuple[
        List[ManyOnlyCodegenPlanStep],
        Dict[InstanceKey, int],
        str,
        InstanceKey,
    ]:
        """
        Build the ordered many-only step list from model sections.
        """
        graph_shape = self._state.graph_shape
        order_shape = self._state.order_shape
        instance_shape = self._state.instance_shape
        injection_shape = self._state.injection_shape
        spell_runtime_shape = self._state.spell_runtime_shape
        if (
                graph_shape is None
                or order_shape is None
                or instance_shape is None
                or injection_shape is None
                or spell_runtime_shape is None
        ):
            raise ValueError(
                "Many-only lane build requires graph/order/instance/injection/runtime sections."
            )

        steps: List[ManyOnlyCodegenPlanStep] = []
        instance_key_to_step_index: Dict[InstanceKey, int] = {}
        path_registry = graph_shape.path_registry

        for spell_id in order_shape.execution_order:
            runtime_record = spell_runtime_shape.records_by_spell_id.get(spell_id)
            if runtime_record is None:
                raise ValueError(
                    f"Many-only lane build is missing runtime record for '{spell_id}'."
                )
            if runtime_record.existence is not Existence.many:
                raise ValueError(
                    "Many-only lane build received a non-many runtime record."
                )

            for instance_key in instance_shape.instance_keys_by_spell_id.get(spell_id, []):
                occurrence = self._occurrence_for_instance_key(
                    instance_key=instance_key,
                    instance_shape=instance_shape,
                )
                inject_spec = injection_shape.instance_specs_by_instance_key.get(
                    instance_key
                )
                if inject_spec is None:
                    raise ValueError(
                        f"Many-only lane build is missing injection spec for {instance_key!r}."
                    )

                dependency_resolution_order = self._dependency_resolution_order(
                    inject_spec=inject_spec
                )
                contract_payload = inject_spec.contract_payload
                contract_positional_override = None
                has_contract_payload = bool(contract_payload)
                if (
                        inject_spec.uses_positional_override
                        and contract_payload is not None
                        and "__args__" in contract_payload
                ):
                    contract_positional_override = contract_payload["__args__"]

                override_match_prefix = None
                override_match_prefix_len = 0
                if self._plan_variant == ManyOnlyCodegenPlanVariant.OVERRIDES:
                    override_match_prefix = occurrence[1]
                    override_match_prefix_len = path_registry.depth(
                        override_match_prefix
                    )

                step = ManyOnlyCodegenPlanStep(
                    instance_key=instance_key,
                    occurrence=occurrence,
                    spell=runtime_record.spell,
                    shared_instance=(
                        spell_id in instance_shape.shared_spell_ids
                    ),
                    dependency_resolution_order=dependency_resolution_order,
                    collection_param_names=inject_spec.collection_param_names,
                    uses_positional_override=inject_spec.uses_positional_override,
                    contract_positional_override=contract_positional_override,
                    has_contract_payload=has_contract_payload,
                    contract_payload=contract_payload,
                    override_match_prefix=override_match_prefix,
                    override_match_prefix_len=override_match_prefix_len,
                )
                instance_key_to_step_index[instance_key] = len(steps)
                steps.append(step)

        return (
            steps,
            instance_key_to_step_index,
            graph_shape.root_spell_id,
            instance_shape.root_instance_key,
        )

    def _build_no_overrides_plan(self) -> ManyOnlyNoOverridesPlan:
        """
        Build the standalone many-only no-overrides plan.
        """
        (
            steps,
            instance_key_to_step_index,
            root_spell_id,
            root_instance_key,
        ) = self._build_ordered_steps()

        step_count = len(steps)
        step_call_targets: List[Any] = [None] * step_count
        step_call_modes: List[int] = [ManyOnlyCodegenPlanCallMode.CALLN] * step_count
        step_dep1: List[int] = [-1] * step_count
        step_dep2a: List[int] = [-1] * step_count
        step_dep2b: List[int] = [-1] * step_count
        step_dep3a: List[int] = [-1] * step_count
        step_dep3b: List[int] = [-1] * step_count
        step_dep3c: List[int] = [-1] * step_count
        step_dep4a: List[int] = [-1] * step_count
        step_dep4b: List[int] = [-1] * step_count
        step_dep4c: List[int] = [-1] * step_count
        step_dep4d: List[int] = [-1] * step_count
        step_dep5a: List[int] = [-1] * step_count
        step_dep5b: List[int] = [-1] * step_count
        step_dep5c: List[int] = [-1] * step_count
        step_dep5d: List[int] = [-1] * step_count
        step_dep5e: List[int] = [-1] * step_count
        step_dep6a: List[int] = [-1] * step_count
        step_dep6b: List[int] = [-1] * step_count
        step_dep6c: List[int] = [-1] * step_count
        step_dep6d: List[int] = [-1] * step_count
        step_dep6e: List[int] = [-1] * step_count
        step_dep6f: List[int] = [-1] * step_count
        step_dep7a: List[int] = [-1] * step_count
        step_dep7b: List[int] = [-1] * step_count
        step_dep7c: List[int] = [-1] * step_count
        step_dep7d: List[int] = [-1] * step_count
        step_dep7e: List[int] = [-1] * step_count
        step_dep7f: List[int] = [-1] * step_count
        step_dep7g: List[int] = [-1] * step_count
        step_dep8a: List[int] = [-1] * step_count
        step_dep8b: List[int] = [-1] * step_count
        step_dep8c: List[int] = [-1] * step_count
        step_dep8d: List[int] = [-1] * step_count
        step_dep8e: List[int] = [-1] * step_count
        step_dep8f: List[int] = [-1] * step_count
        step_dep8g: List[int] = [-1] * step_count
        step_dep8h: List[int] = [-1] * step_count
        step_spell_ids: List[str] = [step.spell.spell_id for step in steps]
        step_has_disposal_methods: List[bool] = [
            bool(step.spell.has_disposal_methods)
            for step in steps
        ]
        step_disposal_methods: List[Tuple[str, ...]] = [
            tuple(step.spell.disposal_method_names)
            for step in steps
        ]

        root_step_index = instance_key_to_step_index.get(root_instance_key)
        if root_step_index is None:
            raise ValueError(
                "Many-only no-overrides build is missing the root step index."
            )

        for step_index, step in enumerate(steps):
            step_call_targets[step_index] = step.spell.spell
            requirements = step.spell.requirements
            if requirements is not None:
                params = requirements.parameters
                param_order = [param.name for param in params]
                di_param_names = {
                    param_name
                    for param_name, dependency_keys in step.dependency_resolution_order
                    if dependency_keys
                }
                last_di_index = -1
                for index, param in enumerate(params):
                    if param.name in di_param_names:
                        last_di_index = index
                positional_ok = True
                if last_di_index >= 0:
                    for index, param in enumerate(params):
                        if index > last_di_index:
                            break
                        if (
                                param.is_keyword_only
                                or param.is_var_keyword
                                or param.is_var_positional
                        ):
                            positional_ok = False
                            break
                        if param.name not in di_param_names:
                            positional_ok = False
                            break
            else:
                param_order = [
                    param_name
                    for param_name, _dependency_keys
                    in step.dependency_resolution_order
                ]
                positional_ok = False

            if step.collection_param_names:
                # Specialized positional CALLn modes pass one bare scalar per
                # dependency; collection sockets must inject a list even with
                # one member, so any collection param routes this step through
                # the CALLN fallback (kwargs path, which wraps by socket truth).
                positional_ok = False

            ordered_dependency_groups: List[List[int]] = []
            dependency_map = {
                param_name: dependency_keys
                for param_name, dependency_keys
                in step.dependency_resolution_order
            }
            for param_name in param_order:
                dependency_keys = dependency_map.get(param_name)
                if not dependency_keys:
                    continue
                dependency_indexes: List[int] = []
                for dependency_key in dependency_keys:
                    dependency_step_index = instance_key_to_step_index.get(
                        dependency_key
                    )
                    if dependency_step_index is None:
                        raise ValueError(
                            "Many-only no-overrides build found a dependency "
                            "outside the step index."
                        )
                    dependency_indexes.append(dependency_step_index)
                ordered_dependency_groups.append(dependency_indexes)

            if not positional_ok or step.has_contract_payload:
                continue

            group_count = len(ordered_dependency_groups)
            if group_count == 0:
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL0
                continue
            if group_count == 1 and len(ordered_dependency_groups[0]) == 1:
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL1
                step_dep1[step_index] = ordered_dependency_groups[0][0]
                continue
            if group_count == 2 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL2
                step_dep2a[step_index] = ordered_dependency_groups[0][0]
                step_dep2b[step_index] = ordered_dependency_groups[1][0]
                continue
            if group_count == 3 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL3
                step_dep3a[step_index] = ordered_dependency_groups[0][0]
                step_dep3b[step_index] = ordered_dependency_groups[1][0]
                step_dep3c[step_index] = ordered_dependency_groups[2][0]
                continue
            if group_count == 4 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL4
                step_dep4a[step_index] = ordered_dependency_groups[0][0]
                step_dep4b[step_index] = ordered_dependency_groups[1][0]
                step_dep4c[step_index] = ordered_dependency_groups[2][0]
                step_dep4d[step_index] = ordered_dependency_groups[3][0]
                continue
            if group_count == 5 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL5
                step_dep5a[step_index] = ordered_dependency_groups[0][0]
                step_dep5b[step_index] = ordered_dependency_groups[1][0]
                step_dep5c[step_index] = ordered_dependency_groups[2][0]
                step_dep5d[step_index] = ordered_dependency_groups[3][0]
                step_dep5e[step_index] = ordered_dependency_groups[4][0]
                continue
            if group_count == 6 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL6
                step_dep6a[step_index] = ordered_dependency_groups[0][0]
                step_dep6b[step_index] = ordered_dependency_groups[1][0]
                step_dep6c[step_index] = ordered_dependency_groups[2][0]
                step_dep6d[step_index] = ordered_dependency_groups[3][0]
                step_dep6e[step_index] = ordered_dependency_groups[4][0]
                step_dep6f[step_index] = ordered_dependency_groups[5][0]
                continue
            if group_count == 7 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL7
                step_dep7a[step_index] = ordered_dependency_groups[0][0]
                step_dep7b[step_index] = ordered_dependency_groups[1][0]
                step_dep7c[step_index] = ordered_dependency_groups[2][0]
                step_dep7d[step_index] = ordered_dependency_groups[3][0]
                step_dep7e[step_index] = ordered_dependency_groups[4][0]
                step_dep7f[step_index] = ordered_dependency_groups[5][0]
                step_dep7g[step_index] = ordered_dependency_groups[6][0]
                continue
            if group_count == 8 and all(len(group) == 1 for group in ordered_dependency_groups):
                step_call_modes[step_index] = ManyOnlyCodegenPlanCallMode.CALL8
                step_dep8a[step_index] = ordered_dependency_groups[0][0]
                step_dep8b[step_index] = ordered_dependency_groups[1][0]
                step_dep8c[step_index] = ordered_dependency_groups[2][0]
                step_dep8d[step_index] = ordered_dependency_groups[3][0]
                step_dep8e[step_index] = ordered_dependency_groups[4][0]
                step_dep8f[step_index] = ordered_dependency_groups[5][0]
                step_dep8g[step_index] = ordered_dependency_groups[6][0]
                step_dep8h[step_index] = ordered_dependency_groups[7][0]

        metadata = {
            "plan_family": "many_only",
            "no_overrides_plan_kind": "many_only_no_overrides",
        }
        return ManyOnlyNoOverridesPlan(
            lane_id=ManyOnlyCodegenPlanVariant.NO_OVERRIDES,
            root_spell_id=root_spell_id,
            root_instance_key=root_instance_key,
            steps=steps,
            root_step_index=root_step_index,
            step_call_targets=step_call_targets,
            step_call_modes=step_call_modes,
            step_dep1=step_dep1,
            step_dep2a=step_dep2a,
            step_dep2b=step_dep2b,
            step_dep3a=step_dep3a,
            step_dep3b=step_dep3b,
            step_dep3c=step_dep3c,
            step_dep4a=step_dep4a,
            step_dep4b=step_dep4b,
            step_dep4c=step_dep4c,
            step_dep4d=step_dep4d,
            step_dep5a=step_dep5a,
            step_dep5b=step_dep5b,
            step_dep5c=step_dep5c,
            step_dep5d=step_dep5d,
            step_dep5e=step_dep5e,
            step_dep6a=step_dep6a,
            step_dep6b=step_dep6b,
            step_dep6c=step_dep6c,
            step_dep6d=step_dep6d,
            step_dep6e=step_dep6e,
            step_dep6f=step_dep6f,
            step_dep7a=step_dep7a,
            step_dep7b=step_dep7b,
            step_dep7c=step_dep7c,
            step_dep7d=step_dep7d,
            step_dep7e=step_dep7e,
            step_dep7f=step_dep7f,
            step_dep7g=step_dep7g,
            step_dep8a=step_dep8a,
            step_dep8b=step_dep8b,
            step_dep8c=step_dep8c,
            step_dep8d=step_dep8d,
            step_dep8e=step_dep8e,
            step_dep8f=step_dep8f,
            step_dep8g=step_dep8g,
            step_dep8h=step_dep8h,
            step_spell_ids=step_spell_ids,
            step_has_disposal_methods=step_has_disposal_methods,
            step_disposal_methods=step_disposal_methods,
            metadata=metadata,
        )

    def _build_overrides_plan(self) -> ManyOnlyOverridesPlan:
        """
        Build the standalone many-only overrides plan.
        """
        (
            steps,
            _instance_key_to_step_index,
            root_spell_id,
            root_instance_key,
        ) = self._build_ordered_steps()
        metadata = {
            "plan_family": "many_only",
            "overrides_plan_kind": "many_only_overrides",
        }
        return ManyOnlyOverridesPlan(
            lane_id=ManyOnlyCodegenPlanVariant.OVERRIDES,
            root_spell_id=root_spell_id,
            root_instance_key=root_instance_key,
            steps=steps,
            metadata=metadata,
        )

    @staticmethod
    def _occurrence_for_instance_key(
            *,
            instance_key: InstanceKey,
            instance_shape: Any,
    ) -> OccurrenceKey:
        """
        Resolve the occurrence key backing one instance key.
        """
        spell_id, path_id = instance_key
        if path_id is not None:
            return spell_id, path_id
        canonical_occurrence = instance_shape.canonical_occurrences_by_spell_id.get(
            spell_id
        )
        if canonical_occurrence is None:
            raise ValueError(
                f"Many-only lane plan: canonical occurrence missing for '{spell_id}'."
            )
        return canonical_occurrence

    @staticmethod
    def _dependency_resolution_order(
            *,
            inject_spec: Optional["SpellInjectionInstanceSpec"],
    ) -> List[Tuple[str, List[InstanceKey]]]:
        """
        Build ordered parameter dependency bindings for one injection spec.
        """
        if inject_spec is None:
            return []
        dependency_resolution_order: List[Tuple[str, List[InstanceKey]]] = []
        for param_name, source in inject_spec.param_sources.items():
            if not source.dependency_keys:
                if source.kind == "dependency" and source.is_collection:
                    # Zero-provider required collection socket: keep the param
                    # with an empty key list so downstream emitters inject []
                    # (owner policy: an empty collection spawns with an empty
                    # list instead of failing).
                    dependency_resolution_order.append((param_name, []))
                continue
            dependency_resolution_order.append(
                (
                    param_name,
                    list(source.dependency_keys),
                )
            )
        return dependency_resolution_order
