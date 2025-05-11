import uuid
import threading
from enum import Enum
from typing import List
from melder.aether.aether import Aether
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_set import ConcurrentSet
from melder.utilities.interfaces import IConduit, IConduitWard, IPolicy
from melder.aether.conduit.conduit_state.conduit_state import ConduitState

#region ConduitWard
class ConduitWard(IConduitWard):
    """
    Conduitward is a class that manages the links between conduits.
    """
    _aether = Aether()
    def __init__(self, conduit: IConduit, dynamic: bool, conduit_type: ConduitState):
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
        self._policy = None

        ## Internal structures
        self._create_internal_configuration()

        ## Conduit links
        self._conduit_links = None
        self._parent_conduit_link = None
        self._lesser_conduits_links = None


#region Properties
    @property
    def policy(self) -> IPolicy:
        """
        Gets the policy for the conduit ward.
        :return:
        """
        return self._policy

    @policy.setter
    def policy(self, value: IPolicy):
        """
        Sets the policy for the conduit ward.
        :param policy:
        :return:
        """
        self._policy = value

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
                self._conduit_type = ConduitState.normal
                # TODO: we need to add some kind of policy change here
            else:
                raise RuntimeError("No parent conduit link found. Cannot convert to normal conduit. Unknown error")

    def _create_internal_configuration(self) -> None:
        """
        Creates per-Conduit internal structures based on the current world configuration.
        """
        self._configure_conduit_links()

    def _configure_conduit_links(self) -> None:
        """
        Configures whether this Conduit maintains linkable connections.
        Only enabled in dynamic environments.
        """
        if self._dynamic:
            self._conduit_links = ConcurrentList()
        else:
            self._conduit_links = None
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