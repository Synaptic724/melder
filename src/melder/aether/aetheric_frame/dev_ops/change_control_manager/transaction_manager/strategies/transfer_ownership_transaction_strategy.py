from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import (
    TransferOfOwnership,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spell import Spell


class TransferOwnershipTransactionStrategy(TransactionStrategy):
    """
    Ownership-transfer transaction resolver.

    Purpose:
        Resolve one `TRANSFER_OWNERSHIP` request into the normalized
        change-control plan used by the mediator, while keeping the existing
        `TransferOfOwnership` helper as the execution body.

    Design split:
        - Strategy owns planning:
          participant validation, transfer-option normalization, affected
          identity collection, and scope planning.
        - `TransferOfOwnership` owns execution:
          preflight intent recording, lineage disable/flip, rollback, creation
          handling, borrower repair, dependency transfer, and incident
          reporting.

    Contract:
        - Requires a conduit submitter identity.
        - Uses the frame registry to resolve both source and target conduits.
        - Uses a pure transfer-preflight summary to discover borrower and
          cluster participants without mutating change-control state.
        - Uses sets for scope and identity accumulation, then normalizes once
          at the return boundary.
    """

    @classmethod
    def build_start_plan(
            cls,
            *,
            transaction_manager: "ChangeControlTransactionManager",
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build the change-control request inputs for one ownership transfer.

        Args:
            transaction_manager:
                Scope-key helper owner used to normalize the transfer request.
            devops_information_registry:
                Frame-local topology registry used to resolve source/target
                conduits, spellbooks, wards, clusters, and borrower
                participants.
            identity:
                Conduit identity originating the transfer request.
            metadata:
                Caller-supplied transfer metadata.

        Returns:
            Dict[str, object]:
                Normalized request inputs for mediator admission.
        """
        if identity.owner_kind != "conduit":
            raise RuntimeError(
                "Transfer-ownership transactions must originate from a conduit identity."
            )

        source_conduit = cls._resolve_conduit_object(
            devops_information_registry=devops_information_registry,
            conduit_id=identity.owner_id,
            role_label="source",
        )
        target_conduit_id = cls._resolve_target_conduit_id(metadata)
        target_conduit = cls._resolve_conduit_object(
            devops_information_registry=devops_information_registry,
            conduit_id=target_conduit_id,
            role_label="target",
        )
        spell_obj = cls._resolve_transfer_spell(
            source_conduit=source_conduit,
            metadata=metadata,
        )

        move_creations = bool(metadata.get("move_creations", False))
        include_dependencies = bool(metadata.get("include_dependencies", False))
        force_unshare = bool(metadata.get("force_unshare", True))
        invalidate_after_transfer = bool(
            metadata.get("invalidate_after_transfer", True)
        )
        mark_dependencies_dirty = bool(
            metadata.get("mark_dependencies_dirty", False)
        )

        transfer_helper = TransferOfOwnership(
            source_conduit=source_conduit,
            target_conduit=target_conduit,
            spell=spell_obj,
            move_creations=move_creations,
            include_dependencies=include_dependencies,
            force_unshare=force_unshare,
            invalidate_after_transfer=invalidate_after_transfer,
            mark_dependencies_dirty=mark_dependencies_dirty,
        )
        try:
            preflight_summary = transfer_helper._build_preflight_summary(spell_obj)
        finally:
            transfer_helper.cleanup()

        source_spellbook_id = cls._resolve_spellbook_id_for_conduit(
            devops_information_registry=devops_information_registry,
            conduit=source_conduit,
        )
        target_spellbook_id = cls._resolve_spellbook_id_for_conduit(
            devops_information_registry=devops_information_registry,
            conduit=target_conduit,
        )

        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        explicit_contract_keys = tuple(metadata.get("contract_keys", ()))

        conduit_ids: Set[str] = {
            source_conduit._id,
            target_conduit._id,
        }
        cluster_ids: Set[str] = set()
        affected_identity_keys: Set[Tuple[str, str]] = {
            ("conduit", source_conduit._id),
            ("conduit", target_conduit._id),
            ("conduit_ward", source_conduit._id),
            ("conduit_ward", target_conduit._id),
        }

        if source_spellbook_id is not None:
            affected_identity_keys.add(("spellbook", source_spellbook_id))
        if target_spellbook_id is not None:
            affected_identity_keys.add(("spellbook", target_spellbook_id))

        cls._collect_cluster_memberships(
            devops_information_registry=devops_information_registry,
            conduit_id=source_conduit._id,
            conduit_ids=conduit_ids,
            cluster_ids=cluster_ids,
            affected_identity_keys=affected_identity_keys,
        )
        cls._collect_cluster_memberships(
            devops_information_registry=devops_information_registry,
            conduit_id=target_conduit._id,
            conduit_ids=conduit_ids,
            cluster_ids=cluster_ids,
            affected_identity_keys=affected_identity_keys,
        )
        cls._collect_borrower_participants(
            devops_information_registry=devops_information_registry,
            borrowers=preflight_summary["borrowers"],
            conduit_ids=conduit_ids,
            cluster_ids=cluster_ids,
            affected_identity_keys=affected_identity_keys,
        )

        scope_keys: Set[str] = set(explicit_scope_keys)
        for conduit_id in conduit_ids:
            scope_keys.add(transaction_manager.make_scope_key_conduit(conduit_id))
            scope_keys.add(
                transaction_manager.make_scope_key_identity(
                    owner_kind="conduit_ward",
                    owner_id=conduit_id,
                )
            )

        spellbook_ids = cls._collect_spellbook_ids_from_identities(
            affected_identity_keys=affected_identity_keys,
        )
        for spellbook_id in spellbook_ids:
            scope_keys.add(transaction_manager.make_scope_key_spellbook(spellbook_id))

        for cluster_id in cluster_ids:
            scope_keys.add(transaction_manager.make_scope_key_cluster(cluster_id))

        binding_keys = explicit_binding_keys
        if not binding_keys:
            binding_keys = (spell_obj.key,)
        for frame_key, binding_key in binding_keys:
            scope_keys.add(
                transaction_manager.make_scope_key_binding(frame_key, binding_key)
            )

        for owner_kind, owner_id in sorted(affected_identity_keys):
            resolved_identity = devops_information_registry.get_identity(
                owner_kind=owner_kind,
                owner_id=owner_id,
            )
            if resolved_identity is None:
                continue
            cls._add_transaction_owner_scopes(
                scope_keys=scope_keys,
                transaction_manager=transaction_manager,
                identity=resolved_identity,
            )

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["transfer_mode"] = "conduit_transfer_ownership"
        normalized_metadata["source_conduit_id"] = source_conduit._id
        normalized_metadata["target_conduit_id"] = target_conduit._id
        normalized_metadata["source_spellbook_id"] = source_spellbook_id
        normalized_metadata["target_spellbook_id"] = target_spellbook_id
        normalized_metadata["spell_id"] = spell_obj.spell_id
        normalized_metadata["spell_index_id"] = spell_obj.spell_index.id
        normalized_metadata["participant_conduit_ids"] = tuple(sorted(conduit_ids))
        normalized_metadata["affected_cluster_ids"] = tuple(sorted(cluster_ids))
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )
        normalized_metadata["move_creations"] = move_creations
        normalized_metadata["include_dependencies"] = include_dependencies
        normalized_metadata["force_unshare"] = force_unshare
        normalized_metadata["invalidate_after_transfer"] = (
            invalidate_after_transfer
        )
        normalized_metadata["mark_dependencies_dirty"] = mark_dependencies_dirty
        normalized_metadata["preflight_borrowers"] = tuple(
            sorted(
                cls._normalize_borrower_metadata(preflight_summary["borrowers"])
            )
        )
        normalized_metadata["preflight_dependencies"] = tuple(
            preflight_summary["dependencies"]
        )

        return {
            "initiator_conduit_id": source_conduit._id,
            "spellbook_id": source_spellbook_id,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": binding_keys,
            "contract_keys": explicit_contract_keys,
            "granted_capabilities": (
                "transfer_ownership",
                "contract_mutation",
                "cluster_link",
            ),
            "required_capabilities": (
                "transfer_ownership",
                "contract_mutation",
                "cluster_link",
            ),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _resolve_conduit_object(
            *,
            devops_information_registry: DevopsInformationRegistry,
            conduit_id: str,
            role_label: str,
    ) -> "Conduit":
        """
        Resolve one live conduit object from the frame registry.

        Args:
            devops_information_registry:
                Registry used to resolve the live conduit.
            conduit_id:
                Conduit identifier to resolve.
            role_label:
                Human-readable role label used in error messages.

        Returns:
            Conduit:
                Resolved live conduit object.
        """
        conduit = devops_information_registry.get_object(
            owner_kind="conduit",
            owner_id=conduit_id,
        )
        if conduit is None:
            raise RuntimeError(
                f"Transfer-ownership strategy could not resolve the {role_label} conduit object."
            )
        return conduit

    @staticmethod
    def _resolve_target_conduit_id(metadata: Dict[str, object]) -> str:
        """
        Resolve the target conduit id from transfer metadata.

        Args:
            metadata:
                Caller-supplied transfer metadata.

        Returns:
            str:
                Target conduit identifier.
        """
        target_conduit_id = metadata.get("target_conduit_id")
        if not isinstance(target_conduit_id, str) or not target_conduit_id.strip():
            raise RuntimeError(
                "Transfer-ownership transaction requires target_conduit_id metadata."
            )
        return target_conduit_id

    @staticmethod
    def _resolve_transfer_spell(
            *,
            source_conduit: "Conduit",
            metadata: Dict[str, object],
    ) -> "Spell":
        """
        Resolve the spell being transferred from normalized metadata.

        Args:
            source_conduit:
                Source conduit that currently owns the spell.
            metadata:
                Caller-supplied transfer metadata.

        Returns:
            Spell:
                Resolved live spell object to transfer.
        """
        spell_index_id = metadata.get("spell_index_id")
        spell_id = metadata.get("spell_id")

        resolved_spell = None
        if isinstance(spell_index_id, str) and spell_index_id.strip():
            resolved_spell = source_conduit.get_spell_by_index_id(spell_index_id)
        if resolved_spell is None and isinstance(spell_id, str) and spell_id.strip():
            resolved_spell = source_conduit.get_spell_by_id(
                spell_id,
                source_conduit._aetheric_frame_name,
            )
        if resolved_spell is None:
            raise RuntimeError(
                "Transfer-ownership strategy could not resolve the source spell."
            )
        if (
                isinstance(spell_id, str)
                and spell_id.strip()
                and resolved_spell.spell_id != spell_id
        ):
            raise RuntimeError(
                "Transfer-ownership strategy resolved a spell whose current spell_id "
                "does not match the requested spell_id metadata."
            )
        return resolved_spell

    @staticmethod
    def _resolve_spellbook_id_for_conduit(
            *,
            devops_information_registry: DevopsInformationRegistry,
            conduit: "Conduit",
    ) -> Optional[str]:
        """
        Resolve the owning spellbook id for one conduit.

        Args:
            devops_information_registry:
                Registry used for ownership lookups.
            conduit:
                Conduit whose owner spellbook should be resolved.

        Returns:
            Optional[str]:
                Owning spellbook id when available.
        """
        spellbook_id = devops_information_registry.get_spellbook_for_conduit(
            conduit._id
        )
        if spellbook_id:
            return spellbook_id
        spellbook = conduit._spellbook
        if spellbook is None:
            return None
        return spellbook._id

    @staticmethod
    def _collect_cluster_memberships(
            *,
            devops_information_registry: DevopsInformationRegistry,
            conduit_id: str,
            conduit_ids: Set[str],
            cluster_ids: Set[str],
            affected_identity_keys: Set[Tuple[str, str]],
    ) -> None:
        """
        Collect cluster memberships for one conduit into the planning sets.

        Args:
            devops_information_registry:
                Registry used to resolve memberships.
            conduit_id:
                Conduit whose memberships should be folded into the plan.
            conduit_ids:
                Participant conduit-id set being built.
            cluster_ids:
                Cluster-id set being built.
            affected_identity_keys:
                Affected identity-key set being built.
        """
        resolved_cluster_ids = devops_information_registry.get_clusters_for_conduit(
            conduit_id
        )
        for cluster_id in resolved_cluster_ids:
            cluster_ids.add(cluster_id)
            affected_identity_keys.add(("conduit_cluster", cluster_id))
            cluster_object = devops_information_registry.get_object(
                owner_kind="conduit_cluster",
                owner_id=cluster_id,
            )
            if cluster_object is None:
                continue
            conduit_ids.update(cluster_object.get_members())

    @staticmethod
    def _collect_borrower_participants(
            *,
            devops_information_registry: DevopsInformationRegistry,
            borrowers: Union[
                Tuple[Dict[str, object], ...],
                List[Dict[str, object]],
            ],
            conduit_ids: Set[str],
            cluster_ids: Set[str],
            affected_identity_keys: Set[Tuple[str, str]],
    ) -> None:
        """
        Fold borrower participants discovered during pure preflight into the plan.

        Args:
            devops_information_registry:
                Registry used to resolve spellbook ownership for borrower
                conduits.
            borrowers:
                Pure preflight borrower descriptors.
            conduit_ids:
                Participant conduit-id set being built.
            cluster_ids:
                Cluster-id set being built.
            affected_identity_keys:
                Affected identity-key set being built.
        """
        for borrower in borrowers:
            borrower_type = borrower.get("type")
            if borrower_type == "contract":
                borrower_conduit_id = borrower.get("borrower_conduit_id")
                if not isinstance(borrower_conduit_id, str) or not borrower_conduit_id:
                    continue
                conduit_ids.add(borrower_conduit_id)
                affected_identity_keys.add(("conduit", borrower_conduit_id))
                affected_identity_keys.add(("conduit_ward", borrower_conduit_id))
                borrower_spellbook_id = (
                    devops_information_registry.get_spellbook_for_conduit(
                        borrower_conduit_id
                    )
                )
                if borrower_spellbook_id:
                    affected_identity_keys.add(
                        ("spellbook", borrower_spellbook_id)
                    )
            elif borrower_type == "cluster":
                cluster_id = borrower.get("cluster_id")
                if isinstance(cluster_id, str) and cluster_id:
                    cluster_ids.add(cluster_id)
                    affected_identity_keys.add(("conduit_cluster", cluster_id))
                member_conduit_ids = borrower.get("member_conduit_ids")
                if not isinstance(member_conduit_ids, tuple):
                    continue
                for conduit_id in member_conduit_ids:
                    if not isinstance(conduit_id, str) or not conduit_id:
                        continue
                    conduit_ids.add(conduit_id)
                    affected_identity_keys.add(("conduit", conduit_id))
                    affected_identity_keys.add(("conduit_ward", conduit_id))
                    member_spellbook_id = (
                        devops_information_registry.get_spellbook_for_conduit(
                            conduit_id
                        )
                    )
                    if member_spellbook_id:
                        affected_identity_keys.add(
                            ("spellbook", member_spellbook_id)
                        )

    @staticmethod
    def _collect_spellbook_ids_from_identities(
            *,
            affected_identity_keys: Set[Tuple[str, str]],
    ) -> Set[str]:
        """
        Collect spellbook ids from the affected identity set.

        Args:
            affected_identity_keys:
                Affected identity keys accumulated so far.

        Returns:
            Set[str]:
                Spellbook ids represented in the affected identity set.
        """
        spellbook_ids: Set[str] = set()
        for owner_kind, owner_id in affected_identity_keys:
            if owner_kind == "spellbook":
                spellbook_ids.add(owner_id)
        return spellbook_ids

    @staticmethod
    def _add_transaction_owner_scopes(
            *,
            scope_keys: Set[str],
            transaction_manager: "ChangeControlTransactionManager",
            identity: DevopsIdentity,
    ) -> None:
        """
        Add transaction-owner scopes for every declared transaction on one identity.

        Args:
            scope_keys:
                Scope-key set being accumulated.
            transaction_manager:
                Scope-key helper owner.
            identity:
                Identity whose available transactions should be turned into
                owner-specific scopes.
        """
        for transaction_name in identity.available_transactions:
            scope_keys.add(
                transaction_manager.make_scope_key_transaction_owner(
                    owner_kind=identity.owner_kind,
                    owner_id=identity.owner_id,
                    transaction_name=transaction_name,
                )
            )

    @staticmethod
    def _normalize_borrower_metadata(
            borrowers: Union[
                Tuple[Dict[str, object], ...],
                List[Dict[str, object]],
            ],
    ) -> Set[str]:
        """
        Build a lightweight borrower summary for request metadata.

        Purpose:
            Keep request metadata descriptive without embedding the full
            mutable preflight payload.

        Args:
            borrowers:
                Borrower descriptors from pure preflight.

        Returns:
            Set[str]:
                Stable string summaries of borrower participants.
        """
        normalized: Set[str] = set()
        for borrower in borrowers:
            borrower_type = borrower.get("type")
            if borrower_type == "contract":
                borrower_conduit_id = borrower.get("borrower_conduit_id")
                if isinstance(borrower_conduit_id, str) and borrower_conduit_id:
                    normalized.add(f"contract:{borrower_conduit_id}")
            elif borrower_type == "cluster":
                cluster_id = borrower.get("cluster_id")
                if isinstance(cluster_id, str) and cluster_id:
                    normalized.add(f"cluster:{cluster_id}")
        return normalized

    @staticmethod
    def on_start(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Ownership-transfer transactions do not need extra local start effects yet.
        """
        return None

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Ownership-transfer transactions do not need extra local end effects yet.
        """
        return None
