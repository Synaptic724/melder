from logging import LogRecord
from types import TracebackType
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Union, runtime_checkable

@runtime_checkable
class IChannelLogger(Protocol):
    """
    ChannelLogger
    -------------
    Concurrency-safe facade over one or more Python `logging.Logger` instances,
    registered to IRIS channels. Emits a single `LogRecord` per call, forwards it
    to all configured loggers, then notifies IRIS subscribers.

    This version adds **local state controls** so each ChannelLogger can be
    independently enabled/disabled and filtered by a minimum level, with
    optional **overrides** that can be imposed by a higher-level controller.

    Additions:
    - **groups** (membership): `Set[str]` of tokens (e.g., "SYSTEM", "PIPELINE_A").
      Snapshot is attached to each record as `record.groups` (List[str]).
    - **properties** (key/value): `Dict[str, Any]` of flat scalars you want
      stamped on every record (e.g., small IDs/flags). Snapshot is attached to each
      record as `record.properties` (Dict[str, Any]).
      (Thread/agent fields from `ContextFilter` are still injected separately.)
    - **state**:
        * `enabled` (bool): default, local on/off switch.
        * `min_level` (int): default local minimum level (e.g., `logging.INFO`).
        * `override_enabled` (Optional[bool]): if set, takes precedence over `enabled`.
        * `override_min_level` (Optional[int]): if set, takes precedence over `min_level`.

    Snapshot semantics:
    - On emit, the logger captures *current* groups/properties under lock and
      attaches those snapshots to the `LogRecord`. Mutations after that do not
      affect the already-created record.
    """
    _id: str
    @property
    def id(self) -> str:
        """
        Get the unique ID of this ChannelLogger.

        Returns:
            str: The ID assigned at construction.
        """
        ...

    @property
    def last_log_time(self) -> float:
        """
        Get the UNIX timestamp of the last emitted (accepted) log call for this ChannelLogger.

        Returns:
            float: Seconds since the epoch for the last accepted record emit attempt.
        """
        ...

    @property
    def name(self) -> str:
        """
        Get the name of this ChannelLogger.

        Returns:
            str: The name assigned at construction.
        """
        ...

    # ===== Channels =====
    def add_channel(self, channel_name: str) -> None:
        """
        Route this ChannelLogger to an additional IRIS channel.

        Creates/attaches the child logger under the channel's parent logger name
        (e.g., "Iris.<console>.<{registrant}>") and records the routing in
        self._channels / self._loggers.
        """
        ...

    def remove_channel(self, channel_name: str) -> bool:
        """
        Stop routing this ChannelLogger to a specific IRIS channel.

        We detect the child logger(s) to drop by inspecting their *parent* logger's
        monkey-patched attribute `_command_ops_name`, which IrisChannel sets when
        constructing the parent (e.g., "console").
        """
        ...

    # ===== State (enabled/min level/overrides) =====
    def set_enabled(self, value: bool) -> None:
        """
        Set the local-enabled flag.

        Args:
            value: True to enable locally, False to disable locally.

        Notes:
            - If `override_enabled` is set (not None), it *overrides* this local flag.
            - Use `get_effective_enabled()` to read the computed effective state.
        """
        ...

    def get_enabled(self) -> bool:
        """
        Get the current local-enabled flag (ignoring overrides).

        Returns:
            bool: The local `enabled` setting.
        """
        ...

    def set_override_enabled(self, value: Optional[bool]) -> None:
        """
        Set or clear the override for the enabled flag.

        Args:
            value: True/False to force enabled/disabled; None to remove the override.

        Notes:
            - When not None, `override_enabled` takes precedence over the local `enabled`.
        """
        ...

    def clear_override_enabled(self) -> None:
        """
        Clear the enabled override, reverting to the local `enabled` flag.
        """
        ...

    def get_override_enabled(self) -> Optional[bool]:
        """
        Get the current override for the enabled flag.

        Returns:
            Optional[bool]: The `override_enabled` value (True/False), or None if unset.
        """
        ...

    def get_effective_enabled(self) -> bool:
        """
        Compute the effective enabled state for this ChannelLogger.

        Returns:
            bool: `override_enabled` if set; otherwise the local `enabled` flag.
        """
        ...

    def setLevel(self, level: int) -> None:
        """
        Apply one concrete numeric logging threshold to this channel logger.

        Purpose:
            Mirror the stdlib logger-style level-setting contract used by
            `SafeLogger` so the adapter can push its resolved numeric threshold
            onto either a channel logger or an stdlib logger through one shared
            path.

        Args:
            level:
                Concrete numeric logging threshold (for example,
                `logging.INFO`).

        Returns:
            None.
        """
        ...

    def set_min_level(self, level: str) -> None:
        """
        Set the local minimum logging level.

        Level Reference (standard `logging` levels):
            - NOTSET (0): Special value; if used as a threshold, it effectively lets everything through.
            - DEBUG (10): Detailed diagnostic information useful for development and deep troubleshooting.
            - INFO (20): High-level operational events (what the system is doing).
            - WARNING (30): Something unexpected or suboptimal happened, but the system can continue.
            - ERROR (40): A failure occurred for the current operation; the system may still be running.
            - CRITICAL (50): The system is in a bad state and may require immediate attention / shutdown.

        Args:
            level: A standard logging level name (e.g., "INFO").

        Notes:
            - Records with a level *below* the effective min level are dropped.
            - If `override_min_level` is set, it takes precedence.
        """
        ...

    def get_min_level(self) -> int:
        """
        Get the current local minimum logging level (ignoring overrides).

        Returns:
            int: The local `min_level` integer.
        """
        ...

    def set_override_min_level(self, level: Optional[str]) -> None:
        """
        Set or clear the override for the minimum logging level.

        Level Reference (standard `logging` levels):
            - NOTSET (0): Special value; if used as a threshold, it effectively lets everything through.
            - DEBUG (10): Detailed diagnostic information useful for development and deep troubleshooting.
            - INFO (20): High-level operational events (what the system is doing).
            - WARNING (30): Something unexpected or suboptimal happened, but the system can continue.
            - ERROR (40): A failure occurred for the current operation; the system may still be running.
            - CRITICAL (50): The system is in a bad state and may require immediate attention / shutdown.

        Args:
            level: A standard logging level integer (e.g., `INFO`), or None to clear the override.

        Notes:
            - When not None, `override_min_level` takes precedence over local `min_level`.
        """
        ...

    def clear_override_min_level(self) -> None:
        """
        Clear the min-level override, reverting to the local `min_level`.
        """
        ...

    def get_override_min_level(self) -> Optional[int]:
        """
        Get the current override for the minimum logging level.

        Returns:
            Optional[int]: The `override_min_level` value, or None if unset.
        """
        ...

    def _effective_min_level(self) -> int:
        """
        Compute the effective minimum logging level for this ChannelLogger.

        Returns:
            int: `override_min_level` if set; otherwise the local `min_level`.
        """
        ...

    def _should_emit(self, record_level: int) -> bool:
        """
        Decide whether a record at `record_level` should be emitted given the current state.

        Args:
            record_level: The logging level of the prospective record (e.g., `logging.DEBUG`).

        Returns:
            bool: True if the ChannelLogger is effectively enabled *and*
                  `record_level >= effective_min_level`; otherwise False.

        Notes:
            - This method performs no side effects and does not construct a `LogRecord`.
            - Called early in `_log()` to avoid unnecessary work when filtered out.
        """
        ...

    # ===== Groups =====
    def add_group(self, name: str) -> None:
        """
        Add a group token.

        Args:
            name: Non-empty string token. No normalization is applied.

        Behaviour:
            - No-op if `name` is falsy.
            - Safe under concurrent calls.
        """
        ...

    def remove_group(self, name: str) -> None:
        """
        Remove a group token if present.

        Args:
            name: Group token to remove.

        Behaviour:
            - No error if not present (discard semantics).
        """
        ...

    def clear_groups(self) -> None:
        """
        Remove all group tokens from this ChannelLogger.
        """
        ...

    def get_groups_snapshot(self) -> List[str]:
        """
        Get a stable, sorted snapshot of current group tokens.

        Returns:
            List[str]: Unique tokens sorted case-insensitively.
        """
        ...

    # ===== Properties =====
    def set_property(self, key: str, value: Any) -> None:
        """
        Set or update a property to stamp on subsequent records.

        Args:
            key: Non-empty string key (conventional guidance: <= 64 chars, token-like).
            value: Scalar value (str/int/float/bool) recommended. Small payloads only.

        Notes:
            - No serialization is performed here; downstream formatters/archivers decide.
            - Oversized or complex values may increase log overhead.
        """
        ...

    def set_properties(self, data: Dict[str, Any]) -> None:
        """
        Bulk update of properties.

        Args:
            data: Mapping of keys to values. Falsy/empty keys are skipped.

        Notes:
            - Each entry is applied atomically under the internal lock.
        """
        ...

    def remove_property(self, key: str) -> None:
        """
        Remove a property if present.

        Args:
            key: Property key to remove.

        Behaviour:
            - Silent no-op when the key is absent.
        """
        ...

    def clear_properties(self) -> None:
        """
        Remove all properties from this ChannelLogger.
        """
        ...

    def get_properties_snapshot(self) -> Dict[str, Any]:
        """
        Get a shallow copy snapshot of all properties.

        Returns:
            Dict[str, Any]: Copy of current properties suitable for attaching to a record.
        """
        ...

    # ===== Emit / Logging =====
    def mask_log(
            self,
            level: int,
            message: str,
            *,
            owner: object,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
            exc_info: Union[None, bool, BaseException] = None,
            **kwargs: Any
    ) -> None:
        """
        Log once with masking enabled, using the owner's display identity
        ('<ULID>.<ClassName>'), and optionally overriding groups/system_groups/properties.
        """
        ...

    def _should_fast_exit(self, level: int) -> bool:
        """
        Fast-path filter to avoid work when logger is cleaned/disabled or the level is below gates.
        """
        ...

    def _resolve_caller(
            self,
            tmpl_logger: Any,
            *,
            stacklevel: int,
            manual_stack: bool,
            kwargs: Dict[str, Any],
    ) -> tuple[str, int, str, object]:
        """
        Compute caller metadata for `LogRecord` creation.

        Returns:
            tuple[str, int, str, object]:
                "(filename, line_number, function_name, stack_info)" tuple
                suitable for downstream record construction.
        """
        ...

    def _normalize_exc_info(
            self,
            exc_info: Any,
    ) -> Optional[tuple[type[BaseException], BaseException, Optional[TracebackType]]]:
        """
        Normalize exc_info to either a (type, value, tb) tuple or None.

        - True -> sys.exc_info(), unless outside an excepted block (then None)
        - tuple -> passthrough
        - other truthy -> None (conservative)
        - falsy/None -> None

        Returns:
            object: Normalized "exc_info" payload accepted by record creation,
            or "None" when no exception context should be attached.
        """
        ...

    def _build_record(
            self,
            tmpl_logger: Any,
            *,
            level: int,
            msg: str,
            args: tuple[Any, ...],
            exc_info: Optional[
                tuple[type[BaseException], BaseException, Optional[TracebackType]]
            ],
            fn: str,
            lno: int,
            func: str,
            sinfo: object,
    ) -> LogRecord:
        """
        Build one `LogRecord` with resolved caller metadata.
        """
        ...

    def _apply_identity_and_tags(
            self,
            record: LogRecord,
            *,
            mask: bool,
            kwargs: Dict[str, Any],
    ) -> LogRecord:
        """
        Apply identity masking plus group/property tags to a `LogRecord`.
        """
        ...

    def _emit_record(self, record: LogRecord) -> None:
        """
        Fan out one prepared record to backing loggers and channel subscribers.
        """
        ...

    def _log(
            self,
            level: int,
            msg: str,
            *args: Any,
            mask: bool = False,
            **kwargs: Any,
    ) -> None:
        """
        Internal logging method that creates and dispatches a LogRecord to all
        configured loggers if enabled and above the min level.

        Args:
            level: Logging level (e.g., `logging.INFO`).
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            mask: If True, use masked identity and optional overrides from kwargs.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).
                     Internal keys are consumed here (and removed):
                       - _stack_info: bool -> if True, compute caller info (default False)
                       - stacklevel: int -> passed to findCaller (default 3)
                       - _mask_display_name/_mask_display_id/_groups_override/
                         _system_groups_override/_properties_override (masking branch)

        Returns:
            None.
        """
        ...

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with the ` INFO ` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with the ` WARNING ` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    warn: Callable[..., None] = warning  # alias

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with the ` ERROR ` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with the ` DEBUG ` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Convenience helper to log an exception with `ERROR` level, including traceback.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments. `exc_info` is forced to True.

        Notes:
            - Equivalent to `error(..., exc_info=True)`.
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with the ` CRITICAL ` level.
        """
        ...

    fatal: Callable[..., None] = critical

    # ===== System Groups =====
    def _add_system_group(self, name: str) -> None:
        """
        Internal: add a single system group token.

        Args:
            name: Non-empty string token. No normalization is applied.

        Behaviour:
            - No-op if `name` is falsy.
            - Safe under concurrent calls.
        """
        ...

    def _add_system_groups(self, names: Optional[Iterable[str]]) -> None:
        """
        Internal: add multiple system group tokens.

        Args:
            names: Iterable of tokens. Falsy/empty tokens are skipped. If None, no-op.

        Behaviour:
            - Safe under concurrent calls.
        """
        ...

    def _remove_system_group(self, name: str) -> None:
        """
        Internal: remove a system group token if present.

        Args:
            name: Token to remove.

        Behaviour:
            - Silent no-op if not present (discard semantics).
        """
        ...

    def _remove_system_groups(self, names: Optional[Iterable[str]]) -> None:
        """
        Internal: remove multiple system group tokens.

        Args:
            names: Iterable of tokens to remove. If None, no-op.

        Behaviour:
            - Silent no-op on missing tokens.
        """
        ...

    def _clear_system_groups(self) -> None:
        """
        Internal: remove all system group tokens.
        """
        ...

    def _has_system_group(self, name: str) -> bool:
        """
        Internal: check membership of a system group token.

        Args:
            name: Token to check.

        Returns:
            bool: True if present, else False.
        """
        ...

    def _get_system_groups_snapshot(self) -> List[str]:
        """
        Internal: get a stable, sorted snapshot of current system group tokens.

        Returns:
            List[str]: Unique tokens sorted case-insensitively.
        """
        ...

    # ===== Metadata convenience =====
    def add_metadata(
            self,
            *,
            groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add group tokens and/or set properties in one call.

        Args:
            groups: Iterable of group tokens to add (ignored if None).
            properties: Mapping of properties to set/overwrite (ignored if None).

        Returns:
            None.
        """
        ...

    def remove_metadata(
            self,
            *,
            groups: Optional[Iterable[str]] = None,
            properties: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Remove group tokens and/or delete properties in one call.

        Args:
            groups: Iterable of group tokens to remove (ignored if None).
            properties: Iterable of property keys to delete (ignored if None).

        Returns:
            None.
        """
        ...

    def refresh_properties(self, **kwargs: Any) -> None:
        """
        Refresh (set/overwrite) per-record properties in-place.

        Usage:
            ch.refresh_properties(open=self._open, queued=queue.size)

        Returns:
            None.
        """
        ...

    refresh_props: Callable[..., None] = refresh_properties
