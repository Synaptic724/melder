import ast
import hashlib
import threading
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Tuple

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
from melder.mutation_research.diff.diff_engine import DiffEngine
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
        "_diff_engine",
        "_synthesizer",
        "_active_campaign",
        "_staged_ancestry",
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
            self._diff_engine: Optional[DiffEngine] = None
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
            if self._diff_engine is not None:
                try:
                    self._diff_engine.cleanup()
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
            del self._diff_engine
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
            *,
            hydrate_from_record: bool = True,
    ) -> None:
        """
        Activate the mutation-research root using one activated configuration.

        Args:
            configuration:
                Optional configuration to install before activation.
            hydrate_from_record:
                When True (default), a VIRGIN registry (nothing but the
                untouched default set) rebuilds itself from the active
                profile's recorded composition at activation - the twin
                docking loop: emit while live, hydrate on the way up. Live
                research is never clobbered; a non-virgin registry skips
                hydration and re-records itself instead.

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
        if hydrate_from_record:
            self._hydrate_from_record_when_virgin()
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
        if not self._configured or self._configuration is None:
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

    def _registry_is_virgin(self) -> bool:
        """
        Return whether no research has ever been declared on this root.

        Contract:
            - Virgin means exactly the guaranteed default set with its
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

    def _hydrate_from_record_when_virgin(self) -> None:
        """
        Rebuild a virgin registry from the recorded composition, when any.

        Contract:
            - NO-OP while the crystallizer is cleaned/inactive, when the
              active profile has never recorded the MR twin, when the
              recorded composition is empty, or when live research already
              exists (live truth wins; it re-records at the next emission).

        Returns:
            None.
        """
        crystallizer = self._crystallizer
        if crystallizer.cleaned:
            return
        if not crystallizer.activated:
            return
        recorded = crystallizer.describe_mutation_research_record()
        if not isinstance(recorded, dict):
            return
        composition = recorded.get("composition_payload")
        if not isinstance(composition, dict) or not composition:
            return
        if not self._registry_is_virgin():
            return
        self.load_recorded_composition(composition)

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
        # New sets inherit the configured join-policy posture immediately.
        self._propagate_lane_type_enforcement()
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
        node = research_set.record_world_entry(
            spell_id,
            staged=staged,
            parent_spell_ids=staged_parents,
            author=author,
            reason=reason,
            campaign=effective_campaign,
        )
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
            - An undeclared `to_spell_id` is declared first (world-entry
              catch-up: a promotion proves the version exists), then the
              `promoted` event records with the supplied endpoints.

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
            research_set.record_world_entry(
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
            - `in_custody` is None when the crystallizer cannot answer
              (inactive/cleaned) - a read never fabricates or raises there.

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
        if lane_id is not None:
            lane = research_set.get_lane(lane_id)
            lane_name = lane.name
            lane_state = lane.state.value
            lane_type = lane.lane_type.value
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
            "runtime": runtime,
            "frame_name": frame_name,
            "index_id": index_id,
            "in_custody": in_custody,
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

        Returns:
            Tuple[Optional[str], Optional[str], bool]:
                `(frame_name, index_id, selected)` - Nones/False when the
                identity is not a live index member anywhere.
        """
        aether = self._aether
        if aether is None or aether.cleaned:
            return None, None, False
        for frame_name, frame in list(aether._aetheric_frames.items()):
            try:
                if frame.cleaned:
                    continue
                index = frame.find_index_for_spell(spell_id)
            except Exception:
                continue
            if index is None or index.cleaned:
                continue
            return (
                frame_name,
                index.id,
                index.selected_spell_id == spell_id,
            )
        return None, None, False

    def _probe_custody(self, spell_id: str) -> Optional[bool]:
        """
        Probe crystallizer custody for one identity, without raising.

        Args:
            spell_id:
                Identity to probe.

        Returns:
            Optional[bool]:
                True/False for custody presence; None when the crystallizer
                cannot answer (inactive or cleaned).
        """
        crystallizer = self._crystallizer
        if crystallizer.cleaned or not crystallizer.activated:
            return None
        try:
            crystallizer.get_spell_crystal(spell_id)
        except KeyError:
            return False
        except Exception:
            return None
        return True

    # ------------------------------------------------------------------
    # Derived diff reads
    # ------------------------------------------------------------------

    def diff_research(
            self,
            left_spell_id: str,
            right_spell_id: str,
            *,
            strategy: str = "source",
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two version identities.

        Purpose:
            The read verb behind "commits are full objects, diffs are
            derived": material resolves through crystallizer custody (the
            SHA is the SpellCrystal id) and the comparison runs in the
            registered strategy - nothing is stored.

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
        with self._lock:
            if self._diff_engine is None:
                self._diff_engine = DiffEngine(self._resolve_diff_material)
            engine = self._diff_engine
        return engine.diff(left_spell_id, right_spell_id, strategy=strategy)

    def create_diff_engine(self) -> DiffEngine:
        """
        Create one standalone diff engine over crystallizer custody.

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
        if crystallizer.cleaned or not crystallizer.activated:
            raise RuntimeError(
                "Crystallizer custody is unavailable (inactive or cleaned); "
                "diff material cannot be resolved."
            )
        payload = crystallizer.get_spell_crystal(spell_id).describe()
        sources: Dict[str, object] = {}
        synthetic = payload.get("synthetic_module_sources")
        if isinstance(synthetic, dict):
            for module_name, custody_payload in synthetic.items():
                if isinstance(custody_payload, dict):
                    text = custody_payload.get("source_text")
                    if isinstance(text, str) and text:
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
                If the crystallizer is cleaned or inactive.
        """
        crystallizer = self._crystallizer
        if crystallizer.cleaned or not crystallizer.activated:
            raise RuntimeError(
                "Crystallizer custody is unavailable (inactive or cleaned); "
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
                "unknown_module"?}`.

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
        payload = self._require_live_custody().get_spell_crystal(
            spell_id
        ).describe()
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
        for carrier_key in ("synthetic_module_sources", "user_module_sources"):
            carrier = payload.get(carrier_key)
            if isinstance(carrier, dict):
                entry = carrier.get(module_name)
                if isinstance(entry, dict):
                    text = entry.get("source_text")
                    if isinstance(text, str) and text:
                        return {
                            "source": text,
                            "origin": "recorded",
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
                        "drifted": drifted,
                        "text_unavailable": False,
                    }
        return {
            "source": None,
            "origin": None,
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
        crystallizer = self._require_live_custody()
        radius = crystallizer.analyze_impact(
            module_name=module_name,
            spell_id=spell_id,
        )
        affected = [
            str(sha) for sha in list(radius.get("affected_spells", []))
        ]
        radius["research"] = self._residency_join(affected, set_name)
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
        payload = self._require_live_custody().get_spell_crystal(
            spell_id
        ).describe()
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
            root_payload = self._require_live_custody().get_spell_crystal(
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
