import threading
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.aether.spellbook.spell import Spell

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.persistence.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
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
        "_persistence_crystal",
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
            self._persistence_crystal: PersistenceCrystal = PersistenceCrystal()

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
            if self._persistence_crystal is not None and not self._persistence_crystal.cleaned:
                self._persistence_crystal.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False

            del self._persistence_crystal
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

    def deactivate(self) -> None:
        """
        Deactivate the crystallizer root without dropping configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._activated = False

    def create_spell_crystal(self, spell: Spell) -> SpellCrystal:
        """
        Build one `SpellCrystal` using the installed crystallizer policy.

        Args:
            spell:
                Live spell whose module world should be crystallized.

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
        return self._persistence_crystal.active_profile_name

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
        self._persistence_crystal.create_profile(profile_name, activate=activate)

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
        self._persistence_crystal.set_active_profile(profile_name)

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
            return self._persistence_crystal.active_profile.describe()
        return self._persistence_crystal.get_profile(profile_name).describe()

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
        return self._persistence_crystal.list_profile_names()

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
        self._persistence_crystal.clear_profile(profile_name)

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
        self._persistence_crystal.delete_profile(profile_name)

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
        return self._persistence_crystal.create_checkpoint(
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
        return self._persistence_crystal.describe_checkpoint(checkpoint_id)

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
        return self._persistence_crystal.list_checkpoint_ids()

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
        self._persistence_crystal.load_checkpoint(checkpoint_id)

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
