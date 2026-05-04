from typing import runtime_checkable, Protocol, Optional, Union, Dict, Any, Iterable

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class ISafeLogger(ICleanable, Protocol):
    """
    Structural contract for SafeLogger-like objects.

    Masking (optional; default False):
      - When `mask=True` and the underlying logger is a ChannelLogger, the call routes
        to ChannelLogger.mask_log(...) using the provided identity & tags.
      - When wrapping a standard logging.Logger, masking params are ignored (no-op).

    Notes:
      - Signatures mirror SafeLogger's public API (including mask options).
      - `exception()` is an explicit helper (equivalent to error(..., exc_info=True)).
      - `cleanup()` aligns with Cleanable semantics.
    """

    # Optional: some implementations surface an identifier
    _id: str  # runtime presence not enforced by Protocol, but allowed for duck-typing

    # ---- Core API --------------------------------------------------------------

    def debug(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one `DEBUG`-level log entry through the safe-logger facade.
        """
        ...

    def info(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one `INFO`-level log entry through the safe-logger facade.
        """
        ...

    def warning(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one `WARNING`-level log entry through the safe-logger facade.
        """
        ...

    def error(
            self,
            msg: str,
            method_name: str,
            *,
            exc_info: Union[None, bool, BaseException] = True,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one `ERROR`-level log entry through the safe-logger facade.
        """
        ...

    def exception(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one exception-oriented log entry, typically equivalent to
        `error(..., exc_info=True)`.
        """
        ...

    def critical(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one `CRITICAL`-level log entry through the safe-logger facade.
        """
        ...
