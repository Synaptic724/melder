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

    Purpose:
        Describe where a single constructor parameter should obtain its value
        during meld execution (dependencies, overrides, or contracts).

    Contract:
        - kind is required and stored verbatim (no normalization).
        - dependency_keys, override_key, and contract_key are optional and may be None.
        - This object is treated as immutable after construction.
        - This object does not own any referenced plan or spell objects.

    Threading:
        - Not thread-safe; treat as immutable after build.

    Lifecycle:
        - No cleanup required; normal GC.
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
        """
        Initialize a parameter source descriptor.

        Contract:
            - kind must be non-None.
            - Optional fields are stored by reference without copying.
            - No validation of kind semantics is performed here.

        Args:
            kind:
                Source kind identifier (e.g., "dependency", "override", "contract").
            dependency_keys:
                Instance keys for dependency-based injection, when applicable.
            override_key:
                Raw override key for value-based injection, when applicable.
            contract_key:
                Contract lookup key for spell-contract injection, when applicable.

        Raises:
            ValueError:
                If kind is None.
        """
        if kind is None:
            raise ValueError("kind must not be None.")
        self._kind = kind
        self._dependency_keys = dependency_keys
        self._override_key = override_key
        self._contract_key = contract_key

    @property
    def kind(self) -> str:
        """
        Return the source kind for this parameter.

        Contract:
            - Returns the exact value provided at construction.

        Returns:
            str: Source kind identifier.
        """
        return self._kind

    @property
    def dependency_keys(self) -> Optional[List[InstanceKey]]:
        """
        Return dependency instance keys for this parameter, if any.

        Contract:
            - The returned list is the stored reference; treat as read-only.

        Returns:
            Optional[List[InstanceKey]]:
                Instance keys used to resolve dependency values, or None.
        """
        return self._dependency_keys

    @property
    def override_key(self) -> Optional[str]:
        """
        Return the override key for this parameter, if any.

        Returns:
            Optional[str]:
                Override key string, or None when not applicable.
        """
        return self._override_key

    @property
    def contract_key(self) -> Optional[str]:
        """
        Return the contract lookup key for this parameter, if any.

        Returns:
            Optional[str]:
                Contract key string, or None when not applicable.
        """
        return self._contract_key


class InjectionSpec:
    """
    Internal

    Phase 9 InjectionPlan entry for a single instance key.

    Purpose:
        Capture per-parameter sourcing metadata for a single instance key.

    Contract:
        - param_sources is required and stored by reference.
        - allow_list_aggregation indicates at least one parameter has multiple
          dependency keys.
        - uses_positional_override is a flag the runtime may consult for
          override semantics; no validation is performed here.

    Threading:
        - Not thread-safe; treat as immutable after build.

    Lifecycle:
        - No cleanup required; normal GC.
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
        """
        Initialize a per-instance injection specification.

        Contract:
            - param_sources must be non-None.
            - The mapping is stored by reference; callers must not mutate it.

        Args:
            param_sources:
                Mapping from parameter name to ParamSource.
            allow_list_aggregation:
                True when at least one parameter requires list aggregation.
            uses_positional_override:
                True if the override payload should be interpreted positionally.

        Raises:
            ValueError:
                If param_sources is None.
        """
        if param_sources is None:
            raise ValueError("param_sources must not be None.")
        self._param_sources = param_sources
        self._allow_list_aggregation = allow_list_aggregation
        self._uses_positional_override = uses_positional_override

    @property
    def param_sources(self) -> Dict[str, ParamSource]:
        """
        Return the parameter source mapping.

        Contract:
            - The returned mapping is the stored reference; treat as read-only.

        Returns:
            Dict[str, ParamSource]: Parameter source mapping.
        """
        return self._param_sources

    @property
    def allow_list_aggregation(self) -> bool:
        """
        Return whether list aggregation is allowed for this instance.

        Returns:
            bool: True when at least one parameter has multiple dependencies.
        """
        return self._allow_list_aggregation

    @property
    def uses_positional_override(self) -> bool:
        """
        Return whether positional overrides are expected.

        Returns:
            bool: True if positional override semantics are enabled.
        """
        return self._uses_positional_override


class InjectionPlan(Cleanable):
    """
    Internal

    Phase 9 artifact that captures dependency-to-parameter wiring for each
    instance key.

    Purpose:
        Provide a precomputed mapping from instance keys to parameter wiring
        so meld does not rebuild injection metadata per call.

    Contract:
        - root_spell_id identifies the root spell used to compile the plan.
        - instance_injections is owned by this plan and cleared on cleanup.
        - Accessors call check_cleaned and raise if the plan is cleaned.

    Threading:
        - Not thread-safe; treat as immutable after build.

    Lifecycle:
        - cleanup() is idempotent and clears owned collections.
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
        """
        Initialize a Phase 9 injection plan.

        Contract:
            - All inputs must be non-None.
            - Inputs are stored by reference and treated as owned.
            - Callers must not mutate inputs after construction.

        Args:
            root_spell_id:
                Version id of the root spell used to build the plan.
            instance_injections:
                Mapping from instance key to InjectionSpec.

        Raises:
            ValueError:
                If any required input is None.
        """
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if instance_injections is None:
            raise ValueError("instance_injections must not be None.")
        self._root_spell_id = root_spell_id
        self._instance_injections = instance_injections

    def cleanup(self) -> None:
        """
        Deterministically tear down the plan and owned collections.

        Contract:
            - Idempotent: safe to call multiple times.
            - Clears owned containers and nulls references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._instance_injections.clear()
        self._root_spell_id = None
        self._instance_injections = None

    @property
    def root_spell_id(self) -> str:
        """
        Return the root spell id for this plan.

        Contract:
            - Raises if the plan has been cleaned.

        Returns:
            str: Root spell version id.

        Raises:
            RuntimeError:
                If the plan has been cleaned.
        """
        self.check_cleaned()
        return self._root_spell_id

    @property
    def instance_injections(self) -> Dict[InstanceKey, InjectionSpec]:
        """
        Return the injection spec mapping by instance key.

        Contract:
            - The returned mapping is owned by the plan and should be treated
              as read-only by callers.

        Returns:
            Dict[InstanceKey, InjectionSpec]: Injection specs per instance key.

        Raises:
            RuntimeError:
                If the plan has been cleaned.
        """
        self.check_cleaned()
        return self._instance_injections


class InjectionPlanBuilder(object):
    """
    Internal

    Phase 9 compiler that precomputes parameter wiring for each instance key.

    Purpose:
        Convert a Phase 8 OccurrencePlan into per-instance injection metadata.

    Contract:
        - Does not mutate the provided OccurrencePlan.
        - Uses shared instance keys for shared spell ids.
        - Skips shared instances when no canonical occurrence exists.

    Threading:
        - Not thread-safe; use from a single planner thread.

    Lifecycle:
        - Builder does not own the OccurrencePlan and performs no cleanup.
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
        """
        Initialize the injection plan builder.

        Contract:
            - occurrence_plan must be non-None.
            - The plan reference is stored as-is; no copy is made.

        Args:
            occurrence_plan:
                Phase 8 plan used as the input for injection metadata.

        Raises:
            ValueError:
                If occurrence_plan is None.
        """
        if occurrence_plan is None:
            raise ValueError("occurrence_plan must not be None.")
        self._occurrence_plan = occurrence_plan

    def build(self) -> InjectionPlan:
        """
        Build an InjectionPlan from the stored OccurrencePlan.

        Contract:
            - For shared spell ids, dependency instance keys use (spell_id, None).
            - For non-shared spell ids, dependency instance keys include the path.
            - allow_list_aggregation is True when any parameter has multiple
              dependency occurrences.
            - uses_positional_override is False for all specs produced here.

        Returns:
            InjectionPlan: Compiled plan for the root spell.

        Raises:
            RuntimeError:
                If the underlying OccurrencePlan has been cleaned.
        """
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
