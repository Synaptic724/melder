from typing import Any, Dict, List, Mapping, Optional, Tuple

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ioccurrenceplan import IOccurrencePlan
from melder.utilities.interfaces.iinjectionspec import IInjectionSpec
from melder.utilities.interfaces.iinjectionplan import IInjectionPlan
from melder.utilities.interfaces.iparamsource import IParamSource

OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]
@mypyc_attr(native_class=True)
class ParamSource(IParamSource):
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
                Override identifier for value-based injection, when applicable.
            contract_key:
                Contract identifier for spell-contract injection, when applicable.

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

@mypyc_attr(native_class=True)
class InjectionSpec(IInjectionSpec):
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
        - contract_payload is stored by reference and treated as immutable
          by the runtime.

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
        "_contract_payload",
    ]

    def __init__(
            self,
            *,
            param_sources: Dict[str, ParamSource],
            allow_list_aggregation: bool,
            uses_positional_override: bool,
            contract_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a per-instance injection specification.

        Contract:
            - param_sources must be non-None.
            - The mapping is stored by reference; callers must not mutate it.
            - contract_payload is stored by reference; callers must not mutate it.

        Args:
            param_sources:
                Mapping from parameter name to ParamSource.
            allow_list_aggregation:
                True when at least one parameter requires list aggregation.
            uses_positional_override:
                True if the override payload should be interpreted positionally.
            contract_payload:
                Optional SpellContract override payload for this instance.

        Raises:
            ValueError:
                If param_sources is None.
        """
        if param_sources is None:
            raise ValueError("param_sources must not be None.")
        self._param_sources: Dict[str, ParamSource] = param_sources
        self._allow_list_aggregation: bool = allow_list_aggregation
        self._uses_positional_override: bool = uses_positional_override
        self._contract_payload: Optional[Dict[str, Any]] = contract_payload

    @property
    def param_sources(self) -> Mapping[str, IParamSource]:
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

    @property
    def contract_payload(self) -> Optional[Dict[str, Any]]:
        """
        Return the SpellContract override payload for this instance.

        Contract:
            - The returned mapping is the stored reference; treat as read-only.

        Returns:
            Optional[Dict[str, Any]]: Contract override payload or None.
        """
        return self._contract_payload


def build_kwargs_from_injection_spec(
        *,
        instance_key: InstanceKey,
        occurrence: OccurrenceKey,
        injection_spec: IInjectionSpec,
        instance_results: Dict[InstanceKey, Any],
        override_values: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build keyword arguments for a spell instance using a Phase 9 InjectionSpec.

    Contract:
        - Returns a new kwargs mapping.
        - Raises MeldExecutionError when dependency instances are missing.

    Args:
        instance_key: Instance key being constructed.
        occurrence: (spell_id, path) occurrence for the instance.
        injection_spec: Phase 9 injection specification.
        instance_results: Mapping of instance keys to resolved instances.
        override_values: Precomputed override values for the instance.

    Returns:
        Dict[str, Any]: Keyword arguments for construction.
    """
    spell_id, _ = occurrence
    contract_payload = injection_spec.contract_payload
    positional_override = None
    if (
            contract_payload is not None
            and injection_spec.uses_positional_override
            and "__args__" in contract_payload
    ):
        raw_args = contract_payload["__args__"]
        if not isinstance(raw_args, (list, tuple)):
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell_id,
                node_id=spell_id,
                message="Contract payload __args__ must be a list or tuple.",
            )
        positional_override = tuple(raw_args)

    kwargs: Dict[str, Any] = {}
    for param_name, param_source in injection_spec.param_sources.items():
        if param_source.kind != "dependency":
            continue
        dependency_keys = param_source.dependency_keys
        if dependency_keys is None:
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell_id,
                node_id=spell_id,
                message=(
                    "Dependency param source is missing dependency_keys while "
                    f"building injection kwargs for {param_name!r}."
                ),
            )
        if param_name in override_values:
            kwargs[param_name] = override_values[param_name]
            continue
        values: List[Any] = []
        for dependency_key in dependency_keys:
            if dependency_key not in instance_results:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    message=(
                        "Missing dependency instance for "
                        f"{dependency_key!r} while building injection kwargs."
                    ),
                )
            values.append(instance_results[dependency_key])
        if not values:
            continue
        if len(values) == 1:
            kwargs[param_name] = values[0]
        else:
            kwargs[param_name] = values

    if positional_override is not None:
        kwargs["__args__"] = positional_override

    if contract_payload:
        for param_name, value in contract_payload.items():
            if param_name == "__args__" and injection_spec.uses_positional_override:
                continue
            if param_name in override_values:
                continue
            kwargs[param_name] = value

    for param_name, value in override_values.items():
        if param_name not in kwargs:
            kwargs[param_name] = value

    return kwargs

@mypyc_attr(native_class=True)
class InjectionPlan(Cleanable, IInjectionPlan):
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
        self._root_spell_id: str = root_spell_id
        self._instance_injections: Dict[InstanceKey, InjectionSpec] = instance_injections

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

        del self._root_spell_id
        del self._instance_injections

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
    def instance_injections(self) -> Mapping[InstanceKey, IInjectionSpec]:
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

    def select_for_runtime(
            self,
            *,
            root_spell_id: str,
    ) -> Optional[Mapping[InstanceKey, IInjectionSpec]]:
        """
        Determine whether this Phase 9 plan can drive a meld execution.

        Contract:
            - Returns None if the plan root does not match.
            - Returns None if the plan has been cleaned.

        Args:
            root_spell_id: Current root spell id for this execution.

        Returns:
            Optional[Dict[InstanceKey, InjectionSpec]]: Injection specs when usable.
        """
        if self._cleaned:
            return None
        if root_spell_id != self._root_spell_id:
            return None
        return self._instance_injections

@mypyc_attr(native_class=True)
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

    @staticmethod
    def _clone_contract_payload(
            payload: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Clone contract payloads for plan-local ownership.

        Contract:
            - Returns None when payload is None.
            - Returns a shallow dict copy otherwise.
            - Normalizes __args__ list payloads to tuples.
        """
        if payload is None:
            return None
        cloned_payload = dict(payload)
        if "__args__" in cloned_payload and isinstance(cloned_payload["__args__"], list):
            cloned_payload["__args__"] = tuple(cloned_payload["__args__"])
        return cloned_payload

    def __init__(
            self,
            *,
            occurrence_plan: IOccurrencePlan,
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
            - uses_positional_override is True when a contract payload includes
              __args__ for the instance.
            - Missing contract override entries are treated as no payloads.

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
            if spell_id in shared_spell_ids:
                canonical_occurrence = plan.canonical_occurrences_by_spell_id[spell_id]
                for instance_key in instance_keys:
                    occurrence = canonical_occurrence
                    dependencies = plan.occurrence_graph[occurrence]
                    contract_payload = plan.contract_overrides_by_occurrence.get(occurrence)
                    normalized_contract_payload = self._clone_contract_payload(contract_payload)
                    param_sources: Dict[str, ParamSource] = {}
                    allow_list_aggregation = False
                    uses_positional_override = False

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
                            override_key=param_name,
                        )

                    if normalized_contract_payload is not None:
                        if "__args__" in normalized_contract_payload:
                            uses_positional_override = True
                        for param_name in normalized_contract_payload.keys():
                            if param_name == "__args__":
                                continue
                            existing = param_sources.get(param_name)
                            if existing is None:
                                param_sources[param_name] = ParamSource(
                                    kind="contract",
                                    dependency_keys=[],
                                    override_key=param_name,
                                    contract_key=param_name,
                                )
                            else:
                                param_sources[param_name] = ParamSource(
                                    kind=existing.kind,
                                    dependency_keys=existing.dependency_keys,
                                    override_key=existing.override_key or param_name,
                                    contract_key=param_name,
                                )

                    instance_injections[instance_key] = InjectionSpec(
                        param_sources=param_sources,
                        allow_list_aggregation=allow_list_aggregation,
                        uses_positional_override=uses_positional_override,
                        contract_payload=normalized_contract_payload,
                    )
                continue

            for instance_key in instance_keys:
                occurrence_path = instance_key[1]
                if occurrence_path is None:
                    raise RuntimeError(
                        "Non-shared instance key is missing its occurrence path."
                    )
                instance_occurrence: OccurrenceKey = (spell_id, occurrence_path)
                dependencies = plan.occurrence_graph[instance_occurrence]
                contract_payload = plan.contract_overrides_by_occurrence.get(instance_occurrence)
                normalized_contract_payload = self._clone_contract_payload(contract_payload)
                instance_param_sources: Dict[str, ParamSource] = {}
                allow_list_aggregation = False
                uses_positional_override = False

                for param_name, dependency_occurrences in dependencies.items():
                    instance_dependency_keys: List[InstanceKey] = []
                    for dependency_occurrence in dependency_occurrences:
                        dependency_spell_id, dependency_path = dependency_occurrence
                        if dependency_spell_id in shared_spell_ids:
                            instance_dependency_keys.append((dependency_spell_id, None))
                        else:
                            instance_dependency_keys.append((dependency_spell_id, dependency_path))
                    if len(instance_dependency_keys) > 1:
                        allow_list_aggregation = True
                    instance_param_sources[param_name] = ParamSource(
                        kind="dependency",
                        dependency_keys=instance_dependency_keys,
                        override_key=param_name,
                    )

                if normalized_contract_payload is not None:
                    if "__args__" in normalized_contract_payload:
                        uses_positional_override = True
                    for param_name in normalized_contract_payload.keys():
                        if param_name == "__args__":
                            continue
                        existing = instance_param_sources.get(param_name)
                        if existing is None:
                            instance_param_sources[param_name] = ParamSource(
                                kind="contract",
                                dependency_keys=[],
                                override_key=param_name,
                                contract_key=param_name,
                            )
                        else:
                            instance_param_sources[param_name] = ParamSource(
                                kind=existing.kind,
                                dependency_keys=existing.dependency_keys,
                                override_key=existing.override_key or param_name,
                                contract_key=param_name,
                            )

                instance_injections[instance_key] = InjectionSpec(
                    param_sources=instance_param_sources,
                    allow_list_aggregation=allow_list_aggregation,
                    uses_positional_override=uses_positional_override,
                    contract_payload=normalized_contract_payload,
                )

        return InjectionPlan(
            root_spell_id=plan.root_spell_id,
            instance_injections=instance_injections,
        )
