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
from melder.utilities.interfaces.interfaces import ISpell


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
    CALLN = 4


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
            override_match_prefix: Optional[tuple[str, ...]],
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

        self._instance_key = instance_key
        self._occurrence = occurrence
        self._spell = spell
        self._existence = existence
        self._creations_target_kind = creations_target_kind
        self._shared_instance = shared_instance
        self._inject_spec = inject_spec
        self._dependency_keys = dependency_keys
        self._dependency_keys_by_param = dependency_keys_by_param
        self._dependency_resolution_order = dependency_resolution_order
        self._override_keys = override_keys
        self._override_match_prefix = override_match_prefix
        self._override_match_prefix_len = override_match_prefix_len
        self._expects_overrides = expects_overrides
        self._contract_keys = contract_keys
        self._allow_list_aggregation = allow_list_aggregation
        self._uses_positional_override = uses_positional_override
        self._contract_payload = contract_payload
        self._contract_positional_override = contract_positional_override
        self._has_contract_payload = has_contract_payload
        self._lock_hint = lock_hint
        self._use_spell_lock_hint = use_spell_lock_hint
        self._requires_spellspace = requires_spellspace
        self._owner_conduit_required = owner_conduit_required
        self._must_register = must_register
        self._disposal_method_names = disposal_method_names

    @property
    def instance_key(self) -> InstanceKey:
        return self._instance_key

    @property
    def occurrence(self) -> OccurrenceKey:
        return self._occurrence

    @property
    def spell(self) -> ISpell:
        return self._spell

    @property
    def existence(self) -> Existence:
        return self._existence

    @property
    def creations_target_kind(self) -> int:
        return self._creations_target_kind

    @property
    def shared_instance(self) -> bool:
        return self._shared_instance

    @property
    def inject_spec(self) -> Optional[InjectionSpec]:
        return self._inject_spec

    @property
    def dependency_keys(self) -> List[InstanceKey]:
        return self._dependency_keys

    @property
    def dependency_keys_by_param(self) -> Dict[str, List[InstanceKey]]:
        return self._dependency_keys_by_param

    @property
    def dependency_resolution_order(self) -> List[tuple[str, List[InstanceKey]]]:
        """
        Return the pre-flattened dependency resolution order for this step.
        """
        return self._dependency_resolution_order

    @property
    def override_keys(self) -> List[str]:
        return self._override_keys

    @property
    def override_match_prefix(self) -> Optional[tuple[str, ...]]:
        """
        Return the precomputed override path prefix for this step.
        """
        return self._override_match_prefix

    @property
    def override_match_prefix_len(self) -> int:
        """
        Return the cached override path prefix length for this step.
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
        return self._contract_keys

    @property
    def allow_list_aggregation(self) -> bool:
        return self._allow_list_aggregation

    @property
    def uses_positional_override(self) -> bool:
        return self._uses_positional_override

    @property
    def contract_payload(self) -> Optional[Dict[str, Any]]:
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
        return self._lock_hint

    @property
    def use_spell_lock_hint(self) -> bool:
        return self._use_spell_lock_hint

    @property
    def requires_spellspace(self) -> bool:
        return self._requires_spellspace

    @property
    def owner_conduit_required(self) -> bool:
        return self._owner_conduit_required

    @property
    def must_register(self) -> bool:
        return self._must_register

    @property
    def disposal_method_names(self) -> List[str]:
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
    ]

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
        self._root_spell_id = None
        self._root_instance_key = None
        self._steps = None
        self._spell_id_step_index = None
        self._optimistic_object_refs_by_spell_id = None
        self._available_param_by_spell_id = None
        self._plan_variant = None
        self._fast_dep_indices = None
        self._fast_param_group_names = None
        self._fast_param_group_dep_offsets = None
        self._fast_param_group_dep_counts = None
        self._fast_param_group_offsets = None
        self._fast_param_group_counts = None
        self._fast_use_positional = None
        self._fast_contract_payload_items = None
        self._fast_contract_positional_args = None
        self._fast_instance_keys = None
        self._fast_creations_target_kinds = None
        self._fast_existence = None
        self._fast_must_register = None
        self._fast_set_result_flags = None
        self._fast_spells = None
        self._fast_call_targets = None
        self._fast_existing_objects = None
        self._fast_is_existing_creation = None
        self._fast_is_callable = None
        self._fast_root_step_index = None
        self._fast_call_modes = None
        self._fast_single_dep_indices = None

    @property
    def root_spell_id(self) -> str:
        return self._root_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        return self._root_instance_key

    @property
    def steps(self) -> List[ExecutionPlanStep]:
        return self._steps

    @property
    def spell_id_step_index(self) -> Dict[str, int]:
        return self._spell_id_step_index

    @property
    def optimistic_object_refs_by_spell_id(self) -> Dict[str, Any]:
        return self._optimistic_object_refs_by_spell_id

    @property
    def available_param_by_spell_id(self) -> Dict[str, int]:
        return self._available_param_by_spell_id

    @property
    def plan_variant(self) -> str:
        return self._plan_variant

    @property
    def fast_plan(
            self,
    ) -> Optional[
        Tuple[
            List[int],
            List[str],
            List[int],
            List[int],
            List[int],
            List[int],
            List[bool],
            List[Optional[List[Tuple[str, Any]]]],
            List[Optional[Any]],
            List[InstanceKey],
            List[int],
            List[Existence],
            List[bool],
            List[bool],
            List[ISpell],
            List[Any],
            List[Any],
            List[bool],
            List[bool],
            int,
            List[int],
            List[int],
        ]
    ]:
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
        )


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

            for instance_key in self._occurrence_plan.instance_keys_by_spell_id.get(spell_id, []):
                occurrence = self._occurrence_for_instance_key(instance_key)
                inject_spec = injection_lookup.get(instance_key) if injection_lookup else None
                dependency_keys, dependency_keys_by_param, override_keys, contract_keys = (
                    self._extract_param_keys(inject_spec)
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
                expects_overrides = bool(override_keys)
                override_match_prefix = occurrence[1]
                override_match_prefix_len = (
                    len(override_match_prefix)
                    if override_match_prefix is not None
                    else 0
                )

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
        if self._plan_variant == ExecutionPlanVariant.NO_OVERRIDES_FAST:
            fast_plan_data = self._build_fast_plan_data(
                steps=steps,
                instance_key_to_step_index=instance_key_to_step_index,
                root_instance_key=self._occurrence_plan.root_instance_key,
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
        )

    def _build_fast_plan_data(
            self,
            *,
            steps: List[ExecutionPlanStep],
            instance_key_to_step_index: Dict[InstanceKey, int],
            root_instance_key: InstanceKey,
    ) -> Tuple[
        List[int],
        List[str],
        List[int],
        List[int],
        List[int],
        List[int],
        List[bool],
        List[Optional[List[Tuple[str, Any]]]],
        List[Optional[Any]],
        List[InstanceKey],
            List[int],
            List[Existence],
            List[bool],
            List[bool],
            List[ISpell],
            List[Any],
            List[Any],
            List[bool],
            List[bool],
            int,
            List[int],
            List[int],
    ]:
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
        fast_instance_keys: List[InstanceKey] = [None] * step_count
        fast_creations_target_kinds: List[int] = [0] * step_count
        fast_existence: List[Existence] = [None] * step_count
        fast_must_register: List[bool] = [False] * step_count
        fast_set_result_flags: List[bool] = [False] * step_count
        fast_spells: List[ISpell] = [None] * step_count
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
                elif group_count == 3:
                    group_base = fast_param_group_offsets[step_index]
                    dep_count_a = fast_param_group_dep_counts[group_base]
                    dep_count_b = fast_param_group_dep_counts[group_base + 1]
                    dep_count_c = fast_param_group_dep_counts[group_base + 2]
                    if dep_count_a == 1 and dep_count_b == 1 and dep_count_c == 1:
                        fast_call_modes[step_index] = ExecutionPlanCallMode.CALL3

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
        )

    @staticmethod
    def _creation_target_for_existence(existence: Existence) -> int:
        if existence is Existence.unique_per_conduit:
            return ExecutionPlanTargetKind.CALLER
        if existence is Existence.unique_per_spell_space:
            return ExecutionPlanTargetKind.SPELLSPACE
        if existence is Existence.many:
            return ExecutionPlanTargetKind.CALLER
        return ExecutionPlanTargetKind.OWNER

    @staticmethod
    def _lock_hint_for_existence(existence: Existence) -> str:
        if existence in (
                Existence.unique,
                Existence.unique_per_conduit_cluster,
                Existence.unique_per_conduit_lineage,
        ):
            return "spell_lock"
        return "creations_lock"

    @staticmethod
    def _should_register(spell: ISpell) -> bool:
        if spell.existence is Existence.many and not spell.has_disposal_methods:
            return False
        return True

    def _occurrence_for_instance_key(self, instance_key: InstanceKey) -> OccurrenceKey:
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
