import threading
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from melder.nexus.nexus import Nexus
    from melder.aether.aether import Aether
    from melder.aether.spellbook.spell import Spell

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.spell_crystal import SpellCrystal
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
            if self._configuration is not None:
                self._configuration.cleanup()
            self._configured = False
            self._activated = False

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
