from typing import Any, Dict, Iterable, Optional, Union, Callable
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces.interfaces import IAether, IConduit, ISpellbook  # runtime_checkable Protocols


class IrisLoggerFactory(Cleanable):
    """
    Ultra-thin adapter:
      - Routes by Protocol (IConduit | ISpellbook | IAether | generic).
      - Fills ONLY None values from concrete, built-in defaults.
      - Forwards to your resolver and wraps with SafeLogger.
    """

    # ---- Concrete, built-in defaults (change here if you want different baked-ins) ----
    _CONDUIT_DEFAULTS: Dict[str, Any] = {
        "groups": ["lifecycle", "organization"],
        "system_groups": ["spellbook", "aether"],   # <- per request
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
    )

    def __init__(
            self,
            resolve_fn: Callable[..., Any],
            *,
            # Optional overrides for the baked-in defaults; omit to use concrete defaults above.
            conduit: Optional[Dict[str, Any]] = None,
            spellbook: Optional[Dict[str, Any]] = None,
            aether: Optional[Dict[str, Any]] = None,
            generic: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self._resolve_fn = resolve_fn
        self._def_conduit = conduit or self._CONDUIT_DEFAULTS
        self._def_spellbook = spellbook or self._SPELLBOOK_DEFAULTS
        self._def_aether = aether or self._AETHER_DEFAULTS
        self._def_generic = generic or self._GENERIC_DEFAULTS

    def cleanup(self):
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

    # ---- internals ---------------------------------------------------------

    def _defaults_for(self, registrant: object) -> Dict[str, Any]:
        if isinstance(registrant, IConduit):
            return self._def_conduit
        if isinstance(registrant, ISpellbook):
            return self._def_spellbook
        if isinstance(registrant, IAether):
            return self._def_aether
        return self._def_generic

    # ---- call --------------------------------------------------------------

    def __call__(
            self,
            registrant: object,
            *,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            props: Optional[Dict[str, Any]] = None,
            channels: Optional[Union[str, Iterable[str]]] = None,
    ) -> Any:
        """
        Fill only Nones from per-kind defaults, then resolve and wrap.
        """
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
        return SafeLogger(logger)
