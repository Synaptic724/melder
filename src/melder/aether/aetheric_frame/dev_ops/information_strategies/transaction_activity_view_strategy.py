from typing import TYPE_CHECKING, Dict, List

from melder.aether.aetheric_frame.dev_ops.devops_information_strategy import (
    DevopsInformationStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.information_strategy_support import (
    InformationFreshnessInspector,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class TransactionActivityViewStrategy(DevopsInformationStrategy):
    """
    Registry-backed view of live transaction activity along one axis.

    Purpose:
        Answer "who and what is doing something right now" for one identity,
        one scope, or one transaction type without touching the mediator or
        any live runtime objects.

    Why this exists:
        The admission plane records every in-flight transaction in the
        registry's reverse indexes. Agents deciding whether to start risky
        work (transfer, mutation) want the current activity picture for their
        target before claiming scopes; this strategy is that read.

    Contract:
        - Axis selection comes from metadata, first match wins:
          `identity_kind` + `identity_id`, else `scope_key`, else
          `transaction_type`. At least one axis is required.
        - Returns transaction ids only (no live objects) plus a freshness
          block for the touched region when the axis names one.
        - Honors optional `max_age_in_seconds` staleness tolerance.

    Threading:
        Stateless static strategy; reads the registry's reverse indexes through
        its public API.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the information
        family; resolved by name through `DevopsInformationStrategyBuilder`.

    Subsystem Context:
        The live-activity read of the catalog. It deliberately never touches
        the mediator - the registry's reverse indexes already carry every
        in-flight transaction, so this view needs no admission-plane access.

    System Context:
        This strategy exists for a specific decision: whether to START risky
        work. An agent about to transfer ownership or run a mutation wants to
        know what is already in flight against its target BEFORE claiming
        scopes, because discovering the conflict at acquisition time means a
        blocked or timed-out transaction rather than a deferred one.
        First-match axis selection (identity, else scope key, else transaction
        type) keeps that query cheap and unambiguous - each axis is a direct
        index lookup rather than a scan, and requiring at least one axis
        prevents an accidental whole-registry dump.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Registry-backed view of live transaction activity along one axis. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    @staticmethod
    def execute(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build one detached transaction-activity view.

        Args:
            devops_information_registry:
                Live mirrored DevOps registry to consume.
            metadata:
                Axis selection plus optional `max_age_in_seconds`:
                - "identity_kind" + "identity_id": activity for one identity.
                - "scope_key": activity indexed under one scope key.
                - "transaction_type": activity for one transaction family.

        Returns:
            Dict[str, object]: {"strategy", "axis", "axis_value",
            "transaction_ids", "transaction_count", "freshness"}.

        Raises:
            ValueError: If no axis is supplied or an axis value is empty.
        """
        identity_kind = metadata.get("identity_kind")
        identity_id = metadata.get("identity_id")
        scope_key = metadata.get("scope_key")
        transaction_type = metadata.get("transaction_type")
        max_age = InformationFreshnessInspector.read_optional_max_age(metadata)

        regions: List[str] = []
        if identity_kind is not None or identity_id is not None:
            if not identity_kind or not identity_id:
                raise ValueError(
                    "identity_kind and identity_id must both be supplied."
                )
            transaction_ids = (
                devops_information_registry.list_transaction_ids_for_identity(
                    owner_kind=str(identity_kind),
                    owner_id=str(identity_id),
                )
            )
            axis = "identity"
            axis_value = f"{identity_kind}:{identity_id}"
            regions.append(axis_value)
        elif scope_key is not None:
            if not scope_key:
                raise ValueError("scope_key must not be empty.")
            transaction_ids = (
                devops_information_registry.list_transaction_ids_for_scope(
                    str(scope_key)
                )
            )
            axis = "scope"
            axis_value = str(scope_key)
            regions.append(
                InformationFreshnessInspector.normalize_region(str(scope_key))
            )
        elif transaction_type is not None:
            if not transaction_type:
                raise ValueError("transaction_type must not be empty.")
            transaction_ids = (
                devops_information_registry.list_transaction_ids_for_type(
                    str(transaction_type)
                )
            )
            axis = "transaction_type"
            axis_value = str(transaction_type)
        else:
            raise ValueError(
                "transaction_activity_view requires one axis: identity_kind+"
                "identity_id, scope_key, or transaction_type."
            )

        return {
            "strategy": "transaction_activity_view",
            "axis": axis,
            "axis_value": axis_value,
            "transaction_ids": tuple(sorted(transaction_ids)),
            "transaction_count": len(transaction_ids),
            "freshness": InformationFreshnessInspector.build_freshness_view(
                devops_information_registry=devops_information_registry,
                regions=regions,
                max_age_in_seconds=max_age,
            ),
        }
