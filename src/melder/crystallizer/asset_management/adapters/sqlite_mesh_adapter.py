import json
import os
import re
import sqlite3
from contextlib import closing
from threading import RLock
from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.persistence.record_version import RecordVersion
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
        ExternalPersistenceManagerConfiguration,
    )


class SqliteMeshAdapter(Cleanable):
    """
    First-party SQLite adapter PROVIDING the external persistence mesh
    callables (patch sqlite_mesh_adapter_2026_07_12).

    Purpose:
        Give users a zero-storage-code path onto the mesh: construct the
        adapter with a database path, register its four handlers through
        the NORMAL configuration fluents (`register_with(...)` is sugar
        over exactly those fluents), and every mesh unit kind -
        checkpoints, formations, index grafts, emissions, and any future
        kind - persists into one SQLite table shaped exactly like
        `MeshInterfaceContract.IDENTITY_COLUMNS`.

    Contract:
        - The callables-first law stands: melder core NEVER imports this
          module (or sqlite3). The user imports the adapter and registers
          it; core only ever calls the registered plain callables.
        - One table, contract-shaped: kind TEXT, profile_name TEXT,
          unit_id TEXT, payload TEXT (the RecordVersion-stamped JSON
          document, stored verbatim via json.dumps/loads), with
          PRIMARY KEY (kind, unit_id). Store is INSERT OR REPLACE, so a
          re-shipped unit follows the record's replace-on-emit precedent.
        - Handler semantics mirror `MeshInterfaceContract
          .HANDLER_SIGNATURES`: fetch returns the payload dict or None
          when absent; list returns unit_id strings for one
          kind+profile partition in lexicographic order (ULID order =
          age); delete is STRICT and raises `KeyError` for a missing
          unit (a half-run retention pass must not lie).
        - Reader gates stay melder-side (RecordVersion.check_readable at
          the reload seams); the adapter never inspects payload content.

    Threading / Concurrency:
        Every verb opens, uses, and closes its OWN sqlite3 connection
        (connection-per-operation), so the handlers are safe from any
        thread on free-threaded builds without `check_same_thread`
        hazards or a shared-connection lock. Mesh calls are flush-time
        IO, never hot-path work. The instance `RLock` guards only
        construction/cleanup state.

    Lifecycle / Cleanup:
        The adapter owns no long-lived connection. `cleanup()` is
        idempotent and drops the identity fields; a cleaned adapter's
        verbs refuse through `check_cleaned()`. The database file itself
        is the user's asset and is never deleted by cleanup.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    # Class-level defaults (no module constants law).
    DEFAULT_TABLE_NAME: ClassVar[str] = "melder_mesh_units"
    _IDENTIFIER_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"^[A-Za-z_][A-Za-z0-9_]*$"
    )

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_database_path",
        "_table_name",
    ]

    def __init__(
            self,
            database_path: str,
            *,
            table_name: Optional[str] = None,
    ) -> None:
        """
        Bind the adapter to one SQLite database file and ensure the table.

        Contract:
            - Creates the database file's parent directory when absent
              (pod-boot friendliness) and the contract table + its
              kind/profile listing index idempotently.
            - `table_name` must be a plain SQL identifier
              (letters/digits/underscore, not digit-leading): identifiers
              cannot be parameterized, so the pattern gate is the
              injection guard.

        Args:
            database_path:
                Filesystem path of the SQLite database (created on first
                use if absent).
            table_name:
                Optional table override; defaults to
                `DEFAULT_TABLE_NAME`.

        Returns:
            None.

        Raises:
            ValueError:
                If `database_path` is falsy or `table_name` is not a
                plain identifier.
            sqlite3.Error:
                Propagated when the database cannot be created/opened.
        """
        super().__init__()
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError(
                "database_path must be a non-empty filesystem path string."
            )
        resolved_table = (
            table_name if table_name is not None else self.DEFAULT_TABLE_NAME
        )
        if not self._IDENTIFIER_PATTERN.match(resolved_table):
            raise ValueError(
                "table_name must be a plain SQL identifier "
                "(letters, digits, underscore; not digit-leading); "
                f"got {resolved_table!r}."
            )
        self._lock: RLock = RLock()
        self._database_path: str = database_path
        self._table_name: str = resolved_table
        parent_directory = os.path.dirname(os.path.abspath(database_path))
        os.makedirs(parent_directory, exist_ok=True)
        self._ensure_schema()

    def cleanup(self) -> None:
        """
        Idempotently retire the adapter.

        Contract:
            - Idempotent and lock-guarded.
            - Owns no connection to close (connection-per-operation);
              teardown deletes the identity fields so a retired adapter
              exposes no live surface. The database FILE is untouched -
              it is the user's durable asset.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._database_path
            del self._table_name
        del self._lock

    # ------------------------------------------------------------------
    # The four mesh handlers (MeshInterfaceContract.HANDLER_SIGNATURES)
    # ------------------------------------------------------------------

    def store_unit(
            self,
            kind: str,
            profile_name: str,
            unit_id: str,
            payload: Dict[str, object],
    ) -> None:
        """
        Persist one mesh unit (INSERT OR REPLACE - latest write wins).

        Contract:
            - Registered as the `with_store_handler` callable.
            - The payload is stored verbatim as its JSON text; the mesh
              only ships JSON-safe RecordVersion-stamped dicts (proven by
              the twin JSON-boundary contract tests).

        Args:
            kind: Unit kind partition (any string kind, future-proof).
            profile_name: Recording profile the unit belongs to.
            unit_id: Kind-specific identity (ULID / name / index id).
            payload: The stamped JSON document.

        Returns:
            None.

        Raises:
            RuntimeError: If the adapter has been cleaned.
            sqlite3.Error: Propagated on storage failure (the manager's
                lenient store lane counts it; strict mode re-raises).
            TypeError: From json.dumps when a payload is not JSON-safe.
        """
        self.check_cleaned()
        document = json.dumps(payload)
        with self._connection() as connection:
            connection.execute(
                f"INSERT OR REPLACE INTO {self._table_name} "
                "(kind, profile_name, unit_id, payload) "
                "VALUES (?, ?, ?, ?)",
                (kind, profile_name, unit_id, document),
            )
            connection.commit()

    def fetch_unit(
            self,
            kind: str,
            unit_id: str,
    ) -> Optional[Dict[str, object]]:
        """
        Return one stored unit's payload dict, or None when absent.

        Contract:
            - Registered as the `with_fetch_handler` callable.
            - Absence is a plain None (the mesh's documented miss shape),
              never an exception.

        Args:
            kind: Unit kind partition.
            unit_id: Kind-specific identity.

        Returns:
            Optional[Dict[str, object]]: The stored JSON document, or
            None when no row matches.

        Raises:
            RuntimeError: If the adapter has been cleaned.
            sqlite3.Error: Propagated on read failure.
        """
        self.check_cleaned()
        with self._connection() as connection:
            row = connection.execute(
                f"SELECT payload FROM {self._table_name} "
                "WHERE kind = ? AND unit_id = ?",
                (kind, unit_id),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def list_units(
            self,
            kind: str,
            profile_name: str,
    ) -> List[str]:
        """
        Return the unit ids stored for one kind+profile partition.

        Contract:
            - Registered as the `with_list_units_handler` callable.
            - Lexicographic order: mesh unit ids are ULIDs where age
              matters (checkpoints/emissions), so lexicographic = age;
              retention passes rely on that ordering.

        Args:
            kind: Unit kind partition.
            profile_name: Recording profile partition.

        Returns:
            List[str]: Matching unit ids (possibly empty).

        Raises:
            RuntimeError: If the adapter has been cleaned.
            sqlite3.Error: Propagated on read failure.
        """
        self.check_cleaned()
        with self._connection() as connection:
            rows = connection.execute(
                f"SELECT unit_id FROM {self._table_name} "
                "WHERE kind = ? AND profile_name = ? "
                "ORDER BY unit_id ASC",
                (kind, profile_name),
            ).fetchall()
        return [row[0] for row in rows]

    def delete_unit(
            self,
            kind: str,
            unit_id: str,
    ) -> None:
        """
        Delete one stored unit - STRICT (a missing unit is an error).

        Contract:
            - Registered as the `with_delete_handler` callable.
            - Deletes are strict by mesh law (a half-run retention pass
              must not lie): a zero-row delete raises `KeyError`,
              mirroring the dict-backed prototype's `del rows[...]`.

        Args:
            kind: Unit kind partition.
            unit_id: Kind-specific identity.

        Returns:
            None.

        Raises:
            RuntimeError: If the adapter has been cleaned.
            KeyError: If no row matches (kind, unit_id).
            sqlite3.Error: Propagated on delete failure.
        """
        self.check_cleaned()
        with self._connection() as connection:
            cursor = connection.execute(
                f"DELETE FROM {self._table_name} "
                "WHERE kind = ? AND unit_id = ?",
                (kind, unit_id),
            )
            connection.commit()
            if cursor.rowcount == 0:
                raise KeyError(
                    f"No mesh unit stored for kind={kind!r}, "
                    f"unit_id={unit_id!r} in table "
                    f"{self._table_name!r} - deletes are strict so "
                    "retention passes never miscount."
                )

    # ------------------------------------------------------------------
    # Registration + description
    # ------------------------------------------------------------------

    def register_with(
            self,
            configuration: ExternalPersistenceManagerConfiguration,
    ) -> ExternalPersistenceManagerConfiguration:
        """
        Register all four handlers through the normal fluents.

        Purpose:
            Convenience sugar over the PUBLIC registration surface -
            exactly the calls a user would write by hand
            (`with_store_handler(adapter.store_unit)` etc.); never a
            bypass of the configuration contract.

        Args:
            configuration:
                The mutable (not yet frozen) manager configuration.

        Returns:
            ExternalPersistenceManagerConfiguration: The same
            configuration, for fluent chaining (the caller still owns
            freeze/validate).

        Raises:
            RuntimeError: If the adapter has been cleaned.
            Exception: Propagated from the configuration fluents (e.g.
                a frozen configuration refusing registration).
        """
        self.check_cleaned()
        configuration.with_store_handler(self.store_unit)
        configuration.with_fetch_handler(self.fetch_unit)
        configuration.with_list_units_handler(self.list_units)
        configuration.with_delete_handler(self.delete_unit)
        return configuration

    def describe(self) -> Dict[str, object]:
        """
        Return the adapter's identity as one stamped detached dict.

        Returns:
            Dict[str, object]: {record_version, adapter, database_path,
            table_name}.

        Raises:
            RuntimeError: If the adapter has been cleaned.
        """
        self.check_cleaned()
        return RecordVersion.stamp({
            "adapter": "sqlite_mesh_adapter",
            "database_path": self._database_path,
            "table_name": self._table_name,
        })

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _connection(self) -> sqlite3.Connection:
        """
        Open one fresh connection for one operation.

        Contract:
            - Connection-per-operation: callers use it as a context
              manager; sqlite3's context manager handles the
              transaction, and the connection is closed by the runtime
              when the object drops (no shared connection ever exists,
              so no cross-thread reuse can occur).

        Returns:
            sqlite3.Connection: A fresh connection to the bound file.

        Raises:
            sqlite3.Error: Propagated when the database cannot open.
        """
        return sqlite3.connect(self._database_path)

    def _ensure_schema(self) -> None:
        """
        Create the contract table and its listing index idempotently.

        Contract:
            - Table shape mirrors MeshInterfaceContract.IDENTITY_COLUMNS
              exactly; PRIMARY KEY (kind, unit_id) enforces the mesh's
              per-kind identity model and powers replace-on-store.
            - The (kind, profile_name) index serves list_units.

        Returns:
            None.

        Raises:
            sqlite3.Error: Propagated when schema creation fails.
        """
        with self._connection() as connection:
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {self._table_name} ("
                "kind TEXT NOT NULL, "
                "profile_name TEXT NOT NULL, "
                "unit_id TEXT NOT NULL, "
                "payload TEXT NOT NULL, "
                "PRIMARY KEY (kind, unit_id))"
            )
            connection.execute(
                f"CREATE INDEX IF NOT EXISTS "
                f"idx_{self._table_name}_kind_profile "
                f"ON {self._table_name} (kind, profile_name)"
            )
            connection.commit()
