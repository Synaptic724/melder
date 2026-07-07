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
from melder.crystallizer.persistence.crystals.crystallizer_crystal import (
    CrystallizerCrystal,
)
from melder.crystallizer.persistence.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.synthetic_module import SyntheticModule
from melder.crystallizer.persistence.persistence_system import PersistenceSystem
from melder.crystallizer.persistence.crystals.contract_crystal import (
    ContractCrystal,
)
from melder.crystallizer.persistence.crystals.spell_index_crystal import (
    SpellIndexCrystal,
)
from melder.crystallizer.persistence.recorded_unit_state import RecordedUnitState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

class Crystallizer(Cleanable):
    """
    Singleton policy and activation root for crystallizer behavior.

    Purpose:
        Provide the first real ownership root above `SpellCrystal` and
        `SyntheticModule`. The crystallizer owns:
        - installed configuration
        - configured/activated state
        - the policy inputs used for crystal construction

    Contract:
        - process-wide singleton
        - hosted by `Aether` in the same private-root posture as `Nexus`
        - configuration is explicit
        - activation is explicit and starts disabled by default
        - lower-level crystallizer objects do not own config policy directly
    """

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
        Idempotently clear crystallizer state and reset singleton bookkeeping.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._persistence_system is not None and not self._persistence_system.cleaned:
                self._persistence_system.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False

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

    def _emit_policy_twin(self) -> None:
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
            CrystallizerCrystal(configuration_payload=configuration_payload)
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
            # immediately (one atomic JSON write per interval).
            self._persistence_system.flush_checkpoint_to_cache(sealed_id)

    def deactivate(self) -> None:
        """
        Deactivate the crystallizer root without dropping configuration.

        Returns:
            None.
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
        self._persistence_system.record(twin)
        self._maybe_create_automatic_checkpoint()

    def create_spell_crystal(
            self,
            spell: Spell,
            spellbook_id: Optional[str] = None,
    ) -> SpellCrystal:
        """
        Build one `SpellCrystal` using the installed crystallizer policy.

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
            - Checkpoint ids are ULIDs: they sort by creation time, so id
              order IS checkpoint chronology.
            - CURRENT DEPTH: metadata registration only (the record carries
              `"twin_custody": "pending"`); the twin seal-copy + cache/save
              land with the bootstrap and persistence epics.

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
        self._emit_policy_twin()
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
        Return all checkpoint ids in creation order (ULID = time order).

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
                The persistence system's describe() payload.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned or is not activated.
        """
        self.check_cleaned()
        self._require_activated()
        return self._persistence_system.describe()

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
        return self._persistence_system.flush_checkpoint_to_cache(
            checkpoint_id
        )

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
        return self._persistence_system.reload_checkpoint_from_cache(
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
        return self._persistence_system.list_cached_checkpoint_ids()

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
        return self._persistence_system.reload_profile_from_cache(
            profile_name
        )

    def load_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Unfold one checkpoint's world into the live runtime (boot verb).

        Purpose:
            Public seat of the restore engine: folds the target's profile
            chain and replays it through the public runtime verbs in canon
            order (all-or-nothing; shortfalls reported, never silently
            under-built).

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
        return self._persistence_system.load_checkpoint(checkpoint_id)

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
