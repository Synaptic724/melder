from typing import Any, Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


InstanceKey = Tuple[str, Optional[int]]


class SpellInjectionParamSource:
    """
    Processor-owned parameter source descriptor.

    Purpose:
        Describe where one injected parameter obtains its value in the fitted
        injection section of `SpellCodegenModel`.

    Contract:
        - `is_collection` carries the phase-3 socket truth
          (`SpellSocketDescriptor.is_collection`) forward so later planner and
          codegen layers can distinguish a one-member collection from single
          DI. It must never be inferred from dependency count: a collection
          socket with exactly one wired provider still injects a list.
    """

    __slots__ = [
        "kind",
        "dependency_keys",
        "override_key",
        "contract_key",
        "is_collection",
    ]

    def __init__(
            self,
            *,
            kind: str,
            dependency_keys: Optional[Tuple[InstanceKey, ...]] = None,
            override_key: Optional[str] = None,
            contract_key: Optional[str] = None,
            is_collection: bool = False,
    ) -> None:
        """
        Build one injection parameter source descriptor.

        Args:
            kind: Source kind ("dependency" or "contract").
            dependency_keys: Instance keys this parameter reads, in order.
            override_key: Root-override key this parameter answers to.
            contract_key: Contract payload key when contract-sourced.
            is_collection: True when the underlying constructor socket is a
                collection DI shape (list[Frame]); the injected value must be
                a list even when exactly one dependency key is present.
        """
        self.kind: str = kind
        self.dependency_keys: Optional[Tuple[InstanceKey, ...]] = dependency_keys
        self.override_key: Optional[str] = override_key
        self.contract_key: Optional[str] = contract_key
        self.is_collection: bool = is_collection


class SpellInjectionInstanceSpec:
    """
    Processor-owned injection spec for one instance key.

    Purpose:
        Hold the per-parameter injection wiring and payload posture for one
        concrete instance key in the fitted model.
    """

    __slots__ = [
        "param_sources",
        "allow_list_aggregation",
        "uses_positional_override",
        "contract_payload",
        "collection_param_names",
    ]

    def __init__(
            self,
            *,
            param_sources: Dict[str, SpellInjectionParamSource],
            allow_list_aggregation: bool,
            uses_positional_override: bool,
            contract_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Build one injection spec for one instance key.

        Contract:
            - `collection_param_names` is derived from the supplied
              param_sources (`is_collection` flags), never from dependency
              counts, so a one-member collection socket stays a collection all
              the way into codegen.
        """
        self.param_sources: Dict[str, SpellInjectionParamSource] = param_sources
        self.allow_list_aggregation: bool = allow_list_aggregation
        self.uses_positional_override: bool = uses_positional_override
        self.contract_payload: Optional[Dict[str, Any]] = contract_payload
        self.collection_param_names: frozenset[str] = frozenset(
            param_name
            for param_name, param_source in param_sources.items()
            if param_source.is_collection
        )


class SpellInjectionAnalysis(Cleanable):
    """
    Processor-owned injection section for one spell.

    Purpose:
        Hold the fitted per-instance injection specs plus the summary facts that
        later planner work will care about.
    """

    __slots__ = Cleanable.__slots__ + [
        "root_spell_id",
        "root_instance_key",
        "instance_specs_by_instance_key",
        "instance_spec_count",
        "root_dependency_count",
        "root_uses_positional_override",
        "positional_override_instance_count",
        "contract_payload_instance_count",
        "list_aggregation_instance_count",
        "param_source_kind_counts",
        "dependency_arity_histogram",
    ]

    def  __init__(
            self,
            *,
            root_spell_id: str,
            root_instance_key: InstanceKey,
            instance_specs_by_instance_key: Dict[InstanceKey, SpellInjectionInstanceSpec],
    ) -> None:
        """
        Build one processor-owned injection section.

        Contract:
            - Computes summary facts directly from the stored instance specs.
            - Treats the supplied mapping as owned section state.
        """
        super().__init__()
        self.root_spell_id: str = root_spell_id
        self.root_instance_key: InstanceKey = root_instance_key
        self.instance_specs_by_instance_key: Dict[InstanceKey, SpellInjectionInstanceSpec] = (
            instance_specs_by_instance_key
        )
        self.instance_spec_count: int = len(instance_specs_by_instance_key)

        root_instance_spec = instance_specs_by_instance_key.get(root_instance_key)
        if root_instance_spec is None:
            self.root_dependency_count = 0
            self.root_uses_positional_override = False
        else:
            self.root_dependency_count = 0
            for param_source in root_instance_spec.param_sources.values():
                if param_source.dependency_keys is not None:
                    self.root_dependency_count += len(param_source.dependency_keys)
            self.root_uses_positional_override = (
                root_instance_spec.uses_positional_override
            )

        positional_override_instance_count = 0
        contract_payload_instance_count = 0
        list_aggregation_instance_count = 0
        param_source_kind_counts: Dict[str, int] = {}
        dependency_arity_histogram: Dict[int, int] = {}

        for instance_spec in instance_specs_by_instance_key.values():
            if instance_spec.uses_positional_override:
                positional_override_instance_count += 1
            if instance_spec.contract_payload:
                contract_payload_instance_count += 1
            if instance_spec.allow_list_aggregation:
                list_aggregation_instance_count += 1
            for param_source in instance_spec.param_sources.values():
                param_source_kind_counts[param_source.kind] = (
                    param_source_kind_counts.get(param_source.kind, 0) + 1
                )
                dependency_keys = param_source.dependency_keys
                if dependency_keys is None:
                    continue
                arity = len(dependency_keys)
                dependency_arity_histogram[arity] = (
                    dependency_arity_histogram.get(arity, 0) + 1
                )

        self.positional_override_instance_count = positional_override_instance_count
        self.contract_payload_instance_count = contract_payload_instance_count
        self.list_aggregation_instance_count = list_aggregation_instance_count
        self.param_source_kind_counts = tuple(sorted(param_source_kind_counts.items()))
        self.dependency_arity_histogram = tuple(
            sorted(dependency_arity_histogram.items())
        )

    def cleanup(self) -> None:
        """
        Deterministically release owned injection section data.
        """
        if self._cleaned:
            return
        self._cleaned = True

        for instance_spec in self.instance_specs_by_instance_key.values():
            instance_spec.param_sources.clear()
            contract_payload = instance_spec.contract_payload
            if contract_payload is not None:
                contract_payload.clear()
        self.instance_specs_by_instance_key.clear()

        del self.root_spell_id
        del self.root_instance_key
        del self.instance_specs_by_instance_key
        del self.instance_spec_count
        del self.root_dependency_count
        del self.root_uses_positional_override
        del self.positional_override_instance_count
        del self.contract_payload_instance_count
        del self.list_aggregation_instance_count
        del self.param_source_kind_counts
        del self.dependency_arity_histogram
