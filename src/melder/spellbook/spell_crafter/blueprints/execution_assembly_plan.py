from typing import Any, Dict, List, Optional

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

    Execution assembly plan variant labels.

    Purpose:
        Identify which precompiled execution assembly plan should be selected
        based on override and mutation payloads at meld time.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ()
    NO_OVERRIDES_FAST = "no_overrides_fast"
    OVERRIDES = "overrides"
    OVERRIDES_WITH_MUTATIONS = "overrides_with_mutations"


class ExecutionAssemblyStep:
    """
    Internal

    Phase 12 execution assembly step metadata.

    Purpose:
        Capture precomputed routing and creations delegation metadata needed
        to execute meld assembly with minimal runtime planning.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_spell_id",
        "_instance_key",
        "_occurrence",
        "_existence",
        "_creations_target_kind",
        "_shared_instance",
        "_inject_spec",
        "_dependency_keys",
        "_override_keys",
        "_contract_keys",
        "_allow_list_aggregation",
        "_uses_positional_override",
        "_contract_payload",
        "_lock_hint",
        "_requires_spellspace",
        "_owner_conduit_required",
        "_must_register",
        "_disposal_method_names",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            instance_key: InstanceKey,
            occurrence: OccurrenceKey,
            existence: Existence,
            creations_target_kind: str,
            shared_instance: bool,
            inject_spec: Optional[InjectionSpec],
            dependency_keys: List[InstanceKey],
            override_keys: List[str],
            contract_keys: List[str],
            allow_list_aggregation: bool,
            uses_positional_override: bool,
            contract_payload: Optional[Dict[str, Any]],
            lock_hint: str,
            requires_spellspace: bool,
            owner_conduit_required: bool,
            must_register: bool,
            disposal_method_names: List[str],
    ) -> None:
        if spell_id is None:
            raise ValueError("spell_id must not be None.")
        if instance_key is None:
            raise ValueError("instance_key must not be None.")
        if occurrence is None:
            raise ValueError("occurrence must not be None.")
        if existence is None:
            raise ValueError("existence must not be None.")
        if creations_target_kind is None:
            raise ValueError("creations_target_kind must not be None.")
        if shared_instance is None:
            raise ValueError("shared_instance must not be None.")
        if dependency_keys is None:
            raise ValueError("dependency_keys must not be None.")
        if override_keys is None:
            raise ValueError("override_keys must not be None.")
        if contract_keys is None:
            raise ValueError("contract_keys must not be None.")
        if allow_list_aggregation is None:
            raise ValueError("allow_list_aggregation must not be None.")
        if uses_positional_override is None:
            raise ValueError("uses_positional_override must not be None.")
        if lock_hint is None:
            raise ValueError("lock_hint must not be None.")
        if requires_spellspace is None:
            raise ValueError("requires_spellspace must not be None.")
        if owner_conduit_required is None:
            raise ValueError("owner_conduit_required must not be None.")
        if must_register is None:
            raise ValueError("must_register must not be None.")
        if disposal_method_names is None:
            raise ValueError("disposal_method_names must not be None.")

        self._spell_id = spell_id
        self._instance_key = instance_key
        self._occurrence = occurrence
        self._existence = existence
        self._creations_target_kind = creations_target_kind
        self._shared_instance = shared_instance
        self._inject_spec = inject_spec
        self._dependency_keys = dependency_keys
        self._override_keys = override_keys
        self._contract_keys = contract_keys
        self._allow_list_aggregation = allow_list_aggregation
        self._uses_positional_override = uses_positional_override
        self._contract_payload = contract_payload
        self._lock_hint = lock_hint
        self._requires_spellspace = requires_spellspace
        self._owner_conduit_required = owner_conduit_required
        self._must_register = must_register
        self._disposal_method_names = disposal_method_names

    @property
    def spell_id(self) -> str:
        return self._spell_id

    @property
    def instance_key(self) -> InstanceKey:
        return self._instance_key

    @property
    def occurrence(self) -> OccurrenceKey:
        return self._occurrence

    @property
    def existence(self) -> Existence:
        return self._existence

    @property
    def creations_target_kind(self) -> str:
        return self._creations_target_kind

    @property
    def shared_instance(self) -> bool:
        return self._shared_instance

    @property
    def inject_spec(self) -> Optional[InjectionSpec]:
        return self._inject_spec

    @property
    def dependency_keys(self) -> List[InstanceKey]:
        return list(self._dependency_keys)

    @property
    def override_keys(self) -> List[str]:
        return list(self._override_keys)

    @property
    def contract_keys(self) -> List[str]:
        return list(self._contract_keys)

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
    def lock_hint(self) -> str:
        return self._lock_hint

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
        return list(self._disposal_method_names)


class ExecutionAssemblyPlan(Cleanable):
    """
    Internal

    Phase 12 artifact that captures execution assembly metadata.
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
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            root_instance_key: InstanceKey,
            steps: List[ExecutionAssemblyStep],
            spell_id_step_index: Dict[str, int],
            optimistic_object_refs_by_spell_id: Dict[str, Any],
            available_param_by_spell_id: Dict[str, str],
            plan_variant: str,
    ) -> None:
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

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        self._steps.clear()
        self._spell_id_step_index.clear()
        self._optimistic_object_refs_by_spell_id.clear()
        self._available_param_by_spell_id.clear()
        self._root_spell_id = None
        self._root_instance_key = None
        self._steps = None
        self._spell_id_step_index = None
        self._optimistic_object_refs_by_spell_id = None
        self._available_param_by_spell_id = None
        self._plan_variant = None

    @property
    def root_spell_id(self) -> str:
        return self._root_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        return self._root_instance_key

    @property
    def steps(self) -> List[ExecutionAssemblyStep]:
        return list(self._steps)

    @property
    def spell_id_step_index(self) -> Dict[str, int]:
        return dict(self._spell_id_step_index)

    @property
    def optimistic_object_refs_by_spell_id(self) -> Dict[str, Any]:
        return dict(self._optimistic_object_refs_by_spell_id)

    @property
    def available_param_by_spell_id(self) -> Dict[str, str]:
        return dict(self._available_param_by_spell_id)

    @property
    def plan_variant(self) -> str:
        return self._plan_variant


class ExecutionAssemblyPlanBuilder:
    """
    Internal

    Build a Phase 12 ExecutionAssemblyPlan from Phase 8/9 artifacts.
    """
    __melder_internal__ = _mrg.sentinel

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

    def build(self) -> ExecutionAssemblyPlan:
        root_spell_id = self._occurrence_plan.root_spell_id
        injection_lookup: Optional[Dict[InstanceKey, InjectionSpec]] = None
        if self._injection_plan is not None:
            injection_lookup = self._injection_plan.select_for_runtime(
                root_spell_id=root_spell_id,
            )
            if injection_lookup is None:
                raise ValueError(
                    "Phase 12 ExecutionAssemblyPlan: injection plan root mismatch or cleaned plan."
                )

        steps: List[ExecutionAssemblyStep] = []
        spell_id_step_index: Dict[str, int] = {}
        optimistic_refs: Dict[str, Any] = {}
        available_param_by_spell_id: Dict[str, str] = {}

        for spell_id in self._occurrence_plan.execution_order:
            spell = self._spell_lookup.get(spell_id)
            if spell is None:
                raise ValueError(
                    f"Phase 12 ExecutionAssemblyPlan: spell id '{spell_id}' missing from lookup."
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
                dependency_keys, override_keys, contract_keys = self._extract_param_keys(inject_spec)
                allow_list_aggregation = inject_spec.allow_list_aggregation if inject_spec else False
                uses_positional_override = inject_spec.uses_positional_override if inject_spec else False
                contract_payload = inject_spec.contract_payload if inject_spec else None

                step = ExecutionAssemblyStep(
                    spell_id=spell_id,
                    instance_key=instance_key,
                    occurrence=occurrence,
                    existence=existence,
                    creations_target_kind=creations_target_kind,
                    shared_instance=shared_instance,
                    inject_spec=inject_spec,
                    dependency_keys=dependency_keys,
                    override_keys=override_keys,
                    contract_keys=contract_keys,
                    allow_list_aggregation=allow_list_aggregation,
                    uses_positional_override=uses_positional_override,
                    contract_payload=contract_payload,
                    lock_hint=lock_hint,
                    requires_spellspace=requires_spellspace,
                    owner_conduit_required=owner_conduit_required,
                    must_register=must_register,
                    disposal_method_names=disposal_method_names,
                )
                steps.append(step)
                if spell_id not in spell_id_step_index:
                    spell_id_step_index[spell_id] = len(steps) - 1

        return ExecutionAssemblyPlan(
            root_spell_id=root_spell_id,
            root_instance_key=self._occurrence_plan.root_instance_key,
            steps=steps,
            spell_id_step_index=spell_id_step_index,
            optimistic_object_refs_by_spell_id=optimistic_refs,
            available_param_by_spell_id=available_param_by_spell_id,
            plan_variant=self._plan_variant,
        )

    @staticmethod
    def _creation_target_for_existence(existence: Existence) -> str:
        if existence is Existence.unique_per_conduit:
            return "caller"
        if existence is Existence.unique_per_spell_space:
            return "spellspace"
        if existence is Existence.many:
            return "caller"
        return "owner"

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
                f"Phase 12 ExecutionAssemblyPlan: canonical occurrence missing for '{spell_id}'."
            )
        return canonical

    @staticmethod
    def _extract_param_keys(
            inject_spec: Optional[InjectionSpec],
    ) -> tuple[List[InstanceKey], List[str], List[str]]:
        if inject_spec is None:
            return [], [], []
        dependency_keys: List[InstanceKey] = []
        override_keys: List[str] = []
        contract_keys: List[str] = []
        for source in inject_spec.param_sources.values():
            if source.dependency_keys:
                dependency_keys.extend(source.dependency_keys)
            if source.override_key:
                override_keys.append(source.override_key)
            if source.contract_key:
                contract_keys.append(source.contract_key)
        return dependency_keys, override_keys, contract_keys
