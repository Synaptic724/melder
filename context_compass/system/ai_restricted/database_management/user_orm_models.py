"""
User-scoped ORM models for context_compass SQLite storage.

Purpose
- Define relational table mappings for user-owned data.
- Provide stable, importable models for build and runtime access.

Contract
- Models are declarative and map to SQLite tables in user.db.
- Tables include audit columns where required.
- JSON is avoided for structured ctx artifacts when practical.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UserBase(DeclarativeBase):
    """
    Declarative base class for user-scoped ORM models.

    Contract:
        - All user ORM models must inherit from this base.
        - Metadata generated from this base targets user.db.
    """


class DbTableRegistry(UserBase):
    """
    Registry entry describing a user SQLite table.

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


class DbQueryRegistry(UserBase):
    """
    Registry entry describing a user SQLite query script.

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


class DbActionRegistry(UserBase):
    """
    Registry entry describing a user SQLite CRUD action script.

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


class HookRegistryUser(UserBase):
    """
    Registry entry describing a user hook script for command execution.

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

    __tablename__ = "hook_registry_user"

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


class DbOperationLog(UserBase):
    """
    Operation log entry for user SQLite mutations.

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


class CommandRegistryUser(UserBase):
    """
    User command registry entry stored in user.db.

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

    __tablename__ = "command_registry_user"

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


class ConfigCtxArtifactOutputCore(UserBase):
    """
    Configuration record for ctx artifact output behavior.

    Attributes:
        config_id (int): Primary key identifier for the config set.
        schema_version (int): Schema version of the configuration payload.
        emit_to_repo (bool): Master toggle for emitting ctx JSON to the target repo.
        emit_file_ctx (bool): Emit file_ctx artifacts when enabled.
        emit_dir_ctx (bool): Emit dir_ctx artifacts when enabled.
        emit_architecture_context (bool): Emit architecture_context artifacts when enabled.
        emit_component_contexts (bool): Emit component_contexts artifacts when enabled.
        notes (str | None): Optional operator notes.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per config_id.
        - Feature toggles are explicit booleans.
    """

    __tablename__ = "config_ctx_artifact_output_core"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    emit_to_repo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    emit_file_ctx: Mapped[bool] = mapped_column(Boolean, nullable=False)
    emit_dir_ctx: Mapped[bool] = mapped_column(Boolean, nullable=False)
    emit_architecture_context: Mapped[bool] = mapped_column(Boolean, nullable=False)
    emit_component_contexts: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class CurrentBranch(UserBase):
    """
    Active branch pointer stored in user.db.

    Attributes:
        record_id (str): Stable record identifier (e.g., "current").
        schema_version (int): Schema version for the payload.
        branch_name (str): Active branch name.
        notes (str | None): Optional operator notes.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per record_id.
        - branch_name is required and non-empty.
    """

    __tablename__ = "current_branch"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    branch_name: Mapped[str] = mapped_column(String(128), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class RepoState(UserBase):
    """
    Branch-scoped repository state stored in a shared repo_state table.

    Attributes:
        branch_name (str): Branch identifier for the repo_state row.
        schema_version (int): Schema version for the repo_state payload.
        repo_id (str | None): Optional repository identifier.
        repo_root (str): Repository root path.
        git_head (str | None): Git HEAD value captured at last assessment.
        scan_counter (int): Total scan count for the branch.
        last_scan_id (str | None): Last scan identifier.
        last_scan_at (str | None): Timestamp for the last scan.
        scanner_version (str | None): Scanner version for last scan.
        template_file_ctx_version (str | None): File ctx template version.
        template_dir_ctx_version (str | None): Dir ctx template version.
        lifecycle_stage (str | None): Lifecycle stage name.
        lifecycle_assessment (str | None): Lifecycle assessment notes.
        lifecycle_confidence (float | None): Lifecycle confidence score.
        lifecycle_assessed_at (str | None): Timestamp for lifecycle assessment.
        tooling_policy_mode (str | None): Tooling policy mode (normal/restricted).
        tooling_policy_notes (str | None): Tooling policy notes.
        tooling_policy_updated_at (str | None): Tooling policy update timestamp.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per branch_name in user.db.
        - Child disabled features live in repo_state_tooling_disabled_features.
    """

    __tablename__ = "repo_state"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    repo_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    repo_root: Mapped[str] = mapped_column(String(1024), nullable=False)
    git_head: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scan_counter: Mapped[int] = mapped_column(Integer, nullable=False)
    last_scan_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_scan_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    scanner_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_file_ctx_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_dir_ctx_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lifecycle_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lifecycle_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    lifecycle_assessed_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tooling_policy_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tooling_policy_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tooling_policy_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class RepoStateToolingDisabledFeature(UserBase):
    """
    Disabled feature row for repo_state tooling_policy.

    Attributes:
        branch_name (str): Branch identifier owning the feature entry.
        position (int): Ordering position for the disabled feature list.
        feature_name (str): Feature name disabled by tooling policy.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, position).
        - branch_name references repo_state.branch_name.
    """

    __tablename__ = "repo_state_tooling_disabled_features"
    __table_args__ = (
        UniqueConstraint("branch_name", "feature_name", name="uq_repo_state_disabled_feature"),
    )

    branch_name: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("repo_state.branch_name", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    feature_name: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ContextProfilesCore(UserBase):
    """
    Core context_profiles record for a branch.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        schema_version (int): Schema version of the payload.
        rules_version (str | None): Rules version tag for the profiles.
        limits_max_items_per_profile (int): Max items per profile limit.
        limits_max_bytes_per_profile (int): Max bytes per profile limit.
        artifact_updated_at (str | None): Payload updated_at value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is branch_name.
        - Child profile rows live in context_profile_items.
    """

    __tablename__ = "context_profiles"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    rules_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    limits_max_items_per_profile: Mapped[int] = mapped_column(Integer, nullable=False)
    limits_max_bytes_per_profile: Mapped[int] = mapped_column(Integer, nullable=False)
    artifact_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ContextProfileItem(UserBase):
    """
    Context profile entry for a branch.

    Attributes:
        branch_name (str): Branch identifier owning the profile.
        profile_name (str): Profile name identifier.
        position (int): Ordering position for profile lists.
        score (float): Profile relevance score.
        grade (str): Review grade for the profile.
        usage_count (int): Usage counter for profile reads.
        last_used_at (str | None): Timestamp of last profile use.
        last_review_at (str | None): Timestamp of last profile review.
        last_review_notes (str | None): Optional review notes.
        last_reviewed_by (str | None): Reviewer identifier.
        review_count_excellent (int): Count of excellent reviews.
        review_count_good (int): Count of good reviews.
        review_count_ok (int): Count of ok reviews.
        review_count_poor (int): Count of poor reviews.
        review_count_bad (int): Count of bad reviews.
        reason (str): Reason string for the profile.
        size_bytes (int): Total size of profile ctx items.
        freshness_state (str): Freshness state for the profile.
        inputs_hash (str | None): Inputs hash for profile drift detection.
        last_checked_at (str | None): Timestamp of last input evaluation.
        profile_updated_at (str | None): Profile updated_at payload value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, profile_name).
        - position preserves payload ordering for profiles.
        - Path rows live in context_profile_item_paths.
        - Staleness rows live in context_profile_item_staleness_reasons.
    """

    __tablename__ = "context_profile_items"
    __table_args__ = (
        UniqueConstraint("branch_name", "profile_name", name="uq_context_profile_items_profile"),
    )

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    profile_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(32), nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False)
    last_used_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_review_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    review_count_excellent: Mapped[int] = mapped_column(Integer, nullable=False)
    review_count_good: Mapped[int] = mapped_column(Integer, nullable=False)
    review_count_ok: Mapped[int] = mapped_column(Integer, nullable=False)
    review_count_poor: Mapped[int] = mapped_column(Integer, nullable=False)
    review_count_bad: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(32), nullable=False)
    inputs_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_checked_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    profile_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ContextProfileItemPath(UserBase):
    """
    Path entry for a context profile.

    Attributes:
        branch_name (str): Branch identifier owning the profile.
        profile_name (str): Profile name identifier.
        position (int): Ordering position for the path list.
        path (str): Repo-relative ctx artifact path.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, profile_name, position).
        - position preserves payload ordering.
    """

    __tablename__ = "context_profile_item_paths"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    profile_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ContextProfileItemStalenessReason(UserBase):
    """
    Staleness reason entry for a context profile.

    Attributes:
        branch_name (str): Branch identifier owning the profile.
        profile_name (str): Profile name identifier.
        position (int): Ordering position for the reason list.
        reason (str): Staleness reason value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, profile_name, position).
        - position preserves payload ordering.
    """

    __tablename__ = "context_profile_item_staleness_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    profile_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanRegistry(UserBase):
    """
    Core scan registry record for a single scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier for the run.
        schema_version (int): Scan payload schema version.
        scanned_at (str): Timestamp when the scan executed.
        repo_root (str): Repository root path for the scan.
        repo_id (str | None): Optional repository identifier.
        git_head (str | None): Optional git head sha.
        scanner_version (str): Scanner version identifier.
        files_scanned (int): Count of scanned files.
        dirs_scanned (int): Count of scanned directories.
        files_skipped_init (int): Count of skipped __init__.py files.
        files_skipped_excluded (int): Count of skipped excluded files.
        files_skipped_unknown (int): Count of skipped non-code files.
        tasks_emitted (int): Count of tasks emitted.
        missing (int): Count of missing ctx records.
        stale (int): Count of stale ctx records.
        needs_review (int): Count of review-needed ctx records.
        blocked (int): Count of blocked ctx records.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id).
        - Summary counters are stored as explicit columns.
    """

    __tablename__ = "scan_registry"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    scanned_at: Mapped[str] = mapped_column(String(32), nullable=False)
    repo_root: Mapped[str] = mapped_column(String(1024), nullable=False)
    repo_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    git_head: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scanner_version: Mapped[str] = mapped_column(String(64), nullable=False)
    files_scanned: Mapped[int] = mapped_column(Integer, nullable=False)
    dirs_scanned: Mapped[int] = mapped_column(Integer, nullable=False)
    files_skipped_init: Mapped[int] = mapped_column(Integer, nullable=False)
    files_skipped_excluded: Mapped[int] = mapped_column(Integer, nullable=False)
    files_skipped_unknown: Mapped[int] = mapped_column(Integer, nullable=False)
    tasks_emitted: Mapped[int] = mapped_column(Integer, nullable=False)
    missing: Mapped[int] = mapped_column(Integer, nullable=False)
    stale: Mapped[int] = mapped_column(Integer, nullable=False)
    needs_review: Mapped[int] = mapped_column(Integer, nullable=False)
    blocked: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanIgnoreConfigCore(UserBase):
    """
    Effective ignore configuration snapshot for a scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        schema_version (int): Ignore config schema version.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id).
        - Rule rows live in scan_ignore_rules.
    """

    __tablename__ = "scan_ignore_config_core"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanIgnoreRule(UserBase):
    """
    Effective ignore rule entry for a scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        position (int): Ordering position for the rule list.
        rule_type (str): Rule type (include_glob/exclude_glob/include_dir/exclude_dir/code_extension).
        rule_value (str): Rule value string.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, position).
    """

    __tablename__ = "scan_ignore_rules"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_value: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanFileItem(UserBase):
    """
    File-level scan entry for a scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        file_path (str): Repo-relative file path.
        ctx_path (str): Repo-relative ctx artifact path.
        state (str): Freshness state for the file ctx.
        position (int): Ordering position for the file list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, file_path).
        - position preserves output ordering for scan reports.
    """

    __tablename__ = "scan_file_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanFileItemReason(UserBase):
    """
    Staleness reason entry for a scan file record.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        file_path (str): Repo-relative file path.
        position (int): Ordering position for the reason list.
        reason (str): Reason string for the file entry.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, file_path, position).
    """

    __tablename__ = "scan_file_item_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanDirectoryItem(UserBase):
    """
    Directory-level scan entry for a scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        dir_path (str): Repo-relative directory path.
        ctx_path (str): Repo-relative ctx artifact path.
        state (str): Freshness state for the directory ctx.
        position (int): Ordering position for the directory list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, dir_path).
        - position preserves output ordering for scan reports.
    """

    __tablename__ = "scan_directory_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanDirectoryItemReason(UserBase):
    """
    Staleness reason entry for a scan directory record.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        dir_path (str): Repo-relative directory path.
        position (int): Ordering position for the reason list.
        reason (str): Reason string for the directory entry.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, dir_path, position).
    """

    __tablename__ = "scan_directory_item_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanArchitectureItem(UserBase):
    """
    Architecture/component scan entry for a scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        position (int): Ordering position for the architecture list.
        path (str): Reference path for the artifact.
        kind (str): Artifact kind identifier.
        state (str): Freshness state for the artifact.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, position).
        - path/kind identify the artifact reference.
    """

    __tablename__ = "scan_architecture_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    kind: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanArchitectureItemReason(UserBase):
    """
    Staleness reason entry for an architecture/component scan record.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        item_position (int): Ordering position of the parent item.
        position (int): Ordering position for the reason list.
        reason (str): Reason string for the artifact entry.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, item_position, position).
    """

    __tablename__ = "scan_architecture_item_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    item_position: Mapped[int] = mapped_column(Integer, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanEmittedTask(UserBase):
    """
    Emitted task entry for a scan run.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        position (int): Ordering position for the task list.
        work_id (str): Work item identifier.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, position).
    """

    __tablename__ = "scan_emitted_tasks"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_id: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanErrorRef(UserBase):
    """
    Scan-level error reference entry.

    Attributes:
        branch_name (str): Branch identifier owning the scan.
        scan_id (str): Scan identifier.
        position (int): Ordering position for the error list.
        error_id (str): Error record identifier.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, scan_id, position).
    """

    __tablename__ = "scan_error_refs"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    error_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ScanErrorRecord(UserBase):
    """
    Scan error record entry persisted from scan failures.

    Attributes:
        branch_name (str): Branch identifier owning the error record.
        error_id (str): Error identifier.
        schema_version (int): Error record schema version.
        occurred_at (str): Timestamp when the error occurred.
        owner_id (str): Actor identifier that owns the error record.
        work_id (str | None): Optional work item identifier.
        target_path (str | None): Optional target path for the error.
        ctx_path (str | None): Optional ctx path for the error.
        category (str): Error category identifier.
        message (str): Error message text.
        details_json (str): JSON-encoded details payload.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, error_id).
        - details_json stores the serialized details object.
    """

    __tablename__ = "scan_error_records"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    error_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(128), nullable=False)
    work_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    target_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ctx_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtx(UserBase):
    """
    Core file_ctx record for a scanned file.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        ctx_path (str): Repo-relative ctx artifact path.
        language (str): Language identifier for the file.
        module (str | None): Optional module path for the file.
        schema_version (int): file_ctx schema version.
        freshness_state (str): Freshness state (missing/stale/fresh/needs_review/blocked).
        last_scan_id (str | None): Last scan identifier.
        last_scanned_at (str | None): Timestamp of last scan.
        review_every_n_scans (int | None): Review cadence.
        scan_counter (int | None): Scan counter at last update.
        last_review_scan_id (str | None): Scan id for last review.
        code_hash_sha256 (str | None): Code hash checksum.
        ctx_semantic_hash_sha256 (str | None): Semantic hash checksum.
        template_version (str | None): Template version identifier.
        analyzer_version (str | None): Analyzer version identifier.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path).
        - ctx_path is unique per branch_name.
    """

    __tablename__ = "file_ctx"
    __table_args__ = (
        UniqueConstraint("branch_name", "ctx_path", name="uq_file_ctx_ctx_path"),
    )

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    language: Mapped[str] = mapped_column(String(64), nullable=False)
    module: Mapped[str | None] = mapped_column(String(256), nullable=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(32), nullable=False)
    last_scan_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_scanned_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    review_every_n_scans: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scan_counter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_review_scan_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ctx_semantic_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    analyzer_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxStalenessReason(UserBase):
    """
    Staleness reason entry for a file_ctx record.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        position (int): Ordering position for the reason list.
        reason (str): Staleness reason value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, position).
        - position preserves reason ordering.
    """

    __tablename__ = "file_ctx_staleness_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentSummary(UserBase):
    """
    Summary block for a file_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        one_liner (str): One-line summary.
        detail (str): Detailed summary.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path).
    """

    __tablename__ = "file_ctx_agent_summary"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    one_liner: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentRole(UserBase):
    """
    Core role_in_system block for a file_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        layer (str): System layer identifier.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path).
    """

    __tablename__ = "file_ctx_agent_role"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    layer: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentRoleItem(UserBase):
    """
    List item for role_in_system arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Role item type (responsibilities/non_goals/invariants/pitfalls).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_role_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentPublicSurfaceItem(UserBase):
    """
    List item for public_surface arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Public surface item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers entrypoints/exports/interfaces_* values.
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_public_surface_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentBehavioralContract(UserBase):
    """
    Core behavioral_contract block for a file_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        error_logging (str): Logging contract description for error_model.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path).
        - error_logging stores error_model.logging.
    """

    __tablename__ = "file_ctx_agent_behavioral_contract"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    error_logging: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentBehavioralContractItem(UserBase):
    """
    List item for behavioral_contract arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Contract item type (inputs/outputs/side_effects).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_behavioral_contract_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentErrorModelItem(UserBase):
    """
    List item for error_model arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Error model item type (raises/retryable).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_error_model_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentDependencyItem(UserBase):
    """
    List item for dependencies arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Dependency item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers internal_imports/external_imports/runtime_couplings/depends_on_files.
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_dependencies_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentDependents(UserBase):
    """
    Core dependents block for a file_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        notes (str): Notes describing usage or constraints.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path).
    """

    __tablename__ = "file_ctx_agent_dependents"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentDependentItem(UserBase):
    """
    List item for dependents arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Dependents item type (used_by_files/used_by_dirs).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_dependents_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentLifecycle(UserBase):
    """
    Core lifecycle block for a file_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        construction (str): Construction notes.
        ownership (str): Ownership notes.
        cleanup_has_cleanup (bool): Whether cleanup is required.
        threading_thread_safe (bool): Whether the module is thread-safe.
        threading_async (bool): Whether async usage is supported.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path).
        - cleanup_has_cleanup reflects lifecycle.cleanup.has_cleanup.
    """

    __tablename__ = "file_ctx_agent_lifecycle"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    construction: Mapped[str] = mapped_column(Text, nullable=False)
    ownership: Mapped[str] = mapped_column(Text, nullable=False)
    cleanup_has_cleanup: Mapped[bool] = mapped_column(Boolean, nullable=False)
    threading_thread_safe: Mapped[bool] = mapped_column(Boolean, nullable=False)
    threading_async: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentLifecycleItem(UserBase):
    """
    List item for lifecycle arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Lifecycle item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers cleanup_method_names/cleanup_order_constraints/threading_locks.
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_lifecycle_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentTestingItem(UserBase):
    """
    List item for testing arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Testing item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers test_types/commands/mocks/fixtures/coverage_expectations.
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_testing_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentExampleSnippet(UserBase):
    """
    Usage snippet entry for a file_ctx agent example.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        position (int): Ordering position for the snippet list.
        title (str): Snippet title.
        code (str): Snippet code.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, position).
    """

    __tablename__ = "file_ctx_agent_examples_snippets"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentExampleItem(UserBase):
    """
    List item for example arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Example item type (integration_flow).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_examples_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxAgentChangeRiskItem(UserBase):
    """
    List item for change_risk arrays on file_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        item_type (str): Change risk item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers review_triggers/risky_changes/safe_changes.
        - Primary key is (branch_name, file_path, item_type, position).
    """

    __tablename__ = "file_ctx_agent_change_risk_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxFactSymbol(UserBase):
    """
    Symbol fact entry for a file_ctx record.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        position (int): Ordering position for the symbol list.
        name (str): Symbol name.
        kind (str | None): Symbol kind (class/function/etc).
        signature (str | None): Symbol signature when available.
        docstring (str | None): Symbol docstring excerpt.
        lineno_start (int | None): Starting line number.
        lineno_end (int | None): Ending line number.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, position).
    """

    __tablename__ = "file_ctx_facts_symbols"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    kind: Mapped[str | None] = mapped_column(String(64), nullable=True)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    docstring: Mapped[str | None] = mapped_column(Text, nullable=True)
    lineno_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lineno_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxFactImport(UserBase):
    """
    Import fact entry for a file_ctx record.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        position (int): Ordering position for the import list.
        value (str): Import value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, position).
    """

    __tablename__ = "file_ctx_facts_imports"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class FileCtxFactExport(UserBase):
    """
    Export fact entry for a file_ctx record.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        file_path (str): Repo-relative file path.
        position (int): Ordering position for the export list.
        value (str): Export value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, file_path, position).
    """

    __tablename__ = "file_ctx_facts_exports"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtx(UserBase):
    """
    Core dir_ctx record for a scanned directory.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        ctx_path (str): Repo-relative ctx artifact path.
        name (str): Directory name label.
        schema_version (int): dir_ctx schema version.
        freshness_state (str): Freshness state (missing/stale/fresh/needs_review/blocked).
        last_scan_id (str | None): Last scan identifier.
        last_scanned_at (str | None): Timestamp of last scan.
        review_every_n_scans (int | None): Review cadence.
        scan_counter (int | None): Scan counter at last update.
        last_review_scan_id (str | None): Scan id for last review.
        subtree_hash_sha256 (str | None): Subtree hash checksum.
        ctx_semantic_hash_sha256 (str | None): Semantic hash checksum.
        template_version (str | None): Template version identifier.
        analyzer_version (str | None): Analyzer version identifier.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path).
        - ctx_path is unique per branch_name.
    """

    __tablename__ = "dir_ctx"
    __table_args__ = (
        UniqueConstraint("branch_name", "ctx_path", name="uq_dir_ctx_ctx_path"),
    )

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(32), nullable=False)
    last_scan_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_scanned_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    review_every_n_scans: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scan_counter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_review_scan_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subtree_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ctx_semantic_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    analyzer_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxStalenessReason(UserBase):
    """
    Staleness reason entry for a dir_ctx record.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        position (int): Ordering position for the reason list.
        reason (str): Staleness reason value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path, position).
        - position preserves reason ordering.
    """

    __tablename__ = "dir_ctx_staleness_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentSummary(UserBase):
    """
    Summary block for a dir_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        one_liner (str): One-line summary.
        detail (str): Detailed summary.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path).
    """

    __tablename__ = "dir_ctx_agent_summary"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    one_liner: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentArchitectureItem(UserBase):
    """
    List item for architecture arrays on dir_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        item_type (str): Architecture item type (responsibilities/non_goals/core_concepts).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path, item_type, position).
    """

    __tablename__ = "dir_ctx_agent_architecture_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentDependencyRules(UserBase):
    """
    Dependency rules core block for a dir_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        notes (str | None): Notes describing dependency rules.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path).
    """

    __tablename__ = "dir_ctx_agent_dependency_rules"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentDependencyRuleItem(UserBase):
    """
    List item for dependency_rules arrays on dir_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        item_type (str): Dependency rule item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers allowed_inbound/allowed_outbound/forbidden_dependencies.
        - Primary key is (branch_name, dir_path, item_type, position).
    """

    __tablename__ = "dir_ctx_agent_dependency_rule_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentKeyFlow(UserBase):
    """
    Key flow entry for a dir_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        flow_name (str): Key flow name.
        position (int): Ordering position for the flow list.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path, flow_name).
        - position preserves flow ordering within a dir_ctx record.
        - position is unique per (branch_name, dir_path).
    """

    __tablename__ = "dir_ctx_agent_key_flows"
    __table_args__ = (
        UniqueConstraint(
            "branch_name",
            "dir_path",
            "position",
            name="uq_dir_ctx_agent_key_flows_position",
        ),
    )

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    flow_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentKeyFlowItem(UserBase):
    """
    List item for key flow arrays on dir_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        flow_name (str): Key flow name.
        item_type (str): Key flow item type (steps/invariants).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path, flow_name, item_type, position).
    """

    __tablename__ = "dir_ctx_agent_key_flow_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    flow_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentInventoryFile(UserBase):
    """
    Inventory file entry for a dir_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        position (int): Ordering position for the inventory list.
        file_path (str): Repo-relative file path.
        ctx_path (str | None): Optional ctx path reference.
        role (str | None): Optional role description.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path, position).
    """

    __tablename__ = "dir_ctx_agent_inventory_files"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    ctx_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentInventorySubdir(UserBase):
    """
    Inventory subdir entry for a dir_ctx agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        position (int): Ordering position for the inventory list.
        subdir_path (str): Repo-relative subdir path.
        ctx_path (str | None): Optional ctx path reference.
        role (str | None): Optional role description.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, dir_path, position).
    """

    __tablename__ = "dir_ctx_agent_inventory_subdirs"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    subdir_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    ctx_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentIntegrationItem(UserBase):
    """
    List item for integration arrays on dir_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        item_type (str): Integration item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers entrypoints/used_by/uses/runtime_notes.
        - Primary key is (branch_name, dir_path, item_type, position).
    """

    __tablename__ = "dir_ctx_agent_integration_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentTestingItem(UserBase):
    """
    List item for testing arrays on dir_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        item_type (str): Testing item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers commands/required_when_changed/recommended_when_changed.
        - Primary key is (branch_name, dir_path, item_type, position).
    """

    __tablename__ = "dir_ctx_agent_testing_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class DirCtxAgentChangeSafetyItem(UserBase):
    """
    List item for change_safety arrays on dir_ctx.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        dir_path (str): Repo-relative directory path.
        item_type (str): Change safety item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers review_triggers/risky_changes/safe_changes.
        - Primary key is (branch_name, dir_path, item_type, position).
    """

    __tablename__ = "dir_ctx_agent_change_safety_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(1024), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContext(UserBase):
    """
    Core architecture_context record for a branch.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind (architecture_context/test_architecture_context).
        schema_version (int): Schema version of the payload.
        artifact_updated_at (str | None): Payload updated_at value.
        freshness_state (str): Computed freshness state.
        holes_count (int): Count of missing citations.
        holes_ratio (float | None): Ratio of missing citations.
        good_ratio (float | None): Ratio of good citations.
        inputs_hash (str | None): Inputs hash for matrix evaluation.
        last_checked_at (str | None): Timestamp of last evaluation.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind).
    """

    __tablename__ = "architecture_context"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    artifact_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    freshness_state: Mapped[str] = mapped_column(String(32), nullable=False)
    holes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    holes_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    good_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    inputs_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_checked_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContextAgentSummary(UserBase):
    """
    Summary block for an architecture_context agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        one_liner (str | None): One-line summary.
        detail (str | None): Detailed summary.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind).
        - Summary fields are optional and may be null when omitted.
    """

    __tablename__ = "architecture_context_agent_summary"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    one_liner: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContextAgentNotes(UserBase):
    """
    Notes block for an architecture_context agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        notes (str | None): Optional agent notes string.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind).
    """

    __tablename__ = "architecture_context_agent_notes"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContextAgentDirectory(UserBase):
    """
    Directory summary entry for an architecture_context agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        position (int): Ordering position for the directory list.
        path (str): Repo-relative directory path.
        summary_one_liner (str | None): Optional directory one-liner.
        summary_detail (str | None): Optional directory detail.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, position).
        - path is required for each directory entry.
    """

    __tablename__ = "architecture_context_agent_directories"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    summary_one_liner: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContextAgentItem(UserBase):
    """
    List item for architecture_context agent arrays.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        item_type (str): Agent list name (key_flows/boundaries).
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, item_type, position).
    """

    __tablename__ = "architecture_context_agent_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContextMatrix(UserBase):
    """
    Matrix entry for architecture_context citations.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        position (int): Ordering position for the matrix list.
        ctx_path (str): Ctx artifact path.
        ctx_kind (str | None): Ctx kind label.
        code_hash_sha256 (str | None): Code hash checksum.
        subtree_hash_sha256 (str | None): Subtree hash checksum.
        ctx_semantic_hash_sha256 (str | None): Semantic hash checksum.
        freshness_state (str | None): Freshness state snapshot.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, position).
    """

    __tablename__ = "architecture_context_matrix"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    ctx_kind: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subtree_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ctx_semantic_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    freshness_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ArchitectureContextStalenessReason(UserBase):
    """
    Staleness reason entry for architecture_context.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        position (int): Ordering position for the reason list.
        reason (str): Staleness reason value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, position).
    """

    __tablename__ = "architecture_context_staleness_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ComponentContexts(UserBase):
    """
    Core component_contexts record for a branch.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind (component_contexts/test_component_contexts).
        schema_version (int): Schema version of the payload.
        artifact_updated_at (str | None): Payload updated_at value.
        freshness_state (str): Computed freshness state.
        holes_count (int): Count of missing citations.
        holes_ratio (float | None): Ratio of missing citations.
        good_ratio (float | None): Ratio of good citations.
        inputs_hash (str | None): Inputs hash for matrix evaluation.
        last_checked_at (str | None): Timestamp of last evaluation.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind).
    """

    __tablename__ = "component_contexts"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    artifact_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    freshness_state: Mapped[str] = mapped_column(String(32), nullable=False)
    holes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    holes_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    good_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    inputs_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_checked_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ComponentContextsAgentSummary(UserBase):
    """
    Summary block for a component_contexts agent section.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        one_liner (str | None): One-line summary.
        detail (str | None): Detailed summary.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind).
        - Summary fields are optional and may be null when omitted.
    """

    __tablename__ = "component_contexts_agent_summary"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    one_liner: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ComponentContextsComponent(UserBase):
    """
    Component entry for a component_contexts record.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        component_id (str): Component identifier.
        name (str | None): Component display name.
        summary_one_liner (str | None): One-line summary.
        summary_detail (str | None): Detailed summary.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, component_id).
    """

    __tablename__ = "component_contexts_components"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    component_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    summary_one_liner: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ComponentContextsComponentItem(UserBase):
    """
    List item for component arrays on component_contexts.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        component_id (str): Component identifier.
        item_type (str): Component item type.
        position (int): Ordering position for the item list.
        value (str): Item value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - item_type covers boundaries/responsibilities/key_flows/ctx_paths.
        - Primary key is (branch_name, kind, component_id, item_type, position).
    """

    __tablename__ = "component_contexts_component_items"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    component_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    item_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ComponentContextsMatrix(UserBase):
    """
    Matrix entry for component_contexts citations.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        position (int): Ordering position for the matrix list.
        ctx_path (str): Ctx artifact path.
        ctx_kind (str | None): Ctx kind label.
        code_hash_sha256 (str | None): Code hash checksum.
        subtree_hash_sha256 (str | None): Subtree hash checksum.
        ctx_semantic_hash_sha256 (str | None): Semantic hash checksum.
        freshness_state (str | None): Freshness state snapshot.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, position).
    """

    __tablename__ = "component_contexts_matrix"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    ctx_kind: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subtree_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ctx_semantic_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    freshness_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class ComponentContextsStalenessReason(UserBase):
    """
    Staleness reason entry for component_contexts.

    Attributes:
        branch_name (str): Branch identifier owning the record.
        kind (str): Context kind.
        position (int): Ordering position for the reason list.
        reason (str): Staleness reason value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (branch_name, kind, position).
    """

    __tablename__ = "component_contexts_staleness_reasons"

    branch_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentProfile(UserBase):
    """
    Persistent agent profile record stored in user.db.

    Attributes:
        agent_id (str): Stable agent identifier (primary key).
        schema_version (int): Schema version for the profile payload.
        agent_kind (str | None): Optional agent kind label.
        status (str): Agent status ("active" or "inactive").
        agent_role (str): Agent role label.
        model_name (str | None): Optional model name or variant.
        runtime (str | None): Optional runtime identifier.
        current_task_id (str | None): Optional current task identifier.
        current_target (str | None): Optional current target path.
        notes (str | None): Optional operator notes.
        last_checkin_at (str | None): Last checkin timestamp.
        last_checkout_at (str | None): Last checkout timestamp.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per agent_id.
        - Last command and certification details live in child tables.
    """

    __tablename__ = "agent_profile"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_kind: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    agent_role: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    runtime: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_task_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_target: Mapped[str | None] = mapped_column(String(512), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_checkin_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_checkout_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentProfileCertification(UserBase):
    """
    Certification metadata for an agent profile.

    Attributes:
        agent_id (str): Agent identifier (primary key).
        schema_version (int): Schema version of the certification payload.
        state (str): Certification state enum value.
        certified (bool): Whether certification has completed.
        certified_at (str | None): Timestamp for certification completion.
        approved_at (str | None): Timestamp for user approval.
        approval_token (str | None): Approval token or external reference.
        approved_by (str | None): Approver identifier.
        self_certification_hash (str | None): Self-certification checksum.
        notes (str | None): Optional certification notes.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per agent_id.
    """

    __tablename__ = "agent_profile_certification"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(128), nullable=False)
    certified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    certified_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    approved_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    approval_token: Mapped[str | None] = mapped_column(String(256), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    self_certification_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentProfileLastCommand(UserBase):
    """
    Last command metadata for an agent profile.

    Attributes:
        agent_id (str): Agent identifier (primary key).
        name (str | None): Command name.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per agent_id.
        - Arguments are stored in AgentProfileLastCommandArg rows.
    """

    __tablename__ = "agent_profile_last_command"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentProfileLastCommandArg(UserBase):
    """
    Ordered argument list entries for the last command record.

    Attributes:
        agent_id (str): Agent identifier.
        position (int): Argument ordering position.
        value (str): Argument value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, position).
        - Ordering preserves the original args list.
    """

    __tablename__ = "agent_profile_last_command_args"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class SelfContext(UserBase):
    """
    Core self-context record per agent.

    Attributes:
        agent_id (str): Agent identifier (primary key).
        schema_version (int): Schema version for the self-context payload.
        understanding_repo_purpose (str): Repository purpose statement.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per agent_id.
        - Child tables store list and map fields.
    """

    __tablename__ = "self_context"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    understanding_repo_purpose: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class SelfContextNonNegotiable(UserBase):
    """
    Ordered list entries for self_context understanding.non_negotiables.

    Attributes:
        agent_id (str): Agent identifier.
        position (int): Ordering position.
        value (str): Non-negotiable value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, position).
    """

    __tablename__ = "self_context_non_negotiables"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class SelfContextStyleModelItem(UserBase):
    """
    Key/value entries for self_context understanding.style_model.

    Attributes:
        agent_id (str): Agent identifier.
        style_key (str): Style model key.
        value_type (str): Value type ("text", "number", "boolean", "json", "null").
        value_text (str | None): Text value for value_type "text".
        value_number (float | None): Numeric value for value_type "number".
        value_bool (bool | None): Boolean value for value_type "boolean".
        value_json (str | None): JSON-encoded value for value_type "json".
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, style_key).
        - Exactly one value_* field should be populated based on value_type.
    """

    __tablename__ = "self_context_style_model_items"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    style_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value_type: Mapped[str] = mapped_column(String(32), nullable=False)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_number: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_bool: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    value_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class SelfContextSkillReceipt(UserBase):
    """
    Ordered skill receipt entries for self_context.skill_receipts.

    Attributes:
        agent_id (str): Agent identifier.
        position (int): Ordering position.
        skill_id (str): Skill identifier.
        version (int): Skill version number.
        read_at (str): Read timestamp.
        agent_summary (str): Agent-provided summary of the skill.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, position).
    """

    __tablename__ = "self_context_skill_receipts"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    read_at: Mapped[str] = mapped_column(String(32), nullable=False)
    agent_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class SelfContextOpenQuestion(UserBase):
    """
    Ordered open question entries for self_context.open_questions.

    Attributes:
        agent_id (str): Agent identifier.
        position (int): Ordering position.
        topic (str): Question topic.
        question (str): Question content.
        blocking (bool): Whether the question is blocking.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, position).
    """

    __tablename__ = "self_context_open_questions"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(256), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    blocking: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class SelfContextOpinionItem(UserBase):
    """
    Ordered opinion list entries for self_context.opinions.

    Attributes:
        agent_id (str): Agent identifier.
        opinion_key (str): Opinion category key.
        position (int): Ordering position.
        value (str): Opinion entry value.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, opinion_key, position).
    """

    __tablename__ = "self_context_opinion_items"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    opinion_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentWorkQueue(UserBase):
    """
    Core agent work queue metadata per agent.

    Attributes:
        agent_id (str): Agent identifier (primary key).
        schema_version (int): Schema version for the queue payload.
        updated_at (str): ISO-8601 update timestamp.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per agent_id.
        - Items live in AgentWorkItem and child tables.
    """

    __tablename__ = "agent_work_queue"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentWorkItem(UserBase):
    """
    Work item entries for per-agent work queues.

    Attributes:
        agent_id (str): Agent identifier.
        work_id (str): Work item identifier.
        parent_work_id (str | None): Parent work identifier.
        root_work_id (str): Root work identifier.
        state (str): Work state enum value.
        kind (str): Work kind label.
        target_path (str): Target path.
        ctx_path (str): Context path.
        priority (int): Priority value.
        attempts (int): Attempt count.
        last_error_ref (str | None): Error reference id.
        position (int): Queue ordering position.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, work_id).
        - position preserves queue ordering.
    """

    __tablename__ = "agent_work_items"
    __table_args__ = (
        UniqueConstraint("agent_id", "position", name="uq_agent_work_item_position"),
    )

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    parent_work_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    root_work_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    last_error_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentWorkItemReason(UserBase):
    """
    Ordered reason entries for a work item.

    Attributes:
        agent_id (str): Agent identifier.
        work_id (str): Work item identifier.
        position (int): Ordering position.
        reason (str): Reason text.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, work_id, position).
    """

    __tablename__ = "agent_work_item_reasons"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class AgentWorkItemLease(UserBase):
    """
    Lease metadata for an agent work item.

    Attributes:
        agent_id (str): Agent identifier.
        work_id (str): Work item identifier.
        schema_version (int): Lease schema version.
        resource (str): Lease resource key.
        owner_id (str): Lease owner id.
        lease_work_id (str | None): Work identifier stored in the lease payload.
        created_at (str): Lease creation timestamp.
        heartbeat_at (str): Lease heartbeat timestamp.
        expires_at (str): Lease expiration timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (agent_id, work_id).
        - Rows are present only when a lease payload exists.
    """

    __tablename__ = "agent_work_item_lease"

    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    resource: Mapped[str] = mapped_column(String(256), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(128), nullable=False)
    lease_work_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    heartbeat_at: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class WorkQueue(UserBase):
    """
    Core work queue metadata for branch/global queues.

    Attributes:
        queue_id (str): Stable queue identifier (primary key).
        scope (str): Queue scope (global/branch).
        branch_name (str | None): Branch identifier for branch-scoped queues.
        bucket (str): Queue bucket name.
        work_kind (str): Work kind name.
        schema_version (int): Schema version for the queue payload.
        repo_id (str | None): Optional repository identifier.
        updated_at (str): ISO-8601 update timestamp.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is queue_id.
        - Items live in WorkQueueItem and child tables.
    """

    __tablename__ = "work_queues"
    __table_args__ = (
        UniqueConstraint(
            "scope",
            "branch_name",
            "bucket",
            "work_kind",
            name="uq_work_queue_scope_bucket",
        ),
    )

    queue_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    branch_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bucket: Mapped[str] = mapped_column(String(32), nullable=False)
    work_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    repo_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class WorkQueueItem(UserBase):
    """
    Work item entries for branch/global work queues.

    Attributes:
        queue_id (str): Queue identifier.
        work_id (str): Work item identifier.
        parent_work_id (str | None): Parent work identifier.
        root_work_id (str): Root work identifier.
        state (str): Work state enum value.
        kind (str): Work kind label.
        target_path (str): Target path.
        ctx_path (str): Context path.
        priority (int): Priority value.
        attempts (int): Attempt count.
        last_error_ref (str | None): Error reference id.
        position (int): Queue ordering position.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (queue_id, work_id).
        - position preserves queue ordering.
    """

    __tablename__ = "work_queue_items"
    __table_args__ = (
        UniqueConstraint("queue_id", "position", name="uq_work_queue_item_position"),
    )

    queue_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    parent_work_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    root_work_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    ctx_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    last_error_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class WorkQueueItemReason(UserBase):
    """
    Ordered reason entries for a work queue item.

    Attributes:
        queue_id (str): Queue identifier.
        work_id (str): Work item identifier.
        position (int): Ordering position.
        reason (str): Reason text.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (queue_id, work_id, position).
    """

    __tablename__ = "work_queue_item_reasons"

    queue_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class WorkQueueItemLease(UserBase):
    """
    Lease metadata for a work queue item.

    Attributes:
        queue_id (str): Queue identifier.
        work_id (str): Work item identifier.
        schema_version (int): Lease schema version.
        resource (str): Lease resource key.
        owner_id (str): Lease owner id.
        lease_work_id (str | None): Work identifier stored in the lease payload.
        created_at (str): Lease creation timestamp.
        heartbeat_at (str): Lease heartbeat timestamp.
        expires_at (str): Lease expiration timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (queue_id, work_id).
        - Rows are present only when a lease payload exists.
    """

    __tablename__ = "work_queue_item_lease"

    queue_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    work_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    resource: Mapped[str] = mapped_column(String(256), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(128), nullable=False)
    lease_work_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    heartbeat_at: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class OnboardingBundle(UserBase):
    """
    Snapshot header for an onboarding bundle.

    Attributes:
        bundle_id (str): Primary key identifier for the bundle snapshot.
        schema_version (int): Schema version for the bundle payload.
        bundle_format (str): Output format requested for the bundle (markdown/json).
        generated_at (str): ISO-8601 timestamp for bundle generation.
        file_count (int): Number of file entries captured in the bundle.
        missing_count (int): Number of missing file references.
        error_count (int): Number of read errors captured.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - One row per bundle_id.
        - Child rows live in onboarding_bundle_files, onboarding_bundle_missing,
          and onboarding_bundle_errors.
    """

    __tablename__ = "onboarding_bundle"

    bundle_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    bundle_format: Mapped[str] = mapped_column(String(16), nullable=False)
    generated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_count: Mapped[int] = mapped_column(Integer, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class OnboardingBundleFile(UserBase):
    """
    File entry captured as part of an onboarding bundle snapshot.

    Attributes:
        bundle_id (str): Bundle identifier owning the file entry.
        position (int): Ordering position within the bundle.
        path (str): Repo-relative path for the file.
        sha256 (str): SHA-256 checksum of the file content.
        content (str): Full file content captured in the snapshot.
        content_bytes (int): Size of the content in bytes (UTF-8).
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (bundle_id, position).
        - bundle_id references onboarding_bundle.bundle_id.
    """

    __tablename__ = "onboarding_bundle_files"
    __table_args__ = (
        UniqueConstraint("bundle_id", "path", name="uq_onboarding_bundle_files_path"),
    )

    bundle_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("onboarding_bundle.bundle_id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class OnboardingBundleMissing(UserBase):
    """
    Missing file entry captured in an onboarding bundle snapshot.

    Attributes:
        bundle_id (str): Bundle identifier owning the missing entry.
        position (int): Ordering position within the missing list.
        path (str): Repo-relative path for the missing file.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (bundle_id, position).
        - bundle_id references onboarding_bundle.bundle_id.
    """

    __tablename__ = "onboarding_bundle_missing"
    __table_args__ = (
        UniqueConstraint(
            "bundle_id", "path", name="uq_onboarding_bundle_missing_path"
        ),
    )

    bundle_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("onboarding_bundle.bundle_id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)


class OnboardingBundleError(UserBase):
    """
    Error entry captured while building an onboarding bundle snapshot.

    Attributes:
        bundle_id (str): Bundle identifier owning the error entry.
        position (int): Ordering position within the error list.
        path (str): Repo-relative path for the file that failed.
        error (str): Error message captured while reading the file.
        created_at (str): ISO-8601 creation timestamp.
        created_by (str): Actor identifier that created the record.
        updated_at (str): ISO-8601 update timestamp.
        updated_by (str): Actor identifier that last updated the record.

    Contract:
        - Primary key is (bundle_id, position).
        - bundle_id references onboarding_bundle.bundle_id.
    """

    __tablename__ = "onboarding_bundle_errors"
    __table_args__ = (
        UniqueConstraint("bundle_id", "path", name="uq_onboarding_bundle_errors_path"),
    )

    bundle_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("onboarding_bundle.bundle_id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    error: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False)
