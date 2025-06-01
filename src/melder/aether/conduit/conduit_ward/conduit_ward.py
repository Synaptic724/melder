from uuid import UUID
import threading
from enum import Enum
from typing import List, Optional
from melder.aether.aether import Aether
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_set import ConcurrentSet
from melder.utilities.general_helpers import EnumHelpers
from melder.utilities.interfaces import IConduit, IConduitWard
from melder.aether.conduit.conduit_state.conduit_state import ConduitState

# TODO: Ensure that links properly connect to the spell and its dependencies not just the spell itself.

#region ConduitWard
class ConduitWard(IConduitWard):
    """
    Conduitward is a class that manages the links between conduits.
    """
    _aether = Aether()
    def __init__(self, conduit: IConduit, dynamic: bool, conduit_type: ConduitState, policy: Policies):
        """
        Conduitward is a class that manages the links between conduits.
        :param conduit:
        """
        super().__init__()
        self._lock = threading.RLock()

        ## Conduit Ward properties
        self._conduit = conduit
        self._dynamic = dynamic
        self._conduit_type = conduit_type

        self._policy_set = False
        self._policy = self._set_initial_policy(policy)

        ## Conduit links
        self._conduit_links = None

        # Internal structures
        self._parent_conduit_link = None
        self._lesser_conduits_links = None

#region Properties
    @property
    def policy(self) -> Policies:
        """
        Gets the policy for the conduit ward.
        :return:
        """
        return self._policy

    @property
    def conduit_type(self) -> ConduitState:
        """
        Gets the policy for the conduit ward.
        :return:
        """
        return self._conduit_type
#endregion
#region Conduit Ward Configuration
    def _convert_to_normal_conduit(self) -> None:
        """
        Converts this Conduit to a normal Conduit.
        This is meant for internal use please do not use this outside of the class.
        """
        if self._conduit_type != ConduitState.lesser:
            raise RuntimeError("Conduit is not a lesser conduit.")
        if self._sealed:
            raise RuntimeError("Cannot convert a sealed Conduit.")
        with self._lock:
            if not self._dynamic:
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._parent_conduit_link is not None and self._conduit_type == ConduitState.lesser:
                self._parent_conduit_link = None
                self._conduit_type = ConduitState.normal #policy stays as delegate until the user adds a spell then it goes to dynamic
            else:
                raise RuntimeError("No parent conduit link found. Cannot convert to normal conduit. Unknown error")

    def _set_initial_policy(self, policy: Policies) -> Optional[Policies]:
        """
        Sets the default policy for this Conduit.
        This is meant for internal use please do not use this outside of the class.
        """
        if self._sealed:
            raise RuntimeError("Cannot set policy on a sealed Conduit.")

        # Ensure only valid enum instances are passed
        if not policy is None:
            if not isinstance(policy, Policies):
                raise TypeError(f"permissions must be an instance of Permissions enum, got {type(policy).__name__}")
            self._policy_set = True
            return policy

        with self._lock:
            if self._dynamic and self._conduit_type == ConduitState.lesser:
                raise NotImplementedError("Parent conduit link is not implemented yet as delegate.")
            else:
                raise RuntimeError("Policy already set. Cannot set policy again.")

    def _set_new_policy(self, policy: str) -> None:
        """
        Sets a new policy for this Conduit.
        This is meant for internal use; do not call externally.

        Please note that policies will automatically change if a delegate policy is set and a spell is added.
        It will automatically change to dynamic policy.
        """
        if self._sealed:
            raise RuntimeError("Cannot set policy on a sealed Conduit.")
        if not self._dynamic:
            raise RuntimeError("Dynamic environment is not enabled. Cannot set policy.")
        if self._conduit_type == ConduitState.lesser:
            raise RuntimeError("Cannot set policy on a lesser Conduit. Convert to a normal Conduit first.")

        with self._lock:
            spellcount = self._conduit._spellbook._find_spell_count()
            new_policy = EnumHelpers.convert_enum_and_check(policy, Policies)

            if spellcount == 0:
                if new_policy != Policies.delegate:
                    raise RuntimeError("Must add at least one spell before changing policy. "
                                       "Only 'delegate' is allowed when spellbook is empty.")
            else:
                if new_policy == Policies.delegate:
                    raise RuntimeError("Cannot set policy to 'delegate' when spells exist in the conduit.")

            if new_policy == Policies.automatic:
                raise RuntimeError("Cannot set policy to 'automatic' in dynamic mode.")

            self._policy = new_policy

    #endregion Conduit Ward Configuration
#region Link Management
    def link(self, target_conduit) -> bool:
        """
        Attempts to link this Conduit to another Conduit.

        Linking is only allowed if the world is in dynamic mode.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        if not self._dynamic:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

    def sever_link(self):
        """
        Sever the link between this Conduit and its target Conduit.

        This is meant for internal use please do not use this outside of the class.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever a link in a sealed Conduit.")
        if not self._dynamic:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            raise NotImplementedError("Severing links is not implemented yet.")

    def _link_lesser_conduit(self, target_conduit) -> bool:
        """
        Attempts to link this Conduit to a lesser Conduit.
        This is meant for internal use please do not use this outside of the class.

        Linking for Automatic mode will transfer the spellbook of the existing conduit into the
        lesser conduit and setup permissions between objects using link.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        with self._lock:
            if self._lesser_conduits_links is None:
                self._lesser_conduits_links = ConcurrentList()
            else:
                raise NotImplementedError("Linking conduits is not implemented yet.")

    def _link_parent_conduit(self, target_conduit) -> bool:
        """
        Attempts to link this Conduit to a parent Conduit.
        This is meant for internal use please do not use this outside of the class.

        Linking for Automatic mode will transfer the spellbook of the existing conduit into the
        lesser conduit and setup permissions between objects using link.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        with self._lock:
            if self._parent_conduit_link is None:
                self._parent_conduit_link = target_conduit
            else:
                raise RuntimeError("Parent Conduit already set.")

    def remove_link(self, other_conduit):
        pass

    def get_links(self):
        return self._active_links

    def add_link(self, other_conduit):
        pass

#endregion Link Management
#region Cleanup
    def seal(self):
        """
        Seals the conduit ward, preventing any further modifications.
        """
        if self._sealed:
            return
        with self._lock:
            self._clean_up_links()
            self._clean_up_lesser_conduits_links()
            self._conduit = None
            self._dynamic = None
            self.sever_link(self._parent_conduit_link)
            self._conduit_type = self._conduit_type.sealed
            self._policy = None
            self._sealed = True


    def _clean_up_lesser_conduits_links(self):
        """
        Cleans up all lesser conduits.
        :return:
        """
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                lesser_conduit.seal()
            self._lesser_conduits_links.dispose()

    def _clean_up_links(self):
        """
        Cleans up all links.
        :return:
        """
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()
#endregion Cleanup
#endregion ConduitWard