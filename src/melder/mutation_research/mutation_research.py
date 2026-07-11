import threading
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.crystallizer.crystallizer import Crystallizer

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.research_set.research_set import ResearchSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class MutationResearch(Cleanable):
    """
    Singleton mutation-research root hosted by `Aether`.

    Purpose:
        Own the formal declaration record of research over the live spell
        world. The root manages `ResearchSet` networks by name (one
        guaranteed `default` set), carries the mutation-research
        configuration lifecycle, and is the ONLY object in the package that
        touches the crystallizer: sets emit detached payloads through an
        injected callback, and the root records them into the persistence
        layer as the `MutationResearchCrystal` composition payload.

    Contract:
        - Singleton, mirroring the hosting pattern used by `Nexus` and
          `Crystallizer`; hosted by `Aether`, not by `AethericFrame`.
        - Owns configuration state and the research-set registry.
        - Emission is replace-on-emit through `Crystallizer.emit(...)` and is
          a NO-OP while the crystallizer records nothing; lifecycle flips
          ride the `RecordedUnitState` switch as before.
        - Conduits and frames carry NO mutation dimension: the old
          conduit/frame facades and SpellIndex-keyed sessions are out of the
          model and gone.

    Threading:
        Class lock guards singleton identity; instance verbs serialize under
        the same reentrant lock; lock order is root -> set -> crystallizer,
        one-way.

    Lifecycle:
        `cleanup()` cascades into owned sets and configuration, emits the
        cleaned state while the record outlives the root, and resets
        singleton bookkeeping; idempotent.
    """

    DEFAULT_RESEARCH_SET_NAME: ClassVar[str] = "default"

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _instance: ClassVar[Optional["MutationResearch"]] = None
    _lock: ClassVar[threading.RLock] = threading.RLock()
    _initialized: ClassVar[bool] = False
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_aether",
        "_configuration",
        "_configured",
        "_activated",
        "_research_sets_by_name",
        "_crystallizer",
    ]

    def __new__(
            cls,
            *args: object,
            **kwargs: object,
    ) -> "MutationResearch":
        """
        Return the singleton MutationResearch instance.

        Returns:
            MutationResearch: Process-wide mutation-research root.
        """
        instance = cls._instance
        if instance is None:
            with cls._lock:
                instance = cls._instance
                if instance is None:
                    instance = super(MutationResearch, cls).__new__(cls)
                    cls._instance = instance
        assert instance is not None
        return instance

    def __init__(
            self,
            aether: "Aether",
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
            self._aether: Optional["Aether"] = aether
            self._crystallizer: "Crystallizer" = aether._crystallizer
            self._configuration: Optional[MutationResearchConfiguration] = None
            self._configured: bool = False
            self._activated: bool = False
            self._research_sets_by_name: Dict[str, ResearchSet] = {}
            self._research_sets_by_name[
                MutationResearch.DEFAULT_RESEARCH_SET_NAME
            ] = ResearchSet(
                MutationResearch.DEFAULT_RESEARCH_SET_NAME,
                on_mutation=self._emit_research_composition,
            )
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
            # Record the teardown when the record outlives MR. In the Aether
            # full-teardown lane the crystallizer is already cleaned
            # (frames -> crystallizer -> MR), so this skips there.
            if not self._crystallizer.cleaned and self._crystallizer.activated:
                self._crystallizer.emit_mutation_research_state(
                    RecordedUnitState.cleaned
                )
            if self._research_sets_by_name is not None:
                for _, research_set in list(
                        self._research_sets_by_name.items()
                ):
                    try:
                        research_set.cleanup()
                    except Exception:
                        pass
                self._research_sets_by_name.clear()
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False
            del self._crystallizer
            del self._research_sets_by_name
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
            # Record the lifecycle flip: the twin (emitted at configuration
            # activation) is retained; the switch carries activation truth.
            if self._crystallizer.activated:
                self._crystallizer.emit_mutation_research_state(
                    RecordedUnitState.enabled
                )
        # Activation makes the composition recordable: re-emit the twin so
        # the record carries whatever research already exists.
        self._emit_research_composition()

    def deactivate(self) -> None:
        """
        Deactivate the mutation-research root without dropping configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._activated = False
            # Deactivate keeps the installed configuration, so the twin
            # stays; the record flips the state switch instead of evicting.
            if self._crystallizer.activated:
                self._crystallizer.emit_mutation_research_state(
                    RecordedUnitState.disabled
                )

    # ------------------------------------------------------------------
    # Research-set registry
    # ------------------------------------------------------------------

    def research_set(
            self,
            name: str = "default",
    ) -> ResearchSet:
        """
        Return one owned research set by name.

        Args:
            name:
                Set name; the guaranteed `default` set when omitted.

        Returns:
            ResearchSet: Owned research network.

        Raises:
            KeyError:
                If no set carries the name; the error lists known names.
        """
        self.check_cleaned()
        with self._lock:
            research_set = self._research_sets_by_name.get(name)
            if research_set is None:
                known = sorted(self._research_sets_by_name.keys())
                raise KeyError(
                    f"MutationResearch has no research set '{name}'. "
                    f"Known sets: {known}."
                )
            return research_set

    def create_research_set(self, name: str) -> ResearchSet:
        """
        Create one additional named research set.

        Args:
            name:
                Unique set name.

        Returns:
            ResearchSet: Newly created research network.

        Raises:
            ValueError:
                If the name is empty or already registered.
        """
        self.check_cleaned()
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string.")
        with self._lock:
            if name in self._research_sets_by_name:
                raise ValueError(
                    f"MutationResearch already owns a research set '{name}'."
                )
            research_set = ResearchSet(
                name,
                on_mutation=self._emit_research_composition,
            )
            self._research_sets_by_name[name] = research_set
        self._emit_research_composition()
        return research_set

    def list_research_set_names(self) -> List[str]:
        """
        Return every owned research-set name, sorted.

        Returns:
            List[str]: Sorted set names.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._research_sets_by_name.keys())

    def describe_research_composition(self) -> Dict[str, object]:
        """
        Return the detached composition payload across every owned set.

        Returns:
            Dict[str, object]:
                set name -> `ResearchSet.describe_composition()` payload
                (bounded journal windows; the twin feed).
        """
        self.check_cleaned()
        with self._lock:
            return {
                name: research_set.describe_composition()
                for name, research_set in self._research_sets_by_name.items()
            }

    def load_recorded_composition(
            self,
            composition_payload: Dict[str, object],
    ) -> None:
        """
        Rebuild the research-set registry from a recorded composition.

        Purpose:
            The hydration seam: a recorded `MutationResearchCrystal`
            composition payload replaces the current registry wholesale (the
            record is the truth being loaded, never merged). The guaranteed
            `default` set is recreated when the recording lacks one.

        Args:
            composition_payload:
                Mapping of set name -> `describe_composition()` payload, as
                recorded by `describe_research_composition()`.

        Returns:
            None.

        Raises:
            ValueError:
                If the payload is not a mapping of set payloads.
        """
        self.check_cleaned()
        if not isinstance(composition_payload, dict):
            raise ValueError(
                "composition_payload must be a dict of set payloads."
            )
        with self._lock:
            rebuilt: Dict[str, ResearchSet] = {}
            for name, set_payload in composition_payload.items():
                rebuilt[str(name)] = ResearchSet.from_payload(
                    set_payload,
                    on_mutation=self._emit_research_composition,
                )
            if MutationResearch.DEFAULT_RESEARCH_SET_NAME not in rebuilt:
                rebuilt[
                    MutationResearch.DEFAULT_RESEARCH_SET_NAME
                ] = ResearchSet(
                    MutationResearch.DEFAULT_RESEARCH_SET_NAME,
                    on_mutation=self._emit_research_composition,
                )
            for _, research_set in list(self._research_sets_by_name.items()):
                try:
                    research_set.cleanup()
                except Exception:
                    pass
            self._research_sets_by_name = rebuilt
        self._emit_research_composition()

    # ------------------------------------------------------------------
    # Persistence emission seam
    # ------------------------------------------------------------------

    def _emit_research_composition(self) -> None:
        """
        Re-emit the MutationResearchCrystal twin with the live composition.

        Contract:
            - The single crystallizer touchpoint for research state: sets
              call this through their injected `on_mutation` callback after
              every successful mutating verb; the root also calls it at
              activation and after hydration.
            - NO-OP while the root is inactive, or while the crystallizer is
              cleaned/inactive (the sink additionally no-ops when recording
              is off, preserving the R-A covenant).

        Returns:
            None.
        """
        if self._cleaned or not self._activated:
            return
        crystallizer = self._crystallizer
        if crystallizer.cleaned:
            return
        if not crystallizer.activated:
            return
        configuration_payload: Dict[str, object] = {}
        if self._configured and self._configuration is not None:
            configuration_payload = (
                self._configuration.describe_configuration_payload()
            )
        crystallizer.emit(
            MutationResearchCrystal(
                activated=self._activated,
                configuration_payload=configuration_payload,
                composition_payload=self.describe_research_composition(),
            )
        )

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
                "MutationResearchConfiguration must be configured before "
                "this operation."
            )
