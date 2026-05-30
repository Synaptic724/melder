"""Direct codegen contract tests for creation_context_codegen."""
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

import pytest

import melder.aether.conduit.meld.creation_context.creation_context_codegen as codegen


def test_compile_instance_overrides_only_executor_delegates_to_selected_template(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify instance overrides-only compilation delegates through the selected template."""
    captured: dict[str, Any] = {}
    sentinel_executor = object()

    def _template(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return sentinel_executor

    monkeypatch.setattr(codegen, "_select_overrides_only_template", lambda **kwargs: _template)

    result = codegen.compile_creation_context_instance_overrides_only_executor(
        resolve_route_key="many",
        spell="spell",
        spell_id="spell-id",
        owner_creations="owner",
        no_overrides_executor="executor",
        execute_with_overrides="override-executor",
        meld_execution_error_type=RuntimeError,
        spell_space_scope_error_type=ValueError,
    )

    assert result is sentinel_executor
    assert captured["_spell"] == "spell"
    assert captured["_spell_id"] == "spell-id"
    assert captured["_owner_creations"] == "owner"
    assert captured["_no_overrides_executor"] == "executor"
    assert captured["_execute_with_overrides"] == "override-executor"


@pytest.mark.parametrize(
    ("route_key", "enabled", "expected_fast"),
    [
        ("many", True, True),
        ("many", False, False),
        ("shared", True, False),
    ],
)
def test_compile_instance_no_overrides_executor_computes_fast_flag(
        monkeypatch: pytest.MonkeyPatch,
        route_key: str,
        enabled: bool,
        expected_fast: bool,
) -> None:
    """Verify instance no-overrides compilation computes the expected fast flag."""
    captured: dict[str, Any] = {}
    sentinel_executor = object()

    def _template(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return sentinel_executor

    monkeypatch.setattr(codegen, "_select_no_overrides_only_template", lambda **kwargs: _template)

    result = codegen.compile_creation_context_instance_no_overrides_executor(
        resolve_route_key=route_key,
        fast_transient_no_overrides_enabled=enabled,
        spell="spell",
        spell_id="spell-id",
        owner_creations="owner",
        no_overrides_executor="executor",
        spell_space_scope_error_type=ValueError,
    )

    assert result is sentinel_executor
    assert captured["_spell"] == "spell"
    assert captured["_spell_id"] == "spell-id"
    assert captured["_owner_creations"] == "owner"
    assert captured["_no_overrides_executor"] == "executor"


def test_compile_hooks_overrides_only_executor_delegates_to_selected_template(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify hooks overrides-only compilation delegates through the selected template."""
    captured: dict[str, Any] = {}
    sentinel_executor = object()

    def _template(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return sentinel_executor

    monkeypatch.setattr(codegen, "_select_overrides_only_hooks_template", lambda **kwargs: _template)

    result = codegen.compile_creation_context_hooks_overrides_only_executor(
        resolve_route_key="shared",
        spell="spell",
        spell_id="spell-id",
        owner_creations="owner",
        no_overrides_executor="executor",
        execute_with_overrides="override-executor",
        meld_execution_error_type=RuntimeError,
        spell_space_scope_error_type=ValueError,
    )

    assert result is sentinel_executor
    assert captured["_spell"] == "spell"
    assert captured["_spell_id"] == "spell-id"
    assert captured["_owner_creations"] == "owner"
    assert captured["_execute_with_overrides"] == "override-executor"


@pytest.mark.parametrize(
    ("route_key", "enabled", "expected_fast"),
    [
        ("many", True, True),
        ("many", False, False),
        ("shared", True, False),
    ],
)
def test_compile_hooks_no_overrides_executor_computes_fast_flag(
        monkeypatch: pytest.MonkeyPatch,
        route_key: str,
        enabled: bool,
        expected_fast: bool,
) -> None:
    """Verify hooks no-overrides compilation computes the expected fast flag."""
    captured: dict[str, Any] = {}
    sentinel_executor = object()

    def _template(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return sentinel_executor

    monkeypatch.setattr(codegen, "_select_no_overrides_only_hooks_template", lambda **kwargs: _template)

    result = codegen.compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=route_key,
        fast_transient_no_overrides_enabled=enabled,
        spell="spell",
        spell_id="spell-id",
        owner_creations="owner",
        no_overrides_executor="executor",
        spell_space_scope_error_type=ValueError,
    )

    assert result is sentinel_executor
    assert captured["_spell"] == "spell"
    assert captured["_spell_id"] == "spell-id"
    assert captured["_owner_creations"] == "owner"
    assert captured["_no_overrides_executor"] == "executor"


@pytest.mark.parametrize(
    ("fn_name", "kwargs", "match"),
    [
        ("_select_overrides_only_template", {"resolve_route_key": "bad"}, "Unsupported CreationContext overrides-only route key"),
        ("_select_overrides_only_hooks_template", {"resolve_route_key": "bad"}, "Unsupported CreationContext overrides-only route key"),
        ("_select_no_overrides_only_template", {"resolve_route_key": "bad", "use_fast_transient": False}, "Unsupported CreationContext resolve route key"),
        ("_select_no_overrides_only_hooks_template", {"resolve_route_key": "bad", "use_fast_transient": False}, "Unsupported CreationContext resolve route key"),
    ],
)
def test_selector_helpers_raise_for_unsupported_routes(
        fn_name: str,
        kwargs: Dict[str, Any],
        match: str,
) -> None:
    """Verify selector helpers fail fast on unsupported route keys."""
    fn = getattr(codegen, fn_name)
    with pytest.raises(RuntimeError, match=match):
        fn(**kwargs)


def test_selector_helpers_return_registered_templates_for_supported_routes() -> None:
    """Verify selector helpers return the registered template objects for valid routes."""
    assert codegen._select_overrides_only_template(resolve_route_key="many") is (
        codegen._OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE["many"]
    )
    assert codegen._select_overrides_only_hooks_template(resolve_route_key="shared") is (
        codegen._OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE["shared"]
    )
    assert codegen._select_no_overrides_only_template(
        resolve_route_key="many",
        use_fast_transient=True,
    ) is codegen._NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST[("many", True)]
    assert codegen._select_no_overrides_only_hooks_template(
        resolve_route_key="shared",
        use_fast_transient=False,
    ) is codegen._NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST[("shared", False)]


def test_compile_template_source_wraps_compile_failures() -> None:
    """Verify template compilation wraps source compile failures with the supplied message."""
    with pytest.raises(RuntimeError, match="compile-failed"):
        codegen._compile_creation_context_template_source(
            source="def broken(:\n    pass\n",
            source_name="<broken>",
            expected_callable_name="factory",
            compile_error_message="compile-failed",
            missing_callable_message="missing-callable",
        )


def test_compile_template_source_raises_when_callable_missing() -> None:
    """Verify template compilation fails when the expected callable export is missing."""
    with pytest.raises(RuntimeError, match="missing-callable"):
        codegen._compile_creation_context_template_source(
            source="x = 1\n",
            source_name="<missing>",
            expected_callable_name="factory",
            compile_error_message="compile-failed",
            missing_callable_message="missing-callable",
        )


def test_build_creation_context_template_source_name_includes_fast_flag() -> None:
    """Verify template source names include the optional fast-transient discriminator."""
    assert (
        codegen._build_creation_context_template_source_name(
            template_kind="kind",
            resolve_route_key="many",
            return_created=True,
            fast_transient_no_overrides_enabled=True,
        )
        == "<kind:many:1:1>"
    )


def test_build_no_overrides_lines_unsupported_route_raises() -> None:
    """Verify no-overrides line builder rejects unsupported routes."""
    with pytest.raises(RuntimeError, match="Unsupported CreationContext no-overrides route key"):
        codegen._build_no_overrides_lines(
            resolve_route_key="bad",
            fast_transient_no_overrides_enabled=False,
            return_created=True,
        )


def test_build_with_overrides_lines_shared_route_contains_expected_branches() -> None:
    """Verify shared-route override lines include lock/reuse and override-guard branches."""
    lines = codegen._build_with_overrides_lines(
        resolve_route_key="shared",
        return_created=True,
        overrides_maybe_none=True,
    )
    joined = "\n".join(lines)
    assert "creation = _owner_creations.get_creation(_spell_id)" in joined
    assert "with _spell._lock:" in joined
    assert "_existing_override_message" in joined


def test_build_with_overrides_lines_spellspace_route_uses_direct_store_access() -> None:
    """Verify spellspace-route override lines use direct spellspace store access."""
    lines = codegen._build_with_overrides_lines(
        resolve_route_key="spellspace",
        return_created=True,
        overrides_maybe_none=True,
    )
    joined = "\n".join(lines)
    assert "caller_creations.get_creation(_spell_id)" in joined
    assert "caller_creations.get_spellspace_creation" not in joined


def test_build_with_overrides_lines_existing_creation_route_contains_override_guard() -> None:
    """Verify existing-creation override lines include override and missing-instance guards."""
    lines = codegen._build_with_overrides_lines(
        resolve_route_key="existing_creation",
        return_created=False,
        overrides_maybe_none=True,
    )
    joined = "\n".join(lines)
    assert "if overrides is not None:" in joined
    assert "_existing_override_message" in joined
    assert "_existing_creation_missing_message" in joined


def test_build_with_overrides_lines_unique_per_conduit_route_contains_lock_and_override_guard() -> None:
    """Verify unique-per-conduit override lines include reuse, lock, and override-guard branches."""
    lines = codegen._build_with_overrides_lines(
        resolve_route_key="unique_per_conduit",
        return_created=True,
        overrides_maybe_none=True,
    )
    joined = "\n".join(lines)
    assert "creation = caller_creations.get_creation(_spell_id)" in joined
    assert "with caller_creations._lock:" in joined
    assert "_existing_override_message" in joined
    assert "_execute_with_overrides(caller_creations, overrides, True)" in joined


def test_build_with_overrides_lines_unsupported_route_raises() -> None:
    """Verify with-overrides line builder rejects unsupported routes."""
    with pytest.raises(RuntimeError, match="Unsupported CreationContext with-overrides route key"):
        codegen._build_with_overrides_lines(
            resolve_route_key="bad",
            return_created=True,
        )


def test_build_return_and_indent_helpers_format_expected_source() -> None:
    """Verify small emitted-source helpers format strings deterministically."""
    assert (
        codegen._build_return_statement(
            value_expression="instance",
            created=True,
            return_created=True,
        )
        == "return instance, True"
    )
    assert (
        codegen._build_return_statement(
            value_expression="instance",
            created=False,
            return_created=False,
        )
        == "return instance"
    )
    assert codegen._prefix_one_indent("line") == "    line"
    assert codegen._prefix_two_indent("line") == "        line"
    assert codegen._indent_lines(["a", "b"], 2) == ["        a", "        b"]
