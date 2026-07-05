import threading
import time
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.aether.spellbook.spell import Spell

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.persistence.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.synthetic_module import SyntheticModule
from melder.crystallizer.persistence.persistence_system import PersistenceSystem
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
            self._last_automatic_checkpoint_monotonic = time.monotonic()
        self._catch_up_live_world()

    def _catch_up_live_world(self) -> None:
        """
        Internal

        Sweep the already-live world into the record after activation.

        Purpose:
            A crystallizer activated mid-flight (after frames/spellbooks/
            binds exist) walks the live world and emits custody for every
            bound spell in dynamic-posture spellbooks - active and parked -
            so the record starts truthful instead of empty. Replace-on-emit
            makes re-activation sweeps idempotent.

        Contract:
            - Dynamic-posture spellbooks only (the recorded lane).
            - Custody only: configuration twins re-emit at their own
              activation points, not here.

        Returns:
            None.
        """
        aether = self._aether
        if aether is None:
            return
        for frame in list(aether._aetheric_frames.values()):
            for conduit in list(frame._conduits.values()):
                spellbook = conduit._spellbook
                if spellbook.cleaned or not spellbook._is_dynamic_posture():
                    continue
                for bound_spell in list(spellbook._spells.values()):
                    self.emit_spell_crystal(
                        self.create_spell_crystal(
                            bound_spell, spellbook_id=spellbook._id
                        ),
                        active=True,
                    )
                for parked_spell in list(spellbook._inactive_spells.values()):
                    self.emit_spell_crystal(
                        self.create_spell_crystal(
                            parked_spell, spellbook_id=spellbook._id
                        ),
                        active=False,
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
        self._persistence_system.create_checkpoint(
            description="automatic cadence checkpoint",
        )

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
            - Tolerates missing custody (record-only worlds before the
              catch-up walk exists).

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

    def load_checkpoint(self, checkpoint_id: str) -> None:
        """
        Load one checkpoint back toward the live system (restore input).

        Args:
            checkpoint_id:
                ULID identity of the checkpoint to load.

        Returns:
            None.

        Raises:
            RuntimeError:
                If crystallizer is cleaned or not yet active.
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
            NotImplementedError:
                Placeholder until the restore engine lands (bootstrap epic).
        """
        self.check_cleaned()
        self._require_activated()
        self._persistence_system.load_checkpoint(checkpoint_id)

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
