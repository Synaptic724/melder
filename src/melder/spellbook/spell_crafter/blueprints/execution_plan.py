from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.injection_plan import InjectionPlan, InjectionSpec
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    InstanceKey,
    OccurrenceKey,
    OccurrencePlan,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell


class ExecutionPlanStep:
    """
    Internal

    Phase 11 execution step metadata.

    Purpose:
        Capture precomputed execution metadata needed for the strict best-case
        executor described in the Phase 11 artifacts.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_spell_id",
        "_instance_key",
        "_occurrence",
        "_existence",
        "_creation_target",
        "_action",
        "_inject_spec",
        "_register",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            instance_key: InstanceKey,
            occurrence: OccurrenceKey,
            existence: Existence,
            creation_target: str,
            action: str,
            inject_spec: Optional[InjectionSpec],
            register: bool,
    ) -> None:
        """
        Initialize a Phase 11 execution step.

        Contract:
            - All inputs must be non-None except inject_spec (optional).
            - Stores values by reference and treats them as immutable.

        Args:
            spell_id: Spell version id to execute.
            instance_key: Instance key for the step.
            occurrence: Occurrence used for dependency lookup.
            existence: Existence policy for the spell.
            creation_target: Target creations container label.
            action: "reuse" or "construct" execution action.
            inject_spec: Optional Phase 9 injection spec for kwargs wiring.
            register: Whether the step should register the constructed instance.
        """
        if spell_id is None:
            raise ValueError("spell_id must not be None.")
        if instance_key is None:
            raise ValueError("instance_key must not be None.")
        if occurrence is None:
            raise ValueError("occurrence must not be None.")
        if existence is None:
            raise ValueError("existence must not be None.")
        if creation_target is None:
            raise ValueError("creation_target must not be None.")
        if action is None:
            raise ValueError("action must not be None.")
        if register is None:
            raise ValueError("register must not be None.")

        self._spell_id = spell_id
        self._instance_key = instance_key
        self._occurrence = occurrence
        self._existence = existence
        self._creation_target = creation_target
        self._action = action
        self._inject_spec = inject_spec
        self._register = register

    @property
    def spell_id(self) -> str:
        """
        Spell version id for this execution step.
        """
        return self._spell_id

    @property
    def instance_key(self) -> InstanceKey:
        """
        Instance key for this execution step.
        """
        return self._instance_key

    @property
    def occurrence(self) -> OccurrenceKey:
        """
        Occurrence used for dependency lookup.
        """
        return self._occurrence

    @property
    def existence(self) -> Existence:
        """
        Existence policy for this step.
        """
        return self._existence

    @property
    def creation_target(self) -> str:
        """
        Creation target label for this step.
        """
        return self._creation_target

    @property
    def action(self) -> str:
        """
        Execution action for this step.
        """
        return self._action

    @property
    def inject_spec(self) -> Optional[InjectionSpec]:
        """
        Optional Phase 9 injection spec for kwargs wiring.
        """
        return self._inject_spec

    @property
    def register(self) -> bool:
        """
        Whether the step should register the constructed instance.
        """
        return self._register


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


class ExecutionPlan(Cleanable):
    """
    Internal

    Phase 11 artifact that captures a flat list of execution steps for a root spell.

    Purpose:
        Provide a precompiled, best-case execution plan that can be consumed by
        a fast-path executor once gating rules allow it. The plan carries
        contract override payloads, shared-spell metadata, and mutation
        override snapshots needed to execute without rebuilding routing data.
        Each plan is tagged with a variant label to support override-aware
        selection at meld time.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_root_instance_key",
        "_steps",
        "_contract_overrides_by_occurrence",
        "_contract_overrides_by_spell_id",
        "_shared_spell_ids",
        "_contract_dependencies_complete",
        "_mutation_override_payload",
        "_plan_variant",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            root_instance_key: InstanceKey,
            steps: List[ExecutionPlanStep],
            contract_overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, object]],
            contract_overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, object]]]],
            shared_spell_ids: List[str],
            contract_dependencies_complete: bool,
            mutation_override_payload: Dict[str, object],
            plan_variant: str,
    ) -> None:
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if root_instance_key is None:
            raise ValueError("root_instance_key must not be None.")
        if steps is None:
            raise ValueError("steps must not be None.")
        if contract_overrides_by_occurrence is None:
            raise ValueError("contract_overrides_by_occurrence must not be None.")
        if contract_overrides_by_spell_id is None:
            raise ValueError("contract_overrides_by_spell_id must not be None.")
        if shared_spell_ids is None:
            raise ValueError("shared_spell_ids must not be None.")
        if contract_dependencies_complete is None:
            raise ValueError("contract_dependencies_complete must not be None.")
        if mutation_override_payload is None:
            raise ValueError("mutation_override_payload must not be None.")
        if plan_variant is None:
            raise ValueError("plan_variant must not be None.")

        self._root_spell_id = root_spell_id
        self._root_instance_key = root_instance_key
        self._steps = steps
        self._contract_overrides_by_occurrence = contract_overrides_by_occurrence
        self._contract_overrides_by_spell_id = contract_overrides_by_spell_id
        self._shared_spell_ids = shared_spell_ids
        self._contract_dependencies_complete = contract_dependencies_complete
        self._mutation_override_payload = mutation_override_payload
        self._plan_variant = plan_variant

    def cleanup(self) -> None:
        """
        Deterministically tear down owned collections.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._steps.clear()
        self._contract_overrides_by_occurrence.clear()
        self._contract_overrides_by_spell_id.clear()
        self._shared_spell_ids.clear()
        self._mutation_override_payload.clear()
        self._contract_overrides_by_occurrence = None
        self._contract_overrides_by_spell_id = None
        self._shared_spell_ids = None
        self._contract_dependencies_complete = None
        self._mutation_override_payload = None
        self._plan_variant = None

    @property
    def root_spell_id(self) -> str:
        return self._root_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        return self._root_instance_key

    @property
    def steps(self) -> Sequence[ExecutionPlanStep]:
        return self._steps

    @property
    def contract_overrides_by_occurrence(self) -> Dict[OccurrenceKey, Dict[str, object]]:
        return self._contract_overrides_by_occurrence

    @property
    def contract_overrides_by_spell_id(self) -> Dict[str, List[Tuple[OccurrenceKey, Dict[str, object]]]]:
        return self._contract_overrides_by_spell_id

    @property
    def shared_spell_ids(self) -> Sequence[str]:
        return self._shared_spell_ids

    @property
    def contract_dependencies_complete(self) -> bool:
        return self._contract_dependencies_complete

    @property
    def mutation_override_payload(self) -> Dict[str, object]:
        return self._mutation_override_payload

    @property
    def plan_variant(self) -> str:
        """
        Execution plan variant label for selection gating.
        """
        return self._plan_variant


class ExecutionPlanBuilder:
    """
    Internal

    Build a Phase 11 ExecutionPlan from Phase 8/9 artifacts.
    """
    __melder_internal__ = _mrg.sentinel

    def __init__(
            self,
            *,
            occurrence_plan: OccurrencePlan,
            injection_plan: Optional[InjectionPlan],
            spell_lookup: Dict[str, ISpell],
            mutation_override_payload: Optional[Dict[str, object]],
            plan_variant: str,
    ) -> None:
        if occurrence_plan is None:
            raise ValueError("occurrence_plan must not be None.")
        if spell_lookup is None:
            raise ValueError("spell_lookup must not be None.")
        if mutation_override_payload is None:
            mutation_override_payload = {}
        if plan_variant is None:
            raise ValueError("plan_variant must not be None.")

        self._occurrence_plan = occurrence_plan
        self._injection_plan = injection_plan
        self._spell_lookup = spell_lookup
        self._mutation_override_payload = mutation_override_payload
        self._plan_variant = plan_variant

    def build(self) -> ExecutionPlan:
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

        for spell_id in self._occurrence_plan.execution_order:
            spell = self._spell_lookup.get(spell_id)
            if spell is None:
                raise ValueError(
                    f"Phase 11 ExecutionPlan: spell id '{spell_id}' missing from lookup."
                )

            for instance_key in self._occurrence_plan.instance_keys_by_spell_id.get(spell_id, []):
                occurrence = self._occurrence_for_instance_key(instance_key)
                inject_spec = None
                if injection_lookup is not None:
                    inject_spec = injection_lookup.get(instance_key)

                existence = spell.existence
                action = self._action_for_existence(existence)
                creation_target = self._creation_target_for_existence(existence)
                register = self._should_register(spell)

                steps.append(
                    ExecutionPlanStep(
                        spell_id=spell_id,
                        instance_key=instance_key,
                        occurrence=occurrence,
                        existence=existence,
                        creation_target=creation_target,
                        action=action,
                        inject_spec=inject_spec,
                        register=register,
                    )
                )

        contract_overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, object]] = {}
        for occurrence, payload in self._occurrence_plan.contract_overrides_by_occurrence.items():
            contract_overrides_by_occurrence[occurrence] = dict(payload) if payload else {}

        contract_overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, object]]]] = {}
        for spell_id, overrides in self._occurrence_plan.contract_overrides_by_spell_id.items():
            contract_overrides_by_spell_id[spell_id] = [
                (occurrence, dict(payload) if payload else {})
                for occurrence, payload in overrides
            ]

        shared_spell_ids = list(self._occurrence_plan.shared_spell_ids)

        return ExecutionPlan(
            root_spell_id=root_spell_id,
            root_instance_key=self._occurrence_plan.root_instance_key,
            steps=steps,
            contract_overrides_by_occurrence=contract_overrides_by_occurrence,
            contract_overrides_by_spell_id=contract_overrides_by_spell_id,
            shared_spell_ids=shared_spell_ids,
            contract_dependencies_complete=self._occurrence_plan.contract_dependencies_complete,
            mutation_override_payload=dict(self._mutation_override_payload),
            plan_variant=self._plan_variant,
        )

    @staticmethod
    def _action_for_existence(existence: Existence) -> str:
        if existence is Existence.many:
            return "construct"
        return "reuse"

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
