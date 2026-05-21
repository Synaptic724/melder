import threading
from typing import TYPE_CHECKING, Any, Dict, List, Optional, ClassVar

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.nexus import Nexus
    from melder.aether.aether import Aether
    from melder.aether.spellbook.bind.spell_index import SpellIndex

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.mutation_conduit import MutationConduit
from melder.mutation_research.mutation_frame import MutationFrame
from melder.mutation_research.research.creation.node.creation_mutation_node import (
    CreationMutationNode,
)
from melder.mutation_research.research.research import Research
from melder.mutation_research.research.spell.node.spell_mutation_node import (
    SpellMutationNode,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
class MutationResearch(Cleanable):
    """
    Singleton mutation-research root hosted by `Aether`.

    Purpose:
        Provide the process-wide mutation authority for spell and module
        mutation relationships without tying mutation ownership to one
        `AethericFrame`. The root manages research sessions keyed by
        `SpellIndex.id`, owns mutation configuration, and is the construction
        point for future runtime mutation facades such as `MutationConduit`
        and `MutationFrame`.

    Contract:
        - Singleton, mirroring the hosting pattern used by `Nexus` and
          `Crystallizer`.
        - Hosted by `Aether`, not by `AethericFrame`.
        - Owns configuration state and research sessions.
        - Does not itself own frame-local dev-ops or spell-system-state
          registries; those remain at runtime-local layers and are passed into
          future facades when needed.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _instance = None
    _lock = threading.RLock()
    _initialized = False
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_aether",
        "_configuration",
        "_configured",
        "_activated",
        "_sessions_by_index",
    ]

    def __new__(cls, *args, **kwargs):
        """
        Return the singleton MutationResearch instance.

        Returns:
            MutationResearch: Process-wide mutation-research root.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MutationResearch, cls).__new__(cls)
        return cls._instance

    def __init__(
            self,
            aether: Aether,
            *,
            configuration: Optional[MutationResearchConfiguration] = None,
    ) -> None:
        """
        Initialize the singleton mutation-research root.

        Args:
            aether:
                Hosting `Aether` singleton. First-time initialization requires
                this host.
            configuration:
                Optional initial mutation-research configuration.

        Returns:
            None.
        """
        if MutationResearch._initialized:
            return
        try:
            super().__init__()
            self._id: str = IDBuilder.create_id()
            self._aether: Optional[Aether] = aether
            self._configuration: Optional[MutationResearchConfiguration] = None
            self._configured: bool = False
            self._activated: bool = False
            self._sessions_by_index: Dict[str, Research] = {}
            if configuration is not None:
                self.configure(configuration)
            MutationResearch._initialized = True
        except Exception:
            with MutationResearch._lock:
                if MutationResearch._instance is self:
                    MutationResearch._instance = None
                MutationResearch._initialized = False
            raise

    def cleanup(self) -> None:
        """
        Idempotently clear mutation-research root state and reset singleton bookkeeping.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._sessions_by_index is not None:
                for _, session in list(self._sessions_by_index.items()):
                    try:
                        session.cleanup()
                    except Exception:
                        pass
                self._sessions_by_index.clear()
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False

            del self._sessions_by_index
            del self._configuration
            del self._aether
            del self._id
        with MutationResearch._lock:
            MutationResearch._instance = None
            MutationResearch._initialized = False

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the singleton for isolated test setup.

        Returns:
            None.
        """
        with cls._lock:
            instance = cls._instance
        if instance is not None:
            if getattr(instance, "_cleaned", None) is False:
                instance.cleanup()
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    @property
    def id(self) -> str:
        """
        Return the stable root id.

        Returns:
            str: Stable root id.
        """
        self.check_cleaned()
        return self._id

    @property
    def configured(self) -> bool:
        """
        Return whether a configuration is installed.

        Returns:
            bool: True when the root has an installed configuration.
        """
        self.check_cleaned()
        return self._configured

    @property
    def is_configured(self) -> bool:
        """
        Alias for the configured-state flag.

        Returns:
            bool: True when a configuration is installed.
        """
        return self.configured

    @property
    def activated(self) -> bool:
        """
        Return whether the mutation-research root is active.

        Returns:
            bool: True when configuration is installed and activated.
        """
        self.check_cleaned()
        return self._activated

    @property
    def is_activated(self) -> bool:
        """
        Alias for the activated-state flag.

        Returns:
            bool: True when the root is active.
        """
        return self.activated

    @property
    def configuration(self) -> Optional[MutationResearchConfiguration]:
        """
        Return the installed configuration, if any.

        Returns:
            Optional[MutationResearchConfiguration]: Installed configuration.
        """
        self.check_cleaned()
        return self._configuration

    def create_configuration(self) -> MutationResearchConfiguration:
        """
        Create a fresh mutation-research configuration object.

        Returns:
            MutationResearchConfiguration: New mutable config object.
        """
        self.check_cleaned()
        return MutationResearchConfiguration()

    def create_configuration_builder(self) -> MutationResearchConfigurationBuilder:
        """
        Create a fresh fluent builder for mutation-research configuration assembly.

        Returns:
            MutationResearchConfigurationBuilder: New builder instance.
        """
        self.check_cleaned()
        return MutationResearchConfigurationBuilder()

    def configure(self, configuration: MutationResearchConfiguration) -> None:
        """
        Install one configuration on the mutation-research root.

        Args:
            configuration:
                Configuration object to install.

        Returns:
            None.

        Raises:
            TypeError:
                If the supplied object is not a mutation-research
                configuration.
            RuntimeError:
                If mutation research is already active.
        """
        self.check_cleaned()
        if not isinstance(configuration, MutationResearchConfiguration):
            raise TypeError(
                "configuration must be a MutationResearchConfiguration instance."
            )
        with self._lock:
            if self._activated:
                raise RuntimeError(
                    "Cannot reconfigure MutationResearch while it is active."
                )
            self._configuration = configuration
            self._configured = True

    def activate(
            self,
            configuration: Optional[MutationResearchConfiguration] = None,
    ) -> None:
        """
        Activate the mutation-research root using one activated configuration.

        Args:
            configuration:
                Optional configuration to install before activation.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no configuration is installed or the configuration has not
                itself been activated.
        """
        self.check_cleaned()
        if configuration is not None:
            self.configure(configuration)
        self._require_configured()
        if not self._configuration.activated:
            raise RuntimeError(
                "MutationResearchConfiguration must be activated before activating MutationResearch."
            )
        self._configuration.validate()
        with self._lock:
            self._activated = True

    def deactivate(self) -> None:
        """
        Deactivate the mutation-research root without dropping configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._activated = False

    def create_mutation_conduit(self, conduit: Conduit) -> MutationConduit:
        """
        Create one placeholder mutation-conduit facade for a live conduit.

        Args:
            conduit:
                Underlying conduit reference for the placeholder.

        Returns:
            MutationConduit: Placeholder mutation-conduit object.
        """
        self.check_cleaned()
        if conduit is None:
            raise ValueError("conduit cannot be None.")
        spellbook = conduit._spellbook
        if spellbook is None:
            raise RuntimeError("Conduit has no spellbook.")
        spell_system_states = spellbook._spell_system_states
        change_control = self._aether._get_change_control_manager(conduit._aetheric_frame_name)
        return MutationConduit(
            conduit=conduit,
            mutation_research=self,
            spell_system_states=spell_system_states,
            change_control_manager=change_control,
        )

    def create_mutation_frame(self, aetheric_frame_name: str = "default") -> MutationFrame:
        """
        Create one placeholder mutation-frame facade for a named frame.

        Args:
            aetheric_frame_name:
                Frame name the placeholder should coordinate.

        Returns:
            MutationFrame: Placeholder mutation-frame object.
        """
        self.check_cleaned()
        spell_system_states = self._aether._get_spell_system_states(aetheric_frame_name)
        change_control = self._aether._get_change_control_manager(aetheric_frame_name)
        return MutationFrame(
            aetheric_frame_name=aetheric_frame_name,
            mutation_research=self,
            spell_system_states=spell_system_states,
            change_control_manager=change_control,
        )

    def create_session(
            self,
            target_index: SpellIndex,
            *,
            name: Optional[str] = None,
            level: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Research:
        """
        Create or return one `Research` session anchored to a spell lineage.

        Args:
            target_index:
                Spell lineage to anchor the session to.
            name:
                Human-friendly name for the session.
            level:
                Optional level/difficulty metadata for the session.
            metadata:
                Arbitrary metadata attached to the session.

        Returns:
            Research: Resolved or newly created research session.
        """
        self.check_cleaned()
        if target_index is None:
            raise ValueError("target_index cannot be None")

        index_id = getattr(target_index, "id", None)
        if not index_id:
            raise ValueError("SpellIndex is expected to expose a non-empty 'id' attribute.")

        session_name = name or f"Research:{index_id}"

        with self._lock:
            if self._sessions_by_index is None:
                raise RuntimeError("MutationResearch has been cleaned.")

            existing = self._sessions_by_index.get(index_id)
            if existing is not None:
                return existing

            session = Research(
                target_index=target_index,
                name=session_name,
                level=level,
                metadata=metadata,
            )
            self._sessions_by_index[index_id] = session
            return session

    def get_session_for_index(self, target_index: SpellIndex) -> Optional[Research]:
        """
        Retrieve the `Research` session for a given SpellIndex, if it exists.

        Args:
            target_index:
                Spell lineage to search for.

        Returns:
            Optional[Research]: Matching research session, or `None`.
        """
        self.check_cleaned()
        if target_index is None:
            return None

        index_id = getattr(target_index, "id", None)
        if not index_id:
            return None

        with self._lock:
            if self._sessions_by_index is None:
                return None
            return self._sessions_by_index.get(index_id)

    def get_session_by_index_id(self, index_id: str) -> Optional[Research]:
        """
        Retrieve the `Research` session by SpellIndex id, if it exists.

        Args:
            index_id:
                SpellIndex ULID string.

        Returns:
            Optional[Research]: Matching research session, or `None`.
        """
        self.check_cleaned()
        if not index_id:
            return None

        with self._lock:
            if self._sessions_by_index is None:
                return None
            return self._sessions_by_index.get(index_id)

    def list_sessions(self) -> List[Research]:
        """
        Return all registered research sessions.

        Returns:
            List[Research]: All live research sessions.
        """
        self.check_cleaned()
        with self._lock:
            if self._sessions_by_index is None:
                return []
            return list(self._sessions_by_index.values())

    def remove_session_for_index(self, target_index: SpellIndex) -> None:
        """
        Remove and cleanup the session associated with one SpellIndex, if present.

        Args:
            target_index:
                Spell lineage whose session should be removed.

        Returns:
            None.
        """
        self.check_cleaned()
        if target_index is None:
            return

        index_id = getattr(target_index, "id", None)
        if not index_id:
            return

        with self._lock:
            if self._sessions_by_index is None:
                return
            session = self._sessions_by_index.pop(index_id, None)

        if session is not None:
            try:
                session.cleanup()
            except Exception:
                pass

    def begin_spell_mutation(
            self,
            target_index: SpellIndex,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ) -> "SpellMutationNode":
        """
        Start one spell-mutation line for the current version of a spell index.

        Args:
            target_index:
                Spell lineage to target.
            research_name:
                Optional research/session name.
            message:
                Message for the new mutation node.
            tags:
                Tags for the new mutation node.

        Returns:
            SpellMutationNode: Newly created uncommitted mutation node.
        """
        self.check_cleaned()
        if target_index is None:
            raise ValueError("target_index cannot be None")

        session = self.get_session_for_index(target_index)
        if session is None:
            session = self.create_session(target_index, name=research_name)

        current_id = getattr(target_index, "current", None)
        if not current_id:
            raise RuntimeError("SpellIndex.current is not set; cannot begin spell mutation.")

        spell_research = None
        for candidate in session.list_spell_researches():
            if candidate.spell_id == current_id:
                spell_research = candidate
                break

        if spell_research is None:
            spell_research = session.start_spell_research(current_id, name=research_name)

        return spell_research.begin_mutation(message=message, tags=tags)

    def begin_creation_mutation(
            self,
            target_index: SpellIndex,
            creation_id: str,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ) -> "CreationMutationNode":
        """
        Start one creation-mutation line for a specific creation id.

        Args:
            target_index:
                Spell lineage to associate with the mutation.
            creation_id:
                Creation identifier to mutate.
            research_name:
                Optional research/session name.
            message:
                Message for the new mutation node.
            tags:
                Tags for the new mutation node.

        Returns:
            CreationMutationNode: Newly created uncommitted mutation node.
        """
        self.check_cleaned()
        if target_index is None:
            raise ValueError("target_index cannot be None")
        if not creation_id:
            raise ValueError("creation_id cannot be empty")

        session = self.get_session_for_index(target_index)
        if session is None:
            session = self.create_session(target_index, name=research_name)

        creation_research = None
        for candidate in session.list_creation_researches():
            if candidate.creation_id == creation_id:
                creation_research = candidate
                break

        if creation_research is None:
            creation_research = session.start_creation_research(creation_id, name=research_name)

        return creation_research.begin_mutation(message=message, tags=tags)

    def _require_configured(self) -> None:
        """
        Raise when no configuration is installed.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no configuration is installed.
        """
        if not self._configured or self._configuration is None:
            raise RuntimeError(
                "MutationResearchConfiguration must be configured before this operation."
            )


