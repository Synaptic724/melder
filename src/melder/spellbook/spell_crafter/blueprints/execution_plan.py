from typing import Any, Dict, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionPlan,
    InjectionSpec,
)
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    InstanceKey,
    OccurrenceKey,
    OccurrencePlan,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import ISpell

FastPlanData = Tuple[Any, ...]
FastTransientPlan = Tuple[Any, ...]


class ExecutionPlanVariant:
    """
    Internal

    Phase 11 execution plan variant labels.

    Purpose:
        Identify which precompiled execution plan should be selected based on
        override and mutation payloads at meld time.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ()
    NO_OVERRIDES_FAST = "no_overrides_fast"
    OVERRIDES = "overrides"
    OVERRIDES_WITH_MUTATIONS = "overrides_with_mutations"


class ExecutionPlanTargetKind:
    """
    Internal

    Phase 11 execution plan creations target kinds.

    Purpose:
        Represent creations routing as a compact enum-like value to avoid
        repeated string comparisons at runtime.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ()
    CALLER = 1
    OWNER = 2
    SPELLSPACE = 3


class ExecutionPlanCallMode:
    """
    Internal

    Fast-path call modes for NO_OVERRIDES_FAST execution.

    Purpose:
        Capture trivial call shapes (0, 1, 2, or 3 dependencies) to avoid
        per-step list allocation and inner loop overhead.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ()
    CALL0 = 0
    CALL1 = 1
    CALL2 = 2
    CALL3 = 3
    CALL4 = 4
    CALL5 = 5
    CALL6 = 6
    CALL7 = 7
    CALL8 = 8
    CALLN = 9


class ExecutionPlanStep:
    """
    Internal

    Phase 11 execution step metadata.

    Purpose:
        Capture precomputed routing, call recipes, and spell references needed
        to execute meld with minimal runtime planning.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_instance_key",
        "_occurrence",
        "_spell",
        "_existence",
        "_creations_target_kind",
        "_shared_instance",
        "_inject_spec",
        "_dependency_keys",
        "_dependency_keys_by_param",
        "_dependency_resolution_order",
        "_override_keys",
        "_override_match_prefix",
        "_override_match_prefix_len",
        "_expects_overrides",
        "_contract_keys",
        "_allow_list_aggregation",
        "_uses_positional_override",
        "_contract_payload",
        "_contract_positional_override",
        "_has_contract_payload",
        "_lock_hint",
        "_use_spell_lock_hint",
        "_requires_spellspace",
        "_owner_conduit_required",
        "_must_register",
        "_disposal_method_names",
    ]

    def __init__(
            self,
            *,
            instance_key: InstanceKey,
            occurrence: OccurrenceKey,
            spell: ISpell,
            existence: Existence,
            creations_target_kind: int,
            shared_instance: bool,
            inject_spec: Optional[InjectionSpec],
            dependency_keys: List[InstanceKey],
            dependency_keys_by_param: Dict[str, List[InstanceKey]],
            dependency_resolution_order: List[tuple[str, List[InstanceKey]]],
            override_keys: List[str],
            override_match_prefix: Optional[int],
            override_match_prefix_len: int,
            expects_overrides: bool,
            contract_keys: List[str],
            allow_list_aggregation: bool,
            uses_positional_override: bool,
            contract_payload: Optional[Dict[str, Any]],
            contract_positional_override: Optional[Any],
            has_contract_payload: bool,
            lock_hint: str,
            use_spell_lock_hint: bool,
            requires_spellspace: bool,
            owner_conduit_required: bool,
            must_register: bool,
            disposal_method_names: List[str],
    ) -> None:
        """
        Initialize one Phase 11 execution step.

        Contract:
            - Stores all precomputed routing and execution metadata for one
              instance key in the plan.
            - Does not derive or normalize semantics beyond required-null
              validation; upstream builders are responsible for producing
              coherent values.
            - Treats dependency, override, and contract metadata as already
              compiled runtime inputs.
        """
        if instance_key is None:
            raise ValueError("instance_key must not be None.")
        if occurrence is None:
            raise ValueError("occurrence must not be None.")
        if spell is None:
            raise ValueError("spell must not be None.")
        if existence is None:
            raise ValueError("existence must not be None.")
        if creations_target_kind is None:
            raise ValueError("creations_target_kind must not be None.")
        if shared_instance is None:
            raise ValueError("shared_instance must not be None.")
        if dependency_keys is None:
            raise ValueError("dependency_keys must not be None.")
        if dependency_keys_by_param is None:
            raise ValueError("dependency_keys_by_param must not be None.")
        if dependency_resolution_order is None:
            raise ValueError("dependency_resolution_order must not be None.")
        if override_keys is None:
            raise ValueError("override_keys must not be None.")
        if override_match_prefix_len is None:
            raise ValueError("override_match_prefix_len must not be None.")
        if expects_overrides is None:
            raise ValueError("expects_overrides must not be None.")
        if contract_keys is None:
            raise ValueError("contract_keys must not be None.")
        if allow_list_aggregation is None:
            raise ValueError("allow_list_aggregation must not be None.")
        if uses_positional_override is None:
            raise ValueError("uses_positional_override must not be None.")
        if has_contract_payload is None:
            raise ValueError("has_contract_payload must not be None.")
        if lock_hint is None:
            raise ValueError("lock_hint must not be None.")
        if use_spell_lock_hint is None:
            raise ValueError("use_spell_lock_hint must not be None.")
        if requires_spellspace is None:
            raise ValueError("requires_spellspace must not be None.")
        if owner_conduit_required is None:
            raise ValueError("owner_conduit_required must not be None.")
        if must_register is None:
            raise ValueError("must_register must not be None.")
        if disposal_method_names is None:
            raise ValueError("disposal_method_names must not be None.")

        self._instance_key: InstanceKey = instance_key
        self._occurrence: OccurrenceKey = occurrence
        self._spell: ISpell = spell
        self._existence: Existence = existence
        self._creations_target_kind: int = creations_target_kind
        self._shared_instance: bool = shared_instance
        self._inject_spec: Optional[InjectionSpec] = inject_spec
        self._dependency_keys: List[InstanceKey] = dependency_keys
        self._dependency_keys_by_param: Dict[str, List[InstanceKey]] = dependency_keys_by_param
        self._dependency_resolution_order: List[tuple[str, List[InstanceKey]]] = dependency_resolution_order
        self._override_keys: List[str] = override_keys
        self._override_match_prefix: Optional[int] = override_match_prefix
        self._override_match_prefix_len: int = override_match_prefix_len
        self._expects_overrides: bool = expects_overrides
        self._contract_keys: List[str] = contract_keys
        self._allow_list_aggregation: bool = allow_list_aggregation
        self._uses_positional_override: bool = uses_positional_override
        self._contract_payload: Optional[Dict[str, Any]] = contract_payload
        self._contract_positional_override: Optional[Any] = contract_positional_override
        self._has_contract_payload: bool = has_contract_payload
        self._lock_hint: str = lock_hint
        self._use_spell_lock_hint: bool = use_spell_lock_hint
        self._requires_spellspace: bool = requires_spellspace
        self._owner_conduit_required: bool = owner_conduit_required
        self._must_register: bool = must_register
        self._disposal_method_names: List[str] = disposal_method_names

    @property
    def instance_key(self) -> InstanceKey:
        """Return the instance key this execution step constructs or reuses."""
        return self._instance_key

    @property
    def occurrence(self) -> OccurrenceKey:
        """Return the occurrence-plan entry this step was derived from."""
        return self._occurrence

    @property
    def spell(self) -> ISpell:
        """Return the spell object this step executes."""
        return self._spell

    @property
    def existence(self) -> Existence:
        """Return the existence policy that governs reuse/registration here."""
        return self._existence

    @property
    def creations_target_kind(self) -> int:
        """Return which creations container this step should target at runtime."""
        return self._creations_target_kind

    @property
    def shared_instance(self) -> bool:
        """Return whether this step resolves through a shared-instance lane."""
        return self._shared_instance

    @property
    def inject_spec(self) -> Optional[InjectionSpec]:
        """Return the Phase 9 injection spec attached to this step, if any."""
        return self._inject_spec

    @property
    def dependency_keys(self) -> List[InstanceKey]:
        """Return the flattened dependency instance keys for this step."""
        return self._dependency_keys

    @property
    def dependency_keys_by_param(self) -> Dict[str, List[InstanceKey]]:
        """Return dependency instance keys grouped by constructor parameter."""
        return self._dependency_keys_by_param

    @property
    def dependency_resolution_order(self) -> List[tuple[str, List[InstanceKey]]]:
        """
        Return the pre-flattened dependency resolution order for this step.
        """
        return self._dependency_resolution_order

    @property
    def override_keys(self) -> List[str]:
        """Return the Phase 10 override keys that can target this step."""
        return self._override_keys

    @property
    def override_match_prefix(self) -> Optional[int]:
        """
        Return the precomputed override path id for this step.
        """
        return self._override_match_prefix

    @property
    def override_match_prefix_len(self) -> int:
        """
        Return the cached override path depth for this step.
        """
        return self._override_match_prefix_len

    @property
    def expects_overrides(self) -> bool:
        """
        Return whether this step expects override sockets in its plan metadata.
        """
        return self._expects_overrides

    @property
    def contract_keys(self) -> List[str]:
        """Return the SpellContract keys associated with this step."""
        return self._contract_keys

    @property
    def allow_list_aggregation(self) -> bool:
        """Return whether list-style dependency aggregation is allowed here."""
        return self._allow_list_aggregation

    @property
    def uses_positional_override(self) -> bool:
        """Return whether this step expects positional override payloads."""
        return self._uses_positional_override

    @property
    def contract_payload(self) -> Optional[Dict[str, Any]]:
        """Return the pre-normalized contract payload for this step, if any."""
        return self._contract_payload

    @property
    def contract_positional_override(self) -> Optional[Any]:
        """
        Return the pre-split positional override value, if present.
        """
        return self._contract_positional_override

    @property
    def has_contract_payload(self) -> bool:
        """
        Return True when a contract payload is present for this step.
        """
        return self._has_contract_payload

    @property
    def lock_hint(self) -> str:
        """Return the runtime lock strategy hint for this step."""
        return self._lock_hint

    @property
    def use_spell_lock_hint(self) -> bool:
        """Return whether the runtime should prefer the spell lock for this step."""
        return self._use_spell_lock_hint

    @property
    def requires_spellspace(self) -> bool:
        """Return whether this step requires an active spellspace context."""
        return self._requires_spellspace

    @property
    def owner_conduit_required(self) -> bool:
        """Return whether owner-conduit access is required for this step."""
        return self._owner_conduit_required

    @property
    def must_register(self) -> bool:
        """Return whether the created/reused result must be registered."""
        return self._must_register

    @property
    def disposal_method_names(self) -> List[str]:
        """Return disposal-method names carried into runtime registration."""
        return self._disposal_method_names


class ExecutionPlan(Cleanable):
    """
    Internal

    Phase 11 artifact that captures execution plan metadata.

    This plan can optionally carry a compact, array-style fast path for
    no-override execution to minimize runtime overhead.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_root_instance_key",
        "_steps",
        "_spell_id_step_index",
        "_optimistic_object_refs_by_spell_id",
        "_available_param_by_spell_id",
        "_plan_variant",
        "_fast_dep_indices",
        "_fast_param_group_names",
        "_fast_param_group_dep_offsets",
        "_fast_param_group_dep_counts",
        "_fast_param_group_offsets",
        "_fast_param_group_counts",
        "_fast_use_positional",
        "_fast_contract_payload_items",
        "_fast_contract_positional_args",
        "_fast_instance_keys",
        "_fast_creations_target_kinds",
        "_fast_existence",
        "_fast_must_register",
        "_fast_set_result_flags",
        "_fast_spells",
        "_fast_call_targets",
        "_fast_existing_objects",
        "_fast_is_existing_creation",
        "_fast_is_callable",
        "_fast_root_step_index",
        "_fast_call_modes",
        "_fast_single_dep_indices",
        "_fast_call2_dep_indices_a",
        "_fast_call2_dep_indices_b",
        "_fast_call3_dep_indices_a",
        "_fast_call3_dep_indices_b",
        "_fast_call3_dep_indices_c",
        "_fast_call4_dep_indices_a",
        "_fast_call4_dep_indices_b",
        "_fast_call4_dep_indices_c",
        "_fast_call4_dep_indices_d",
        "_fast_call5_dep_indices_a",
        "_fast_call5_dep_indices_b",
        "_fast_call5_dep_indices_c",
        "_fast_call5_dep_indices_d",
        "_fast_call5_dep_indices_e",
        "_fast_call6_dep_indices_a",
        "_fast_call6_dep_indices_b",
        "_fast_call6_dep_indices_c",
        "_fast_call6_dep_indices_d",
        "_fast_call6_dep_indices_e",
        "_fast_call6_dep_indices_f",
        "_fast_call7_dep_indices_a",
        "_fast_call7_dep_indices_b",
        "_fast_call7_dep_indices_c",
        "_fast_call7_dep_indices_d",
        "_fast_call7_dep_indices_e",
        "_fast_call7_dep_indices_f",
        "_fast_call7_dep_indices_g",
        "_fast_call8_dep_indices_a",
        "_fast_call8_dep_indices_b",
        "_fast_call8_dep_indices_c",
        "_fast_call8_dep_indices_d",
        "_fast_call8_dep_indices_e",
        "_fast_call8_dep_indices_f",
        "_fast_call8_dep_indices_g",
        "_fast_call8_dep_indices_h",
        "_fast_transient_plan",
        "_fast_has_contract_payloads",
        "_fast_has_existing_creations",
    ]

    _cleaned: bool

    def __init__(
            self,
            *,
            root_spell_id: str,
            root_instance_key: InstanceKey,
            steps: List[ExecutionPlanStep],
            spell_id_step_index: Dict[str, int],
            optimistic_object_refs_by_spell_id: Dict[str, Any],
            available_param_by_spell_id: Dict[str, int],
            plan_variant: str,
            fast_dep_indices: Optional[List[int]] = None,
            fast_param_group_names: Optional[List[str]] = None,
            fast_param_group_dep_offsets: Optional[List[int]] = None,
            fast_param_group_dep_counts: Optional[List[int]] = None,
            fast_param_group_offsets: Optional[List[int]] = None,
            fast_param_group_counts: Optional[List[int]] = None,
            fast_use_positional: Optional[List[bool]] = None,
            fast_contract_payload_items: Optional[List[Optional[List[Tuple[str, Any]]]]] = None,
            fast_contract_positional_args: Optional[List[Optional[Any]]] = None,
            fast_instance_keys: Optional[List[InstanceKey]] = None,
            fast_creations_target_kinds: Optional[List[int]] = None,
            fast_existence: Optional[List[Existence]] = None,
            fast_must_register: Optional[List[bool]] = None,
            fast_set_result_flags: Optional[List[bool]] = None,
            fast_spells: Optional[List[ISpell]] = None,
            fast_call_targets: Optional[List[Any]] = None,
            fast_existing_objects: Optional[List[Any]] = None,
            fast_is_existing_creation: Optional[List[bool]] = None,
            fast_is_callable: Optional[List[bool]] = None,
            fast_root_step_index: Optional[int] = None,
            fast_call_modes: Optional[List[int]] = None,
            fast_single_dep_indices: Optional[List[int]] = None,
            fast_call2_dep_indices_a: Optional[List[int]] = None,
            fast_call2_dep_indices_b: Optional[List[int]] = None,
            fast_call3_dep_indices_a: Optional[List[int]] = None,
            fast_call3_dep_indices_b: Optional[List[int]] = None,
            fast_call3_dep_indices_c: Optional[List[int]] = None,
            fast_call4_dep_indices_a: Optional[List[int]] = None,
            fast_call4_dep_indices_b: Optional[List[int]] = None,
            fast_call4_dep_indices_c: Optional[List[int]] = None,
            fast_call4_dep_indices_d: Optional[List[int]] = None,
            fast_call5_dep_indices_a: Optional[List[int]] = None,
            fast_call5_dep_indices_b: Optional[List[int]] = None,
            fast_call5_dep_indices_c: Optional[List[int]] = None,
            fast_call5_dep_indices_d: Optional[List[int]] = None,
            fast_call5_dep_indices_e: Optional[List[int]] = None,
            fast_call6_dep_indices_a: Optional[List[int]] = None,
            fast_call6_dep_indices_b: Optional[List[int]] = None,
            fast_call6_dep_indices_c: Optional[List[int]] = None,
            fast_call6_dep_indices_d: Optional[List[int]] = None,
            fast_call6_dep_indices_e: Optional[List[int]] = None,
            fast_call6_dep_indices_f: Optional[List[int]] = None,
            fast_call7_dep_indices_a: Optional[List[int]] = None,
            fast_call7_dep_indices_b: Optional[List[int]] = None,
            fast_call7_dep_indices_c: Optional[List[int]] = None,
            fast_call7_dep_indices_d: Optional[List[int]] = None,
            fast_call7_dep_indices_e: Optional[List[int]] = None,
            fast_call7_dep_indices_f: Optional[List[int]] = None,
            fast_call7_dep_indices_g: Optional[List[int]] = None,
            fast_call8_dep_indices_a: Optional[List[int]] = None,
            fast_call8_dep_indices_b: Optional[List[int]] = None,
            fast_call8_dep_indices_c: Optional[List[int]] = None,
            fast_call8_dep_indices_d: Optional[List[int]] = None,
            fast_call8_dep_indices_e: Optional[List[int]] = None,
            fast_call8_dep_indices_f: Optional[List[int]] = None,
            fast_call8_dep_indices_g: Optional[List[int]] = None,
            fast_call8_dep_indices_h: Optional[List[int]] = None,
            fast_transient_plan: Optional[FastTransientPlan] = None,
            fast_has_contract_payloads: Optional[bool] = None,
            fast_has_existing_creations: Optional[bool] = None,
    ) -> None:
        """
        Initialize a Phase 11 execution plan.

        Contract:
            - Stores plan metadata and precompiled steps by reference.
            - Optional fast-path arrays are aligned to `steps` order when provided.
            - Fast-path arrays are only used for no-override execution.

        Args:
            root_spell_id: Root spell id for the plan.
            root_instance_key: Instance key for the root occurrence.
            steps: Ordered plan steps.
            spell_id_step_index: First step index per spell id.
            optimistic_object_refs_by_spell_id: Pre-known objects per spell id.
            available_param_by_spell_id: Precomputed creations target per spell id.
            plan_variant: Plan variant identifier.
            fast_dep_indices: Flattened dependency step indices (fast path).
            fast_param_group_names: Parameter names for dependency groups (fast path).
            fast_param_group_dep_offsets: Dependency offset per group (fast path).
            fast_param_group_dep_counts: Dependency count per group (fast path).
            fast_param_group_offsets: Group offset per step (fast path).
            fast_param_group_counts: Group count per step (fast path).
            fast_use_positional: Positional-arg eligibility per step (fast path).
            fast_contract_payload_items: Pre-split contract payload items per step (fast path).
            fast_contract_positional_args: Pre-split contract positional args per step (fast path).
            fast_instance_keys: Instance keys aligned to steps (fast path).
            fast_creations_target_kinds: Creations routing kind per step (fast path).
            fast_existence: Existence policy per step (fast path).
            fast_must_register: Registration flag per step (fast path).
            fast_set_result_flags: First-result flags per spell id (fast path).
            fast_spells: Spell objects aligned to steps (fast path).
            fast_call_targets: Spell call targets aligned to steps (fast path).
            fast_existing_objects: Existing objects aligned to steps (fast path).
            fast_is_existing_creation: Existing-creation flags per step (fast path).
            fast_is_callable: Callable-spell flags per step (fast path).
            fast_root_step_index: Root instance index within the fast arrays (fast path).
            fast_call_modes: Call-mode selector per step (fast path).
            fast_single_dep_indices: Single dependency index per step (fast path).
            fast_call2_dep_indices_a: First dependency index for CALL2 steps (fast path).
            fast_call2_dep_indices_b: Second dependency index for CALL2 steps (fast path).
            fast_call3_dep_indices_a: First dependency index for CALL3 steps (fast path).
            fast_call3_dep_indices_b: Second dependency index for CALL3 steps (fast path).
            fast_call3_dep_indices_c: Third dependency index for CALL3 steps (fast path).
            fast_call4_dep_indices_a: First dependency index for CALL4 steps (fast path).
            fast_call4_dep_indices_b: Second dependency index for CALL4 steps (fast path).
            fast_call4_dep_indices_c: Third dependency index for CALL4 steps (fast path).
            fast_call4_dep_indices_d: Fourth dependency index for CALL4 steps (fast path).
            fast_call5_dep_indices_a: First dependency index for CALL5 steps (fast path).
            fast_call5_dep_indices_b: Second dependency index for CALL5 steps (fast path).
            fast_call5_dep_indices_c: Third dependency index for CALL5 steps (fast path).
            fast_call5_dep_indices_d: Fourth dependency index for CALL5 steps (fast path).
            fast_call5_dep_indices_e: Fifth dependency index for CALL5 steps (fast path).
            fast_call6_dep_indices_a: First dependency index for CALL6 steps (fast path).
            fast_call6_dep_indices_b: Second dependency index for CALL6 steps (fast path).
            fast_call6_dep_indices_c: Third dependency index for CALL6 steps (fast path).
            fast_call6_dep_indices_d: Fourth dependency index for CALL6 steps (fast path).
            fast_call6_dep_indices_e: Fifth dependency index for CALL6 steps (fast path).
            fast_call6_dep_indices_f: Sixth dependency index for CALL6 steps (fast path).
            fast_call7_dep_indices_a: First dependency index for CALL7 steps (fast path).
            fast_call7_dep_indices_b: Second dependency index for CALL7 steps (fast path).
            fast_call7_dep_indices_c: Third dependency index for CALL7 steps (fast path).
            fast_call7_dep_indices_d: Fourth dependency index for CALL7 steps (fast path).
            fast_call7_dep_indices_e: Fifth dependency index for CALL7 steps (fast path).
            fast_call7_dep_indices_f: Sixth dependency index for CALL7 steps (fast path).
            fast_call7_dep_indices_g: Seventh dependency index for CALL7 steps (fast path).
            fast_call8_dep_indices_a: First dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_b: Second dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_c: Third dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_d: Fourth dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_e: Fifth dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_f: Sixth dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_g: Seventh dependency index for CALL8 steps (fast path).
            fast_call8_dep_indices_h: Eighth dependency index for CALL8 steps (fast path).
            fast_transient_plan: Specialized plan for transient-only fast execution.
            fast_has_contract_payloads: True when any fast step has contract payloads.
            fast_has_existing_creations: True when any fast step is an existing-creation.

        Contract:
            - The plan owns its step list, index maps, and optional fast-path
              arrays after construction.
            - Optional fast-path arrays are only meaningful for the
              `NO_OVERRIDES_FAST` variant and are expected to stay aligned to
              `steps`.
        """
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if root_instance_key is None:
            raise ValueError("root_instance_key must not be None.")
        if steps is None:
            raise ValueError("steps must not be None.")
        if spell_id_step_index is None:
            raise ValueError("spell_id_step_index must not be None.")
        if optimistic_object_refs_by_spell_id is None:
            raise ValueError("optimistic_object_refs_by_spell_id must not be None.")
        if available_param_by_spell_id is None:
            raise ValueError("available_param_by_spell_id must not be None.")
        if plan_variant is None:
            raise ValueError("plan_variant must not be None.")

        self._root_spell_id = root_spell_id
        self._root_instance_key = root_instance_key
        self._steps = steps
        self._spell_id_step_index = spell_id_step_index
        self._optimistic_object_refs_by_spell_id = optimistic_object_refs_by_spell_id
        self._available_param_by_spell_id = available_param_by_spell_id
        self._plan_variant = plan_variant
        self._fast_dep_indices = fast_dep_indices
        self._fast_param_group_names = fast_param_group_names
        self._fast_param_group_dep_offsets = fast_param_group_dep_offsets
        self._fast_param_group_dep_counts = fast_param_group_dep_counts
        self._fast_param_group_offsets = fast_param_group_offsets
        self._fast_param_group_counts = fast_param_group_counts
        self._fast_use_positional = fast_use_positional
        self._fast_contract_payload_items = fast_contract_payload_items
        self._fast_contract_positional_args = fast_contract_positional_args
        self._fast_instance_keys = fast_instance_keys
        self._fast_creations_target_kinds = fast_creations_target_kinds
        self._fast_existence = fast_existence
        self._fast_must_register = fast_must_register
        self._fast_set_result_flags = fast_set_result_flags
        self._fast_spells = fast_spells
        self._fast_call_targets = fast_call_targets
        self._fast_existing_objects = fast_existing_objects
        self._fast_is_existing_creation = fast_is_existing_creation
        self._fast_is_callable = fast_is_callable
        self._fast_root_step_index = fast_root_step_index
        self._fast_call_modes = fast_call_modes
        self._fast_single_dep_indices = fast_single_dep_indices
        self._fast_call2_dep_indices_a = fast_call2_dep_indices_a
        self._fast_call2_dep_indices_b = fast_call2_dep_indices_b
        self._fast_call3_dep_indices_a = fast_call3_dep_indices_a
        self._fast_call3_dep_indices_b = fast_call3_dep_indices_b
        self._fast_call3_dep_indices_c = fast_call3_dep_indices_c
        self._fast_call4_dep_indices_a = fast_call4_dep_indices_a
        self._fast_call4_dep_indices_b = fast_call4_dep_indices_b
        self._fast_call4_dep_indices_c = fast_call4_dep_indices_c
        self._fast_call4_dep_indices_d = fast_call4_dep_indices_d
        self._fast_call5_dep_indices_a = fast_call5_dep_indices_a
        self._fast_call5_dep_indices_b = fast_call5_dep_indices_b
        self._fast_call5_dep_indices_c = fast_call5_dep_indices_c
        self._fast_call5_dep_indices_d = fast_call5_dep_indices_d
        self._fast_call5_dep_indices_e = fast_call5_dep_indices_e
        self._fast_call6_dep_indices_a = fast_call6_dep_indices_a
        self._fast_call6_dep_indices_b = fast_call6_dep_indices_b
        self._fast_call6_dep_indices_c = fast_call6_dep_indices_c
        self._fast_call6_dep_indices_d = fast_call6_dep_indices_d
        self._fast_call6_dep_indices_e = fast_call6_dep_indices_e
        self._fast_call6_dep_indices_f = fast_call6_dep_indices_f
        self._fast_call7_dep_indices_a = fast_call7_dep_indices_a
        self._fast_call7_dep_indices_b = fast_call7_dep_indices_b
        self._fast_call7_dep_indices_c = fast_call7_dep_indices_c
        self._fast_call7_dep_indices_d = fast_call7_dep_indices_d
        self._fast_call7_dep_indices_e = fast_call7_dep_indices_e
        self._fast_call7_dep_indices_f = fast_call7_dep_indices_f
        self._fast_call7_dep_indices_g = fast_call7_dep_indices_g
        self._fast_call8_dep_indices_a = fast_call8_dep_indices_a
        self._fast_call8_dep_indices_b = fast_call8_dep_indices_b
        self._fast_call8_dep_indices_c = fast_call8_dep_indices_c
        self._fast_call8_dep_indices_d = fast_call8_dep_indices_d
        self._fast_call8_dep_indices_e = fast_call8_dep_indices_e
        self._fast_call8_dep_indices_f = fast_call8_dep_indices_f
        self._fast_call8_dep_indices_g = fast_call8_dep_indices_g
        self._fast_call8_dep_indices_h = fast_call8_dep_indices_h
        self._fast_transient_plan = fast_transient_plan
        self._fast_has_contract_payloads = fast_has_contract_payloads
        self._fast_has_existing_creations = fast_has_existing_creations

    def cleanup(self) -> None:
        """
        Deterministically clear the execution plan and owned collections.

        Contract:
            - Idempotent and safe to call multiple times.
            - Clears all lists/maps and nulls references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._steps.clear()
        self._spell_id_step_index.clear()
        self._optimistic_object_refs_by_spell_id.clear()
        self._available_param_by_spell_id.clear()
        if self._fast_dep_indices is not None:
            self._fast_dep_indices.clear()
        if self._fast_param_group_names is not None:
            self._fast_param_group_names.clear()
        if self._fast_param_group_dep_offsets is not None:
            self._fast_param_group_dep_offsets.clear()
        if self._fast_param_group_dep_counts is not None:
            self._fast_param_group_dep_counts.clear()
        if self._fast_param_group_offsets is not None:
            self._fast_param_group_offsets.clear()
        if self._fast_param_group_counts is not None:
            self._fast_param_group_counts.clear()
        if self._fast_use_positional is not None:
            self._fast_use_positional.clear()
        if self._fast_contract_payload_items is not None:
            self._fast_contract_payload_items.clear()
        if self._fast_contract_positional_args is not None:
            self._fast_contract_positional_args.clear()
        if self._fast_instance_keys is not None:
            self._fast_instance_keys.clear()
        if self._fast_creations_target_kinds is not None:
            self._fast_creations_target_kinds.clear()
        if self._fast_existence is not None:
            self._fast_existence.clear()
        if self._fast_must_register is not None:
            self._fast_must_register.clear()
        if self._fast_set_result_flags is not None:
            self._fast_set_result_flags.clear()
        if self._fast_spells is not None:
            self._fast_spells.clear()
        if self._fast_call_targets is not None:
            self._fast_call_targets.clear()
        if self._fast_existing_objects is not None:
            self._fast_existing_objects.clear()
        if self._fast_is_existing_creation is not None:
            self._fast_is_existing_creation.clear()
        if self._fast_is_callable is not None:
            self._fast_is_callable.clear()
        if self._fast_call_modes is not None:
            self._fast_call_modes.clear()
        if self._fast_single_dep_indices is not None:
            self._fast_single_dep_indices.clear()
        if self._fast_call2_dep_indices_a is not None:
            self._fast_call2_dep_indices_a.clear()
        if self._fast_call2_dep_indices_b is not None:
            self._fast_call2_dep_indices_b.clear()
        if self._fast_call3_dep_indices_a is not None:
            self._fast_call3_dep_indices_a.clear()
        if self._fast_call3_dep_indices_b is not None:
            self._fast_call3_dep_indices_b.clear()
        if self._fast_call3_dep_indices_c is not None:
            self._fast_call3_dep_indices_c.clear()
        if self._fast_call4_dep_indices_a is not None:
            self._fast_call4_dep_indices_a.clear()
        if self._fast_call4_dep_indices_b is not None:
            self._fast_call4_dep_indices_b.clear()
        if self._fast_call4_dep_indices_c is not None:
            self._fast_call4_dep_indices_c.clear()
        if self._fast_call4_dep_indices_d is not None:
            self._fast_call4_dep_indices_d.clear()
        if self._fast_call5_dep_indices_a is not None:
            self._fast_call5_dep_indices_a.clear()
        if self._fast_call5_dep_indices_b is not None:
            self._fast_call5_dep_indices_b.clear()
        if self._fast_call5_dep_indices_c is not None:
            self._fast_call5_dep_indices_c.clear()
        if self._fast_call5_dep_indices_d is not None:
            self._fast_call5_dep_indices_d.clear()
        if self._fast_call5_dep_indices_e is not None:
            self._fast_call5_dep_indices_e.clear()
        if self._fast_call6_dep_indices_a is not None:
            self._fast_call6_dep_indices_a.clear()
        if self._fast_call6_dep_indices_b is not None:
            self._fast_call6_dep_indices_b.clear()
        if self._fast_call6_dep_indices_c is not None:
            self._fast_call6_dep_indices_c.clear()
        if self._fast_call6_dep_indices_d is not None:
            self._fast_call6_dep_indices_d.clear()
        if self._fast_call6_dep_indices_e is not None:
            self._fast_call6_dep_indices_e.clear()
        if self._fast_call6_dep_indices_f is not None:
            self._fast_call6_dep_indices_f.clear()
        if self._fast_call7_dep_indices_a is not None:
            self._fast_call7_dep_indices_a.clear()
        if self._fast_call7_dep_indices_b is not None:
            self._fast_call7_dep_indices_b.clear()
        if self._fast_call7_dep_indices_c is not None:
            self._fast_call7_dep_indices_c.clear()
        if self._fast_call7_dep_indices_d is not None:
            self._fast_call7_dep_indices_d.clear()
        if self._fast_call7_dep_indices_e is not None:
            self._fast_call7_dep_indices_e.clear()
        if self._fast_call7_dep_indices_f is not None:
            self._fast_call7_dep_indices_f.clear()
        if self._fast_call7_dep_indices_g is not None:
            self._fast_call7_dep_indices_g.clear()
        if self._fast_call8_dep_indices_a is not None:
            self._fast_call8_dep_indices_a.clear()
        if self._fast_call8_dep_indices_b is not None:
            self._fast_call8_dep_indices_b.clear()
        if self._fast_call8_dep_indices_c is not None:
            self._fast_call8_dep_indices_c.clear()
        if self._fast_call8_dep_indices_d is not None:
            self._fast_call8_dep_indices_d.clear()
        if self._fast_call8_dep_indices_e is not None:
            self._fast_call8_dep_indices_e.clear()
        if self._fast_call8_dep_indices_f is not None:
            self._fast_call8_dep_indices_f.clear()
        if self._fast_call8_dep_indices_g is not None:
            self._fast_call8_dep_indices_g.clear()
        if self._fast_call8_dep_indices_h is not None:
            self._fast_call8_dep_indices_h.clear()
        if self._fast_transient_plan is not None:
            for plan_list in self._fast_transient_plan[2:]:
                if isinstance(plan_list, list):
                    plan_list.clear()

        del self._root_spell_id
        del self._root_instance_key
        del self._steps
        del self._spell_id_step_index
        del self._optimistic_object_refs_by_spell_id
        del self._available_param_by_spell_id
        del self._plan_variant
        del self._fast_dep_indices
        del self._fast_param_group_names
        del self._fast_param_group_dep_offsets
        del self._fast_param_group_dep_counts
        del self._fast_param_group_offsets
        del self._fast_param_group_counts
        del self._fast_use_positional
        del self._fast_contract_payload_items
        del self._fast_contract_positional_args
        del self._fast_instance_keys
        del self._fast_creations_target_kinds
        del self._fast_existence
        del self._fast_must_register
        del self._fast_set_result_flags
        del self._fast_spells
        del self._fast_call_targets
        del self._fast_existing_objects
        del self._fast_is_existing_creation
        del self._fast_is_callable
        del self._fast_root_step_index
        del self._fast_call_modes
        del self._fast_single_dep_indices
        del self._fast_call2_dep_indices_a
        del self._fast_call2_dep_indices_b
        del self._fast_call3_dep_indices_a
        del self._fast_call3_dep_indices_b
        del self._fast_call3_dep_indices_c
        del self._fast_call4_dep_indices_a
        del self._fast_call4_dep_indices_b
        del self._fast_call4_dep_indices_c
        del self._fast_call4_dep_indices_d
        del self._fast_call5_dep_indices_a
        del self._fast_call5_dep_indices_b
        del self._fast_call5_dep_indices_c
        del self._fast_call5_dep_indices_d
        del self._fast_call5_dep_indices_e
        del self._fast_call6_dep_indices_a
        del self._fast_call6_dep_indices_b
        del self._fast_call6_dep_indices_c
        del self._fast_call6_dep_indices_d
        del self._fast_call6_dep_indices_e
        del self._fast_call6_dep_indices_f
        del self._fast_call7_dep_indices_a
        del self._fast_call7_dep_indices_b
        del self._fast_call7_dep_indices_c
        del self._fast_call7_dep_indices_d
        del self._fast_call7_dep_indices_e
        del self._fast_call7_dep_indices_f
        del self._fast_call7_dep_indices_g
        del self._fast_call8_dep_indices_a
        del self._fast_call8_dep_indices_b
        del self._fast_call8_dep_indices_c
        del self._fast_call8_dep_indices_d
        del self._fast_call8_dep_indices_e
        del self._fast_call8_dep_indices_f
        del self._fast_call8_dep_indices_g
        del self._fast_call8_dep_indices_h
        del self._fast_transient_plan
        del self._fast_has_contract_payloads
        del self._fast_has_existing_creations

    @property
    def root_spell_id(self) -> str:
        """Return the root spell id this execution plan was compiled for."""
        return self._root_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        """Return the root occurrence's instance key for result lookup."""
        return self._root_instance_key

    @property
    def steps(self) -> List[ExecutionPlanStep]:
        """Return the ordered execution steps owned by this plan."""
        return self._steps

    @property
    def spell_id_step_index(self) -> Dict[str, int]:
        """Return the first step index for each spell id in the plan."""
        return self._spell_id_step_index

    @property
    def optimistic_object_refs_by_spell_id(self) -> Dict[str, Any]:
        """Return pre-known optimistic object refs keyed by spell id."""
        return self._optimistic_object_refs_by_spell_id

    @property
    def available_param_by_spell_id(self) -> Dict[str, int]:
        """Return precomputed creations-target routing keyed by spell id."""
        return self._available_param_by_spell_id

    @property
    def plan_variant(self) -> str:
        """Return which Phase 11 variant this plan represents."""
        return self._plan_variant

    @property
    def fast_plan(
            self,
    ) -> Optional[FastPlanData]:
        """
        Return precompiled fast-path arrays for no-override execution.

        Contract:
            - Returns None when no fast-path data is available.
            - Arrays are aligned to `steps` order.
            - Includes instance keys, routing metadata, and construct metadata
              for direct execution.
            - Includes the root step index for fast-path result lookup.
            - Includes call-mode metadata and single-dependency indices for
              trivial call shapes.
            - Includes direct dependency indices for CALL2–CALL8 steps.
        """
        if self._fast_dep_indices is None:
            return None
        return (
            self._fast_dep_indices,
            self._fast_param_group_names,
            self._fast_param_group_dep_offsets,
            self._fast_param_group_dep_counts,
            self._fast_param_group_offsets,
            self._fast_param_group_counts,
            self._fast_use_positional,
            self._fast_contract_payload_items,
            self._fast_contract_positional_args,
            self._fast_instance_keys,
            self._fast_creations_target_kinds,
            self._fast_existence,
            self._fast_must_register,
            self._fast_set_result_flags,
            self._fast_spells,
            self._fast_call_targets,
            self._fast_existing_objects,
            self._fast_is_existing_creation,
            self._fast_is_callable,
            self._fast_root_step_index,
            self._fast_call_modes,
            self._fast_single_dep_indices,
            self._fast_call2_dep_indices_a,
            self._fast_call2_dep_indices_b,
            self._fast_call3_dep_indices_a,
            self._fast_call3_dep_indices_b,
            self._fast_call3_dep_indices_c,
            self._fast_call4_dep_indices_a,
            self._fast_call4_dep_indices_b,
            self._fast_call4_dep_indices_c,
            self._fast_call4_dep_indices_d,
            self._fast_call5_dep_indices_a,
            self._fast_call5_dep_indices_b,
            self._fast_call5_dep_indices_c,
            self._fast_call5_dep_indices_d,
            self._fast_call5_dep_indices_e,
            self._fast_call6_dep_indices_a,
            self._fast_call6_dep_indices_b,
            self._fast_call6_dep_indices_c,
            self._fast_call6_dep_indices_d,
            self._fast_call6_dep_indices_e,
            self._fast_call6_dep_indices_f,
            self._fast_call7_dep_indices_a,
            self._fast_call7_dep_indices_b,
            self._fast_call7_dep_indices_c,
            self._fast_call7_dep_indices_d,
            self._fast_call7_dep_indices_e,
            self._fast_call7_dep_indices_f,
            self._fast_call7_dep_indices_g,
            self._fast_call8_dep_indices_a,
            self._fast_call8_dep_indices_b,
            self._fast_call8_dep_indices_c,
            self._fast_call8_dep_indices_d,
            self._fast_call8_dep_indices_e,
            self._fast_call8_dep_indices_f,
            self._fast_call8_dep_indices_g,
            self._fast_call8_dep_indices_h,
        )

    @property
    def fast_transient_plan(
            self,
    ) -> Optional[FastTransientPlan]:
        """
        Return a specialized transient-only plan for the no-overrides path.

        Contract:
            - Returns None when no transient-only plan is available.
            - Only valid when all steps are Existence.many, callable, and require no registration.
        """
        return self._fast_transient_plan

    @property
    def fast_has_contract_payloads(self) -> bool:
        """
        Return True when any fast-path step carries contract payloads.
        """
        return bool(self._fast_has_contract_payloads)

    @property
    def fast_has_existing_creations(self) -> bool:
        """
        Return True when any fast-path step is an existing-creation.
        """
        return bool(self._fast_has_existing_creations)


class ExecutionPlanBuilder:
    """
    Internal

    Build a Phase 11 ExecutionPlan from Phase 8/9 artifacts.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_occurrence_plan",
        "_injection_plan",
        "_spell_lookup",
        "_plan_variant",
    ]

    def __init__(
            self,
            *,
            occurrence_plan: OccurrencePlan,
            injection_plan: Optional[InjectionPlan],
            spell_lookup: Dict[str, ISpell],
            plan_variant: str,
    ) -> None:
        """
        Initialize the Phase 11 execution-plan builder.

        Contract:
            - Stores references to the Phase 8/9 inputs without copying them.
            - Assumes callers have already selected a compatible plan variant.
            - Treats the supplied occurrence and injection plans as read-only.
        """
        if occurrence_plan is None:
            raise ValueError("occurrence_plan must not be None.")
        if spell_lookup is None:
            raise ValueError("spell_lookup must not be None.")
        if plan_variant is None:
            raise ValueError("plan_variant must not be None.")

        self._occurrence_plan = occurrence_plan
        self._injection_plan = injection_plan
        self._spell_lookup = spell_lookup
        self._plan_variant = plan_variant

    def build(self) -> ExecutionPlan:
        """
        Build a Phase 11 ExecutionPlan from Phase 8/9 artifacts.

        Contract:
            - Produces ordered steps aligned to the occurrence plan.
            - For NO_OVERRIDES_FAST, also compiles fast-path arrays.
            - Does not mutate the input plans.

        Returns:
            ExecutionPlan: Compiled Phase 11 execution plan.

        Raises:
            ValueError: If required plan roots are missing or mismatched.
        """
        root_spell_id = self._occurrence_plan.root_spell_id
        injection_lookup: Optional[Dict[InstanceKey, InjectionSpec]] = None
        if self._injection_plan is not None:
            injection_lookup = self._injection_plan.select_for_runtime(
                root_spell_id=root_spell_id,
            )
            if injection_lookup is None:
                raise ValueError(
                    "Phase 11 ExecutionPlan: injection plan root mismatch or cleaned plan."
                )

        steps: List[ExecutionPlanStep] = []
        spell_id_step_index: Dict[str, int] = {}
        optimistic_refs: Dict[str, Any] = {}
        available_param_by_spell_id: Dict[str, int] = {}
        instance_key_to_step_index: Dict[InstanceKey, int] = {}
        path_registry = self._occurrence_plan.path_registry

        for spell_id in self._occurrence_plan.execution_order:
            spell = self._spell_lookup.get(spell_id)
            if spell is None:
                raise ValueError(
                    f"Phase 11 ExecutionPlan: spell id '{spell_id}' missing from lookup."
                )

            if spell.user_created_object is not None:
                optimistic_refs[spell_id] = spell.user_created_object

            existence = spell.existence
            creations_target_kind = self._creation_target_for_existence(existence)
            available_param_by_spell_id[spell_id] = creations_target_kind
            shared_instance = spell_id in self._occurrence_plan.shared_spell_ids
            lock_hint = self._lock_hint_for_existence(existence)
            requires_spellspace = existence is Existence.unique_per_spell_space
            owner_conduit_required = existence is Existence.unique_per_spell_space
            must_register = self._should_register(spell)
            disposal_method_names = list(spell.disposal_method_names) if spell.has_disposal_methods else []
            strip_override_metadata = (
                self._plan_variant == ExecutionPlanVariant.NO_OVERRIDES_FAST
            )

            for instance_key in self._occurrence_plan.instance_keys_by_spell_id.get(spell_id, []):
                occurrence = self._occurrence_for_instance_key(instance_key)
                inject_spec = injection_lookup.get(instance_key) if injection_lookup else None
                if strip_override_metadata:
                    dependency_keys, dependency_keys_by_param = (
                        self._extract_param_keys_no_overrides(inject_spec)
                    )
                    override_keys: list[str] = []
                    contract_keys: list[str] = []
                    expects_overrides = False
                    override_match_prefix = None
                    override_match_prefix_len = 0
                else:
                    dependency_keys, dependency_keys_by_param, override_keys, contract_keys = (
                        self._extract_param_keys(inject_spec)
                    )
                    expects_overrides = bool(override_keys)
                    override_match_prefix = occurrence[1]
                    override_match_prefix_len = (
                        path_registry.depth(override_match_prefix)
                        if override_match_prefix is not None
                        else 0
                    )
                dependency_resolution_order = list(dependency_keys_by_param.items())
                allow_list_aggregation = inject_spec.allow_list_aggregation if inject_spec else False
                uses_positional_override = inject_spec.uses_positional_override if inject_spec else False
                contract_payload = inject_spec.contract_payload if inject_spec else None
                contract_positional_override = None
                if (
                        uses_positional_override
                        and contract_payload is not None
                        and "__args__" in contract_payload
                ):
                    contract_positional_override = contract_payload["__args__"]
                has_contract_payload = bool(contract_payload)

                step = ExecutionPlanStep(
                    instance_key=instance_key,
                    occurrence=occurrence,
                    spell=spell,
                    existence=existence,
                    creations_target_kind=creations_target_kind,
                    shared_instance=shared_instance,
                    inject_spec=inject_spec,
                    dependency_keys=dependency_keys,
                    dependency_keys_by_param=dependency_keys_by_param,
                    dependency_resolution_order=dependency_resolution_order,
                    override_keys=override_keys,
                    override_match_prefix=override_match_prefix,
                    override_match_prefix_len=override_match_prefix_len,
                    expects_overrides=expects_overrides,
                    contract_keys=contract_keys,
                    allow_list_aggregation=allow_list_aggregation,
                    uses_positional_override=uses_positional_override,
                    contract_payload=contract_payload,
                    contract_positional_override=contract_positional_override,
                    has_contract_payload=has_contract_payload,
                    lock_hint=lock_hint,
                    use_spell_lock_hint=lock_hint == "spell_lock",
                    requires_spellspace=requires_spellspace,
                    owner_conduit_required=owner_conduit_required,
                    must_register=must_register,
                    disposal_method_names=disposal_method_names,
                )
                steps.append(step)
                instance_key_to_step_index[instance_key] = len(steps) - 1
                if spell_id not in spell_id_step_index:
                    spell_id_step_index[spell_id] = len(steps) - 1

        fast_plan_data = None
        fast_transient_plan = None
        fast_has_contract_payloads = None
        fast_has_existing_creations = None
        if self._plan_variant == ExecutionPlanVariant.NO_OVERRIDES_FAST:
            fast_plan_data = self._build_fast_plan_data(
                steps=steps,
                instance_key_to_step_index=instance_key_to_step_index,
                root_instance_key=self._occurrence_plan.root_instance_key,
            )
            if fast_plan_data is not None:
                fast_has_contract_payloads = any(fast_plan_data[7]) or any(fast_plan_data[8])
                fast_has_existing_creations = any(fast_plan_data[17])
                fast_transient_plan = self._build_fast_transient_plan(
                    steps=steps,
                    fast_call_targets=fast_plan_data[15],
                    fast_existence=fast_plan_data[11],
                    fast_must_register=fast_plan_data[12],
                    fast_is_existing_creation=fast_plan_data[17],
                    fast_is_callable=fast_plan_data[18],
                    fast_call_modes=fast_plan_data[20],
                    fast_single_dep_indices=fast_plan_data[21],
                    fast_call2_dep_indices_a=fast_plan_data[22],
                    fast_call2_dep_indices_b=fast_plan_data[23],
                    fast_call3_dep_indices_a=fast_plan_data[24],
                    fast_call3_dep_indices_b=fast_plan_data[25],
                    fast_call3_dep_indices_c=fast_plan_data[26],
                    fast_call4_dep_indices_a=fast_plan_data[27],
                    fast_call4_dep_indices_b=fast_plan_data[28],
                    fast_call4_dep_indices_c=fast_plan_data[29],
                    fast_call4_dep_indices_d=fast_plan_data[30],
                    fast_call5_dep_indices_a=fast_plan_data[31],
                    fast_call5_dep_indices_b=fast_plan_data[32],
                    fast_call5_dep_indices_c=fast_plan_data[33],
                    fast_call5_dep_indices_d=fast_plan_data[34],
                    fast_call5_dep_indices_e=fast_plan_data[35],
                    fast_call6_dep_indices_a=fast_plan_data[36],
                    fast_call6_dep_indices_b=fast_plan_data[37],
                    fast_call6_dep_indices_c=fast_plan_data[38],
                    fast_call6_dep_indices_d=fast_plan_data[39],
                    fast_call6_dep_indices_e=fast_plan_data[40],
                    fast_call6_dep_indices_f=fast_plan_data[41],
                    fast_call7_dep_indices_a=fast_plan_data[42],
                    fast_call7_dep_indices_b=fast_plan_data[43],
                    fast_call7_dep_indices_c=fast_plan_data[44],
                    fast_call7_dep_indices_d=fast_plan_data[45],
                    fast_call7_dep_indices_e=fast_plan_data[46],
                    fast_call7_dep_indices_f=fast_plan_data[47],
                    fast_call7_dep_indices_g=fast_plan_data[48],
                    fast_call8_dep_indices_a=fast_plan_data[49],
                    fast_call8_dep_indices_b=fast_plan_data[50],
                    fast_call8_dep_indices_c=fast_plan_data[51],
                    fast_call8_dep_indices_d=fast_plan_data[52],
                    fast_call8_dep_indices_e=fast_plan_data[53],
                    fast_call8_dep_indices_f=fast_plan_data[54],
                    fast_call8_dep_indices_g=fast_plan_data[55],
                    fast_call8_dep_indices_h=fast_plan_data[56],
                    root_step_index=fast_plan_data[19],
                )

        return ExecutionPlan(
            root_spell_id=root_spell_id,
            root_instance_key=self._occurrence_plan.root_instance_key,
            steps=steps,
            spell_id_step_index=spell_id_step_index,
            optimistic_object_refs_by_spell_id=optimistic_refs,
            available_param_by_spell_id=available_param_by_spell_id,
            plan_variant=self._plan_variant,
            fast_dep_indices=fast_plan_data[0] if fast_plan_data else None,
            fast_param_group_names=fast_plan_data[1] if fast_plan_data else None,
            fast_param_group_dep_offsets=fast_plan_data[2] if fast_plan_data else None,
            fast_param_group_dep_counts=fast_plan_data[3] if fast_plan_data else None,
            fast_param_group_offsets=fast_plan_data[4] if fast_plan_data else None,
            fast_param_group_counts=fast_plan_data[5] if fast_plan_data else None,
            fast_use_positional=fast_plan_data[6] if fast_plan_data else None,
            fast_contract_payload_items=fast_plan_data[7] if fast_plan_data else None,
            fast_contract_positional_args=fast_plan_data[8] if fast_plan_data else None,
            fast_instance_keys=fast_plan_data[9] if fast_plan_data else None,
            fast_creations_target_kinds=fast_plan_data[10] if fast_plan_data else None,
            fast_existence=fast_plan_data[11] if fast_plan_data else None,
            fast_must_register=fast_plan_data[12] if fast_plan_data else None,
            fast_set_result_flags=fast_plan_data[13] if fast_plan_data else None,
            fast_spells=fast_plan_data[14] if fast_plan_data else None,
            fast_call_targets=fast_plan_data[15] if fast_plan_data else None,
            fast_existing_objects=fast_plan_data[16] if fast_plan_data else None,
            fast_is_existing_creation=fast_plan_data[17] if fast_plan_data else None,
            fast_is_callable=fast_plan_data[18] if fast_plan_data else None,
            fast_root_step_index=fast_plan_data[19] if fast_plan_data else None,
            fast_call_modes=fast_plan_data[20] if fast_plan_data else None,
            fast_single_dep_indices=fast_plan_data[21] if fast_plan_data else None,
            fast_call2_dep_indices_a=fast_plan_data[22] if fast_plan_data else None,
            fast_call2_dep_indices_b=fast_plan_data[23] if fast_plan_data else None,
            fast_call3_dep_indices_a=fast_plan_data[24] if fast_plan_data else None,
            fast_call3_dep_indices_b=fast_plan_data[25] if fast_plan_data else None,
            fast_call3_dep_indices_c=fast_plan_data[26] if fast_plan_data else None,
            fast_call4_dep_indices_a=fast_plan_data[27] if fast_plan_data else None,
            fast_call4_dep_indices_b=fast_plan_data[28] if fast_plan_data else None,
            fast_call4_dep_indices_c=fast_plan_data[29] if fast_plan_data else None,
            fast_call4_dep_indices_d=fast_plan_data[30] if fast_plan_data else None,
            fast_call5_dep_indices_a=fast_plan_data[31] if fast_plan_data else None,
            fast_call5_dep_indices_b=fast_plan_data[32] if fast_plan_data else None,
            fast_call5_dep_indices_c=fast_plan_data[33] if fast_plan_data else None,
            fast_call5_dep_indices_d=fast_plan_data[34] if fast_plan_data else None,
            fast_call5_dep_indices_e=fast_plan_data[35] if fast_plan_data else None,
            fast_call6_dep_indices_a=fast_plan_data[36] if fast_plan_data else None,
            fast_call6_dep_indices_b=fast_plan_data[37] if fast_plan_data else None,
            fast_call6_dep_indices_c=fast_plan_data[38] if fast_plan_data else None,
            fast_call6_dep_indices_d=fast_plan_data[39] if fast_plan_data else None,
            fast_call6_dep_indices_e=fast_plan_data[40] if fast_plan_data else None,
            fast_call6_dep_indices_f=fast_plan_data[41] if fast_plan_data else None,
            fast_call7_dep_indices_a=fast_plan_data[42] if fast_plan_data else None,
            fast_call7_dep_indices_b=fast_plan_data[43] if fast_plan_data else None,
            fast_call7_dep_indices_c=fast_plan_data[44] if fast_plan_data else None,
            fast_call7_dep_indices_d=fast_plan_data[45] if fast_plan_data else None,
            fast_call7_dep_indices_e=fast_plan_data[46] if fast_plan_data else None,
            fast_call7_dep_indices_f=fast_plan_data[47] if fast_plan_data else None,
            fast_call7_dep_indices_g=fast_plan_data[48] if fast_plan_data else None,
            fast_call8_dep_indices_a=fast_plan_data[49] if fast_plan_data else None,
            fast_call8_dep_indices_b=fast_plan_data[50] if fast_plan_data else None,
            fast_call8_dep_indices_c=fast_plan_data[51] if fast_plan_data else None,
            fast_call8_dep_indices_d=fast_plan_data[52] if fast_plan_data else None,
            fast_call8_dep_indices_e=fast_plan_data[53] if fast_plan_data else None,
            fast_call8_dep_indices_f=fast_plan_data[54] if fast_plan_data else None,
            fast_call8_dep_indices_g=fast_plan_data[55] if fast_plan_data else None,
            fast_call8_dep_indices_h=fast_plan_data[56] if fast_plan_data else None,
            fast_transient_plan=fast_transient_plan,
            fast_has_contract_payloads=fast_has_contract_payloads,
            fast_has_existing_creations=fast_has_existing_creations,
        )

    def _build_fast_plan_data(
            self,
            *,
            steps: List[ExecutionPlanStep],
            instance_key_to_step_index: Dict[InstanceKey, int],
            root_instance_key: InstanceKey,
    ) -> FastPlanData:
        """
        Build compact arrays for the no-override fast path.

        Contract:
            - Arrays are aligned to `steps` order.
            - Parameter group order follows Phase 1 parameter positions.
            - Uses positional args only when all DI parameters are positional-safe.
            - Contract payloads are applied via precomputed payload items.
            - Instance keys and creations routing metadata are precompiled per step.
            - First-result flags are precomputed to avoid runtime guard checks.
            - Construct metadata is precompiled to avoid runtime spell-type checks.
            - Root step index is precomputed for fast-path result retrieval.
            - Call modes precompute trivial 0/1-dependency call shapes.
        """
        step_count = len(steps)
        fast_dep_indices: List[int] = []
        fast_param_group_names: List[str] = []
        fast_param_group_dep_offsets: List[int] = []
        fast_param_group_dep_counts: List[int] = []
        fast_param_group_offsets: List[int] = [0] * step_count
        fast_param_group_counts: List[int] = [0] * step_count
        fast_use_positional: List[bool] = [False] * step_count
        fast_contract_payload_items: List[Optional[List[Tuple[str, Any]]]] = [None] * step_count
        fast_contract_positional_args: List[Optional[Any]] = [None] * step_count
        fast_instance_keys: List[InstanceKey] = [
            step.instance_key
            for step in steps
        ]
        fast_creations_target_kinds: List[int] = [0] * step_count
        fast_existence: List[Existence] = [
            step.existence
            for step in steps
        ]
        fast_must_register: List[bool] = [False] * step_count
        fast_set_result_flags: List[bool] = [False] * step_count
        fast_spells: List[ISpell] = [
            step.spell
            for step in steps
        ]
        fast_call_targets: List[Any] = [None] * step_count
        fast_existing_objects: List[Any] = [None] * step_count
        fast_is_existing_creation: List[bool] = [False] * step_count
        fast_is_callable: List[bool] = [False] * step_count
        root_step_index = instance_key_to_step_index.get(root_instance_key)
        if root_step_index is None:
            raise ValueError(
                "Phase 11 fast plan: root instance key missing from step index."
            )
        fast_call_modes: List[int] = [ExecutionPlanCallMode.CALLN] * step_count
        fast_single_dep_indices: List[int] = [-1] * step_count
        fast_call2_dep_indices_a: List[int] = [-1] * step_count
        fast_call2_dep_indices_b: List[int] = [-1] * step_count
        fast_call3_dep_indices_a: List[int] = [-1] * step_count
        fast_call3_dep_indices_b: List[int] = [-1] * step_count
        fast_call3_dep_indices_c: List[int] = [-1] * step_count
        fast_call4_dep_indices_a: List[int] = [-1] * step_count
        fast_call4_dep_indices_b: List[int] = [-1] * step_count
        fast_call4_dep_indices_c: List[int] = [-1] * step_count
        fast_call4_dep_indices_d: List[int] = [-1] * step_count
        fast_call5_dep_indices_a: List[int] = [-1] * step_count
        fast_call5_dep_indices_b: List[int] = [-1] * step_count
        fast_call5_dep_indices_c: List[int] = [-1] * step_count
        fast_call5_dep_indices_d: List[int] = [-1] * step_count
        fast_call5_dep_indices_e: List[int] = [-1] * step_count
        fast_call6_dep_indices_a: List[int] = [-1] * step_count
        fast_call6_dep_indices_b: List[int] = [-1] * step_count
        fast_call6_dep_indices_c: List[int] = [-1] * step_count
        fast_call6_dep_indices_d: List[int] = [-1] * step_count
        fast_call6_dep_indices_e: List[int] = [-1] * step_count
        fast_call6_dep_indices_f: List[int] = [-1] * step_count
        fast_call7_dep_indices_a: List[int] = [-1] * step_count
        fast_call7_dep_indices_b: List[int] = [-1] * step_count
        fast_call7_dep_indices_c: List[int] = [-1] * step_count
        fast_call7_dep_indices_d: List[int] = [-1] * step_count
        fast_call7_dep_indices_e: List[int] = [-1] * step_count
        fast_call7_dep_indices_f: List[int] = [-1] * step_count
        fast_call7_dep_indices_g: List[int] = [-1] * step_count
        fast_call8_dep_indices_a: List[int] = [-1] * step_count
        fast_call8_dep_indices_b: List[int] = [-1] * step_count
        fast_call8_dep_indices_c: List[int] = [-1] * step_count
        fast_call8_dep_indices_d: List[int] = [-1] * step_count
        fast_call8_dep_indices_e: List[int] = [-1] * step_count
        fast_call8_dep_indices_f: List[int] = [-1] * step_count
        fast_call8_dep_indices_g: List[int] = [-1] * step_count
        fast_call8_dep_indices_h: List[int] = [-1] * step_count

        seen_spell_ids: set[str] = set()

        for step_index, step in enumerate(steps):
            dep_keys_by_param = step.dependency_keys_by_param
            instance_key = step.instance_key
            spell_id = instance_key[0]
            if spell_id not in seen_spell_ids:
                seen_spell_ids.add(spell_id)
                fast_set_result_flags[step_index] = True
            fast_instance_keys[step_index] = instance_key
            fast_creations_target_kinds[step_index] = step.creations_target_kind
            fast_existence[step_index] = step.existence
            fast_must_register[step_index] = step.must_register
            fast_spells[step_index] = step.spell
            fast_call_targets[step_index] = step.spell.spell
            fast_existing_objects[step_index] = step.spell.user_created_object
            fast_is_existing_creation[step_index] = step.spell.is_existing_creation
            fast_is_callable[step_index] = (
                step.spell.is_class_spell
                or step.spell.is_method_spell
                or step.spell.is_lambda_spell
            )
            requirements = step.spell.requirements
            if requirements is not None:
                params = requirements.parameters
                param_order = [param.name for param in params]
                di_param_names = set(dep_keys_by_param.keys())
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
                param_order = list(dep_keys_by_param.keys())
                positional_ok = False

            fast_param_group_offsets[step_index] = len(fast_param_group_names)
            group_count = 0

            for param_name in param_order:
                dependency_keys = dep_keys_by_param.get(param_name)
                if not dependency_keys:
                    continue

                fast_param_group_names.append(param_name)
                fast_param_group_dep_offsets.append(len(fast_dep_indices))
                for dependency_key in dependency_keys:
                    dep_index = instance_key_to_step_index.get(dependency_key)
                    if dep_index is None:
                        raise ValueError(
                            f"Phase 11 fast plan: dependency '{dependency_key[0]}' "
                            "missing from step index."
                        )
                    fast_dep_indices.append(dep_index)
                fast_param_group_dep_counts.append(len(dependency_keys))
                group_count += 1

            fast_param_group_counts[step_index] = group_count

            contract_payload = step.contract_payload
            contract_positional = None
            contract_items: Optional[List[Tuple[str, Any]]] = None
            if contract_payload:
                items: List[Tuple[str, Any]] = []
                for key, value in contract_payload.items():
                    if key == "__args__":
                        continue
                    items.append((key, value))
                if items:
                    contract_items = items
                if step.uses_positional_override and "__args__" in contract_payload:
                    contract_positional = contract_payload["__args__"]

            fast_contract_payload_items[step_index] = contract_items
            fast_contract_positional_args[step_index] = contract_positional
            fast_use_positional[step_index] = (
                positional_ok and contract_items is None and contract_positional is None
            )
            if fast_use_positional[step_index]:
                if group_count == 0:
                    fast_call_modes[step_index] = ExecutionPlanCallMode.CALL0
                elif group_count == 1:
                    group_base = fast_param_group_offsets[step_index]
                    dep_offset = fast_param_group_dep_offsets[group_base]
                    dep_count = fast_param_group_dep_counts[group_base]
                    if dep_count == 1:
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL1
                        fast_single_dep_indices[step_index] = fast_dep_indices[dep_offset]
                elif group_count == 2:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    if dep_count_a == 1 and dep_count_b == 1:
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL2
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        fast_call2_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call2_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                elif group_count == 3:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    if dep_count_a == 1 and dep_count_b == 1 and dep_count_c == 1:
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL3
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        dep_offset_c = fast_param_group_dep_offsets[group_base + 2]
                        fast_call3_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call3_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                        fast_call3_dep_indices_c[step_index] = fast_dep_indices[dep_offset_c]
                elif group_count == 4:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    dep_count_d = fast_param_group_dep_counts[group_base + 3]
                    if (
                            dep_count_a == 1
                            and dep_count_b == 1
                            and dep_count_c == 1
                            and dep_count_d == 1
                    ):
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL4
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        dep_offset_c = fast_param_group_dep_offsets[group_base + 2]
                        dep_offset_d = fast_param_group_dep_offsets[group_base + 3]
                        fast_call4_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call4_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                        fast_call4_dep_indices_c[step_index] = fast_dep_indices[dep_offset_c]
                        fast_call4_dep_indices_d[step_index] = fast_dep_indices[dep_offset_d]
                elif group_count == 5:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    dep_count_d = fast_param_group_dep_counts[group_base + 3]
                    dep_count_e = fast_param_group_dep_counts[group_base + 4]
                    if (
                            dep_count_a == 1
                            and dep_count_b == 1
                            and dep_count_c == 1
                            and dep_count_d == 1
                            and dep_count_e == 1
                    ):
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL5
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        dep_offset_c = fast_param_group_dep_offsets[group_base + 2]
                        dep_offset_d = fast_param_group_dep_offsets[group_base + 3]
                        dep_offset_e = fast_param_group_dep_offsets[group_base + 4]
                        fast_call5_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call5_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                        fast_call5_dep_indices_c[step_index] = fast_dep_indices[dep_offset_c]
                        fast_call5_dep_indices_d[step_index] = fast_dep_indices[dep_offset_d]
                        fast_call5_dep_indices_e[step_index] = fast_dep_indices[dep_offset_e]
                elif group_count == 6:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    dep_count_d = fast_param_group_dep_counts[group_base + 3]
                    dep_count_e = fast_param_group_dep_counts[group_base + 4]
                    dep_count_f = fast_param_group_dep_counts[group_base + 5]
                    if (
                            dep_count_a == 1
                            and dep_count_b == 1
                            and dep_count_c == 1
                            and dep_count_d == 1
                            and dep_count_e == 1
                            and dep_count_f == 1
                    ):
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL6
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        dep_offset_c = fast_param_group_dep_offsets[group_base + 2]
                        dep_offset_d = fast_param_group_dep_offsets[group_base + 3]
                        dep_offset_e = fast_param_group_dep_offsets[group_base + 4]
                        dep_offset_f = fast_param_group_dep_offsets[group_base + 5]
                        fast_call6_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call6_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                        fast_call6_dep_indices_c[step_index] = fast_dep_indices[dep_offset_c]
                        fast_call6_dep_indices_d[step_index] = fast_dep_indices[dep_offset_d]
                        fast_call6_dep_indices_e[step_index] = fast_dep_indices[dep_offset_e]
                        fast_call6_dep_indices_f[step_index] = fast_dep_indices[dep_offset_f]
                elif group_count == 7:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    dep_count_d = fast_param_group_dep_counts[group_base + 3]
                    dep_count_e = fast_param_group_dep_counts[group_base + 4]
                    dep_count_f = fast_param_group_dep_counts[group_base + 5]
                    dep_count_g = fast_param_group_dep_counts[group_base + 6]
                    if (
                            dep_count_a == 1
                            and dep_count_b == 1
                            and dep_count_c == 1
                            and dep_count_d == 1
                            and dep_count_e == 1
                            and dep_count_f == 1
                            and dep_count_g == 1
                    ):
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL7
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        dep_offset_c = fast_param_group_dep_offsets[group_base + 2]
                        dep_offset_d = fast_param_group_dep_offsets[group_base + 3]
                        dep_offset_e = fast_param_group_dep_offsets[group_base + 4]
                        dep_offset_f = fast_param_group_dep_offsets[group_base + 5]
                        dep_offset_g = fast_param_group_dep_offsets[group_base + 6]
                        fast_call7_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call7_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                        fast_call7_dep_indices_c[step_index] = fast_dep_indices[dep_offset_c]
                        fast_call7_dep_indices_d[step_index] = fast_dep_indices[dep_offset_d]
                        fast_call7_dep_indices_e[step_index] = fast_dep_indices[dep_offset_e]
                        fast_call7_dep_indices_f[step_index] = fast_dep_indices[dep_offset_f]
                        fast_call7_dep_indices_g[step_index] = fast_dep_indices[dep_offset_g]
                elif group_count == 8:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    dep_count_d = fast_param_group_dep_counts[group_base + 3]
                    dep_count_e = fast_param_group_dep_counts[group_base + 4]
                    dep_count_f = fast_param_group_dep_counts[group_base + 5]
                    dep_count_g = fast_param_group_dep_counts[group_base + 6]
                    dep_count_h = fast_param_group_dep_counts[group_base + 7]
                    if (
                            dep_count_a == 1
                            and dep_count_b == 1
                            and dep_count_c == 1
                            and dep_count_d == 1
                            and dep_count_e == 1
                            and dep_count_f == 1
                            and dep_count_g == 1
                            and dep_count_h == 1
                    ):
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL8
                        dep_offset_a = fast_param_group_dep_offsets[group_base]
                        dep_offset_b = fast_param_group_dep_offsets[group_base + 1]
                        dep_offset_c = fast_param_group_dep_offsets[group_base + 2]
                        dep_offset_d = fast_param_group_dep_offsets[group_base + 3]
                        dep_offset_e = fast_param_group_dep_offsets[group_base + 4]
                        dep_offset_f = fast_param_group_dep_offsets[group_base + 5]
                        dep_offset_g = fast_param_group_dep_offsets[group_base + 6]
                        dep_offset_h = fast_param_group_dep_offsets[group_base + 7]
                        fast_call8_dep_indices_a[step_index] = fast_dep_indices[dep_offset_a]
                        fast_call8_dep_indices_b[step_index] = fast_dep_indices[dep_offset_b]
                        fast_call8_dep_indices_c[step_index] = fast_dep_indices[dep_offset_c]
                        fast_call8_dep_indices_d[step_index] = fast_dep_indices[dep_offset_d]
                        fast_call8_dep_indices_e[step_index] = fast_dep_indices[dep_offset_e]
                        fast_call8_dep_indices_f[step_index] = fast_dep_indices[dep_offset_f]
                        fast_call8_dep_indices_g[step_index] = fast_dep_indices[dep_offset_g]
                        fast_call8_dep_indices_h[step_index] = fast_dep_indices[dep_offset_h]

        return (
            fast_dep_indices,
            fast_param_group_names,
            fast_param_group_dep_offsets,
            fast_param_group_dep_counts,
            fast_param_group_offsets,
            fast_param_group_counts,
            fast_use_positional,
            fast_contract_payload_items,
            fast_contract_positional_args,
            fast_instance_keys,
            fast_creations_target_kinds,
            fast_existence,
            fast_must_register,
            fast_set_result_flags,
            fast_spells,
            fast_call_targets,
            fast_existing_objects,
            fast_is_existing_creation,
            fast_is_callable,
            root_step_index,
            fast_call_modes,
            fast_single_dep_indices,
            fast_call2_dep_indices_a,
            fast_call2_dep_indices_b,
            fast_call3_dep_indices_a,
            fast_call3_dep_indices_b,
            fast_call3_dep_indices_c,
            fast_call4_dep_indices_a,
            fast_call4_dep_indices_b,
            fast_call4_dep_indices_c,
            fast_call4_dep_indices_d,
            fast_call5_dep_indices_a,
            fast_call5_dep_indices_b,
            fast_call5_dep_indices_c,
            fast_call5_dep_indices_d,
            fast_call5_dep_indices_e,
            fast_call6_dep_indices_a,
            fast_call6_dep_indices_b,
            fast_call6_dep_indices_c,
            fast_call6_dep_indices_d,
            fast_call6_dep_indices_e,
            fast_call6_dep_indices_f,
            fast_call7_dep_indices_a,
            fast_call7_dep_indices_b,
            fast_call7_dep_indices_c,
            fast_call7_dep_indices_d,
            fast_call7_dep_indices_e,
            fast_call7_dep_indices_f,
            fast_call7_dep_indices_g,
            fast_call8_dep_indices_a,
            fast_call8_dep_indices_b,
            fast_call8_dep_indices_c,
            fast_call8_dep_indices_d,
            fast_call8_dep_indices_e,
            fast_call8_dep_indices_f,
            fast_call8_dep_indices_g,
            fast_call8_dep_indices_h,
        )

    def _build_fast_transient_plan(
            self,
            *,
            steps: List[ExecutionPlanStep],
            fast_call_targets: List[Any],
            fast_existence: List[Existence],
            fast_must_register: List[bool],
            fast_is_existing_creation: List[bool],
            fast_is_callable: List[bool],
            fast_call_modes: List[int],
            fast_single_dep_indices: List[int],
            fast_call2_dep_indices_a: List[int],
            fast_call2_dep_indices_b: List[int],
            fast_call3_dep_indices_a: List[int],
            fast_call3_dep_indices_b: List[int],
            fast_call3_dep_indices_c: List[int],
            fast_call4_dep_indices_a: List[int],
            fast_call4_dep_indices_b: List[int],
            fast_call4_dep_indices_c: List[int],
            fast_call4_dep_indices_d: List[int],
            fast_call5_dep_indices_a: List[int],
            fast_call5_dep_indices_b: List[int],
            fast_call5_dep_indices_c: List[int],
            fast_call5_dep_indices_d: List[int],
            fast_call5_dep_indices_e: List[int],
            fast_call6_dep_indices_a: List[int],
            fast_call6_dep_indices_b: List[int],
            fast_call6_dep_indices_c: List[int],
            fast_call6_dep_indices_d: List[int],
            fast_call6_dep_indices_e: List[int],
            fast_call6_dep_indices_f: List[int],
            fast_call7_dep_indices_a: List[int],
            fast_call7_dep_indices_b: List[int],
            fast_call7_dep_indices_c: List[int],
            fast_call7_dep_indices_d: List[int],
            fast_call7_dep_indices_e: List[int],
            fast_call7_dep_indices_f: List[int],
            fast_call7_dep_indices_g: List[int],
            fast_call8_dep_indices_a: List[int],
            fast_call8_dep_indices_b: List[int],
            fast_call8_dep_indices_c: List[int],
            fast_call8_dep_indices_d: List[int],
            fast_call8_dep_indices_e: List[int],
            fast_call8_dep_indices_f: List[int],
            fast_call8_dep_indices_g: List[int],
            fast_call8_dep_indices_h: List[int],
            root_step_index: int,
    ) -> Optional[FastTransientPlan]:
        """
        Build a specialized transient-only plan for no-overrides execution.

        Contract:
            - Returns None if any step is not a transient callable without registration.
            - CALLN steps are not supported by the transient plan.
        """
        step_count = len(steps)
        transient_targets: List[Any] = [None] * step_count
        transient_call_modes: List[int] = [ExecutionPlanCallMode.CALLN] * step_count
        transient_dep1: List[int] = [-1] * step_count
        transient_dep2a: List[int] = [-1] * step_count
        transient_dep2b: List[int] = [-1] * step_count
        transient_dep3a: List[int] = [-1] * step_count
        transient_dep3b: List[int] = [-1] * step_count
        transient_dep3c: List[int] = [-1] * step_count
        transient_dep4a: List[int] = [-1] * step_count
        transient_dep4b: List[int] = [-1] * step_count
        transient_dep4c: List[int] = [-1] * step_count
        transient_dep4d: List[int] = [-1] * step_count
        transient_dep5a: List[int] = [-1] * step_count
        transient_dep5b: List[int] = [-1] * step_count
        transient_dep5c: List[int] = [-1] * step_count
        transient_dep5d: List[int] = [-1] * step_count
        transient_dep5e: List[int] = [-1] * step_count
        transient_dep6a: List[int] = [-1] * step_count
        transient_dep6b: List[int] = [-1] * step_count
        transient_dep6c: List[int] = [-1] * step_count
        transient_dep6d: List[int] = [-1] * step_count
        transient_dep6e: List[int] = [-1] * step_count
        transient_dep6f: List[int] = [-1] * step_count
        transient_dep7a: List[int] = [-1] * step_count
        transient_dep7b: List[int] = [-1] * step_count
        transient_dep7c: List[int] = [-1] * step_count
        transient_dep7d: List[int] = [-1] * step_count
        transient_dep7e: List[int] = [-1] * step_count
        transient_dep7f: List[int] = [-1] * step_count
        transient_dep7g: List[int] = [-1] * step_count
        transient_dep8a: List[int] = [-1] * step_count
        transient_dep8b: List[int] = [-1] * step_count
        transient_dep8c: List[int] = [-1] * step_count
        transient_dep8d: List[int] = [-1] * step_count
        transient_dep8e: List[int] = [-1] * step_count
        transient_dep8f: List[int] = [-1] * step_count
        transient_dep8g: List[int] = [-1] * step_count
        transient_dep8h: List[int] = [-1] * step_count

        for index in range(step_count):
            if fast_existence[index] is not Existence.many:
                return None
            if fast_must_register[index]:
                return None
            if fast_is_existing_creation[index]:
                return None
            if not fast_is_callable[index]:
                return None
            call_mode = fast_call_modes[index]
            if call_mode == ExecutionPlanCallMode.CALLN:
                return None
            transient_targets[index] = fast_call_targets[index]
            transient_call_modes[index] = call_mode
            if call_mode == ExecutionPlanCallMode.CALL1:
                transient_dep1[index] = fast_single_dep_indices[index]
            elif call_mode == ExecutionPlanCallMode.CALL2:
                transient_dep2a[index] = fast_call2_dep_indices_a[index]
                transient_dep2b[index] = fast_call2_dep_indices_b[index]
            elif call_mode == ExecutionPlanCallMode.CALL3:
                transient_dep3a[index] = fast_call3_dep_indices_a[index]
                transient_dep3b[index] = fast_call3_dep_indices_b[index]
                transient_dep3c[index] = fast_call3_dep_indices_c[index]
            elif call_mode == ExecutionPlanCallMode.CALL4:
                transient_dep4a[index] = fast_call4_dep_indices_a[index]
                transient_dep4b[index] = fast_call4_dep_indices_b[index]
                transient_dep4c[index] = fast_call4_dep_indices_c[index]
                transient_dep4d[index] = fast_call4_dep_indices_d[index]
            elif call_mode == ExecutionPlanCallMode.CALL5:
                transient_dep5a[index] = fast_call5_dep_indices_a[index]
                transient_dep5b[index] = fast_call5_dep_indices_b[index]
                transient_dep5c[index] = fast_call5_dep_indices_c[index]
                transient_dep5d[index] = fast_call5_dep_indices_d[index]
                transient_dep5e[index] = fast_call5_dep_indices_e[index]
            elif call_mode == ExecutionPlanCallMode.CALL6:
                transient_dep6a[index] = fast_call6_dep_indices_a[index]
                transient_dep6b[index] = fast_call6_dep_indices_b[index]
                transient_dep6c[index] = fast_call6_dep_indices_c[index]
                transient_dep6d[index] = fast_call6_dep_indices_d[index]
                transient_dep6e[index] = fast_call6_dep_indices_e[index]
                transient_dep6f[index] = fast_call6_dep_indices_f[index]
            elif call_mode == ExecutionPlanCallMode.CALL7:
                transient_dep7a[index] = fast_call7_dep_indices_a[index]
                transient_dep7b[index] = fast_call7_dep_indices_b[index]
                transient_dep7c[index] = fast_call7_dep_indices_c[index]
                transient_dep7d[index] = fast_call7_dep_indices_d[index]
                transient_dep7e[index] = fast_call7_dep_indices_e[index]
                transient_dep7f[index] = fast_call7_dep_indices_f[index]
                transient_dep7g[index] = fast_call7_dep_indices_g[index]
            elif call_mode == ExecutionPlanCallMode.CALL8:
                transient_dep8a[index] = fast_call8_dep_indices_a[index]
                transient_dep8b[index] = fast_call8_dep_indices_b[index]
                transient_dep8c[index] = fast_call8_dep_indices_c[index]
                transient_dep8d[index] = fast_call8_dep_indices_d[index]
                transient_dep8e[index] = fast_call8_dep_indices_e[index]
                transient_dep8f[index] = fast_call8_dep_indices_f[index]
                transient_dep8g[index] = fast_call8_dep_indices_g[index]
                transient_dep8h[index] = fast_call8_dep_indices_h[index]

        return (
            step_count,
            root_step_index,
            transient_targets,
            transient_call_modes,
            transient_dep1,
            transient_dep2a,
            transient_dep2b,
            transient_dep3a,
            transient_dep3b,
            transient_dep3c,
            transient_dep4a,
            transient_dep4b,
            transient_dep4c,
            transient_dep4d,
            transient_dep5a,
            transient_dep5b,
            transient_dep5c,
            transient_dep5d,
            transient_dep5e,
            transient_dep6a,
            transient_dep6b,
            transient_dep6c,
            transient_dep6d,
            transient_dep6e,
            transient_dep6f,
            transient_dep7a,
            transient_dep7b,
            transient_dep7c,
            transient_dep7d,
            transient_dep7e,
            transient_dep7f,
            transient_dep7g,
            transient_dep8a,
            transient_dep8b,
            transient_dep8c,
            transient_dep8d,
            transient_dep8e,
            transient_dep8f,
            transient_dep8g,
            transient_dep8h,
        )

    @staticmethod
    def _creation_target_for_existence(existence: Existence) -> int:
        """
        Map an existence policy to the runtime creations-target kind.

        Shared/root-owned existences route to owner creations, while per-caller
        or spellspace-scoped existences stay on the caller-side container.
        """
        if existence is Existence.unique_per_conduit:
            return ExecutionPlanTargetKind.CALLER
        if existence is Existence.unique_per_spell_space:
            return ExecutionPlanTargetKind.SPELLSPACE
        if existence is Existence.many:
            return ExecutionPlanTargetKind.CALLER
        return ExecutionPlanTargetKind.OWNER

    @staticmethod
    def _lock_hint_for_existence(existence: Existence) -> str:
        """
        Return the preferred runtime lock family for an existence policy.

        Shared existences prefer the spell lock; caller-local existences use
        the creations lock path.
        """
        if existence in (
                Existence.unique,
                Existence.unique_per_conduit_cluster,
                Existence.unique_per_conduit_lineage,
        ):
            return "spell_lock"
        return "creations_lock"

    @staticmethod
    def _should_register(spell: ISpell) -> bool:
        """
        Decide whether a spell's result must be registered in creations.

        Contract:
            `Existence.many` without disposal methods can skip registration;
            all other spell shapes remain registration-backed.
        """
        if spell.existence is Existence.many and not spell.has_disposal_methods:
            return False
        return True

    def _occurrence_for_instance_key(self, instance_key: InstanceKey) -> OccurrenceKey:
        """
        Resolve the occurrence key backing one instance key.

        Shared instance keys recover their canonical occurrence from the Phase 8
        plan; path-bearing instance keys map directly.
        """
        spell_id, path = instance_key
        if path is not None:
            return spell_id, path
        canonical = self._occurrence_plan.canonical_occurrences_by_spell_id.get(spell_id)
        if canonical is None:
            raise ValueError(
                f"Phase 11 ExecutionPlan: canonical occurrence missing for '{spell_id}'."
            )
        return canonical

    @staticmethod
    def _extract_param_keys(
            inject_spec: Optional[InjectionSpec],
    ) -> tuple[List[InstanceKey], Dict[str, List[InstanceKey]], List[str], List[str]]:
        """
        Flatten dependency, override, and contract keys from one injection spec.

        Returns:
            tuple:
                `(dependency_keys, dependency_keys_by_param, override_keys,
                contract_keys)` for use while building execution steps.
        """
        if inject_spec is None:
            return [], {}, [], []
        dependency_keys: List[InstanceKey] = []
        dependency_keys_by_param: Dict[str, List[InstanceKey]] = {}
        override_keys: List[str] = []
        contract_keys: List[str] = []
        for source in inject_spec.param_sources.values():
            if source.dependency_keys:
                dependency_keys.extend(source.dependency_keys)
            if source.override_key:
                override_keys.append(source.override_key)
            if source.contract_key:
                contract_keys.append(source.contract_key)
        for param_name, source in inject_spec.param_sources.items():
            if source.dependency_keys:
                dependency_keys_by_param[param_name] = list(source.dependency_keys)
        return dependency_keys, dependency_keys_by_param, override_keys, contract_keys

    @staticmethod
    def _extract_param_keys_no_overrides(
            inject_spec: Optional[InjectionSpec],
    ) -> tuple[List[InstanceKey], Dict[str, List[InstanceKey]]]:
        """
        Flatten only dependency keys for the no-overrides branch.

        Contract:
            - Returns dependency routing only.
            - Skips override-key and contract-key collection entirely.
            - Preserves dependency ordering semantics from the full helper.
        """
        if inject_spec is None:
            return [], {}
        dependency_keys: List[InstanceKey] = []
        dependency_keys_by_param: Dict[str, List[InstanceKey]] = {}
        for source in inject_spec.param_sources.values():
            if source.dependency_keys:
                dependency_keys.extend(source.dependency_keys)
        for param_name, source in inject_spec.param_sources.items():
            if source.dependency_keys:
                dependency_keys_by_param[param_name] = list(source.dependency_keys)
        return dependency_keys, dependency_keys_by_param
