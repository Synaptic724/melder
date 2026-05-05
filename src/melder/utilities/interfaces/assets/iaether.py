from typing import Any, Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.iconduit import IConduit
from melder.utilities.interfaces.assets.iconduitcloud import IConduitCloud

@runtime_checkable
class IAether(ICleanable, Protocol):
    """
    An Interface for the global singleton that holds and manages all AethericFrames.

    Aether is the top-level "universe" of the melder system and acts as the
    central service provider for other internal components of the library.
    """

    def _bind_configuration(self, configuration: Any, aetheric_frame_name: str = "default") -> None:
        """
        Binds a configuration object to a specific Aetheric Frame.

        Args:
            configuration: The configuration object to bind.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_configuration(self, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Retrieves the configuration object from a specific Aetheric Frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            The configuration object, or None if not set.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _ensure_frame(self, aetheric_frame_name: str = "default") -> "IAethericFrame":
        """
        Ensure an AethericFrame exists for the given name, creating it if missing.

        Purpose:
            Provide a single, thread-safe creation path for named frames so
            Spellbooks can initialize against a new frame without raising.

        Contract:
            - Returns the existing frame when it already exists.
            - Creates and registers a new frame when absent.
            - Does not mutate the default frame pointer unless the name is "default".

        Args:
            aetheric_frame_name: The frame name to ensure exists.

        Returns:
            IAethericFrame: The existing or newly created frame.

        Raises:
            RuntimeError: If the Aether is cleaned or its frame registry is unavailable.
            ValueError: If the frame name is invalid for frame construction.

        Threading:
            Implementations must synchronize frame creation to prevent duplicates.

        Lifecycle:
            Frames created via this method are owned by Aether and cleaned by it.
        """
        ...

    def _detach_cleaned_frame(
            self,
            frame_name: str,
            frame: "IAethericFrame",
    ) -> None:
        """
        Remove one already-cleaned frame from the Aether registry.

        Args:
            frame_name:
                Name of the cleaned frame.
            frame:
                Cleaned frame instance requesting detachment.

        Returns:
            None.
        """
        ...

    def _register_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Registers a conduit with the ConduitCloud of a specific frame.

        Args:
            conduit: The conduit to register.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Retrieves the ConduitCloud instance from a specific frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            IConduitCloud: The ConduitCloud for that frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Return the conduit cloud for one frame.
        """
        ...

    def list_conduit_ids(
            self,
            aetheric_frame_name: str = "default",
    ) -> Tuple[str, ...]:
        """
        Return the registered root conduit ids for one frame.
        """
        ...

    def list_conduit_names(
            self,
            aetheric_frame_name: str = "default",
    ) -> Tuple[str, ...]:
        """
        Return the registered root conduit names for one frame.
        """
        ...

    def count_conduits(self, aetheric_frame_name: str = "default") -> int:
        """
        Return the number of registered root conduits for one frame.
        """
        ...

    def has_conduit_id(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Return whether one root conduit id exists in one frame.
        """
        ...

    def has_conduit_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Return whether one root conduit name exists in one frame.
        """
        ...

    def find_conduit_id_by_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> Optional[str]:
        """
        Return the conduit id registered under one root conduit name, if present.
        """
        ...

    def get_conduit_by_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> IConduit:
        """
        Return one registered root conduit by name.
        """
        ...

    def get_conduit_by_id(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
    ) -> IConduit:
        """
        Return one registered root conduit by id.
        """
        ...

    def _get_conduit_by_name(self, name: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its name.

        Args:
            name (str): The name of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _get_conduit_by_id(self, signature: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its id.

        Args:
            signature (str): The id of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _add_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Adds a new root conduit to a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID already exists.
        """
        ...

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Removes a root conduit from a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Creates a new conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name for the new cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster name is taken.
        """
        ...

    def _add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Adds a conduit's str to a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _remove_conduit_from_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Removes a conduit's str from a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> 'List[str]':
        """
        Gets a list of all conduit id in a specific cluster.

        Args:
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            List[str]: A list of conduit ids.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds the conduit that owns a specific spell ID within a frame.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            IConduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        """
        ...

    def _check_for_spell(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Checks if a spell ID is registered in any conduit within a frame.

        Args:
            spell_id (str): The spell ID to check.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            bool: True if the spell exists, False otherwise.

        Raises:
            ValueError: If the frame does not exist.
        """
        ...

    def _add_spells_to_aether(self, conduit_id: str, spell_set: 'Set[str]', aetheric_frame_name: str = "default"):
        """
        Registers a set of spell IDs as being owned by a specific conduit.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (Set[str]): A set of spell IDs to register.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID is
                already registered.
        """
        ...

    def cleanup_aetheric_frames(self):
        """
        Cleans all aetheric frames and their contents.
        """
        ...
