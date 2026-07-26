from typing import TYPE_CHECKING, Dict, List, Tuple

from melder.aether.aetheric_frame.dev_ops.devops_information_strategy import (
    DevopsInformationStrategy,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class RegistryConsistencyAuditStrategy(DevopsInformationStrategy):
    """
    Internal symmetry audit over the registry's mirrored relationship maps.

    Purpose:
        Verify that every bidirectional map pair and transaction reverse
        index agrees with its partner, and report each asymmetry as one
        finding.

    Why this exists:
        The control plane's correctness story is "transactions write the
        registry through commit deltas while scopes are held". If that story
        holds, the forward and reverse maps can never disagree — so any
        asymmetry is direct evidence that some write bypassed the plane or a
        delta was applied partially. This audit is the cheap sampled check
        that the philosophy artifact calls for: it verifies the deltas'
        bookkeeping without probing live runtime objects (live-truth probes
        need probe contracts on runtime classes and are the catalog's
        recorded next extension).

    Contract:
        - No required metadata.
        - Checks ownership, link, and cluster map pairs plus the
          transaction scope/type/identity reverse indexes.
        - Returns `consistent` plus one detached finding per asymmetry;
          never mutates the registry.

    Threading:
        Stateless static strategy; the audit is a read-only comparison over the
        registry's mirrored maps.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the information
        family; resolved by name through `DevopsInformationStrategyBuilder`.

    Subsystem Context:
        The self-check of the control plane, distinct from every other
        information strategy: the others report what the registry SAYS, this
        one tests whether the registry is internally COHERENT.

    System Context:
        The reasoning here is the sharpest in the package and worth restating.
        The correctness story is "transactions write the registry through
        commit deltas while scopes are held". If that story is true, forward
        and reverse maps CANNOT disagree - the eager mirrors are written
        together under the same claim. Therefore any asymmetry is not a
        cosmetic drift to reconcile; it is direct evidence that a write bypassed
        the transaction plane or that a delta applied partially.
        That makes this audit a falsification test for the plane's core
        invariant, and a cheap one - it needs no live-object probes, only the
        mirrors themselves. Live-truth probing would require probe contracts on
        the runtime classes and is the catalog's recorded next extension, not a
        gap.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Internal symmetry audit over the registry's mirrored relationship
        maps. Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
    """

    @staticmethod
    def execute(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Run one full symmetry audit over the mirrored maps.

        Args:
            devops_information_registry:
                Live mirrored DevOps registry to audit.
            metadata:
                Unused; accepted for catalog-uniform invocation.

        Returns:
            Dict[str, object]: {"strategy", "consistent", "finding_count",
            "findings" (tuple of {"check", "detail"}), "checked_pairs"}.
        """
        maps = devops_information_registry.snapshot_relationship_maps()
        findings: List[Dict[str, str]] = []

        def _audit_pair(
                check: str,
                forward: Dict[str, Tuple[str, ...]],
                reverse: Dict[str, Tuple[str, ...]],
        ) -> None:
            """
            Record findings for every forward edge missing its reverse twin.
            """
            for left_key, right_values in forward.items():
                for right_key in right_values:
                    if left_key not in reverse.get(right_key, ()):
                        findings.append(
                            {
                                "check": check,
                                "detail": (
                                    f"forward edge {left_key!r} -> "
                                    f"{right_key!r} has no reverse entry"
                                ),
                            }
                        )

        def _audit_value_map(
                check: str,
                forward: Dict[str, Tuple[str, ...]],
                reverse: Dict[str, str],
        ) -> None:
            """
            Record findings where a many-to-one reverse map disagrees.
            """
            for left_key, right_values in forward.items():
                for right_key in right_values:
                    if reverse.get(right_key) != left_key:
                        findings.append(
                            {
                                "check": check,
                                "detail": (
                                    f"forward edge {left_key!r} -> "
                                    f"{right_key!r} disagrees with reverse "
                                    f"value {reverse.get(right_key)!r}"
                                ),
                            }
                        )
            for right_key, left_key in reverse.items():
                if right_key not in forward.get(left_key, ()):
                    findings.append(
                        {
                            "check": check,
                            "detail": (
                                f"reverse entry {right_key!r} -> "
                                f"{left_key!r} has no forward edge"
                            ),
                        }
                    )

        checked_pairs = (
            "spellbook_to_conduits/conduit_to_spellbook",
            "provider_to_borrowers/borrower_to_providers",
            "borrower_to_providers/provider_to_borrowers",
            "cluster_to_conduits/conduit_to_clusters",
            "conduit_to_clusters/cluster_to_conduits",
            "transaction_ids_by_scope/transaction_scope_keys_by_id",
            "transaction_scope_keys_by_id/transaction_ids_by_scope",
            "transaction_ids_by_type/transaction_type_by_id",
            "transaction_ids_by_identity/transaction_identity_keys_by_id",
            "transaction_identity_keys_by_id/transaction_ids_by_identity",
        )

        _audit_value_map(
            "spellbook_to_conduits/conduit_to_spellbook",
            maps["spellbook_to_conduits"],
            maps["conduit_to_spellbook"],
        )
        _audit_pair(
            "provider_to_borrowers/borrower_to_providers",
            maps["provider_to_borrowers"],
            maps["borrower_to_providers"],
        )
        _audit_pair(
            "borrower_to_providers/provider_to_borrowers",
            maps["borrower_to_providers"],
            maps["provider_to_borrowers"],
        )
        _audit_pair(
            "cluster_to_conduits/conduit_to_clusters",
            maps["cluster_to_conduits"],
            maps["conduit_to_clusters"],
        )
        _audit_pair(
            "conduit_to_clusters/cluster_to_conduits",
            maps["conduit_to_clusters"],
            maps["cluster_to_conduits"],
        )
        _audit_pair(
            "transaction_ids_by_scope/transaction_scope_keys_by_id",
            maps["transaction_ids_by_scope"],
            maps["transaction_scope_keys_by_id"],
        )
        _audit_pair(
            "transaction_scope_keys_by_id/transaction_ids_by_scope",
            maps["transaction_scope_keys_by_id"],
            maps["transaction_ids_by_scope"],
        )
        _audit_value_map(
            "transaction_ids_by_type/transaction_type_by_id",
            maps["transaction_ids_by_type"],
            maps["transaction_type_by_id"],
        )
        _audit_pair(
            "transaction_ids_by_identity/transaction_identity_keys_by_id",
            maps["transaction_ids_by_identity"],
            maps["transaction_identity_keys_by_id"],
        )
        _audit_pair(
            "transaction_identity_keys_by_id/transaction_ids_by_identity",
            maps["transaction_identity_keys_by_id"],
            maps["transaction_ids_by_identity"],
        )

        return {
            "strategy": "registry_consistency_audit",
            "consistent": not findings,
            "finding_count": len(findings),
            "findings": tuple(findings),
            "checked_pairs": checked_pairs,
        }
