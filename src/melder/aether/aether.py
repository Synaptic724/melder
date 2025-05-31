import uuid
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_set import ConcurrentSet
from melder.utilities.interfaces import ISeal, IConduit, IConduitCloud
from threading import RLock, Lock

class AethericFrame(ISeal):
    """
    This object is used to hold the Aetheric Frame for the Aether. It isolates
    the Aetheric Frame from the Aether itself, allowing for a clean separation
    of concerns. It allows multiple packages or modules to use the Aether
    without interfering with each other. This is useful for dynamic mode where
    conduits are created at runtime and need to be registered and retrieved by name.

    This object is thread-safe and can be used in a multi-threaded environment.
    """
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self._lock = RLock()
        self._conduits: ConcurrentDict[uuid.UUID, IConduit] = ConcurrentDict()  # This retains all normal conduits i.e roots created by a spellbook
        self._spell_registry: ConcurrentDict[uuid.UUID, ConcurrentSet[str]] = ConcurrentDict()  # Holds conduit UUIDs and their spell IDs which are SHA256 hashes of internal components
        self._conduit_clusters: ConcurrentDict[str, ConcurrentList[uuid.UUID]] = ConcurrentDict()  # Clusters only
        self._conduit_cloud = ConduitCloud(name)  # This is the dynamic mode registry
        self._configuration = None  # This is the configuration for the Aetheric Frame

    def seal(self):
        """
        Dispose of the Aetheric Frame and all its conduits.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            # Seal all conduits and clear the registry
            for conduit in self._conduits.values():
                conduit.seal()
            self._conduits.clear()
            self._spell_registry.clear()
            self._conduit_clusters.clear()
            self._conduit_cloud.seal()
            self._sealed = True



class ConduitCloud(IConduitCloud):
    """
    This object will only be active if dynamic mode is enabled.
    It will automatically register all named conduits into a specific location for retrieval and usage.

    This object is thread-safe and can be used in a multi-threaded environment. This is meant to
    behave like an abstract factory for conduits. It allows you to store your conduits in a central
    location and retrieve them by name. This is useful for dynamic mode where conduits are created
    at runtime and need to be registered and retrieved by name.

    This object is meant to be used in your project to call your conduits in situations where you
    don't want to create a contract to bind them to a specific conduit. It helps balance
    seperation of concerns between conduit types.
    """
    def __init__(self, name: str):
        super().__init__()
        self._lock = Lock()
        self._name = name
        self._registry = ConcurrentDict()


    def get_conduit(self, name: str) -> IConduit:
        """
        Returns a conduit by its name.
        """
        if self._sealed:
            raise RuntimeError("ConduitCloud is sealed and cannot be used.")
        if name in self._registry:
            return self._registry[name]
        raise ValueError(f"Conduit with name {name} not found.")

    def _register_conduit(self, conduit: IConduit):
        """
        Register a conduit in the dynamic mode registry.
        :param conduit:
        :return:
        """
        if conduit.name is None:
            raise ValueError("Conduit name cannot be None.")

        if conduit.name in self._registry:
            raise ValueError(f"Conduit with name {conduit.name} already exists in the cloud. Please rename conduit to something unique.")
        self._registry[conduit.name] = conduit

    def seal(self):
        """
        Dispose of the ConduitCloud and all its conduits.
        """
        with self._lock:
            if self._sealed:
                return
            self._registry.clear()
            self._sealed = True

class Aether(ISeal):
    """
    Aether is a class that holds a reference to all conduit systems.
    Aether is also responsible for disposing of all conduits if required.

    It's a tool that will be used by conduits to link them together and
    allow them to communicate and extend their own behaviours.

    UUID for each conduit is created by __creation_context__.conduit_id in each conduit class.
    """
    _instance = None
    _lock = RLock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Aether, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Aether._initialized:
            super().__init__()
            Aether._initialized = True
            self._aetheric_frames: ConcurrentDict[str, AethericFrame] = ConcurrentDict()
            self._aetheric_frames["default"] = AethericFrame("default")
            self._default_frame = self._aetheric_frames["default"]


    def _reset_for_testing(self):
        with self._lock:
            self._default_frame._conduits.clear()
            self._default_frame._conduit_clusters.clear()
            self._default_frame._sealed = False
            self._sealed = False
            Aether._initialized = False
            Aether._instance = None

    def _bind_configuration(self, configuration, aetheric_frame_name: str = None) -> None:
        """
        Binds a configuration to the Aetheric Frame.
        :param configuration: The configuration to bind.
        :param aetheric_frame_name: The name of the Aetheric Frame to bind the configuration to.
        """
        if aetheric_frame_name is not None:
            try:
                self._aetheric_frames[aetheric_frame_name]._configuration = configuration
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._default_frame._configuration = configuration

    def _get_configuration(self, aetheric_frame_name: str = None) -> 'Configuration' or None:
        """
        Binds a configuration to the Aetheric Frame.
        :param aetheric_frame_name: The name of the Aetheric Frame to bind the configuration to.
        """
        if aetheric_frame_name is not None:
            try:
                return self._aetheric_frames[aetheric_frame_name]._configuration
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            return self._default_frame._configuration

    def _register_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = None):
        """
        Register a conduit in the dynamic mode registry.
        :param conduit:
        :return:
        """
        if aetheric_frame_name is not None:
            try:
                conduit_cloud =  self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_cloud = self._default_frame._conduit_cloud

        conduit_cloud._register_conduit(conduit)

    def _get_conduit_cloud(self, aetheric_frame_name: str = None) -> ConduitCloud:
        """
        Returns the conduit cloud associated with the specified Aetheric Frame.
        If no name is provided, returns the default frame's conduit cloud.
        """
        if aetheric_frame_name is not None:
            try:
                return self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            return self._default_frame._conduit_cloud

    def _check_for_spell(self, spell_id: str, aetheric_frame_name: str = None):
        """
        This will check if the spell exists within the spell registry.
        :param spell_id:
        :return:
        """
        if aetheric_frame_name is not None:
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

    def _add_spells_to_aether(self, conduit_id: uuid.UUID, spell_set: ConcurrentSet[str], aetheric_frame_name: str = None):
        """
        Register a group of spell IDs under a conduit ID in the global registry.

        Args:
            conduit_id: The UUID of the owning conduit.
            spell_set: A concurrent set of spell IDs to register.

        Raises:
            ValueError: If the conduit ID is already registered.
        """
        if aetheric_frame_name is not None:
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

    def get_conduit(self, name: str, aetheric_frame_name: str = None) -> IConduit:
        """
        Returns a conduit by its name.
        """
        if aetheric_frame_name is not None:
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

    def get_conduit_by_signature(self, signature: uuid.uuid4, aetheric_frame_name: str = None) -> IConduit:
        """
        Returns a conduit by its signature.
        """
        if aetheric_frame_name is not None:
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        if signature in conduits:
            return conduits[signature]
        raise ValueError(f"Conduit with signature {signature} not found.")

    def _add_conduit(self, conduit: IConduit, aetheric_frame_name: str = None):
        """
        Adds a new conduit to the Aether. This is primarily used by conduits internally. Not meant for external use.
        """
        if aetheric_frame_name is not None:
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        if conduit.__creation_context__._conduit_id in conduits:
            raise ValueError(f"Conduit with ID {conduit.__creation_context__._conduit_id} already exists.")
        conduits[conduit.__creation_context__._conduit_id] = conduit

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = None):
        """
        Removes a conduit from the Aether. Not meant for external use.
        """
        if aetheric_frame_name is not None:
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


    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = None):
        """
        Creates a new cluster in the Aether. Not meant for external use.
        """
        if aetheric_frame_name is not None:
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} already exists.")
        conduit_clusters[cluster_name] = ConcurrentList()

    def _add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = None):
        """
        Adds a conduit to a cluster in the Aether. Not meant for external use.
        """
        if aetheric_frame_name is not None:
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        conduit_clusters[cluster_name].append(conduit.__creation_context__._conduit_id)

    def _remove_conduit_from_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = None):
        """
        Removes a conduit from a cluster in the Aether. Not meant for external use.
        """
        if aetheric_frame_name is not None:
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        conduit_clusters[cluster_name].remove(conduit.__creation_context__._conduit_id)

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = None) -> ConcurrentList[uuid.UUID]:
        """
        Returns a list of conduits in a cluster. Not meant for external use.
        """
        if aetheric_frame_name is not None:
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        return conduit_clusters[cluster_name]

    def _link_conduit_by_signature(self, req_conduit, conduit_signature: uuid.uuid4, aetheric_frame_name: str = None):
        """
        Returns a conduit in order to link them. Not meant for external use.
        """
        raise NotImplementedError()
        for conduit in self._conduits.values():
            if conduit.signature == conduit_signature:
                req_conduit.link(conduit)
                return
        raise ValueError(f"Conduit signature: {conduit_signature}, not found.")

    def _link_conduit_by_name(self, req_conduit: IConduit, conduit_name: str, aetheric_frame_name: str = None):
        """
        Returns a conduit in order to link them. Not meant for external use.
        """
        raise NotImplementedError("Not implemented.")
        for conduit in self._conduits.values():
            if conduit.name == conduit_name:
                req_conduit.link(conduit)
                return
        raise ValueError(f"Conduit name: {conduit_name}, not found.")

    def seal(self):
        """
        Dispose of the Aether and all its conduits.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self.seal_aetheric_frames()
            self._default_frame = None
            self._aetheric_frames.clear()
            self._sealed = True


    def seal_aetheric_frames(self):
        """
        Seals all aetheric frames and their contents.
        """
        for frame in self._aetheric_frames.values():
            frame.seal()
