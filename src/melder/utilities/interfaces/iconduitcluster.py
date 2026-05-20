from typing import Dict, Protocol, Set, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.ispellindex import ISpellIndex


@runtime_checkable
class IConduitCluster(ICleanable, Protocol):
    """
    Interface for a conduit-cluster membership and shared-root manager.

    Contract:
        - Tracks conduit membership by conduit id.
        - Tracks which root spell lineages each owner contributes for sharing.
        - Exposes detached snapshots for members and shared-root mappings.
    """

    def add_member(self, conduit_id: str) -> None:
        """
        Add one conduit id to the cluster membership.
        """
        ...

    def remove_member(self, conduit_id: str) -> None:
        """
        Remove one conduit id and its owned shared-root registry.
        """
        ...

    def add_shared_spell(self, owner_id: str, spell_index: ISpellIndex) -> None:
        """
        Record one shareable root lineage for the supplied owner conduit.
        """
        ...

    def remove_shared_spell(
            self,
            owner_id: str,
            spell_index: ISpellIndex,
    ) -> None:
        """
        Remove one recorded shareable root lineage for the supplied owner.
        """
        ...

    def get_shared_spells(self) -> Dict[str, Set[ISpellIndex]]:
        """
        Return a detached snapshot of shared-root lineages by owner conduit id.
        """
        ...

    def get_members(self) -> Set[str]:
        """
        Return a detached snapshot of current conduit-member ids.
        """
        ...

    def handle_join(
            self,
            conduit: IConduit,
    ) -> None:
        """
        Share eligible roots when one conduit joins the cluster.
        """
        ...

    def handle_leave(
            self,
            conduit: IConduit,
    ) -> None:
        """
        Tear down shared roots when one conduit leaves the cluster.
        """
        ...

    def refresh_member_shares(
            self,
            conduit: IConduit,
    ) -> None:
        """
        Refresh one member's shareable roots against the current peers.
        """
        ...

    def share_to_borrower(self, owner: IConduit, borrower: IConduit) -> None:
        """
        Push the owner's shareable roots into one borrower conduit.
        """
        ...
