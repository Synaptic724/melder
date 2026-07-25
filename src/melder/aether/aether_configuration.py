import logging
import threading
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.aether_crystal import AetherCrystal
from melder.utilities.helpers.id_builder import IDBuilder


class AetherConfiguration(Cleanable):
    """
    Mutable-to-frozen configuration surface for Aether root policy.

    Purpose:
        Hold process-wide Aether policy inputs before the root applies them to
        hosted subsystems. The current owned policy slice is logger activation
        control for `AetherUtilitySystem`.

    Contract:
        - mutable until frozen
        - activation is explicit and implies successful validation/freeze
        - automatic channel logger activation is disabled by default
        - explicit logger attachment remains outside this config surface

    Note:
        System caching policy is owned by `AethericFrameConfiguration`
        (frame-level toggle plus the cache root path), not by this root config.

    Registration:
        MELDER KERNEL - guarded. Obtained through
        `Aether.create_configuration()`.

    Subsystem Context:
        The root policy surface, following the same mutable-then-frozen shape as
        the Spellbook, crystallizer, mutation-research, and Nexus configurations
        - so an agent that has learned one configuration lane can drive all of
        them.

    System Context:
        Its scope is deliberately NARROW: process-wide logger activation policy
        for `AetherUtilitySystem`, and the docstring's Note draws the boundary
        explicitly by pointing system caching policy at
        `AethericFrameConfiguration` instead. Root configuration answers only
        what must be true for the whole process.
        Automatic channel-logger activation being DISABLED BY DEFAULT is the
        conservative posture that matters: a library that silently activated
        logging on import would emit into a host application's logging
        configuration uninvited. Explicit attachment via `attach_logger(...)`
        stays outside this surface for the same reason - handing over a live
        logger object is an act, not a policy.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Root logger-activation policy for AetherUtilitySystem. Mutable until frozen; "
        "activation implies validation. Automatic channel logging is OFF by default. Obtain via "
        "Aether.create_configuration()."
    )

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_activated",
        "_properties",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty Aether configuration with the default logger policy.

        Contract:
            - Starts MUTABLE, UNFROZEN and INACTIVE, with the default logger policy
              not yet applied - call `with_defaults()` to seed it.
            - Part of the three-stage configuration lifecycle: MUTABLE -> FROZEN ->
              ACTIVATED. Setters work only while mutable; `freeze()` seals values;
              `activate()` additionally marks the config live and records it.

        Owned State:
            Owns its lock, id, and the backing property map.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._activated: bool = False
        self._properties: Dict[str, object] = {
            "channel_logger_activation_enabled": False,
            "channel_logger_resolver": None,
            "default_logger": None,
        }

    def cleanup(self) -> None:
        """
        Idempotently clear configuration state.

        Contract:
            - IDEMPOTENT: a second call returns without re-running teardown.
            - Releases only configuration-owned state. Loggers and resolvers handed
              in by the caller are BORROWED and are not cleaned here.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frozen = True
            self._activated = False
            self._properties.clear()

            del self._properties
            del self._id

    @property
    def id(self) -> str:
        """
        Return the stable configuration id.

        Contract:
            - Identifies THIS CONFIGURATION OBJECT, not the Aether it configures.
            - Assigned at construction and stable for the object's life; freezing
              and activating do not change it.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration is frozen.

        Contract:
            - True once `freeze()` has sealed the values. Frozen means SETTERS ARE
              REFUSED; it does NOT mean the configuration is in use - that is
              `activated`.
            - Part of the three-stage configuration lifecycle: MUTABLE -> FROZEN ->
              ACTIVATED. Setters work only while mutable; `freeze()` seals values;
              `activate()` additionally marks the config live and records it.
        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when the mutation is closed.
        """
        self.check_cleaned()
        return self._frozen

    @property
    def activated(self) -> bool:
        """
        Return whether the configuration has been activated.

        Contract:
            - True only after `activate()`. Activation implies frozen, but frozen does
              NOT imply activated: `finalize()` freezes WITHOUT activating, so a
              configuration can be sealed and never made live.
            - Part of the three-stage configuration lifecycle: MUTABLE -> FROZEN ->
              ACTIVATED. Setters work only while mutable; `freeze()` seals values;
              `activate()` additionally marks the config live and records it.
        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when validated, frozen, and marked ready for Aether.
        """
        self.check_cleaned()
        return self._activated

    @property
    def channel_logger_activation_enabled(self) -> bool:
        """
        Return whether automatic channel logger activation is enabled.

        Contract:
            - DEFENSIVE READ: the stored value's type is re-checked on every read and
              a drifted value raises `TypeError` rather than being returned. That
              guards against direct tampering with the underlying property map.
            - Reflects the sealed value once frozen, so a post-freeze read is stable.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when `resolve_channel_logger(...)` may auto-attach.
        """
        self.check_cleaned()
        value = self._properties["channel_logger_activation_enabled"]
        if not isinstance(value, bool):
            raise TypeError(
                "channel_logger_activation_enabled must remain a bool."
            )
        return value

    @property
    def channel_logger_resolver(self) -> Optional[Callable[..., Any]]:
        """
        Return the configured channel logger resolver, if any.

        Contract:
            - `None` is a legitimate value meaning "no resolver attached", not an
              error. The read accepts None and rejects any non-callable.
            - DEFENSIVE READ: the stored value's type is re-checked on every read and
              a drifted value raises `TypeError` rather than being returned. That
              guards against direct tampering with the underlying property map.
            - Reflects the sealed value once frozen, so a post-freeze read is stable.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            Optional[Callable[..., Any]]: Configured resolver.
        """
        self.check_cleaned()
        value = self._properties["channel_logger_resolver"]
        if value is not None and not callable(value):
            raise TypeError(
                "channel_logger_resolver must remain callable or None."
            )
        return value

    @property
    def default_logger(self) -> Optional[logging.Logger]:
        """
        Return the configured stdlib fallback logger, if any.

        Contract:
            - `None` is a legitimate value meaning "no default logger", not an error.
              Any non-`logging.Logger` value raises on read.
            - DEFENSIVE READ: the stored value's type is re-checked on every read and
              a drifted value raises `TypeError` rather than being returned. That
              guards against direct tampering with the underlying property map.
            - Reflects the sealed value once frozen, so a post-freeze read is stable.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            Optional[logging.Logger]: Configured default logger.
        """
        self.check_cleaned()
        value = self._properties["default_logger"]
        if value is not None and not isinstance(value, logging.Logger):
            raise TypeError("default_logger must remain logging.Logger or None.")
        return value

    def with_defaults(self) -> "AetherConfiguration":
        """
        Apply the default Aether logger policy.

        Contract:
            - MUTATES THIS OBJECT and returns `self`; it is not a copying builder.
            - Applies the default logger policy in place, overwriting anything set
              earlier, so call it FIRST and override afterwards.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_channel_logger_activation_enabled(False)
        self.set_channel_logger_resolver(None)
        self.set_default_logger(None)
        return self

    @classmethod
    def from_recorded_payload(
            cls,
            recorded_payload: Dict[str, object],
    ) -> Tuple["AetherConfiguration", Dict[str, List[str]]]:
        """
        Reload lane: rebuild one Aether configuration from its recorded
        twin payload.

        Purpose:
            The restore counterpart to the fluent authoring lane. A sealed
            AetherCrystal payload is the configuration truth; the reload
            lane applies it and seals in one motion (load it in, freeze
            it), reporting every deviation to the caller.

        Contract:
            - channel_logger_activation_enabled reloads from the record;
              when absent it falls to the documented default (False) and
              is reported under "missing".
            - Callable-bearing entries can NEVER reload from a record:
              when the payload marks channel_logger_resolver_present or
              default_logger_present True, the key is reported under
              "code_participation" and the live value stays None - the
              booting code must re-supply its callables explicitly.
            - LOADS AND FREEZES in one motion: the returned configuration
              is sealed. The freeze carries no emission; emission rides
              `activate()`, which the booting Aether performs.

        Args:
            recorded_payload:
                AetherCrystal configuration_payload shaped mapping
                (JSON-safe, the cached-item shape).

        Returns:
            Tuple[AetherConfiguration, Dict[str, List[str]]]:
                (the rebuilt FROZEN configuration,
                 {"missing": [keys defaulted-with-report],
                  "code_participation": [keys needing live callables]}).

        Raises:
            ValueError: If the reloaded values fail validation at the
                internal freeze.
        """
        configuration = cls()
        missing: List[str] = []
        code_participation: List[str] = []
        if "channel_logger_activation_enabled" in recorded_payload:
            configuration.set_channel_logger_activation_enabled(
                bool(recorded_payload["channel_logger_activation_enabled"])
            )
        else:
            missing.append("channel_logger_activation_enabled")
        # Presence flags are honesty signals, not reloadable values: a
        # record can say a resolver existed, but only live code can
        # supply one.
        if bool(recorded_payload.get("channel_logger_resolver_present")):
            code_participation.append("channel_logger_resolver")
        if bool(recorded_payload.get("default_logger_present")):
            code_participation.append("default_logger")
        # Reload seals: load it in, freeze it - the reload lane never
        # hands back a mutable configuration.
        configuration.freeze()
        return configuration, {
            "missing": missing,
            "code_participation": code_participation,
        }

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "AetherConfiguration":
        """
        Set whether automatic channel logger resolution is enabled.

        Args:
            enabled:
                True when `resolve_channel_logger(...)` may auto-attach a
                logger for callers that opt into that path.

        Contract:
            - FLUENT WRAPPER over the matching `set_...` method: it delegates and
              returns `self`, adding no validation of its own.
            - MUTATES THIS OBJECT; it does not produce a variant.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_channel_logger_activation_enabled(enabled)
        return self

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "AetherConfiguration":
        """
        Set the channel logger resolver used by the utility system.

        Args:
            resolver:
                Resolver callable or None.

        Contract:
            - FLUENT WRAPPER over the matching `set_...` method; delegates and returns
              `self`, adding no validation of its own.
            - `None` is accepted and clears the resolver.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_channel_logger_resolver(resolver)
        return self

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "AetherConfiguration":
        """
        Set the stdlib fallback logger used by the utility system.

        Args:
            logger:
                Fallback stdlib logger or None.

        Contract:
            - FLUENT WRAPPER over the matching `set_...` method; delegates and returns
              `self`, adding no validation of its own.
            - `None` is accepted and clears the default logger.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_default_logger(logger)
        return self

    def set_channel_logger_activation_enabled(self, enabled: bool) -> None:
        """
        Set the automatic channel logger activation flag.

        Args:
            enabled:
                Desired activation state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `enabled` is not a bool.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["channel_logger_activation_enabled"] = enabled

    def set_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> None:
        """
        Set the channel logger resolver.

        Args:
            resolver:
                Resolver callable or None.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `resolver` is neither callable nor None.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if resolver is not None and not callable(resolver):
            raise TypeError("resolver must be callable or None.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["channel_logger_resolver"] = resolver

    def set_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> None:
        """
        Set the stdlib fallback logger.

        Args:
            logger:
                Fallback logger or None.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `logger` is neither `logging.Logger` nor None.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if logger is not None and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be logging.Logger or None.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["default_logger"] = logger

    def validate(self) -> bool:
        """
        Validate the logger policy values.

        Contract:
            - NEVER RETURNS False. Every failure raises `ValueError`; the `bool` return
              is a convention, not a verdict channel. Treat it as an assertion.
              (`freeze()`'s `if not self.validate()` branch is consequently
              unreachable.)
            - Checks VALUE TYPES only - the activation flag must be a bool, the
              resolver must be callable or None, the default logger must be a
              `logging.Logger` or None.
            - Does not mutate, and may be called before or after freeze.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when the configuration is valid.
        """
        self.check_cleaned()
        if not isinstance(self._properties["channel_logger_activation_enabled"], bool):
            raise ValueError("channel_logger_activation_enabled must be a bool.")
        if (
                self._properties["channel_logger_resolver"] is not None
                and not callable(self._properties["channel_logger_resolver"])
        ):
            raise ValueError("channel_logger_resolver must be callable or None.")
        if (
                self._properties["default_logger"] is not None
                and not isinstance(self._properties["default_logger"], logging.Logger)
        ):
            raise ValueError(
                "default_logger must be logging.Logger or None."
            )
        return True

    def freeze(self) -> None:
        """
        Validate and freeze the configuration.

        Contract:
            - IDEMPOTENT: a second call returns immediately without re-validating.
            - VALIDATES BEFORE SEALING, so an invalid configuration raises and stays
              MUTABLE. Freeze is all-or-nothing.
            - Seals values only; it does NOT activate. Use `activate()` for that.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("AetherConfiguration validation failed.")
        with self._lock:
            self._frozen = True

    def finalize(self) -> "AetherConfiguration":
        """
        Validate and freeze the configuration, then return it.

        Contract:
            - `freeze()` plus `return self` - nothing more. It seals the configuration
              WITHOUT activating it and WITHOUT recording anything.
            - Use this when you want an immutable configuration to hand somewhere;
              use `activate()` when the configuration is going live now.
            - Idempotent, inheriting `freeze()`'s early return.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def activate(self) -> "AetherConfiguration":
        """
        Validate, freeze, and mark the configuration active.

        Contract:
            - Freezes, marks the configuration ACTIVE, and then EMITS a configured-twin
              record when recording is on. That emission is a real side effect that
              `finalize()` does not have.
            - NOT FULLY IDEMPOTENT. The freeze and the flag are, but the emission is
              NOT guarded by the activated flag, so calling `activate()` twice
              records TWICE. Call it once.
            - Emission happens after the flag is set, so the configuration is already
              observably active while the record is written.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: This activated configuration instance.
        """
        self.freeze()
        with self._lock:
            self._activated = True
        self.emit_configured_twin_when_recording()
        return self

    def emit_configured_twin_when_recording(self) -> None:
        """
        Internal emission seam

        Emit the Aether root twin for this configuration into the record.

        Purpose:
            Configuration activation is the emission factor, so
            `activate()` emits here. BUT the Aether root structurally
            precedes the crystallizer (it hosts it), so in the normal boot
            order this fires before recording is possible and captures
            nothing - `Crystallizer.activate` therefore calls this seam as
            a targeted root catch-up once recording is live. Same seam
            class as the nexus enable-time emission.

        Contract:
            - NO-OP before the crystallizer singleton boots or while it is
              not activated.
            - Callable-bearing entries record as PRESENCE flags only (a
              record cannot carry live callables); the reload lane reports
              them as code_participation.
            - Replace-on-emit in the profile keeps exactly one root twin.

        Returns:
            None.
        """
        # Pull the crystallizer singleton directly (guarding the pre-boot
        # case, where the singleton is not yet initialized and
        # construction requires the hosting Aether), emit when recording,
        # then drop the local handle.
        if Crystallizer._initialized:
            crystallizer = Crystallizer()
            if crystallizer.activated:
                crystallizer.emit(
                    AetherCrystal(
                        configuration_payload={
                            "channel_logger_activation_enabled": (
                                self._properties["channel_logger_activation_enabled"]
                            ),
                            "channel_logger_resolver_present": (
                                self._properties["channel_logger_resolver"] is not None
                            ),
                            "default_logger_present": (
                                self._properties["default_logger"] is not None
                            ),
                        },
                    )
                )
            del crystallizer
