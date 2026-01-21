from typing import Any, Dict, Iterable, Optional, Union, Callable
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces.interfaces import IAether, IConduit, ISpellbook


class IrisLoggerFactory(Cleanable):
    """
    Ultra-thin adapter:
      - Routes by Protocol (IConduit | ISpellbook | IAether | generic).
      - Fills ONLY None values from concrete, built-in defaults.
      - Forwards to your resolver and wraps with SafeLogger.
      - Optionally applies a SafeLogger level (numeric or by name) with a fast-path reject.

    Level behavior:
      * You can set a factory-wide default via `set_default_level(int)` or `set_default_level_by_name(str)`.
      * You can override per-call using `level=` or `level_name=`.
      * SafeLogger will drop messages below its threshold before touching the underlying logger.
    """
    __melder_internal__ = _mrg.sentinel

    # ---- Concrete, built-in defaults (change here if you want different baked-ins) ----
    _CONDUIT_DEFAULTS: Dict[str, Any] = {
        "groups": ["lifecycle", "organization"],
        "system_groups": ["spellbook", "aether"],
        "props": None,
        "channels": "system",
    }
    _SPELLBOOK_DEFAULTS: Dict[str, Any] = {
        "groups": ["spellbook", "lifecycle"],
        "system_groups": ["aether"],
        "props": None,
        "channels": "system",
    }
    _AETHER_DEFAULTS: Dict[str, Any] = {
        "groups": ["aether", "lifecycle"],
        "system_groups": ["aether"],
        "props": None,
        "channels": "system",
    }
    _GENERIC_DEFAULTS: Dict[str, Any] = {
        "groups": ["general"],
        "system_groups": [],
        "props": None,
        "channels": "system",
    }

    __slots__ = (
        *Cleanable.__slots__,
        "_resolve_fn",
        "_def_conduit",
        "_def_spellbook",
        "_def_aether",
        "_def_generic",
        "_default_level_name",
        "_default_level",
    )

    def __init__(
            self,
            resolve_fn: Callable[..., Any],
            *,
            conduit: Optional[Dict[str, Any]] = None,
            spellbook: Optional[Dict[str, Any]] = None,
            aether: Optional[Dict[str, Any]] = None,
            generic: Optional[Dict[str, Any]] = None,
            default_level_name: Optional[str] = None,
            default_level: Optional[int] = None,
    ):
        """
        Initialize the Iris logger adapter.

        Args:
            resolve_fn: Callable(registrant, groups, system_groups, props, channels) -> channel logger-like object.
            conduit: Optional overrides for Conduit defaults (only fills when call-time args are None).
            spellbook: Optional overrides for Spellbook defaults (only fills when call-time args are None).
            aether: Optional overrides for Aether defaults (only fills when call-time args are None).
            generic: Optional overrides for generic defaults (only fills when call-time args are None).
            default_level_name: Optional symbolic level ("debug", "info", "warning", "error", "critical").
            default_level: Optional numeric level (e.g., logging.INFO). Ignored if `default_level_name` is provided.
        """
        super().__init__()
        self._resolve_fn = resolve_fn
        self._def_conduit = conduit or self._CONDUIT_DEFAULTS
        self._def_spellbook = spellbook or self._SPELLBOOK_DEFAULTS
        self._def_aether = aether or self._AETHER_DEFAULTS
        self._def_generic = generic or self._GENERIC_DEFAULTS

        # Establish a factory-wide SafeLogger level default.
        if default_level_name is not None:
            name = default_level_name.lower()
            if name not in SafeLogger._LEVELS:
                raise ValueError(f"Invalid log level name '{default_level_name}'. Expected one of: {list(SafeLogger._LEVELS)}")
            self._default_level_name = name
            self._default_level = SafeLogger._LEVELS[name]
        else:
            self._default_level = int(default_level) if default_level is not None else SafeLogger._LEVELS["notset"]
            reverse = {v: k for k, v in SafeLogger._LEVELS.items()}
            self._default_level_name = reverse.get(self._default_level, "notset")

    def cleanup(self):
        """
        Idempotent teardown of the factory and its resolver.
        """
        fn = self._resolve_fn
        if fn is not None and hasattr(fn, "cleanup"):
            try:
                fn.cleanup()
            except Exception:
                pass
        self._resolve_fn = None
        self._def_conduit = None
        self._def_spellbook = None
        self._def_aether = None
        self._def_generic = None
        self._default_level_name = None
        self._default_level = None

    # ---- internals ---------------------------------------------------------

    def _defaults_for(self, registrant: object) -> Dict[str, Any]:
        if isinstance(registrant, IConduit):
            return self._def_conduit
        if isinstance(registrant, ISpellbook):
            return self._def_spellbook
        if isinstance(registrant, IAether):
            return self._def_aether
        return self._def_generic

    # ---- public API --------------------------------------------------------

    def set_default_level(self, level: int) -> None:
        """
        Set the factory-wide numeric SafeLogger level used when `__call__` is invoked without overrides.
        """
        self.check_cleaned()
        self._default_level = int(level)
        reverse = {v: k for k, v in SafeLogger._LEVELS.items()}
        self._default_level_name = reverse.get(self._default_level, "notset")

    def set_default_level_by_name(self, level_name: str) -> None:
        """
        Set the factory-wide symbolic SafeLogger level used when `__call__` is invoked without overrides.

        Raises:
            ValueError: If `level_name` is not a recognized level name.
        """
        self.check_cleaned()
        name = level_name.lower()
        if name not in SafeLogger._LEVELS:
            raise ValueError(f"Invalid log level name '{level_name}'. Expected one of: {list(SafeLogger._LEVELS)}")
        self._default_level_name = name
        self._default_level = SafeLogger._LEVELS[name]

    def __call__(
            self,
            registrant: object,
            *,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            props: Optional[Dict[str, Any]] = None,
            channels: Optional[Union[str, Iterable[str]]] = None,
            level: Optional[int] = None,
            level_name: Optional[str] = None,
    ) -> SafeLogger:
        """
        Fill only Nones from per-kind defaults, resolve a channel logger, and wrap with SafeLogger.

        You may override the SafeLogger level per call with `level` (numeric) or `level_name` (symbolic).
        If neither is supplied, the factory-wide default is applied.
        """
        self.check_cleaned()

        dfl = self._defaults_for(registrant)
        final_groups = groups if groups is not None else dfl.get("groups")
        final_system_groups = system_groups if system_groups is not None else dfl.get("system_groups")
        final_props = props if props is not None else dfl.get("props")
        final_channels = channels if channels is not None else dfl.get("channels")

        logger = self._resolve_fn(
            registrant=registrant,
            groups=final_groups,
            system_groups=final_system_groups,
            props=final_props,
            channels=final_channels,
        )
        safe = SafeLogger(logger)

        # Apply level override or factory default for fast-path rejection in SafeLogger.
        if level_name is not None:
            safe.set_level_by_name(level_name)
        elif level is not None:
            safe.set_level(level)
        else:
            # Use factory default if present; if notset, SafeLogger keeps its internal default.
            if self._default_level_name != "notset" or self._default_level != SafeLogger._LEVELS["notset"]:
                safe.set_level(self._default_level)

        return safe
