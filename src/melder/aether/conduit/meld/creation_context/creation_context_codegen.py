from typing import Optional, Any, Callable, Sequence


def compile_creation_context_instance_overrides_only_executor(
        *,
        resolve_route_key: str,
        spell: Any,
        spell_id: str,
        owner_creations: Any,
        no_overrides_executor: Optional[Callable[..., Any]],
        execute_with_overrides: Callable[..., Any],
        meld_execution_error_type: Any,
        spell_space_scope_error_type: Any,
) -> Callable[..., Any]:
    """
    Build one spell-bound overrides-only CreationContext executor.

    Purpose:
        Provide a no-hooks override lane that never branches on
        `overrides is None` before entering existence-specific override routing.

    Contract:
        - Output callable signature: `(caller_creations, overrides) -> Any`.
        - Caller must pass a frontdoor-normalized override payload.
        - Emits the same existence-specific override semantics as the
          tuple-return hook lane.
    """
    template = _select_overrides_only_template(
        resolve_route_key=resolve_route_key,
    )
    return template(
        _spell=spell,
        _spell_id=spell_id,
        _owner_creations=owner_creations,
        _no_overrides_executor=no_overrides_executor,
        _execute_with_overrides=execute_with_overrides,
        _MeldExecutionError=meld_execution_error_type,
        _SpellSpaceScopeError=spell_space_scope_error_type,
        _existing_override_message=(
            "Overrides were supplied for a spell instance that already exists. "
            "Shared instances cannot be overridden after creation."
        ),
        _existing_creation_missing_message=(
            "[MELD] EXISTING_CREATION spell has no `user_created_object` "
            f"(spell_id={spell_id})."
        ),
        _spellspace_required_message=(
            "Existence.unique_per_spell_space requires an active SpellSpace. "
            "Use 'with conduit.enter_spellspace()' when melding."
        ),
    )


def compile_creation_context_instance_no_overrides_executor(
        *,
        resolve_route_key: str,
        fast_transient_no_overrides_enabled: bool,
        spell: Any,
        spell_id: str,
        owner_creations: Any,
        no_overrides_executor: Optional[Callable[..., Any]],
        spell_space_scope_error_type: Any,
) -> Callable[..., Any]:
    """
    Build one spell-bound no-overrides-only CreationContext executor.

    Purpose:
        Provide the no-hooks / no-overrides fast door with no override branch.

    Contract:
        - Output callable signature: `(caller_creations) -> Any`.
        - Caller must ensure override payload is absent for this lane.
    """
    use_fast_transient = bool(
        resolve_route_key == "many"
        and fast_transient_no_overrides_enabled
    )
    template = _select_no_overrides_only_template(
        resolve_route_key=resolve_route_key,
        use_fast_transient=use_fast_transient,
    )
    return template(
        _spell=spell,
        _spell_id=spell_id,
        _owner_creations=owner_creations,
        _no_overrides_executor=no_overrides_executor,
        _SpellSpaceScopeError=spell_space_scope_error_type,
        _existing_creation_missing_message=(
            "[MELD] EXISTING_CREATION spell has no `user_created_object` "
            f"(spell_id={spell_id})."
        ),
        _spellspace_required_message=(
            "Existence.unique_per_spell_space requires an active SpellSpace. "
            "Use 'with conduit.enter_spellspace()' when melding."
        ),
    )


def compile_creation_context_hooks_overrides_only_executor(
        *,
        resolve_route_key: str,
        spell: Any,
        spell_id: str,
        owner_creations: Any,
        no_overrides_executor: Optional[Callable[..., Any]],
        execute_with_overrides: Callable[..., Any],
        meld_execution_error_type: Any,
        spell_space_scope_error_type: Any,
) -> Callable[..., Any]:
    """
    Build one spell-bound hooks-lane overrides-only CreationContext executor.

    Purpose:
        Provide the hooks override lane with no local `overrides is None`
        branch. Meld chooses this door only when an override payload exists.

    Contract:
        - Output callable signature:
          `(caller_creations, overrides) -> tuple[Any, bool]`.
        - Caller must pass a frontdoor-normalized override payload.
        - Returns `(instance, created)` for hook activation routing.
    """
    template = _select_overrides_only_hooks_template(
        resolve_route_key=resolve_route_key,
    )
    return template(
        _spell=spell,
        _spell_id=spell_id,
        _owner_creations=owner_creations,
        _no_overrides_executor=no_overrides_executor,
        _execute_with_overrides=execute_with_overrides,
        _MeldExecutionError=meld_execution_error_type,
        _SpellSpaceScopeError=spell_space_scope_error_type,
        _existing_override_message=(
            "Overrides were supplied for a spell instance that already exists. "
            "Shared instances cannot be overridden after creation."
        ),
        _existing_creation_missing_message=(
            "[MELD] EXISTING_CREATION spell has no `user_created_object` "
            f"(spell_id={spell_id})."
        ),
        _spellspace_required_message=(
            "Existence.unique_per_spell_space requires an active SpellSpace. "
            "Use 'with conduit.enter_spellspace()' when melding."
        ),
    )


def compile_creation_context_hooks_no_overrides_executor(
        *,
        resolve_route_key: str,
        fast_transient_no_overrides_enabled: bool,
        spell: Any,
        spell_id: str,
        owner_creations: Any,
        no_overrides_executor: Optional[Callable[..., Any]],
        spell_space_scope_error_type: Any,
) -> Callable[..., Any]:
    """
    Build one spell-bound hooks-lane no-overrides CreationContext executor.

    Purpose:
        Provide the hooks no-overrides lane with no local override branch.
        Meld chooses this door only when no override payload exists.

    Contract:
        - Output callable signature: `(caller_creations) -> tuple[Any, bool]`.
        - Returns `(instance, created)` for hook activation routing.
    """
    use_fast_transient = bool(
        resolve_route_key == "many"
        and fast_transient_no_overrides_enabled
    )
    template = _select_no_overrides_only_hooks_template(
        resolve_route_key=resolve_route_key,
        use_fast_transient=use_fast_transient,
    )
    return template(
        _spell=spell,
        _spell_id=spell_id,
        _owner_creations=owner_creations,
        _no_overrides_executor=no_overrides_executor,
        _SpellSpaceScopeError=spell_space_scope_error_type,
        _existing_creation_missing_message=(
            "[MELD] EXISTING_CREATION spell has no `user_created_object` "
            f"(spell_id={spell_id})."
        ),
        _spellspace_required_message=(
            "Existence.unique_per_spell_space requires an active SpellSpace. "
            "Use 'with conduit.enter_spellspace()' when melding."
        ),
    )


def _select_overrides_only_template(
        *,
        resolve_route_key: str,
) -> Callable[..., Any]:
    """
    Resolve one precompiled overrides-only template by existence route.
    """
    template = _OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE.get(resolve_route_key)
    if template is not None:
        return template
    raise RuntimeError(
        f"Unsupported CreationContext overrides-only route key: {resolve_route_key}"
    )


def _select_overrides_only_hooks_template(
        *,
        resolve_route_key: str,
) -> Callable[..., Any]:
    """
    Resolve one precompiled hooks overrides-only template by existence route.
    """
    template = _OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE.get(resolve_route_key)
    if template is not None:
        return template
    raise RuntimeError(
        f"Unsupported CreationContext overrides-only route key: {resolve_route_key}"
    )


def _select_no_overrides_only_template(
        *,
        resolve_route_key: str,
        use_fast_transient: bool,
) -> Callable[..., Any]:
    """
    Resolve one precompiled no-overrides-only template by existence route.
    """
    template = _NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST.get(
        (resolve_route_key, use_fast_transient),
    )
    if template is not None:
        return template
    raise RuntimeError(
        f"Unsupported CreationContext resolve route key: {resolve_route_key}"
    )


def _select_no_overrides_only_hooks_template(
        *,
        resolve_route_key: str,
        use_fast_transient: bool,
) -> Callable[..., Any]:
    """
    Resolve one precompiled hooks no-overrides-only template by route.
    """
    template = _NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST.get(
        (resolve_route_key, use_fast_transient),
    )
    if template is not None:
        return template
    raise RuntimeError(
        f"Unsupported CreationContext resolve route key: {resolve_route_key}"
    )


def _compile_creation_context_overrides_only_template(
        *,
        resolve_route_key: str,
        return_created: bool,
) -> Callable[..., Any]:
    """
    Compile one overrides-only template factory for no-hooks overrides door.
    """
    with_overrides_lines = _build_with_overrides_lines(
        resolve_route_key=resolve_route_key,
        return_created=return_created,
        overrides_maybe_none=False,
    )
    source = _build_overrides_only_template_source(
        with_overrides_lines=with_overrides_lines,
    )
    source_name = _build_creation_context_template_source_name(
        template_kind="creation_context_overrides_only_template",
        resolve_route_key=resolve_route_key,
        return_created=return_created,
    )
    return _compile_creation_context_template_source(
        source=source,
        source_name=source_name,
        expected_callable_name="_creation_context_overrides_only_template",
        compile_error_message=(
            "Failed to compile CreationContext overrides-only template source."
        ),
        missing_callable_message=(
            "CreationContext overrides-only template source did not define callable "
            "_creation_context_overrides_only_template."
        ),
    )


def _compile_creation_context_no_overrides_only_template(
        *,
        resolve_route_key: str,
        fast_transient_no_overrides_enabled: bool,
        return_created: bool,
) -> Callable[..., Any]:
    """
    Compile one no-overrides-only template factory for no-hooks fast door.
    """
    no_overrides_lines = _build_no_overrides_lines(
        resolve_route_key=resolve_route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        return_created=return_created,
    )
    source = _build_no_overrides_only_template_source(
        no_overrides_lines=no_overrides_lines,
    )
    source_name = _build_creation_context_template_source_name(
        template_kind="creation_context_no_overrides_only_template",
        resolve_route_key=resolve_route_key,
        return_created=return_created,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
    )
    return _compile_creation_context_template_source(
        source=source,
        source_name=source_name,
        expected_callable_name="_creation_context_no_overrides_only_template",
        compile_error_message=(
            "Failed to compile CreationContext no-overrides-only template source."
        ),
        missing_callable_message=(
            "CreationContext no-overrides-only template source did not define callable "
            "_creation_context_no_overrides_only_template."
        ),
    )


def _compile_creation_context_template_source(
        *,
        source: str,
        source_name: str,
        expected_callable_name: str,
        compile_error_message: str,
        missing_callable_message: str,
) -> Callable[..., Any]:
    """
    Compile emitted template source and resolve one expected callable export.

    Contract:
        - Executes compiled `source` in an isolated local namespace.
        - Returns the callable named by `expected_callable_name`.
        - Raises RuntimeError with caller-provided messages for compile or export
          contract failures.
    """
    local_namespace: dict[str, Any] = {}
    try:
        exec(
            compile(source, source_name, "exec"),
            {},
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(compile_error_message) from exc
    template = local_namespace.get(expected_callable_name)
    if callable(template):
        return template
    raise RuntimeError(missing_callable_message)


def _build_creation_context_template_source_name(
        *,
        template_kind: str,
        resolve_route_key: str,
        return_created: bool,
        fast_transient_no_overrides_enabled: Optional[bool] = None,
) -> str:
    """
    Build one deterministic compile source name for emitted template code.
    """
    source_name = (
        f"<{template_kind}:{resolve_route_key}:"
    )
    if fast_transient_no_overrides_enabled is not None:
        source_name += f"{int(fast_transient_no_overrides_enabled)}:"
    source_name += f"{int(return_created)}>"
    return source_name


def _build_creation_context_template_source(
        *,
        template_callable_name: str,
        template_parameter_lines: Sequence[str],
        execution_callable_name: str,
        execution_signature: str,
        execution_lines: Sequence[str],
) -> str:
    """
    Build emitted source for one CreationContext template/executor pair.
    """
    lines = [f"def {template_callable_name}("]
    lines.extend(template_parameter_lines)
    lines.append("    ):")
    lines.append(f"    def {execution_callable_name}({execution_signature}):")
    lines.extend(_indent_lines(execution_lines, 2))
    lines.append(f"    return {execution_callable_name}")
    return "\n".join(lines)


def _build_no_overrides_only_template_source(
        *,
        no_overrides_lines: Sequence[str],
) -> str:
    """
    Build emitted source for one no-overrides-only template factory.
    """
    return _build_creation_context_template_source(
        template_callable_name="_creation_context_no_overrides_only_template",
        template_parameter_lines=[
        "        _spell,",
        "        _spell_id,",
        "        _owner_creations,",
        "        _no_overrides_executor,",
        "        _SpellSpaceScopeError,",
        "        _existing_creation_missing_message,",
        "        _spellspace_required_message,",
        ],
        execution_callable_name="_creation_context_execute_no_overrides_only",
        execution_signature="caller_creations",
        execution_lines=no_overrides_lines,
    )


def _build_overrides_only_template_source(
        *,
        with_overrides_lines: Sequence[str],
) -> str:
    """
    Build emitted source for one overrides-only template factory.
    """
    return _build_creation_context_template_source(
        template_callable_name="_creation_context_overrides_only_template",
        template_parameter_lines=[
        "        _spell,",
        "        _spell_id,",
        "        _owner_creations,",
        "        _no_overrides_executor,",
        "        _execute_with_overrides,",
        "        _MeldExecutionError,",
        "        _SpellSpaceScopeError,",
        "        _existing_override_message,",
        "        _existing_creation_missing_message,",
        "        _spellspace_required_message,",
        ],
        execution_callable_name="_creation_context_execute_overrides_only",
        execution_signature="caller_creations, overrides",
        execution_lines=with_overrides_lines,
    )


def _build_no_overrides_lines(
        *,
        resolve_route_key: str,
        fast_transient_no_overrides_enabled: bool,
        return_created: bool,
) -> Sequence[str]:
    """
    Build no-overrides existence path source lines.
    """
    if resolve_route_key == "existing_creation":
        return [
            "instance = _spell.user_created_object",
            "if instance is None:",
            "    raise RuntimeError(_existing_creation_missing_message)",
            _build_return_statement(
                value_expression="instance",
                created=False,
                return_created=return_created,
            ),
        ]
    if resolve_route_key == "many":
        if fast_transient_no_overrides_enabled:
            return [
                "instance = _no_overrides_executor()",
                _build_return_statement(
                    value_expression="instance",
                    created=True,
                    return_created=return_created,
                ),
            ]
        return _build_no_overrides_create_lines(
            caller_creations_lock_held=False,
            return_created=return_created,
        )
    if resolve_route_key == "unique_per_conduit":
        return [
            "caller_creations_values = caller_creations._creations",
            "creation = caller_creations_values.get(_spell_id)",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations_values.get(_spell_id)",
            "    if creation is None:",
        ] + _indent_lines(
            _build_no_overrides_create_lines(
                caller_creations_lock_held=True,
                return_created=return_created,
            ),
            2,
        ) + [
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "spellspace":
        return [
            "spellspace = caller_creations._conduit.get_active_spellspace()",
            "if spellspace is None:",
            "    raise _SpellSpaceScopeError(_spellspace_required_message)",
            "spellspace_id = spellspace.id",
            "caller_creations_values = caller_creations._creations",
            "spellspace_bucket = caller_creations_values.get(spellspace_id)",
            "creation = spellspace_bucket.get(_spell_id) if isinstance(spellspace_bucket, dict) else None",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    spellspace_bucket = caller_creations_values.get(spellspace_id)",
            "    creation = spellspace_bucket.get(_spell_id) if isinstance(spellspace_bucket, dict) else None",
            "    if creation is None:",
        ] + _indent_lines(
            _build_no_overrides_create_lines(
                caller_creations_lock_held=True,
                return_created=return_created,
            ),
            2,
        ) + [
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "shared":
        return [
            "owner_creations_values = _owner_creations._creations",
            "creation = owner_creations_values.get(_spell_id)",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with _spell._lock:",
            "    with _owner_creations._lock:",
            "        creation = owner_creations_values.get(_spell_id)",
            "    if creation is None:",
        ] + _indent_lines(
            _build_no_overrides_create_lines(
                caller_creations_lock_held=False,
                return_created=return_created,
            ),
            2,
        ) + [
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    raise RuntimeError(
        f"Unsupported CreationContext no-overrides route key: {resolve_route_key}"
    )


def _build_with_overrides_lines(
        *,
        resolve_route_key: str,
        return_created: bool,
        overrides_maybe_none: bool = True,
) -> Sequence[str]:
    """
    Build with-overrides existence path source lines.
    """
    if resolve_route_key == "existing_creation":
        if not overrides_maybe_none:
            return [
                "raise _MeldExecutionError(",
                "    spell_id=_spell.spell_index.current,",
                "    spell_name=_spell.spell_name,",
                "    message=_existing_override_message,",
                ")",
            ]
        return [
            "if overrides is not None:",
            "    raise _MeldExecutionError(",
            "        spell_id=_spell.spell_index.current,",
            "        spell_name=_spell.spell_name,",
            "        message=_existing_override_message,",
            "    )",
            "instance = _spell.user_created_object",
            "if instance is None:",
            "    raise RuntimeError(_existing_creation_missing_message)",
            _build_return_statement(
                value_expression="instance",
                created=False,
                return_created=return_created,
            ),
        ]
    if resolve_route_key == "many":
        return [
            "instance = _execute_with_overrides(caller_creations, overrides, False)",
            _build_return_statement(
                value_expression="instance",
                created=True,
                return_created=return_created,
            ),
        ]
    if resolve_route_key == "unique_per_conduit":
        if not overrides_maybe_none:
            return [
                "creation = caller_creations._creations.get(_spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with caller_creations._lock:",
                "    creation = caller_creations._creations.get(_spell_id)",
                "    if creation is None:",
                "        instance = _execute_with_overrides(caller_creations, overrides, True)",
                _prefix_two_indent(
                    _build_return_statement(
                        value_expression="instance",
                        created=True,
                        return_created=return_created,
                    ),
                ),
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
            ]
        return [
            "creation = caller_creations._creations.get(_spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations._creations.get(_spell_id)",
            "    if creation is None:",
            "        instance = _execute_with_overrides(caller_creations, overrides, True)",
            _prefix_two_indent(
                _build_return_statement(
                    value_expression="instance",
                    created=True,
                    return_created=return_created,
                ),
            ),
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "spellspace":
        if not overrides_maybe_none:
            return [
                "spellspace = caller_creations._conduit.get_active_spellspace()",
                "if spellspace is None:",
                "    raise _SpellSpaceScopeError(_spellspace_required_message)",
                "creation = caller_creations.get_spellspace_creation(spellspace.id, _spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with caller_creations._lock:",
                "    creation = caller_creations.get_spellspace_creation(spellspace.id, _spell_id)",
                "    if creation is None:",
                "        instance = _execute_with_overrides(caller_creations, overrides, True)",
                _prefix_two_indent(
                    _build_return_statement(
                        value_expression="instance",
                        created=True,
                        return_created=return_created,
                    ),
                ),
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
            ]
        return [
            "spellspace = caller_creations._conduit.get_active_spellspace()",
            "if spellspace is None:",
            "    raise _SpellSpaceScopeError(_spellspace_required_message)",
            "creation = caller_creations.get_spellspace_creation(spellspace.id, _spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations.get_spellspace_creation(spellspace.id, _spell_id)",
            "    if creation is None:",
            "        instance = _execute_with_overrides(caller_creations, overrides, True)",
            _prefix_two_indent(
                _build_return_statement(
                    value_expression="instance",
                    created=True,
                    return_created=return_created,
                ),
            ),
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "shared":
        if not overrides_maybe_none:
            return [
                "creation = _owner_creations._creations.get(_spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with _spell._lock:",
                "    with _owner_creations._lock:",
                "        creation = _owner_creations._creations.get(_spell_id)",
                "    if creation is None:",
                "        instance = _execute_with_overrides(caller_creations, overrides, False)",
                _prefix_two_indent(
                    _build_return_statement(
                        value_expression="instance",
                        created=True,
                        return_created=return_created,
                    ),
                ),
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
            ]
        return [
            "creation = _owner_creations._creations.get(_spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with _spell._lock:",
            "    with _owner_creations._lock:",
            "        creation = _owner_creations._creations.get(_spell_id)",
            "    if creation is None:",
            "        instance = _execute_with_overrides(caller_creations, overrides, False)",
            _prefix_two_indent(
                _build_return_statement(
                    value_expression="instance",
                    created=True,
                    return_created=return_created,
                ),
            ),
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation.value",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    raise RuntimeError(
        f"Unsupported CreationContext with-overrides route key: {resolve_route_key}"
    )


def _build_no_overrides_create_lines(
        *,
        caller_creations_lock_held: bool,
        return_created: bool,
) -> Sequence[str]:
    """
    Build emitted source lines for no-overrides creation executor call.
    """
    return [
        "instance = _no_overrides_executor(",
        "    caller_creations,",
        "    _owner_creations,",
        f"    {caller_creations_lock_held},",
        ")",
        _build_return_statement(
            value_expression="instance",
            created=True,
            return_created=return_created,
        ),
    ]


def _build_return_statement(
        *,
        value_expression: str,
        created: bool,
        return_created: bool,
) -> str:
    """
    Build one emitted return line for template route branches.
    """
    if return_created:
        return f"return {value_expression}, {created}"
    return f"return {value_expression}"


def _prefix_one_indent(line: str) -> str:
    """
    Prefix one indentation level to one emitted source line.
    """
    return f"    {line}"


def _prefix_two_indent(line: str) -> str:
    """
    Prefix two indentation levels to one emitted source line.
    """
    return f"        {line}"


def _indent_lines(lines: Sequence[str], level: int) -> list[str]:
    """
    Indent emitted source lines by indentation level.
    """
    prefix = "    " * level
    return [f"{prefix}{line}" for line in lines]


_TEMPLATE_EXISTING_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="existing_creation",
        return_created=True,
    )
)
_TEMPLATE_MANY_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="many",
        return_created=True,
    )
)
_TEMPLATE_UNIQUE_PER_CONDUIT_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="unique_per_conduit",
        return_created=True,
    )
)
_TEMPLATE_SPELLSPACE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="spellspace",
        return_created=True,
    )
)
_TEMPLATE_SHARED_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="shared",
        return_created=True,
    )
)
_TEMPLATE_EXISTING_INSTANCE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="existing_creation",
        return_created=False,
    )
)
_TEMPLATE_MANY_INSTANCE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="many",
        return_created=False,
    )
)
_TEMPLATE_UNIQUE_PER_CONDUIT_INSTANCE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="unique_per_conduit",
        return_created=False,
    )
)
_TEMPLATE_SPELLSPACE_INSTANCE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="spellspace",
        return_created=False,
    )
)
_TEMPLATE_SHARED_INSTANCE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="shared",
        return_created=False,
    )
)
_TEMPLATE_EXISTING_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="existing_creation",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
_TEMPLATE_MANY_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="many",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
_TEMPLATE_MANY_NO_OVERRIDES_ONLY_FAST = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="many",
        fast_transient_no_overrides_enabled=True,
        return_created=True,
    )
)
_TEMPLATE_UNIQUE_PER_CONDUIT_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="unique_per_conduit",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
_TEMPLATE_SPELLSPACE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="spellspace",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
_TEMPLATE_SHARED_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="shared",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
_TEMPLATE_EXISTING_INSTANCE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="existing_creation",
        fast_transient_no_overrides_enabled=False,
        return_created=False,
    )
)
_TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="many",
        fast_transient_no_overrides_enabled=False,
        return_created=False,
    )
)
_TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY_FAST = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="many",
        fast_transient_no_overrides_enabled=True,
        return_created=False,
    )
)
_TEMPLATE_UNIQUE_PER_CONDUIT_INSTANCE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="unique_per_conduit",
        fast_transient_no_overrides_enabled=False,
        return_created=False,
    )
)
_TEMPLATE_SPELLSPACE_INSTANCE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="spellspace",
        fast_transient_no_overrides_enabled=False,
        return_created=False,
    )
)
_TEMPLATE_SHARED_INSTANCE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="shared",
        fast_transient_no_overrides_enabled=False,
        return_created=False,
    )
)


_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE = {
    "existing_creation": _TEMPLATE_EXISTING_INSTANCE_OVERRIDES_ONLY,
    "many": _TEMPLATE_MANY_INSTANCE_OVERRIDES_ONLY,
    "unique_per_conduit": _TEMPLATE_UNIQUE_PER_CONDUIT_INSTANCE_OVERRIDES_ONLY,
    "spellspace": _TEMPLATE_SPELLSPACE_INSTANCE_OVERRIDES_ONLY,
    "shared": _TEMPLATE_SHARED_INSTANCE_OVERRIDES_ONLY,
}

_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE = {
    "existing_creation": _TEMPLATE_EXISTING_OVERRIDES_ONLY,
    "many": _TEMPLATE_MANY_OVERRIDES_ONLY,
    "unique_per_conduit": _TEMPLATE_UNIQUE_PER_CONDUIT_OVERRIDES_ONLY,
    "spellspace": _TEMPLATE_SPELLSPACE_OVERRIDES_ONLY,
    "shared": _TEMPLATE_SHARED_OVERRIDES_ONLY,
}

_NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST = {
    ("existing_creation", False): _TEMPLATE_EXISTING_INSTANCE_NO_OVERRIDES_ONLY,
    ("existing_creation", True): _TEMPLATE_EXISTING_INSTANCE_NO_OVERRIDES_ONLY,
    ("many", False): _TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY,
    ("many", True): _TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY_FAST,
    ("unique_per_conduit", False): _TEMPLATE_UNIQUE_PER_CONDUIT_INSTANCE_NO_OVERRIDES_ONLY,
    ("unique_per_conduit", True): _TEMPLATE_UNIQUE_PER_CONDUIT_INSTANCE_NO_OVERRIDES_ONLY,
    ("spellspace", False): _TEMPLATE_SPELLSPACE_INSTANCE_NO_OVERRIDES_ONLY,
    ("spellspace", True): _TEMPLATE_SPELLSPACE_INSTANCE_NO_OVERRIDES_ONLY,
    ("shared", False): _TEMPLATE_SHARED_INSTANCE_NO_OVERRIDES_ONLY,
    ("shared", True): _TEMPLATE_SHARED_INSTANCE_NO_OVERRIDES_ONLY,
}

_NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST = {
    ("existing_creation", False): _TEMPLATE_EXISTING_NO_OVERRIDES_ONLY,
    ("existing_creation", True): _TEMPLATE_EXISTING_NO_OVERRIDES_ONLY,
    ("many", False): _TEMPLATE_MANY_NO_OVERRIDES_ONLY,
    ("many", True): _TEMPLATE_MANY_NO_OVERRIDES_ONLY_FAST,
    ("unique_per_conduit", False): _TEMPLATE_UNIQUE_PER_CONDUIT_NO_OVERRIDES_ONLY,
    ("unique_per_conduit", True): _TEMPLATE_UNIQUE_PER_CONDUIT_NO_OVERRIDES_ONLY,
    ("spellspace", False): _TEMPLATE_SPELLSPACE_NO_OVERRIDES_ONLY,
    ("spellspace", True): _TEMPLATE_SPELLSPACE_NO_OVERRIDES_ONLY,
    ("shared", False): _TEMPLATE_SHARED_NO_OVERRIDES_ONLY,
    ("shared", True): _TEMPLATE_SHARED_NO_OVERRIDES_ONLY,
}
