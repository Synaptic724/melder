import ast
import difflib
import hashlib
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Callable, ClassVar, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.crystallizer.crystallizer import Crystallizer

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
from melder.mutation_research.diff.diff_engine import DiffEngine
from melder.mutation_research.group_diff.group_diff_engine import (
    GroupDiffEngine,
)
from melder.mutation_research.research_set.grouped_research_node import (
    GroupedResearchNode,
)
from melder.mutation_research.research_set.research_set import ResearchSet
from melder.mutation_research.synthesis.structural_synthesizer import (
    StructuralSynthesizer,
)
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
        the same reentrant lock. A dedicated reentrant emission lock makes
        the persistence emission atomic (snapshot build + replace-on-emit
        publication happen under one holder, so a paused emitter can never
        publish a stale composition over a newer one). Lock order is
        emission -> root -> set -> crystallizer, one-way: every path that
        can trigger an emission while holding the root lock (set creation,
        hydration) acquires the emission lock first.

    Lifecycle:
        `cleanup()` cascades into owned sets and configuration, emits the
        cleaned state while the record outlives the root, and resets
        singleton bookkeeping; idempotent.

    Registration:
        MELDER KERNEL - guarded. Reached through `Aether.mutation_research`;
        constructing or registering a second root would break the singleton
        contract the emission model depends on.

    IT IS THE ONLY CRYSTALLIZER TOUCHPOINT IN THE PACKAGE:
        Sets do not emit. They fire an injected `on_mutation` callback and this
        root does the recording. That single-writer rule is what keeps the
        dependency acyclic - the record layer never has to know about research
        internals, and research never has to know about persistence mechanics.

        It is also why the emission lock exists and why lock order is
        emission -> root -> set -> crystallizer, strictly one-way. Set
        constructors fire `on_mutation` while the root lock is held, so any path
        that can emit while holding the root - set creation, hydration - must
        take the emission lock FIRST. Without that, a paused emitter could
        publish a stale composition over a newer one, since emission is
        replace-on-emit.

    Subsystem Context:
        The package root, hosting `ResearchSet` networks by name with a
        guaranteed `default`. Sets own the record; the root owns the sets, the
        configuration lifecycle, and the emission seam. The diff engines and the
        synthesizer are also root-owned, which is why they receive injected
        resolvers rather than reaching for custody themselves.

    System Context:
        Hosted by `Aether`, not by a frame - deliberately. Frames carry NO
        mutation dimension, so research is a WORLD-scope concern that outlives
        any individual frame or conduit. Spellbook and Conduit reach it through
        borrowed read-only accessor properties rather than owning it. In the
        boot order it sits after the crystallizer and before Nexus, which is
        exactly why configuration activation must carry the recorded composition
        forward: the config's emission moment necessarily precedes the root's.


    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The research root, reached through Aether. Configure and activate, then
        create_research_set(...) and use the read verbs: source_view, impact_view, module_view,
        part_view, diff_research, residency_view, group_view.
    """

    DEFAULT_RESEARCH_SET_NAME: ClassVar[str] = "default"

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
        "_diff_engine",
        "_group_diff_engine",
        "_synthesizer",
        "_active_campaign",
        "_staged_ancestry",
        "_crystallizer",
        "_emission_lock",
    ]

    def __new__(
            cls,
            *args: object,
            **kwargs: object,
    ) -> "MutationResearch":
        """
        Return the singleton MutationResearch instance.

        Contract:
            - PROCESS-WIDE SINGLETON via double-checked locking: every construction
              returns THE SAME instance. There is no way to get a second one.
            - The fast path reads the cached instance without the lock and only
              locks on the miss, so steady-state construction is uncontended.

        Threading:
            Double-checked under the class lock; safe to call concurrently.

        Lifecycle / Cleanup:
            Allocation only - initialization state is handled by `__init__`.

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
        return instance

    def __init__(
            self,
            *,
            aether: Optional["Aether"] = None,
            configuration: Optional[MutationResearchConfiguration] = None,
    ) -> None:
        """
        Initialize the singleton mutation-research root.

        Args:
            aether:
                Optional hosting `Aether` singleton. First-time initialization
                requires this host; later constructions are lookups and ignore
                it. Reach this root through `Aether.mutation_research` rather
                than constructing it - that accessor supplies the host.
            configuration:
                Optional initial mutation-research configuration.

        Contract:
            - RUNS ITS BODY ONCE. Because the class is a singleton, a second
              construction returns early, which means CONSTRUCTOR ARGUMENTS ARE
              SILENTLY IGNORED after the first call - passing a different `aether`
              does NOT rebind the existing instance. Treat later calls as lookups,
              not configuration.
            - ROLLS BACK ITS OWN ALLOCATION when constructed without an Aether
              before the singleton is initialized: it clears `_instance` and the
              initialized flag so the half-built object is NOT left installed,
              then raises `ValueError`. This matches `Crystallizer` and `Nexus`
              exactly, and it is why a pre-boot `MutationResearch()` probe is
              safe - a later proper construction still gets a clean singleton.
              Before this rollback existed the missing host raised `TypeError`
              from the signature, which fired BEFORE any cleanup could run and
              left `_instance` pointing at an object whose `_cleaned` slot was
              never assigned; `_reset_singleton_for_tests` then raised
              `AttributeError` on every subsequent use.
            - Establishes a dedicated emission lock that must exist before the first
              `ResearchSet` fires `on_mutation`, so snapshot build and publication in
              the emission seam are serialized from the very first event.

        Owned State:
            Owns its id, the emission lock, and the research-set registry. BORROWS
            the hosting Aether.

        Threading:
            Initialization is guarded by the singleton flag; the emission lock it
            creates serializes the publication seam thereafter.

        Lifecycle / Cleanup:
            One-time. Later constructions are no-ops that return the live instance.

        Returns:
            None.
        """
        if MutationResearch._initialized:
            return

        if aether is None:
            with MutationResearch._lock:
                if (
                        MutationResearch._instance is self
                        and not MutationResearch._initialized
                ):
                    MutationResearch._instance = None
                    MutationResearch._initialized = False
            raise ValueError(
                "Aether must be provided to initialize MutationResearch."
            )

        try:
            super().__init__()
            self._id: str = IDBuilder.create_id()
            # Serializes snapshot build + publication in the emission seam;
            # must exist before the first ResearchSet fires on_mutation.
            self._emission_lock: threading.RLock = threading.RLock()
            self._aether: "Aether" = aether
            self._crystallizer: "Crystallizer" = aether._crystallizer
            self._configuration: Optional[MutationResearchConfiguration] = None
            self._configured: bool = False
            self._activated: bool = False
            self._research_sets_by_name: Dict[str, ResearchSet] = {}
            self._diff_engine: Optional[DiffEngine] = None
            self._group_diff_engine: Optional[GroupDiffEngine] = None
            self._synthesizer: Optional[StructuralSynthesizer] = None
            self._active_campaign: Optional[str] = None
            self._staged_ancestry: Optional[List[str]] = None
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

        Contract:
            - IDEMPOTENT under double-checked locking: it returns immediately if already
              cleaned, then re-checks inside the lock.
            - Tears down research-set state; the hosting Aether is BORROWED and is not
              cleaned here.
            - The teardown state emission is BEST-EFFORT: a raising sink is
              swallowed so the cascade (sets, engines, configuration) and
              the singleton reset always complete.

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
            # Best-effort by contract (BUG-036): the state sink is an
            # optional observer - a raising sink must never abort the
            # cascade or the singleton reset, or cleanup wedges
            # half-complete forever behind the idempotency guard.
            try:
                if (
                        not self._crystallizer.cleaned
                        and self._crystallizer.activated
                ):
                    self._crystallizer.emit_mutation_research_state(
                        RecordedUnitState.cleaned
                    )
            except Exception:
                pass
            for _, research_set in list(
                    self._research_sets_by_name.items()
            ):
                try:
                    research_set.cleanup()
                except Exception:
                    pass
            self._research_sets_by_name.clear()
            if self._diff_engine is not None:
                try:
                    self._diff_engine.cleanup()
                except Exception:
                    pass
            if self._group_diff_engine is not None:
                try:
                    self._group_diff_engine.cleanup()
                except Exception:
                    pass
            if self._synthesizer is not None:
                try:
                    self._synthesizer.cleanup()
                except Exception:
                    pass
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False
            del self._crystallizer
            del self._emission_lock
            del self._diff_engine
            del self._group_diff_engine
            del self._synthesizer
            del self._active_campaign
            del self._staged_ancestry
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
        if instance is not None and not instance._cleaned:
            instance.cleanup()
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    @property
    def id(self) -> str:
        """
        Return the stable root id.

        Contract:
            - Identifies the singleton instance; assigned once at first construction and
              stable for the process.
            - Distinct from any research-set or lane id.
            - Identifies the singleton instance, assigned once at first construction
              and stable for the process.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            str: Stable root id.
        """
        self.check_cleaned()
        return self._id

    @property
    def configured(self) -> bool:
        """
        Return whether a configuration is installed.

        Contract:
            - Reports that a configuration has been INSTALLED, not that mutation
              research is running - that is `activated`.
            - `deactivate()` does NOT clear this: the configuration stays installed
              and only the activation flag flips. So `configured and not activated`
              is the normal deactivated state, not an inconsistency.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            bool: True when the root has an installed configuration.
        """
        self.check_cleaned()
        return self._configured

    @property
    def is_configured(self) -> bool:
        """
        Alias for the configured-state flag.

        Contract:
            - ALIAS for the `configured` property, kept for call-site readability.
            - Identical behaviour and identical guard - there is no difference to choose
              between.
            - ALIAS for the `configured` property, kept for call-site readability.
              Identical behaviour and identical guard - there is no difference to
              choose between.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            bool: True when a configuration is installed.
        """
        return self.configured

    @property
    def activated(self) -> bool:
        """
        Return whether the mutation-research root is active.

        Contract:
            - Reports that mutation research is LIVE. Activation implies a
              configuration is installed; the converse does not hold.
            - Flipped back to False by `deactivate()` without losing configuration.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            bool: True when configuration is installed and activated.
        """
        self.check_cleaned()
        return self._activated

    @property
    def is_activated(self) -> bool:
        """
        Alias for the activated-state flag.

        Contract:
            - ALIAS for the `activated` property, kept for call-site readability.
            - Identical behaviour and identical guard.
            - ALIAS for the `activated` property, kept for call-site readability.
              Identical behaviour and identical guard.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            bool: True when the root is active.
        """
        return self.activated

    @property
    def configuration(self) -> Optional[MutationResearchConfiguration]:
        """
        Return the installed configuration, if any.

        Contract:
            - Returns the INSTALLED configuration by reference, not a copy. It stays
              non-None after `deactivate()`, because deactivation keeps the install.
            - None means nothing has been installed yet.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            Optional[MutationResearchConfiguration]: Installed configuration.
        """
        self.check_cleaned()
        return self._configuration

    def create_configuration(self) -> MutationResearchConfiguration:
        """
        Create a fresh mutation-research configuration object.

        Contract:
            - FACTORY ONLY. It returns a FRESH, EMPTY, UNATTACHED configuration and
              does NOT install it on this singleton - installation is a separate
              step. Calling it twice yields two unrelated objects.
            - The returned configuration starts empty, so seed it before freezing.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            MutationResearchConfiguration: New mutable config object.
        """
        self.check_cleaned()
        return MutationResearchConfiguration()

    def create_configuration_builder(self) -> MutationResearchConfigurationBuilder:
        """
        Create a fresh fluent builder for mutation-research configuration assembly.

        Contract:
            - FACTORY ONLY. Returns a fresh builder wrapping a new configuration and
              does NOT install anything here.
            - Remember the builder's exits are one-shot: `build()` yields a MUTABLE
              configuration, `finalize()` a frozen one, `activate()` an activated one.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            MutationResearchConfigurationBuilder: New builder instance.
        """
        self.check_cleaned()
        return MutationResearchConfigurationBuilder()

    def configure(self, configuration: MutationResearchConfiguration) -> None:
        """
        Install one configuration on the mutation-research root.

        Contract:
            - INSTALLS ONLY - it does not validate, freeze or activate, and it accepts a
              configuration that is still mutable.
            - Type-checked: a non-`MutationResearchConfiguration` raises `TypeError`.

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
            *,
            hydrate_from_record: bool = True,
    ) -> None:
        """
        Activate the mutation-research root using one activated configuration.

        Contract:
            - ORDERING RULE: THE CONFIGURATION MUST BE ACTIVATED FIRST. Activating with a
              merely-frozen configuration raises.
            - Two distinct failure modes: "not configured" and "configuration not
              activated".

        Args:
            configuration:
                Optional configuration to install before activation.
            hydrate_from_record:
                When True (default), an UNTOUCHED registry (nothing but
                the pristine default set) rebuilds itself from the active
                profile's recorded composition at activation - the twin
                docking loop: emit while live, hydrate on the way up. Live
                research is never clobbered; a touched registry skips
                hydration and re-records itself instead. Hydration runs
                BEFORE the root reports active, so the public ingress can
                never open into a registry that is about to be swapped.

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
        # Hydration precedes the activation flip (BUG-035): the public
        # ingress opens when the root reports active, so completing the
        # untouched-check/registry-swap FIRST guarantees live research recorded
        # through the documented seam can never race the swap and be
        # clobbered. Mid-hydration emissions no-op on the inactive guard;
        # the final emission below records the hydrated (or live) truth.
        if hydrate_from_record:
            self._hydrate_from_record()
        with self._lock:
            self._activated = True
            # Record the lifecycle flip: the twin (emitted at configuration
            # activation) is retained; the switch carries activation truth.
            if self._crystallizer.activated:
                self._crystallizer.emit_mutation_research_state(
                    RecordedUnitState.enabled
                )
        # Policy propagation AFTER hydration so rebuilt sets carry the
        # configured posture too (sets stay configuration-free).
        self._propagate_lane_type_enforcement()
        # Activation makes the composition recordable: re-emit the twin so
        # the record carries whatever research exists now (hydrated or live).
        self._emit_research_composition()

    def _propagate_lane_type_enforcement(self) -> None:
        """
        Push the configured lane-type-enforcement posture onto every set.

        Contract:
            - NO-OP while unconfigured or when the configuration predates
              the `lane_type_enforcement` key (absent = off, the default).

        Returns:
            None.
        """
        if not self._configured:
            return
        if not self._configuration.has_property("lane_type_enforcement"):
            return
        enabled = bool(
            self._configuration.get_property("lane_type_enforcement")
        )
        with self._lock:
            research_sets = list(self._research_sets_by_name.values())
        for research_set in research_sets:
            research_set.set_lane_type_enforcement(enabled)

    def _registry_is_untouched(self) -> bool:
        """
        Return whether no research has ever been declared on this root.

        Contract:
            - Untouched means exactly the guaranteed default set with its
              untouched default lane: one set, one lane, zero registered
              versions, and no journal history beyond the birth event.

        Returns:
            bool:
                True when hydration may safely replace the registry.
        """
        with self._lock:
            if len(self._research_sets_by_name) != 1:
                return False
            default_set = self._research_sets_by_name.get(
                MutationResearch.DEFAULT_RESEARCH_SET_NAME
            )
            if default_set is None:
                return False
            if default_set.lane_names() != [ResearchSet.DEFAULT_LANE_NAME]:
                return False
            if default_set.default_lane.node_count != 0:
                return False
            return default_set.journal.latest_sequence <= 1

    def _hydrate_from_record(self) -> None:
        """
        Rebuild an untouched registry from the recorded composition, when any.

        Contract:
            - NO-OP while the crystallizer is cleaned/inactive, when the
              active profile has never recorded the MR twin, when the
              recorded composition is empty, or when live research already
              exists (live truth wins; it re-records at the next emission).

        Returns:
            None.
        """
        crystallizer = self._crystallizer
        if not crystallizer.activated:
            return
        recorded = crystallizer.describe_mutation_research_record()
        if recorded is None:
            return
        composition = recorded.get("composition_payload")
        if not isinstance(composition, dict) or not composition:
            return
        if not self._registry_is_untouched():
            return
        self.load_recorded_composition(composition)

    def deactivate(self) -> None:
        """
        Deactivate the mutation-research root without dropping configuration.

        Contract:
            - KEEPS THE INSTALLED CONFIGURATION. It flips the activation switch only,
              so `configured` stays True and the recorded twin is not evicted - the
              state record flips to `disabled` instead of being removed.
            - That makes deactivate REVERSIBLE without re-supplying configuration,
              which is the whole point of separating the two flags.
            - Emits a state record only when the crystallizer is activated, so a
              missing record does not imply the deactivation failed.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

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

        Contract:
            - REQUIRED lookup: an unknown name RAISES, and the error LISTS THE KNOWN NAMES
              so a typo is self-diagnosing.
            - Omitting the name resolves the default set rather than returning all sets.

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

        Contract:
            - LOCK ORDER LAW: THE EMISSION LOCK IS TAKEN BEFORE THE ROOT LOCK. The set
              constructor fires `on_mutation` while the root lock is held, so the one-way
              order is emission -> root. Reversing it deadlocks.
            - Rejects a non-string or empty name up front.

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
        # Emission lock first: the set constructor fires on_mutation while
        # the root lock is held, and the one-way order is emission -> root.
        with self._emission_lock:
            with self._lock:
                if name in self._research_sets_by_name:
                    raise ValueError(
                        f"MutationResearch already owns a research set "
                        f"'{name}'."
                    )
                research_set = ResearchSet(
                    name,
                    on_mutation=self._emit_research_composition,
                )
                self._research_sets_by_name[name] = research_set
            # New sets inherit the configured join-policy posture
            # immediately.
            self._propagate_lane_type_enforcement()
            self._emit_research_composition()
        return research_set

    def list_research_set_names(self) -> List[str]:
        """
        Return every owned research-set name, sorted.

        Contract:
            - SORTED, so iteration order is deterministic across calls and processes.
            - Snapshot taken under the lock; it goes stale as sets are registered or
              removed.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            List[str]: Sorted set names.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._research_sets_by_name.keys())

    def describe_research_composition(self) -> Dict[str, object]:
        """
        Return the detached composition payload across every owned set.

        Contract:
            - FANS OUT across EVERY registered research set, so cost scales with the
              number of sets - this is a whole-world description, not a targeted
              query.
            - Keys are set names; each value is that set's own composition
              description.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

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

        Contract:
            - Expects a DICT OF SET PAYLOADS keyed by set name; any other shape raises
              `ValueError` before anything is loaded.
            - Restores recorded composition rather than recomputing it, so it reflects
              what was captured, not current truth.

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
        # Emission lock first: rebuilt-set constructors fire on_mutation
        # while the root lock is held, and the one-way order is
        # emission -> root.
        with self._emission_lock:
            with self._lock:
                rebuilt: Dict[str, ResearchSet] = {}
                for name, set_payload in composition_payload.items():
                    rebuilt[str(name)] = ResearchSet.from_payload(
                        set_payload,
                        on_mutation=self._emit_research_composition,
                    )
                if (
                        MutationResearch.DEFAULT_RESEARCH_SET_NAME
                        not in rebuilt
                ):
                    rebuilt[
                        MutationResearch.DEFAULT_RESEARCH_SET_NAME
                    ] = ResearchSet(
                        MutationResearch.DEFAULT_RESEARCH_SET_NAME,
                        on_mutation=self._emit_research_composition,
                    )
                for _, research_set in list(
                        self._research_sets_by_name.items()
                ):
                    try:
                        research_set.cleanup()
                    except Exception:
                        pass
                self._research_sets_by_name = rebuilt
            # Rebuilt sets inherit the configured join-policy posture.
            self._propagate_lane_type_enforcement()
            self._emit_research_composition()

    # ------------------------------------------------------------------
    # Campaign context
    # ------------------------------------------------------------------

    @property
    def active_campaign(self) -> Optional[str]:
        """
        Return the ambient campaign stamp, when one is set.

        Contract:
            - AMBIENT DEFAULT. Group operations that take a `campaign=None` fall back
              to this value, so setting it changes the attribution of later calls
              that did not name a campaign explicitly.
            - None means no ambient campaign, and calls without an explicit campaign
              are then unattributed rather than failing.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            Optional[str]:
                Active campaign name or None.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_campaign

    def set_active_campaign(self, campaign: str) -> None:
        """
        Set the ambient research-campaign stamp.

        Purpose:
            Multi-agent campaigns stamp work ACROSS lanes; once set, every
            runtime auto-record routed through the root facades
            (`record_world_entry` / `record_promotion` - i.e. every dynamic
            bind, staged bind, and notch) carries this stamp until cleared,
            so campaign membership never depends on remembering to pass it.

        Contract:
            - Sets the AMBIENT DEFAULT that later group operations inherit when they pass
              `campaign=None`. It does not retroactively attribute earlier operations.
            - Rejects a non-string or empty campaign.

        Args:
            campaign:
                Non-empty campaign name.

        Returns:
            None.

        Raises:
            ValueError:
                If campaign is empty.
        """
        self.check_cleaned()
        if not isinstance(campaign, str) or not campaign:
            raise ValueError("campaign must be a non-empty string.")
        with self._lock:
            self._active_campaign = campaign

    def clear_active_campaign(self) -> None:
        """
        Clear the ambient research-campaign stamp.

        Contract:
            - Removes the ambient default so later group operations are unattributed
              unless they name a campaign explicitly. It does NOT rewrite attribution
              already recorded on earlier operations.
            - Idempotent: clearing when nothing is set is a no-op.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._active_campaign = None

    # ------------------------------------------------------------------
    # Staged ancestry (the synthesis mint seam)
    # ------------------------------------------------------------------

    @property
    def staged_ancestry(self) -> Optional[List[str]]:
        """
        Return the staged parent identities, when any.

        Contract:
            - Returns a COPY of the staged ancestry list, so mutating the result does
              NOT change staged state.
            - None and empty list mean different things: None is "nothing staged",
              an empty list is "staged, with no ancestors".

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            Optional[List[str]]:
                Detached parent list or None.
        """
        self.check_cleaned()
        with self._lock:
            return (
                list(self._staged_ancestry)
                if self._staged_ancestry is not None
                else None
            )

    def stage_ancestry(self, parent_spell_ids: List[str]) -> None:
        """
        Stage parent ancestry for the NEXT world entry (one-shot).

        Purpose:
            The mint half of surgical synthesis: composition happens in the
            codegen workshop, but the composed candidate's binding-signature
            SHA does not exist until it binds - and the bind auto-record
            fires before the agent ever sees that SHA. Staging bridges the
            gap exactly like the ambient campaign stamp: stage the parents,
            execute the candidate, and the next fresh world entry mints the
            multi-parent node. Consumed ONE-SHOT by the first NEW
            declaration (rediscoveries do not consume it); restage for
            another synthesis.

        Contract:
            - Requires a NON-EMPTY LIST of parent identities; an empty list raises rather
              than being treated as "no ancestry".
            - Staging is ambient state consumed by a later operation; clearing it is a
              separate explicit step.

        Args:
            parent_spell_ids:
                Non-empty list of parent identities; each must be formally
                declared by the time the world entry lands (the set
                validates residence at mint time).

        Returns:
            None.

        Raises:
            ValueError:
                If the list is empty or carries non-string entries.
        """
        self.check_cleaned()
        if not isinstance(parent_spell_ids, list) or not parent_spell_ids:
            raise ValueError(
                "parent_spell_ids must be a non-empty list of identities."
            )
        for parent in parent_spell_ids:
            if not isinstance(parent, str) or not parent:
                raise ValueError(
                    "parent_spell_ids entries must be non-empty strings."
                )
        with self._lock:
            self._staged_ancestry = list(parent_spell_ids)

    def clear_staged_ancestry(self) -> None:
        """
        Clear the staged parent ancestry without consuming it.

        Contract:
            - Resets staged ancestry to None - the "nothing staged" state, not an
              empty list.
            - Idempotent: clearing when nothing is staged is a no-op.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._staged_ancestry = None

    # ------------------------------------------------------------------
    # Runtime world-entry seams
    # ------------------------------------------------------------------

    def record_world_entry(
            self,
            spell_id: str,
            *,
            staged: bool = False,
            author: Optional[str] = None,
            reason: Optional[str] = None,
            campaign: Optional[str] = None,
    ) -> bool:
        """
        Idempotently declare one world-entry into the default set.

        Purpose:
            The runtime-seam facade: the spellbook's bind and bind_inactive
            confirmation points call this on every dynamic-lane world entry
            once the root is active. Rediscovery (identical content, same
            SHA) is a quiet no-op - the runtime never fails on research
            bookkeeping.

        Contract:
            - CAMPAIGN DEFAULTS TO THE AMBIENT ONE: `campaign=None` inherits
              `active_campaign` rather than meaning "no campaign".
            - Records against the DEFAULT research set, not a named one.

        Args:
            spell_id:
                Binding-signature SHA256 entering the world.
            staged:
                True for parked (`bind_inactive`) entries.
            author:
                Optional acting agent name.
            reason:
                Optional reason line.

        Returns:
            bool:
                True when a new declaration was recorded; False when the
                identity was already declared.
        """
        self.check_cleaned()
        research_set = self.research_set()
        effective_campaign = (
            campaign if campaign is not None else self.active_campaign
        )
        # One-shot ancestry consumption (the synthesis mint): staged parents
        # ride the FIRST fresh declaration only. A rediscovery (quiet None
        # below) re-stages them untouched, because identical content
        # re-entering the world is not the synthesized candidate arriving.
        with self._lock:
            staged_parents = self._staged_ancestry
            self._staged_ancestry = None
        try:
            node = research_set.record_world_entry(
                spell_id,
                staged=staged,
                parent_spell_ids=staged_parents,
                author=author,
                reason=reason,
                campaign=effective_campaign,
            )
        except Exception:
            # One-shot means consumed by the first SUCCESSFUL declaration
            # (BUG-151): a pre-commit refusal (for example an unresident
            # parent) re-arms the stamp for the corrected retry, then the
            # refusal re-raises untouched.
            if staged_parents is not None:
                with self._lock:
                    if self._staged_ancestry is None:
                        self._staged_ancestry = staged_parents
            raise
        if node is None and staged_parents is not None:
            with self._lock:
                if self._staged_ancestry is None:
                    self._staged_ancestry = staged_parents
        return node is not None

    def record_promotion(
            self,
            from_spell_id: Optional[str],
            to_spell_id: str,
            *,
            actor: Optional[str] = None,
            reason: Optional[str] = None,
            campaign: Optional[str] = None,
    ) -> None:
        """
        Record one runtime selection change (notch) into the default set.

        Contract:
            - CAMPAIGN DEFAULTS TO THE AMBIENT ONE, exactly as in `record_world_entry`.
            - Records against the DEFAULT research set.
            - An undeclared `to_spell_id` is declared first (world-entry
              catch-up: a promotion proves the version exists) THROUGH the
              root world-entry verb, so staged ancestry is consumed by the
              candidate it was staged for; then the `promoted` event
              records with the supplied endpoints.

        Args:
            from_spell_id:
                Previously selected identity, when known.
            to_spell_id:
                Newly selected identity.
            actor:
                Optional acting agent name.
            reason:
                Optional reason line.

        Returns:
            None.
        """
        self.check_cleaned()
        research_set = self.research_set()
        effective_campaign = (
            campaign if campaign is not None else self.active_campaign
        )
        if research_set.residence_of(to_spell_id) is None:
            # Catch-up rides the ROOT world-entry verb (BUG-049): the
            # promoted candidate IS the arrival any staged ancestry was
            # staged to describe, so the one-shot consumption must fire
            # here - a direct set-level declaration would leave the stamp
            # armed to leak onto the next unrelated entry.
            self.record_world_entry(
                to_spell_id,
                staged=True,
                author=actor,
                reason="world-entry catch-up at promotion",
                campaign=effective_campaign,
            )
        research_set.record_promotion(
            from_spell_id,
            to_spell_id,
            actor=actor,
            reason=reason,
            campaign=effective_campaign,
        )

    # ------------------------------------------------------------------
    # Residency reads
    # ------------------------------------------------------------------

    def residency_view(
            self,
            spell_id: str,
            *,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return the query-time residency join for one identity.

        Purpose:
            The record stores NO active flags by design; where a version
            currently lives (active / parked / stored) is a runtime +
            custody JOIN performed at read time. This verb performs it:
            declared truth from the research set, runtime truth from the
            frames (SpellIndex membership + selection), custody truth from
            the crystallizer.

        Contract:
            - Total read: never raises for unknown identities (empty sha is
              the only refusal); every uncertainty reports honestly.
            - `runtime` verdicts: `active` (some index's selected member),
              `parked` (a live index member, not selected), `stored`
              (custody only), `declared_only` (record only), `unknown`
              (nowhere, incl. custody unavailable).
            - `in_custody` is None when the crystallizer is not recording
              (inactive) - a read never fabricates or raises there.

        Args:
            spell_id:
                Binding-signature SHA256 to locate.
            set_name:
                Research set to read declared truth from.

        Returns:
            Dict[str, object]:
                `spell_id`, `declared`, `lane_id`/`lane_name`/`lane_state`
                (None when undeclared), `runtime`, `frame_name`/`index_id`
                (None when not live), and `in_custody`.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        research_set = self.research_set(set_name)
        lane_id = research_set.residence_of(spell_id)
        lane_name: Optional[str] = None
        lane_state: Optional[str] = None
        lane_type: Optional[str] = None
        node_type: Optional[str] = None
        if lane_id is not None:
            lane = research_set.get_lane(lane_id)
            lane_name = lane.name
            lane_state = lane.state.value
            lane_type = lane.lane_type.value
            if lane.has_node(spell_id):
                node_type = (
                    "group"
                    if isinstance(
                        lane.get_node(spell_id), GroupedResearchNode,
                    )
                    else "spell"
                )
        if node_type == "group":
            # Composition identities are PURELY INFORMATIONAL: no custody
            # crystal exists or is expected, and frame membership is a
            # spell-grain question - probing either would report a
            # misleading miss.
            return {
                "spell_id": spell_id,
                "declared": True,
                "lane_id": lane_id,
                "lane_name": lane_name,
                "lane_state": lane_state,
                "lane_type": lane_type,
                "node_type": node_type,
                "runtime": "informational",
                "frame_name": None,
                "index_id": None,
                "in_custody": None,
            }
        frame_name, index_id, selected = self._locate_live_membership(
            spell_id,
        )
        in_custody = self._probe_custody(spell_id)
        if selected:
            runtime = "active"
        elif index_id is not None:
            runtime = "parked"
        elif in_custody:
            runtime = "stored"
        elif lane_id is not None:
            runtime = "declared_only"
        else:
            runtime = "unknown"
        return {
            "spell_id": spell_id,
            "declared": lane_id is not None,
            "lane_id": lane_id,
            "lane_name": lane_name,
            "lane_state": lane_state,
            "lane_type": lane_type,
            "node_type": node_type,
            "runtime": runtime,
            "frame_name": frame_name,
            "index_id": index_id,
            "in_custody": in_custody,
            # Reverse lift: which CURRENT compositions pin this spell.
            "pinned_by_compositions": self.compositions_of(
                spell_id, set_name=set_name,
            ),
        }

    def _locate_live_membership(
            self,
            spell_id: str,
    ) -> Tuple[Optional[str], Optional[str], bool]:
        """
        Scan live frames for one identity's index membership.

        Args:
            spell_id:
                Identity to locate.

        Contract:
            - Scans EVERY live frame: a selected (active) membership
              anywhere wins over any unselected membership, honoring the
              residency contract's active-if-any verdict rule.
            - When no frame selects the identity, the first live unselected
              membership (frame iteration order) is reported as parked.

        Returns:
            Tuple[Optional[str], Optional[str], bool]:
                `(frame_name, index_id, selected)` - Nones/False when the
                identity is not a live index member anywhere.
        """
        aether = self._aether
        parked_frame: Optional[str] = None
        parked_index: Optional[str] = None
        for frame_name, frame in list(aether._aetheric_frames.items()):
            try:
                if frame.cleaned:
                    continue
                index = frame.find_index_for_spell(spell_id)
            except Exception:
                continue
            if index is None or index.cleaned:
                continue
            if index.selected_spell_id == spell_id:
                return frame_name, index.id, True
            if parked_frame is None:
                parked_frame = frame_name
                parked_index = index.id
        return parked_frame, parked_index, False

    def _probe_custody(self, spell_id: str) -> Optional[bool]:
        """
        Probe crystallizer custody for one identity, without raising.

        Args:
            spell_id:
                Identity to probe.

        Returns:
            Optional[bool]:
                True/False for custody presence; None when the crystallizer
                is not recording (inactive).
        """
        crystallizer = self._crystallizer
        if not crystallizer.activated:
            return None
        try:
            crystallizer.get_spell_crystal(spell_id)
        except KeyError:
            return False
        return True

    # ------------------------------------------------------------------
    # Derived diff reads
    # ------------------------------------------------------------------

    def is_composition(self, identity: str) -> bool:
        """
        Return whether one identity resolves to a recorded composition.

        Purpose:
            Public kind probe for mediating seams (the codegen room's
            polymorphic verbs pick kind-aware strategy defaults with it)
            without exposing node internals.

        Contract:
            - Tests whether an identity names a GROUP NODE (a composition) rather than a
              single spell - the discriminator the diff verbs dispatch on.
            - False for an unknown identity as well as for a plain spell, so it is not an
              existence check.

        Args:
            identity:
                Spell or composition identity to classify.

        Returns:
            bool:
                True when the identity is a recorded GroupedResearchNode
                in any owned set; False otherwise (including unknown).
        """
        self.check_cleaned()
        return self._as_group_node(identity) is not None

    def diff_research(
            self,
            left_spell_id: str,
            right_spell_id: str,
            *,
            strategy: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two version identities.

        Purpose:
            The read verb behind "commits are full objects, diffs are
            derived": material resolves through crystallizer custody (the
            SHA is the SpellCrystal id) and the comparison runs in the
            registered strategy - nothing is stored.

        Contract:
            - KIND DISPATCH (parity law): two COMPOSITIONS diff through the grouped engine,
              two SPELLS through the spell engine.
            - A MIXED PAIR REFUSES, teach-grade, because a spell and a subsystem share no
              common grain to diff at. That refusal is deliberate, not a gap.

        Args:
            left_spell_id:
                Left version identity (binding-signature SHA256).
            right_spell_id:
                Right version identity.
            strategy:
                Registered strategy name; "source" by default.

        Returns:
            Dict[str, object]:
                Detached verdict payload from the owned `DiffEngine`.

        Raises:
            RuntimeError:
                If the crystallizer is not live (custody unavailable).
            KeyError:
                If either identity has no custody crystal, or the strategy
                name is unknown.
        """
        self.check_cleaned()
        # Kind dispatch (parity law - same verb, both node families):
        # two compositions diff through the grouped engine; a mixed pair
        # refuses teach-grade (a spell and a subsystem share no grain).
        left_group = self._as_group_node(left_spell_id)
        right_group = self._as_group_node(right_spell_id)
        if left_group is not None and right_group is not None:
            # The caller's strategy rides the dispatch (BUG-044): an unknown
            # name must surface the documented KeyError, never silently
            # reroute to the grouped default.
            if strategy is None:
                return self.group_diff_research(
                    left_group.group_id, right_group.group_id,
                )
            return self.group_diff_research(
                left_group.group_id,
                right_group.group_id,
                strategy=strategy,
            )
        if (left_group is None) != (right_group is None):
            raise ValueError(
                "diff_research cannot compare a spell version with a "
                "COMPOSITION - diff two spells, diff two compositions, "
                "or descend the composition to a member spell_id."
            )
        with self._lock:
            if self._diff_engine is None:
                self._diff_engine = DiffEngine(self._resolve_diff_material)
            engine = self._diff_engine
        return engine.diff(
            left_spell_id,
            right_spell_id,
            strategy=strategy if strategy is not None else "source",
        )

    def create_diff_engine(self) -> DiffEngine:
        """
        Create one standalone diff engine over crystallizer custody.

        Contract:
            - FACTORY: returns a FRESH engine on every call, bound to this singleton's
              material resolver. It is not cached and not owned by the singleton.
            - The engine resolves material LAZILY through that callback, so it
              reflects state at diff time rather than at construction time.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            DiffEngine:
                Caller-owned engine (the caller cleans it up); the root's
                own engine stays private to `diff_research`.
        """
        self.check_cleaned()
        return DiffEngine(self._resolve_diff_material)

    def _resolve_diff_material(
            self,
            spell_id: str,
    ) -> Dict[str, object]:
        """
        Resolve one version's diff material from crystallizer custody.

        Contract:
            - The custody crystal shares the spell's binding-signature
              SHA256 as its id; its describe() payload supplies synthetic
              module SOURCE TEXT and physical module FINGERPRINTS.
            - Loud by design: a dead/inactive crystallizer raises rather
              than fabricating empty material.

        Args:
            spell_id:
                Version identity to resolve.

        Returns:
            Dict[str, object]:
                `{"spell_id", "sources", "fingerprints"}` material payload.

        Raises:
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If no custody crystal exists for the identity.
        """
        self.check_cleaned()
        crystallizer = self._crystallizer
        if not crystallizer.activated:
            raise RuntimeError(
                "Crystallizer custody is unavailable (not recording); "
                "diff material cannot be resolved."
            )
        payload = self._get_spell_crystal_for_read(spell_id).describe()
        sources: Dict[str, object] = {}
        # BOTH recorded carriers feed comparison material (owner ruling
        # 2026-07-11: diffs speak the FULL module, physical or synthetic):
        # synthetic text first, user-retained text fills the gaps. The
        # live disk NEVER feeds a diff - both sides of a version
        # comparison would read the same present-day file and lie about
        # both versions; absent text stays honest fingerprint-only rows.
        for carrier_key in ("synthetic_module_sources", "user_module_sources"):
            carrier = payload.get(carrier_key)
            if isinstance(carrier, dict):
                for module_name, custody_payload in carrier.items():
                    if str(module_name) in sources:
                        continue
                    if isinstance(custody_payload, dict):
                        text = custody_payload.get("source_text")
                        # Empty string is VALID recorded Python (BUG-152):
                        # presence is the str type, never truthiness.
                        if isinstance(text, str):
                            sources[str(module_name)] = text
        fingerprints = payload.get("physical_module_fingerprints")
        return {
            "spell_id": spell_id,
            "sources": sources,
            "fingerprints": (
                dict(fingerprints) if isinstance(fingerprints, dict) else {}
            ),
        }

    # ------------------------------------------------------------------
    # Foresight reads (source / impact / module graph / candidate preview)
    # ------------------------------------------------------------------

    def _as_group_node(
            self,
            identity: str,
            set_name: str = "default",
    ) -> Optional["GroupedResearchNode"]:
        """
        Return the resident composition for one identity, or None.

        Purpose:
            The kind-dispatch point (owner ruling: the SAME verbs serve
            both node families): spell-grain reads call this first and
            fan out per member when the identity is a composition.

        Args:
            identity:
                Identity to classify.
            set_name:
                Research set to resolve within.

        Returns:
            Optional[GroupedResearchNode]:
                The composition node, or None for spells/unknowns.
        """
        try:
            research_set = self.research_set(set_name)
            lane_id = research_set.residence_of(identity)
            if lane_id is None:
                return None
            node = research_set.get_lane(lane_id).get_node(identity)
            return node if isinstance(node, GroupedResearchNode) else None
        except Exception:
            return None

    def _fan_out_members(
            self,
            node: "GroupedResearchNode",
            read: "Callable[[str], Dict[str, object]]",
    ) -> Dict[str, object]:
        """
        Apply one spell-grain read to every member of a composition.

        Args:
            node:
                The composition being read.
            read:
                The per-member read (bound verb accepting one member
                identity).

        Returns:
            Dict[str, object]:
                `{"node_type": "group", "group_id", "member_count",
                "members": {member: payload | {"unknown_custody": True}}}`
                - custody-less members answer honestly instead of killing
                the fan-out.
        """
        members: Dict[str, object] = {}
        for member in node.member_spell_ids:
            try:
                members[member] = read(member)
            except KeyError:
                members[member] = {"unknown_custody": True}
        return {
            "node_type": "group",
            "group_id": node.group_id,
            "member_count": node.member_count,
            "members": members,
        }

    def _get_spell_crystal_for_read(self, spell_id: str) -> object:
        """
        Fetch one custody crystal for a spell-grain read, teach-grade.

        Contract:
            - Parity law: pointing a spell-grain read at a COMPOSITION
              identity must teach, not confuse - a raw custody KeyError
              says "no crystal" when the truth is "wrong grain". When the
              custody miss turns out to be a resident GroupedResearchNode,
              the refusal names the grain and the right verbs.

        Args:
            spell_id:
                Identity the read was pointed at.

        Returns:
            object:
                The custody crystal.

        Raises:
            RuntimeError:
                If the crystallizer is cleaned/inactive, or the identity
                is a composition (teach-grade redirect).
            KeyError:
                If no custody crystal exists and the identity is not a
                composition (the honest original).
        """
        crystallizer = self._require_live_custody()
        try:
            return crystallizer.get_spell_crystal(spell_id)
        except KeyError:
            try:
                research_set = self.research_set()
                lane_id = research_set.residence_of(spell_id)
                if lane_id is not None and isinstance(
                        research_set.get_lane(lane_id).get_node(spell_id),
                        GroupedResearchNode,
                ):
                    raise RuntimeError(
                        f"Identity '{spell_id[:12]}...' is a COMPOSITION "
                        f"(GroupedResearchNode) - it has no custody "
                        f"crystal of its own. Use the composition reads "
                        f"(group_view / group_footprint_view / "
                        f"group_impact_view / group_drift_view / "
                        f"group_history_view) or descend to a member "
                        f"spell_id for spell-grain reads."
                    ) from None
            except RuntimeError:
                raise
            except Exception:
                pass
            raise

    def _require_live_custody(self) -> "Crystallizer":
        """
        Return the live crystallizer or refuse teach-grade.

        Contract:
            - Foresight reads ask for RECORDED truth explicitly, so a dead
              or inactive record refuses loudly (diff precedent) instead of
              fabricating empty answers.

        Returns:
            Crystallizer:
                The live, activated crystallizer.

        Raises:
            RuntimeError:
                If the crystallizer is not recording (inactive).
        """
        crystallizer = self._crystallizer
        if not crystallizer.activated:
            raise RuntimeError(
                "Crystallizer custody is unavailable (not recording); "
                "foresight reads need the record - activate the "
                "crystallizer before asking for source, impact, or module "
                "graphs."
            )
        return crystallizer

    def source_view(
            self,
            spell_id: str,
            *,
            module_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the code of one spell's module world (or one module of it).

        Purpose:
            The agent QoL bedrock: "show me the code of this object". Text
            resolves recorded-first (synthetic module sources are always
            harvested; user module text rides the opt-in retention lane),
            then falls back to a live disk read through the recorded module
            path, and reports honestly when neither side has text.

        Contract:
            - Per-module rows carry `source`, `origin`
              ("recorded" | "live_disk" | None), `drifted` (live text vs the
              sealed fingerprint; None when unknowable), and
              `text_unavailable`.
            - `module_name` narrows the answer to one module; a module the
              spell's world does not carry answers `unknown_module: True`
              (a read never raises on an honest miss).

        Args:
            spell_id:
                Binding-signature SHA256 whose world to read.
            module_name:
                Optional single module to return.

        Returns:
            Dict[str, object]:
                `{"spell_id", "root_module", "modules": {name: row},
                "unknown_module"?}`. A COMPOSITION identity fans out per
                member (same verb, both node families - parity law):
                `{"node_type": "group", "group_id", "member_count",
                "members": {member: <this payload>}}`.

        Raises:
            ValueError:
                If spell_id is empty.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If no custody crystal exists for the identity.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        group = self._as_group_node(spell_id)
        if group is not None:
            return self._fan_out_members(
                group,
                lambda member: self.source_view(
                    member, module_name=module_name,
                ),
            )
        payload = self._get_spell_crystal_for_read(spell_id).describe()
        targets = [str(name) for name in list(payload.get("module_targets", []))]
        if module_name is not None:
            if str(module_name) not in targets:
                return {
                    "spell_id": spell_id,
                    "root_module": str(payload.get("root_module_name")),
                    "unknown_module": True,
                    "modules": {},
                }
            targets = [str(module_name)]
        modules: Dict[str, Dict[str, object]] = {}
        for name in targets:
            modules[name] = self._resolve_module_source(payload, name)
        return {
            "spell_id": spell_id,
            "root_module": str(payload.get("root_module_name")),
            "modules": modules,
        }

    def _resolve_module_source(
            self,
            payload: Dict[str, object],
            module_name: str,
    ) -> Dict[str, object]:
        """
        Resolve one module's source row from a custody payload.

        Args:
            payload:
                One crystal describe() payload.
            module_name:
                Module to resolve within that payload.

        Returns:
            Dict[str, object]:
                `{"source", "origin", "drifted", "text_unavailable"}` row.
        """
        for carrier_key, carrier_kind in (
                ("synthetic_module_sources", "synthetic"),
                ("user_module_sources", "user"),
        ):
            carrier = payload.get(carrier_key)
            if isinstance(carrier, dict):
                entry = carrier.get(module_name)
                if isinstance(entry, dict):
                    text = entry.get("source_text")
                    # Empty string is VALID recorded Python (BUG-152).
                    if isinstance(text, str):
                        return {
                            "source": text,
                            "origin": "recorded",
                            "kind": carrier_kind,
                            "drifted": None,
                            "text_unavailable": False,
                        }
        paths = payload.get("module_to_path")
        recorded_path = (
            paths.get(module_name) if isinstance(paths, dict) else None
        )
        if recorded_path:
            live_path = Path(str(recorded_path))
            if live_path.exists():
                try:
                    text = live_path.read_text(encoding="utf-8")
                except Exception:
                    text = None
                if text is not None:
                    drifted: Optional[bool] = None
                    fingerprints = payload.get(
                        "physical_module_fingerprints"
                    )
                    if isinstance(fingerprints, dict):
                        sealed = fingerprints.get(module_name)
                        if sealed is not None:
                            live_sha = hashlib.sha256(
                                text.encode("utf-8")
                            ).hexdigest()
                            drifted = live_sha != str(sealed)
                    return {
                        "source": text,
                        "origin": "live_disk",
                        "kind": "live_disk",
                        "drifted": drifted,
                        "text_unavailable": False,
                    }
        return {
            "source": None,
            "origin": None,
            "kind": None,
            "drifted": None,
            "text_unavailable": True,
        }

    def impact_view(
            self,
            *,
            spell_id: Optional[str] = None,
            module_name: Optional[str] = None,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return one blast radius joined with research residency.

        Purpose:
            The agent-meaningful impact answer: not just "these modules and
            spells sit in the radius" (the crystallizer's raw view) but
            "these spells, in these lanes, under these campaigns" - the
            join between recorded custody impact and the research record.

        Contract:
            - Exactly one question per call (spell_id OR module_name).
            - The raw radius payload is preserved verbatim; the join adds
              one `research` map (affected spell_id -> declared/lane_id/
              lane_name/lane_state/campaign row; undeclared spells report
              `declared: False` honestly).

        Args:
            spell_id:
                Optional spell SHA256 at the blast center.
            module_name:
                Optional canonical module name at the blast center.
            set_name:
                Research set supplying declared truth for the join.

        Returns:
            Dict[str, object]:
                The `analyze_impact` payload plus `research`.

        Raises:
            ValueError:
                If neither or both center arguments are supplied.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If `set_name` names no research set.
        """
        self.check_cleaned()
        if (spell_id is None) == (module_name is None):
            raise ValueError(
                "impact_view answers one question per call: supply "
                "spell_id OR module_name."
            )
        if spell_id is not None:
            group = self._as_group_node(spell_id, set_name)
            if group is not None:
                # Same verb, both node families: a composition's impact
                # IS its group radius (union + direction split + closure).
                return self.group_impact_view(
                    group.group_id, set_name=set_name,
                )
        crystallizer = self._require_live_custody()
        radius = crystallizer.analyze_impact(
            module_name=module_name,
            spell_id=spell_id,
        )
        affected = [
            str(sha) for sha in list(radius.get("affected_spells", []))
        ]
        radius["research"] = self._residency_join(affected, set_name)
        # Composition lift (units-and-scales law: the crossing move rises
        # to the highest rung): which CURRENT subsystems this radius
        # touches.
        affected_set = set(affected)
        research_set = self.research_set(set_name)
        affected_compositions: List[Dict[str, object]] = []
        for tip_node in self._current_compositions(set_name):
            shared = sorted(
                set(tip_node.member_spell_ids) & affected_set
            )
            if shared:
                tip_lane_id = research_set.residence_of(tip_node.group_id)
                affected_compositions.append({
                    "group_id": tip_node.group_id,
                    "lane_name": research_set.get_lane(tip_lane_id).name,
                    "shared_members": shared,
                })
        radius["affected_compositions"] = affected_compositions
        return radius

    def _residency_join(
            self,
            spell_ids: List[str],
            set_name: str,
    ) -> Dict[str, Dict[str, object]]:
        """
        Join affected identities with declared research truth.

        Args:
            spell_ids:
                Identities to join.
            set_name:
                Research set supplying declared truth.

        Returns:
            Dict[str, Dict[str, object]]:
                spell_id -> `{"declared", "lane_id", "lane_name",
                "lane_state", "campaign"}` rows.

        Raises:
            KeyError:
                If `set_name` names no research set.
        """
        research_set = self.research_set(set_name)
        joined: Dict[str, Dict[str, object]] = {}
        for spell_id in spell_ids:
            lane_id = research_set.residence_of(spell_id)
            if lane_id is None:
                joined[spell_id] = {
                    "declared": False,
                    "lane_id": None,
                    "lane_name": None,
                    "lane_state": None,
                    "lane_type": None,
                    "campaign": None,
                }
                continue
            lane = research_set.get_lane(lane_id)
            campaign: Optional[str] = None
            if lane.has_node(spell_id):
                campaign = lane.get_node(spell_id).campaign
            joined[spell_id] = {
                "declared": True,
                "lane_id": lane_id,
                "lane_name": lane.name,
                "lane_state": lane.state.value,
                "lane_type": lane.lane_type.value,
                "campaign": campaign,
            }
        return joined

    def module_graph_view(self, spell_id: str) -> Dict[str, object]:
        """
        Return one spell's module world as a walkable graph payload.

        Purpose:
            The "walk the graph and understand the underlying module
            impacts" read: every module the spell's recorded world carries,
            the direct dependency edges between them, the LOCAL reverse
            edges (who inside this world imports whom), export surfaces,
            sealed fingerprints, recorded paths, and the topological load
            order. Cross-record radius stays `impact_view`'s job.

        Contract:
            - Dispatches on kind: a group identity is analyzed as a composition, a plain
              spell as a single unit.
            - Rejects a non-string or empty `spell_id` up front.

        Args:
            spell_id:
                Binding-signature SHA256 whose world to walk.

        Returns:
            Dict[str, object]:
                `{"spell_id", "root_module", "modules",
                "direct_dependencies", "local_importers",
                "export_surfaces", "fingerprints", "module_paths",
                "load_order"}`.

        Raises:
            ValueError:
                If spell_id is empty.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If no custody crystal exists for the identity.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        group = self._as_group_node(spell_id)
        if group is not None:
            return self._fan_out_members(
                group,
                lambda member: self.module_graph_view(member),
            )
        payload = self._get_spell_crystal_for_read(spell_id).describe()
        dependency_map = {
            str(importer): [str(name) for name in list(imported)]
            for importer, imported in dict(
                payload.get("module_to_direct_dependencies", {})
            ).items()
        }
        local_importers: Dict[str, List[str]] = {}
        for importer, imported_list in dependency_map.items():
            for imported in imported_list:
                local_importers.setdefault(imported, []).append(importer)
        for imported in local_importers:
            local_importers[imported].sort()
        exports = payload.get("export_surfaces")
        fingerprints = payload.get("physical_module_fingerprints")
        paths = payload.get("module_to_path")
        return {
            "spell_id": spell_id,
            "root_module": str(payload.get("root_module_name")),
            "modules": sorted(
                str(name) for name in list(payload.get("module_targets", []))
            ),
            "direct_dependencies": dependency_map,
            "local_importers": local_importers,
            "export_surfaces": (
                dict(exports) if isinstance(exports, dict) else {}
            ),
            "fingerprints": (
                dict(fingerprints) if isinstance(fingerprints, dict) else {}
            ),
            "module_paths": dict(paths) if isinstance(paths, dict) else {},
            "load_order": [
                str(name) for name in list(payload.get("module_load_order", []))
            ],
        }

    def source_drift_view(self) -> Dict[str, object]:
        """
        Return the full recorded-vs-disk drift report.

        Purpose:
            The "what will my uncommitted edits break" read: every sealed
            fingerprint re-hashed against the live disk, with a blast
            radius attached to every module that is not unchanged.

        Contract:
            - REQUIRES LIVE CUSTODY: it reaches through the crystallizer, so it raises when
              recording custody is unavailable rather than returning an empty report.
            - Reports drift between recorded sources and current ones; it changes nothing.

        Returns:
            Dict[str, object]:
                The crystallizer's full impact describe (custody counts +
                drift statuses + radii).

        Raises:
            RuntimeError:
                If the crystallizer is cleaned or inactive.
        """
        self.check_cleaned()
        return self._require_live_custody().analyze_impact()

    def module_view(
            self,
            spell_id: str,
            module_name: str,
    ) -> Dict[str, object]:
        """
        Return everything the crystal knows about one module in one call.

        Purpose:
            The crystal-well dossier (units-and-scales philosophy 4.1):
            full source text labeled by kind (synthetic / user /
            live_disk), sealed fingerprint, recorded path, local
            dependency edges both ways, export surface, and drift - the
            single call behind "give me the module data from synthetic or
            physical modules".

        Contract:
            - Rejects a non-string or empty `spell_id` AND `module_name` up front, so both
              arguments fail fast rather than producing an empty view.
            - Scoped to ONE module of one spell.

        Args:
            spell_id:
                Binding-signature SHA256 whose world carries the module.
            module_name:
                Module to gather.

        Returns:
            Dict[str, object]:
                Dossier payload; a module outside the world answers
                `unknown_module: True` honestly.

        Raises:
            ValueError:
                If either argument is empty.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If no custody crystal exists for the identity.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        if not isinstance(module_name, str) or not module_name:
            raise ValueError("module_name must be a non-empty string.")
        group = self._as_group_node(spell_id)
        if group is not None:
            return self._fan_out_members(
                group,
                lambda member: self.module_view(member, module_name),
            )
        payload = self._get_spell_crystal_for_read(spell_id).describe()
        targets = [str(name) for name in list(payload.get("module_targets", []))]
        if module_name not in targets:
            return {
                "spell_id": spell_id,
                "module_name": module_name,
                "unknown_module": True,
            }
        row = self._resolve_module_source(payload, module_name)
        dependency_map = dict(payload.get("module_to_direct_dependencies", {}))
        direct = [
            str(name) for name in list(dependency_map.get(module_name, []))
        ]
        importers = sorted(
            str(importer)
            for importer, imported in dependency_map.items()
            if module_name in [str(name) for name in list(imported)]
        )
        fingerprints = payload.get("physical_module_fingerprints")
        paths = payload.get("module_to_path")
        exports = payload.get("export_surfaces")
        return {
            "spell_id": spell_id,
            "module_name": module_name,
            "unknown_module": False,
            "source": row["source"],
            "source_kind": row["kind"],
            "drifted": row["drifted"],
            "text_unavailable": row["text_unavailable"],
            "fingerprint": (
                fingerprints.get(module_name)
                if isinstance(fingerprints, dict) else None
            ),
            "path": (
                paths.get(module_name) if isinstance(paths, dict) else None
            ),
            "direct_dependencies": direct,
            "local_importers": importers,
            "export_surface": (
                list(exports.get(module_name, []))
                if isinstance(exports, dict) else []
            ),
        }

    def part_view(
            self,
            spell_id: str,
            part_name: str,
            *,
            kind: Optional[str] = None,
            module_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one named top-level part's text from a version's world.

        Purpose:
            The part-grain read: locate a function or class by name across
            the version's resolvable module texts (recorded-first,
            live-disk fallback - present-tense rules, like source_view)
            and return its text, span, and carrying module.

        Contract:
            - Rejects a non-string or empty `spell_id` AND `part_name` up front.
            - Scoped to ONE part, the finest grain of the research views.

        Args:
            spell_id:
                Binding-signature SHA256 whose world to search.
            part_name:
                Top-level function/class name to locate.
            kind:
                Optional filter: "function" or "class".
            module_name:
                Optional single module to search.

        Returns:
            Dict[str, object]:
                Found: `{"found": True, "module_name", "source_kind",
                "drifted", "kind", "start_line", "end_line", "text"}`.
                Missed: `{"found": False, "searched_modules",
                "parse_errors"}` - honest, never raising on a miss.

        Raises:
            ValueError:
                If arguments are empty or kind is unknown.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If no custody crystal exists for the identity.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        if not isinstance(part_name, str) or not part_name:
            raise ValueError("part_name must be a non-empty string.")
        if kind is not None and kind not in ("function", "class"):
            raise ValueError(
                f"Unknown part kind '{kind}'. Known kinds: "
                f"['class', 'function']."
            )
        group = self._as_group_node(spell_id)
        if group is not None:
            # First hit across the roster (a subsystem's part is one of
            # its members' parts); the winning member is named.
            searched_members: List[str] = []
            for member in group.member_spell_ids:
                searched_members.append(member)
                try:
                    hit = self.part_view(
                        member,
                        part_name,
                        kind=kind,
                        module_name=module_name,
                    )
                except KeyError:
                    continue
                if hit.get("found"):
                    hit["member_spell_id"] = member
                    hit["group_id"] = group.group_id
                    return hit
            return {
                "found": False,
                "node_type": "group",
                "group_id": group.group_id,
                "part_name": part_name,
                "kind": kind,
                "searched_members": searched_members,
            }
        payload = self._get_spell_crystal_for_read(spell_id).describe()
        targets = [str(name) for name in list(payload.get("module_targets", []))]
        if module_name is not None:
            search_order = [module_name] if module_name in targets else []
        else:
            root_module = str(payload.get("root_module_name"))
            search_order = (
                [root_module] if root_module in targets else []
            ) + sorted(name for name in targets if name != root_module)
        synthesizer = self._get_synthesizer()
        searched: List[str] = []
        parse_errors: Dict[str, str] = {}
        for candidate in search_order:
            row = self._resolve_module_source(payload, candidate)
            text = row["source"]
            if not isinstance(text, str) or not text:
                continue
            searched.append(candidate)
            try:
                part = synthesizer.extract_part(
                    text, part_name, kind=kind,
                )
            except ValueError as error:
                parse_errors[candidate] = str(error)
                continue
            if part is not None:
                part["found"] = True
                part["spell_id"] = spell_id
                part["module_name"] = candidate
                part["source_kind"] = row["kind"]
                part["drifted"] = row["drifted"]
                return part
        return {
            "found": False,
            "spell_id": spell_id,
            "part_name": part_name,
            "kind": kind,
            "searched_modules": searched,
            "parse_errors": parse_errors,
        }

    def parts_view(
            self,
            spell_id: str,
            *,
            module_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return every top-level part of a version's world, with code.

        Purpose:
            The class-code inventory (owner ruling 2026-07-11: the agent
            chooses the grain - module text OR class code): all top-level
            functions/classes per module, each with its full text and
            span, without the agent knowing any names up front.

        Contract:
            - Dispatches on kind: a group identity enumerates parts across the composition,
              a plain spell across itself.
            - Rejects a non-string or empty `spell_id` up front.

        Args:
            spell_id:
                Binding-signature SHA256 whose world to inventory.
            module_name:
                Optional single module to inventory.

        Returns:
            Dict[str, object]:
                `{"spell_id", "root_module", "modules": {name:
                {"source_kind", "drifted", "parts": [rows] |
                "parse_error" | "text_unavailable"}}, "unknown_module"?}`
                - per-module honesty, never raising on misses.

        Raises:
            ValueError:
                If spell_id is empty.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If no custody crystal exists for the identity.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        group = self._as_group_node(spell_id)
        if group is not None:
            return self._fan_out_members(
                group,
                lambda member: self.parts_view(
                    member, module_name=module_name,
                ),
            )
        payload = self._get_spell_crystal_for_read(spell_id).describe()
        targets = [str(name) for name in list(payload.get("module_targets", []))]
        if module_name is not None:
            if str(module_name) not in targets:
                return {
                    "spell_id": spell_id,
                    "root_module": str(payload.get("root_module_name")),
                    "unknown_module": True,
                    "modules": {},
                }
            targets = [str(module_name)]
        synthesizer = self._get_synthesizer()
        modules: Dict[str, Dict[str, object]] = {}
        for name in targets:
            row = self._resolve_module_source(payload, name)
            module_entry: Dict[str, object] = {
                "source_kind": row["kind"],
                "drifted": row["drifted"],
            }
            text = row["source"]
            if not isinstance(text, str) or not text:
                module_entry["text_unavailable"] = True
                module_entry["parts"] = []
            else:
                try:
                    module_entry["parts"] = synthesizer.list_parts(text)
                except ValueError as error:
                    module_entry["parse_error"] = str(error)
                    module_entry["parts"] = []
            modules[name] = module_entry
        return {
            "spell_id": spell_id,
            "root_module": str(payload.get("root_module_name")),
            "modules": modules,
        }

    def part_diff(
            self,
            left_spell_id: str,
            right_spell_id: str,
            part_name: str,
            *,
            kind: Optional[str] = None,
            module_name: Optional[str] = None,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Unified text diff of one named part between two versions.

        Purpose:
            The class/function-grain comparison the owner asked for -
            WITH its blast radius. Part texts extract from RECORDED
            material only (comparison law: the live disk would compare a
            file with itself and lie about both versions); the radius
            section is the carrying module's current blast radius joined
            with research residency (impact stays module-grain per the
            grain laws - a part's honest radius IS its module's radius).

        Contract:
            - Rejects a non-string or empty id on BOTH sides before any work, so a
              half-specified diff fails immediately.
            - Compares one part across two identities and reports differences without
              reconciling them.

        Args:
            left_spell_id:
                Left version identity.
            right_spell_id:
                Right version identity.
            part_name:
                Top-level function/class name to compare.
            kind:
                Optional filter: "function" or "class".
            module_name:
                Optional single module to search on both sides.
            set_name:
                Research set for the impact residency join.

        Returns:
            Dict[str, object]:
                `{"left_spell_id", "right_spell_id", "part_name",
                "left_found", "right_found", "left_module",
                "right_module", "left_kind", "right_kind", "identical",
                "unified_diff", "impact"}` - absent sides answer honestly
                (found flags), never raising.

        Raises:
            ValueError:
                If identities/name are empty or kind is unknown.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If either identity has no custody crystal.
        """
        self.check_cleaned()
        if not isinstance(left_spell_id, str) or not left_spell_id:
            raise ValueError("left_spell_id must be a non-empty string.")
        if not isinstance(right_spell_id, str) or not right_spell_id:
            raise ValueError("right_spell_id must be a non-empty string.")
        if not isinstance(part_name, str) or not part_name:
            raise ValueError("part_name must be a non-empty string.")
        if kind is not None and kind not in ("function", "class"):
            raise ValueError(
                f"Unknown part kind '{kind}'. Known kinds: "
                f"['class', 'function']."
            )
        left_part = self._locate_recorded_part(
            left_spell_id, part_name, kind=kind, module_name=module_name,
        )
        right_part = self._locate_recorded_part(
            right_spell_id, part_name, kind=kind, module_name=module_name,
        )
        result: Dict[str, object] = {
            "left_spell_id": left_spell_id,
            "right_spell_id": right_spell_id,
            "part_name": part_name,
            "left_found": left_part is not None,
            "right_found": right_part is not None,
            "left_module": left_part["module_name"] if left_part else None,
            "right_module": right_part["module_name"] if right_part else None,
            "left_kind": left_part["kind"] if left_part else None,
            "right_kind": right_part["kind"] if right_part else None,
            "left_member": (
                left_part.get("member_spell_id") if left_part else None
            ),
            "right_member": (
                right_part.get("member_spell_id") if right_part else None
            ),
            "identical": None,
            "unified_diff": None,
            "impact": None,
        }
        if left_part is not None and right_part is not None:
            identical = left_part["text"] == right_part["text"]
            result["identical"] = identical
            if not identical:
                result["unified_diff"] = list(difflib.unified_diff(
                    str(left_part["text"]).splitlines(),
                    str(right_part["text"]).splitlines(),
                    fromfile=f"left/{part_name}",
                    tofile=f"right/{part_name}",
                    lineterm="",
                ))
        impact_module = (
            result["right_module"]
            if result["right_module"] is not None
            else result["left_module"]
        )
        if impact_module is not None:
            result["impact"] = self.impact_view(
                module_name=str(impact_module),
                set_name=set_name,
            )
        return result

    def _locate_recorded_part(
            self,
            spell_id: str,
            part_name: str,
            *,
            kind: Optional[str],
            module_name: Optional[str],
    ) -> Optional[Dict[str, object]]:
        """
        Locate one part in one version's RECORDED material only.

        Args:
            spell_id:
                Version identity to search.
            part_name:
                Part name to locate.
            kind:
                Optional kind filter.
            module_name:
                Optional single module to search.

        Returns:
            Optional[Dict[str, object]]:
                Part payload plus `module_name`, or None (misses and
                unparseable recorded modules skip quietly - the diff
                verdict reports found flags honestly).
        """
        group = self._as_group_node(spell_id)
        if group is not None:
            # A composition's recorded part lives in one of its members'
            # recorded material; the first roster hit wins and is named.
            for member in group.member_spell_ids:
                try:
                    located = self._locate_recorded_part(
                        member,
                        part_name,
                        kind=kind,
                        module_name=module_name,
                    )
                except KeyError:
                    continue
                if located is not None:
                    located["member_spell_id"] = member
                    return located
            return None
        material = self._resolve_diff_material(spell_id)
        sources = material["sources"]
        if module_name is not None:
            names = [module_name] if module_name in sources else []
        else:
            names = sorted(sources.keys())
        synthesizer = self._get_synthesizer()
        for candidate in names:
            text = sources[candidate]
            try:
                part = synthesizer.extract_part(
                    str(text), part_name, kind=kind,
                )
            except ValueError:
                continue
            if part is not None:
                part["module_name"] = candidate
                return part
        return None

    def _get_synthesizer(self) -> StructuralSynthesizer:
        """
        Return the lazily-owned synthesizer (DiffEngine precedent).

        Returns:
            StructuralSynthesizer:
                The root-owned instance.
        """
        with self._lock:
            if self._synthesizer is None:
                self._synthesizer = StructuralSynthesizer()
            return self._synthesizer

    def preview_candidate(
            self,
            code: str,
            *,
            against_spell_id: Optional[str] = None,
            module_name: Optional[str] = None,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Mock one candidate codegen and report what would happen next.

        Purpose:
            The foresight centerpiece: BEFORE anything executes, binds, or
            records, answer what the candidate code defines, what it
            imports, how it differs from the version it would replace, and
            what blast radius that replacement would have - so an agent can
            guess what happens next instead of finding out.

        Contract:
            - Read-only: nothing executes, binds, or records.
            - Unparseable code answers honestly (`parse_error` row; the
              analysis/diff/impact sections go None) - previewing broken
              code is a legitimate question.
            - With `against_spell_id`, the candidate text adopts that
              spell's root module name so the would-be diff compares module
              universes honestly; the impact section is that root module's
              current blast radius joined with research residency.
            - With only `module_name`, the impact section is that module's
              radius; with neither, impact is None (nothing to center on).

        Args:
            code:
                Candidate Python source text.
            against_spell_id:
                Optional current version the candidate would replace.
            module_name:
                Optional module identity for the candidate when no
                against-version exists.
            set_name:
                Research set for the impact residency join.

        Returns:
            Dict[str, object]:
                `{"candidate_sha256", "module_name", "parse_error",
                "defines", "import_roots", "diff", "impact",
                "against_spell_id"}`.

        Raises:
            ValueError:
                If code is empty.
            RuntimeError:
                If an against/impact read needs custody and the
                crystallizer is cleaned or inactive.
            KeyError:
                If `against_spell_id` has no custody crystal.
        """
        self.check_cleaned()
        if not isinstance(code, str) or not code:
            raise ValueError("code must be a non-empty string.")
        if against_spell_id is not None and (
                self._as_group_node(against_spell_id) is not None
        ):
            raise RuntimeError(
                f"'{against_spell_id[:12]}...' is a COMPOSITION - a "
                f"candidate previews against ONE version's module world; "
                f"preview against a member spell_id instead."
            )
        candidate_sha = hashlib.sha256(code.encode("utf-8")).hexdigest()
        analysis = self._analyze_candidate(code)
        result: Dict[str, object] = {
            "candidate_sha256": candidate_sha,
            "module_name": module_name,
            "against_spell_id": against_spell_id,
            "parse_error": analysis["parse_error"],
            "defines": analysis["defines"],
            "import_roots": analysis["import_roots"],
            "diff": None,
            "impact": None,
        }
        if analysis["parse_error"] is not None:
            return result
        target_module: Optional[str] = module_name
        if against_spell_id is not None:
            left_material = self._resolve_diff_material(against_spell_id)
            root_payload = self._get_spell_crystal_for_read(
                against_spell_id
            ).describe()
            target_module = str(root_payload.get("root_module_name"))
            result["module_name"] = target_module
            right_material = {
                "spell_id": f"candidate:{candidate_sha[:12]}",
                "sources": {target_module: code},
                "fingerprints": {target_module: candidate_sha},
            }
            with self._lock:
                if self._diff_engine is None:
                    self._diff_engine = DiffEngine(
                        self._resolve_diff_material
                    )
                engine = self._diff_engine
            result["diff"] = {
                "source": engine.diff_materials(
                    left_material, right_material, strategy="source",
                ),
                "structural": engine.diff_materials(
                    left_material, right_material, strategy="structural",
                ),
                "parts": engine.diff_materials(
                    left_material, right_material, strategy="parts",
                ),
            }
        if target_module is not None:
            result["impact"] = self.impact_view(
                module_name=target_module,
                set_name=set_name,
            )
        return result

    def _analyze_candidate(self, code: str) -> Dict[str, object]:
        """
        Statically analyze one candidate source text.

        Args:
            code:
                Candidate Python source text.

        Returns:
            Dict[str, object]:
                `{"parse_error": None | {"message", "line"},
                "defines": {"classes": [...], "functions": [...]},
                "import_roots": [...]}` - names sorted, roots deduped.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as error:
            return {
                "parse_error": {
                    "message": str(error.msg),
                    "line": error.lineno,
                },
                "defines": {"classes": [], "functions": []},
                "import_roots": [],
            }
        classes: List[str] = []
        functions: List[str] = []
        roots: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    roots.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    roots.append(node.module.split(".")[0])
        return {
            "parse_error": None,
            "defines": {
                "classes": sorted(classes),
                "functions": sorted(functions),
            },
            "import_roots": sorted(set(roots)),
        }

    def synthesize_candidate(
            self,
            base_spell_id: str,
            donor_spell_id: str,
            *,
            take_functions: Optional[List[str]] = None,
            take_classes: Optional[List[str]] = None,
            stage_ancestry: bool = False,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Surgically compose one candidate from two recorded versions.

        Purpose:
            The salvaged May "surgical mutation" verb: take named top-level
            parts (functions/classes) from the DONOR version's root module
            and splice them into the BASE version's root module, then run
            the composed candidate through the full foresight preview
            (against the base). With `stage_ancestry=True`, both parents
            stage for the next world entry, so executing the candidate
            mints the multi-parent node automatically - compose, preview,
            execute, and the record keeps the whole story.

        Contract:
            - Read-only (staging is ambient context, not a record write).
            - Source resolution rides `source_view` (recorded-first,
              live-disk fallback); a root module with no resolvable text on
              either side answers `text_unavailable` honestly.
            - Unknown selections refuse loudly (synthesizer law); parse
              errors on recorded text answer honestly inside the verdict.

        Args:
            base_spell_id:
                Version being upgraded (the candidate starts as its root
                module text; the preview diffs against it).
            donor_spell_id:
                Version parts are taken from.
            take_functions:
                Top-level function names to take.
            take_classes:
                Top-level class names to take.
            stage_ancestry:
                Stage [base, donor] as the next world entry's parents.
            set_name:
                Research set for the preview's residency join.

        Returns:
            Dict[str, object]:
                `{"base_spell_id", "donor_spell_id", "parents",
                "base_module", "donor_module", "selections",
                "composed_source", "parse_error", "text_unavailable",
                "ancestry_staged", "preview"}`.

        Raises:
            ValueError:
                If identities are empty, no selection is supplied, or a
                selection is unknown to the donor.
            RuntimeError:
                If the crystallizer is cleaned or inactive.
            KeyError:
                If either identity has no custody crystal.
        """
        self.check_cleaned()
        if not isinstance(base_spell_id, str) or not base_spell_id:
            raise ValueError("base_spell_id must be a non-empty string.")
        if not isinstance(donor_spell_id, str) or not donor_spell_id:
            raise ValueError("donor_spell_id must be a non-empty string.")
        for role, identity in (
                ("base", base_spell_id), ("donor", donor_spell_id),
        ):
            if self._as_group_node(identity) is not None:
                raise RuntimeError(
                    f"The {role} '{identity[:12]}...' is a COMPOSITION - "
                    f"synthesis splices ONE version's module world; use "
                    f"member spell_ids (part_view on the composition "
                    f"finds the carrying member)."
                )
        base_view = self.source_view(base_spell_id)
        donor_view = self.source_view(donor_spell_id)
        result: Dict[str, object] = {
            "base_spell_id": base_spell_id,
            "donor_spell_id": donor_spell_id,
            "parents": [base_spell_id, donor_spell_id],
            "base_module": base_view["root_module"],
            "donor_module": donor_view["root_module"],
            "selections": [],
            "composed_source": None,
            "parse_error": None,
            "text_unavailable": False,
            "ancestry_staged": False,
            "preview": None,
        }
        base_row = base_view["modules"].get(str(base_view["root_module"]))
        donor_row = donor_view["modules"].get(str(donor_view["root_module"]))
        base_text = base_row.get("source") if base_row else None
        donor_text = donor_row.get("source") if donor_row else None
        if not base_text or not donor_text:
            result["text_unavailable"] = True
            return result
        with self._lock:
            if self._synthesizer is None:
                self._synthesizer = StructuralSynthesizer()
            synthesizer = self._synthesizer
        verdict = synthesizer.synthesize(
            base_text,
            donor_text,
            take_functions=take_functions,
            take_classes=take_classes,
        )
        result["parse_error"] = verdict["parse_error"]
        result["selections"] = verdict["selections"]
        composed = verdict["composed_source"]
        result["composed_source"] = composed
        if composed is None:
            return result
        result["preview"] = self.preview_candidate(
            composed,
            against_spell_id=base_spell_id,
            set_name=set_name,
        )
        if stage_ancestry:
            self.stage_ancestry([base_spell_id, donor_spell_id])
            result["ancestry_staged"] = True
        return result

    # ------------------------------------------------------------------
    # Composition reads (GroupedResearchNode surface)
    # ------------------------------------------------------------------

    def _locate_group_node(
            self,
            group_id: str,
            set_name: str = "default",
    ) -> "GroupedResearchNode":
        """
        Resolve one resident composition node or refuse teach-grade.

        Args:
            group_id:
                Composition identity (content-addressed SHA256).
            set_name:
                Research set to resolve within.

        Returns:
            GroupedResearchNode:
                The resident composition record.

        Raises:
            ValueError:
                If group_id is empty.
            RuntimeError:
                If the identity is unknown, or resident but a spell
                version (the error says which).
            KeyError:
                If `set_name` names no research set.
        """
        if not isinstance(group_id, str) or not group_id:
            raise ValueError("group_id must be a non-empty string.")
        research_set = self.research_set(set_name)
        lane_id = research_set.residence_of(group_id)
        if lane_id is None:
            raise RuntimeError(
                f"Composition '{group_id}' is not resident in research "
                f"set '{set_name}'."
            )
        node = research_set.get_lane(lane_id).get_node(group_id)
        if not isinstance(node, GroupedResearchNode):
            raise RuntimeError(
                f"Identity '{group_id}' is a spell version, not a "
                f"composition; the grouped reads answer "
                f"GroupedResearchNodes only."
            )
        return node

    def _resolve_group_material(
            self,
            group_id: str,
    ) -> Dict[str, object]:
        """
        Resolve one composition's diff material from the default set.

        Contract:
            - The members join carries lane-evidenced residence truth
              (lane_id/name/state/type/tip) so the `members` strategy can
              pair version moves without guessing.

        Args:
            group_id:
                Composition identity to resolve.

        Returns:
            Dict[str, object]:
                `{"group_id", "member_spell_ids", "parent_group_ids",
                "ancestor_group_ids", "members"}` material payload (each
                member row carries its lane join plus transitive
                `ancestor_spell_ids`).
        """
        self.check_cleaned()
        node = self._locate_group_node(group_id)
        research_set = self.research_set()
        members: Dict[str, Dict[str, object]] = {}
        for member in node.member_spell_ids:
            lane_id = research_set.residence_of(member)
            if lane_id is None:
                members[member] = {
                    "lane_id": None,
                    "lane_name": None,
                    "lane_state": None,
                    "lane_type": None,
                    "lane_tip": None,
                    "ancestor_spell_ids": [],
                }
                continue
            lane = research_set.get_lane(lane_id)
            members[member] = {
                "lane_id": lane_id,
                "lane_name": lane.name,
                "lane_state": lane.state.value,
                "lane_type": lane.lane_type.value,
                "lane_tip": lane.tip_spell_id,
                # Version truth for honest move pairing (BUG-046): the
                # member's TRANSITIVE spell ancestry, so the strategy can
                # require a real version relation instead of inferring one
                # from a shared lane.
                "ancestor_spell_ids": self._transitive_ancestors(
                    research_set, member, kind="spell",
                ),
            }
        return {
            "group_id": node.group_id,
            "member_spell_ids": node.member_spell_ids,
            "parent_group_ids": node.parent_group_ids,
            # Transitive composition ancestry (BUG-045): the documented
            # parent-chain relationship includes every recorded ancestor,
            # not just direct parents.
            "ancestor_group_ids": self._transitive_ancestors(
                research_set, node.group_id, kind="group",
            ),
            "members": members,
        }

    def _transitive_ancestors(
            self,
            research_set: ResearchSet,
            identity: str,
            *,
            kind: str,
    ) -> List[str]:
        """
        Walk one identity's recorded ancestry chain to closure.

        Args:
            research_set:
                Owning set to resolve residence and nodes through.
            identity:
                Spell or composition identity to start from.
            kind:
                "spell" walks parent_spell_ids; "group" walks
                parent_group_ids.

        Returns:
            List[str]:
                Sorted transitive ancestor identities (cycle-safe; the
                starting identity is excluded; unresident links end their
                branch - ancestry never guesses).
        """
        seen: set = set()
        frontier: List[str] = [identity]
        while frontier:
            current = frontier.pop()
            lane_id = research_set.residence_of(current)
            if lane_id is None:
                continue
            node = research_set.get_lane(lane_id).get_node(current)
            parents = (
                node.parent_group_ids
                if kind == "group"
                else node.parent_spell_ids
            )
            for parent in parents:
                if parent not in seen and parent != identity:
                    seen.add(parent)
                    frontier.append(parent)
        return sorted(seen)

    def group_diff_research(
            self,
            left_group_id: str,
            right_group_id: str,
            *,
            strategy: str = "members",
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two recorded compositions.

        Purpose:
            The grouped mirror of `diff_research`, dispatched through the
            root-owned `GroupDiffEngine` (its own strategy family - owner
            ruling 2026-07-11). The default `members` strategy answers
            added/removed members and LANE-EVIDENCED version moves; each
            moved pair descends into `diff_research` grains
            (source/structural/parts) on the agent's next call.

        Contract:
            - LAZILY CONSTRUCTS AND CACHES the group diff engine on first use, so the first
              call pays construction and later calls do not.
            - Construction happens under the root lock, so concurrent first calls cannot
              produce two engines.

        Args:
            left_group_id:
                Left composition identity.
            right_group_id:
                Right composition identity.
            strategy:
                Registered grouped strategy name; "members" by default.

        Returns:
            Dict[str, object]:
                Detached verdict payload from the owned engine.

        Raises:
            RuntimeError:
                If either identity is unknown or not a composition.
            KeyError:
                If the strategy name is unknown.
        """
        self.check_cleaned()
        with self._lock:
            if self._group_diff_engine is None:
                self._group_diff_engine = GroupDiffEngine(
                    self._resolve_group_material,
                )
            engine = self._group_diff_engine
        return engine.diff(
            left_group_id, right_group_id, strategy=strategy,
        )

    def group_view(
            self,
            group_id: str,
            *,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return one composition's roster with residence and drift truth.

        Args:
            group_id:
                Composition identity to gather.
            set_name:
                Research set to resolve within.

        Contract:
            - Reports each member's LANE RESIDENCE, and a member with no residence is
              still reported rather than skipped - absence of a lane is data here,
              not an omission.
            - Read-only projection; it does not stage, promote or move anything.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            Dict[str, object]:
                `{"group_id", "member_count", "parent_group_ids",
                "author", "campaign", "created_at", "members":
                {spell_id: {lane join + "behind": bool|None}},
                "behind_count"}` - `behind` is True when the member's lane
                tip has moved past the pinned version (None when the
                member is unresident and drift is unknowable).
        """
        self.check_cleaned()
        node = self._locate_group_node(group_id, set_name)
        research_set = self.research_set(set_name)
        members: Dict[str, Dict[str, object]] = {}
        behind_count = 0
        for member in node.member_spell_ids:
            lane_id = research_set.residence_of(member)
            if lane_id is None:
                members[member] = {
                    "lane_id": None,
                    "lane_name": None,
                    "lane_state": None,
                    "lane_type": None,
                    "lane_tip": None,
                    "behind": None,
                }
                continue
            lane = research_set.get_lane(lane_id)
            behind = lane.tip_spell_id != member
            if behind:
                behind_count += 1
            members[member] = {
                "lane_id": lane_id,
                "lane_name": lane.name,
                "lane_state": lane.state.value,
                "lane_type": lane.lane_type.value,
                "lane_tip": lane.tip_spell_id,
                "behind": behind,
            }
        return {
            "group_id": node.group_id,
            "member_count": node.member_count,
            "parent_group_ids": node.parent_group_ids,
            "author": node.author,
            "campaign": node.campaign,
            "created_at": node.created_at,
            "members": members,
            "behind_count": behind_count,
        }

    def register_group(
            self,
            member_spell_ids: List[str],
            *,
            lane: Optional[str] = None,
            parent_group_ids: Optional[List[str]] = None,
            author: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            set_name: str = "default",
    ) -> "GroupedResearchNode":
        """
        Declare one composition WITH the ambient campaign stamp (parity
        law: compositions registered through the root carry the active
        campaign exactly as runtime auto-records do).

        Args:
            member_spell_ids:
                Non-empty member identities to pin.
            lane:
                Optional lane (name or id).
            parent_group_ids:
                Optional composition ancestry.
            author:
                Optional registering agent name.
            campaign:
                Optional explicit stamp (wins over the ambient one).
            reason:
                Optional reason line.
            set_name:
                Research set to register into.

        Contract:
            - CAMPAIGN DEFAULTS TO THE AMBIENT ONE. Passing `campaign=None` does not
              mean "no campaign" - it falls back to `active_campaign`. To record a
              group with no campaign you must clear the ambient one first.
            - Delegates the actual registration to the named research set, so that
              set's rules on lanes and parents apply.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            GroupedResearchNode:
                The recorded composition node.
        """
        self.check_cleaned()
        effective_campaign = (
            campaign if campaign is not None else self.active_campaign
        )
        return self.research_set(set_name).register_group(
            member_spell_ids,
            lane=lane,
            parent_group_ids=parent_group_ids,
            author=author,
            campaign=effective_campaign,
            reason=reason,
        )

    def recompose_group(
            self,
            previous_group_id: str,
            *,
            add: Optional[List[str]] = None,
            remove: Optional[List[str]] = None,
            author: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            set_name: str = "default",
    ) -> "GroupedResearchNode":
        """
        Evolve one composition WITH the ambient campaign stamp.

        Args:
            previous_group_id:
                The composition being evolved.
            add:
                Member identities to add.
            remove:
                Member identities to drop.
            author:
                Optional acting agent name.
            campaign:
                Optional explicit stamp (wins over the ambient one).
            reason:
                Optional reason line.
            set_name:
                Research set to evolve within.

        Contract:
            - CAMPAIGN DEFAULTS TO THE AMBIENT ONE, exactly as in `register_group` -
              `campaign=None` inherits `active_campaign` rather than meaning none.
            - Recomposition is expressed as ADD and REMOVE against a previous group
              rather than as a full replacement, so unlisted members are retained.
            - Delegates to the named research set.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            GroupedResearchNode:
                The new composition node.
        """
        self.check_cleaned()
        effective_campaign = (
            campaign if campaign is not None else self.active_campaign
        )
        return self.research_set(set_name).recompose_group(
            previous_group_id,
            add=add,
            remove=remove,
            author=author,
            campaign=effective_campaign,
            reason=reason,
        )

    def _current_compositions(
            self,
            set_name: str = "default",
    ) -> List["GroupedResearchNode"]:
        """
        Return every lane TIP that is a composition (current subsystems).

        Contract:
            - Tips only: historical compositions are history (walk the
              lane); the CURRENT composition of a subsystem is its tip.

        Args:
            set_name:
                Research set to scan.

        Returns:
            List[GroupedResearchNode]:
                Each lane's latest composition record (unaffected by later
                ordinary spell entries on the same lane).
        """
        research_set = self.research_set(set_name)
        tips: List["GroupedResearchNode"] = []
        for lane_name in research_set.lane_names():
            lane = research_set.get_lane(lane_name)
            # Current means each lane's LATEST composition record
            # (BUG-150): raw-tip probing let any later unrelated spell on
            # a mixed/default lane displace a still-resident composition
            # out of the reverse lift. Registration order decides; ordinary
            # spell records never revoke an informational composition.
            latest_group: Optional["GroupedResearchNode"] = None
            for candidate_id in lane.node_spell_ids():
                candidate = lane.get_node(candidate_id)
                if isinstance(candidate, GroupedResearchNode):
                    latest_group = candidate
            if latest_group is not None:
                tips.append(latest_group)
        return tips

    def compositions_of(
            self,
            spell_id: str,
            *,
            set_name: str = "default",
    ) -> List[Dict[str, object]]:
        """
        Return the current compositions pinning one spell (reverse lift).

        Args:
            spell_id:
                Member identity to look up.
            set_name:
                Research set to scan.

        Contract:
            - Rejects a non-string or empty `spell_id` up front with `ValueError`.
            - Searches only CURRENT composition tips, so a spell that appears solely
              in superseded compositions returns nothing. An empty result means "not
              in any current composition", not "unknown spell".
            - Resolves each hit's lane residence, so the result carries placement as
              well as membership.

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            List[Dict[str, object]]:
                `{"group_id", "lane_name"}` rows for every lane-tip
                composition whose roster pins the identity.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        research_set = self.research_set(set_name)
        rows: List[Dict[str, object]] = []
        for tip_node in self._current_compositions(set_name):
            if spell_id in tip_node.member_spell_ids:
                lane_id = research_set.residence_of(tip_node.group_id)
                lane = research_set.get_lane(lane_id)
                rows.append({
                    "group_id": tip_node.group_id,
                    "lane_name": lane.name,
                })
        return rows

    def group_footprint_view(
            self,
            group_id: str,
            *,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return one composition's physical shadow (module footprint).

        Purpose:
            The union of the pinned members' recorded module worlds -
            derived at read time, never stored (stored footprints would
            rot as compositions evolve). The per-module member map exposes
            SHARED matter: modules carried by more than one member are
            where the subsystem physically couples to itself.

        Contract:
            - REQUIRES LIVE CUSTODY through the crystallizer; without it this raises rather
              than returning a partial footprint.
            - Reports UNKNOWN MEMBERS separately from resolved ones, so an incomplete
              footprint is visible in the result rather than silently short.

        Args:
            group_id:
                Composition identity to shadow.
            set_name:
                Research set to resolve within.

        Returns:
            Dict[str, object]:
                `{"group_id", "modules", "module_members":
                {module: [members]}, "shared_modules",
                "unknown_custody_members"}` - members without a custody
                crystal report honestly instead of raising (the
                composition is informational; its members may predate
                custody).

        Raises:
            RuntimeError:
                If the identity is unknown/not a composition, or the
                crystallizer is cleaned or inactive.
        """
        self.check_cleaned()
        node = self._locate_group_node(group_id, set_name)
        crystallizer = self._require_live_custody()
        module_members: Dict[str, List[str]] = {}
        unknown_members: List[str] = []
        for member in node.member_spell_ids:
            try:
                payload = crystallizer.get_spell_crystal(member).describe()
            except Exception:
                unknown_members.append(member)
                continue
            for module_name in list(payload.get("module_targets", [])):
                module_members.setdefault(
                    str(module_name), [],
                ).append(member)
        return {
            "group_id": node.group_id,
            "modules": sorted(module_members.keys()),
            "module_members": module_members,
            "shared_modules": sorted(
                module_name
                for module_name, members in module_members.items()
                if len(members) > 1
            ),
            "unknown_custody_members": unknown_members,
        }

    def group_drift_view(
            self,
            group_id: str,
            *,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return recorded-vs-disk drift filtered to one composition's shadow.

        Purpose:
            "What is already broken in THIS area": the full custody drift
            report (sealed fingerprints re-hashed against the live disk)
            narrowed to the composition's module footprint, with counts
            recomputed over the narrowed set so the numbers describe the
            subsystem, not the world.

        Contract:
            - BUILT ON `group_footprint_view`, so it inherits the live-custody requirement
              and the unknown-member reporting.
            - Intersects the footprint's modules with the custody drift report, so a module
              absent from either side simply does not appear.

        Args:
            group_id:
                Composition identity to check.
            set_name:
                Research set to resolve within.

        Returns:
            Dict[str, object]:
                `{"group_id", "statuses": {module: status}, "radii":
                {module: radius}, "counts": {status: n},
                "footprint_size"}`.

        Raises:
            RuntimeError:
                If the identity is unknown/not a composition, or the
                crystallizer is cleaned or inactive.
        """
        self.check_cleaned()
        footprint = self.group_footprint_view(group_id, set_name=set_name)
        modules = set(footprint["modules"])
        report = self._require_live_custody().analyze_impact()
        drift = report.get("drift") if isinstance(report, dict) else None
        statuses_all = (
            drift.get("statuses") if isinstance(drift, dict) else None
        )
        radii_all = drift.get("radii") if isinstance(drift, dict) else None
        statuses: Dict[str, str] = {}
        counts: Dict[str, int] = {}
        if isinstance(statuses_all, dict):
            for module_name, status in statuses_all.items():
                if str(module_name) in modules:
                    statuses[str(module_name)] = str(status)
                    counts[str(status)] = counts.get(str(status), 0) + 1
        radii: Dict[str, object] = {}
        if isinstance(radii_all, dict):
            for module_name, radius in radii_all.items():
                if str(module_name) in modules:
                    radii[str(module_name)] = radius
        return {
            "group_id": footprint["group_id"],
            "statuses": statuses,
            "radii": radii,
            "counts": counts,
            "footprint_size": len(modules),
        }

    def group_history_view(
            self,
            group_id: str,
            *,
            campaign: Optional[str] = None,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return the journal story of one subsystem area.

        Args:
            group_id:
                Composition identity to gather around.
            campaign:
                Optional campaign stamp - the WHERE x WHEN join: narrow
                the area's story to one effort.
            set_name:
                Research set to resolve within.

        Contract:
            - Straight delegation to the named research set's group history; it adds no
              filtering or ordering of its own.
            - `campaign` is passed through AS GIVEN here - unlike `register_group`
              and `recompose_group`, this one does NOT fall back to the ambient
              campaign, so None means "unfiltered".

        Threading:
            Unsynchronized read of a plain flag; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If mutation research has been cleaned.

        Returns:
            Dict[str, object]:
                The set's `group_history` payload (subsystem-lane,
                member, and member-lane events in journal order).
        """
        self.check_cleaned()
        return self.research_set(set_name).group_history(
            group_id, campaign=campaign,
        )

    def recent_activity_view(
            self,
            *,
            limit: int = 50,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return the newest journal events across the whole record.

        Purpose:
            The cold-landing read: an agent arriving in a room asks "what
            happened here lately" before choosing where to work - one
            call, newest-first context, campaign stamps intact.

        Contract:
            - CLAMPS `limit` to a non-negative integer, so a negative value becomes 0 rather
              than raising or reading backwards.
            - Reads the set's journal, which is append-only history rather than current
              state.

        Args:
            limit:
                Bound on the number of newest entries (the journal's
                bounded-window read).
            set_name:
                Research set to read.

        Returns:
            Dict[str, object]:
                `{"set_name", "entries", "entry_count",
                "next_sequence"}` - entries in journal order (oldest of
                the window first).
        """
        self.check_cleaned()
        payload = self.research_set(set_name).journal.describe(
            recent=max(0, int(limit)),
        )
        return {
            "set_name": set_name,
            "entries": payload["entries"],
            "entry_count": payload["entry_count"],
            "next_sequence": payload["next_sequence"],
        }

    def group_impact_view(
            self,
            group_id: str,
            *,
            set_name: str = "default",
    ) -> Dict[str, object]:
        """
        Return one composition's union blast radius with the closure math.

        Purpose:
            The crossing move at composition grain: every member's blast
            radius (custody truth) unioned, split by DIRECTION - internal
            (consequences landing on fellow members) vs outbound
            (consequences escaping the composition) - with CLOSURE (the
            fraction of affected spells that are members; ~1.0 = a safe
            workspace) and the ADJACENCY lift (which OTHER current
            compositions the radius touches).

        Contract:
            - REQUIRES LIVE CUSTODY through the crystallizer.
            - Computes affected modules from the group's MEMBER SET, so a member that
              resolves to no module contributes nothing rather than failing the call.

        Args:
            group_id:
                Composition identity at the blast center.
            set_name:
                Research set supplying declared truth for the joins.

        Returns:
            Dict[str, object]:
                `{"group_id", "member_count", "affected_modules",
                "affected_spells", "internal_spells", "outbound_spells",
                "closure", "affected_compositions", "research",
                "per_member"}`.

        Raises:
            RuntimeError:
                If the identity is unknown/not a composition, or the
                crystallizer is cleaned or inactive.
        """
        self.check_cleaned()
        node = self._locate_group_node(group_id, set_name)
        crystallizer = self._require_live_custody()
        member_set = set(node.member_spell_ids)
        affected_modules: set = set()
        affected_spells: set = set()
        per_member: Dict[str, Dict[str, object]] = {}
        for member in node.member_spell_ids:
            radius = crystallizer.analyze_impact(spell_id=member)
            member_modules = [
                str(name) for name in list(radius.get("affected_modules", []))
            ]
            member_spells = [
                str(sha) for sha in list(radius.get("affected_spells", []))
            ]
            affected_modules.update(member_modules)
            affected_spells.update(member_spells)
            per_member[member] = {
                "affected_modules": sorted(member_modules),
                "affected_spells": sorted(member_spells),
                "unknown_spell": bool(radius.get("unknown_spell", False)),
            }
        internal = sorted(affected_spells & member_set)
        outbound = sorted(affected_spells - member_set)
        closure: Optional[float] = None
        if affected_spells:
            closure = len(internal) / len(affected_spells)
        research_set = self.research_set(set_name)
        affected_compositions: List[Dict[str, object]] = []
        for tip_node in self._current_compositions(set_name):
            if tip_node.group_id == node.group_id:
                continue
            shared = sorted(
                set(tip_node.member_spell_ids) & affected_spells
            )
            if shared:
                tip_lane_id = research_set.residence_of(tip_node.group_id)
                affected_compositions.append({
                    "group_id": tip_node.group_id,
                    "lane_name": research_set.get_lane(tip_lane_id).name,
                    "shared_members": shared,
                })
        return {
            "group_id": node.group_id,
            "member_count": node.member_count,
            "affected_modules": sorted(affected_modules),
            "affected_spells": sorted(affected_spells),
            "internal_spells": internal,
            "outbound_spells": outbound,
            "closure": closure,
            "affected_compositions": affected_compositions,
            "research": self._residency_join(
                sorted(affected_spells), set_name,
            ),
            "per_member": per_member,
        }

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
            - NO-OP while the root is inactive or the crystallizer is not
              recording (cleanup sets `_activated` False, so late teardown
              callbacks fall out here too - no cleaned-probing needed).

        Threading:
            The whole verb runs under the reentrant emission lock: the
            composition snapshot is built and published by the same holder,
            so replace-on-emit publication can never move the durable
            composition backwards relative to committed live mutations (a
            later-arriving emitter always reads the newer live state before
            it publishes). Lock order is emission -> root -> set.

        Returns:
            None.
        """
        if not self._activated:
            return
        with self._emission_lock:
            if not self._activated:
                return
            crystallizer = self._crystallizer
            if not crystallizer.activated:
                return
            configuration_payload: Dict[str, object] = {}
            if self._configured:
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
