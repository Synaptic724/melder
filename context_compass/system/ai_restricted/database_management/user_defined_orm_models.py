"""
User-defined ORM models for context_compass SQLite storage.

Purpose
- Reserve a declarative base for user-defined table mappings.
- Keep system/user schemas isolated from user extension schemas.

Contract
- User-defined models must inherit from UserDefinedBase.
- Tables mapped here are stored in the user_defined SQLite database.
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UserDefinedBase(DeclarativeBase):
    """
    Declarative base class for user-defined ORM models.

    Contract:
        - All user-defined ORM models must inherit from this base.
        - Metadata generated from this base targets user_defined.db.
    """


class DbTableRegistry(UserDefinedBase):
    """
    Registry entry describing a user-defined SQLite table.

    Attributes:
        table_name (str): Primary key table name recorded in the registry.
        schema_ref (str | None): Optional schema reference path for the table.
        purpose (str | None): Human-readable purpose for the table.
        notes (str | None): Optional notes for the table entry.
        created_at (str): ISO-8601 creation timestamp.
        updated_at (str): ISO-8601 last update timestamp.

    Contract:
        - One row per table_name.
        - Records are descriptive and do not enforce table creation.
    """

    __tablename__ = "db_table_registry"

    table_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    schema_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)


class DbQueryRegistry(UserDefinedBase):
    """
    Registry entry describing a user-defined SQLite query script.

    Attributes:
        query_name (str): Primary key query name recorded in the registry.
        scope (str): Scope label for the query (system/user/user_defined).
        script_path (str): Relative path to the query script file.
        tables_involved_json (str | None): JSON-encoded list of tables involved.
        operation_type (str | None): High-level operation type description.
        operation_notes (str | None): Detailed operation notes for the query.
        schema_ref (str | None): Optional schema reference path for the query payload.
        purpose (str | None): Human-readable purpose for the query.
        notes (str | None): Optional notes for the query entry.
        payload_schema_json (str | None): JSON schema for query payloads.
        output_schema_json (str | None): JSON schema for query outputs.
        examples_json (str | None): JSON examples for query usage.
        requires_actor (bool): Whether an actor_id is required to execute.
        requires_work_id (bool): Whether a work_id is required to execute.
        enabled (bool): Whether the query is enabled for execution.
        owner_id (str | None): Registry owner identifier.
        created_at (str): ISO-8601 creation timestamp.
        updated_at (str): ISO-8601 last update timestamp.

    Contract:
        - One row per query_name.
        - script_path must be present for query execution.
    """

    __tablename__ = "db_query_registry"

    query_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    script_path: Mapped[str] = mapped_column(Text, nullable=False)
    tables_involved_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    operation_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    operation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_actor: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_work_id: Mapped[bool] = mapped_column(Boolean, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)


class DbActionRegistry(UserDefinedBase):
    """
    Registry entry describing a user-defined SQLite CRUD action script.

    Attributes:
        scope (str): Scope label for the action (system/user/user_defined).
        table_name (str): Target table name for the action.
        operation (str): CRUD operation name (create/read/update/delete).
        action (str): Action name within the operation folder.
        script_path (str): Relative path to the action script file.
        purpose (str | None): Human-readable purpose for the action.
        operation_notes (str | None): Detailed operation notes for the action.
        payload_schema_json (str | None): JSON schema for action payloads.
        output_schema_json (str | None): JSON schema for action outputs.
        examples_json (str | None): JSON examples for action usage.
        requires_actor (bool): Whether an actor_id is required to execute.
        requires_work_id (bool): Whether a work_id is required to execute.
        enabled (bool): Whether the action is enabled for execution.
        owner_id (str | None): Registry owner identifier.
        created_at (str): ISO-8601 creation timestamp.
        updated_at (str): ISO-8601 last update timestamp.

    Contract:
        - One row per (scope, table_name, operation, action).
        - table_name must reference db_table_registry.
        - script_path must be present for action execution.
    """

    __tablename__ = "db_action_registry"

    scope: Mapped[str] = mapped_column(String(32), primary_key=True)
    table_name: Mapped[str] = mapped_column(
        String(256), ForeignKey("db_table_registry.table_name"), primary_key=True
    )
    operation: Mapped[str] = mapped_column(String(32), primary_key=True)
    action: Mapped[str] = mapped_column(String(128), primary_key=True)
    script_path: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    operation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_actor: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_work_id: Mapped[bool] = mapped_column(Boolean, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)


class DbOperationLog(UserDefinedBase):
    """
    Operation log entry for user-defined SQLite mutations.

    Attributes:
        log_id (str): Primary key log identifier.
        transaction_id (str): Transaction identifier for grouped operations.
        request_id (str): Request identifier for the specific operation.
        operation (str): Operation name (seed_config, seed_registry, etc.).
        table_name (str): Target table name.
        record_id (str | None): Optional record identifier touched.
        actor_id (str): Actor identifier for auditing.
        status (str): Status value (ok/error).
        error_code (str | None): Optional error code.
        error_details (str | None): Optional error details payload.
        started_at (str): ISO-8601 start timestamp.
        completed_at (str): ISO-8601 completion timestamp.
        duration_ms (int): Duration in milliseconds.

    Contract:
        - Every row records a single operation attempt.
        - status must reflect whether the operation succeeded.
    """

    __tablename__ = "db_operation_log"

    log_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    operation: Mapped[str] = mapped_column(String(64), nullable=False)
    table_name: Mapped[str] = mapped_column(String(256), nullable=False)
    record_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str] = mapped_column(String(32), nullable=False)
    completed_at: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
