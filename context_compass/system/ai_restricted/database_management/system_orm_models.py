"""
System-scoped ORM models for context_compass SQLite storage.

Purpose
- Define relational table mappings for system-owned data.
- Provide stable, importable models for build and runtime access.

Contract
- Models are declarative and map to SQLite tables in system.db.
- Tables include audit columns where required.
- JSON is not stored at rest for modeled entities.
"""

from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class SystemBase(DeclarativeBase):
    """
    Declarative base class for system-scoped ORM models.

    Contract:
        - All system ORM models must inherit from this base.
        - Metadata generated from this base targets system.db.
    """


class DbTableRegistry(SystemBase):
    """
    Registry entry describing a system SQLite table.

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


class DbQueryRegistry(SystemBase):
    """
    Registry entry describing a system SQLite query script.

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


class DbActionRegistry(SystemBase):
    """
    Registry entry describing a system SQLite CRUD action script.

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


class HookRegistrySystem(SystemBase):
    """
    Registry entry describing a system hook script for command execution.

    Attributes:
        hook_id (str): Stable hook identifier (primary key).
        phase (str): Hook phase (pre, activation, post, on_error).
        order (int): Ordering within the hook phase.
        script_kind (str): Script kind identifier (python for now).
        script_path (str): Relative path to the hook script file.
        entrypoint (str): Entrypoint callable name for python hooks.
        applies_to_json (str | None): JSON-encoded applies_to selectors.
        enabled (bool): Whether the hook is enabled for execution.
        notes (str | None): Optional notes describing the hook.
        owner_id (str | None): Registry owner identifier.
        created_at (str): ISO-8601 creation timestamp.
        updated_at (str): ISO-8601 last update timestamp.

    Contract:
        - One row per hook_id.
        - script_path must be present for hook execution.
        - entrypoint must be present for python hooks.
    """

    __tablename__ = "hook_registry_system"

    hook_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    phase: Mapped[str] = mapped_column(String(32), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    script_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    script_path: Mapped[str] = mapped_column(Text, nullable=False)
    entrypoint: Mapped[str] = mapped_column(String(128), nullable=False)
    applies_to_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)


class DbOperationLog(SystemBase):
    """
    Operation log entry for system SQLite mutations.

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


class CommandRegistrySystem(SystemBase):
    """
    System command registry entry stored in system.db.

    Attributes:
        command_name (str): Stable command identifier (primary key).
        category (str): Command category label.
        entry (str): CLI entry string.
        summary (str): Command summary text.
        requires_certification (bool): Whether certification is required.
        requires_work_id (bool): Whether a work id is required.
        feature_flag (str | None): Feature flag gate for the command.
        notes (str | None): Optional notes describing behavior.
        spec_json (str | None): JSON-serialized spec payload.
        registry_schema_version (int): Registry schema version.
        registry_generated_at (str | None): Registry generation timestamp.
        registry_updated_at (str | None): Registry update timestamp.

    Contract:
        - One row per command_name.
        - spec_json is minified JSON or null when absent.
    """

    __tablename__ = "command_registry_system"

    command_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    entry: Mapped[str] = mapped_column(String(256), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    requires_certification: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_work_id: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feature_flag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    spec_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    registry_schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    registry_generated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    registry_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)


class ConfigContextCompassCore(SystemBase):
    """
    Core configuration record for context_compass feature flags and work mode.

    Attributes:
        config_id (int): Primary key identifier for the config set.
        schema_version (int): Schema version of the configuration payload.
        work_mode (str): Work mode setting (hard or soft).
        notes (str | None): Optional operator notes.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        flags (list[ConfigContextCompassFlag]): Feature flag rows.
        skill_rules (list[ConfigContextCompassSkillRule]): Skill disable rules.

    Contract:
        - One row per config_id.
        - Child tables must reference config_id.
    """

    __tablename__ = "config_context_compass_core"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    work_mode: Mapped[str] = mapped_column(String(16), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    flags: Mapped[List["ConfigContextCompassFlag"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )
    skill_rules: Mapped[List["ConfigContextCompassSkillRule"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )


class ConfigContextCompassFlag(SystemBase):
    """
    Feature flag entry for the context_compass configuration.

    Attributes:
        config_id (int): Parent config identifier.
        feature_name (str): Feature flag name.
        enabled (bool): Whether the feature is enabled.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigContextCompassCore): Parent configuration record.

    Contract:
        - Primary key is (config_id, feature_name).
        - feature_name values are unique per config_id.
    """

    __tablename__ = "config_context_compass_flags"

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_context_compass_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_name: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigContextCompassCore] = relationship(back_populates="flags")


class ConfigContextCompassSkillRule(SystemBase):
    """
    Skill disable rule for the context_compass configuration.

    Attributes:
        config_id (int): Parent config identifier.
        position (int | None): Optional ordering index for the rule list.
        rule_type (str): Rule type (id or prefix).
        rule_value (str): Rule value (skill id or prefix).
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigContextCompassCore): Parent configuration record.

    Contract:
        - Primary key is (config_id, rule_type, rule_value).
        - rule_type is constrained to "id" or "prefix".
        - position may be None if ordering is not required.
    """

    __tablename__ = "config_context_compass_skill_rules"
    __table_args__ = (
        CheckConstraint("rule_type IN ('id', 'prefix')", name="ck_skill_rule_type"),
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_context_compass_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_type: Mapped[str] = mapped_column(String(16), primary_key=True)
    rule_value: Mapped[str] = mapped_column(String(256), primary_key=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigContextCompassCore] = relationship(back_populates="skill_rules")


class ConfigIgnoreCore(SystemBase):
    """
    Core ignore configuration record for scanning rules.

    Attributes:
        config_id (int): Primary key identifier for the config set.
        schema_version (int): Schema version of the configuration payload.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        rules (list[ConfigIgnoreRule]): Ignore rule rows.

    Contract:
        - One row per config_id.
        - Child rules reference config_id.
    """

    __tablename__ = "config_ignore_core"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    rules: Mapped[List["ConfigIgnoreRule"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )


class ConfigIgnoreRule(SystemBase):
    """
    Ignore rule entry for the context_compass ignore configuration.

    Attributes:
        config_id (int): Parent config identifier.
        rule_type (str): Rule type (include_glob, exclude_glob, include_dir,
            exclude_dir, or code_extension).
        rule_value (str): Rule value string.
        position (int | None): Optional ordering index for the rule list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigIgnoreCore): Parent configuration record.

    Contract:
        - Primary key is (config_id, rule_type, rule_value).
        - rule_type is constrained to the allowed ignore rule types.
        - position may be None if ordering is not required.
    """

    __tablename__ = "config_ignore_rules"
    __table_args__ = (
        CheckConstraint(
            "rule_type IN ("
            "'include_glob', "
            "'exclude_glob', "
            "'include_dir', "
            "'exclude_dir', "
            "'code_extension'"
            ")",
            name="ck_ignore_rule_type",
        ),
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_ignore_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_type: Mapped[str] = mapped_column(String(32), primary_key=True)
    rule_value: Mapped[str] = mapped_column(String(256), primary_key=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigIgnoreCore] = relationship(back_populates="rules")


class ConfigSourceRootsCore(SystemBase):
    """
    Core source root configuration record for prod/test roots.

    Attributes:
        config_id (int): Primary key identifier for the config set.
        schema_version (int): Schema version of the configuration payload.
        notes (str | None): Optional operator notes.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        roots (list[ConfigSourceRootsEntry]): Source root rows.

    Contract:
        - One row per config_id.
        - Child rows reference config_id and classify root_type.
    """

    __tablename__ = "config_source_roots_core"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    roots: Mapped[List["ConfigSourceRootsEntry"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )


class ConfigSourceRootsEntry(SystemBase):
    """
    Source root entry for prod/test root classification.

    Attributes:
        config_id (int): Parent config identifier.
        root_type (str): Root type (prod or test).
        root_path (str): Root path entry.
        position (int | None): Optional ordering index for the root list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigSourceRootsCore): Parent configuration record.

    Contract:
        - Primary key is (config_id, root_type, root_path).
        - root_type is constrained to "prod" or "test".
    """

    __tablename__ = "config_source_roots_entries"
    __table_args__ = (
        CheckConstraint("root_type IN ('prod', 'test')", name="ck_source_root_type"),
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_source_roots_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    root_type: Mapped[str] = mapped_column(String(16), primary_key=True)
    root_path: Mapped[str] = mapped_column(String(512), primary_key=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigSourceRootsCore] = relationship(back_populates="roots")


class ConfigLanguagesCore(SystemBase):
    """
    Core language configuration record for extension and directory mappings.

    Attributes:
        config_id (int): Primary key identifier for the config set.
        schema_version (int): Schema version of the configuration payload.
        default_language (str): Default language when no match exists.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        extensions (list[ConfigLanguagesExtension]): Extension mapping rows.
        directory_hints (list[ConfigLanguagesDirectoryHint]): Directory hint rows.

    Contract:
        - One row per config_id.
        - Child rows reference config_id.
    """

    __tablename__ = "config_languages_core"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    default_language: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    extensions: Mapped[List["ConfigLanguagesExtension"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )
    directory_hints: Mapped[List["ConfigLanguagesDirectoryHint"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )


class ConfigLanguagesExtension(SystemBase):
    """
    Extension-to-language mapping entry for language configuration.

    Attributes:
        config_id (int): Parent config identifier.
        extension (str): File extension key (without leading dot).
        language (str): Language identifier for the extension.
        position (int | None): Optional ordering index for the mapping list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigLanguagesCore): Parent configuration record.

    Contract:
        - Primary key is (config_id, extension).
        - extension must be a non-empty string.
    """

    __tablename__ = "config_languages_extensions"
    __table_args__ = (
        CheckConstraint("extension <> ''", name="ck_languages_extension"),
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_languages_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    extension: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigLanguagesCore] = relationship(back_populates="extensions")


class ConfigLanguagesDirectoryHint(SystemBase):
    """
    Directory hint mapping entry for language configuration.

    Attributes:
        config_id (int): Parent config identifier.
        hint_pattern (str): Directory hint or glob pattern.
        language (str): Language identifier for the hint.
        position (int | None): Optional ordering index for the mapping list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigLanguagesCore): Parent configuration record.

    Contract:
        - Primary key is (config_id, hint_pattern).
        - hint_pattern must be a non-empty string.
    """

    __tablename__ = "config_languages_directory_hints"
    __table_args__ = (
        CheckConstraint("hint_pattern <> ''", name="ck_languages_hint_pattern"),
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_languages_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    hint_pattern: Mapped[str] = mapped_column(String(256), primary_key=True)
    language: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigLanguagesCore] = relationship(back_populates="directory_hints")


class ConfigPoliciesCore(SystemBase):
    """
    Core policy configuration record for context_compass runtime behavior.

    Attributes:
        config_id (int): Primary key identifier for the policy set.
        schema_version (int): Schema version of the policies payload.
        architecture_context_faulty_ratio_threshold (float): Faulty ratio threshold.
        architecture_context_good_ratio_threshold (float): Good ratio threshold.
        architecture_context_stale_ratio_threshold (float): Stale ratio threshold.
        ci_fail_on_needs_review (bool): Whether CI should fail on needs_review.
        context_profiles_max_bytes_per_profile (int): Max bytes per profile.
        context_profiles_max_items_per_profile (int): Max items per profile.
        context_profiles_optimize_score_threshold (float): Optimize score cutoff.
        context_profiles_popular_usage_threshold (int): Popular usage cutoff.
        context_profiles_prune_score_threshold (float): Prune score cutoff.
        dir_review_every_n_scans_default (int): Directory review scan interval.
        lease_heartbeat_seconds (int): Lease heartbeat interval in seconds.
        lease_ttl_seconds (int): Lease TTL in seconds.
        lock_wait_seconds (int): Lock wait duration in seconds.
        max_task_attempts (int): Max attempts per task.
        review_every_n_scans_default (int): File review scan interval.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        ci_fail_states (list[ConfigPoliciesCiFailState]): CI fail state rows.

    Contract:
        - One row per config_id.
        - Ratio thresholds are constrained to [0, 1].
        - Interval counters are non-negative.
        - Child rows reference config_id.
    """

    __tablename__ = "config_policies_core"
    __table_args__ = (
        CheckConstraint(
            "architecture_context_faulty_ratio_threshold BETWEEN 0 AND 1",
            name="ck_policies_faulty_ratio",
        ),
        CheckConstraint(
            "architecture_context_good_ratio_threshold BETWEEN 0 AND 1",
            name="ck_policies_good_ratio",
        ),
        CheckConstraint(
            "architecture_context_stale_ratio_threshold BETWEEN 0 AND 1",
            name="ck_policies_stale_ratio",
        ),
        CheckConstraint("context_profiles_max_bytes_per_profile >= 1", name="ck_policies_max_bytes"),
        CheckConstraint("context_profiles_max_items_per_profile >= 1", name="ck_policies_max_items"),
        CheckConstraint(
            "context_profiles_optimize_score_threshold >= 0",
            name="ck_policies_optimize_threshold",
        ),
        CheckConstraint(
            "context_profiles_popular_usage_threshold >= 0",
            name="ck_policies_popular_usage",
        ),
        CheckConstraint(
            "context_profiles_prune_score_threshold >= 0",
            name="ck_policies_prune_threshold",
        ),
        CheckConstraint("dir_review_every_n_scans_default >= 0", name="ck_policies_dir_review"),
        CheckConstraint("lease_heartbeat_seconds >= 1", name="ck_policies_lease_heartbeat"),
        CheckConstraint("lease_ttl_seconds >= 1", name="ck_policies_lease_ttl"),
        CheckConstraint("lock_wait_seconds >= 0", name="ck_policies_lock_wait"),
        CheckConstraint("max_task_attempts >= 0", name="ck_policies_max_task_attempts"),
        CheckConstraint("review_every_n_scans_default >= 0", name="ck_policies_review_every_n"),
    )

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    architecture_context_faulty_ratio_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    architecture_context_good_ratio_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    architecture_context_stale_ratio_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    ci_fail_on_needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False)
    context_profiles_max_bytes_per_profile: Mapped[int] = mapped_column(Integer, nullable=False)
    context_profiles_max_items_per_profile: Mapped[int] = mapped_column(Integer, nullable=False)
    context_profiles_optimize_score_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    context_profiles_popular_usage_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    context_profiles_prune_score_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    dir_review_every_n_scans_default: Mapped[int] = mapped_column(Integer, nullable=False)
    lease_heartbeat_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    lease_ttl_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    lock_wait_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    max_task_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    review_every_n_scans_default: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    ci_fail_states: Mapped[List["ConfigPoliciesCiFailState"]] = relationship(
        back_populates="config",
        cascade="all, delete-orphan",
    )


class ConfigPoliciesCiFailState(SystemBase):
    """
    CI fail-state entry for policy configuration.

    Attributes:
        config_id (int): Parent config identifier.
        state (str): CI fail state value.
        position (int): Ordering index for the state list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.
        config (ConfigPoliciesCore): Parent policy configuration record.

    Contract:
        - Primary key is (config_id, state).
        - position must be >= 1 when provided.
    """

    __tablename__ = "config_policies_ci_fail_states"
    __table_args__ = (
        CheckConstraint("position >= 1", name="ck_policies_ci_fail_position"),
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("config_policies_core.config_id", ondelete="CASCADE"),
        primary_key=True,
    )
    state: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)

    config: Mapped[ConfigPoliciesCore] = relationship(back_populates="ci_fail_states")


class BranchRegistry(SystemBase):
    """
    System registry entry for known branches.

    Attributes:
        branch_name (str): Branch identifier (primary key).
        schema_version (int): Branch registry schema version.
        status (str): Branch status (active, archived, disabled).
        notes (str | None): Optional operator notes.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per branch_name.
        - status must be one of the allowed enum values.
    """

    __tablename__ = "branch_registry"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'archived', 'disabled')",
            name="ck_branch_registry_status",
        ),
    )

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class EnvironmentState(SystemBase):
    """
    Recorded environment metadata for context_compass runtime checks.

    Attributes:
        record_id (str): Stable primary key (e.g., "current").
        schema_version (int): Schema version of the environment payload.
        checked_at (str): ISO-8601 timestamp when the check ran.
        os_name (str): Operating system name.
        os_platform (str): Platform identifier.
        os_release (str): OS release.
        os_version (str): OS version string.
        os_machine (str): Machine architecture string.
        os_processor (str): Processor description string.
        os_is_windows (bool): Windows flag.
        os_is_linux (bool): Linux flag.
        os_is_macos (bool): macOS flag.
        python_available (bool): Whether Python is available.
        python_executable (str | None): Python executable path if present.
        python_version (str | None): Python version string if available.
        python_version_major (int): Major version.
        python_version_minor (int): Minor version.
        python_version_patch (int): Patch version.
        python_implementation (str | None): Python implementation name.
        tools_git_available (bool): Git availability flag.
        tools_git_path (str | None): Git executable path.
        tools_rg_available (bool): ripgrep availability flag.
        tools_rg_path (str | None): ripgrep executable path.
        tools_pytest_available (bool): pytest availability flag.
        tools_pytest_path (str | None): pytest executable path.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per record_id.
        - Tool availability is stored as explicit columns.
    """

    __tablename__ = "environment_state"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    checked_at: Mapped[str] = mapped_column(String(32), nullable=False)
    os_name: Mapped[str] = mapped_column(String(64), nullable=False)
    os_platform: Mapped[str] = mapped_column(String(64), nullable=False)
    os_release: Mapped[str] = mapped_column(String(64), nullable=False)
    os_version: Mapped[str] = mapped_column(String(128), nullable=False)
    os_machine: Mapped[str] = mapped_column(String(64), nullable=False)
    os_processor: Mapped[str] = mapped_column(String(128), nullable=False)
    os_is_windows: Mapped[bool] = mapped_column(Boolean, nullable=False)
    os_is_linux: Mapped[bool] = mapped_column(Boolean, nullable=False)
    os_is_macos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    python_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    python_executable: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    python_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    python_version_major: Mapped[int] = mapped_column(Integer, nullable=False)
    python_version_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    python_version_patch: Mapped[int] = mapped_column(Integer, nullable=False)
    python_implementation: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tools_git_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tools_git_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    tools_rg_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tools_rg_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    tools_pytest_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tools_pytest_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class LeaseLock(SystemBase):
    """
    Centralized lease record for resource locks.

    Attributes:
        lock_id (str): Deterministic lock identifier (primary key).
        repo_id (str): Repository identifier for scoping.
        resource_type (str): Resource type label (path or logical).
        resource_key (str): Normalized resource identifier.
        owner_id (str): Current lock owner.
        schema_version (int): Lease schema version.
        work_id (str | None): Optional work id for traceability.
        ticket_id (str | None): Optional ticket id hint for traceability.
        lock_group_id (str | None): Optional lock bundle identifier.
        created_at (str): Lease creation timestamp.
        heartbeat_at (str): Lease heartbeat timestamp.
        expires_at (str): Lease expiration timestamp.
        updated_at (str): ISO-8601 update timestamp.
        created_by (str): Actor identifier that created the record.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Uniqueness is enforced on (repo_id, resource_type, resource_key).
        - re-entrant acquisition is allowed for the same owner_id.
    """

    __tablename__ = "lease_locks"
    __table_args__ = (
        UniqueConstraint(
            "repo_id",
            "resource_type",
            "resource_key",
            name="uq_lease_lock_resource",
        ),
    )

    lock_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    repo_id: Mapped[str] = mapped_column(String(256), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_key: Mapped[str] = mapped_column(String(2048), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(128), nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    work_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ticket_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lock_group_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    heartbeat_at: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)
