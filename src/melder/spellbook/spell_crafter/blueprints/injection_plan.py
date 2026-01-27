from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    InstanceKey,
    OccurrencePlan,
)
from melder.utilities.general_base.cleanable import Cleanable


class ParamSource:
    """
    Internal

    Phase 9 parameter source descriptor for an InjectionPlan.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_kind",
        "_dependency_keys",
        "_override_key",
        "_contract_key",
    ]

    def __init__(
            self,
            *,
            kind: str,
            dependency_keys: Optional[List[InstanceKey]] = None,
            override_key: Optional[str] = None,
            contract_key: Optional[str] = None,
    ) -> None:
        if kind is None:
            raise ValueError("kind must not be None.")
        self._kind = kind
        self._dependency_keys = dependency_keys
        self._override_key = override_key
        self._contract_key = contract_key

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def dependency_keys(self) -> Optional[List[InstanceKey]]:
        return self._dependency_keys

    @property
    def override_key(self) -> Optional[str]:
        return self._override_key

    @property
    def contract_key(self) -> Optional[str]:
        return self._contract_key


class InjectionSpec:
    """
    Internal

    Phase 9 InjectionPlan entry for a single instance key.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_param_sources",
        "_allow_list_aggregation",
        "_uses_positional_override",
    ]

    def __init__(
            self,
            *,
            param_sources: Dict[str, ParamSource],
            allow_list_aggregation: bool,
            uses_positional_override: bool,
    ) -> None:
        if param_sources is None:
            raise ValueError("param_sources must not be None.")
        self._param_sources = param_sources
        self._allow_list_aggregation = allow_list_aggregation
        self._uses_positional_override = uses_positional_override

    @property
    def param_sources(self) -> Dict[str, ParamSource]:
        return self._param_sources

    @property
    def allow_list_aggregation(self) -> bool:
        return self._allow_list_aggregation

    @property
    def uses_positional_override(self) -> bool:
        return self._uses_positional_override


class InjectionPlan(Cleanable):
    """
    Internal

    Phase 9 artifact that captures dependency-to-parameter wiring for each
    instance key.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_instance_injections",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            instance_injections: Dict[InstanceKey, InjectionSpec],
    ) -> None:
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if instance_injections is None:
            raise ValueError("instance_injections must not be None.")
        self._root_spell_id = root_spell_id
        self._instance_injections = instance_injections

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        self._instance_injections.clear()
        self._root_spell_id = None
        self._instance_injections = None

    @property
    def root_spell_id(self) -> str:
        self.check_cleaned()
        return self._root_spell_id

    @property
    def instance_injections(self) -> Dict[InstanceKey, InjectionSpec]:
        self.check_cleaned()
        return self._instance_injections


class InjectionPlanBuilder(object):
    """
    Internal

    Phase 9 compiler that precomputes parameter wiring for each instance key.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_occurrence_plan",
    ]

    def __init__(
            self,
            *,
            occurrence_plan: OccurrencePlan,
    ) -> None:
        if occurrence_plan is None:
            raise ValueError("occurrence_plan must not be None.")
        self._occurrence_plan = occurrence_plan

    def build(self) -> InjectionPlan:
        plan = self._occurrence_plan
        instance_injections: Dict[InstanceKey, InjectionSpec] = {}
        shared_spell_ids = plan.shared_spell_ids

        for spell_id, instance_keys in plan.instance_keys_by_spell_id.items():
            canonical_occurrence = plan.canonical_occurrences_by_spell_id.get(spell_id)
            for instance_key in instance_keys:
                if instance_key[1] is None:
                    if canonical_occurrence is None:
                        continue
                    occurrence = canonical_occurrence
                else:
                    occurrence = (spell_id, instance_key[1])
                dependencies = plan.occurrence_graph.get(occurrence, {})
                param_sources: Dict[str, ParamSource] = {}
                allow_list_aggregation = False

                for param_name, dependency_occurrences in dependencies.items():
                    dependency_keys: List[InstanceKey] = []
                    for dependency_occurrence in dependency_occurrences:
                        dependency_spell_id, dependency_path = dependency_occurrence
                        if dependency_spell_id in shared_spell_ids:
                            dependency_keys.append((dependency_spell_id, None))
                        else:
                            dependency_keys.append((dependency_spell_id, dependency_path))
                    if len(dependency_keys) > 1:
                        allow_list_aggregation = True
                    param_sources[param_name] = ParamSource(
                        kind="dependency",
                        dependency_keys=dependency_keys,
                    )

                instance_injections[instance_key] = InjectionSpec(
                    param_sources=param_sources,
                    allow_list_aggregation=allow_list_aggregation,
                    uses_positional_override=False,
                )

        return InjectionPlan(
            root_spell_id=plan.root_spell_id,
            instance_injections=instance_injections,
        )
