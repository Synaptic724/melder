import threading
import time
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit_ward.contract.contract import Contract
    from melder.aether.spellbook.bind.spell_index import SpellIndex
    from melder.aether.spellbook.spell import Spell

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystals.crystallizer_crystal import (
    CrystallizerCrystal,
)
from melder.crystallizer.asset_management.asset_management_system import (
    AssetManagementSystem,
)
from melder.crystallizer.crystal_loader_system.crystal_loader_system import (
    CrystalLoaderSystem,
)
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.synthetic_module import SyntheticModule
from melder.crystallizer.persistence.persistence_system import PersistenceSystem
from melder.crystallizer.crystals.contract_crystal import (
    ContractCrystal,
)
from melder.crystallizer.crystals.spell_index_crystal import (
    SpellIndexCrystal,
)
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

class Crystallizer(Cleanable):
    """
    Public facade and singleton ownership root for crystallizer behavior.

    Purpose:
        Present one stable public surface over the crystallizer's three V3
        subsystems while keeping their implementation objects private:

        - `PersistenceSystem`: the in-process record and checkpoint ledger.
        - `AssetManagementSystem`: cache, formation files, and external mesh.
        - `CrystalLoaderSystem`: admission planning and runtime unfolding.

        The package-level crystal classes remain value carriers, and
        `crystal_analysis` remains a shared service; neither becomes another
        root owned by callers.

    Usage:
        Importing `melder` constructs the hosting `Aether`, so subsequent
        `Crystallizer()` calls return its hosted facade. Create and activate a
        configuration, activate this root, then use facade verbs for profiles,
        checkpoints, formations, impact analysis, or restore. Treat the three
        owned subsystem classes as implementation boundaries; construct and
        operate them only through this facade.

    Contract:
        - Process-wide singleton privately hosted by `Aether`.
        - Construction starts unconfigured and inactive unless an explicit
          configuration is supplied; activation remains a separate act.
        - Public record, asset, analysis, and load operations require an
          activated root and reject use after cleanup.
        - Callers exchange names, ids, detached dictionaries, and crystal
          carriers through this facade. Persistence profiles, load plans,
          engines, and asset managers do not escape as public state.
        - Recording is passive: runtime owners push twins into `emit()`;
          this root does not discover or walk the live world.
        - Crystallizer-off worlds preserve runtime behavior because inactive
          emission paths do not record.

    Threading:
        The class lock protects singleton publication. The instance lock
        serializes lifecycle and facade state transitions; owned subsystems
        apply their own narrower locking contracts.

    Lifecycle / Cleanup:
        `Aether` owns the singleton. Cleanup is terminal and orders borrowers
        before the record: loader, assets, persistence, then configuration.
        Singleton bookkeeping is reset only after child teardown completes.
    """
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. The persistence facade. Configure and activate it, then use the profile and "
        "checkpoint verbs (create_checkpoint, load_checkpoint, describe_profile, list_checkpoint_ids) "
        "plus analyze_impact(...). Every emit verb is a NO-OP while inactive."
    )

    __melder_internal__ = _mrg.sentinel
    _instance = None
    _lock = threading.RLock()
    _initialized = False
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_aether",
        "_configuration",
        "_configured",
        "_activated",
        "_persistence_system",
        "_asset_management_system",
        "_crystal_loader_system",
        "_checkpoint_interval_seconds",
        "_last_automatic_checkpoint_monotonic",
        "_auto_flush_checkpoints",
    ]

    def __new__(
            cls,
            *args: object,
            **kwargs: object,
    ) -> "Crystallizer":
        """
        Ensure `Crystallizer` behaves as a singleton.

        Returns:
            Crystallizer: The one process-wide crystallizer instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Crystallizer, cls).__new__(cls)
        return cls._instance

    def __init__(
            self,
            *,
            aether: Optional[Aether] = None,
            configuration: Optional[CrystallizerConfiguration] = None,
    ) -> None:
        """
        Initialize the singleton crystallizer root.

        Args:
            aether:
                Optional hosting `Aether` singleton. When provided, the
                crystallizer records the private runtime host that owns this
                root in the same style as Nexus. First-time initialization
                requires this host.
            configuration:
                Optional initial crystallizer configuration. When omitted, the
                root starts unconfigured and inactive.

        Returns:
            None.
        """
        if Crystallizer._initialized:
            return

        if aether is None:
            with Crystallizer._lock:
                if Crystallizer._instance is self and not Crystallizer._initialized:
                    Crystallizer._instance = None
                    Crystallizer._initialized = False
            raise ValueError("Aether must be provided to initialize Crystallizer.")

        try:
            super().__init__()
            self._id: str = IDBuilder.create_id()
            self._aether: Optional[Aether] = aether
            self._configuration: Optional[CrystallizerConfiguration] = None
            self._configured: bool = False
            self._activated: bool = False
            self._persistence_system: PersistenceSystem = PersistenceSystem()
            # Same-rank children (V3 ownership): the record and the asset
            # system. The asset system BORROWS the record (feedstock in,
            # insert sink back) and OWNS the cache + the optional
            # ExternalPersistenceManager the user attaches via
            # configure_external_persistence_manager.
            self._asset_management_system: AssetManagementSystem = (
                AssetManagementSystem(self._persistence_system)
            )
            # The unfold owner (V3 third child): every load runs through
            # its mediated admission pipeline and it remembers the last
            # load's detached payload. The borrowed aether (may be None in
            # bare-record tests) lets load verbs claim system-wide load
            # authority through the Aether LoadGate for their span.
            self._crystal_loader_system: CrystalLoaderSystem = (
                CrystalLoaderSystem(self._persistence_system, aether=aether)
            )
            # Automatic-checkpoint cadence; installed from the frozen
            # configuration at activate() (0.0 = not yet activated).
            self._checkpoint_interval_seconds: float = 0.0
            self._last_automatic_checkpoint_monotonic: float = 0.0
            self._auto_flush_checkpoints: bool = False

            if configuration is not None:
                self.configure(configuration)
            Crystallizer._initialized = True
        except Exception:
            with Crystallizer._lock:
                if Crystallizer._instance is self:
                    Crystallizer._instance = None
                Crystallizer._initialized = False
            raise

    def cleanup(self) -> None:
        """
        Tear down the crystallizer root and release singleton publication.

        Contract:
            - Idempotent and terminal; public methods reject later use.
            - Cleans the loader and asset borrowers before the persistence
              record they reference, preserving the V3 edge and lock laws.
            - Cleans the installed configuration after all three subsystems.
            - Resets class-level singleton state only after instance teardown.

        Returns:
            None.

        Threading:
            Serialized by the instance lock. Singleton publication is reset
            under the class lock after owned state has been released.

        Lifecycle / Cleanup:
            Called by the hosting `Aether` during root teardown. This method
            does not deactivate and preserve state; use `deactivate()` for
            that reversible lifecycle transition.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Children first, borrowers BEFORE the record they borrow:
            # loader, then assets, then the record.
            if (
                    self._crystal_loader_system is not None
                    and not self._crystal_loader_system.cleaned
            ):
                self._crystal_loader_system.cleanup()
            if (
                    self._asset_management_system is not None
                    and not self._asset_management_system.cleaned
            ):
                self._asset_management_system.cleanup()
            if self._persistence_system is not None and not self._persistence_system.cleaned:
                self._persistence_system.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False

            del self._crystal_loader_system
            del self._asset_management_system
            del self._persistence_system
            del self._checkpoint_interval_seconds
            del self._last_automatic_checkpoint_monotonic
            del self._auto_flush_checkpoints
            del self._configuration
            del self._aether
            del self._id
        with Crystallizer._lock:
            Crystallizer._instance = None
            Crystallizer._initialized = False

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the singleton for isolated test setup.

        Returns:
            None.
        """
        with cls._lock:
            instance = cls._instance
        if instance is not None and not instance.cleaned:
            instance.cleanup()
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    @property
    def id(self) -> str:
        """
        Return the stable crystallizer root id.

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
            bool: True when crystallizer has an installed configuration.
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
        Return whether the crystallizer root is active.

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
            bool: True when the crystallizer root is active.
        """
        return self.activated

    @property
    def configuration(self) -> Optional[CrystallizerConfiguration]:
        """
        Return the installed configuration, if any.

        Returns:
            Optional[CrystallizerConfiguration]: Installed configuration.
        """
        self.check_cleaned()
        return self._configuration

    def create_configuration(self) -> CrystallizerConfiguration:
        """
        Create a fresh crystallizer configuration object.

        Returns:
            CrystallizerConfiguration: New mutable config object.
        """
        self.check_cleaned()
        return CrystallizerConfiguration()

    def configure(self, configuration: CrystallizerConfiguration) -> None:
        """
        Install one configuration on the crystallizer root.

        Args:
            configuration:
                Configuration object to install.

        Returns:
            None.

        Raises:
            TypeError:
                If the supplied object is not a crystallizer configuration.
            RuntimeError:
                If crystallizer is already active.
        """
        self.check_cleaned()
        if not isinstance(configuration, CrystallizerConfiguration):
            raise TypeError(
                "configuration must be a CrystallizerConfiguration instance."
            )
        with self._lock:
            if self._activated:
                raise RuntimeError(
                    "Cannot reconfigure Crystallizer while it is active."
                )
            self._configuration = configuration
            self._configured = True

    def activate(
            self,
            configuration: Optional[CrystallizerConfiguration] = None,
    ) -> None:
        """
        Activate the crystallizer root using one activated configuration.

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
                "CrystallizerConfiguration must be activated before activating Crystallizer."
            )
        self._configuration.validate()
        with self._lock:
            self._activated = True
            # Install the checkpoint policy from the frozen configuration:
            # cadence for the emit-driven ticker, retention for the ledger.
            self._checkpoint_interval_seconds = (
                float(self._configuration.checkpoint_interval_minutes) * 60.0
            )
            self._persistence_system.set_checkpoint_retention(
                self._configuration.max_persistence_crystals
            )
            self._auto_flush_checkpoints = (
                self._configuration.auto_flush_checkpoints
            )
            # Restore driver policy (S4, parallel_restore_ulid_identity;
            # owner ruling 2026-07-19: parallel is the driver): install
            # the loader's execution pool from the frozen configuration.
            # The three knobs are defaulted-optional by validate()'s
            # contract, so activation reads the typed properties (schema
            # defaults True/4/60000) exactly like checkpoint policy above.
            self._crystal_loader_system.configure_restore_scheduler(
                parallel_enabled=(
                    self._configuration.restore_parallel_enabled
                ),
                worker_count=(
                    self._configuration.restore_scheduler_workers
                ),
                barrier_timeout_ms=(
                    self._configuration
                    .restore_scheduler_barrier_timeout_milliseconds
                ),
            )
            self._last_automatic_checkpoint_monotonic = time.monotonic()
        # Self-emission: the recorder's own policy is recorded truth.
        # Activation is the crystallizer's configured moment, so the twin
        # emits here into the (now live) active profile - a cache-booted
        # world can reload this exact policy via
        # CrystallizerConfiguration.load_recorded_dictionary before
        # activating its own crystallizer.
        self._emit_policy_twin()
        # Root catch-up: the Aether structurally precedes the crystallizer
        # (it hosts it), so its configuration twin could never record at
        # its own activation in the normal boot order. Now that recording
        # is live, capture the already-active root exactly once - a
        # targeted root emission, not a world walk (bind still owns every
        # structural emission).
        if (
                self._aether is not None
                and self._aether.configured
                and self._aether.configuration is not None
        ):
            self._aether.configuration.emit_configured_twin_when_recording()

    def _emit_policy_twin(self, profile_name: Optional[str] = None) -> None:
        """
        Internal emission seam

        Emit the crystallizer's own policy twin from the frozen
        configuration.

        Purpose:
            The recorder's policy is recorded truth, and EVERY snapshot
            must be self-describing (owner ruling): activation emits the
            twin first, and every checkpoint seal re-emits it so each
            sealed window carries the policy alongside all the other
            captured items - a single cached crystal then tells a booting
            process exactly which recording policy made it, no chain fold
            required.

        Contract:
            - NO-OP while not activated (emit gates internally as well).
            - The twin records the CONFIGURED surface: fluent-built
              configurations legally leave optional keys unset, and the
              reload lane backfills-with-report on the way back in.
            - Replace-on-emit keeps exactly one live twin per profile;
              per-seal re-emission costs one journal entry per window.

        Args:
            profile_name:
                Profile the policy twin records into; None means the
                active profile. A profile-scoped checkpoint passes its
                explicit target so the twin lands in the sealed profile's
                window instead of leaking into the active one (BUG-158).

        Returns:
            None.
        """
        if not self._activated or self._configuration is None:
            return
        configuration_payload: Dict[str, object] = {}
        for property_name in self._configuration.available_properties.keys():
            if not self._configuration.has_property(property_name):
                continue
            property_value = self._configuration.get_property(property_name)
            if (
                    isinstance(property_value, (str, int, float, bool))
                    or property_value is None
            ):
                configuration_payload[property_name] = property_value
            elif isinstance(property_value, (list, tuple, set, frozenset)):
                configuration_payload[property_name] = [
                    str(item) for item in property_value
                ]
            else:
                configuration_payload[property_name] = str(property_value)
        # Direct record (NOT self.emit): the seal paths call this seam,
        # and emit's cadence ticker could interleave an automatic seal
        # mid-checkpoint. The record verb is the same sink minus the
        # ticker.
        self._persistence_system.record(
            CrystallizerCrystal(configuration_payload=configuration_payload),
            profile_name=profile_name,
        )

    def _maybe_create_automatic_checkpoint(self) -> None:
        """
        Internal

        Seal an automatic checkpoint when the configured cadence elapsed.

        Purpose:
            The emit-driven ticker: every sink verb calls this after
            recording. When at least `checkpoint_interval_minutes` of wall
            time passed since the previous automatic checkpoint, the active
            profile's delta window is sealed into a new PersistenceCrystal.
            Activity-driven by design - a quiet world journals nothing and
            therefore mints nothing; no background thread exists.

        Contract:
            - NO-OP while not activated.
            - The cadence stamp advances BEFORE sealing so a failing seal
              cannot hot-loop on every subsequent emit.
            - Ledger retention (FIFO dropout) is enforced by the
              persistence system at every seal.

        Returns:
            None.
        """
        if not self._activated:
            return
        now = time.monotonic()
        with self._lock:
            if (
                    now - self._last_automatic_checkpoint_monotonic
                    < self._checkpoint_interval_seconds
            ):
                return
            self._last_automatic_checkpoint_monotonic = now
        # Every snapshot is self-describing: the policy twin re-emits into
        # this seal's window (owner ruling).
        self._emit_policy_twin()
        sealed_id = self._persistence_system.create_checkpoint(
            description="automatic cadence checkpoint",
        )
        if self._auto_flush_checkpoints:
            # Crash-safe lane: the cadence seal ships to the local cache
            # immediately (one atomic JSON write per interval), then to
            # the external manager when one is attached (the DB opt-in).
            # S3 decomposition: one asset verb runs both legs.
            self._asset_management_system.flush_checkpoint(sealed_id)

    def deactivate(self) -> None:
        """
        Deactivate the crystallizer root without dropping configuration.

        Contract:
            Stops activated-only facade operations and future recording while
            preserving the installed configuration and all subsystem state.
            Existing profiles, checkpoints, cache files, and formation files
            are not deleted.

        Returns:
            None.

        Threading:
            Serialized by the instance lock.

        Lifecycle / Cleanup:
            Reversible through `activate()`. This is not teardown and does
            not clean any owned object.
        """
        self.check_cleaned()
        with self._lock:
            self._activated = False


    def get_spell_crystal(self, spell_id: str) -> SpellCrystal:
        """
        Return the recorded custody crystal for one spell (active profile).

        Purpose:
            The runtime custody lookup: loaders (seed/unseed) and
            MutationResearch fetch a spell's crystal through this facade -
            the persistence model stays in the depths. Fetch fresh per
            use; the record cleans displaced crystals on re-emission, so
            long-lived references go stale by design.

        Args:
            spell_id:
                The spell's SHA256 identity.

        Returns:
            SpellCrystal:
                The currently recorded crystal for the spell.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If the active profile records no crystal for `spell_id`.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.get_spell_crystal(spell_id)

    def describe_mutation_research_record(self) -> Optional[Dict[str, object]]:
        """
        Return the recorded MutationResearch twin payload (active profile).

        Purpose:
            The MR hydration read facade: at activation the MR root pulls
            the recorded composition to rebuild its research registry from
            the record. Detached dict only - the persistence model stays
            in the depths.

        Returns:
            Optional[Dict[str, object]]:
                The recorded twin's `describe()` payload (carrying
                `configuration_payload` and `composition_payload`), or None
                when the active profile has never recorded the MR twin.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.describe_mutation_research_record()

    def analyze_impact(
            self,
            module_name: Optional[str] = None,
            spell_id: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Answer blast-radius questions over the recorded custody surface.

        Purpose:
            The S3 impact facade: "which spells does this module reach?",
            "what does changing this spell touch?", or - with no
            arguments - the full source-drift report ("what will my
            uncommitted edits break?"). Read-only over the record; the
            live runtime is never inspected.

        Contract:
            - module_name -> that module's transitive blast radius.
            - spell_id -> the spell's root-module radius (+ identity).
            - Both None -> the engine's full describe (custody counts +
              drift statuses + radii for every drifted/absent module).
            - Supplying BOTH refuses (one question per call).
            - Unknown modules/spells answer honestly with "unknown_*"
              markers, never a raise.

        Args:
            module_name:
                Optional canonical module name at the blast center.
            spell_id:
                Optional spell SHA256 custody identity.

        Returns:
            Dict[str, object]: The detached impact view.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            ValueError:
                If both module_name and spell_id are supplied.
        """
        self.check_cleaned()
        self._require_activated()
        if module_name is not None and spell_id is not None:
            raise ValueError(
                "analyze_impact answers one question per call: supply "
                "module_name OR spell_id, not both."
            )
        # Lazy import mirrors the loader's runtime-surface import law.
        from melder.crystallizer.crystal_analysis.impact_engine import (
            ImpactEngine,
        )

        engine = ImpactEngine(
            self._persistence_system.describe_spell_crystals()
        )
        try:
            if module_name is not None:
                return engine.blast_radius_of_module(module_name)
            if spell_id is not None:
                return engine.blast_radius_of_spell(spell_id)
            return engine.describe()
        finally:
            engine.cleanup()

    def capture_index_graft(self, index_id: str) -> Dict[str, object]:
        """
        Capture one spell_index's graft record from the active profile.

        Purpose:
            The graft lane's capture half (owner ruling: the graft unit
            is the INDEX - all members, custody, selection). The record
            is a versioned, JSON-safe dict; store it wherever you like
            (mesh handlers, formations, plain files) and hand it to
            graft_index against any live conjured book.

        Args:
            index_id:
                The recorded index identity.

        Returns:
            Dict[str, object]: The versioned graft record.

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active.
            KeyError: If no index twin is recorded under `index_id`.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.capture_index_graft(index_id)

    def graft_index(
            self,
            graft_record: Dict[str, object],
            host_spellbook: Any,
            skip_resident: bool = False,
            merge_into_index: Optional[Any] = None,
            adopt_recorded_selection: bool = False,
    ) -> Dict[str, object]:
        """
        Re-integrate one captured index into a LIVE host book.

        Purpose:
            The graft lane's restore half: the selected member binds
            ACTIVE (bind creates the fresh index and selects it), parked
            members ride bind_inactive onto it - normal verbs only,
            existing indexes never mutated. Blast-radius due diligence
            is one call away: analyze_impact BEFORE grafting into a
            world you care about.

        Args:
            graft_record:
                The versioned record from capture_index_graft.
            host_spellbook:
                The live, CONJURED book receiving the graft (live-object
                facade per the create_spell_crystal precedent).
            skip_resident:
                True skips members already resident in the host frame
                (shortfall each); False refuses the whole graft on the
                first resident member (default - the conservative
                overlap rule).
            merge_into_index:
                MERGE MODE (slice 3, 2026-07-11): a LIVE SpellIndex in
                the host frame; members park onto IT via the public
                bind_inactive verb instead of minting a fresh index.
                Fresh-index-only remains the default.
            adopt_recorded_selection:
                Merge-mode only: notch the record's selected member
                active on the target after grafting (public notch verb;
                honest shortfall when the selection did not graft).

        Returns:
            Dict[str, object]: The runner's detached report ({status,
            recorded/live index ids, merged_into_existing,
            selection_adopted, members_bound, members_parked,
            skipped_resident, shortfalls}).

        Raises:
            RuntimeError: If crystallizer is cleaned/not active, the
                host is unconjured, or a resident member is met without
                skip_resident.
            ValueError: If the record is not a spell_index graft, was
                written by a newer record major, or its selected member
                cannot anchor.
        """
        self.check_cleaned()
        self._require_activated()
        # Lazy import mirrors the loader's runtime-surface import law.
        from melder.crystallizer.crystal_loader_system.graft_runner import (
            GraftRunner,
        )

        runner = GraftRunner(
            graft_record,
            host_spellbook,
            skip_resident=skip_resident,
            merge_into_index=merge_into_index,
            adopt_recorded_selection=adopt_recorded_selection,
        )
        try:
            return runner.run()
        finally:
            runner.cleanup()

    def emit_spell_crystal(self, crystal: SpellCrystal, active: bool = True) -> None:
        """
        Record one custody crystal into the active profile's locations.

        Purpose:
            The bind-seam emission verb: active binds record active;
            staged (bind_inactive) binds record inactive - mirroring the
            spellbook's own active/parked split.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            crystal:
                The custody crystal to record.
            active:
                Which record location receives it (default active).

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.record_spell_crystal(crystal, active=active)
        self._maybe_create_automatic_checkpoint()

    def emit_spell_removed(self, spell_id: str) -> None:
        """
        Evict one removed spell's custody from the record.

        Purpose:
            Called by the spellbook's true-removal seam
            (cleanup_and_remove_spell). Custody leaves both record locations
            so restore never rebuilds a shed spell. The module world is NOT
            touched here: the spell's own cleanup path owns its teardown.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            spell_id:
                The removed spell's SHA256 identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_spell_crystal(spell_id)
        self._maybe_create_automatic_checkpoint()

    def emit_spellbook_removed(self, spellbook_id: str) -> None:
        """
        Evict one dead spellbook's ENTIRE record subtree.

        Purpose:
            Called by Spellbook._cleanup_components at true book death
            (root-conduit teardown and direct cleanup both land there).
            The book twin, its conduit twin(s), and all its spell custody
            leave the record so restore never rebuilds a dead book's world.
            Lesser conduits share the root's book and never trigger this.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            spellbook_id:
                The dead spellbook's identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_spellbook_subtree(spellbook_id)
        self._maybe_create_automatic_checkpoint()

    def create_contract_crystal(self, contract: Contract) -> ContractCrystal:
        """
        Build one relationship twin from a live ward Contract.

        Purpose:
            Project the contract's full truth - both conduit endpoints and
            both sides' spell Details and lineage subscriptions - into
            detached plain data. Callers emit the result so replace-on-emit
            keeps exactly one snapshot per contract.

        Contract:
            - Snapshots under the contract's own lock (consistent view of
              both detail maps).
            - Enum values project as `.name` strings; sources sets project
              as sorted lists; index identities are record-local ULIDs.

        Args:
            contract:
                The live Contract to snapshot.

        Returns:
            ContractCrystal: Detached relationship snapshot.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
        """
        self.check_cleaned()
        self._require_activated()

        def _detail_payload(detail) -> Dict[str, object]:
            return {
                "spell_id": detail.spell_id,
                "index_id": detail.spell_index.id,
                "permissions": detail.permissions.name,
                "contract_type": detail.contract_type.name,
                "reason": detail.reason.name,
                "sources": sorted(detail.sources) if detail.sources else [],
            }

        def _subscription_payload(index_detail) -> Dict[str, object]:
            return {
                "index_id": index_detail.spell_index.id,
                "selected_spell_id": index_detail.selected_spell_id,
                "permissions": index_detail.permissions.name,
                "contract_type": index_detail.contract_type.name,
                "reason": index_detail.reason.name,
                "sources": (
                    sorted(index_detail.sources)
                    if index_detail.sources else []
                ),
            }

        with contract._lock:
            return ContractCrystal(
                contract_id=contract._id,
                conduit_a_id=contract._ward_a._id,
                conduit_b_id=contract._ward_b._id,
                details_a=[
                    _detail_payload(detail)
                    for detail in contract._details_a.values()
                ],
                details_b=[
                    _detail_payload(detail)
                    for detail in contract._details_b.values()
                ],
                index_details_a=[
                    _subscription_payload(entry)
                    for entry in contract._index_details_a.values()
                ],
                index_details_b=[
                    _subscription_payload(entry)
                    for entry in contract._index_details_b.values()
                ],
            )

    def emit_cluster_removed(self, cluster_id: str) -> None:
        """
        Evict one deleted cluster's twin from the record.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            cluster_id:
                The deleted cluster's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_cluster_crystal(cluster_id)
        self._maybe_create_automatic_checkpoint()

    def emit_contract_removed(self, contract_id: str) -> None:
        """
        Evict one severed contract's relationship twin from the record.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            contract_id:
                The severed contract's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_contract_crystal(contract_id)
        self._maybe_create_automatic_checkpoint()

    def create_spell_index_crystal(
            self,
            spell_index: SpellIndex,
            spellbook_id: str,
    ) -> SpellIndexCrystal:
        """
        Build one membership twin from a live SpellIndex.

        Purpose:
            Snapshot the index's grouping truth (owner edge, selection,
            full member set) for the record; callers emit the result so
            replace-on-emit keeps exactly one snapshot per index.

        Args:
            spell_index:
                The live index to snapshot.
            spellbook_id:
                The owning spellbook's identity.

        Returns:
            SpellIndexCrystal: Detached membership snapshot.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
        """
        self.check_cleaned()
        self._require_activated()
        return SpellIndexCrystal(
            index_id=spell_index.id,
            spellbook_id=spellbook_id,
            selected_spell_id=spell_index.selected_spell_id,
            member_spell_ids=list(spell_index._spells_in_index),
        )

    def emit_spell_index_removed(self, index_id: str) -> None:
        """
        Evict one destroyed index's membership twin from the record.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            index_id:
                The destroyed index's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_spell_index_crystal(index_id)
        self._maybe_create_automatic_checkpoint()

    def emit_frame_removed(self, frame_name: str) -> None:
        """
        Evict one dead frame's twin (+ leftover book subtrees).

        Purpose:
            Called by AethericFrame.cleanup after its teardown cascade: the
            frame genuinely leaves the live world (Aether detaches it), so
            its twin leaves the record. Books normally evicted themselves
            during the cascade; the profile's by-frame net covers the rest.

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            frame_name:
                The dead frame's canonical name.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_frame_crystal(frame_name)
        self._maybe_create_automatic_checkpoint()

    def emit_nexus_state(self, state: RecordedUnitState) -> None:
        """
        Record a Nexus lifecycle flip (enabled / disabled / cleaned).

        Purpose:
            Nexus disable keeps its installed configuration, so the twin is
            RETAINED and this switch carries the truth (owner model:
            state-switch, not eviction, for MR/Nexus; Aether/Crystallizer
            are skipped - the record dies with them).

        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            state:
                The new recorded state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.record_nexus_state(state)
        self._maybe_create_automatic_checkpoint()

    def emit_mutation_research_state(self, state: RecordedUnitState) -> None:
        """
        Record a MutationResearch lifecycle flip (enabled/disabled/cleaned).

        Contract:
            - NO-OP while the crystallizer is not activated.
            - Twin retained; the switch is the recorded truth (see
              emit_nexus_state).

        Args:
            state:
                The new recorded state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.record_mutation_research_state(state)
        self._maybe_create_automatic_checkpoint()

    def emit_spell_activity(self, spell_id: str, active: bool) -> None:
        """
        Mirror one runtime park/promote flip into the record and, when
        configured, into the live module world.

        Purpose:
            Called by the spellbook's park/promote seams. The record flip
            is unconditional (crystal moves between active/inactive
            locations). The module-world reaction is knob-gated:
            - promote (active=True): the spell's synthetic root module is
              re-published if it is registered (self-healing; a no-op when
              it never left `sys.modules`).
            - park (active=False): when `remove_inactive_synthmodules` is
              True, the synthetic root module is UNPUBLISHED (depth-2:
              reversible; registry + custody retained; captured references
              survive as ghosts per the hot-swap law).
            Physical-authority spells never touch the module world here.

        Contract:
            - NO-OP while the crystallizer is not activated.
            - Tolerates missing custody (activity for a spell the record
              never held is journaled without a crystal move).

        Args:
            spell_id:
                The spell whose activity flipped.
            active:
                True = promoted to active; False = parked inactive.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.record_spell_activity(spell_id, active=active)
        self._maybe_create_automatic_checkpoint()
        try:
            crystal = self._persistence_system.get_spell_crystal(spell_id)
        except KeyError:
            return
        if crystal.root_module_kind != "synthetic_module":
            return
        module_name = crystal.root_module_name
        with SyntheticModule._registry_lock:
            module = SyntheticModule._registered_modules_by_name.get(module_name)
        if module is None or module.cleaned:
            return
        if active:
            module.publish_to_sys_modules()
        elif self._configuration.remove_inactive_synthmodules:
            # R11 (patch persistence_loop_load_order_r11_2026_07_12):
            # reverse-edge-aware unseed - a parked module with LIVE
            # synthetic dependents stays resident; unpublishing it would
            # strand their next lazy/deferred import mid-flight. The
            # registry is the checkable live surface (physical importers
            # cannot be enumerated at runtime; their edges are recorded
            # at analysis time and governed by the hot-swap law).
            if SyntheticModule.has_live_synthetic_dependents(module_name):
                self._logger.info(
                    "Park kept module '{0}' resident: live synthetic "
                    "dependents exist (R11 reverse-edge law).".format(
                        module_name,
                    ),
                    "record_spell_activity",
                )
            else:
                module.unpublish_from_sys_modules()

    def emit(self, twin: Cleanable) -> None:
        """
        Record one emitted twin into the active persistence profile.

        Purpose:
            The single sink entry of the EMIT model: structural units push
            their twins here at configuration lock-in and at the pivotal
            runtime points; the crystallizer passively records into the
            ACTIVE profile. The sink never reaches into emitters.

        Contract:
            - NO-OP while the crystallizer is not activated: hosts may call
              unconditionally without behavioral impact on non-recorded
              worlds (call-sites still pre-gate to avoid building payloads).
            - Twin-type validation is owned by the profile record path.

        Args:
            twin:
                One twin from the persistence crystal family.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
            TypeError:
                If the twin type is unsupported (raised by the profile).
        """
        self.check_cleaned()
        if not self._activated:
            return
        # Opt-in emission tap (external_mesh 2026-07-12, owner ruling):
        # every recorded twin streams as a delta row through the user's
        # generic store handler. THREAD SAFETY: the payload is captured
        # BEFORE record() - once recorded, replace-on-emit means a
        # concurrent same-kind emit may clean THIS twin, and a
        # post-record describe() would race that cleanup. Shipping still
        # happens AFTER the record lands (local truth leads the mirror);
        # the lane is lenient + counted, so a dying DB never touches the
        # R-A covenant. Untapped worlds pay one property read.
        tap_enabled = self._asset_management_system.emission_tap_enabled
        if tap_enabled:
            tap_kind = type(twin).__name__
            tap_payload = twin.describe()
        self._persistence_system.record(twin)
        if tap_enabled:
            self._asset_management_system.stream_emission(
                self._persistence_system.active_profile_name,
                tap_kind,
                tap_payload,
            )
        self._maybe_create_automatic_checkpoint()

    def create_spell_crystal(
            self,
            spell: Spell,
            spellbook_id: Optional[str] = None,
    ) -> SpellCrystal:
        """
        Build one `SpellCrystal` using the installed crystallizer policy.

        Purpose:
            Capture one live spell's bind identity and module-world analysis
            into the carrier used by persistence and restore.

        Contract:
            `SpellCrystal` invokes a single-use `CrystalAnalyzer`, retains
            only its value-only `CrystalAnalysisResult`, and never owns the
            analyzer or strategy machinery. User-source text is retained only
            when the installed policy enables it; bind-time fingerprints are
            recorded independently of that opt-in.

        Args:
            spell:
                Live spell whose module world should be crystallized.
            spellbook_id:
                Optional owning-spellbook identity recorded on the crystal
                as its parent edge inside a persistence profile.

        Returns:
            SpellCrystal: Loader-facing manifest for the given spell.

        Raises:
            RuntimeError:
                If crystallizer is not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return SpellCrystal(
            spell,
            user_source_root_paths=self._configuration.user_source_root_paths,
            spellbook_id=spellbook_id,
            retain_user_sources=self._configuration.retain_user_sources,
            site_package_dependency_descent=(
                self._configuration.site_package_dependency_descent
            ),
        )


    @property
    def active_profile_name(self) -> str:
        """
        Return the name of the persistence profile emissions currently target.

        Returns:
            str:
                Active profile name ("default" unless switched).

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.active_profile_name

    def create_profile(self, profile_name: str, activate: bool = True) -> None:
        """
        Create one new persistence profile and (by default) switch to it.

        Purpose:
            Facade over the buried persistence model: users and agents create
            worlds by name only; PersistenceProfile objects never escape the
            depths.

        Args:
            profile_name:
                New profile name; must not collide with an existing profile.
            activate:
                When True (default), the new profile becomes the emission
                target immediately (owner model: create and default to it).

        Returns:
            None.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            ValueError:
                If `profile_name` is empty or already exists.
        """
        self.check_cleaned()
        self._require_activated()
        self._persistence_system.create_profile(profile_name, activate=activate)

    def set_active_profile(self, profile_name: str) -> None:
        """
        Switch the emission target to one existing persistence profile.

        Args:
            profile_name:
                Name of an existing profile to activate.

        Returns:
            None.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        self._require_activated()
        self._persistence_system.set_active_profile(profile_name)

    def describe_profile(self, profile_name: Optional[str] = None) -> Dict[str, object]:
        """
        Return a detached structural summary of one persistence profile.

        Args:
            profile_name:
                Profile to describe; None means the active profile.

        Returns:
            Dict[str, object]:
                Profile summary (name, per-level twin counts, emission
                sequence).

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If `profile_name` names no existing profile.
        """
        self.check_cleaned()
        self._require_activated()
        if profile_name is None:
            return self._persistence_system.active_profile.describe()
        return self._persistence_system.get_profile(profile_name).describe()

    def list_profile_names(self) -> List[str]:
        """
        Return the names of all persistence profiles.

        Returns:
            List[str]:
                Sorted, detached profile-name list.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.list_profile_names()

    def clear_profile(self, profile_name: str) -> None:
        """
        Reset one persistence profile's recorded content to empty.

        Purpose:
            The generalized clear_bootstrap: clearing "default" resets the
            default bootstrap record.

        Args:
            profile_name:
                Name of an existing profile to clear.

        Returns:
            None.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        self._require_activated()
        self._persistence_system.clear_profile(profile_name)

    def delete_profile(self, profile_name: str) -> None:
        """
        Delete one NAMED persistence profile ("default" is never deletable).

        Args:
            profile_name:
                Name of the named profile to delete.

        Returns:
            None.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            ValueError:
                If asked to delete the default profile.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        self._require_activated()
        self._persistence_system.delete_profile(profile_name)

    def create_checkpoint(
            self,
            profile_name: Optional[str] = None,
            description: Optional[str] = None,
    ) -> str:
        """
        Snapshot one persistence profile and return the checkpoint's ULID id.

        Contract:
            - Checkpoint ids are ULIDs, while exact chronology comes from
              the ledger's insertion order (including same-millisecond seals).
            - The crystallizer policy twin is emitted into the window before
              sealing, so every checkpoint identifies the policy that made it.
            - `PersistenceSystem` captures the current incremental window as
              value-only twin custody and advances that profile's journal mark.
            - Sealing updates the in-process ledger only. Use
              `flush_checkpoint()` to ship the sealed artifact to local cache
              and the optional external mesh.

        Args:
            profile_name:
                Profile to checkpoint; None means the active profile.
            description:
                Optional caller note stored on the checkpoint record.

        Returns:
            str:
                The new checkpoint's ULID id.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If `profile_name` names no existing profile.
        """
        self.check_cleaned()
        self._require_activated()
        # Every snapshot is self-describing: the policy twin re-emits into
        # this seal's window (owner ruling), so a single cached crystal
        # carries the recording policy that made it.
        self._emit_policy_twin(profile_name)
        return self._persistence_system.create_checkpoint(
            profile_name=profile_name,
            description=description,
        )

    def describe_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Return a detached copy of one checkpoint's metadata record.

        Args:
            checkpoint_id:
                ULID identity returned by `create_checkpoint`.

        Returns:
            Dict[str, object]:
                Detached checkpoint record.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.describe_checkpoint(checkpoint_id)

    def list_checkpoint_ids(self) -> List[str]:
        """
        Return all checkpoint ids in exact ledger creation order.

        Returns:
            List[str]:
                Chronologically sorted, detached checkpoint-id list.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.list_checkpoint_ids()

    def describe_record(self) -> Dict[str, object]:
        """
        Return the whole record's one-shot operational summary
        (profiles + twin counts + ledger + cache, in one call).

        Returns:
            Dict[str, object]:
                The persistence system's describe() payload, enriched
                with the asset system's cached checkpoint count (disk
                truth moved custody in S3; the facade payload stays
                complete).

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
        """
        self.check_cleaned()
        self._require_activated()
        record_description = self._persistence_system.describe()
        record_description["cached_checkpoint_count"] = len(
            self._asset_management_system.list_cached_checkpoint_ids()
        )
        return record_description

    def checkpoint_replay_data(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Return one checkpoint's detached replay inputs (journal window +
        captured payloads) - the restore engine's read surface.

        Args:
            checkpoint_id:
                ULID identity returned by `create_checkpoint`.

        Returns:
            Dict[str, object]:
                {"journal": [[sequence, kind, key], ...],
                 "payloads": {kind: {key: payload}}}.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.checkpoint_replay_data(checkpoint_id)

    def flush_checkpoint(self, checkpoint_id: Optional[str] = None) -> List[str]:
        """
        Flush sealed checkpoint(s) into the local crystallizer cache.

        Args:
            checkpoint_id:
                One ledger ULID, or None to flush the whole ledger.

        Returns:
            List[str]:
                The flushed checkpoint ids.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
            KeyError:
                If `checkpoint_id` names no ledger crystal.
        """
        self.check_cleaned()
        self._require_activated()
        # Seal-then-ship: the asset system pulls feedstock from the
        # record, writes the cache, FIFO-caps it, and runs the lenient
        # remote upload leg when a manager is attached - one verb, both
        # legs (S3 decomposition absorbed the old upload hook).
        return self._asset_management_system.flush_checkpoint(checkpoint_id)

    def reload_cached_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Reload one cached checkpoint back into the ledger (history
        recovery; world restore remains `load_checkpoint`).

        Args:
            checkpoint_id:
                ULID of a previously flushed checkpoint.

        Returns:
            Dict[str, object]:
                The (re)loaded checkpoint's describe() summary.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
            KeyError:
                If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.reload_checkpoint_from_cache(
            checkpoint_id
        )

    def list_cached_checkpoint_ids(self) -> List[str]:
        """
        Return every checkpoint id present in the local cache.

        Returns:
            List[str]:
                Sorted cached checkpoint ids.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.list_cached_checkpoint_ids()

    def verify_checkpoint_chain(
            self,
            profile_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Report one profile's checkpoint-chain fold-safety (read-only).

        Purpose:
            Answer BEFORE a restore whether the retained chain is safe to
            fold: "intact", "truncated_prefix" (head history dropped), or
            "broken" (number/window damage with evidence rows).

        Args:
            profile_name:
                Profile to audit; None means the active profile.

        Returns:
            Dict[str, object]:
                The detached chain-integrity report.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If `profile_name` names no existing profile.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.verify_checkpoint_chain(profile_name)

    def reload_profile_from_cache(
            self,
            profile_name: str,
    ) -> Dict[str, object]:
        """
        Reload EVERY cached checkpoint of one profile into the ledger.

        Purpose:
            Facade over PersistenceSystem.reload_profile_from_cache: a
            profile's cache folder IS its portable form - copy the
            folder, reload it here, then load_checkpoint unfolds the
            chain.

        Args:
            profile_name:
                Profile whose cached checkpoints should reload.

        Returns:
            Dict[str, object]:
                {"profile_name", "inserted", "skipped_existing"}.

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active.
            KeyError: If the profile has no cached checkpoints.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.reload_profile_from_cache(
            profile_name
        )

    def save_formation(
            self,
            formation_name: str,
            conduit_id: Optional[str] = None,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            description: str = "",
    ) -> str:
        """
        Capture and store one user-named formation.

        Purpose:
            Facade over PersistenceSystem.save_formation: keep a conduit
            formation you like (its spellbook rides along) or a whole
            frame subtree, under your own name, durable in the cache.

        Args:
            formation_name:
                The user's filesystem-safe name.
            conduit_id:
                Conduit-scope anchor (exactly one scope required).
            frame_name:
                Frame-scope anchor.
            profile_name:
                Profile to capture from; None means the active profile.
            description:
                Optional user note.

        Returns:
            str: Absolute path of the stored formation file.

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active.
            ValueError/KeyError: Per the system verb's contract.
        """
        self.check_cleaned()
        self._require_activated()
        # Record side captures + assembles; asset side persists the file.
        formation_record = self._persistence_system.capture_formation_record(
            formation_name,
            conduit_id=conduit_id,
            frame_name=frame_name,
            profile_name=profile_name,
            description=description,
        )
        return self._asset_management_system.store_formation(formation_record)

    def restore_formation(
            self,
            formation_name: str,
            profile_name: Optional[str] = None,
            target_frame_name: Optional[str] = None,
            skip_existing: bool = False,
    ) -> Dict[str, object]:
        """
        Rebuild one stored formation directly (scoped restore).

        Purpose:
            Facade over PersistenceSystem.restore_formation: reload JUST
            the formation - not the world - with the engine's normal
            all-or-nothing and shortfall semantics. S1 load-scope
            maturity: formations COMPOSE into live worlds - optionally
            retargeted onto another frame, optionally skipping host name
            collisions instead of refusing on them.

        Args:
            formation_name:
                The stored formation's name.
            profile_name:
                Profile whose formation store is read; None = active.
            target_frame_name:
                Optional frame the formation should compose into instead
                of its recorded frame (the rewrite happens in the
                detached window; the stored record is never mutated).
            skip_existing:
                When True, host name-collision blockers downgrade to
                "skipped_existing" in the admission view and the engine
                runs its skip lanes (a taken conduit name builds unnamed
                with a shortfall; an existing cluster is reused and
                recorded members join it).

        Returns:
            Dict[str, object]: The detached restore report (+ "admission"
                view carrying the additive "host" findings key).

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active,
                admission refused the load (host-collision or preflight
                blockers), or the replay failed (torn down; cause
                chained).
            KeyError: If the formation does not exist.
            ValueError: If a retarget hits a multi-frame window or an
                invalid target name.
        """
        self.check_cleaned()
        self._require_activated()
        # Asset side loads the stored record; the loader side mints the
        # scoped plan and runs the gated engine (S4 - the ledger never
        # replays anything anymore).
        formation_record = self._asset_management_system.load_formation_record(
            formation_name, profile_name=profile_name
        )
        return self._crystal_loader_system.restore_formation_record(
            formation_record,
            target_frame_name=target_frame_name,
            skip_existing=skip_existing,
        )

    def list_formations(
            self,
            profile_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return the targeted profile's stored formation names.

        Args:
            profile_name:
                Profile to list; None means the active profile.

        Returns:
            List[str]: Sorted formation names.

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.list_formations(profile_name)

    def analyze_formation(
            self,
            formation_name: str,
            profile_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Pre-flight one stored formation's bootload viability.

        Purpose:
            Run the complete default `PersistenceAnalyzer` strategy set over
            the stored formation before the user trusts a restore. The set
            covers topology, hydration, configuration, frame/cluster posture,
            synthetic and retained-source integrity, mutation-research
            composition, and live source drift.

        Contract:
            Analysis is read-only over the stored payload bundle. It does not
            execute admission, claim the LoadGate, or replay any runtime unit.

        Args:
            formation_name:
                The stored formation's name.
            profile_name:
                Profile whose formation store is read; None = active.

        Returns:
            Dict[str, object]:
                {"findings", "counts", "verdict"} analyzer report.

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active.
            KeyError: If the formation does not exist.
        """
        self.check_cleaned()
        self._require_activated()
        from melder.crystallizer.crystal_analysis.preflight.persistence_analyzer import (
            PersistenceAnalyzer,
        )

        formation_record = (
            self._asset_management_system.load_formation_record(
                formation_name, profile_name=profile_name
            )
        )
        analyzer = PersistenceAnalyzer()
        try:
            return analyzer.analyze(dict(formation_record["payloads"]))
        finally:
            analyzer.cleanup()

    def analyze_checkpoint(
            self,
            checkpoint_id: str,
    ) -> Dict[str, object]:
        """
        Pre-flight one sealed checkpoint's bootload viability.

        Purpose:
            Run the complete default `PersistenceAnalyzer` strategy set over
            this checkpoint's captured window.

        Contract:
            This method analyzes the named checkpoint window only; it does not
            fold the target's complete profile chain and does not replay any
            runtime unit. `load_checkpoint()` owns chain detachment, folded
            preflight, blocker refusal, and execution.

        Args:
            checkpoint_id:
                One ledger checkpoint's ULID.

        Returns:
            Dict[str, object]:
                {"findings", "counts", "verdict"} analyzer report.

        Raises:
            RuntimeError: If crystallizer is cleaned or not yet active.
            KeyError: If no checkpoint exists under the id.
        """
        self.check_cleaned()
        self._require_activated()
        from melder.crystallizer.crystal_analysis.preflight.persistence_analyzer import (
            PersistenceAnalyzer,
        )

        cached_item = self._persistence_system.cached_item_form(
            checkpoint_id
        )
        analyzer = PersistenceAnalyzer()
        try:
            return analyzer.analyze(
                dict(cached_item.get("captured_payloads", {}))
            )
        finally:
            analyzer.cleanup()

    def configure_external_persistence_manager(
            self,
            manager_configuration: ExternalPersistenceManagerConfiguration,
    ) -> None:
        """
        Attach an external transport at the configuration step.

        Purpose:
            Attach optional durability beyond the built-in local cache. An
            integration may register generic mesh callables or use a provider
            such as `SqliteMeshAdapter`; this verb builds the asset-owned manager
            while credentials, connection policy, and remote-store operation
            remain application responsibilities.

        Guidance:
            Prefer the generic store/fetch/list/delete handlers for new code
            because they carry checkpoints, formations, grafts, and emission
            events. The legacy upload/download/list trio remains supported for
            checkpoint-only integrations.

        Contract:
            - Freezes the configuration if the caller has not (load it
              in, freeze it - the reload-lane law).
            - Re-configuring replaces the previous manager (the old one
              cleans); attach BEFORE relying on upload-on-flush.

        Args:
            manager_configuration:
                The handler-bearing configuration (ownership transfers
                to the built manager).

        Returns:
            None.

        Raises:
            RuntimeError: If the crystallizer has been cleaned.
            TypeError/ValueError: Propagated from the manager's
                construction contract.
        """
        self.check_cleaned()
        # Custody moved (S3): the asset system owns the manager; freeze +
        # replace-and-clean semantics live on its verb.
        self._asset_management_system.configure_external_persistence_manager(
            manager_configuration
        )

    def describe_external_persistence_manager(self) -> Dict[str, object]:
        """
        Return the attached manager's record-safe presence description.

        Returns:
            Dict[str, object]:
                Presence flags + knobs + failure diagnostics; an
                {"attached": False} stub when no manager is configured.

        Raises:
            RuntimeError: If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        return (
            self._asset_management_system
            .describe_external_persistence_manager()
        )

    def reload_profile_from_external(
            self,
            profile_name: str,
    ) -> Dict[str, object]:
        """
        Download and insert EVERY remote checkpoint of one profile.

        Purpose:
            The remote import lane: the manager downloads the profile's
            stored cached items (list + per-id download through the
            user's callables) and the persistence system inserts them
            insert-if-absent - then load_checkpoint unfolds as usual.

        Args:
            profile_name:
                Profile whose remote history should reload.

        Returns:
            Dict[str, object]:
                {"profile_name", "inserted", "skipped_existing"}.

        Raises:
            RuntimeError: If cleaned, not yet active, no manager is
                attached, or download/list handlers are missing.
            ValueError: If the remote lists an id it cannot return.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.reload_profile_from_external(
            profile_name
        )

    def reload_formations_from_external(
            self,
            profile_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Download and store EVERY remote formation of one profile.

        Purpose:
            The formation half of the remote import lane (external_mesh
            2026-07-12): the manager lists + fetches through the user's
            generic callables, the local formation store inserts-if-
            absent, and restore_formation reads them as usual afterwards.

        Args:
            profile_name:
                Profile whose remote formations reload; None = active.

        Returns:
            Dict[str, object]:
                {"profile_name", "inserted", "skipped_existing"}.

        Raises:
            RuntimeError: If cleaned, not yet active, no manager is
                attached, or the generic fetch/list lanes are missing.
            ValueError: If the remote lists a formation it cannot return.
        """
        self.check_cleaned()
        self._require_activated()
        resolved = (
            profile_name
            if profile_name is not None
            else self._persistence_system.active_profile_name
        )
        return self._asset_management_system.reload_formations_from_external(
            resolved
        )

    def apply_external_retention(
            self,
            profile_name: Optional[str] = None,
            max_checkpoints: Optional[int] = None,
    ) -> List[str]:
        """
        Trim the remote checkpoint history to one retention cap.

        Purpose:
            Melder-driven remote retention (owner ruling 2026-07-12,
            opt-in via the delete handler): mirrors the local FIFO - the
            newest `max_checkpoints` survive, everything older deletes
            through the user's callable.

        Args:
            profile_name:
                Profile to trim; None = active.
            max_checkpoints:
                Survivor cap; None = the crystallizer configuration's
                max_persistence_crystals (the same knob the local FIFO
                honors).

        Returns:
            List[str]: The deleted checkpoint ids, oldest first.

        Raises:
            RuntimeError: If cleaned, not yet active, no manager is
                attached, or the list-units/delete lanes are missing.
            ValueError: If the resolved cap is not a positive int.
        """
        self.check_cleaned()
        self._require_activated()
        resolved_profile = (
            profile_name
            if profile_name is not None
            else self._persistence_system.active_profile_name
        )
        resolved_cap = (
            max_checkpoints
            if max_checkpoints is not None
            else self._configuration.max_persistence_crystals
        )
        return self._asset_management_system.apply_external_retention(
            resolved_profile, resolved_cap
        )

    def delete_cached_checkpoint(self, checkpoint_id: str) -> str:
        """
        Evict one checkpoint cached-item from the local cache by id.

        Purpose:
            Facade of the asset system's single-item delete (asset CRUD
            completion, 2026-07-11): the FIFO cap trims by age; this
            removes one specific cached snapshot.

        Args:
            checkpoint_id:
                ULID identity of a previously flushed checkpoint.

        Returns:
            str: The deleted file's path.

        Raises:
            RuntimeError: If cleaned or not yet active.
            KeyError: If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.delete_cached_checkpoint(
            checkpoint_id
        )

    def delete_formation(
            self,
            formation_name: str,
            profile_name: Optional[str] = None,
            include_remote: bool = False,
    ) -> Dict[str, object]:
        """
        Delete one stored formation locally and, optionally, remotely.

        Args:
            formation_name:
                The user-chosen formation name to delete.
            profile_name:
                Owning profile; None = the active profile.
            include_remote:
                When True, also delete the remote copy (STRICT leg via
                the user's delete handler).

        Returns:
            Dict[str, object]: {"deleted_local_path", "remote_deleted"}.

        Raises:
            RuntimeError: If cleaned, not active, or include_remote is
                set without a manager/delete lane.
            KeyError: If the local formation file does not exist.
        """
        self.check_cleaned()
        self._require_activated()
        resolved_profile = (
            profile_name
            if profile_name is not None
            else self._persistence_system.active_profile_name
        )
        return self._asset_management_system.delete_formation(
            resolved_profile, formation_name, include_remote
        )

    def store_index_graft_external(
            self,
            graft_record: Dict[str, object],
            profile_name: Optional[str] = None,
    ) -> str:
        """
        Ship one captured spell-index graft through the generic mesh.

        Purpose:
            First-class graft lane (asset CRUD completion): the record
            ships under kind "index_graft" keyed by its own index_id, so
            capture -> store -> fetch -> graft_index round-trips without
            the user naming a kind.

        Args:
            graft_record:
                The dict from capture_index_graft(...), unmodified.
            profile_name:
                Recording profile; None = the active profile.

        Returns:
            str: The unit id the record shipped under (its index_id).

        Raises:
            RuntimeError: If cleaned, not active, or no store lane.
            ValueError: If the record carries no "index_id".
        """
        self.check_cleaned()
        self._require_activated()
        resolved_profile = (
            profile_name
            if profile_name is not None
            else self._persistence_system.active_profile_name
        )
        return self._asset_management_system.store_index_graft(
            resolved_profile, graft_record
        )

    def fetch_index_graft_external(
            self,
            index_id: str,
    ) -> Dict[str, object]:
        """
        Fetch one graft record back from the user's store, version-gated.

        Args:
            index_id:
                The captured index id the graft shipped under.

        Returns:
            Dict[str, object]: The graft record, ready for graft_index.

        Raises:
            RuntimeError: If cleaned, not active, or no fetch lane.
            ValueError: If the record's version MAJOR is newer than this
                melder reads (the reader-gate law).
            KeyError: If the remote store has no such graft.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.fetch_index_graft(index_id)

    def list_index_grafts_external(
            self,
            profile_name: Optional[str] = None,
    ) -> List[str]:
        """
        List one profile's stored graft ids through the generic lane.

        Args:
            profile_name:
                Profile to list; None = the active profile.

        Returns:
            List[str]: Unit ids (captured index ids) the store reports.

        Raises:
            RuntimeError: If cleaned, not active, or no list lane.
        """
        self.check_cleaned()
        self._require_activated()
        resolved_profile = (
            profile_name
            if profile_name is not None
            else self._persistence_system.active_profile_name
        )
        return self._asset_management_system.list_index_grafts(
            resolved_profile
        )

    def describe_external_interface(self) -> Dict[str, object]:
        """
        Emit the mesh interface contract joined with live presence.

        Purpose:
            The owner's "emit the table and the shape" verb: the static
            kind/shape/signature table (MeshInterfaceContract) plus this
            world's live handler presence, so users build storage and
            register callables from the emitted contract alone.

        Returns:
            Dict[str, object]: The stamped contract dict plus
            "live_manager" (the attached manager's presence flags, or
            None when nothing is attached).

        Raises:
            RuntimeError: If cleaned or not yet active.
        """
        self.check_cleaned()
        self._require_activated()
        return self._asset_management_system.describe_external_interface()

    # NOTE (S3 decomposition): the upload hook
    # (_upload_flushed_checkpoints) was absorbed into
    # AssetManagementSystem.flush_checkpoint - one feedstock pull now
    # serves both the cache write and the remote upload leg.

    def load_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Unfold one checkpoint's world into the live runtime (boot verb).

        Purpose:
            Public seat of the restore engine: folds the target's profile
            chain and replays it through the public runtime verbs in canon
            order (all-or-nothing; shortfalls reported, never silently
            under-built).

        Contract:
            The owned loader builds a world-scoped `LoadPlan`, claims
            Aether's load authority for the replay span, refuses blocker
            verdicts before activation, and always releases authority.
            Successful payloads include the additive, detached `admission`
            view alongside the restore report.

        Args:
            checkpoint_id:
                ULID identity of the checkpoint to load.

        Returns:
            Dict[str, object]:
                The detached RestoreReport payload (status, built counts,
                shortfall entries, identity translation map).

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active, or a replay
                stage failed (after teardown; original error chained).
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        self._require_activated()
        # S4: every load runs the loader's mediated admission pipeline
        # (plan -> gated engine -> adjudicated payload; blockers refuse
        # before any replay). Payload gains the additive "admission" key.
        return self._crystal_loader_system.load_checkpoint(checkpoint_id)

    def _require_configured(self) -> None:
        """
        Require that a configuration has been installed.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no configuration is installed.
        """
        self.check_cleaned()
        if not self._configured or self._configuration is None:
            raise RuntimeError("Crystallizer is not configured.")

    def _require_activated(self) -> None:
        """
        Require that crystallizer is active.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the root is not activated.
        """
        self.check_cleaned()
        if not self._activated:
            raise RuntimeError("Crystallizer is not activated.")
