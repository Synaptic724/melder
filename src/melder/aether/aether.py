import uuid
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_set import ConcurrentSet
from melder.utilities.interfaces.interfaces import IConduit, IConduitCloud
from melder.utilities.general_base.sealable import Sealable
from melder.aether.aetheric_frame import AethericFrame
from threading import RLock

class Aether(Sealable):
    """
    The global singleton that holds and manages all AethericFrames.

    Aether is the top-level "universe" of the melder system. It is
    responsible for creating and managing isolated frames, holding the
    "default" frame, and acting as the central point of access for
    all conduit-related systems.

    It provides internal-only methods (prefixed with '_') for other
    parts of the melder system to interact with the global state in a
    thread-safe manner.
    """
    _instance = None
    _lock = RLock()
    _initialized = False

    def __new__(cls):
        """Ensures that Aether is a singleton."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Aether, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the Aether singleton, creating the 'default' frame."""
        if not Aether._initialized:
            super().__init__()
            Aether._initialized = True
            self._aetheric_frames: ConcurrentDict[str, AethericFrame] = ConcurrentDict()
            self._aetheric_frames["default"] = AethericFrame("default")
            self._default_frame = self._aetheric_frames["default"]


    def seal(self):
        """
        Seals the entire Aether, recursively sealing all frames and conduits.

        Clears all registries and renders the Aether unusable.
        This operation is idempotent.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self.seal_aetheric_frames()
            self._default_frame = None
            self._aetheric_frames.cleanup()
            self._sealed = True


    def seal_aetheric_frames(self):
        """
        Signs all aetheric frames and their contents.
        """
        for frame in self._aetheric_frames.values():
            try:
                frame.seal()
            except Exception:
                pass

    def _reset_for_testing(self):
        """
        Resets the Aether singleton to a clean state.

        WARNING: This is for testing purposes ONLY. Do not use in production.
        """
        with self._lock:
            self._default_frame._conduits.clear()
            self._default_frame._conduit_clusters.clear()
            self._default_frame._sealed = False
            self._sealed = False
            Aether._initialized = False
            Aether._instance = None

    #region Configuration

    def _bind_configuration(self, configuration, aetheric_frame_name: str = "default") -> None:
        """
        Binds a configuration object to a specific Aetheric Frame.

        Args:
            configuration: The configuration object to bind.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        with self._lock:
            if aetheric_frame_name != "default":
                try:
                    self._aetheric_frames[aetheric_frame_name]._configuration = configuration
                except KeyError:
                    raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
            else:
                self._default_frame._configuration = configuration

    def _get_configuration(self, aetheric_frame_name: str = "default") -> 'Configuration' or None:
        """
        Retrieves the configuration object from a specific Aetheric Frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            The configuration object, or None if not set.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                return self._aetheric_frames[aetheric_frame_name]._configuration
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            return self._default_frame._configuration

    #endregion Configuration
    #region Conduit Management
    def _register_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Registers a conduit with the ConduitCloud of a specific frame.

        Args:
            conduit: The conduit to register.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                conduit_cloud =  self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_cloud = self._default_frame._conduit_cloud

        conduit_cloud._register_conduit(conduit)

    def _get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Retrieves the ConduitCloud instance from a specific frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            ConduitCloud: The ConduitCloud for that frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                return self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            return self._default_frame._conduit_cloud

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
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        for conduit in conduits.values():
            if conduit.name == name:
                return conduit
        raise ValueError(f"Conduit with name {name} not found.")

    def _get_conduit_by_id(self, signature: uuid.uuid4, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its UUID.

        Args:
            signature (uuid.uuid4): The UUID of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        if signature in conduits:
            return conduits[signature]
        raise ValueError(f"Conduit with signature {signature} not found.")

    def _add_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Adds a new root conduit to a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID already exists.
        """
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        if conduit.__creation_context__._conduit_id in conduits:
            raise ValueError(f"Conduit with ID {conduit.__creation_context__._conduit_id} already exists.")
        conduits[conduit.__creation_context__._conduit_id] = conduit

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Removes a root conduit from a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        conduit_id = conduit.__creation_context__._conduit_id
        removed = conduits.pop(conduit_id, None)
        if removed is None:
            raise ValueError(f"Conduit with ID {conduit_id} does not exist.")


    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Creates a new conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name for the new cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster name is taken.
        """
        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} already exists.")
        conduit_clusters[cluster_name] = ConcurrentList()

    def _add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Adds a conduit's UUID to a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        conduit_clusters[cluster_name].append(conduit.__creation_context__._conduit_id)

    def _remove_conduit_from_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Removes a conduit's UUID from a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        conduit_clusters[cluster_name].remove(conduit.__creation_context__._conduit_id)

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> ConcurrentList[uuid.UUID]:
        """
        Gets a list of all conduit UUIDs in a specific cluster.

        Args:
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            ConcurrentList[uuid.UUID]: A list of conduit UUIDs.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        return conduit_clusters[cluster_name]

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
        if aetheric_frame_name != "default":
            try:
                spell_registry = self._aetheric_frames[aetheric_frame_name]._spell_registry
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            spell_registry = self._default_frame._spell_registry

        for conduit_id, spell_set in spell_registry.items():
            if spell_id in spell_set:
                return self._get_conduit_by_id(conduit_id, aetheric_frame_name)
        raise ValueError(f"Spell ID {spell_id} not found in any conduit.")

    #endregion Conduit Management
    #region Spell Management

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
        if aetheric_frame_name != "default":
            try:
                spell_registry = self._aetheric_frames[aetheric_frame_name]._spell_registry
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            spell_registry = self._default_frame._spell_registry

        for spell_set in spell_registry.values():
            if spell_id in spell_set:
                return True
        return False

    def _add_spells_to_aether(self, conduit_id: uuid.UUID, spell_set: ConcurrentSet[str], aetheric_frame_name: str = "default"):
        """
        Registers a set of spell IDs as being owned by a specific conduit.

        Args:
            conduit_id (uuid.UUID): The UUID of the owning conduit.
            spell_set (ConcurrentSet[str]): A set of spell IDs to register.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID is
                already registered.
        """
        if aetheric_frame_name != "default":
            try:
                spell_registry = self._aetheric_frames[aetheric_frame_name]._spell_registry
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            spell_registry = self._default_frame._spell_registry

        if conduit_id not in spell_registry:
            spell_registry[conduit_id] = spell_set
        else:
            raise ValueError(f"Spell registry already contains Conduit ID {conduit_id}.")

    #endregion Spell Management